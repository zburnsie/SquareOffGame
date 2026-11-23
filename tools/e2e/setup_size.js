const { chromium } = require('playwright-core');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1920, height: 1080 } })).newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('http://localhost:8765/index.html'); await pg.waitForSelector('#tvSize');
  await pg.selectOption('#tvSize', '1.9'); await pg.waitForTimeout(500);
  await pg.screenshot({ path: OUT + '/setup_huge.png' });
  console.log('zoom applied on setup:', await pg.evaluate(() => getComputedStyle(document.querySelector('#app')).zoom), '| page scrolls inside app:', await pg.evaluate(() => document.querySelector('.setup').scrollHeight > document.querySelector('.setup').clientHeight));
  await pg.selectOption('#tvSize', '1'); await pg.waitForTimeout(300);
  console.log('Normal ->', await pg.evaluate(() => getComputedStyle(document.querySelector('#app')).zoom));
  console.log('errors:', errs.length ? errs : 'none'); await b.close();
})().catch(e => { console.error('TEST FAILED:', e.message); process.exit(1); });
