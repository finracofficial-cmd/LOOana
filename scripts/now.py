# -*- coding: utf-8 -*-
"""現時点評価ツール — 「今この瞬間」を、比較できる形で他の日と並べる。

   使い方: python3 scripts/now.py [切り取り時刻(JST・既定=直近の完了時刻)]

   設計の3原則:
     1. **同じ時刻でカットする。** 終日の数字と日中の数字を比べない
     2. **同じ曜日を主基準にする。** 曜日で「午前に前倒しする割合」も消化率も違う（月曜38.5% / 7日平均45.6%）
     3. **配信量で説明できる分を先に引く。** 残差だけが「今日固有の良し悪し」

   出せるもの / 出せないもの:
     ○ 消化・クリック・注文・実売・MER（すべて同時刻カットどうしの比較）
     ○ 「配信量から期待される注文」との差と、そのポアソン確率
     × 着地予測（本ツールは一切出さない）
"""
import csv, sys, math, datetime, statistics, collections

CUT = int(sys.argv[1]) if len(sys.argv) > 1 else None   # この時刻の直前まで（0..CUT-1 を集計）
B = 'data/'

def load_ad():
    o = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for r in csv.DictReader(open(B+'raw/hourly_ad_jst.csv', encoding='utf-8')):
        o[r['date']][int(r['hour_jst'])] = [int(r['cost']), int(r['clicks'])]
    return o

def load_sales():   # UTC で持っているので JST へ寄せる
    o = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for r in csv.DictReader(open(B+'raw/hourly_sales_utc.csv', encoding='utf-8')):
        d, h = r['hour'].split('T'); u = datetime.datetime.fromisoformat(d) + datetime.timedelta(hours=int(h)+9)
        o[u.date().isoformat()][u.hour] = [int(r['gross']), -int(r['disc'])]
    return o

def daily(path, key, cols):
    o = collections.defaultdict(lambda: [0]*len(cols))
    for r in csv.DictReader(open(path, encoding='utf-8')):
        for i, c in enumerate(cols): o[r[key]][i] += int(r[c])
    return o

AD, SA = load_ad(), load_sales()
DAD = daily(B+'daily/daily_ad.csv', 'date', ['cost'])
DSA = daily(B+'daily/daily_sales.csv', 'date', ['gross', 'disc'])
ORD = {  # 同時刻カットの注文数
 17: {'2026-08-17':69,'2026-08-18':60,'2026-08-19':73,'2026-08-20':69,'2026-08-21':78,'2026-08-22':73,
      '2026-08-23':71,'2026-08-24':68,'2026-08-25':53,'2026-08-26':65,'2026-08-27':80,'2026-08-28':49,
      '2026-08-29':77,'2026-08-30':68,'2026-08-31':50},
 15: {'2026-08-17':61,'2026-08-18':50,'2026-08-19':68,'2026-08-20':62,'2026-08-21':72,'2026-08-22':64,
      '2026-08-23':62,'2026-08-24':62,'2026-08-25':44,'2026-08-26':59,'2026-08-27':71,'2026-08-28':44,
      '2026-08-29':72,'2026-08-30':60,'2026-08-31':42},   # Shopify ordersCount = EXACT。切り取り時刻ごとに持つ
 13: {'2026-08-17':49,'2026-08-18':35,'2026-08-19':63,'2026-08-20':52,'2026-08-21':61,'2026-08-22':46,
      '2026-08-23':55,'2026-08-24':50,'2026-08-25':39,'2026-08-26':50,'2026-08-27':59,'2026-08-28':37,
      '2026-08-29':59,'2026-08-30':52,'2026-08-31':30},
 12: {'2026-08-17':42,'2026-08-18':31,'2026-08-19':55,'2026-08-20':45,'2026-08-21':48,'2026-08-22':44,
      '2026-08-23':45,'2026-08-24':41,'2026-08-25':36,'2026-08-26':44,'2026-08-27':51,'2026-08-28':33,
      '2026-08-29':52,'2026-08-30':48,'2026-08-31':29}}
GM = 0.7306   # 粗利率【近似・直近7日実測】

today = max(AD)
if CUT is None: CUT = max(h for h in AD[today] if AD[today][h][0] > 0)   # 最後に消化のあった時間
assert CUT in ORD, f'切り取り時刻 {CUT} の注文数が未取得。ordersCount を取ってから実行する'
WD = ['月','火','水','木','金','土','日']
wd = lambda d: WD[datetime.date.fromisoformat(d).weekday()]

def cut(d):
    c = sum(AD[d][h][0] for h in range(CUT)); k = sum(AD[d][h][1] for h in range(CUT))
    s = sum(SA[d][h][0]-SA[d][h][1] for h in range(CUT))
    return c, k, s, ORD[CUT].get(d)

days = sorted(d for d in AD if d in ORD[CUT] and len(AD[d]) >= CUT)
past = [d for d in days if d != today and d in DAD]

print(f'=== 現時点評価  {today}({wd(today)}) JST {CUT}:00 時点 ===')
print(f'    切り取り: 0:00〜{CUT-1}:59 の累計。すべて同じ時刻でそろえてある\n')

# ---- ① まず「この断面が終日を当てられるのか」を検証する ----
print('① 検証: 断面のMERは終日のMERを当てられるか（8/17-8/30 の14日）')
xs, ys = [], []
for d in past:
    c, k, s, o = cut(d)
    fs = DSA[d][0]-DSA[d][1]; fc = DAD[d][0]
    if c and fc: xs.append(s/c); ys.append(fs/fc)
mx, my = statistics.mean(xs), statistics.mean(ys)
sxy = sum((a-mx)*(b-my) for a, b in zip(xs, ys)); sxx = sum((a-mx)**2 for a in xs); syy = sum((b-my)**2 for b in ys)
r = sxy/math.sqrt(sxx*syy)
ratio = [b/a for a, b in zip(xs, ys)]
print(f'   相関 r = {r:+.2f}（n={len(xs)}）')
print(f'   終日MER ÷ 断面MER = 平均 {statistics.mean(ratio):.3f} / SD {statistics.pstdev(ratio):.3f}'
      f' → 断面から終日へは平均 {statistics.mean(ratio)-1:+.1%} 動き、そのブレは ±{statistics.pstdev(ratio):.1%}')
print(f'   ★r={r:+.2f} なので' + ('**断面は終日をほぼ当てられない。順位の目安としてのみ読む**' if abs(r) < 0.5
      else '断面はある程度終日を予測する') + '\n')

# ---- ② 同時刻カットの実数を並べる ----
print(f'② 同時刻({CUT}:00)カットの実数')
print(f'{"日付":11} {"曜":3} {"消化":>9} {"クリック":>7} {"注文":>5} {"実売":>10} {"MER":>6} {"注文/CL":>8}')
rec = {}
for d in days:
    c, k, s, o = cut(d)
    rec[d] = (c, k, s, o)
    mark = '  ← 今' if d == today else ''
    print(f'{d:11} {wd(d):3} {c:>9,} {k:>7,} {o:>5} {s:>10,} {s/c:>6.2f} {o/k:>8.2%}{mark}')

# ---- ③ 配信量で説明できる分を引く ----
c0, k0, s0, o0 = rec[today]
same = [d for d in past if wd(d) == wd(today)]
allp = past
print(f'\n③ 「配信量から期待される注文」との差（＝今日固有の良し悪し）')
for lbl, base in [(f'同じ{wd(today)}曜 (n={len(same)})', same), (f'直近{len(allp)}日 全曜日', allp)]:
    if not base: continue
    cvr = sum(rec[d][3] for d in base) / sum(rec[d][1] for d in base)
    rpc = sum(rec[d][2] for d in base) / sum(rec[d][1] for d in base)
    eo = k0*cvr; es = k0*rpc
    z = (o0-eo)/math.sqrt(eo)
    p = sum(math.exp(-eo)*eo**x/math.factorial(x) for x in range(0, o0+1))
    p = min(p, 1-p)*2   # 両側
    print(f'  【{lbl}】基準CVR {cvr:.2%} / 基準 売上perクリック {rpc:,.0f}円')
    print(f'    期待注文 {eo:5.1f} 件 vs 実績 {o0} 件 → z = {z:+.2f} / 両側P = {p:.0%}'
          f'  {"平常" if abs(z) < 2 else "⚠️ 要確認"}')
    print(f'    期待実売 {es:9,.0f}円 vs 実績 {s0:,}円 → {s0/es-1:+.1%}')
# ---- ④ 上流（配信量そのもの）が同曜日基準からどれだけズレているか ----
if same:
    print(f'\n④ 上流の配信量（同じ{wd(today)}曜 平均との比）  ※n={len(same)}なのでzは出さない（標本が小さすぎる）')
    for lbl, i in [('消化', 0), ('クリック', 1)]:
        b = statistics.mean([rec[d][i] for d in same])
        print(f'  {lbl:6} 今日 {rec[today][i]:>9,} / 基準 {b:>9,.0f} = {rec[today][i]/b:>6.0%}')

# ---- ⑤ 断面MERそのものを14日の分布に置く（これが「今の総合点」）----
BE = 1/GM
mers = [rec[d][2]/rec[d][0] for d in allp]
m, sd = statistics.mean(mers), statistics.pstdev(mers)
t = rec[today][2]/rec[today][0]
below = sum(1 for x in mers if x <= t)
print(f'\n⑤ 断面MER を直近{len(allp)}日の分布に置く（総合点）')
print(f'  今日 {t:.2f} / 平均 {m:.2f} / SD {sd:.2f} → z = {(t-m)/sd:+.2f}')
print(f'  {len(allp)}日中 {below}日 が今日以下  = ' + ('**観測範囲で最低**' if below == 0 else f'約{len(allp)/below:.0f}日に1回'))
print(f'  分岐MER {BE:.2f}（粗利率{GM:.1%}）に対する余裕 {t-BE:+.2f}'
      + ('  🚨 分岐割れ' if t < BE else '  ⚠️ 分岐すれすれ' if t-BE < 0.20 else ''))
print(f'  ★①の検証より、ここから終日までに平均{statistics.mean(ratio)-1:+.1%}・ブレ±{statistics.pstdev(ratio):.0%}動く'
      f' → 終日の見込み幅は {t*(statistics.mean(ratio)-statistics.pstdev(ratio)):.2f}〜{t*(statistics.mean(ratio)+statistics.pstdev(ratio)):.2f}'
      '（幅であって予測ではない）')
print('\n※ 着地予測は出さない。ここに出るのは「同時刻どうしで比べた現在地」だけ')
