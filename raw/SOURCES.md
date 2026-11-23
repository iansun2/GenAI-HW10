# Raw Sources

抓取日期：2026-11-23

| # | 檔案 | 論文 | 發表 | 來源 | 備註 |
|---|---|---|---|---|---|
| 1 | `papers/second.txt` | SECOND: Sparsely Embedded Convolutional Detection | Sensors 2018 | PMC6210968（open access） | 不在 arXiv；MDPI PDF 下載被擋，改從 PMC HTML 抽出全文文字（不含圖） |
| 2 | `papers/pointpillars.pdf` | PointPillars: Fast Encoders for Object Detection from Point Clouds | CVPR 2019 | arXiv 1812.05784v2 | |
| 3 | `papers/pv-rcnn.pdf` | PV-RCNN: Point-Voxel Feature Set Abstraction for 3D Object Detection | CVPR 2020 | arXiv 1912.13192v2 | |
| 4 | `papers/voxel-rcnn.pdf` | Voxel R-CNN: Towards High Performance Voxel-based 3D Object Detection | AAAI 2021 | arXiv 2012.15712v2 | ⭐ 主線 |
| 5 | `papers/casa.pdf`（主）<br>`papers/casa-readme.md`（輔） | CasA: A Cascade Attention Network for 3-D Object Detection From LiDAR Point Clouds | IEEE TGRS Vol. 60, 2022 | 使用者透過 IEEE 提供全文 PDF（11 頁）；README 來自 github.com/hailanyi/CasA | ⭐ 主線；不在 arXiv。PDF 抽出的文字夾雜行號，引用數字時需核對。**因版權因素未上傳至 GitHub**，請自行從 IEEE Xplore 取得並放在 `raw/papers/casa.pdf` |
| 6 | `papers/nv3d.pdf` | NV3D: Leveraging Spatial Shape Through Normal Vector-based 3D Object Detection | arXiv 2025 | arXiv 2510.11632v1 | ⭐ 主線 |
| 7 | `papers/voxelnext.pdf` | VoxelNeXt: Fully Sparse VoxelNet for 3D Object Detection and Tracking | CVPR 2023 | arXiv 2303.11301v1 | 新趨勢：fully sparse |
| 8 | `papers/lion.pdf` | LION: Linear Group RNN for 3D Object Detection in Point Clouds | arXiv 預印本（v1 標示「Preprint. Under review.」） | arXiv 2407.18232v1 | 新趨勢：linear RNN / Mamba 類 backbone。⚠️ 原本此欄寫「NeurIPS 2024」，是憑記憶填的，raw 無法證實 → 2026-11-23 更正 |

## 發表資訊的查證（2026-11-23，LION ingest 後補做）

| 論文 | 發表資訊 | raw 中的證據 |
|---|---|---|
| SECOND | Sensors 2018 | second.txt 本身（PMC 頁面） |
| PointPillars | CVPR 2019 | PV-RCNN Table 1、LION Table 1 |
| PV-RCNN | CVPR 2020 | LION Table 1 |
| Voxel R-CNN | AAAI 2021 | voxel-rcnn.pdf 版權頁「Copyright © 2021, AAAI」 |
| CasA | IEEE TGRS Vol. 60, 2022 | casa.pdf 頁首 |
| NV3D | arXiv 2025 | nv3d.pdf 的 arXiv 浮水印（2025-10-13） |
| VoxelNeXt | CVPR 2023 | LION Table 1 |
| LION | arXiv 預印本，under review | lion.pdf 第 1 頁註腳 |
