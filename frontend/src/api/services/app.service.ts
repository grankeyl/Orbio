import { api } from '@/api/clients/axios';

export const variables = async () => {
  try {
    const response = await api.get('/app/variables', {});

    console.log(response);

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