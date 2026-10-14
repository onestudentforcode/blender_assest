# 植物四阶段资产与母版

日期：2026-10-14。状态：**六种成熟体已由用户验收通过；stage_0～2已完成并通过阶段连续性、透明、留白和根点检查**。新版速生杉包含在本批四阶段中。

采用《灵田》原仓库的柔和体积、图形化仙侠生态风；造型依据工作区的《植物清单与建模提示词_v1》。
已验收松脂树作为参考。速生杉另做强化成熟候选，旧杉四阶段和松脂树原工程、主图均保留。

[成熟期对照图](成熟植物验收对照.png) · [整批可编辑工程](成熟植物整批母版.blend) · [对照工程](成熟植物验收对照.blend) · [机器检查记录](mature_qc.json)

[六物种四阶段总览](植物四阶段总览.png) · [全阶段总工程](植物全阶段总工程.blend) · [成长阶段检查](growth_qc.json) · [对照图检查](growth_contact_qc.json)

## 四阶段工程与对照

| 物种 | 四阶段对照 | 家族工程 | 生长变化 |
|---|---|---|---|
| 金穗麦 | [对照图](golden_wheat/contact.png) | [工程](golden_wheat/family.blend) | 短芽→少量叶秆→营养生长期分蘖→肥粒重穗；0～2不带麦穗 |
| 木腐菇 | [对照图](wood_decay_mushroom/contact.png) | [工程](wood_decay_mushroom/family.blend) | 菌丝结点→闭合菇蕾→三片初展耳盖→四片成熟厚褶耳盖 |
| 青牧草 | [对照图](pasture_grass/contact.png) | [工程](pasture_grass/family.blend) | 两片直立芽叶→少量束鞘分蘖→六分蘖窄折脊叶→九分蘖挺硬草丛 |
| 蜜铃灌木 | [对照图](honeybell_bush/contact.png) | [工程](honeybell_bush/family.blend) | 对生初叶→幼枝网→闭合花芽→中空下垂花囊与蜜滴 |
| 油籽花 | [对照图](oilseed_flower/contact.png) | [工程](oilseed_flower/family.blend) | 子叶→小铲叶→闭合花芽→成熟籽盘；另保留已审花期状态 |
| 新版速生杉 | [对照图](fast_fir/contact.png) | [工程](fast_fir/family.blend) | 针叶芽→一轮幼枝→三层枝轮→五层破裙针叶冠 |

各目录均含 `stage_0..3.blend`、`stage_0..3.png`；小作物为 `stage_0..3_64.png`，新版速生杉为 `stage_0..3_128.png`（128×192）。
`family.blend` 含四个独立阶段场景和并排场景；油籽花另含已审花期场景。松脂树已有四阶段仍见工作区根目录。
新增18个阶段、36张主图/小尺寸图。六份同尺度家族对照和总览均已检查，阶段独立场景根点为 `(0,0,0)`。
同物种阶段共享成熟体的相机、世界和灯光；早期图不会单独放大。对照场景只移动复制体，不修改单阶段根点。
总览对每个物种行使用一个展示缩放系数，行内四阶段比例不变；各家族 `contact.png` 保留真实世界尺度。
已审成熟文件通过 `approved_mature_hashes.json` 的24项SHA256比对，保持原文件不变。

对照图按展示框归一尺度，方便比较造型。它不是世界尺寸对比；物种工程保留1格=2单位的实际尺寸。

| 物种 | 成熟主体 | 主图 / 小尺寸 | 独立工程 | 识别重点 |
|---|---|---|---|---|
| 金穗麦 `golden_wheat` | 驼背算盘穗 | [主图](golden_wheat/stage_3.png) / [64²](golden_wheat/stage_3_64.png) | [Blender](golden_wheat/stage_3.blend) | 六根弯秆、错位双列肥粒、籽粒裂缝和长芒 |
| 木腐菇 `wood_decay_mushroom` | 烂耳叠菇 | [主图](wood_decay_mushroom/stage_3.png) / [64²](wood_decay_mushroom/stage_3_64.png) | [Blender](wood_decay_mushroom/stage_3.blend) | 四片偏生厚菌盖、前缘外翻、米白厚菌褶 |
| 青牧草 `pasture_grass` | 束鞘劲草 v2 | [主图](pasture_grass/stage_3.png) / [64²](pasture_grass/stage_3_64.png) | [Blender](pasture_grass/stage_3.blend) | 密集基部分蘖、短节间与包茎叶鞘、直立窄长V形折脊叶；抗倒伏的挺硬姿态 |
| 蜜铃灌木 `honeybell_bush` | 吊囊铃丛 | [主图](honeybell_bush/stage_3.png) / [64²](honeybell_bush/stage_3_64.png) | [Blender](honeybell_bush/stage_3.blend) | 可见枝网、成对厚叶、四只中空下垂花囊与附着蜜滴 |
| 油籽花 `oilseed_flower` | 偏头油碟花 | [成熟主图](oilseed_flower/stage_3.png) / [64²](oilseed_flower/stage_3_64.png) | [成熟工程](oilseed_flower/stage_3.blend) | 椭圆厚盘沿、肥厚油籽与中央沟、残留萎缩瓣、铲形叶 |
| 速生杉 `fast_fir` | 偏脊扫帚杉强化候选 | [主图](fast_fir/stage_3.png) / [128×192](fast_fir/stage_3_128.png) | [Blender](fast_fir/stage_3.blend) | 微弯脊干、五层轮生枝、下垂针叶束形成的破裙树冠 |

油籽花另附[花期图](oilseed_flower/flowering.png)、[花期64²图](oilseed_flower/flowering_64.png)、[花期工程](oilseed_flower/flowering.blend)。
这是成熟前花源器官的对照，不是 stage_0～2 交付。成熟籽盘与花期花簇由独立器官集合管理，保持同机位同根点。

## 本批检查结果

- 六个成熟工程与主图、小尺寸图齐全；小作物主图1280²，杉树1280×1920。
- 非空alpha、四角透明、四边留白与防裁切通过；倾斜根部下穿部分已修为接地截面。
- 各株根点均 `(0,0,0)`；所有镜头均35°俯角正交、HORIZONTAL，复制已审松脂树主光/补光/世界设置。
- 64²/128×192原尺寸视觉已检查。细麦芒、菌褶和种子沟依赖主图阅读，小尺寸保留穗/盖/卷叶/花囊/籽盘/层冠轮廓。
- 旧杉工程、已审松脂树成熟工程和主图与已提交版本哈希一致。
- 已完成四阶段的单株、实际尺寸及同族连续性检查；游戏场景接入另做。

## 建模与复现

共用套件：`../_plant_kit.py`。六物种器官生成器：`../_build_plants_mature.py`。
渲染与校验：`../_render_plants_mature.py`。验收场景：`../_plants_mature_review.py`。
杉树复用 `../_resin_needles.py` 的针叶结构，但拥有独立材质、枝条包络和成熟物种目录。

在 Blender 执行构建脚本（将 `__file__` 设为脚本绝对路径），然后执行渲染脚本，再执行验收场景脚本。
构建/渲染脚本支持 `ASSET_IDS` 指定物种；不传则生成全部六种成熟体。资产目录中的工程仅含该物种场景及依赖。
整批工程保留各物种独立场景和验收场景，当前默认显示验收场景。

其余成长阶段使用 `../_build_plant_stages.py`，渲染/校验使用 `../_render_plant_stages.py`；
家族并排场景使用 `../_plant_growth_review.py`，正式对照渲染使用 `../_render_growth_review.py`。
构建器只管理 `PG_` 数据，从已有成熟母版共享镜头和材料；不会覆盖成熟图或工程。
上述构建、渲染器支持 `ASSET_IDS`；构建器另支持 `STAGE_IDS`，默认0～2。
执行顺序：新增阶段构建→新增阶段渲染→家族对照构建→家族对照渲染。
全阶段总工程默认打开 `PC_AllGrowth` 总览，单株可通过场景切换选择 `PG_<id>_Stage0..2` 或 `PM_<id>_Stage3`。

## 配色与形态审查

本轮配色关系沿用提示词稿：灰橄榄麦叶与谷金穗、灰陶紫菌盖与米白褶、茶青窄草叶、蓝绿灌木叶与蜜桃花囊、橄榄铲叶与深棕油籽、深茶绿杉针叶。
材质为概括明暗与哑光组织，籽粒、花蜜允许少量油润高光；世界材质独立于UI色板。无大面积发光、脸谱和悬浮法阵。
各物种通过轮廓和核心生产器官区分，成熟母版现已由用户确认。

青牧草 v2 依据用户“更像草、强化抗倒伏”的反馈重做：原来的8片宽回卷叶改为9个紧密分蘖、18片向上窄叶和3片中心直立新叶。
纵向V形折脊、缩短叶片外展力臂、紧包茎秆的叶鞘和短节间共同表达韧性；叶尖不再绕回成卷。
成熟体相机与根点沿用上一版，整批工程与验收对照同步更新；用户后续已确认成熟体通过，再据此生成直立窄叶的其他阶段。
