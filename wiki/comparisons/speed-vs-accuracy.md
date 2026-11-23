# 速度 vs 精度比較

> 這一頁會隨著每篇論文 ingest 持續更新。
> **規則（使用者決定）：主表以「同一張來源表格」的數字為準**；原論文的數字放在備註欄。
> **閱讀前請先看** [KITTI：跨論文比較數字的注意事項](../concepts/kitti-benchmark.md#跨論文比較數字的注意事項)。

## 主表：KITTI val R11 — Car 3D AP

**來源：Voxel R-CNN Table 5**（目前涵蓋最多本 wiki 方法的同一張表）

| 方法 | 年份 | 架構 | 表示法 | Easy | **Mod.** | Hard | 原論文數字（備註） |
|---|---|---|---|---|---|---|---|
| VoxelNet | 2018 | one-stage | voxel（dense） | 81.97 | 65.46 | 62.85 | 同（SECOND Table 4） |
| [SECOND](../papers/second.md) | 2018 | one-stage | voxel（sparse） | 88.61 | 78.62 | 77.22 | Mod. 76.48（SECOND Table 4） |
| [PointPillars](../papers/pointpillars.md) | 2019 | one-stage | pillar | 86.62 | 76.06 | 68.91 | Mod. 77.98，推定 R11（PointPillars §5） |
| PointRCNN | 2019 | two-stage | point | 88.88 | 78.63 | 77.38 | – |
| STD | 2019 | two-stage | point | 89.70 | 79.80 | 79.30 | – |
| SA-SSD | 2020 | one-stage | voxel | 90.15 | 79.91 | 78.78 | – |
| [PV-RCNN](../papers/pv-rcnn.md) | 2020 | two-stage | point + voxel | 89.35 | 83.69 | 78.70 | Mod. 83.90（PV-RCNN Table 2） |
| [Voxel R-CNN](../papers/voxel-rcnn.md) | 2021 | two-stage | voxel | 89.41 | **84.52** | 78.93 | 本表即原論文 |
| [CasA](../papers/casa.md)+V | 2022 | multi-stage | voxel | 89.88 | 86.58 | 79.38 | ⚠️ **不在本表**，數字來自 CasA Table III，只供參考 |
| [NV3D](../papers/nv3d.md) | 2025 | two-stage | voxel + 法向量 | 89.32 | 84.13 | 78.77 | ⚠️ **不在本表**，數字來自 NV3D Table 5（不取樣），只供參考；arXiv 預印本 |

⚠️ CasA、NV3D 兩列和其他列**不是同一張表**（依規則 B 的例外處理，方案 A）。要公平比較，請看下方的「CasA Table III」和「NV3D Table 7」。

## 同表比較：CasA 加在不同 base detector 上（KITTI val）

**來源：CasA Table III**（同一篇論文、同樣的訓練設定）

| Base detector | Car Mod. R11 | +CasA | 提升 | Car Mod. R40 | +CasA | Ped. Mod. R40 | +CasA |
|---|---|---|---|---|---|---|---|
| PV-RCNN | 83.90 | 86.17 | +2.27 | 84.83 | 85.89 | 56.67 | 59.86 |
| Voxel R-CNN | 84.52 | 86.58 | +2.06 | 85.29 | 86.37 | 60.97 | 66.62 |
| CT3D | 86.06 | 86.63 | +0.57 | 85.82 | 86.42 | 58.56 | 62.59 |

- 這張表中 PV-RCNN、Voxel R-CNN 的 baseline 數字和兩者的原論文一致。
- base 越強（CT3D），CasA 帶來的提升越小。（整理）

## 同表比較：輸入取樣前後（KITTI val R40, Car）

**來源：NV3D Table 7**（max 16,000 voxels）。「三難度平均」= NV3D 論文所稱的 mAP。

| 方法 | 不取樣 Car Mod. | 不取樣三難度平均 | 取樣後（丟 53%）三難度平均 | 差異 |
|---|---|---|---|---|
| SECOND | 78.62 | 81.48 | 82.66 | +1.18 |
| PointPillars | 78.39 | 80.44 | 78.91 | −1.53 |
| PV-RCNN | 84.83 | 86.70 | 86.03 | −0.67 |
| Voxel R-CNN | **85.29** | **86.84** | 85.80 | −1.04 |
| NV3D | 84.78 | 86.60 | 85.54 | −1.06 |

- 在這張表中，**NV3D 的 Car 精度略低於 Voxel R-CNN**。
- 取樣方法本身是 NV3D 最有價值的貢獻：丟掉一半資料，大多數方法只掉約 1 個百分點。
- ⚠️ 表中 SECOND 的 88.61 / 78.62 / 77.22 標為 R40，但和 Voxel R-CNN Table 5 的 **R11** 數字完全相同，可能是誤標。詳見 [NV3D 資料品質備註](../papers/nv3d.md#資料品質備註本次-ingest-發現)。

## 速度表：KITTI test R40 — Car 3D AP + FPS

**來源：Voxel R-CNN Table 3**

| 方法 | 架構 | FPS | Easy | Mod. | Hard |
|---|---|---|---|---|---|
| SECOND | one-stage | 30.4 | 83.34 | 72.55 | 65.82 |
| PointPillars | one-stage | 42.4 | 82.58 | 74.31 | 68.99 |
| PointRCNN | two-stage | 10.0 | 86.96 | 75.64 | 70.70 |
| STD | two-stage | 12.5 | 87.95 | 79.71 | 75.09 |
| SA-SSD | one-stage | 25.0 | 88.75 | 79.79 | 74.16 |
| PV-RCNN | two-stage | 8.9 | 90.25 | 81.43 | 76.82 |
| **Voxel R-CNN** | two-stage | **25.2** | **90.90** | **81.62** | **77.06** |

⚠️ FPS 備註：
- 表中各方法的 FPS 來源和硬體，原文沒有說明。Voxel R-CNN 自己是在 RTX 2080 Ti 上量的。
- PointPillars 42.4 = 原論文的 **PyTorch 版**速度；原論文標題的 62 Hz 是 TensorRT 版（PointPillars §6）。
- SECOND 原論文為 20 FPS（0.05 s，GTX 1080 Ti，SECOND Table 2）。
- **CasA+V 不在本表**：自己報告 3 個階段 86 ms（約 11.6 FPS，單張 3090，CasA Table VI）。GPU 和 Voxel R-CNN 不同，不能直接比。

## 補充精度表：KITTI test R40（CasA Table IV，無 FPS）

涵蓋最多方法、三個類別的 test 表。

| 方法 | Car Mod. | Ped. Mod. | Cyc. Mod. |
|---|---|---|---|
| PointRCNN | 75.64 | 39.37 | 58.82 |
| STD | 79.71 | 42.47 | 61.59 |
| Part-A² | 78.49 | 43.35 | 63.52 |
| SA-SSD | 79.79 | – | – |
| PV-RCNN | 81.43 | 43.29 | 63.71 |
| Voxel R-CNN | 81.62 | – | – |
| CT3D | 81.77 | – | – |
| SE-SSD | 82.54 | – | – |
| BtcDet | 82.86 | 41.63 | 68.68 |
| **CasA+V** | **83.06** | **47.09** | **73.47** |

## 歷史參考：KITTI test R11（PointPillars Table 2）

2019-10-08 改用 R40 之前的口徑，只供了解早期方法的速度演進。

| 方法 | 速度 (Hz) | Car Mod. | Ped. Mod. | Cyc. Mod. |
|---|---|---|---|---|
| VoxelNet | 4.4 | 65.11 | 33.69 | 48.36 |
| SECOND | 20 | 73.66 | 42.56 | 53.85 |
| PointPillars | 62 | 74.99 | 43.53 | 59.07 |

## 觀察（整理）

1. **2018–2019：追求速度。**
   - VoxelNet → SECOND → PointPillars，速度 4.4 → 20 → 62 Hz（PointPillars Table 2）。
   - 手段都是減少空白空間上的計算：SECOND 用 sparse conv，PointPillars 拿掉 z 軸。
2. **2020：追求精度。**
   - PV-RCNN 用 two-stage + point 特徵，val R11 Car Mod. 達 83.69，比 SECOND 的 78.62 高約 5（Voxel R-CNN Table 5）。
   - 但速度只有 8.9 FPS（Voxel R-CNN Table 3）。
3. **2021：兼顧兩者。**
   - Voxel R-CNN 證明只用 voxel 也能達到 two-stage 的精度（84.52），同時維持 25.2 FPS。
   - 在速度表中，它是唯一同時達到「Mod. > 81」和「FPS > 25」的方法。
4. **2022：多階段精修。**
   - CasA 在 Voxel R-CNN 上加 cascade attention：val R11 Car Mod. 84.52 → 86.58，test R40 81.62 → 83.06（CasA Table III / IV）。
   - 進步集中在**遠處物體**和**行人**。
   - 代價是 86 ms（3 個階段）。回到「以速度換精度」的方向。
5. **2025：改輸入端。**
   - NV3D 不改第二階段，而是加入法向量特徵，並用取樣丟掉多餘的 voxel。
   - 精度沒有超越 Voxel R-CNN（NV3D Table 7：Car Mod. 84.78 vs 85.29）。
   - 但證明丟掉約一半資料只掉約 1 個百分點。論文沒有報告速度。
6. **2023：連 head 都 sparse。**
   - VoxelNeXt 不轉 dense、不用 anchor、不用 NMS。
   - 沒有 KITTI 數字，改看 [Waymo 同表比較](waymo-same-table.md)：整體 L2 mAPH 70.1，高於 PV-RCNN 的 63.3。
   - 速度優勢在**長距離**最明顯：200 m 時 66 ms，CenterPoint 為 246 ms（VoxelNeXt Fig. 3）。
   - ⚠️ FLOPs 少約 80%，實際延遲只少約 31%（66 vs 96 ms，VoxelNeXt §5）→ **FLOPs 不等於速度**。
7. **2024：換掉 backbone 本身。**
   - LION 用 linear RNN（Mamba 等）讓數千個 voxel 在同一群組內互動。
   - Waymo L2 mAPH：LION-Mamba 73.2、-L 74.0，DSVT 72.1（LION Table 1，見 [Waymo 同表比較](waymo-same-table.md)）。
   - FLOPs 比 DSVT 少約 42%，但**沒有實際延遲**，作者承認速度仍需改進（LION §5）。
   - KITTI 只在附錄，Car Mod. 約 78（R11），因為搭配的是 one-stage head。

## 總結：兩條主軸（整理）

| 時期 | 精度路線（KITTI 為主） | 效率與新架構路線（Waymo、nuScenes 為主） |
|---|---|---|
| 2018–19 | SECOND、PointPillars：先求快 | — |
| 2020–21 | PV-RCNN → Voxel R-CNN：two-stage 精修，兼顧速度 | — |
| 2022 | CasA：多階段精修 | — |
| 2023 | — | VoxelNeXt：全 sparse，長距離友善 |
| 2024 | — | LION：linear RNN backbone，大群組長距離關係 |
| 2025 | NV3D：改輸入端（法向量、取樣） | — |

- 兩條路線使用**不同的資料集**，數字無法直接比較。這也是為什麼本 wiki 需要分別建立 KITTI 和 Waymo 的同表比較。
