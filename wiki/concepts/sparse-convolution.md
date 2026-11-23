# Sparse Convolution（稀疏卷積）

## 白話解釋（給初學者）

想像一棟有 1000 個房間的大樓，裡面只有 5 個房間有人。
- **一般（dense）卷積**：保全每晚把 1000 個房間都巡一遍，大部分時間都在看空房間。
- **Sparse 卷積**：保全手上有一份「有人的房間清單」，只去那 5 間和它們的鄰居。

LiDAR 點雲切成 [voxel](voxelization.md) 後正是這樣：KITTI 一個場景只有約 5k–8k 個非空 voxel，稀疏度約 **0.005**（[SECOND](../papers/second.md) §3.1.3）。
所以「只在有資料的地方算」可以省下大量計算，結果和 dense 卷積在非空位置上是一樣的。

## 兩種 sparse 卷積

| 種類 | 規則 | 直覺 | 用途 |
|---|---|---|---|
| **一般 Sparse Conv** | 只要卷積核範圍內有任何輸入點，輸出位置就變成「有資料」 | 資料會往外「擴散」一圈 | downsample，擴大感受野 |
| **Submanifold Sparse Conv** | 只有輸入有資料的位置才會有輸出 | 有資料的位置完全不變，不擴散 | 提取特徵，保持稀疏 |

為什麼需要 submanifold：如果一直用一般 sparse conv，有資料的位置會每層往外擴，幾層後就不稀疏了，速度優勢消失（SECOND §3.1.3）。

典型做法（SECOND 的中間層）：**多層 submanifold conv 提特徵 → 一層一般 sparse conv 降採樣**，重複數次。

## 技術細節（給想深入的人）

- 實作分成兩步：
  1. **建 rule**：找出「哪個輸入位置，透過卷積核的哪個偏移，貢獻到哪個輸出位置」的對應表。
  2. 依 rule 把輸入特徵 **gather** 起來做矩陣乘法（GEMM），再 **scatter** 回輸出位置。
- SECOND 的貢獻：把 rule 的建立從 CPU hash table 改成 **GPU 平行演算法**，避免 CPU-GPU 資料搬移（§3.1.3, Algorithm 1）。
- 速度（單層 sparse conv，64×64 channels，GTX 1080 Ti）：SECOND 8.6、SpConvNet 21.2、Dense 567（SECOND Table 1，原文未寫單位）。
- 整體效果：和 dense 網路相比，訓練快約 4 倍、推論快約 3 倍（SECOND §1）。

## 出現在哪些論文

- [SECOND](../papers/second.md)：首次用於 LiDAR 偵測。
- 之後以 SECOND 式 sparse 3D backbone 為基礎的方法：[PV-RCNN](../papers/pv-rcnn.md)、[Voxel R-CNN](../papers/voxel-rcnn.md)、[CasA](../papers/casa.md)、[NV3D](../papers/nv3d.md)。
  - PV-RCNN：3×3×3 sparse conv 下採樣到 1×、2×、4×、8×（PV-RCNN §3.1）。
  - Voxel R-CNN：沿用 SECOND / PV-RCNN 的 3D backbone，4 個 stage（Voxel R-CNN §4.2）。
  - CasA：同樣的 3×3×3 sparse conv backbone（CasA §III-B）。
  - NV3D：沿用 Voxel R-CNN 的 backbone（NV3D §4.2）。
  - LION：3D SFD 使用 submanifold sparse conv 補局部資訊（LION §3.2）。
- [VoxelNeXt](../papers/voxelnext.md)：**全程維持 sparse**。
  - 前面的方法 backbone 用 sparse conv，最後仍轉成 dense BEV 給 head 使用；VoxelNeXt 連 head 也是 sparse。
  - 搭配**額外下採樣**（stride 16、32）擴大感受野。
  - **Voxel pruning**：只讓特徵強的一半 voxel 在下採樣時擴張，FLOPs 從 83.8G 降到 33.6G，mAP 只從 56.5 掉到 56.2（VoxelNeXt Table 3）。
  - 這也回應了上面「一般 sparse conv 會讓資料往外擴散」的問題。

## 常見誤解

- 「Sparse conv 是一種近似，會犧牲準確度」→ 一般 sparse conv 在非空位置上的計算結果和 dense 相同，只是不算空的地方。Submanifold conv 則是**刻意設計**成不擴散，屬於架構選擇，不是近似誤差。
- 「Sparse conv 一定比較快」→ 只有資料夠稀疏時才划算。（整理）
