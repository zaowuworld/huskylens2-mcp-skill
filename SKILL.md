---
name: huskylens2-mcp
description: |
  DFRobot HUSKYLENS 2 (二哈识图2) AI视觉传感器的MCP服务调用技能。通过SSE协议连接HUSKYLENS 2内置MCP服务，实现AI视觉识别、拍照、算法切换和条件任务调度。当用户提到"二哈识图"、"HUSKYLENS"、"huskylens"、"AI视觉传感器"、"视觉识别"、"HUSKYLENS MCP"时触发。支持操作：查看/切换AI算法、拍照/截图/录音、获取识别结果、学习/遗忘目标、屏幕绘图、设备控制、条件触发任务等10种工具。需确保HUSKYLENS 2已开启MCP服务且与运行环境在同一WiFi网络。
---

# HUSKYLENS 2 MCP 技能

通过MCP协议连接DFRobot HUSKYLENS 2 (二哈识图2) AI视觉传感器，实现远程视觉识别控制。

## 前提条件

- HUSKYLENS 2 系统版本 >= V1.1.6
- WiFi配件已插入并连接网络
- MCP服务已开启（屏幕 -> MCP服务 -> 打开开关）
- 运行环境与HUSKYLENS 2在同一WiFi网络

## 连接配置

HUSKYLENS 2开启MCP后屏幕显示SSE地址，格式：`http://<device-ip>:3000/sse`

默认地址：`http://192.168.88.1:3000/sse`（设备AP模式）或WiFi分配的IP地址。

在OpenClaw中配置MCP服务：将SSE地址添加为MCP Server端点。

## MCP工具说明（10个工具）

### 1. manage_applications - 算法管理

管理HUSKYLENS 2当前运行的AI模型/算法。

**参数：**
- `operation`（必需）：`application_list` | `current_application` | `switch_application`
- `algorithm`（switch_application时必需）：算法英文名称，如 "Face Recognition"

**支持的对话指令：**
- "当前有哪些模型/算法" → application_list
- "切换到物体追踪" → switch_application（支持模糊匹配，如"人脸检测"会自动匹配"Face Recognition"）
- "当前运行的是什么算法" → current_application

**内置算法（已验证）：**

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
| 9+ | ... | 手掌检测、人体检测、姿态识别、车牌识别、OCR、巡线、表情识别、注视方向、人脸朝向、标签识别、二维码/条形码、跌倒检测等 |

### 2. multimedia_control - 多媒体控制

控制摄像头拍照、截图、音乐播放和录音。

**参数：**
- `operation`（必需）：`take_photo` | `take_screenshot` | `play_music` | `start_recording_audio` | `stop_recording_audio`
- `resolution`（仅take_photo）：`1920x1080` | `1280x720` | `640x480`，默认1280x720
- `filename`（play_music/start_recording_audio必需）：文件名
- `volume`（play_music可选）：音量
- `duration`（start_recording_audio可选）：录音时长

**支持的对话指令：**
- "拍照" → take_photo
- "高清拍照" → take_photo + resolution=1920x1080
- "截屏" → take_screenshot
- "录音" → start_recording_audio

**拍照返回格式：**
```json
{"cmd": "take_photo", "filename": "20260512_162011_1920x1080.jpg", "ret": "success"}
```
照片存储在设备 `/photo/` 路径下，可通过 `http://<device-ip>/photo/<filename>` 下载。

### 3. get_recognition_result - 获取识别结果

获取当前视觉识别结果，包括带标注的图像和识别标签。

**参数：**
- `operation`（必需）：`get_result`
- `algorithm`（必需）：当前运行的算法ID（数字）

**返回内容：**
- `resource_link`：带标注框的结果图像URL（mimeType: image/jpeg）
- `text`：识别结果JSON数组（包含目标ID、名称、位置坐标、置信度等）

**图像URL格式：** `http://192.168.88.1/photo/<filename>`（需替换为设备实际IP下载）

**支持的对话指令：**
- "你看到了什么" → get_result
- "告诉我键盘的位置" → get_result

### 4. task_scheduler - 任务调度

设置条件触发的自动任务。目标出现后执行一次，消失后重新出现才会再次执行。

**参数：**
- `operation`（必需）：任务操作类型
- `tasks`（必需）：任务定义数组

**支持的对话指令：**
- "当看到键盘时拍照" — 设置条件触发拍照任务

### 5. learn_control - 学习/遗忘控制

控制对屏幕上目标的学习和遗忘操作。

**参数：**
- `operation`（必需）：`learn` | `learn_block` | `forget` | `set_name_by_id`
- `algorithm`（必需）：算法ID
- `x, y, width, height`（仅learn_block必需）：区域坐标
- `id`（set_name_by_id必需）：目标ID
- `name`（set_name_by_id必需）：目标名称

**说明：** learn返回的id为0表示学习失败，否则为学习到的目标ID。

### 6. knowledges_control - 知识库管理

保存和加载已学习的模型数据。

**参数：**
- `operation`（必需）：`save_knowledges` | `load_knowledges`
- `algorithm`（必需）：算法ID
- `knowledges_id`（必需）：知识库槽位ID

### 7. algorithm_params_control - 算法参数控制

获取和设置算法的运行参数（检测阈值、识别阈值、NMS阈值等）。

**参数：**
- `operation`（必需）：`get_algorithm_params` | `set_algorithm_params`
- `algorithm`（必需）：算法ID
- `params`（仅set_algorithm_params必需）：JSON字符串，如 `[{"show_name": true}, {"rec_thres": 0.2}]`

### 8. device_control - 设备控制

控制设备级设置：背光、音量、闪光灯。

**参数：**
- `operation`（必需）：`set_backlight` | `get_backlight` | `set_system_volume` | `get_system_volume` | `set_flashlight` | `get_flashlight`
- `backlight`（0-100）、`volume`（0-100，步进10）、`flashlight`（0-100）

### 9. draw_control - 屏幕绘图

在设备屏幕上绘制文字、矩形，或清除绘制内容。

**参数：**
- `operation`（必需）：`draw_text` | `draw_rect` | `draw_unique_rect` | `clear_text` | `clear_rect`
- `text, color, x, y, font_size`（draw_text必需）
- `color, x, y, width, height, line_width`（draw_rect/draw_unique_rect必需）
- color格式：RGBA uint32十六进制，如 `#00FF00` 或 `#FF00FF80`

### 10. multi_algorithm_control - 多算法配置

配置屏幕上同时显示的多个算法。

**参数：**
- `operation`（必需）：操作类型
- `algorithms`：算法ID数组
- `ratios`：屏幕比例分配

## 使用流程

1. **确认连接**：确保HUSKYLENS 2 MCP服务开启，获取SSE地址
2. **配置OpenClaw**：将SSE地址添加为MCP Server
3. **自然语言交互**：通过对话使用上述工具
4. **获取结果**：识别结果、照片等通过MCP返回

## 算法切换示例

| 用户意图 | 推荐算法ID | 英文名 |
|---------|-----------|--------|
| 识别通用物体 | 2 | Object Recognition |
| 识别人脸/区分不同人 | 1 | Face Recognition |
| 追踪移动物体 | 3 | Object Tracking |
| 区分颜色 | 4 | Color Recognition |
| 自定义分类 | 6 | Self-Learning Classifier |
| 识别手势 | 8 | Hand Recognition |
| 实例分割 | 7 | Instance Segmentation |
| 识别车牌 | 16 | License Plate Recognition |
| 文字识别 | 17 | OCR |
| 巡线 | 18 | Line Tracking |

## 故障排查

- **连接失败**：检查WiFi连接、IP地址、MCP服务开关
- **Session not found**：SSE连接断开后session失效，需重新建立连接
- **拍照无图像**：照片不会内嵌在MCP响应中，需通过HTTP下载 `http://<ip>/photo/<filename>`
- **识别结果为null/空**：算法ID可能不匹配，先用 current_application 查询当前算法
- **SSH调试**：`ssh root@192.168.88.1`，配置文件 `llm_agent.json` 和 `huskylens_mcp_server.json`

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
