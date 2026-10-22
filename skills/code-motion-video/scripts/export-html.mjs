#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';

const HELP = `Export the basic motion-video template as one offline playable HTML file.

Usage:
  node export-html.mjs --project DIR --out /absolute/output/film.html [options]

Options:
  --project DIR  Project containing video.config.json and the basic template.
  --out FILE     Absolute output HTML path; existing files are protected.
  --title TEXT   Page title (default: project directory name).
  --overwrite    Replace an existing regular output file.
  --help         Show this help.

Embeds the entry HTML's CSS, src/main.js, configuration and optional local audio.
Extra scripts, external resources and module imports need a project-specific
bundling method. This is a template exporter, not a general website bundler.
`;
const unsupported = detail => new Error(`Unsupported template extension: ${detail}. Use a project-specific bundling method to produce an offline HTML file.`);
const inside = (root, file) => { const relative = path.relative(root, file); return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative)); };
const htmlText = text => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const inlineJson = value => JSON.stringify(value).replaceAll('<', '\\u003c').replaceAll('\u2028', '\\u2028').replaceAll('\u2029', '\\u2029');

async function main() {
  const options = {};
  for (let index = 0; index < process.argv.length - 2; index += 1) {
    const args = process.argv.slice(2);
    const key = args[index];
    if (key === '--help' || key === '--overwrite') { options[key.slice(2)] = true; continue; }
    if (!['--project', '--out', '--title'].includes(key)) throw new Error(`Unknown option: ${key}`);
    if (options[key.slice(2)] !== undefined) throw new Error(`Duplicate option: ${key}`);
    const value = args[++index];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for ${key}`);
    options[key.slice(2)] = value;
  }
  if (options.help) { console.log(HELP); return; }
  if (!options.project || !options.out || !path.isAbsolute(options.out)) throw new Error('--project DIR and an absolute --out FILE are required.');
  if (!/\.html?$/i.test(options.out)) throw new Error('--out must end in .html or .htm.');
  const project = await fs.realpath(path.resolve(options.project));
  const config = JSON.parse(await fs.readFile(path.join(project, 'video.config.json'), 'utf8'));
  if (!config || typeof config !== 'object' || Array.isArray(config)) throw new Error('video.config.json must contain an object.');
  for (const key of ['width', 'height', 'duration']) if (!Number.isFinite(Number(config[key])) || Number(config[key]) <= 0) throw new Error(`Config ${key} must be positive.`);
  const entry = await fs.realpath(path.resolve(project, config.entry ?? 'index.html'));
  const mainPath = await fs.realpath(path.join(project, 'src/main.js'));
  if (!inside(project, entry) || !inside(project, mainPath)) throw new Error('Entry HTML and src/main.js must be inside the project.');
  if (path.resolve(options.out) === entry) throw new Error('Output must not replace the editable entry HTML.');
  let html = await fs.readFile(entry, 'utf8');
  let script = await fs.readFile(mainPath, 'utf8');
  const scripts = [...html.matchAll(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi)];
  if (scripts.length !== 1 || !/^<script\s+type=["']module["']\s+src=["']\.\/src\/main\.js["']\s*>\s*<\/script\s*>$/i.test(scripts[0][0])) throw unsupported('expected exactly the template module tag for ./src/main.js');
  if (!script.includes('#video-inline-config') || !script.includes('window.seek')) throw unsupported('main.js does not implement the inline configuration and seek contract');
  const withoutMain = html.replace(scripts[0][0], '');
  if (/<(?:base|iframe|object|embed)\b/i.test(withoutMain)) throw unsupported('embedded pages or objects');
  const attributes = [...withoutMain.matchAll(/\b(?:src|href|poster|srcset|data|xlink:href)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/gi)];
  for (const match of attributes) {
    const url = match[1] ?? match[2] ?? match[3];
    if (url && !url.startsWith('data:') && !url.startsWith('#')) throw unsupported(`HTML resource ${url}`);
  }
  if (/@import\b/i.test(withoutMain)) throw unsupported('CSS imports');
  for (const match of withoutMain.matchAll(/url\(\s*(["']?)(.*?)\1\s*\)/gi)) {
    if (!match[2].trim().startsWith('data:') && !match[2].trim().startsWith('#')) throw unsupported(`CSS resource ${match[2]}`);
  }
  if (/\bimport\s*(?:\(|["'{*])|^\s*(?:import|export)\b/m.test(script)) throw unsupported('JavaScript module imports or exports');
  // Remove only the known template configuration fallback; offline output never fetches.
  const configFetch = /await fetch\('\.\/video\.config\.json'\)\.then\(\(response\) => \{\s*if \(!response\.ok\) throw new Error\(`Cannot load video\.config\.json: HTTP \$\{response\.status\}`\);\s*return response\.json\(\);\s*\}\)/;
  script = script.replace(configFetch, `(() => { throw new Error('Embedded video configuration is missing.'); })()`);
  const resourceCode = script.replace(/new Audio\(config\.audio\)/g, 'null');
  if (/\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|Worker|importScripts)\s*\(|\bnew\s+(?:Image|Audio)\s*\(|\.src\s*=|\.load\s*\(|\bsetAttribute\s*\(\s*['"](?:src|href)|https?:\/\/|file:\/\//i.test(resourceCode)) throw unsupported('additional JavaScript resource loading');
  if (config.audio) {
    if (typeof config.audio !== 'string' || /^(?:https?:|data:|file:)/i.test(config.audio)) throw unsupported('audio must be an existing local file path');
    const audioPath = await fs.realpath(path.resolve(project, config.audio));
    if (!(await fs.stat(audioPath)).isFile()) throw new Error('Configured audio is not a regular file.');
    const mime = { '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.m4a': 'audio/mp4', '.mp4': 'audio/mp4', '.aac': 'audio/aac', '.ogg': 'audio/ogg', '.opus': 'audio/ogg', '.flac': 'audio/flac', '.webm': 'audio/webm' }[path.extname(audioPath).toLowerCase()];
    if (!mime) throw unsupported(`audio format ${path.extname(audioPath)}`);
    config.audio = `data:${mime};base64,${(await fs.readFile(audioPath)).toString('base64')}`;
  } else config.audio = null;
  const title = options.title ?? path.basename(project);
  if (!/<title\b[^>]*>[\s\S]*?<\/title>/i.test(html)) throw unsupported('missing title element');
  html = html.replace(/<title\b[^>]*>[\s\S]*?<\/title>/i, () => `<title>${htmlText(title)}</title>`);
  const safeScript = script.replace(/<\/script/gi, '<\\/script').replace(/<!--/g, '<\\!--');
  html = html.replace(scripts[0][0], () => `<script id="video-inline-config" type="application/json">${inlineJson(config)}</script>\n    <script type="module">\n${safeScript}\n</script>`);
  try {
    const stat = await fs.lstat(options.out);
    if (!options.overwrite || !stat.isFile() || stat.isSymbolicLink()) throw new Error('Output exists; use a new --out or --overwrite for a regular file.');
  } catch (error) { if (error.code !== 'ENOENT') throw error; }
  await fs.mkdir(path.dirname(options.out), { recursive: true });
  await fs.writeFile(options.out, html, { flag: options.overwrite ? 'w' : 'wx' });
  console.log(JSON.stringify({ html: options.out, title, audioEmbedded: Boolean(config.audio), bytes: Buffer.byteLength(html) }, null, 2));
}

try { await main(); } catch (error) { console.error(error.message); process.exitCode = 1; }
