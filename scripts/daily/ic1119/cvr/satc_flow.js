// 11/19 固定カートボタン（全商品用）の動作確認: まとめ買いの割引・色の選択・値段の違うバリエーション・選択肢なし
const { chromium, devices } = require('playwright'); const { open } = require('./satc_lib.js');
const OUT = process.argv[2];
const J = o => JSON.stringify(o);
(async () => {
  const b = await chromium.launch();
  // ① ナノ: 2個のまとめ買いを選んでから帯のボタン → 2個・10%オフで入るか
  { const t = await open(b, devices, 'washable-reusable-fuzz-remover'); console.log('① ナノ 開いた直後', J(await t.st()));
    const two = t.p.locator('.pumper_block .pmpr-tier-shell__card', { hasText: '2個購入' }).first(); await two.scrollIntoViewIfNeeded(); await two.tap(); await t.p.waitForTimeout(1500);
    await t.p.evaluate(() => window.scrollTo(0, 300)); await t.p.waitForTimeout(900);
    console.log('   2個を選んで上に戻った', J(await t.st())); await t.p.screenshot({ path: OUT + '/v2_nano_2ko.png' });
    await t.tapBar(); await t.p.waitForTimeout(4000); console.log('   帯のボタンを1回 → カート', J(await t.cart()), '｜増えたエラーの種類', J([...new Set(t.errs.slice(t.e0))])); await t.ctx.close(); }
  // ② ガラス: 上の色ボタンでグレーを選んでから帯のボタン → グレーが入るか
  { const t = await open(b, devices, 'nano-fine-fiber-defogging-and-windproof-window-cleaning-brush'); console.log('② ガラス 開いた直後', J(await t.st()));
    await t.tapBar(); await t.p.waitForTimeout(1500); console.log('   1回目のタップ（選ぶ場所へ）', J(await t.st()), 'カート', J((await t.cart()).items)); await t.p.screenshot({ path: OUT + '/v2_glass_tap1.png' });
    await t.p.evaluate(() => window.scrollTo(0, 0)); await t.p.waitForTimeout(600);
    const g = t.p.locator('variant-selects label', { hasText: 'グレー' }).first(); await g.scrollIntoViewIfNeeded(); await g.tap(); await t.p.waitForTimeout(1500);
    console.log('   上の色ボタンでグレー', J(await t.st())); await t.tapBar(); await t.p.waitForTimeout(4000); console.log('   帯のボタン → カート', J(await t.cart())); await t.ctx.close(); }
  // ③ ブランケット（サイズで値段が違う）: ラージを選ぶと帯の値段が変わるか
  { const t = await open(b, devices, 'thickened-toka-long-wool-casual-blanket'); console.log('③ ブランケット 開いた直後', J(await t.st()));
    const l = t.p.locator('variant-selects label', { hasText: 'ラージ' }).first(); if (await l.count()) { await l.scrollIntoViewIfNeeded(); await l.tap(); await t.p.waitForTimeout(2000); }
    await t.p.evaluate(() => window.scrollTo(0, 300)); await t.p.waitForTimeout(1200); console.log('   ラージを選んだ後', J(await t.st())); await t.p.screenshot({ path: OUT + '/v2_blanket_large.png' });
    await t.tapBar(); await t.p.waitForTimeout(4000); console.log('   帯のボタン → カート', J(await t.cart())); await t.ctx.close(); }
  // ④ ワイパー（選択肢なし）: 1回で入るか
  { const t = await open(b, devices, 'soft-silicone-car-squeegee-integrated-windshield-glass-scraper-tool-scratch-free-paint-safe-auto-washing-accessory-for-home-use'); console.log('④ ワイパー 開いた直後', J(await t.st()));
    await t.tapBar(); await t.p.waitForTimeout(4000); console.log('   帯のボタンを1回 → カート', J(await t.cart())); await t.ctx.close(); }
  // ⑤ インソール（色×サイズ）: 1回目で選ぶ場所へ → まとめ買いの枠の中でサイズを変える → 2回目で入るか
  { const t = await open(b, devices, 'soft-super-sports-shock-absorption-sweat-absorbent-sockliner-with-massage-function'); console.log('⑤ インソール 開いた直後', J(await t.st()));
    await t.tapBar(); await t.p.waitForTimeout(1600); console.log('   1回目のタップ（選ぶ場所へ）', J(await t.st())); await t.p.screenshot({ path: OUT + '/v2_insole_tap1.png' });
    const trig = t.p.locator('.pumper_block .pmpr-tier-shell__card[data-selected="true"] .pmpr_optsel_trigger'); const n = await trig.count();
    if (n) { await trig.nth(n - 1).tap(); await t.p.waitForTimeout(700); const opt = t.p.locator('.pmpr_optsel_list:not(.pmpr_optsel_list--hidden) .pmpr_optsel_option').nth(3); if (await opt.count()) { await opt.tap(); await t.p.waitForTimeout(1200); } }
    await t.p.evaluate(() => window.scrollTo(0, 300)); await t.p.waitForTimeout(900);
    await t.tapBar(); await t.p.waitForTimeout(4000); console.log('   まとめ買いの枠でサイズを変えて、帯のボタン → カート', J(await t.cart())); await t.ctx.close(); }
  await b.close();
})();
