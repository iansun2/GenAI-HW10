# nuScenes 與 Argoverse2

> 使用者決定（方案 A）：兩個資料集合併成一頁，因為只有 VoxelNeXt 和 LION 用到，簡報也只會帶過。
> 資料限制：本 wiki 的 raw 資料**沒有**這兩個資料集的官方論文，以下內容都來自 VoxelNeXt（和之後的 LION）的描述。NDS 的計算公式不在 raw 資料中，所以本頁不寫公式。

## 白話解釋（給初學者）

除了 [KITTI](kitti-benchmark.md)（小考）和 [Waymo](waymo-open-dataset.md)（期末考），還有兩個常見的大型資料集：
- **nuScenes**：**類別最多**，有 10 類，而且除了「框得準不準」，還要評「速度、朝向、屬性」等。
- **Argoverse2**：**偵測範圍最遠**，可達 200 m，類別也很多，特別考驗遠距離偵測和效率。

## nuScenes

### 規格（LION §4.1）
- 1000 個場景：train 750 / val 150 / test 150。
- 感知範圍最遠 **50 m**；標註頻率 2 Hz。

### 類別（10 類，依 VoxelNeXt Table 2 / 12 的欄位）
Car、Truck、Bus、Trailer、Construction Vehicle（C.V.）、Pedestrian、Motorcycle、Bicycle、Traffic Cone（T.C.）、Barrier

### 指標
- **mAP**：10 個類別的平均精度。（整理：nuScenes 的配對方式和 KITTI 用 3D IoU 不同，但 raw 資料中沒有細節，待補）
- **NDS（nuScenes Detection Score）**：綜合分數，除了 mAP，還考慮以下 5 種誤差（VoxelNeXt Table 8）：

| 縮寫 | 意義 |
|---|---|
| ATE | 位置誤差 |
| ASE | 大小誤差 |
| AOE | 朝向誤差 |
| AVE | 速度誤差 |
| AAE | 屬性誤差 |

- 因為要評**速度**，nuScenes 上的方法通常也會回歸速度（VoxelNeXt §3.2）。
- 追蹤指標：AMOTA、AMOTP、MOTA、IDS（VoxelNeXt Table 11 / 13 / 14）。

### 代表數字（test，VoxelNeXt Table 12，同一張表）

| 方法 | mAP | NDS | 延遲 |
|---|---|---|---|
| PointPillars | 30.5 | 45.3 | 31 ms |
| CenterPoint | 58.0 | 65.5 | 96 ms |
| VoxelNeXt | 64.5 | 70.0 | 66 ms |

### 注意
- **測試增強（†，double-flip）**：有些方法的 test 結果有用增強，不能和沒用的直接比（VoxelNeXt Table 12）。
- **訓練資料量**：消融實驗常只用 1/4 的訓練集（VoxelNeXt Table 8），數字會比完整訓練低。

## Argoverse2

- **偵測範圍可達 200 m**（VoxelNeXt Fig. 3；LION §4.1）。
- 1000 個序列：train 700 / val 150 / test 150；標註頻率 10 Hz；mAP 的計算方式和 nuScenes 類似（LION §4.1）。
- LION Table 3 列出 26 個類別。
- 類別很多：VoxelNeXt Table 16 列出 20 多個類別，包含 Stop sign、Bollard、Construction barrel、Wheelchair 等少見的類別。
- 指標：mAP。
- 代表數字（VoxelNeXt Table 16）：CenterPoint 22.0、FSD 28.2、VoxelNeXt 30.0、VoxelNeXt K3 30.7。
  - 數字比 nuScenes 低很多，因為類別多、距離遠、很多小物體。（整理）

### 為什麼 Argoverse2 適合測試「效率」
- 偵測範圍越大，dense BEV 圖的面積越大（距離加倍，面積變 4 倍）。
- VoxelNeXt Fig. 3（RTX 2080 Ti）：範圍從 50 m 擴大到 200 m 時，
  - CenterPoint：82 → 246 ms
  - VoxelNeXt：61 → 66 ms
- 見 [Anchor-free 與 Sparse Head](anchor-free-and-sparse-head.md)。

## 附：ONCE

- 40 線 LiDAR，點比 KITTI、Waymo（64 線）稀疏（CasA §IV-G）。
- train 5000 / val 3000 / test 8000 幀；5 類（Car、Bus、Truck 合併為 Vehicle，另有 Pedestrian、Cyclist）；mAP 有特別考慮朝向（LION §4.1）。
- 用到的論文：[CasA](../papers/casa.md)（Table IX）、[LION](../papers/lion.md)（Table 4）。

## 和 KITTI、Waymo 的比較（整理）

| | KITTI | Waymo | nuScenes | Argoverse2 |
|---|---|---|---|---|
| 視角 | 前方約 90° | 360° | 360°（整理） | 360°（整理） |
| 主要指標 | 3D AP（R11 / R40） | mAP / mAPH（L1 / L2） | mAP / NDS | mAP |
| 感知範圍 | x 0–70.4 m（常用設定） | 150 m × 150 m | 50 m | 200 m |
| 類別數 | 3 | 3 | 10 | 26 |
| 特色 | 經典、小 | 大、有朝向指標 | 類別多、評速度 | 超遠距離 |
| 本 wiki 使用的論文 | 前 6 篇 | PV-RCNN、Voxel R-CNN、CasA、VoxelNeXt | VoxelNeXt、LION | VoxelNeXt、LION |

- KITTI 的 90° 和 Waymo 的 360° 出自 PV-RCNN §4.1。
- 感知範圍：KITTI 出自 SECOND §3.1.1；其餘出自 LION §4.1。
- nuScenes 和 Argoverse2 的視角 raw 資料中沒有明寫，標為整理。

## 出現在哪些論文

[VoxelNeXt](../papers/voxelnext.md)、[LION](../papers/lion.md)
