# -*- coding: utf-8 -*-
"""2026-08-31: 当月(8/01-8/28)の daily_ad.csv を data_query の実測で置き換える。

背景: 日次書き込み時に小数点以下を切り捨てていたため、CSVは実測より一貫して過少だった
（8/01-8/28 の累計 −5,083円 / −0.047%）。広告費が過少＝利益が過大に出る方向。
1日あたり −169円で判定にも予算にも影響しない水準だが、`data_query` が復活して
実測をそのまま書けるようになったので、当月分はズレそのものを消す。
（8/29・8/30 は append0830_ad.py で既に実測。7月以前は遡及修正しない＝当時の判断の記録を保つ）
"""
import csv, collections

TRUE = collections.defaultdict(dict)
for r in csv.reader(open('data/raw/meta_daily_campaign_20260801_20260828.csv', encoding='utf-8')):
    if r: TRUE[r[0]][r[1]] = int(r[2])
DAYS = sorted(TRUE); assert DAYS[0] == '2026-08-01' and DAYS[-1] == '2026-08-28' and len(DAYS) == 28

ACCT = {'2026-08-01':560465,'2026-08-02':575073,'2026-08-03':491867,'2026-08-04':548564,'2026-08-05':476554,
'2026-08-06':441813,'2026-08-07':396600,'2026-08-08':454055,'2026-08-09':472558,'2026-08-10':395874,
'2026-08-11':439426,'2026-08-12':362195,'2026-08-13':363096,'2026-08-14':363592,'2026-08-15':364677,
'2026-08-16':382670,'2026-08-17':276324,'2026-08-18':303447,'2026-08-19':284380,'2026-08-20':304814,
'2026-08-21':284616,'2026-08-22':256336,'2026-08-23':273264,'2026-08-24':256966,'2026-08-25':258054,
'2026-08-26':231544,'2026-08-27':283498,'2026-08-28':245336}
for d in DAYS:   # 検算1: 日ごとに Σキャンペーン = アカウントレベル（別クエリの実測）
    assert sum(TRUE[d].values()) == ACCT[d], (d, sum(TRUE[d].values()), ACCT[d])
print(f'検算1 Σキャンペーン = アカウントレベル: 28日すべて差0円 ✓')

P = 'data/daily/daily_ad.csv'
rows = list(csv.reader(open(P, encoding='utf-8')))
head, body = rows[0], [r for r in rows[1:] if r]
old = {d: sum(int(r[2]) for r in body if r[0] == d) for d in DAYS}
oldcp = {(r[0], r[1]) for r in body if r[0] in TRUE and int(r[2]) > 0}   # 消化0の行は比較対象外
newcp = {(d, c) for d in TRUE for c in TRUE[d]}
assert oldcp == newcp, ('キャンペーン×日の集合が違う', sorted(oldcp ^ newcp)[:10])
print(f'検算2 消化>0 のキャンペーン×日の集合が一致（{len(newcp)}行）✓ 取りこぼしも重複もない')
print('      ※CSVにあった消化0の行（8/24 4WAY）は落とす。実測に0行は存在しない')

body = [r for r in body if r[0] not in TRUE] + [[d, c, v] for d in DAYS for c, v in TRUE[d].items()]
body.sort(key=lambda r: (r[0], r[1]))
with open(P, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f); w.writerow(head); w.writerows(body)
to = sum(old.values()); tn = sum(ACCT.values())
print(f'検算3 8/01-8/28 合計: {to:,} → {tn:,} 円（{tn-to:+,} / {(tn-to)/to*100:+.3f}%）')
print(f'      1日あたり {(tn-to)/28:+,.0f}円。利益はこの分だけ下方修正される（実態に一致する方向）')
