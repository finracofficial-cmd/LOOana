// 11/19 インソール: 色・サイズを選んでから「2個購入で10％オフ」を選ぶと、2個それぞれの色・サイズが何になるか（iPhone 13 の画面・購入はしない）
const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  const p = await ctx.newPage();
  await p.goto('https://looty-japan.com/products/soft-super-sports-shock-absorption-sweat-absorbent-sockliner-with-massage-function', { waitUntil: 'load', timeout: 60000 });
  await p.waitForTimeout(3500);
  const widget = async () => p.evaluate(() => { const e = [...document.querySelectorAll('div')].filter(d => /1個購入/.test(d.innerText || '') && /2個購入/.test(d.innerText || '')).sort((a, b) => a.innerText.length - b.innerText.length)[0]; return e ? { text: e.innerText.replace(/\s+/g, ' ').slice(0, 420), selects: [...e.querySelectorAll('select')].filter(s => s.offsetParent).map(s => s.options[s.selectedIndex] ? s.options[s.selectedIndex].text.trim() : '') } : null; });
  for (const t of ['グレー', '25.5~26.5cm']) { const lab = p.locator('label', { hasText: t }).first(); await lab.scrollIntoViewIfNeeded(); await lab.tap({ timeout: 8000 }).catch(e => console.log('tap error', t, e.message.slice(0, 60))); await p.waitForTimeout(1200); }
  console.log('① 色グレー・サイズ25.5~26.5 を選んだ直後のまとめ買いの表示:', JSON.stringify(await widget()));
  const two = p.getByText('2個購入で10％オフ', { exact: false }).first();
  await two.scrollIntoViewIfNeeded(); await two.tap({ timeout: 8000 }).catch(e => console.log('tap2 error', e.message.slice(0, 80)));
  await p.waitForTimeout(2000);
  console.log('② 「2個購入」をタップした後の表示:', JSON.stringify(await widget()));
  await p.screenshot({ path: OUT + '/6_bundle_two.png' });
  const btn = p.locator('button[name="add"], .product-form__submit').first();
  await btn.scrollIntoViewIfNeeded().catch(() => {}); await btn.tap({ timeout: 10000 }).catch(e => console.log('add error', e.message.slice(0, 80)));
  await p.waitForTimeout(4500);
  const cart = await p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return { total: j.total_price / 100, items: j.items.map(i => ({ variant: i.variant_title, qty: i.quantity, price: i.final_line_price / 100, title: i.product_title.slice(0, 12) })) }; });
  console.log('③ カートの中身:', JSON.stringify(cart));
  await b.close();
})();
