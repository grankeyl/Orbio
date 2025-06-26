import { api } from "@/api/clients/axios";

export const gifts = async () => {
  try {
    const response = await api.get(
      '/nfts',
      { },
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