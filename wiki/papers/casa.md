# CasA: A Cascade Attention Network for 3-D Object Detection From LiDAR Point Clouds

> 出處：IEEE TGRS Vol. 60, 2022, Art. 5704511 · DOI 10.1109/TGRS.2022.3203163 · `raw/papers/casa.pdf`（主）、`raw/papers/casa-readme.md`（輔）
> 作者：Hai Wu, Jinhao Deng, Chenglu Wen, Xin Li, Cheng Wang, Jonathan Li（廈門大學等）
> 資料限制：
> - PDF 的**表格是圖片**，抽文字時只拿到標題。本頁的表格數字是把頁面轉成圖片後**人工讀取**的。
> - README 的 model zoo 數字和論文 Table III 不完全一致，本頁**以論文為準**，README 的數字放備註。
> 程式碼：github.com/hailanyi/CasA（基於 OpenPCDet）

## 一句話總結

把 two-stage 的「精修一次」延伸成 **多階段 cascade 精修**。每個階段用 **attention** 匯總前面所有階段的 RoI 特徵，解決傳統 cascade 在 3D 中「忽略遠處物體」和「誤差傳遞」兩個問題。可以接在任何 two-stage 偵測器上，接在 [Voxel R-CNN](voxel-rcnn.md) 時，KITTI test Car Mod. 從 81.62 提升到 83.06。

## 要解決的問題（動機）

- 既有 two-stage 方法只用**一個子網路**精修。但 LiDAR 點雲近密遠疏，近處和遠處物體的分布差異很大，一個子網路難以同時處理好（§I）。
- 2D 偵測中的 **Cascade R-CNN**：串接多個精修頭，IoU 門檻逐步提高，效果很好。
- **但直接套用到 3D 反而沒用**（Table I，KITTI val R40, Car Mod.）：

| | Stage 1 | Stage 2 | Stage 3 |
|---|---|---|---|
| Voxel R-CNN（單一精修） | 85.27 | – | – |
| + 傳統 cascade | 82.96 | 84.88 | 84.82 |

- 原因（§III-A1）：
  1. **忽略遠處物體**：後面的階段 IoU 門檻較高，能被選為正樣本的多半是點多、框準的**近處**物體；遠處物體常被當成負樣本 → 後面的階段只學會處理近處物體。
  2. **誤差傳遞**：3D 框還要估高度和非軸對齊的旋轉角，前一階段的小誤差會一路往後傳。
- CasA 的解法：**在階段之間建立更多連結**，讓後面的階段也看得到前面階段的物體特徵。

## 核心方法

架構（Fig. 1）：**Voxel 化 → 3D sparse backbone → BEV + RPN 產生候選框 → Cascade Refinement Network（CRN：3 個階段，每階段一個 CAM）→ Boxes voting → NMS**

### 1. RPN 與 backbone（§III-B、III-C）
- 和 [SECOND](second.md)、[PV-RCNN](pv-rcnn.md)、[Voxel R-CNN](voxel-rcnn.md) 相同：3×3×3 sparse conv 下採樣到 8×，壓成 BEV，用 [anchor](../concepts/anchor-and-box-encoding.md) 產生候選框。

### 2. Cascade Attention Module（CAM）（§III-A2，核心貢獻）
- 第 j 階段：
  1. 用 base detector 原本的 RoI pooling（例如 Voxel RoI Pooling）取得本階段的特徵 F̂ʲ，並串接一個「階段編號」的 position embedding。
  2. 收集**第 0 到第 j 階段**的所有特徵 Fʲ = [F̂⁰, …, F̂ʲ]。
  3. Query 來自**本階段**，Key 和 Value 來自**所有階段** → multi-head attention（Eq. 2）。
  4. 把本階段特徵和 H 個 head 的 attention 輸出串接，作為最終特徵（Eq. 3）。直覺是本階段的特徵最重要，所以要保留原樣。
- 第 1 階段等於 self-attention；之後各階段是 cross-attention。
- 設定：3 個階段、4 個 attention head、256 維特徵。
- 為什麼用 attention，不直接串接？直接串接很難學到「哪個階段的特徵比較重要」（Table II，val R40, Car Mod.）：

| 匯總方式 | Car Mod. |
|---|---|
| 串接（Concatenation） | 85.32 |
| GRU | 86.01 |
| 只用 self-attention | 86.22 |
| 只用 cross-attention | 86.29 |
| **Self + Cross attention** | **86.37** |

- 詳見 [Cascade Refinement](../concepts/cascade-refinement.md)。

### 3. Part-aided Scoring（§III-A3）
- 信心分數 = **全域信心分支** + **部位分數**（Eq. 4）。
- 部位分數：RPN 在 BEV 上預測一張「這裡是物體哪個部位」的分數圖，把框內各部位的分數取平均（part-sensitive warping，源自 SA-SSD）。
- 直覺：一台車的車頭、車身、車尾都有被偵測到，比只偵測到一角的框更可信。

### 4. Boxes Voting（§III-A4）
- 測試時，3 個階段各自輸出框和信心分數。
- 信心分數取平均：`C = (1/Nr) Σ Cʲ`（Eq. 5）。
- 框依信心分數加權平均：`B = Σ Cʲ·Bʲ / Σ Cʲ`（Eq. 6）。
- 再做 NMS 去除重複的框。
- 和只取信心最高框的 NMS 相比，voting 能利用**低信心但有用的預測**，讓各階段互補。

### 5. 訓練設定（§IV-B）
- 各階段 IoU 門檻逐步提高：Vehicle 0.5 → 0.55 → 0.6；Pedestrian、Cyclist 0.4 → 0.45 → 0.5。
- 三個類別用**一個模型**訓練。
- KITTI：2 張 3090、batch 4、80 epochs。第二階段取 128 個 proposal（正負 1:1）；測試時取前 100 個。
- 套到 PV-RCNN 時，因為 GPU 記憶體不夠，做了簡化：移除 PKW、只保留最後兩層 3D 特徵和 BEV 特徵、2D backbone 通道數減半。

## 主要結果

### KITTI val（Table III，同一張表）

| Base detector | Car Mod. R11 | → +CasA | Car Mod. R40 | → +CasA | Ped. Mod. R40 | Cyc. Mod. R40 |
|---|---|---|---|---|---|---|
| PV-RCNN | 83.90 | **86.17**（+2.27） | 84.83 | 85.89 | 56.67 → 59.86 | 71.95 → 70.69 ↓ |
| Voxel R-CNN | 84.52 | **86.58**（+2.06） | 85.29 | **86.37** | 60.97 → **66.62** | 72.54 → 73.94 |
| CT3D | 86.06 | **86.63**（+0.57） | 85.82 | 86.42 | 58.56 → 62.59 | 71.60 → 72.63 |

- 三種 base 全部進步，**Pedestrian 進步最多**（Voxel R-CNN +5.65）。
- CasA+PV 的 Cyclist 下降，作者解釋是因為簡化了 2D backbone（§IV-C1）。
- Voxel R-CNN 的 Ped / Cyc 數字是 CasA 作者用開源碼重現的（Table III 標題）。

### KITTI test（R40，Table IV）

| 方法 | Car E / M / H | Ped. E / M / H | Cyc. E / M / H |
|---|---|---|---|
| PV-RCNN | 90.25 / 81.43 / 76.82 | 52.17 / 43.29 / 40.29 | 78.60 / 63.71 / 57.65 |
| Voxel R-CNN | 90.90 / 81.62 / 77.06 | – | – |
| BtcDet | 90.64 / 82.86 / 78.09 | 47.80 / 41.63 / 39.30 | 82.81 / 68.68 / 61.81 |
| **CasA+V** | **91.58 / 83.06 / 80.08** | **54.04 / 47.09 / 44.56** | **87.91 / 73.47 / 66.17** |

- 在三個類別上都勝過所有已發表的方法（§IV-C2）。

### 遠距離（Fig. 5，KITTI val Car Mod.，Voxel R-CNN → CasA+V）

| 距離 | 0–10 m | 10–20 m | 20–30 m | 30–40 m | 40–50 m | 50 m+ |
|---|---|---|---|---|---|---|
| Voxel R-CNN | 92.3 | 96.4 | 91.4 | 75.5 | 45.8 | 7.0 |
| CasA+V | 92.4 | 96.5 | 91.5 | 78.7 | 50.5 | 16.1 |

→ 近處幾乎沒變，**進步集中在 30 m 以上**，正好對應動機中「忽略遠處物體」的問題。

### Waymo（v1.2 val，Table V，LEVEL 1 mAP / mAPH）

| 方法 | Vehicle | Pedestrian |
|---|---|---|
| Voxel R-CNN‡ | 77.43 / 76.71 | 76.37 / 68.21 |
| CasA+V | 78.54 / 78.00 | 80.88 / 73.10 |

（‡ 表示 CasA 作者重跑；PV-RCNN† 的 77.51 / 76.89 和 PV-RCNN 原論文 Table 6 一致。Waymo 版本 v1.2 出自 README。）

### ONCE（40 線 LiDAR，比 KITTI / Waymo 的 64 線更稀疏，Table IX）
- Voxel R-CNN → CasA+V：Vehicle 77.12 → 78.34、Pedestrian 41.90 → 50.34、Cyclist 62.31 → 70.01。

### 消融實驗（KITTI val R40, Car Mod., CasA+V）

**元件貢獻**（Table VIII，各階段輸出的 AP）：

| 設定 | Stage 1 | Stage 2 | Stage 3 |
|---|---|---|---|
| Voxel R-CNN | 85.27 | – | – |
| + 傳統 cascade | 82.96 | 84.88 | 84.82 |
| + Cascade Attention | 85.48 | 85.73 | 85.72 |
| + Part-aided Scoring | 85.67 | 85.89 | 85.85 |
| + Boxes Voting | 85.67 | 86.24 | **86.37** |

**階段數 vs 速度**（Table VI）：

| 階段數 | Car Mod. | 執行時間 (ms) |
|---|---|---|
| 1 | 85.49 | 64 |
| 2 | 85.96 | 77 |
| **3** | **86.37** | **86** |
| 4 | 86.27 | 101 |
| 5 | 86.24 | 114 |

- 3 個階段最好；4 個以上沒有進步，只會更慢。86 ms 約 11.6 FPS（單張 3090）。作者稱之為「real-time」（§IV-E1）。
- 依 Voxel R-CNN 自己報告的 25.2 FPS（RTX 2080 Ti）推估，CasA+V 約慢一倍以上，但兩者 GPU 不同，不能直接比較。（整理）

**Attention head 數**（Table VII）：1 → 86.11、**4 → 86.37**、8 → 86.27、16 → 86.17。

**Proposal 品質**（Fig. 6）：階段越後面，proposal 和真實框的 3D IoU 分布越靠近 1；CasA 比傳統 cascade 更集中在高 IoU。

## 和其他方法的關係

- **Base detector**：[PV-RCNN](pv-rcnn.md)、[Voxel R-CNN](voxel-rcnn.md)、CT3D。README 還有接 PV-RCNN++ 的 CasA-PV2。
- **借用**：
  - 2D 的 Cascade R-CNN（逐階段提高 IoU 門檻）
  - SA-SSD 的 part-sensitive warping（part-aided scoring）
  - Transformer 的 multi-head attention
- **後續**：README 提到以 CasA 偵測結果為基礎的 3D 多物件追蹤器 CasTrack。
- 和 [NV3D](nv3d.md) 的關係：兩者都以 Voxel R-CNN 為基礎，但改進的位置不同。
  - CasA 改**第二階段**（多階段精修）。
  - NV3D 改**輸入端**（法向量、取樣）。
  - NV3D 沒有和 CasA 比較。（整理）理論上兩者可以疊加使用，但沒有論文驗證過。

## 限制與討論（§V）

- **計算成本和效能的取捨**：作者自己承認，未來要研究更有效率的精修方式。
- **行人仍然最難**：體積小、方向難以分辨（Tables IV、V、IX 中行人的數字都最低）。
- 套到 PV-RCNN 時需要簡化才放得進 GPU 記憶體，所以「通用」實際上還是有成本。（整理）

## 資料品質備註（本次 ingest 發現）

- **內文和表格矛盾**：
  - §I 寫「改進 PV-RCNN、Voxel-RCNN、CT3D 分別 2.27%、2.06%、0.57%」。
  - §IV-C1 寫成「Voxel-RCNN、PV-RCNN、CT3D 分別 2.27%、2.06%、0.57%」，順序對調。
  - 對照 Table III，**§I 正確**（83.90→86.17 = +2.27；84.52→86.58 = +2.06）。
- **README 和論文不一致**（val R11, Car Mod.）：

| | README | 論文 Table III |
|---|---|---|
| CasA-V | 86.54 | 86.58 |
| CasA-T | 86.76 | 86.63 |
| CT3D baseline | 84.97 | 86.06 |

  推測 README 是開源模型重新訓練的結果。本 wiki 以論文為準。
- **同一篇論文內 baseline 不同**：Voxel R-CNN val R40 Car Mod. 在 Table I / VIII 為 85.27，在 Table III 為 85.29。

## 相關概念

[Cascade Refinement](../concepts/cascade-refinement.md) · [One-stage vs Two-stage](../concepts/one-stage-vs-two-stage.md) · [RoI Pooling](../concepts/roi-pooling.md) · [KITTI Benchmark](../concepts/kitti-benchmark.md) · [Waymo Open Dataset](../concepts/waymo-open-dataset.md)
