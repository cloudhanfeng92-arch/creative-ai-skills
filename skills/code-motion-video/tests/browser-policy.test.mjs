import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import net from 'node:net';
import childProcess from 'node:child_process';
import { syncBuiltinESMExports } from 'node:module';
import { openRenderer, getOptions } from '../scripts/render-common.mjs';

const isDisabled = error => {
  assert.equal(error.code, 'EXTERNAL_BROWSER_DISABLED');
  assert.match(error.message, /Codex 内置浏览器/);
  assert.match(error.message, /已有兼容原生后台绘制入口/);
  return true;
};

test('renderer refuses every configuration before inspecting it', async () => {
  const unreadable = new Proxy({}, { get() { throw new Error('configuration must not be read'); } });
  for (const options of [undefined, null, {}, { project: '/unused', config: { headless: true } }, { config: { headless: false, executablePath: '/unused/chrome' } }, unreadable]) {
    await assert.rejects(openRenderer(options), isDisabled);
  }
});

test('legacy browser environments cannot trigger process or server startup', async t => {
  const startup = [];
  const traps = [[http, 'createServer'], [net.Server.prototype, 'listen'], ...['spawn', 'spawnSync', 'exec', 'execSync', 'execFile', 'execFileSync', 'fork'].map(name => [childProcess, name])];
  for (const [target, name] of traps) t.mock.method(target, name, () => { startup.push(name); throw new Error(`forbidden startup: ${name}`); });
  syncBuiltinESMExports();
  const legacy = {
    PLAYWRIGHT_MODULE_PATH: '/must-not-load/playwright.cjs',
    BROWSER_EXECUTABLE_PATH: '/must-not-run/chrome',
    CHROMIUM_EXECUTABLE: '/must-not-run/chromium',
    PUPPETEER_EXECUTABLE_PATH: '/must-not-run/chrome-for-testing',
    PWDEBUG: '1',
  };
  const previous = Object.fromEntries(Object.keys(legacy).map(key => [key, process.env[key]]));
  try {
    Object.assign(process.env, legacy);
    await assert.rejects(openRenderer({ project: '/unused', config: { width: 1920, height: 1080 } }), isDisabled);
    assert.deepEqual(startup, []);
    for (const [key, value] of Object.entries(legacy)) assert.equal(process.env[key], value);
  } finally {
    for (const [key, value] of Object.entries(previous)) {
      if (value === undefined) delete process.env[key]; else process.env[key] = value;
    }
    t.mock.restoreAll();
    syncBuiltinESMExports();
  }
});

test('help describes the disabled renderer without installing external browsers', async t => {
  let output = '';
  t.mock.method(console, 'log', value => { output += value; });
  assert.equal(await getOptions('video', ['--help']), null);
  assert.match(output, /Codex built-in browser/);
  assert.match(output, /project-native drawing entry/);
  assert.doesNotMatch(output, /npm install|playwright install|BROWSER_EXECUTABLE_PATH|PLAYWRIGHT_MODULE_PATH/);
});

test('both legacy CLI commands reject before reading config or creating outputs', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'code-browser-guard-'));
  try {
    for (const mode of ['preview', 'video']) {
      const file = fileURLToPath(new URL(`../scripts/render-${mode}.mjs`, import.meta.url));
      await assert.rejects(promisify(childProcess.execFile)(process.execPath, [file, '--project', root], { cwd: root }), error => {
        assert.equal(error.code, 1);
        assert.match(error.stderr, /EXTERNAL_BROWSER_DISABLED/);
        assert.doesNotMatch(error.stderr, /ENOENT|ffmpeg exited/);
        return true;
      });
      assert.deepEqual(await fs.readdir(root), []);
    }
  } finally { await fs.rm(root, { recursive: true, force: true }); }
});
