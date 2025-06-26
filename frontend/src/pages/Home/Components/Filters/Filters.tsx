import { FC, useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app.store";
import { ChevroneIcon, HashtagIcon, TonWhiteIcon } from "@/components/Icons";
import { getNameSortFilter } from "@/utils/filter";

import Styles from "./Filters.module.scss";
import Collection from "./Collection/Collection";
import Model from "./Model/Model";
import Sort from "./Sort/Sort";

const Filters: FC = () => {
  const { filtersHomeData, setFiltersHomeData } = useAppStore();
  
  const [activeDropdown, setActiveDropdown] = useState<"collection" | "model" | "sort" | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const [collectionsValue, setCollectionsValue] = useState<any>();
  const [modelsValue, setModelsValue] = useState<any>();
  const [sortValue, setSortValue] = useState<any>("latest");
  const [fromPriceValue, setFromPriceValue] = useState<number>(0);
  const [toPriceValue, setToPriceValue] = useState<number>(0);
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
    setCollectionsValue(filtersHomeData.collection);
    setModelsValue(filtersHomeData.model);
    setSortValue(filtersHomeData.sort_by);
  }, [filtersHomeData]);

  useEffect(() => {
    setTimeout(() => {
      if (fromPriceValue === 0 && toPriceValue === 0 && numberValue === 0) {
        setFiltersHomeData({ 
          collection: filtersHomeData.collection,
          model: filtersHomeData.model,
          sort_by: sortValue,
          from_price: null,
          to_price: null,
          number: null,
        });
        return;
      }

      setFiltersHomeData({ 
        collection: filtersHomeData.collection,
        model: filtersHomeData.model,
        sort_by: sortValue,
        from_price: fromPriceValue,
        to_price: toPriceValue,
        number: numberValue,
      });
    }, 340);
  }, [fromPriceValue, toPriceValue, numberValue]);

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

          <div 
            className={cn(Styles.FiltersInnerSelector, !filtersHomeData.collection || !filtersHomeData.collection.length && Styles.Inactive)}
            onClick={() => toggleDropdown("model")}
          >
            <div className={cn(Styles.FiltersInnerSelectorLabel, modelsValue && Styles.Active)}>
              <p>{modelsValue && modelsValue.join(", ") || "Models"}</p>
            </div>
            <div className={cn(Styles.FiltersInnerSelectorChevrone, activeDropdown === "model" && Styles.Active)}>
              <ChevroneIcon />
            </div>

            <Model 
              isActive={activeDropdown === "model"}
              onToggle={() => toggleDropdown("model")}
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
          <div className={Styles.FiltersInnerInput}>
            <div className={Styles.FiltersInnerInputType}>
              <input 
                type="text" 
                placeholder="Price from" 
                onChange={(e) => setFromPriceValue(Number(e.target.value))}
                value={fromPriceValue === 0 ? "" : fromPriceValue}
              />
            </div>
            <div className={Styles.FiltersInnerInputIcon}>
              <TonWhiteIcon />
            </div>
          </div>
          <div className={Styles.FiltersInnerInput}>
            <div className={Styles.FiltersInnerInputType}>
              <input 
                type="text" 
                placeholder="Price to" 
                onChange={(e) => setToPriceValue(Number(e.target.value))}
                value={toPriceValue === 0 ? "" : toPriceValue}
              />
            </div>
            <div className={Styles.FiltersInnerInputIcon}>
              <TonWhiteIcon />
            </div>
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