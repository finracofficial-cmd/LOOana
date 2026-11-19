// 11/19 インソール: サイズのラベルをタップして選び、カートに正しいサイズが入るか（iPhone 13 の画面・購入はしない）
const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 100)));
  await p.goto('https://looty-japan.com/products/soft-super-sports-shock-absorption-sweat-absorbent-sockliner-with-massage-function', { waitUntil: 'load', timeout: 60000 });
  await p.waitForTimeout(3000);
  const e0 = errs.length;
  const state = async () => p.evaluate(() => ({ id: (document.querySelector('form[action*="/cart/add"] input[name="id"]') || {}).value, checked: [...document.querySelectorAll('input[type=radio]:checked')].map(e => e.value), url: location.search }));
  console.log('開いた直後:', JSON.stringify(await state()), '｜読み込み時のエラー', e0);
  const lab = p.locator('label', { hasText: '25.5~26.5cm' }).first();
  await lab.scrollIntoViewIfNeeded(); await lab.tap({ timeout: 8000 }).catch(async e => { console.log('tap error', e.message.slice(0, 80)); await lab.click({ force: true }).catch(() => {}); });
  await p.waitForTimeout(1500);
  const lab2 = p.locator('label', { hasText: 'グレー' }).first();
  await lab2.tap({ timeout: 8000 }).catch(e => console.log('tap2 error', e.message.slice(0, 80)));
  await p.waitForTimeout(1500);
  console.log('サイズ 25.5~26.5cm・色 グレー をタップした後:', JSON.stringify(await state()), '｜タップ後に増えたエラー', errs.length - e0);
  const btn = p.locator('button[name="add"], .product-form__submit').first();
  await btn.scrollIntoViewIfNeeded().catch(() => {}); await btn.tap({ timeout: 10000 }).catch(e => console.log('add error', e.message.slice(0, 80)));
  await p.waitForTimeout(4000);
  const cart = await p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return j.items.map(i => ({ variant: i.variant_title, qty: i.quantity, price: i.final_price / 100 })); });
  console.log('カートの中身:', JSON.stringify(cart));
  const dr = await p.evaluate(() => { const e = [...document.querySelectorAll('body *')].filter(e => { const cs = getComputedStyle(e); const r = e.getBoundingClientRect(); return cs.position === 'fixed' && r.height > 300 && r.width > 200 && e.innerText; })[0]; return e ? e.innerText.replace(/\s+/g, ' ').slice(0, 300) : '（カートの画面は出ていない）'; });
  console.log('カートの画面の文字:', dr);
  console.log('エラーの中身:', JSON.stringify([...new Set(errs)].slice(0, 3)));
  await b.close();
})();
