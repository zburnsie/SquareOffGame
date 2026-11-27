// End-to-end: a "TV" page and a "phone" page talk over PeerJS; the phone drives a duel.
const { chromium } = require('playwright-core');
const OUT = process.argv[2];
const URL = 'http://localhost:8765/index.html';
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const tvCtx = await browser.newContext({ viewport: { width: 1400, height: 860 } });
  const phCtx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const tv = await tvCtx.newPage(), ph = await phCtx.newPage();
  if (process.env.RELAY_ONLY) await phCtx.route(/peerjs/, r => r.abort());   // phone can't use the direct route at all
  const errs = [];
  tv.on('pageerror', e => errs.push('TV: ' + e.message));
  ph.on('pageerror', e => errs.push('PHONE: ' + e.message));

  await tv.goto(URL); await tv.waitForSelector('#pn-0');
  const names = ['Ann', 'Ben', 'Cat', 'Dan', 'Eve', 'Fox'];
  await tv.fill('#pn-0', names[0]); await tv.press('#pn-0', 'Enter');
  for (let i = 1; i < names.length; i++) { await tv.fill(`#pn-${i}`, names[i]); if (i < names.length - 1) await tv.press(`#pn-${i}`, 'Enter'); }
  await sleep(1500); // let photo index load so Deal uses photo categories
  await tv.click('#mixCats');
  const cats = await tv.$$eval('.pcat', els => els.map(e => e.textContent.trim()));
  console.log('dealt:', cats.join(' | '));
  await tv.screenshot({ path: OUT + '/e2e_setup.png' });
  await tv.click('#start'); await tv.waitForSelector('#board .cell');
  await tv.click('#remoteBtn'); await tv.waitForSelector('.code');
  const code = (await tv.textContent('.code')).trim();
  console.log('room code:', code);
  await sleep(2500); // host registers with broker

  await ph.goto(URL + '?remote=' + code);
  await ph.waitForFunction(() => /Connected/.test(document.querySelector('#rStat')?.textContent || ''), null, { timeout: 45000 });
  console.log('phone connected; TV says:', (await tv.textContent('#remoteState')).trim());
  await tv.click('#closeRemote');
  await ph.waitForSelector('[data-cmd="random"]');
  await ph.screenshot({ path: OUT + '/e2e_phone_board.png' });

  await ph.click('[data-cmd="random"]');
  await ph.waitForSelector('[data-cmd="target"]', { timeout: 15000 });
  const challenger = await ph.textContent('.r-msg em');
  await ph.click('[data-cmd="target"] >> nth=0');
  await ph.waitForSelector('[data-cmd="first"]', { timeout: 10000 });
  console.log('duel started on phone; TV overlay:', (await tv.textContent('#ov h2')).trim(), '| challenger', challenger);
  await ph.click('[data-cmd="first"] >> nth=0');
  await ph.waitForSelector('[data-cmd="correct"]', { timeout: 10000 });
  await sleep(1500);
  const ans1 = (await ph.textContent('.r-ans')).trim();
  const activeBefore = await tv.$eval('.pl.on .pl-name', e => e.textContent);
  await ph.screenshot({ path: OUT + "/e2e_phone_duel.png" });
  await tv.screenshot({ path: OUT + '/e2e_tv_duel.png' });
  console.log('phone answer shown:', ans1, '| TV active:', activeBefore);

  await ph.click('[data-cmd="correct"]'); await sleep(700);
  const activeAfter = await tv.$eval('.pl.on .pl-name', e => e.textContent);
  const ans2 = (await ph.textContent('.r-ans')).trim();
  console.log('after Correct -> TV active:', activeAfter, '| new answer:', ans2);

  const clk = async () => parseFloat(await tv.$eval('.pl.on .clock', e => e.textContent));
  const t0 = await clk();
  await ph.click('[data-cmd="pass"]'); await sleep(400);
  const t1 = await clk();
  const ans3 = (await ph.textContent('.r-ans')).trim();
  console.log(`after Pass -> clock ${t0} -> ${t1} (dropped ${(t0 - t1).toFixed(1)}s) | new answer: ${ans3} | TV last line: ${(await tv.textContent('#last')).trim()}`);

  // fast back-to-back taps 400 ms apart (faster than the TV update would previously allow) must all count
  const s0 = await tv.evaluate(() => D.seq);
  for (let i = 0; i < 3; i++){ await ph.dispatchEvent('[data-cmd="correct"]', 'pointerdown'); await sleep(400); }
  await sleep(500);
  console.log('3 quick Correct taps (400ms apart) advanced clues by', (await tv.evaluate(() => D.seq)) - s0, '(want 3)');
  // tap, then tap again before any update arrives: block the network round trip by tapping within 150 ms
  const s1 = await tv.evaluate(() => D.seq);
  await ph.dispatchEvent('[data-cmd="pass"]', 'pointerdown'); await sleep(120); await ph.dispatchEvent('[data-cmd="pass"]', 'pointerdown'); await sleep(600);
  console.log('accidental double tap of Pass (120ms) advanced clues by', (await tv.evaluate(() => D.seq)) - s1, '(want 1)');
  // double tap Correct quickly: should advance only once
  const seqA = await tv.evaluate(() => D.seq);
  await ph.dispatchEvent('[data-cmd="correct"]','pointerdown'); await ph.dispatchEvent('[data-cmd="correct"]','pointerdown'); await sleep(700);
  const seqB = await tv.evaluate(() => D.seq);
  console.log('double tap Correct advanced clues by', seqB - seqA);

  await ph.click('[data-cmd="pause"]'); await ph.waitForSelector('[data-cmd="win"]');
  await ph.click('[data-cmd="win"] >> nth=0'); await ph.waitForSelector('[data-cmd="back"]');
  await ph.click('[data-cmd="back"]'); await ph.waitForSelector('[data-cmd="random"]', { timeout: 10000 });
  console.log('back on board; players left on phone:', await ph.$$eval('[data-cmd="chal"]', e => e.length));
  await tv.screenshot({ path: OUT + '/e2e_tv_board.png' });
  console.log('page errors:', errs.length ? errs : 'none');
  await browser.close();
})().catch(async e => { console.error('TEST FAILED:', e.message); process.exit(1); });
