import { FC, useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app.store";
import { HeartIcon, ShareIcon, TonWhiteIcon } from "@/components/Icons";
import { useNavigate, useParams } from "react-router-dom";
import { TelegramModule } from "@/hooks/telegram";
import { getGiftLottie } from "@/utils/gift";
import { showToast } from "@/utils/showToast";

import * as marketApi from "@/api/services/market.service";

import Lottie from "lottie-react";
import Styles from "./Gift.module.scss";
import Loader from "@/components/Loader/Loader";
import { validateBalance } from "@/utils/app";


const Gift: FC = () => {
  const navigate = useNavigate();

  const { id } = useParams<{ id: string }>();
  const { meData, favoritesGifts, setFavoritesGifts, setMeData } = useAppStore();

  const [gift, setGift] = useState<any>(null);
  const [animationData, setAnimationData] = useState<any>(null);

  const handleFavorite = (gift: any) => {
    const isFavorite = favoritesGifts.find((item: any) => item.id === gift.id);
    if (isFavorite) {
      setFavoritesGifts(favoritesGifts.filter((item: any) => item.id !== gift.id));
      return;
    }
    setFavoritesGifts([...favoritesGifts, gift]);
  };

  const fetchGifts = async () => {
    const response = await marketApi.giftGetById(Number(id)) as any;
    if (response.type === "success" && response.data) {
      const data = response.data;

      if (data && data.is_active === false) {
        navigate("/");
      }

      setGift(data);

      const lottieUrl = getGiftLottie(data.type, data.number);
      const json = await fetch(lottieUrl).then((res) => res.json());
      setAnimationData(json);
    }
  };

  const fetchBuy = async (id: number) => {
    const response = await marketApi.buyGift({ id: id }) as any;
    
    if (response.type === "success") {
      return true
    }
  }

  const handleShareReferral = (id: number) => {
    TelegramModule.useSendMessage(
      `https://t.me/${import.meta.env.VITE_APP_BOT.replace("@", "")}/store?startapp=gift_${id}`,
      "Look at this gift, it's wonderful!"
    );
  }

  const handleBuy = (gift: any) => {
    if (!meData) return;

    if (meData.id === gift.seller_id) {
      showToast("You can't buy your own gift!", "error");
      return;
    }

    if (meData.balance < gift.price) {
      showToast("You don't have enough balance!", "error");
      return;
    }

    const isSuccess = fetchBuy(gift.id);
    if (!isSuccess) {
      showToast("Something went wrong!", "error");
      return;
    };

    setMeData({ ...meData, balance: meData.balance - gift.price });
    showToast("Gift bought!", "success");

    setTimeout(() => {
      navigate(`/gifts`);
    }, 1300);
  }

  useEffect(() => {
    fetchGifts();
  }, [id]);

  if (!gift || gift.is_active === false || !animationData) return <Loader />;

  return (
    <div className={Styles.Gift}>
      <main>
        <div className={Styles.GiftInner}>
          <div className={Styles.GiftInnerContent}>
            <div className={Styles.GiftInnerContentCover}>
                {meData.id !== gift.seller_id && (
                  <div
                    onClick={() => handleFavorite(gift)}
                    className={cn(
                      Styles.GiftInnerContentCoverLike,
                      favoritesGifts.find((item: any) => item.id === gift.id) && Styles.Active
                    )}
                  >
                    <HeartIcon />
                  </div>
                )}

              <div className={Styles.GiftInnerContentCoverImage}>
                <Lottie
                  animationData={animationData}
                  loop={false}
                  autoplay
                  style={{ height: 240, width: 240 }}
                />
              </div>
            </div>

            <div className={Styles.GiftInnerContentInfo}>
              <div className={Styles.GiftInnerContentInfoFlexed}>
                <div className={Styles.GiftInnerContentInfoTitle}>
                  <p>{gift.type}</p>
                </div>
                <div className={Styles.GiftInnerContentInfoNumber}>
                  <p>#{gift.number}</p>
                </div>
              </div>
              <div className={Styles.GiftInnerContentInfoId}>
                <p>ID: {gift.id}</p>
              </div>
            </div>
          </div>

          <div className={Styles.GiftInnerStats}>
            <div className={Styles.GiftInnerStatsItem}>
              <div className={Styles.GiftInnerStatsItemContent}>
                <p>Model</p>
                <span>{gift.model_name}</span>
              </div>
              <div className={Styles.GiftInnerStatsItemMark}>
                <span>{gift.model}%</span>
              </div>
            </div>
            <div className={Styles.GiftInnerStatsItem}>
              <div className={Styles.GiftInnerStatsItemContent}>
                <p>Symbol</p>
                <span>{gift.pattern_name}</span>
              </div>
              <div className={Styles.GiftInnerStatsItemMark}>
                <span>{gift.pattern}%</span>
              </div>
            </div>
            <div className={Styles.GiftInnerStatsItem}>
              <div className={Styles.GiftInnerStatsItemContent}>
                <p>Backdrop</p>
                <span>{gift.background_name}</span>
              </div>
              <div className={Styles.GiftInnerStatsItemMark}>
                <span>{gift.background}%</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      <div className={Styles.GiftBottom}>
        <div className={Styles.GiftBottomInner}>
          <div className={Styles.GiftBottomInnerButton}>
            <button onClick={() => handleShareReferral(gift.id)}>
              <span>Share link</span>
              <ShareIcon />
            </button>
          </div>
          <div className={Styles.GiftBottomInnerButton}>
            <button onClick={() => handleBuy(gift)}>
              <span>Buy for {validateBalance(gift.price)}</span>
              <TonWhiteIcon />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Gift;