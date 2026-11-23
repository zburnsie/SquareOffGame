const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  await pg.goto('http://localhost:8765/index.html'); await pg.waitForSelector('#pn-0');
  await pg.evaluate(z => localStorage.setItem('sq_tvzoom', z), process.env.Z || '1.9');
  await pg.waitForFunction(() => PHOTO_CATS.length > 0);
  await pg.fill('#pn-0', 'Ann'); await pg.press('#pn-0', 'Enter'); await pg.fill('#pn-1', 'Ben');
  await pg.click('#mixCats');
  await pg.click('#start'); await pg.waitForSelector('#board .cell');
  await pg.click('#board .cell >> nth=0'); await pg.click('#board .cell.target >> nth=0'); await pg.click('#firstA');
  await pg.waitForFunction(() => D && D.phase === 'run'); await pg.waitForTimeout(1200);
  if (process.env.REMOTE) await pg.evaluate(() => document.body.classList.add('has-remote'));
  await pg.waitForTimeout(200); await pg.screenshot({ path: process.argv[2] + '/tv_probe_' + (process.env.Z||'1.9') + (process.env.REMOTE?'_r':'') + '.png' });
  console.log(await pg.evaluate(() => {
    const m = sel => { const e = document.querySelector(sel); if (!e) return null; const r = e.getBoundingClientRect(); return [sel, Math.round(r.width), Math.round(r.height), 'client', e.clientWidth, e.clientHeight]; };
    const img = document.querySelector('#clue img');
    return JSON.stringify([m('.stage'), m('#prompt'), m('#clue'), m('#reveal'), m('#clue img'), img && [img.naturalWidth, img.naturalHeight], getComputedStyle(document.querySelector('#clue')).flex]);
  }));
  await b.close();
})().catch(e => { console.error('FAILED', e.message); process.exit(1); });
