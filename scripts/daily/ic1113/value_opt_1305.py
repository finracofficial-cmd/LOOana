# -*- coding: utf-8 -*-
"""11/13(金) 13時台 「CV数の最大化とCV値の最大化はどっちがいいの？多分今全部前者だと思うけど」
入力: value_opt_1305_raw.json（有効10キャンペーンの広告セット別 最適化目標＝Meta直接読み／Shopify 商品別 注文数・販売額 10/14〜11/12／Meta キャンペーン別 購入・購入金額 同期間）
見ること: ①今の設定 ②商品ごとに「1注文の金額」がどれだけばらつくか（＝値の最大化が見分けられる差があるか）"""
import os, json
D = os.path.dirname(os.path.abspath(__file__)) + '/'
R = json.load(open(D + 'value_opt_1305_raw.json'))
src = open(D + '../../product_tabs.py', encoding='utf-8').read(); g = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], g); PRICE, COST = g['PRICE'], g['COST']

print('■ 今の設定（有効な広告セット）')
on = [(c, a) for c, v in R['optgoal'].items() for a in v if a[1] == 'ENABLED']
print(f"  {len(on)}本すべて: " + ' / '.join(sorted({f'{a[2]}・{a[3]}・{a[4]}' for c, a in on})))

SH = {}
for t, o, n, gs, ds in R['shopify_30d']['rows']:
    SH[t] = (int(o), int(n), int(gs), -int(ds))
ME = {}
for line in R['meta_30d']['data'].split('\n')[1:]:
    c, co, pu, va = line.strip().split(',')
    ME[c] = (float(co), 0 if pu == 'null' else int(pu), 0 if va == 'null' else float(va))
ACT = ['ナノガラス脱毛パッド', '伸縮ガラスクリーナー', 'W固定スマホ車載ホルダー', '快適マジックインソール', '伸縮ワックス洗車ブラシ',
       '4-in-1マルチクリーナー', 'ワイド水切りワイパー', 'マグネットドアクッション', '防風あったか裏起毛パンツ']
print('\n■ 商品別（10/14〜11/12）: 1注文あたりの個数（Shopify・販売額÷売価÷注文数）／Meta 購入1件の金額÷売価（カート全体の金額）')
rows = []
for k in ACT:
    t = [x for x in SH if k in x]; assert len(t) == 1, (k, t); o, n, gs, ds = SH[t[0]]
    assert gs % PRICE[k] == 0, k; u = gs // PRICE[k]
    co, pu, va = ME[k]
    rows.append((k, o, u, u / o, ds / gs, va / pu / PRICE[k] if pu else None, pu))
for k, o, u, upo, dr, mr, pu in sorted(rows, key=lambda x: -x[3]):
    print(f"  {k}: 注文{o}・{u}個＝1注文 {upo:.2f}個（値引率 {dr*100:.1f}%）｜Meta 購入{pu}件・1件の金額 売価の{mr:.2f}倍")
co, pu, va = ME['カタログ全部（テスト）']
print(f"  カタログ全部（テスト）: Meta 購入{pu}件・1件の金額 {va/pu:,.0f}円（全商品横断なので売価との比は出さない）")
print('\n■ 1注文の利益（売価−値引−原価・2個以上で10%OFF）: 1個 → 2個')
for k in ('快適マジックインソール', '伸縮ガラスクリーナー', 'マグネットドアクッション'):
    p, c = PRICE[k], COST[k]
    print(f"  {k}: 1個 {p-c:,}円 → 2個 {round(2*p*0.9)-2*c:,}円（{(round(2*p*0.9)-2*c)/(p-c):.2f}倍）")
