# SECOND: Sparsely Embedded Convolutional Detection

> 出處：Sensors 2018, 18(10), 3337 · DOI 10.3390/s18103337 · `raw/papers/second.txt`
> 作者：Yan Yan, Yuxing Mao, Bo Li
> 資料限制：全文取自 PMC 開放版 HTML 的文字，**沒有圖**（Figure 1–7 只有圖說）。Table 1 的時間單位原文沒有寫明。

## 一句話總結

把 **[Sparse Convolution](../concepts/sparse-convolution.md)** 帶進 LiDAR 3D 偵測：只在有點的 voxel 上計算，讓 voxel-based 3D CNN 從「準但很慢」變成「準又能即時」，之後幾乎所有 voxel-based 方法都以它當 backbone。

## 要解決的問題（動機）

- 前作 VoxelNet 先把點雲分成 [voxel](../concepts/voxelization.md)，再轉成 **dense 3D tensor** 做 3D 卷積。3D CNN 的計算量隨解析度**立方成長**，所以很慢（VoxelNet 每幀 0.23 s，SECOND Table 4）。
- 但 LiDAR 點雲非常稀疏：一個 KITTI 場景切完 voxel 只有約 **5k–8k 個非空 voxel，稀疏度約 0.005**（SECOND §3.1.3）。大部分計算都花在空格子上。
- 另外兩個小問題：
  - 角度回歸在 0 和 π 之間會出現「同一個框卻得到很大 loss」的矛盾（VoxelNet 的做法）。
  - 每個場景的物體（ground truth）太少，訓練收斂慢。

## 核心方法

整體架構：**點雲 → voxel 分組 → VFE 特徵 → Sparse 3D CNN 中間層 → 轉成 BEV 2D 特徵圖 → RPN 輸出框**

### 1. Voxel 分組與 VFE（Voxel Feature Encoding）
- 沿用 VoxelNet：把點雲切成小格子，每格最多取 T 個點（Car T=35；行人、自行車 T=45，因為物體小、需要更多點）。
- voxel 大小 0.4 × 0.2 × 0.2 m（z × y × x）；Car 的偵測範圍 z∈[−3,1]、y∈[−40,40]、x∈[0,70.4] m（§3.1.1）。
- VFE：對格子內每個點用小型全連接網路提特徵，再 max pooling 成一個 voxel 特徵。

### 2. Sparse Convolutional Middle Extractor（核心）
- 用 [Sparse Convolution](../concepts/sparse-convolution.md) 取代 dense 3D 卷積：**只在有資料的位置計算**。
- 交替使用兩種卷積：
  - **Submanifold 卷積**：輸出位置 = 輸入位置，有效位置不會變多，用來提特徵。
  - **一般 sparse 卷積**：負責在 z 軸方向 downsample。
- z 軸被壓到 1–2 層後，把 sparse 資料轉回 dense，再 reshape 成類似影像的 **BEV（鳥瞰圖）特徵圖**，交給 2D 網路處理。
- SECOND 的工程貢獻：把建立「輸入-輸出對應表（rule）」的演算法搬到 **GPU**，比當時的 SparseConvNet 快（Table 1）。

### 3. RPN 與 anchor
- SSD 風格的 2D RPN：3 個 stage 下採樣，再上採樣串接，最後用 3 個 1×1 卷積分別輸出類別、框回歸、方向。
- 使用固定大小的 [anchor](../concepts/anchor-and-box-encoding.md)：每類一種尺寸、兩個角度（0° 和 90°）。

### 4. Sine-error 角度損失 + 方向分類器
- 角度 loss：`L_θ = SmoothL1( sin(θ_p − θ_t) )`（Eq. 7）。
- 兩個好處：(1) 角度差 π 時 sin 為 0，不會懲罰「其實是同一個框」的預測；(2) 很自然地反映角度誤差對 IoU 的影響。
- 副作用：分不出車頭和車尾 → 另加一個**方向分類器**（softmax）判斷方向。
- 細節見 [Anchor 與 Box Encoding](../concepts/anchor-and-box-encoding.md)。

### 5. Focal Loss
- 一個 KITTI 點雲約有 **70k 個 anchor**，但每個物體只會配到 4–6 個正樣本 → 前景/背景極度不平衡 → 使用 RetinaNet 的 focal loss（α=0.25, γ=2）（§3.2.1）。
- 總 loss：`L = 1.0·L_cls + 2.0·(L_θ + L_reg) + 0.2·L_dir`（Eq. 9）。

### 6. GT-sampling 資料增強
- 建立資料庫，存放訓練集中每個物體的標註和框內的點；訓練時隨機抽幾個「貼」進目前場景，並做碰撞檢查。
- 詳見 [GT-sampling](../concepts/gt-sampling-augmentation.md)。

## 主要結果

以 KITTI **val** 為主（Car 類，3D AP %，SECOND Table 4）：

| 方法 | 每幀時間 (s) | Easy | Moderate | Hard |
|---|---|---|---|---|
| VoxelNet | 0.23 | 81.97 | 65.46 | 62.85 |
| **SECOND** | **0.05** | **87.43** | **76.48** | **69.10** |
| SECOND (small) | 0.025 | 85.50 | 75.04 | 68.78 |

BEV AP（val, Car, Table 5）：SECOND 89.96 / 87.07 / 79.66。

以上 val 數字為 **R11**（PV-RCNN Table 2 列出相同的 76.48，並註明 R11）。

KITTI **test**（3D AP %，Table 2，並列參考）。這是**當時的 R11** 口徑；KITTI 改用 R40 後，Car 變成 83.34 / 72.55 / 65.82（PV-RCNN Table 1），見 [R11 vs R40](../concepts/kitti-benchmark.md#r11-vs-r40ap-的兩種計算方式)：

| 類別 | Easy | Moderate | Hard |
|---|---|---|---|
| Car | 83.13 | 73.66 | 66.20 |
| Pedestrian | 51.07 | 42.56 | 37.29 |
| Cyclist | 70.51 | 53.85 | 46.90 |

消融實驗：
- **速度**：和 dense 網路相比，訓練快約 4 倍，推論快約 3 倍（§1）。單層 sparse conv（64×64 channels）：SECOND 8.6、SpConvNet 21.2、Dense 567（Table 1，原文沒有寫單位）。
- **角度編碼**（val, Car, Table 6）：Vector 編碼（AVOD）74.79 → SECOND 76.48（Moderate）。
- **GT-sampling**：大幅加快收斂並提升最終結果（Figure 7，只有曲線，沒有數字）。

## 和其他方法的關係

- **前作**：VoxelNet（voxel + dense 3D CNN）。
- **後續**：
  - [PointPillars](pointpillars.md) 進一步把 z 軸整個拿掉（pillar），追求速度。
  - [PV-RCNN](pv-rcnn.md)、[Voxel R-CNN](voxel-rcnn.md)、[CasA](casa.md) 都以 SECOND 式的 sparse 3D backbone 作為第一階段。
  - SECOND 的 sparse 卷積實作後來發展成 `spconv` 函式庫，被 OpenPCDet 等框架廣泛使用。（整理：依 CasA README 提到 Spconv2.X 支援推知其延續性，`raw/papers/casa-readme.md`）

## 限制與討論

- 少於約 10 個點的遠距離車輛常常漏偵測，旋轉和尺寸估計也不準（§4.3.1）。
- 行人、自行車的誤報和漏報比車多：物體小、點少、容易和雜訊混淆（§4.3.2）。
- 它是 **one-stage** 方法，沒有第二階段 refinement。這正是後來 [two-stage 方法](../concepts/one-stage-vs-two-stage.md) 要補強的地方。（整理）

## 相關概念

[點雲與 LiDAR](../concepts/point-cloud-and-lidar.md) · [Voxelization](../concepts/voxelization.md) · [Sparse Convolution](../concepts/sparse-convolution.md) · [Anchor 與 Box Encoding](../concepts/anchor-and-box-encoding.md) · [GT-sampling](../concepts/gt-sampling-augmentation.md) · [KITTI Benchmark](../concepts/kitti-benchmark.md)
