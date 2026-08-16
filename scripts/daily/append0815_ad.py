# -*- coding: utf-8 -*-
"""2026-08-15 の Meta広告費を daily_ad.csv へ追記する（冪等）。

2026-08-16 に Supermetrics が復旧したので、8/16朝に取得できなかった分を遡って追記する。
ds_id=FA / act_1124340806289175 / timezone=Asia/Tokyo / date=2026-08-15
広告費は四捨五入で書き込む（SKILL 2026-08-01 の決定）。

横照合: Σキャンペーン別 ≒ アカウントレベル（別クエリの実測 364,579円）を ±0.1% で検算する。
"""
import csv, os
B = '/home/user/LOOana/data/daily/'
D = '2026-08-15'

AD = {  # キャンペーン名はMetaの表記のまま
 'ナノガラス脱毛パッド': 91876, '形状記憶日傘': 38910, 'W固定スマホ車載ホルダー': 31246,
 '害虫ブロッカー': 24671, 'カタログ全部（テスト）': 23961, 'ムダ毛シェーバー': 23165,
 '接触冷感UVパーカー': 19720, '偏光・調光サングラス': 16895,
 '完全遮光・形状記憶・晴雨兼用・UV日傘': 16455, '2WAYシートボックス': 12158,
 '完全遮光・接触冷感UVハット': 11174, '快適マジックインソール': 11061,
 '姿勢サポートチェア': 9784, '4WAY 取り付けOK 小型瞬間冷却ハンディファン': 7638,
 '接触冷感UVアームカバー': 7471, '5WAY腰掛けファン': 6939,
 'ナノバブルシャワーヘッド': 6186, 'バランスケアスリッパ': 5269,
}
ACCOUNT = 364579          # アカウントレベルの別クエリ実測
tot = sum(AD.values())
diff = tot - ACCOUNT
assert abs(diff) / ACCOUNT < 0.001, (tot, ACCOUNT, diff)
print(f'横照合OK: Σキャンペーン {tot:,}円 vs アカウント {ACCOUNT:,}円'
      f'（差 {diff:+,}円 / {diff/ACCOUNT:+.4%}）')
print(f'  ※ 害虫ブロッカーは 24,671円 消化（8/15の日中まで稼働）。8/16は消化ゼロで停止を確認済み。')

def append(path, rows):
    body = list(csv.reader(open(path, encoding='utf-8')))[1:]
    have = {tuple(r[:2]) for r in body}
    added = 0
    with open(path, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        for r in rows:
            if tuple(str(x) for x in r[:2]) in have: continue
            w.writerow(r); added += 1
    print(f'{os.path.basename(path)}: {added}行追記（既存 {len(body)}行）')

append(B + 'daily_ad.csv', [[D, c, v] for c, v in AD.items()])
