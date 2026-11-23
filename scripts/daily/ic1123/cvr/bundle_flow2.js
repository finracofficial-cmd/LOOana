// 11/23 「2個購入」で2個目を別の色にしてカート→決済画面まで（iPhone 13・購入しない・連絡先は入れない・計測の通信は止める）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
const OUT = process.argv[2]; const URL = 'https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush';
const cartJs = async (p) => p.evaluate(async () => { const c = await (await fetch('/cart.js')).json(); return { total: c.total_price / 100, original: c.original_total_price / 100, items: c.items.map(i => ({ t: i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 22), v: i.variant_title, q: i.quantity, line: i.final_line_price / 100, props: Object.keys(i.properties || {}), disc: (i.line_level_discount_allocations || []).map(d => d.discount_application.title + ' ' + d.amount / 100) })), cartDisc: (c.cart_level_discount_applications || []).map(d => d.title + ' ' + d.total_allocated_amount / 100) }; });
(async () => {
  const b = await chromium.launch();
  const run = async (label, fn) => {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
    await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
    const p = await ctx.newPage(); await p.goto(URL, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4000);
    console.log('\n■■', label); await fn(p); await ctx.close();
  };
  const addBtn = async (p) => { const btn = p.locator('form[action*="/cart/add"] button[type=submit], button[name=add]').first(); await btn.scrollIntoViewIfNeeded(); await btn.click(); await p.waitForTimeout(3500); };
  await run('① 「2個購入」で2個目をグレーにしてカートへ', async (p) => {
    await p.evaluate(() => { const el = document.querySelector('.pumper_block'); const t = [...el.querySelectorAll('.basic-tier-mount__left')].find(e => /2個購入/.test(e.innerText)); t.scrollIntoView({ block: 'center' }); t.click(); });
    await p.waitForTimeout(1200);
    const info = await p.evaluate(() => [...document.querySelectorAll('.pumper_block [class*="pmpr_optsel"], .pumper_block [class*="pumper_variant"]')].map(e => ({ c: String(e.className).slice(0, 70), t: (e.innerText || '').replace(/\s+/g, ' ').slice(0, 40), tag: e.tagName })).slice(0, 30));
    console.log('枠の中の色の部品:', JSON.stringify(info));
    // 2つ目の色の部品を開いてグレーを選ぶ
    const opened = await p.evaluate(() => { const rows = [...document.querySelectorAll('.pumper_block .pumper_variant_row')]; const r = rows[1] || rows[0]; if (!r) return 'row なし'; const trg = r.querySelector('[class*="pmpr_optsel"]') || r.querySelector('.pumper_variant_dropdowns') || r; trg.click(); return rows.length + ' rows / clicked ' + String(trg.className).slice(0, 60); });
    console.log('開いた:', opened); await p.waitForTimeout(800);
    const picked = await p.evaluate(() => { const o = [...document.querySelectorAll('.pumper_block *, body > div *')].filter(e => e.children.length === 0 && (e.innerText || '').trim() === 'グレー' && e.offsetParent); if (!o.length) return 'グレーの選択肢なし'; o[o.length - 1].click(); return 'グレーを押した（候補 ' + o.length + '）'; });
    console.log(picked); await p.waitForTimeout(1000);
    console.log('枠の文字:', await p.evaluate(() => document.querySelector('.pumper_block').innerText.replace(/\s+/g, ' ').slice(0, 260)));
    await (await p.$('.pumper_block')).screenshot({ path: OUT + '/bundle_2colors.png' });
    await addBtn(p); console.log('カートの中身:', JSON.stringify(await cartJs(p)));
    await p.goto('https://looty-japan.com/cart', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4500);
    console.log('カート（VIP の自動追加のあと）:', JSON.stringify(await cartJs(p)));
    await p.goto('https://looty-japan.com/checkout', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(7000);
    console.log('決済画面の URL:', p.url().replace(/\?.*/, '').replace(/[0-9a-f]{20,}/, '…'));
    console.log('決済画面の文字:', (await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '))).slice(0, 1800));
    await p.screenshot({ path: OUT + '/checkout_2colors.png', fullPage: true });
  });
  await run('② 1個（ブルー）を入れたあと、色をグレーに変えてもう1度「カートに追加」', async (p) => {
    await addBtn(p); console.log('1回目のあと:', JSON.stringify(await cartJs(p)));
    await p.goto(URL, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500);
    const ch = await p.evaluate(() => { const lab = [...document.querySelectorAll('variant-radios label, fieldset label, .product-form__input label')].find(l => (l.innerText || '').trim() === 'グレー'); if (lab) { lab.scrollIntoView({ block: 'center' }); lab.click(); return 'ページの色の選択でグレーを押した'; } const sel = document.querySelector('variant-selects select, select[name^="options"]'); if (sel) { const o = [...sel.options].find(o => o.text.trim() === 'グレー'); if (o) { sel.value = o.value; sel.dispatchEvent(new Event('change', { bubbles: true })); return 'select でグレー'; } } return 'ページ側の色の選択が見つからない'; });
    console.log(ch); await p.waitForTimeout(1500);
    console.log('枠の文字（色を変えたあと）:', await p.evaluate(() => document.querySelector('.pumper_block').innerText.replace(/\s+/g, ' ').slice(0, 120)));
    await addBtn(p); console.log('2回目のあと:', JSON.stringify(await cartJs(p)));
    await p.goto('https://looty-japan.com/cart', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(4500);
    console.log('カートのページを開いたあと:', JSON.stringify(await cartJs(p)));
    console.log('カートの画面の下の文字:', (await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '))).slice(-520));
    await p.screenshot({ path: OUT + '/cart_2lines.png', fullPage: false });
  });
  await b.close();
})();
