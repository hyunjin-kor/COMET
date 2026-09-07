import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(new URL('../frontend/package.json', import.meta.url));
const ts = require('typescript');
const source = readFileSync(new URL('../frontend/src/lib/hosted-session.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText;

test('hosted identity changes clear private drafts, preserve preferences and invalidate responses', async () => {
  const original = globalThis.window;
  const persistent = new Map([['comet_lang', 'ko'], ['comet_calculator_draft', 'legacy-secret']]);
  const temporary = new Map([['comet_calculator_result', 'first-account-result']]);
  const events = [];
  globalThis.window = {
    localStorage: { removeItem: (key) => persistent.delete(key), setItem: (key, value) => persistent.set(key, value) },
    sessionStorage: { removeItem: (key) => temporary.delete(key) },
    dispatchEvent: (event) => events.push(event.type),
  };
  try {
    const session = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`);
    session.setBrowserAccount('desktop', null);
    assert.equal(temporary.get('comet_calculator_result'), 'first-account-result');
    session.setBrowserAccount('hosted', 'first-account');
    assert.equal(temporary.size, 0);
    assert.equal(persistent.get('comet_lang'), 'ko');
    assert.ok(!persistent.has('comet_calculator_draft'));
    temporary.set('comet_calculator_draft', 'private-input');
    const generation = session.hostedRequestState().generation;
    session.setBrowserAccount('hosted', 'first-account');
    assert.equal(temporary.size, 1); // An ordinary status refresh preserves editing.
    session.setBrowserAccount('hosted', 'second-account');
    assert.equal(temporary.size, 0);
    assert.ok(session.hostedRequestState().generation > generation);
    session.invalidateBrowserAccount();
    assert.equal(session.hostedRequestState().accountId, null);
    assert.deepEqual(events, [session.SESSION_INVALID_EVENT]);
  } finally { globalThis.window = original; }
});
