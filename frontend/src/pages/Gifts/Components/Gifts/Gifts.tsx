import { TonWhiteIcon } from "@/components/Icons";
import { getGiftImage } from "@/utils/gift";
import { showToast } from "@/utils/showToast";
import { TelegramModule } from "@/hooks/telegram";

import * as userApi from "@/api/services/user.service";

import Styles from "./Gifts.module.scss";

import NotFound from "@/components/NotFound/NotFound";

const Gifts = ({ section, unlistedGifts, listedGifts, onSelectGift, removeGift }: any) => {
  const handleOpenWithdrawConfirmation = (gift: any) => {
    onSelectGift(gift);
    window.dispatchEvent(new Event("openWithdrawConfirmationModal"));
  };

  const handleOpenSell = (gift: any) => {
    onSelectGift(gift);
    window.dispatchEvent(new Event("openSellModal"));
  };

  const fetchUnsellGift = async (id: number) => {
    const response = await userApi.unsellGift({ gift_id: id }) as any;
    
    if (response.type === "success") {
      removeGift(id);
      return true
    }
  }

  const handleUnsell = (id: number) => {
    const isSuccess = fetchUnsellGift(id);
    if (!isSuccess) {
      showToast("Something went wrong!", "error");
      return;
    };

    showToast("The gift is now on the marketplace!", "success");
  }

  const handleShareReferral = (id: number) => {
    TelegramModule.useSendMessage(
      `https://t.me/${import.meta.env.VITE_APP_BOT.replace("@", "")}/store?startapp=gift_${id}`,
      "Look at this gift, it's wonderful!"
    );
  }

  return (
    <div className={Styles.Gifts}>
      <div className={Styles.GiftsInner}>

        {section === "unlisted" && (
          <>
            {unlistedGifts.map((gift: any, i: number) => (
              <div key={i} className={Styles.GiftsInnerItem}>
                <div className={Styles.GiftsInnerItemCover}>
                  <div className={Styles.GiftsInnerItemCoverImage}>
                    <img
                      src={getGiftImage(gift.type, gift.number)}
                      alt={gift.model_name}
                    />
                  </div>
                </div>
                <div className={Styles.GiftsInnerItemInfo}>
                  <div className={Styles.GiftsInnerItemInfoTitle}>
                    <p>{gift.type}</p>
                  </div>
                  <div className={Styles.GiftsInnerItemInfoNumber}>
                    <p>#{gift.number}</p>
                  </div>
                </div>
                <div className={Styles.GiftsInnerItemButtons}>
                  <div className={Styles.GiftsInnerItemButtonsButton}>
                    <button onClick={() => handleOpenWithdrawConfirmation(gift)}>
                      <span>Withdraw</span>
                    </button>
                  </div>
                  <div className={Styles.GiftsInnerItemButtonsButton}>
                    <button onClick={() => handleOpenSell(gift)}>
                      <span>Sell gift</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </>
        )}

        {section === "listed" && (
          <>
            {listedGifts.map((gift: any, i: number) => (
              <div key={i} className={Styles.GiftsInnerItem}>
                <div className={Styles.GiftsInnerItemCover}>
                  <div className={Styles.GiftsInnerItemCoverImage}>
                    <img
                      src={getGiftImage(gift.type, gift.number)}
                      alt={gift.model_name}
                    />
                  </div>
                </div>
                <div className={Styles.GiftsInnerItemInfo}>
                  <div className={Styles.GiftsInnerItemInfoTitle}>
                    <p>{gift.type}</p>
                  </div>
                  <div className={Styles.GiftsInnerItemInfoNumber}>
                    <p>#{gift.number}</p>
                  </div>
                </div>
                <div className={Styles.GiftsInnerItemPrice}>
                  <p>{gift.price}</p>
                  <TonWhiteIcon />
                </div>
                <div className={Styles.GiftsInnerItemButtons}>
                  <div className={Styles.GiftsInnerItemButtonsButton}>
                    <button onClick={() => handleShareReferral(gift.id)}>
                      <span>Share link</span>
                    </button>
                  </div>
                  <div className={Styles.GiftsInnerItemButtonsButton}>
                    <button onClick={() => handleUnsell(gift.id)}>
                      <span>Take it off</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </>
        )}

      </div>

      {section === "unlisted" && unlistedGifts.length === 0 && <NotFound title="Gifts not found!" />}
      {section === "listed" && listedGifts.length === 0 && <NotFound title="Gifts not found!" />}
    </div>
  );
};

export default Gifts;