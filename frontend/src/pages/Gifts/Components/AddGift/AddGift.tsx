import { FC } from "react";
import { cn } from "@/lib/utils";
import { CloseIcon, PenIcon, NetworkIcon } from "@/components/Icons";
import { TelegramModule } from "@/hooks/telegram";

import Styles from "./AddGift.module.scss";


interface AddGiftProps {
  isActive: boolean;
  onToggle: () => void;
}

const AddGift: FC<AddGiftProps> = ({ isActive, onToggle }) => {
  const handleAddGift = () => {
    const userbot = import.meta.env.VITE_APP_USERBOT.replace("@", "");
    const link = `https://t.me/${userbot}`;
    TelegramModule.useLink(link);
  };

  return (
    <div className={cn(Styles.AddGift, isActive && Styles.Active)}>
      <div className={Styles.AddGiftClose} onClick={onToggle}>
        <CloseIcon />
      </div>

      <div className={Styles.AddGiftInner}>
        <div className={Styles.AddGiftInnerContent}>
          <h4>Add gift</h4>
        </div>

        <div className={Styles.AddGiftInnerLists}>
          <div className={Styles.AddGiftInnerListsItem}>
            <div className={Styles.AddGiftInnerListsItemIcon}>
              <PenIcon />
            </div>
            <div className={Styles.AddGiftInnerListsItemContent}>
              <h4>Go to the bot and text it</h4>
              <p>Write any message to userbot <span>{import.meta.env.VITE_APP_USERBOT}</span></p>
            </div>
          </div>
          <div className={Styles.AddGiftInnerListsItem}>
            <div className={Styles.AddGiftInnerListsItemIcon}>
              <NetworkIcon />
            </div>
            <div className={Styles.AddGiftInnerListsItemContent}>
              <h4>Send a gift to the userbot</h4>
              <p>Make a gift transfer <span>{import.meta.env.VITE_APP_USERBOT}</span></p>
            </div>
          </div>
        </div>
        
        <div className={Styles.AddGiftInnerButtons}>
          <div className={Styles.AddGiftInnerButtonsButton}>
            <button onClick={handleAddGift}>
              <span>Add gift</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default AddGift;