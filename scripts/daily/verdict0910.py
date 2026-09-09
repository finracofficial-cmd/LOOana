# -*- coding: utf-8 -*-
"""2026-09-10 快適マジックインソール 再テスト判定。CSV実測のみ（w0908.py 経由）。

宣言済み基準（9/4に設定）: 「27,000へ戻したあとの7日利益 ≥ 27,000時代の7日平均」

★窓の取り方: 30,000への増額は8/30、27,000への復帰日は特定できていない（9/05朝のMeta直読で27,000を確認）。
  そこで 27,000時代 = **8/23-8/29**（増額前の7日）を基準とし、
  復帰後は **7日窓 9/02-9/08**（主窓）と **確実に27,000だった 9/05-9/08**（狭窓）の2通りで測る。
  両方が同じ結論なら採用（スリッパ判定と同じ考え方）。
"""
import runpy
g = runpy.run_path('scripts/daily/w0908.py')
S, AD, STORE, MAP, COST, PRICE = g['S'], g['AD'], g['STORE'], g['MAP'], g['COST'], g['PRICE']
ALLD = sorted(STORE); N = '快適マジックインソール'

def blk(dd):
    s = sum(S[N][d][0]-S[N][d][1] for d in dd if d in S[N])
    a = sum(AD[MAP.get(N, N)].get(d, 0) for d in dd)
    q = sum(round(S[N][d][0]/PRICE[N]) for d in dd if d in S[N])
    c = q*COST[N]
    return s, q, a, c, s-c-a

P1 = [d for d in ALLD if '2026-08-23' <= d <= '2026-08-29']
s, q, a, c, p = blk(P1)
BASE = p
print('■ 基準（宣言済み・27,000時代 8/23-8/29 の7日）')
print(f'  実売{s:>8,} {q:>3}点 広告{a:>8,.0f} 原価{c:>7,} → **7日利益 {p:>+9,.0f}円**（1日あたり {p/7:>+8,.0f}円）')

print('\n■ 判定（27,000へ戻したあと）')
ok = []
for lbl, dd in [('主窓 9/02-9/08（7日）', [d for d in ALLD if '2026-09-02' <= d <= '2026-09-08']),
                ('狭窓 9/05-9/08（27,000を実測確認済み・4日）', [d for d in ALLD if '2026-09-05' <= d <= '2026-09-08'])]:
    s, q, a, c, p = blk(dd)
    per7 = p/len(dd)*7          # 7日換算
    j = per7 >= BASE; ok.append(j)
    print(f'  {lbl}')
    print(f'    実売{s:>8,} {q:>3}点 広告{a:>8,.0f} 原価{c:>7,} → 利益{p:>+9,.0f}円 '
          f'（7日換算 **{per7:>+9,.0f}円**）→ {"✅合格" if j else "❌不合格"}（基準{BASE:,.0f}の{per7/BASE:.0%}）')

print(f'\n  → {"✅ 両窓とも合格 → 27,000で据え置き・実験終了" if all(ok) else ("❌ 両窓とも不合格" if not any(ok) else "⚠️ 窓で結論が割れた → 判定保留")}')

print('\n■ 日別（参考）')
for d in [x for x in ALLD if '2026-08-23' <= x <= '2026-09-08']:
    s2, q2, a2, c2, p2 = blk([d])
    mk = '  ←8/30 増額30,000' if d == '2026-08-30' else ''
    print(f'  {d[5:]}({g["wd"](d)}) 実売{s2:>7,} {q2:>2}点 広告{a2:>7,.0f} → 利益{p2:>+8,.0f}{mk}')

print('\n■ 3窓判定（参考）')
for k in (3, 5, 7):
    i = ALLD.index('2026-09-08'); dd = ALLD[i-k+1:i+1]
    s2, q2, a2, c2, p2 = blk(dd)
    print(f'  {k}日 {dd[0][5:]}-{dd[-1][5:]}: MER{s2/a2:5.2f} 分岐{1/(1-c2/s2):4.2f} 余裕{s2/a2-1/(1-c2/s2):+5.2f} 利益{p2:>+9,.0f}')
