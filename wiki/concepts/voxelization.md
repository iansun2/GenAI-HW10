# Voxelization（體素化）

## 白話解釋（給初學者）

**Voxel（體素）**就是 3D 版的像素：把空間切成一個個同樣大小的小方塊。
**Voxelization** 就是把[點雲](point-cloud-and-lidar.md)裡的每個點，丟進它所在的那個小方塊。

做完之後，原本「無序的一堆點」就變成「規則的 3D 網格」，可以用卷積來處理。
大部分格子裡沒有點，是空的，這就是為什麼需要 [Sparse Convolution](sparse-convolution.md)。

## 技術細節

以 [SECOND](../papers/second.md) 的設定為例（§3.1.1）：

1. **裁切範圍**（Car）：z∈[−3, 1]、y∈[−40, 40]、x∈[0, 70.4] m。
2. **voxel 大小**：0.4 × 0.2 × 0.2 m（z × y × x）。
3. **每格點數上限 T**：Car T=35；行人、自行車 T=45。點太多的格子只取一部分。
4. 用 hash table 記錄哪些格子已存在；非空 voxel 數達到上限就停止。
5. **VFE（Voxel Feature Encoding）**：對格子內的點各自做 Linear-BN-ReLU，再用 max pooling 匯總成一個 voxel 特徵向量（源自 VoxelNet）。

產生的資料（SECOND 大模型）：sparse tensor 大小 128 × 10 × 400 × 352（C × Z × Y × X）（§3.2.4）。

### 取捨：voxel 大小

- 小格子：保留更多細節，但格子數變多、計算量變大。
- 大格子：快，但多個點被合併，細節流失。
- 這個量化損失是兩篇論文爭論的核心：
  - [PV-RCNN](../papers/pv-rcnn.md)：用原始點特徵「部分彌補 voxel 化的量化損失」（PV-RCNN §3.2，Extended VSA）。
  - [Voxel R-CNN](../papers/voxel-rcnn.md)：「原始點的精確位置不是必要的，粗糙的 voxel 粒度也能提供足夠的資訊」（Voxel R-CNN 摘要）。
  - 見 [PV-RCNN vs Voxel R-CNN](../comparisons/pv-rcnn-vs-voxel-rcnn.md)。

## 相關變體：Pillar（柱體）

- **Pillar**：z 方向不切，每根柱子從地面延伸到頂。見 [PointPillars](../papers/pointpillars.md)。
- 白話比喻：voxel 像把空間切成一顆顆骰子；pillar 像把地面切成一塊塊磁磚，每塊磁磚上方整根柱子算一格。
- 預設格子 0.16 m × 0.16 m；KITTI 範圍內只有 6k–9k 個非空 pillar，約 97% 是空的（PointPillars §2.1）。
- 每根 pillar 用簡化版 PointNet 壓成一個特徵向量，再放回 2D 畫布成為**偽影像（pseudo-image）**，之後只用 2D 卷積。

| | Voxel（SECOND） | Pillar（PointPillars） |
|---|---|---|
| 切法 | x、y、z 都切 | 只切 x、y |
| 中間層 | Sparse 3D conv | 無，直接 2D |
| 速度 | 20 Hz（SECOND test, PointPillars Table 2） | 62 Hz（同上） |
| 高度資訊 | 由 3D conv 逐步壓縮 | 一開始就在柱內 max pooling 壓掉 |

### 格子大小的取捨（PointPillars §7.1）
- 格子越大，非空格子越少，encoder 和 backbone 都更快；0.28² m² 時可達 105 Hz。
- 但精度下降，主要是**小物體**（行人、自行車）掉最多，Car 很穩定。
- 直覺：格子大到和行人差不多時，一個行人只佔一兩格，細節就沒了。（整理）

### 不同稀疏度數字的口徑
- SECOND：「稀疏度約 0.005」→ 指 3D voxel 中**非空**的比例。
- PointPillars：「約 97% sparsity」→ 指 2D pillar 中**空**的比例。
- 兩者的格子定義和計算方式不同，不能直接比較。（整理）

## Voxel 化之後的「減量」

voxel 化之後，還可以進一步減少 voxel 數量：
- **輸入端取樣**（[NV3D](../papers/nv3d.md)）：送進網路前，依法向量密度和距離丟掉多餘的 voxel。見 [輸入取樣](input-sampling.md)。
- **網路中剪枝**（[VoxelNeXt](../papers/voxelnext.md)）：在 backbone 下採樣時，只讓特徵強的 voxel 擴張（voxel pruning）。見 [Sparse Convolution](sparse-convolution.md)。

## 出現在哪些論文

[SECOND](../papers/second.md)、[PointPillars](../papers/pointpillars.md)（pillar 版）、[Voxel R-CNN](../papers/voxel-rcnn.md)、[CasA](../papers/casa.md)、[PV-RCNN](../papers/pv-rcnn.md)、[VoxelNeXt](../papers/voxelnext.md)、[LION](../papers/lion.md)、[NV3D](../papers/nv3d.md)

## 常見誤解

- 「voxel 會保留所有的點」→ 不一定。超過上限 T 的點會被丟掉，格子內的位置細節也被壓縮成一個特徵向量。
