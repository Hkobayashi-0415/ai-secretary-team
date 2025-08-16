# Phase 11: UI/UX設計書 - アクセシビリティ設計

## 1. 設計概要

### 1.1 設計目的
統合版プラットフォームのアクセシビリティ設計において、障害の有無・年齢・技術的制約に関係なく、すべてのユーザーが平等に利用できる包括的なアクセシビリティ仕様を定義する。

### 1.2 設計の役割
- **包括的デザイン**: 全ユーザーを対象とした設計
- **法的準拠**: WCAG 2.1 AA準拠の実現
- **ユーザビリティ向上**: 全ユーザーの使いやすさ向上
- **技術的対応**: 支援技術との適切な連携
- **継続的改善**: アクセシビリティの継続的向上

### 1.3 対象ユーザー
- **視覚障害**: 全盲・弱視・色覚異常
- **聴覚障害**: 全聾・難聴
- **運動障害**: 上肢・下肢の制限
- **認知障害**: 学習障害・注意力障害
- **高齢者**: 加齢による能力変化
- **一時的制約**: 片手操作・騒音環境

## 2. WCAG 2.1準拠設計

### 2.1 レベルA準拠
**基本的なアクセシビリティ**:
- **代替テキスト**: 画像・動画の適切な説明
- **キーボード操作**: マウスなしでの完全操作
- **時間制限**: 十分な操作時間の提供
- **色の使用**: 色以外の情報提供

**実装例**:
```html
<!-- 代替テキスト -->
<img src="icon.png" alt="新規作成アイコン">

<!-- キーボード操作 -->
<button tabindex="0" onkeydown="handleKeyDown(event)">
  新規作成
</button>

<!-- 時間制限 -->
<div aria-live="polite">
  残り時間: <span id="timer">30</span>秒
</div>
```

### 2.2 レベルAA準拠
**高度なアクセシビリティ**:
- **コントラスト比**: 4.5:1以上の十分なコントラスト
- **フォントサイズ**: 200%ズームでの可読性
- **フォーカス表示**: 明確なフォーカスインジケーター
- **エラー識別**: エラーの明確な識別・説明

**実装例**:
```css
/* コントラスト比 */
.text-primary {
  color: #1a1a1a; /* 背景色: #ffffff, コントラスト比: 15.6:1 */
}

/* フォーカス表示 */
.button:focus {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}

/* エラー表示 */
.input-error {
  border: 2px solid #d32f2f;
  background-color: #ffebee;
}
```

### 2.3 レベルAAA準拠（推奨）
**最高レベルのアクセシビリティ**:
- **コントラスト比**: 7:1以上の高コントラスト
- **音声制御**: 音声コマンドでの操作
- **動的コンテンツ**: 動的変更の適切な通知
- **入力支援**: 入力ミスの防止・修正支援

## 3. 視覚的アクセシビリティ

### 3.1 色覚異常対応
**色以外の情報提供**:
- **アイコン**: 色に加えてアイコンでの識別
- **パターン**: 色に加えてパターンでの識別
- **テキスト**: 色に加えてテキストでの識別
- **コントラスト**: 十分なコントラスト比の確保

**実装例**:
```css
/* 色覚異常対応 */
.status-success {
  color: #2e7d32;
  background-color: #e8f5e8;
  border-left: 4px solid #2e7d32;
}

.status-error {
  color: #c62828;
  background-color: #ffebee;
  border-left: 4px solid #c62828;
}

/* アイコン追加 */
.status-success::before {
  content: "✓";
  margin-right: 8px;
}

.status-error::before {
  content: "✗";
  margin-right: 8px;
}
```

### 3.2 視力障害対応
**拡大・縮小対応**:
- **ズーム対応**: 200%ズームでの表示確認
- **フォントサイズ**: ユーザー設定の尊重
- **行間**: 読みやすい行間設定
- **余白**: 適切な要素間の余白

**高コントラスト対応**:
```css
/* 高コントラストモード対応 */
@media (prefers-contrast: high) {
  .button {
    border: 2px solid currentColor;
    background-color: transparent;
  }
  
  .text {
    font-weight: bold;
  }
}
```

### 3.3 全盲対応
**スクリーンリーダー対応**:
- **セマンティックHTML**: 適切なHTML要素の使用
- **ARIA属性**: 状態・関係性の適切な通知
- **見出し構造**: 論理的な見出し階層
- **ランドマーク**: 主要セクションの識別

**実装例**:
```html
<!-- セマンティックHTML -->
<main role="main">
  <h1>ダッシュボード</h1>
  
  <section aria-labelledby="stats-heading">
    <h2 id="stats-heading">統計情報</h2>
    <div role="region" aria-label="統計データ">
      <!-- 統計データ -->
    </div>
  </section>
</main>

<!-- ARIA属性 -->
<button aria-expanded="false" aria-controls="menu">
  メニュー
</button>
<div id="menu" aria-hidden="true">
  <!-- メニュー内容 -->
</div>
```

## 4. 聴覚的アクセシビリティ

### 4.1 音声コンテンツ対応
**字幕・音声解説**:
- **字幕**: 動画・音声の文字起こし
- **音声解説**: 視覚情報の音声説明
- **手話**: 手話動画の提供
- **テキスト版**: 音声コンテンツのテキスト版

**実装例**:
```html
<!-- 字幕付き動画 -->
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="subtitles" src="subtitles-ja.vtt" srclang="ja" label="日本語">
  <track kind="subtitles" src="subtitles-en.vtt" srclang="en" label="English">
</video>

<!-- 音声解説 -->
<audio controls>
  <source src="audio.mp3" type="audio/mpeg">
  <track kind="descriptions" src="descriptions-ja.vtt" srclang="ja" label="日本語解説">
</audio>
```

### 4.2 音声制御対応
**音声コマンド**:
- **音声認識**: 音声入力での操作
- **音声フィードバック**: 操作結果の音声通知
- **音量調整**: ユーザー設定の音量調整
- **音声無効化**: 音声の無効化オプション

**実装例**:
```javascript
// 音声認識
if ('webkitSpeechRecognition' in window) {
  const recognition = new webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  
  recognition.onresult = function(event) {
    const command = event.results[event.results.length - 1][0].transcript;
    executeVoiceCommand(command);
  };
}

// 音声フィードバック
function speak(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';
    speechSynthesis.speak(utterance);
  }
}
```

## 5. 運動障害対応

### 5.1 キーボード操作
**完全キーボード操作**:
- **Tab順序**: 論理的なTab移動順序
- **ショートカット**: 頻繁な操作のショートカット
- **フォーカス管理**: 適切なフォーカス移動
- **スキップリンク**: 主要コンテンツへの直接移動

**実装例**:
```html
<!-- スキップリンク -->
<a href="#main-content" class="skip-link">
  メインコンテンツにスキップ
</a>

<!-- ショートカット -->
<button accesskey="n" title="Alt+N">
  新規作成
</button>

<!-- フォーカス管理 -->
<div tabindex="-1" id="main-content">
  <!-- メインコンテンツ -->
</div>
```

**キーボードナビゲーション**:
```javascript
// カスタムキーボードナビゲーション
document.addEventListener('keydown', function(event) {
  switch(event.key) {
    case 'ArrowRight':
      navigateNext();
      break;
    case 'ArrowLeft':
      navigatePrevious();
      break;
    case 'Enter':
      activateCurrent();
      break;
    case 'Escape':
      closeModal();
      break;
  }
});
```

### 5.2 入力支援
**入力の最適化**:
- **大きなターゲット**: 操作しやすい要素サイズ
- **十分な間隔**: 誤操作を防ぐ要素間隔
- **入力検証**: リアルタイムでの入力検証
- **自動補完**: 入力内容の自動補完

**実装例**:
```css
/* 大きなターゲット */
.button, .link, .input {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
}

/* 十分な間隔 */
.form-group {
  margin-bottom: 24px;
}

.form-control {
  margin-bottom: 16px;
}
```

## 6. 認知障害対応

### 6.1 理解しやすさ
**シンプルな設計**:
- **明確な構造**: 論理的な情報構造
- **一貫性**: 統一されたデザイン・操作
- **予測可能性**: 操作結果の予測可能性
- **エラー防止**: 誤操作の防止

**実装例**:
```html
<!-- 明確な構造 -->
<nav aria-label="メインナビゲーション">
  <ul>
    <li><a href="/dashboard" aria-current="page">ダッシュボード</a></li>
    <li><a href="/projects">プロジェクト</a></li>
    <li><a href="/tasks">タスク</a></li>
  </ul>
</nav>

<!-- 一貫性のある操作 -->
<button class="btn btn-primary" type="submit">
  保存
</button>
<button class="btn btn-secondary" type="button">
  キャンセル
</button>
```

### 6.2 注意・記憶支援
**注意の維持**:
- **段階的表示**: 情報の段階的表示
- **進捗表示**: 処理進捗の明確な表示
- **確認ダイアログ**: 重要な操作の確認
- **自動保存**: データの自動保存

**記憶の支援**:
```html
<!-- 進捗表示 -->
<div role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100">
  <div class="progress-bar" style="width: 75%"></div>
  <span class="sr-only">75%完了</span>
</div>

<!-- 確認ダイアログ -->
<dialog id="confirm-dialog" aria-labelledby="confirm-title">
  <h2 id="confirm-title">確認</h2>
  <p>本当に削除しますか？</p>
  <button onclick="confirmDelete()">削除</button>
  <button onclick="closeDialog()">キャンセル</button>
</dialog>
```

## 7. 高齢者対応

### 7.1 視認性向上
**読みやすさの向上**:
- **フォントサイズ**: 適切なフォントサイズ
- **行間**: 読みやすい行間設定
- **コントラスト**: 十分なコントラスト比
- **余白**: 適切な要素間の余白

**実装例**:
```css
/* 高齢者向け設定 */
.accessible-text {
  font-size: 18px;
  line-height: 1.6;
  letter-spacing: 0.5px;
}

.accessible-button {
  font-size: 16px;
  padding: 16px 24px;
  border-radius: 8px;
}

.accessible-input {
  font-size: 16px;
  padding: 12px 16px;
  border: 2px solid #ccc;
}
```

### 7.2 操作の簡素化
**操作の最適化**:
- **大きなボタン**: 操作しやすいボタンサイズ
- **明確なラベル**: 分かりやすいラベル
- **段階的操作**: 複雑な操作の段階化
- **ヘルプ機能**: 操作支援のヘルプ機能

## 8. 支援技術対応

### 8.1 スクリーンリーダー対応
**適切な情報提供**:
- **見出し構造**: h1-h6の適切な使用
- **リスト**: ul, ol, dlの適切な使用
- **テーブル**: th, captionの適切な使用
- **フォーム**: label, fieldsetの適切な使用

**実装例**:
```html
<!-- 適切な見出し構造 -->
<h1>メインページ</h1>
<h2>セクション1</h2>
<h3>サブセクション1.1</h3>

<!-- 適切なリスト -->
<ul>
  <li>項目1</li>
  <li>項目2</li>
  <li>項目3</li>
</ul>

<!-- 適切なテーブル -->
<table>
  <caption>ユーザー一覧</caption>
  <thead>
    <tr>
      <th scope="col">名前</th>
      <th scope="col">メール</th>
      <th scope="col">役割</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>田中太郎</td>
      <td>tanaka@example.com</td>
      <td>管理者</td>
    </tr>
  </tbody>
</table>
```

### 8.2 音声ブラウザ対応
**音声での情報提供**:
- **代替テキスト**: 画像の適切な説明
- **音声順序**: 論理的な音声読み上げ順序
- **音声ランドマーク**: 主要セクションの音声識別
- **音声ナビゲーション**: 音声での効率的なナビゲーション

### 8.3 点字ディスプレイ対応
**点字での情報提供**:
- **テキスト情報**: 点字変換可能なテキスト
- **構造情報**: 点字での構造理解
- **ナビゲーション**: 点字でのナビゲーション
- **入力支援**: 点字での入力支援

## 9. テスト・検証

### 9.1 自動テスト
**ツールによる検証**:
- **Lighthouse**: Googleのアクセシビリティ監査
- **axe**: Dequeのアクセシビリティテスト
- **WAVE**: WebAIMのアクセシビリティ評価
- **HTML_CodeSniffer**: HTMLのアクセシビリティチェック

**実装例**:
```javascript
// axe-coreによるテスト
import axe from 'axe-core';

// ページ全体のテスト
axe.run(function(err, results) {
  if (err) {
    console.error('アクセシビリティテストエラー:', err);
    return;
  }
  
  if (results.violations.length > 0) {
    console.log('アクセシビリティ違反:', results.violations);
  } else {
    console.log('アクセシビリティテスト完了');
  }
});
```

### 9.2 手動テスト
**ユーザビリティテスト**:
- **キーボード操作**: マウスなしでの完全操作
- **スクリーンリーダー**: 音声での情報理解
- **ズーム対応**: 200%ズームでの表示確認
- **高コントラスト**: 高コントラストモードでの表示確認

**テストチェックリスト**:
```markdown
## アクセシビリティテストチェックリスト

### キーボード操作
- [ ] Tabキーでの移動が論理的
- [ ] すべての操作がキーボードで可能
- [ ] フォーカスが明確に表示される
- [ ] ショートカットが適切に動作

### スクリーンリーダー
- [ ] 見出し構造が適切
- [ ] 画像に代替テキストがある
- [ ] フォームに適切なラベルがある
- [ ] テーブルが適切に構造化されている

### 視覚的アクセシビリティ
- [ ] コントラスト比が十分
- [ ] 色以外の情報提供がある
- [ ] フォントサイズが適切
- [ ] ズーム対応が適切
```

## 10. 実装ガイドライン

### 10.1 HTML実装
**セマンティックHTML**:
```html
<!-- 適切なHTML要素の使用 -->
<main role="main">
  <header role="banner">
    <nav role="navigation" aria-label="メインナビゲーション">
      <!-- ナビゲーション -->
    </nav>
  </header>
  
  <aside role="complementary" aria-labelledby="sidebar-title">
    <h2 id="sidebar-title">サイドバー</h2>
    <!-- サイドバーコンテンツ -->
  </aside>
  
  <footer role="contentinfo">
    <!-- フッターコンテンツ -->
  </footer>
</main>
```

**ARIA属性**:
```html
<!-- 状態の通知 -->
<button aria-expanded="false" aria-controls="menu">
  メニュー
</button>
<div id="menu" aria-hidden="true">
  <!-- メニュー内容 -->
</div>

<!-- 関係性の説明 -->
<label for="username">ユーザー名</label>
<input id="username" type="text" aria-describedby="username-help">
<div id="username-help">ユーザー名は3文字以上で入力してください</div>
```

### 10.2 CSS実装
**フォーカス表示**:
```css
/* フォーカス表示 */
.focusable:focus {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}

/* 高コントラストモード */
@media (prefers-contrast: high) {
  .focusable:focus {
    outline: 3px solid currentColor;
    outline-offset: 2px;
  }
}

/* フォーカス可視性 */
.focusable:focus-visible {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}
```

**メディアクエリ**:
```css
/* ユーザー設定の尊重 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

@media (prefers-color-scheme: dark) {
  :root {
    --background-color: #1a1a1a;
    --text-color: #ffffff;
  }
}
```

### 10.3 JavaScript実装
**アクセシビリティ対応**:
```javascript
// フォーカス管理
function manageFocus(modal) {
  const focusableElements = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];
  
  // フォーカストラップ
  lastElement.addEventListener('keydown', function(e) {
    if (e.key === 'Tab' && !e.shiftKey) {
      e.preventDefault();
      firstElement.focus();
    }
  });
  
  firstElement.addEventListener('keydown', function(e) {
    if (e.key === 'Tab' && e.shiftKey) {
      e.preventDefault();
      lastElement.focus();
    }
  });
}

// ライブリージョン
function announceToScreenReader(message) {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}
```

## 11. 継続的改善

### 11.1 監視・測定
**アクセシビリティメトリクス**:
- **WCAG準拠率**: 各レベルでの準拠率
- **エラー率**: アクセシビリティエラーの発生率
- **ユーザビリティ**: アクセシビリティユーザーの満足度
- **パフォーマンス**: 支援技術での動作性能

### 11.2 フィードバック収集
**ユーザーフィードバック**:
- **障害者ユーザー**: 実際の使用体験からのフィードバック
- **支援技術ユーザー**: スクリーンリーダー等での使用体験
- **専門家評価**: アクセシビリティ専門家による評価
- **継続的監査**: 定期的なアクセシビリティ監査

## 12. まとめ

アクセシビリティ設計の詳細設計書が完成しました。この設計書では以下の特徴を実現しています：

### 12.1 主要な特徴
- **包括的デザイン**: 全ユーザーを対象とした設計
- **WCAG準拠**: 国際標準に準拠したアクセシビリティ
- **支援技術対応**: スクリーンリーダー等との適切な連携
- **継続的改善**: アクセシビリティの継続的向上
- **ユーザビリティ**: 全ユーザーの使いやすさ向上

### 12.2 設計のポイント
- **平等性**: 障害の有無に関係ない平等な利用
- **包括性**: 全ユーザーを考慮した設計
- **標準準拠**: 国際標準への準拠
- **実用性**: 実際の使用に適した実装
- **将来性**: 新技術・新要件への対応

### 12.3 次のステップ
この設計書を基に、以下の設計書作成を進めます：
- パフォーマンス設計

各設計書においても、高度推論を活用し、包括的で実用的な設計を提供いたします。
