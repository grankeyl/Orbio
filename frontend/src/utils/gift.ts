export const getGiftImage = (gift_type: string, gift_number: number) => {
    if (!gift_type) return "";
    
    const giftType = gift_type.toLowerCase().replace(" ", "");
    return `https://nft.fragment.com/gift/${giftType}-${gift_number}.large.jpg`;
};

export const getGiftLottie = (gift_type: string, gift_number: number) => {
    if (!gift_type) return "";

    const giftType = gift_type.toLowerCase().replace(" ", "");
    return `https://nft.fragment.com/gift/${giftType}-${gift_number}.lottie.json`;
};

export const getGiftModel = (gift_type: string, gift_model: string) => {
    if (!gift_type) return "";

    const giftType = gift_type.toLowerCase();
    const giftModel = gift_model.replace("’", "'");
    return `https://gifts.coffin.meme/${giftType}/${giftModel}.png`;
};