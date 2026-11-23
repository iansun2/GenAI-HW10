# Transformer 與 Linear RNN Backbone（長距離關係）

## 白話解釋（給初學者）

Backbone 的工作是讓每個 voxel「了解周圍的情況」。差別在於**能看多遠**、**要花多少計算**：

| 方式 | 比喻 | 能看多遠 | 計算量 |
|---|---|---|---|
| **Sparse Conv**（[SECOND](../papers/second.md) 等） | 只和**隔壁鄰居**講話，一層一層傳下去 | 受限於卷積核大小和層數 | 低 |
| **Transformer**（SST、DSVT） | **小組會議**：組內每個人都和其他人講話 | 組內全部 | 人數的**平方** |
| **Linear RNN**（[LION](../papers/lion.md)） | **傳紙條**：每人讀完前面的摘要，加上自己的資訊再往下傳 | 整條隊伍 | 人數的**線性** |

- Transformer 的問題：人數加倍，計算變 4 倍。所以 3D Transformer 只能分成**小組**（例如 256 個 voxel 一組）（LION §1、Table 5）。
- Linear RNN（Mamba、RWKV、RetNet）：人數加倍，計算只變 2 倍 → 一組可以放 **4096 個 voxel**（LION §4.2）。

## 為什麼長距離關係重要

- 大物體（卡車、公車）跨越很多 voxel，需要整體資訊才能框準。
  - VoxelNeXt 也發現，感受野不夠時大物體掉最多（VoxelNeXt Table 2：Bus 從 67.5 掉到 38.3）。
- LION 的消融實驗：只把群組從小（256）改大（4096…512），L2 mAPH 就 +1.1（LION Table 5）。

## Linear RNN 的弱點：一維序列會丟失空間資訊

- RNN 只能處理**一條線**上的序列，所以要先把 3D voxel 依 X 軸（或 Y 軸）排成一列。
- 問題（LION Fig. 4）：兩個在空間中**相鄰**的 voxel（例如上下相鄰），排成一列後可能相隔幾十個位置。
- 比喻：教室座位依「列」編號，前後座的同學在名單上相隔一整列的人數。
- LION 的解法：
  1. 交替用 **X 軸和 Y 軸**排序，讓兩個方向的鄰居都有機會靠近。
  2. 加一層 **submanifold sparse conv**（3D Spatial Feature Descriptor），直接補回局部的 3D 鄰近資訊。
     - 效果（LION Table 6）：L2 mAPH 67.6 → 69.3。改用 MLP（67.7）或再加一層 RNN（67.9）都幾乎沒用。

→ **長距離交給 RNN，局部交給卷積**，兩者互補。（整理）

## 計算量 vs 實際速度

| Backbone | FLOPs (G) | 實際延遲 |
|---|---|---|
| DSVT-Voxel（Transformer） | 100.8 | raw 資料未提供 |
| LION-Mamba（linear RNN） | 58.5 | **未報告** |

（LION 附錄 Table 12）

- LION 作者承認：linear RNN 的**平行運算效率不如 Transformer**，實際執行速度還需要改進（LION §5）。
- 同樣的現象：VoxelNeXt 的 FLOPs 只有 CenterPoint 的 1/5，延遲卻只少約 1/3（VoxelNeXt §5）。
- → **FLOPs 是理論計算量，實際速度還要看能不能在 GPU 上平行化**。

## 出現在哪些論文

- [LION](../papers/lion.md)：linear RNN backbone（Mamba、RWKV、RetNet、xLSTM、TTT）。
- Transformer 方法（SST、DSVT、SWFormer 等）只透過 LION 和 VoxelNeXt 的比較表得知，本 wiki 沒有 ingest 原論文。

## 常見誤解

- 「Mamba 一定比 Transformer 快」→ 理論上計算量較少，但 LION 作者自己說實際速度仍需改進（LION §5）。
- 「群組越大越好」→ 推論時把群組從 4096 改到 8192，L2 mAPH 反而從 73.24 降到 73.02（LION Table 11）。
