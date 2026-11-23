# RoI Pooling（3D 區域特徵提取）

## 白話解釋（給初學者）

[Two-stage](one-stage-vs-two-stage.md) 偵測器的第二階段要「放大看每個候選框」。
**RoI Pooling** 就是：**給定一個 3D 框，從網路的特徵中，把屬於這個框的資訊撈出來，整理成固定大小的向量**，交給後面的小網路修正框。

比喻：第一階段在地圖上圈出「這附近好像有車」，RoI Pooling 就是派人去那個圈裡，按照固定的格子位置逐格記錄看到什麼，回來交一份固定格式的報告。

不管框大或小、裡面點多或少，輸出都要是**固定大小**，因為後面接的是 MLP。

## 為什麼 3D 的 RoI Pooling 很難

- 3D 特徵圖經過下採樣後**解析度低**（例如 8 倍）。
- 特徵圖也**很稀疏**。2D 常用的 RoIAlign 只用最近的 4 個（雙線性）或 8 個（三線性）鄰居插值，在稀疏的 3D 特徵上，**大部分取到的是 0**（PV-RCNN §3.1）。
- 如果改成讓每個格點向所有 voxel 搜尋鄰居，記憶體需求又太大（PV-RCNN §3.1 的例子：2,700 個格點 × 18,000 個 voxel）。

## 各論文的做法

### RoI-grid Pooling（[PV-RCNN](../papers/pv-rcnn.md)）
1. 每個框內均勻放 **6×6×6 = 216 個格點**。
2. 每個格點用 **set abstraction**（找半徑內的鄰居 → MLP → max pooling），向附近的 **keypoint**（不是直接向 voxel）收集特徵。
3. 使用多個半徑（0.8 m、1.6 m），**可以超出框外**，所以能看到周圍環境。
4. 216 個格點的特徵攤平 → MLP → 這個框的表示。

- 為什麼要透過 keypoint？2048 個 keypoint 遠少於幾萬個 voxel，搜尋鄰居比較省記憶體。
- 效果（KITTI val R40, Car Mod., PV-RCNN Table 9）：改用 RoI-aware pooling 為 82.97，RoI-grid pooling 為 84.83。

### Voxel RoI Pooling（[Voxel R-CNN](../papers/voxel-rcnn.md)）
1. 每個框同樣切成 **6×6×6** 個子格，以子格中心為格點。
2. 每個格點用 **voxel query** 直接找周圍的非空 voxel：
   - 以曼哈頓距離為門檻（2 和 4）。
   - 用索引加減就能找到鄰居，複雜度 O(K)，不必像 ball query 掃描全部 O(N)。
3. 用 PointNet 式匯總（相對座標 + voxel 特徵 → MLP → max pooling），再用 **accelerated PointNet** 把 FC 層拆成特徵和座標兩部分以加速。
4. 從 3D backbone 最後兩個 stage 取特徵，多尺度串接。

- 為什麼不能直接 max pooling 每個子格？3D 特徵中非空 voxel 不到 3%，大部分子格是空的（Voxel R-CNN §3.1）。
- 效果（Voxel R-CNN Table 7, val R11）：精修頭 +6.2 AP；voxel query + 加速 PointNet 把 FPS 從 17.4 拉到 25.2。

### 對照：RoI-grid vs Voxel RoI

| | RoI-grid Pooling（PV-RCNN） | Voxel RoI Pooling（Voxel R-CNN） |
|---|---|---|
| 格點 | 6×6×6 | 6×6×6 |
| 收集對象 | keypoint（2,048 個，由 VSA 從 voxel、點、BEV 濃縮而來） | 直接收集 3D voxel |
| 找鄰居 | ball query（半徑） | voxel query（曼哈頓距離，索引運算） |
| 速度（整體） | 8.9 FPS | 25.2 FPS |
| 出處 | PV-RCNN §3.3 | Voxel R-CNN §3.1；FPS：Voxel R-CNN Table 3 |

詳見 [PV-RCNN vs Voxel R-CNN](../comparisons/pv-rcnn-vs-voxel-rcnn.md)。

### Cascade 中的 RoI 特徵（[CasA](../papers/casa.md)）
- CasA 本身**不換** RoI pooling：沿用 base detector 的方法（例如 CasA+V 用 Voxel RoI Pooling）。
- 不同的是：
  - **每個階段**都用前一階段修正過的框重新做一次 RoI pooling。
  - 再用 **cascade attention** 把本階段和前面所有階段的 RoI 特徵匯總起來（CasA §III-A2）。
- 詳見 [Cascade Refinement](cascade-refinement.md)。

## 出現在哪些論文

[PV-RCNN](../papers/pv-rcnn.md)、[Voxel R-CNN](../papers/voxel-rcnn.md)、[CasA](../papers/casa.md)

## 常見誤解

- 「RoI Pooling 只看框內的東西」→ PV-RCNN 的 RoI-grid pooling 刻意讓搜尋半徑超出框外，因為**物體周圍的環境**（地面、旁邊的車）也有助於判斷。
