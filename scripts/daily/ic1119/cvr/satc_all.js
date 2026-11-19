// 11/19 固定カートボタン（全商品用）を、公開中の全商品のページに仮で差し込んで表示を確かめる（カートには入れない・計測の通信は止める）
const { chromium, devices } = require('playwright'); const { open } = require('./satc_lib.js'); const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const c0 = await b.newContext(); const p0 = await c0.newPage();
  const list = await (await p0.request.get('https://looty-japan.com/products.json?limit=250')).json(); await c0.close();
  const hs = list.products.map(x => x.handle); const rows = []; let ok = 0;
  for (const h of hs) {
    let r; try {
      const t = await open(b, devices, encodeURIComponent(h)); const s = await t.st();
      const first = (t.prod.variants.find(v => v.available) || t.prod.variants[0]).price / 100;
      const want = s.tierPrice || ('¥' + first.toLocaleString('en-US'));
      const wantLabel = t.prod.variants.length > 1 ? '選んでカートに追加' : 'カートに追加する';
      const newErr = [...new Set(t.errs.slice(t.e0))].filter(e => !/Cannot set properties of null \(setting 'textContent'\)/.test(e));
      const good = s.price === want && s.label === wantLabel && s.barTop > 0 && s.barTop < s.vh && !s.off && s.origTop !== null && newErr.length === 0;
      if (good) ok++;
      r = { h: h.slice(0, 44), variants: t.prod.variants.length, pumper: s.pumper, price: s.price, want, tier: s.tier, label: s.label, barTop: s.barTop, origTop: s.origTop, newErr, good };
      await t.ctx.close();
    } catch (e) { r = { h: h.slice(0, 44), error: String(e.message).slice(0, 120), good: false }; }
    rows.push(r); console.log(JSON.stringify(r));
  }
  console.log(`■ 合計 ${hs.length} 商品・表示が合った ${ok}・合わなかった ${hs.length - ok}`);
  await b.close();
})();
