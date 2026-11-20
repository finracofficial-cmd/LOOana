// 11/20 商品ページとカートに読み込まれているアプリのスクリプトと、画面に出ているものを読む（読むだけ・計測の送信は止める）
const { chromium, devices } = require('playwright');
const BEACON = /\/api\/collect|monorail-edge|\/\.well-known\/shopify\/monorail|facebook\.com\/tr|google-analytics\.com\/(g\/)?collect|analytics\.tiktok\.com\/api|clarity\.ms\/collect|doubleclick\.net/i;
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage(); await p.route(u => BEACON.test(u.href), r => r.abort());
  const reqs = []; p.on('response', r => { const q = r.request(); if (q.resourceType() === 'script') reqs.push([r.url(), parseInt(r.headers()['content-length'] || '0')]); });
  await p.goto('https://looty-japan.com/products/nano-fine-fiber-defogging-and-windproof-window-cleaning-brush', { waitUntil: 'load', timeout: 60000 }); await p.waitForTimeout(5000);
  const host = u => { try { const x = new URL(u); if (x.hostname === 'cdn.shopify.com') { const m = x.pathname.match(/\/extensions\/[^/]+\/([^/]+)\//); return m ? 'shopify拡張:' + m[1].replace(/-\d+$/, '') : (x.pathname.includes('/shopifycloud/') ? 'shopify本体' : 'テーマ・shopify'); } return x.hostname; } catch (e) { return '?'; } };
  const agg = {}; for (const [u, n] of reqs) { const h = host(u); agg[h] = agg[h] || [0, 0]; agg[h][0]++; agg[h][1] += n; }
  console.log('スクリプトの読み込み元（本数・サイズ）:'); Object.entries(agg).sort((a, c) => c[1][1] - a[1][1]).slice(0, 24).forEach(([h, v]) => console.log(`  ${h}: ${v[0]}本・${(v[1] / 1000).toFixed(0)}KB`));
  const vis = await p.evaluate(() => { const q = s => [...document.querySelectorAll(s)].filter(e => e.offsetParent !== null && e.getBoundingClientRect().height > 5); const txt = e => (e.innerText || '').replace(/\s+/g, ' ').slice(0, 70);
    return { bundler: q('[class*="bundler"],[id*="bundler"]').map(txt).slice(0, 3), selleasy: q('[class*="lb-upsell"],[id*="lb-upsell"],[class*="selleasy"],lb-upsell-box,[class*="lb-"]').map(txt).slice(0, 3), judgeme: q('.jdgm-prev-badge').map(txt).slice(0, 2), provesrc: q('[class*="provesrc"],[id*="provesrc"]').map(txt).slice(0, 2), fv: { h1Top: Math.round((document.querySelector('h1') || document.body).getBoundingClientRect().top), priceTop: Math.round((document.querySelector('.price') || document.body).getBoundingClientRect().top), badgeTop: (document.querySelector('.jdgm-prev-badge') ? Math.round(document.querySelector('.jdgm-prev-badge').getBoundingClientRect().top) : null), video: document.querySelectorAll('video, deferred-media, iframe[src*="youtube"]').length, firstImgH: Math.round((document.querySelector('media-gallery') || document.body).getBoundingClientRect().height) } }; });
  console.log('画面に出ているもの:', JSON.stringify(vis, null, 1));
  const pol = await p.evaluate(() => [...document.querySelectorAll('footer a, .footer a')].map(a => a.innerText.trim()).filter(Boolean).slice(0, 20));
  console.log('フッターのリンク:', JSON.stringify(pol));
  await b.close();
})();
