import { FC, useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app.store";
import { copyToClipboard } from "@/utils/copyToClipboard";
import { AddIcon, ChevroneIcon, CopyIcon, RemoveIcon, ShareIcon, TonWhiteIcon } from "@/components/Icons";
import { showToast } from "@/utils/showToast";
import { useTonAddress, useTonConnectUI } from "@tonconnect/ui-react";
import { shortenString, validateBalance } from "@/utils/app";
import { TelegramModule } from "@/hooks/telegram";

import Styles from "./Profile.module.scss";

import DisconnectModal from "./Components/Disconnect/Disconnect";
import FriendsComponent from "./Components/Friends/Friends";
import WithdrawModal from "./Components/Withdraw/Withdraw";
import WithdrawErrorModal from "./Components/Withdraw/Error/Error";
import DepositModal from "./Components/Deposit/Deposit";

const Profile: FC = () => {
  const userFriendlyAddress = useTonAddress();

  const { meData } = useAppStore();

  const [tonConnectUI] = useTonConnectUI();
  const [activeDropdown, setActiveDropdown] = useState<"disconnect" | "witdraw" | "withdraw-error" | "deposit" | null>(null);
  const [modalWithdrawErrorText, setModalWithdrawErrorText] = useState<string>("");
  const [isCopyLink, setIsCopyLink] = useState(false);

  const handleOpenDisconnect = () => {
    if (activeDropdown === "disconnect") {
      setActiveDropdown(null);
      return;
    };
    setActiveDropdown("disconnect");
  };

  const handleOpenWithdraw = () => setActiveDropdown("witdraw");
  const handleOpenWithdrawError = () => setActiveDropdown("withdraw-error");
  const handleOpenDeposit = () => setActiveDropdown("deposit");

  useEffect(() => {
    window.addEventListener("openDisconnectModal", handleOpenDisconnect);
    window.addEventListener("openWithdrawModal", handleOpenWithdraw);
    window.addEventListener("openWithdrawErrorModal", handleOpenWithdrawError);
    window.addEventListener("openDepositModal", handleOpenDeposit);

    return () => {
      window.removeEventListener("openDisconnectModal", handleOpenDisconnect);
      window.removeEventListener("openWithdrawModal", handleOpenWithdraw);
      window.removeEventListener("openWithdrawErrorModal", handleOpenWithdrawError);
      window.removeEventListener("openDepositModal", handleOpenDeposit);
    };
  }, []);

  const handleCloseModals = () => {
    setActiveDropdown(null);
  };

  const handleConnectWallet = () => {
    tonConnectUI.openModal();
  }

  const handleWithdraw = () => {
    if (!userFriendlyAddress) {
      showToast("Please connect wallet first!", "error");
      return;
    }

    handleOpenWithdraw();
  }

  const handleDeposit = () => {
    if (!userFriendlyAddress) {
      showToast("Please connect wallet first!", "error");
      return;
    }

    handleOpenDeposit();
  }

  const handleCopyLink = (link: string) => {
    const copy = copyToClipboard(link);
    if (!copy) return;

    setIsCopyLink(true);
    showToast("Link copied to clipboard!", "success");
    setTimeout(() => setIsCopyLink(false), 1900);
  }

  const handleShareReferral = (url: string) => {
    TelegramModule.useSendMessage(
      url,
      "This is the place to get and sell gifts! Check it out!"
    );
  }

  return (
    <div className={Styles.Profile}>
      <main>
        <div className={Styles.ProfileInner}>
          
          <div className={Styles.ProfileInnerUser}>
            <div className={Styles.ProfileInnerUserImage}>
              <img src={meData.photo_url} alt="" />
            </div>
            <div className={Styles.ProfileInnerUserName}>
              <h4>{meData.first_name}</h4>
            </div>
            {!userFriendlyAddress ? (
              <div className={Styles.ProfileInnerUserWallet} onClick={handleConnectWallet}>
                <button>
                  <span>Connect wallet</span>
                </button>
              </div>
            ) : (
              <div className={cn(Styles.ProfileInnerUserWallet, Styles.ProfileInnerUserWalletConnected)}>
                <button onClick={handleOpenDisconnect}>
                  <span>{shortenString(userFriendlyAddress)}</span>
                  <ChevroneIcon />
                </button>

                {activeDropdown === "disconnect" && (
                  <DisconnectModal isActive={activeDropdown === "disconnect"} onToggle={handleCloseModals} />
                )}
              </div>
            )}
            <div className={Styles.ProfileInnerUserBalance}>
              <div className={Styles.ProfileInnerUserBalanceAmount}>
                <p>{validateBalance(meData.balance)}</p>
                <TonWhiteIcon />
              </div>
              <div className={Styles.ProfileInnerUserBalanceButtons}>
                <div className={Styles.ProfileInnerUserBalanceButtonsButton}>
                  <button onClick={handleWithdraw}>
                    <RemoveIcon />
                  </button>
                </div>
                <div className={Styles.ProfileInnerUserBalanceButtonsButton}>
                  <button onClick={handleDeposit}>
                    <AddIcon />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className={Styles.ProfileInnerReferral}>
            <div className={Styles.ProfileInnerReferralInner}>
              <div className={Styles.ProfileInnerReferralInnerContent}>
                <h4>Earn TON</h4>
                <p>Invite your friends and earn a TON</p>
              </div>

              <div className={Styles.ProfileInnerReferralInnerInput}>
                <p>{meData.referral_link}</p>
              </div>
              
              <div className={Styles.ProfileInnerReferralInnerButtons}>
                <div 
                  onClick={() => handleCopyLink(meData.referral_link)}
                  className={cn(
                    Styles.ProfileInnerReferralInnerButtonsButton,
                    isCopyLink && Styles.CopyActive
                  )} 
                >
                  <button>
                    <span>{isCopyLink ? "Copied!" : "Copy link"}</span>
                    <CopyIcon />
                  </button>
                </div>
                <div 
                  onClick={() => handleShareReferral(meData.referral_link)}
                  className={Styles.ProfileInnerReferralInnerButtonsButton}
                >
                  <button>
                    <span>Share</span>
                    <ShareIcon />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <FriendsComponent />

        </div>

        <WithdrawModal
          isActive={activeDropdown === "witdraw"}
          onToggle={handleCloseModals}
          setModalWithdrawErrorText={setModalWithdrawErrorText}
        />

        <WithdrawErrorModal
          isActive={activeDropdown === "withdraw-error"}
          onToggle={handleCloseModals}
          text={modalWithdrawErrorText}
        />

        <DepositModal
          isActive={activeDropdown === "deposit"}
          onToggle={handleCloseModals}
        />

        <div className={cn(Styles.Overlay, activeDropdown && activeDropdown !== "disconnect" && Styles.Active)} onClick={handleCloseModals} />
      </main>
    </div>
  )
}

export default Profile;