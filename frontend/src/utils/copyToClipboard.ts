export const copyToClipboard = (text: string): boolean => {
  const el = document.createElement("textarea");
  el.value = text;
  document.body.appendChild(el);
  const selection = document.getSelection();
  if (!selection) return false;
  const selected = selection.rangeCount > 0 ? selection.getRangeAt(0) : false;
  el.select();
  document.execCommand("copy");
  document.body.removeChild(el);
  if (selected) {
    selection.removeAllRanges();
    selection.addRange(selected);
  }

  return true;
};
