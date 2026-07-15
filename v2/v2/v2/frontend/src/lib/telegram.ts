import type { ReactNode } from "react";
import { createContext, useContext, useEffect, useState } from "react";
import React from "react";

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
}

export interface TelegramHaptic {
  impactOccurred: (style: "light" | "medium" | "heavy" | "rigid" | "soft") => void;
  notificationOccurred: (type: "error" | "success" | "warning") => void;
  selectionChanged: () => void;
  toggleOccurred?: (is_on: boolean) => void;
}

export interface TelegramWebApp {
  ready: () => void;
  expand: () => void;
  close: () => void;
  sendData: (data: string) => void;
  switchInlineQuery: (query: string, choose_chats?: string[]) => void;
  openTelegramLink: (url: string) => void;
  showAlert: (message: string, callback?: () => void) => void;
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void;
  HapticFeedback: TelegramHaptic;
  initData: string;
  initDataUnsafe: {
    query_id?: string;
    user?: TelegramUser;
    receiver?: TelegramUser;
    chat?: TelegramUser;
    start_param?: string;
  };
  version: string;
  platform: string;
  colorScheme: "light" | "dark";
  themeParams: { [key: string]: string };
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
}

interface TelegramContextValue {
  isReady: boolean;
  webApp: TelegramWebApp | null;
  user: TelegramUser | null;
  haptic: {
    impact: (style: "light" | "medium" | "heavy" | "rigid" | "soft") => void;
    notification: (type: "error" | "success" | "warning") => void;
    selectionChanged: () => void;
    toggleOccurred: (is_on: boolean) => void;
  };
  share: (text: string, title?: string) => void;
  isDark: boolean;
  openLink: (url: string) => void;
  showConfirm: (message: string) => Promise<boolean>;
  showAlert: (message: string) => Promise<void>;
}

const TelegramContext = createContext<TelegramContextValue | null>(null);

export function TelegramProvider({ children }: { children: ReactNode }) {
  const [isReady, setIsReady] = useState(false);
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);
  const [user, setUser] = useState<TelegramUser | null>(null);

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (!tg) {
      setIsReady(true);
      return;
    }

    tg.ready();
    tg.expand();
    setWebApp(tg);
    setUser(tg.initDataUnsafe?.user || null);
    setIsReady(true);
  }, []);

  const haptic = {
    impact: (style: "light" | "medium" | "heavy" | "rigid" | "soft") => {
      webApp?.HapticFeedback?.impactOccurred(style);
    },
    notification: (type: "error" | "success" | "warning") => {
      webApp?.HapticFeedback?.notificationOccurred(type);
    },
    selectionChanged: () => {
      webApp?.HapticFeedback?.selectionChanged();
    },
    toggleOccurred: (is_on: boolean) => {
      webApp?.HapticFeedback?.toggleOccurred?.(is_on);
    },
  };

  const share = (text: string, title?: string) => {
    if (webApp?.switchInlineQuery) {
      webApp.switchInlineQuery(text, ["users", "groups", "channels"]);
    } else if (navigator.share) {
      navigator.share({ title: title || "Share", text });
    }
  };

  const isDark = webApp?.colorScheme === "dark" || false;

  const openLink = (url: string) => {
    if (webApp?.openTelegramLink) {
      webApp.openTelegramLink(url);
    } else {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  };

  const showConfirm = (message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      if (webApp?.showConfirm) {
        webApp.showConfirm(message, (confirmed) => resolve(confirmed));
      } else {
        resolve(window.confirm(message));
      }
    });
  };

  const showAlert = (message: string): Promise<void> => {
    return new Promise((resolve) => {
      if (webApp?.showAlert) {
        webApp.showAlert(message, resolve);
      } else {
        alert(message);
        resolve();
      }
    });
  };

  const value: TelegramContextValue = {
    isReady,
    webApp,
    user,
    haptic,
    share,
    isDark,
    openLink,
    showConfirm,
    showAlert,
  };

  return React.createElement(
    TelegramContext.Provider,
    { value },
    children as ReactNode
  );
}

export function useTelegram() {
  const ctx = useContext(TelegramContext);
  if (!ctx) throw new Error("useTelegram must be used within TelegramProvider");
  return ctx;
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}
