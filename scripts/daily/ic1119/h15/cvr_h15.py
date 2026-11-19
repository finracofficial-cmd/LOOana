# 11/19 15時台: 今日の買う率（購入÷来訪）が戻ったかを、時間帯別と「同じ時刻で切った過去21日」で見る。入力は raw.txt だけ
import math, os
D = os.path.dirname(os.path.abspath(__file__)); T = {}; B = {}; C = {}
for l in open(os.path.join(D, 'raw.txt')):
    p = l.strip().split(',')
    if p[0] == 'T': T[int(p[1])] = list(map(int, p[2:]))
    elif p[0] == 'B': B[p[1]] = list(map(int, p[2:]))
    elif p[0] == 'C': C[p[1]] = list(map(int, p[2:]))
TODAY = '2026-11-19'
def ple(k, lam): return sum(math.exp(-lam + i * math.log(lam) - math.lgamma(i + 1)) for i in range(0, k + 1))
def pge(k, lam): return 1 - ple(k - 1, lam) if k > 0 else 1.0
out = []
def blk(hs): s = [sum(T[h][i] for h in hs) for i in range(4)]; return s
out.append('■ 今日の時間帯別（来訪・カート追加・決済画面・購入 ｜ カート率・買う率）')
for name, hs in (('0〜9時台', range(0, 10)), ('10〜13時台', range(10, 14)), ('14時台', [14]), ('15時台（途中）', [15]), ('14時台〜今', [14, 15])):
    s = blk(hs); out.append(f'  {name}: {s[0]}・{s[1]}・{s[2]}・{s[3]} ｜ {s[1]/s[0]*100:.1f}%・{s[3]/s[0]*100:.2f}%')
def past(X):
    k = [d for d in X if d != TODAY]; S = sum(X[d][0] for d in k); return k, S, sum(X[d][1] for d in k) / S, sum(X[d][3] for d in k) / S
k, S, cart_r, cvr_r = past(C)
out.append(f'■ 0〜14時台で切った過去{len(k)}日: カート率 {cart_r*100:.2f}%・買う率 {cvr_r*100:.2f}%')
t = C[TODAY]; r = sorted(X[3] / X[0] for X in C.values()); pos = sorted(C, key=lambda d: C[d][3] / C[d][0]).index(TODAY) + 1
exp = t[0] * cvr_r
out.append(f'  今日 0〜14時台: 来訪 {t[0]}・購入 {t[3]}・買う率 {t[3]/t[0]*100:.2f}%（22日のうち低い方から {pos} 番目・最小 {r[0]*100:.2f}%〜最大 {r[-1]*100:.2f}%）')
out.append(f'  ふだんの買う率なら購入は {exp:.1f} 件の見込み → 実際 {t[3]} 件。これ以下になる確率 {ple(t[3], exp)*100:.0f}%')
out.append(f'  購入の件数: 今日 {t[3]} ｜過去21日の同じ時刻まで 最小 {min(C[d][3] for d in k)}〜最大 {max(C[d][3] for d in k)}')
k2, S2, cart2, cvr2 = past(B); b = B[TODAY]; e2 = b[0] * cvr2
out.append(f'■ 13〜14時台だけ: 今日 来訪 {b[0]}・購入 {b[3]}（{b[3]/b[0]*100:.2f}%）｜過去21日 {cvr2*100:.2f}% → 見込み {e2:.1f} 件。{b[3]} 件以下の確率 {ple(b[3], e2)*100:.0f}%')
s = blk([14, 15]); e3 = s[0] * cvr_r; e4 = s[0] * cart_r
out.append(f'■ 14時台〜今（{s[0]} 来訪）: 購入 {s[3]}（見込み {e3:.1f}・{s[3]} 件以上の確率 {pge(s[3], e3)*100:.0f}%）・カート追加 {s[1]}（見込み {e4:.1f}・{s[1]} 件以上の確率 {pge(s[1], e4)*100:.0f}%）')
s = blk(range(10, 14)); e5 = s[0] * cvr_r
out.append(f'■ 10〜13時台（{s[0]} 来訪）: 購入 {s[3]}（見込み {e5:.1f}・{s[3]} 件以下の確率 {ple(s[3], e5)*100:.1f}%）')
open(os.path.join(D, 'cvr_h15.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
