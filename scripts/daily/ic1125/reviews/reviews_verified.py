# -*- coding: utf-8 -*-
"""11/25 14時台「レビューも Google に反映したい。既存のをもってこれる？」
公開の商品ページの HTML（スクリプトは動かさない＝計測の通信は出ない）から、Judge.me のレビューの件数・購入者確認の印（data-verified-buyer）・本文の有無を数える。
ページに出るのは各商品の1ページ目だけ（合計の件数は data-number-of-reviews）。"""
import json, re, subprocess, time, datetime as dt, collections
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
def get(u):
    for _ in range(3):
        r = subprocess.run(['curl', '-sS', '-L', '--max-time', '40', '-A', UA, u], capture_output=True, text=True)
        if len(r.stdout) > 50000 or 'products.json' in u: return r.stdout
        time.sleep(1.5)
    return r.stdout
prods = json.loads(get('https://looty-japan.com/products.json?limit=250'))['products']
out = []
for p in prods:
    h = get('https://looty-japan.com/products/' + p['handle'])
    n = re.search(r'data-number-of-reviews=[\'"](\d+)', h)
    revs = re.findall(r'<div class=[\'"]jdgm-rev [^>]*>', h)
    ver = [re.search(r'data-verified-buyer=[\'"](\w+)', r).group(1) if re.search(r'data-verified-buyer=[\'"](\w+)', r) else '?' for r in revs]
    body = len(re.findall(r'jdgm-rev__body', h))
    ts = re.findall(r'jdgm-rev__timestamp[^>]*data-content=[\'"]([^\'"]+)', h)
    out.append({'handle': p['handle'], 'title': p['title'], 'n': int(n.group(1)) if n else None, 'shown': len(revs), 'verified': ver.count('true'), 'unverified': ver.count('false'), 'unknown': ver.count('?'), 'bodies': body, 'dates': ts, 'html_len': len(h),
                'barcode': [v.get('barcode') for v in p.get('variants', [])][:3] if any('barcode' in v for v in p.get('variants', [])) else None, 'sku': [v.get('sku') for v in p.get('variants', [])][:2], 'vendor': p.get('vendor')})
    time.sleep(0.3)
json.dump({'fetched_at_utc': dt.datetime.utcnow().isoformat(), 'products': out}, open('reviews_verified_raw.json', 'w'), ensure_ascii=False, indent=1)
ok = [o for o in out if o['n'] is not None]
L = []
def P(*x):
    s = ' '.join(str(i) for i in x); print(s); L.append(s)
P(f"■ 公開ページの Judge.me のレビュー（取得 {dt.datetime.utcnow().isoformat()[:16]} UTC）: 商品 {len(out)}・読めた {len(ok)}・読めなかった {len(out)-len(ok)}")
P(f"  レビューの合計（data-number-of-reviews）{sum(o['n'] for o in ok)}件・ページに出ている {sum(o['shown'] for o in ok)}件 → 購入者確認の印あり {sum(o['verified'] for o in ok)}・なし {sum(o['unverified'] for o in ok)}・印が読めない {sum(o['unknown'] for o in ok)}")
mon = collections.Counter(d[:7] for o in ok for d in o['dates'])
P('  月別（ページに出ている分の日付）: ' + '・'.join(f'{k} {v}' for k, v in sorted(mon.items())))
P('  いま広告を出している商品:')
for key in ('伸縮ガラスクリーナー', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', '快適マジックインソール', '4-in-1マルチクリーナー', '360°マルチクリップ', 'マグネットドアクッション', 'スマートノーズ', 'レインガードフィルム', '姿勢サポートチェア'):
    for o in ok:
        if key in o['title']: P(f"    {key}: 合計 {o['n']}件・出ている {o['shown']}件（確認あり {o['verified']}・なし {o['unverified']}）・日付 {sorted(set(d[:10] for d in o['dates']))[:6]}・SKU {o['sku']}・ベンダー {o['vendor']}")
open('reviews_verified.txt', 'w').write('\n'.join(L) + '\n')
