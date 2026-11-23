# 簡報事實清單（Fact Sheet）

> 用途：簡報中**每一個數字**都必須來自這份清單；這份清單的每一條都必須能在對應的 wiki 頁找到。
> 格式：`ID | 事實 | 數字（以 ; 分隔，供自動檢查） | wiki 頁 | 原始出處`
> 檢查程式：`slides/check_facts.py`

| ID | 事實 | 數字 | wiki 頁 | 原始出處 |
|---|---|---|---|---|
| F01 | 影像方法 2D 車輛 AP 約 90%，3D 只有約 15% | 90; 15 | concepts/point-cloud-and-lidar.md | SECOND §1 |
| F02 | KITTI 場景切成 voxel 後只有約 5k–8k 個非空 voxel，稀疏度約 0.005 | 0.005 | concepts/sparse-convolution.md | SECOND §3.1.3 |
| F03 | 少於約 10 個點的遠方車輛常被漏偵測 | 10 | papers/second.md | SECOND §4.3.1 |
| F04 | KITTI 只使用前鏡頭看得到的點，約佔 10% | 10% | concepts/kitti-benchmark.md | PointPillars §6 |
| F05 | SECOND voxel 大小 0.4 × 0.2 × 0.2 m | 0.4; 0.2 | concepts/voxelization.md | SECOND §3.1.1 |
| F06 | PointPillars 格子 0.16 m × 0.16 m；約 97% pillar 是空的 | 0.16; 97% | papers/pointpillars.md | PointPillars §2.1、§4.2 |
| F07 | 3D 框 7 個參數 (x, y, z, w, l, h, θ)；Car anchor 1.6 × 3.9 × 1.56 m | 1.6; 3.9; 1.56 | concepts/anchor-and-box-encoding.md | SECOND §3.1.5 |
| F08 | 約 70k 個 anchor，每個物體只配到 4–6 個正樣本 | 70k | concepts/anchor-and-box-encoding.md | SECOND §3.2.1 |
| F09 | KITTI 切分 train 3712 / val 3769 | 3712; 3769 | concepts/kitti-benchmark.md | SECOND §4 |
| F10 | IoU 門檻 Car 0.7、Ped 0.5、Cyc 0.5 | 0.7; 0.5 | concepts/kitti-benchmark.md | PV-RCNN §4.2；CasA §IV-A1 |
| F11 | KITTI 2019-10-08 從 R11 改為 R40 | 2019-10-08 | concepts/kitti-benchmark.md | Voxel R-CNN §4.3 註腳 |
| F12 | SECOND：訓練快約 4 倍、推論快約 3 倍（vs dense） | 4 倍; 3 倍 | concepts/sparse-convolution.md | SECOND §1 |
| F13 | VoxelNet 0.23 s/幀、val Car Mod. 65.46；SECOND 0.05 s、76.48 | 0.23; 65.46; 0.05; 76.48 | papers/second.md | SECOND Table 4 |
| F14 | PointPillars 62 Hz、每幀 16.2 ms；encoder 1.3 ms vs VoxelNet 190 ms | 62; 16.2; 1.3; 190 | papers/pointpillars.md | PointPillars §6 |
| F15 | PointPillars val Car Mod. 77.98 | 77.98 | papers/pointpillars.md | PointPillars §5 |
| F16 | VoxelNet → SECOND → PointPillars：4.4 → 20 → 62 Hz | 4.4; 20; 62 | comparisons/speed-vs-accuracy.md | PointPillars Table 2 |
| F17 | PV-RCNN：只有 RPN 80.87 → 加第二階段 84.83（val R40） | 80.87; 84.83 | concepts/one-stage-vs-two-stage.md | PV-RCNN Table 7 |
| F18 | RoI 切成 6×6×6 = 216 個格點 | 216 | concepts/roi-pooling.md | PV-RCNN §3.3 |
| F19 | 3D 特徵中非空 voxel 不到 3% | 3% | concepts/roi-pooling.md | Voxel R-CNN §3.1 |
| F20 | PV-RCNN 各模組耗時：VSA 49.4 ms，約一半 | 49.4; 21.1; 9.4; 19.1 | papers/voxel-rcnn.md | Voxel R-CNN Table 2 |
| F21 | SECOND 加 BEV 精修頭只 +0.6：78.62 → 79.26 | 78.62; 79.26; 0.6 | papers/voxel-rcnn.md | Voxel R-CNN Table 1 |
| F22 | 同表 val R11：PV-RCNN 83.69、Voxel R-CNN 84.52 | 83.69; 84.52 | comparisons/pv-rcnn-vs-voxel-rcnn.md | Voxel R-CNN Table 5 |
| F23 | FPS：PV-RCNN 8.9、Voxel R-CNN 25.2 | 8.9; 25.2 | comparisons/pv-rcnn-vs-voxel-rcnn.md | Voxel R-CNN Table 3 |
| F24 | Waymo 50 m+：PV-RCNN 42.17、Voxel R-CNN 53.15 | 42.17; 53.15 | comparisons/pv-rcnn-vs-voxel-rcnn.md | Voxel R-CNN Table 6 |
| F25 | Voxel R-CNN 消融：77.99@40.8 / 84.21@17.4 / 84.33@19.1 / 84.27@21.4 / 84.52@25.2 | 77.99; 40.8; 84.21; 17.4; 84.33; 19.1; 84.27; 21.4; 84.52; 25.2 | papers/voxel-rcnn.md | Voxel R-CNN Table 7 |
| F26 | 傳統 cascade：Voxel R-CNN 85.27 → 84.82（下降） | 85.27; 84.82 | concepts/cascade-refinement.md | CasA Table I |
| F27 | CasA 元件：+CAM 85.72、+part 85.85、+voting 86.37 | 85.72; 85.85; 86.37 | papers/casa.md | CasA Table VIII |
| F28 | CasA 遠距離：40–50 m 45.8 → 50.5；50 m+ 7.0 → 16.1 | 45.8; 50.5; 7.0; 16.1 | papers/casa.md | CasA Fig. 5 |
| F29 | test R40 Car Mod.：Voxel R-CNN 81.62 → CasA+V 83.06 | 81.62; 83.06 | papers/casa.md | CasA Table IV |
| F30 | 階段數：1 階段 64 ms、3 階段 86 ms | 64; 86 | papers/casa.md | CasA Table VI |
| F31 | 法向量：KNN K=7 + PCA；不到 20% 的 voxel 有超過 3 個點 | 7; 20% | papers/nv3d.md | NV3D §3.1 |
| F32 | 約 90% 的 voxel 集中在 30 m 以內 | 90%; 30 m | papers/nv3d.md | NV3D §3.2 |
| F33 | ND + FOV 取樣丟掉 53.14% 的 voxel | 53.14 | papers/nv3d.md | NV3D Table 7 |
| F34 | 同表（不取樣）Car Mod.：Voxel R-CNN 85.29、NV3D 84.78；三難度平均 86.84 vs 86.60 | 85.29; 84.78; 86.84; 86.60 | papers/nv3d.md | NV3D Table 7 |
| F35 | 取樣後變化：SECOND +1.18、Voxel R-CNN −1.04、NV3D −1.06 | 1.18; 1.04; 1.06 | papers/nv3d.md | NV3D Table 7 |
| F36 | NV3D 取樣後 Pedestrian 三難度平均 −18.16 | 18.16 | papers/nv3d.md | NV3D Table 1 |
| F37 | CenterPoint heatmap 上 Car 有反應的位置不到 1% | 1% | papers/voxelnext.md | VoxelNeXt §1 |
| F38 | 範圍 50 → 200 m：CenterPoint 82 → 246 ms；VoxelNeXt 61 → 66 ms | 82; 246; 61; 66 | papers/voxelnext.md | VoxelNeXt Fig. 3 |
| F39 | nuScenes test：CenterPoint 58.0 / 65.5 / 96 ms；VoxelNeXt 64.5 / 70.0 / 66 ms | 58.0; 65.5; 96; 64.5; 70.0 | papers/voxelnext.md | VoxelNeXt Table 12 |
| F40 | 負責預測的 voxel：72.8% 在邊界附近、只有 9.9% 在中心附近 | 72.8; 9.9 | papers/voxelnext.md | VoxelNeXt Table 7 |
| F41 | FLOPs：VoxelNeXt 38.7G vs CenterPoint 186.6G | 38.7; 186.6 | papers/voxelnext.md | VoxelNeXt §5 |
| F42 | LION 群組大小 4096 / 2048 / 1024 / 512；小群組 256 | 4096; 2048; 1024; 512; 256 | papers/lion.md | LION §4.2、Table 5 |
| F43 | Waymo L2 mAPH：SECOND 57.2、PV-RCNN 67.2、VoxelNeXt 70.1、DSVT-Voxel 72.1、HEDNet 73.4、LION-Mamba 73.2、LION-Mamba-L 74.0 | 57.2; 67.2; 70.1; 72.1; 73.4; 73.2; 74.0 | comparisons/waymo-same-table.md | LION Table 1 |
| F44 | FLOPs：LION-Mamba 58.5G vs DSVT-Voxel 100.8G | 58.5; 100.8 | papers/lion.md | LION Table 12 |
| F45 | LION 消融（L2 mAPH）：65.8 → 66.9 → 68.6 → 69.3 | 65.8; 66.9; 68.6; 69.3 | papers/lion.md | LION Table 5 |
| F46 | KITTI val R11 同表 Car Mod.：VoxelNet 65.46、PointPillars 76.06、SECOND 78.62、PointRCNN 78.63、STD 79.80、SA-SSD 79.91、PV-RCNN 83.69、Voxel R-CNN 84.52 | 65.46; 76.06; 78.62; 78.63; 79.80; 79.91; 83.69; 84.52 | comparisons/speed-vs-accuracy.md | Voxel R-CNN Table 5 |
| F47 | CasA 同表 val R11：PV-RCNN 83.90 → 86.17；Voxel R-CNN 84.52 → 86.58；CT3D 86.06 → 86.63 | 83.90; 86.17; 84.52; 86.58; 86.06; 86.63 | comparisons/speed-vs-accuracy.md | CasA Table III |
| F48 | SECOND Car Mod.：val 76.48、test 73.66（R11）、test 72.55（R40） | 76.48; 73.66; 72.55 | concepts/kitti-benchmark.md | SECOND Table 4 / 2；PV-RCNN Table 1 |
| F49 | NV3D 宣稱「Car 86.60% mAP」= 三難度平均；Moderate 為 84.78 | 86.60; 84.78 | concepts/kitti-benchmark.md | NV3D Table 1 / 4 |
| F50 | FLOPs 約 1/5，延遲 66 vs 96 ms（只少約 1/3） | 66; 96 | comparisons/speed-vs-accuracy.md | VoxelNeXt §5 |
| F51 | Waymo L2 mAPH 主表（LION Table 1）其餘：PointPillars 57.8、CenterPoint 65.8、PV-RCNN++ 69.5、FSD 70.8 | 57.8; 65.8; 69.5; 70.8 | comparisons/waymo-same-table.md | LION Table 1 |
