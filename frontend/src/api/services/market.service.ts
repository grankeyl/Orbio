import { api } from '@/api/clients/axios';
import Cookies from 'js-cookie';

export const gifts = async (payload: {
  limit: number,
  offset: number,
  collection: string[],
  model: string[],
  sort_by: string,
  from_price: number,
  to_price: number,
  number: number,
}) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.get('/market/gifts', {
      headers: { Authorization: `${tokenBearer}` },
      params: payload
    });

    if (response.status === 200) {
      const responseData = response.data;
      return {
        type: "success",
        data: responseData
      }
    }
  } catch (e: any) {
    console.log(e);
    throw new Error("Get gifts failed");
  }
}

export const giftGetById = async (id: number) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.get(
      `/market/gifts/${id}`,
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
    console.log(e);
    throw new Error("Get gifts failed");
  }
}

export const buyGift = async (payload: {
  id: number,
}) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.post(
      `/market/gift/buy`,
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
    throw new Error("Buy gift failed");
  }
}