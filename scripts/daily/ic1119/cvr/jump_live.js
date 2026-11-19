// 11/19 公開中の全商品のページを「何も差し込まずに」開き、お店に入っている「商品を選ぶ」ボタン（#looty-jump）の有無と動きを確かめる
// 計測の通信は止める・カートには入れない
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
(async () => {
  const b = await chromium.launch();
  const c0 = await b.newContext(); const p0 = await c0.newPage();
  const list = await (await p0.request.get('https://looty-japan.com/products.json?limit=250')).json(); await c0.close();
  const hs = list.products.map(x => ({ h: x.handle, t: x.title.replace(/【[^】]*】/g, '').replace(/LOOTY\s*/, '').trim().slice(0, 18), price: '¥' + Number(x.variants[0].price).toLocaleString('en-US') }));
  let i = 0; const rows = [];
  const work = async () => { while (i < hs.length) { const x = hs[i++]; let r = { t: x.t };
    try { const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage(); await p.route(u => BLOCK.test(u.href), q => q.abort());
      const errs = []; p.on('pageerror', e => errs.push((e.message || '').slice(0, 60)));
      await p.goto('https://looty-japan.com/products/' + encodeURIComponent(x.h), { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
      const st = () => p.evaluate(() => { const bars = document.querySelectorAll('#looty-jump'); if (!bars.length) return { n: 0, old: document.querySelectorAll('#looty-sticky-atc').length }; const bar = bars[0]; const r = bar.getBoundingClientRect(); const o = document.querySelector('product-form form[action*="/cart/add"] button[name="add"], button.product-form__submit'); const or = o.getBoundingClientRect(); const sel = document.querySelector('.pumper_block .pmpr-tier-shell__card[data-selected="true"] .pmpr-tier-price__total'); let data = null; try { data = Object.keys(JSON.parse(document.getElementById('looty-jump-data').textContent)).length; } catch (e) { data = 'JSONエラー'; } const sec = bar.closest('.shopify-section'); const pad = sec ? Math.round(sec.getBoundingClientRect().height) : null; return { n: bars.length, hidden: bar.hidden, ready: bar.dataset.ready, price: bar.querySelector('.looty-jump__price').textContent.trim(), tier: bar.querySelector('.looty-jump__tier').textContent, label: bar.querySelector('button').textContent.trim(), note: bar.querySelector('.looty-jump__note').textContent.trim(), off: bar.classList.contains('is-off'), barTop: Math.round(r.top), barH: Math.round(r.height), vh: innerHeight, origTop: Math.round(or.top), origBottom: Math.round(or.bottom), tierPrice: sel ? sel.textContent.trim() : null, data, secId: sec ? sec.id.slice(0, 60) : null, secH: pad }; });
      const a = await st(); r.before = a;
      if (a.n) { await p.locator('#looty-jump button').first().tap(); await p.waitForTimeout(2200); const c = await st(); const n = await p.evaluate(async () => (await (await fetch('/cart.js')).json()).item_count);
        r.after = { origTop: c.origTop, origBottom: c.origBottom, off: c.off, cart: n }; r.errs = [...new Set(errs)];
        r.good = a.n === 1 && !a.hidden && a.barTop > 0 && a.barTop < a.vh && !a.off && (a.price === (a.tierPrice || x.price)) && typeof a.data === 'number' && c.origTop >= 0 && c.origBottom <= c.vh && c.off && n === 0; }
      await ctx.close(); } catch (e) { r.error = String(e.message).slice(0, 100); }
    rows.push(r); console.log(JSON.stringify(r)); } };
  await Promise.all([work(), work(), work()]);
  const has = rows.filter(r => r.before && r.before.n > 0), no = rows.filter(r => r.before && r.before.n === 0), er = rows.filter(r => r.error);
  console.log(`■ 合計 ${rows.length} 商品 ｜ お店にボタンが入っている ${has.length}（うち動きが合った ${has.filter(r => r.good).length}）｜入っていない ${no.length} ｜読み込み失敗 ${er.length}`);
  console.log('  入っている商品:', has.map(r => r.t).join(' / '));
  console.log('  前の版（#looty-sticky-atc）が入っている商品:', rows.filter(r => r.before && r.before.old).map(r => r.t).join(' / ') || 'なし');
  await b.close();
})();
