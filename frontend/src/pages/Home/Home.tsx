import { FC, useEffect, useState, useRef } from "react";
import { useAppStore } from "@/stores/app.store";
import * as marketApi from "@/api/services/market.service";
import Styles from "./Home.module.scss";
import FiltersComponent from "./Components/Filters/Filters";
import GiftsComponent from "./Components/Gifts/Gifts";

const Home: FC = () => {
  const { filtersHomeData } = useAppStore();

  const giftsObserverRef = useRef<HTMLDivElement | null>(null);

  const [gifts, setGifts] = useState<any[]>([]);
  const [giftsOffset, setGiftsOffset] = useState(0);
  const [giftsHasMore, setGiftsHasMore] = useState(true);

  const fetchGifts = async (newOffset = 0, append = false) => {
    const response = await marketApi.gifts({
      limit: 20,
      offset: newOffset,
      collection: filtersHomeData.collection,
      model: filtersHomeData.model,
      sort_by: filtersHomeData.sort_by,
      from_price: filtersHomeData.from_price,
      to_price: filtersHomeData.to_price,
      number: filtersHomeData.number,
    }) as any;

    if (response.type === "success") {
      const data = response.data;
      if (data.length < 20) setGiftsHasMore(false);
      setGifts(prev => append ? [...prev, ...data] : data);
      setGiftsOffset((prev) => prev + 20);
    }
  };

  useEffect(() => {
    setGiftsOffset(0);
    setGiftsHasMore(true);
    fetchGifts(0, false);
  }, [filtersHomeData]);

  useEffect(() => {
    if (!giftsObserverRef.current || !giftsHasMore) return;

    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && giftsHasMore) {
        fetchGifts(giftsOffset, true);
      }
    });

    observer.observe(giftsObserverRef.current);
    return () => observer.disconnect();
  }, [giftsOffset, giftsHasMore, gifts]);

  return (
    <div className={Styles.Home}>
      <main>
        <div className={Styles.HomeInner}>
          <FiltersComponent />
          <GiftsComponent gifts={gifts} />
          {giftsHasMore && <div ref={giftsObserverRef} style={{ height: 1 }} />}
        </div>
      </main>
    </div>
  );
};

export default Home;