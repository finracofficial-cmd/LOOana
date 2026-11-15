# -*- coding: utf-8 -*-
"""高見えレザーヘッドレストフックはなぜ急に売れなくなったか（2026-11-15 15:1x ユーザー「レザーフックって何で急に売れなくなったんだ？」）
入力: hook_meta_daily_0909_1114.txt（Meta キャンペーン日別）・Shopify 日別の注文（下に貼る・WHERE product_title CONTAINS 'ヘッドレストフック'）・data/daily（売上・広告費の照合）
週ごとに 注文/広告費1万円 ＝ 表示/1万円（CPMの逆）× クリック率 × 注文/クリック に分ける"""
import csv, math, collections, datetime
R = __file__.rsplit('/scripts/', 1)[0] + '/'
M = {}
for l in open(R + 'scripts/daily/ic1115/hook_meta_daily_0909_1114.txt'):
    if l[0] != '#': p = l.strip().split(','); M[p[0]] = [int(x) for x in p[1:]]
O = dict(zip([(datetime.date(2026, 9, 9) + datetime.timedelta(k)).isoformat() for k in range(67)],
  [2,4,7,3,6,6,8,8,7,5,11,13,17,12,7,2,8,10,15,7,7,11,8,14,6,11,8,11,2,5,6,6,5,10,2,3,4,4,5,5,5,1,2,7,5,5,3,2,0,1,3,1,1,5,2,0,0,0,0,0,0,0,1,0,1,0,0]))
G = collections.defaultdict(int); A = collections.defaultdict(float)
for r in csv.DictReader(open(R + 'data/daily/daily_sales.csv')):
    if r['name'] == '高見えレザーヘッドレストフック': G[r['date']] += int(r['gross'])
for r in csv.DictReader(open(R + 'data/daily/daily_ad.csv')):
    if r['campaign'].startswith('高見えレザーヘッドレストフック'): A[r['date']] += float(r['cost'])
for d, v in M.items(): assert abs(v[0] - A[d]) <= max(3, v[0] * 0.005), (d, v[0], A[d])   # Meta の取り直し＝data/daily
st = datetime.date(2026, 9, 9)
W = [(f'{(st+datetime.timedelta(7*w)).isoformat()[5:]}〜{(st+datetime.timedelta(7*w+6)).isoformat()[5:]}', [(st + datetime.timedelta(7 * w + k)).isoformat() for k in range(7)]) for w in range(8)]
W.append(('11-11〜11-12（再開）', ['2026-11-11', '2026-11-12']))
print('週            広告費/日  注文/日  注文/1万円 = 表示/1万円 × クリック率 × 注文/クリック ｜ 1注文の売上 頻度（表示÷到達）')
for lab, ds in W:
    ds = [d for d in ds if d in M and M[d][0] > 0]
    c, im, rc, cl = (sum(M[d][i] for d in ds) for i in range(4)); o = sum(O[d] for d in ds); g = sum(G[d] for d in ds)
    print(f'{lab:<20} {c/len(ds):8,.0f}  {o/len(ds):5.1f}   {o/c*10000:5.2f}   =  {im/c*10000:6,.0f}  × {cl/im*100:5.2f}% × {o/cl*100:5.2f}%  ｜ {g/o if o else 0:6,.0f}   {im/rc:.3f}')
