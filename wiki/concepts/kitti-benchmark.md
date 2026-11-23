# KITTI 3D Object Detection Benchmark

## 白話解釋（給初學者）

**KITTI** 是在德國街道收集的自動駕駛資料集，有 LiDAR 點雲、相機影像，以及人工標註的 3D 框。
它是 LiDAR 3D 偵測最常用的「考卷」：大家在同一份資料上比分數。

- **類別**：Car、Pedestrian、Cyclist。
- **難度**：Easy / Moderate / Hard，依物體在影像中的**高度**、**遮擋程度**、**截斷程度**分級（SECOND §4）。
- **最常被引用的數字是 Car Moderate 的 3D AP**。官方排行榜以 Moderate 排名（PointPillars §5）；本 wiki 的 8 篇中，有 KITTI 結果的 7 篇都以 Car Moderate 為主要指標（VoxelNeXt 沒有 KITTI 結果）。

## 資料切分

- 官方訓練集 7481 個樣本，常見切法：**train 3712 / val 3769**（SECOND §4，沿用 MV3D 的切法）。
- **test 集**的標註不公開，必須上傳到官方伺服器評測，次數有限制。

**本 wiki 的規則**：主要數字以 **val** 為主，test 並列參考。因為多數論文用 val 做消融比較，數字比較齊全。
注意：val 和 test 的分數**不能直接互相比較**，例如 SECOND Car Moderate 在 val 是 76.48，在 test 是 73.66（SECOND Table 4 / Table 2）。

## 評估指標

- **AP（Average Precision）**：綜合 precision 和 recall 的分數，0–100%，越高越好。
- **3D AP**：用 3D 框的 IoU 判斷對錯。
- **BEV AP**：只看鳥瞰圖上的 2D 旋轉框，忽略高度，通常比 3D AP 高。
  - 例如 SECOND val Car Moderate：BEV 87.07 vs 3D 76.48（SECOND Table 5 / Table 4）。

- **AOS（Average Orientation Similarity）**：評估**朝向**是否正確。做法是把 3D 框投影到影像上做 2D 配對，再比較朝向。**BEV AP 和 3D AP 都不考慮車頭方向**，所以需要 AOS（PointPillars §5）。
- KITTI 官方排行榜以 **Moderate** 排名（PointPillars §5）。

## KITTI 的資料特性

- 官方 test 集有 7518 個樣本（PointPillars §4.1）。
- 只有前鏡頭看得到的物體有標註，所以慣例上**只使用投影到影像內的點**，約佔全部點雲的 **10%**（PointPillars §4.1、§6）。
  - 影響：論文報告的速度是在「只有 10% 點雲」的條件下測的，實際自駕車要處理全部 360° 點雲，會慢很多。
- 慣例上 Car 一個網路、Pedestrian + Cyclist 另一個網路（PointPillars §4.1）。

### IoU 門檻（PV-RCNN §4.2）
- 判定「偵測正確」的旋轉 3D IoU 門檻：**Car 0.7**、**Pedestrian 0.5**、**Cyclist 0.5**。
  - Car 和 Cyclist 出自 PV-RCNN §4.2；Pedestrian 出自 CasA §IV-A1（PV-RCNN 沒有報告 Pedestrian）。

### R11 vs R40（AP 的兩種計算方式）
- AP 是 precision-recall 曲線下的面積，實際計算時只在固定的 recall 位置取樣：
  - **R11**：11 個 recall 位置
  - **R40**：40 個 recall 位置
- KITTI 官方 test 伺服器使用 **R40**；早期論文和 val 比較常用 **R11**（PV-RCNN §4.2）。
- **改版日期：2019-10-08**，從 R11 改為 R40（Voxel R-CNN §4.3 註腳）。所以 2019 年 10 月以前的論文，test 數字都是 R11。
- **同一個模型，R11 和 R40 的分數不同**，不能混比。例：PV-RCNN val Car Moderate，R11 為 83.90、R40 為 84.83（PV-RCNN Table 2 / 3）。
- 本 wiki 的規則：每個 KITTI 數字都標註 R11 或 R40。原文沒寫的，標「推定」並說明理由。

## 跨論文比較數字的注意事項

同一個方法，在不同論文裡的分數可能不同。比較時要確認以下幾點：

1. **val 還是 test？** 例：SECOND Car Moderate 3D AP 在 val 是 76.48，在 test 是 73.66（SECOND Table 4 / Table 2）。
2. **R11 還是 R40？** 例：SECOND 的 test Car Moderate 3D AP，在 SECOND 原論文是 **73.66**，在 PV-RCNN Table 1（R40）是 **72.55**；PointPillars 也從 74.99 變成 74.31（PointPillars Table 2 vs PV-RCNN Table 1）。
   - 原因：KITTI 官方後來把 test 的 AP 計算從 R11 改成 R40，PV-RCNN 列的是改版後排行榜上的數字。
   - SECOND（2018）和 PointPillars（2018-12 上 arXiv）都早於 2019-10-08 改版，所以原論文中的 test 數字是 R11（改版日期出自 Voxel R-CNN §4.3 註腳）。
3. **誰跑的？** PointPillars 在自己的程式碼裡重新實作其他方法的 encoder，結果比原論文報告的**高 1–10 mAP**（PointPillars §7.4）。作者認為原因包括：
   - 資料增強的超參數更好
   - 加了 GT-sampling（約 +3 mAP）
   - 網路設計、anchor、loss、optimizer 等多個超參數的差異
   - 第二個例子（val R11, Car Mod.），原論文 vs Voxel R-CNN Table 5 重新列出的數字：
     - SECOND：76.48 → 78.62
     - PointPillars：77.98 → 76.06
     - PV-RCNN：83.90 → 83.69
     - Voxel R-CNN 沒有說明原因，推測是用 OpenPCDet 重新訓練。（整理）
4. **速度在什麼硬體上量的？**
   - 例：Voxel R-CNN Table 3 中 PointPillars 是 42.4 FPS，剛好是 PointPillars 論文的 **PyTorch 版**速度；原論文標題的 62 Hz 是 **TensorRT 版**。
   - 同一張表中 SECOND 是 30.4 FPS，SECOND 原論文是 20 FPS。表中各方法的 FPS 來源不一，Voxel R-CNN 原文沒有說明。 GPU 型號不同（1080 vs 1080 Ti）、有沒有用 TensorRT，都會影響數字。例：PointPillars 用 TensorRT 比 PyTorch 快 45.5%（§6）。
5. **點雲範圍？** KITTI 只用前視角約 10% 的點（PointPillars §6）。
6. **論文本身也可能寫錯。** CasA 的 §I 和 §IV-C1 把三個 baseline 的進步幅度寫成不同順序，要對照 Table III 才知道 §I 是對的（見 [CasA](../papers/casa.md#資料品質備註本次-ingest-發現)）。同一篇論文中 Voxel R-CNN 的 baseline 也有兩個數字：85.27（Table I / VIII）和 85.29（Table III）。
7. **README / model zoo 不等於論文。** CasA README 的 CasA-V 是 86.54，論文 Table III 是 86.58；CT3D baseline 是 84.97 vs 86.06。開源模型的數字可能是重新訓練的結果。
8. **「mAP」的定義不一樣。**
   - KITTI 慣例：分別報 Easy / Moderate / Hard 的 AP，以 **Moderate** 為主。
   - PointPillars 的「mAP」：Car、Ped、Cyc 三個**類別**的 Moderate 平均（PointPillars Table 1 / 2）。
   - NV3D 的「mAP」：同一類別 Easy / Mod. / Hard 三個**難度**的平均（NV3D Table 1）。例如 Car「86.60% mAP」，實際 Moderate 只有 84.78。
   - → 看到「mAP」一定要確認是**哪些東西的平均**。
9. **論文自己的 baseline 可能前後不一。** NV3D 的 Voxel R-CNN baseline 在 Table 1 為 83.83，在 Table 4 / 7 為 85.29（Car Mod., R40）。和不同 baseline 比，「提升幅度」差很多。
10. **表格標示 val，內容卻可能是 test 數字。**
    - LION 附錄 Table 8 標題寫「KITTI validation set、R11」。
    - 但表中 SECOND 83.1 / 73.7 / 66.2、PointPillars 79.1 / 75.0 / 68.3 和各自原論文的 **test R11** 數字相同（SECOND Table 2、PointPillars Table 2）。
    - NV3D Table 4 / 7 也有類似情況：SECOND 標示為 R40，數字卻和 Voxel R-CNN Table 5 的 R11 相同。
    - → **把數字和原論文對照**，是發現這類錯誤的唯一方法。

**結論**：最可靠的比較是**同一篇論文、同一張表、同一個設定**下的數字。

**本 wiki 的規則（使用者決定，2026-11-23）**：comparisons 頁的主表**以同一張來源表格為準**，原論文的數字放在備註欄。

## 其他資料集

- **Waymo Open Dataset**：規模大很多、360° 標註，指標也不同（LEVEL 1/2、mAPH）。見 [Waymo Open Dataset](waymo-open-dataset.md)。
- **nuScenes、Argoverse2、ONCE**：見 [nuScenes 與 Argoverse2](nuscenes-and-argoverse2.md)。

## 出現在哪些論文

全部。

## 常見誤解

- 「論文 A 的 val 分數比論文 B 的 test 分數高，所以 A 比較好」→ val 和 test 不能混比，R11 和 R40 也不能混比。
