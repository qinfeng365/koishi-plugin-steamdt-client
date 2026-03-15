# NPM发布指南

本文档说明如何将SteamDT Koishi客户端发布到NPM。

## 前置要求

1. **NPM账户**
   - 访问 https://www.npmjs.com/signup 注册账户
   - 验证邮箱

2. **本地环境**
   - Node.js 16+
   - npm 8+

## 发布步骤

### 步骤1：登录NPM

```bash
npm login
```

输入以下信息：
- Username: 你的NPM用户名
- Password: 你的NPM密码
- Email: 你的NPM邮箱

### 步骤2：验证包配置

确保 `package.json` 中的以下字段正确：

```json
{
  "name": "koishi-plugin-steamdt-client",
  "version": "1.0.0",
  "description": "SteamDT 异动数据爬虫 Koishi 客户端插件",
  "main": "index.js",
  "types": "index.d.ts",
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

### 步骤3：编译代码

```bash
npm run build
```

确保 `index.js` 和 `index.d.ts` 已生成。

### 步骤4：发布到NPM

```bash
npm publish
```

或使用官方镜像（如果配置了国内镜像）：

```bash
npm publish --registry https://registry.npmjs.org
```

### 步骤5：验证发布

发布成功后，可以在NPM上查看：

```bash
npm view koishi-plugin-steamdt-client
```

或访问：https://www.npmjs.com/package/koishi-plugin-steamdt-client

## 更新版本

当需要发布新版本时：

### 1. 更新版本号

```bash
# 小版本更新（1.0.0 -> 1.0.1）
npm version patch

# 中版本更新（1.0.0 -> 1.1.0）
npm version minor

# 大版本更新（1.0.0 -> 2.0.0）
npm version major
```

### 2. 编译代码

```bash
npm run build
```

### 3. 提交到Git

```bash
git add .
git commit -m "Release v1.0.1"
git push
```

### 4. 发布到NPM

```bash
npm publish
```

## 常见问题

### Q: 包名已存在？
A: 修改 `package.json` 中的 `name` 字段，使用唯一的包名。

### Q: 需要验证邮箱？
A: 检查NPM账户邮箱，完成邮箱验证后重试。

### Q: 发布失败，提示权限不足？
A: 确保你有权限发布该包。如果是新包，应该没有权限问题。

### Q: 如何撤销已发布的版本？
A: 使用 `npm unpublish` 命令（仅在发布后72小时内可用）。

### Q: 如何弃用某个版本？
A: 使用 `npm deprecate` 命令标记为已弃用。

```bash
npm deprecate koishi-plugin-steamdt-client@1.0.0 "This version is deprecated"
```

## 发布后

### 在Koishi插件市场中显示

发布到NPM后，插件会自动显示在Koishi插件市场中（通常需要15分钟）。

访问：https://koishi.chat/market/

### 用户安装

用户可以通过以下方式安装你的插件：

```bash
npm install koishi-plugin-steamdt-client
```

或在Koishi控制台中搜索并安装。

## 发布检查清单

- [ ] NPM账户已创建并验证
- [ ] 本地已登录NPM（`npm whoami`）
- [ ] `package.json` 配置正确
- [ ] 代码已编译（`npm run build`）
- [ ] 版本号已更新
- [ ] Git提交已推送
- [ ] 所有文件已添加到Git
- [ ] 准备好发布

## 相关文档

- [`PUBLISH_GUIDE.md`](PUBLISH_GUIDE.md) - 发布指南
- [`QUICKSTART.md`](QUICKSTART.md) - 快速开始
- [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md) - 项目总结
- [NPM官方文档](https://docs.npmjs.com/)
- [Koishi插件市场](https://koishi.chat/market/)
