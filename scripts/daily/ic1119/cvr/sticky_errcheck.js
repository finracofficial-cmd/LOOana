// 11/19 固定カートボタンを差し込んだとき／差し込まないときで、ページのエラーを並べる（同じ操作: 色を選ぶ→元のボタンでカートに入れる→元のボタンまでスクロール）
const { chromium, devices } = require('playwright'); const fs = require('fs');
let src = fs.readFileSync('/home/user/LOOana/data/theme-ops/sticky-atc-2026-11-19/sticky-atc.liquid', 'utf8');
src = src.replace(/\{%-? comment -?%\}[\s\S]*?\{%-? endcomment -?%\}/, '').replace(/\{\{[^}]*\}\}/, '¥3,980');
const html = src.slice(0, src.indexOf('<style>')), css = src.match(/<style>([\s\S]*?)<\/style>/)[1], js = src.match(/<script>([\s\S]*?)<\/script>/)[1];
(async () => {
  const b = await chromium.launch();
  for (const inject of [false, true]) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
    const errs = []; p.on('pageerror', e => errs.push((e.message || '').slice(0, 70) + ' @ ' + ((e.stack || '').split('\n')[1] || '').trim().slice(0, 110)));
    await p.goto('https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3000);
    const e0 = errs.length;
    if (inject) { await p.evaluate(h => { const d = document.createElement('div'); d.innerHTML = h; document.body.appendChild(d.firstElementChild); }, html); await p.addStyleTag({ content: css }); await p.evaluate(js); await p.waitForTimeout(800); }
    if (inject) { await p.locator('#looty-sticky-atc button').tap(); await p.waitForTimeout(1500); await p.locator('#looty-sticky-atc button').tap(); await p.waitForTimeout(4000); }
    else { const btn = p.locator('button[name="add"], .product-form__submit').first(); await btn.scrollIntoViewIfNeeded(); await btn.tap(); await p.waitForTimeout(4000); }
    const cart = await p.evaluate(async () => (await (await fetch('/cart.js')).json()).items.map(i => ({ v: i.variant_title, q: i.quantity })));
    await p.evaluate(() => document.querySelector('button[name="add"], .product-form__submit').scrollIntoView({ block: 'center' })); await p.waitForTimeout(900);
    const after = errs.slice(e0); const kinds = {}; after.forEach(m => kinds[m] = (kinds[m] || 0) + 1);
    console.log(inject ? '■ 差し込みあり' : '■ 差し込みなし（今のページのまま）', '｜開いた時点のエラー', e0, '｜操作中のエラー', after.length, '｜カート', JSON.stringify(cart));
    Object.entries(kinds).forEach(([m, n]) => console.log('   ', n, '回:', m));
    await ctx.close();
  }
  await b.close();
})();
