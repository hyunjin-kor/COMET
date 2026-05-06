/**
 * CatPrice Electron Main Process
 * Launches the FastAPI backend as a sidecar and shows the React frontend
 */

const { app, BrowserWindow, shell, dialog, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

// Prevent black-window rendering issues on some Windows GPU/driver setups.
app.disableHardwareAcceleration();

// ─── Configuration ───────────────────────────────────────────────────────────
// BACKEND_PORT is the single source of truth for the desktop sidecar port.
// Keep these references in sync if you change it:
//   - package.json (dev:backend, dev:frontend, electron:wait scripts)
//   - frontend/src/lib/api.ts (file:// fallback URL)
//   - scripts/smoke_test_desktop.ps1
//   - scripts/stop_catprice_processes.ps1
const BACKEND_PORT = 8765;      // Avoid conflicts with other services
const BACKEND_HOST = '127.0.0.1';
const BACKEND_URL  = `http://${BACKEND_HOST}:${BACKEND_PORT}`;
const HEALTH_URL   = `${BACKEND_URL}/api/health`;
const MAX_WAIT_MS  = 30_000;    // 30 seconds max startup wait
const POLL_INTERVAL_MS = 500;
const ALLOWED_EXTERNAL_HOSTS = new Set([
  'github.com',
  'doi.org',
  'sigmaaldrich.com',
  'fuelcellstore.com',
  'energy.gov',
  'nature.com',
  'pubs.acs.org',
  'science.org',
  'onlinelibrary.wiley.com',
  'sciencedirect.com',
  'pubmed.ncbi.nlm.nih.gov',
  'naos-be.zcu.cz',
  'metals.dev',
  'metalpriceapi.com',
  'bls.gov',
]);

// ─── State ────────────────────────────────────────────────────────────────────
let mainWindow = null;
let backendProcess = null;
let shutdownPromise = null;
let appIsQuitting = false;

function isAllowedExternalUrl(urlString) {
  try {
    const parsed = new URL(urlString);
    if (parsed.protocol !== 'https:') {
      return false;
    }

    const hostname = parsed.hostname.toLowerCase();
    for (const allowedHost of ALLOWED_EXTERNAL_HOSTS) {
      if (hostname === allowedHost || hostname.endsWith(`.${allowedHost}`)) {
        return true;
      }
    }
    return false;
  } catch (_error) {
    return false;
  }
}

function isAppNavigationUrl(urlString) {
  try {
    const parsed = new URL(urlString);
    if (parsed.protocol === 'file:') {
      return true;
    }

    const isLoopbackHost = parsed.hostname === '127.0.0.1' || parsed.hostname === 'localhost';
    if (!isLoopbackHost) {
      return false;
    }

    return parsed.port === String(BACKEND_PORT) || parsed.port === '5173';
  } catch (_error) {
    return false;
  }
}

function sendWindowState() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  mainWindow.webContents.send('window-state-changed', {
    isMaximized: mainWindow.isMaximized(),
  });
}

function debugLog(message) {
  const line = `[${new Date().toISOString()}] ${message}`;
  console.log(line);
  try {
    const baseDir = app.isReady()
      ? app.getPath('userData')
      : (process.env.TEMP || __dirname);
    fs.mkdirSync(baseDir, { recursive: true });
    fs.appendFileSync(path.join(baseDir, 'catprice-launcher.log'), `${line}\n`);
  } catch (_error) {
    // Ignore file logging failures.
  }
}

function showAndFocusMainWindow(reason = 'show') {
  if (!mainWindow || mainWindow.isDestroyed()) return;

  debugLog(`Showing main window (${reason})`);
  if (mainWindow.isMinimized()) {
    mainWindow.restore();
  }
  if (!mainWindow.isVisible()) {
    mainWindow.show();
  }
  mainWindow.moveTop();
  mainWindow.focus();
  mainWindow.setAlwaysOnTop(true);
  mainWindow.setAlwaysOnTop(false);
}

function waitForBackend(timeoutMs) {
  return new Promise((resolve) => {
    const start = Date.now();
    let settled = false;

    const finish = (value) => {
      if (!settled) {
        settled = true;
        resolve(value);
      }
    };

    const retryOrFinish = () => {
      if (Date.now() - start >= timeoutMs) {
        finish(false);
      } else {
        setTimeout(poll, POLL_INTERVAL_MS);
      }
    };

    const poll = () => {
      const req = http.get(HEALTH_URL, (res) => {
        res.resume();
        if (res.statusCode === 200) {
          finish(true);
        } else {
          // Some other process is listening on the port but isn't our
          // backend (or hasn't finished initializing). Keep polling
          // until the timeout — this avoids giving up when a stale
          // sidecar / unrelated server holds the port.
          retryOrFinish();
        }
      });

      req.setTimeout(2000, () => {
        req.destroy();
      });

      req.on('error', retryOrFinish);
    };

    poll();
  });
}

// ─── Backend Detection ────────────────────────────────────────────────────────
function getPythonExecutable() {
  // 1. Explicitly set by start.bat via env var
  if (process.env.CATPRICE_PYTHON && fs.existsSync(process.env.CATPRICE_PYTHON)) {
    return process.env.CATPRICE_PYTHON;
  }

  // 2. Packaged app: bundled venv
  if (app.isPackaged) {
    const bundledPython = path.join(process.resourcesPath, 'backend', '.venv', 'Scripts', 'python.exe');
    if (fs.existsSync(bundledPython)) return bundledPython;
  }

  // 3. Development: common Python 3.11 paths on Windows
  const username = require('os').userInfo().username;
  const candidates = [
    `C:\\Users\\${username}\\AppData\\Local\\Programs\\Python\\Python311\\python.exe`,
    'C:\\Python311\\python.exe',
    `C:\\Users\\${username}\\AppData\\Local\\Programs\\Python\\Python312\\python.exe`,
    'C:\\Python312\\python.exe',
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }

  // 4. Venv in project root
  const projectRoot = path.resolve(__dirname, '..');
  const venvPaths = [
    path.join(projectRoot, '.venv', 'Scripts', 'python.exe'),
    path.join(projectRoot, 'venv',  'Scripts', 'python.exe'),
  ];
  for (const p of venvPaths) {
    if (fs.existsSync(p)) return p;
  }

  return 'python'; // final fallback
}

function getBackendDir() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend');
  }
  return path.join(__dirname, '..', 'backend');
}

function getPackagedBackendExecutable() {
  const candidates = [
    path.join(process.resourcesPath, 'backend-sidecar', 'CatPriceBackend.exe'),
    path.join(process.resourcesPath, 'backend-sidecar', 'CatPriceBackend', 'CatPriceBackend.exe'),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) || null;
}

function getDatabasePath() {
  if (app.isPackaged) {
    return path.join(app.getPath('userData'), 'catprice.db');
  }
  return path.join(__dirname, '..', 'catprice.db');
}

function getFrontendEntry() {
  if (app.isPackaged) {
    return path.join(app.getAppPath(), 'frontend', 'dist', 'index.html');
  }
  return path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
}

// ─── Backend Lifecycle ────────────────────────────────────────────────────────
async function startBackend() {
  debugLog('Checking for existing backend');
  if (await waitForBackend(5_000)) {
    debugLog('Reusing existing backend server');
    return;
  }

  return new Promise((resolve, reject) => {
    let startupSettled = false;
    const finishStartup = (handler, value) => {
      if (startupSettled) return;
      startupSettled = true;
      handler(value);
    };

    const env = {
      ...process.env,
      PORT: String(BACKEND_PORT),
      HOST: BACKEND_HOST,
      DATABASE_URL: `sqlite:///${getDatabasePath().replace(/\\/g, '/')}`,
    };

    if (app.isPackaged) {
      const backendExe = getPackagedBackendExecutable();
      if (!backendExe) {
        reject(new Error('Packaged backend sidecar not found. Rebuild the desktop bundle.'));
        return;
      }

      debugLog(`Starting packaged backend sidecar: ${backendExe}`);
      backendProcess = spawn(backendExe, [], {
        cwd: path.dirname(backendExe),
        env,
        windowsHide: true,
      });
    } else {
      const python = getPythonExecutable();
      const backendCwd = path.join(__dirname, '..');
      const backendDir = getBackendDir();

      debugLog(`Starting development backend with ${python}`);
      debugLog(`Backend CWD: ${backendCwd}`);
      debugLog(`Backend source dir: ${backendDir}`);

      backendProcess = spawn(
        python,
        [
          '-m', 'uvicorn', 'backend.main:app',
          '--host', BACKEND_HOST,
          '--port', String(BACKEND_PORT),
          '--log-level', 'warning',
        ],
        {
          cwd: backendCwd,
          env,
          windowsHide: true,
        }
      );
    }

    // Keep the most recent stderr lines so we can surface a useful error
    // message (e.g. "port already in use") instead of a generic timeout.
    const stderrTail = [];
    const STDERR_TAIL_MAX = 8;

    backendProcess.stdout.on('data', (d) => debugLog(`[Backend] ${d.toString().trim()}`));
    backendProcess.stderr.on('data', (d) => {
      const text = d.toString().trim();
      debugLog(`[Backend:stderr] ${text}`);
      for (const line of text.split(/\r?\n/)) {
        if (line.trim()) stderrTail.push(line.trim());
      }
      while (stderrTail.length > STDERR_TAIL_MAX) stderrTail.shift();
    });
    backendProcess.on('error', (err) => {
      debugLog(`Backend failed to start: ${err.message}`);
      finishStartup(reject, err);
    });
    backendProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        debugLog(`Backend exited with code ${code}`);
      }
      if (!startupSettled) {
        const tail = stderrTail.join('\n');
        const portInUse = /10048|EADDRINUSE|address already in use/i.test(tail);
        const reason = portInUse
          ? `Port ${BACKEND_PORT} is already in use by another process. Stop any running CatPrice or development backend (e.g. uvicorn) and try again.`
          : `Backend exited during startup (code ${code ?? 'unknown'}).${tail ? `\n\n${tail}` : ''}`;
        finishStartup(reject, new Error(reason));
      }
    });

    waitForBackend(MAX_WAIT_MS).then((ready) => {
      if (ready) {
        debugLog('Backend is ready');
        finishStartup(resolve);
      } else {
        debugLog('Backend startup timed out');
        finishStartup(reject, new Error('Backend startup timed out'));
      }
    });
  });
}

function stopBackend() {
  if (shutdownPromise) return shutdownPromise;
  if (!backendProcess) {
    shutdownPromise = Promise.resolve();
    return shutdownPromise;
  }

  const proc = backendProcess;
  backendProcess = null;

  shutdownPromise = new Promise((resolve) => {
    let settled = false;
    const settle = (reason) => {
      if (settled) return;
      settled = true;
      debugLog(`Backend shutdown settled (${reason})`);
      resolve();
    };

    proc.once('exit', () => settle('child exit'));

    debugLog('Stopping backend (SIGTERM)');
    try {
      proc.kill('SIGTERM');
    } catch (err) {
      debugLog(`Backend SIGTERM failed: ${err.message}`);
    }

    // Escalate to SIGKILL if the child is still alive after the grace period.
    const force = setTimeout(() => {
      if (!proc.killed) {
        debugLog('Backend SIGTERM timed out, sending SIGKILL');
        try { proc.kill('SIGKILL'); } catch (_err) { /* already gone */ }
      }
      // Cap total wait so app.quit() can't hang indefinitely.
      setTimeout(() => settle('forced timeout'), 500);
    }, 3000);
    proc.once('exit', () => clearTimeout(force));
  });

  return shutdownPromise;
}

// ─── Main Window ──────────────────────────────────────────────────────────────
function createMainWindow() {
  debugLog('Creating main window');
  const desktopChromeOptions = process.platform === 'win32'
    ? {
        frame: false,
        autoHideMenuBar: true,
      }
    : process.platform === 'darwin'
      ? { titleBarStyle: 'hiddenInset' }
      : {};

  mainWindow = new BrowserWindow({
    width: 1480,
    height: 940,
    minWidth: 1120,
    minHeight: 720,
    title: 'CatPrice | Catalyst Cost Tool',
    backgroundColor: '#fbf7f1',
    show: false,
    icon: path.join(__dirname, 'icon.png'),
    ...desktopChromeOptions,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webviewTag: false,
      allowRunningInsecureContent: false,
      webSecurity: true,
      safeDialogs: true,
      navigateOnDragDrop: false,
    },
  });

  // Build menu
  const menu = Menu.buildFromTemplate([
    {
      label: 'File',
      submenu: [
        { label: 'New Estimate', accelerator: 'CmdOrCtrl+N', click: () => mainWindow.webContents.send('new-estimate') },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        { label: 'About CatPrice', click: showAbout },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);

  // Development uses Vite. Desktop builds load bundled files directly.
  const isDev = process.env.NODE_ENV === 'development';
  const frontendEntry = getFrontendEntry();

  function showMain() {
    if (mainWindow && !mainWindow.isDestroyed() && !mainWindow.isVisible()) {
      showAndFocusMainWindow('ready-to-show');
    }
  }

  mainWindow.once('ready-to-show', showMain);
  mainWindow.webContents.once('dom-ready', () => showAndFocusMainWindow('dom-ready'));
  mainWindow.webContents.once('did-finish-load', () => {
    showAndFocusMainWindow('did-finish-load');
    sendWindowState();
  });

  // Fallback: force-show after 12 s if ready-to-show never fires
  const showTimer = setTimeout(showMain, 12000);
  mainWindow.once('ready-to-show', () => clearTimeout(showTimer));

  // If the page fails to load, show an inline error so the window appears
  mainWindow.webContents.on('did-fail-load', (event, code, desc, url) => {
    console.error(`[Window] did-fail-load ${url} → ${desc} (${code})`);
    debugLog(`Window failed to load ${url} (${code})`);
    showAndFocusMainWindow('did-fail-load');
    mainWindow.webContents.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(`
<!DOCTYPE html><html><head><style>
body{background:#060b14;color:#ccc;font-family:'Segoe UI Variable Text','Segoe UI','Noto Sans KR','Malgun Gothic',sans-serif;display:flex;
flex-direction:column;align-items:center;justify-content:center;height:100vh;margin:0}
h1{color:#ff4444;font-size:22px}code{background:#1a2a4a;padding:4px 10px;border-radius:4px;color:#00d4ff}
p{color:#7099cc;font-size:14px;max-width:500px;text-align:center}
</style></head><body>
<h1>Could not connect to backend</h1>
<p>Failed to load <code>${url}</code><br><br>${desc}</p>
<p>Try restarting the app. If the issue persists, run <code>start.bat</code> from the command line to see error details.</p>
</body></html>`)}`)
      .catch(() => {});
  });

  if (isDev) {
    debugLog('Loading development frontend URL');
    mainWindow.loadURL('http://localhost:5173').catch((err) => {
      debugLog(`Window loadURL threw: ${err.message}`);
    });
  } else {
    debugLog(`Loading desktop frontend file: ${frontendEntry}`);
    mainWindow.loadFile(frontendEntry, { hash: '/' }).catch((err) => {
      debugLog(`Window loadFile threw: ${err.message}`);
    });
  }

  mainWindow.on('closed', () => { mainWindow = null; });
  mainWindow.on('maximize', sendWindowState);
  mainWindow.on('unmaximize', sendWindowState);
  mainWindow.on('enter-full-screen', sendWindowState);
  mainWindow.on('leave-full-screen', sendWindowState);

  // Open external links in default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (isAllowedExternalUrl(url)) {
      shell.openExternal(url);
    } else {
      debugLog(`Blocked external navigation to ${url}`);
    }
    return { action: 'deny' };
  });

  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (isAppNavigationUrl(url)) {
      return;
    }

    event.preventDefault();
    if (isAllowedExternalUrl(url)) {
      shell.openExternal(url);
    } else {
      debugLog(`Blocked same-window navigation to ${url}`);
    }
  });

  mainWindow.webContents.on('will-attach-webview', (event) => {
    event.preventDefault();
    debugLog('Blocked webview attachment');
  });

  mainWindow.webContents.session.setPermissionRequestHandler((_webContents, _permission, callback) => {
    callback(false);
  });
  if (typeof mainWindow.webContents.session.setPermissionCheckHandler === 'function') {
    mainWindow.webContents.session.setPermissionCheckHandler(() => false);
  }
}

function showAbout() {
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'About CatPrice',
    message: 'CatPrice | Catalyst Cost Tool',
    detail: [
      `Version ${app.getVersion()}`,
      '',
      'Real-time metal price based catalyst manufacturing cost estimator.',
      'Based on CatCost methodology (Baddour et al. 2018, Van Allsburg et al. 2022).',
      '',
      'Copyright 2026 hyunjin.kang | All rights reserved',
    ].join('\n'),
    buttons: ['OK'],
  });
  mainWindow.center();
}

ipcMain.handle('window:minimize', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.minimize();
  }
});

ipcMain.handle('window:toggle-maximize', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;

  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow.maximize();
  }

  sendWindowState();
  return mainWindow.isMaximized();
});

ipcMain.handle('window:close', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.close();
  }
});

ipcMain.handle('window:is-maximized', () => {
  if (!mainWindow || mainWindow.isDestroyed()) return false;
  return mainWindow.isMaximized();
});

// ─── App Lifecycle ────────────────────────────────────────────────────────────
app.whenReady().then(() => {
  if (!gotLock) {
    debugLog('Skipping startup because single-instance lock is not owned');
    app.quit();
    return;
  }

  debugLog('App ready');

  // Open the main window immediately. The frontend renders skeletons until
  // the FastAPI sidecar finishes booting, so a separate splash isn't needed.
  createMainWindow();

  // Start the backend in parallel. Any failure surfaces as an error dialog
  // *after* the window is up, so the user can still see the app shell.
  startBackend()
    .then(() => {
      debugLog('Backend startup complete');
    })
    .catch((err) => {
      debugLog(`Backend startup failure: ${err.message}`);
      dialog.showErrorBox(
        'Backend not running',
        `CatPrice could not start the local server.\n\n${err.message}\n\nMake sure Python 3.11+ is installed and dependencies are set up.\nRun: pip install -r requirements.txt`
      );
    });
});

app.on('render-process-gone', (_event, webContents, details) => {
  debugLog(`Renderer process gone: ${JSON.stringify(details)}`);
  if (mainWindow && webContents.id === mainWindow.webContents.id) {
    dialog.showErrorBox(
      'Renderer Error',
      `The CatPrice window stopped responding (${details.reason}). Please restart the app.`
    );
  }
});

app.on('window-all-closed', () => {
  debugLog('All windows closed');
  // app.quit() triggers `before-quit`, which awaits the backend shutdown.
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  debugLog('App activate');
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  } else {
    showAndFocusMainWindow('activate');
  }
});

app.on('before-quit', (event) => {
  if (appIsQuitting) return;          // already in the shutdown sequence
  if (!backendProcess && !shutdownPromise) return; // nothing to wait for

  event.preventDefault();
  appIsQuitting = true;
  stopBackend().finally(() => {
    debugLog('Backend stopped; exiting app');
    app.exit(0);
  });
});

// Prevent multiple instances
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  debugLog('Another CatPrice instance already owns the single-instance lock');
  app.quit();
} else {
  app.on('second-instance', () => {
    debugLog('Received second-instance event');
    if (mainWindow && !mainWindow.isDestroyed()) {
      showAndFocusMainWindow('second-instance');
    } else if (app.isReady()) {
      createMainWindow();
    }
  });
}
