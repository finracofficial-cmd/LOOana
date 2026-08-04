#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-04 「カタログのCPA高騰は夏物需要の減退か」の検証
Metaの日次×キャンペーンから週次に集計し、季節物 / 通年物 / カタログ で分けて
CPA を CPM ÷ (CTR × CVR × 1000) に分解する。
"""
import json, re, sys
from collections import defaultdict
from datetime import date, timedelta

SRC = '/root/.claude/projects/-home-user-LOOana/42be2ed9-9967-56df-ab9c-75166f45bbc9/tool-results/mcp-Supermetrics_Marketing_Analytics-get_async_query_results-1785826958958.txt'
raw = json.load(open(SRC))['data']['data']

# 行フォーマット: "  - [8,]: 2026-06-22,形状記憶日傘,12345,678,0.04,90,1.2,3"
rows = []
for line in raw.split('\n'):
    m = re.match(r'\s*- \[\d+,\]: (\d{4}-\d{2}-\d{2}),(.+)$', line)
    if not m:
        continue
    d = m.group(1)
    rest = m.group(2).rsplit(',', 6)   # 後ろ6個が数値、残りがキャンペーン名
    name = rest[0]
    def num(x):
        return 0.0 if x in ('', 'null', None) else float(x)
    cost, imp, ctr, clicks, freq, purch = (num(x) for x in rest[1:])
    rows.append((d, name, cost, imp, ctr, clicks, freq, purch))

print(f'読み込み {len(rows)} 行 / 期間 {min(r[0] for r in rows)} 〜 {max(r[0] for r in rows)}')
names = sorted({r[1] for r in rows})
print(f'キャンペーン {len(names)} 本')

# 分類
SEASONAL = {'4WAY 取り付けOK 小型瞬間冷却ハンディファン','卓上冷感クーラー','3WAYサーキュレーター扇風機',
            '5WAY腰掛けファン','瞬間冷感ポンチョ','湯上がりガーゼワンピース','瞬間冷却ハンディファン',
            '形状記憶日傘','完全遮光・形状記憶・晴雨兼用・UV日傘','接触冷感UVパーカー',
            '偏光・調光サングラス','接触冷感UVアームカバー','完全遮光・接触冷感UVハット','害虫ブロッカー'}
CATALOG  = {'カタログ全部（テスト）'}
def cls(n):
    if n in CATALOG: return 'カタログ'
    if n in SEASONAL: return '季節物'
    return '通年物'

def wk(d):
    y, m, dd = map(int, d.split('-'))
    t = date(y, m, dd)
    return (t - timedelta(days=t.weekday())).isoformat()   # 月曜起点

agg = defaultdict(lambda: [0.0]*4)   # (week, class) -> cost, imp, clicks, purch
for d, n, cost, imp, ctr, clicks, freq, purch in rows:
    a = agg[(wk(d), cls(n))]
    a[0] += cost; a[1] += imp; a[2] += clicks; a[3] += purch

weeks = sorted({k[0] for k in agg})
weeks = [w for w in weeks if w >= '2026-06-22' and w <= '2026-07-27']

def show(cl):
    print()
    print('=' * 100)
    print(f'【{cl}】週次ファネル（月曜起点・Meta実測）')
    print('=' * 100)
    print(f"{'週':12}{'広告費':>11}{'CPM':>8}{'CTR':>8}{'CVR':>8}{'CTR×CVR':>10}{'購入':>7}{'CPA':>8}")
    base = None
    out = []
    for w in weeks:
        cost, imp, clicks, purch = agg[(w, cl)]
        if imp == 0: continue
        cpm = cost/imp*1000; ctr = clicks/imp; cvr = purch/clicks if clicks else 0
        cpa = cost/purch if purch else float('nan')
        print(f'{w:12}{cost:11,.0f}{cpm:8,.0f}{ctr*100:7.2f}%{cvr*100:7.2f}%{ctr*cvr*10000:9.2f}‱{purch:7,.0f}{cpa:8,.0f}')
        out.append((w, cpm, ctr, cvr, cpa))
    a, b = out[0], out[-1]
    print('-' * 100)
    print(f'{a[0]} → {b[0]} の変化:  CPM {(b[1]/a[1]-1)*100:+.1f}%  CTR {(b[2]/a[2]-1)*100:+.1f}%  '
          f'CVR {(b[3]/a[3]-1)*100:+.1f}%  CTR×CVR {((b[2]*b[3])/(a[2]*a[3])-1)*100:+.1f}%  CPA {(b[4]/a[4]-1)*100:+.1f}%')
    return out

res = {cl: show(cl) for cl in ['カタログ', '季節物', '通年物']}

# ---- 判別 ----
print()
print('=' * 100)
print('診断: 需要そのものの減退か、広告側の問題か')
print('=' * 100)
print('需要減退のシグネチャ = CTRが下がり、CPMも下がる（オークションが冷える）')
print('広告側の疲弊       = CTRが下がるが、CPMは横ばい〜上昇（同じ人に当て続けている）')
print()
for cl in ['カタログ', '季節物', '通年物']:
    a, b = res[cl][0], res[cl][-1]
    dcpm, dctr, dcvr = (b[1]/a[1]-1), (b[2]/a[2]-1), (b[3]/a[3]-1)
    if dctr < -0.05 and dcpm < -0.05:   sig = '需要減退型（CTR↓ CPM↓）'
    elif dctr < -0.05 and dcpm >= -0.05: sig = '広告疲弊型（CTR↓ CPM横ばい以上）'
    elif dcvr < -0.10 and abs(dctr) < 0.10: sig = 'LP/オファー型（CVRのみ↓）'
    else: sig = '明確な劣化なし'
    print(f'{cl:8} CPM {dcpm*100:+6.1f}%  CTR {dctr*100:+6.1f}%  CVR {dcvr*100:+6.1f}%  → {sig}')

# ---- 季節物を「夏物」に絞って再検証 ----
print()
print('=' * 100)
print('季節物のうち「夏物のみ」（害虫を除く13商品）で再検証')
print('=' * 100)
SUMMER = SEASONAL - {'害虫ブロッカー'}
agg2 = defaultdict(lambda: [0.0]*4)
for d, n, cost, imp, ctr, clicks, freq, purch in rows:
    if n not in SUMMER: continue
    a = agg2[wk(d)]
    a[0]+=cost; a[1]+=imp; a[2]+=clicks; a[3]+=purch
print(f"{'週':12}{'広告費':>11}{'CPM':>8}{'CTR':>8}{'CVR':>8}{'購入':>7}{'CPA':>8}")
o=[]
for w in weeks:
    cost, imp, clicks, purch = agg2[w]
    cpm=cost/imp*1000; ctr=clicks/imp; cvr=purch/clicks; cpa=cost/purch
    print(f'{w:12}{cost:11,.0f}{cpm:8,.0f}{ctr*100:7.2f}%{cvr*100:7.2f}%{purch:7,.0f}{cpa:8,.0f}')
    o.append((cpm,ctr,cvr,cpa))
print('-'*100)
print(f'変化: CPM {(o[-1][0]/o[0][0]-1)*100:+.1f}%  CTR {(o[-1][1]/o[0][1]-1)*100:+.1f}%  '
      f'CVR {(o[-1][2]/o[0][2]-1)*100:+.1f}%  CPA {(o[-1][3]/o[0][3]-1)*100:+.1f}%')

# ---- 非広告流入（Shopify実測・需要の外部指標） ----
print()
print('=' * 100)
print('広告に依存しない流入（Shopify実測・週次セッション）')
print('=' * 100)
SESS = {
 '2026-06-22': {'social':33386,'direct':8210,'search':771},
 '2026-06-29': {'social':36610,'direct':9561,'search':918},
 '2026-07-06': {'social':33649,'direct':8397,'search':841},
 '2026-07-13': {'social':33613,'direct':9370,'search':811},
 '2026-07-20': {'social':39959,'direct':12942,'search':946},
 '2026-07-27': {'social':35683,'direct':13900,'search':816},
}
print(f"{'週':12}{'social':>9}{'direct':>9}{'search':>9}{'direct+search':>15}")
for w in sorted(SESS):
    s = SESS[w]
    print(f"{w:12}{s['social']:9,}{s['direct']:9,}{s['search']:9,}{s['direct']+s['search']:15,}")
f, l = SESS['2026-06-22'], SESS['2026-07-27']
print('-'*100)
print(f"変化: social {(l['social']/f['social']-1)*100:+.1f}%  direct {(l['direct']/f['direct']-1)*100:+.1f}%  "
      f"search {(l['search']/f['search']-1)*100:+.1f}%  direct+search {((l['direct']+l['search'])/(f['direct']+f['search'])-1)*100:+.1f}%")
print('※ direct+search は広告を打たなくても来る客＝需要そのものの代理指標')

# ---- カタログのCVR崩れは「いつ」起きたか（日次） ----
print()
print('=' * 100)
print('カタログ全部（テスト）日次 — CVRの崩れた日を特定する')
print('=' * 100)
print(f"{'日付':12}{'広告費':>9}{'CPM':>8}{'CTR':>8}{'クリック':>8}{'購入':>6}{'CVR':>8}{'CPA':>8}")
for d, n, cost, imp, ctr, clicks, freq, purch in sorted(rows):
    if n != 'カタログ全部（テスト）' or d < '2026-07-14':
        continue
    cpm = cost/imp*1000 if imp else 0
    cvr = purch/clicks if clicks else 0
    cpa = cost/purch if purch else float('nan')
    print(f'{d:12}{cost:9,.0f}{cpm:8,.0f}{ctr*100:7.2f}%{clicks:8,.0f}{purch:6,.0f}{cvr*100:7.2f}%{cpa:8,.0f}')
