# LION: Linear Group RNN for 3D Object Detection in Point Clouds

> 出處：**arXiv 預印本** 2407.18232v1（2024-07-25，PDF 標示「Preprint. Under review.」）· `raw/papers/lion.pdf` · 專案頁：happinesslz.github.io/projects/LION
> 作者：Zhe Liu, Jinghua Hou, Xinyu Wang, Xiaoqing Ye, Jingdong Wang, Hengshuang Zhao, Xiang Bai（華中科技大學 / 港大 / 百度）
> 資料限制：
> - 發表狀態以 raw 檔案為準（under review）。先前 SOURCES.md 寫的「NeurIPS 2024」是憑記憶填的，已更正。
> - **沒有延遲或 FPS**，只有 FLOPs 和參數量。
> - KITTI 結果只在附錄（Table 8），而且表中 baseline 疑似是 test 數字（見資料品質備註）。

## 一句話總結

用 **linear RNN**（Mamba、RWKV、RetNet 等）取代 Transformer 當 3D backbone，讓**數千個 voxel 在同一群組內互動**，看得更遠。再用 3D spatial feature descriptor 補回局部空間資訊、用 voxel generation 補強稀疏的前景。在 Waymo、nuScenes、Argoverse2、ONCE 上都達到 SOTA。

## 在演進中的位置（整理）

- [SECOND](second.md) 到 [CasA](casa.md)：backbone 都是 **sparse conv**，感受野受限於卷積核大小。
- [VoxelNeXt](voxelnext.md)：用額外下採樣擴大感受野。
- Transformer 路線（SST、DSVT，本 wiki 未 ingest，透過 LION 得知）：用 attention 建立長距離關係，但只能在小群組內做。
- **LION**：用 linear RNN，在**大群組**內建立長距離關係。

## 要解決的問題（動機）

- Transformer 的計算量對序列長度是**平方**成長，所以 3D Transformer 只能讓**小群組**內的 voxel 互相 attention，難以建立長距離關係（§1）。
- Linear RNN（Mamba、RWKV 等）在 LLM 中已能和 Transformer 競爭，計算量對長度**線性**成長（§1）。
- 問題：**能不能用 linear RNN，以較低成本在大群組中建立長距離關係？**
- 挑戰：
  1. RNN 需要一維序列作為輸入，3D voxel 攤平成一維後會**丟失空間鄰近關係**（§1、Fig. 4）。
  2. 點雲非常稀疏，前景特徵不足（§1）。

## 核心方法

架構（Fig. 2）：**Voxel 化 → 3D sparse window 分組 → N 個 LION block（各接 voxel generation 和 voxel merging）→ BEV backbone → Detection head**
- 論文的貢獻只在 **3D backbone**，BEV backbone 和 head 沿用其他方法（Waymo 用 DSVT 的 center-based head）（§3.1、§4.2）。

### 1. 3D Sparse Window 分組（§3.1）
- 把 voxel 分到不重疊的 3D 窗口，依 **X 軸**或 **Y 軸**排序。
- 依 FlatFormer 的做法切成**大小相同的群組**（每群 K 個 voxel），而不是形狀相同的窗口。
- **群組大小**：四個 block 分別是 **4096、2048、1024、512**；對照用的「小群組」為 256（Table 5）。
- 比喻：Transformer 像小組討論，每組 256 人，人一多就討論不完；linear RNN 像傳紙條，傳 4096 人也只多花線性的時間。

### 2. LION Block（§3.2、Fig. 3）
- **LION layer**：兩個 linear group RNN，一個用 X 軸分組，一個用 Y 軸分組，讓特徵在兩個方向都能交流。
- 階層式結構：用 voxel merging（下採樣）和 voxel expanding（上採樣）取得多尺度特徵，透過 index mapping 在稀疏資料上實作。
- 算子採**雙向**結構。

### 3. 3D Spatial Feature Descriptor（3D SFD）（§3.2）
- **問題**（Fig. 4）：voxel 01 和 34 在 3D 空間中相鄰，但依 X 軸攤平成一維後，在序列中相隔很遠。
- 一種解法是增加掃描順序（例如 VMamba），但掃描順序是人工設計的，計算量也會跟著增加。
- LION 的解法：加一個 **3D submanifold sparse conv + LayerNorm + GELU**，補回局部的 3D 鄰近資訊。
- 放在 voxel merging **之前**，以減少下採樣時的資訊損失（Table 9）。
- 比較（Table 6，Waymo 20% 資料，L2 mAPH）：

| 替代方案 | L2 mAPH |
|---|---|
| 不用 | 67.6 |
| MLP | 67.7 |
| linear group RNN | 67.9 |
| **3D SFD（submanifold conv）** | **69.3** |

  → linear RNN **擅長長距離、不擅長局部**；局部關係還是交給卷積。（整理）

### 4. Voxel Generation（§3.3）
- **選前景（不需額外監督）**：計算每個 voxel 的特徵反應（channel 平均，Eq. 1），取前 **r = 20%** 作為前景（Eq. 2）。
- **擴散**：每個前景 voxel 往 4 個斜角方向（[±1, ±1, 0]）各長出一個新 voxel，特徵初始化為 **0**。
- **自回歸生成**：把新 voxel 和原本的特徵一起送進下一個 LION block，由 RNN 依其他 voxel 的資訊把特徵「填上」（Eq. 3、4）。
- 比較（Table 7，L2 mAPH）：

| 方法 | L2 mAPH |
|---|---|
| 不生成 | 68.6 |
| 0 特徵 + sparse conv | 66.6 |
| KNN 特徵 + 自回歸 | 68.3 |
| **0 特徵 + 自回歸（LION）** | **69.3** |

  → 效果來自 RNN 的自回歸能力，而不是單純多了 voxel。
- r = 0.5 時只比 0.2 好一點（69.3 → 69.3 mAPH，mAP 71.4 → 71.5），所以採用 0.2 以平衡計算量（Table 10）。

### 5. 實作設定（§4.2）
- Waymo：grid (0.32, 0.32, 0.1875) m、C=64（-L 版本 C=128）、4 個 block、窗口 (13, 13, 32/16/8/4)、DSVT 的 center-based head、8 張 V100 訓練 24 epochs。
- nuScenes：只把 DSVT 的 3D backbone 換成 LION，訓練 36 epochs，不用 CBGS。
- Argoverse2：換掉 VoxelNeXt 或 SAFDNet 的 3D backbone。
- ONCE：換掉 SECOND 的 3D backbone，使用 CenterPoint 的 head。
- KITTI：使用 SECOND 的 BEV backbone 和 head（A.1）。

## 主要結果

### Waymo val（Table 1，同一張表，單幀、無測試增強）

| 方法 | 類型 | Vehicle L1 AP/APH | Ped. L1 AP/APH | L2 mAP/mAPH |
|---|---|---|---|---|
| SECOND | sparse conv | 72.3 / 71.7 | 68.7 / 58.2 | 61.0 / 57.2 |
| PV-RCNN‡ | sparse conv | 78.0 / 77.5 | 79.2 / 73.0 | 69.6 / 67.2 |
| PV-RCNN++‡ | sparse conv | 79.3 / 78.8 | 81.3 / 76.3 | 71.7 / 69.5 |
| VoxelNeXt | sparse conv | 78.2 / 77.7 | 81.5 / 76.3 | 72.2 / 70.1 |
| HEDNet | sparse conv | **81.1 / 80.6** | 84.4 / 80.0 | 75.3 / 73.4 |
| DSVT-Voxel | Transformer | 79.7 / 79.3 | 83.7 / 78.9 | 74.0 / 72.1 |
| LION-RetNet | linear RNN | 79.0 / 78.5 | 84.6 / 80.0 | 74.6 / 72.7 |
| LION-RWKV | linear RNN | 79.7 / 79.3 | 84.6 / 80.0 | 74.7 / 72.8 |
| LION-Mamba | linear RNN | 79.5 / 79.1 | 84.9 / 80.4 | 75.1 / 73.2 |
| **LION-Mamba-L** | linear RNN | 80.3 / 79.9 | **85.8 / 81.4** | **75.9 / 74.0** |

‡ = two-stage。
- LION-Mamba-L 的 L2 mAPH 比 DSVT-Voxel 高 1.9（§4.3）。
- ⚠️ HEDNet（sparse conv）在 Vehicle 最強，L2 mAPH 73.4 也略高於 LION-Mamba 的 73.2。**只有 -L 大模型才全面超越 HEDNet**。（整理）

### nuScenes（Table 2，無測試增強）

| 方法 | val NDS / mAP | test NDS / mAP |
|---|---|---|
| CenterPoint | 66.5 / 59.2 | – |
| VoxelNeXt | 66.7 / 60.5 | – |
| DSVT | 71.1 / 66.4 | 72.7 / 68.4 |
| HEDNet | 71.4 / 66.7 | 72.0 / 67.7 |
| **LION-Mamba** | **72.1 / 68.0** | **73.9 / 69.8** |

### Argoverse2 val（Table 3，mAP）
- CenterPoint 22.0、FSDv1 28.2、VoxelNeXt 30.7、HEDNet 37.1、FSDv2 37.6、SAFDNet 39.7、**LION-Mamba 41.5**。

### ONCE val（Table 4，mAP，使用 CenterPoint head）
- SECOND 51.9、PV-RCNN 53.6、CenterPoint 60.1、**LION-Mamba 66.6**。
- 行人進步最多：CenterPoint 49.9 → LION-Mamba 53.2（overall）。

### KITTI val（附錄 Table 8，R11，「mAP」= 所有類別、所有難度的平均）

| 方法 | Car Mod. | Ped. Mod. | Cyc. Mod. | mAP |
|---|---|---|---|---|
| DSVT-Voxel*（作者重跑） | 77.8 | 59.7 | 66.7 | 70.8 |
| LION-Mamba | 78.3 | 60.2 | 68.6 | 71.4 |
| LION-RWKV | 78.3 | 62.2 | 71.2 | **73.4** |

- ⚠️ Car Mod. 只有約 78，遠低於本 wiki 主線的 two-stage 方法（Voxel R-CNN val R11 84.52，Voxel R-CNN Table 5；不同的表）。原因是 KITTI 實驗為了公平比較 backbone，使用 SECOND 的 one-stage BEV backbone 和 head（A.1）。
- 這張表的用途是**比較不同 linear RNN 算子**（TTT、xLSTM、RetNet、Mamba、RWKV），不是追求 KITTI SOTA。

### 消融實驗（Table 5，Waymo val，20% 訓練資料、12 epochs，L2 mAP/mAPH）

| 大群組 | 3D SFD | Voxel Gen. | L2 mAP / mAPH |
|---|---|---|---|
| | | | 68.8 / 65.8 |
| ✓ | | | 69.5 / 66.9 |
| ✓ | ✓ | | 70.8 / 68.6 |
| ✓ | | ✓ | 70.1 / 67.6 |
| ✓ | ✓ | ✓ | **71.4 / 69.3** |

- 大群組 +1.1、3D SFD +1.7、voxel generation +0.7，合計 +3.5 mAPH（§4.4）。
- 3D SFD 對**行人**幫助最大（Ped. L2 APH 67.2 → 69.6）。

### 計算量（附錄 Table 12，Waymo val）

| Backbone | 算子 | L2 mAPH | FLOPs (G) | Params (M) |
|---|---|---|---|---|
| ResBackbone8×（CenterPoint） | sparse conv | 65.8 | 48.2 | 2.7 |
| DSVT-Voxel | Transformer | 72.1 | 100.8 | 2.7 |
| LION-RetNet | linear RNN | 72.7 | 51.3 | 2.0 |
| LION-Mamba | linear RNN | 73.2 | 58.5 | 1.4 |
| LION-RWKV | linear RNN | 72.8 | 79.4 | 3.0 |

- LION-Mamba 的 FLOPs 約為 DSVT-Voxel 的 58%，參數量也更少。
- ⚠️ **但沒有實際延遲**。作者自己承認：「linear RNN 在平行運算上不如 Transformer 有效率，**執行速度仍需改進**」（§5 Limitations），對自駕車硬體的要求也比較高（A.8）。
- 呼應 [VoxelNeXt](voxelnext.md) 的教訓：**FLOPs 少不代表比較快**。

### 推論時的穩健性（附錄 Table 11）
- 用同一個訓練好的模型，推論時改變窗口大小（7 到 25）或群組大小（2048 到 8192），L2 mAPH 都在 73.02–73.25 之間。
- 作者認為 LION 對人工設定的超參數依賴較低（A.2）。

## 和其他方法的關係

- **借用**：
  - FlatFormer 的等大小分組
  - DSVT 的設定和 head
  - Mamba、RWKV、RetNet 等 linear RNN 算子
  - [Sparse Convolution](../concepts/sparse-convolution.md)：3D SFD 使用 submanifold conv
- **可替換性**：LION 是 backbone，可以換進 DSVT、[VoxelNeXt](voxelnext.md)、SAFDNet、[SECOND](second.md) 等偵測器（§4.2）。
- **和主線的對比**：主線（Voxel R-CNN、CasA、NV3D）在 head 或輸入端改進，LION 改進的是 **backbone 本身**。

## 限制與討論

- **速度**：沒有延遲數字，作者承認需要改進（§5）。
- **遠距離**：在稀疏的遠處仍會漏掉物體，作者打算未來融合影像特徵（A.7）。
- **硬體需求**較高（A.8）。

## 資料品質備註（本次 ingest 發現）

| # | 問題 | 說明 |
|---|---|---|
| 1 | 發表狀態 | raw PDF 為「Preprint. Under review.」；本 wiki 先前在 SOURCES.md 寫成 NeurIPS 2024（憑記憶，未經 raw 證實）→ 已更正 |
| 2 | **KITTI Table 8 疑似把 test 數字放進 val 表** | 表標題寫「KITTI validation set」，但 VoxelNet 77.5/65.1/57.7、SECOND 83.1/73.7/66.2、PointPillars 79.1/75.0/68.3 和各自原論文的 **test R11** 數字相同（SECOND Table 2、PointPillars Table 2） |
| 3 | 和 VoxelNeXt Table 15 的數字不一致 | 見 [Waymo 同表比較](../comparisons/waymo-same-table.md) 的對照表：PV-RCNN、CenterPoint、FSD 不同；SECOND、PointPillars、VoxelNeXt 相同 |
| 4 | Waymo LEVEL 定義 | LION：L1「多於 5 點」、L2「至少 1 點」，和 PV-RCNN、Voxel R-CNN 的描述都不同 |

## 相關概念

[Transformer 與 Linear RNN Backbone](../concepts/transformer-and-linear-rnn-backbone.md) · [Sparse Convolution](../concepts/sparse-convolution.md) · [Waymo Open Dataset](../concepts/waymo-open-dataset.md) · [nuScenes 與 Argoverse2](../concepts/nuscenes-and-argoverse2.md) · [Waymo 同表比較](../comparisons/waymo-same-table.md)
