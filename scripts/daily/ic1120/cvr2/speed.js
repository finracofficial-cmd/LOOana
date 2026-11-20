// 11/20 商品ページの表示の速さと重さを測る（スマホ・回線を 4G 相当に絞る）。読むだけ。計測の送信（集計・ピクセルの送信先）だけ止める
const { chromium, devices } = require('playwright');
const OUT = process.argv[2];
const BEACON = /\/api\/collect|monorail-edge|\/\.well-known\/shopify\/monorail|facebook\.com\/tr|google-analytics\.com\/(g\/)?collect|analytics\.tiktok\.com\/api|clarity\.ms\/collect|doubleclick\.net/i;
const P = [['ガラスクリーナー', 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush'], ['ワイパー', 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use'], ['ナノ', 'washable-reusable-fuzz-remover']];
(async () => {
  const b = await chromium.launch();
  for (const [name, slug] of P) {
    for (const mode of ['4G（下り9Mbps・遅延150ms）・CPU 4倍遅く', '絞りなし']) {
      const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'ja-JP' }); const p = await ctx.newPage();
      await p.route(u => BEACON.test(u.href), r => r.abort());
      const cdp = await ctx.newCDPSession(p);
      if (mode.startsWith('4G')) { await cdp.send('Network.enable'); await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 9e6 / 8, uploadThroughput: 3e6 / 8 }); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 }); }
      let bytes = 0, n = 0; const byType = {}; p.on('response', async r => { try { const h = r.headers(); const len = parseInt(h['content-length'] || '0'); const t = r.request().resourceType(); n++; bytes += len; byType[t] = (byType[t] || 0) + len; } catch (e) {} });
      await p.addInitScript(() => { window.__lcp = 0; window.__cls = 0; new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true }); new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: 'layout-shift', buffered: true }); });
      const t0 = Date.now(); await p.goto('https://looty-japan.com/products/' + slug, { waitUntil: 'load', timeout: 120000 }); const tLoad = Date.now() - t0; await p.waitForTimeout(4000);
      const m = await p.evaluate(() => { const nav = performance.getEntriesByType('navigation')[0]; const fcp = (performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime; const imgs = [...document.images]; return { ttfb: Math.round(nav.responseStart), fcp: Math.round(fcp || 0), lcp: Math.round(window.__lcp), dcl: Math.round(nav.domContentLoadedEventEnd), load: Math.round(nav.loadEventEnd), cls: +window.__cls.toFixed(3), imgs: imgs.length, lazy: imgs.filter(i => i.loading === 'lazy').length, scripts: document.scripts.length, height: document.documentElement.scrollHeight }; });
      console.log(`${name}｜${mode}: 最初の応答 ${m.ttfb}ms・最初の表示 ${m.fcp}ms・いちばん大きい要素の表示（LCP） ${m.lcp}ms・読み込み完了 ${m.load}ms・ずれ（CLS） ${m.cls}｜通信 ${n}本・${(bytes / 1e6).toFixed(1)}MB（画像 ${((byType.image || 0) / 1e6).toFixed(1)}・スクリプト ${((byType.script || 0) / 1e6).toFixed(1)}・動画など ${((byType.media || 0) / 1e6).toFixed(1)}）・画像 ${m.imgs}枚（遅延読み込み ${m.lazy}）・スクリプト ${m.scripts}本・ページの長さ ${m.height}px（画面 ${Math.round(m.height / 664)}枚分）`);
      if (mode.startsWith('4G') && name === 'ガラスクリーナー') await p.screenshot({ path: OUT + '/first_view_glass.png' });
      await ctx.close();
    }
  }
  await b.close();
})();
