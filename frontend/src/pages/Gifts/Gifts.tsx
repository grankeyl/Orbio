import { FC, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

import * as userApi from "@/api/services/user.service";

import Styles from "./Gifts.module.scss";
import GiftsComponent from "./Components/Gifts/Gifts";
import FavoritesComponent from "./Components/Favorites/Favorites";

import AddGiftModal from "./Components/AddGift/AddGift";
import SellModal from "./Components/Sell/Sell";
import SellMarketModal from "./Components/SellMarket/SellMarket";
import WithdrawConfirmationModal from "./Components/Withdraw/Withdraw";
import WithdrawErrorModal from "./Components/Withdraw/Error/Error";

const Gifts: FC = () => {
  const giftsUnlistedObserverRef = useRef<HTMLDivElement | null>(null);
  const giftsListedObserverRef = useRef<HTMLDivElement | null>(null);
    
  const [isLoadingUnlisted, setIsLoadingUnlisted] = useState(false);
  const [isLoadingListed, setIsLoadingListed] = useState(false);

  const [giftsUnlisted, setGiftsUnlisted] = useState<any[]>([]);
  const [giftsUnlistedOffset, setGiftsUnlistedOffset] = useState(0);
  const [giftsUnlistedHasMore, setGiftsUnlistedHasMore] = useState(true);

  const [giftsListed, setGiftsListed] = useState<any[]>([]);
  const [giftsListedOffset, setGiftsListedOffset] = useState(0);
  const [giftsListedHasMore, setGiftsListedHasMore] = useState(true);

  const [activePage, setActivePage] = useState<"gifts" | "favorites" | null>("gifts");
  const [activeSection, setActiveSection] = useState<"unlisted" | "listed" | any>("unlisted");
  const [activeDropdown, setActiveDropdown] = useState<"add-gift" | "sell" | "sell-market" | "withdraw-confirmation" | "withdraw-error" | null>(null);
  const [modalWithdrawErrorText, setModalWithdrawErrorText] = useState<string>("");
  
  const [selectedGift, setSelectedGift] = useState<any>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  const handleOpenAddGift = () => setActiveDropdown("add-gift");
  const handleOpenSell = () => setActiveDropdown("sell");
  const handleOpenSellMarket = () => setActiveDropdown("sell-market");
  const handleOpenWithdrawConfirmation = () => setActiveDropdown("withdraw-confirmation")
  const handleOpenWithdrawError = () => setActiveDropdown("withdraw-error")

  useEffect(() => {
    window.addEventListener("openAddGiftModal", handleOpenAddGift);
    window.addEventListener("openSellModal", handleOpenSell);
    window.addEventListener("openSellMarketModal", handleOpenSellMarket);
    window.addEventListener("openWithdrawConfirmationModal", handleOpenWithdrawConfirmation);
    window.addEventListener("openWithdrawErrorModal", handleOpenWithdrawError);

    return () => {
      window.removeEventListener("openAddGiftModal", handleOpenAddGift);
      window.removeEventListener("openSellModal", handleOpenSell);
      window.removeEventListener("openSellMarketModal", handleOpenSellMarket);
      window.removeEventListener("openWithdrawConfirmationModal", handleOpenWithdrawConfirmation);
      window.removeEventListener("openWithdrawErrorModal", handleOpenWithdrawError);
    };
  }, []);

  const handleCloseModals = () => setActiveDropdown(null);

  const fetchUnlistedGifts = async (newOffset = 0, append = false) => {
    if (!append) setIsLoadingUnlisted(true);

    const response = await userApi.getGifts({ 
      limit: 20, 
      offset: newOffset, 
      for_sell: 1
    }) as any;

    if (response.type === "success") {
      const data = response.data;
      if (data.length < 20) setGiftsUnlistedHasMore(false);
      setGiftsUnlisted(prev => append ? [...prev, ...data] : data);
      setGiftsUnlistedOffset(prev => append ? prev + 20 : 20);
    }

    if (!append) setIsLoadingUnlisted(false);
  };

  const fetchListedGifts = async (newOffset = 0, append = false) => {
    if (!append) setIsLoadingListed(true);

    const response = await userApi.getGifts({ 
      limit: 20, 
      offset: newOffset, 
      for_sell: 0
    }) as any;

    if (response.type === "success") {
      const data = response.data;
      if (data.length < 20) setGiftsListedHasMore(false);
      setGiftsListed(prev => append ? [...prev, ...data] : data);
      setGiftsListedOffset(append ? newOffset + 20 : 20);
    }

    if (!append) setIsLoadingListed(false);
  };

  const handleRemoveUnlistedGift = async (id: number) => {
    setGiftsUnlisted((prev: any) => prev.filter((gift: any) => gift.id !== id));
  };

  const handleRemoveListedGift = (id: any) => {
    setGiftsListed((prev: any) => prev.filter((gift: any) => gift.id !== id));
  };

  const handleSetSection = (section: "unlisted" | "listed") => {
    setActiveSection(section);

    if (section === "unlisted") {
      setGiftsUnlisted([]);
      setGiftsUnlistedOffset(0);
      setGiftsUnlistedHasMore(true);
      fetchUnlistedGifts(0, false);
    }

    if (section === "listed") {
      setGiftsListed([]);
      setGiftsListedOffset(0);
      setGiftsListedHasMore(true);
      fetchListedGifts(0, false);
    }
  };

  useEffect(() => {
    if (!giftsUnlistedObserverRef.current || !giftsUnlistedHasMore || activeSection !== "unlisted" || isLoadingUnlisted) return;

    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && giftsUnlistedHasMore) {
        fetchUnlistedGifts(giftsUnlistedOffset, true);
      }
    });

    observer.observe(giftsUnlistedObserverRef.current);
    return () => observer.disconnect();
  }, [giftsUnlistedOffset, giftsUnlistedHasMore, giftsUnlisted, activeSection, isLoadingUnlisted]);

  useEffect(() => {
    if (!giftsListedObserverRef.current || !giftsListedHasMore || activeSection !== "listed" || isLoadingListed) return;

    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && giftsListedHasMore) {
        fetchListedGifts(giftsListedOffset, true);
      }
    });

    observer.observe(giftsListedObserverRef.current);
    return () => observer.disconnect();
  }, [giftsListedOffset, giftsListedHasMore, giftsListed, activeSection, isLoadingListed]);

  return (
    <div className={Styles.Gifts} ref={containerRef}>
      <main>
        <div className={Styles.GiftsInner}>
          <div className={Styles.GiftsInnerPage}>
            <div 
              onClick={() => setActivePage("gifts")}
              className={cn(
                Styles.GiftsInnerPageItem, 
                activePage === "gifts" && Styles.Active
                )}
              >
              <h4>My gifts</h4>
            </div>
            <div 
              onClick={() => setActivePage("favorites")}
              className={cn(
                Styles.GiftsInnerPageItem, 
                activePage === "favorites" && Styles.Active
                )}
              >
              <h4>Favorites</h4>
            </div>
          </div>

          {activePage === "gifts" && (
            <>
              <div className={Styles.GiftsInnerSections}>
                <div 
                  onClick={() => handleSetSection("unlisted")}
                  className={cn(
                    Styles.GiftsInnerSectionsItem, 
                    activeSection === "unlisted" && Styles.Active
                  )}
                >
                  <h4>Unlisted</h4>
                  <span>{giftsUnlisted.length}</span>
                </div>
                <div 
                  onClick={() => handleSetSection("listed")}
                  className={cn(
                    Styles.GiftsInnerSectionsItem, 
                    activeSection === "listed" && Styles.Active
                  )}
                >
                  <h4>Listed</h4>
                  <span>{giftsListed.length}</span>
                </div>
              </div>

              <div className={Styles.GiftsInnerAddGift} onClick={handleOpenAddGift}>
                <div className={Styles.GiftsInnerAddGiftBg}></div>
                <div className={Styles.GiftsInnerAddGiftLeft}>
                  <h4>Add gift</h4>
                  <button>
                    <span>Deposit gift</span>
                  </button>
                </div>
                <div className={Styles.GiftsInnerAddGiftRight}>
                  <img src="/gifts-photos/addgift-el.png" alt="el" />
                </div>
              </div>

              <GiftsComponent 
                section={activeSection}
                unlistedGifts={giftsUnlisted}
                listedGifts={giftsListed}
                onSelectGift={setSelectedGift}
                removeGift={handleRemoveListedGift}
              />
              {giftsUnlisted && <div ref={giftsUnlistedObserverRef} style={{ height: 1 }} />}
              {giftsListed && <div ref={giftsListedObserverRef} style={{ height: 1 }} />}
            </>
          )}

          {activePage === "favorites" && (
            <FavoritesComponent />
          )}

        </div>

        <AddGiftModal
          isActive={activeDropdown === "add-gift"}
          onToggle={handleCloseModals}
        />

        <SellModal
          isActive={activeDropdown === "sell"}
          onToggle={handleCloseModals}
          selectedGift={selectedGift}
        />

        <SellMarketModal
          isActive={activeDropdown === "sell-market"}
          onToggle={handleCloseModals}
          selectedGift={selectedGift}
          removeGift={handleRemoveUnlistedGift}
        />

        <WithdrawConfirmationModal
          isActive={activeDropdown === "withdraw-confirmation"}
          onToggle={handleCloseModals}
          selectedGift={selectedGift}
          removeGiftUnlisted={handleRemoveUnlistedGift}
          setModalWithdrawErrorText={setModalWithdrawErrorText}
        />

        <WithdrawErrorModal
          isActive={activeDropdown === "withdraw-error"}
          onToggle={handleCloseModals}
          text={modalWithdrawErrorText}
        />
        
        <div className={cn(Styles.Overlay, activeDropdown && Styles.Active)} onClick={handleCloseModals} />
      </main>
    </div>
  );
};

export default Gifts;