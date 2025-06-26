import { FC, useState } from "react";
import { cn } from "@/lib/utils";
import { CloseIcon, TonWhiteIcon } from "@/components/Icons";
import { checkAmount } from "@/utils/app";
import { showToast } from "@/utils/showToast";
import { useAppStore } from "@/stores/app.store";

import * as userApi from "@/api/services/user.service";

import Styles from "./Withdraw.module.scss";
import { useTonAddress, useTonConnectUI } from "@tonconnect/ui-react";


interface WithdrawProps {
  isActive: boolean;
  onToggle: () => void;
  setModalWithdrawErrorText: (text: string) => void;
}

const Withdraw: FC<WithdrawProps> = ({ isActive, onToggle, setModalWithdrawErrorText }) => {
  const userFriendlyAddress = useTonAddress();

  const { meData } = useAppStore();

  const [tonConnectUI] = useTonConnectUI();
  const [priceValue, setPriceValue] = useState<any>(0.0);

  const fetchWithdraw = async () => {
    const response = await userApi.withdrawBalance({ 
      amount: priceValue, 
      address: userFriendlyAddress
    }) as any;

    if (response.type === "success") {
      return response.data
    }
  }

  const handleWithdraw = async () => {
    if (!userFriendlyAddress) {
      tonConnectUI.openModal();
      showToast("Please connect wallet first!", "error");
      return;
    }

    if (!checkAmount(priceValue)) {
      showToast("Minimum amount is 0.65 TON!", "error");
      return;
    }

    if (meData.balance < priceValue) {
      showToast("You don't have enough balance!", "error");
      return;
    }
  
    const isSuccess = await fetchWithdraw();
    if (!isSuccess) {
      showToast("Something went wrong!", "error");
      return;
    };

    if (isSuccess && isSuccess.withdraw_money_type === "withdraw_error") {
      setModalWithdrawErrorText(isSuccess.withdraw_money_text);
      window.dispatchEvent(new Event("openWithdrawErrorModal"));
      return;
    }

    if (isSuccess && isSuccess.withdraw_money_type === "withdraw_success") {
      showToast(isSuccess.withdraw_money_text, "success");
      meData.balance = meData.balance - priceValue;
      onToggle();
      return;
    }
  };
  
  return (
    <div className={cn(Styles.Withdraw, isActive && Styles.Active)}>
      <div className={Styles.WithdrawClose} onClick={onToggle}>
        <CloseIcon />
      </div>

      <div className={Styles.WithdrawInner}>
        <div className={Styles.WithdrawInnerContent}>
          <h4>Withdraw</h4>
          <p>Specify the amount and withdraw the balance to your wallet</p>
        </div>

        <div className={Styles.WithdrawInnerInput}>
          <div className={Styles.WithdrawInnerInputType}>
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
        
        <div className={Styles.WithdrawInnerButtons}>
          <div className={Styles.WithdrawInnerButtonsButton}>
            <button onClick={onToggle}>
              <span>Close</span>
            </button>
          </div>
          <div className={Styles.WithdrawInnerButtonsButton}>
            <button onClick={handleWithdraw}>
              <span>Withdraw</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Withdraw;