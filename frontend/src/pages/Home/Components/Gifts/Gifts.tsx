import { FC, useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "@/stores/app.store";
import { getGiftImage } from "@/utils/gift";
import { HeartIcon, TonWhiteIcon } from "@/components/Icons";
import { showToast } from "@/utils/showToast";
import { validateBalance } from "@/utils/app";

import Styles from "./Gifts.module.scss";

import LoadingItems from "@/components/LoadingItems/LoadingItems";
// import NotFound from "@/components/NotFound/NotFound";

interface GiftsProps {
  gifts?: any[];
}

const Gifts: FC<GiftsProps> = ({ gifts = [] }) => {
  const navigate = useNavigate();
  const { meData, favoritesGifts, setFavoritesGifts } = useAppStore();

  const [isLoading, setIsLoading] = useState(true);

  const handleFavorite = (gift: any) => {
    const isFavorite = favoritesGifts.find((item: any) => item.id === gift.id);

    if (isFavorite) {
      setFavoritesGifts(favoritesGifts.filter((item: any) => item.id !== gift.id));
      return;
    }

    showToast("Gift added to favorites!", "success");
    setFavoritesGifts([...favoritesGifts, gift]);
  };

  useEffect(() => {
    setTimeout(() => {
      setIsLoading(false);
    }, 300);
  }, [gifts]);

  const handleNavigate = (id: number) => {
    navigate(`/gift/${id}`);
  };

  return (
    <div className={Styles.Gifts}>
      {isLoading && <LoadingItems title="Loading gifts..." />}

      <div className={Styles.GiftsInner}>
        {!isLoading && gifts.length > 0 && (
          gifts.map((gift, i) => (
            <div
              key={i}
              className={Styles.GiftsInnerItem}
            >
              <div className={Styles.GiftsInnerItemCover}>
                {meData.id !== gift.seller_id && (
                  <div 
                    onClick={() => handleFavorite(gift)}
                    className={cn(
                      Styles.GiftsInnerItemCoverLike,
                      favoritesGifts.find((item: any) => item.id === gift.id) && Styles.Active
                    )} >
                    <HeartIcon />
                  </div>
                )}
                <div className={Styles.GiftsInnerItemCoverImage} onClick={() => handleNavigate(gift.id)}>
                  <img src={getGiftImage(gift.type, gift.number)} alt="" />
                </div>
              </div>
              <div className={Styles.GiftsInnerItemInfo} onClick={() => handleNavigate(gift.id)}>
                <div className={Styles.GiftsInnerItemInfoTitle}>
                  <p>{gift.type}</p>
                </div>
                <div className={Styles.GiftsInnerItemInfoNumber}>
                  <p>#{gift.number}</p>
                </div>
              </div>
              <div className={Styles.GiftsInnerItemButtons} onClick={() => handleNavigate(gift.id)}>
                <div className={Styles.GiftsInnerItemButtonsButton}>
                  <button>
                    <span>{validateBalance(gift.price)}</span>
                    <TonWhiteIcon />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* {!isLoading && gifts.length === 0 && <NotFound title="Gifts not found!" />} */}
      {!isLoading && gifts.length === 0 && <LoadingItems title="Loading gifts..." />}
    </div>
  );
};

export default Gifts;