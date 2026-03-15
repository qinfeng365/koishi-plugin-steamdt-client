# Koishi插件市场自动显示说明

## 自动显示条件

发布到NPM后，插件会自动显示在Koishi插件市场中，需要满足以下条件：

### 必需条件

1. **包名格式**
   - `koishi-plugin-*` ✅ 我们的包名：`koishi-plugin-steamdt-client`
   - `@bar/koishi-plugin-*`
   - `@koishijs/plugin-*`

2. **peerDependencies**
   - 必须包含 `koishi` ✅ 已配置：`"koishi": "^4.3.2"`

3. **koishi字段**
   - 必须包含 `description` 字段 ✅ 已配置中英文描述

4. **不是私有包**
   - `private` 不能为 `true` ✅ 未设置，默认为public

5. **最新版本未被弃用**
   - 不能使用 `npm deprecate` 标记为已弃用 ✅ 未弃用

## 显示时间

发布到NPM后，通常需要 **15分钟** 左右才能在Koishi插件市场中显示。

## 查看位置

### 官方插件市场
https://koishi.chat/market/

### NPM包页面
https://www.npmjs.com/package/koishi-plugin-steamdt-client

## 我们的配置

### package.json中的koishi字段

```json
{
  "name": "koishi-plugin-steamdt-client",
  "version": "1.0.0",
  "peerDependencies": {
    "koishi": "^4.3.2"
  },
  "koishi": {
    "description": {
      "en": "SteamDT market data scraper client for Koishi. Provides commands to manage scraping tasks, view queue status, and retrieve market data.",
      "zh": "SteamDT市场数据爬虫Koishi客户端。提供指令来管理爬取任务、查看队列状态和获取市场数据。"
    },
    "service": {
      "required": [],
      "optional": []
    }
  }
}
```

## 发布后的步骤

### 1. 发布到NPM
```bash
npm publish --registry https://registry.npmjs.org
```

### 2. 等待15分钟
插件市场会自动同步NPM上的新包。

### 3. 在Koishi中搜索
用户可以在Koishi控制台中搜索 `steamdt-client` 并安装。

### 4. 用户安装
```bash
npm install koishi-plugin-steamdt-client
```

## 插件市场显示的信息

插件市场会显示以下信息：

- **插件名称**：steamdt-client（去掉 `koishi-plugin-` 前缀）
- **版本**：1.0.0
- **描述**：来自 `koishi.description` ��段
- **作者**：来自 `package.json` 的 `author` 字段
- **许可证**：MIT
- **主页**：来自 `package.json` 的 `homepage` 字段
- **仓库**：来自 `package.json` 的 `repository` 字段

## 更新插件

当需要更新插件时：

1. 修改代码
2. 更新版本号
3. 编译代码
4. 提交到Git
5. 发布到NPM

```bash
npm version patch
npm run build
git add .
git commit -m "Release v1.0.1"
git push
npm publish --registry https://registry.npmjs.org
```

## 常见问题

### Q: 发布后多久能在市场中看到？
A: 通常15分钟内，最长可能需要1小时。

### Q: 如何更新插件信息？
A: 修改 `package.json` 中的 `koishi` 字段，然后发布新版本。

### Q: 如何隐藏插件？
A: 使用 `npm deprecate` 标记为已弃用，或设置 `"koishi": { "hidden": true }`。

### Q: 如何让插件显示为"开发中"？
A: 在 `koishi` 字段中添加 `"preview": true`。

### Q: 用户如何安装我的插件？
A: 在Koishi控制台中搜索插件名称并安装，或使用命令：
```bash
npm install koishi-plugin-steamdt-client
```

## 相关链接

- [Koishi插件市场](https://koishi.chat/market/)
- [Koishi插件开发指南](https://koishi.chat/guide/plugin/)
- [NPM包页面](https://www.npmjs.com/package/koishi-plugin-steamdt-client)
- [GitHub仓库](https://github.com/qinfeng365/koishi-plugin-steamdt-client)
