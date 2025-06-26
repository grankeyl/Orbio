import { api } from '@/api/clients/axios';
import Cookies from 'js-cookie';

export const login = async (payload: {
  init_data: string,
}) => {
  try {
    const response = await api.post(
      '/user/login',
      { ...payload },
      { }
    );

    if (response.status === 200) {
      const responseData = response.data;
      Cookies.set("token", responseData.token, { path: "/" });
      return {
        type: "success",
        ...responseData
      }
    }
  } catch (e: any) {
    throw new Error("Login failed");
  }
}

export const me = async () => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.get(
      '/user/me',
      { headers: { Authorization: `${tokenBearer}` } }
    );

    if (response.status === 200) {
      const responseData = response.data;
      return {
        type: "success",
        data: responseData
      }
    }
  } catch (e: any) {
    throw new Error("Me failed");
  }
}

export const meReferrals = async () => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.get(
      '/user/me/referrals',
      { headers: { Authorization: `${tokenBearer}` } },
    );

    if (response.status === 200) {
      const responseData = response.data;
      return {
        type: "success",
        data: responseData
      }
    }
  } catch (e: any) {
    throw new Error("Me failed");
  }
}

export const getGifts = async (payload: {
  limit: number,
  offset: number,
  for_sell: number,
}) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.get(
      '/user/gifts',
      { headers: { Authorization: `${tokenBearer}` }, params: payload }
    );

    if (response.status === 200) {
      const responseData = response.data;
      return {
        type: "success",
        data: responseData
      }
    }
  } catch (e: any) {
    throw new Error("Get gifts failed");
  }
}

export const withdrawGift = async (payload: {
  id: number,
}) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.post(
      '/user/gifts/withdraw',
      { ...payload },
      { headers: { Authorization: `${tokenBearer}` } }
    );

    if (response.status === 200) {
      const responseData = response.data;
      console.log(responseData);
      return {
        type: "success",
        data: responseData
      }
    }
  } catch (e: any) {
    throw new Error("Sell gift failed");
  }
}

export const sellGift = async (payload: {
  gift_id: number,
  price: number,
}) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.post(
      '/user/gift/sell',
      { ...payload },
      { headers: { Authorization: `${tokenBearer}` } }
    );

    if (response.status === 200) {
      const responseData = response.data;
      return {
        type: "success",
        ...responseData
      }
    }
  } catch (e: any) {
    throw new Error("Sell gift failed");
  }
}

export const unsellGift = async (payload: {
  gift_id: number,
}) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.post(
      '/user/gift/unsell',
      { ...payload },
      { headers: { Authorization: `${tokenBearer}` } }
    );

    if (response.status === 200) {
      const responseData = response.data;
      return {
        type: "success",
        ...responseData
      }
    }
  } catch (e: any) {
    throw new Error("Sell gift failed");
  }
}

export const withdrawBalance = async (payload: {
  amount: number,
  address: string,
}) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.post(
      '/user/withdraw/balance',
      { ...payload },
      { headers: { Authorization: `${tokenBearer}` } }
    );

    if (response.status === 200) {
      const responseData = response.data;
      return {
        type: "success",
        data: responseData
      }
    }
  } catch (e: any) {
    throw new Error("Withdraw balance failed");
  }
}