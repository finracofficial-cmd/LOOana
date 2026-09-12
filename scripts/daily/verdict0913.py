# -*- coding: utf-8 -*-
"""2026-09-13 伸縮ガラスクリーナー 増額判定（2つの判定を1本化）。CSV実測のみ（w0911.py 経由）。

宣言①（9/10設定・50点到達時）: 7日MER ≥ 目標MER かつ 週消化率 ≥95% なら +25%
宣言②（9/11設定）: 16,000時代（9/09以降）の1日あたり利益 ≥ 8,000時代（9/07-9/08）の +15,294円
"""
import runpy
g = runpy.run_path('scripts/daily/w0911.py')
S, AD, STORE, MAP, VARC, VG = g['S'], g['AD'], g['STORE'], g['MAP'], g['VARC'], g['VG']
ALLD = sorted(STORE); N = '伸縮ガラスクリーナー'
GP = {'ブルー': 3980, 'グレー': 3980, 'グリーン': 3980, 'レッド': 3980}
CG = {'ブルー': VARC[N][0], 'グレー': VARC[N][1], 'グリーン': VARC[N][2], 'レッド': VARC[N][3]}
BUD = {'2026-09-07': 8000, '2026-09-08': 8000, '2026-09-09': 16000, '2026-09-10': 16000, '2026-09-11': 16000}

def blk(dd):
    s = sum(S[N][d][0]-S[N][d][1] for d in dd if d in S[N])
    a = sum(AD[MAP.get(N, N)].get(d, 0) for d in dd)
    q = c = 0
    for d in dd:
        for grp, gg in VG[N].get(d, {}).items():
            if gg: x = round(gg/GP[grp]); q += x; c += x*CG[grp]
    return s, q, a, c, s-c-a

print('■ 日別')
for d in [x for x in ALLD if x >= '2026-09-07']:
    if d not in S[N]: continue
    s, q, a, c, p = blk([d])
    print(f'  {d[5:]}({g["wd"](d)}) 実売{s:>7,} {q:>2}点 広告{a:>7,.0f} 原価{c:>6,} → 利益{p:>+8,.0f} '
          f'MER{s/a:5.2f} 消化率{a/BUD[d]:>5.0%}')

P1 = ['2026-09-07', '2026-09-08']; P2 = ['2026-09-09', '2026-09-10', '2026-09-11']
s1, q1, a1, c1, p1 = blk(P1); s2, q2, a2, c2, p2 = blk(P2)
print(f'\n■ 判定② 増額の効果（8,000 → 16,000）')
print(f'  基準 8,000時代 9/07-08: 実売{s1:>7,} {q1:>2}点 広告{a1:>7,.0f} → 利益{p1:>+8,.0f} ／ 1日 **{p1/2:>+8,.0f}円**')
print(f'  P2   16,000時代 9/09-11: 実売{s2:>7,} {q2:>2}点 広告{a2:>7,.0f} → 利益{p2:>+8,.0f} ／ 1日 **{p2/3:>+8,.0f}円**')
ok2 = p2/3 >= p1/2
print(f'  → {"✅ 合格" if ok2 else "❌ 不合格"}（{p2/3:,.0f} vs 基準 {p1/2:,.0f} ＝ {p2/3/(p1/2):.0%}）')

print(f'\n■ 判定① 50点到達時の増額条件')
D7 = [d for d in ALLD if d >= '2026-09-05']
s7, q7, a7, c7, p7 = blk(D7)
mer = s7/a7; be = 1/(1-c7/s7); tgt = 1/(1-c7/s7-0.35)
print(f'  7日(9/05-11): 実売{s7:,} {q7}点 広告{a7:,.0f} 原価{c7:,} → 利益{p7:+,.0f}')
print(f'  原価率{c7/s7:.1%} / MER **{mer:.2f}** / 分岐{be:.2f} / 目標**{tgt:.2f}** → {"✅" if mer>=tgt else "❌"} MER ≥ 目標')
act = [d for d in P2]
util = sum(AD[MAP.get(N,N)].get(d,0) for d in act) / sum(BUD[d] for d in act)
print(f'  16,000での消化率（9/09-11の3日）: {util:.0%} → {"✅" if util>=0.95 else "❌"} ≥95%')
print(f'  累計販売数: {sum(round(gg/3980) for d in ALLD if d in VG[N] for gg in VG[N][d].values() if gg)}点')

ok1 = (mer >= tgt) and (util >= 0.95)
print(f'\n  ★総合: 判定①{"✅" if ok1 else "❌"} / 判定②{"✅" if ok2 else "❌"} → '
      f'{"**両方合格 → 16,000 を 20,000 へ（+25%）**" if (ok1 and ok2) else "**据え置き**"}')
