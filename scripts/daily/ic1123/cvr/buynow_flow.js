// 11/23 商品ページの「カートに追加する」の下にある速い決済ボタン（別のお支払い方法）を押すと、決済画面に何が入るか
// A: 枠は最初のまま（1個）／B: 枠で「2個購入」を選んでから／C: カートに2色を入れてから
// iPhone 13・購入しない・連絡先は入れない・計測の通信は止める
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const OUT = process.argv[2]; const URL = 'https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush';
(async () => {
  const b = await chromium.launch();
  const run = async (label, pre) => {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
    await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
    const p = await ctx.newPage(); await p.goto(URL, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4500);
    console.log('\n■■', label); await pre(p);
    const area = p.locator('.shopify-payment-button').first(); await area.scrollIntoViewIfNeeded(); await p.waitForTimeout(600);
    if (label.startsWith('A')) { await p.screenshot({ path: OUT + '/buy_area.png' }); console.log('ボタンの中の文字:', JSON.stringify(await p.evaluate(() => { const out = []; const walk = (root) => { for (const e of root.querySelectorAll('*')) { if (e.shadowRoot) walk(e.shadowRoot); const t = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(''); if (t && e.getBoundingClientRect().width > 0) out.push(e.tagName.toLowerCase() + ':' + t.slice(0, 30)); const a = e.getAttribute && (e.getAttribute('aria-label') || ''); if (a) out.push('aria:' + a.slice(0, 40)); } }; walk(document.querySelector('.shopify-payment-button')); return [...new Set(out)].slice(0, 20); }))); }
    const more = p.getByText('別のお支払い方法').first(); await more.click({ timeout: 8000 }).catch(e => console.log('押せず:', String(e).slice(0, 120)));
    await p.waitForTimeout(8000);
    console.log('移った先:', p.url().replace(/\?.*/, '').replace(/[0-9a-zA-Z]{24,}/, '…'));
    const txt = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
    const i = txt.search(/注文の概要|ご注文内容|小計/); console.log('決済画面の合計まわり:', txt.slice(Math.max(0, i - 500), i + 420));
    console.log('文字の中の値段:', JSON.stringify((txt.match(/¥[\d,]+/g) || []).slice(0, 14)), '／VIP:', /VIP特典/.test(txt), '／ブルー:', (txt.match(/ブルー/g) || []).length, 'グレー:', (txt.match(/グレー/g) || []).length);
    await p.screenshot({ path: OUT + '/buynow_' + label[0] + '.png', fullPage: true }); await ctx.close();
  };
  await run('A 枠は最初のまま（1個）', async () => {});
  await run('B 枠で「2個購入」を選んでから', async (p) => { const t = p.locator('.pumper_block .basic-tier-mount__left', { hasText: '2個購入' }).first(); await t.scrollIntoViewIfNeeded(); await t.click(); await p.waitForTimeout(1500); console.log('枠の文字:', (await p.evaluate(() => document.querySelector('.pumper_block').innerText.replace(/\s+/g, ' '))).slice(0, 200)); });
  await run('C カートに2色（ブルー→グレー）を入れてから', async (p) => {
    const add = async () => { const btn = p.locator('form[action*="/cart/add"] button[type=submit], button[name=add]').first(); await btn.scrollIntoViewIfNeeded(); await btn.click(); await p.waitForTimeout(3500); };
    await add(); await p.goto(URL, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
    await p.evaluate(() => { const lab = [...document.querySelectorAll('variant-radios label, fieldset label, .product-form__input label')].find(l => (l.innerText || '').trim() === 'グレー'); if (lab) { lab.scrollIntoView({ block: 'center' }); lab.click(); } });
    await p.waitForTimeout(1500); await add(); await p.goto(URL, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
    console.log('カート:', JSON.stringify(await p.evaluate(async () => { const c = await (await fetch('/cart.js')).json(); return { total: c.total_price / 100, items: c.items.map(i => i.variant_title + '×' + i.quantity + ' ' + i.final_line_price / 100) }; })));
  });
  await b.close();
})();
