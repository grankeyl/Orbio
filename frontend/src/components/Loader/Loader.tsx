import { FC } from "react";

import Style from "./Loader.module.scss";

const Loader: FC = () => {
  return (
    <div className={Style.Loader}>
      <div className={Style.Spinner}></div>
    </div>
  );
};

export default Loader;