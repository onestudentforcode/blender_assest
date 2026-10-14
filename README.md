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
| 扇叶灵树 | `_build_broadleaf.py` | `阔叶树_broadleaf_stage_{0..3}[_128].png` + 对照图 | 验证物种（无 P8 id），疙瘩干/卷尾枝/折叠扇叶 |
| 拼装验证 | `_build_map.py` | `灵田拼装_map.png` | 7×7 仓库土块网格 + 全资产摆位（评审 PASS） |

## 工具

- `_stage_driver.py`：通用阶段渲染驱动——不用可见性标志（远距平移隔离），
  每张图渲染后 alpha 非空断言 + 不透明包围盒校验（防空帧/防裁切）。
- `_mcp_autostart.py`：Blender 启动时自动启用 blender_mcp 插件。

## 统一规格

35° 俯角正交（`sensor_fit=HORIZONTAL`）、左上主光右下软影、底部中心锚点、
真 alpha 透明；树类 128×192 竖版语言（主图 1280×1920 = 10 倍）；建筑方形画布。
已知坑：竖版渲染必须显式 `sensor_fit`，否则 ortho_scale 映射到垂直维度导致取景错位。
