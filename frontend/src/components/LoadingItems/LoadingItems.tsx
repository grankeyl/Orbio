import { FC } from "react";

import Style from "./LoadingItems.module.scss";

interface LoadingItemsProps {
  title: string,
};

const LoadingItems: FC<LoadingItemsProps> = ({ title }) => {
  return (
    <div className={Style.LoadingItems}>
      <div className={Style.LoadingItemsInner}>
        <div className={Style.LoadingItemsInnerSpinner}></div>
        <div className={Style.LoadingItemsInnerText}>
          <h4>{title}</h4>
        </div>
      </div>
    </div>
  );
};

export default LoadingItems;