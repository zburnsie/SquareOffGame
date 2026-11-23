const { chromium } = require('playwright-core');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1920, height: 1080 } })).newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('http://localhost:8765/index.html'); await pg.waitForSelector('#pn-0');
  await pg.evaluate(() => { localStorage.setItem('sq_tvzoom', '1.9'); }); await pg.reload(); await pg.waitForSelector('#pn-0');
  await pg.waitForFunction(() => PHOTO_CATS.length > 0);
  if (await pg.isChecked('#photoOnly')) await pg.click('#photoOnly');
  await pg.click('#pc-0'); await pg.waitForSelector('.catpick');
  const r = await pg.$eval('.cp-card', e => { const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]; });
  const groups = await pg.$$eval('.cp-group h3', e => e.map(x => x.textContent));
  console.log('card box', r, '| groups', groups.join(' / '));
  await pg.screenshot({ path: OUT + '/shot_picker_tv.png' });
  await pg.mouse.wheel(0, 3000); await pg.waitForTimeout(300);
  await pg.screenshot({ path: OUT + '/shot_picker_tv2.png' });
  console.log('errors:', errs.length ? errs : 'none'); await b.close();
})().catch(e => { console.error('TEST FAILED:', e.message); process.exit(1); });
