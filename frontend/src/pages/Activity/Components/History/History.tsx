import { FC } from "react";
import { cn } from "@/lib/utils";
import { TonWhiteIcon } from "@/components/Icons";
import { getGiftImage } from "@/utils/gift";
import { formatToLocalTime } from "@/utils/app";

import Styles from "./History.module.scss";

import NotFound from "@/components/NotFound/NotFound";

const History: FC<any> = ({ activity }) => {
  return (
    <div className={Styles.History}>
      <div className={Styles.HistoryInner}>

        {activity.length > 0 ? (
          <div className={Styles.HistoryInnerItems}>
            {activity
              .filter((item: any) => item.type !== "deposit")
              .map((item: any, index: number) => (
              <div key={index} className={Styles.HistoryInnerItemsItem}>
                <div className={Styles.HistoryInnerItemsItemCover}>
                  <div className={Styles.HistoryInnerItemsItemCoverImage}>
                    <img src={getGiftImage(item.gift, item.gift_number)} alt="" />
                  </div>
                </div>
                <div className={Styles.HistoryInnerItemsItemInfo}>
                  <div className={Styles.HistoryInnerItemsItemInfoTop}>
                    <div className={Styles.HistoryInnerItemsItemInfoTopTitle}>
                      <p>{item.gift}</p>
                    </div>
                    <div className={Styles.HistoryInnerItemsItemInfoTopNumber}>
                      <p>#{item.gift_number}</p>
                    </div>
                  </div>
                  <div className={Styles.HistoryInnerItemsItemInfoBottom}>
                    <div className={Styles.HistoryInnerItemsItemInfoBottomPrice}>
                      <p>{item.price}</p>
                      <TonWhiteIcon />
                    </div>
                    <div className={Styles.HistoryInnerItemsItemInfoBottomDate}>
                      <p>{formatToLocalTime(item.created_at)}</p>
                    </div>
                  </div>
                </div>
                {item.type === "withdraw" && (
                  <div className={cn(Styles.HistoryInnerItemsItemStatus, Styles.Withdraw)}>
                    <h4>Withdraw</h4>
                  </div>
                )}
                {item.type === "sell_gift" && (
                  <div className={cn(Styles.HistoryInnerItemsItemStatus, Styles.Listing)}>
                    <h4>Listing</h4>
                  </div>
                )}
                {item.type === "unlisted_gift" && (
                  <div className={cn(Styles.HistoryInnerItemsItemStatus, Styles.Listing)}>
                    <h4>Unlisting</h4>
                  </div>
                )}
                {item.type === "buy_gift" && (
                  <div className={cn(Styles.HistoryInnerItemsItemStatus, Styles.Purchase)}>
                    <h4>Purchase</h4>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <NotFound title="No activity found" />
        )}

      </div>
    </div>
  );
};

export default History;