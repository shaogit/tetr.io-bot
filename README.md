# TETR.IO AstrBot 插件

一个功能全面、美观的 TETR.IO 数据查询 AstrBot 插件，提供用户信息、排行榜、游戏记录等多种查询功能。

## ✨ 特性

- 🎮 **完整的数据查询**：支持用户信息、TETRA LEAGUE、40 LINES、BLITZ 等所有游戏模式
- 🖼️ **美观的图像渲染**：参考 ch.tetr.io 网站风格，生成精美的数据卡片
- ⚡ **智能缓存系统**：减少 API 请求，提升响应速度
- 🌍 **国际化支持**：支持多语言（当前支持中文）
- 📊 **排行榜查询**：查看各模式的全球排行榜
- 🔍 **用户搜索**：快速搜索 TETR.IO 用户

## 📦 安装

1. 将本插件克隆或下载到 AstrBot 的插件目录：
   ```bash
   cd AstrBot/data/plugins
   git clone https://github.com/yourusername/astrbot-plugin-tetrio
   ```

2. 安装依赖：
   ```bash
   cd astrbot-plugin-tetrio
   pip install -r requirements.txt
   ```

3. 重启 AstrBot 或在 WebUI 中重载插件

## 🎯 使用方法

### 基础指令

```
/tetr                      - 显示帮助信息
/tetr user <用户名>        - 查询用户完整信息
/tetr u <用户名>           - 查询用户信息（简化）
```

### 游戏模式查询

```
/tetr league <用户名>      - 查询 TETRA LEAGUE 数据
/tetr 40l <用户名>         - 查询 40 LINES 数据
/tetr blitz <用户名>       - 查询 BLITZ 数据
```

### 排行榜查询

```
/tetr lb <模式> [条数]     - 查询排行榜
/tetr leaderboard <模式> [条数] - 查询排行榜（完整）

支持的模式：
- league  : TETRA LEAGUE 排行榜
- 40l     : 40 LINES 排行榜
- blitz   : BLITZ 排行榜
- xp      : XP 排行榜
- ar      : 成就评分排行榜
```

### 其他指令

```
/tetr stats                - 查询服务器统计
/tetr search <关键词>      - 搜索用户
```

## 📖 使用示例

```
# 查询用户信息
/tetr user folx
/tetr u folx

# 查询 TETRA LEAGUE 数据
/tetr league folx

# 查询排行榜
/tetr lb league 10
/tetr lb 40l 25

# 搜索用户
/tetr search folx

# 服务器统计
/tetr stats
```

## ⚙️ 配置

配置文件位于 `config/default_config.yaml`：

```yaml
api:
  base_url: "https://ch.tetr.io/api"
  timeout: 10
  retry_times: 3

cache:
  enabled: true
  user_info_ttl: 300     # 用户信息缓存时间（秒）
  summary_ttl: 300       # 游戏数据缓存时间
  leaderboard_ttl: 600   # 排行榜缓存时间
  server_stats_ttl: 60   # 服务器统计缓存时间

render:
  image_format: "png"    # 图片格式：png 或 webp
  image_quality: 85      # 图片质量 (1-100)
  default_width: 800     # 默认宽度

display:
  language: "zh_CN"      # 显示语言
```

## 🎨 自定义

### 添加自定义字体

将字体文件放置在 `assets/fonts/` 目录：
- `NotoSansSC-Regular.ttf` - 常规字体
- `NotoSansSC-Bold.ttf` - 粗体字体

推荐使用 Noto Sans SC 或其他支持中文的字体。

### 添加背景素材

将背景图片放置在 `assets/backgrounds/` 目录：
- `base/` - 基础纹理
- `gradients/` - 渐变背景
- `effects/` - 光效素材
- `patterns/` - 图案装饰

## 🔧 开发

### 项目结构

```
astrbot-plugin-tetrio/
├── main.py                # 插件入口
├── metadata.yaml          # 插件元数据
├── requirements.txt       # 依赖列表
├── config/
│   └── default_config.yaml
├── src/
│   ├── api/              # API 客户端
│   ├── cache/            # 缓存管理
│   ├── render/           # 图像渲染
│   └── utils/            # 工具函数
├── assets/               # 资源文件
└── locales/              # 语言文件
```

### 运行测试

```bash
# TODO: 添加测试
```

## 📝 API 参考

本插件使用 [TETR.IO TETRA CHANNEL API](https://tetr.io/about/api/)。

### 主要 API 端点：
- `/users/:user` - 用户信息
- `/users/:user/summaries/:mode` - 游戏模式数据
- `/users/by/:leaderboard` - 排行榜
- `/general/stats` - 服务器统计

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目使用 AGPL-3.0 许可证。

## 🙏 致谢

- [TETR.IO](https://tetr.io/) - 提供优秀的游戏和 API
- [AstrBot](https://github.com/Soulter/AstrBot) - 优秀的聊天机器人框架
- ch.tetr.io - 视觉设计参考

## 📞 支持

- 问题反馈：[GitHub Issues](https://github.com/yourusername/astrbot-plugin-tetrio/issues)
- QQ 群：975206796（AstrBot 官方群）
