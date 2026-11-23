# PointPillars: Fast Encoders for Object Detection from Point Clouds

> 出處：CVPR 2019 · arXiv 1812.05784v2 · `raw/papers/pointpillars.pdf`
> 作者：Alex H. Lang, Sourabh Vora, Holger Caesar, Lubing Zhou, Jiong Yang, Oscar Beijbom（nuTonomy）
> 資料限制：PDF 抽出的文字會吃掉上標，原文的「0.162 m2」實為 **0.16² m²**，本頁已更正。KITTI val 只有 Moderate 的數字（§5 內文）。

## 一句話總結

把點雲切成**直立的柱子（pillar）**而不是 3D voxel，讓整個網路只用 **2D 卷積**，速度達到 **62 Hz**，精度還比當時的 LiDAR-only 方法更好。

## 要解決的問題（動機）

- [SECOND](second.md) 用 [Sparse Convolution](../concepts/sparse-convolution.md) 把速度提升到 20 Hz，但 **3D 卷積仍然是瓶頸**。PointPillars 指出 SECOND 開源實作中光 encoder 就要 48 ms（§6）。
- 傳統 BEV 方法用**手工設計**的方式把點雲壓成鳥瞰圖，雖然快，但特徵不是學出來的，換資料或換感測器就要重新調整（§1）。
- 目標：**又快、又是 end-to-end 學出來的特徵**。

## 核心方法

整體架構（Figure 2）：**點雲 → Pillar Feature Net → Pseudo-image → 2D CNN backbone → SSD detection head**

### 1. Pillar 切分
- 只在 x-y 平面切成均勻格子（預設 **0.16 m × 0.16 m**，§4.2），z 方向不切，每格就是一根從地面延伸到頂的柱子。
- 好處：**不需要調 z 方向的切法**這個超參數（§2.1）。
- 稀疏性：0.16² m² 的格子在 KITTI 常用範圍內只有 6k–9k 個非空 pillar，約 **97% 是空的**（§2.1）。
- 限制每個樣本最多 P=12000 根 pillar、每根最多 N=100 個點，超過就隨機取樣、不足就補零，組成 dense tensor (D, P, N)（§2.1、§4.2）。

### 2. Point decoration（點特徵擴充）
- 每個點原本是 (x, y, z, r)，r 是反射強度。再加上：
  - (x_c, y_c, z_c)：到柱內所有點平均位置的距離
  - (x_p, y_p)：到柱子中心的 x、y 偏移
- 擴充後 **D = 9 維**。其中 x_p、y_p 是 PointPillars 新加的，貢獻 **+0.5 mAP**（§7.3）。

### 3. Pillar Feature Net → Pseudo-image
- 簡化版 PointNet：每個點過 Linear-BN-ReLU（可寫成 1×1 卷積），再對柱內的點做 max → 每根 pillar 得到一個 C=64 維特徵（§2.1、§3.1）。
- 把特徵依 pillar 的位置**放回**（scatter）畫布，得到大小 (C, H, W) 的**偽影像**。之後就能直接套影像的 2D CNN。

### 4. Backbone 與 Detection Head
- 2D backbone：三個 block 由上而下降採樣，再上採樣後串接，類似 VoxelNet 和 [SECOND](second.md) 的 RPN（§2.2、§3.1）。
- Detection head：SSD 式，以 2D IoU 配對 [anchor](../concepts/anchor-and-box-encoding.md)，高度和 z 位置當額外的回歸目標（§2.3）。
- 推論時用 axis-aligned NMS（IoU 0.5），效果和旋轉 NMS 差不多但更快（§4.2）。
- 屬於 **one-stage** 方法。論文引用 focal loss 的研究，認為 one-stage 已經可以和 two-stage 競爭（§1.1.1）。

### 5. Loss（沿用 SECOND）
- 框回歸用 SmoothL1，角度用 `sin(θ_gt − θ_a)`，再加方向分類器 L_dir。
- 分類用 focal loss（α=0.25, γ=2）。
- 總 loss 權重：β_loc=2、β_cls=1、β_dir=0.2（§3.2）。
- 詳見 [Anchor 與 Box Encoding](../concepts/anchor-and-box-encoding.md)。

## 主要結果

**KITTI val**（只有 Moderate，§5 內文）：

| 類別 | 3D AP (Mod.) | BEV AP (Mod.) |
|---|---|---|
| Car | 77.98 | 87.98 |
| Pedestrian | 57.86 | 63.55 |
| Cyclist | 66.02 | 69.71 |

以上 val 數字原文沒有寫 R11 或 R40，依年份**推定 R11**。

**KITTI test**（3D AP %，Table 2，並列參考，**R11 口徑**）。改用 R40 後，Car 變成 82.58 / 74.31 / 68.99（PV-RCNN Table 1）：

| 方法 | 速度 (Hz) | Car E / M / H | Ped. E / M / H | Cyc. E / M / H |
|---|---|---|---|---|
| VoxelNet | 4.4 | 77.47 / 65.11 / 57.73 | 39.48 / 33.69 / 31.5 | 61.22 / 48.36 / 44.37 |
| SECOND | 20 | 83.13 / 73.66 / 66.20 | 51.07 / 42.56 / 37.29 | 70.51 / 53.85 / 46.90 |
| **PointPillars** | **62** | 79.05 / **74.99** / **68.30** | **52.08** / **43.53** / **41.49** | **75.78** / **59.07** / **52.92** |

- Car Easy 輸給 SECOND，其他項目都勝過 LiDAR-only 方法（§5）。
- 朝向（AOS, test, Table 3）：mAOS 68.86，SECOND 為 54.53。

### 速度拆解（Car 網路，i7 + 1080 Ti，§6）

| 步驟 | 時間 (ms) |
|---|---|
| 載入與過濾點雲 | 1.4 |
| 分 pillar + decoration | 2.7 |
| 上傳到 GPU | 2.9 |
| Encoder | 1.3 |
| Scatter 成偽影像 | 0.1 |
| Backbone + head | 7.7 |
| NMS（CPU） | 0.1 |
| **總計** | **16.2**（≈ 62 Hz） |

- Encoder 只要 1.3 ms，VoxelNet encoder 要 190 ms（§6）。
- 用 TensorRT 比 PyTorch（42.4 Hz）快 45.5%（§6）。

### 消融實驗
- **格子大小 vs 速度**：格子越大越快，0.28² m² 可達 **105 Hz**。精度下降主要來自行人和自行車，Car 很穩定（§7.1、Figure 5）。
- **學習式 vs 固定式 encoder**：在同一個網路裡只換 encoder 比較（BEV mAP, val, Table 4），學習式全面勝出，格子越大差距越大。

| Encoder | 類型 | 0.16² | 0.20² | 0.24² | 0.28² |
|---|---|---|---|---|---|
| MV3D | 固定 | 72.8 | 71.0 | 70.8 | 67.6 |
| PIXOR | 固定 | 72.9 | 71.3 | 69.9 | 65.6 |
| VoxelNet | 學習 | 74.4 | 74.0 | 72.9 | 71.9 |
| PointPillars | 學習 | 73.7 | 72.6 | 72.9 | 72.0 |

  - VoxelNet encoder 精度略高，但慢了好幾個數量級、參數也多很多，不是公平比較（§7.4）。

## 和其他方法的關係

- **前作**：
  - VoxelNet：提出用 PointNet 學 voxel 特徵。
  - [SECOND](second.md)：提供 loss、anchor、GT-sampling；論文的程式碼也是 fork 自 second.pytorch（§1）。
- **差異**：SECOND 保留 3D 結構，用 sparse 3D conv 處理；PointPillars **直接把高度壓掉**，只用 2D。
- **後續**：精度取向的 two-stage 方法（[PV-RCNN](pv-rcnn.md)、[Voxel R-CNN](voxel-rcnn.md)、[CasA](casa.md)）都回到 SECOND 式的 **3D voxel** backbone，而不是 pillar。Voxel R-CNN 的診斷實驗指出「只有 BEV 表示不足以精確預測 3D 框」（Voxel R-CNN §2.2、Table 1）。

## 限制與討論

- 常見錯誤（§5）：
  - 遠處或被遮擋的物體漏偵測。
  - 廂型車、電車誤判成車。
  - 行人和自行車互相混淆。
  - 行人和電線桿、樹幹混淆。
- 速度的但書（§6）：KITTI 只用前鏡頭看得到的點，約佔全部點雲的 **10%**。實際的自駕車要處理全部點雲，執行時間會大幅增加。
- 高度方向一開始就被 max pooling 壓掉。Voxel R-CNN 指出 voxel 方法的關鍵缺點在於「把 3D 特徵轉成 BEV 後就沒有再恢復 3D 結構」（Voxel R-CNN §1）。該論文的分析對象是 SECOND，但同樣適用於一開始就壓成 2D 的 PointPillars（整理）。在 Voxel R-CNN Table 5（val R11）中，PointPillars 的 Car Mod. 為 76.06，是 voxel-based 方法中最低的。

## 相關概念

[點雲與 LiDAR](../concepts/point-cloud-and-lidar.md) · [Voxelization（含 Pillar）](../concepts/voxelization.md) · [Anchor 與 Box Encoding](../concepts/anchor-and-box-encoding.md) · [GT-sampling](../concepts/gt-sampling-augmentation.md) · [KITTI Benchmark](../concepts/kitti-benchmark.md) · [速度 vs 精度比較](../comparisons/speed-vs-accuracy.md)
