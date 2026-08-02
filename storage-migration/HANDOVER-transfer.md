# リポジトリ移管 申し送り一覧（tagyukidaruru-cloud/test → lunard-jp/style-archive）

---
## ✅ ストレージ移行 完了記録（2026-08-01 実行・本番検証済み）
CEO明示GO（8/4予定を前倒し）で 手順0〜3＋実測 を完了。

**実測値（Egress対策の効果）**
- 一覧クエリ posts payload: **3,022,182 bytes → 2,195 bytes（約99.9%減）**
- DBから除去した base64 実体: 2.16 MB / 移行画像 15枚・8投稿・エラー0
- 画像配信: 原寸URL 200 image/jpeg（例117KB）／導出サムネ `_t.jpg` 200 image/jpeg（例15.7KB）＝Storage CDN
- ライブ(GitHub Pages)実サイト: 新コード反映済み、ホーム全タイルが Storage サムネから描画、base64=0
- データ欠損: なし（posts8/accounts5/saves12/groups2＝バックアップと一致。移行は before_img/after_img のみ変更）
- バックアップ: `/Users/uuto/Desktop/style-archive-backup-20260801/`（全4テーブル・リポジトリ外）

**残課題**
1. **Netlify(公開用/)は旧コードのまま**（クレジット枯渇で再デプロイ不可）。素URL方式なので表示は崩れないが、旧コードは一覧で原寸を読む（サムネ最適化が効かない）。→ 配信一本化（Pages）で解消。
2. **数日 Egress を監視**し 8/7 枠内を確認（移行前191%との比較）。
3. 検証用テスト画像 `post-images/verify/test-*.png`（69B×1）が残存（匿名DELETE不可の設計上、消すならダッシュボード）。
4. その後の Pages一本化＋lunard-jp移管（本書の本題・秘書gh実務）。
5. gh認証は当面 tagyukidaruru-cloud（移管実務でも使用）。

---


対象: GitHub Pages 一本化＋lunard-jp へ移管（想定URL `https://lunard-jp.github.io/style-archive/`）
**前提の実行順序（厳守）**: Egress対応（バケット作成→移行→デプロイ→実測報告）が完了してから、この移管に着手する。移管の gh 実務は秘書が担当。

---

## 0. 事前調査の結論（コード側は移管に強い）
- **旧URL/ホスト名のハードコードなし**（`tagyukidaruru-cloud.github.io` / `netlify` / `github.io` の grep=0件）。
- **CNAMEなし＝独自ドメイン不使用**。素の `github.io` サブパス運用なので、URLは `.../style-archive/` になる。
- **絶対 `/test/` 依存なし・`<base>`なし・assetsは相対参照**（`url('assets/…')`）→ サブパスが `/test/`→`/style-archive/` に変わっても**アプリは壊れない**。
- **Supabase バックエンドは絶対URLで無関係** → アカウント・投稿・グループ等の実データは移管後もそのまま（利用者のデータは消えない）。

---

## 1. ローカルの git remote 付け替え
移管（owner変更＋リネーム）後、ローカルのremoteを新URLへ:
```bash
cd /Users/uuto/Downloads/test   # ※リポジトリを~/Downloads外へ移すのは別タスク(後述)
git remote set-url origin https://github.com/lunard-jp/style-archive.git
git remote -v   # 確認
```
- GitHubは旧URLを一定期間リダイレクトするが、明示更新が安全。
- 現在: `origin = https://github.com/tagyukidaruru-cloud/test.git`

## 2. 自動commitスクリプト／plist の参照
`~/Library/Application Support/lunard-autocommit/autocommit.sh`
- `REPO_DIR="/Users/uuto/Downloads/test"` … **リポジトリの実ディレクトリを移す場合はここを更新**（remote名は `origin` 参照なので、上の set-url を行えばスクリプト側の remote 修正は不要）。
- `git push origin main` … remote名 `origin` のまま。set-url済みなら追従。
- LaunchAgent: `com.uuto.test-autocommit`（ログ出力は Application Support 側）。
- ⚠️ 既知の恒久課題（別タスク・Egress後）: `~/Downloads` は TCC 保護で launchd から入れず**autocommitは成功していない**。リポジトリを ~/Downloads の外へ移すのが恒久対応。**移管とディレクトリ移動を同時にやらない**（切り分け不能になる）。移動する順序も Egress→移管→(その後で)ディレクトリ移動、が無難。

## 3. 旧URLのハードコード grep
- 結果: **0件**（コード修正不要）。
- 補足: リポジトリ内に旧ログ `/.claude/scripts/autocommit.log`（追跡済み・14KB・7/21で停止）が残存。実害なしだが、移管時に削除しておくと綺麗（現行ログは Application Support 側）。

## 4. Netlify の扱い（**推奨A で確定**／秘書判断・CEO包括承認）
現状 Netlify `majestic-nasturtium-a43a04`（公開用/配信）＝CEOブックマーク。クレジット枯渇で新規デプロイ不安定。
- **確定: 推奨A** = 新Pages URLの稼働を確認 → CEO/test groupへ新URL共有 → **その後に Netlifyサイトを停止(unpublish)**。
- **順序厳守**: 稼働確認より先に停止しない（稼働確認 → 周知 → 停止）。
- 却下: 推奨B（301転送）。理由=①転送にNetlifyデプロイ枠を消費（枯渇が一本化の動機なので本末転倒）②2系統管理が残り一本化の目的が半減。
- 参考SQL/設定は不要（停止のみ）。

## 5. 利用者へのURL変更周知
- 影響: **CEO本人 ＋ test group メンバー**（＝Supabase上のアカウント保有者）。データは不変、必要なのは**新URLの共有のみ**。
- 旧URLの挙動: 移管後、旧 `tagyukidaruru-cloud.github.io/test/` はGitHub Pagesのリダイレクト保証が弱く**404になり得る**。Netlify旧URLは上の4次第。
- 推奨: 人数が少ないので、**新URLを直接周知**（＋必要なら移行期間だけNetflix…Netlify転送を残す）。周知先=CEO＋グループ内アナウンス。

---

## 6. 移管当日チェック（秘書のgh実務と併走）
- [ ] 新リポジトリ `lunard-jp/style-archive` で **Pages 有効（source = main / `docs`）** を確認（`https://lunard-jp.github.io/style-archive/` が200）。
- [ ] ローカル `git remote set-url`（項目1）→ `git push` 疎通確認。
- [ ] Netlify を停止 or 転送（項目4の決定に従う）。
- [ ] 新URLで **画像がStorageから表示**されること、ログイン・投稿・グループが動くことを実機確認。
- [ ] CEO＋グループへ新URL周知（項目5）。
- [ ] （任意）旧 `.claude/scripts/autocommit.log` 削除。

## セキュリティ注記
- 公開リポジトリのまま lunard-jp へ移る。埋め込みは **anon キーのみ**（service_role キーは不在＝既確認）。露出レベルは現状と同じ。
