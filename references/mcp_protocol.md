# HUSKYLENS 2 MCP 协议技术细节

## SSE连接

HUSKYLENS 2 MCP服务通过SSE (Server-Sent Events) + JSON-RPC 2.0协议通信。

**SSE端点：** `http://<device-ip>:3000/sse`
**消息端点：** `http://<device-ip>:3000/message?session_id=<session-id>`

**连接流程：**
1. `GET /sse` → 获取 `endpoint` 事件（含 `session_id`）
2. `POST /message?session_id=xxx` → 发送 JSON-RPC 请求
3. 响应通过 SSE 事件流返回（事件类型：`message`）

**关键限制：** SSE连接是临时的。连接断开后session立即失效，每次交互需重新建立SSE连接并保持长连接读取响应。

## MCP协议交互序列（必须按顺序执行）

```
Client                          Server
  |--- GET /sse ----------------->|
  |<-- event:endpoint ------------|
  |<-- event:heartbeat (0,1,2...)|
  |                               |
  |--- POST /message (initialize) ->|
  |<-- event:message (id=1, result: serverInfo) --|
  |                               |
  |--- POST /message (initialized notif) ->|
  |                               |
  |--- POST /message (tools/list) -->|
  |<-- event:message (id=2, result: tools[]) --|
  |                               |
  |--- POST /message (tools/call) -->|
  |<-- event:message (id=N, result: content[]) --|
```

**注意：** 每条POST的响应不立即返回，需通过SSE流接收。所有请求必须在此SSE连接内完成。

## 初始化参数

```json
{
  "jsonrpc": "2.0", "id": 1, "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "hl2-client", "version": "1.0"}
  }
}
```

**服务器响应：**
```json
{
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {}},
    "serverInfo": {"name": "Huskylens MCP Server", "version": "1.0.1"}
  }
}
```

## 工具详细说明（10个，已验证）

### 1. manage_applications
**operation值：** `application_list` | `current_application` | `switch_application`
**algorithm参数：** 仅 `switch_application` 时必需（算法英文名）

返回示例（application_list）：
```json
{
  "algorithms": [
    {"id": 1, "name_en": "Face Recognition", "name_cn": "人脸识别"},
    {"id": 2, "name_en": "Object Recognition", "name_cn": "物体识别"},
    ...
  ]
}
```

### 2. multimedia_control
**operation值：** `take_photo` | `take_screenshot` | `play_music` | `start_recording_audio` | `stop_recording_audio`
**resolution：** `1920x1080` | `1280x720` | `640x480`，仅take_photo有效

**返回示例（take_photo）：**
```json
{"cmd": "take_photo", "filename": "20260512_162011_1920x1080.jpg", "ret": "success"}
```

照片不会内嵌在响应中。下载方式：`http://<device-ip>/photo/`

### 3. get_recognition_result
**operation值：** `get_result`
**algorithm值：** 当前运行算法ID（数字，需先用current_application查询）

返回：
```json
{
  "content": [
    {"type": "resource_link", "mimeType": "image/jpeg", "uri": "http://192.168.88.1/photo/result.jpg"},
    {"type": "text", "text": "[{\"id\":1,\"name\":\"keyboard\",\"x\":320,\"y\":240,\"w\":100,\"h\":80}]"}
  ]
}
```

### 4. task_scheduler
**operation值：** 任务操作
**tasks参数：** 任务数组

### 5. learn_control
**operation值：** `learn` | `learn_block` | `forget` | `set_name_by_id`
**参数规则：** `learn`仅需algorithm；`learn_block`需algorithm+x+y+width+height；`set_name_by_id`需algorithm+id+name
**返回值：** id为0表示学习失败

### 6. knowledges_control
**operation值：** `save_knowledges` | `load_knowledges`
需algorithm+knowledges_id

### 7. algorithm_params_control
**operation值：** `get_algorithm_params` | `set_algorithm_params`
`set_algorithm_params`时params为JSON字符串数组：`[{"rec_thres": 0.2}]`

### 8. device_control
**operation值：** `set_backlight` | `get_backlight` | `set_system_volume` | `get_system_volume` | `set_flashlight` | `get_flashlight`
- backlight/volume/flashlight范围：0-100，volume仅支持步进10

### 9. draw_control
**operation值：** `draw_text` | `draw_rect` | `draw_unique_rect` | `clear_text` | `clear_rect`
- draw_text：`text, color, x, y, font_size`（font_size仅支持20/24/26/27/28/32/36/40/48）
- draw_rect/draw_unique_rect：`color, x, y, width, height, line_width`
- color格式：`#RRGGBB` 或 `#RRGGBBAA`（十六进制RGBA）

### 10. multi_algorithm_control
**operation值：** 多算法配置
**algorithms/ratios：** 算法ID数组和屏幕比例

## 终端调试

SSH连接：
```
ssh root@192.168.88.1
```

配置文件：
- `/mnt/udisk0/llm_agent.json` — 大模型API配置
- `/mnt/udisk0/huskylens_mcp_server.json` — MCP服务工具描述

启动MCP服务：
```bash
/opt/huskylens_mcp_server
```

检查运行状态：
```bash
ps -ef | grep mcp
```

## Python客户端实现参考

```python
import subprocess, json, re, time, base64, threading

def mcp_call(host, port, tool_name, args, timeout=30):
    """Execute a single MCP tool call."""
    sse_file = "_sse.txt"
    open(sse_file, 'wb').close()
    sse_proc = subprocess.Popen(
        ["curl.exe", "-s", "-N", "--max-time", f"{timeout+10}", f"http://{host}:{port}/sse"],
        stdout=open(sse_file, "wb"), stderr=subprocess.PIPE
    )
    time.sleep(2)
    with open(sse_file, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    m = re.search(r'session_id=(\S+)', text)
    if not m: return None
    sid = re.split(r'[\s&]', m.group(1))[0]
    msg_url = f"http://{host}:{port}/message?session_id={sid}"
    
    id_ctr = [0]
    def find_resp(tid, to):
        deadline = time.time() + to
        while time.time() < deadline:
            with open(sse_file, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
            for line in text.split('\n'):
                line = line.strip()
                if not line.startswith('data: ') or len(line) <= 8: continue
                payload = line[6:].strip()
                if not payload or payload.isdigit(): continue
                depth = 0
                for i, ch in enumerate(payload):
                    if ch == '{': depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            try:
                                obj = json.loads(payload[:i+1])
                                if isinstance(obj, dict) and obj.get('id') == tid:
                                    return obj
                            except: pass
                            break
            time.sleep(0.5)
        return None
    
    # Initialize
    id_ctr[0] = 1
    subprocess.run(["curl.exe", "-s", "-X", "POST", msg_url,
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize",
          "params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"hl2","version":"1.0"}}})],
        capture_output=True, timeout=15)
    time.sleep(1)
    subprocess.run(["curl.exe", "-s", "-X", "POST", msg_url,
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})],
        capture_output=True, timeout=15)
    time.sleep(0.5)
    
    # Call tool
    tid = 10
    subprocess.run(["curl.exe", "-s", "-X", "POST", msg_url,
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"jsonrpc":"2.0","id":tid,"method":"tools/call",
          "params":{"name":tool_name,"arguments":args}})],
        capture_output=True, timeout=15)
    
    resp = find_resp(tid, timeout)
    sse_proc.terminate()
    return resp
```