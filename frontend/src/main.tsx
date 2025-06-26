import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import { TonConnectUIProvider } from "@tonconnect/ui-react";

import App from "@/App";
import Toast from "@/components/Toast/index.tsx";

const rootElement = document.getElementById("root");

createRoot(rootElement!).render(
  <StrictMode>
    <TonConnectUIProvider manifestUrl="https://holdslaves.com/tonconnect-manifest.json">
      <BrowserRouter>
        <App />
        <Toast />
      </BrowserRouter>
    </TonConnectUIProvider>
  </StrictMode>
);