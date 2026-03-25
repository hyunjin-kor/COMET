/**
 * CatPrice Electron Preload Script
 * Exposes safe IPC bridge to renderer process (React app)
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('catpriceDesktop', {
  // App version
  getVersion: () => process.versions,
  platform: process.platform,

  // IPC listeners (from main process)
  onNewEstimate: (callback) => {
    ipcRenderer.on('new-estimate', callback);
    return () => ipcRenderer.removeListener('new-estimate', callback);
  },

  // Open file dialog
  openFile: () => ipcRenderer.invoke('open-file-dialog'),

  // Save file dialog
  saveFile: (data, filename) => ipcRenderer.invoke('save-file-dialog', { data, filename }),
});
