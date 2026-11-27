const { chromium } = require('playwright-core');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1920, height: 1080 } })).newPage();
  await pg.goto('http://localhost:8765/index.html'); await pg.waitForSelector('#pn-0');
  await pg.waitForFunction(() => PHOTO_CATS.length > 0);
  await pg.fill('#pn-0', 'Ann'); await pg.press('#pn-0', 'Enter'); await pg.fill('#pn-1', 'Ben');
  if (await pg.isChecked('#photoOnly')) await pg.click('#photoOnly');
  await pg.click('#pc-0'); await pg.fill('.cp-find', 'slogans'); await pg.press('.cp-find', 'Enter');
  await pg.click('#pc-1'); await pg.fill('.cp-find', 'christmas'); await pg.press('.cp-find', 'Enter');
  await pg.click('#start'); await pg.waitForSelector('#board .cell');
  // game from previous test is saved: duel the movie-quotes player
  await pg.evaluate(() => { const q = S.players.find(p => p.cat === 'slogans'), o = S.players.find(p => p !== q); startDuel(o.id, q.id); });
  await pg.waitForSelector('#ov button'); await pg.click('#ov button >> nth=0'); await pg.waitForTimeout(4500);
  const long = await pg.evaluate(() => cat('slogans').items.reduce((a, b) => (b[0].length > a[0].length ? b : a))[0]);
  await pg.evaluate(t => { document.querySelector('#clue').textContent = t; }, long);
  await pg.screenshot({ path: OUT + '/quote_duel.png' });
  await b.close();
})().catch(e => { console.error('TEST FAILED:', e.message); process.exit(1); });
