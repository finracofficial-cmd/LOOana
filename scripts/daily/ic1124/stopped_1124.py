# -*- coding: utf-8 -*-
"""11/24「過去に止めた商品で、今出せそうなものはあるか。幅広に」: 6/29〜11/23 に広告費があった全商品の、広告を出した日だけの数字。
入力: w1123.py（売上・原価・広告費の積み直し）。バリエーションで原価が違う商品（ナノ・ディスペンサー）の日別の内訳が 7/17 からなので、7/17〜11/23 で見る（それより前に出して止めた商品は途中から）。広告を出していない日の売上は ⑤ で別に数える。種類（車まわり等）と季節は Claude の判断"""
import io, contextlib, collections, csv, datetime, json
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(open('scripts/daily/w1123.py').read(), g)
A, ALLD, agg, WIN, MAP, MULTI, PRICE = g['A'], g['ALLD'], g['agg'], g['WIN'], g['MAP'], g['MULTI'], g['PRICE']
camps = lambda n: MULTI.get(n, (MAP.get(n, n),))
ALLD = [d for d in ALLD if d >= '2026-07-17']
names = sorted({n for n in set(PRICE) | set(MAP) | set(MULTI) if any(A([d], n) for d in ALLD)})
DAY = {}
for d in ALLD:
    WIN['d' + d] = [d]; N1, D1, Q1, K1 = agg([d], 'd' + d); DAY[d] = (N1, K1)
def gp_day(n, d): N1, K1 = DAY[d]; return N1.get(n, 0) - K1.get(n, 0)
rows = []
for n in names:
    ds = [d for d in ALLD if A([d], n) > 0]
    a = [A([d], n) for d in ds]; p = [gp_day(n, d) for d in ds]
    def win(ix): aa = sum(a[i] for i in ix); return sum(p[i] for i in ix) / aa if aa else 0
    best = max(win(range(i, i + 7)) for i in range(max(1, len(ds) - 6))) if len(ds) >= 7 else win(range(len(ds)))
    last = ds[-1]; rest = (datetime.date(2026, 11, 23) - datetime.date.fromisoformat(last)).days
    noad = [d for d in ALLD if d >= '2026-10-25' and not A([d], n)]
    WIN['na' + n] = noad; Nn, Dn, Qn, Kn = agg(noad, 'na' + n) if noad else ({}, {}, {}, {})
    q30 = Qn.get(n, 0)
    rows.append(dict(n=n, first=ds[0], last=last, days=len(ds), ad=sum(a), gp=sum(p), m=sum(p) / sum(a), m7a=win(range(min(7, len(ds)))), best=best,
                     m7z=win(range(max(0, len(ds) - 7), len(ds))), rest=rest, noad=q30, price=PRICE.get(n)))
json.dump(rows, open('scripts/daily/ic1124/stopped_1124.json', 'w'), ensure_ascii=False, indent=1)
print('商品（7/17〜11/23）: 最初〜最後に広告を出した日（日数）｜広告費・利益・通算の倍率｜最初の7日・いちばん良い7日・最後の7日｜止めてからの日数（11/23 まで）｜10/25〜11/23 の広告なしの日の個数｜売価')
for r in sorted(rows, key=lambda r: -(r['gp'] - r['ad'])):
    st = '配信中' if r['last'] == '2026-11-23' else f"止めて{r['rest']}日"
    print(f"  {r['n']}: {r['first'][5:]}〜{r['last'][5:]}（{r['days']}日）｜{r['ad']:,.0f}・{r['gp']-r['ad']:+,.0f}・{r['m']:.2f}｜{r['m7a']:.2f}・{r['best']:.2f}・{r['m7z']:.2f}｜{st}｜広告なし {r['noad']}個｜{r['price']}")
