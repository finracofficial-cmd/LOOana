# -*- coding: utf-8 -*-
"""関連商品セクションを車まわり2商品でオンにする場合の、導入前ベースライン。
判定日(8/22)に同じ式で測り直すため、基準を先に確定させておく。

Shopify実測 8/07-13（gross/discounts/net_items_sold/orders, GROUP BY product_title）
Meta実測   8/07-13（cost/impressions/outbound_clicks, キャンペーン別）
CVR = Shopify注文 ÷ Metaアウトバウンドクリック（SKILL既定）
"""
P = {  # 商品: (gross, disc, items, orders, cost, impressions, clicks, 原価, 売価)
 'W固定スマホ車載ホルダー': (652720, 13731, 164, 147, 205584, 140633, 3897, 1182, 3980),
 '2WAYシートボックス':     (338640, 13197,  68,  55,  94260,  42235, 1148, 1943, 4980),
}
print('■ 導入前ベースライン（2026-08-07〜13 実測）')
h = f"{'商品':<22}{'注文':>5}{'点数':>5}{'点数/注文':>10}{'クリック':>9}{'CVR':>8}{'広告費':>9}{'CPA':>7}{'実売':>9}{'利益':>9}"
print(h); print('=' * 96)
T = [0] * 6
for n, (g, dc, it, od, c, imp, ck, cost, price) in P.items():
    q = g // price; assert g % price == 0, (n, g)
    net = g - dc; prof = net - q * cost - c
    print(f"{n:<22}{od:>5}{q:>5}{q/od:>10.3f}{ck:>9,}{od/ck:>8.3%}{c:>9,}{c/od:>7,.0f}{net:>9,}{prof:>+9,}")
    T = [a + b for a, b in zip(T, [od, q, ck, c, net, prof])]
od, q, ck, c, net, prof = T
print('-' * 96)
print(f"{'合計':<22}{od:>5}{q:>5}{q/od:>10.3f}{ck:>9,}{od/ck:>8.3%}{c:>9,}{c/od:>7,.0f}{net:>9,}{prof:>+9,}")

print(f"""
■ 8/22の判定基準（先に宣言。当日はこの式に当てはめるだけ）
   測り直す窓 : 2026-08-15〜21（7日）。式・データ源は上と同一。
   対象       : W固定 + 2WAYシートボックス の合算

   ① 合算CVR < {od/ck:.3%}          → 即オフ（クロスセルの微益よりCVR低下の損が桁違いに大きい）
   ② 合算CVR >= {od/ck:.3%} かつ 点数/注文 >= {q/od+0.05:.3f}  → 維持。車カテゴリの新商品にも展開
   ③ 上のどちらでもない（両方ほぼ横ばい）       → 効いていない。オフに戻す

   ※ CVRは分母がMetaクリックなので、広告の配信構成が変わると動く。
     判定日に合算CPMが {sum(P[n][4] for n in P)/sum(P[n][5] for n in P)*1000:,.0f}円 から±25%を超えて動いていたら、
     配信側の変化が混ざっているので判定を1週間延ばす。
""")
