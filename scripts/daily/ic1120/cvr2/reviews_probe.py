# 商品ページの HTML（スクリプトは動かさない＝計測の通信は出ない）から、Judge.me のレビュー件数と日付を読む
# 使い方: python3 reviews_probe.py  → reviews_raw.json（生）と reviews_probe.txt
import json, re, subprocess, sys, time, datetime as dt
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
def get(u):
    r = subprocess.run(['curl', '-sS', '-L', '--max-time', '40', '-A', UA, u], capture_output=True, text=True)
    return r.stdout
prods = json.loads(get('https://looty-japan.com/products.json?limit=250'))['products']
out = []
for p in prods:
    h = get('https://looty-japan.com/products/' + p['handle'])
    n = re.search(r'data-number-of-reviews=[\'"](\d+)', h)
    avg = re.search(r'data-average-rating=[\'"]([\d.]+)', h)
    ts = re.findall(r'jdgm-rev__timestamp[^>]*data-content=[\'"]([^\'"]+)', h)
    pics = len(re.findall(r'jdgm-rev__pic-link|jdgm-rev__pic-img', h))
    out.append({'handle': p['handle'], 'title': p['title'], 'n': int(n.group(1)) if n else None, 'avg': avg.group(1) if avg else None,
                'dates': ts, 'pics': pics, 'html_len': len(h)})
    time.sleep(0.4)
json.dump({'fetched_at_utc': dt.datetime.utcnow().isoformat(), 'products': out}, open('reviews_raw.json', 'w'), ensure_ascii=False, indent=1)
print(len(out), 'products')
