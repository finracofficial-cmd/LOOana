# -*- coding: utf-8 -*-
"""「午前が悪い日は、午後に戻るのか」を実測で答える（予測ではなく基準率）。

   午前 = JST 0:00-12:59 ／ 午後 = JST 13:00-23:59 で各日を2つに割り、
   午前のMERと午後のMERの関係を見る。平均回帰があるなら負の相関が出る。
"""
import csv, collections, datetime, statistics, math

AD = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r in csv.DictReader(open('data/raw/hourly_ad_jst.csv', encoding='utf-8')):
    AD[r['date']][int(r['hour_jst'])] = [int(r['cost']), int(r['clicks'])]
SA = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r in csv.DictReader(open('data/raw/hourly_sales_utc.csv', encoding='utf-8')):
    d, h = r['hour'].split('T')
    u = datetime.datetime.fromisoformat(d) + datetime.timedelta(hours=int(h) + 9)
    SA[u.date().isoformat()][u.hour] = [int(r['gross']), -int(r['disc'])]

WD = ['月','火','水','木','金','土','日']
days = sorted(d for d in AD if len(AD[d]) == 24)
def half(d, rng):
    c = sum(AD[d][h][0] for h in rng); s = sum(SA[d][h][0] - SA[d][h][1] for h in rng)
    return c, s
print(f'午前(0-12時) と 午後(13-23時) を割って比べる  n={len(days)}日')
print(f'{"日付":11} {"曜":3} {"午前MER":>8} {"午後MER":>8} {"午後/午前":>9} {"終日MER":>8}')
am, pm, ratio = [], [], []
for d in days:
    ca, sa = half(d, range(13)); cp, sp = half(d, range(13, 24))
    ma, mp = sa/ca, sp/cp
    am.append(ma); pm.append(mp); ratio.append(mp/ma)
    print(f'{d:11} {WD[datetime.date.fromisoformat(d).weekday()]:3} {ma:>8.2f} {mp:>8.2f} {mp/ma:>9.2f} {(sa+sp)/(ca+cp):>8.2f}')
mx, my = statistics.mean(am), statistics.mean(pm)
sxy = sum((a-mx)*(b-my) for a, b in zip(am, pm)); sxx = sum((a-mx)**2 for a in am); syy = sum((b-my)**2 for b in pm)
r = sxy/math.sqrt(sxx*syy)
print(f'\n【午前MER と 午後MER の相関】 r = {r:+.2f}（n={len(days)}）')
print(f'  午前 平均 {mx:.2f} ／ 午後 平均 {my:.2f}  → 午後は午前の {my/mx:.2f}倍が平常')
print(f'  午後/午前 の比: 平均 {statistics.mean(ratio):.2f} / SD {statistics.pstdev(ratio):.2f} / '
      f'範囲 {min(ratio):.2f}〜{max(ratio):.2f}')
med = statistics.median(am)
low = [(d, a, p) for d, a, p in zip(days, am, pm) if a < med]
hi  = [(d, a, p) for d, a, p in zip(days, am, pm) if a >= med]
print(f'\n【午前が弱かった日（中央値{med:.2f}未満・{len(low)}日）だけ取り出す】')
print(f'  その日の午後MER 平均 {statistics.mean([p for _,_,p in low]):.2f}'
      f'  ／ 午前が強かった日({len(hi)}日)の午後MER 平均 {statistics.mean([p for _,_,p in hi]):.2f}')
print(f'  午後/午前 の比: 弱い日 {statistics.mean([p/a for _,a,p in low]):.2f}倍'
      f'  ／ 強い日 {statistics.mean([p/a for _,a,p in hi]):.2f}倍')
if statistics.mean([p/a for _,a,p in low]) > statistics.mean([p/a for _,a,p in hi]):
    print('  → **午前が弱い日ほど午後に戻る（平均回帰がある）**')
else:
    print('  → 午前が弱い日は午後も弱い（回帰しない）')
for d, a, p in sorted(low, key=lambda x: x[1]):
    print(f'    {d}({WD[datetime.date.fromisoformat(d).weekday()]}) 午前{a:.2f} → 午後{p:.2f}  ({p/a:+.0%}相当 {p/a:.2f}倍)')
print(f'\n【今日 8/31 の午前MER 1.41 を当てはめると】')
lo = statistics.mean([p/a for _,a,p in low]); sd = statistics.pstdev([p/a for _,a,p in low])
print(f'  午前が弱い日の「午後/午前」は 平均{lo:.2f}倍・SD{sd:.2f}')
print(f'  → 午後MERの中心は 1.41×{lo:.2f} = {1.41*lo:.2f}、幅は {1.41*(lo-sd):.2f}〜{1.41*(lo+sd):.2f}')
print('  ※これは「過去の弱い日がどうなったか」の基準率であって、今日の予測ではない')
