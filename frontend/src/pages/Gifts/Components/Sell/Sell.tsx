import { FC } from "react";
import { cn } from "@/lib/utils";
import { CloseIcon, TonWhiteIcon } from "@/components/Icons";
import { getGiftImage } from "@/utils/gift";
import { useAppStore } from "@/stores/app.store";
import { validateBalance } from "@/utils/app";

import Styles from "./Sell.module.scss";


interface SellProps {
  isActive: boolean;
  onToggle: () => void;
  selectedGift: any;
}

const Sell: FC<SellProps> = ({ isActive, onToggle, selectedGift }) => {
  const { appGifts } = useAppStore();

  const handleOpenSellMarket = () => {
    window.dispatchEvent(new Event("openSellMarketModal"));
  };

  if (!selectedGift) return;

  const getQuickSellPrice = () => {
    if (!appGifts || appGifts.length === 0) return;
    
    const floor = appGifts.find((item: any) => item.type === selectedGift.type);
    if (!floor) return;

    const quickPrice = floor.floor * 1.2;
    return validateBalance(quickPrice);
  };

  return (
    <div className={cn(Styles.Sell, isActive && Styles.Active)}>
      <div className={Styles.SellClose} onClick={onToggle}>
        <CloseIcon />
      </div>

      <div className={Styles.SellInner}>
        
        <div className={Styles.SellInnerCover}>
          <div className={Styles.SellInnerCoverImage}>
            <img src={getGiftImage(selectedGift.type, selectedGift.number)} alt="" />
          </div>
        </div>

        <div className={Styles.SellInnerContent}>
          <div className={Styles.SellInnerContentInfo}>
            <div className={Styles.SellInnerContentInfoTitle}>
              <p>{selectedGift.type}</p>
            </div>
            <div className={Styles.SellInnerContentInfoNumber}>
              <p>#{selectedGift.number}</p>
            </div>
          </div>
        </div>

        <div className={Styles.SellInnerButtons}>
          <div className={Styles.SellInnerButtonsButton}>
            <button onClick={handleOpenSellMarket}>
              <span>Sell on the market</span>
            </button>
          </div>
          <div className={Styles.SellInnerButtonsButton}>
            <button>
              <span>Quick Sell for {getQuickSellPrice()}</span>
              <TonWhiteIcon />
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Sell;