# GT-sampling 資料增強（Ground-Truth Sampling）

## 白話解釋（給初學者）

KITTI 一個場景裡的車子和行人不多，網路「看到的例子」太少，學得很慢。
GT-sampling 就像**剪貼簿**：
1. 先把訓練集中所有物體連同框內的點「剪下來」存成資料庫。
2. 訓練時，隨機挑幾個物體「貼」到目前的場景裡。

一個場景就能多出好幾個物體可以學。這招之所以可行，是因為點雲是 3D 座標，搬移物體很容易，不像影像會有光影、遮擋不自然的問題。

## 技術細節（[SECOND](../papers/second.md) §3.2.2）

- **建資料庫**：記錄每個 ground truth 的標註，以及落在其 3D 框內的點。
- **取樣貼上**：訓練時隨機取樣，直接把點串接（concatenate）到目前的點雲。
- **碰撞檢查**：貼上後若和其他物體重疊就移除，避免物理上不可能的情況。
- SECOND 一起使用的其他增強：
  - **Object noise**：每個物體各自隨機旋轉 Δθ∈[−π/2, π/2]，並加上高斯隨機平移（平均 0、標準差 1.0）。
  - **全域旋轉與縮放**：旋轉 [−π/4, π/4]，縮放 [0.95, 1.05]。
- 效果：明顯加快收斂並提升最終 AP（SECOND Figure 7，原文只有曲線圖，沒有表格數字）。

### PointPillars 的調整（§4.3、§7.2、§7.4）
- 每個樣本貼入 Car 15、Pedestrian 0、Cyclist 8 個物體，作者表示比 SECOND 原本的設定更好。
- GT-sampling 大約帶來 **+3% mAP**（§7.4，在固定式 encoder 的實驗中觀察到）。
- **單一物體增強要少**：PointPillars 把旋轉縮小到 [−π/20, π/20]、平移 N(0, 0.25)，比 SECOND 的 [−π/2, π/2] 小很多。增強太多時，行人的表現明顯變差。
- 作者推測：有了 GT-sampling，就不太需要大量的單一物體增強了（§7.2）。
- 其他增強：沿 x 軸隨機鏡像翻轉、全域旋轉和縮放、全域平移 N(0, 0.2)，用來模擬定位誤差。

## 出現在哪些論文

- 首次提出：[SECOND](../papers/second.md)
- 沿用並調參：[PointPillars](../papers/pointpillars.md)
- [PV-RCNN](../papers/pv-rcnn.md)（§4.1）、[CasA](../papers/casa.md)（§IV-B4）：明確寫出使用 ground-truth sampling。
- [Voxel R-CNN](../papers/voxel-rcnn.md)：資料增強「依照 PointPillars、PV-RCNN 等」（§4.2），沒有逐項列出。
- [VoxelNeXt](../papers/voxelnext.md)：在 Waymo 上「減少 GT-sampling 貼入的物體數」反而更好（Vehicle L1 78.2 → 79.1，VoxelNeXt Table A-20），和 PointPillars「增強不是越多越好」的發現一致。

## 常見誤解

- 「貼上去的物體會讓場景不真實，所以有害」→ 有碰撞檢查。SECOND 的實驗顯示整體是正面效果。不過貼上的物體可能出現在不合理的位置（例如懸空或在建築物內），這是已知的副作用。（整理）
