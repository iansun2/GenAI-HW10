# Anchor-free 與 Sparse Head（偵測頭怎麼「指出物體在哪」）

## 白話解釋（給初學者）

backbone 抽完特徵後，**偵測頭（head）**要回答：「物體在哪裡？框多大？」
主要有三種做法：

| 做法 | 比喻 | 代表 |
|---|---|---|
| **Anchor-based** | 在地圖的每個格子都擺好「標準尺寸的車子模型」，逐一判斷「這裡有沒有車、要怎麼調整」 | [SECOND](../papers/second.md)、[PointPillars](../papers/pointpillars.md)、[Voxel R-CNN](../papers/voxel-rcnn.md) 的 RPN |
| **Center-based（anchor-free）** | 在地圖上畫一張「哪裡像物體中心」的熱度圖，找出最熱的點，再從那裡長出框 | CenterPoint（透過 VoxelNeXt 得知） |
| **Sparse voxel-based** | 不畫整張圖，只讓「有資料的格子」各自舉手說「我屬於某個物體，框是這樣」 | [VoxelNeXt](../papers/voxelnext.md) |

前兩種都需要把特徵轉成**完整的 2D 圖（dense）**，每個位置都要計算；第三種只在有資料的地方計算。

## 為什麼要擺脫 dense head

- **浪費**：CenterPoint 的 heatmap 上，nuScenes Car 類別有反應的位置**不到 1%**（VoxelNeXt §1）。
- **成本隨偵測範圍暴增**：偵測範圍從 50 m 到 200 m，CenterPoint 的 head 從 54 ms 增加到 218 ms；VoxelNeXt 的 sparse head 只從 26 ms 增加到 28 ms（VoxelNeXt Fig. 3，Argoverse2）。
- **設計來源不合**：anchor 和 center 是為 2D 影像（規則、密集）設計的，沒有考慮 3D 點雲的稀疏性（VoxelNeXt §1）。

## 「物體中心」的問題

- LiDAR 只會打到物體的**表面**，物體中心通常沒有點。
- Center-based 方法要在「空的中心」預測物體，所以需要 dense 特徵圖或投票機制（FSD）。
- VoxelNeXt 的發現（Table 7，nuScenes val）：
  - 負責預測框的 voxel，只有 **9.9%** 在中心附近。
  - **72.8%** 在邊界附近。
  - **17.3%** 甚至在框外（行人為 45.2%）。
  - → **物體中心不是必要的**，只要感受野夠大，邊界上的 voxel 也能預測整個框。

## NMS 和 Sparse Max Pooling

- **NMS（Non-Maximum Suppression）**：同一個物體常被預測出好幾個框，NMS 只保留信心最高的那個，刪掉和它重疊太多的其他框。
  - 前面所有論文都用 NMS，例如 PV-RCNN 推論時 IoU 門檻 0.7、Voxel R-CNN 0.1（各自的 §4）。
- **Sparse Max Pooling**（VoxelNeXt）：在非空 voxel 上做局部 max pooling，只保留局部分數最高的 voxel，直接達到去重的效果。
  - 效果（VoxelNeXt Table 10，nuScenes val）：只用 NMS 56.0 mAP；只用 max pooling **56.2**；兩個都不用只有 33.0。

## 和 Anchor 的關係

- Anchor 的編碼方式見 [Anchor 與 Box Encoding](anchor-and-box-encoding.md)。
- VoxelNeXt 的角度用 (sin α, cos α) 回歸（VoxelNeXt §3.2），和 SECOND 的 sin-error loss 不同。

## 出現在哪些論文

- Anchor-based：[SECOND](../papers/second.md)、[PointPillars](../papers/pointpillars.md)、[PV-RCNN](../papers/pv-rcnn.md)、[Voxel R-CNN](../papers/voxel-rcnn.md)、[CasA](../papers/casa.md)（RPN 部分）
- Sparse voxel-based：[VoxelNeXt](../papers/voxelnext.md)
- [LION](../papers/lion.md)：只改 backbone，head 沿用其他方法。Waymo 用 DSVT 的 center-based head，Argoverse2 和 ONCE 用 CenterPoint head，KITTI 用 SECOND 的 anchor head（LION §4.2、A.1）。

## 常見誤解

- 「anchor-free 就是 sparse」→ 不是。CenterPoint 是 anchor-free，但仍然是 **dense** head。
- 「拿掉 dense head 就會變快又一樣準」→ 直接拿掉時 mAP 從 55.6 掉到 46.7，大物體掉最多（VoxelNeXt Table 2）。必須補上額外下採樣來擴大感受野。
