# -*- coding: utf-8 -*-
"""ヘッダーの流れるバナー（Marqueeセクション）に流す文言を、実注文から生成する。

入力は Shopify Admin API の実注文（financial_status:paid の直近50件・2026-08-15取得）。
出せるのは 都道府県 × 商品 × 個数 だけ。氏名・市区町村・注文番号は一切使わない。
捏造しない。実際に売れていない商品は1つも出てこない。
"""
import collections, json

PREF = {'Tōkyō':'東京都','Ōsaka':'大阪府','Kanagawa':'神奈川県','Aichi':'愛知県','Hyōgo':'兵庫県',
 'Nara':'奈良県','Ibaraki':'茨城県','Gifu':'岐阜県','Shizuoka':'静岡県','Chiba':'千葉県',
 'Yamanashi':'山梨県','Nagasaki':'長崎県','Gunma':'群馬県','Fukushima':'福島県','Yamaguchi':'山口県',
 'Ishikawa':'石川県','Kumamoto':'熊本県','Ehime':'愛媛県','Miyagi':'宮城県','Aomori':'青森県',
 'Mie':'三重県','Kagoshima':'鹿児島県','Saga':'佐賀県','Fukuoka':'福岡県','Kagawa':'香川県'}

def short(t):
    return (t.replace('【本日終了⏰】【累計15万台突破🏆】','')
             .replace('【顧客満足度No.1獲得商品🥇】【全国送料無料🚗】','')
             .replace('LOOTY','').replace('LOTTY','').strip())

# Shopify実測（orders first:50, sortKey CREATED_AT desc, financial_status:paid）
ORDERS = [
 ('Tōkyō',[('ムダ毛シェーバー',1)]), ('Yamanashi',[('快適マジックインソール',3),('姿勢サポートチェア',1),('携帯電動シェーバー',1)]),
 ('Ōsaka',[('ナノガラス脱毛パッド',2)]), ('Aichi',[('ナノガラス脱毛パッド',2)]),
 ('Nagasaki',[('バランスケアスリッパ',1)]), ('Aichi',[('接触冷感UVパーカー',1)]),
 ('Gunma',[('ナノガラス脱毛パッド',1)]), ('Fukushima',[('ムダ毛シェーバー',1)]),
 ('Yamaguchi',[('ナノガラス脱毛パッド',1)]), ('Ishikawa',[('ナノガラス脱毛パッド',1)]),
 ('Ōsaka',[('ナノガラス脱毛パッド',1)]), ('Ibaraki',[('4WAY 取り付けOK 小型瞬間冷却ハンディファン',2)]),
 ('Kanagawa',[('形状記憶日傘',1)]), ('Ibaraki',[('ナノガラス脱毛パッド',1)]),
 ('Ōsaka',[('ナノガラス脱毛パッド',1)]), ('Hyōgo',[('姿勢サポートチェア',1)]),
 ('Nara',[('害虫ブロッカー',3)]), ('Tōkyō',[('完全遮光・接触冷感UVハット',1)]),
 ('Kumamoto',[('接触冷感UVアームカバー',1)]), ('Nara',[('2WAYシートボックス',2)]),
 ('Gifu',[('害虫ブロッカー',1)]), ('Ehime',[('ナノガラス脱毛パッド',1)]),
 ('Miyagi',[('W固定スマホ車載ホルダー',1)]), ('Kanagawa',[('ナノガラス脱毛パッド',2)]),
 ('Kanagawa',[('形状記憶日傘',2)]), ('Aichi',[('ナノガラス脱毛パッド',1)]),
 ('Shizuoka',[('偏光・調光サングラス',1)]), ('Nara',[('害虫ブロッカー',2)]),
 ('Kanagawa',[('ナノガラス脱毛パッド',1)]), ('Tōkyō',[('接触冷感UVパーカー',1)]),
 ('Aomori',[('ナノガラス脱毛パッド',2)]), ('Mie',[('ナノガラス脱毛パッド',1)]),
 ('Nara',[('2WAYシートボックス',1)]), ('Kagoshima',[('ナノガラス脱毛パッド',1)]),
 ('Chiba',[('W固定スマホ車載ホルダー',1)]), ('Ōsaka',[('W固定スマホ車載ホルダー',1)]),
 ('Nara',[('完全遮光・接触冷感UVハット',1)]), ('Gifu',[('害虫ブロッカー',3)]),
 ('Aichi',[('偏光・調光サングラス',1)]), ('Shizuoka',[('ナノガラス脱毛パッド',1)]),
 ('Saga',[('形状記憶日傘',1)]), ('Ōsaka',[('4WAY 取り付けOK 小型瞬間冷却ハンディファン',1)]),
 ('Ōsaka',[('ナノガラス脱毛パッド',1)]), ('Hyōgo',[('偏光・調光サングラス',1)]),
 ('Kanagawa',[('害虫ブロッカー',1)]), ('Tōkyō',[('害虫ブロッカー',2)]),
 ('Fukuoka',[('害虫ブロッカー',1)]), ('Kagawa',[('偏光・調光サングラス',1)]),
 ('Shizuoka',[('バランスケアスリッパ',1)]), ('Tōkyō',[('4WAY 取り付けOK 小型瞬間冷却ハンディファン',2)]),
]

# 2026-08-15: 害虫ブロッカー・保温プレートはPSEのため非公開にしたので、文言からも外す
DELISTED = {'害虫ブロッカー', '保温プレート'}

items, seen = [], set()
for pv, lines in ORDERS:
    for name, qty in lines:
        if name == '優先配送' or name in DELISTED: continue
        pref = PREF.get(pv, pv)
        txt = f"🛒 {pref}の方が「{name}」を{qty}個 購入しました" if qty > 1 \
              else f"🛒 {pref}の方が「{name}」を購入しました"
        if txt in seen: continue          # 同じ文言の重複だけ落とす
        seen.add(txt); items.append(txt)

print(f'■ 実注文50件から {len(items)} 本の文言を生成（重複除去後）\n')
for x in items: print('  ' + x)

# 商品の登場回数（偏りの確認）
c = collections.Counter(x.split('「')[1].split('」')[0] for x in items)
print('\n■ 商品ごとの登場回数（実際の売れ方をそのまま反映している）')
for n, v in c.most_common(): print(f'  {n:<34}{v:>3}本')

out = ' | '.join(items)
open('data/lp/marquee-message-2026-08-15.txt', 'w', encoding='utf-8').write(out + '\n')
print(f'\n■ Marqueeの Message 欄に貼る1行（{len(out):,}文字）')
print('  data/lp/marquee-message-2026-08-15.txt に書き出し')
