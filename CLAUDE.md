# LLM Wiki：LiDAR 3D Object Detection

這個 repo 是一個由 LLM 維護的知識庫（LLM Wiki），主題是 LiDAR 點雲 3D 物件偵測，
主線為 voxel-based two-stage 方法（Voxel R-CNN → CasA → NV3D），並涵蓋基礎與新趨勢論文。
最終用途：作為知識來源，產生給「懂一點深度學習、但沒碰過點雲」的人看的教學 HTML 簡報。

## 目錄結構

- `raw/` — 原始資料，**唯讀**，LLM 不修改。`raw/SOURCES.md` 記錄每份資料的出處。
- `wiki/index.md` — 所有 wiki 頁面的目錄，每頁一行摘要。每次新增頁面都要更新。
- `wiki/log.md` — 依時間記錄每次 ingest / 修改 / 檢查發現的問題（append-only）。
- `wiki/concepts/` — 概念頁（如 voxelization、sparse convolution、RoI pooling、KITTI 指標）。
- `wiki/papers/` — 每篇論文一頁。
- `wiki/comparisons/` — 跨論文的比較表、演進時間線。

## 寫作規則

- 語言：繁體中文說明，專有名詞保留英文，第一次出現時附中文，例如「Voxel RoI Pooling（體素區域池化）」。
- 檔名：小寫 kebab-case，例如 `voxel-rcnn.md`、`sparse-convolution.md`。
- 頁面間用相對連結互相引用，例如 `[Sparse Convolution](../concepts/sparse-convolution.md)`。
- **每個數字（AP、FPS、參數量）都必須標註來源論文與表格**，例如 `（Voxel R-CNN, Table 1, KITTI val, Moderate）`。
  沒有出處的數字不能寫進 wiki。
- 區分「論文宣稱」與「wiki 的整理/推論」；推論要標註「（整理）」。
- 來源不完整時（例如 CasA 只有 README）要在頁面開頭標註資料限制。
- KITTI 數字一律標註 **val/test** 與 **R11/R40**；以 val 為主，test 並列。原文沒寫 R11/R40 時標「推定」並說明理由。
- **comparisons 頁的主表以「同一張來源表格」為準**，原論文的數字放備註欄。不同表格的數字不能混在同一欄比大小。
- PDF 抽出的文字可能吃掉上標（例如 0.16² 變成 0.162）、混入行號，引用數字時要核對語意。
- **抽文字後先檢查每張 Table 是否有數字**。若表格是圖片（例如 IEEE 排版），要把頁面轉成圖片再讀，不能拿 README 等次要來源的數字代替。
- 論文的內文和表格衝突時，**以表格為準**，並在頁面的「資料品質備註」中記錄。

## 論文頁模板（wiki/papers/*.md）

```
# <論文名稱>
> 出處：<會議/期刊 年份> · arXiv/DOI · raw 檔案路徑
> 資料限制：<若有>

## 一句話總結
## 要解決的問題（動機）
## 核心方法
### 關鍵模組 1 …
## 主要結果（附表格出處）
## 和其他方法的關係（前作 / 後續 / 比較對象）
## 限制與討論
## 相關概念
```

## 概念頁模板（wiki/concepts/*.md）

```
# <概念名稱>
## 白話解釋（給初學者）
## 技術細節
## 出現在哪些論文
## 常見誤解
```

## Ingest 流程（先討論、後生成）

1. 讀 raw 資料，列出 3–5 個重點，以及預計新增/更新的頁面清單 → **交給使用者確認，先不寫檔**。
2. 使用者確認或修改後，寫論文頁；新增或更新相關概念頁；補上雙向連結。
3. 更新 `wiki/index.md`；在 `wiki/log.md` 追加一筆紀錄（日期、來源、改動頁面、討論中被修正的地方）。

## Lint（定期檢查）

- 找出沒有被任何頁面連到的孤兒頁、壞掉的連結。
- 找出沒有出處的數字。
- 找出不同頁面之間互相矛盾的敘述。
- 檢查結果寫進 `wiki/log.md`。
