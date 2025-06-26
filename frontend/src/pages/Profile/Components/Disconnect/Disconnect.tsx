import { FC } from "react";
import { cn } from "@/lib/utils";
import { useTonAddress, useTonConnectUI } from "@tonconnect/ui-react";
import { copyToClipboard } from "@/utils/copyToClipboard";
import { showToast } from "@/utils/showToast";

import Styles from "./Disconnect.module.scss";


interface DisconnectProps {
  isActive: boolean;
  onToggle: () => void;
}

const Disconnect: FC<DisconnectProps> = ({ isActive, onToggle }) => {
  const userFriendlyAddress = useTonAddress();

  const [tonConnectUI] = useTonConnectUI();

  const handleCopyLink = () => {
    const copy = copyToClipboard(userFriendlyAddress);
    if (!copy) return;

    showToast("Address copied to clipboard!", "success");
    onToggle();
  }

  const handleDisconnect = () => {
    tonConnectUI.disconnect();
    onToggle();
  }

  return (
    <div className={cn(Styles.Disconnect, isActive && Styles.Active)}>
      <div className={Styles.DisconnectInner}>

        <div className={Styles.DisconnectInnerI} onClick={handleCopyLink}>
          <div className={Styles.DisconnectInnerItem}>
            <div className={Styles.DisconnectInnerItemContent}>
              <div className={Styles.DisconnectInnerItemContentInfo}>
                <div className={Styles.DisconnectInnerItemContentInfoTitle}>
                  <p>Copy address</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className={Styles.DisconnectInnerItem}>
            <div className={Styles.DisconnectInnerItemBorder}></div>
          </div>
        </div>

        <div className={Styles.DisconnectInnerI} onClick={handleDisconnect}>
          <div className={Styles.DisconnectInnerItem}>
            <div className={Styles.DisconnectInnerItemContent}>
              <div className={Styles.DisconnectInnerItemContentInfo}>
                <div className={Styles.DisconnectInnerItemContentInfoTitle}>
                  <p>Disconnect wallet</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Disconnect;