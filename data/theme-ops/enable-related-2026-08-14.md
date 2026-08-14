# 関連商品セクションを全商品テンプレートで表示にする（2026-08-14）

対象テーマ: 20260226（MA時LP）rev20260226 / MAIN
gid://shopify/OnlineStoreTheme/159681577202

## 変更内容
各 templates/product*.json の `"related-products"` セクションから
`"disabled": true,` の1行を削除する。他は一切変更しない。

## 元に戻す方法
同じ位置に `"disabled": true,` を書き戻す。
（変更が1行の削除のみなので、フルバックアップは不要）

## 判定
2026-08-22 に scripts/adhoc/reco_baseline0814.py の基準で評価する。

## 実行状況
2026-08-14: **未実行**。このセッションのShopify MCP接続は読み取り専用で、
graphql_mutation もテーマ書き込み系ツールも利用できないため、こちらからは
書き換えられない。ユーザーが管理画面のコードエディタ / Shopify CLI で実行するか、
write_themes スコープのAdmin APIトークンを渡してもらう必要がある。

## 注意
各テンプレートには `"disabled": true` が複数箇所ある（Selleasyのアップセル
ウィジェット、未使用のFAQタブなど）。消すのはファイル末尾の
`"related-products"` ブロック内の1つだけ。

## Shopify CLI でやる場合
```
shopify theme pull --theme 159681577202 --only 'templates/product*.json'
perl -0pi -e 's/("type":\s*"related-products",\s*)"disabled":\s*true,\s*/$1/s' templates/product*.json
shopify theme push --theme 159681577202 --only 'templates/product*.json'
```

## オン時の表示設定（現状の値）
heading「よく一緒に購入されている商品」/ products_to_show 10 /
columns_desktop 6 / columns_mobile 2 / 位置は main セクションの下

## 対象ファイル
- [ ]  1. templates/product.json
- [ ]  2. templates/product.3waycirculator.json
- [ ]  3. templates/product.4waykogatahandy.json
- [ ]  4. templates/product.5waykoshikake.json
- [ ]  5. templates/product.ashiuracare.json
- [ ]  6. templates/product.carholder.json
- [ ]  7. templates/product.chair.json
- [ ]  8. templates/product.cleaner.json
- [ ]  9. templates/product.datumoupad.json
- [ ] 10. templates/product.dendoushaver.json
- [ ] 11. templates/product.dendoutorimaer.json
- [ ] 12. templates/product.dis.json
- [ ] 13. templates/product.gaityu.json
- [ ] 14. templates/product.gauzeonepic.json
- [ ] 15. templates/product.haisou.json
- [ ] 16. templates/product.handyfan.json
- [ ] 17. templates/product.insole.json
- [ ] 18. templates/product.koshipack.json
- [ ] 19. templates/product.kyouseibelt.json
- [ ] 20. templates/product.massage.json
- [ ] 21. templates/product.mat.json
- [ ] 22. templates/product.mixer.json
- [ ] 23. templates/product.nosemassage.json
- [ ] 24. templates/product.poncho.json
- [ ] 25. templates/product.recoverysandals.json
- [ ] 26. templates/product.reikanku-ra-.json
- [ ] 27. templates/product.shoes.json
- [ ] 28. templates/product.shower-head.json
- [ ] 29. templates/product.soap.json
- [ ] 30. templates/product.styleupinnner.json
- [ ] 31. templates/product.sunglass.json
- [ ] 32. templates/product.umb.json
- [ ] 33. templates/product.umb2.json
- [ ] 34. templates/product.uvarmer.json
- [ ] 35. templates/product.uvhat.json
- [ ] 36. templates/product.uvparker.json
- [ ] 37. templates/product.uvtoothe.json
- [ ] 38. templates/product.waterflosser.json

計 38 ファイル
