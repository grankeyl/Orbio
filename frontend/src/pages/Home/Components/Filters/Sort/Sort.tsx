import { FC, useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app.store";
import { DoneIcon } from "@/components/Icons";

import Styles from "./Sort.module.scss";


interface SortProps {
  isActive: boolean;
  onToggle: () => void;
}

const Sort: FC<SortProps> = ({ isActive, onToggle }) => {
  const { filtersHomeData, setFiltersHomeData } = useAppStore();

  const [sortBy, setSortBy] = useState<string>("latest");

  const handleSortBy = (sortBy: string) => {
    setSortBy(sortBy);
    onToggle();
  };

  useEffect(() => {
    setFiltersHomeData({ 
      collection: filtersHomeData.collection,
      model: filtersHomeData.model,
      sort_by: sortBy,
      from_price: filtersHomeData.from_price,
      to_price: filtersHomeData.to_price,
      number: filtersHomeData.number,
    });
  }, [sortBy]);

  return (
    <div className={cn(Styles.Sort, isActive && Styles.Active)} onClick={onToggle}>
      <div className={Styles.SortInner}>

        <div className={Styles.SortInnerI}>
          <div className={Styles.SortInnerItem} onClick={() => handleSortBy("latest")}>
            <div className={cn(Styles.SortInnerItemSelect, sortBy === "latest" && Styles.Active)}>
              <DoneIcon />
            </div>
            <div className={Styles.SortInnerItemContent}>
              <div className={Styles.SortInnerItemContentInfo}>
                <div className={Styles.SortInnerItemContentInfoTitle}>
                  <p>Latest</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className={Styles.SortInnerItem}>
            <div className={Styles.SortInnerItemBorder}></div>
          </div>
        </div>

        <div className={Styles.SortInnerI}>
          <div className={Styles.SortInnerItem} onClick={() => handleSortBy("price_low_to_high")}>
            <div className={cn(Styles.SortInnerItemSelect, sortBy === "price_low_to_high" && Styles.Active)}>
              <DoneIcon />
            </div>
            <div className={Styles.SortInnerItemContent}>
              <div className={Styles.SortInnerItemContentInfo}>
                <div className={Styles.SortInnerItemContentInfoTitle}>
                  <p>Price, Low to High</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className={Styles.SortInnerItem}>
            <div className={Styles.SortInnerItemBorder}></div>
          </div>
        </div>

        <div className={Styles.SortInnerI}>
          <div className={Styles.SortInnerItem} onClick={() => handleSortBy("price_high_to_low")}>
            <div className={cn(Styles.SortInnerItemSelect, sortBy === "price_high_to_low" && Styles.Active)}>
              <DoneIcon />
            </div>
            <div className={Styles.SortInnerItemContent}>
              <div className={Styles.SortInnerItemContentInfo}>
                <div className={Styles.SortInnerItemContentInfoTitle}>
                  <p>Price, High to Low</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className={Styles.SortInnerItem}>
            <div className={Styles.SortInnerItemBorder}></div>
          </div>
        </div>

        <div className={Styles.SortInnerI}>
          <div className={Styles.SortInnerItem} onClick={() => handleSortBy("random")}>
            <div className={cn(Styles.SortInnerItemSelect, sortBy === "random" && Styles.Active)}>
              <DoneIcon />
            </div>
            <div className={Styles.SortInnerItemContent}>
              <div className={Styles.SortInnerItemContentInfo}>
                <div className={Styles.SortInnerItemContentInfoTitle}>
                  <p>Random</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Sort;