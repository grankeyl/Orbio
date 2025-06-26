import { FC, useEffect, useRef, useState } from "react";
import { useAppStore } from "@/stores/app.store";

import * as historyApi from "@/api/services/history.service";

import Styles from "./Activity.module.scss";
import FiltersComponent from "./Components/Filters/Filters";
import HistoryComponent from "./Components/History/History";

const Activity: FC = () => {
  const { filtersActivityData } = useAppStore();

  const activityObserverRef = useRef<HTMLDivElement | null>(null);

  const [activity, setActivity] = useState<any[]>([]);
  const [activityOffset, setActivityOffset] = useState(0);
  const [activityHasMore, setActivityHasMore] = useState(true);

  const fetchActivity = async (newOffset = 0, append = false) => {
    const response = await historyApi.activity({
      collection: filtersActivityData.collection,
      sort_by: filtersActivityData.sort_by,
      number: filtersActivityData.number,
      limit: 20,
      offset: newOffset
    }) as any;

    if (response.type === "success") {
      const data = response.data;
      if (data.length < 20) setActivityHasMore(false);
      setActivity(prev => append ? [...prev, ...data] : data);
      setActivityOffset((prev) => prev + 20);
    }
  };

  useEffect(() => {
    setActivityOffset(0);
    setActivityHasMore(true);
    fetchActivity(0, false);
  }, [filtersActivityData]);

  useEffect(() => {
    if (!activityObserverRef.current || !activityHasMore) return;

    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && activityHasMore) {
        fetchActivity(activityOffset, true);
      }
    });

    observer.observe(activityObserverRef.current);
    return () => observer.disconnect();
  }, [activityOffset, activityHasMore, activity]);

  return (
    <div className={Styles.Activity}>
      <main>
        <div className={Styles.ActivityInner}>
          <FiltersComponent />
          <HistoryComponent
            activity={activity}
          />
          {activityHasMore && <div ref={activityObserverRef} style={{ height: 1 }} />}
        </div>
      </main>
    </div>
  )
}

export default Activity;