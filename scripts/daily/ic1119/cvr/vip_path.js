// 11/19 VIP特典の行が自動で入るかを、買い方別に確かめる（計測の通信は止める・連絡先は入れない・支払いはしない）
//  ア: まとめ買いの枠で「2個」を選んで入れる（Pumper の特典）
//  イ: 「1個」を2回入れる（#32296 と同じ形。カート合計 7,000円以上 → Monster Cart の特典のはず）
//  ウ: 別の商品を1個ずつ（合計 7,000円以上）
const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/i;
const NANO = 'washable-reusable-fuzz-remover', WIPER = 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use';
(async () => {
  const b = await chromium.launch();
  const mk = async () => { const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage(); await p.route(u => BLOCK.test(u.href), r => r.abort()); return { ctx, p }; };
  const open = async (p, slug) => { await p.goto('https://looty-japan.com/products/' + slug, { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3500); };
  const add = async p => { const btn = p.locator('product-form form[action*="/cart/add"] button[name="add"]').first(); await btn.scrollIntoViewIfNeeded(); await btn.tap(); await p.waitForTimeout(5000); };
  const cart = p => p.evaluate(async () => { const j = await (await fetch('/cart.js')).json(); return { total: j.total_price / 100, items: j.items.map(i => ({ t: i.product_title.replace(/【[^】]*】/g, '').trim().slice(0, 22), q: i.quantity, line: i.final_line_price / 100, props: Object.keys(i.properties || {}).join(',') })) }; });
  const top = p => p.evaluate(() => { const k = [...document.querySelectorAll('body *')].filter(e => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return (s.position === 'fixed' || s.position === 'absolute') && r.height > 400 && r.width > 250 && /ご購入手続き/.test(e.innerText || ''); }).sort((a, c) => (a.innerText || '').length - (c.innerText || '').length)[0]; return k ? k.innerText.replace(/\s+/g, ' ').slice(0, 150) : '（カートの画面が見つからず）'; });
  const co = async p => { await p.goto('https://looty-japan.com/checkout', { waitUntil: 'domcontentloaded', timeout: 60000 }); await p.waitForTimeout(6000); const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')); return (t.match(/\d+個のアイテム/) || ['（個数の表示なし）'])[0] + '｜VIP特典の文字: ' + (/VIP特典/.test(t) ? 'あり' : 'なし'); };
  { const { ctx, p } = await mk(); await open(p, NANO); const two = p.locator('.pumper_block .pmpr-tier-shell__card', { hasText: '2個購入' }).first(); await two.scrollIntoViewIfNeeded(); await two.tap(); await p.waitForTimeout(1500); await add(p);
    console.log('ア 2個を選んで入れる:', JSON.stringify(await cart(p))); console.log('   カートの画面の上:', await top(p)); await ctx.close(); }
  { const { ctx, p } = await mk(); await open(p, NANO); await add(p); console.log('イ 1個を入れた:', JSON.stringify(await cart(p)));
    await open(p, NANO); await add(p); await p.waitForTimeout(3000); console.log('   もう1回 1個を入れた:', JSON.stringify(await cart(p))); console.log('   カートの画面の上:', await top(p)); await p.screenshot({ path: OUT + '/vip_i.png' });
    await p.waitForTimeout(4000); console.log('   4秒後のカート:', JSON.stringify((await cart(p)).items.map(i => i.t + '×' + i.q))); console.log('   決済画面:', await co(p)); await ctx.close(); }
  { const { ctx, p } = await mk(); await open(p, NANO); await add(p); await open(p, WIPER); await add(p); await p.waitForTimeout(3000);
    console.log('ウ ナノ1個＋ワイパー1個:', JSON.stringify(await cart(p))); console.log('   カートの画面の上:', await top(p)); await p.screenshot({ path: OUT + '/vip_u.png' }); console.log('   決済画面:', await co(p)); await ctx.close(); }
  await b.close();
})();
