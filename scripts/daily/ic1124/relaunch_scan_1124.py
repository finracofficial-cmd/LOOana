# -*- coding: utf-8 -*-
"""11/24「レインガードもインソールも同じ動画で良い。止めた商品で今出せそうなものは？」:
これまでの出し直し（data/relaunch-log.csv の日付）ごとに、止める前の出稿（7/17 以降・3日以内の空きはつなぐ）の 通算・いちばん良い7日・最後の7日・休ませた日数 と、
出し直した後の最初の7日（広告を出した日だけ）の倍率を並べる。入力: w1123.py（売上・原価・広告費）"""
import io, contextlib, datetime, json
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD0, agg, WIN = g['A'], g['ALLD'], g['agg'], g['WIN']
ALLD = [d for d in ALLD0 if d >= '2026-07-17']
DAY = {}
for d in ALLD:
    WIN['r' + d] = [d]; N1, D1, Q1, K1 = agg([d], 'r' + d); DAY[d] = (N1, K1)
gp = lambda n, d: DAY[d][0].get(n, 0) - DAY[d][1].get(n, 0)
dd = lambda a, b: (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days
EV = [('UV歯ブラシ除菌器', '2026-09-18', 'A'), ('携帯電動シェーバー', '2026-09-18', 'A'), ('4-in-1マルチクリーナー', '2026-10-04', 'A'), ('ナノバブルシャワーヘッド', '2026-10-14', 'A'),
      ('むくみ取りかっさ', '2026-10-14', 'A'), ('壁掛けディスペンサー', '2026-10-17', 'A'), ('2WAYシートボックス', '2026-10-29', 'A'), ('健康サンダル', '2026-10-31', 'A'),
      ('高見えレザーヘッドレストフック', '2026-11-11', 'A'), ('UV歯ブラシ除菌器', '2026-11-12', 'A'), ('バランスケアスリッパ', '2026-11-12', 'A'),
      ('携帯電動シェーバー', '2026-11-14', 'C1+D'), ('高見えレザーヘッドレストフック', '2026-11-15', 'D'), ('快適マジックインソール', '2026-11-16', 'C1'),
      ('ポータブルヒートシーラー', '2026-11-18', 'D→C1'), ('壁掛けディスペンサー', '2026-11-18', 'C1'), ('コードレス毛玉クリーナー', '2026-11-22', 'D'), ('UV歯ブラシ除菌器', '2026-11-22', 'D'),
      ('クリアビューレインガードフィルム', '2026-11-23', 'C1')]
def m(n, ds):
    a = sum(A([d], n) for d in ds); return (sum(gp(n, d) for d in ds) / a) if a else None
out = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); out.append(s)
P('出し直し: 型｜前の出稿（日数・通算・いちばん良い7日・最後の7日）｜休ませた日数｜出し直した後の最初の7日（広告を出した日だけ・日数）')
rows = []
for n, R, t in EV:
    pre = [d for d in ALLD if d < R and A([d], n) > 0]
    if not pre: P(f'  {n} {R}（{t}）: 7/17 以降に前の出稿なし'); continue
    blk = [pre[-1]]
    for d in reversed(pre[:-1]):
        if dd(d, blk[0]) <= 4: blk.insert(0, d)
        else: break
    best = max(m(n, blk[i:i + 7]) for i in range(max(1, len(blk) - 6)))
    post = [d for d in ALLD if d >= R and A([d], n) > 0][:7]
    po = m(n, post)
    rows.append(dict(n=n, R=R, t=t, days=len(blk), all=m(n, blk), best=best, last=m(n, blk[-7:]), rest=dd(blk[-1], R), post=po, pdays=len(post)))
    P(f"  {n} {R[5:]}（{t}）: {len(blk)}日・{m(n, blk):.2f}・{best:.2f}・{m(n, blk[-7:]):.2f}｜休み {dd(blk[-1], R)}日｜後 {po:.2f}（{len(post)}日）")
json.dump(rows, open('scripts/daily/ic1124/relaunch_scan_1124.json', 'w'), ensure_ascii=False, indent=1)
open('scripts/daily/ic1124/relaunch_scan_1124.txt', 'w').write('\n'.join(out) + '\n')
