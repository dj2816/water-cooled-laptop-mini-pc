# CAD 模型与生成脚本 [中文]

**语言 / Language: 中文（简体） | [English](README.en.md)**

本目录对应三块 363 × 244 × 3 mm 亚克力板，外角 R3 mm，每块加工 1 件。尺寸单位为 mm。脚本沿用原有目录名，`TopBottomPlateGenerator` 实际只生成内存侧板。

| 脚本目录 | 生成零件 | 默认开孔与缺口 |
| --- | --- | --- |
| `FusionScripts/TopBottomPlateGenerator` | `RAMSidePlate`（内存侧板） | 2 个 Ø55 通风圆孔、1 个 Ø30 操作孔、8 个 Ø3.2 M3 间隙孔 |
| `FusionScripts/SolidBackPlateGenerator` | `SolidBackPlate`（背板） | 12 个 Ø3.2 M3 间隙孔；上边缘 5 × 5 缺口，缺口右边距板右边 180 mm；无通风大孔 |
| `FusionScripts/ThirdPlateGenerator` | `ThirdPlate`（第三块板） | 仅 6 个 Ø3.2 M3 间隙孔；无大孔、无缺口 |

第三块板孔中心以成品板左上角为原点、向右与向下为正方向：`(95, 6)`、`(256, 6)`、`(12, 238)`、`(125, 238)`、`(238, 238)`、`(351, 238)`。它没有前两块板上的 `(21, 46)` 与 `(342, 46)` 两个孔。

## 打开现有模型

在 Autodesk Fusion 中使用“打开／从计算机打开”，选择本目录发布的 `.f3d` 文件；也可以通过数据面板上传 F3D 后打开。`.step` 用于跨 CAD 软件交换实体，`.dxf` 用于二维切割轮廓。导入加工软件后应核对单位为 mm、比例为 1:1，以及外形 363 × 244 mm。

## 用源脚本重新生成

需要 Autodesk Fusion 提供的 Python 环境与 `adsk.core`、`adsk.fusion` API。三个 `.manifest` 当前均声明 `supportedOS: windows`，本次保留原文件，没有验证 macOS 运行。其他导入均为 Python 标准库，无需额外 pip 包。普通 Python 解释器不能直接运行这些 Fusion 脚本。

1. 将整个项目放到可写的本地目录，完整保留 `CAD/FusionScripts` 下三个脚本目录及各自的 `.py`、`.manifest`，保持文件名和目录名一致。
2. 在 Fusion 的“脚本和附加模块 / Scripts and Add-Ins”中进入“脚本 / Scripts”页，通过添加或 `+` 选择其中一个脚本目录，例如 `TopBottomPlateGenerator`，不要只选择 `.py` 文件。
3. 选中对应脚本并运行。需要哪块板就运行哪一个；第三块板会自动读取相邻的 `SolidBackPlateGenerator/SolidBackPlateGenerator.py` 中的共用函数，不要求先运行背板脚本。
4. 成功后脚本会新建一个设计文档，显示生成结果与输出目录。三块板分别运行即可。

第三块板依赖相邻背板脚本，不能单独搬走它的目录。脚本按自身位置定位输出；保持仓库结构时，文件写入 `CAD/output/`，与启动 Fusion 时的工作目录无关。需要给该目录写入权限。

每块板生成以下文件，`<零件名>` 为上表中的 `RAMSidePlate`、`SolidBackPlate` 或 `ThirdPlate`：

- `<零件名>.f3d`：Fusion 文档。
- `<零件名>.step`：实体交换文件。
- `<零件名>_QTY1_1to1.dxf`：单件、1:1 切割草图。
- `<零件名>_preview.png`：Fusion 视图预览。
- `<零件名>_report.json`：参数与本次导出信息。

再次运行会覆盖 `CAD/output/` 中对应零件的同名导出文件。需要保留自定义版本时，先把输出复制到另一个版本目录。仓库的既有发布模型与本次生成输出应分别管理。

## 修改参数的实际行为

前两块板的主要初始尺寸位于各自 `.py` 文件顶部的 `DEFAULTS`。脚本会检查当前活动设计：只有找到同名组件 `RAMSidePlate` 或 `SolidBackPlate` 时，才读取该设计里与 `DEFAULTS` 同名的用户参数；否则使用默认值。读取后重新建模到新文档。

当前版本有一些固定修订值，即使在 Fusion 参数表中修改，重新运行仍会恢复到源码 `DEFAULTS`：

- 两块板共有：`acrylicThickness`、`newTopHoleOffsetTop`、`newTopHole1OffsetLeft`、`newTopHole2OffsetRight`、`bottomMountOffsetLeft`、`bottomMountOffsetRight`、`bottomMountOffsetBottom`。
- 内存侧板另有：`accessHoleDiameter`、`accessHoleOffsetLeft`、`accessHoleOffsetBottom`。
- 背板另有：`topNotchWidth`、`topNotchDepth`、`topNotchRightEdgeOffsetRight`。

若要改变上述固定值，需修改源码 `DEFAULTS` 后重跑。修改其他默认值时，可以从空白设计启动以避免读取旧模型参数。`plateLength`、`plateWidth` 是由主板长宽、装配间隙和预留侧壁厚度推导的值；直接改这两个派生参数不会成为重跑输入。轮廓是脚本按数值绘制的，不能假定编辑任意 Fusion 用户参数就能自动更新所有草图孔位；修改后应重新运行并检查新输出。

第三块板使用源码常量 `PLATE_LENGTH`、`PLATE_WIDTH`、`PLATE_THICKNESS`、`CORNER_RADIUS`、`MOUNT_HOLE_DIAMETER` 和固定列表 `HOLE_CENTERS_FROM_TOP_LEFT`。它不读取当前设计的用户参数。改变板尺寸不会自动重新计算六个孔的位置，需要同时修改孔中心列表；源码中 `_add_user_parameters` 的孔位说明值与报告里的固定说明也需要同步核对。不要把参数表中可见的孔位名称理解为已建立完整联动约束。

`cutQuantity` 用于前两块板的参数与报告；脚本仍生成一个实体，DXF 文件名固定为 `QTY1`，不会自动排版多件。修改默认厚度后，部分实体名和提示文字也仍含 `3mm`，应以实际几何和报告数值核对。

## 本地理论几何检查

`tools/validate_geometry.py` 使用 Python 3.8 或更新版本及标准库，可以脱离 Fusion 运行。在仓库根目录执行：

```shell
python CAD/tools/validate_geometry.py
```

它根据脚本自身写死的尺寸与孔位计算边距、圆孔间距和部分缺口间距，输出到 `CAD/output/`：

- `RAMSidePlate_local_preview.svg`
- `SolidBackPlate_local_preview.svg`
- `ThirdPlate_local_preview.svg`
- `RevisedPlates_local_validation.json`

该工具不会读取、解析或验证 F3D、STEP、DXF 实体，也不会自动读取三个 Fusion 生成脚本的参数。改变设计后必须同步更新它的常量。报告中的 `bounds_ok` 与 `no_circular_cutout_intersections` 仅表示所实现的理论检查结果；进程正常退出本身不等于检查通过，还需查看这两个值。边界检查按外接矩形计算，并非完整圆角边界、实体拓扑、装配干涉或加工可行性检查。
