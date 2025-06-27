import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import { THEME, TonConnectUIProvider } from "@tonconnect/ui-react";

import App from "@/App";
import Toast from "@/components/Toast/index.tsx";

const rootElement = document.getElementById("root");

createRoot(rootElement!).render(
  <StrictMode>
    <TonConnectUIProvider
      manifestUrl="https://orbiomarket.com/tonconnect-manifest.json"
      uiPreferences={{
        theme: THEME.DARK,
      }}
    >
      <BrowserRouter>
        <App />
        <Toast />
      </BrowserRouter>
    </TonConnectUIProvider>
  </StrictMode>
);