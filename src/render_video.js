// Render the animation to video (or preview stills) with headless Chromium.
//   node render_video.js <lang> <build_dir> video  [workers=3]
//   node render_video.js <lang> <build_dir> stills t1,t2,...
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const [lang, build, mode, arg] = process.argv.slice(2);
const FPS = 30, DUR = 60, N = FPS * DUR;
const script = JSON.parse(fs.readFileSync(path.join(__dirname, 'script.json'), 'utf8'));
const cues = JSON.parse(fs.readFileSync(path.join(build, `cues_${lang}.json`), 'utf8'));
const pageUrl = 'file://' + path.join(__dirname, 'render', 'index.html');

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
  await page.goto(pageUrl);
  const ok = await page.evaluate(async (d) => { window.setup(d); return window.ready(); }, { text: script[lang].text, cues });
  if (!ok) console.error('WARNING: Inter font not confirmed');
  return page;
}
async function frame(page, t, type = 'png') {
  const b64 = await page.evaluate(([t, type]) => { window.renderFrame(t); return document.getElementById('c').toDataURL(type === 'png' ? 'image/png' : 'image/jpeg', 0.95).split(',')[1]; }, [t, type]);
  return Buffer.from(b64, 'base64');
}

(async () => {
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  if (mode === 'stills') {
    const page = await openPage(browser);
    fs.mkdirSync(path.join(build, 'stills'), { recursive: true });
    for (const ts of arg.split(',')) {
      const t = parseFloat(ts); const buf = await frame(page, t);
      fs.writeFileSync(path.join(build, 'stills', `${lang}_${t.toFixed(2)}.png`), buf);
    }
    await browser.close(); return;
  }
  const workers = parseInt(arg || '3', 10);
  const per = Math.ceil(N / workers);
  const t0 = Date.now();
  let done = 0;
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const a = w * per, b = Math.min(N, a + per);
    const page = await openPage(browser);
    const out = path.join(build, `seg_${lang}_${w}.mp4`);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', '-threads', '1', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = a; i < b; i++) {
      const buf = await frame(page, i / FPS);
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      done++;
      if (done % 150 === 0) console.log(`[${lang}] ${done}/${N} frames, ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise((r) => ff.on('close', r));
    await page.close();
  }));
  fs.writeFileSync(path.join(build, `segs_${lang}.txt`), Array.from({ length: workers }, (_, w) => `file 'seg_${lang}_${w}.mp4'`).join('\n') + '\n');
  await browser.close();
  console.log(`[${lang}] video frames done in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
})();
