import { api } from '@/api/clients/axios';
import Cookies from 'js-cookie';

export const activity = async (payload: {
  collection: string[],
  sort_by: string,
  number: number,
  limit: number,
  offset: number
}) => {
  try {
    const tokenBearer = Cookies.get("token");
    if (!tokenBearer) return { type: "error", status: 401 };

    const response = await api.get('/history/activity', {
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
    throw new Error("Get activity failed");
  }
}