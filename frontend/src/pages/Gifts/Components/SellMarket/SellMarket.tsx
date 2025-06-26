import { FC, useState } from "react";
import { cn } from "@/lib/utils";
import { CloseIcon, TonWhiteIcon } from "@/components/Icons";
import { showToast } from "@/utils/showToast";
import { checkAmount } from "@/utils/app";

import * as userApi from "@/api/services/user.service";

import Styles from "./SellMarket.module.scss";


interface SellMarketProps {
  isActive: boolean;
  onToggle: () => void;
  selectedGift: any;
  removeGift: (id: number) => void;
}


const SellMarket: FC<SellMarketProps> = ({ isActive, onToggle, selectedGift, removeGift }) => {
  const [priceValue, setPriceValue] = useState<any>(0.0);

  const fetchSellGift = async () => {
      const response = await userApi.sellGift({ 
        gift_id: selectedGift.id,
        price: priceValue
      }) as any;
      
      if (response.type === "success") {
        removeGift(selectedGift.id);
        return true
      }
  }

  const handleSell = () => {
    if (!checkAmount(priceValue)) {
      showToast("Minimum amount is 0.65 TON!", "error");
      return;
    }

    const isSuccess = fetchSellGift();
    if (!isSuccess) {
      showToast("Something went wrong!", "error");
      return;
    };

    showToast("The gift is now on the marketplace!", "success");
    setPriceValue(0.0);
    onToggle();
  }

  return (
    <div className={cn(Styles.SellMarket, isActive && Styles.Active)}>
      <div className={Styles.SellMarketClose} onClick={onToggle}>
        <CloseIcon />
      </div>

      <div className={Styles.SellMarketInner}>
        <div className={Styles.SellMarketInnerContent}>
          <h4>Sell on the market</h4>
          <p>Enter the amount for which you want to give the gift</p>
        </div>

        <div className={Styles.SellMarketInnerInput}>
          <div className={Styles.SellMarketInnerInputType}>
            <input 
              type="text"
              inputMode="decimal"
              step="0.01"
              placeholder="0.0" 
              value={priceValue}
              onChange={(e) => {
                const raw = e.target.value;
                if (/^[0-9]*\.?[0-9]*$/.test(raw)) {
                  setPriceValue(raw);
                }
              }}
            />
          </div>
          <TonWhiteIcon />
        </div>
        
        <div className={Styles.SellMarketInnerButtons}>
          <div className={Styles.SellMarketInnerButtonsButton}>
            <button onClick={onToggle}>
              <span>Close</span>
            </button>
          </div>
          <div className={Styles.SellMarketInnerButtonsButton} onClick={handleSell}>
            <button>
              <span>Expose</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default SellMarket;