# PV-RCNN vs Voxel R-CNN：需要原始點嗎？

> 兩篇論文有共同作者（Shaoshuai Shi），卻提出相反的主張，很適合用來說明「研究是怎麼推進的」。

## 一句話對比

| | [PV-RCNN](../papers/pv-rcnn.md)（CVPR 2020） | [Voxel R-CNN](../papers/voxel-rcnn.md)（AAAI 2021） |
|---|---|---|
| 主張 | voxel 會損失精確位置 → **要用 point 補回來** | 精確位置**不是必要的** → **voxel 就夠** |
| RoI 特徵從哪取 | voxel → **keypoint**（VSA）→ RoI 格點 | **直接從 3D voxel** → RoI 格點 |
| 找鄰居 | ball query（掃描所有點，O(N)） | voxel query（索引加減，O(K)） |
| 額外輸入 | 原始點、BEV 圖、多層 voxel | 3D backbone 最後兩個 stage 的 voxel |

## 共同點

- 第一階段都是 [SECOND](../papers/second.md) 式的 sparse 3D CNN + anchor RPN。
- RoI 都切成 **6×6×6** 個格點，用 PointNet 式的「收集鄰居 → MLP → max pooling」。
- 信心分數都用 **IoU-guided**。
- KITTI voxel 大小都是 (0.05, 0.05, 0.1) m（PV-RCNN §4.1、Voxel R-CNN §4.2）。

→ 差異其實集中在**一個模組**：第二階段的特徵從哪裡、用什麼方式收集。

## 數字對比（同一張表）

| 指標 | PV-RCNN | Voxel R-CNN | 出處 |
|---|---|---|---|
| KITTI val R11 Car Mod. | 83.69 | 84.52 | Voxel R-CNN Table 5 |
| KITTI test R40 Car Mod. | 81.43 | 81.62 | Voxel R-CNN Table 3 |
| FPS | 8.9 | 25.2 | Voxel R-CNN Table 3 |
| Waymo L1 3D mAP | 70.30 | 75.59 | Voxel R-CNN Table 6 |
| Waymo L1 50 m+ | 42.17 | 53.15 | Voxel R-CNN Table 6 |

（PV-RCNN 原論文的 val R11 為 83.90，見 PV-RCNN Table 2）

## Voxel R-CNN 怎麼找到問題（研究方法的示範）

1. **假設 1**：SECOND 輸給 PV-RCNN，是因為少了精修？
   - 實驗：在 SECOND 的 BEV 上加精修頭 → 只 +0.6（Voxel R-CNN Table 1）。
   - 結論：精修有用，但只在 BEV 上精修不夠，**需要 3D 結構**。
2. **假設 2**：PV-RCNN 慢在哪？
   - 實驗：逐模組計時 → VSA 佔 49.4 ms，約一半（Voxel R-CNN Table 2）。
   - 結論：**point-voxel 互動是速度瓶頸**。
3. **解法**：保留 3D 結構，去掉 point → 直接從 3D voxel 取特徵。
4. **驗證**：消融實驗（Voxel R-CNN Table 7）。精修頭帶來 +6.2 AP，voxel query 和加速 PointNet 把 FPS 從 17.4 拉回 25.2。

## 教學重點（整理）

- 「更精確的輸入」不一定帶來更好的結果。關鍵在於**模型架構有沒有用到 3D 結構**（第二階段在 3D 特徵上精修）。
- 好的研究常從**診斷實驗**開始：先證明瓶頸在哪，再對症下藥。
- 速度優化（voxel query、拆解 FC 層）來自**資料結構的特性**（voxel 是規則格子），不是靠更大的模型。
