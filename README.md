# 灵田美术资产工作区（blender_assest）

《灵田》项目美术资产的程序化生成工作区：Blender 5.2 + MCP（OptiX 渲染），
每个资产 = 一个参数化构建脚本（固定随机种子，可复现）+ 渲染产出 + .blend 工程。

服务对象：`C:\Users\88445\Desktop\code\rpgmap`（P8 经营模块）。比例约定
**1 游戏格 = 2.0 Blender 单位**（与仓库耕地土块白模原生 2.0×2.0 一致）。

## 资产清单

| 素材 | 脚本 | 产出 | 说明 |
|---|---|---|---|
| 水井 | `_build_well.py` | `水井_water_well.png` | 建筑，2048² 透明，风格验证 PASS |
| 矿场 | `_build_mine.py` | `矿场_mine.png` | 建筑 |
| 伐木场 | `_build_lumber.py` | `伐木场_lumber_{front,left,right}.png` | 建筑，三角度 |
| 速生杉 | `_build_fir.py` | `速生杉_fir_stage_{0..3}[_128].png` + 对照图 | 作物（P8 id `fast_fir`），器官化：放样主干/轮生枝/针叶束/包络树冠 |
| 松脂树四阶段 | `_build_resin_tree.py` + `_build_resin_family.py` + `_resin_needles.py` | `松脂树_resin_tree.blend`、`松脂树_resin_tree_stage_{0..3}[_128].png`、`松脂树_resin_tree_contact.png` | 作物（P8 id `resin_tree`），针叶芽→弯干幼苗→初生腹瘤与三刷冠→成熟漏脂松；已审 stage_3 原工程与PNG保留 |
| 扇叶灵树 | `_build_broadleaf.py` | `阔叶树_broadleaf_stage_{0..3}[_128].png` + 对照图 | 验证物种（无 P8 id），疙瘩干/卷尾枝/折叠扇叶 |
| 拼装验证 | `_build_map.py` | `灵田拼装_map.png` | 7×7 仓库土块网格 + 全资产摆位（评审 PASS） |

## 工具

- `_stage_driver.py`：通用阶段渲染驱动——不用可见性标志（远距平移隔离），
  每张图渲染后 alpha 非空断言 + 不透明包围盒校验（防空帧/防裁切）。
- `_mcp_autostart.py`：Blender 启动时自动启用 blender_mcp 插件。
- `_render_resin_tree.py`：松脂树单阶段渲染与 alpha 非空、四角透明、四边留白校验，生成 `松脂树_resin_tree_stage_3_qc.json`。
- `_render_resin_family.py`：渲染 stage_0～2 和四阶段对照，验证非空alpha/透明四角/防裁切/高度递增/共同相机和根点投影；读取并核验已审 stage_3，不重渲染或覆盖成熟期文件。

## 统一规格

35° 俯角正交（`sensor_fit=HORIZONTAL`）、左上主光右下软影、底部中心锚点、
真 alpha 透明；树类 128×192 竖版语言（主图 1280×1920 = 10 倍）；建筑方形画布。
已知坑：竖版渲染必须显式 `sensor_fit`，否则 ortho_scale 映射到垂直维度导致取景错位。

松脂树本批世界包围盒约 3.21×1.30×3.56 单位，置于4×4的2×2玩法占地中；
根点 `(0,0,0)`。相机横宽3.60，角度和灯光沿用系列；主图1280×1920，
游戏尺寸预览128×192。`RT_BODY`、`RT_SCARS`、`RT_RESIN` 分组独立。
成熟母版复现：在 Blender 执行 `_build_resin_tree.py`，再执行 `_render_resin_tree.py`。
新增三阶段复现：执行 `_build_resin_family.py`，再执行 `_render_resin_family.py`；
family 构建脚本可从已审成熟工程加载母版。脚本的 `__file__` 需设为工作区对应脚本路径。
完整工程含 stage_0～2 的独立场景、已审成熟场景与 `RF_ResinTree_Contact` 并排场景。
单阶段根点均为 `(0,0,0)`，共享同一个 `RT_Camera_Stage` 与灯光；
128×192画布内根点投影为 `(64,176.711)`。只在对照场景中平移复制体。
四阶段实际株高约0.262/1.086/2.405/3.558单位；幼龄不带采脂伤口或脂滴。
完整验收记录为 `松脂树_resin_tree_family_qc.json`，完成单株/阶段视觉与alpha校验，游戏场景接入另做。
