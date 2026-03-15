# SteamDT Koishi 客户端 - 发布指南

本文档说明如何将此插件发布到NPM和Koishi插件市场。

## 📋 发布前检查清单

在发布前，请确保完成以下检查：

- [ ] 代码已编译：`npm run build`
- [ ] 所有测试通过
- [ ] 版本号已更新（在 `package.json` 中）
- [ ] `package.json` 中的所有必需字段已填写
- [ ] README或文档已更新
- [ ] Git仓库已初始化并提交
- [ ] 没有敏感信息在代码中

## 🔧 准备工作

### 1. 更新package.json

确保 `package.json` 包含以下必需字段：

```json
{
  "name": "koishi-plugin-steamdt-client",
  "version": "1.0.0",
  "peerDependencies": {
    "koishi": "^4.3.2"
  },
  "koishi": {
    "description": {
      "en": "SteamDT market data scraper client",
      "zh": "SteamDT市场数据爬虫客户端"
    }
  }
}
```

### 2. 编译代码

```bash
npm run build
```

确保 `dist/` 目录已生成。

### 3. 创建Git仓库

```bash
git init
git add .
git commit -m "Initial commit: SteamDT Koishi client v1.0.0"
git remote add origin https://github.com/yourusername/koishi-plugin-steamdt-client.git
git push -u origin main
```

### 4. 创建NPM账户

如果还没有NPM账户，请访问 [npmjs.com](https://www.npmjs.com/) 注册。

## 📤 发布步骤

### 步骤1：登录NPM

```bash
npm login
```

输入你的NPM用户名、密码和邮箱。

### 步骤2：验证包名

确保包名唯一且符合规范：

```bash
npm search koishi-plugin-steamdt-client
```

如果没有结果，说明包名可用。

### 步骤3：发布到NPM

```bash
npm publish
```

如果是第一次发布，可能需要验证邮箱。

### 步骤4：验证发布

发布成功后，可以在NPM上查看：

```bash
npm view koishi-plugin-steamdt-client
```

或访问：`https://www.npmjs.com/package/koishi-plugin-steamdt-client`

## 🔄 更新插件版本

当修改代码后，需要更新版本号才能重新发布。

### 更新版本号

```bash
# 小版本更新（1.0.0 -> 1.0.1）
npm version patch

# 中版本更新（1.0.0 -> 1.1.0）
npm version minor

# 大版本更新（1.0.0 -> 2.0.0）
npm version major
```

### 发布新版本

```bash
npm publish
```

## 📝 版本管理

### 语义化版本规范

遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)：

- **主版本号（Major）**：不兼容的API修改
- **次版本号（Minor）**：向下兼容的功能��增
- **修订号（Patch）**：向下兼容的问题修复

### 版本号示例

```
1.0.0  - 初始版本
1.0.1  - 修复bug
1.1.0  - 新增功能
2.0.0  - 重大更新，可能不兼容
```

## 🎯 Koishi插件市场

### 自动显示条件

满足以下条件的插件会自动显示在Koishi插件市场中：

✅ 包名符合格式：`koishi-plugin-*`
✅ `peerDependencies` 包含 `koishi`
✅ `package.json` 中有 `koishi` 字段
✅ 包含 `description` 字段（中英文）
✅ 不是私有包（`private` 不为 `true`）
✅ 最新版本未被弃用

### 插件市场链接

发布后，插件会显示在：
- [Koishi插件市场](https://koishi.chat/market/)
- [NPM包页面](https://www.npmjs.com/package/koishi-plugin-steamdt-client)

## 🚀 发布检查清单

### 代码质量
- [ ] 代码已编译无错误
- [ ] TypeScript类型检查通过
- [ ] 没有console.log调试代码
- [ ] 错误处理完整

### 文档完整性
- [ ] README或主文档已更新
- [ ] 指令文档完整
- [ ] 配置选项已说明
- [ ] 示例代码可运行

### 版本信息
- [ ] 版本号已更新
- [ ] CHANGELOG已更新
- [ ] Git标签已创建

### 包配置
- [ ] package.json格式正确
- [ ] 所有必需字段已填写
- [ ] 依赖版本正确
- [ ] koishi字段完整

## 📊 发布后监控

### 检查发布状态

```bash
# 查看包信息
npm view koishi-plugin-steamdt-client

# 查看版本历史
npm view koishi-plugin-steamdt-client versions

# 查看下载统计
npm view koishi-plugin-steamdt-client downloads
```

### 监控用户反馈

- 定期检查NPM包页面的评论
- 关注GitHub Issues
- 收集用户反馈

## 🔧 常见问题

### Q: 发布失败，提示包名已存在？
A: 修改 `package.json` 中的 `name` 字段，使用唯一的包名。

### Q: 发布失败，提示需要验证邮箱？
A: 检查NPM账户邮箱，完成邮箱验证后重试。

### Q: 如何撤销已发布的版本？
A: 使用 `npm unpublish` 命令（仅在发布后72小时内可用）。

### Q: 如何弃用某个版本？
A: 使用 `npm deprecate` 命令标记为已弃用。

### Q: 如何更新已发布的包？
A: 修改代码后，更新版本号，然后重新发布。

## 📚 相关资源

- [NPM官方文档](https://docs.npmjs.com/)
- [Koishi插件开发指南](https://koishi.chat/guide/plugin/)
- [Semantic Versioning](https://semver.org/lang/zh-CN/)
- [Koishi插件市场](https://koishi.chat/market/)

## 🎓 发布流程总结

```
1. 准备工作
   ├─ 更新package.json
   ├─ 编译代码
   ├─ 创建Git仓库
   └─ 创建NPM账户

2. 发布步骤
   ├─ npm login
   ├─ npm publish
   └─ 验证发布

3. 后续维护
   ├─ 监控用户反馈
   ├─ 修复bug
   ├─ 更新版本
   └─ 重新发布
```

## 📝 发布记录模板

创建 `CHANGELOG.md` 记录版本变化：

```markdown
# 更新日志

## [1.0.0] - 2026-03-15

### 新增
- 初始版本发布
- 6个Koishi指令
- 完整的文档和示例

### 修复
- 无

### 变更
- 无

## [1.0.1] - 2026-03-16

### 新增
- 无

### 修复
- 修复超时处理bug
- 改进错误消息

### 变更
- 更新依赖版本
```

## ✅ 发布成功标志

发布成功后，你应该能够：

✅ 在NPM上搜索到你的包
✅ 在Koishi插件市场中看到你的插件
✅ 其他用户可以通过 `npm install` 安装
✅ 其他用户可以在Koishi中启用你的插件

## 🎉 恭喜！

你已经成功发布了一个Koishi插件！

现在你可以：
- 收集用户反馈
- 修复发现的问题
- 添加新功能
- 发布新版本

感谢你为Koishi社区做出的贡献！
