# 公開した 67本目（クリア仕上げガラスクロス）が下書きと同じ中身か、公開ページが開けるかを確かめる（2026-11-27）
import json, re, subprocess, html, urllib.parse, sys, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'; sys.path.insert(0, D)
import build_cloth_article as C
B = C.B; SP = '/tmp/claude-0/-home-user-LOOana/91ae6ee3-db77-5228-ad52-aeac6ce2aa54/scratchpad/cloth1127/work/pub_cloth.html'
s = json.load(open(D + 'article_created_1127_raw.json', encoding='utf-8'))['data']['nodes'][0]
norm = lambda x: re.sub(r'>\s+<', '><', x.replace('\n', '')).strip()
text = lambda x: [html.unescape(t.strip()) for t in re.split(r'<[^>]+>', re.sub(r'<style>.*?</style>', '', x, flags=re.S)) if len(t.strip()) >= 6]
path, n, _, _, _, v = B.build('cloth', None); a = v['article']; mf = {m['key']: m['value'] for m in s['metafields']['nodes']}
same = dict(本文=norm(s['body']) == norm(a['body']), タイトル=s['title'] == a['title'], 要約=s['summary'] == a['summary'], タグ=sorted(s['tags']) == sorted(a['tags']),
            SEOタイトル=mf.get('title_tag') == a['metafields'][0]['value'], SEO説明=mf.get('description_tag') == a['metafields'][1]['value'], 公開=s['isPublished'] is True, 著者=s['author']['name'] == 'LOOTY')
url = 'https://looty-japan.com/blogs/' + urllib.parse.quote(s['blog']['handle']) + '/' + s['handle']
r = subprocess.run(['curl', '-s', '-L', '-o', SP, '-w', '%{http_code}', url], capture_output=True, text=True); page = html.unescape(open(SP, encoding='utf-8', errors='replace').read())
pieces = text(a['body']); miss = [t for t in pieces if t not in page]; imgs = re.findall(r'<img src="([^"]+)"', a['body']); imiss = [u for u in imgs if u.split('?')[0].split('/')[-1] not in page]
idx = subprocess.run(['curl', '-s', '-L', 'https://looty-japan.com/blogs/' + urllib.parse.quote(s['blog']['handle'])], capture_output=True, text=True).stdout; top = list(dict.fromkeys(re.findall(r'blogs/[^"]*?/([a-z0-9\-]+-guide)', idx)))[:1]
out = (f"67本目 {B.A['cloth']['name']}｜{s['id'].split('/')[-1]}｜公開 {s['publishedAt']}（UTC）\n  URL: https://looty-japan.com/blogs/{s['blog']['handle']}/{s['handle']}\n"
       f"  登録内容と下書きの一致: {' '.join(f'{x}={y}' for x, y in same.items())}\n"
       f"  公開ページ: HTTP {r.stdout}・本文の文 {len(pieces) - len(miss)}/{len(pieces)} が出ている・画像 {len(imgs) - len(imiss)}/{len(imgs)}・タイトルあり={a['title'] in page}・商品ページへのリンクあり={B.A['cloth']['url'] in page}・ブログ一覧の先頭={top}"
       + (f"\n  出ていない文: {miss[:5]}" if miss else '') + (f"\n  出ていない画像: {imiss}" if imiss else ''))
assert all(same.values()), same
print(out); open(D + 'verify_cloth_article.txt', 'w', encoding='utf-8').write(out + '\n')
