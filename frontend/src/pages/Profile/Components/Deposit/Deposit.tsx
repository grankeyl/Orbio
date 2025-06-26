import { FC, useState } from "react";
import { cn } from "@/lib/utils";
import { CloseIcon, TonWhiteIcon } from "@/components/Icons";
import { checkAmount } from "@/utils/app";
import { showToast } from "@/utils/showToast";
import { useTonAddress, useTonConnectUI } from "@tonconnect/ui-react";
import { beginCell, toNano } from 'ton-core';
import { useAppStore } from "@/stores/app.store";

import Styles from "./Deposit.module.scss";


interface DepositProps {
  isActive: boolean;
  onToggle: () => void;
}

const Deposit: FC<DepositProps> = ({ isActive, onToggle }) => {
  const userFriendlyAddress = useTonAddress();

  const { appVariables, meData } = useAppStore();
  
  const [tonConnectUI] = useTonConnectUI();
  const [depositPriceValue, setDepositPriceValue] = useState<any>(0.0);

  const sendPayment = async () => {
    const wallets = await tonConnectUI.getWallets();
    if (!wallets.length) return;
  
    const numericAmount = parseFloat(depositPriceValue);
    if (!numericAmount || !userFriendlyAddress) return;

    const nanotonAmount = toNano(numericAmount).toString();
    const depositComment = meData?.deposit_comment ?? "";

    let body = beginCell()
      .storeUint(0, 32)
      .storeStringTail(`${depositComment}`)
      .endCell();

    const response = await tonConnectUI.sendTransaction({
      validUntil: Math.floor(Date.now() / 1000) + 60,
      messages: [
        {
            address: appVariables.wallet,
            amount: nanotonAmount,
            payload: body.toBoc().toString('base64')
        },
      ],
    });
  
    if (response && response.boc) {
      showToast("Deposit received, balance will be updated within 5 minutes", "success");
      return true;
    }
  };

  const handleDeposit = async () => {
    if (!checkAmount(depositPriceValue)) {
      showToast("Minimum amount is 0.65 TON!", "error");
      return;
    }

    const isSuccess = await sendPayment();
    if (!isSuccess) {
      showToast("Something went wrong!", "error");
      return;
    };
    
    // payment success

    onToggle();
  }

  return (
    <div className={cn(Styles.Deposit, isActive && Styles.Active)}>
      <div className={Styles.DepositClose} onClick={onToggle}>
        <CloseIcon />
      </div>

      <div className={Styles.DepositInner}>
        <div className={Styles.DepositInnerContent}>
          <h4>Deposit</h4>
          <p>Specify the amount and top up your balance</p>
        </div>

        <div className={Styles.DepositInnerInput}>
          <div className={Styles.DepositInnerInputType}>
            <input 
              type="text"
              inputMode="decimal"
              step="0.01"
              placeholder="0.0" 
              value={depositPriceValue}
              onChange={(e) => {
                const raw = e.target.value;
                if (/^[0-9]*\.?[0-9]*$/.test(raw)) {
                  setDepositPriceValue(raw);
                }
              }}
            />
          </div>
          <TonWhiteIcon />
        </div>
        
        <div className={Styles.DepositInnerButtons}>
          <div className={Styles.DepositInnerButtonsButton}>
            <button onClick={onToggle}>
              <span>Close</span>
            </button>
          </div>
          <div className={Styles.DepositInnerButtonsButton}>
            <button onClick={handleDeposit}>
              <span>Deposit</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Deposit;