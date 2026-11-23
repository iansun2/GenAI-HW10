# VoxelNeXt: Fully Sparse VoxelNet for 3D Object Detection and Tracking

> 出處：CVPR 2023 · arXiv 2303.11301v1 · `raw/papers/voxelnext.pdf` · 程式碼：github.com/dvlab-research/VoxelNeXt
> 作者：Yukang Chen, Jianhui Liu, Xiangyu Zhang, Xiaojuan Qi, Jiaya Jia（CUHK / HKU / MEGVII）
> 資料限制：
> - **沒有 KITTI 結果**，只在 nuScenes、Waymo、Argoverse2 上評估，所以無法放進本 wiki 的 KITTI 主表。
> - Table 10 的 ✓/✗ 在抽出的文字中遺失，已轉成圖片人工讀取。
> - 同一篇論文中 CenterPoint 有四組數字（見資料品質備註）。

## 一句話總結

**全程 sparse** 的偵測器：不把特徵轉回 dense BEV 圖，也不用 anchor、center heatmap、RPN、RoI pooling 和 NMS，**直接由 sparse voxel 預測物體**。在 nuScenes 上比 CenterPoint 更準、更快，而且偵測範圍越大，速度優勢越明顯。

## 要解決的問題（動機）

- 前面所有方法（[SECOND](second.md)、[PointPillars](pointpillars.md)、[PV-RCNN](pv-rcnn.md)、[Voxel R-CNN](voxel-rcnn.md)、CenterPoint）都把 3D sparse 特徵**轉成 2D dense 的 BEV 圖**，再用 dense head 預測（Fig. 2）。
- dense head 繼承自 2D 影像偵測（anchor、center），**是為規則、密集的影像設計的**，沒有考慮 3D 資料的稀疏性（§1）。
- **大量浪費**：CenterPoint 的 heatmap 上絕大多數位置接近 0；nuScenes val 中 Car 類別有反應的位置**不到 1%**，但 dense head 每個位置都要計算（§1、Fig. 1）。
- 還要用 **NMS** 去除重複預測，流程複雜（§1）。
- （整理）這和 [SECOND](second.md) 當初的動機一樣：不要在空的地方計算。SECOND 解決了 backbone 的部分，VoxelNeXt 把它延伸到 **head**。

## 核心方法

架構（Fig. 4）：**Voxel → Sparse 3D CNN（6 個 stage，含 2 層額外下採樣 + voxel pruning）→ Sparse 高度壓縮成 2D sparse 特徵 → 每個 voxel 預測分數 → Sparse max pooling 選出 query voxel → 直接回歸框**

### 1. 額外下採樣（擴大感受野）（§3.1）
- 原本的 sparse CNN 有 4 個 stage（stride 1、2、4、8）。少了 dense head 後，**感受野不夠**，尤其是大物體。
- 解法很簡單：**多加 2 層下採樣**（stride 16、32），把最後三個 stage 的特徵對齊到 stride 8 後合併（Eq. 1）。
- 效果（nuScenes val，Table 2）：

| 版本 | Stride | 延遲 | mAP | NDS | Truck | Bus |
|---|---|---|---|---|---|---|
| CenterPoint（dense head） | 2, 4, 8 | 96 ms | 55.6 | 63.2 | 54.9 | 67.5 |
| D3（直接拿掉 dense head） | 2, 4, 8 | 56 ms | 46.7 | 56.2 | 41.3 | 38.3 |
| D3 + 5×5×5 大 kernel | 2, 4, 8 | 225 ms | 51.6 | 60.4 | 49.2 | 56.8 |
| D5（**+2 層下採樣**） | 2…32 | 66 ms | **56.5** | **64.5** | 54.0 | 67.4 |

  → 直接拿掉 dense head，大物體掉很多（Bus 67.5 → 38.3）；加大 kernel 有幫助但很慢；**多 2 層下採樣**便宜又有效。
- 最後兩層的 voxel 很少（3.0K、1.3K），計算量合計不到整個 backbone 的 1/3（Table 9）。

### 2. Sparse 高度壓縮（§3.1）
- 其他方法：sparse → dense，再把 z 軸併入 channel。
- VoxelNeXt：**把所有 voxel「放到地面上」，同一個 (x, y) 位置的特徵直接相加**（Eq. 2），全程維持 sparse，耗時不到 1 ms。
- 用 3D backbone + 2D sparse head 時，延遲 66 ms、mAP 56.2；若 head 也用 3D，延遲 92 ms、mAP 56.3（Table 5）。

### 3. Spatial Voxel Pruning（§3.1）
- 下採樣時，sparse conv 會讓每個 voxel 往外「擴張」（見 [Sparse Convolution](../concepts/sparse-convolution.md)）。
- VoxelNeXt 只讓**特徵強度排前 50%** 的 voxel 擴張，其餘不擴張（沿用 SPS-Conv）。
- 效果（Table 3）：

| 剪除比例 | 0 | 0.3 | **0.5** | 0.7 | 0.9 |
|---|---|---|---|---|---|
| FLOPs (G) | 83.8 | 60.1 | **33.6** | 19.8 | 7.6 |
| mAP | 56.5 | 56.4 | **56.2** | 53.7 | 45.1 |

  → 剪掉一半，FLOPs 少六成，mAP 只掉 0.3。
- 只用在前 3 個下採樣層（Table 4）。

### 4. Sparse Prediction Head（§3.2）
- **Voxel selection**：每個 voxel 預測 K 個類別的分數。訓練時，**最靠近 GT 框中心的 voxel** 為正樣本（focal loss）。
- **Box regression**：直接從被選中的 voxel 特徵回歸位置偏移、高度、3D 大小、角度 (sin α, cos α)。nuScenes 另外回歸速度；Waymo 另外預測 IoU。
  - 用 3×3 submanifold sparse conv 比 FC 層好（mAP 56.8 vs 56.2），只多 5 ms（Table 6）。表中標為 K3 的版本即使用 3×3 conv。
- **用 Sparse max pooling 取代 NMS**：只在非空的位置做 max pooling，留下局部最大值（Table 10，nuScenes val）：

| Max-pool | NMS | mAP | NDS |
|---|---|---|---|
| ✗ | ✗ | 33.0 | 51.0 |
| ✗ | ✓ | 56.0 | 64.2 |
| ✓ | ✗ | **56.2** | **64.3** |
| ✓ | ✓ | 56.2 | 63.3 |

  → max pooling 單獨使用就和 NMS 一樣好，兩個都不用就會大幅退步（重複的框太多）。

### 5. 負責預測的 voxel 在哪裡？（Table 7，nuScenes val，只統計高品質預測）

| | 平均 | Car | Truck | Ped |
|---|---|---|---|---|
| 接近中心 | 9.9% | 10.3% | 5.6% | 12.5% |
| 接近邊界 | **72.8%** | 84.3% | 39.2% | 42.3% |
| **框外** | 17.3% | 5.4% | **55.3%** | **45.2%** |

- **物體中心不是必要的**：LiDAR 點本來就在物體**表面**，中心通常是空的（§3）。
- 行人和卡車約一半由框外的 voxel 預測。

### 6. 3D 追蹤（§3.3）
- CenterPoint 用預測的中心點配對前後幀。
- VoxelNeXt 額外用**負責預測的 voxel 位置**配對。voxel 是真實存在的資料，比預測的中心偏差小。
- AMOTA：69.1 → 70.2（nuScenes val，Table 11）。

## 主要結果

### nuScenes test（Table 12，同一張表，LiDAR only）

| 方法 | mAP | NDS | 延遲 |
|---|---|---|---|
| PointPillars | 30.5 | 45.3 | 31 ms |
| CenterPoint | 58.0 | 65.5 | 96 ms |
| Focals Conv | 63.8 | 70.0 | 138 ms |
| PillarNet-18† | 65.0 | 70.8 | 78 ms |
| VoxelNeXt-2D | 64.1 | 69.8 | **61 ms** |
| **VoxelNeXt** | 64.5 | 70.0 | 66 ms |
| VoxelNeXt† | **66.2** | **71.4** | – |

† = double-flip 測試增強。PillarNet-18† 有用增強，所以和沒有增強的 VoxelNeXt 不能直接比。

### nuScenes 追蹤 test（Table 13）
- VoxelNeXt AMOTA 69.5；VoxelNeXt† **71.0**，在 nuScenes LiDAR-only 追蹤排行榜排名第 1（§4.2）。

### Waymo val（Table 15，同一張表）

| 方法 | 整體 L2 mAP / mAPH | Vehicle L1 AP / APH | Ped. L1 AP / APH |
|---|---|---|---|
| SECOND | 61.0 / 57.2 | 72.3 / 71.7 | 68.7 / 58.2 |
| PointPillars | 62.8 / 57.8 | 72.1 / 71.5 | 70.6 / 56.7 |
| PV-RCNN | 66.8 / 63.3 | 77.5 / 76.9 | 75.0 / 65.6 |
| PV-RCNN++ | 68.4 / 64.9 | **78.8 / 78.2** | 76.7 / 67.2 |
| CenterPoint | 69.8 / 67.6 | 76.6 / 76.0 | 79.0 / 73.4 |
| FSD | 71.9 / 69.7 | 77.8 / 77.3 | **81.9 / 76.4** |
| **VoxelNeXt (K3)** | **72.2 / 70.1** | 78.2 / 77.7 | 81.5 / 76.3 |

- 整體最高，但 Vehicle 輸給 PV-RCNN++，Pedestrian 和 FSD 接近。
- 表中 SECOND、PV-RCNN 的數字和 PV-RCNN 論文 Table 6（Waymo v1.2）一致 ✅。

### Argoverse2（長距離，最遠 200 m）
- mAP（Table 16）：CenterPoint 22.0、FSD 28.2、VoxelNeXt 30.0、VoxelNeXt K3 **30.7**。
- **延遲 vs 偵測範圍**（Fig. 3，RTX 2080 Ti，batch 1，voxel 0.1×0.1×0.2 m）：

| 偵測範圍 | 50 m | 100 m | 150 m | 200 m |
|---|---|---|---|---|
| CenterPoint 整體 | 82 | 113 | 164 | **246** ms |
| FSD 整體 | 81 | 92 | 96 | 99 ms |
| **VoxelNeXt 整體** | 61 | 63 | 65 | **66** ms |
| CenterPoint head | 54 | 78 | 128 | 218 ms |
| VoxelNeXt head | 26 | 27 | 28 | 28 ms |

→ dense head 的成本隨**面積**成長（範圍加倍，面積變 4 倍）；sparse head 只和**有資料的 voxel 數**有關，幾乎不變。（解讀為整理）

## 和其他方法的關係

- **基礎**：
  - [SECOND](second.md) 的 sparse CNN backbone。
  - CenterPoint 的回歸目標設計（本 wiki 未 ingest CenterPoint，只透過 VoxelNeXt 得知）。
  - SPS-Conv 的 voxel pruning。
- **對比**：
  - [Voxel R-CNN](voxel-rcnn.md)、[CasA](casa.md) 走「dense RPN + RoI 精修」的 two-stage 路線，追求精度。
  - VoxelNeXt 走「**全 sparse、one-stage、無 NMS**」路線，追求效率和長距離的擴展性。
- 同為 fully sparse 的 FSD：用投票找中心再迭代修正，流程複雜，效率也不如 VoxelNeXt（§1、Fig. 3）。
- **後續**：[LION](lion.md)
  - 在 Argoverse2 上把 VoxelNeXt 的 3D backbone 換成 LION：30.7 → 41.5 mAP（LION Table 3）。
  - Waymo L2 mAPH：70.1 → 73.2（LION Table 1）。

## 限制與討論

- **FLOPs ≠ 實際速度**（§5，作者自述）：VoxelNeXt 38.7G FLOPs，CenterPoint 186.6G，約 1/5；但延遲是 66 ms vs 96 ms，只少約 1/3。實際速度還受實作和硬體影響。
- 沒有 KITTI 結果，無法直接和本 wiki 主線（Voxel R-CNN、CasA）比較 KITTI 精度。
- （整理）它是 one-stage，沒有 RoI 精修；在 Waymo Vehicle 上仍略輸 two-stage 的 PV-RCNN++（78.2 vs 78.8 L1 AP，Table 15）。

## 資料品質備註（本次 ingest 發現）

- **CenterPoint 在同一篇論文有四組數字**（nuScenes mAP / NDS）：

| 表 | mAP / NDS | 設定 |
|---|---|---|
| Table 1 | 58.6 / 66.2 | 未說明 |
| Table 2 | 55.6 / 63.2 | 未說明（VoxelNeXt D5 = 56.5 / 64.5，和 Table 8 相同） |
| Table 8 | 55.6 / 63.5 | 1/4 訓練資料，val |
| Table 12 | 58.0 / 65.5 | test |

  Table 2 和 Table 8 的 mAP 相同、NDS 不同（63.2 vs 63.5），論文沒有解釋。
- **Table 10 的 ✓/✗** 在抽出的文字中遺失，只剩數字 → 轉成圖片確認。

## 相關概念

[Anchor-free 與 Sparse Head](../concepts/anchor-free-and-sparse-head.md) · [Sparse Convolution](../concepts/sparse-convolution.md) · [nuScenes 與 Argoverse2](../concepts/nuscenes-and-argoverse2.md) · [Waymo Open Dataset](../concepts/waymo-open-dataset.md) · [Waymo 同表比較](../comparisons/waymo-same-table.md) · [Voxelization](../concepts/voxelization.md)
