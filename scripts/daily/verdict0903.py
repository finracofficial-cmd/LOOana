# -*- coding: utf-8 -*-
"""2026-09-03 が期日だった2件の増額判定 ＋ 非常ブレーキの深掘り。CSV実測のみ（w0902.py 経由）。
   ★9/3の定例が出せず1日遅れたため、判定日は9/3のまま・基準も宣言時のままで執行する。"""
import runpy
g = runpy.run_path('scripts/daily/w0902.py')
S, AD, STORE, IDX = g['S'], g['AD'], g['STORE'], g['IDX']
COST, PRICE, MAP, wd, VARC, VG = g['COST'], g['PRICE'], g['MAP'], g['wd'], g['VARC'], g['VG']
ALLD = sorted(STORE)
GP = {'ナノガラス脱毛パッド': {'白緑': 3980, '黒桃': 3980},
      '壁掛けディスペンサー': {'3本': 6980, '2本': 5980},
      '温感EMSフェイシャルワンド': {'シルバー': 5980, 'ピンク': 5980}}
CG = {n: {grp: VARC[n][i] for i, grp in enumerate(GP[n])} for n in GP}
PBD = g['PRICEBYDATE']; price_on = g['price_on']

def ad(n, dd): return sum(AD[MAP.get(n, n)].get(d, 0) for d in dd)
def sale(n, dd): return sum(S[n][d][0]-S[n][d][1] for d in dd if d in S[n])
def qc(n, dd):
    if n in VARC:
        q = c = 0
        for d in dd:
            for grp, gg in VG[n].get(d, {}).items():
                if not gg: continue
                x = round(gg/GP[n][grp]); q += x; c += x*CG[n][grp]
        return q, c
    q = 0
    for d in dd:
        gd = S[n][d][0] if d in S[n] else 0
        if not gd: continue
        p = price_on(n, d) if n in PBD else PRICE[n]
        x = gd/p; assert abs(x-round(x)) < 1e-6, (n, d, gd, p); q += round(x)
    return q, q*COST[n]
def prof(n, dd):
    q, c = qc(n, dd); return sale(n, dd) - c - ad(n, dd), q

print('■ 判定A 快適マジックインソール 増額判定（27,000 → 30,000）')
print('  宣言済み基準: P2(8/31-9/2)の「1日あたり利益」 ≥ 23,280円（= P1 8/28-29 の1日あたり利益）')
P1 = ['2026-08-28', '2026-08-29']; P2 = ['2026-08-31', '2026-09-01', '2026-09-02']
for lbl, dd in [('P1 8/28-29 (27,000)', P1), ('P2 8/31-9/2 (30,000)', P2)]:
    p, q = prof('快適マジックインソール', dd)
    print(f'  {lbl:<24} 実売 {sale("快適マジックインソール",dd):>8,} / {q:>3}点 / 広告 {ad("快適マジックインソール",dd):>8,.0f}'
          f' → 利益 {p:>+9,.0f} ／ **1日あたり {p/len(dd):>+9,.0f}円**')
p2, _ = prof('快適マジックインソール', P2); d2 = p2/len(P2)
print(f'  → {"✅ 合格・30,000で据え置き" if d2 >= 23280 else "❌ 不合格"}（{d2:,.0f} vs 基準 23,280）')
print('  日別:')
for d in P1 + ['2026-08-30'] + P2:
    p, q = prof('快適マジックインソール', [d])
    mk = '  ←変更当日(両窓から除外)' if d == '2026-08-30' else ''
    print(f'    {d[5:]}({wd(d)}) {q:>3}点 / 広告 {ad("快適マジックインソール",[d]):>7,.0f} / 利益 {p:>+9,.0f}{mk}')

print('\n■ 判定B バランスケアスリッパ 増額判定（10,000 → 12,000、8/30実施）')
print('  宣言済み基準: 増額後の「1日あたり利益」 ≥ 増額前(8/23-29)の7日平均')
BEF = [d for d in ALLD if '2026-08-23' <= d <= '2026-08-29']
AFT = [d for d in ALLD if '2026-08-31' <= d <= '2026-09-02']   # 8/30は変更当日で除外
for lbl, dd in [('増額前 8/23-29 (10,000)', BEF), ('増額後 8/31-9/2 (12,000)', AFT)]:
    p, q = prof('バランスケアスリッパ', dd)
    print(f'  {lbl:<26} 実売 {sale("バランスケアスリッパ",dd):>8,} / {q:>3}点 / 広告 {ad("バランスケアスリッパ",dd):>8,.0f}'
          f' → 利益 {p:>+9,.0f} ／ **1日あたり {p/len(dd):>+9,.0f}円**')
pb, _ = prof('バランスケアスリッパ', BEF); pa, _ = prof('バランスケアスリッパ', AFT)
base = pb/len(BEF); now = pa/len(AFT)
print(f'  → {"✅ 合格・12,000で据え置き" if now >= base else "❌ 不合格・10,000へ戻す"}（{now:,.0f} vs 基準 {base:,.0f}）')

print('\n■ 非常ブレーキの深掘り: 9/02(水) を前週の水曜 8/26 と比べる')
A, B = ['2026-08-26'], ['2026-09-02']
print(f'  全店 実売 {STORE[A[0]]:,} → {STORE[B[0]]:,} ({STORE[B[0]]/STORE[A[0]]-1:+.1%})')
aa = sum(AD[c].get(A[0], 0) for c in AD); bb = sum(AD[c].get(B[0], 0) for c in AD)
print(f'  全店 広告 {aa:,.0f} → {bb:,.0f} ({bb/aa-1:+.1%})   MER {STORE[A[0]]/aa:.2f} → {STORE[B[0]]/bb:.2f}')
rows = []
for n in S:
    if not n: continue
    s1, s2 = sale(n, A), sale(n, B); a1, a2 = ad(n, A), ad(n, B)
    if s1 == 0 and s2 == 0 and a1 == 0 and a2 == 0: continue
    rows.append((s2-s1, n, s1, s2, a1, a2))
rows.sort()
print(f'  {"商品":<24}{"8/26":>10}{"9/02":>10}{"売上差":>11}{"広告8/26":>10}{"広告9/02":>10}{"広告差":>10}')
for d, n, s1, s2, a1, a2 in rows:
    if abs(d) < 10000 and abs(a2-a1) < 5000: continue
    print(f'  {n:<24}{s1:>10,}{s2:>10,}{d:>+11,}{a1:>10,.0f}{a2:>10,.0f}{a2-a1:>+10,.0f}')

print('\n■ 9/03(木) Shopify速報（広告費は09:00 JSTに窓が回ってから確定）')
print('  実売 518,956円 / 注文103 / 販売数118 / 客単価 5,038円 / セッション3,340 / カート追加率5.90%')
print(f'  前週の木曜 8/27 は実売 {STORE["2026-08-27"]:,}円 → 同曜日比 {518956/STORE["2026-08-27"]-1:+.1%}')
