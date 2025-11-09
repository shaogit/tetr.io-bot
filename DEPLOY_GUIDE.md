# 资源自动部署使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行部署脚本

```bash
python deploy_resources.py
```

脚本将自动完成：
- ✓ 从 GitHub 下载开源字体（Noto Sans SC、Roboto Mono、Inter）
- ✓ 生成背景素材（纹理、光效、图案等）
- ✓ 创建许可证文件
- ✓ 生成部署报告

### 3. 查看结果

部署完成后，资源将保存在以下目录：

```
assets/
├── fonts/                      # 字体文件
│   ├── NotoSansSC-Regular.ttf
│   ├── NotoSansSC-Bold.ttf
│   ├── RobotoMono-Regular.ttf
│   └── Inter-Bold.ttf
└── backgrounds/                # 背景素材
    ├── base/                   # 基础纹理（5个文件）
    ├── effects/                # 光效素材（4个文件）
    ├── patterns/               # 装饰图案（2个文件）
    └── gradients/              # 渐变背景（自动）
```

## 部署报告

部署完成后会生成两个文件：
- `deploy_resources.log` - 详细日志
- `deployment_report.txt` - 部署报告

## 常见问题

### Q: 字体下载失败怎么办？
A: 可能是网络问题或 GitHub 访问限制。可以：
1. 检查网络连接
2. 使用代理
3. 手动从链接下载并放置到 `assets/fonts/` 目录

### Q: 背景素材不够丰富？
A: 当前提供的是程序生成的基础素材。你可以：
1. 从 Unsplash、Pexels 等网站手动下载高质量背景图
2. 将图片放置到 `assets/backgrounds/downloaded/` 目录
3. 后续版本将支持自动爬取功能

### Q: 如何更新资源？
A: 直接重新运行部署脚本：
```bash
python deploy_resources.py
```
已存在的文件不会被覆盖。

## 资源许可

所有自动下载和生成的资源都符合开源许可：
- 字体：SIL OFL 1.1 / Apache 2.0
- 背景：程序生成，无版权限制

详见 `assets/LICENSES.txt`

## 高级功能（计划中）

### 自动爬取背景图
- 定时从 Unsplash/Pexels 爬取新背景
- 智能筛选符合风格的图片
- 自动管理素材库

敬请期待！
