# Voxel R-CNN: Towards High Performance Voxel-based 3D Object Detection

> 出處：AAAI 2021 · arXiv 2012.15712v2 · `raw/papers/voxel-rcnn.pdf`
> 作者：Jiajun Deng, Shaoshuai Shi, Peiwei Li, Wengang Zhou, Yanyong Zhang, Houqiang Li（USTC / CUHK）
> 備註：第二作者 Shaoshuai Shi 也是 [PV-RCNN](pv-rcnn.md) 的第一作者。
> 程式碼：github.com/djiajunustc/Voxel-R-CNN（實驗基於 OpenPCDet）

## 一句話總結

**只用 voxel** 的 two-stage 偵測器：直接從 3D voxel 特徵做 RoI pooling，不經過原始點或 keypoint。精度追平 [PV-RCNN](pv-rcnn.md)，速度約快 3 倍（25.2 vs 8.9 FPS）。

## 核心論點

> 「原始點的精確位置**不是**高效能 3D 偵測的必要條件，粗糙的 voxel 粒度也能提供足夠的空間資訊。」（摘要、§1）

這和 [PV-RCNN](pv-rcnn.md) 的出發點相反：PV-RCNN 認為需要 point 來補回 voxel 量化損失的精確位置。兩者的對照見 [PV-RCNN vs Voxel R-CNN](../comparisons/pv-rcnn-vs-voxel-rcnn.md)。

## 要解決的問題（動機）：兩個診斷實驗（§2）

### 診斷 1：只在 BEV 上精修不夠
- 在 [SECOND](second.md) 的 2D BEV 特徵上加一個精修頭（用 Rotated RoI Align 取特徵）。
- 結果（KITTI val R11, Car Mod., Table 1）：
  - SECOND：78.62
  - SECOND + BEV 精修頭：79.26（只 +0.6）
  - PV-RCNN：83.69
- → **BEV 表示的容量有限，需要 3D 結構資訊。**

### 診斷 2：PV-RCNN 慢在 point-voxel 互動
- PV-RCNN 各模組的耗時（KITTI val 3,769 個樣本平均，Table 2）：

| 3D backbone | 2D backbone | **VSA** | Detect head |
|---|---|---|---|
| 21.1 ms | 9.4 ms | **49.4 ms** | 19.1 ms |

- → VSA（voxel → keypoint）大約佔**一半**的時間。

**結論**：要 3D 結構，但不要 point-voxel 轉換 → **直接從 3D voxel 特徵取 RoI 特徵**。

## 核心方法

架構（Figure 2）：**Voxel 化 → 3D backbone（sparse conv）→ 轉 BEV → 2D backbone + RPN 產生候選框 → Voxel RoI Pooling（從 3D 特徵取）→ Detect head 精修**

對照 Figure 1：
- STD、PV-RCNN 從**點**的表示取 RoI 特徵。
- Voxel R-CNN 直接從 **3D voxel 特徵**取。

### 1. Voxel RoI Pooling（§3.1，核心貢獻）
- 把非空 voxel 視為「點」：用 voxel 中心座標 + 特徵向量表示。
- 每個候選框切成 **6×6×6** 個子格，以各子格中心為格點（grid point）。
- 3D 特徵非常稀疏，非空 voxel 不到 3% 的空間，所以不能直接對子格做 max pooling（大多是空的）→ 改成每個格點**向周圍的 voxel 收集特徵**：
  - `η_i = max_k MLP([v_k − g_i ; φ_k])`（Eq. 2）：相對座標 + voxel 特徵 → MLP → max pooling。
- 從 3D backbone 的**最後兩個 stage** 取特徵，每個 stage 用兩種距離門檻（多尺度），全部串接成 RoI 特徵。
- 詳見 [RoI Pooling](../concepts/roi-pooling.md)。

### 2. Voxel Query（加速找鄰居）
- 點雲是無序的，找鄰居要用 **ball query**：掃過所有 N 個點算距離，O(N)。
- Voxel 排列在規則格子上，鄰居可以直接用**索引加減**算出來，例如 (i±1, j±1, k±1) 就是周圍 26 格 → O(K)，K 為鄰居數。
- 用**曼哈頓距離** `|Δi| + |Δj| + |Δk|` 當門檻，KITTI 設為 2 和 4（§4.2）。
- 白話：在一棟大樓裡找鄰居，ball query 是問遍全大樓「你離我多遠」，voxel query 是直接敲隔壁和上下樓的門。

### 3. Accelerated PointNet Module（加速特徵匯總）
- 原本：每個格點收集 K 個 voxel，每個都要過 FC 層，計算量 O(M × K × (C+3) × C′)，M 為格點總數。
- 拆解：FC 權重 W 拆成「特徵部分 W_F」和「座標部分 W_C」。
  - voxel 特徵和格點無關 → **分組前**先對 N 個 voxel 各算一次 W_F。
  - 分組後只需計算 3 維相對座標的 W_C。
- 計算量降為 O(N × C × C′ + M × K × 3 × C′)。M × K 比 N 大一個數量級，所以省很多（§3.1）。

### 4. Backbone、RPN、Detect head（§3.2–3.4）
- 3D backbone 沿用 SECOND / PV-RCNN 的設計，4 個 stage，通道數 16、32、48、64。
- 2D backbone：2 個 block，各 5 層卷積。
- RPN：anchor-based，focal loss + Huber loss。
- Detect head：2 層 MLP，再分成兩支：
  - 框殘差回歸
  - IoU 相關的信心分數：IoU < 0.25 → 0；IoU > 0.75 → 1；中間線性插值（Eq. 4）
- 訓練時每個場景取 128 個 RoI，正負各半；IoU > 0.55 才算回歸 loss。
- KITTI voxel 大小 (0.05, 0.05, 0.1) m，和 PV-RCNN 相同。

## 主要結果

**KITTI val**（Car 3D AP）：

| 口徑 | Easy | Moderate | Hard | 出處 |
|---|---|---|---|---|
| R11 | 89.41 | **84.52** | 78.93 | Table 5 |
| R40 | 92.38 | 85.29 | 82.86 | Table 4 |

同一張表的比較（val R11, Car Mod., Table 5）：

| 類型 | 方法 | Car Mod. |
|---|---|---|
| point-based | PointRCNN | 78.63 |
| | STD | 79.80 |
| | PV-RCNN | 83.69 |
| voxel-based | SECOND | 78.62 |
| | PointPillars | 76.06 |
| | Part-A² | 79.47 |
| | SA-SSD | 79.91 |
| | **Voxel R-CNN** | **84.52** |

**KITTI test**（R40, Car, Table 3，含 FPS）：

| 方法 | FPS | Easy | Mod. | Hard |
|---|---|---|---|---|
| PV-RCNN | 8.9 | 90.25 | 81.43 | 76.82 |
| SECOND | 30.4 | 83.34 | 72.55 | 65.82 |
| PointPillars | 42.4 | 82.58 | 74.31 | 68.99 |
| SA-SSD | 25.0 | 88.75 | 79.79 | 74.16 |
| **Voxel R-CNN** | **25.2** | **90.90** | **81.62** | **77.06** |

- 精度和 PV-RCNN 相當，執行時間約只有 **1/3**（§4.3）。
- 比 SA-SSD（當時最強的 voxel-based 方法）在 Easy / Mod. / Hard 分別高 2.15 / 1.83 / 2.90（§4.3）。
- Voxel R-CNN 自己的 FPS 量測環境是 RTX 2080 Ti（摘要）；**表中其他方法 FPS 的來源和硬體，原文沒有說明**。

**Waymo**（Vehicle, 3D mAP, IoU 0.7, Table 6）：

| 方法 | LEVEL 1 全部 | 0–30 m | 30–50 m | 50 m+ |
|---|---|---|---|---|
| PV-RCNN | 70.30 | 91.92 | 69.21 | 42.17 |
| **Voxel R-CNN** | **75.59** | **92.49** | **74.09** | **53.15** |

- **遠距離（50 m 以上）的進步最大**：+10.98（§4.4）。
- LEVEL 2：66.59 vs PV-RCNN 65.36。

### 消融實驗（val R11, Car Mod., Table 7）

| 設定 | 精修頭 | Voxel Query | Accel. PointNet | AP | FPS |
|---|---|---|---|---|---|
| (a) one-stage | | | | 77.99 | 40.8 |
| (b) | ✓ | | | 84.21 | 17.4 |
| (c) | ✓ | ✓ | | 84.33 | 19.1 |
| (d) | ✓ | | ✓ | 84.27 | 21.4 |
| (e) Voxel R-CNN | ✓ | ✓ | ✓ | 84.52 | 25.2 |

- 加上精修頭：**+6.2 AP**，但 FPS 少了 23.4（原本的 ball query 和 PointNet 很慢）。
- Voxel Query 和 Accelerated PointNet 主要是**拿回速度**，精度幾乎不變。

## 和其他方法的關係

- **基礎**：[SECOND](second.md) 的 sparse 3D backbone；[PV-RCNN](pv-rcnn.md) 的 two-stage 框架、6×6×6 格點、IoU-guided 信心分數。
- **對比**：PV-RCNN 用 point 補精度，Voxel R-CNN 證明 voxel 就夠。見 [PV-RCNN vs Voxel R-CNN](../comparisons/pv-rcnn-vs-voxel-rcnn.md)。
- **後續**：
  - [CasA](casa.md)：在 Voxel R-CNN 上加 cascade attention（CasA+V）。
    - val R11 Car Mod.：84.52 → 86.58（CasA Table III）
    - test R40 Car Mod.：81.62 → 83.06（CasA Table IV）
    - 代價：3 個階段 86 ms（單張 3090，CasA Table VI）。
  - [NV3D](nv3d.md)：沿用 Voxel R-CNN 的完整架構，在輸入端加入法向量特徵和取樣。在同一張表中，Car Mod. 為 84.78，Voxel R-CNN 為 85.29（NV3D Table 7，val R40）。
- 作者自己的定位：「一個簡單但有效的 baseline，方便後續研究。」（§1）

## 限制與討論

- （整理）只有 Car 類的 KITTI 結果，原文沒有報告 Pedestrian / Cyclist。
- （整理）仍是 anchor-based 的 RPN，第一階段和 SECOND 相同。精度提升主要來自第二階段。
- 跨論文數字的出入：本文重跑的 SECOND（78.62）、PointPillars（76.06）、PV-RCNN（83.69），和各自原論文（76.48、77.98、83.90）不同。原文沒有說明原因，推測是用 OpenPCDet 重新訓練（整理）。見 [KITTI 注意事項](../concepts/kitti-benchmark.md#跨論文比較數字的注意事項)。

## 相關概念

[RoI Pooling](../concepts/roi-pooling.md) · [One-stage vs Two-stage](../concepts/one-stage-vs-two-stage.md) · [Sparse Convolution](../concepts/sparse-convolution.md) · [Voxelization](../concepts/voxelization.md) · [KITTI Benchmark](../concepts/kitti-benchmark.md) · [Waymo Open Dataset](../concepts/waymo-open-dataset.md)
