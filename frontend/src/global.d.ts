export {};

declare global {
  interface Window {
    cometDesktop?: {
      platform: string;
      minimizeWindow?: () => Promise<void>;
      toggleMaximizeWindow?: () => Promise<boolean>;
      closeWindow?: () => Promise<void>;
      isWindowMaximized?: () => Promise<boolean>;
      onWindowStateChanged?: (callback: (payload: { isMaximized: boolean }) => void) => () => void;
    };
  }
}
