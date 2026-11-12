# 外部調査（ウェブ検索・2026-11-12 19時台）: 「Metaのアップデートでおかしくなっている説」

調査はウェブ検索と、別のエージェントによるページの読み取り（Shopify・Metaのデータには触れていない）。Xの投稿（https://x.com/PhilKiel/status/2120259704849060099）は HTTP 402 で読めなかった。

## 障害・不具合
- Metaの公式の障害発表は見つからなかった。第三者の状況ページ: StatusGator は 11/10 02:00 UTC 時点で正常（11/9 に35分の警告）https://statusgator.com/services/meta ／ Ads Manager の履歴は最新が 9/22 の配信障害 https://metastatus.com/ads-manager/history

## 11/9〜11/12 に日付のある変更
- **11/12: Pixel の設定「Measure conversions on customer devices」（顧客の端末で購入を計測する）が既定でオン**。EU・英国は対象外（日本は除外の記載なし）。変わるのは主に「Metaが数える購入数」。入札・最適化に効くかは記事によって食い違う（効くと読める／未確認／意見が割れている）。Events Manager → データソース → Pixel → 設定で切り替え。
  - https://ppc.land/meta-pixel-will-count-more-conversions-from-nov-12-unless-advertisers-opt-out/ ／ https://www.metricmaven.io/blog/meta-measure-conversions-on-customer-devices ／ https://tofuads.com/resources/meta-measure-conversions-customer-devices ／ https://note.com/threeplussix/n/n8f395a369bb7 ／ https://admakeai.com/blog/meta-ads-updates-november-2026 ／ https://admanage.ai/blog/meta-ads-update ／ https://theecommerceoperator.substack.com/p/black-friday-cpms-started-climbing
  - 適用条件として「Pixelをページに直接設置し、メールアドレスか電話番号でのログインを求めるサイト」と書く記事あり（MetricMaven の整理・note 経由）
- 11/10: Marketing API v24.0 の停止（admakeai の要約部分のみ・未検証）

## 10月の変更（admakeai・admanage）
- 10/28〜: 既存の広告に「商品の閲覧」（タップ後の行き先が Meta 側の商品ページ）を既定でオン（一部アカウントのみとの報告）
- 10/19〜: 販売キャンペーンで「広告ごとのオーディエンス」が既定オン（他の人にも届く場合あり）
- 10/12〜: 販売・リード・アプリの広告セットで配置の除外ができなくなった
- 10/8〜: TikTokへのリンクを含む広告の配信停止（日本を含む7か国）
- 10/13: Meta が広告推薦AI（GEM）を公表。広告主の設定項目の追加はなし（marketingone https://marketingone.co.jp/web-ads-update-2026-11/）

## 不調の報告
- 日本の運用者の note（2026/11/8）https://note.com/topcast/n/n102e14ddf97c : 「2026年10月以降、Meta広告のパフォーマンスが明らかに悪い」「CTRやCPCは悪くないのにCVが出ない」「新規キャンペーンは初動だけ…その後は急激に悪化」。データセット・広告アカウントを替えても「改善せず」、過去の勝ちクリエイティブの少額配信で「微妙に回復傾向」。筆者は「原因はまだ特定できていません」「Metaの公式な仕様変更と…因果関係を示すものではありません」と明記。10月にこの筆者の広告主のページで購入タグの誤発火があったとも書いている
- Reddit のスレッド題「50% conversion drop after 10/18」（admakeai が題名だけ紹介・中身は未確認）
- 表示単価: 米国では今年は9月から上昇（Birch の米国データ・10月の月平均CPM 前年比 +34.6%）。Meta の Q3 決算で広告1件あたりの単価が全地域で前年比 +14%（theecommerceoperator・admakeai）
