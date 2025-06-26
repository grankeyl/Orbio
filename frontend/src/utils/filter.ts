export const getNameSortFilter = (sort_by: string) => {
    switch (sort_by) {
        case "latest":
            return "Latest";
        case "price_low_to_high":
            return "Price, Low to High";
        case "price_high_to_low":
            return "Price, High to Low";
        case "random":
            return "Random";
        default:
            return "Latest";
    }
};