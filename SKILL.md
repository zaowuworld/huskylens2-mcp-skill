---
name: huskylens2-mcp
description: |
  DFRobot HUSKYLENS 2 (二哈识图2) AI视觉传感器的MCP服务调用技能。通过SSE协议连接HUSKYLENS 2内置MCP服务，实现AI视觉识别、拍照、算法切换和条件任务调度。当用户提到"二哈识图"、"HUSKYLENS"、"huskylens"、"AI视觉传感器"、"视觉识别"、"HUSKYLENS MCP"时触发。支持操作：查看/切换AI算法、拍照、获取识别结果、设置条件触发拍照任务。需确保HUSKYLENS 2已开启MCP服务且与运行环境在同一WiFi网络。
---

# HUSKYLENS 2 MCP 技能

通过MCP协议连接DFRobot HUSKYLENS 2 (二哈识图2) AI视觉传感器，实现远程视觉识别控制。

## 前提条件

- HUSKYLENS 2 系统版本 >= V1.1.6
- WiFi配件已插入并连接网络
- MCP服务已开启（屏幕 -> MCP服务 -> 打开开关）
- 运行环境与HUSKYLENS 2在同一WiFi网络

## 连接配置

HUSKYLENS 2开启MCP后屏幕显示SSE地址，格式：`http://192.168.xx.xx:3000/sse`

默认地址：`http://192.168.88.1:3000/sse`（设备AP模式）或WiFi分配的IP地址。

在OpenClaw中配置MCP服务：将SSE地址添加为MCP Server端点。

## MCP工具说明

HUSKYLENS 2 MCP服务提供4个工具：

### 1. manage_applications - 算法管理

管理HUSKYLENS 2当前运行的AI模型/算法。

**支持的对话指令：**
- "当前有哪些模型/算法" — 列出所有可用算法
- "切换到物体追踪算法" — 切换算法（支持模糊识别，如"人脸检测"会自动匹配到"人脸识别"）
- "当前运行的是什么算法" — 查询当前算法

**内置算法列表：**
人脸检测、人脸识别、人脸五官检测、物体识别、物体追踪、颜色识别、物体分类、自学习分类、实例分割、手掌检测、手掌关键点检测、手势识别、人体检测、人体关键点检测、姿态识别、车牌识别、文字识别(OCR)、巡线追踪、表情识别、注视方向检测、人脸朝向检测、标签识别、二维码识别、条形码识别、跌倒检测

### 2. multimedia_control - 多媒体控制

控制摄像头拍照等操作。

**支持的对话指令：**
- "拍照" — 拍摄当前画面

### 3. get_recognition_result - 获取识别结果

获取当前视觉识别结果，包括检测到的物体、位置、置信度等信息。

**支持的对话指令：**
- "你看到了什么" — 获取当前识别结果
- "告诉我键盘的位置" — 查询特定物体的位置

### 4. task_scheduler - 任务调度

设置条件触发的自动任务。目标出现后执行一次，消失后重新出现才会再次执行。

**支持的对话指令：**
- "当看到键盘时拍照" — 设置条件触发拍照任务
- 拍摄的照片存储在U盘系统的photo文件夹中

## 使用流程

1. **确认连接**：确保HUSKYLENS 2 MCP服务开启，获取SSE地址
2. **配置OpenClaw**：将SSE地址添加为MCP Server
3. **自然语言交互**：通过对话使用上述4个工具
4. **获取结果**：识别结果、照片等通过MCP返回

## 算法切换示例

| 用户意图 | 推荐算法 |
|---------|---------|
| 识别通用物体 | 物体识别 |
| 识别人脸/区分不同人 | 人脸识别 |
| 追踪移动物体 | 物体追踪 |
| 区分颜色 | 颜色识别 |
| 自定义分类 | 自学习分类 |
| 识别手势 | 手势识别 |
| 识别人体姿态 | 姿态识别 |
| 识别车牌 | 车牌识别 |
| 文字识别 | 文字识别 |
| 巡线 | 巡线追踪 |

## 故障排查

- **连接失败**：检查WiFi连接、IP地址、MCP服务开关
- **工具未显示**：重启HUSKYLENS 2和客户端，确认同一网络
- **识别无结果**：调整检测阈值，确保光线充足，检查算法是否正确
- **SSH调试**：`ssh root@192.168.88.1`，配置文件在`llm_agent.json`和`huskylens_mcp_server.json`

## 技术规格参考

- 处理器：Kendryte K230 双核 1.6GHz
- 算力：6 TOPS
- 内存：1GB LPDDR4
- 存储：8GB EMMC
- 屏幕：2.4寸 640x480 IPS电容触摸
- 摄像头：GC2093 200W像素 60FPS
- WiFi：AIC8800D40L 2.4GHz
- 接口：Type-C x1, 4Pin Gravity x1, TF卡槽 x1

## Resources

### references/
- `mcp_protocol.md` — MCP SSE协议连接和工具调用技术细节
- `hardware_guide.md` — 硬件接口、接线、参数设置详细说明

### scripts/
- `test_connection.py` — 测试HUSKYLENS 2 MCP服务连通性
- `huskylens2_client.py` — Python客户端，直接调用MCP工具（不依赖OpenClaw）
