// 11/19 インソールの商品ページ（サイズ・色あり）で、選んだサイズがカートと決済画面に正しく入るかを確かめる（iPhone 13 の画面・購入はしない）
const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 120)));
  await p.goto('https://looty-japan.com/products/soft-super-sports-shock-absorption-sweat-absorbent-sockliner-with-massage-function', { waitUntil: 'load', timeout: 60000 });
  await p.waitForTimeout(3000);
  const info = await p.evaluate(() => {
    const vh = window.innerHeight;
    const pos = e => Math.round(e.getBoundingClientRect().top + scrollY);
    const radios = [...document.querySelectorAll('variant-radios input[type=radio], variant-selects select, fieldset input[type=radio], .product-form__input input[type=radio]')];
    const groups = {};
    radios.forEach(r => { (groups[r.name] = groups[r.name] || []).push({ v: r.value, checked: r.checked, top: pos(r.closest('fieldset') || r) }); });
    const sel = [...document.querySelectorAll('select')].filter(s => s.offsetParent).map(s => ({ name: s.name || s.id, value: s.value, n: s.options.length, top: pos(s) }));
    const add = document.querySelector('button[name="add"], .product-form__submit');
    const idInput = document.querySelector('form[action*="/cart/add"] input[name="id"]');
    return { vh, groups, sel, addTop: add ? pos(add) : null, addText: add ? add.innerText.trim() : null, variantId: idInput ? idInput.value : null };
  });
  console.log('画面の高さ', info.vh, '｜カートボタンの位置', info.addTop, 'px（' + (info.addTop / info.vh).toFixed(1) + '画面下）｜最初に選ばれている variant', info.variantId);
  for (const [k, v] of Object.entries(info.groups)) console.log('  選択肢', k, '位置', v[0].top, 'px:', v.map(x => (x.checked ? '●' : '') + x.v).join(' / '));
  if (info.sel.length) console.log('  select:', JSON.stringify(info.sel));
  // いちばん大きいサイズ（最後の選択肢）を選んでカートへ
  const names = Object.keys(info.groups);
  for (const nme of names) { const opts = info.groups[nme]; const last = opts[opts.length - 1].v; await p.locator(`input[type=radio][name="${nme}"][value="${last}"]`).first().evaluate(e => { e.click(); }).catch(() => {}); await p.waitForTimeout(600); }
  const chosen = await p.evaluate(() => ({ id: (document.querySelector('form[action*="/cart/add"] input[name="id"]') || {}).value, checked: [...document.querySelectorAll('input[type=radio]:checked')].map(e => e.value) }));
  console.log('選んだ後: variant', chosen.id, '選択', JSON.stringify(chosen.checked));
  const btn = p.locator('button[name="add"], .product-form__submit').first();
  await btn.scrollIntoViewIfNeeded().catch(() => {}); await btn.click({ timeout: 10000 }).catch(e => console.log('click error', e.message.slice(0, 100)));
  await p.waitForTimeout(4000);
  const cart = await p.evaluate(async () => { const r = await fetch('/cart.js'); const j = await r.json(); return j.items.map(i => ({ title: i.product_title.slice(-20), variant: i.variant_title, id: i.variant_id, qty: i.quantity, price: i.final_price / 100 })); });
  console.log('カートの中身:', JSON.stringify(cart));
  await p.screenshot({ path: OUT + '/5_insole_drawer.png' });
  console.log('ページのエラー:', errs.length ? JSON.stringify(errs.slice(0, 5)) : 'なし');
  await b.close();
})();
