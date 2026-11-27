# 公開した3本（64〜66本目）が下書きと同じ中身か、公開ページが開けるかを確かめる（2026-11-27）
import json, re, subprocess, html, urllib.parse, sys
sys.path.insert(0, '/home/user/LOOana/scripts/daily/ic1127/blog')
from build_articles import build, A
raw = json.load(open('/home/user/LOOana/scripts/daily/ic1127/blog/articles_created_1127_raw.json', encoding='utf-8'))
nodes = {n['handle']: n for n in raw['data']['nodes']}
norm = lambda s: re.sub(r'>\s+<', '><', s.replace('\n', '')).strip()
text = lambda s: [t.strip() for t in re.split(r'<[^>]+>', re.sub(r'<style>.*?</style>', '', s, flags=re.S)) if len(t.strip()) >= 6]
out = []
for k in ('visor', 'humid', 'glove'):
    path, n, _, _, _, v = build(k, 'ベージュ・ホワイト・木目調の3種類')
    a = v['article']; s = nodes[a['handle']]
    mf = {m['key']: m['value'] for m in s['metafields']['nodes']}
    same = dict(本文=norm(s['body']) == norm(a['body']), タイトル=s['title'] == a['title'], 要約=s['summary'] == a['summary'],
                タグ=sorted(s['tags']) == sorted(a['tags']), SEOタイトル=mf.get('title_tag') == a['metafields'][0]['value'],
                SEO説明=mf.get('description_tag') == a['metafields'][1]['value'], 公開=s['isPublished'] is True, 著者=s['author']['name'] == 'LOOTY')
    url = 'https://looty-japan.com/blogs/' + urllib.parse.quote(s['blog']['handle']) + '/' + s['handle']
    r = subprocess.run(['curl', '-s', '-L', '-o', f'/tmp/claude-0/-home-user-LOOana/91ae6ee3-db77-5228-ad52-aeac6ce2aa54/scratchpad/blog1127/pub_{k}.html', '-w', '%{http_code}', url], capture_output=True, text=True)
    page = html.unescape(open(f'/tmp/claude-0/-home-user-LOOana/91ae6ee3-db77-5228-ad52-aeac6ce2aa54/scratchpad/blog1127/pub_{k}.html', encoding='utf-8', errors='replace').read())
    pieces = [html.unescape(t) for t in text(a['body'])]; miss = [t for t in pieces if t not in page]
    imgs = re.findall(r'<img src="([^"]+)"', a['body']); imiss = [u for u in imgs if u.split('?')[0].split('/')[-1] not in page]
    out.append(f"{A[k]['no']}本目 {A[k]['name']}｜{s['id'].split('/')[-1]}｜公開 {s['publishedAt']}（UTC）\n  URL: https://looty-japan.com/blogs/{s['blog']['handle']}/{s['handle']}\n"
               f"  登録内容と下書きの一致: {' '.join(f'{x}={y}' for x, y in same.items())}\n"
               f"  公開ページ: HTTP {r.stdout}・本文の文 {len(pieces) - len(miss)}/{len(pieces)} が出ている・画像 {len(imgs) - len(imiss)}/{len(imgs)}・タイトルあり={a['title'] in page}・商品ページへのリンクあり={A[k]['url'] in page}"
               + (f"\n  出ていない文: {miss[:5]}" if miss else '') + (f"\n  出ていない画像: {imiss}" if imiss else ''))
    assert all(same.values()), (k, same)
print('\n'.join(out))
