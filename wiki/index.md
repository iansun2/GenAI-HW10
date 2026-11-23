# Wiki Index

## Concepts
- [點雲與 LiDAR](concepts/point-cloud-and-lidar.md) — 給初學者：點雲是什麼、三大特性、三種表示法（point / voxel / pillar）
- [Voxelization](concepts/voxelization.md) — 把點雲切成 3D 小格子；VFE；voxel vs pillar；格子大小的取捨
- [Sparse Convolution](concepts/sparse-convolution.md) — 只在有資料的地方算；一般 vs submanifold
- [Anchor 與 Box Encoding](concepts/anchor-and-box-encoding.md) — 7 參數 3D 框、anchor、角度 sin loss 與方向分類器
- [GT-sampling](concepts/gt-sampling-augmentation.md) — 把其他場景的物體貼進來的資料增強
- [KITTI Benchmark](concepts/kitti-benchmark.md) — 難度分級、train/val 切分、3D AP / BEV AP / AOS、IoU 門檻、R11 vs R40；跨論文比較數字的注意事項；本 wiki 以 val 為主
- [Waymo Open Dataset](concepts/waymo-open-dataset.md) — 360° 大型資料集；LEVEL 1/2、mAPH、距離分段
- [nuScenes 與 Argoverse2](concepts/nuscenes-and-argoverse2.md) — 10 類 + NDS；200 m 長距離；四個資料集對照表
- [Anchor-free 與 Sparse Head](concepts/anchor-free-and-sparse-head.md) — anchor / center / sparse voxel 三種 head；物體中心不是必要的；NMS vs sparse max pooling
- [One-stage vs Two-stage](concepts/one-stage-vs-two-stage.md) — 直接出框 vs 先提案再精修；第二階段約 +4 AP
- [RoI Pooling](concepts/roi-pooling.md) — 從 3D 特徵中為每個候選框取出固定大小的特徵；RoI-grid vs Voxel RoI
- [法向量](concepts/normal-vector.md) — 表面朝向；KNN + PCA 計算；法向量密度可找出地面
- [輸入取樣](concepts/input-sampling.md) — 丟掉近處冗餘、保留遠處；ND sampling 與 FOV-aware bin sampling
- [Transformer 與 Linear RNN Backbone](concepts/transformer-and-linear-rnn-backbone.md) — 鄰居 / 小組會議 / 傳紙條；一維序列丟失空間資訊；FLOPs ≠ 速度
- [Cascade Refinement](concepts/cascade-refinement.md) — 多階段精修；為什麼 2D cascade 在 3D 失效；cascade attention 與 boxes voting

## Papers
- [SECOND](papers/second.md) — 2018，把 sparse conv 帶進 LiDAR 偵測，voxel-based 方法的共同 backbone
- [PointPillars](papers/pointpillars.md) — 2019，把點雲切成柱子、只用 2D 卷積，62 Hz
- [PV-RCNN](papers/pv-rcnn.md) — 2020，two-stage；voxel 產生候選框 + keypoint / RoI-grid pooling 精修
- [Voxel R-CNN](papers/voxel-rcnn.md) — 2021 ⭐，只用 voxel 的 two-stage；Voxel RoI Pooling + voxel query；精度追平 PV-RCNN、快約 3 倍
- [CasA](papers/casa.md) — 2022 ⭐，cascade attention 多階段精修；可接任何 two-stage；進步集中在遠處物體和行人
- [NV3D](papers/nv3d.md) — 2025 ⭐（arXiv 預印本），輸入端加法向量特徵與取樣；丟掉 53% voxel 只掉約 1 點；**同表中 Car 精度未超越 Voxel R-CNN**，資料品質問題多
- [VoxelNeXt](papers/voxelnext.md) — 2023，全程 sparse，不用 anchor / dense head / NMS；長距離速度優勢；無 KITTI 結果
- [LION](papers/lion.md) — 2024（arXiv 預印本），linear RNN（Mamba 等）3D backbone，大群組 + 3D SFD + voxel generation；Waymo、nuScenes SOTA；無延遲數字

## Comparisons
- [速度 vs 精度](comparisons/speed-vs-accuracy.md) — 主表採同一張來源表格（目前為 Voxel R-CNN Table 5），速度表含 FPS
- [Waymo 同表比較](comparisons/waymo-same-table.md) — 主表為 LION Table 1（第二張表為 VoxelNeXt Table 15）；兩表數字不一致的對照
- [PV-RCNN vs Voxel R-CNN](comparisons/pv-rcnn-vs-voxel-rcnn.md) — 需要原始點嗎？兩篇相反主張的對照與研究方法示範
