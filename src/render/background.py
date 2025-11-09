"""
背景生成器
程序化生成渐变、几何图案等背景元素
"""
from PIL import Image, ImageDraw, ImageFilter
from typing import Tuple, Optional, List
import math
import random


class BackgroundGenerator:
    """背景生成器"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """将 HEX 颜色转换为 RGB"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    
    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """在两个颜色之间插值"""
        r = int(color1[0] + (color2[0] - color1[0]) * factor)
        g = int(color1[1] + (color2[1] - color1[1]) * factor)
        b = int(color1[2] + (color2[2] - color1[2]) * factor)
        return (r, g, b)
    
    @classmethod
    def generate_linear_gradient(
        cls,
        width: int,
        height: int,
        color1: str,
        color2: str,
        direction: str = "diagonal"
    ) -> Image.Image:
        """
        生成线性渐变背景
        
        Args:
            width: 宽度
            height: 高度
            color1: 起始颜色 (HEX)
            color2: 结束颜色 (HEX)
            direction: 方向 (horizontal/vertical/diagonal)
        
        Returns:
            渐变图像
        """
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        rgb1 = cls.hex_to_rgb(color1)
        rgb2 = cls.hex_to_rgb(color2)
        
        if direction == "horizontal":
            for x in range(width):
                factor = x / width
                color = cls.interpolate_color(rgb1, rgb2, factor)
                draw.line([(x, 0), (x, height)], fill=color)
        elif direction == "vertical":
            for y in range(height):
                factor = y / height
                color = cls.interpolate_color(rgb1, rgb2, factor)
                draw.line([(0, y), (width, y)], fill=color)
        else:  # diagonal
            max_dist = math.sqrt(width**2 + height**2)
            for y in range(height):
                for x in range(width):
                    dist = math.sqrt(x**2 + y**2)
                    factor = dist / max_dist
                    color = cls.interpolate_color(rgb1, rgb2, factor)
                    img.putpixel((x, y), color)
        
        return img
    
    @classmethod
    def generate_radial_gradient(
        cls,
        width: int,
        height: int,
        color1: str,
        color2: str
    ) -> Image.Image:
        """
        生成径向渐变背景
        
        Args:
            width: 宽度
            height: 高度
            color1: 中心颜色 (HEX)
            color2: 外围颜色 (HEX)
        
        Returns:
            渐变图像
        """
        img = Image.new('RGB', (width, height))
        
        rgb1 = cls.hex_to_rgb(color1)
        rgb2 = cls.hex_to_rgb(color2)
        
        center_x, center_y = width // 2, height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(height):
            for x in range(width):
                dx, dy = x - center_x, y - center_y
                distance = math.sqrt(dx**2 + dy**2)
                factor = min(distance / max_radius, 1.0)
                color = cls.interpolate_color(rgb1, rgb2, factor)
                img.putpixel((x, y), color)
        
        return img
    
    @staticmethod
    def generate_hexagon_grid(
        width: int,
        height: int,
        hex_size: int = 30,
        line_width: int = 2,
        color: str = "#FFFFFF",
        opacity: float = 0.1
    ) -> Image.Image:
        """
        生成六角形网格
        
        Args:
            width: 宽度
            height: 高度
            hex_size: 六角形半径
            line_width: 线宽
            color: 颜色 (HEX)
            opacity: 透明度
        
        Returns:
            带透明通道的图像
        """
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        rgb = BackgroundGenerator.hex_to_rgb(color)
        rgba = rgb + (int(255 * opacity),)
        
        # 六角形几何参数
        h = hex_size * math.sqrt(3)
        
        for row in range(-1, int(height / h) + 2):
            for col in range(-1, int(width / (1.5 * hex_size)) + 2):
                x = col * 1.5 * hex_size
                y = row * h + (h / 2 if col % 2 else 0)
                
                # 绘制六角形
                points = []
                for i in range(6):
                    angle = math.pi / 3 * i
                    px = x + hex_size * math.cos(angle)
                    py = y + hex_size * math.sin(angle)
                    points.append((px, py))
                
                draw.polygon(points, outline=rgba, width=line_width)
        
        return img
    
    @staticmethod
    def add_noise(img: Image.Image, intensity: float = 0.05) -> Image.Image:
        """
        添加噪点到图像
        
        Args:
            img: 原图像
            intensity: 噪点强度 (0.0-1.0)
        
        Returns:
            添加噪点后的图像
        """
        img_array = img.copy()
        width, height = img_array.size
        
        for _ in range(int(width * height * intensity)):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            # 随机添加亮或暗的点
            if random.random() > 0.5:
                noise_color = (255, 255, 255, int(random.random() * 50))
            else:
                noise_color = (0, 0, 0, int(random.random() * 50))
            
            if img_array.mode == 'RGBA':
                current = img_array.getpixel((x, y))
                img_array.putpixel((x, y), noise_color)
        
        return img_array
    
    @staticmethod
    def apply_glow(
        img: Image.Image,
        radius: int = 20,
        color: Optional[str] = None
    ) -> Image.Image:
        """
        添加外发光效果
        
        Args:
            img: 原图像
            radius: 发光半径
            color: 发光颜色 (HEX)，None 则使用图像自身颜色
        
        Returns:
            添加发光后的图像
        """
        # 创建发光层
        glow = img.copy()
        
        # 应用高斯模糊
        glow = glow.filter(ImageFilter.GaussianBlur(radius))
        
        # 创建输出图像
        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(glow, (0, 0))
        result.paste(img, (0, 0), img if img.mode == 'RGBA' else None)
        
        return result
