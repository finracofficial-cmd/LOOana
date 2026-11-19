// 11/19 カートに追加した後に出る画面で「ご購入手続きへ」のボタンが最初から見えるか・決済画面が出るまでの時間（iPhone 13 の画面・サーバーから。日本のスマホ回線ではない）
const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const slug of ['washable-reusable-fuzz-remover', 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush']) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
    const p = await ctx.newPage();
    await p.goto('https://looty-japan.com/products/' + slug, { waitUntil: 'load', timeout: 60000 });
    await p.waitForTimeout(2500);
    const btn = p.locator('button[name="add"], form[action*="/cart/add"] button[type="submit"], .product-form__submit').first();
    await btn.scrollIntoViewIfNeeded().catch(() => {});
    await btn.click({ timeout: 10000 }).catch(e => console.log('click error', e.message.slice(0, 100)));
    await p.waitForTimeout(4000);
    const r = await p.evaluate(() => {
      const vh = window.innerHeight;
      const els = [...document.querySelectorAll('button, a, input[type=submit]')].filter(e => /ご購入手続きへ/.test(e.innerText || e.value || '') && e.getBoundingClientRect().width > 0);
      return { vh, buttons: els.map(e => { const rc = e.getBoundingClientRect(); return { text: (e.innerText || e.value).replace(/\s+/g, ' ').slice(0, 24), top: Math.round(rc.top), bottom: Math.round(rc.bottom), inView: rc.top >= 0 && rc.bottom <= vh }; }) };
    });
    console.log(slug.slice(0, 30), '｜画面の高さ', r.vh, '｜「ご購入手続きへ」', JSON.stringify(r.buttons));
    const t0 = Date.now();
    await p.goto('https://looty-japan.com/checkout', { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(e => console.log('err', e.message.slice(0, 80)));
    const t1 = Date.now() - t0;
    await p.locator('input[type=email], input[name=email]').first().waitFor({ state: 'visible', timeout: 30000 }).catch(() => {});
    console.log('  決済画面: 最初の応答まで', t1, 'ms・メール欄が出るまで', Date.now() - t0, 'ms');
    await ctx.close();
  }
  await b.close();
})();
