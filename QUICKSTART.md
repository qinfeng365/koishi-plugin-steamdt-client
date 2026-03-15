# SteamDT Koishi 客户端 - 快速开始指南

## 5分钟快速开始

### 第一步：准备环境

确保已安装：
- Node.js 16+ 
- npm 或 yarn
- Koishi 4.0+

### 第二步：安装插件

```bash
# 1. 进入项目目录
cd /path/to/defend

# 2. 安装依赖
npm install

# 3. 编译TypeScript
npm run build
```

### 第三步：配置Koishi

复制示例配置文件：
```bash
cp koishi.yml.example koishi.yml
```

编辑 `koishi.yml`，确保API地址正确：
```yaml
plugins:
  steamdt-client:
    apiUrl: http://127.0.0.1:1145
    timeout: 30000
```

### 第四步：启动服务

1. 启动SteamDT API服务（在另一个终端）：
```bash
python api_server.py 1145
```

2. 启动Koishi机器人：
```bash
koishi start
```

### 第五步：使用指令

在Koishi中使用以下指令：

```
# 查看健康状态
/health

# 添加爬取任务（10次滚动，优先级5）
/scrape 10 5

# 查看队��状态
/queue

# 查看任务结果（任务0）
/task 0

# 获取任务图片
/image 0

# 显示帮助
/steamdt help
```

## 常见问题

### Q: 连接被拒绝？
A: 确保API服务已启动在正确的端口（默认1145）

```bash
# 检查服务是否运行
curl http://127.0.0.1:1145/health
```

### Q: 超时错误？
A: 增加超时时间，编辑 `koishi.yml`：
```yaml
plugins:
  steamdt-client:
    timeout: 60000  # 改为60秒
```

### Q: 如何修改API地址？
A: 编辑 `koishi.yml` 中的 `apiUrl`：
```yaml
plugins:
  steamdt-client:
    apiUrl: http://your-server:1145
```

### Q: 如何查看日志？
A: 在Koishi控制台中查看，标签为 `steamdt-client`

## 指令速查表

| 指令 | 说明 | 示例 |
|------|------|------|
| `/scrape [scrolls] [priority]` | 添加任务 | `/scrape 10 5` |
| `/queue` | 查看队列 | `/queue` |
| `/task <index>` | 查看任务 | `/task 0` |
| `/image <index>` | 获取图片 | `/image 0` |
| `/health` | 健康检查 | `/health` |
| `/steamdt help` | 帮助信息 | `/steamdt help` |

## 开发模式

监视文件变化并自动编译：
```bash
npm run dev
```

## 项目文件说明

```
defend/
├── koishi_client.ts           # 主插件源代码
├── package.json               # 项目配置和依赖
├── tsconfig.json              # TypeScript编译配置
├── koishi.yml.example         # Koishi配置示例
├── KOISHI_CLIENT_README.md    # 详细文档
├── QUICKSTART.md              # 本文件
├── dist/                      # 编译输出（自动生成）
│   ├── index.js
│   ├── index.d.ts
│   └── index.js.map
└── api_server.py              # SteamDT API服务（Python）
```

## 工作流程

```
用户输入指令
    ↓
Koishi客户端解析
    ↓
调用对应的API端点
    ↓
API服务处理请求
    ↓
返回结果给用户
```

## 任务队列工作原理

```
添加任务 (/scrape)
    ↓
任务进入队列
    ↓
按优先级排序
    ↓
后台线程处理
    ↓
爬虫运行
    ↓
生成表格图片
    ↓
任务完成 (/task 查看结果)
```

## 性能建议

1. **合理设置滚动次数**：
   - 5-10次：快速爬取，数据量小
   - 20-30次：平衡速度和数据量
   - 50+次：完整数据，耗时较长

2. **使用优先级**：
   - 0-3：低优先级，后台任务
   - 4-7：中优先级，普通任务
   - 8-10：高优先级，紧急任务

3. **监控队列**：
   定期使用 `/queue` 检查队列状态，避免堆积

## 故障排查

### 检查清单

- [ ] API服务是否运行？ `curl http://127.0.0.1:1145/health`
- [ ] Koishi是否启动？ 检查控制台输出
- [ ] 网络连接是否正常？ 检查防火墙
- [ ] 配置文件是否正确？ 检查 `koishi.yml`
- [ ] 依赖是否安装？ 运行 `npm install`
- [ ] TypeScript是否编译？ 运行 `npm run build`

### 获取帮助

查看详细文档：
```bash
cat KOISHI_CLIENT_README.md
```

查看API文档：
```bash
cat API_DOCS.md
```

## 下一步

- 阅读 [详细文档](KOISHI_CLIENT_README.md)
- 查看 [API文档](API_DOCS.md)
- 探索 [源代码](koishi_client.ts)
- 加入社区讨论

祝你使用愉快！🚀
