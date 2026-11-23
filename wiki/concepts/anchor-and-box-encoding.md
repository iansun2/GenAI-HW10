# Anchor 與 3D Box Encoding（錨框與 3D 框編碼）

## 白話解釋（給初學者）

**3D 框**用 7 個數字描述一個物體：
- 中心位置 `(x, y, z)`
- 大小 `(w, l, h)`：寬、長、高
- 朝向 `θ`：繞垂直軸（z 軸）的旋轉角，也叫 yaw

**Anchor（錨框）**：在鳥瞰圖的每個位置，預先擺好幾個「標準尺寸」的框，當作猜測的起點。
網路不用從零猜框，只要預測「這個 anchor 是不是物體」以及「要怎麼微調成真正的框」。
就像先拿一個「一般轎車大小」的模板蓋上去，再調整位置和大小。

## 技術細節（以 [SECOND](../papers/second.md) 為例）

### Anchor 設定（§3.1.5）
- 尺寸取自 KITTI 訓練集的平均值；每個位置擺 0° 和 90° 兩個角度。

| 類別 | w × l × h (m) | 中心 z (m) |
|---|---|---|
| Car | 1.6 × 3.9 × 1.56 | −1.0 |
| Pedestrian | 0.6 × 0.8 × 1.73 | −0.6 |
| Cyclist | 0.6 × 1.76 × 1.73 | −0.6 |

### 正負樣本分配（IoU 門檻，SECOND §3.1.5）
- Car：IoU ≥ 0.6 為正樣本，< 0.45 為負樣本，中間忽略。
- 行人、自行車：≥ 0.5 正、< 0.35 負。
- 樣本極度不平衡：約 70k 個 anchor，每個物體只配到 4–6 個正樣本 → 使用 focal loss（SECOND §3.2.1）。

### 回歸目標編碼（Eq. 6）
- 位置：`x_t = (x_g − x_a) / d_a`，`d_a = √(l_a² + w_a²)` 是 anchor 底面的對角線長；z 用 `h_a` 正規化。
- 大小：`w_t = log(w_g / w_a)`，l、h 同理。
- 角度：`θ_t = θ_g − θ_a`。

### 角度的難題與 SECOND 的解法
- 問題：朝向 θ 和 θ+π 的框，**形狀和位置完全相同**（只是車頭車尾相反）。直接回歸角度差時，這種情況會產生很大的 loss，讓網路無所適從。
- SECOND 的解法：`L_θ = SmoothL1( sin(θ_p − θ_t) )`。差 π 時 sin = 0，不懲罰。
- 再加一個**方向分類器**分辨車頭朝向（目標：yaw > 0 為正）。
- 效果（KITTI val, Car, Moderate）：Vector 編碼 74.79 → SECOND 76.48（SECOND Table 6）。

## 出現在哪些論文

- Anchor-based：[SECOND](../papers/second.md)、[PointPillars](../papers/pointpillars.md)，以及 Voxel R-CNN 的第一階段 RPN（「foreground anchors」，Voxel R-CNN §3.4）、[CasA](../papers/casa.md) 的 RPN（CasA §III-C）。
  - PointPillars 沿用同樣的編碼和 sin 角度 loss，但 Car anchor 高度寫 1.5 m（SECOND 為 1.56 m）；配對時只用 2D IoU，高度另外回歸（PointPillars §2.3、§4.2）。
- Anchor-free 路線：
  - CenterPoint（center heatmap，仍是 dense）
  - [VoxelNeXt](../papers/voxelnext.md)（直接由 sparse voxel 預測）
  - 詳見 [Anchor-free 與 Sparse Head](anchor-free-and-sparse-head.md)。

## 常見誤解

- 「anchor 越多越好」→ anchor 越多，負樣本越多，不平衡越嚴重，計算也越多。
