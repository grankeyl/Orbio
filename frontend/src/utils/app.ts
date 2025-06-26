export const shortenString = (str: string, startLength = 5, endLength = 5): string => {
    if (str.length <= startLength + endLength) return str;
    return `${str.slice(0, startLength)}...${str.slice(-endLength)}`;
};

export const formatToLocalTime = (isoString: string): string => {
  const date = new Date(isoString);

  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();

  return `${hours}:${minutes} ${day}.${month}.${year}`;
}

export function checkAmount(amount: number) {
  if (amount < 0.09) {
    return false;
  }
  return true;
}

export const validateBalance = (number: number): number => {
  const str = number.toFixed(20);

  if (str.includes(".")) {
    const [integerPart, decimalPart] = str.split(".");

    const trimmedDecimal = decimalPart.replace(/0+$/, "");

    if (trimmedDecimal.length > 3) {
      return parseFloat(`${integerPart}.${trimmedDecimal.slice(0, 3)}`);
    }
  }

  return number;
};