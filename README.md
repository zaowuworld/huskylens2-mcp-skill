# HUSKYLENS 2 MCP Skill

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/zaowuworld/huskylens2-mcp-skill)

DFRobot HUSKYLENS 2 (二哈识图2) AI视觉传感器的MCP服务调用技能。通过SSE协议连接HUSKYLENS 2内置MCP服务，实现AI视觉识别、拍照、算法切换和条件任务调度。

## 功能特性

- 🔍 **算法管理** — 查看/切换20+种AI算法（人脸识别、物体追踪、OCR等）
- 📸 **多媒体控制** — 拍照/截图/录音，支持1920x1080高清
- 🎯 **识别结果获取** — 获取带标注框的识别图像和JSON结果
- 🧠 **学习控制** — 学习/遗忘目标、设置目标名称
- 🔧 **设备控制** — 背光/音量/闪光灯调节
- 📝 **屏幕绘图** — 在设备屏幕上绘制文字和矩形框
- ⚡ **条件任务调度** — 设置"当看到X时拍照"等条件触发任务

## 前提条件

- HUSKYLENS 2 系统版本 >= V1.1.6
- WiFi配件已插入并连接网络
- MCP服务已开启（屏幕 → MCP服务 → 打开开关）
- 运行环境与HUSKYLENS 2在同一WiFi网络

## 快速开始

### 1. 在OpenClaw中安装

```bash
skillhub install huskylens2-mcp
```

> 如果从GitHub安装：将本仓库内容复制到 `~/.qclaw/skills/huskylens2-mcp/`，然后重启OpenClaw。

### 2. 获取MCP服务地址

HUSKYLENS 2开启MCP后，屏幕会显示SSE地址，格式：
```
http://<device-ip>:3000/sse
```

默认AP模式地址：`http://192.168.88.1:3000/sse`
WiFi网络地址：`http://192.168.x.x:3000/sse`（在屏幕查看）

### 3. 配置到OpenClaw

将SSE地址添加为OpenClaw的MCP Server端点（具体配置方式参见OpenClaw文档）。

### 4. 开始使用

直接用自然语言与HUSKYLENS 2交互：

- "当前有哪些算法"
- "切换到物体识别"
- "拍一张高清照片"
- "你看到了什么"
- "告诉我键盘的位置"
- "当看到键盘时拍照"

## MCP工具说明（10个工具）

| 工具 | 功能 | 关键参数 |
|------|------|---------|
| `manage_applications` | 查看/切换AI算法 | operation, algorithm |
| `multimedia_control` | 拍照/截图/录音 | operation, resolution |
| `get_recognition_result` | 获取识别结果 | operation, algorithm |
| `task_scheduler` | 条件触发任务 | operation, tasks |
| `learn_control` | 学习/遗忘目标 | operation, algorithm, id |
| `knowledges_control` | 保存/加载知识库 | operation, algorithm, knowledges_id |
| `algorithm_params_control` | 算法参数设置 | operation, algorithm, params |
| `device_control` | 背光/音量/闪光灯 | operation, backlight/volume/flashlight |
| `draw_control` | 屏幕绘图 | operation, text/color/x/y |
| `multi_algorithm_control` | 多算法配置 | operation, algorithms |

## 支持的AI算法（部分）

| ID | 英文名 | 中文名 |
|----|--------|--------|
| 1 | Face Recognition | 人脸识别 |
| 2 | Object Recognition | 物体识别 |
| 3 | Object Tracking | 物体追踪 |
| 4 | Color Recognition | 颜色识别 |
| 5 | Object Classification | 物体分类 |
| 6 | Self-Learning Classifier | 自学习分类 |
| 7 | Instance Segmentation | 实例分割 |
| 8 | Hand Recognition | 手势识别 |
| 16 | License Plate Recognition | 车牌识别 |
| 17 | OCR | 文字识别 |
| 18 | Line Tracking | 巡线追踪 |

完整列表通过 `manage_applications` 工具的 `application_list` 操作获取。

## 项目结构

```
huskylens2-mcp/
├── SKILL.md                          # 技能定义文件（OpenClaw加载）
├── README.md                         # 本文件
├── LICENSE                           # MIT许可证
├── references/
│   ├── mcp_protocol.md               # MCP SSE协议技术细节（已验证）
│   └── hardware_guide.md             # 硬件接口和参数说明
└── scripts/
    ├── huskylens2_client.py          # Python MCP客户端（独立使用）
    └── test_connection.py            # 连通性测试脚本
```

## 独立使用（不依赖OpenClaw）

### 测试连接

```bash
python scripts/test_connection.py --host 192.168.1.111
```

### 交互式客户端

```bash
# 列出算法
python scripts/huskylens2_client.py --host 192.168.1.111 list-algorithms

# 拍照（高清）
python scripts/huskylens2_client.py --host 192.168.1.111 take-photo 1920x1080

# 获取识别结果
python scripts/huskylens2_client.py --host 192.168.1.111 recognize 2

# 交互模式
python scripts/huskylens2_client.py --host 192.168.1.111 interactive
```

## 拍照与照片下载

`multimedia_control` 的 `take_photo` 操作支持三种分辨率：
- `1920x1080` — 高清（约94KB）
- `1280x720` — 标清（约40KB）
- `640x480` — 低清（约18KB）

拍照成功后返回：
```json
{"cmd": "take_photo", "filename": "20260512_162011_1920x1080.jpg", "ret": "success"}
```

照片通过HTTP下载：
```
http://<device-ip>/photo/<filename>
```

## 技术规格

| 参数 | 规格 |
|------|------|
| 处理器 | Kendryte K230 双核 1.6GHz |
| AI算力 | 6 TOPS |
| 内存 | 1GB LPDDR4 |
| 存储 | 8GB EMMC |
| 屏幕 | 2.4寸 640x480 IPS触摸 |
| 摄像头 | GC2093 200W像素 60FPS |
| WiFi | AIC8800D40L 2.4GHz |
| 接口 | Type-C x1, 4Pin Gravity x1, TF卡槽 x1 |

## MCP协议要点

HUSKYLENS 2 MCP服务使用 **SSE + JSON-RPC 2.0** 协议：

1. `GET /sse` 建立SSE长连接，获取 `session_id`
2. `POST /message?session_id=xxx` 发送JSON-RPC请求
3. 响应通过SSE事件流返回（`event: message`）
4. **SSE连接断开后session立即失效**，需重新建立

详细协议说明见 `references/mcp_protocol.md`。

## 故障排查

- **连接失败**：检查WiFi连接、IP地址、MCP服务开关
- **Session not found**：SSE连接断开，需重新建立
- **拍照无图像**：照片不会内嵌在MCP响应中，需通过 `http://<ip>/photo/<filename>` 下载
- **识别结果为null**：算法ID可能不匹配，先用 `current_application` 查询当前算法
- **SSH调试**：`ssh root@<device-ip>`，配置文件在 `/mnt/udisk0/`

## 相关链接

- [HUSKYLENS 2 官方文档](https://wiki.dfrobot.com.cn/_SKU_SEN0638_Gravity_HUSKYLENS_2_AI_Camera_Vision_Sensor)
- [MCP协议规范](https://spec.modelcontextprotocol.io/)
- [OpenClaw](https://github.com/openclaw/openclaw)

## 许可证

MIT License

## 致谢

- [DFRobot](https://www.dfrobot.com/) — HUSKYLENS 2 硬件及MCP服务
- [OpenClaw](https://github.com/openclaw/openclaw) — 技能框架
