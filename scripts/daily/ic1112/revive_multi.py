# -*- coding: utf-8 -*-
"""11/12 00時台: 止めている商品のうち「1回の注文で複数買われる」商品はどれか（読み取りのみ）。
個数/注文・注文1件あたりの売上 = ShopifyQL 実測（6/29〜11/11・units_per_order_0629_1111_raw.json）。
広告の実績（通算利益・最後の配信期間の倍率）= CSV実測を w1111.py の積み直し関数で集計（revival.py と同じ定義。ラン=広告費500円以上の日の連なり・3日以上空いたら別のラン）。
季節の区分（夏物）はこちらの分類で、データではない。"""
import io, contextlib, datetime, collections, json, csv
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1111.py').read(), g)
WIN, ALLD, MAP, AD, S, COST, PRICE = g['WIN'], g['ALLD'], g['MAP'], g['AD'], g['S'], g['COST'], g['PRICE']
INV = {v: k for k, v in MAP.items()}
D = lambda s: datetime.date.fromisoformat(s)
def W(days, n):
    key = 'm' + n + days[0] + days[-1] + str(len(days)); WIN[key] = days
    sal = sum(S[n][d][0] - S[n][d][1] for d in days if d in S[n])
    q, k = g['qty'](n, days, key)
    return sal, k, q
raw = json.load(open('scripts/daily/ic1112/units_per_order_0629_1111_raw.json'))
def short(t):
    for n in sorted(PRICE, key=len, reverse=True):
        if n in t: return n
    return None
SH = collections.defaultdict(lambda: [0, 0, 0, 0])
for t, o, u, gr, dc in raw['rows']:
    n = short(t)
    if not n: continue
    for i, v in enumerate((int(o), int(u), int(gr), -int(dc))): SH[n][i] += v
# 検算: ShopifyQL の gross 合計 = CSV の gross 合計（同じ期間）
cg = sum(int(r['gross']) for r in csv.DictReader(open('data/daily/daily_sales.csv')) if '2026-06-29' <= r['date'] <= '2026-11-11')
sg = sum(int(r[3]) for r in raw['rows'])
print(f'検算: ShopifyQL gross {sg:,} / CSV gross {cg:,} / 差 {sg-cg:,}')
ACTIVE = {'すき間収納シートポケット', '防風あったか裏起毛パンツ', 'クリアビューレインガードフィルム', 'ワイド水切りワイパー', 'マグネットドアクッション', '伸縮ワックス洗車ブラシ',
          '伸縮ガラスクリーナー', '4-in-1マルチクリーナー', '快適マジックインソール', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド'}   # 11/12 00:3x Meta直読で配信中
SUMMER = {'害虫ブロッカー', '4WAY', '形状記憶日傘', '完全遮光・形状記憶', '接触冷感UVパーカー', '偏光・調光サングラス', '接触冷感UVアームカバー', '卓上冷感クーラー', '5WAY腰掛けファン',
          '3WAYサーキュレーター', '健康サンダル', '完全遮光・接触冷感UVハット', '瞬間冷感ポンチョ', '瞬間冷却ハンディファン', 'もちふわ肉球サンダル', 'リカバリーサンダル', '湯上がりガーゼワンピース'}
runs = {}
for c in AD:
    if 'カタログ' in c: continue
    n = INV.get(c, c)
    days = sorted(d for d in AD[c] if AD[c][d] >= 500 and d in ALLD)
    if not days: continue
    rs = [[days[0]]]
    for d in days[1:]:
        if (D(d) - D(rs[-1][-1])).days >= 3: rs.append([d])
        else: rs[-1].append(d)
    out = []
    for r in rs:
        span = [d for d in ALLD if r[0] <= d <= r[-1]]
        try: s, k, q = W(span, n)
        except Exception as e: out.append(None); continue
        a = sum(AD[c].get(d, 0) for d in span)
        out.append((r[0], r[-1], len(r), a, q, s - k - a, (s - k) / a if a else None))
    runs[n] = out
def adinfo(n):
    out = [o for o in runs.get(n, []) if o]
    if not out: return None
    ta = sum(o[3] for o in out); tp = sum(o[5] for o in out)
    # 7日以上続いた最後のラン（1日だけの再開テストは除く）と、その終わり7日
    long = [o for o in out if o[2] >= 7]
    last = long[-1] if long else out[-1]
    c = MAP.get(n, n); ld = [d for d in ALLD if last[0] <= d <= last[1]][-7:]
    s, k, q = W(ld, n); a = sum(AD[c].get(d, 0) for d in ld)
    return tp, ta, last, (s - k) / a if a else None, out[-1]
print('\n商品 | 注文 | 個数/注文 | 値引率 | 注文1件あたりの売上 | 広告: 通算利益 / 7日以上続いた最後の配信（期間・倍率）/ その終わり7日の倍率 / いちばん最近の配信')
rows = []
for n, (o, u, gr, dc) in SH.items():
    if n in ('優先配送', 'VIP特典') or o < 30: continue
    rows.append((u / o, n, o, dc / gr * 100, (gr - dc) / o))
for sect, cond in [('■ 止めている商品（夏物を除く）', lambda n: n not in ACTIVE and n not in SUMMER), ('■ 止めている商品（夏物）', lambda n: n not in ACTIVE and n in SUMMER), ('■ 配信中（参考）', lambda n: n in ACTIVE)]:
    print(sect)
    for upo, n, o, dr, ov in sorted(rows, reverse=True):
        if not cond(n): continue
        ai = adinfo(n)
        if ai:
            tp, ta, last, m7, rec = ai
            txt = f'{tp:+,.0f} / {last[0][5:]}〜{last[1][5:]}（{last[2]}日）{last[6]:.2f} / {m7:.2f} / {rec[0][5:]}〜{rec[1][5:]}（{rec[2]}日）広告{rec[3]:,.0f}・{rec[4]}個'
        else: txt = '広告の実績なし（6/29以降）'
        print(f'  {n[:15]} | {o} | {upo:.2f} | {dr:.1f}% | {ov:,.0f} | {txt}')
