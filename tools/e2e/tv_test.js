const { chromium } = require('playwright-core');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('http://localhost:8765/index.html'); await pg.waitForSelector('#pn-0');
  await pg.waitForFunction(() => PHOTO_CATS.length > 0);
  const names = ['Ann', 'Ben', 'Cat', 'Dan', 'Eve', 'Fox', 'Gus', 'Hal', 'Ivy', 'Jo', 'Kim', 'Lou'];
  for (let i = 0; i < names.length; i++) { await pg.fill(`#pn-${i}`, names[i]); if (i < names.length - 1) await pg.press(`#pn-${i}`, 'Enter'); }
  await pg.click('#mixCats'); await pg.click('#start'); await pg.waitForSelector('#board .cell'); await pg.waitForTimeout(600);
  const fits = () => pg.evaluate(() => { const r = document.querySelector('#board').getBoundingClientRect(); const a = document.querySelector('.screen').getBoundingClientRect(); return {boardBottom: Math.round(r.bottom), boardRight: Math.round(r.right), screenH: innerHeight, screenW: innerWidth, docScroll: document.documentElement.scrollHeight > innerHeight + 2}; });
  console.log('tv class on:', await pg.evaluate(() => document.documentElement.classList.contains('tv')), 'zoom', await pg.evaluate(() => tvZoom()));
  console.log('board fit @1.3:', JSON.stringify(await fits()));
  await pg.screenshot({ path: OUT + '/tv_board_13.png' });
  await pg.click('#board .cell >> nth=0'); await pg.click('#board .cell.target >> nth=0'); await pg.click('#firstA');
  await pg.waitForFunction(() => D && D.phase === 'run'); await pg.waitForTimeout(800);
  console.log('duel overflow @1.3:', await pg.evaluate(() => { const c = document.querySelector('.controls').getBoundingClientRect(); return {controlsBottom: Math.round(c.bottom), screenH: innerHeight}; }));
  await pg.screenshot({ path: OUT + '/tv_duel_13.png' });
  for (let k = 0; k < 6; k++) await pg.keyboard.press('='); await pg.waitForTimeout(400);
  console.log('zoom after +x6:', await pg.evaluate(() => tvZoom()), await pg.evaluate(() => { const c = document.querySelector('.controls').getBoundingClientRect(); return {controlsBottom: Math.round(c.bottom), screenH: innerHeight}; }));
  await pg.screenshot({ path: OUT + '/tv_duel_19.png' });
  console.log('errors:', errs.length ? errs : 'none');
  await b.close();
})().catch(e => { console.error('TEST FAILED:', e.message); process.exit(1); });
