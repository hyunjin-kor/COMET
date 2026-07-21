/**
 * CatPrice Electron Preload Script
 * Exposes safe IPC bridge to renderer process (React app)
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('catpriceDesktop', {
  platform: process.platform,

  // Window controls
  minimizeWindow: () => ipcRenderer.invoke('window:minimize'),
  toggleMaximizeWindow: () => ipcRenderer.invoke('window:toggle-maximize'),
  closeWindow: () => ipcRenderer.invoke('window:close'),
  isWindowMaximized: () => ipcRenderer.invoke('window:is-maximized'),
  onWindowStateChanged: (callback) => {
    const handler = (_event, payload) => callback(payload);
    ipcRenderer.on('window-state-changed', handler);
    return () => ipcRenderer.removeListener('window-state-changed', handler);
  },

  // IPC listeners (from main process)
  onNewEstimate: (callback) => {
    ipcRenderer.on('new-estimate', callback);
    return () => ipcRenderer.removeListener('new-estimate', callback);
  },
});
