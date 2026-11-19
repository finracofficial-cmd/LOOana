// 11/19 「商品を選ぶ」ボタンを、公開中の全商品のページに仮で差し込んで確かめる（カートには入れない・計測の通信は止める）
// 合格: 帯が出る・値段が合う・押すと元の「カートに追加する」が画面内に全部入る・帯が隠れる・カートは0のまま・新しい種類のエラーなし
const { chromium, devices } = require('playwright'); const { open, label } = require('./jump_lib.js');
(async () => {
  const b = await chromium.launch();
  const c0 = await b.newContext(); const p0 = await c0.newPage();
  const list = await (await p0.request.get('https://looty-japan.com/products.json?limit=250')).json(); await c0.close();
  const hs = list.products.map(x => x.handle); let ok = 0, i = 0;
  const work = async () => { while (i < hs.length) { const h = hs[i++]; let r; try {
      const t = await open(b, devices['iPhone 13'], encodeURIComponent(h)); const a = await t.st();
      const want = a.tierPrice || ('¥' + (t.first.price / 100).toLocaleString('en-US'));
      await t.tapBar(); await t.p.waitForTimeout(2200); const c = await t.st(); const n = await t.cartN();
      const newErr = [...new Set(t.errs.slice(t.e0))].filter(e => !/Cannot set properties of null \(setting 'textContent'\)/.test(e));
      const good = a.price === want && a.label === label && a.barTop > 0 && a.barTop < a.vh && !a.off && c.origTop >= 0 && c.origBottom <= c.vh && c.off && n === 0 && newErr.length === 0;
      if (good) ok++;
      r = { h: h.slice(0, 44), variants: t.prod.variants.length, price: a.price, want, before: a.origTop, after: [c.origTop, c.origBottom, c.vh], boxTop: c.boxTop, off: c.off, cart: n, newErr, good };
      await t.ctx.close();
    } catch (e) { r = { h: h.slice(0, 44), error: String(e.message).slice(0, 120), good: false }; }
    console.log(JSON.stringify(r)); } };
  await Promise.all([work(), work(), work()]);
  console.log(`■ 合計 ${hs.length} 商品・合格 ${ok}・不合格 ${hs.length - ok}`);
  await b.close();
})();
