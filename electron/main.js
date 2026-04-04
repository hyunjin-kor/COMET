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
const BACKEND_PORT = 8765;      // Avoid conflicts with other services
const BACKEND_HOST = '127.0.0.1';
const BACKEND_URL  = `http://${BACKEND_HOST}:${BACKEND_PORT}`;
const HEALTH_URL   = `${BACKEND_URL}/api/health`;
const MAX_WAIT_MS  = 30_000;    // 30 seconds max startup wait
const POLL_INTERVAL_MS = 500;
const ALLOWED_EXTERNAL_HOSTS = new Set([
  'github.com',
  'sigmaaldrich.com',
  'nature.com',
  'pubmed.ncbi.nlm.nih.gov',
  'naos-be.zcu.cz',
  'metals.dev',
  'metalpriceapi.com',
  'bls.gov',
]);

// ─── State ────────────────────────────────────────────────────────────────────
let mainWindow = null;
let backendProcess = null;
let splashWindow = null;

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

function sendWindowState() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  mainWindow.webContents.send('window-state-changed', {
    isMaximized: mainWindow.isMaximized(),
  });
}

const BRAND_MARK_SVG = `
<svg viewBox="0 0 512 512" width="42" height="42" fill="none" aria-hidden="true">
  <defs>
    <linearGradient id="cp-bg" x1="86" y1="64" x2="426" y2="448" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#171c24"/>
      <stop offset="100%" stop-color="#2a313d"/>
    </linearGradient>
    <linearGradient id="cp-frame" x1="192" y1="134" x2="320" y2="362" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#f1f6ff"/>
      <stop offset="100%" stop-color="#a1b1c8"/>
    </linearGradient>
    <linearGradient id="cp-signal" x1="154" y1="338" x2="358" y2="208" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#3ac8ff"/>
      <stop offset="100%" stop-color="#49e0c1"/>
    </linearGradient>
  </defs>

  <rect x="40" y="40" width="432" height="432" rx="110" fill="url(#cp-bg)" />
  <rect x="54" y="54" width="404" height="404" rx="96" fill="none" stroke="#3c4659" stroke-width="8" />
  <g opacity="0.16" stroke="#d8e1ef" stroke-width="4" stroke-linecap="round">
    <path d="M156 166H356" />
    <path d="M156 214H356" />
    <path d="M156 262H356" />
    <path d="M156 310H356" />
    <path d="M156 358H356" />
    <path d="M192 142V382" />
    <path d="M256 142V382" />
    <path d="M320 142V382" />
  </g>
  <path
    d="M214 132 H298 L320 176 V308
       C320 338 296 362 266 362
       H246
       C216 362 192 338 192 308
       V176
       Z"
    fill="none"
    stroke="url(#cp-frame)"
    stroke-width="20"
    stroke-linejoin="round"
  />
  <path
    d="M204 232 H308 V298
       C308 317 293 332 274 332
       H238
       C219 332 204 317 204 298
       Z"
    fill="#243240"
  />
  <g fill="#e7eef8">
    <circle cx="228" cy="256" r="12" />
    <circle cx="256" cy="240" r="12" />
    <circle cx="284" cy="256" r="12" />
    <circle cx="240" cy="286" r="12" />
    <circle cx="268" cy="286" r="12" />
  </g>
  <path
    d="M154 338
       C194 320 226 304 258 286
       C292 266 324 240 358 208"
    fill="none"
    stroke="url(#cp-signal)"
    stroke-width="18"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
  <g fill="#171c24" stroke="#49dec6" stroke-width="7">
    <circle cx="154" cy="338" r="11" />
    <circle cx="258" cy="286" r="11" />
    <circle cx="358" cy="208" r="11" />
  </g>
</svg>`;

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
  if (splashWindow && !splashWindow.isDestroyed()) {
    splashWindow.close();
    splashWindow = null;
  }
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

    backendProcess.stdout.on('data', (d) => debugLog(`[Backend] ${d.toString().trim()}`));
    backendProcess.stderr.on('data', (d) => debugLog(`[Backend:stderr] ${d.toString().trim()}`));
    backendProcess.on('error', (err) => {
      debugLog(`Backend failed to start: ${err.message}`);
      finishStartup(reject, err);
    });
    backendProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        debugLog(`Backend exited with code ${code}`);
      }
      if (!startupSettled) {
        finishStartup(reject, new Error(`Backend exited during startup (code ${code ?? 'unknown'})`));
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
    width: 560,
    height: 356,
    frame: false,
    transparent: false,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    backgroundColor: '#091321',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  const splashHTML = `
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background:
      radial-gradient(circle at 16% 18%, rgba(120, 242, 208, 0.16), transparent 0 26%),
      radial-gradient(circle at 84% 12%, rgba(239, 195, 108, 0.14), transparent 0 22%),
      linear-gradient(160deg, #0a1320 0%, #101d31 52%, #09111d 100%);
    color: #f8fafc;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    overflow: hidden;
    padding: 14px;
  }
  body::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px),
      linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
    background-size: 84px 84px;
    mask-image: radial-gradient(circle at center, black 22%, transparent 82%);
    opacity: 0.5;
  }
  .panel {
    position: relative;
    width: 100%;
    min-height: 100%;
    padding: 18px 18px 16px;
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
    box-shadow: 0 22px 52px rgba(0, 0, 0, 0.28);
    backdrop-filter: blur(18px);
    display: flex;
    flex-direction: column;
  }
  .panel::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: radial-gradient(circle at top left, rgba(120, 242, 208, 0.16), transparent 0 34%);
    pointer-events: none;
  }
  .row {
    position: relative;
    display: flex;
    align-items: center;
    gap: 14px;
    z-index: 1;
  }
  .mark {
    width: 64px;
    height: 64px;
    border-radius: 22px;
    display: grid;
    place-items: center;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
  }
  .eyebrow {
    color: #94a3b8;
    font-size: 11px;
    letter-spacing: 0.28em;
    text-transform: uppercase;
  }
  .logo {
    margin-top: 4px;
    font-size: 34px;
    font-weight: 700;
    letter-spacing: -0.045em;
    line-height: 1;
    font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
  }
  .logo span.cat { color: #f8fafc; }
  .logo span.price { color: #78f2d0; }
  .subtitle {
    margin-top: 8px;
    max-width: 300px;
    color: #cbd5e1;
    font-size: 13px;
    line-height: 1.5;
  }
  .meta {
    position: relative;
    z-index: 1;
    margin-top: 16px;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
  }
  .stat {
    padding: 12px 12px 13px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.04);
  }
  .stat .label {
    color: #94a3b8;
    font-size: 10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
  }
  .stat .value {
    margin-top: 8px;
    color: #f8fafc;
    font-size: 15px;
    font-weight: 600;
  }
  .progress {
    position: relative;
    z-index: 1;
    margin-top: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .track {
    flex: 1;
    height: 9px;
    overflow: hidden;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
  }
  .bar {
    height: 100%;
    width: 42%;
    border-radius: inherit;
    background: linear-gradient(90deg, #78f2d0, #efc36c);
    animation: loading 1.5s ease-in-out infinite;
    transform-origin: left center;
  }
  .status {
    position: relative;
    z-index: 1;
    margin-top: 10px;
    color: #cbd5e1;
    font-size: 12.5px;
    line-height: 1.45;
  }
  .version {
    position: relative;
    z-index: 1;
    margin-top: auto;
    padding-top: 10px;
    color: #64748b;
    font-size: 11px;
  }
  @keyframes loading {
    0% { transform: translateX(-38%) scaleX(0.72); opacity: 0.78; }
    50% { transform: translateX(18%) scaleX(1); opacity: 1; }
    100% { transform: translateX(128%) scaleX(0.72); opacity: 0.78; }
  }
</style>
</head>
<body>
  <div class="panel">
    <div class="row">
      <div class="mark">${BRAND_MARK_SVG}</div>
      <div>
        <div class="eyebrow">Desktop Workspace</div>
        <div class="logo"><span class="cat">Cat</span><span class="price">Price</span></div>
        <div class="subtitle">Live metals, catalyst cost intelligence, and process economics loading into the desktop workspace.</div>
      </div>
    </div>
    <div class="meta">
      <div class="stat"><div class="label">Mode</div><div class="value">Desktop launch</div></div>
      <div class="stat"><div class="label">Engine</div><div class="value">FastAPI shell</div></div>
      <div class="stat"><div class="label">Focus</div><div class="value">Cost studio</div></div>
    </div>
    <div class="progress"><div class="track"><div class="bar"></div></div></div>
    <div class="status">Starting the backend and fitting the market workspace to the window...</div>
    <div class="version">v${app.getVersion()}</div>
  </div>
</body>
</html>`;

  splashWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(splashHTML)}`);
  splashWindow.show();
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
      if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.close();
        splashWindow = null;
      }
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
      'Copyright 2026 CatPrice contributors | All rights reserved',
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
