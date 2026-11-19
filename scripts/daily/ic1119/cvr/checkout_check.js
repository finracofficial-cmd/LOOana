// 11/19 決済までの流れをスマホの画面（iPhone 13）で開いて確かめる（購入はしない・連絡先も入れない）。商品ページ → カートに追加 → 決済画面の最初の画面
const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
  const p = await ctx.newPage();
  await p.goto('https://looty-japan.com/products/washable-reusable-fuzz-remover', { waitUntil: 'load', timeout: 60000 });
  await p.waitForTimeout(3000);
  const btn = p.locator('button[name="add"], form[action*="/cart/add"] button[type="submit"], .product-form__submit').first();
  const txt = (await btn.innerText().catch(() => '')).trim();
  await btn.scrollIntoViewIfNeeded().catch(() => {});
  await p.screenshot({ path: OUT + '/1_button.png' });
  await btn.click({ timeout: 10000 }).catch(e => console.log('click error', e.message.slice(0, 120)));
  await p.waitForTimeout(4000);
  await p.screenshot({ path: OUT + '/2_after_add.png' });
  const after = await p.evaluate(() => ({ url: location.href, drawer: [...document.querySelectorAll('body *')].filter(e => { const cs = getComputedStyle(e); const r = e.getBoundingClientRect(); return cs.position === 'fixed' && r.height > 300 && r.width > 200 && e.innerText; }).map(e => e.innerText.replace(/\s+/g, ' ').slice(0, 600)).slice(0, 2) }));
  console.log('ボタンの文字:', txt, '｜押した後のURL:', after.url);
  console.log('押した後に出た画面:', JSON.stringify(after.drawer, null, 0).slice(0, 1500));
  const t0 = Date.now();
  await p.goto('https://looty-japan.com/checkout', { waitUntil: 'load', timeout: 60000 }).catch(e => console.log('checkout error', e.message.slice(0, 120)));
  await p.waitForTimeout(5000);
  console.log('決済画面のURL:', p.url().split('?')[0].replace(/\/cn\/[^/]+/, '/cn/…'), '読み込み', Date.now() - t0, 'ms');
  await p.screenshot({ path: OUT + '/3_checkout_top.png' });
  await p.screenshot({ path: OUT + '/4_checkout_full.png', fullPage: true });
  const co = await p.evaluate(() => ({ h: document.body.scrollHeight, inputs: [...document.querySelectorAll('input, select')].filter(e => e.type !== 'hidden' && e.offsetParent).map(e => (e.getAttribute('placeholder') || e.getAttribute('aria-label') || e.name || e.id || e.type)).slice(0, 40),
    buttons: [...document.querySelectorAll('button, [role=button], a')].filter(e => e.offsetParent && e.innerText.trim()).map(e => e.innerText.trim().replace(/\s+/g, ' ').slice(0, 30)).slice(0, 40), text: document.body.innerText.replace(/\s+/g, ' ').slice(0, 2500) }));
  console.log('決済画面の長さ', co.h, 'px'); console.log('入力欄:', JSON.stringify(co.inputs)); console.log('ボタン:', JSON.stringify(co.buttons)); console.log('文字:', co.text);
  await b.close();
})();
