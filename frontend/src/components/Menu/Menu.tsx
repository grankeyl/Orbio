import { FC } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { GiftIcon, GraphIcon, ProfileIcon, StoreIcon } from "@/components/Icons";

import Style from "./Menu.module.scss";

const Menu: FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const path = location.pathname;

  const links = [
    { path: "/", label: "Store", Icon: StoreIcon },
    { path: "/gifts", label: "My gifts", Icon: GiftIcon },
    { path: "/activity", label: "Activity", Icon: GraphIcon },
    { path: "/profile", label: "Profile", Icon: ProfileIcon },
  ];

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  return (
    <div className={Style.Menu}>
      <div className={Style.MenuInner}>
        {links.map(({ path: linkPath, label, Icon }) => {
          const isActive = path === linkPath;

          return (
            <div
              key={linkPath}
              onClick={() => handleNavigate(linkPath)}
              className={`${Style.MenuInnerLink} ${isActive ? Style.active : ""}`}
            >
              <div className={Style.MenuInnerLinkIcon}>
                <Icon />
              </div>
              <div className={Style.MenuInnerLinkText}>
                <p>{label}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Menu;