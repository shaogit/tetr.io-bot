"""
字体下载器

从 GitHub 官方仓库下载开源字体文件
"""

import os
import requests
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FontDownloader:
    """字体下载器类"""
    
    # 字体配置映射
    FONT_CONFIGS = {
        "NotoSansSC-Regular.ttf": {
            "repo": "googlefonts/noto-cjk",
            "name": "Noto Sans SC Regular",
            "direct_url": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
        },
        "NotoSansSC-Bold.ttf": {
            "repo": "googlefonts/noto-cjk",
            "name": "Noto Sans SC Bold",
            "direct_url": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Bold.otf"
        },
        "RobotoMono-Regular.ttf": {
            "repo": "googlefonts/RobotoMono",
            "pattern": "RobotoMono[wght].ttf",
            "name": "Roboto Mono Regular",
            "direct_url": "https://github.com/googlefonts/RobotoMono/raw/main/fonts/ttf/RobotoMono-Regular.ttf"
        },
        "Inter-Bold.ttf": {
            "repo": "rsms/inter",
            "pattern": "Inter-Bold.ttf",
            "name": "Inter Bold",
            "direct_url": "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip",
            "is_archive": True
        },
    }
    
    def __init__(self, target_dir: str, timeout: int = 30, retry_times: int = 3):
        """
        初始化字体下载器
        
        Args:
            target_dir: 字体目标目录
            timeout: 下载超时时间（秒）
            retry_times: 下载失败重试次数
        """
        self.target_dir = Path(target_dir)
        self.timeout = timeout
        self.retry_times = retry_times
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def download_all(self) -> Dict[str, bool]:
        """
        下载所有字体
        
        Returns:
            字体下载结果字典 {字体名: 是否成功}
        """
        results = {}
        
        # 确保目标目录存在
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        for font_name, config in self.FONT_CONFIGS.items():
            target_path = self.target_dir / font_name
            
            # 检查文件是否已存在
            if target_path.exists():
                logger.info(f"字体 {font_name} 已存在，跳过下载")
                results[font_name] = True
                continue
            
            logger.info(f"开始下载字体: {config['name']}")
            success = self._download_font(font_name, config, target_path)
            results[font_name] = success
            
            if success:
                logger.info(f"✓ {config['name']} 下载成功")
            else:
                logger.error(f"✗ {config['name']} 下载失败")
        
        return results
    
    def _download_font(self, font_name: str, config: Dict, target_path: Path) -> bool:
        """
        下载单个字体文件
        
        Args:
            font_name: 字体文件名
            config: 字体配置
            target_path: 目标路径
            
        Returns:
            是否下载成功
        """
        # 优先使用直接下载链接
        if "direct_url" in config:
            return self._download_from_url(config["direct_url"], target_path)
        
        # 否则从 GitHub Release 获取
        return self._download_from_release(config["repo"], config["pattern"], target_path)
    
    def _download_from_url(self, url: str, target_path: Path) -> bool:
        """
        从指定 URL 下载文件
        
        Args:
            url: 下载 URL
            target_path: 目标路径
            
        Returns:
            是否下载成功
        """
        tmp_path: Optional[Path] = None
        
        for attempt in range(self.retry_times):
            try:
                logger.info(f"尝试从 URL 下载 (第 {attempt + 1}/{self.retry_times} 次): {url}")
                
                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ttf') as tmp_file:
                    tmp_path = Path(tmp_file.name)
                
                # 下载文件
                response = self.session.get(url, timeout=self.timeout, stream=True)
                response.raise_for_status()
                
                # 写入临时文件
                with open(tmp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # 验证文件大小
                file_size = tmp_path.stat().st_size
                if file_size < 1024:  # 至少 1KB
                    logger.warning(f"下载的文件过小: {file_size} bytes")
                    tmp_path.unlink()
                    continue
                
                # 移动到目标位置
                shutil.move(str(tmp_path), str(target_path))
                logger.info(f"文件大小: {file_size / 1024:.1f} KB")
                return True
                
            except Exception as e:
                logger.warning(f"下载失败 (尝试 {attempt + 1}): {e}")
                if tmp_path and tmp_path.exists():
                    tmp_path.unlink()
                
                if attempt < self.retry_times - 1:
                    continue
        
        return False
    
    def _download_from_release(self, repo: str, pattern: str, target_path: Path) -> bool:
        """
        从 GitHub Release 下载文件
        
        Args:
            repo: GitHub 仓库（owner/repo）
            pattern: 文件名模式
            target_path: 目标路径
            
        Returns:
            是否下载成功
        """
        try:
            # 获取最新 release
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            logger.info(f"查询 GitHub Release: {repo}")
            
            response = self.session.get(api_url, timeout=self.timeout)
            response.raise_for_status()
            release_data = response.json()
            
            # 查找匹配的 asset
            for asset in release_data.get('assets', []):
                asset_name = asset['name']
                if pattern in asset_name or asset_name.endswith(pattern):
                    download_url = asset['browser_download_url']
                    logger.info(f"找到匹配文件: {asset_name}")
                    return self._download_from_url(download_url, target_path)
            
            logger.warning(f"未找到匹配的文件: {pattern}")
            return False
            
        except Exception as e:
            logger.error(f"从 GitHub Release 下载失败: {e}")
            return False
    
    def verify_fonts(self) -> Dict[str, bool]:
        """
        验证已下载的字体文件
        
        Returns:
            验证结果字典 {字体名: 是否有效}
        """
        results = {}
        
        for font_name in self.FONT_CONFIGS.keys():
            font_path = self.target_dir / font_name
            
            if not font_path.exists():
                results[font_name] = False
                continue
            
            # 检查文件大小
            file_size = font_path.stat().st_size
            if file_size < 10240:  # 至少 10KB
                logger.warning(f"字体文件过小，可能损坏: {font_name}")
                results[font_name] = False
                continue
            
            # 检查文件扩展名
            if not font_name.endswith(('.ttf', '.otf')):
                logger.warning(f"不支持的字体格式: {font_name}")
                results[font_name] = False
                continue
            
            results[font_name] = True
        
        return results
    
    def get_missing_fonts(self) -> List[str]:
        """
        获取缺失的字体列表
        
        Returns:
            缺失的字体文件名列表
        """
        missing = []
        
        for font_name in self.FONT_CONFIGS.keys():
            font_path = self.target_dir / font_name
            if not font_path.exists():
                missing.append(font_name)
        
        return missing
