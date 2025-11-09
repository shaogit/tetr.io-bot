# 测试和使用指南

## 快速开始

### 1. 部署到 AstrBot

```bash
# 复制插件到 AstrBot 插件目录
cp -r tetr.io-bot /path/to/AstrBot/data/plugins/

# 安装依赖
cd /path/to/AstrBot/data/plugins/tetr.io-bot
pip install -r requirements.txt

# 重启 AstrBot
```

### 2. 在 AstrBot WebUI 中

1. 打开 AstrBot WebUI
2. 进入"插件管理"页面
3. 找到"TETR.IO 数据查询"插件
4. 点击"启用"
5. 点击"重载"

### 3. 测试指令

在聊天窗口中发送以下指令测试：

```
/tetr
```

应该看到帮助信息。

## 功能测试

### 测试用户查询

```
/tetr user folx
/tetr u osk
```

预期结果：返回用户信息卡片图像

### 测试排行榜

```
/tetr lb league 5
/tetr lb 40l 10
```

预期结果：返回排行榜图像

### 测试服务器统计

```
/tetr stats
```

预期结果：返回服务器统计卡片图像

### 测试搜索

```
/tetr search test
```

预期结果：返回匹配用户列表

## 常见问题

### 1. 图片无法显示

**问题**：指令执行成功但看不到图片

**解决方案**：
- 检查 AstrBot 的图片发送权限
- 确认消息平台支持图片消息
- 查看 AstrBot 日志是否有错误

### 2. API 请求失败

**问题**：提示"API 请求失败"或"网络连接错误"

**解决方案**：
- 检查网络连接
- 确认可以访问 https://ch.tetr.io/api/
- 检查防火墙设置
- 查看 `config/default_config.yaml` 中的 API 配置

### 3. 用户未找到

**问题**：提示"未找到用户"

**解决方案**：
- 确认用户名拼写正确
- 用户名区分大小写（但插件会自动转小写）
- 该用户可能不存在

### 4. 字体显示异常

**问题**：中文显示为方块或乱码

**解决方案**：
- 安装中文字体到 `assets/fonts/` 目录
- 参考 `assets/fonts/README.md`
- 重启插件

## 性能优化建议

### 1. 启用缓存

在 `config/default_config.yaml` 中：

```yaml
cache:
  enabled: true
  user_info_ttl: 300
  leaderboard_ttl: 600
```

### 2. 调整图片质量

如果图片文件过大：

```yaml
render:
  image_format: "webp"  # 使用 WebP 格式
  image_quality: 75     # 降低质量
```

### 3. 限制请求频率

避免短时间内大量请求，遵守 TETR.IO API 使用规范。

## 开发和调试

### 查看日志

AstrBot 日志位置：
```
AstrBot/data/logs/
```

查找包含 "TETR" 的日志：
```bash
grep -i tetr AstrBot/data/logs/latest.log
```

### 手动测试 API

```bash
# 测试 API 连接
curl https://ch.tetr.io/api/general/stats

# 测试用户查询
curl https://ch.tetr.io/api/users/folx
```

### 清空缓存

如果需要强制刷新数据，可以：
1. 重启插件
2. 或修改代码临时禁用缓存

## 下一步

### 添加更多功能

参考设计文档，可以添加：
- 用户对比功能
- 数据趋势图
- 更多游戏模式支持
- 自定义主题

### 贡献代码

1. Fork 项目
2. 创建功能分支
3. 提交 Pull Request

### 反馈问题

在 GitHub Issues 提交问题，请包含：
- AstrBot 版本
- 插件版本
- 错误日志
- 复现步骤

## 许可和致谢

本插件遵循 AGPL-3.0 许可证。

感谢：
- TETR.IO 提供优秀的游戏和 API
- AstrBot 社区的支持
- 所有贡献者
