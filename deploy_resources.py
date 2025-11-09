#!/usr/bin/env python3
"""
资源部署脚本

自动下载字体和生成背景素材
"""

import sys
import logging
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from resource_deploy.font_downloader import FontDownloader
from resource_deploy.background_generator import BackgroundGenerator


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deploy_resources.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """打印欢迎信息"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║       TETR.IO Plugin - 资源自动部署工具               ║
╚═══════════════════════════════════════════════════════╝
    """
    print(banner)


def deploy_fonts(base_dir: Path) -> dict:
    """
    部署字体资源
    
    Args:
        base_dir: 项目根目录
        
    Returns:
        部署结果
    """
    logger.info("=" * 60)
    logger.info("开始部署字体资源...")
    logger.info("=" * 60)
    
    fonts_dir = base_dir / "assets" / "fonts"
    downloader = FontDownloader(str(fonts_dir))
    
    # 下载所有字体
    results = downloader.download_all()
    
    # 验证字体
    valid_fonts = downloader.verify_fonts()
    
    # 统计结果
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    logger.info("=" * 60)
    logger.info(f"字体部署完成: {success_count}/{total_count} 成功")
    logger.info("=" * 60)
    
    return {
        'download_results': results,
        'validation_results': valid_fonts,
        'success_count': success_count,
        'total_count': total_count
    }


def deploy_backgrounds(base_dir: Path) -> dict:
    """
    部署背景素材
    
    Args:
        base_dir: 项目根目录
        
    Returns:
        部署结果
    """
    logger.info("=" * 60)
    logger.info("开始生成背景素材...")
    logger.info("=" * 60)
    
    backgrounds_dir = base_dir / "assets" / "backgrounds"
    generator = BackgroundGenerator(str(backgrounds_dir))
    
    # 生成所有素材
    results = generator.generate_all()
    
    # 统计结果
    total_success = 0
    total_count = 0
    
    for category, items in results.items():
        success = sum(1 for v in items.values() if v)
        total = len(items)
        total_success += success
        total_count += total
        logger.info(f"{category}: {success}/{total} 成功")
    
    logger.info("=" * 60)
    logger.info(f"背景素材生成完成: {total_success}/{total_count} 成功")
    logger.info("=" * 60)
    
    return {
        'results': results,
        'success_count': total_success,
        'total_count': total_count
    }


def generate_report(font_results: dict, bg_results: dict) -> str:
    """
    生成部署报告
    
    Args:
        font_results: 字体部署结果
        bg_results: 背景部署结果
        
    Returns:
        报告内容
    """
    report = []
    report.append("\n" + "=" * 70)
    report.append("资源部署报告")
    report.append("=" * 70)
    
    # 字体部署部分
    report.append("\n【字体部署】")
    report.append("-" * 70)
    for font_name, success in font_results['download_results'].items():
        status = "✓" if success else "✗"
        report.append(f"  {status} {font_name}")
    
    report.append(f"\n字体部署统计: {font_results['success_count']}/{font_results['total_count']} 成功")
    
    # 背景素材部分
    report.append("\n【背景素材生成】")
    report.append("-" * 70)
    
    for category, items in bg_results['results'].items():
        report.append(f"\n{category}/:")
        for item_name, success in items.items():
            status = "✓" if success else "✗"
            report.append(f"  {status} {item_name}")
    
    report.append(f"\n背景素材统计: {bg_results['success_count']}/{bg_results['total_count']} 成功")
    
    # 总体状态
    total_success = font_results['success_count'] + bg_results['success_count']
    total_count = font_results['total_count'] + bg_results['total_count']
    success_rate = (total_success / total_count * 100) if total_count > 0 else 0
    
    report.append("\n" + "=" * 70)
    report.append(f"部署状态: {total_success}/{total_count} 成功 ({success_rate:.1f}%)")
    
    if total_success == total_count:
        report.append("状态: 完全成功 ✓")
    elif total_success > 0:
        report.append("状态: 部分成功 ⚠")
    else:
        report.append("状态: 失败 ✗")
    
    report.append("=" * 70)
    
    return "\n".join(report)


def create_license_file(base_dir: Path):
    """创建许可证信息文件"""
    license_content = """资源许可证信息
==================

本目录包含的资源文件许可证信息：

【字体资源】
-----------

1. Noto Sans SC (思源黑体)
   - 来源: Google Fonts / Adobe
   - 仓库: https://github.com/googlefonts/noto-cjk
   - 许可证: SIL Open Font License 1.1
   - 说明: 可自由使用、修改和分发

2. Roboto Mono
   - 来源: Google Fonts
   - 仓库: https://github.com/googlefonts/RobotoMono
   - 许可证: Apache License 2.0
   - 说明: 可自由使用、修改和分发

3. Inter
   - 来源: Rasmus Andersson
   - 仓库: https://github.com/rsms/inter
   - 许可证: SIL Open Font License 1.1
   - 说明: 可自由使用、修改和分发

【背景素材】
-----------

所有背景素材均为程序自动生成，不受版权限制。
可作为本项目的一部分自由使用、修改和分发。

生成方式：
- 使用 Python PIL/Pillow 库程序化生成
- 几何图案、纹理效果、光效等均为算法生成
- 无第三方版权问题

【使用说明】
-----------

1. 所有资源均符合开源许可，可用于商业和非商业用途
2. 建议在使用时保留此许可证文件
3. 如需更多信息，请访问各资源的原始仓库

最后更新: 2024
"""
    
    license_path = base_dir / "assets" / "LICENSES.txt"
    with open(license_path, 'w', encoding='utf-8') as f:
        f.write(license_content)
    
    logger.info(f"✓ 创建许可证文件: {license_path}")


def main():
    """主函数"""
    print_banner()
    
    # 获取项目根目录
    base_dir = Path(__file__).parent
    logger.info(f"项目目录: {base_dir}")
    
    try:
        # 部署字体
        font_results = deploy_fonts(base_dir)
        
        # 生成背景素材
        bg_results = deploy_backgrounds(base_dir)
        
        # 创建许可证文件
        create_license_file(base_dir)
        
        # 生成并显示报告
        report = generate_report(font_results, bg_results)
        print(report)
        
        # 保存报告到文件
        report_path = base_dir / "deployment_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"\n报告已保存到: {report_path}")
        
        # 返回状态码
        total_success = font_results['success_count'] + bg_results['success_count']
        total_count = font_results['total_count'] + bg_results['total_count']
        
        if total_success == total_count:
            logger.info("\n✓ 所有资源部署成功！")
            return 0
        elif total_success > 0:
            logger.warning("\n⚠ 部分资源部署成功，请查看报告了解详情")
            return 1
        else:
            logger.error("\n✗ 资源部署失败")
            return 2
            
    except Exception as e:
        logger.error(f"\n部署过程发生错误: {e}", exc_info=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
