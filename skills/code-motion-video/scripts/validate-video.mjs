#!/usr/bin/env node
import { readFile, access } from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';

const HELP = `Validate an encoded motion video with ffprobe and FFmpeg.

Usage:
  node validate-video.mjs --video output/final.mp4 [--project .]

Options:
  --video PATH       Required video path, relative to the current directory.
  --project DIR      Read expected specs from DIR/video.config.json.
  --width NUMBER     Expected width; overrides project config.
  --height NUMBER    Expected height; overrides project config.
  --fps NUMBER       Expected frame rate; overrides project config.
  --duration NUMBER  Expected seconds; overrides project config.
  --expect-audio     Require at least one audio stream.
  --full-decode      Count decoded frames and fully decode video/audio (slower).
  --help            Show this help.

By default, checks H.264, yuv420p and ffprobe metadata only. When supplied,
expected specs also check size, frame rate, available frame count and duration
within one frame. A missing metadata frame count is reported as unavailable.
--full-decode requires a decoded frame count and full video/audio decoding.
A configured audio path requires audio; null does not prohibit it.
JSON goes to stdout. Exit 0 = passed, 1 = failed, 2 = invalid invocation.
These are technical checks, not an aesthetic or audio-sync review.
`;

function parseArgs(argv) {
  const options = {};
  const valueOptions = new Set(['video', 'project', 'width', 'height', 'fps', 'duration']);
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--help') { options.help = true; continue; }
    if (argument === '--expect-audio') { options.expectAudio = true; continue; }
    if (argument === '--full-decode') { options.fullDecode = true; continue; }
    const key = argument.startsWith('--') ? argument.slice(2) : '';
    if (!valueOptions.has(key)) throw new Error(`Unknown option: ${argument}`);
    if (options[key] !== undefined) throw new Error(`Duplicate option: ${argument}`);
    const value = argv[++index];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for ${argument}`);
    options[key] = value;
  }
  return options;
}

function positive(value, name, integer = false) {
  const number = Number(value);
  if (!Number.isFinite(number) || number <= 0 || (integer && !Number.isInteger(number))) {
    throw new Error(`${name} must be a positive ${integer ? 'integer' : 'number'}.`);
  }
  return number;
}

function rational(value) {
  if (typeof value !== 'string') return NaN;
  const [numerator, denominator = '1'] = value.split('/');
  return Number(numerator) / Number(denominator);
}

function run(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: ['ignore', 'pipe', 'pipe'], shell: false });
    let stdout = '';
    let stderr = '';
    let oversized = false;
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk) => {
      if (oversized) return;
      stdout += chunk;
      if (stdout.length > 8 * 1024 * 1024) { oversized = true; child.kill(); }
    });
    child.stderr.on('data', (chunk) => { stderr = (stderr + chunk).slice(-65536); });
    child.on('error', (error) => reject(new Error(`${command}: ${error.code === 'ENOENT' ? 'command not found; install FFmpeg and ffprobe.' : error.message}`)));
    child.on('close', (code, signal) => {
      if (oversized) reject(new Error(`${command}: output exceeded 8 MiB.`));
      else if (code !== 0) reject(new Error(`${command} failed (${signal ?? code}): ${stderr.trim() || 'no diagnostic output'}`));
      else resolve({ stdout, stderr });
    });
  });
}

function report(result, exitCode) {
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exitCode = exitCode;
}

async function main() {
  let options;
  let expected;
  let videoPath;
  try {
    options = parseArgs(process.argv.slice(2));
    if (options.help) { process.stdout.write(HELP); return; }
    if (!options.video) throw new Error('--video PATH is required.');
    videoPath = path.resolve(options.video);
    let config = {};
    if (options.project) {
      const configPath = path.join(path.resolve(options.project), 'video.config.json');
      config = JSON.parse(await readFile(configPath, 'utf8'));
      if (!config || typeof config !== 'object' || Array.isArray(config)) throw new Error('video.config.json must contain an object.');
    }
    expected = { codec: 'h264', pixelFormat: 'yuv420p', audio: Boolean(options.expectAudio || config.audio) };
    for (const key of ['width', 'height', 'fps', 'duration']) {
      const value = options[key] ?? config[key];
      if (value !== undefined) expected[key] = positive(value, key, key === 'width' || key === 'height');
    }
    await access(videoPath);
  } catch (error) {
    report({ valid: false, scope: 'technical', errors: [error.message] }, 2);
    return;
  }

  const errors = [];
  let observed = null;
  let fullDecode = false;
  let frameCountSource = null;
  try {
    const probe = await run('ffprobe', ['-v', 'error', ...(options.fullDecode ? ['-count_frames'] : []), '-show_streams', '-show_format', '-of', 'json', videoPath]);
    const metadata = JSON.parse(probe.stdout);
    const video = metadata.streams?.find((stream) => stream.codec_type === 'video');
    if (!video) throw new Error('No video stream found.');
    const audioStreams = metadata.streams.filter((stream) => stream.codec_type === 'audio');
    const fps = rational(video.avg_frame_rate);
    const duration = Number(video.duration ?? metadata.format?.duration);
    const containerDuration = Number(metadata.format?.duration);
    const frames = Number(options.fullDecode ? video.nb_read_frames : video.nb_frames);
    const hasFrameCount = Number.isSafeInteger(frames) && frames > 0;
    if (hasFrameCount) frameCountSource = options.fullDecode ? 'decoded' : 'metadata';
    observed = {
      codec: video.codec_name,
      pixelFormat: video.pix_fmt,
      width: video.width,
      height: video.height,
      fps: Number.isFinite(fps) ? fps : null,
      duration: Number.isFinite(duration) ? duration : null,
      containerDuration: Number.isFinite(containerDuration) ? containerDuration : null,
      frames: hasFrameCount ? frames : null,
      audioStreams: audioStreams.length,
    };
    if (video.codec_name !== expected.codec) errors.push(`Codec: expected h264, got ${video.codec_name}.`);
    if (video.pix_fmt !== expected.pixelFormat) errors.push(`Pixel format: expected yuv420p, got ${video.pix_fmt}.`);
    for (const key of ['width', 'height']) {
      if (expected[key] !== undefined && observed[key] !== expected[key]) errors.push(`${key}: expected ${expected[key]}, got ${observed[key]}.`);
    }
    if (!Number.isFinite(fps) || fps <= 0) errors.push('Cannot determine a positive average frame rate.');
    else if (expected.fps !== undefined && Math.abs(fps - expected.fps) > 0.001) errors.push(`Frame rate: expected ${expected.fps}, got ${fps}.`);
    if (options.fullDecode && !hasFrameCount) errors.push('Cannot determine a positive decoded frame count.');
    if (!Number.isFinite(duration) || duration <= 0) errors.push('Cannot determine a positive video duration.');
    if (!Number.isFinite(containerDuration) || containerDuration <= 0) errors.push('Cannot determine a positive container duration.');
    if (expected.duration !== undefined) {
      const targetFps = expected.fps ?? fps;
      if (Number.isFinite(targetFps) && targetFps > 0) {
        const targetFrames = Math.round(expected.duration * targetFps);
        if ((hasFrameCount || options.fullDecode) && frames !== targetFrames) errors.push(`Frame count: expected ${targetFrames}, got ${hasFrameCount ? frames : 'unknown'}.`);
        if (Math.abs(duration - expected.duration) > 1 / targetFps + 0.000001) errors.push(`Duration: expected ${expected.duration}s ± one frame, got ${duration}s.`);
        if (Math.abs(containerDuration - expected.duration) > 1 / targetFps + 0.000001) errors.push(`Container duration: expected ${expected.duration}s ± one frame, got ${containerDuration}s.`);
      }
    }
    if (expected.audio && audioStreams.length === 0) errors.push('An audio stream is required but none was found.');
    if (options.fullDecode) {
      await run('ffmpeg', ['-hide_banner', '-v', 'error', '-xerror', '-nostdin', '-i', videoPath, '-map', '0:v:0', '-map', '0:a?', '-f', 'null', '-']);
      fullDecode = true;
    }
  } catch (error) {
    errors.push(error.message);
  }
  report({ valid: errors.length === 0, scope: 'technical', mode: options.fullDecode ? 'full-decode' : 'metadata', video: videoPath, expected, observed, frameCountSource, fullDecode, errors }, errors.length === 0 ? 0 : 1);
}

await main();
