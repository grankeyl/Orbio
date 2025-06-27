import { useEffect, useState } from "react"
import { Routes, Route, useNavigate } from "react-router"
import { useAppStore } from "@/stores/app.store";
import { TelegramModule } from "@/hooks/telegram";

declare global {
  interface Window {
    Telegram: any;
  }
}

import * as userApi from "@/api/services/user.service";
import * as nftsApi from "@/api/services/nfts.service";
import * as appApi from "@/api/services/app.service";

import Layout from "@/layouts/Layout"
import Home from "@/pages/Home/Home"
import Gift from "@/pages/Gift/Gift"
import Gifts from "@/pages/Gifts/Gifts"
import Activity from "@/pages/Activity/Activity"
import Profile from "@/pages/Profile/Profile"

import Loader from "@/components/Loader/Loader"

import "@/styles/index.scss"
import "@/styles/fonts/stylesheet.css"

const App = () => {
  const navigate = useNavigate();

  const { setMeData, setAppGifts, setAppVariables } = useAppStore();

  const [isTokenReady, setIsTokenReady] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    TelegramModule.initMiniApp();
  }, []);

  const checkStartParam = () => {
    const startParam = TelegramModule.checkStartParam();

    if (startParam && startParam.startsWith("gift_")) {
      const giftId = startParam.split("_")[1];
      if (giftId) {
        navigate(`/gift/${giftId}`);
      }
    }
  }

  const fetchLogin = async () => {
    // if (!window.Telegram.WebApp.initData) { return; }

    let initData = import.meta.env.VITE_APP_INIT_DATA as any;

    // if (window.Telegram.WebApp.initData) { initData = window.Telegram.WebApp.initData; }
    const response = await userApi.login({ init_data: initData });

    if (response.type === "success") {
      setIsTokenReady(true);
      setIsLoading(false);
    }
  };

  const fetchMeData = async () => {
    const response = await userApi.me() as any;
    
    if (response.type === "success") {
      const data = response.data;
      setMeData(data);
    }
  };

  const fetchGifts = async () => {
    const response = await nftsApi.gifts() as any;
    
    if (response.type === "success") {
      const data = response.data;
      setAppGifts(data);
    }
  };

  const fetchVariables = async () => {
    const response = await appApi.variables() as any;
    
    if (response.type === "success") {
      const data = response.data;
      setAppVariables(data);
    }
  };

  useEffect(() => {
    const handleWheel = (event: WheelEvent) => {
      if (event.target instanceof HTMLInputElement && event.target.type === "number") {
        event.preventDefault()
      }
    }
    document.addEventListener("wheel", handleWheel, { passive: false })
    return () => {
      document.removeEventListener("wheel", handleWheel)
    }
  }, [])

  useEffect(() => {
    fetchLogin();
  }, [])

  useEffect(() => {
    fetchMeData();
    fetchGifts();
    fetchVariables();
    checkStartParam();
  }, [isTokenReady])

  if (isLoading) { return ( <Loader /> ) }

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="gift/:id" element={<Gift />} />
        <Route path="gifts" element={<Gifts />} />
        <Route path="activity" element={<Activity />} />
        <Route path="profile" element={<Profile />} />
      </Route>
      <Route path="*" element="Not Found" />
    </Routes>
  )
}

export default App