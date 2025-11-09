"""
图像渲染器
核心渲染逻辑，生成各种数据卡片
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional, Dict, Any, Tuple, Union
import io
import base64
from pathlib import Path

from ..api.models import UserInfo, LeagueData, RecordData, ServerStats
from .background import BackgroundGenerator


class ImageRenderer:
    """图像渲染器"""
    
    # 段位颜色映射
    RANK_COLORS = {
        'x': ('#A855F7', '#8B5CF6'),  # 紫色渐变
        'u': ('#EC4899', '#A855F7'),  # 红紫渐变
        'ss': ('#EF4444', '#DC2626'),  # 红色
        's+': ('#F97316', '#EA580C'),  # 橙红
        's': ('#F59E0B', '#D97706'),   # 橙色
        's-': ('#FBBF24', '#F59E0B'),  # 黄橙
        'a+': ('#EAB308', '#CA8A04'),  # 黄色
        'a': ('#84CC16', '#65A30D'),   # 绿黄
        'a-': ('#22C55E', '#16A34A'),  # 绿色
        'b+': ('#10B981', '#059669'),  # 青绿
        'b': ('#14B8A6', '#0D9488'),   # 青色
        'b-': ('#06B6D4', '#0891B2'),  # 蓝青
        'c+': ('#3B82F6', '#2563EB'),  # 蓝色
        'c': ('#3B82F6', '#2563EB'),
        'c-': ('#3B82F6', '#2563EB'),
        'd+': ('#6B7280', '#4B5563'),  # 灰蓝
        'd': ('#6B7280', '#4B5563'),   # 灰色
        'z': ('#6B7280', '#4B5563'),   # 未排名
    }
    
    # 配色方案
    COLORS = {
        'bg_primary': '#0F0F14',
        'bg_secondary': '#1A1A24',
        'bg_tertiary': '#242430',
        'border': '#2A2A35',
        'text_primary': '#FFFFFF',
        'text_secondary': '#9B9BA5',
        'text_disabled': '#5A5A66',
        'accent': '#6366F1',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化渲染器
        
        Args:
            config: 渲染配置
        """
        self.config = config
        self.default_width = config.get('default_width', 800)
        self.image_format = config.get('image_format', 'png')
        self.quality = config.get('image_quality', 85)
        
        # 字体路径（使用系统默认字体作为后备）
        self.font_path = Path(config.get('font_path', 'assets/fonts'))
        
        # 背景生成器
        self.bg_gen = BackgroundGenerator()
    
    def _get_font(self, size: int = 16, bold: bool = False) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        """获取字体对象，如果没有自定义字体则使用默认"""
        try:
            if bold:
                font_file = self.font_path / 'NotoSansSC-Bold.ttf'
            else:
                font_file = self.font_path / 'NotoSansSC-Regular.ttf'
            
            if font_file.exists():
                return ImageFont.truetype(str(font_file), size)
        except:
            pass
        
        # 使用默认字体
        return ImageFont.load_default()
    
    def _get_rank_colors(self, rank: str) -> Tuple[str, str]:
        """获取段位对应的颜色"""
        rank_lower = rank.lower()
        return self.RANK_COLORS.get(rank_lower, ('#6B7280', '#4B5563'))
    
    def render_user_card(self, user: UserInfo, league: Optional[LeagueData] = None) -> bytes:
        """
        渲染用户信息卡片
        
        Args:
            user: 用户信息
            league: TETRA LEAGUE 数据（可选）
        
        Returns:
            图像字节数据
        """
        # 创建画布
        width, height = 800, 600
        img = Image.new('RGB', (width, height), self.COLORS['bg_primary'])
        draw = ImageDraw.Draw(img)
        
        # 如果有段位，使用段位颜色生成渐变背景
        if league and league.rank:
            color1, color2 = self._get_rank_colors(league.rank)
            gradient = self.bg_gen.generate_linear_gradient(
                width, height // 3, color1, color2, "horizontal"
            )
            # 降低透明度并粘贴
            gradient = gradient.convert('RGBA')
            gradient.putalpha(128)  # 50% 透明度
            bg = Image.new('RGB', (width, height), self.COLORS['bg_primary'])
            bg.paste(gradient, (0, 0), gradient)
            img = bg
            draw = ImageDraw.Draw(img)
        
        # 绘制用户名
        font_large = self._get_font(36, bold=True)
        font_medium = self._get_font(20)
        font_small = self._get_font(14)
        
        y_pos = 40
        draw.text((40, y_pos), user.username, fill=self.COLORS['text_primary'], font=font_large)
        
        # 绘制基础信息
        y_pos += 60
        info_text = f"XP: {user.xp:,.0f}  |  游戏时长: {user.gametime / 3600:.1f}h"
        if user.gamesplayed >= 0:
            info_text += f"  |  游戏场次: {user.gamesplayed}"
        
        draw.text((40, y_pos), info_text, fill=self.COLORS['text_secondary'], font=font_medium)
        
        # 如果有 League 数据，绘制
        if league:
            y_pos += 80
            
            # 段位标题
            rank_text = f"{league.rank.upper()} Rank"
            draw.text((40, y_pos), rank_text, fill=self.COLORS['text_primary'], font=font_large)
            
            y_pos += 50
            # TR 值
            tr_text = f"TR: {league.tr:.2f}"
            draw.text((40, y_pos), tr_text, fill=self.COLORS['text_primary'], font=font_medium)
            
            y_pos += 40
            # 核心数据
            stats_text = f"APM: {league.apm:.2f}  |  PPS: {league.pps:.2f}  |  VS: {league.vs:.2f}"
            draw.text((40, y_pos), stats_text, fill=self.COLORS['text_secondary'], font=font_medium)
            
            y_pos += 40
            # 排名
            if league.global_rank > 0:
                rank_text = f"全球排名: #{league.global_rank:,}"
                if league.percentile > 0:
                    rank_text += f"  |  百分位: Top {league.percentile:.2f}%"
                draw.text((40, y_pos), rank_text, fill=self.COLORS['text_secondary'], font=font_small)
            
            y_pos += 40
            # 战绩
            winrate = league.winrate
            wins_text = f"胜场: {league.wins}  |  败场: {league.losses}  |  胜率: {winrate:.1f}%"
            draw.text((40, y_pos), wins_text, fill=self.COLORS['text_secondary'], font=font_small)
        
        # 转换为字节
        return self._image_to_bytes(img)
    
    def render_leaderboard(
        self,
        entries: list,
        mode: str,
        limit: int
    ) -> bytes:
        """
        渲染排行榜
        
        Args:
            entries: 排行榜条目列表
            mode: 游戏模式
            limit: 显示条数
        
        Returns:
            图像字节数据
        """
        # 计算高度
        entry_height = 50
        header_height = 100
        height = header_height + len(entries) * entry_height + 40
        width = 800
        
        img = Image.new('RGB', (width, height), self.COLORS['bg_primary'])
        draw = ImageDraw.Draw(img)
        
        # 标题
        font_title = self._get_font(32, bold=True)
        font_entry = self._get_font(16)
        
        mode_names = {
            'league': 'TETRA LEAGUE',
            '40l': '40 LINES',
            'blitz': 'BLITZ',
            'xp': 'XP',
            'ar': '成就评分'
        }
        title = f"{mode_names.get(mode, mode.upper())} 排行榜 - 前 {limit} 名"
        draw.text((40, 40), title, fill=self.COLORS['text_primary'], font=font_title)
        
        # 表头
        y_pos = header_height
        draw.line([(40, y_pos), (width - 40, y_pos)], fill=self.COLORS['border'], width=2)
        
        # 绘制条目
        for i, entry in enumerate(entries):
            y_pos = header_height + i * entry_height + 20
            
            # 排名
            rank_text = f"#{entry.rank}"
            draw.text((50, y_pos), rank_text, fill=self.COLORS['text_secondary'], font=font_entry)
            
            # 用户名
            draw.text((120, y_pos), entry.username, fill=self.COLORS['text_primary'], font=font_entry)
            
            # 数值
            if entry.value is not None:
                if mode == '40l':
                    value_text = f"{entry.value:.3f}s"
                elif mode in ['blitz', 'xp', 'ar']:
                    value_text = f"{entry.value:,.0f}"
                elif mode == 'league':
                    value_text = f"{entry.value:.2f} TR"
                else:
                    value_text = str(entry.value)
                
                draw.text((500, y_pos), value_text, fill=self.COLORS['text_primary'], font=font_entry)
            
            # 分隔线
            if i < len(entries) - 1:
                y_line = y_pos + entry_height - 10
                draw.line([(40, y_line), (width - 40, y_line)], fill=self.COLORS['border'], width=1)
        
        return self._image_to_bytes(img)
    
    def render_server_stats(self, stats: ServerStats) -> bytes:
        """
        渲染服务器统计卡片
        
        Args:
            stats: 服务器统计数据
        
        Returns:
            图像字节数据
        """
        width, height = 800, 600
        img = Image.new('RGB', (width, height), self.COLORS['bg_primary'])
        draw = ImageDraw.Draw(img)
        
        # 标题
        font_title = self._get_font(32, bold=True)
        font_label = self._get_font(14)
        font_value = self._get_font(24, bold=True)
        
        draw.text((40, 40), "TETR.IO 服务器统计", fill=self.COLORS['text_primary'], font=font_title)
        
        # 统计数据网格
        stats_data = [
            ("总玩家数", f"{stats.usercount:,}"),
            ("注册用户", f"{stats.totalaccounts:,}"),
            ("匿名用户", f"{stats.anoncount:,}"),
            ("排位用户", f"{stats.rankedcount:,}"),
            ("游戏记录", f"{stats.recordcount:,}"),
            ("总游戏场次", f"{stats.gamesplayed:,}"),
            ("完成场次", f"{stats.gamesfinished:,}"),
            ("游戏时长", f"{stats.gametime / 3600:,.0f}h"),
            ("方块放置", f"{stats.piecesplaced:,}"),
            ("总按键数", f"{stats.inputs:,}"),
        ]
        
        # 3列布局
        cols = 3
        col_width = (width - 80) // cols
        row_height = 80
        start_y = 120
        
        for i, (label, value) in enumerate(stats_data):
            col = i % cols
            row = i // cols
            
            x = 40 + col * col_width
            y = start_y + row * row_height
            
            # 标签
            draw.text((x, y), label, fill=self.COLORS['text_secondary'], font=font_label)
            
            # 数值
            draw.text((x, y + 25), value, fill=self.COLORS['text_primary'], font=font_value)
        
        return self._image_to_bytes(img)
    
    def _image_to_bytes(self, img: Image.Image) -> bytes:
        """将图像转换为字节数据"""
        buffer = io.BytesIO()
        
        if self.image_format.lower() == 'webp':
            img.save(buffer, format='WebP', quality=self.quality)
        else:
            img.save(buffer, format='PNG', optimize=True)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def image_to_base64(self, img_bytes: bytes) -> str:
        """将图像字节转换为 base64 字符串"""
        return base64.b64encode(img_bytes).decode('utf-8')
