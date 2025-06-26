import WebApp from '@twa-dev/sdk';

export const TelegramModule = {
  async initMiniApp() {
    WebApp.requestWriteAccess();
    WebApp.disableVerticalSwipes();
    WebApp.ready();
    WebApp.expand();
  },

  initDataRaw() {
    return WebApp.initData;
  },

  initData() {
    return WebApp.initDataUnsafe;
  },

  checkStartParam() {
    return WebApp.initDataUnsafe?.start_param || null;
  },

  hideBackButton() {
    const backButton = WebApp.BackButton;
    if (backButton?.isVisible !== undefined) {
      backButton.hide();
    }
  },

  useBackButton(action: () => void) {
    const backButton = WebApp.BackButton;
    if (backButton?.show && backButton.onClick) {
      backButton.show();
      backButton.onClick(action);
    }
  },

  useSoftHaptic() {
    WebApp.HapticFeedback?.impactOccurred?.('soft');
  },

  useLightHaptic() {
    WebApp.HapticFeedback?.impactOccurred?.('light');
  },

  useMediumHaptic() {
    WebApp.HapticFeedback?.impactOccurred?.('medium');
  },

  useHeavyHaptic() {
    WebApp.HapticFeedback?.impactOccurred?.('heavy');
  },

  useLink(link: string) {
    WebApp.openTelegramLink(link);
  },

  async useShareStory(
    storyMedia: string,
    language: string,
    referralLink: string
  ) {
    const text =
      language === 'ru'
        ? `${referralLink} Зарабатывайте, ничего не делая. Пусть рабы работают на вас в холде.`
        : `${referralLink} Earn by doing nothing. Let the slaves work for you in Hold.`;

    WebApp.shareToStory(storyMedia, {
      text,
      widget_link: {
        url: referralLink,
        name: import.meta.env.VITE_APP_MINI_APP_USERNAME,
      },
    });

    return true;
  },

  async useSendMessage(url: string, message: string) {
    const encodedUrl = encodeURIComponent(url);
    const encodedMessage = encodeURIComponent(message);
    const shareLink = `https://t.me/share/url?url=${encodedUrl}&text=${encodedMessage}`;
    WebApp.openTelegramLink(shareLink);
  },
};