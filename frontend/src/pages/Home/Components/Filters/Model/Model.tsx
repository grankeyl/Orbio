import { FC, useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { getGiftModel } from "@/utils/gift";
import { useAppStore } from "@/stores/app.store";

import Styles from "./Model.module.scss";


interface ModelProps {
  isActive: boolean;
  onToggle: () => void;
}

const Model: FC<ModelProps> = ({ isActive, onToggle }) => {
  const { appGifts, filtersHomeData, setFiltersHomeData } = useAppStore();

  const [models, setModels] = useState<any>([]);
  const [selectedModels, setSelectedModels] = useState<any>([]);

  const handleSelectModel = (name: any) => {
    if (selectedModels.includes(name)) {
      setSelectedModels(selectedModels.filter((item: any) => item !== name));
      return;
    }

    setSelectedModels([...selectedModels, name]);
  };

  const findModelsByName = (names: any) => {
    let result: Record<string, any> = {};

    names.forEach((name: string) => {
      const gift = appGifts.find((item: any) => item.type === name);
      if (gift) {
        result[name] = {
          models: gift.info.models
        };
      }
    });

    setModels(result);
  };

  useEffect(() => {
    if (isActive) return;

    setFiltersHomeData({ 
      collection: filtersHomeData.collection,
      model: selectedModels,
      sort_by: filtersHomeData.sort_by,
      from_price: filtersHomeData.from_price,
      to_price: filtersHomeData.to_price, 
      number: filtersHomeData.number,
    });
  }, [isActive]);

  useEffect(() => {
    if (!filtersHomeData.collection || !filtersHomeData.collection.length) {
      setModels([]);
      return;
    };
    findModelsByName(filtersHomeData.collection);
  }, [filtersHomeData]);
  
  return (
    <div className={cn(Styles.Model, isActive && Styles.Active)} onClick={onToggle}>
      <div className={Styles.ModelInner}>

        {!models || Object.keys(models).length === 0 ? (
          <div className={Styles.ModelInnerEmpty}>
            <p>No models available</p>
          </div>
        ) : (
          Object.entries(models).map(([giftName, giftData]: any) => (
            <div className={Styles.ModelInnerI} key={giftName}>
              <h2 className={Styles.ModelInnerITitle}>{giftName}</h2>

              {!giftData.models || giftData.models.length === 0 ? (
                <div className={Styles.ModelInnerEmpty}>
                  <p>No models available</p>
                </div>
              ) : (
                giftData.models.map((model: any, i: number) => (
                  <div key={i} className={Styles.ModelInnerI}>
                    <div className={Styles.ModelInnerItem} onClick={() => handleSelectModel(model.name)}>
                      <div className={cn(Styles.ModelInnerItemSelect, selectedModels.includes(model.name) && Styles.Active)}>
                        <div className={Styles.ModelInnerItemSelectCircle}></div>
                      </div>
                      <div className={Styles.ModelInnerItemContent}>
                        <div className={Styles.ModelInnerItemContentImage}>
                          <img
                            src={getGiftModel(giftName, model.name)}
                            alt={model.name}
                          />
                        </div>
                        <div className={Styles.ModelInnerItemContentInfo}>
                          <div className={Styles.ModelInnerItemContentInfoTitle}>
                            <p>{model.name}</p>
                          </div>
                        </div>
                      </div>
                      <div className={Styles.ModelInnerItemPercent}>
                        <button>
                          <span>{model.rarity} %</span>
                        </button>
                      </div>
                    </div>

                    <div className={Styles.ModelInnerItem}>
                      <div className={Styles.ModelInnerItemBorder}></div>
                    </div>
                  </div>
                ))
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default Model;