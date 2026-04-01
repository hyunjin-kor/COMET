export {};

declare global {
  interface Window {
    catpriceDesktop?: {
      getVersion: () => Record<string, string>;
      platform: string;
      minimizeWindow?: () => Promise<void>;
      toggleMaximizeWindow?: () => Promise<boolean>;
      closeWindow?: () => Promise<void>;
      isWindowMaximized?: () => Promise<boolean>;
      onWindowStateChanged?: (callback: (payload: { isMaximized: boolean }) => void) => () => void;
      onNewEstimate?: (callback: (...args: unknown[]) => void) => () => void;
      openFile?: () => Promise<unknown>;
      saveFile?: (data: string, filename: string) => Promise<unknown>;
    };
  }
}
