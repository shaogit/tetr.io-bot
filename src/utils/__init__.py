"""
工具函数模块
提供各种辅助功能
"""
from typing import Dict, Any
import json
from pathlib import Path


class I18n:
    """国际化工具"""
    
    def __init__(self, locale: str = "zh_CN"):
        """
        初始化国际化工具
        
        Args:
            locale: 语言代码
        """
        self.locale = locale
        self.translations: Dict[str, Any] = {}
        self.load_translations()
    
    def load_translations(self):
        """加载翻译文件"""
        locale_file = Path(f"locales/{self.locale}.json")
        if locale_file.exists():
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
    
    def t(self, key: str, **kwargs) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键（支持点号分隔，如 "command.user.not_found"）
            **kwargs: 格式化参数
        
        Returns:
            翻译后的文本
        """
        # 支持嵌套键
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key  # 如果找不到，返回键本身
        
        # 格式化
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except:
                return value
        
        return str(value)


def format_time(seconds: float) -> str:
    """
    格式化时间
    
    Args:
        seconds: 秒数
    
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.2f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def format_number(num: float) -> str:
    """
    格式化数字（添加千位分隔符）
    
    Args:
        num: 数字
    
    Returns:
        格式化的数字字符串
    """
    return f"{num:,.0f}"


def validate_username(username: str) -> bool:
    """
    验证用户名格式
    
    Args:
        username: 用户名
    
    Returns:
        是否合法
    """
    if not username:
        return False
    
    if len(username) < 3 or len(username) > 16:
        return False
    
    # 只允许字母、数字、下划线
    return username.replace('_', '').isalnum()


def validate_mode(mode: str) -> bool:
    """
    验证游戏模式
    
    Args:
        mode: 游戏模式
    
    Returns:
        是否合法
    """
    valid_modes = ['league', '40l', 'blitz', 'xp', 'ar', 'qp', 'zen']
    return mode.lower() in valid_modes
