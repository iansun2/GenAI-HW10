# One-stage vs Two-stage 偵測器

## 白話解釋（給初學者）

- **One-stage（一階段）**：網路看一次場景，直接輸出所有框。像考試時一看題目就寫答案。
- **Two-stage（兩階段）**：
  - 第一階段先粗略圈出「可能有東西的地方」，稱為 **proposal** 或 **RoI（Region of Interest）**。
  - 第二階段針對每個候選區域「放大仔細看」，再修正框的位置、大小和信心分數。
  - 像考試時先寫草稿，再逐題檢查修改。

一般來說，two-stage 比較準但比較慢，one-stage 比較快。

## 技術細節

| | One-stage | Two-stage |
|---|---|---|
| 流程 | backbone → 每個位置直接分類 + 回歸 | backbone → RPN 產生 proposal → **RoI 特徵提取** → refinement head |
| 代表（LiDAR） | [SECOND](../papers/second.md)、[PointPillars](../papers/pointpillars.md) | [PV-RCNN](../papers/pv-rcnn.md)、[Voxel R-CNN](../papers/voxel-rcnn.md)、[CasA](../papers/casa.md) |
| 關鍵難題 | 前景/背景不平衡 → focal loss | 怎麼從 3D 特徵中為每個框取出好特徵 → [RoI Pooling](roi-pooling.md) |

### 起源（2D 影像偵測）
- PointPillars 的文獻回顧（§1.1.1）提到：
  - R-CNN 系列確立了 two-stage 架構：RPN 提出候選，第二階段再分類。
  - RetinaNet 的 focal loss 讓 one-stage 在準確度和速度上都能和 two-stage 競爭，所以 PointPillars 選擇 one-stage。

### 第二階段實際帶來多少？
- PV-RCNN 的消融實驗（KITTI val R40, Car Mod., Table 7）：
  - 只有第一階段 RPN：80.87
  - 加上第二階段：84.83
  - → 約 **+4 AP**
- Voxel R-CNN 的消融實驗（KITTI val R11, Car Mod., Table 7）：
  - one-stage：77.99 @ 40.8 FPS
  - 加上精修頭：84.21 @ 17.4 FPS
  - → **+6.2 AP，但速度少了一半以上**
  - 這就是 two-stage 的典型取捨：精度變高，速度變慢。Voxel R-CNN 再用 voxel query 和加速 PointNet 把速度拉回 25.2 FPS。

### 第二階段在哪裡做精修很重要
- 只在 2D BEV 特徵上精修：SECOND 78.62 → 79.26，只 +0.6（Voxel R-CNN Table 1）。
- 在 3D 特徵上精修：+6.2（Voxel R-CNN Table 7）。
- → 第二階段要能看到 **3D 結構**，效果才明顯。

### Two-stage 的延伸：Cascade（多階段）
- 第二階段可以重複好幾次，每次在前一次修正過的框上再修正一次。
- 但在 3D 中直接套用 2D 的 cascade 反而變差：Voxel R-CNN 85.27 → 84.82（CasA Table I，val R40）。
- [CasA](../papers/casa.md) 用 cascade attention 解決這個問題，達到 86.37，代價是執行時間從 64 ms（1 階段）增加到 86 ms（3 階段）（CasA Table VI）。
- 詳見 [Cascade Refinement](cascade-refinement.md)。

## 出現在哪些論文

- One-stage：[SECOND](../papers/second.md)、[PointPillars](../papers/pointpillars.md)
- Two-stage：[PV-RCNN](../papers/pv-rcnn.md)、[Voxel R-CNN](../papers/voxel-rcnn.md)
- Multi-stage：[CasA](../papers/casa.md)
- Two-stage（沿用 Voxel R-CNN 的 head）：[NV3D](../papers/nv3d.md)（NV3D §3）
- One-stage、無 NMS：[VoxelNeXt](../papers/voxelnext.md)（VoxelNeXt Fig. 2）
- One-stage（center-based head，LION Table 1 未標 ‡ two-stage）：[LION](../papers/lion.md)

## 常見誤解

- 「two-stage 的第一階段沒用」→ 第一階段的 proposal 品質（recall）決定了上限：第二階段只能修正已經被圈到的物體。PV-RCNN 特別報告了 RPN 的 recall（Table 4）。
- 「two-stage 一定比 one-stage 準」→ 2D 偵測中 focal loss 已讓 one-stage 追上（PointPillars §1.1.1）；在 LiDAR 偵測上，KITTI 排行榜前段多為 two-stage（整理，依 PV-RCNN Table 1）。
