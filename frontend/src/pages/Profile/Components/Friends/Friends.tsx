import { FC, useEffect, useState } from "react";
import { useAppStore } from "@/stores/app.store";

import * as userApi from "@/api/services/user.service";

import Styles from "./Friends.module.scss";
import NotFound from "@/components/NotFound/NotFound";

const Friends: FC = () => {
  const { meData } = useAppStore();

  const [referrals, setReferrals] = useState<any>([]);

  const getReferrals = async () => {
    const response = await userApi.meReferrals() as any;
    
    if (response.type === "success") {
      const data = response.data;
      setReferrals(data);
    }
  };

  useEffect(() => {
    getReferrals();
  }, []);
  
  return (
    <div className={Styles.Friends}>
      <div className={Styles.FriendsInner}>
        <div className={Styles.FriendsInnerTitle}>
          <h4>Friends</h4>
          <span>{meData.count_referrals}</span>
        </div>

        <div className={Styles.FriendsInnerItems}>
          
          {referrals && referrals.length > 0 ? (
            referrals.map((ref: any) => (
              <div className={Styles.FriendsInnerItemsItem} key={ref.id}>
                <div className={Styles.FriendsInnerItemsItemCover}>
                  <div className={Styles.FriendsInnerItemsItemCoverImage}>
                    <img src={ref.photo_url || "/default-avatar.svg"} alt={ref.first_name || "Friend"} />
                  </div>
                </div>
                <div className={Styles.FriendsInnerItemsItemInfo}>
                  <div className={Styles.FriendsInnerItemsItemInfoTop}>
                    <div className={Styles.FriendsInnerItemsItemInfoTopTitle}>
                      <p>{ref.first_name || "No name"}</p>
                    </div>
                  </div>
                  <div className={Styles.FriendsInnerItemsItemInfoBottom}>
                    <div className={Styles.FriendsInnerItemsItemInfoBottomPrice}>
                      <p>ID: {ref.id}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <NotFound title="No friends found!" />
          )}

        </div>

        {!referrals && referrals.length === 0 && (
          <NotFound title="No friends found!" />
        )}
      </div>
    </div>
  );
};

export default Friends;