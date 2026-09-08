export {};

declare global {
  interface Window {
    cometDesktop?: {
      platform: string;
      setAboutCopy?: (copy: { title: string; description: string; workflow: string; priorWork: string; button: string }) => Promise<void>;
      minimizeWindow?: () => Promise<void>;
      toggleMaximizeWindow?: () => Promise<boolean>;
      closeWindow?: () => Promise<void>;
      isWindowMaximized?: () => Promise<boolean>;
      onWindowStateChanged?: (callback: (payload: { isMaximized: boolean }) => void) => () => void;
    };
  }
}
