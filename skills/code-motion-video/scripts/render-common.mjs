import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';

const defaults = { entry: 'index.html', width: 1920, height: 1080, fps: 30, duration: 15, audio: null };
const positive = (value, key) => {
  const n = Number(value);
  if (!Number.isFinite(n) || n <= 0) throw new Error(`${key} must be a positive finite number.`);
  return n;
};
const inside = (root, file) => { const rel = path.relative(root, file); return rel === '' || (!rel.startsWith(`..${path.sep}`) && rel !== '..' && !path.isAbsolute(rel)); };
export const frameName = (index) => `${String(index).padStart(6, '0')}.png`;

export async function getOptions(mode, argv = process.argv.slice(2)) {
  const args = {};
  const values = new Set(['project', 'out', 'width', 'height', 'fps', 'duration', ...(mode === 'preview' ? ['times'] : [])]);
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i].startsWith('--') ? argv[i].slice(2) : '';
    if (key === 'help' || key === 'overwrite' || key === 'check-determinism') { args[key] = true; continue; }
    if (!values.has(key)) throw new Error(`Unknown option: ${argv[i]}`);
    if (args[key] !== undefined) throw new Error(`Duplicate option: --${key}`);
    const value = argv[++i];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for --${key}`);
    args[key] = value;
  }
  if (args.help) {
    console.log(`Usage: node render-${mode}.mjs --project DIR [options]\n\n` +
      `Read DIR/video.config.json. This legacy browser renderer is disabled.\n` +
      `--out DIR       Output directory (default: project/${mode === 'preview' ? 'preview' : 'output'})\n` +
      `--width N --height N --fps N --duration SECONDS  Override project config\n` +
      (mode === 'preview' ? `--times 0,2,5   Preview times; default 3 samples at 10%, 50%, 90%\n` : '') +
      `--check-determinism  Run the optional A-B-A seek consistency check\n` +
      `--overwrite     Replace named output files from an earlier run\n--help          Show help\n\n` +
      `Use official Codex built-in browser tools and their available capabilities for webpages.\n` +
      `Use native background export only with an existing compatible project-native drawing entry.\n` +
      `The built-in browser must not be treated as a local Playwright executable.\n` +
      `See references/rendering-standard.md for the supported workflow.`);
    return null;
  }
  if (!args.project) throw new Error('--project DIR is required.');
  const project = await fs.realpath(path.resolve(args.project));
  const supplied = JSON.parse(await fs.readFile(path.join(project, 'video.config.json'), 'utf8'));
  if (!supplied || typeof supplied !== 'object' || Array.isArray(supplied)) throw new Error('video.config.json must contain an object.');
  const config = { ...defaults, ...supplied };
  for (const key of ['width', 'height', 'fps', 'duration']) config[key] = positive(args[key] ?? config[key], key);
  for (const key of ['width', 'height']) {
    if (!Number.isInteger(config[key]) || config[key] % 2 !== 0) throw new Error(`${key} must be a positive even integer for yuv420p.`);
  }
  const totalFrames = Math.round(config.duration * config.fps);
  if (!Number.isSafeInteger(totalFrames) || totalFrames < 1) throw new Error('duration × fps must produce at least one valid frame.');
  if (typeof config.entry !== 'string' || !config.entry) throw new Error('entry must be a relative file path.');
  const entry = await fs.realpath(path.resolve(project, config.entry));
  if (!inside(project, entry) || !(await fs.stat(entry)).isFile()) throw new Error('entry must be a file inside the project.');
  config.entry = path.relative(project, entry).split(path.sep).join('/');
  if (config.audio !== null) {
    if (typeof config.audio !== 'string' || !config.audio) throw new Error('audio must be null or a local file path.');
    config.audio = await fs.realpath(path.resolve(project, config.audio));
    if (!(await fs.stat(config.audio)).isFile()) throw new Error('audio must point to a local file.');
  }
  let indices;
  if (mode === 'preview') {
    const raw = args.times === undefined ? [0.1, 0.5, 0.9].map(fraction => Math.round(fraction * (totalFrames - 1))) : args.times.split(',').map((value) => {
      if (!value.trim()) throw new Error('--times cannot contain empty values.');
      const seconds = Number(value);
      if (!Number.isFinite(seconds) || seconds < 0 || seconds >= config.duration) throw new Error(`Preview time must be in [0, duration): ${value}`);
      return Math.min(totalFrames - 1, Math.round(seconds * config.fps));
    });
    indices = [...new Set(raw)].sort((a, b) => a - b);
  }
  return { project, out: path.resolve(args.out ?? path.join(project, mode === 'preview' ? 'preview' : 'output')), config, totalFrames, effectiveDuration: totalFrames / config.fps, indices, overwrite: Boolean(args.overwrite), checkDeterminism: Boolean(args['check-determinism']) };
}

export async function prepareOutputs(options, names) {
  await fs.mkdir(options.out, { recursive: true });
  for (const name of names) {
    const target = path.join(options.out, name);
    try {
      const stat = await fs.lstat(target);
      if (!options.overwrite || !stat.isFile() || stat.isSymbolicLink()) throw new Error(`Output exists; use a new --out or --overwrite for regular files: ${target}`);
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
}

export async function openRenderer(options) {
  const error = new Error('外部浏览器采帧入口已禁用；请通过 Codex 内置浏览器的官方工具和实际可用能力完成网页操作。只有项目已有兼容原生后台绘制入口时才用其导出；不能将内置浏览器写成本地 Playwright 可执行路径。');
  error.code = 'EXTERNAL_BROWSER_DISABLED';
  throw error;
}

export function run(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { shell: false, stdio: ['ignore', 'ignore', 'pipe'] });
    let diagnostic = '';
    child.stderr.on('data', data => { diagnostic = (diagnostic + data.toString()).slice(-65536); });
    child.on('error', error => reject(new Error(`${command}: ${error.message}`)));
    child.on('close', code => code === 0 ? resolve() : reject(new Error(`${command} exited ${code}: ${diagnostic}`)));
  });
}

export function manifest(options, renderer) {
  return { schemaVersion: 1, project: options.project, config: options.config, totalFrames: options.totalFrames, effectiveDuration: options.effectiveDuration, deterministicCheck: renderer.deterministicCheck };
}
