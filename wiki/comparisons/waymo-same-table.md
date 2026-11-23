# Waymo 同表比較

> 規則 B：以同一張來源表格為準。
> **主表：LION Table 1**（使用者決定方案 A，2026-11-23，取代原本的 VoxelNeXt Table 15）。
> 為什麼需要這頁：[VoxelNeXt](../papers/voxelnext.md) 沒有 KITTI 結果，[LION](../papers/lion.md) 的 KITTI 結果只是附錄。**Waymo 是唯一能把新趨勢方法和主線方法放在同一張表比較的資料集**。
> 指標說明見 [Waymo Open Dataset](../concepts/waymo-open-dataset.md)。

## 主表：LION Table 1（Waymo val，100% 訓練資料，單幀，無測試增強）

| 方法 | Backbone | 架構 | Vehicle L1 AP / APH | Ped. L1 AP / APH | Cyc. L1 AP / APH | **L2 mAP / mAPH** |
|---|---|---|---|---|---|---|
| [SECOND](../papers/second.md) | sparse conv | one-stage | 72.3 / 71.7 | 68.7 / 58.2 | 60.6 / 59.3 | 61.0 / 57.2 |
| [PointPillars](../papers/pointpillars.md) | sparse conv | one-stage | 72.1 / 71.5 | 70.6 / 56.7 | 64.4 / 62.3 | 62.8 / 57.8 |
| CenterPoint | sparse conv | one-stage | 74.2 / 73.6 | 76.6 / 70.5 | 72.3 / 71.1 | 68.2 / 65.8 |
| [PV-RCNN](../papers/pv-rcnn.md) | sparse conv | two-stage | 78.0 / 77.5 | 79.2 / 73.0 | 71.5 / 70.3 | 69.6 / 67.2 |
| PV-RCNN++ | sparse conv | two-stage | 79.3 / 78.8 | 81.3 / 76.3 | 73.7 / 72.7 | 71.7 / 69.5 |
| FSD | sparse conv | two-stage | 79.2 / 78.8 | 82.6 / 77.3 | 77.1 / 76.0 | 72.9 / 70.8 |
| [VoxelNeXt](../papers/voxelnext.md) | sparse conv | one-stage, fully sparse | 78.2 / 77.7 | 81.5 / 76.3 | 76.1 / 74.9 | 72.2 / 70.1 |
| HEDNet | sparse conv | one-stage | **81.1 / 80.6** | 84.4 / 80.0 | 78.7 / 77.7 | 75.3 / 73.4 |
| DSVT-Voxel | Transformer | one-stage | 79.7 / 79.3 | 83.7 / 78.9 | 77.5 / 76.5 | 74.0 / 72.1 |
| [LION](../papers/lion.md)-Mamba | linear RNN | one-stage | 79.5 / 79.1 | 84.9 / 80.4 | 79.7 / 78.7 | 75.1 / 73.2 |
| **LION-Mamba-L** | linear RNN | one-stage | 80.3 / 79.9 | **85.8 / 81.4** | **80.1 / 79.0** | **75.9 / 74.0** |

「架構」欄的 two-stage 依 LION Table 1 的 ‡ 標記；其餘為 one-stage（整理）。

## 第二張表：VoxelNeXt Table 15（原主表，保留）

| 方法 | Vehicle L1 AP / APH | L2 mAP / mAPH |
|---|---|---|
| SECOND | 72.3 / 71.7 | 61.0 / 57.2 |
| PointPillars | 72.1 / 71.5 | 62.8 / 57.8 |
| PV-RCNN | 77.5 / 76.9 | 66.8 / 63.3 |
| PV-RCNN++ | 78.8 / 78.2 | 68.4 / 64.9 |
| CenterPoint | 76.6 / 76.0 | 69.8 / 67.6 |
| FSD | 77.8 / 77.3 | 71.9 / 69.7 |
| VoxelNeXt (K3) | 78.2 / 77.7 | 72.2 / 70.1 |

## ⚠️ 兩張表的數字不一致

| 方法 | VoxelNeXt T15：Vehicle L1 | LION T1：Vehicle L1 | VoxelNeXt T15：L2 mAPH | LION T1：L2 mAPH | 一致？ |
|---|---|---|---|---|---|
| SECOND | 72.3 | 72.3 | 57.2 | 57.2 | ✅ |
| PointPillars | 72.1 | 72.1 | 57.8 | 57.8 | ✅ |
| VoxelNeXt | 78.2 | 78.2 | 70.1 | 70.1 | ✅ |
| PV-RCNN | 77.5 | **78.0** | 63.3 | **67.2** | ❌ |
| PV-RCNN++ | 78.8 | **79.3** | 64.9 | **69.5** | ❌ |
| CenterPoint | 76.6 | **74.2** | 67.6 | **65.8** | ❌ |
| FSD | 77.8 | **79.2** | 69.7 | **70.8** | ❌ |

- 兩篇論文都**沒有說明**引用的是哪個版本或設定。
- VoxelNeXt T15 中 PV-RCNN 的 77.5 / 76.9 和 PV-RCNN 原論文 Table 6（v1.2）一致；LION 的 78.0 / 77.5 來源不明。
- 規則 B 的價值：在**同一張表內**比較，結論才可靠。不要拿 LION 表中的 LION 和 VoxelNeXt 表中的 PV-RCNN 相比。

## 不在兩張表中、只供參考

| 方法 | Vehicle L1 AP / APH | 來源 | 備註 |
|---|---|---|---|
| [Voxel R-CNN](../papers/voxel-rcnn.md) | 77.43 / 76.71 | CasA Table V | CasA 作者重跑，v1.2 |
| [CasA](../papers/casa.md)+V | 78.54 / 78.00 | CasA Table V | v1.2 |

## 觀察（整理，以主表為準）

1. **Backbone 演進**：sparse conv（SECOND 57.2）→ two-stage（PV-RCNN 67.2）→ fully sparse（VoxelNeXt 70.1）→ Transformer（DSVT 72.1）→ linear RNN（LION-Mamba 73.2、-L 74.0），單位為 L2 mAPH。
2. **但 sparse conv 並沒有被淘汰**：HEDNet（sparse conv）的 73.4 高於 LION-Mamba 的 73.2，Vehicle 也是全表最高。只有 LION-Mamba-L（通道數加倍）才全面超越。
3. **行人、自行車進步最多**：SECOND → LION-Mamba-L，Ped. L1 APH 58.2 → 81.4、Cyc. 59.3 → 79.0；Vehicle 只從 71.7 → 79.9。
4. **one-stage 新方法在整體分數上超越 two-stage**（PV-RCNN++ 69.5 vs VoxelNeXt 70.1、LION 73.2）。
