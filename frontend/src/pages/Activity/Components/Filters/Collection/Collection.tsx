import { FC, useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app.store";
import { getGiftModel } from "@/utils/gift";

import Styles from "./Collection.module.scss";


interface CollectionProps {
  isActive: boolean;
  onToggle: () => void;
}

const Collection: FC<CollectionProps> = ({ isActive, onToggle }) => {
  const { appGifts, filtersActivityData, setFiltersActivityData } = useAppStore();

  const [selectedCollections, setSelectedCollections] = useState<any>([]);

  const handleSelectCollection = (name: any) => {
    if (selectedCollections.includes(name)) {
      setSelectedCollections(selectedCollections.filter((item: any) => item !== name));
      return;
    }

    setSelectedCollections([...selectedCollections, name]);
  };

  useEffect(() => {
    if (isActive) return;

    setFiltersActivityData({ 
      collection: selectedCollections,
      sort_by: filtersActivityData.sort_by,
      number: filtersActivityData.number,
    });
  }, [isActive]);

  return (
    <div className={cn(Styles.Collection, isActive && Styles.Active)} onClick={onToggle}>
      <div className={Styles.CollectionInner}>

        {appGifts.map((giftItem: any, index: number) => (
          <div key={index} className={Styles.CollectionInnerI}>
            <div className={Styles.CollectionInnerItem} onClick={() => handleSelectCollection(giftItem.info.gift.name)}>
              <div className={cn(Styles.CollectionInnerItemSelect, selectedCollections.includes(giftItem.info.gift.name) && Styles.Active)}>
                <div className={Styles.CollectionInnerItemSelectCircle}></div>
              </div>
              <div className={Styles.CollectionInnerItemContent}>
                <div className={Styles.CollectionInnerItemContentImage}>
                  <img
                    src={getGiftModel(giftItem.info.gift.name, giftItem.info.models?.[0]?.name || "")}
                    alt=""
                  />
                </div>
                <div className={Styles.CollectionInnerItemContentInfo}>
                  <div className={Styles.CollectionInnerItemContentInfoTitle}>
                    <p>{giftItem.info.gift.name}</p> {/* Название подарка */}
                  </div>
                  <div className={Styles.CollectionInnerItemContentInfoModels}>
                    <p>{giftItem.info.models.length + " models" || "No models"}</p> {/* Название первой модели */}
                  </div>
                </div>
              </div>
              <div className={Styles.CollectionInnerItemFloor}>
              </div>
            </div>

            <div className={Styles.CollectionInnerItem}>
              <div className={Styles.CollectionInnerItemBorder}></div>
            </div>
          </div>
        ))}

      </div>
    </div>
  )
}

export default Collection;