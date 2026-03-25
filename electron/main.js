/**
 * CatPrice Electron Main Process
 * Launches the FastAPI backend as a sidecar and shows the React frontend
 */

const { app, BrowserWindow, shell, dialog, Menu, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

// Prevent black-window rendering issues on some Windows GPU/driver setups.
app.disableHardwareAcceleration();

// ─── Configuration ───────────────────────────────────────────────────────────
const BACKEND_PORT = 8765;      // Avoid conflicts with other services
const BACKEND_HOST = '127.0.0.1';
const BACKEND_URL  = `http://${BACKEND_HOST}:${BACKEND_PORT}`;
const HEALTH_URL   = `${BACKEND_URL}/api/health`;
const MAX_WAIT_MS  = 30_000;    // 30 seconds max startup wait
const POLL_INTERVAL_MS = 500;

// ─── State ────────────────────────────────────────────────────────────────────
let mainWindow = null;
let backendProcess = null;
let splashWindow = null;
let tray = null;

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
  mainWindow.center();
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

    const poll = () => {
      const req = http.get(HEALTH_URL, (res) => {
        res.resume();
        finish(res.statusCode === 200);
      });

      req.setTimeout(2000, () => {
        req.destroy();
      });

      req.on('error', () => {
        if (Date.now() - start >= timeoutMs) {
          finish(false);
        } else {
          setTimeout(poll, POLL_INTERVAL_MS);
        }
      });
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

// ─── Backend Lifecycle ────────────────────────────────────────────────────────
async function startBackend() {
  debugLog('Checking for existing backend');
  if (await waitForBackend(5_000)) {
    debugLog('Reusing existing backend server');
    return;
  }

  return new Promise((resolve, reject) => {
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

    backendProcess.stdout.on('data', (d) => debugLog(`[Backend] ${d.toString().trim()}`));
    backendProcess.stderr.on('data', (d) => debugLog(`[Backend:stderr] ${d.toString().trim()}`));
    backendProcess.on('error', (err) => {
      debugLog(`Backend failed to start: ${err.message}`);
      reject(err);
    });
    backendProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        debugLog(`Backend exited with code ${code}`);
      }
    });

    waitForBackend(MAX_WAIT_MS).then((ready) => {
      if (ready) {
        debugLog('Backend is ready');
        resolve();
      } else {
        debugLog('Backend startup timed out');
        reject(new Error('Backend startup timed out'));
      }
    });
  });
}

function stopBackend() {
  if (backendProcess) {
    debugLog('Stopping backend');
    backendProcess.kill('SIGTERM');
    // Force kill after 3 seconds
    setTimeout(() => {
      if (backendProcess && !backendProcess.killed) {
        backendProcess.kill('SIGKILL');
      }
    }, 3000);
    backendProcess = null;
  }
}

// ─── Splash Screen ────────────────────────────────────────────────────────────
function createSplashWindow() {
  debugLog('Creating splash window');
  splashWindow = new BrowserWindow({
    width: 480,
    height: 300,
    frame: false,
    transparent: false,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    backgroundColor: '#060b14',
    webPreferences: { nodeIntegration: false },
  });

  const splashHTML = `
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: linear-gradient(135deg, #0f1b35 0%, #060b14 100%);
    border: 1px solid #00d4ff44;
    border-radius: 16px;
    color: white;
    font-family: 'Segoe UI', Arial, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    overflow: hidden;
  }
  .logo { font-size: 52px; font-weight: 800; letter-spacing: 2px; margin-bottom: 8px; }
  .logo span.cat { color: #00d4ff; }
  .logo span.price { color: #ffd700; }
  .subtitle { color: #5580aa; font-size: 13px; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 32px; }
  .spinner {
    width: 40px; height: 40px;
    border: 3px solid #1a2a4a;
    border-top: 3px solid #00d4ff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 16px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .status { color: #7099cc; font-size: 14px; }
  .version { position: absolute; bottom: 16px; color: #2a3a5a; font-size: 11px; }
</style>
</head>
<body>
  <div class="logo"><span class="cat">Cat</span><span class="price">Price</span></div>
  <div class="subtitle">Catalyst Cost Tool</div>
  <div class="spinner"></div>
  <div class="status">Starting backend server...</div>
  <div class="version">v${app.getVersion()}</div>
</body>
</html>`;

  splashWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(splashHTML)}`);
  splashWindow.show();
}

// ─── Main Window ──────────────────────────────────────────────────────────────
function createMainWindow() {
  debugLog('Creating main window');
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    title: 'CatPrice | Catalyst Cost Tool',
    backgroundColor: '#060b14',
    show: false,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
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
        { label: 'CatPrice Documentation', click: () => shell.openExternal('https://github.com/hyunjin-kor/CatPrice') },
        { label: 'About CatPrice', click: showAbout },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);

  // Load from backend-served frontend (in prod) or Vite dev server
  // dev mode: NODE_ENV=development AND a Vite server is expected on 5173
  const isDev = process.env.NODE_ENV === 'development';
  const packagedIndex = path.join(app.getAppPath(), 'frontend', 'dist', 'index.html');

  function showMain() {
    if (mainWindow && !mainWindow.isDestroyed() && !mainWindow.isVisible()) {
      if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.close();
        splashWindow = null;
      }
      showAndFocusMainWindow('ready-to-show');
    }
  }

  mainWindow.once('ready-to-show', showMain);
  mainWindow.webContents.once('dom-ready', () => showAndFocusMainWindow('dom-ready'));
  mainWindow.webContents.once('did-finish-load', () => showAndFocusMainWindow('did-finish-load'));

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
body{background:#060b14;color:#ccc;font-family:'Segoe UI',sans-serif;display:flex;
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
  } else if (app.isPackaged) {
    debugLog(`Loading packaged frontend file: ${packagedIndex}`);
    mainWindow.loadFile(packagedIndex).catch((err) => {
      debugLog(`Window loadFile threw: ${err.message}`);
    });
  } else {
    debugLog(`Loading backend frontend URL: ${BACKEND_URL}`);
    mainWindow.loadURL(BACKEND_URL).catch((err) => {
      debugLog(`Window loadURL threw: ${err.message}`);
    });
  }

  mainWindow.on('closed', () => { mainWindow = null; });

  // Open external links in default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) shell.openExternal(url);
    return { action: 'deny' };
  });
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
      'Copyright 2026 hyunjin-kor | All rights reserved',
    ].join('\n'),
    buttons: ['OK'],
  });
}

// ─── App Lifecycle ────────────────────────────────────────────────────────────
app.whenReady().then(async () => {
  if (!gotLock) {
    debugLog('Skipping startup because single-instance lock is not owned');
    app.quit();
    return;
  }

  debugLog('App ready');
  createSplashWindow();

  try {
    await startBackend();
  } catch (err) {
    debugLog(`Backend startup failure: ${err.message}`);
    dialog.showErrorBox(
      'Backend Error',
      `Could not start the CatPrice server.\n\n${err.message}\n\nMake sure Python 3.11+ is installed and dependencies are set up.\nRun: pip install -r requirements.txt`
    );
    app.quit();
    return;
  }

  createMainWindow();
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
  stopBackend();
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

app.on('before-quit', () => stopBackend());

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
    } else if (splashWindow && !splashWindow.isDestroyed()) {
      debugLog('Showing splash window for second-instance');
      splashWindow.show();
      splashWindow.moveTop();
      splashWindow.focus();
    } else if (app.isReady()) {
      createMainWindow();
    }
  });
}
