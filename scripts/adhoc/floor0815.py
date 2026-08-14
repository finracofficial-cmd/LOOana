# -*- coding: utf-8 -*-
"""赤字までの距離を確定させる。全店の実効分岐MER（手数料込み）と、そこまでの余白。
手数料は実効ブレンド率 3.452%（2026-08-01 実測）を全店サマリーにのみ適用する。
"""
import csv, collections, datetime, io, runpy, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path('/home/user/LOOana/scripts/adhoc/day0815.py')
S, AD, COST, PRICE, STORE = ns['S'], ns['AD'], ns['COST'], ns['PRICE'], ns['STORE']
FEE = 0.03452
ALL = sorted(STORE)

def dayfig(d):
    q = {n: round(v[d][0] / PRICE[n]) for n, v in S.items()
         if n in PRICE and d in v and v[d][0]}
    cst = sum(q[n] * COST[n] for n in q)
    c = sum(AD[cp].get(d, 0) for cp in AD)
    net = STORE[d]
    return net, cst, c, net - cst - c

print('■ 全店の実効分岐MER（手数料3.452%を入れた本当の赤字ライン）')
print(f"{'日付':<12}{'曜':<3}{'実売':>10}{'原価率':>7}{'MER':>6}{'実効分岐':>9}{'余裕':>7}"
      f"{'手数料後利益':>12}{'赤字まで':>9}")
WD = '月火水木金土日'
for d in ALL[-10:]:
    net, cst, c, prof = dayfig(d)
    r = cst / net
    br_eff = 1 / (1 - r - FEE)              # 手数料込みの分岐MER
    mer = net / c
    after = prof - net * FEE
    # 広告費を据え置いたまま、売上が何%落ちると手数料後がゼロになるか
    room = (c * br_eff) / net - 1
    w = WD[datetime.date(*map(int, d.split('-'))).weekday()]
    print(f"{d:<12}{w:<3}{net:>10,}{r:>7.1%}{mer:>6.2f}{br_eff:>9.2f}{mer-br_eff:>+7.2f}"
          f"{after:>+12,.0f}{room:>+9.1%}")

print('\n■ この47日で、全店MERが実効分岐を割った日はあるか')
bad = []
for d in ALL:
    net, cst, c, prof = dayfig(d)
    if not c or not net: continue
    br_eff = 1 / (1 - cst / net - FEE)
    if net / c < br_eff: bad.append((d, net / c, br_eff, prof - net * FEE))
print(f"  対象 {len(ALL)}日中、赤字だった日 = {len(bad)}日")
for d, m, b, a in bad: print(f"    {d}  MER {m:.2f} < 実効分岐 {b:.2f}  手数料後 {a:+,.0f}")
mins = sorted(((dayfig(d)[0] / dayfig(d)[2], d) for d in ALL if dayfig(d)[2]), key=lambda x: x[0])[:3]
print(f"  最低MERの3日: " + " / ".join(f"{d} {m:.2f}" for m, d in mins))

print('\n■ 最悪ケースの上限（在庫を持たないビジネスなので、上限が計算できる）')
BUD = 0
for r in csv.DictReader(open('/home/user/LOOana/data/budget-snapshots.csv', encoding='utf-8')):
    if r['snapshot_date'] == '2026-08-15': BUD += int(r['daily_budget'])
print(f"  記録済みの日予算合計（8/15スナップショット分）: {BUD:,}円/日")
print(f"  1日に失いうる最大額 = その日の広告費だけ。在庫も固定費も無いので、これ以上は増えない。")
print(f"  原価は「売れた分だけ」かかる。売れなければ原価も発生しない。")

net, cst, c, prof = dayfig(ALL[-1])
print(f"\n■ もし 8/14（直近で一番悪い日）が7日続いたら")
print(f"  1日 手数料後 {prof - net*FEE:+,.0f}円 × 7日 = 週 {(prof - net*FEE)*7:+,.0f}円")

print('\n■ 安全弁（これを下回ったら手を動かす、という線）')
net, cst, c, prof = dayfig(ALL[-1])
br_eff = 1 / (1 - cst / net - FEE)
print(f"  現在の実効分岐MER = {br_eff:.2f}（8/14の原価率 {cst/net:.1%} ベース）")
print(f"  ① 全店MERが {br_eff:.2f} を 2日連続で下回ったら → その時点で赤字の商品を一律 −25%")
print(f"  ② 全店MERが単日で 1.20 を下回ったら → その日の赤字商品を即停止")
print(f"  現在 {net/c:.2f}。①まで {net/c - br_eff:+.2f}、②まで {net/c - 1.20:+.2f} の余白。")
