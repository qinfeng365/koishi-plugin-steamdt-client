# SteamDT Koishi 客户端 - 文档索引

## 📚 文档导航

### 🚀 快速开始（5分钟）
- **[`QUICKSTART.md`](QUICKSTART.md)** - 快速开始指南
  - 环境准备
  - 安装步骤
  - 配置步骤
  - 基本使用
  - 常见问题

### 📖 详细文档
- **[`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md)** - 完整功能文档
  - 功能特性
  - 安装指南
  - 配置选项
  - 指令详解
  - 开发指南
  - 错误处理

- **[`API_MAPPING.md`](API_MAPPING.md)** - API映射文档
  - 指令与API映射
  - API端点详解
  - 请求/响应示例
  - 参数验证规则
  - 性能指标

### 💡 使用示例
- **[`EXAMPLES.md`](EXAMPLES.md)** - 16个实际使用示例
  - 基础使用
  - 队列管理
  - 任务查询
  - 错误处理
  - 完整工作流程
  - 提示和技巧

### 📋 项目信息
- **[`INSTALLATION.md`](INSTALLATION.md)** - 项目总结
  - 文件清单
  - 文件结构
  - 快速开始
  - 技术栈
  - 项目统计

---

## 🎯 按用途查找

### 我是新手，想快速上手
1. 阅读 [`QUICKSTART.md`](QUICKSTART.md) - 5分钟快速开始
2. 查看 [`EXAMPLES.md`](EXAMPLES.md) - 实际使用示例
3. 尝试 `/health` 指令验证

### 我想了解所有功能
1. 阅读 [`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md) - 完整功能说明
2. 查看 [`API_MAPPING.md`](API_MAPPING.md) - API详细说明
3. 参考 [`EXAMPLES.md`](EXAMPLES.md) - 实际示例

### 我想开发或修改代码
1. 查看 [`koishi_client.ts`](koishi_client.ts) - 源代码
2. 查看 [`package.json`](package.json) - 项目配置
3. 查看 [`tsconfig.json`](tsconfig.json) - 编译配置
4. 阅读 [`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md) 的开发部分

### 我遇到了问题
1. 查看 [`QUICKSTART.md`](QUICKSTART.md) 的常见问题部分
2. 查看 [`API_MAPPING.md`](API_MAPPING.md) 的错误处理部分
3. 查看 [`EXAMPLES.md`](EXAMPLES.md) 的错误处理示例

### 我想了解API细节
1. 阅读 [`API_MAPPING.md`](API_MAPPING.md) - 完整API说明
2. 查看 [`EXAMPLES.md`](EXAMPLES.md) - 请求/响应示例
3. 参考 [`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md) 的API端点映射表

---

## 📁 文件清单

### 核心代码
| 文件 | 类型 | 说明 |
|------|------|------|
| [`koishi_client.ts`](koishi_client.ts) | TypeScript | 主插件实现，~250行 |
| [`package.json`](package.json) | JSON | NPM项目配置 |
| [`tsconfig.json`](tsconfig.json) | JSON | TypeScript编译配置 |

### 配置文件
| 文件 | 类型 | 说明 |
|------|------|------|
| [`koishi.yml.example`](koishi.yml.example) | YAML | Koishi配置示例 |

### 文档文件
| 文件 | 行数 | 说明 |
|------|------|------|
| [`QUICKSTART.md`](QUICKSTART.md) | ~300 | 快速开始指南 |
| [`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md) | ~400 | 详细功能文档 |
| [`API_MAPPING.md`](API_MAPPING.md) | ~500 | API映射文档 |
| [`EXAMPLES.md`](EXAMPLES.md) | ~400 | 使用示例集合 |
| [`INSTALLATION.md`](INSTALLATION.md) | ~300 | 项目总结 |
| [`INDEX.md`](INDEX.md) | ~200 | 本文件 |

---

## 🎮 指令速查

### 基础指令
```
/health              # 健康检查
/scrape 10 5         # 添加爬取任务
/queue               # 查看队列状态
/task 0              # 查看任务结果
/image 0             # 获取任务图片
/steamdt help        # 显示帮助
```

### 参数说明
- `scrolls`: 滚动次数（1-100，默认5）
- `priority`: 优先级（0-10，默认0）
- `index`: 任务索引（非负整数）

---

## 🔧 配置速查

### 基础配置
```yaml
plugins:
  steamdt-client:
    apiUrl: http://127.0.0.1:1145
    timeout: 30000
```

### 常见配置修改
```yaml
# 修改API地址
apiUrl: http://your-server:1145

# 增加超时时间
timeout: 60000

# 本地开发
apiUrl: http://localhost:1145
```

---

## 📊 API端点映射

| 指令 | HTTP方法 | 端点 | 说明 |
|------|---------|------|------|
| `/scrape` | POST | `/api/scrape` | 添加爬取任务 |
| `/queue` | GET | `/api/queue` | 获取队列状态 |
| `/task` | GET | `/api/task/{index}` | 获取任务结果 |
| `/image` | GET | `/api/task/{index}/image` | 获取任务图片 |
| `/health` | GET | `/health` | 健康检查 |

---

## 🚀 快速命令

### 安装和编译
```bash
npm install          # 安装依赖
npm run build        # 编译代码
npm run dev          # 监视模式
```

### 启动服务
```bash
# 终端1：启动API服务
python api_server.py 1145

# 终端2：启动Koishi
koishi start
```

### 验证安装
```bash
# 检查服务状态
curl http://127.0.0.1:1145/health

# 在Koishi中测试
/health
```

---

## ✨ 功能特性

✅ **6个Koishi指令** - 覆盖所有API功能
✅ **完整的参数验证** - 确保数据有效性
✅ **详细的错误处理** - 用户友好的错误提示
✅ **格式化输出** - 美观的消息展示
✅ **日志记录** - 便于调试和监控
✅ **超时配置** - 可根据网络调整
✅ **完整文档** - 6份详细文档
✅ **使用示例** - 16个实际示例
✅ **API映射** - 清晰的接口说明
✅ **快速开始** - 5分钟上手

---

## 📈 项目统计

- **代码行数：** ~250行（TypeScript）
- **文档行数：** ~2000行（Markdown）
- **指令数量：** 6个
- **API端点：** 5个
- **文档文件：** 6个
- **配置文件：** 3个
- **使用示例：** 16个

---

## 🔗 相关链接

### 官方文档
- [Koishi官网](https://koishi.chat/)
- [Koishi文档](https://koishi.chat/guide/)
- [FastAPI文档](https://fastapi.tiangolo.com/)

### 项目文件
- [API服务](api_server.py) - 同步版本API
- [爬虫实现](steamdt_scraper_final.py) - 数据爬虫
- [表格生成](generate_table_image.py) - 图片生成

---

## 💬 常见问题速查

**Q: 如何快速开始？**
A: 查看 [`QUICKSTART.md`](QUICKSTART.md)

**Q: 如何使用指令？**
A: 查看 [`EXAMPLES.md`](EXAMPLES.md)

**Q: API如何工作？**
A: 查看 [`API_MAPPING.md`](API_MAPPING.md)

**Q: 如何配置？**
A: 查看 [`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md) 的配置部分

**Q: 遇到错误怎么办？**
A: 查看 [`QUICKSTART.md`](QUICKSTART.md) 的故障排查部分

**Q: 如何修改代码？**
A: 查看 [`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md) 的开发部分

---

## 📝 版本信息

- **版本：** 1.0.0
- **创建时间：** 2026-03-15
- **状态：** ✅ 完成
- **许可证：** MIT

---

## 🎓 学习路径

### 初级（了解基础）
1. [`QUICKSTART.md`](QUICKSTART.md) - 快速开始
2. [`EXAMPLES.md`](EXAMPLES.md) - 基础示例

### 中级（掌握功能）
1. [`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md) - 完整功能
2. [`API_MAPPING.md`](API_MAPPING.md) - API详解
3. [`EXAMPLES.md`](EXAMPLES.md) - 高级示例

### 高级（开发扩展）
1. [`koishi_client.ts`](koishi_client.ts) - 源代码
2. [`package.json`](package.json) - 项目配置
3. [`KOISHI_CLIENT_README.md`](KOISHI_CLIENT_README.md) - 开发指南

---

## 🎯 下一步

1. ✅ 阅读本索引文件
2. ✅ 选择合适的文档开始阅读
3. ✅ 按照 [`QUICKSTART.md`](QUICKSTART.md) 安装和配置
4. ✅ 参考 [`EXAMPLES.md`](EXAMPLES.md) 尝试使用
5. ✅ 根据需要查阅其他文档

---

**祝你使用愉快！🚀**

如有问题，请查阅相应的文档或查看源代码实现。
