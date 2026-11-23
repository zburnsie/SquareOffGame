const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('http://localhost:8765/index.html'); await pg.waitForSelector('#pn-0'); await pg.waitForFunction(() => PHOTO_CATS.length > 0);
  await pg.fill('#pn-0', 'Ann'); await pg.press('#pn-0', 'Enter'); await pg.fill('#pn-1', 'Ben'); await pg.click('#mixCats'); await pg.click('#start');
  await pg.waitForSelector('#board .cell'); await pg.click('#board .cell >> nth=0'); await pg.click('#board .cell.target >> nth=0'); await pg.click('#firstA');
  await pg.waitForFunction(() => D && D.phase === 'run');
  console.log('in full screen during duel:', await pg.evaluate(() => !!document.fullscreenElement));
  await pg.evaluate(() => document.exitFullscreen()); await pg.waitForTimeout(500);
  console.log('after leaving full screen -> phase:', await pg.evaluate(() => D.phase));
  console.log('errors:', errs.length ? errs : 'none'); await b.close();
})().catch(e => { console.error('TEST FAILED:', e.message); process.exit(1); });
