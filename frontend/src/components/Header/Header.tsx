import { FC, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { shortenString, validateBalance } from "@/utils/app";
import { useLocation, useNavigate } from "react-router-dom";
import { useAppStore } from "@/stores/app.store";
import { ChevroneIcon, TonWhiteIcon } from "@/components/Icons";
import { useTonAddress, useTonConnectUI } from "@tonconnect/ui-react";

import Style from "./Header.module.scss";

import DisconnectModal from "./Components/Disconnect/Disconnect";

const Header: FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const userFriendlyAddress = useTonAddress();

  const { meData } = useAppStore();

  const [tonConnectUI] = useTonConnectUI();
  const [activeDropdown, setActiveDropdown] = useState<"disconnect" | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const toggleDropdown = (key: "disconnect") => {
    setActiveDropdown((prev) => (prev === key ? null : key));
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setActiveDropdown(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  if (location.pathname === "/profile") return null;

  const handleConnectWallet = () => {
    tonConnectUI.openModal();
  }

  return (
    <div className={Style.Header}>
      <div className={Style.HeaderInner}>

        <div className={Style.HeaderInnerImage} onClick={() => navigate("/profile")}>
          <img src={meData.photo_url} alt="" />
        </div>

        {!userFriendlyAddress ? (
          <div className={Style.HeaderInnerWallet} onClick={handleConnectWallet}>
            <button>
              <span>Connect wallet</span>
            </button>
          </div>
        ) : (
          <div className={cn(Style.HeaderInnerWallet, Style.HeaderInnerWalletConnected)} onClick={() => toggleDropdown("disconnect")}>
            <button>
              <span>{shortenString(userFriendlyAddress)}</span>
              <ChevroneIcon />
            </button>

            <DisconnectModal 
              isActive={activeDropdown === "disconnect"} 
              onToggle={() => toggleDropdown("disconnect")}
            />
          </div>
        )}

        <div className={Style.HeaderInnerBalance} onClick={() => navigate("/profile")}>
          <button>
            <span>{validateBalance(meData.balance)}</span>
            <TonWhiteIcon />
          </button>
        </div>

      </div>
    </div>
  );
};

export default Header;