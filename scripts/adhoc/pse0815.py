# -*- coding: utf-8 -*-
"""害虫ブロッカー（コンセント直挿し）と保温プレートを非公開にした影響を実測で出す。

2026-08-15 に Shopify で両商品を DRAFT に変更（当方で status を確認済み）。
PSEマークが日本向けに取れていない＝コンセントに挿す商品は販売できないため。

売上・値引 = data/daily/daily_sales.csv（実測）
広告費     = data/daily/daily_ad.csv（Meta実測）
"""
import csv, collections, runpy

COST = {'害虫ブロッカー': 867}
PRICE = {'害虫ブロッカー': 3980}
D14 = [f'2026-08-{i:02d}' for i in range(1, 15)]
JUL = [f'2026-07-{i:02d}' for i in range(1, 32)]

S = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv', encoding='utf-8')):
    S[r['name']][r['date']][0] += int(r['gross']); S[r['name']][r['date']][1] += int(r['disc'])
AD = collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv', encoding='utf-8')):
    AD[r['campaign']][r['date']] += float(r['cost'])

def blk(days, label, orders=None):
    n = '害虫ブロッカー'
    g = sum(S[n][d][0] for d in days if d in S[n])
    dc = sum(S[n][d][1] for d in days if d in S[n])
    c = sum(AD[n].get(d, 0) for d in days)
    q = round(g / PRICE[n]); cost = q * COST[n]; net = g - dc
    prof = net - cost - c
    nd = len(days)
    print(f"\n  【{label}】{nd}日")
    print(f"    実売(gross−値引) {net:>11,}円   販売数 {q:>5}個")
    print(f"    原価             {cost:>11,}円   広告費 {c:>11,.0f}円")
    print(f"    利益             {prof:>+11,.0f}円   MER {net/c:>5.2f}（分岐 {1/(1-cost/g):.2f}）")
    print(f"    1日あたり        利益 {prof/nd:>+9,.0f}円 / 広告費 {c/nd:>9,.0f}円")
    if orders:
        print(f"    CPA(注文) {c/orders:>8,.0f}円   粗利/注文 {(g-cost)/orders:>8,.0f}円"
              f"   倍率 {(g-cost)/orders/(c/orders):.2f}")
    return prof/nd, c/nd

print('■ 害虫ブロッカー ── 止めたことで何が変わるか（Shopify・Meta実測）')
p14, c14 = blk(D14, '2026-08-01〜08-14', orders=195)
blk(JUL, '2026-07 全月')

g = runpy.run_path('scripts/daily/d0815.py')
STORE_PROF_DAY = (sum(g['N7'].values()) - sum(g['K7'].values()) - g['ACCT'](g['D7'])) / 7
print(f"\n■ 全店への影響")
print(f"  全店の1日あたり利益（8/08-14実測）      {STORE_PROF_DAY:>10,.0f}円")
print(f"  害虫ブロッカーの1日あたり利益（8/01-14） {p14:>+10,.0f}円   全店の {p14/STORE_PROF_DAY:.1%}")
print(f"  → 明日から1日 {abs(p14):,.0f}円・30日で {abs(p14)*30:,.0f}円 の利益が消える。")
print(f"\n  同時に、1日 {c14:,.0f}円の広告費が空く（30日で {c14*30:,.0f}円）。")
print(f"  これを他の商品に回せば一部は取り返せる。ただし回す先の限界MERで決まる。")

print('\n■ 空いた広告費をどこへ回すか（数字はすべて実測から出す）')

# 8/15時点の設定予算（data/budget-snapshots.csv の最終スナップショット）
BUD = {}
for r in csv.DictReader(open('data/budget-snapshots.csv', encoding='utf-8')):
    if r['snapshot_date'] != '2026-08-15': continue
    BUD[r['campaign']] = BUD.get(r['campaign'], 0) + int(r['daily_budget'])
FREED = BUD.pop('害虫ブロッカー')
print(f"  害虫ブロッカーの設定予算（8/15スナップショット・広告セット2本の合計） {FREED:,}円/日")
print(f"  ※ 実消化は 47,204円/日 だったので、止めれば実際にはこれに近い額が空く。")

COST7 = {'4WAY 取り付けOK 小型瞬間冷却ハンディファン':(4980,1730),'形状記憶日傘':(4980,1309),
 '完全遮光・形状記憶・晴雨兼用・UV日傘':(4980,1309),'接触冷感UVパーカー':(3980,1434),
 '5WAY腰掛けファン':(4980,1848),'偏光・調光サングラス':(3980,893),'接触冷感UVアームカバー':(3980,784),
 'ムダ毛シェーバー':(6980,2798),'完全遮光・接触冷感UVハット':(4980,1411),'W固定スマホ車載ホルダー':(3980,1182),
 '姿勢サポートチェア':(5980,1811),'2WAYシートボックス':(4980,1943),'快適マジックインソール':(3980,677),
 'ナノガラス脱毛パッド':(3980,750),'バランスケアスリッパ':(4980,1304),'ナノバブルシャワーヘッド':(6980,2255)}
SMAP = {'4WAY 取り付けOK 小型瞬間冷却ハンディファン':'4WAY',
        '完全遮光・形状記憶・晴雨兼用・UV日傘':'完全遮光・形状記憶'}
D7 = [f'2026-08-{i:02d}' for i in range(8, 15)]

print(f"\n  各商品の実測（8/08-14）と、+25%増額したときの1日あたり利益の変化")
print(f"  頑健性: 限界MER = 平均MER × 0.6 / 0.7 / 0.8 の3端すべてで符号が同じものだけ採用する")
print(f"  {'商品':<26}{'予算':>8}{'MER':>7}{'粗利率':>8}"
      f"{'×0.6':>8}{'×0.7':>8}{'×0.8':>8}{'+25%':>9}{'日利益':>10}")
take = []
for camp, bud in sorted(BUD.items(), key=lambda x: -x[1]):
    if camp not in COST7: continue
    p_, c_ = COST7[camp]; sn = SMAP.get(camp, camp)
    g = sum(S[sn][d][0] for d in D7 if d in S[sn]); dc = sum(S[sn][d][1] for d in D7 if d in S[sn])
    ad = sum(AD[camp].get(d, 0) for d in D7)
    if not ad or not g: continue
    mer = (g-dc)/ad; gm = 1 - c_/p_
    ends = [mer*k*gm - 1 for k in (0.6, 0.7, 0.8)]
    ok = all(e > 0 for e in ends)
    add = bud*0.25 if ok else 0
    print(f"  {camp[:24]:<26}{bud:>8,}{mer:>7.2f}{gm:>8.1%}"
          f"{ends[0]:>+8.2f}{ends[1]:>+8.2f}{ends[2]:>+8.2f}"
          f"{add:>9,.0f}{ends[1]*add:>+10,.0f}")
    if ok: take.append((camp, add, ends[1]*add))
tot_add = sum(t[1] for t in take); tot_pr = sum(t[2] for t in take)
print(f"\n  3端すべて正だったのは {len(take)}品。+25%ずつ配ると受け皿は 合計 {tot_add:,.0f}円/日")
print(f"    空く予算            {FREED:>12,}円/日")
print(f"    受け皿（+25%の枠）  {tot_add:>12,.0f}円/日")
print(f"    それが生む利益      {tot_pr:>+12,.0f}円/日")
print(f"    害虫が生んでいた利益 {p14:>+12,.0f}円/日")
print(f"    差引                {tot_pr-p14:>+12,.0f}円/日  → 全額を既存に回しても "
      f"{abs(tot_pr-p14):,.0f}円/日 足りない")

print(f"\n  ここが判断どころ。空いた {FREED:,}円/日 の使い道は2つある。")
print(f"    A案 全部を既存商品に +25%   → 利益 {tot_pr:+,.0f}円/日。害虫の {tot_pr/p14:.0%} を回収。")
print(f"                                   ただし9月の受け皿は1つも増えない。")
half = FREED // 2
share = half / tot_add if tot_add else 0
print(f"    B案 半分ずつ                 → 既存に {half:,}円（+{share*25:.0f}%相当）"
      f"・利益 {tot_pr*share:+,.0f}円/日")
print(f"                                   残り {FREED-half:,}円で新商品Phase1を "
      f"{(FREED-half)//5000}品 同時に回せる。")
print(f"\n  9月の崖まで2週間しかないので、B案を推す。")
print(f"    A案とB案の差は {tot_pr-tot_pr*share:,.0f}円/日（30日で {(tot_pr-tot_pr*share)*30:,.0f}円）。")
print(f"    その額で新商品を {(FREED-half)//5000}品スクリーニングできるなら、そちらが安い。")

print('\n■ 9月の絵の描き直し（前回 2026-08-15 の提案からの差分）')
print('  前回: 夏カテゴリの利益 月2,661,006円 が9月に消える、という前提だった。')
print(f"  今回: そのうち害虫ブロッカー分（月 {abs(p14)*30:,.0f}円）が、9月ではなく今日から消える。")
print(f"  残りの夏カテゴリ  月 {2661006-abs(p14)*30:,.0f}円 は、これまでどおり9月に向けて細る。")
print('  つまり穴の総額は変わらないが、2週間早く来た。新商品テストの締切が2週間前倒しになる。')
