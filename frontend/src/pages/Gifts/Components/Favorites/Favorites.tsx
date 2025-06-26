import { FC, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "@/stores/app.store";
import { CloseIcon } from "@/components/Icons";
import { getGiftImage } from "@/utils/gift";

import Styles from "./Favorites.module.scss";
import NotFound from "@/components/NotFound/NotFound";

const Favorites: FC = () => {
  const navigate = useNavigate();

  const { favoritesGifts, setFavoritesGifts } = useAppStore();
  const [removingGiftIds, setRemovingGiftIds] = useState<number[]>([]);

  const handleDeleteGift = (giftId: number) => {
    // запускаем анимацию
    setRemovingGiftIds((prev) => [...prev, giftId]);

    // удаляем после завершения анимации
    setTimeout(() => {
      setFavoritesGifts(favoritesGifts.filter((item: any) => item.id !== giftId));
      setRemovingGiftIds((prev) => prev.filter((id) => id !== giftId));
    }, 300);
  };

  const handleOpenGift = (id: number) => {
    navigate(`/gift/${id}`);
  };

  return (
    <div className={Styles.Favorites}>
      <div className={Styles.FavoritesInner}>

        {favoritesGifts.map((gift: any, index: number) => (
          <div
            key={index}
            className={`${Styles.FavoritesInnerItem} ${removingGiftIds.includes(gift.id) ? Styles.removing : ""}`}
          >
            <div className={Styles.FavoritesInnerItemCover}>
              <div
                className={Styles.FavoritesInnerItemCoverClose}
                onClick={() => handleDeleteGift(gift.id)}
              >
                <CloseIcon />
              </div>
              <div className={Styles.FavoritesInnerItemCoverImage}>
                <img
                  src={getGiftImage(gift.type, gift.number)}
                  alt={gift.model_name}
                />
              </div>
            </div>
            <div className={Styles.FavoritesInnerItemInfo}>
              <div className={Styles.FavoritesInnerItemInfoTitle}>
                <p>{gift.type}</p>
              </div>
              <div className={Styles.FavoritesInnerItemInfoNumber}>
                <p>#{gift.number}</p>
              </div>
            </div>
            <div className={Styles.FavoritesInnerItemButtons}>
              <div className={Styles.FavoritesInnerItemButtonsButton}>
                <button onClick={() => handleOpenGift(gift.gift_id)}>
                  <span>Show gift</span>
                </button>
              </div>
            </div>
          </div>
        ))}

      </div>

      {!favoritesGifts || favoritesGifts.length === 0 && (
        <NotFound title="Favorites gifts not found!" />
      )}
    </div>
  );
};

export default Favorites;