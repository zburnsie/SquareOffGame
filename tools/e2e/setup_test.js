const { chromium } = require('playwright-core');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1400, height: 900 } })).newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('http://localhost:8765/index.html'); await pg.waitForSelector('#pn-0');
  await pg.waitForFunction(() => PHOTO_CATS.length > 0);
  const names = ['Ann', 'Ben', 'Cat', 'Dan', 'Eve'];
  for (let i = 0; i < names.length; i++) { await pg.fill(`#pn-${i}`, names[i]); if (i < names.length - 1) await pg.press(`#pn-${i}`, 'Enter'); }
  await pg.click('#shuffleP');
  const order = await pg.$$eval('.pname', e => e.map(x => x.value));
  console.log('order after randomize:', order.join(', '), '| next:', await pg.textContent('.next-pick b'));
  const firstOpt = await pg.$eval('#pc-0', s => [...s.options].find(o => o.value && !o.disabled).value);
  await pg.selectOption('#pc-0', firstOpt);
  const takenInRow2 = await pg.$eval('#pc-1', (s, v) => { const o = [...s.options].find(o => o.value === v); return o && o.disabled; }, firstOpt);
  console.log('#1 picked', firstOpt, '| shown as taken for #2:', takenInRow2, '| next:', await pg.textContent('.next-pick b'));
  const optCount = await pg.$eval('#pc-1', s => s.options.length - 1);
  console.log('menu choices with photo-only on:', optCount);
  await pg.click('#start'); console.log('start without all picks ->', (await pg.textContent('.err')).trim());
  await pg.click('#mixCats');
  const cats = await pg.$$eval('.pcat', e => e.map(s => s.value));
  console.log('after deal:', cats.join(', '), '| #1 kept pick:', cats[0] === firstOpt, '| all unique:', new Set(cats).size === cats.length, '| all photo:', cats.every(c => c.startsWith('ph-')));
  await pg.screenshot({ path: OUT + '/shot_pick.png' });
  await pg.click('#start'); await pg.waitForSelector('#board .cell', { timeout: 5000 });
  console.log('game started; errors:', errs.length ? errs : 'none');
  await b.close();
})().catch(e => { console.error('TEST FAILED:', e.message); process.exit(1); });
