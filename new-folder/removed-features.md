# 削除した機能のログ（復元用）

プロトタイプから削除したが、今後復活させる可能性のある機能のマークアップを残しておく。

## 投稿フロー「工程と時間」ステップ（2026-07-02 削除）

もともと投稿フローのステップ4（全5ステップ中）にあった画面。
復元する場合は `prototype.html` の「ステップ4: 仕上げと公開」の直前に以下を挿入し、
仕上げと公開の `data-step` を `5` に戻す。

```html
<!-- ステップ4: 工程 -->
<div class="form-body form-step" data-step="4" hidden>
  <div class="form-step-title">
    <h2>工程と時間</h2>
    <p>放置時間と塗り分けを記録</p>
  </div>
  <div class="form-fieldset">
    <div class="field">
      <label>放置時間<span class="req">*</span></label>
      <input type="text" id="f-time" value="25 min">
    </div>
    <div class="field">
      <label>工程メモ</label>
      <textarea style="min-height:140px;">STEP1: 根元リタッチ(5/13 + OX6%)
STEP2: 中間〜毛先 6/13:6/00:Ash-8 塗布
STEP3: 25分放置
STEP4: 流し→シャンプー→TR→ドライ</textarea>
    </div>
  </div>
</div>
```

### あわせて戻す必要がある変更

1. **ステッパーのドット**: `data-step="5"` のドットを1つ追加し、`st-num` の初期表示を `1 / 5` に戻す。
2. **JS**: `var totalSteps = 4;` → `5` に戻す。
3. **投稿データ**: `submitPost()` の post オブジェクトに以下を追加する。
   ```js
   time: document.getElementById("f-time").value,
   ```
4. **カード表示（任意）**: `makePostCard()` の case-meta に放置時間タグを追加する場合:
   ```js
   (post.time ? '<span class="tag accent">' + esc(post.time) + '</span>' : '') +
   ```

### 備考

- 施術詳細画面（モーダル）の「工程」タブは削除しておらず、現在も残っている。
- 投稿ステップ3にあった「ブリーチ有無」セレクタ（なし/履歴あり/1回/2回以上 の damage-slider）も
  2026-07-02 に削除した。JSからの参照はなかったため、復元はマークアップの追加のみでよい。
