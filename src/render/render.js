/* BANG TAF — "Why are modern cars becoming smarter?"
 * Deterministic frame renderer: window.renderFrame(t) draws the frame at time t (seconds).
 * window.setup({text, cues}) must be called first with the language data.
 * Everything is procedural (no external images): custom 3D projection, wireframe vehicles,
 * motion graphics, kinetic type, bloom.
 */
'use strict';
const W = 1080, H = 1920, CX = 525;           // content centre is nudged left of the TikTok side-rail
const canvas = document.getElementById('c');
let ctx = canvas.getContext('2d');
const mainCtx = ctx;
const layerC = document.createElement('canvas'); layerC.width = W; layerC.height = H;
const layerCtx = layerC.getContext('2d');
const bloomC = document.createElement('canvas'); bloomC.width = 270; bloomC.height = 480;
const bctx = bloomC.getContext('2d');

const COL = {
  bg: '#030507', graphite: '#11151b', blue: '#1ea7ff', blueHi: '#8fdcff', blueDeep: '#0a4f8a',
  silver: '#c9d1db', white: '#ffffff', amber: '#ffb21e', red: '#ff3d4d', dim: '#5d6b7a',
};
const FONT = '"Inter", "Inter Display", "DejaVu Sans", sans-serif';
const FONTD = '"Inter Display", "Inter", "DejaVu Sans", sans-serif';

let TXT = {}, CUES = [];
let LOGO = null, logoLoad = Promise.resolve();
// Official logo (optional, per language): used unaltered, only cropped to its frame and shown as a badge.
window.setup = (d) => {
  TXT = d.text; CUES = d.cues;
  if (d.logo) logoLoad = new Promise((res) => { const im = new Image(); im.onload = () => {
    const [sx, sy, sw, sh] = d.logoCrop || [0, 0, im.width, im.height];
    const c = document.createElement('canvas'); c.width = sw * 4; c.height = sh * 4; const g = c.getContext('2d');
    g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high'; g.drawImage(im, sx, sy, sw, sh, 0, 0, c.width, c.height);
    LOGO = c; res(); }; im.onerror = () => res(); im.src = d.logo; });
};
function drawLogo(cx, cy, w, a = 1, o = {}) {
  if (!LOGO) return;
  const h = w * LOGO.height / LOGO.width, x = cx - w / 2, y = cy - h / 2, r = Math.max(6, w * 0.035);
  ctx.save(); alpha(a);
  if (o.glow) { ctx.shadowColor = 'rgba(30,167,255,0.55)'; ctx.shadowBlur = o.glow; ctx.fillStyle = '#000'; ctx.fill(rrect(x, y, w, h, r)); ctx.shadowBlur = 0; }
  ctx.save(); ctx.clip(rrect(x, y, w, h, r)); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(LOGO, x, y, w, h);
  if (o.sweep != null && o.sweep > 0 && o.sweep < 1) { // light glint passing over the badge
    const sx = lerp(x - w * 0.4, x + w * 1.4, o.sweep); const g = ctx.createLinearGradient(sx - w * 0.18, y, sx + w * 0.18, y + h);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,255,255,0.35)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = g; ctx.fillRect(x, y, w, h); }
  ctx.restore();
  ctx.lineWidth = Math.max(1.5, w * 0.004); ctx.strokeStyle = 'rgba(255,255,255,0.18)'; ctx.stroke(rrect(x, y, w, h, r));
  ctx.restore();
}

// ---------------------------------------------------------------- math
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const eio = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const eo = (t) => 1 - Math.pow(1 - t, 3);
const ei = (t) => t * t * t;
const eback = (t) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const env = (t, a, b, fi = 0.4, fo = 0.4) => Math.min(eo(prog(t, a, a + fi)), 1 - eio(prog(t, b - fo, b)));
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const rotZ = (p, a) => { const c = Math.cos(a), s = Math.sin(a); return [p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2]]; };
function rng(seed) { return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const hexA = (hex, a) => { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };
const mixHex = (h1, h2, t) => { const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16);
  const r = Math.round(lerp(a >> 16, b >> 16, t)), g = Math.round(lerp((a >> 8) & 255, (b >> 8) & 255, t)), bl = Math.round(lerp(a & 255, b & 255, t));
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + bl).toString(16).slice(1); };

// draw fn() into an offscreen layer, fade its top edge (y0 -> y1) to transparent, composite onto main
function fadedLayer(y0, y1, fn) {
  layerCtx.setTransform(1, 0, 0, 1, 0, 0); layerCtx.globalCompositeOperation = 'source-over'; layerCtx.globalAlpha = 1; layerCtx.clearRect(0, 0, W, H);
  ctx = layerCtx; try { fn(); } finally { ctx = mainCtx; }
  const g = layerCtx.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,1)');
  layerCtx.globalCompositeOperation = 'destination-in'; layerCtx.globalAlpha = 1; layerCtx.fillStyle = g; layerCtx.fillRect(0, 0, W, H);
  layerCtx.globalCompositeOperation = 'source-over';
  ctx.save(); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.drawImage(layerC, 0, 0); ctx.restore();
}

// ---------------------------------------------------------------- global alpha stack
let GA = 1;
function withAlpha(a, fn) { const old = GA; GA *= a; if (GA > 0.002) fn(); GA = old; }
function alpha(a) { ctx.globalAlpha = clamp(GA * a); }

// ---------------------------------------------------------------- camera
function camLook(pos, target, fov = 40, cx = CX, cy = 760) {
  const f = norm(sub(target, pos));
  const r = norm(cross(f, [0, 0, 1]));
  const u = cross(r, f);
  return { pos, f, r, u, focal: (W / 2) / Math.tan(fov * Math.PI / 360), cx, cy };
}
function camOrbit(target, yaw, pitch, dist, fov, cx, cy) {
  const pos = add(target, [dist * Math.cos(pitch) * Math.cos(yaw), dist * Math.cos(pitch) * Math.sin(yaw), dist * Math.sin(pitch)]);
  return camLook(pos, target, fov, cx, cy);
}
function P(cam, p) {
  const d = sub(p, cam.pos); const z = dot(d, cam.f);
  if (z < 0.15) return null;
  const s = cam.focal / z;
  return [cam.cx + dot(d, cam.r) * s, cam.cy - dot(d, cam.u) * s, z];
}

// ---------------------------------------------------------------- drawing primitives
function pathFrom(cam, pts, reveal = 1, closed = false, xf = null) {
  const path = new Path2D(); let pen = false;
  const n = pts.length; const lim = reveal * (n - 1);
  for (let i = 0; i < n; i++) {
    if (i > lim + 1e-6) {
      if (i - 1 <= lim && pen && i > 0) { // partial last segment
        const f = lim - (i - 1);
        const a = xf ? xf(pts[i - 1]) : pts[i - 1], b = xf ? xf(pts[i]) : pts[i];
        const q = P(cam, [lerp(a[0], b[0], f), lerp(a[1], b[1], f), lerp(a[2], b[2], f)]);
        if (q) path.lineTo(q[0], q[1]);
      }
      break;
    }
    const q = P(cam, xf ? xf(pts[i]) : pts[i]);
    if (!q) { pen = false; continue; }
    if (!pen) { path.moveTo(q[0], q[1]); pen = true; } else path.lineTo(q[0], q[1]);
  }
  if (closed && reveal >= 1) path.closePath();
  return path;
}
function glow(path, color, w = 2, a = 1, spread = 4) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.strokeStyle = color;
  if (spread > 0) { alpha(a * 0.16); ctx.lineWidth = w * spread; ctx.stroke(path); }
  alpha(a); ctx.lineWidth = w; ctx.stroke(path);
  ctx.restore();
}
function dotGlow(x, y, r, color, a = 1) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createRadialGradient(x, y, 0, x, y, r * 4);
  g.addColorStop(0, hexA(color, 0.9)); g.addColorStop(0.25, hexA(color, 0.35)); g.addColorStop(1, hexA(color, 0));
  alpha(a); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 4, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x, y, r * 0.6, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
function rrect(x, y, w, h, r) { const p = new Path2D(); p.roundRect(x, y, w, h, r); return p; }

function text(str, x, y, o = {}) {
  const size = o.size || 40, weight = o.weight || 700;
  ctx.save();
  ctx.font = `${weight} ${size}px ${o.display ? FONTD : FONT}`;
  ctx.letterSpacing = (o.spacing || 0) + 'px';
  ctx.textAlign = o.align || 'center'; ctx.textBaseline = o.baseline || 'middle';
  alpha(o.a == null ? 1 : o.a);
  if (o.glow) { ctx.shadowColor = hexA(o.glowColor || COL.blue, 0.85); ctx.shadowBlur = o.glow; }
  ctx.fillStyle = o.color || COL.white;
  ctx.fillText(str, x, y);
  ctx.restore();
}
function measure(str, size, weight = 700, spacing = 0, display = false) {
  ctx.save(); ctx.font = `${weight} ${size}px ${display ? FONTD : FONT}`; ctx.letterSpacing = spacing + 'px';
  const w = ctx.measureText(str).width; ctx.restore(); return w;
}
function wrap(str, size, weight, maxW) {
  const words = str.split(' '); const lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (measure(t, size, weight) > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur); return lines;
}
// kinetic word-by-word reveal
function kinetic(str, x, y, t, t0, o = {}) {
  const size = o.size || 60, weight = o.weight || 800, sp = o.spacing || 0;
  const words = str.split(' '); const gap = size * 0.28;
  const ws = words.map((w) => measure(w, size, weight, sp, o.display));
  const total = ws.reduce((a, b) => a + b, 0) + gap * (words.length - 1);
  let cx = x - total / 2;
  words.forEach((w, i) => {
    const p = prog(t, t0 + i * (o.stagger || 0.07), t0 + i * (o.stagger || 0.07) + 0.5);
    if (p > 0) {
      const dy = (1 - eback(p)) * size * 0.6;
      const hl = o.hl && o.hl.includes(w.replace(/[.,:]/g, ''));
      text(w, cx + ws[i] / 2, y + dy, { size, weight, spacing: sp, display: o.display, a: eo(p) * (o.a == null ? 1 : o.a),
        color: hl ? COL.blue : (o.color || COL.white), glow: o.glow });
    }
    cx += ws[i] + gap;
  });
}

// ---------------------------------------------------------------- icons (line icons, s = size)
function icon(name, x, y, s, color = COL.blue, a = 1, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.globalCompositeOperation = 'lighter';
  ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = Math.max(2, s * 0.07); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  alpha(a);
  const k = s / 2; const b = () => ctx.beginPath();
  switch (name) {
    case 'chip': {
      ctx.strokeRect(-k * 0.55, -k * 0.55, k * 1.1, k * 1.1); ctx.strokeRect(-k * 0.25, -k * 0.25, k * 0.5, k * 0.5);
      for (let i = -2; i <= 2; i++) { const o = i * k * 0.2; b(); ctx.moveTo(o, -k * 0.55); ctx.lineTo(o, -k * 0.85); ctx.moveTo(o, k * 0.55); ctx.lineTo(o, k * 0.85);
        ctx.moveTo(-k * 0.55, o); ctx.lineTo(-k * 0.85, o); ctx.moveTo(k * 0.55, o); ctx.lineTo(k * 0.85, o); ctx.stroke(); }
      break; }
    case 'engine': {
      b(); ctx.moveTo(-k * 0.8, -k * 0.2); ctx.lineTo(-k * 0.5, -k * 0.2); ctx.lineTo(-k * 0.5, -k * 0.5); ctx.lineTo(k * 0.3, -k * 0.5); ctx.lineTo(k * 0.3, -k * 0.3);
      ctx.lineTo(k * 0.55, -k * 0.3); ctx.lineTo(k * 0.55, -k * 0.05); ctx.lineTo(k * 0.85, -k * 0.05); ctx.lineTo(k * 0.85, k * 0.45); ctx.lineTo(k * 0.55, k * 0.45);
      ctx.lineTo(k * 0.55, k * 0.6); ctx.lineTo(-k * 0.5, k * 0.6); ctx.lineTo(-k * 0.5, k * 0.3); ctx.lineTo(-k * 0.8, k * 0.3); ctx.closePath(); ctx.stroke();
      b(); ctx.moveTo(-k * 0.2, -k * 0.5); ctx.lineTo(-k * 0.2, -k * 0.75); ctx.moveTo(-k * 0.4, -k * 0.75); ctx.lineTo(0, -k * 0.75); ctx.stroke(); break; }
    case 'radar': case 'sensor': {
      b(); ctx.arc(-k * 0.6, 0, k * 0.12, 0, Math.PI * 2); ctx.fill();
      for (let i = 1; i <= 3; i++) { const ph = (t * 1.5 + i * 0.33) % 1; b(); ctx.globalAlpha = clamp(GA * a * (name === 'radar' ? 1 - ph * 0.3 : 1));
        ctx.arc(-k * 0.6, 0, k * 0.45 * i, -0.75, 0.75); ctx.stroke(); }
      break; }
    case 'gear': {
      const n = 8; b();
      for (let i = 0; i < n * 2; i++) { const an = t + (i / (n * 2)) * Math.PI * 2; const r = i % 2 ? k * 0.62 : k * 0.85;
        const a1 = an - Math.PI / (n * 2) * 0.6, a2 = an + Math.PI / (n * 2) * 0.6;
        ctx.lineTo(Math.cos(a1) * r, Math.sin(a1) * r); ctx.lineTo(Math.cos(a2) * r, Math.sin(a2) * r); }
      ctx.closePath(); ctx.stroke(); b(); ctx.arc(0, 0, k * 0.25, 0, Math.PI * 2); ctx.stroke(); break; }
    case 'brain': case 'network': {
      const pts = [[-0.6, -0.3], [-0.1, -0.65], [0.5, -0.4], [0.65, 0.2], [0.1, 0.6], [-0.5, 0.4], [0, 0]];
      b(); [[0, 6], [1, 6], [2, 6], [3, 6], [4, 6], [5, 6], [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]].forEach(([i, j]) => { ctx.moveTo(pts[i][0] * k, pts[i][1] * k); ctx.lineTo(pts[j][0] * k, pts[j][1] * k); });
      ctx.stroke(); pts.forEach((p) => { b(); ctx.arc(p[0] * k, p[1] * k, k * 0.1, 0, Math.PI * 2); ctx.fill(); }); break; }
    case 'camera': {
      ctx.strokeRect(-k * 0.75, -k * 0.4, k * 1.1, k * 0.8);
      b(); ctx.moveTo(k * 0.35, -k * 0.15); ctx.lineTo(k * 0.8, -k * 0.4); ctx.lineTo(k * 0.8, k * 0.4); ctx.lineTo(k * 0.35, k * 0.15); ctx.stroke();
      b(); ctx.arc(-k * 0.2, 0, k * 0.2, 0, Math.PI * 2); ctx.stroke(); break; }
    case '360': {
      b(); ctx.arc(0, 0, k * 0.8, 0, Math.PI * 2); ctx.stroke();
      b(); ctx.arc(0, 0, k * 0.8, t * 2, t * 2 + 1.0); ctx.lineWidth *= 2.2; ctx.stroke(); ctx.lineWidth /= 2.2;
      ctx.strokeRect(-k * 0.22, -k * 0.38, k * 0.44, k * 0.76); break; }
    case 'eye': case 'blind': {
      b(); ctx.moveTo(-k * 0.85, 0); ctx.quadraticCurveTo(0, -k * 0.75, k * 0.85, 0); ctx.quadraticCurveTo(0, k * 0.75, -k * 0.85, 0); ctx.stroke();
      b(); ctx.arc(0, 0, k * 0.22, 0, Math.PI * 2); ctx.stroke();
      if (name === 'blind') { b(); ctx.moveTo(-k * 0.6, k * 0.6); ctx.lineTo(k * 0.6, -k * 0.6); ctx.stroke(); }
      break; }
    case 'lane': {
      b(); ctx.moveTo(-k * 0.35, k * 0.85); ctx.lineTo(-k * 0.15, -k * 0.85); ctx.moveTo(k * 0.35, k * 0.85); ctx.lineTo(k * 0.15, -k * 0.85); ctx.stroke();
      ctx.setLineDash([k * 0.18, k * 0.18]); b(); ctx.moveTo(0, k * 0.85); ctx.lineTo(0, -k * 0.85); ctx.stroke(); ctx.setLineDash([]); break; }
    case 'shield': case 'adas': {
      b(); ctx.moveTo(0, -k * 0.85); ctx.lineTo(k * 0.7, -k * 0.55); ctx.lineTo(k * 0.6, k * 0.25); ctx.quadraticCurveTo(k * 0.35, k * 0.7, 0, k * 0.9);
      ctx.quadraticCurveTo(-k * 0.35, k * 0.7, -k * 0.6, k * 0.25); ctx.lineTo(-k * 0.7, -k * 0.55); ctx.closePath(); ctx.stroke();
      b(); ctx.moveTo(-k * 0.3, 0); ctx.lineTo(-k * 0.05, k * 0.28); ctx.lineTo(k * 0.35, -k * 0.25); ctx.stroke(); break; }
    case 'screen': {
      ctx.strokeRect(-k * 0.85, -k * 0.55, k * 1.7, k * 1.0);
      b(); ctx.moveTo(-k * 0.3, k * 0.75); ctx.lineTo(k * 0.3, k * 0.75); ctx.stroke();
      ctx.fillRect(-k * 0.65, -k * 0.35, k * 0.45, k * 0.25); ctx.fillRect(-k * 0.1, -k * 0.35, k * 0.75, k * 0.6); break; }
    case 'wheel': { // steering wheel = driver assist
      b(); ctx.arc(0, 0, k * 0.8, 0, Math.PI * 2); ctx.stroke(); b(); ctx.arc(0, 0, k * 0.22, 0, Math.PI * 2); ctx.stroke();
      b(); ctx.moveTo(-k * 0.8, 0); ctx.lineTo(-k * 0.22, 0); ctx.moveTo(k * 0.8, 0); ctx.lineTo(k * 0.22, 0); ctx.moveTo(0, k * 0.22); ctx.lineTo(0, k * 0.8); ctx.stroke(); break; }
    case 'link': { // connectivity
      for (let i = 1; i <= 3; i++) { b(); ctx.arc(0, k * 0.55, k * 0.32 * i, -Math.PI * 0.78, -Math.PI * 0.22); ctx.stroke(); }
      b(); ctx.arc(0, k * 0.55, k * 0.1, 0, Math.PI * 2); ctx.fill(); break; }
    case 'comfort': { // sun / sunroof
      b(); ctx.arc(0, 0, k * 0.32, 0, Math.PI * 2); ctx.stroke();
      for (let i = 0; i < 8; i++) { const an = i * Math.PI / 4; b(); ctx.moveTo(Math.cos(an) * k * 0.5, Math.sin(an) * k * 0.5); ctx.lineTo(Math.cos(an) * k * 0.78, Math.sin(an) * k * 0.78); ctx.stroke(); }
      break; }
    case 'brake': {
      b(); ctx.arc(0, 0, k * 0.75, 0, Math.PI * 2); ctx.stroke(); b(); ctx.arc(0, 0, k * 0.3, 0, Math.PI * 2); ctx.stroke();
      b(); ctx.arc(0, 0, k * 0.95, -0.9, 0.9); ctx.lineWidth *= 2; ctx.stroke(); break; }
    case 'gearbox': {
      for (const xx of [-0.5, 0, 0.5]) { b(); ctx.arc(xx * k, -k * 0.5, k * 0.1, 0, Math.PI * 2); ctx.fill(); b(); ctx.arc(xx * k, k * 0.5, k * 0.1, 0, Math.PI * 2); ctx.fill(); }
      b(); ctx.moveTo(-k * 0.5, -k * 0.5); ctx.lineTo(-k * 0.5, k * 0.5); ctx.moveTo(0, -k * 0.5); ctx.lineTo(0, k * 0.5); ctx.moveTo(k * 0.5, -k * 0.5); ctx.lineTo(k * 0.5, 0);
      ctx.moveTo(-k * 0.5, 0); ctx.lineTo(k * 0.5, 0); ctx.stroke(); break; }
    case 'control': { // sliders
      for (const [yy, p] of [[-0.5, 0.3], [0, -0.35], [0.5, 0.1]]) { b(); ctx.moveTo(-k * 0.8, yy * k); ctx.lineTo(k * 0.8, yy * k); ctx.stroke(); b(); ctx.arc(p * k, yy * k, k * 0.14, 0, Math.PI * 2); ctx.fill(); }
      break; }
    case 'warning': {
      b(); ctx.moveTo(0, -k * 0.8); ctx.lineTo(k * 0.85, k * 0.65); ctx.lineTo(-k * 0.85, k * 0.65); ctx.closePath(); ctx.stroke();
      b(); ctx.moveTo(0, -k * 0.25); ctx.lineTo(0, k * 0.2); ctx.stroke(); b(); ctx.arc(0, k * 0.42, k * 0.06, 0, Math.PI * 2); ctx.fill(); break; }
  }
  ctx.restore();
}

// ---------------------------------------------------------------- vehicles
const BODIES = {
  modern: { L: 4.5, hw: 0.92, r: 0.36, wheels: [0.19, 0.79],
    u: [0, .03, .10, .22, .55, .66, .74, .90, .975, 1], top: [.74, 1.04, 1.44, 1.60, 1.60, 1.40, 1.08, .99, .87, .60],
    belt: [.74, 1.0, 1.02, 1.03, 1.03, 1.02, 1.0, .97, .87, .60], bot: [.42, .30, .24, .22, .22, .22, .22, .24, .30, .42], wf: [.84, .95, 1, 1, 1, 1, 1, .98, .92, .80] },
  old: { L: 4.6, hw: 0.86, r: 0.33, wheels: [0.2, 0.8],
    u: [0, .03, .24, .32, .58, .64, .70, .94, .98, 1], top: [.80, .95, .98, 1.36, 1.38, 1.36, 1.0, .98, .92, .72],
    belt: [.80, .95, .98, .98, .98, .98, .98, .98, .92, .72], bot: [.40, .33, .30, .28, .28, .28, .28, .30, .33, .40], wf: [.96, 1, 1, 1, 1, 1, 1, 1, 1, .96] },
  suv_ev: { L: 4.6, hw: 0.95, r: 0.38, wheels: [0.19, 0.8],   // coupe-like roofline SUV (e.MAS 7 proportions)
    u: [0, .03, .12, .28, .52, .64, .73, .90, .975, 1], top: [.80, 1.02, 1.36, 1.60, 1.64, 1.46, 1.08, 1.0, .88, .62],
    belt: [.80, 1.0, 1.04, 1.06, 1.06, 1.05, 1.02, .98, .88, .62], bot: [.42, .32, .25, .23, .23, .23, .23, .25, .32, .42], wf: [.82, .94, 1, 1, 1, 1, 1, .98, .92, .80] },
  suv_compact: { L: 4.33, hw: 0.9, r: 0.36, wheels: [0.2, 0.79], // upright compact SUV (X50 proportions)
    u: [0, .025, .08, .20, .56, .66, .74, .90, .975, 1], top: [.80, 1.10, 1.52, 1.60, 1.60, 1.42, 1.08, 1.0, .88, .62],
    belt: [.80, 1.06, 1.06, 1.06, 1.06, 1.05, 1.02, .98, .88, .62], bot: [.42, .32, .25, .23, .23, .23, .23, .25, .32, .42], wf: [.84, .95, 1, 1, 1, 1, 1, .98, .92, .80] },
};
function lerpBody(a, b, m) {
  const o = {};
  for (const k in a) o[k] = Array.isArray(a[k]) ? a[k].map((v, i) => lerp(v, b[k][i], m)) : lerp(a[k], b[k], m);
  return o;
}
function sampleKeys(body, key, u) {
  const U = body.u; let i = 0; while (i < U.length - 2 && u > U[i + 1]) i++;
  const f = clamp((u - U[i]) / (U[i + 1] - U[i])); const s = f * f * (3 - 2 * f) * 0.35 + f * 0.65;
  return lerp(body[key][i], body[key][i + 1], s);
}
const carCache = new Map();
function buildCar(body, n = 34, cacheKey = null) {
  if (cacheKey && carCache.has(cacheKey)) return carCache.get(cacheKey);
  const rings = [], L = body.L;
  for (let i = 0; i < n; i++) {
    const u = i / (n - 1), x = (u - 0.5) * L;
    const zb = sampleKeys(body, 'bot', u), zt = sampleKeys(body, 'top', u), zbe = Math.min(sampleKeys(body, 'belt', u), zt);
    const hw = body.hw * sampleKeys(body, 'wf', u); const g = clamp((zt - zbe) / 0.3);
    const side = (s) => [
      [x, s * hw * 0.90, zb], [x, s * hw, zb + 0.18 * (zbe - zb)], [x, s * hw, zb + 0.66 * (zbe - zb)], [x, s * hw * 0.97, zbe],
      [x, s * hw * lerp(0.94, 0.80, g), zbe + 0.6 * (zt - zbe)], [x, s * hw * lerp(0.88, 0.66, g), zt]];
    const l = side(1), r = side(-1);
    rings.push(l.concat(r.slice().reverse()));
  }
  const longs = [];
  for (let k = 0; k < 12; k++) longs.push(rings.map((rg) => rg[k]));
  longs.push(rings.map((rg) => [rg[5][0], 0, rg[5][2]])); // roof centre line
  const wheels = body.wheels.map((u) => (u - 0.5) * L);
  const car = { rings, longs, wheels, body, L, hw: body.hw };
  if (cacheKey) carCache.set(cacheKey, car);
  return car;
}
function drawCar(cam, car, o = {}) {
  const color = o.color || COL.blue, a = o.a == null ? 1 : o.a, rev = o.reveal == null ? 1 : o.reveal;
  const xf = (p) => { let q = p; if (o.yaw) q = rotZ(q, o.yaw); return o.pos ? add(q, o.pos) : q; };
  // body volume (translucent ring fills)
  ctx.save();
  car.rings.forEach((rg, i) => {
    if (i / (car.rings.length - 1) > rev) return;
    const p = pathFrom(cam, rg, 1, true, xf); alpha(a * (o.fill == null ? 0.05 : o.fill)); ctx.fillStyle = hexA(o.fillColor || '#1a6fb0', 1); ctx.fill(p);
  });
  ctx.restore();
  // rings
  car.rings.forEach((rg, i) => {
    if (i % 2 || i / (car.rings.length - 1) > rev) return;
    glow(pathFrom(cam, rg, 1, true, xf), color, 1.1, a * (o.ringA == null ? 0.28 : o.ringA), 0);
  });
  // longitudinal feature lines (drawn front -> rear)
  car.longs.forEach((ln, k) => {
    const pts = ln.slice().reverse();
    const strong = k === 3 || k === 8 || k === 5 || k === 6 || k === 12;
    glow(pathFrom(cam, pts, rev, false, xf), strong ? (o.hiColor || COL.blueHi) : color, strong ? 2.2 : 1.4, a * (strong ? 0.95 : 0.55), 4);
  });
  // wheels
  const wr = car.body.r; const rot = o.wheelRot || 0;
  car.wheels.forEach((wx) => [1, -1].forEach((s) => {
    const y = s * car.hw * 0.99; const circ = (r, n = 28) => Array.from({ length: n + 1 }, (_, i) => { const an = (i / n) * Math.PI * 2; return [wx + Math.cos(an) * r, y, wr + Math.sin(an) * r]; });
    const wrev = clamp(rev * 1.6 - 0.3);
    glow(pathFrom(cam, circ(wr), wrev, false, xf), color, 2.2, a * 0.95, 4);
    glow(pathFrom(cam, circ(wr * 0.62), wrev, false, xf), color, 1.3, a * 0.6, 0);
    if (wrev >= 1) for (let i = 0; i < 5; i++) {
      const an = rot + (i / 5) * Math.PI * 2;
      glow(pathFrom(cam, [[wx + Math.cos(an) * wr * 0.15, y, wr + Math.sin(an) * wr * 0.15], [wx + Math.cos(an) * wr * 0.6, y, wr + Math.sin(an) * wr * 0.6]], 1, false, xf), color, 1.2, a * 0.5, 0);
    }
  }));
  // lights
  if (o.lights) {
    const fr = car.rings[car.rings.length - 2], rr = car.rings[1];
    [fr[2], fr[9]].forEach((p) => { const q = P(cam, xf(p)); if (q) dotGlow(q[0], q[1], 9 * o.lights, '#dff4ff', a * o.lights); });
    [rr[3], rr[8]].forEach((p) => { const q = P(cam, xf(p)); if (q) dotGlow(q[0], q[1], 6 * o.lights, COL.red, a * 0.8 * o.lights); });
  }
}
function box3(cam, c, s, o = {}) { // wireframe / shaded box; c centre, s size
  const yaw = o.yaw || 0, hx = s[0] / 2, hy = s[1] / 2, hz = s[2] / 2;
  const V = [[-hx, -hy, -hz], [hx, -hy, -hz], [hx, hy, -hz], [-hx, hy, -hz], [-hx, -hy, hz], [hx, -hy, hz], [hx, hy, hz], [-hx, hy, hz]].map((v) => add(rotZ(v, yaw), c));
  const Q = V.map((v) => P(cam, v)); if (Q.some((q) => !q)) return;
  const faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]];
  if (o.shade) {
    const order = faces.map((f) => ({ f, z: f.reduce((a, i) => a + Q[i][2], 0) / 4 })).sort((a, b) => b.z - a.z);
    for (const { f } of order) {
      const p = new Path2D(); p.moveTo(Q[f[0]][0], Q[f[0]][1]); f.slice(1).forEach((i) => p.lineTo(Q[i][0], Q[i][1])); p.closePath();
      const nrm = cross(sub(V[f[1]], V[f[0]]), sub(V[f[3]], V[f[0]]));
      const lit = clamp(0.25 + 0.75 * Math.abs(dot(norm(nrm), norm([0.4, -0.5, 0.8]))));
      ctx.save(); alpha(o.a == null ? 1 : o.a); ctx.fillStyle = mixHex('#0b0f15', o.shade, lit * 0.55); ctx.fill(p); ctx.restore();
    }
  }
  const edges = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]];
  const p = new Path2D(); edges.forEach(([i, j]) => { p.moveTo(Q[i][0], Q[i][1]); p.lineTo(Q[j][0], Q[j][1]); });
  glow(p, o.color || COL.blue, o.w || 1.6, (o.a == null ? 1 : o.a) * (o.edgeA || 0.9), 3);
  return V;
}

// ---------------------------------------------------------------- environment
const PARTS = (() => { const r = rng(7); return Array.from({ length: 150 }, () => ({ x: r() * W, y: r() * H, z: 0.3 + r() * 0.7, s: r(), ph: r() * 6.28 })); })();
const GRAIN = (() => { const c = document.createElement('canvas'); c.width = 256; c.height = 256; const g = c.getContext('2d'); const d = g.createImageData(256, 256); const r = rng(3);
  for (let i = 0; i < d.data.length; i += 4) { const v = r() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; } g.putImageData(d, 0, 0); return c; })();
function background(t, tint = 0) {
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  ctx.fillStyle = COL.bg; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(CX, 760, 50, CX, 760, 1300);
  g.addColorStop(0, mixHex('#16202c', '#0d2742', tint)); g.addColorStop(0.45, '#0a0e14'); g.addColorStop(1, '#020304');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // slow light beams
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 3; i++) {
    const x = (W * (0.2 + 0.35 * i) + Math.sin(t * 0.21 + i * 2) * 140);
    const bg = ctx.createLinearGradient(x - 160, 0, x + 160, 0);
    bg.addColorStop(0, 'rgba(30,167,255,0)'); bg.addColorStop(0.5, 'rgba(30,167,255,0.035)'); bg.addColorStop(1, 'rgba(30,167,255,0)');
    ctx.fillStyle = bg; ctx.save(); ctx.translate(x, 0); ctx.rotate(0.18 - i * 0.12); ctx.translate(-x, 0); ctx.fillRect(x - 160, -200, 320, H + 400); ctx.restore();
  }
  ctx.restore();
}
function particles(t, a = 1, speed = 1) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (const p of PARTS) {
    const y = (p.y - t * 18 * p.z * speed) % H; const yy = y < 0 ? y + H : y;
    const x = p.x + Math.sin(t * 0.4 + p.ph) * 12 * p.z;
    const tw = 0.4 + 0.6 * Math.sin(t * 2 + p.ph * 3) ** 2;
    ctx.globalAlpha = clamp(GA * a * tw * 0.55 * p.z); ctx.fillStyle = p.s > 0.85 ? COL.white : COL.blueHi;
    ctx.beginPath(); ctx.arc(x, yy, 0.8 + p.z * 1.8, 0, Math.PI * 2); ctx.fill();
  }
  ctx.restore();
}
function floorGrid(cam, a = 1, ext = 7, step = 0.5, origin = [0, 0], color = COL.blue) {
  const p = new Path2D();
  for (let v = -ext; v <= ext + 1e-6; v += step) {
    const s1 = P(cam, [origin[0] + v, origin[1] - ext, 0]), s2 = P(cam, [origin[0] + v, origin[1] + ext, 0]);
    if (s1 && s2) { p.moveTo(s1[0], s1[1]); p.lineTo(s2[0], s2[1]); }
    const s3 = P(cam, [origin[0] - ext, origin[1] + v, 0]), s4 = P(cam, [origin[0] + ext, origin[1] + v, 0]);
    if (s3 && s4) { p.moveTo(s3[0], s3[1]); p.lineTo(s4[0], s4[1]); }
  }
  glow(p, color, 1, a * 0.16, 0);
  // floor reflection pool
  const c = P(cam, [origin[0], origin[1], 0]);
  if (c) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createRadialGradient(c[0], c[1], 0, c[0], c[1], 520);
    g.addColorStop(0, hexA(COL.blue, 0.10)); g.addColorStop(1, hexA(COL.blue, 0)); alpha(a); ctx.fillStyle = g; ctx.fillRect(c[0] - 520, c[1] - 260, 1040, 520); ctx.restore(); }
}
function shadowUnder(cam, pos, L, a = 1) {
  const c = P(cam, [pos[0], pos[1], 0.01]); if (!c) return;
  const e = P(cam, [pos[0] + L * 0.6, pos[1], 0.01]); const rx = e ? Math.abs(e[0] - c[0]) + 60 : 200;
  ctx.save(); ctx.translate(c[0], c[1]); ctx.scale(1, 0.32); const g = ctx.createRadialGradient(0, 0, 0, 0, 0, rx);
  g.addColorStop(0, 'rgba(0,0,0,0.7)'); g.addColorStop(1, 'rgba(0,0,0,0)'); alpha(a); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, rx, 0, Math.PI * 2); ctx.fill(); ctx.restore();
}
function bloom(strength = 0.6) {
  bctx.globalCompositeOperation = 'source-over'; bctx.filter = 'none'; bctx.clearRect(0, 0, 270, 480);
  bctx.filter = 'blur(4px) brightness(1.2)'; bctx.drawImage(canvas, 0, 0, 270, 480); bctx.filter = 'none';
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = strength; ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(bloomC, 0, 0, W, H); ctx.restore();
}
function finish(t) {
  // vignette + grain
  ctx.save(); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  const v = ctx.createRadialGradient(CX, 860, 500, CX, 860, 1250);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.6)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.07;
  const ox = Math.floor((t * 977) % 256), oy = Math.floor((t * 613) % 256);
  ctx.translate(-ox, -oy); ctx.fillStyle = ctx.createPattern(GRAIN, 'repeat'); ctx.fillRect(0, 0, W + 256, H + 256);
  ctx.restore();
}

// ---------------------------------------------------------------- UI chrome
function brandBug(t, a = 1) {
  if (LOGO) return withAlpha(a, () => {
    drawLogo(110 + 64, 156, 128, 1);
    text('AUTOMOTIVE INTELLIGENCE', 110 + 128 + 18, 157, { size: 18, weight: 600, spacing: 4, align: 'left', color: COL.silver, a: 0.85 });
  });
  withAlpha(a, () => {
    text('BANG TAF', 110, 172, { size: 26, weight: 900, spacing: 5, align: 'left', color: COL.white, display: true });
    const w = measure('BANG TAF', 26, 900, 5, true);
    ctx.save(); alpha(1); ctx.fillStyle = COL.blue; ctx.fillRect(110 + w + 14, 160, 3, 24); ctx.restore();
    text('AUTOMOTIVE INTELLIGENCE', 110 + w + 30, 173, { size: 18, weight: 600, spacing: 4, align: 'left', color: COL.silver, a: 0.85 });
  });
}
function header(str, t, t0, t1, num) {
  const a = env(t, t0, t1, 0.5, 0.35);
  withAlpha(a, () => {
    const p = eo(prog(t, t0, t0 + 0.7));
    ctx.save(); alpha(1); ctx.fillStyle = COL.blue; ctx.fillRect(110, 214, 70 * p, 4); ctx.restore();
    text(num, 110 + 70 * p + 14, 216, { size: 22, weight: 700, spacing: 3, align: 'left', color: COL.blue, a: p });
    text(str, 110 + (1 - p) * -30, 262, { size: 44, weight: 900, spacing: 2, align: 'left', display: true, a: p });
  });
}
function chip(x, y, w, h, label, o = {}) {
  const on = o.on == null ? 1 : o.on;
  ctx.save(); alpha(o.a == null ? 1 : o.a);
  const p = rrect(x - w / 2, y - h / 2, w, h, h / 2);
  ctx.fillStyle = `rgba(${lerp(14, 10, on)},${lerp(18, 60, on)},${lerp(24, 100, on)},${lerp(0.75, 0.85, on)})`; ctx.fill(p);
  ctx.lineWidth = 2; ctx.strokeStyle = mixHex('#2a3340', COL.blue, on); ctx.stroke(p); ctx.restore();
  if (o.icon) icon(o.icon, x - w / 2 + h * 0.62, y, h * 0.55, on > 0.5 ? COL.blueHi : COL.silver, (o.a == null ? 1 : o.a), o.t || 0);
  text(label, x + (o.icon ? h * 0.32 : 0), y + 1, { size: o.size || 26, weight: 800, spacing: 1.5, color: on > 0.5 ? COL.white : COL.silver, a: o.a == null ? 1 : o.a });
}
function callout(px, py, lx, ly, label, o = {}) {
  const p = o.p == null ? 1 : o.p; if (p <= 0) return;
  const ex = lerp(px, lx, eo(clamp(p * 2))), ey = lerp(py, ly, eo(clamp(p * 2)));
  const path = new Path2D(); path.moveTo(px, py); path.lineTo(ex, ey);
  const dir = lx < px ? -1 : 1; const len = o.len || 120;
  if (p > 0.5) path.lineTo(ex + dir * len * eo(clamp((p - 0.5) * 2)), ey);
  glow(path, o.color || COL.blue, 2, 0.95, 3); dotGlow(px, py, 5, o.color || COL.blue, 1);
  if (p > 0.6) text(label, ex + dir * (len + 14), ey, { size: o.size || 30, weight: 800, spacing: 1.5, align: dir < 0 ? 'right' : 'left', a: eo(clamp((p - 0.6) * 2.5)), glow: 8 });
}

// ---------------------------------------------------------------- subtitles
function subtitles(t) {
  const cue = CUES.find((c) => t >= c.start - 0.08 && t < c.hold);
  if (!cue) return;
  const a = Math.min(eo(prog(t, cue.start - 0.08, cue.start + 0.14)), 1 - prog(t, cue.hold - 0.12, cue.hold));
  const tokens = [];
  cue.show.split(/(\*[^*]+\*)/).forEach((s) => { if (!s) return; const hl = s.startsWith('*');
    const parts = s.replace(/\*/g, '').split(' ');
    parts.forEach((w, i) => { if (!w) return;
      if (i === 0 && !hl && tokens.length && !s.startsWith(' ')) { tokens[tokens.length - 1].suf = (tokens[tokens.length - 1].suf || '') + w; return; }
      tokens.push({ w, hl }); }); });
  let size = 52; const maxW = 860; let lines;
  for (;;) {
    lines = [[]]; let cw = 0; const sp = measure(' ', size, 800);
    for (const tk of tokens) { const tw = measure(tk.w + (tk.suf || ''), size, 800); if (cw + tw > maxW && lines[lines.length - 1].length) { lines.push([]); cw = 0; } lines[lines.length - 1].push({ ...tk, tw }); cw += tw + sp; }
    if (lines.length <= 2 || size <= 40) break; size -= 3;
  }
  const lh = size * 1.22, cy = 1392, y0 = cy - (lines.length - 1) * lh / 2;
  const sp = measure(' ', size, 800);
  const widths = lines.map((l) => l.reduce((s, k) => s + k.tw, 0) + sp * (l.length - 1));
  const bw = Math.max(...widths) + 56, bh = lines.length * lh + 30;
  const sc = lerp(0.94, 1, eo(prog(t, cue.start - 0.08, cue.start + 0.16)));
  ctx.save(); ctx.translate(CX, cy); ctx.scale(sc, sc); ctx.translate(-CX, -cy);
  ctx.globalAlpha = a * 0.62; ctx.fillStyle = '#04070b'; ctx.fill(rrect(CX - bw / 2, cy - bh / 2, bw, bh, 18));
  ctx.globalAlpha = a * 0.9; ctx.fillStyle = COL.blue; ctx.fillRect(CX - bw / 2 + 18, cy - bh / 2, 46, 4);
  lines.forEach((l, i) => {
    let x = CX - widths[i] / 2; const y = y0 + i * lh;
    l.forEach((k) => {
      ctx.font = `800 ${size}px ${FONT}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.letterSpacing = '0px';
      ctx.globalAlpha = a; ctx.lineWidth = 6; ctx.strokeStyle = 'rgba(0,0,0,0.55)'; ctx.strokeText(k.w, x, y + 2);
      if (k.hl) { ctx.shadowColor = 'rgba(30,167,255,0.7)'; ctx.shadowBlur = 16; }
      if (k.suf) ctx.strokeText(k.suf, x + measure(k.w, size, 800), y + 2);
      ctx.fillStyle = k.hl ? '#35b4ff' : '#ffffff'; ctx.fillText(k.w, x, y + 2); ctx.shadowBlur = 0;
      if (k.suf) { ctx.fillStyle = '#ffffff'; ctx.fillText(k.suf, x + measure(k.w, size, 800), y + 2); }
      x += k.tw + sp;
    });
  });
  ctx.restore();
}

// ---------------------------------------------------------------- transitions
function transitionFX(t) {
  const cuts = [7, 17, 27, 39, 51];
  for (const c of cuts) {
    const d = t - c; if (d < -0.3 || d > 0.45) continue;
    const p = prog(t, c - 0.3, c + 0.45);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const y = lerp(-100, H + 100, eio(p));
    const g = ctx.createLinearGradient(0, y - 140, 0, y + 140);
    g.addColorStop(0, 'rgba(30,167,255,0)'); g.addColorStop(0.5, 'rgba(120,210,255,0.35)'); g.addColorStop(1, 'rgba(30,167,255,0)');
    ctx.fillStyle = g; ctx.fillRect(0, y - 140, W, 280);
    ctx.globalAlpha = 0.9; ctx.fillStyle = '#cdeeff'; ctx.fillRect(0, y - 1.5, W, 3);
    const fl = Math.max(0, 1 - Math.abs(d) / 0.18) * 0.22; ctx.globalAlpha = fl; ctx.fillStyle = '#9fdcff'; ctx.fillRect(0, 0, W, H);
    ctx.restore();
  }
}

// =================================================================== SCENES
// ---- Scene 1: hook (0-7)
function scene1(t) {
  const a = env(t, -1, 7.25, 0.1, 0.4);
  withAlpha(a, () => {
    const car = buildCar(BODIES.modern, 34, 'modern');
    const zoom = eio(prog(t, 2.6, 5.6));
    const yaw = lerp(-0.95, -0.35, t / 7) + zoom * 0.2, pitch = lerp(0.24, 0.34, zoom);
    const dist = lerp(9.2, 6.4, zoom), target = [lerp(0, 0.6, zoom), 0, lerp(0.75, 0.8, zoom)];
    const cam = camOrbit(target, yaw, pitch, dist, 38, CX, lerp(770, 690, zoom));
    floorGrid(cam, eo(prog(t, 0.2, 1.6)));
    shadowUnder(cam, [0, 0, 0], car.L);
    const reveal = eio(prog(t, 0.35, 2.3));
    const lights = eo(prog(t, 1.45, 1.75)) * (0.85 + 0.15 * Math.sin(t * 9));
    drawCar(cam, car, { reveal, a: lerp(1, 0.55, zoom), lights, fill: 0.04 });
    // dashboard power-up: arc across the cabin + gauge glows
    const dash = prog(t, 1.5, 2.2);
    if (dash > 0) {
      const L = car.L, dx = L * 0.17;
      const arc = Array.from({ length: 21 }, (_, i) => { const v = i / 20 - 0.5; return [dx + 0.06 * Math.cos(v * 3), v * 1.45, 1.02 + 0.03 * Math.cos(v * Math.PI)]; });
      glow(pathFrom(cam, arc, eo(dash)), COL.blueHi, 3, 1, 5);
      [[dx, 0.42, 1.06], [dx, 0, 1.06]].forEach((p, i) => { const q = P(cam, p); if (q) dotGlow(q[0], q[1], 7, i ? '#ffffff' : COL.blue, eo(dash) * (0.8 + 0.2 * Math.sin(t * 6 + i))); });
    }
    // internal technology
    const inner = eo(prog(t, 2.8, 4.0));
    if (inner > 0) withAlpha(inner, () => {
      const L = car.L;
      box3(cam, [L * 0.33, 0, 0.62], [0.55, 0.62, 0.42], { color: COL.silver, shade: '#8fa3b8', a: 0.9 });
      for (let i = 0; i < 4; i++) { const q = P(cam, [L * 0.33 - 0.18 + i * 0.12, 0, 0.86]); if (q) dotGlow(q[0], q[1], 3, COL.silver, 0.6 + 0.4 * Math.sin(t * 12 + i * 1.6)); }
      box3(cam, [L * 0.17, 0, 0.5], [0.34, 0.3, 0.3], { color: COL.silver, a: 0.7 });
      const ecu = [L * 0.2, 0.36, 0.98];
      box3(cam, ecu, [0.24, 0.16, 0.06], { color: COL.blueHi, shade: COL.blue, a: 1 });
      const sensors = [[L / 2 - 0.02, 0, 0.5], [L * 0.17, 0, 1.42], [L * 0.14, 0.97, 1.05], [L * 0.14, -0.97, 1.05], [-L / 2 + 0.02, 0, 0.95], [L / 2 - 0.1, 0.65, 0.45], [L / 2 - 0.1, -0.65, 0.45]];
      sensors.forEach((s, i) => {
        const route = [ecu, [ecu[0], ecu[1] * 0.5, 0.35], [s[0], s[1] * 0.8, 0.35], s];
        const rp = eo(prog(t, 3.0 + i * 0.08, 3.9 + i * 0.08));
        glow(pathFrom(cam, route, rp), COL.blue, 1.4, 0.7, 3);
        if (rp >= 1) { const ph = ((t * 0.9 + i * 0.37) % 1) * 3; const seg = Math.floor(ph), f = ph - seg;
          const pp = [lerp(route[seg][0], route[seg + 1][0], f), lerp(route[seg][1], route[seg + 1][1], f), lerp(route[seg][2], route[seg + 1][2], f)];
          const q = P(cam, pp); if (q) dotGlow(q[0], q[1], 3.5, COL.white, 0.9); }
        const q = P(cam, s); if (q) dotGlow(q[0], q[1], 5, COL.blueHi, rp);
      });
      // labels
      const qE = P(cam, [L * 0.33, 0.2, 0.84]), qC = P(cam, ecu), qS = P(cam, sensors[2]);
      if (qC) callout(qC[0], qC[1], qC[0] - 120, qC[1] - 210, TXT.computer, { p: prog(t, 3.7, 4.5), len: 60, size: 28 });
      if (qE) callout(qE[0], qE[1], qE[0] + 90, qE[1] - 190, TXT.engine, { p: prog(t, 4.4, 5.2), len: 60, size: 28 });
      if (qS) callout(qS[0], qS[1], qS[0] - 110, qS[1] + 150, TXT.sensors, { p: prog(t, 5.0, 5.8), len: 60, size: 28 });
    });
    // scan line during reveal
    if (t < 2.6) { const sy = lerp(420, 1140, eio(prog(t, 0.2, 2.3))); ctx.save(); ctx.globalCompositeOperation = 'lighter'; alpha(env(t, 0.2, 2.5, 0.2, 0.3) * 0.7);
      const g = ctx.createLinearGradient(0, sy - 30, 0, sy + 30); g.addColorStop(0, 'rgba(30,167,255,0)'); g.addColorStop(0.5, 'rgba(143,220,255,0.5)'); g.addColorStop(1, 'rgba(30,167,255,0)');
      ctx.fillStyle = g; ctx.fillRect(0, sy - 30, W, 60); ctx.restore(); }
  });
}
function scene1UI(t) {
  const a = env(t, -1, 7.2, 0.1, 0.35);
  withAlpha(a, () => {
    brandBug(t, eo(prog(t, 0.4, 1.2)));
    const tp = eo(prog(t, 0.6, 1.4));
    const lines = wrap(TXT.s1tag, 44, 900, 820);
    lines.forEach((l, i) => text(l, CX, 262 + i * 54 + (1 - tp) * 20, { size: 44, weight: 900, display: true, spacing: 1, a: tp * (1 - 0.35 * prog(t, 3.5, 4.2)) }));
    // formula
    const f0 = 3.55;
    const pc = eo(prog(t, f0, f0 + 0.5));
    text(TXT.car, CX - 40, 1105 + (1 - pc) * 30, { size: 92, weight: 900, display: true, spacing: 6, a: pc, glow: 20 });
    text('=', CX - 40 + measure(TXT.car, 92, 900, 6, true) / 2 + 60, 1105, { size: 92, weight: 300, color: COL.blue, a: eo(prog(t, f0 + 0.2, f0 + 0.6)) });
    const items = [[TXT.computer, 'chip'], [TXT.engine, 'engine'], [TXT.sensors, 'radar']];
    const cw = 268, gap = 22, x0 = CX - (cw * 3 + gap * 2) / 2 + cw / 2;
    items.forEach(([lab, ic], i) => {
      const p = prog(t, f0 + 0.5 + i * 0.6, f0 + 1.0 + i * 0.6); if (p <= 0) return;
      const x = x0 + i * (cw + gap), y = 1232 + (1 - eback(p)) * 40;
      withAlpha(eo(p), () => {
        ctx.save(); alpha(0.85); ctx.fillStyle = 'rgba(10,30,52,0.85)'; const r = rrect(x - cw / 2, y - 52, cw, 104, 16); ctx.fill(r); ctx.lineWidth = 2; ctx.strokeStyle = COL.blue; ctx.stroke(r); ctx.restore();
        icon(ic, x, y - 16, 44, COL.blueHi, 1, t);
        text(lab, x, y + 28, { size: lab.length > 8 ? 26 : 30, weight: 900, spacing: 2 });
        if (i > 0) text('+', x - cw / 2 - gap / 2, y, { size: 40, weight: 800, color: COL.blue });
      });
    });
  });
}

// ---- Scene 2: evolution (7-17)
function scene2(t) {
  const a = env(t, 6.85, 17.25, 0.35, 0.4);
  withAlpha(a, () => {
    const m = eio(prog(t, 9.7, 14.6));
    const body = lerpBody(BODIES.old, BODIES.modern, m);
    const car = buildCar(body, 34);
    const yaw = lerp(-1.5708 + 0.12, -0.75, eio(prog(t, 7, 16.5)));
    const cam = camOrbit([0, 0, 0.75], yaw, lerp(0.12, 0.22, prog(t, 7, 17)), lerp(7.6, 7.0, prog(t, 7, 17)), 36, CX, 790);
    floorGrid(cam, 0.8);
    shadowUnder(cam, [0, 0, 0], car.L);
    const col = mixHex('#b9c3cf', COL.blue, m), hi = mixHex('#ffffff', COL.blueHi, m);
    const morphFlash = Math.sin(Math.PI * prog(t, 9.7, 14.6));
    drawCar(cam, car, { color: col, hiColor: hi, a: 1, fill: 0.05, fillColor: mixHex('#6b7480', '#1a6fb0', m), wheelRot: -t * 3, lights: m });
    // morph particles streaming along the body
    if (morphFlash > 0.02) {
      const r = rng(11);
      for (let i = 0; i < 70; i++) {
        const ln = car.longs[Math.floor(r() * car.longs.length)]; const k = Math.floor(((r() + t * 0.6) % 1) * (ln.length - 1));
        const q = P(cam, ln[k]); if (q) dotGlow(q[0] + (r() - 0.5) * 6, q[1] + (r() - 0.5) * 6, 2.5, r() > 0.5 ? COL.white : COL.blueHi, morphFlash * 0.8);
      }
    }
    const L = car.L; const eng = P(cam, [L * 0.32, 0, 0.65]);
    // stage 1: mechanical — gears, rods, cable
    const s1 = 1 - prog(t, 9.6, 10.6);
    if (s1 > 0 && eng) withAlpha(s1, () => {
      icon('gear', eng[0], eng[1], 120, COL.silver, 0.95, t * 1.4);
      icon('gear', eng[0] + 88, eng[1] - 52, 70, COL.silver, 0.9, -t * 2.4 + 0.2);
      const rear = P(cam, [-L * 0.3, 0, 0.45]);
      if (rear) { ctx.save(); ctx.setLineDash([10, 8]); ctx.lineDashOffset = -t * 40; const p = new Path2D(); p.moveTo(eng[0], eng[1] + 30); p.lineTo(rear[0], rear[1]); glow(p, COL.silver, 2, 0.8, 0); ctx.restore(); }
    });
    // stage 2: electronic — chip with circuit traces
    const s2 = env(t, 9.9, 14.9, 0.6, 0.6);
    if (s2 > 0 && eng) withAlpha(s2, () => {
      const cx = eng[0], cy = eng[1];
      const r = rng(5); const tr = eo(prog(t, 10.0, 11.4));
      for (let i = 0; i < 14; i++) {
        const an = r() * Math.PI * 2, len = 60 + r() * 150; const p = new Path2D();
        const x1 = cx + Math.cos(an) * 34, y1 = cy + Math.sin(an) * 34; const x2 = cx + Math.cos(an) * len * tr, y2 = cy + Math.sin(an) * len * tr;
        p.moveTo(x1, y1); p.lineTo(x2, y1 + (y2 - y1) * 0.5); p.lineTo(x2, y2); glow(p, COL.blue, 1.6, 0.85, 3);
        if (tr >= 1) dotGlow(x2, y2, 3, COL.blueHi, 0.6 + 0.4 * Math.sin(t * 5 + i));
      }
      icon('chip', cx, cy, 78, COL.blueHi, 1, t);
      // electronic systems tags around car
      const tags = [['ABS', [-L * 0.3, car.hw, 0.36]], ['EFI', [L * 0.3, 0.2, 0.95]], ['AIRBAG', [L * 0.12, -0.3, 1.15]]];
      tags.forEach(([lab, p3], i) => { const q = P(cam, p3); if (q) callout(q[0], q[1], q[0] + (i === 1 ? 70 : -60), q[1] - 150 - i * 40, lab, { p: prog(t, 10.6 + i * 0.5, 11.4 + i * 0.5), len: 40, size: 26 }); });
    });
    // stage 3: intelligent — sensing field + neural links
    const s3 = eo(prog(t, 14.2, 15.0));
    if (s3 > 0) withAlpha(s3, () => {
      const nose = [L / 2, 0, 0.55];
      for (let k = 0; k < 4; k++) {
        const ph = ((t * 0.8 + k * 0.25) % 1), rr = 0.6 + ph * 4.5;
        const arc = Array.from({ length: 25 }, (_, i) => { const an = (i / 24 - 0.5) * 1.1; return [nose[0] + Math.cos(an) * rr, Math.sin(an) * rr, 0.05]; });
        glow(pathFrom(cam, arc), COL.blue, 2, (1 - ph) * 0.9, 4);
      }
      const nodes = [[L * 0.2, 0, 1.75], [-L * 0.1, 0.5, 1.9], [-L * 0.32, -0.4, 1.7], [L * 0.38, -0.5, 1.4], [L * 0.05, -0.7, 2.1], [0, 0, 1.2]].map((p) => P(cam, p));
      const links = [[0, 1], [1, 2], [0, 3], [0, 4], [4, 1], [5, 0], [5, 2], [5, 3], [2, 4]];
      links.forEach(([i, j], n) => { if (!nodes[i] || !nodes[j]) return; const p = new Path2D(); const lp = eo(prog(t, 14.3 + n * 0.08, 14.9 + n * 0.08));
        p.moveTo(nodes[i][0], nodes[i][1]); p.lineTo(lerp(nodes[i][0], nodes[j][0], lp), lerp(nodes[i][1], nodes[j][1], lp)); glow(p, COL.blueHi, 1.4, 0.7, 3); });
      nodes.forEach((q, i) => q && dotGlow(q[0], q[1], 5, i === 5 ? COL.white : COL.blueHi, 0.7 + 0.3 * Math.sin(t * 4 + i)));
    });
  });
}
function scene2UI(t) {
  const a = env(t, 6.9, 17.2, 0.35, 0.35);
  withAlpha(a, () => {
    brandBug(t);
    header(TXT.evoTitle, t, 7.0, 17.2, '01');
    // timeline
    const stages = [[TXT.mechanical, 'gear', 7.2, 9.8], [TXT.electronic, 'chip', 9.8, 14.3], [TXT.intelligent, 'brain', 14.3, 99]];
    const y = 360, xs = [CX - 290, CX, CX + 290];
    const lineP = eo(prog(t, 7.2, 8.0));
    ctx.save(); alpha(0.5); ctx.fillStyle = '#26303c'; ctx.fillRect(xs[0], y - 2, (xs[2] - xs[0]) * lineP, 4); ctx.restore();
    const fillTo = t < 9.8 ? 0 : t < 14.3 ? lerp(0, 0.5, eo(prog(t, 9.8, 10.6))) : lerp(0.5, 1, eo(prog(t, 14.3, 15.1)));
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; alpha(1); ctx.fillStyle = COL.blue; ctx.fillRect(xs[0], y - 2, (xs[2] - xs[0]) * fillTo, 4); ctx.restore();
    stages.forEach(([lab, ic, s0, s1], i) => {
      const ap = eo(prog(t, 7.3 + i * 0.15, 7.9 + i * 0.15)); const on = env(t, s0, s1 + 0.3, 0.35, 0.3);
      const done = t > s0 ? 1 : 0;
      withAlpha(ap, () => {
        ctx.save(); alpha(1); ctx.beginPath(); ctx.arc(xs[i], y, 40 + on * 6, 0, Math.PI * 2); ctx.fillStyle = on > 0.5 ? 'rgba(12,60,100,0.95)' : '#0c1118'; ctx.fill();
        ctx.lineWidth = 3; ctx.strokeStyle = done ? COL.blue : '#2a3440'; ctx.stroke(); ctx.restore();
        icon(ic, xs[i], y, 44, done ? COL.blueHi : COL.dim, 1, t);
        text(lab, xs[i], y + 76, { size: on > 0.5 ? 30 : 26, weight: 900, spacing: 2, color: done ? COL.white : COL.dim, glow: on > 0.5 ? 12 : 0 });
        if (i < 2) text('→', (xs[i] + xs[i + 1]) / 2, y, { size: 36, weight: 700, color: t > stages[i + 1][2] ? COL.blue : COL.dim });
      });
    });
    // stage tags under the car
    const tags = [[TXT.mechTags, 7.4, 9.9], [TXT.elecTags, 10.0, 14.4], [TXT.intTags, 14.5, 17.3]];
    tags.forEach(([s, a0, a1], i) => { const e = env(t, a0, a1, 0.4, 0.3); if (e <= 0) return;
      const w = measure(s, 32, 700) + 60; withAlpha(e, () => {
        ctx.save(); alpha(0.8); ctx.fillStyle = 'rgba(8,14,22,0.85)'; const r = rrect(CX - w / 2, 1155 - 32, w, 64, 32); ctx.fill(r); ctx.strokeStyle = i ? COL.blue : COL.silver; ctx.lineWidth = 2; ctx.stroke(r); ctx.restore();
        text(s, CX, 1156 + (1 - eo(prog(t, a0, a0 + 0.4))) * 16, { size: 32, weight: 700, color: i ? COL.white : COL.silver });
      }); });
    // large kinetic stage word
    const big = t < 9.8 ? TXT.mechanical : t < 14.3 ? TXT.electronic : TXT.intelligent;
    const b0 = t < 9.8 ? 7.4 : t < 14.3 ? 9.9 : 14.4; const b1 = t < 9.8 ? 9.85 : t < 14.3 ? 14.35 : 17.3;
    withAlpha(env(t, b0, b1, 0.3, 0.25), () => kinetic(big, CX, 1255, t, b0, { size: 74, weight: 900, display: true, spacing: 6, color: t < 9.8 ? COL.silver : COL.blue, glow: t < 9.8 ? 0 : 18 }));
  });
}

// ---- Scene 3: ECU brain (17-27)
function ecuModel(cam, c, yaw, a, t) {
  const V = box3(cam, c, [1.5, 1.0, 0.26], { yaw, shade: '#9fb2c6', color: COL.silver, a, edgeA: 0.8 });
  // cooling fins on top
  for (let i = 0; i < 9; i++) { const x = -0.6 + i * 0.12; const p1 = add(rotZ([x, -0.42, 0.13], yaw), c), p2 = add(rotZ([x, 0.15, 0.13], yaw), c);
    glow(pathFrom(cam, [p1, p2]), COL.silver, 1.2, a * 0.55, 0); }
  // connector block + pins
  box3(cam, add(c, rotZ([0.0, 0.62, -0.02], yaw)), [1.1, 0.24, 0.2], { yaw, shade: '#3a4656', color: COL.blue, a, edgeA: 0.9 });
  for (let i = 0; i < 12; i++) { const q = P(cam, add(c, rotZ([-0.45 + i * 0.082, 0.75, -0.02], yaw))); if (q) dotGlow(q[0], q[1], 2.2, COL.blueHi, a * (0.5 + 0.5 * Math.sin(t * 8 + i))); }
  // glowing die
  const die = [[-0.22, 0.25], [0.22, 0.25], [0.22, -0.2], [-0.22, -0.2]].map(([x, y]) => add(rotZ([x + 0.35, y - 0.05, 0.135], yaw), c));
  const p = pathFrom(cam, die.concat([die[0]]));
  ctx.save(); alpha(a * 0.9); ctx.fillStyle = 'rgba(30,167,255,0.25)'; ctx.fill(p); ctx.restore();
  glow(p, COL.blueHi, 2, a, 5);
  return V;
}
function scene3(t) {
  const a = env(t, 16.85, 27.25, 0.4, 0.4);
  withAlpha(a, () => {
    const intro = eo(prog(t, 17.0, 18.6));
    const yaw = -0.5 + Math.sin(t * 0.35) * 0.35 + (1 - intro) * 1.2;
    const cam = camOrbit([0, 0, 0], -1.5708 + 0.25, lerp(0.55, 0.62, prog(t, 17, 27)), lerp(9, 6.4, intro), 32, CX, 790);
    // halo rings
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 3; i++) { const r = 210 + i * 70 + Math.sin(t * 1.3 + i) * 6; alpha(a * 0.15 * intro); ctx.strokeStyle = COL.blue; ctx.lineWidth = 2;
      ctx.setLineDash([4 + i * 6, 10]); ctx.lineDashOffset = t * (20 + i * 15) * (i % 2 ? -1 : 1); ctx.beginPath(); ctx.ellipse(CX, 810, r, r * 0.42, 0, 0, Math.PI * 2); ctx.stroke(); }
    ctx.restore();
    ecuModel(cam, [0, 0, 0], yaw, intro, t);
    // network nodes (2D, around the ECU)
    const nodes = [
      { lab: TXT.nSensors, ic: 'radar', x: CX - 300, y: 575, t0: 20.9, input: true },
      { lab: TXT.nEngine, ic: 'engine', x: CX + 300, y: 575, t0: 22.8 },
      { lab: TXT.nTrans, ic: 'gearbox', x: CX + 330, y: 985, t0: 23.5 },
      { lab: TXT.nBrakes, ic: 'brake', x: CX - 330, y: 985, t0: 24.2 },
      { lab: TXT.nControl, ic: 'control', x: CX, y: 1040, t0: 24.8 },
    ];
    const ec = [CX, 790];
    nodes.forEach((n, i) => {
      const p = prog(t, n.t0, n.t0 + 0.6); if (p <= 0) return;
      const cp = [lerp(ec[0], n.x, 0.5) + (i % 2 ? 60 : -60), lerp(ec[1], n.y, 0.5) - 40];
      const path = new Path2D(); const N = 30; const lp = eo(p);
      const bez = (u) => [(1 - u) * (1 - u) * ec[0] + 2 * (1 - u) * u * cp[0] + u * u * n.x, (1 - u) * (1 - u) * ec[1] + 2 * (1 - u) * u * cp[1] + u * u * n.y];
      for (let k = 0; k <= N * lp; k++) { const q = bez(k / N); k ? path.lineTo(q[0], q[1]) : path.moveTo(q[0], q[1]); }
      glow(path, COL.blue, 2, 0.8, 4);
      if (p >= 1) for (let k = 0; k < 3; k++) { let u = ((t * 0.7 + k / 3 + i * 0.13) % 1); if (n.input) u = 1 - u; const q = bez(u); dotGlow(q[0], q[1], 4, n.input ? COL.white : COL.blueHi, 0.95); }
      withAlpha(eo(p), () => {
        const s = lerp(0.6, 1, eback(p));
        ctx.save(); ctx.translate(n.x, n.y); ctx.scale(s, s);
        const hex = new Path2D(); for (let k = 0; k < 6; k++) { const an = Math.PI / 6 + k * Math.PI / 3; k ? hex.lineTo(Math.cos(an) * 62, Math.sin(an) * 62) : hex.moveTo(Math.cos(an) * 62, Math.sin(an) * 62); } hex.closePath();
        alpha(0.92); ctx.fillStyle = '#0a1a2a'; ctx.fill(hex); ctx.lineWidth = 3; ctx.strokeStyle = n.input ? COL.white : COL.blue; ctx.stroke(hex);
        ctx.restore();
        icon(n.ic, n.x, n.y, 56 * s, n.input ? COL.white : COL.blueHi, 1, t);
        text(n.lab, n.x, n.y + 92, { size: 26, weight: 900, spacing: 1.5 });
        text(n.input ? TXT.inputs : TXT.outputs, n.x, n.y - 84, { size: 18, weight: 700, spacing: 4, color: n.input ? COL.silver : COL.blue });
      });
    });
  });
}
function scene3UI(t) {
  const a = env(t, 16.9, 27.2, 0.4, 0.35);
  withAlpha(a, () => {
    brandBug(t);
    header(TXT.ecuTitle, t, 17.0, 27.2, '02');
    const p = eo(prog(t, 17.6, 18.3));
    text(TXT.ecuName, CX, 345 + (1 - p) * 20, { size: 96, weight: 900, display: true, spacing: 14, a: p * (1 - 0.6 * prog(t, 20.6, 21.2)), glow: 24 });
    text(TXT.ecuFull, CX, 412, { size: 28, weight: 700, spacing: 6, color: COL.blueHi, a: eo(prog(t, 18.0, 18.6)) * (1 - 0.6 * prog(t, 20.6, 21.2)) });
    // equation
    const e0 = 25.35;
    if (t > e0) {
      const parts = TXT.ecuEq.split(' + ');
      const size = 40; const gap = 22; const ws = parts.map((s) => measure(s, size, 900, 2, true)); const plus = measure('+', size, 800);
      const total = ws.reduce((s, x) => s + x, 0) + (plus + gap * 2) * (parts.length - 1);
      let x = CX - total / 2;
      const y = 1225;
      ctx.save(); alpha(eo(prog(t, e0, e0 + 0.4)) * 0.85); ctx.fillStyle = 'rgba(6,16,28,0.9)'; ctx.fill(rrect(CX - total / 2 - 30, y - 42, total + 60, 84, 42)); ctx.strokeStyle = COL.blue; ctx.lineWidth = 2; ctx.stroke(rrect(CX - total / 2 - 30, y - 42, total + 60, 84, 42)); ctx.restore();
      parts.forEach((s, i) => {
        const pp = prog(t, e0 + 0.1 + i * 0.22, e0 + 0.5 + i * 0.22);
        text(s, x + ws[i] / 2, y + (1 - eback(pp)) * 24, { size, weight: 900, spacing: 2, display: true, a: eo(pp), color: i === 0 ? COL.blueHi : COL.white });
        x += ws[i];
        if (i < parts.length - 1) { text('+', x + gap + plus / 2, y, { size, weight: 800, color: COL.blue, a: eo(pp) }); x += plus + gap * 2; }
      });
    }
    // fact chip
    const f = env(t, 21.0, 25.2, 0.4, 0.3);
    if (f > 0) withAlpha(f, () => { const w = measure(TXT.ecuFact, 26, 700) + 70;
      ctx.save(); alpha(0.85); ctx.fillStyle = 'rgba(8,14,22,0.9)'; ctx.fill(rrect(CX - w / 2, 1200, w, 52, 26)); ctx.restore();
      icon('chip', CX - w / 2 + 30, 1226, 26, COL.blue, 1, t);
      text(TXT.ecuFact, CX + 14, 1227, { size: 26, weight: 700, color: COL.silver }); });
  });
}

// ---- Scene 4: safety (27-39)
const PH = { cam: [27.0, 30.4], bsm: [30.4, 33.0], lane: [33.0, 35.4], adas: [35.4, 39.2] };
function scene4(t) {
  const a = env(t, 26.85, 39.25, 0.4, 0.4);
  withAlpha(a, () => {
    const car = buildCar(BODIES.modern, 34, 'modern');
    const drift = PH.lane[0] < t && t < PH.lane[1] ? Math.sin(Math.PI * prog(t, PH.lane[0] + 0.2, PH.lane[1] - 0.2)) * 0.55 : 0;
    const carPos = [0, -drift, 0];
    const intro4 = 1 - eo(prog(t, 27, 28.4));
    const sway = Math.sin(t * 0.5) * 0.8;
    const cam = camLook([lerp(-10.5, -9.5, prog(t, 27, 39)) - intro4 * 3, -1.4 + sway, lerp(5.6, 5.0, prog(t, 27, 39)) + intro4 * 2], [6, 0.6, 0], 50, CX, 800);
    const speed = 14, off = (t * speed) % 6;
    // road
    const roadW = 5.4;
    const surf = [[-6, -roadW, 0], [60, -roadW, 0], [60, roadW, 0], [-6, roadW, 0]].map((p) => P(cam, p));
    if (surf.every(Boolean)) { ctx.save(); alpha(0.85); ctx.fillStyle = '#0b0f14'; ctx.beginPath(); surf.forEach((q, i) => (i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]))); ctx.fill(); ctx.restore(); }
    [-roadW, roadW].forEach((y) => glow(pathFrom(cam, Array.from({ length: 34 }, (_, i) => [-8 + i * 2, y, 0])), COL.silver, 2.5, 0.75, 3));
    const laneOn = env(t, PH.lane[0], PH.lane[1] + 0.3, 0.3, 0.4);
    [-1.8, 1.8].forEach((y) => {
      const dp = new Path2D();
      for (let x = -6 - off; x < 60; x += 6) { const a1 = P(cam, [x, y, 0]), a2 = P(cam, [x + 3, y, 0]); if (a1 && a2) { dp.moveTo(a1[0], a1[1]); dp.lineTo(a2[0], a2[1]); } }
      glow(dp, laneOn > 0.05 ? mixHex('#c9d1db', COL.blueHi, laneOn) : COL.silver, 3 + laneOn * 2, 0.8, 3);
    });
    // lane detection overlay
    if (laneOn > 0) withAlpha(laneOn, () => {
      [-1.8, 1.8].forEach((y) => {
        const pts = Array.from({ length: 12 }, (_, i) => [carPos[0] + 1 + i * 1.6, y, 0.02]);
        glow(pathFrom(cam, pts, eo(prog(t, PH.lane[0], PH.lane[0] + 0.6))), COL.blueHi, 5, 0.9, 4);
        pts.forEach((p, i) => { const q = P(cam, p); if (q && i % 2 === 0) dotGlow(q[0], q[1], 4, COL.white, 0.8 * eo(prog(t, PH.lane[0] + i * 0.05, PH.lane[0] + 0.4 + i * 0.05))); });
      });
      const fill = [[carPos[0] + 1, -1.8, 0.01], [carPos[0] + 18, -1.8, 0.01], [carPos[0] + 18, 1.8, 0.01], [carPos[0] + 1, 1.8, 0.01]].map((p) => P(cam, p));
      if (fill.every(Boolean)) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; alpha(0.12); ctx.fillStyle = COL.blue; ctx.beginPath(); fill.forEach((q, i) => (i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]))); ctx.fill(); ctx.restore(); }
    });
    // 360 camera
    const c360 = env(t, PH.cam[0] + 0.6, PH.cam[1] + 0.25, 0.5, 0.4);
    if (c360 > 0) withAlpha(c360, () => {
      const L = car.L;
      const camsP = [[[L / 2, 0, 0.6], 0], [[-L / 2, 0, 0.9], Math.PI], [[L * 0.14, 0.97, 1.0], Math.PI / 2], [[L * 0.14, -0.97, 1.0], -Math.PI / 2]];
      camsP.forEach(([p, dir], i) => {
        const pp = add(p, carPos); const fan = [pp];
        for (let k = 0; k <= 12; k++) { const an = dir + (k / 12 - 0.5) * 2.6; fan.push([pp[0] + Math.cos(an) * 3.2, pp[1] + Math.sin(an) * 3.2, 0.02]); }
        const q = fan.map((v) => P(cam, v)); if (!q.every(Boolean)) return;
        ctx.save(); ctx.globalCompositeOperation = 'lighter'; const pulse = 0.5 + 0.5 * Math.sin(t * 3 + i * 1.5);
        alpha(0.10 + 0.06 * pulse); ctx.fillStyle = COL.blue; ctx.beginPath(); q.forEach((v, k) => (k ? ctx.lineTo(v[0], v[1]) : ctx.moveTo(v[0], v[1]))); ctx.closePath(); ctx.fill(); ctx.restore();
        glow(pathFrom(cam, fan.slice(1)), COL.blueHi, 1.6, 0.7, 3);
        dotGlow(q[0][0], q[0][1], 5, COL.white, 1);
      });
      const ring = Array.from({ length: 49 }, (_, k) => { const an = (k / 48) * Math.PI * 2; return [carPos[0] + Math.cos(an) * 3.6, carPos[1] + Math.sin(an) * 3.0, 0.02]; });
      glow(pathFrom(cam, ring), COL.blue, 2, 0.8, 4);
      const sw = (t * 2.2) % (Math.PI * 2);
      const swp = Array.from({ length: 9 }, (_, k) => { const an = sw + k * 0.06; return [carPos[0] + Math.cos(an) * 3.6, carPos[1] + Math.sin(an) * 3.0, 0.03]; });
      glow(pathFrom(cam, swp), COL.white, 5, 0.9, 4);
    });
    // other vehicle for blind-spot demo (left-rear lane, overtaking)
    const bsmOn = env(t, PH.bsm[0], PH.bsm[1] + 0.2, 0.3, 0.4);
    const other = buildCar(BODIES.modern, 18, 'modern_lo');
    if (t > PH.bsm[0] - 0.4 && t < PH.bsm[1] + 1.0) {
      const ox = lerp(-6.5, 4.5, eio(prog(t, PH.bsm[0] - 0.4, PH.bsm[1] + 1.0)));
      const pos = [ox, 3.6, 0];
      const inZone = ox > -5.5 && ox < -0.5;
      // zone
      const zone = [[-5.6, 1.1, 0.02], [-0.6, 1.1, 0.02], [-0.6, 5.2, 0.02], [-5.6, 5.2, 0.02]].map((p) => P(cam, add(p, carPos)));
      if (zone.every(Boolean)) withAlpha(bsmOn, () => { const c = inZone ? COL.amber : COL.blue; ctx.save(); ctx.globalCompositeOperation = 'lighter';
        alpha(inZone ? 0.25 + 0.12 * Math.sin(t * 14) : 0.12); ctx.fillStyle = c; ctx.beginPath(); zone.forEach((q, i) => (i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]))); ctx.closePath(); ctx.fill(); ctx.restore();
        const zp = new Path2D(); zone.forEach((q, i) => (i ? zp.lineTo(q[0], q[1]) : zp.moveTo(q[0], q[1]))); zp.closePath(); glow(zp, c, 2, 0.9, 3);
        const zoneR = [[-5.6, -1.1, 0.02], [-0.6, -1.1, 0.02], [-0.6, -5.2, 0.02], [-5.6, -5.2, 0.02]].map((p) => P(cam, add(p, carPos)));
        if (zoneR.every(Boolean)) { const zr = new Path2D(); zoneR.forEach((q, i) => (i ? zr.lineTo(q[0], q[1]) : zr.moveTo(q[0], q[1]))); zr.closePath(); glow(zr, COL.blue, 1.5, 0.6, 0); }
        if (inZone) { const mq = P(cam, add([car.L * 0.14, 1.0, 1.05], carPos)); if (mq) dotGlow(mq[0], mq[1], 9, COL.amber, 0.8 + 0.2 * Math.sin(t * 16)); }
      });
      drawCar(cam, other, { pos, color: COL.silver, hiColor: '#ffffff', a: 0.85, ringA: 0.15, fill: 0.03, fillColor: '#5a6470', wheelRot: -t * 6 });
    }
    // ADAS: radar + lead vehicle + following distance
    const adOn = env(t, PH.adas[0], 39.3, 0.4, 0.4);
    if (adOn > 0) withAlpha(adOn, () => {
      const lead = [lerp(16, 11.5, eio(prog(t, PH.adas[0], PH.adas[0] + 2))), 0, 0];
      drawCar(cam, other, { pos: lead, color: COL.silver, hiColor: '#ffffff', a: 0.85, ringA: 0.15, fill: 0.03, fillColor: '#5a6470', wheelRot: -t * 6, lights: 0.6 });
      const nose = add([car.L / 2, 0, 0.5], carPos);
      for (let k = 0; k < 5; k++) { const ph = (t * 1.1 + k / 5) % 1; const rr = 0.4 + ph * 9;
        const arc = Array.from({ length: 21 }, (_, i) => { const an = (i / 20 - 0.5) * 0.7; return [nose[0] + Math.cos(an) * rr, nose[1] + Math.sin(an) * rr, 0.04]; });
        glow(pathFrom(cam, arc), COL.blue, 2.4, (1 - ph) * 0.9, 4); }
      const gapLen = lead[0] - car.L / 2 - nose[0];
      for (let k = 0; k < 6; k++) { const x = nose[0] + 0.4 + k * (gapLen - 2.0) / 5; const bar = [[x, -1.2, 0.03], [x, 1.2, 0.03]];
        glow(pathFrom(cam, bar), k > 3 ? COL.amber : COL.blueHi, 3, 0.4 + 0.6 * ((Math.floor(t * 6) + k) % 6 === 0 ? 1 : 0.5), 3); }
    });
    // the car itself
    shadowUnder(cam, carPos, car.L, 0.9);
    drawCar(cam, car, { pos: carPos, a: 1, fill: 0.06, wheelRot: -t * 8, lights: 1 });
  });
}
function scene4UI(t) {
  const a = env(t, 26.9, 39.2, 0.4, 0.35);
  withAlpha(a, () => {
    brandBug(t);
    header(TXT.safetyTitle, t, 27.0, 39.2, '03');
    const nl = wrap(TXT.safetyNote, 24, 600, 820);
    nl.forEach((l, i) => text(l, 110, 312 + i * 32, { size: 24, weight: 600, align: 'left', color: COL.silver, a: eo(prog(t, 27.5, 28.2)) * 0.95 }));
    // feature chips 2x2
    const feats = [[TXT.f360, '360', PH.cam], [TXT.fBsm, 'blind', PH.bsm], [TXT.fLane, 'lane', PH.lane], [TXT.fAdas, 'adas', PH.adas]];
    const cw = 410, ch = 70;
    feats.forEach(([lab, ic, ph], i) => {
      const x = CX + (i % 2 ? 1 : -1) * (cw / 2 + 10), y = 1165 + Math.floor(i / 2) * (ch + 16);
      const ap = eo(prog(t, 27.6 + i * 0.12, 28.1 + i * 0.12));
      const on = env(t, ph[0], ph[1], 0.25, 0.25);
      chip(x, y + (1 - ap) * 20, cw, ch, lab, { a: ap, on, icon: ic, t, size: lab.length > 18 ? 22 : 25 });
      if (on > 0.02) { const pr = prog(t, ph[0], ph[1]); ctx.save(); ctx.globalCompositeOperation = 'lighter'; alpha(on); ctx.fillStyle = COL.blueHi; ctx.fillRect(x - cw / 2 + ch / 2, y + ch / 2 - 4, (cw - ch) * pr, 3); ctx.restore(); }
    });
    // status popups
    const pops = [[TXT.warning, 'warning', COL.amber, 31.2, 32.9], [TXT.laneOk, 'lane', COL.blueHi, 33.6, 35.4], [TXT.braking, 'adas', COL.blueHi, 36.0, 39.2]];
    pops.forEach(([lab, ic, c, a0, a1]) => { const e = env(t, a0, a1, 0.25, 0.25); if (e <= 0) return;
      const w = measure(lab, 28, 900, 2) + 100; const y = 470;
      withAlpha(e, () => { ctx.save(); alpha(0.9); ctx.fillStyle = 'rgba(6,10,16,0.9)'; const r = rrect(CX - w / 2, y - 34, w, 68, 12); ctx.fill(r); ctx.lineWidth = 2.5; ctx.strokeStyle = c; ctx.stroke(r); ctx.restore();
        icon(ic, CX - w / 2 + 40, y, 36, c, 1, t); text(lab, CX + 26, y + 1, { size: 28, weight: 900, spacing: 2, color: c }); }); });
    const sub = env(t, PH.adas[0] + 0.5, 39.2, 0.4, 0.3);
    if (sub > 0) text(TXT.adasSub, CX, 532, { size: 26, weight: 600, color: COL.silver, a: sub });
  });
}

// ---- Scene 5: Proton (39-51)
const CARD_T = [[39.0, 45.1], [45.1, 51.2]];
const ITEM_ICONS = ['screen', '360', 'wheel', 'link'];
function itemIcon(i, label) {
  const l = label.toUpperCase();
  if (/COMFORT|KESELESAAN/.test(l)) return 'comfort';
  if (/CONNECT|KETERHUBUNGAN/.test(l)) return 'link';
  return ITEM_ICONS[i];
}
function scene5(t) {
  const a = env(t, 38.85, 51.25, 0.4, 0.4);
  withAlpha(a, () => {
    CARD_T.forEach(([c0, c1], ci) => {
      const e = env(t, c0, c1, 0.5, 0.4); if (e <= 0) return;
      const card = TXT.cards[ci];
      withAlpha(e, () => {
        const car = buildCar(BODIES[card.body], 34, card.body);
        const spin = lerp(-0.6, 0.35, prog(t, c0, c1)) + (1 - eo(prog(t, c0, c0 + 1.2))) * -1.2;
        const cam = camOrbit([0, 0, 0.7], spin - 0.9, 0.2, 9.4, 34, CX, 650);
        floorGrid(cam, 0.8, 6);
        shadowUnder(cam, [0, 0, 0], car.L);
        drawCar(cam, car, { a: 1, reveal: eio(prog(t, c0 + 0.1, c0 + 1.3)), fill: 0.07, lights: 1, wheelRot: 0 });
        // anchor points on the car for each callout
        const L = car.L;
        const anchors = [[L * 0.12, 0.25, 1.1], [L * 0.14, 0.97, 1.05], [L / 2 - 0.02, 0, 0.55], ci === 0 ? [L * 0.05, 0, 1.3] : [-L * 0.05, 0, card.body === 'suv_compact' ? 1.6 : 1.6]];
        anchors.forEach((p3, i) => { const q = P(cam, p3); const pp = prog(t, c0 + 1.2 + i * 0.75, c0 + 1.8 + i * 0.75);
          if (q && pp > 0) { dotGlow(q[0], q[1], 6, COL.blueHi, eo(pp) * (0.7 + 0.3 * Math.sin(t * 5 + i)));
            const ring = 10 + 26 * ((t * 1.2 + i * 0.3) % 1); ctx.save(); ctx.globalCompositeOperation = 'lighter'; alpha(eo(pp) * (1 - ((t * 1.2 + i * 0.3) % 1))); ctx.strokeStyle = COL.blueHi; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(q[0], q[1], ring, 0, Math.PI * 2); ctx.stroke(); ctx.restore(); } });
      });
    });
  });
}
function scene5UI(t) {
  const a = env(t, 38.9, 51.2, 0.4, 0.35);
  withAlpha(a, () => {
    brandBug(t);
    header(TXT.protonTitle, t, 39.0, 51.2, '04');
    CARD_T.forEach(([c0, c1], ci) => {
      const e = env(t, c0, c1, 0.5, 0.4); if (e <= 0) return;
      const card = TXT.cards[ci];
      withAlpha(e, () => {
        const p = eo(prog(t, c0 + 0.2, c0 + 0.8));
        text(card.model, 110 + (1 - p) * 40, 340, { size: 54, weight: 900, display: true, spacing: 2, align: 'left', a: p, glow: 14 });
        text(card.sub, 110, 392, { size: 26, weight: 600, align: 'left', color: COL.blueHi, a: eo(prog(t, c0 + 0.4, c0 + 1.0)) });
        text(TXT.illus, CX, 842, { size: 20, weight: 500, color: COL.dim, a: eo(prog(t, c0 + 0.8, c0 + 1.4)) });
        card.items.forEach(([lab, val], i) => {
          const pp = prog(t, c0 + 1.2 + i * 0.75, c0 + 1.8 + i * 0.75); if (pp <= 0) return;
          const y = 872 + i * 88, x = 110;
          withAlpha(eo(pp), () => {
            const dx = (1 - eo(pp)) * 60;
            ctx.save(); alpha(0.85); ctx.fillStyle = 'rgba(8,16,26,0.88)'; const r = rrect(x + dx, y, 820, 80, 14); ctx.fill(r); ctx.lineWidth = 1.5; ctx.strokeStyle = 'rgba(30,167,255,0.6)'; ctx.stroke(r);
            ctx.fillStyle = COL.blue; ctx.fillRect(x + dx, y + 14, 4, 52); ctx.restore();
            icon(itemIcon(i, lab), x + dx + 50, y + 40, 40, COL.blueHi, 1, t);
            text(lab, x + dx + 96, y + 24, { size: 19, weight: 800, spacing: 3, align: 'left', color: COL.blue });
            let vs = 30; while (measure(val, vs, 700) > 700 && vs > 22) vs -= 1;
            text(val, x + dx + 96, y + 54, { size: vs, weight: 700, align: 'left' });
          });
        });
      });
    });
    const nl = wrap(TXT.protonNote, 21, 500, 830);
    nl.forEach((l, i) => text(l, CX, 1236 + i * 27, { size: 21, weight: 500, color: COL.silver, a: eo(prog(t, 40.5, 41.2)) * 0.9 }));
  });
}

// ---- Scene 6: ending (51-60)
const STREAKS = (() => { const r = rng(21); return Array.from({ length: 46 }, () => ({ y: (r() < 0.5 ? -1 : 1) * (6.5 + r() * 9), z: 0.3 + r() * 5, x: r() * 120, s: 0.7 + r() * 0.8, w: r() })); })();
const SKY = (() => { const r = rng(33); let x = -40; const b = []; while (x < W + 40) { const w = 30 + r() * 70; b.push({ x, w, h: 40 + r() * 190 }); x += w + 4; } return b; })();
function scene6(t) {
  const a = env(t, 50.85, 61, 0.4, 0.1);
  withAlpha(a, () => {
    const crane = eio(prog(t, 54.6, 57.2));
    const carX = lerp(0, 9, ei(prog(t, 53.5, 57.5))) + (t - 51) * 0.0;
    const cam = camLook([lerp(-7.5, -10, crane), lerp(2.2, 0.6, crane), lerp(1.7, 11, crane)], [lerp(6, 18, crane), 0, lerp(0.9, 0, crane)], lerp(46, 50, crane), CX, lerp(820, 700, crane));
    const hz = P(cam, [400, 0, 0]);
    // horizon glow & skyline
    if (hz) { const hy = hz[1];
      ctx.save(); const g = ctx.createLinearGradient(0, hy - 380, 0, hy + 60); g.addColorStop(0, 'rgba(30,167,255,0)'); g.addColorStop(0.75, 'rgba(30,120,200,0.22)'); g.addColorStop(1, 'rgba(160,220,255,0.35)');
      alpha(1 - crane * 0.6); ctx.fillStyle = g; ctx.fillRect(0, hy - 380, W, 440);
      alpha((1 - crane) * 0.9); ctx.fillStyle = '#05080c'; SKY.forEach((b) => ctx.fillRect(b.x, hy - b.h * 0.8, b.w, b.h * 0.8));
      ctx.globalCompositeOperation = 'lighter'; const r = rng(44); SKY.forEach((b) => { for (let k = 0; k < 4; k++) { if (r() < 0.5) continue; alpha((1 - crane) * 0.5 * r()); ctx.fillStyle = r() > 0.7 ? COL.blueHi : '#9fb6cc'; ctx.fillRect(b.x + r() * b.w, hy - r() * b.h * 0.75, 3, 3); } });
      ctx.restore(); }
    // road
    const roadW = 5.4, speed = 26, off = (t * speed) % 8;
    const surf = [[-20, -roadW, 0], [400, -roadW, 0], [400, roadW, 0], [-20, roadW, 0]].map((p) => P(cam, p));
    if (surf.every(Boolean)) { ctx.save(); alpha(1); const g = ctx.createLinearGradient(0, surf[1][1], 0, H); g.addColorStop(0, '#0d1218'); g.addColorStop(1, '#06080b'); ctx.fillStyle = g; ctx.beginPath(); surf.forEach((q, i) => (i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]))); ctx.fill(); ctx.restore(); }
    [-roadW, roadW].forEach((y) => glow(pathFrom(cam, Array.from({ length: 40 }, (_, i) => [-20 + i * 10.5, y, 0])), COL.blueHi, 3, 0.9, 4));
    [-1.8, 1.8].forEach((y) => { const dp = new Path2D(); for (let x = -20 - off; x < 300; x += 8) { const a1 = P(cam, [x, y, 0]), a2 = P(cam, [x + 4, y, 0]); if (a1 && a2) { dp.moveTo(a1[0], a1[1]); dp.lineTo(a2[0], a2[1]); } } glow(dp, COL.silver, 3, 0.85, 3); });
    // light streaks (motion)
    STREAKS.forEach((s) => { const x = ((s.x - t * speed * 1.6 * s.s) % 120 + 120) % 120 - 20; const len = 5 + s.s * 6;
      const p1 = P(cam, [x, s.y, s.z]), p2 = P(cam, [x + len, s.y, s.z]); if (!p1 || !p2) return; const path = new Path2D(); path.moveTo(p1[0], p1[1]); path.lineTo(p2[0], p2[1]);
      glow(path, s.w > 0.8 ? '#ffffff' : COL.blue, 2, 0.55, 4); });
    // car
    const car = buildCar(BODIES.modern, 34, 'modern');
    shadowUnder(cam, [carX, 0, 0], car.L);
    drawCar(cam, car, { pos: [carX, 0, 0], a: 1, fill: 0.08, lights: 1, wheelRot: -t * 14 });
    // rear light trails
    const tl = P(cam, [carX - car.L / 2, 0.7, 0.9]), tr = P(cam, [carX - car.L / 2, -0.7, 0.9]);
    [tl, tr].forEach((q) => q && dotGlow(q[0], q[1], 7, COL.red, 0.9));
  });
}
function scene6UI(t) {
  const a = env(t, 50.9, 61, 0.4, 0.1);
  withAlpha(a, () => {
    brandBug(t, 1 - prog(t, 55.4, 56.0));
    // tagline over highway
    const f0 = 53.9;
    const fa = LOGO ? 1 - prog(t, 55.3, 55.85) : 1 - prog(t, 56.0, 56.5);
    withAlpha(fa, () => { const lines = wrap(TXT.future, 64, 900, 860);
      lines.forEach((l, i) => kinetic(l, CX, 400 + i * 78, t, f0 + i * 0.25, { size: 64, weight: 900, display: true, spacing: 2, glow: 18, stagger: 0.09 })); });
    // logo reveal
    const lr = prog(t, 55.9, 57.0);
    if (lr > 0) {
      ctx.save(); alpha(eo(lr) * 0.92); ctx.fillStyle = 'rgba(2,4,7,0.88)'; ctx.fillRect(0, 0, W, H); ctx.restore();
      particles(t, eo(lr), 2);
      const y = 760;
      // rings
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 2; i++) { alpha(eo(lr) * (0.35 - i * 0.12)); ctx.strokeStyle = COL.blue; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(CX, y, 330 + i * 46 + Math.sin(t * 1.4 + i) * 4, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * eio(lr)); ctx.stroke(); }
      ctx.restore();
      if (LOGO) {
        const lw0 = 640, s0 = lerp(1.12, 1, eo(lr));
        drawLogo(CX, y - 20, lw0 * s0, eo(lr), { glow: 50 * eo(lr), sweep: prog(t, 56.5, 57.7) });
      } else {
      // wordmark (placeholder typographic wordmark, used when no official logo file is supplied)
      const size = 136; const word = 'BANG TAF';
      const s = lerp(1.15, 1, eo(lr));
      ctx.save(); ctx.translate(CX, y); ctx.scale(s, s);
      ctx.font = `900 ${size}px ${FONTD}`; ctx.letterSpacing = '10px'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      const mw = ctx.measureText(word).width;
      const g = ctx.createLinearGradient(-mw / 2, -size / 2, mw / 2, size / 2);
      g.addColorStop(0, '#8f9aa6'); g.addColorStop(0.35, '#f4f7fa'); g.addColorStop(0.5, '#b8c2cc'); g.addColorStop(0.7, '#ffffff'); g.addColorStop(1, '#7d8792');
      alpha(eo(lr)); ctx.shadowColor = 'rgba(30,167,255,0.55)'; ctx.shadowBlur = 40; ctx.fillStyle = g; ctx.fillText(word, 0, 0); ctx.shadowBlur = 0;
      // light sweep across letters
      const sx = lerp(-mw, mw, prog(t, 56.4, 57.6));
      const sg = ctx.createLinearGradient(sx - 120, 0, sx + 120, 0); sg.addColorStop(0, 'rgba(143,220,255,0)'); sg.addColorStop(0.5, 'rgba(200,240,255,0.95)'); sg.addColorStop(1, 'rgba(143,220,255,0)');
      ctx.globalCompositeOperation = 'source-atop'; ctx.fillStyle = sg; ctx.fillRect(-mw / 2 - 20, -size / 2, mw + 40, size);
      ctx.restore();
      }
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; alpha(eo(lr)); ctx.fillStyle = COL.blue; const ly = LOGO ? y + 215 : y + 108; const lw = 520 * eio(prog(t, 56.3, 57.1)); ctx.fillRect(CX - lw / 2, ly, lw, 5); ctx.restore();
      text(TXT.tagline, CX, (LOGO ? y + 262 : y + 160), { size: 32, weight: 700, spacing: 12, color: COL.blueHi, a: eo(prog(t, 56.6, 57.2)) });
      // future line + CTA
      text(TXT.future, CX, (LOGO ? y + 340 : y + 290), { size: TXT.future.length > 30 ? 34 : 40, weight: 900, spacing: 2, display: true, a: eo(prog(t, 56.9, 57.4)) });
      const cp = eo(prog(t, 57.3, 57.9));
      const bw = 560, by = LOGO ? y + 440 : y + 410; const pulse = 1 + 0.03 * Math.sin(t * 6);
      ctx.save(); ctx.translate(CX, by); ctx.scale(pulse * lerp(0.8, 1, cp), pulse * lerp(0.8, 1, cp)); alpha(cp);
      const r = rrect(-bw / 2, -46, bw, 92, 46); ctx.fillStyle = COL.blue; ctx.shadowColor = 'rgba(30,167,255,0.8)'; ctx.shadowBlur = 30; ctx.fill(r); ctx.restore();
      text(TXT.cta1, CX, by + 1, { size: 40, weight: 900, spacing: 3, a: cp });
      text(TXT.cta2, CX, by + (LOGO ? 78 : 92), { size: 28, weight: 700, spacing: 3, color: COL.silver, a: eo(prog(t, 57.6, 58.2)) });
    }
  });
}

// =================================================================== frame
window.renderFrame = (t) => {
  GA = 1;
  const tint = t < 7 ? 0 : t < 17 ? 0.3 : t < 27 ? 0.6 : t < 39 ? 0.4 : t < 51 ? 0.5 : 0.7;
  background(t, tint);
  particles(t, 0.8);
  if (t < 7.3) scene1(t);
  if (t > 6.8 && t < 17.3) scene2(t);
  if (t > 16.8 && t < 27.3) scene3(t);
  if (t > 26.8 && t < 39.3) fadedLayer(470, 720, () => scene4(t));
  if (t > 38.8 && t < 51.3) scene5(t);
  if (t > 50.8) scene6(t);
  bloom(0.75);
  if (t < 7.3) scene1UI(t);
  if (t > 6.8 && t < 17.3) scene2UI(t);
  if (t > 16.8 && t < 27.3) scene3UI(t);
  if (t > 26.8 && t < 39.3) scene4UI(t);
  if (t > 38.8 && t < 51.3) scene5UI(t);
  if (t > 50.8) scene6UI(t);
  transitionFX(t);
  subtitles(t);
  finish(t);
  // opening fade-in from black
  if (t < 0.35) { ctx.save(); ctx.globalAlpha = 1 - t / 0.35; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
};
window.ready = async () => {
  await logoLoad;
  await Promise.all([
    document.fonts.load(`900 40px "Inter Display"`), document.fonts.load(`900 40px "Inter"`), document.fonts.load(`800 40px "Inter"`),
    document.fonts.load(`700 40px "Inter"`), document.fonts.load(`600 40px "Inter"`), document.fonts.load(`500 40px "Inter"`),
  ]);
  return document.fonts.check(`900 40px "Inter"`);
};
