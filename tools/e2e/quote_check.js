const { chromium } = require('playwright-core');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1920, height: 1080 } })).newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('http://localhost:8765/index.html'); await pg.waitForSelector('#pn-0');
  await pg.waitForFunction(() => PHOTO_CATS.length > 0);
  console.log('photo categories:', await pg.evaluate(() => PHOTO_CATS.map(c => c.name + ' ' + c.items.length).join(', ')));
  // a duel in Famous Movie Quotes with the longest quote on screen
  await pg.evaluate(() => { const c = cat('quotes'); const long = c.items.reduce((a, b) => (b[0].length > a[0].length ? b : a)); window.__long = long[0]; });
  await pg.fill('#pn-0', 'Ann'); await pg.press('#pn-0', 'Enter'); await pg.fill('#pn-1', 'Ben');
  if (await pg.isChecked('#photoOnly')) await pg.click('#photoOnly');
  await pg.click('#pc-0'); await pg.fill('.cp-find', 'quotes'); await pg.press('.cp-find', 'Enter');
  await pg.click('#pc-1'); await pg.fill('.cp-find', 'movie posters'); await pg.press('.cp-find', 'Enter');
  await pg.click('#start'); await pg.waitForSelector('#board .cell');
  const r = await pg.evaluate(() => { try { return JSON.stringify(S.players.map(p => p.cat)); } catch (e) { return e.message; } });
  console.log('players cats', r, 'errors:', errs.length ? errs : 'none');
  await b.close();
})().catch(e => { console.error('TEST FAILED:', e.message); process.exit(1); });
