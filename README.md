# HUSKYLENS 2 MCP Skill

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/zaowuworld/huskylens2-mcp-skill)

DFRobot HUSKYLENS 2 (二哈识图2) AI视觉传感器的MCP服务调用技能。通过SSE协议连接HUSKYLENS 2内置MCP服务，实现AI视觉识别、拍照、算法切换和条件任务调度。

## 功能特性

- 🔍 **算法管理** — 查看/切换20+种AI算法（人脸识别、物体追踪、OCR等）
- 📸 **远程拍照** — 通过MCP协议远程控制摄像头拍照
- 🎯 **识别结果获取** — 获取当前视觉识别结果（物体、位置、置信度）
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

### 2. 配置MCP服务地址

HUSKYLENS 2开启MCP后屏幕显示SSE地址，将地址添加为OpenClaw的MCP Server端点：

```
http://192.168.xx.xx:3000/sse
```

默认AP模式地址：`http://192.168.88.1:3000/sse`

### 3. 开始使用

直接用自然语言与HUSKYLENS 2交互：

- "当前有哪些算法"
- "切换到物体追踪"
- "拍照"
- "你看到了什么"
- "告诉我键盘的位置"
- "当看到键盘时拍照"

## MCP工具说明

| 工具 | 功能 | 示例指令 |
|------|------|---------|
| manage_applications | 查看/切换AI算法 | "切换到人脸识别" |
| multimedia_control | 拍照 | "拍照" |
| get_recognition_result | 获取识别结果 | "你看到了什么" |
| task_scheduler | 条件触发任务 | "当看到键盘时拍照" |

## 支持的AI算法

人脸检测、人脸识别、人脸五官检测、物体识别、物体追踪、颜色识别、物体分类、自学习分类、实例分割、手掌检测、手掌关键点检测、手势识别、人体检测、人体关键点检测、姿态识别、车牌识别、文字识别(OCR)、巡线追踪、表情识别、注视方向检测、人脸朝向检测、标签识别、二维码识别、条形码识别、跌倒检测

## 项目结构

```
huskylens2-mcp/
├── SKILL.md                          # 技能定义文件
├── README.md                         # 本文件
├── LICENSE                           # MIT许可证
├── references/
│   ├── mcp_protocol.md               # MCP SSE协议技术细节
│   └── hardware_guide.md             # 硬件接口和参数说明
└── scripts/
    ├── huskylens2_client.py          # Python MCP客户端
    └── test_connection.py            # 连通性测试脚本
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

## 故障排查

- **连接失败**：检查WiFi连接、IP地址、MCP服务开关
- **工具未显示**：重启HUSKYLENS 2和客户端
- **识别无结果**：调整检测阈值，确保光线充足
- **SSH调试**：`ssh root@192.168.88.1`，配置文件在`llm_agent.json`和`huskylens_mcp_server.json`

## 相关链接

- [DFRobot HUSKYLENS 2 官方文档](https://wiki.dfrobot.com.cn/_SKU_SEN0638_Gravity_HUSKYLENS_2_AI_Camera_Vision_Sensor)
- [MCP协议规范](https://spec.modelcontextprotocol.io/)

## 许可证

MIT License

## 致谢

- [DFRobot](https://www.dfrobot.com/) — HUSKYLENS 2 硬件及MCP服务
- [OpenClaw](https://github.com/zaowuworld) — 技能框架
