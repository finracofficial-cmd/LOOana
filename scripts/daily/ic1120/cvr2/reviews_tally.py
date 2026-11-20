# reviews_raw.json（reviews_probe.py の生）を数える。数字はすべてこのファイルから
import json, datetime as dt, collections, subprocess
d = json.load(open('reviews_raw.json'))
ps = d['products']
now = dt.datetime.fromisoformat(d['fetched_at_utc'])
L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)
P('# 11/20 レビューの件数と日付（公開の商品ページの HTML・Judge.me の表示。取得', (now + dt.timedelta(hours=9)).strftime('%m/%d %H:%M'), 'JST）')
ok = [p for p in ps if p['n'] is not None]
P('商品', len(ps), '・レビュー欄が読めた', len(ok), '・読めなかった', len(ps) - len(ok), '（HTML が短い＝取得失敗:', sum(p['html_len'] < 50000 for p in ps), '）')
P('読めなかった商品:', [p['title'][-24:] for p in ps if p['n'] is None][:12])
tot = sum(p['n'] for p in ok)
P('レビュー合計', tot, '件・1商品あたり 最小', min(p['n'] for p in ok), '最大', max(p['n'] for p in ok), '・件数の分布', dict(sorted(collections.Counter(p['n'] for p in ok).items())))
alld = []
for p in ok:
    ds = sorted(dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S UTC') for x in p['dates'])
    p['_d'] = ds
    alld += [(x, p['title']) for x in ds]
P('ページに出ている日付つきレビュー', len(alld), '件（合計', tot, '件のうち。1ページ目に出る分だけ）')
for days in (7, 30, 90):
    P(' 直近', days, '日に付いたもの', sum((now - x).days < days for x, _ in alld), '件')
bym = collections.Counter(x.strftime('%Y-%m') for x, _ in alld)
P(' 月別', dict(sorted(bym.items())))
# 同じ商品で、前のレビューから10分以内に付いたもの
close = 0; pairs = 0
for p in ok:
    ds = p['_d']
    c = sum(1 for a, b in zip(ds, ds[1:]) if (b - a).total_seconds() <= 600)
    close += c
    if c: pairs += 1
P('同じ商品で、前のレビューから10分以内に付いたレビュー', close, '件（', pairs, '商品）／日付つき', len(alld), '件')
# 1商品の全レビューが同じ日
same = sum(1 for p in ok if p['_d'] and len({x.date() for x in p['_d']}) == 1 and len(p['_d']) == p['n'])
P('出ているレビューが全部同じ日付の商品', same, '／', sum(1 for p in ok if p['_d']))
P('写真つきの印がある商品', sum(1 for p in ok if p['pics'] > 0), '／', len(ok))
P('')
P('商品ごと（件数・いちばん新しい日付・いちばん古い日付・10分以内の組）')
for p in sorted(ok, key=lambda p: -(p['n'] or 0)):
    ds = p['_d']
    c = sum(1 for a, b in zip(ds, ds[1:]) if (b - a).total_seconds() <= 600)
    P(' ', p['n'], '件', (ds[-1] + dt.timedelta(hours=9)).strftime('%m/%d') if ds else '—', (ds[0] + dt.timedelta(hours=9)).strftime('%m/%d') if ds else '—', '組', c, '|', p['title'].replace('【在庫セール⏰】', '').replace('【本日終了⏰】', '').replace('【累計15万台突破🏆】', '')[:34])
open('reviews_probe.txt', 'w').write('\n'.join(L) + '\n')
