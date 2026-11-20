// 11/21 カートで数量を増やしたとき・色ちがいを1個ずつ入れたときに、2個10%OFF が付くかを確かめる（購入はしない・計測の通信は止める）
const { chromium, devices } = require('playwright');
const BLOCK = /monorail|facebook\.com\/tr|connect\.facebook\.net|google-analytics|googletagmanager|analytics\.tiktok|clarity\.ms|\/api\/collect|web-pixels|wpm@|provesrc|doubleclick/;
(async () => {
  const b = await chromium.launch();
  const run = async (label, fn) => {
    const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' });
    await ctx.route('**/*', r => BLOCK.test(r.request().url()) ? r.abort() : r.continue());
    const p = await ctx.newPage();
    await p.goto('https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(3000);
    const vs = await p.evaluate(async () => (await (await fetch(location.pathname + '.js')).json()).variants.filter(v => v.available).map(v => ({ id: v.id, t: v.title })));
    const post = (u, body) => p.evaluate(async ([u, body]) => { const r = await fetch(u, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); return r.status; }, [u, body]);
    await fn(vs, post, p);
    await p.waitForTimeout(6000);   // カートのアプリが VIP特典の行などを足すのを待つ
    const c = await p.evaluate(async () => { const c = await (await fetch('/cart.js')).json(); return { total: c.total_price / 100, original: c.original_total_price / 100, discount: c.total_discount / 100, items: c.items.map(i => ({ t: i.product_title.slice(0, 16), v: i.variant_title, q: i.quantity, line: i.final_line_price / 100, disc: (i.line_level_discount_allocations || []).map(d => d.discount_application.title + ' ' + d.amount / 100) })), cartDisc: (c.cart_level_discount_applications || []).map(d => d.title + ' ' + d.total_allocated_amount / 100) }; });
    console.log('■', label); console.log(JSON.stringify(c));
    await ctx.close();
  };
  await run('① 1個を入れてから、数量を 2 に増やす（同じ色）', async (vs, post, p) => { await post('/cart/add.js', { id: vs[0].id, quantity: 1 }); await p.waitForTimeout(2500); await post('/cart/change.js', { id: String(vs[0].id), quantity: 2 }); });
  await run('② 色ちがいを 1個ずつ入れる', async (vs, post, p) => { await post('/cart/add.js', { id: vs[0].id, quantity: 1 }); await p.waitForTimeout(1500); await post('/cart/add.js', { id: vs[1].id, quantity: 1 }); });
  await b.close();
})();
