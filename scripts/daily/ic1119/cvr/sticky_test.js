// 11/19 固定カートボタンのコード（data/theme-ops/sticky-atc-2026-11-19/sticky-atc.liquid）を、実際の商品ページに仮で差し込んで動きを確かめる（お店には書き込まない・購入しない）
const { chromium, devices } = require('playwright'); const fs = require('fs');
const OUT = process.argv[2];
let src = fs.readFileSync('/home/user/LOOana/data/theme-ops/sticky-atc-2026-11-19/sticky-atc.liquid', 'utf8');
src = src.replace(/\{%-? comment -?%\}[\s\S]*?\{%-? endcomment -?%\}/, '').replace(/\{\{[^}]*\}\}/, '¥3,980');
const html = src.slice(0, src.indexOf('<style>')), css = src.match(/<style>([\s\S]*?)<\/style>/)[1], js = src.match(/<script>([\s\S]*?)<\/script>/)[1];
(async () => {
  const b = await chromium.launch();
  for (const [name, slug] of [['ガラス', 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush'], ['ワイパー（選択肢なし）', 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use']]) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
    const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 80)));
    await p.goto('https://looty-japan.com/products/' + slug, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3000);
    const e0 = errs.length;
    await p.evaluate(h => { const d = document.createElement('div'); d.innerHTML = h; document.body.appendChild(d.firstElementChild); }, html);
    await p.addStyleTag({ content: css }); await p.evaluate(js); await p.waitForTimeout(800);
    const st = async () => p.evaluate(() => { const bar = document.getElementById('looty-sticky-atc'); const r = bar.getBoundingClientRect(); const o = document.querySelector('button[name="add"], .product-form__submit').getBoundingClientRect(); return { label: bar.querySelector('button').innerText, off: bar.classList.contains('is-off'), barTop: Math.round(r.top), barH: Math.round(r.height), vh: innerHeight, scrollY: Math.round(scrollY), origTop: Math.round(o.top) }; });
    console.log(name, '① 開いた直後:', JSON.stringify(await st()));
    await p.screenshot({ path: OUT + '/s1_' + slug.slice(0, 8) + '.png' });
    await p.locator('#looty-sticky-atc button').tap(); await p.waitForTimeout(1500);
    console.log(name, '② 1回目のタップの後:', JSON.stringify(await st()));
    let cart = await p.evaluate(async () => (await (await fetch('/cart.js')).json()).items.map(i => ({ v: i.variant_title, q: i.quantity })));
    console.log(name, '   カート:', JSON.stringify(cart));
    await p.screenshot({ path: OUT + '/s2_' + slug.slice(0, 8) + '.png' });
    if (!cart.length) { await p.locator('#looty-sticky-atc button').tap(); await p.waitForTimeout(4000);
      cart = await p.evaluate(async () => (await (await fetch('/cart.js')).json()).items.map(i => ({ v: i.variant_title, q: i.quantity })));
      console.log(name, '③ 2回目のタップの後のカート:', JSON.stringify(cart)); await p.screenshot({ path: OUT + '/s3_' + slug.slice(0, 8) + '.png' }); }
    // 元のボタンまでスクロールすると隠れるか
    await p.evaluate(() => { const k = [...document.querySelectorAll('body *')].find(e => getComputedStyle(e).position === 'fixed' && e.getBoundingClientRect().height > 300 && /カート/.test(e.innerText || '')); if (k) { const x = k.querySelector('[class*="close"], button[aria-label*="閉"], .close'); if (x) x.click(); } });
    await p.waitForTimeout(800);
    await p.evaluate(() => document.querySelector('button[name="add"], .product-form__submit').scrollIntoView({ block: 'center' })); await p.waitForTimeout(900);
    console.log(name, '④ 元のボタンが見える位置:', JSON.stringify(await st()), '｜差し込み後に増えたエラー', errs.length - e0);
    await ctx.close();
  }
  await b.close();
})();
