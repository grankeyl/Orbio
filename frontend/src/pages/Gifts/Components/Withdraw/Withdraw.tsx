import { FC } from "react";
import { cn } from "@/lib/utils";
import { CloseIcon } from "@/components/Icons";
import { showToast } from "@/utils/showToast";

import * as userApi from "@/api/services/user.service";

import Styles from "./Withdraw.module.scss";


interface WithdrawProps {
  isActive: boolean;
  onToggle: () => void;
  selectedGift: any;
  removeGiftUnlisted: (id: number) => void;
  setModalWithdrawErrorText: (text: string) => void;
}


const Withdraw: FC<WithdrawProps> = ({ isActive, onToggle, selectedGift, removeGiftUnlisted, setModalWithdrawErrorText }) => {
  const fetchWithdrawGift = async (id: number) => {
    const response = await userApi.withdrawGift({ id: id }) as any;
    
    if (response.type === "success") {
      return response.data
    }
  }

  const handleWithdraw = async (id: number) => {
    const isSuccess = await fetchWithdrawGift(id) as any;
    if (!isSuccess) {
      showToast("Something went wrong!", "error");
      return;
    };

    if (isSuccess && isSuccess.withdraw_gift_type === "withdraw_error") {
      setModalWithdrawErrorText(isSuccess.withdraw_gift_text);
      window.dispatchEvent(new Event("openWithdrawErrorModal"));
      return;
    }

    if (isSuccess && isSuccess.withdraw_gift_type === "withdraw_success") {
      showToast(isSuccess.withdraw_gift_text, "success");
      removeGiftUnlisted(selectedGift.id);
      onToggle();
      return;
    }
  }

  return (
    <div className={cn(Styles.Withdraw, isActive && Styles.Active)}>
      <div className={Styles.WithdrawClose} onClick={onToggle}>
        <CloseIcon />
      </div>

      <div className={Styles.WithdrawInner}>
        <div className={Styles.WithdrawInnerContent}>
          <h4>Are you sure?</h4>
          <p>Confirm your action when withdrawing your gift</p>
        </div>

        <div className={Styles.WithdrawInnerButtons}>
          <div className={Styles.WithdrawInnerButtonsButton}>
            <button onClick={onToggle}>
              <span>No, exit</span>
            </button>
          </div>
          <div className={Styles.WithdrawInnerButtonsButton}>
            <button onClick={() => handleWithdraw(selectedGift.id)}>
              <span>Yes, withdraw</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Withdraw;