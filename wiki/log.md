# Wiki Log

## [2026-11-23] setup | 建立 wiki 與取得資料
- 討論確定：主題 LiDAR 3D Object Detection；語言繁中＋英文術語；聽眾為「懂一點 DL、沒碰過點雲」。
- 論文清單 8 篇（見 raw/SOURCES.md）；新趨勢從候選中選 VoxelNeXt（取代 CenterPoint）與 LION（取代 DSVT / Voxel Mamba）。
- 取得資料時的問題：
  - SECOND 不在 arXiv，MDPI 擋自動下載 → 改用 PMC 開放版 HTML 抽文字。
  - CasA 不在 arXiv，全文在 IEEE 付費牆 → 暫用官方 GitHub README；待使用者決定是否提供 PDF。
  - NV3D 原本記憶中的年份不確定 → 以 arXiv 2510.11632（2025-10）為準。
- 使用者補上 CasA 全文 PDF（IEEE TGRS 2022）→ 重新命名為 `raw/papers/casa.pdf`，README 改為輔助來源。
- 工具問題：Read 工具無法渲染 PDF（缺 poppler）→ 改用 pypdf 抽文字；IEEE PDF 抽出的文字夾雜行號，數字需人工核對。

## [2026-11-23] ingest | SECOND
- 討論：提出 5 個重點與 7 個預計頁面。
- 使用者決定：sparse conv 頁以**直覺解釋**為主（細節收進技術細節小節）；數字**以 val 為主、test 並列**（已寫進 kitti-benchmark.md 作為 wiki 規則）。
- 新增：papers/second.md、concepts/{point-cloud-and-lidar, voxelization, sparse-convolution, anchor-and-box-encoding, gt-sampling-augmentation, kitti-benchmark}.md
- 生成時的自我檢查：
  - KITTI 的 IoU 門檻、R11/R40 在 SECOND 原文中沒有 → 不憑記憶填寫，標為「待補」。
  - SECOND Table 1 原文沒有時間單位 → 照實標註「原文未寫單位」。
  - 尚未 ingest 的論文之間的關係 → 標註「待 ingest 確認」，之後回頭更新。
- 刻意保留的前向連結：papers/{pointpillars, pv-rcnn, voxel-rcnn, casa, nv3d, voxelnext, lion}.md、concepts/one-stage-vs-two-stage.md

## [2026-11-23] ingest | PointPillars
- 討論：提出 5 個重點、5 個頁面改動；使用者同意照設計進行。
- 新增：papers/pointpillars.md、comparisons/speed-vs-accuracy.md
- 更新：concepts/voxelization.md（pillar 小節、格子大小取捨、稀疏度口徑）、gt-sampling-augmentation.md（PointPillars 調參、+3% mAP）、kitti-benchmark.md（AOS、10% 點雲、**跨論文比較數字的注意事項**）、anchor-and-box-encoding.md
- 檢查發現的問題：
  - **PDF 抽文字吃掉上標**：「0.162 m2」實為 0.16² m²。Table 4、Figure 5 的格子大小同樣受影響，已更正。→ 之後所有 PDF 數字遇到單位或指數時都要核對語意。
  - **跨論文數字不一致**：PointPillars 在自己的程式碼裡重跑其他方法的 encoder，比原論文高 1–10 mAP（§7.4）→ 新增 kitti-benchmark 的注意事項一節；comparisons 頁每一列都標來源。
  - **稀疏度口徑不同**：SECOND 的 0.005（非空比例，3D）vs PointPillars 的 97%（空的比例，2D）→ 在 voxelization.md 註明不可直接比較。
  - PointPillars 的 val 只有 Moderate 數字 → comparisons 表格只放 Moderate。

## [2026-11-23] ingest | PV-RCNN
- 討論：提出 5 個重點、4 個新頁面；使用者決定 Waymo **獨立成頁**。
- 新增：papers/pv-rcnn.md、concepts/{one-stage-vs-two-stage, roi-pooling, waymo-open-dataset}.md
- 更新：kitti-benchmark.md（填上 IoU 門檻、R11/R40，**移除「待補」**）、speed-vs-accuracy.md（新增 R11/R40 欄、三張同表比較）、point-cloud-and-lidar.md（point-voxel 混合）
- 檢查發現的問題：
  - **R11 / R40 混用**：SECOND test Car Mod. 在原論文為 73.66（R11），在 PV-RCNN Table 1 為 72.55（R40）；PointPillars 74.99 → 74.31。→ 回頭修正 speed-vs-accuracy：每個數字加註 R11/R40；PointPillars val 77.98 原文未註明 → 標「推定 R11」。
  - **前一輪的比較表有隱藏錯誤**：PointPillars ingest 時把不同口徑的 test 數字放在一起，當時沒有 R11/R40 的概念。這次發現後回溯修正。→ 教訓：「比較表」節點要在**加入新數字前**先確認口徑，而不是事後才補。
  - PV-RCNN 原文沒有速度 → 速度欄標「原文未報告」，不從其他來源猜。
  - Pedestrian 的 IoU 門檻 PV-RCNN 沒提 → 仍待補。
  - 交叉驗證：CasA README 中 PV-RCNN baseline 的 val 83.90/84.83 和 PV-RCNN 原文一致 ✅

## [2026-11-23] ingest | Voxel R-CNN ⭐
- 討論：提出 5 個重點、7 個頁面改動；使用者決定 comparisons 主表採 **B：以同一張來源表格為準**，原論文數字放備註（已寫進 CLAUDE.md 與 kitti-benchmark.md）。
- 新增：papers/voxel-rcnn.md、comparisons/pv-rcnn-vs-voxel-rcnn.md
- 更新：roi-pooling.md（Voxel RoI Pooling、RoI-grid vs Voxel RoI 對照表）、kitti-benchmark.md（R40 改版日期、第二個跨論文出入實例、FPS 來源不一）、waymo-open-dataset.md（LEVEL 定義出入）、one-stage-vs-two-stage.md（+6.2 AP vs 速度減半；BEV 精修只 +0.6）、pv-rcnn.md（補上速度 8.9 FPS、各模組耗時）
- **依規則 B 重建** speed-vs-accuracy.md：主表改用 Voxel R-CNN Table 5，速度表改用 Voxel R-CNN Table 3，舊 R11 test 表降為「歷史參考」。
- 檢查發現的問題：
  - ✅ 上一輪「SECOND、PointPillars 的 test 是 R11」原本是推論，現在由 Voxel R-CNN 註腳（2019-10-08 改版）**證實**，kitti-benchmark.md 改為引用出處。
  - ✅ PV-RCNN 速度的空缺由 Voxel R-CNN Table 2 / 3 補上。
  - ⚠️ 同一方法在不同論文的 val R11 不同：SECOND 76.48→78.62、PointPillars 77.98→76.06、PV-RCNN 83.90→83.69 → 觸發使用者決策（規則 B）。
  - ⚠️ FPS 來源混雜：PointPillars 42.4 = PyTorch 版（原論文 62 為 TensorRT 版）；SECOND 30.4 vs 原論文 20 → 在速度表加註。
  - ⚠️ Waymo LEVEL 定義兩篇描述不同 → 兩種都記錄，以 PV-RCNN 為準並標註。
- 觀察：**「比較/整合」節點是最常出錯的地方**。單篇摘要時數字都正確，一旦跨論文放進同一張表，就會出現口徑（R11/R40）、來源（原論文 vs 重跑）、硬體（PyTorch vs TensorRT）不一致的問題。

## [2026-11-23] ingest | CasA ⭐
- 討論：提出 5 個重點、6 個頁面改動；使用者決定比較表採 **A**：主表（Voxel R-CNN Table 5）不動，CasA 列標註「不在本表」，另開 CasA Table III 同表比較；CasA Table IV 作為補充的 test 精度表；速度表維持 Voxel R-CNN Table 3。
- 新增：papers/casa.md、concepts/cascade-refinement.md
- 更新：one-stage-vs-two-stage.md（cascade 小節）、roi-pooling.md、kitti-benchmark.md（Ped IoU 0.5 → **待補項目全部清空**；注意事項 #6 論文內文矛盾、#7 README ≠ 論文）、waymo-open-dataset.md、voxel-rcnn.md（後續關係已確認）、speed-vs-accuracy.md
- **取得資料節點的重大問題**：IEEE PDF 的 Table I–IX 都是**圖片**，pypdf 只抽到標題。
  - 若沒發現，很可能會改用 README 的數字，而 README 和論文不一致（CasA-V 86.54 vs 86.58；CT3D 84.97 vs 86.06）。
  - 修正：安裝 PyMuPDF 把頁面轉成 PNG，人工讀表。
  - **把檢查往前移**：CLAUDE.md 新增規則「抽文字後先檢查每張 Table 是否有數字」。之後的 ingest 在「讀論文」之前先做這個檢查。
- 其他檢查發現：
  - 論文 §I 與 §IV-C1 的提升幅度順序對調 → 以 Table III 為準（§I 正確），記錄在論文頁的資料品質備註。
  - 同一篇論文內 Voxel R-CNN baseline 有 85.27 / 85.29 兩個值。
  - Waymo：Voxel R-CNN 有 75.59（自報）和 77.43（CasA 重跑，v1.2）兩個值，推測是版本不同。
  - ✅ 交叉驗證：CasA Table III 的 PV-RCNN（83.90/84.83）、Voxel R-CNN（84.52/85.29）和原論文一致；CasA test 83.06 − 1.44 = 81.62，和 Voxel R-CNN test 一致。

## [2026-11-23] ingest | NV3D ⭐
- **前移的檢查生效**：讀論文前先確認表格有沒有數字 → NV3D 的表格是文字，可以直接讀（CasA 的教訓已內化為 ingest 第 0 步）。
- 討論：提出 5 個重點與 9 項資料品質問題；使用者決定簡報呈現採 **A：照實呈現**，把 NV3D 定位為「輸入特徵與資料取樣」這個方向，精度問題作為「讀論文要注意什麼」的實例。
- 新增：papers/nv3d.md（開頭列出資料限制）、concepts/{normal-vector, input-sampling}.md
- 更新：speed-vs-accuracy.md（NV3D 列標「不在本表」；新增 NV3D Table 7 取樣前後同表比較；觀察第 5 點）、kitti-benchmark.md（注意事項 #8 mAP 定義、#9 論文 baseline 前後不一）、voxel-rcnn.md、casa.md（後續 / 平行關係）
- 檢查發現的問題（9 項，詳見 nv3d.md 資料品質備註）：
  - **mAP = 三難度平均**，不是 Moderate AP → 若照抄摘要的「86.60% mAP」放進比較表，會和其他論文的 Moderate AP 混在一起，造成誤導。
  - **兩組 baseline**（83.83 vs 85.29）→ 依規則 B 改用同一張表（Table 7），**結論反轉**：NV3D 的 Car 精度略低於 Voxel R-CNN。
  - Q / K / V 分配在摘要和內文中矛盾 → wiki 不採用任何一種說法。
  - SECOND 的「R40」數字和 Voxel R-CNN Table 5 的 R11 數字完全相同 → 可能誤標，已註記。
  - 沒有速度、沒有 test。
- 觀察：這一篇最能說明**為什麼「比較」節點要放在「摘要」之前**。如果只照摘要寫，wiki 會寫成「NV3D 比 Voxel R-CNN 好 2.61%」；實際上同表比較的結果相反。規則 B（使用者在 Voxel R-CNN 那輪做的決定）在這裡發揮了關鍵作用。

## [2026-11-23] ingest | VoxelNeXt
- 第 0 步（表格檢查）：Table 10 的 ✓/✗ 在抽出的文字中遺失 → 轉成圖片讀取。另外確認**沒有 KITTI 結果**（只在附錄提到 KITTI）。
- 討論：提出 5 個重點、4 個新頁面；使用者決定 nuScenes 和 Argoverse2 **合併成一頁**（方案 A）。
- 新增：papers/voxelnext.md、concepts/{anchor-free-and-sparse-head, nuscenes-and-argoverse2}.md、comparisons/waymo-same-table.md
- 更新：sparse-convolution.md（fully sparse、voxel pruning）、anchor-and-box-encoding.md、waymo-open-dataset.md、speed-vs-accuracy.md（觀察 6：FLOPs ≠ 速度）、voxelization.md（輸入取樣 vs 網路剪枝）
- 檢查發現的問題：
  - 沒有 KITTI → 無法放進 KITTI 主表 → 依規則 B 新增 **Waymo 同表比較**（VoxelNeXt Table 15），讓 VoxelNeXt 能和 SECOND、PV-RCNN 放在同一張表比較。
  - ✅ 交叉驗證：Table 15 中 SECOND、PV-RCNN 的數字和 PV-RCNN 論文 Table 6 一致。
  - ⚠️ 同一篇論文中 CenterPoint 有四組數字；Table 2 和 Table 8 的 mAP 相同、NDS 不同（63.2 vs 63.5），論文沒有解釋。
  - ⚠️ 作者自述 FLOPs（1/5）和實際延遲（約少 1/3）差距大 → 寫進比較頁的觀察。
  - NDS 公式不在 raw 資料中 → 不憑記憶補公式，只列出 5 種誤差的名稱。

## [2026-11-23] ingest | LION
- 第 0 步（表格檢查）：表格是文字、數字齊全；KITTI 結果在附錄 Table 8，速度相關只有附錄 Table 12（FLOPs / Params）。
- 討論：提出 5 個重點和 6 項交叉檢查問題；使用者決定 Waymo 主表**改用 LION Table 1**（方案 A），VoxelNeXt Table 15 保留為第二張表。
- 新增：papers/lion.md、concepts/transformer-and-linear-rnn-backbone.md
- 更新：comparisons/waymo-same-table.md（換主表 + 兩表不一致的對照）、speed-vs-accuracy.md（觀察 7 + 兩條主軸總結表）、kitti-benchmark.md（注意事項 #10：表格標 val，內容是 test 數字）、waymo-open-dataset.md（LEVEL 定義的第三種說法、場景規格）、nuscenes-and-argoverse2.md（規格、26 類、ONCE 附錄）、voxelnext.md（後續）
- **發現自己的錯誤**：raw/SOURCES.md 把 LION 寫成「NeurIPS 2024」，是 setup 階段憑記憶填的，raw PDF 上是「Preprint. Under review.」。
  - 修正：更正 SOURCES.md，並**回頭查證所有 8 篇的發表資訊**，每一篇都在 raw 中找到證據（新增「發表資訊的查證」表）。
  - 教訓：「取得資料」節點填 metadata 時同樣不能憑記憶，要和其他數字一樣以 raw 為準。
- 其他檢查發現：
  - LION KITTI Table 8 標 val，但 SECOND、PointPillars、VoxelNet 的數字和各自原論文的 test R11 相同。
  - LION Table 1 和 VoxelNeXt Table 15：SECOND、PointPillars、VoxelNeXt 一致；PV-RCNN、PV-RCNN++、CenterPoint、FSD 不一致。
  - Waymo LEVEL 定義出現第三種說法。

## [2026-11-23] lint | 8 篇 ingest 完成後的全面檢查
- 工具：scratchpad/tools/lint.py（壞連結、錨點、孤兒頁、未列入 index、「有兩位小數但同一行沒有出處」的啟發式檢查）+ 人工檢查過時的「待 ingest / 待確認」標記。
- 結果：28 頁；**0 個壞連結、0 個壞錨點、0 個孤兒頁、全部頁面都已列入 index**。
- 修正：
  1. 沒有出處的數字 4 處 → 補上出處（anchor 門檻 SECOND §3.1.5、PV-RCNN / Voxel R-CNN 的 voxel 大小、PointPillars 格子大小 §4.2）。其餘被標記的行，出處都在小節標題或上一層條列，符合模板。
  2. kitti-benchmark.md 注意事項編號錯亂（#7 出現在 #10 之後）→ 重新排序。
  3. **15 個過時標記**（「待 ingest 確認」等）：早期 ingest 時留下的前向承諾 → 用後來 ingest 的論文逐一補上出處並解決 14 個。唯一保留的是 nuScenes mAP 的配對方式，raw 沒有資料，維持「待補」。
  4. NV3D 頁的「待查證」改寫為「推測，raw 無法證實」。
- 觀察：前向標記如果沒有定期 lint，會一直留在頁面上，和後來寫入的內容互相矛盾（例如 pointpillars.md 寫「待 ingest Voxel R-CNN 時確認」，但 Voxel R-CNN 頁早已寫入相關結論）。

## [2026-11-23] generate | 教學 HTML 簡報（slides/index.html）
- 討論：使用者同意照建議進行（約 20 頁、「讀論文注意事項」濃縮為 1 頁、2–3 個互動元素）。
- 流程：wiki → **事實清單**（slides/facts.md，51 條，每條標 wiki 頁 + 原始出處）→ 投影片（20 頁，3 個互動：格子大小示意、Voxel R-CNN 消融逐步展示、同表比較切換）。
- 檢查節點（slides/check_facts.py，兩段式）：
  1. 事實 ← wiki：每個數字必須出現在標示的 wiki 頁。
     - 第一次跑：**3 個錯誤**（F13、F21 標錯 wiki 頁：數字在論文頁，不在比較頁）→ 修正標示後 0 錯誤。
  2. 簡報 ← 事實：投影片中每個帶小數的數字（含 JS 資料區塊 /*fact*/）都必須在事實清單中；有數字的投影片必須有出處註記。
     - 第一次跑：6 個誤報（章節編號 §3.1 被當成數字）→ 改進 checker 後 0 錯誤。
- 視覺檢查（headless Edge 截圖 20 頁）：
  - 長條圖完全沒有填色：`<span>` 是行內元素，width 無效 → 加上 display:block。
  - JS 數字格式把 79.80 顯示成 79.8 → 依資料集設定小數位數。
  - kicker 的 text-transform:uppercase 把「arXiv」變成「ARXIV」→ 移除。
  - 導覽按鈕蓋住出處列 → 移到右上角。
  - 修正後重新截圖 20 頁確認，並再跑一次兩段式檢查：0 錯誤。
- 觀察：數字層面的錯誤都被 checker 擋下來了；這一輪新出現的錯誤集中在「呈現」（CSS / JS 格式），只有實際渲染並截圖才看得到。

## [2026-11-23] move | 簡報移到根目錄
- slides/index.html → index.html（GitHub Pages 無法從 slides/ 子目錄發布）。事實清單與 checker 仍在 slides/。
