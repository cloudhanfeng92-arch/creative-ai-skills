import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

// Only output naming/ownership is shared. This module does not pick a visual style.
export function safeTitle(title) {
  if (typeof title !== 'string' || !title.trim() || /【|】/.test(title)) {
    throw new Error('填写本条实际视频名称；不得使用空标题或占位标题');
  }
  const replacements = { '<':'＜', '>':'＞', ':':'：', '"':'＂', '/':'／', '\\':'＼', '|':'｜', '?':'？', '*':'＊' };
  let stem = title.normalize('NFC')
    .replace(/[<>:"/\\|?*]/g, char => replacements[char])
    .replace(/[\u0000-\u001f\u007f-\u009f\u202a-\u202e\u2066-\u2069]/g, ' ')
    .replace(/\s+/gu, ' ').trim().replace(/[. ]+$/g, '');
  if (!stem || /^\.+$/.test(stem)) throw new Error('视频名称清理后为空，请使用有意义的名称');
  if (stem.startsWith('.')) stem = '_' + stem;
  if (/^(con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\.|$)/i.test(stem)) stem = '_' + stem;
  // Reserve space for role suffixes on byte-limited file systems; do not split Unicode.
  let shortened = '';
  for (const char of stem) {
    if (Buffer.byteLength(shortened + char, 'utf8') > 180) break;
    shortened += char;
  }
  return shortened.replace(/[. ]+$/g, '');
}

export function artifactNames(title, revision = null) {
  const suffix = revision == null || revision === '' ? '' : '_' + safeTitle(String(revision));
  if (Buffer.byteLength(suffix, 'utf8') > 32) throw new Error('outputRevision过长；使用简短版本后缀，例如v2');
  const stem = safeTitle(title) + suffix;
  return Object.freeze({
    stem,
    video: `${stem}.mp4`,
    html: `${stem}.html`,
    cover: `${stem}_封面.png`,
    source: `${stem}_源码.zip`,
    sourceRoot: `${stem}_源码`,
    partialVideo: `${stem}.partial.mp4`
  });
}

const outputKeys = ['video', 'html', 'cover', 'source', 'partialVideo'];
export function outputPaths(directory, names) {
  return Object.fromEntries(outputKeys.map(key => [key, path.join(directory, names[key])]));
}

export async function claimArtifacts(c) {
  // The same project may update its outputs. Do not overwrite unowned, same-name files.
  await fs.mkdir(c.out, { recursive: true });
  const indexPath = path.join(c.out, 'artifact-index.json');
  let index;
  try { index = JSON.parse(await fs.readFile(indexPath, 'utf8')); }
  catch (error) { if (error.code !== 'ENOENT') throw error; index = { schemaVersion: 1, entries: {} }; }
  if (index.schemaVersion !== 1 || !index.entries || typeof index.entries !== 'object') {
    throw new Error('artifact-index.json格式不正确；不要覆盖已有交付文件');
  }
  const key = crypto.createHash('sha256').update(c.names.stem).digest('hex');
  const owner = crypto.createHash('sha256').update(c.configPath).digest('hex');
  const previous = index.entries[key];
  const ours = previous?.owner === owner && previous?.title === c.title;
  for (const name of outputKeys) {
    let present = false;
    try { await fs.lstat(c.files[name]); present = true; }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (present && !ours && c.overwriteOutputs !== true) {
      throw new Error(`同名文件不属于当前项目：${c.files[name]}。为整组设置outputRevision，或仅在用户允许覆盖后设置overwriteOutputs:true。`);
    }
  }
  index.entries[key] = { owner, title: c.title, files: c.names };
  const temporary = indexPath + `.${process.pid}.tmp`;
  await fs.writeFile(temporary, JSON.stringify(index, null, 2) + '\n');
  await fs.rename(temporary, indexPath);
}
