// Content, palette and scene boundaries are the project-specific edit points.
const CONTENT = [
  { number: '01', title: 'A simple idea.', caption: 'START WITH ONE CLEAR POINT' },
  { number: '02', title: 'Build the rhythm.', caption: 'SHAPE · TIMING · CONTINUITY' },
  { number: '03', title: 'Make it move.', caption: 'CODE / MOTION / VIDEO' },
];
const STYLE = { background: '#12181b', ink: '#f1eee7', muted: '#a3aaa8', accent: '#ef5b34', line: '#354247' };
const SCENES = [0, 1 / 3, 2 / 3, 1]; // Fractions of the configured total duration.
const canvas = document.querySelector('#stage');
const ctx = canvas.getContext('2d');
const renderMode = Boolean(window.__VIDEO_RENDER_CONFIG__) || new URLSearchParams(location.search).get('render') === '1';
document.documentElement.dataset.render = String(renderMode);
const embeddedConfig = document.querySelector('#video-inline-config');
const config = window.__VIDEO_RENDER_CONFIG__ ?? (embeddedConfig ? JSON.parse(embeddedConfig.textContent) : await fetch('./video.config.json').then((response) => {
  if (!response.ok) throw new Error(`Cannot load video.config.json: HTTP ${response.status}`);
  return response.json();
}));
const duration = Number(config.duration);
if (!ctx || !Number.isFinite(duration) || duration <= 0) throw new Error('Canvas and positive duration are required.');
const ratio = Number(config.width) / Number(config.height);
if (!Number.isFinite(ratio) || ratio <= 0) throw new Error('Positive video width and height are required.');
document.documentElement.style.setProperty('--video-ratio', String(ratio));
if (SCENES.length !== CONTENT.length + 1 || SCENES[0] !== 0 || SCENES.at(-1) !== 1 || SCENES.some((value, index) => !Number.isFinite(value) || (index > 0 && value <= SCENES[index - 1]))) {
  throw new Error('SCENES must contain increasing boundaries from 0 to 1, with one interval per CONTENT item.');
}
const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
const ease = (value) => { const x = clamp(value); return x * x * (3 - 2 * x); };
let currentTime = 0;
let onSeek = () => {};

function label(text, x, y, size, color, maxWidth, weight = 500, align = 'center') {
  ctx.font = `${weight} ${size}px Arial, Helvetica, sans-serif`;
  const measured = ctx.measureText(text).width;
  if (measured > maxWidth) ctx.font = `${weight} ${size * maxWidth / measured}px Arial, Helvetica, sans-serif`;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.textBaseline = 'middle';
  ctx.fillText(text, x, y);
}

function roundedBox(x, y, width, height, radius, fill, stroke) {
  ctx.beginPath();
  ctx.roundRect(x, y, width, height, radius);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.stroke(); }
}

function drawScene(index, progress, alpha, width, height) {
  const unit = Math.min(width, height);
  const content = CONTENT[index];
  ctx.save();
  ctx.globalAlpha = alpha;
  label(content.title, width * 0.5, height * 0.27, unit * 0.087, STYLE.ink, width * 0.86, 600);
  label(content.caption, width * 0.5, height * 0.36, unit * 0.019, STYLE.muted, width * 0.84);
  ctx.translate(width * 0.5, height * 0.62);
  ctx.lineWidth = Math.max(1, unit * 0.002);
  const spread = Math.min(width * 0.23, height * 0.23);
  const radius = unit * 0.045;

  if (index === 0) {
    const expansion = ease(progress / 0.68);
    ctx.strokeStyle = STYLE.line;
    ctx.beginPath();
    ctx.moveTo(-spread * expansion, 0);
    ctx.lineTo(spread * expansion, 0);
    ctx.stroke();
    for (let i = -1; i <= 1; i += 1) {
      const scale = i === 0 ? 1 : 0.45 + expansion * 0.2;
      ctx.beginPath();
      ctx.arc(i * spread * expansion, 0, radius * scale, 0, Math.PI * 2);
      ctx.fillStyle = i === 0 ? STYLE.accent : STYLE.ink;
      ctx.fill();
    }
  } else if (index === 1) {
    for (let i = -1; i <= 1; i += 1) {
      const reveal = ease((progress - (i + 1) * 0.07) / 0.4);
      const boxWidth = Math.min(width * 0.21, height * 0.19);
      const boxHeight = unit * (0.13 + (i + 1) * 0.035);
      ctx.save();
      ctx.translate(i * spread, (1 - reveal) * unit * 0.09);
      ctx.globalAlpha = alpha * (0.4 + reveal * 0.6);
      roundedBox(-boxWidth / 2, -boxHeight / 2, boxWidth, boxHeight, unit * 0.015, i === 0 ? STYLE.accent : STYLE.line);
      label(String(i + 2).padStart(2, '0'), 0, 0, unit * 0.039, STYLE.ink, boxWidth * 0.8, 600);
      ctx.restore();
    }
  } else {
    const expansion = ease(progress / 0.5);
    const boxWidth = Math.min(width * 0.66, height * 0.62);
    const boxHeight = unit * 0.22;
    roundedBox(-boxWidth / 2, -boxHeight / 2, boxWidth, boxHeight, unit * 0.023, null, STYLE.ink);
    const orbit = unit * 0.03 * (1 - expansion);
    ctx.beginPath();
    ctx.arc(-boxWidth * 0.26 + orbit, 0, radius, 0, Math.PI * 2);
    ctx.fillStyle = STYLE.accent;
    ctx.fill();
    label('PLAY', boxWidth * 0.12, 0, unit * 0.052, STYLE.ink, boxWidth * 0.48, 600);
  }
  ctx.restore();
}

// Every pixel is derived from t. Repeated and backward seeks require no reset.
window.seek = (seconds, syncPlayback = true) => {
  if (!Number.isFinite(seconds)) throw new TypeError('seek(t) requires finite seconds.');
  currentTime = clamp(seconds, 0, duration);
  const width = renderMode ? window.innerWidth : Math.max(1, Math.round(canvas.clientWidth));
  const height = renderMode ? window.innerHeight : Math.max(1, Math.round(canvas.clientHeight));
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }
  ctx.resetTransform();
  ctx.globalAlpha = 1;
  ctx.fillStyle = STYLE.background;
  ctx.fillRect(0, 0, width, height);
  const unit = Math.min(width, height);
  const phase = currentTime / duration;
  const nextBoundary = SCENES.findIndex((boundary) => boundary > phase);
  const scene = nextBoundary === -1 ? CONTENT.length - 1 : Math.max(0, nextBoundary - 1);
  const progress = clamp((phase - SCENES[scene]) / (SCENES[scene + 1] - SCENES[scene]));
  label('MOTION STUDY', width * 0.07, height * 0.085, unit * 0.016, STYLE.muted, width * 0.58, 500, 'left');
  label(`${CONTENT[scene].number} / ${String(CONTENT.length).padStart(2, '0')}`, width * 0.93, height * 0.085, unit * 0.016, STYLE.muted, width * 0.2, 500, 'right');
  // Crossfades overlap adjacent scenes; the opening and last frame stay visible.
  const blend = scene > 0 ? ease(progress / 0.09) : 1;
  if (scene > 0 && blend < 1) drawScene(scene - 1, 1, 1 - blend, width, height);
  drawScene(scene, progress, blend, width, height);
  ctx.fillStyle = STYLE.line;
  ctx.fillRect(width * 0.07, height * 0.91, width * 0.86, Math.max(1, unit * 0.002));
  ctx.fillStyle = STYLE.accent;
  ctx.fillRect(width * 0.07, height * 0.91, width * 0.86 * phase, Math.max(1, unit * 0.002));
  onSeek(currentTime, syncPlayback);
};

await document.fonts.ready;
window.seek(0);
window.addEventListener('resize', () => window.seek(currentTime));
window.__VIDEO_READY__ = true;

// The player and frame renderer use the same timeline. Render mode stays still.
if (!renderMode) {
  const controls = document.querySelector('#player-controls');
  const toggle = document.querySelector('#player-toggle');
  const restart = document.querySelector('#player-restart');
  const progress = document.querySelector('#player-progress');
  const timeLabel = document.querySelector('#player-time');
  const sound = document.querySelector('#player-sound');
  const audio = config.audio ? new Audio(config.audio) : null;
  if (audio) { audio.id = 'player-audio'; audio.preload = 'auto'; audio.muted = true; audio.hidden = true; document.body.append(audio); }
  let playing = false;
  let soundEnabled = false;
  let animationFrame = 0;
  let playbackRun = 0;
  let anchorTime = currentTime;
  let anchorClock = performance.now();
  const clockText = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
  const syncAudio = () => { if (audio) audio.currentTime = Math.min(currentTime, Number.isFinite(audio.duration) ? audio.duration : currentTime); };
  const updateControls = () => {
    progress.value = String(currentTime);
    timeLabel.textContent = `${clockText(currentTime)} / ${clockText(duration)}`;
    toggle.textContent = playing ? '暂停' : '播放';
  };
  const startAudio = async () => {
    if (!audio || !soundEnabled || !playing) return;
    try { syncAudio(); await audio.play(); if (!playing || !soundEnabled) audio.pause(); }
    catch (error) { if (error.name === 'AbortError') return; soundEnabled = false; audio.muted = true; sound.textContent = '重试声音'; sound.setAttribute('aria-pressed', 'false'); console.warn(`Audio playback: ${error.message}`); }
  };
  const queueFrame = () => { const run = playbackRun; animationFrame = requestAnimationFrame(now => frame(now, run)); };
  const pause = () => { playing = false; playbackRun += 1; cancelAnimationFrame(animationFrame); audio?.pause(); updateControls(); };
  const frame = async (now, run) => {
    if (!playing || run !== playbackRun) return;
    const nextTime = audio && soundEnabled && !audio.paused && !audio.ended ? audio.currentTime : anchorTime + (now - anchorClock) / 1000;
    try {
      await window.seek(Math.min(duration, nextTime), false);
      if (!playing || run !== playbackRun) return;
      anchorTime = currentTime; anchorClock = now;
      if (currentTime >= duration) pause();
      else queueFrame();
    } catch (error) { pause(); console.error(error); }
  };
  const play = () => {
    if (playing) return;
    if (currentTime >= duration) window.seek(0);
    playing = true; playbackRun += 1; anchorTime = currentTime; anchorClock = performance.now();
    updateControls(); void startAudio(); queueFrame();
  };
  onSeek = (time, syncPlayback) => {
    if (syncPlayback) { anchorTime = time; anchorClock = performance.now(); syncAudio(); }
    updateControls();
  };
  controls.hidden = false;
  progress.max = String(duration);
  toggle.addEventListener('click', () => playing ? pause() : play());
  restart.addEventListener('click', () => { pause(); window.seek(0); play(); });
  progress.addEventListener('input', () => { window.seek(Number(progress.value)); });
  if (audio) {
    sound.hidden = false;
    audio.addEventListener('loadedmetadata', syncAudio);
    sound.addEventListener('click', () => {
      soundEnabled = !soundEnabled; audio.muted = !soundEnabled;
      sound.textContent = soundEnabled ? '静音' : '开启声音';
      sound.setAttribute('aria-pressed', String(soundEnabled));
      if (soundEnabled) void startAudio(); else audio.pause();
    });
  }
  updateControls();
  play();
}
