import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AppState {
  meData: any;
  appGifts: any;
  appVariables: any;
  favoritesGifts: any;
  filtersHomeData: any;
  filtersActivityData: any;

  setMeData: (data: any) => void;
  setAppVariables: (data: any) => void;
  setAppGifts: (data: any) => void;
  setFavoritesGifts: (data: any) => void;
  setFiltersHomeData: (data: any) => void;
  setFiltersActivityData: (data: any) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set: any) => ({
      meData: {},
      appGifts: [],
      appVariables: {},
      favoritesGifts: [],
      filtersHomeData: {},
      filtersActivityData: {},

      setMeData: (data: any) => set({ meData: data }),
      setAppGifts: (data: any) => set({ appGifts: data }),
      setAppVariables: (data: any) => set({ appVariables: data }),
      setFavoritesGifts: (data: any) => set({ favoritesGifts: data }),
      setFiltersHomeData: (data: any) => set({ filtersHomeData: data }),
      setFiltersActivityData: (data: any) => set({ filtersActivityData: data }),
    }),
    {
      name: "app-store",
    }
  )
);