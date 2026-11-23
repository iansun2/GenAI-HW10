# Waymo Open Dataset

## 白話解釋（給初學者）

Waymo（Google 旗下的自駕車公司）公開的大型資料集，比 [KITTI](kitti-benchmark.md) **大得多**，而且標註了 **360° 全方位**的物體（KITTI 只有前方約 90°）（PV-RCNN §4.1）。
如果說 KITTI 是小考，Waymo 就是期末考：場景更多、更多樣，也更接近實際自駕車要處理的情況。

## 資料規模（PV-RCNN §4.1）

| | 序列數 | LiDAR 樣本數 |
|---|---|---|
| Training | 798 | 約 158,361 |
| Validation | 202 | 40,077 |

- 版本：v1.0（2019 年 8 月）、v1.2（2020 年 3 月）。**不同版本的數字不能直接比**（PV-RCNN Table 5 / 6）。
- 常見偵測範圍：x、y ∈ [−75.2, 75.2] m，z ∈ [−2, 4] m（PV-RCNN §4.1），比 KITTI 的 x∈[0, 70.4] 大很多，因為要涵蓋全方位。

## 評估指標（PV-RCNN §4.3）

- **mAP**：和 KITTI 類似的平均精度。
- **mAPH**（mAP weighted by Heading）：**有考慮朝向**的 mAP，朝向錯了會被扣分。
  - 對照：KITTI 的 3D AP 不看朝向，要另外看 AOS。
- **IoU 門檻**：Vehicle 0.7；Pedestrian、Cyclist 0.5。
- **難度分級**（不同於 KITTI 的 Easy/Moderate/Hard）：
  - **LEVEL 1**：框內至少 5 個點。
  - **LEVEL 2**：框內至少 1 個點，或人工標為 LEVEL 2。比較難，包含點很少的物體。
- **距離分段**：0–30 m、30–50 m、50 m 以上。可以看出模型在遠距離是否退化。

⚠️ **LEVEL 定義在不同論文中描述不一**：
- PV-RCNN §4.3：LEVEL 1 = 至少 5 個點；LEVEL 2 = 至少 1 個點，**或人工標為 LEVEL 2**。
- Voxel R-CNN §4.4：LEVEL 1 = 多於 5 個點；LEVEL 2 = 1–5 個點。
- LION §4.1：L1 = 多於 5 個點；L2 = 至少 1 個點。
- 三篇論文的描述在「剛好 5 點」和「人工標記」的處理上不同。PV-RCNN 的描述最完整，本 wiki 以它為準（整理）。若要確認，需查 Waymo 官方文件（不在 raw 資料中）。

**其他規格（LION §4.1）**：共 1150 個場景（train 798 / val 202 / test 150），每個場景約 200 幀，感知範圍 150 m × 150 m。

## 代表數字（Vehicle LEVEL 1，3D mAP）

| 方法 | Waymo 版本 | mAP | 出處 |
|---|---|---|---|
| PointPillars | v1.0 | 56.62 | PV-RCNN Table 5（由 MVF 論文重現） |
| PV-RCNN | v1.0 | 70.30 | PV-RCNN Table 5 |
| SECOND | v1.2 | 72.27 | PV-RCNN Table 6（PV-RCNN 作者用開源碼重跑） |
| PV-RCNN | v1.2 | 77.51 | PV-RCNN Table 6 |
| Voxel R-CNN | 未註明（202 個 val 序列） | 75.59 | Voxel R-CNN Table 6 |
| Voxel R-CNN（CasA 作者重跑） | v1.2 | 77.43 | CasA Table V；版本出自 CasA README |
| CasA+V | v1.2 | 78.54 | CasA Table V |

- 注意同一個 Voxel R-CNN 有 75.59 和 77.43 兩個數字，推測是 Waymo 版本不同。PV-RCNN 的 70.30（v1.0）和 77.51（v1.2）也是同樣的情況。（整理）
- CasA 對 **Pedestrian** 的進步最大：Voxel R-CNN 76.37 → CasA+V 80.88（LEVEL 1 mAP，CasA Table V）。

- Voxel R-CNN Table 6 中 PV-RCNN 為 70.30，和 PV-RCNN 的 v1.0 數字相同，推測比較的是 v1.0。（整理）
- 距離的影響：PV-RCNN（v1.0, LEVEL 1）在 0–30 m 為 91.92，到 50 m 以上只剩 42.17（PV-RCNN Table 5）。**遠距離仍然是難題**。
  - Voxel R-CNN 在 50 m 以上為 53.15，比 PV-RCNN 高 10.98（Voxel R-CNN Table 6）。

## 同表比較

見 [Waymo 同表比較](../comparisons/waymo-same-table.md)（主表為 LION Table 1，涵蓋 SECOND、PV-RCNN、VoxelNeXt、DSVT、HEDNet、LION 等；VoxelNeXt Table 15 為第二張表）。

## 出現在哪些論文

[PV-RCNN](../papers/pv-rcnn.md)、[Voxel R-CNN](../papers/voxel-rcnn.md)、[CasA](../papers/casa.md)、[VoxelNeXt](../papers/voxelnext.md)、[LION](../papers/lion.md)。

## 常見誤解

- 「Waymo mAP 和 KITTI AP 可以比」→ 資料集、IoU 規則、難度定義都不同，不能比。
- 「同樣是 Waymo，數字就能比」→ 還要看版本（v1.0 / v1.2）和 LEVEL。
