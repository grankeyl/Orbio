import { FC } from "react";

import Style from "./NotFound.module.scss";

interface NotFoundProps {
  title: string,
};

const NotFound: FC<NotFoundProps> = ({ title }) => {
  return (
    <div className={Style.NotFound}>
      <div className={Style.NotFoundInner}>
        <div className={Style.NotFoundInnerImage}>
          <img src="/logotypes/logotype-primary.svg" alt="" />
        </div>
        <div className={Style.NotFoundInnerText}>
          <h4>{title}</h4>
        </div>
      </div>
    </div>
  );
};

export default NotFound;