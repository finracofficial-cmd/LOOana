// 11/20 17時台 「いまのところ異常ある？」: 公開ページを確認用のブラウザ（iPhone 13 の画面）で開き、商品ページ → カート → 決済画面が動くかを見る。
// 計測の通信（Shopify の集計・Meta などのピクセル）は止める。メール・住所は入れない。支払いはしない。お店には何も保存しない
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const PAGES = [['伸縮ガラスクリーナー', 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush'], ['ナノガラス脱毛パッド', 'washable-reusable-fuzz-remover']];
(async () => {
  const b = await chromium.launch();
  for (const [name, handle] of PAGES) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
    await p.route(u => BLOCK.test(u.toString()), r => r.abort());
    const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 70)));
    const t0 = Date.now(); const res = await p.goto('https://looty-japan.com/products/' + handle, { waitUntil: 'load', timeout: 60000 }); const tLoad = Date.now() - t0;
    await p.waitForTimeout(3000);
    const st = await p.evaluate(() => { const j = document.getElementById('looty-jump'); const a = document.querySelector('button[name="add"], .product-form__submit'); const bx = document.querySelector('.pumper_block');
      return { jump: !!j && !j.hidden && getComputedStyle(j).display !== 'none', jumpPrice: j ? j.querySelector('.looty-jump__price').textContent.trim() : null, addBtn: a ? a.textContent.replace(/\s+/g, ' ').trim() : null, addDisabled: a ? a.disabled : null, bundle: !!bx && bx.offsetParent !== null }; });
    console.log(`■ ${name}: 応答 ${res.status()}・読み込み ${tLoad}ms・下の帯 ${st.jump ? '表示' : 'なし'}（${st.jumpPrice}）・「${st.addBtn}」ボタン ${st.addDisabled ? '押せない' : '押せる'}・限定セールの枠 ${st.bundle ? '表示' : 'なし'}`);
    const btn = p.locator('button[name="add"], .product-form__submit').first(); await btn.scrollIntoViewIfNeeded(); await btn.tap(); await p.waitForTimeout(4000);
    const cart = await p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return { total: j.total_price / 100, n: j.item_count, items: j.items.map(i => i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 18) + '×' + i.quantity) }; });
    console.log('  カート:', JSON.stringify(cart));
    const t1 = Date.now(); const r2 = await p.goto('https://looty-japan.com/checkout', { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(6000);
    const co = await p.evaluate(() => { const t = document.body.innerText.replace(/\s+/g, ' '); const has = w => t.includes(w);
      return { url: location.pathname.slice(0, 14), mail: has('メール') || has('連絡先'), addr: has('郵便番号'), card: has('クレジットカード') || has('カード番号'), paidy: has('ペイディ') || has('あと払い'), qr: has('スマホ決済') || has('PayPay'), pay: has('今すぐ支払う') || has('ご注文手続き') || has('購入する'), total: (t.match(/合計\s*(?:JPY)?\s*¥?[\d,]+/) || [''])[0], twoPkg: has('個の荷物') }; });
    console.log(`  決済画面: 応答 ${r2.status()}・${Date.now() - t1}ms・${JSON.stringify(co)}`);
    console.log('  ページのエラー:', errs.length ? errs.join(' / ') : 'なし');
    await ctx.close();
  }
  await b.close();
})();
