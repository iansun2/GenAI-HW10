# NV3D: Leveraging Spatial Shape Through Normal Vector-based 3D Object Detection

> 出處：**arXiv 預印本** 2510.11632v1（2025-10-13）· `raw/papers/nv3d.pdf` · 程式碼：github.com/krittin-ch/NV3D
> 作者：Krittin Chaowakarn, Paramin Sangwongngam, Nang Htet Htet Aung, Chalie Charoenlarpnopparut（SIIT 法政大學 / NECTEC / 朱拉隆功大學）
> **資料限制（重要，請先讀）：**
> 1. **尚未經過同儕審查**（arXiv 預印本）。
> 2. 論文的「**mAP**」是 **Easy / Mod. / Hard 三個難度的平均**，不是 KITTI 慣用的 Moderate AP。本頁兩者分開標示。
> 3. **Voxel R-CNN baseline 有兩組數字**：Table 1 為 89.39 / 83.83 / 78.73；Table 4 和 Table 7 為 92.38 / 85.29 / 82.86（與 Voxel R-CNN 原論文 R40 一致）。論文沒有說明原因。
> 4. 依本 wiki 規則 B（同一張表），**在 Table 7 中，NV3D 的 Car 精度略低於 Voxel R-CNN**。摘要宣稱的「+2.61%」是和 Table 1 那組比較低的 baseline 比較的結果。
> 5. **沒有報告速度**（FPS 或執行時間）；**沒有 KITTI test 結果**。
> 6. 其他內部不一致見文末的「資料品質備註」。

## 一句話總結

在 [Voxel R-CNN](voxel-rcnn.md) 的輸入端加入每個 voxel 的**表面法向量**特徵，並用法向量密度和距離分 bin 來**丟掉多餘的 voxel**（主要是地面）。最站得住的結果是：**丟掉約 53% 的 voxel，Car 精度只掉約 1 個百分點**；SECOND 套用後精度反而上升。

## 在演進中的位置（整理）

- [Voxel R-CNN](voxel-rcnn.md)、[CasA](casa.md) 改進的是**第二階段**（RoI 特徵怎麼取、精修幾次）。
- NV3D 改進的是**輸入端**：
  - 加入什麼特徵（法向量）
  - 丟掉哪些資料（取樣）
- backbone、RPN、detection head 都**沿用 Voxel R-CNN**（§3、§4.2）。

## 要解決的問題（動機）

- voxel 方法把點分進格子，**難以表達局部的表面形狀**（§1）。
- point 方法（PointNet++、PV-RCNN）能取得鄰居資訊，但鄰居搜尋和分組的**計算成本高**（§1）。
- 作者的兩個假設（§1）：
  1. 近處密集的點雲有大量**冗餘**。
  2. 鄰近點的**幾何特徵**（法向量）可以提供更有用的資訊。

## 核心方法

架構（Fig. 1）：**Voxel 化 → 法向量擷取（KNN + PCA）→ 取樣遮罩 → Element-wise attention 融合 voxel 與法向量特徵 → Voxel R-CNN 的 3D backbone → BEV + RPN → Voxel RoI Pooling → Detection head**

### 1. 法向量擷取（§3.1）
- **為什麼不直接用 voxel 內的點算？**
  - 只有**不到 20%** 的 voxel 內有超過 3 個點，點太少算不出平面。
  - voxel 內點的排列也會讓法向量不穩定（Fig. 2）。
- 做法（Local PCA）：
  1. 對每個 voxel 用 **KNN（K=7）** 找 7 個鄰近 voxel。
  2. 對這些鄰居做 **PCA**，取**變異最小**的方向作為法向量。
  3. **法向量密度**：把所有法向量畫在單位球上，計算半徑 0.25 內有幾個法向量，再對每個 batch 正規化。
- 每個 voxel 的法向量特徵為 (n_x, n_y, n_z, d)。
- 詳見 [法向量](../concepts/normal-vector.md)。

### 2. 兩種取樣（§3.2）
- **法向量密度取樣（ND sampling）**：
  - 地面很平，法向量幾乎都朝上 → 在法向量空間中**密度極高**。
  - 把**正規化密度 > 0.7** 的 voxel **丟掉 50%**。門檻刻意設高、只丟一半，是為了避免丟到車子（§3.2）。
- **FOV-aware bin 取樣**：
  - 約 **90% 的 voxel 集中在 30 m 以內**（§3.2）。
  - 依距離切成 10 個環狀 bin，第 n 個 bin 保留 **500 × (2n−1)** 個 voxel，讓每個 bin 的 voxel **面積密度相同**。
  - 改良自 VirConv 的 bin-based 取樣：原本的做法會造成各 bin 之間密度不連續（Fig. 3）。
- 兩者合用：實際丟掉 **53.14%** 的 voxel（Table 7；論文稱約 55%）。
- 詳見 [輸入取樣](../concepts/input-sampling.md)。

### 3. Element-wise Attention Fusion（§3.3、§4.2）
- voxel 特徵和法向量特徵各自經過 MLP（4 → 16 → 32）編碼，再做 attention 融合，最後解碼（32 → 16 → 4）回 4 維，送進 3D backbone。
- Q / K / V 的分配在論文中**說法不一致**（見資料品質備註），本 wiki 不採用任何一種說法。

### 4. 訓練設定
- 和 Voxel R-CNN 完全相同（§4.2）：
  - 偵測範圍 x∈[0, 70.4]、y∈[−40, 40]、z∈[−3, 1] m
  - voxel 大小 (0.05, 0.05, 0.1) m

## 主要結果

**本頁一律以「同一張表」的數字為準**（規則 B）。KITTI val，**R40**。

### 同表比較 1：不取樣（Table 4，3D AP R40）

| 方法 | Car E / **M** / H | Ped. E / M / H | Cyc. E / M / H |
|---|---|---|---|
| SECOND | 88.61 / 78.62 / 77.22 | 56.55 / 52.98 / 47.73 | 80.58 / 67.15 / 63.10 |
| PointPillars | 87.75 / 78.39 / 75.18 | 57.31 / 51.46 / 46.83 | 81.57 / 63.00 / 59.04 |
| PV-RCNN | 92.57 / 84.83 / 82.69 | 62.75 / 54.47 / 49.94 | 89.09 / 70.37 / 65.98 |
| **Voxel R-CNN** | 92.38 / **85.29** / 82.86 | – | – |
| LoGoNet | 92.04 / 85.04 / 84.31 | 70.20 / 63.72 / 59.46 | 91.74 / 75.35 / 72.42 |
| **NV3D** | 92.46 / **84.78** / 82.55 | 65.50 / 59.60 / 54.62 | 93.31 / 75.97 / 71.25 |

- Car Mod.：NV3D 84.78 **低於** Voxel R-CNN 85.29。
- Cyclist：NV3D 在 Easy 和 Mod. 是表中最高（但 Voxel R-CNN 在這張表沒有 Cyclist 數字）。
- ⚠️ 本表中 SECOND、PointPillars 的數字（78.62、78.39）標示為 R40，但 SECOND 的 88.61 / 78.62 / 77.22 和 Voxel R-CNN Table 5 的 **R11** 數字完全相同。NV3D 是否把 R11 數字誤標成 R40，無法從原文確認。

### 同表比較 2：取樣前後（Table 7，Car 3D AP R40，max 16,000 voxels）

「三難度平均」= NV3D 論文中的「mAP」。

| 取樣方式（丟棄比例） | 方法 | Car Mod. | 三難度平均 | 和不取樣相比 |
|---|---|---|---|---|
| 不取樣（0%） | SECOND | 78.62 | 81.48 | – |
| | PV-RCNN | 84.83 | 86.70 | – |
| | Voxel R-CNN | **85.29** | **86.84** | – |
| | NV3D | 84.78 | 86.60 | – |
| ND（24.02%） | SECOND | 81.38 | 83.57 | **+2.09** |
| | Voxel R-CNN | 84.83 | 86.41 | −0.43 |
| | NV3D | 83.05 | 85.93 | −0.67 |
| FOV（49.16%） | SECOND | 80.92 | 82.74 | +1.26 |
| | Voxel R-CNN | 83.73 | 85.05 | −1.79 |
| | NV3D | 84.07 | 85.61 | −0.99 |
| ND + FOV（53.14%） | SECOND | 80.68 | 82.66 | +1.18 |
| | PointPillars | 76.20 | 78.91 | −1.53 |
| | PV-RCNN | 83.18 | 86.03 | −0.67 |
| | Voxel R-CNN | 84.33 | 85.80 | −1.04 |
| | NV3D | 82.82 | 85.54 | −1.06 |

- **最有價值的發現**：取樣方法可以外掛到其他偵測器。丟掉約一半的 voxel，大多數方法只掉約 1 個百分點（三難度平均）。
- **SECOND 套用後反而進步**（+1.18 到 +2.09）。論文沒有解釋原因。（推測：可能是一階段方法較容易受地面雜訊干擾。raw 資料無法證實，僅供參考）
- 只用 FOV 取樣時，NV3D（−0.99）比 Voxel R-CNN（−1.79）掉得少，或許代表法向量特徵能部分彌補資料的減少。（整理）

### 論文自己的 baseline 比較（Table 1，R40，並列參考）

| 類別 | 指標 | Voxel R-CNN（Table 1 的 baseline） | NV3D 不取樣 | NV3D 取樣後 |
|---|---|---|---|---|
| Car | Mod. | 83.83 | 84.78 | 82.82 |
| Car | 三難度平均 | 83.98 | 86.60（+2.62） | 85.54（+1.56） |
| Pedestrian | 三難度平均 | 63.60 | 59.57（**−4.03**） | 45.44（**−18.16**） |
| Cyclist | 三難度平均 | 75.95 | 80.18（+4.23） | 75.27（−0.68） |

⚠️ 這組 baseline（83.83）和同一篇論文 Table 4 / 7 的 Voxel R-CNN（85.29）不同，論文沒有說明。

### KITTI val R11（Table 5，Car）
- 不取樣：89.32 / **84.13** / 78.77
- 取樣後：88.98 / 79.12 / 78.38
- 對照（不同論文的表，只供參考）：Voxel R-CNN 自報 R11 Mod. 84.52（Voxel R-CNN Table 5）。

### 消融：K 值（Table 6，三類別 3D mAP R40）
- K=3：74.90、K=5：75.21、**K=7：75.56**
- 但只看 Car Mod.，K=3（85.17）反而最好。
- K 無法再加大：KNN 受限於平行執行緒數量，K 一大就太慢（§5）。

## 和其他方法的關係

- **Base**：[Voxel R-CNN](voxel-rcnn.md)（backbone、RPN、Voxel RoI Pooling、detection head 都沿用）。
- **借用**：
  - Local PCA 法向量估計（經典方法）
  - VirConv 的 bin-based 取樣（改成 FOV-aware）
  - attention 機制
- **沒有比較**：[CasA](casa.md)。同為 val R40 Car Mod.：CasA+V 86.37（CasA Table III）vs NV3D 84.78（NV3D Table 4），**不同論文的數字只供參考**。
- 論文自己比較的對象：CB-SSD、PVP-SSD（Table 2 / 3）、LoGoNet、CIANet、MSPV3D（Table 4）。

## 限制與討論

- **行人退步**（§6）：作者推測人體是圓弧表面，不像車和自行車有平面，法向量估計較不準。取樣後行人大幅退步（−18.16），因為行人體積小、點少，更容易被丟掉。（後半句為整理）
- **沒有速度數字**：論文稱「low-complexity」，但沒有量化，KNN 本身還是速度瓶頸（§5）。
- 只在 KITTI val 上評估，沒有 test、沒有 Waymo。

## 資料品質備註（本次 ingest 發現）

| # | 問題 | 位置 |
|---|---|---|
| 1 | 「mAP」= 三難度平均，非慣用的 Moderate AP | 全文 |
| 2 | Voxel R-CNN baseline 兩組數字（83.83 vs 85.29） | Table 1 vs Table 4 / 7 |
| 3 | 同一張表中 NV3D 低於 Voxel R-CNN（Car） | Table 7 |
| 4 | Pedestrian Easy：64.50 vs 65.50 | Table 1 vs Table 4 |
| 5 | 提升幅度：+2.61 vs +2.62 | 摘要 vs Table 1 |
| 6 | Q / K / V 分配說法矛盾：摘要說 voxel 為 Q、V，法向量為 K；§1 和 §4.2 說法向量為 Q，voxel 為 K、V | 摘要 vs §1 / §4.2 |
| 7 | 「如 Fig. 2 和 3 所示」應為 Table 2 和 3 | §4.3 |
| 8 | 丟棄比例：論文說「約 55%」，Table 7 為 53.14% | 摘要 vs Table 7 |
| 9 | SECOND 的「R40」數字和 Voxel R-CNN Table 5 的 R11 數字完全相同 | Table 4 / 7 |

## 相關概念

[法向量](../concepts/normal-vector.md) · [輸入取樣](../concepts/input-sampling.md) · [Voxelization](../concepts/voxelization.md) · [RoI Pooling](../concepts/roi-pooling.md) · [KITTI Benchmark](../concepts/kitti-benchmark.md)
