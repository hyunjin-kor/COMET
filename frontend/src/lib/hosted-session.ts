// Browser identity confirmation only. The HttpOnly cookie is the credential.
let mode: 'unknown' | 'desktop' | 'hosted' = 'unknown';
let accountId: string | null = null;
let generation = 0;
export const SESSION_INVALID_EVENT = 'comet:session-invalid';
export const SESSION_CHANGE_KEY = 'comet.session.change';

function clearPrivateDrafts() {
  for (const name of ['localStorage', 'sessionStorage'] as const) {
    try {
      window[name].removeItem('comet_calculator_draft');
      window[name].removeItem('comet_calculator_result');
    } catch { /* Storage may be disabled; in-memory state is also unmounted. */ }
  }
}

export function setBrowserAccount(nextMode: 'desktop' | 'hosted', nextId: string | null) {
  if (nextMode === 'hosted' && (mode !== nextMode || accountId !== nextId)) {
    // Hosted refresh starts clean as well: no private draft survives bootstrap.
    clearPrivateDrafts();
    generation += 1;
  }
  mode = nextMode;
  accountId = nextId;
}

export function hostedRequestState() {
  return { mode, accountId, generation };
}

export function invalidateBrowserAccount() {
  if (mode !== 'hosted') return;
  clearPrivateDrafts();
  accountId = null;
  generation += 1;
  window.dispatchEvent(new Event(SESSION_INVALID_EVENT));
}

export function notifyOtherTabs() {
  try { window.localStorage.setItem(SESSION_CHANGE_KEY, crypto.randomUUID()); }
  catch { /* The server account header still rejects stale-tab requests. */ }
}
