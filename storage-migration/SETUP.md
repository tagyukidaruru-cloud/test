# STYLE ARCHIVE — 画像を Supabase Storage へ移す手順（Egress 対策）

## 背景
現状、投稿写真とアバターを **base64 のまま DB に保存**しているため、一覧を開くたびに全画像の実体が転送され、Supabase の Egress 無料枠（5GB）を超過している。
対策は「画像は Storage（CDN キャッシュあり）に置き、DB には URL だけ持つ」こと。

- **アプリ側改修は完了済み**（`new-folder/prototype.html`）。新規投稿・アバターは自動で Storage に上がる。
- 残り作業は **(1) バケット作成 (2) 既存データ移行 (3) デプロイ**。(1)(2) は本番に対する作業なので、実施は CEO/本人の GO 後に。

---

## 手順0（移行の前に必須）: DBバックアップを取る

移行(手順2)は**DB書き換えを伴う不可逆操作**。実データ（投稿・アカウント・グループ）が入っているため、**先にバックアップ**を取る。

- Supabase Dashboard → プロジェクト `xwzjrcarawlrcgvynlgh` → **Database → Backups → Download backup**（または Storage内バックアップをダウンロード）
- 取得できたことを確認してから手順2へ。

---

## 手順1: Storage バケットとポリシー作成（Supabase ダッシュボード／要 elevated 権限）

> **重要（セキュリティ）**: 匿名アップロードを許可するが、**無制限にしない**。無制限だと第三者が任意サイズ・任意種別のファイルを大量に置け、今度は Storage 容量と Egress で同じ超過が再発する。**サイズ上限・MIME制限・INSERTのみ**を必ず入れる。

### 1-1. バケット作成（サイズ・MIME制限つき）
Supabase Dashboard → **Storage → New bucket**
- Name: `post-images`
- **Public bucket: ON**（CDN 公開読み取り）
- **Restrict file size: ON → 5 MB**（1ファイル上限）
- **Allowed MIME types**: `image/jpeg, image/png, image/webp` のみ

（上記はバケット設定で入れられる。ダッシュボードに項目が無い版では、下の SQL で bucket の `file_size_limit` / `allowed_mime_types` を設定）

```sql
-- バケット単位のハード制限(ダッシュボードで入れられない場合のフォールバック)
update storage.buckets
  set public = true,
      file_size_limit = 5242880,               -- 5MB
      allowed_mime_types = array['image/jpeg','image/png','image/webp']
  where id = 'post-images';
```

### 1-2. RLSポリシー（**匿名はINSERTのみ**。UPDATE/DELETEは渡さない）
アプリと移行ツールは**キーを毎回ユニーク化**したので、上書き(UPDATE)も削除も匿名には不要。これにより「第三者が他人の画像を上書き/削除」する経路を塞ぐ。

```sql
-- 読み取り: publicバケットなので公開(明示)
create policy "public read post-images"
  on storage.objects for select to public
  using (bucket_id = 'post-images');

-- 書き込み: 匿名はINSERTのみ許可(サイズ/MIMEはバケット側で強制)
create policy "anon insert post-images"
  on storage.objects for insert to anon
  with check (bucket_id = 'post-images');

-- UPDATE / DELETE ポリシーは作らない = 匿名は上書き・削除不可
```

> **本当の所有者制御について（正直な注記）**: このアプリは現在 anon キーだけで動作し、ユーザー認証(auth.uid())が無いため、「所有者のみ更新/削除」をRLSで厳密に強制することはできない。上の「INSERTのみ＋サイズ/MIME制限」が anon 運用での現実的な最善。厳密な所有者制御が要るなら Supabase Auth 導入が必要（別途大きめの改修。CEO判断待ちの将来課題）。

---

## 手順2: 既存 base64 の移行

1. `storage-migration/migrate.html` をブラウザで開く（ローカルでファイルを直接開くか、`python3 -m http.server` 経由）。
2. **① ドライラン** を押す → 対象枚数と転送量が出る（読み取りのみ・無害）。
3. 問題なければ **② 実行** → Storage へアップロードし、DB の `before_img/after_img` と `saves.bg(u)` を URL(JSON) に書き換える。
4. 完了ログを確認。

移行後のデータ形式:
- `posts.before_img / after_img` … `{"f":"…原寸URL","t":"…サムネURL"}`（旧 `data:` は自動で無視され二重移行しない）
- `saves.bg` … `{"u":"…URL","sz":"…","ps":"…"}`

---

## 手順3: アプリを本番へデプロイ

改修済み `new-folder/prototype.html` を配信先へ反映:

```bash
cd /Users/uuto/Downloads/test
for f in docs/index.html public/index.html 公開用/index.html; do cp new-folder/prototype.html "$f"; done
git add -A && git commit -m "画像をSupabase Storageへ移行しDBはURLのみ保持(Egress対策)" && git push
```

- GitHub Pages: `docs/` を配信 → push で反映（10分キャッシュ）
- Netlify: `公開用/` を配信
- ⚠️ **Netlify はクレジット枯渇で新規デプロイが止まっている可能性**。その場合 `公開用/` は古いまま更新されず、GitHub Pages(`docs/`)だけ新しくなって**食い違う**。→ 下の「配信の一本化」を参照。

---

## 実行タイミング（CEO/秘書の指示）
- **手順1（バケット作成）**: CEO操作で5分程度。今日〜8/2 のうちでOK。
- **手順0・2・3（バックアップ→移行→デプロイ）**: **8/4(月)以降**に実施。8/3 は bloom 商談があり STYLE ARCHIVE に注意を割かない。期限は 8/7。
- いずれも**本人(CEO)の明示GO後**に着手。

---

## 配信の一本化（移行後にCEOへ提案）
現状 **GitHub Pages(`docs/`) と Netlify(`公開用/`) の2系統**が並立。2系統は「片方だけ更新→表示が食い違う」リスクがあり、Netlify はクレジット枯渇で新規デプロイも不安定。

- **推奨: GitHub Pages に一本化**（無料・容量無制限・デプロイ制約なし・既に稼働中）。
- 課題: CEO/利用者のブックマークが Netlify(`majestic-nasturtium-a43a04`)。URLが変わる。
- 移行策の候補:
  1. GitHub Pages に**独自ドメイン**を設定し、そのURLに統一（ブックマークはドメインごと移せる）。
  2. Netlify側は「Pages へ転送」だけ残す（ただし Netlify 更新にはデプロイ枠が要る）。
- **判断はCEOへ**。決まるまでは手順3で**両方に反映**して食い違いを防ぐ。

---

## 効果の確認（Egress実測・課金判断の材料）
- 移行**前**の Egress 値を控えておく（現状 9.548/5GB=191%）。
- デプロイ後、ホーム一覧を開いた時のネットワーク転送量を DevTools で確認（画像は Storage の CDN から、2回目以降はキャッシュ）。
- 数日運用して Supabase → Reports → Egress の伸びを計測し、**移行前後を比較**して秘書へ報告。無料枠で収まる見込みが立つかが課金判断の材料。足りなければ実測値を添えて課金判断へ。

## 後片付け（任意）
移行してしばらく問題なければ、DB に残った旧 base64 は既に URL で上書き済みなので追加対応は不要。バックアップを取ってあれば安心。
