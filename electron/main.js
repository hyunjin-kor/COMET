/**
 * CatPrice Electron Main Process
 * Launches the FastAPI backend as a sidecar and shows the React frontend
 */

const { app, BrowserWindow, shell, dialog, Menu, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

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

// ─── Backend Lifecycle ────────────────────────────────────────────────────────
async function startBackend() {
  if (await waitForBackend(5_000)) {
    console.log('[Backend] Reusing existing server');
    return;
  }

  return new Promise((resolve, reject) => {
    const python = getPythonExecutable();
    const backendDir = getBackendDir();
    const mainPy = path.join(backendDir, '..', 'backend', 'main.py');
    const actualMainPy = app.isPackaged
      ? path.join(backendDir, 'main.py')
      : path.join(__dirname, '..', 'backend', 'main.py');

    console.log(`[Backend] Starting: ${python} -m uvicorn backend.main:app`);
    console.log(`[Backend] CWD: ${path.join(__dirname, '..')}`);

    const env = {
      ...process.env,
      PORT: String(BACKEND_PORT),
      HOST: BACKEND_HOST,
      DATABASE_URL: `sqlite:///${path.join(__dirname, '..', 'catprice.db')}`,
    };

    backendProcess = spawn(
      python,
      [
        '-m', 'uvicorn', 'backend.main:app',
        '--host', BACKEND_HOST,
        '--port', String(BACKEND_PORT),
        '--log-level', 'warning',
      ],
      {
        cwd: app.isPackaged ? process.resourcesPath : path.join(__dirname, '..'),
        env,
        windowsHide: true,
      }
    );

    backendProcess.stdout.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));
    backendProcess.stderr.on('data', (d) => console.error(`[Backend] ${d.toString().trim()}`));
    backendProcess.on('error', (err) => {
      console.error('[Backend] Failed to start:', err);
      reject(err);
    });
    backendProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.error(`[Backend] Exited with code ${code}`);
      }
    });

    waitForBackend(MAX_WAIT_MS).then((ready) => {
      if (ready) {
        console.log('[Backend] Ready!');
        resolve();
      } else {
        reject(new Error('Backend startup timed out'));
      }
    });
  });
}

function stopBackend() {
  if (backendProcess) {
    console.log('[Backend] Stopping...');
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
  splashWindow = new BrowserWindow({
    width: 480,
    height: 300,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
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
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    title: 'CatPrice — Catalyst Cost Tool',
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
  const startUrl = isDev ? `http://localhost:5173` : `${BACKEND_URL}`;

  function showMain() {
    if (mainWindow && !mainWindow.isDestroyed() && !mainWindow.isVisible()) {
      if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.close();
        splashWindow = null;
      }
      mainWindow.show();
      mainWindow.focus();
    }
  }

  mainWindow.once('ready-to-show', showMain);

  // Fallback: force-show after 12 s if ready-to-show never fires
  const showTimer = setTimeout(showMain, 12000);
  mainWindow.once('ready-to-show', () => clearTimeout(showTimer));

  // If the page fails to load, show an inline error so the window appears
  mainWindow.webContents.on('did-fail-load', (event, code, desc, url) => {
    console.error(`[Window] did-fail-load ${url} → ${desc} (${code})`);
    showMain();
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

  mainWindow.loadURL(startUrl).catch(err => {
    console.error('[Window] loadURL threw:', err);
  });

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
    message: 'CatPrice — Catalyst Cost Tool',
    detail: [
      `Version ${app.getVersion()}`,
      '',
      'Real-time metal price based catalyst manufacturing cost estimator.',
      'Based on CatCost methodology (Baddour et al. 2018, Van Allsburg et al. 2022).',
      '',
      '© 2024 CatPrice Contributors | MIT License',
    ].join('\n'),
    buttons: ['OK'],
  });
}

// ─── App Lifecycle ────────────────────────────────────────────────────────────
app.whenReady().then(async () => {
  createSplashWindow();

  try {
    await startBackend();
  } catch (err) {
    console.error('Backend failed to start:', err);
    dialog.showErrorBox(
      'Backend Error',
      `Could not start the CatPrice server.\n\n${err.message}\n\nMake sure Python 3.11+ is installed and dependencies are set up.\nRun: pip install -r requirements.txt`
    );
    app.quit();
    return;
  }

  createMainWindow();
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
});

app.on('before-quit', () => stopBackend());

// Prevent multiple instances
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}
