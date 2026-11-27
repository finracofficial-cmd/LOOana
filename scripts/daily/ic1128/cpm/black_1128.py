# -*- coding: utf-8 -*-
"""11/28 07時台「とにかく全商品毎日黒字がいいな」の数字。
① 店全体: 赤字の日（粗利 < 広告費）の数
② 商品ごと（直近30日 10/29〜11/27・広告費が出た日だけ）: 赤字の日の数・30日の倍率と利益・1日の個数／偶然だけで出る赤字の日の見込み（個数を Poisson とみた目安）
③ 「1日の個数」と「平均の倍率」ごとの、偶然だけで赤字になる日の割合
④ LOOTY のアカウントの最初の月（2025/12/15〜2026/3）の CPM（去年の年末と比べられるかの確認）
入力: w1127.py（data/daily/*.csv）・acct_daily_20251001_20260331_raw.json"""
import io, contextlib, json, os, math, collections
D0 = os.path.dirname(os.path.abspath(__file__)) + '/'; os.chdir(D0 + '../../../..')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1127.py').read(), g)
A, ALLD, agg, WIN, ACCT = g['A'], g['ALLD'], g['agg'], g['WIN'], g['ACCT']
out = []
def P(s=''): print(s); out.append(s)
ple = lambda k, l: sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1)) if k >= 0 else 0.0
def day(d):
    k = 'b' + d; WIN[k] = [d]; N, DC, Q, K = agg([d], k); return N, Q, K
DAYS = [d for d in ALLD if d >= '2026-07-17']; DD = {d: day(d) for d in DAYS}
# ---- ① ----
P('■ ① 店全体の赤字の日（粗利 < 広告費）')
prof = {d: sum(DD[d][0].values()) - sum(DD[d][2].values()) - ACCT([d]) for d in DAYS}
for lab, ds in (('直近30日（10/29〜11/27）', DAYS[-30:]), ('直近60日', DAYS[-60:]), (f'7/17〜11/27（{len(DAYS)}日）', DAYS)):
    red = [d for d in ds if prof[d] < 0]; lo = min(ds, key=lambda d: prof[d])
    P(f"  {lab}: 赤字の日 {len(red)}日・いちばん低い日 {lo[5:]} {prof[lo]:+,.0f}円・平均 {sum(prof[d] for d in ds)/len(ds):,.0f}円/日" + (f"（赤字の日: {'・'.join(x[5:] for x in red)}）" if red else ''))
# ---- ② ----
D30 = DAYS[-30:]; assert D30[0] == '2026-10-29'
ST = collections.defaultdict(lambda: dict(n=0, red=0, loss=0, gp=0, ad=0, q=0, last=''))
for d in D30:
    N, Q, K = DD[d]
    for n in {x for x in set(N) | set(g['MAP']) if A([d], x)}:
        gp = N.get(n, 0) - K.get(n, 0); ad = A([d], n); s = ST[n]; s['n'] += 1; s['gp'] += gp; s['ad'] += ad; s['q'] += Q.get(n, 0); s['last'] = d
        if gp < ad: s['red'] += 1; s['loss'] += gp - ad
P('■ ② 商品ごと（直近30日・広告費が出た日だけ数える）: 広告を出した日数｜赤字の日｜30日の倍率・利益｜1日の個数・広告費｜偶然だけで出る赤字の日の見込み')
tr = tn = 0; te = 0.0
for n, s in sorted(ST.items(), key=lambda x: -x[1]['ad']):
    lam = s['q'] / s['n']; gpu = s['gp'] / s['q'] if s['q'] else 0; u0 = (s['ad'] / s['n']) / gpu if gpu else 0
    pr = ple(math.ceil(u0 - 1e-9) - 1, lam) if lam and gpu else 1.0; live = '配信中' if s['last'] == '2026-11-27' and n != '伸縮ワックス洗車ブラシ' else '停止'
    tr += s['red']; tn += s['n']; te += pr * s['n']
    P(f"  {n}（{live}）: {s['n']}日｜赤字 {s['red']}日（{s['red']/s['n']:.0%}・その日の合計 {s['loss']:+,.0f}）｜倍率 {s['gp']/s['ad']:.2f}・利益 {s['gp']-s['ad']:+,.0f}｜{lam:.1f}個/日・{s['ad']/s['n']:,.0f}円/日｜見込み {pr*s['n']:.1f}日（{pr:.0%}）")
P(f"  合計: 商品×日 {tn}のうち赤字 {tr}（{tr/tn:.0%}）・偶然だけの見込み {te:.0f}（{te/tn:.0%}）")
allblack = [d for d in D30 if all((DD[d][0].get(n, 0) - DD[d][2].get(n, 0)) >= A([d], n) for n in {x for x in set(DD[d][0]) | set(g['MAP']) if A([d], x)})]
cnt = {d: sum(1 for n in {x for x in set(DD[d][0]) | set(g['MAP']) if A([d], x)} if (DD[d][0].get(n, 0) - DD[d][2].get(n, 0)) < A([d], n)) for d in D30}
P(f"  広告を出した商品が全部黒字だった日: 30日のうち {len(allblack)}日｜1日あたりの赤字の商品の数: 最小 {min(cnt.values())}・最大 {max(cnt.values())}・平均 {sum(cnt.values())/30:.1f}本（出している商品は 1日 {tn/30:.1f}本）")
big = [(n, s) for n, s in ST.items() if (s['gp'] - s['ad']) >= 100000]
P('  30日の利益が 10万円以上の商品でも: ' + '・'.join(f"{n} 赤字 {s['red']}/{s['n']}日" for n, s in sorted(big, key=lambda x: -(x[1]['gp'] - x[1]['ad']))))
# ---- ③ ----
P('■ ③ 偶然だけで「その日が赤字」になる割合（1日の個数が平均 u 個・平均の倍率が m のとき、個数が u÷m 個より少ない日の割合。まとめ買いがあるので実際はこれより少し多い）')
P('  平均の倍率 →   ' + '   '.join(f'{m:.2f}' for m in (1.25, 1.5, 2.0, 2.5, 3.0)))
for u in (3, 5, 10, 20, 40):
    P(f"  1日 {u:>2}個:     " + '   '.join(f"{ple(math.ceil(u/m - 1e-9) - 1, u):>4.0%}" for m in (1.25, 1.5, 2.0, 2.5, 3.0)))
# ---- ④ ----
rows = [l.strip().split(',') for l in json.load(open(D0 + 'acct_daily_20251001_20260331_raw.json'))['data']['data'].split('\n')[1:] if l.strip()]
M = collections.defaultdict(lambda: [0, 0, 0, 0])
for d, c, i, k in rows:
    m = M[d[:7]]; m[0] += int(c); m[1] += int(i); m[2] += 0 if k == 'null' else int(k); m[3] += 1 if int(c) > 0 else 0
P(f"■ ④ LOOTY のアカウントの最初のころ（2025/10/1〜2026/3/31 を取得。最初の広告費は {rows[0][0]}）")
for k, v in sorted(M.items()): P(f"  {k}: 広告費が出た {v[3]}日・{v[0]/max(v[3],1):,.0f}円/日・CPM {v[0]/v[1]*1000:,.0f}・クリック率 {v[2]/v[1]:.2%}・クリック1回 {v[0]/v[2]:.0f}円")
P('  ＝去年の年末は 1日 3,000〜5,000円で、商品も今と違う。年末に向けて CPM がどう動くかを比べられる数字ではない')
open(D0 + 'black_1128.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
