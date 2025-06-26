import { FC } from "react";
import { cn } from "@/lib/utils";
import { CloseIcon } from "@/components/Icons";

import Styles from "./Error.module.scss";


interface ErrorProps {
  isActive: boolean;
  onToggle: () => void;
  text: string;
}

const Error: FC<ErrorProps> = ({ isActive, onToggle, text }) => {
  return (
    <div className={cn(Styles.Error, isActive && Styles.Active)}>
      <div className={Styles.ErrorClose} onClick={onToggle}>
        <CloseIcon />
      </div>

      <div className={Styles.ErrorInner}>
        <div className={Styles.ErrorInnerContent}>
          <h4>Error</h4>
        </div>

        <div className={Styles.ErrorInnerText}>
          <p>{text}</p>
        </div>
        
        <div className={Styles.ErrorInnerButtons}>
          <div className={Styles.ErrorInnerButtonsButton}>
            <button onClick={onToggle}>
              <span>Close</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Error;