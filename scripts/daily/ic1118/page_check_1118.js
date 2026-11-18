const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'] });
  const p = await ctx.newPage();
  const urls = ['https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush',
                'https://looty-japan.com/products/high-end-nose-massager-white'];
  for (const u of urls) {
    const t0 = Date.now();
    const resp = await p.goto(u, { waitUntil: 'load', timeout: 60000 });
    const tl = Date.now() - t0;
    await p.waitForTimeout(3000);
    const r = await p.evaluate(() => {
      const vh = window.innerHeight;
      const btns = [...document.querySelectorAll('button[name="add"], form[action*="/cart/add"] button[type="submit"], .product-form__submit')];
      const vis = btns.map(x => { const rc = x.getBoundingClientRect(); const cs = getComputedStyle(x); return {text: x.innerText.trim().slice(0,20), top: Math.round(rc.top + scrollY), h: rc.height, fixed: cs.position}; });
      const fixedEls = [...document.querySelectorAll('body *')].filter(e => { const cs = getComputedStyle(e); return (cs.position === 'fixed' || cs.position === 'sticky') && e.getBoundingClientRect().height > 30 && e.innerText && /カート|購入|買/.test(e.innerText); }).map(e => ({tag: e.tagName, cls: (e.className||'').toString().slice(0,60), text: e.innerText.trim().slice(0,30), pos: getComputedStyle(e).position}));
      const nav = performance.getEntriesByType('navigation')[0];
      const res = performance.getEntriesByType('resource');
      return {vh, pageH: document.body.scrollHeight, buttons: vis, fixedEls: fixedEls.slice(0,5), dcl: Math.round(nav.domContentLoadedEventEnd), load: Math.round(nav.loadEventEnd), nRes: res.length, kb: Math.round(res.reduce((a, x) => a + (x.transferSize||0), 0)/1024)};
    });
    console.log(u.split('/').pop(), 'status', resp.status(), 'load(ms)', tl, JSON.stringify(r));
    await p.screenshot({ path: u.split('/').pop().slice(0,20) + '_top.png' });
  }
  await b.close();
})();
