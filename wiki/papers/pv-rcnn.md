# PV-RCNN: Point-Voxel Feature Set Abstraction for 3D Object Detection

> 出處：CVPR 2020 · arXiv 1912.13192v2 · `raw/papers/pv-rcnn.pdf`
> 作者：Shaoshuai Shi, Chaoxu Guo, Li Jiang, Zhe Wang, Jianping Shi, Xiaogang Wang, Hongsheng Li（CUHK / SenseTime）
> 資料限制：**原文沒有報告推論速度**（由 Voxel R-CNN 補上：8.9 FPS）。KITTI val 有 R11（Table 2）和 R40（Table 3）兩種數字，test 為 R40（Table 1）。
> 程式碼：OpenPCDet（github.com/open-mmlab/OpenPCDet）

## 一句話總結

**Two-stage** 偵測器：第一階段用 voxel CNN 產生候選框，第二階段用 PointNet 式的 set abstraction 從 **keypoint** 收集精細特徵來修正框。結合 voxel 的效率和 point 的精確位置。

## 要解決的問題（動機）

- **Voxel 方法**（如 [SECOND](second.md)）：有效率、候選框品質好；但特徵圖下採樣到 8 倍，解析度低，不利精細定位（§3.1）。
- **Point 方法**（如 PointRCNN）：保留精確位置、感受野彈性；但計算量大（§1）。
- 第二階段要從候選框「取特徵」時，傳統的 RoIPooling / RoIAlign 只用 4 或 8 個最近鄰插值。在稀疏的 3D 特徵圖上，**取到的大多是 0**（§3.1）。
- 最直接的做法是讓每個框的格點直接向所有 voxel 取特徵，但記憶體負擔太大。原文的例子：KITTI 一個場景在 4× 下採樣層約有 18,000 個 voxel，100 個框 × 27 個格點 = 2,700 個格點，要計算 2,700 × 18,000 組距離（§3.1）。

## 核心方法

整體架構（Figure 2）：**點雲 → Sparse 3D CNN → (a) BEV + RPN 產生候選框；(b) VSA 把多層 voxel 特徵濃縮到 keypoint → RoI-grid Pooling → 修正框 + 信心分數**

這種「兩階段、中間透過少量 keypoint 轉手」的設計稱為 **voxel-to-keypoint → keypoint-to-grid** 兩步策略。

### 第一階段：3D Voxel CNN + RPN（§3.1）
- 和 SECOND 類似：voxel 化後用 3×3×3 sparse conv，得到 1×、2×、4×、8× 四個尺度的特徵。
- 8× 特徵沿 z 軸疊起來變成 BEV 圖，用 [anchor](../concepts/anchor-and-box-encoding.md)（每類一種尺寸、0°/90° 兩個方向）產生候選框。
- KITTI voxel 大小為 **(0.05, 0.05, 0.1) m**，比 SECOND 的 0.2 × 0.2 × 0.4 m 細很多（§4.1）。
- Proposal 品質（Car Mod. recall @ IoU 0.7，Table 4）：PointRCNN 74.8、STD 76.8、**PV-RCNN 85.5**。

### Voxel Set Abstraction（VSA，Voxel → Keypoint）（§3.2）
- **Keypoint 取樣**：用 Furthest Point Sampling（FPS）從原始點雲取 n 個點（KITTI n=2,048、Waymo n=4,096），讓它們均勻分布。
- **多尺度收集**：每個 keypoint 在每一層 voxel 特徵中，收集半徑 r_k 內的非空 voxel，用 PointNet block（MLP + max pooling）壓成一個向量。每層設兩個半徑。
- **Extended VSA**：額外收集兩種特徵，最後全部串接（Eq. 4）。
  - 原始點特徵：彌補 voxel 化的量化損失。
  - BEV 圖特徵：z 方向的感受野較大。
- **PKW（Predicted Keypoint Weighting）**：用一個小 MLP 預測每個 keypoint 是不是前景（落在真實框內），再依此加權特徵。不需要額外標註，直接用框標註就能產生監督（§3.2）。

### RoI-grid Pooling（Keypoint → Grid）（§3.3）
- 每個候選框內均勻放 **6×6×6 = 216 個格點**。
- 每個格點收集半徑內（0.8 m、1.6 m 兩種）的 keypoint 特徵，用 PointNet block 匯總。
- 收集範圍**可以超出框的邊界**，所以能看到物體周圍的環境。
- 216 個格點特徵攤平後過兩層 MLP（256 維），代表這個框。
- 詳見 [RoI Pooling](../concepts/roi-pooling.md)。

### 修正與 IoU-guided 信心分數（§3.3）
- 兩個分支：框的殘差回歸（SmoothL1），以及信心分數。
- 信心分數的訓練目標不是「是/不是物體」，而是**預測框和真實框的 3D IoU**，正規化為 `y = min(1, max(0, 2·IoU − 0.5))`（Eq. 8）。
- 效果（val R40, Car Mod., Table 9）：分類式 82.50 → IoU-guided 84.83。

### 訓練（§3.4、§4.1）
- 總 loss = L_rpn + L_seg（keypoint 前景分割）+ L_rcnn，三者權重相等。
- 第二階段每個場景取 128 個 proposal，正負 1:1；3D IoU ≥ 0.55 視為正樣本。
- 推論：第一階段保留前 100 個框（NMS 0.7），修正後再做一次 NMS。
- 使用 [GT-sampling](../concepts/gt-sampling-augmentation.md)、x 軸翻轉、全域縮放 [0.95, 1.05]、全域旋轉 [−π/4, π/4]。
- 8 張 GTX 1080 Ti 訓練約 5 小時（KITTI，80 epochs）。
- Car 和 Cyclist 用**同一個模型**偵測，不像前作分開訓練（§4.2）。

## 主要結果

**KITTI val**（Car Moderate 3D AP）：

| AP 計算方式 | Easy | Moderate | Hard | 出處 |
|---|---|---|---|---|
| R11 | – | **83.90** | – | Table 2 |
| R40 | 92.57 | 84.83 | 82.69 | Table 3 |

同一張表（Table 2, val R11, Car Mod.）的比較：SECOND 76.48、PointRCNN 78.63、STD 79.80、**PV-RCNN 83.90**。

**KITTI test**（R40，Table 1，並列參考）：

| 方法 | Car 3D E / M / H | Cyc. 3D E / M / H |
|---|---|---|
| SECOND | 83.34 / 72.55 / 65.82 | 71.33 / 52.08 / 45.83 |
| PointPillars | 82.58 / 74.31 / 68.99 | 77.10 / 58.65 / 51.92 |
| **PV-RCNN** | **90.25 / 81.43 / 76.82** | 78.60 / **63.71 / 57.65** |

截至 2019-11-15，在 KITTI Car 3D 排行榜排名第 1（§4.2）。

**Waymo**（Vehicle LEVEL 1 3D mAP，v1.0，Table 5）：PointPillars 56.62 → MVF 62.93 → **PV-RCNN 70.30**。PV-RCNN 在 30–50 m 距離的進步最大（+9.19）。指標見 [Waymo Open Dataset](../concepts/waymo-open-dataset.md)。

### 消融實驗（val R40, Car）
- **第二階段的效果**（Table 7）：

| 設定 | Easy | Mod. | Hard |
|---|---|---|---|
| 只有 RPN（one-stage） | 90.46 | 80.87 | 77.30 |
| 直接從 encoder pool（不用 keypoint） | 91.88 | 82.86 | 80.52 |
| PV-RCNN（keypoint + RoI-grid） | 92.57 | 84.83 | 82.69 |

  → 第二階段 refinement 讓 Moderate 提升約 **+4 AP**，其中 keypoint 中轉貢獻約 +2。

- **VSA 的特徵來源**（Table 8, Mod.）：只用原始點特徵 81.98，加入高層語意特徵後大幅提升，全部都用時為 84.83。低層特徵只帶來小幅加分。
- **PKW / RoI pooling 方式**（Table 9, Mod.）：
  - 拿掉 PKW：82.95
  - 改用 RoI-aware pooling：82.97
  - 完整版：84.83

## 和其他方法的關係

- **基礎**：
  - [SECOND](second.md) 的 sparse 3D CNN 和 anchor RPN。
  - PointNet++ 的 set abstraction。
  - 同作者的 PointRCNN、Part-A² Net。
- **後續**：
  - [Voxel R-CNN](voxel-rcnn.md)：主張「不需要 point，只用 voxel 就夠準又更快」。KITTI val R11 為 84.52 vs PV-RCNN 83.69，FPS 為 25.2 vs 8.9（Voxel R-CNN Table 3 / 5）。
  - [CasA](casa.md) 有 CasA-PV 變體以 PV-RCNN 為基底，README 中 PV-RCNN baseline 的 val Car R11/R40 為 83.90/84.83（`raw/papers/casa-readme.md`），和本論文一致。
  - 同一個 README 也提到後續版本 PV-RCNN++。

## 限制與討論

- **速度**：原文沒有報告，由後續論文補上：
  - **8.9 FPS**（Voxel R-CNN Table 3，KITTI test 排行榜比較）。
  - 各模組耗時（Voxel R-CNN Table 2，KITTI val 平均）：3D backbone 21.1 ms、2D backbone 9.4 ms、**VSA 49.4 ms**、detect head 19.1 ms。
  - → point-voxel 互動（VSA）約佔一半時間，這正是 [Voxel R-CNN](voxel-rcnn.md) 要解決的問題。
- 對照：[PV-RCNN vs Voxel R-CNN](../comparisons/pv-rcnn-vs-voxel-rcnn.md)。

## 相關概念

[One-stage vs Two-stage](../concepts/one-stage-vs-two-stage.md) · [RoI Pooling](../concepts/roi-pooling.md) · [Sparse Convolution](../concepts/sparse-convolution.md) · [Voxelization](../concepts/voxelization.md) · [KITTI Benchmark](../concepts/kitti-benchmark.md) · [Waymo Open Dataset](../concepts/waymo-open-dataset.md) · [點雲與 LiDAR](../concepts/point-cloud-and-lidar.md)
