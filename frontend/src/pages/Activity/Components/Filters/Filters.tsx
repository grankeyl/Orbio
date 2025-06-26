import { FC, useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app.store";
import { ChevroneIcon, HashtagIcon } from "@/components/Icons";
import { getNameSortFilter } from "@/utils/filter";

import Styles from "./Filters.module.scss";
import Collection from "./Collection/Collection";
import Sort from "./Sort/Sort";

const Filters: FC = () => {
  const { filtersActivityData, setFiltersActivityData } = useAppStore();
  
  const [activeDropdown, setActiveDropdown] = useState<"collection" | "model" | "sort" | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [collectionsValue, setCollectionsValue] = useState<any>();
  const [sortValue, setSortValue] = useState<any>("latest");
  const [numberValue, setNumberValue] = useState<number>(0);

  const toggleDropdown = (key: "collection" | "model" | "sort") => {
    setActiveDropdown((prev) => (prev === key ? null : key));
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setActiveDropdown(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    setCollectionsValue(filtersActivityData.collection);
    setSortValue(filtersActivityData.sort_by);
  }, [filtersActivityData]);

  useEffect(() => {
    setTimeout(() => {
      if (numberValue === 0) {
        setFiltersActivityData({ 
          collection: filtersActivityData.collection,
          sort_by: sortValue,
          number: null,
        });
        return;
      }

      setFiltersActivityData({ 
        collection: filtersActivityData.collection,
        sort_by: sortValue,
        number: numberValue,
      });
    }, 340);
  }, [numberValue]);

  return (
    <div className={Styles.Filters} ref={containerRef}>
      <div className={Styles.FiltersInner}>
        <div className={Styles.FiltersInnerFlexed}>
          <div 
            className={Styles.FiltersInnerSelector}
            onClick={() => toggleDropdown("collection")}
          >
            <div className={cn(Styles.FiltersInnerSelectorLabel, collectionsValue && Styles.Active)}>
              <p>{collectionsValue && collectionsValue.join(", ") || "Collection"}</p>
            </div>
            <div className={cn(Styles.FiltersInnerSelectorChevrone, activeDropdown === "collection" && Styles.Active)}>
              <ChevroneIcon />
            </div>

            <Collection 
              isActive={activeDropdown === "collection"} 
              onToggle={() => toggleDropdown("collection")}
            />
          </div>
        </div>

        <div className={Styles.FiltersInnerFlexed}>
          <div 
            className={Styles.FiltersInnerSelector}
            onClick={() => toggleDropdown("sort")}
          >
            <div className={cn(Styles.FiltersInnerSelectorLabel, sortValue && Styles.Active)}>
              <p>{getNameSortFilter(sortValue)}</p>
            </div>
            <div className={cn(Styles.FiltersInnerSelectorChevrone, activeDropdown === "sort" && Styles.Active)}>
              <ChevroneIcon />
            </div>

            <Sort 
              isActive={activeDropdown === "sort"}
              onToggle={() => toggleDropdown("sort")}
            />
          </div>
        </div>

        <div className={Styles.FiltersInnerFlexed}>
          <div className={Styles.FiltersInnerMultiinput}>
            <div className={Styles.FiltersInnerMultiinputStart}>
              <HashtagIcon />
            </div>
            <div className={Styles.FiltersInnerMultiinputType}>
              <input 
                type="text" 
                placeholder="Search by number" 
                onChange={(e) => setNumberValue(Number(e.target.value))}
                value={numberValue === 0 ? "" : numberValue}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Filters;