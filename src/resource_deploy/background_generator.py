"""
背景素材生成器

程序化生成基础纹理、光效、图案等背景素材
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
from typing import Tuple, List
import logging
import random
import math

logger = logging.getLogger(__name__)


class BackgroundGenerator:
    """背景素材生成器"""
    
    def __init__(self, target_dir: str):
        """
        初始化背景生成器
        
        Args:
            target_dir: 背景素材目标目录
        """
        self.target_dir = Path(target_dir)
        self.base_dir = self.target_dir / "base"
        self.effects_dir = self.target_dir / "effects"
        self.patterns_dir = self.target_dir / "patterns"
        self.gradients_dir = self.target_dir / "gradients"
        
    def generate_all(self) -> dict:
        """
        生成所有背景素材
        
        Returns:
            生成结果字典
        """
        results = {
            'base': {},
            'effects': {},
            'patterns': {},
            'gradients': {}
        }
        
        # 创建目录结构
        self._create_directories()
        
        # 生成基础纹理
        logger.info("生成基础纹理...")
        results['base']['carbon_fiber'] = self.generate_carbon_fiber()
        results['base']['hexagon_grid'] = self.generate_hexagon_grid()
        results['base']['tech_lines'] = self.generate_tech_lines()
        results['base']['circuit_pattern'] = self.generate_circuit_pattern()
        results['base']['noise_texture'] = self.generate_noise_texture()
        
        # 生成光效素材
        logger.info("生成光效素材...")
        results['effects']['radial_glow'] = self.generate_radial_glow()
        results['effects']['edge_light'] = self.generate_edge_light()
        results['effects']['sparkle'] = self.generate_sparkle()
        results['effects']['lens_flare'] = self.generate_lens_flare()
        
        # 生成装饰图案
        logger.info("生成装饰图案...")
        results['patterns']['grid_overlay'] = self.generate_grid_overlay()
        results['patterns']['corner_decorations'] = self.generate_corner_decorations()
        
        return results
    
    def _create_directories(self):
        """创建必需的子目录"""
        for directory in [self.base_dir, self.effects_dir, self.patterns_dir, self.gradients_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_carbon_fiber(self) -> bool:
        """生成碳纤维纹理 (512x512)"""
        try:
            size = (512, 512)
            img = Image.new('RGB', size, color=(10, 10, 10))
            draw = ImageDraw.Draw(img)
            
            # 绘制交叉线条模拟碳纤维
            line_width = 2
            spacing = 8
            
            # 第一层线条（45度）
            for i in range(0, size[0] + size[1], spacing):
                draw.line([(i, 0), (0, i)], fill=(20, 20, 20), width=line_width)
            
            # 第二层线条（135度）
            for i in range(-size[1], size[0], spacing):
                draw.line([(i, 0), (size[0], size[0] - i)], fill=(15, 15, 15), width=line_width)
            
            # 添加噪点
            pixels = np.array(img)
            noise = np.random.randint(-5, 5, pixels.shape, dtype=np.int16)
            pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(pixels)
            
            # 轻微模糊
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            output_path = self.base_dir / "carbon_fiber.png"
            img.save(output_path)
            logger.info(f"✓ 生成碳纤维纹理: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成碳纤维纹理失败: {e}")
            return False
    
    def generate_hexagon_grid(self) -> bool:
        """生成六角网格 (512x512)"""
        try:
            size = (512, 512)
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            hex_size = 30
            line_color = (0, 120, 180, 100)
            line_width = 2
            
            # 计算六角形顶点
            def hexagon_points(center_x, center_y, size):
                points = []
                for i in range(6):
                    angle = math.pi / 3 * i
                    x = center_x + size * math.cos(angle)
                    y = center_y + size * math.sin(angle)
                    points.append((x, y))
                return points
            
            # 绘制六角网格
            rows = int(size[1] / (hex_size * 1.5)) + 2
            cols = int(size[0] / (hex_size * math.sqrt(3))) + 2
            
            for row in range(rows):
                for col in range(cols):
                    x = col * hex_size * math.sqrt(3)
                    y = row * hex_size * 1.5
                    
                    # 偏移奇数行
                    if row % 2 == 1:
                        x += hex_size * math.sqrt(3) / 2
                    
                    points = hexagon_points(x, y, hex_size)
                    draw.polygon(points, outline=line_color, width=line_width)
            
            output_path = self.base_dir / "hexagon_grid.png"
            img.save(output_path)
            logger.info(f"✓ 生成六角网格: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成六角网格失败: {e}")
            return False
    
    def generate_tech_lines(self) -> bool:
        """生成科技线条 (512x512)"""
        try:
            size = (512, 512)
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 随机生成科技感线条
            for _ in range(30):
                x1 = random.randint(0, size[0])
                y1 = random.randint(0, size[1])
                
                # 水平或垂直线条
                if random.random() > 0.5:
                    x2 = random.randint(x1, min(x1 + 150, size[0]))
                    y2 = y1
                else:
                    x2 = x1
                    y2 = random.randint(y1, min(y1 + 150, size[1]))
                
                # 随机颜色（蓝色系）
                color = (0, random.randint(100, 255), random.randint(200, 255), random.randint(50, 150))
                width = random.randint(1, 3)
                
                draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
                
                # 在端点绘制小圆点
                radius = 3
                draw.ellipse([x1-radius, y1-radius, x1+radius, y1+radius], fill=color)
                draw.ellipse([x2-radius, y2-radius, x2+radius, y2+radius], fill=color)
            
            # 添加发光效果
            img = img.filter(ImageFilter.GaussianBlur(radius=1))
            
            output_path = self.base_dir / "tech_lines.png"
            img.save(output_path)
            logger.info(f"✓ 生成科技线条: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成科技线条失败: {e}")
            return False
    
    def generate_circuit_pattern(self) -> bool:
        """生成电路板图案 (512x512)"""
        try:
            size = (512, 512)
            img = Image.new('RGB', size, color=(5, 15, 10))
            draw = ImageDraw.Draw(img)
            
            line_color = (0, 180, 100)
            dot_color = (0, 255, 150)
            
            # 绘制电路线
            grid_size = 40
            for x in range(0, size[0], grid_size):
                for y in range(0, size[1], grid_size):
                    # 随机决定线条方向
                    if random.random() > 0.5:
                        # 横向
                        end_x = x + grid_size
                        draw.line([(x, y), (end_x, y)], fill=line_color, width=2)
                    
                    if random.random() > 0.5:
                        # 纵向
                        end_y = y + grid_size
                        draw.line([(x, y), (x, end_y)], fill=line_color, width=2)
                    
                    # 焊点
                    if random.random() > 0.7:
                        radius = 3
                        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=dot_color)
            
            output_path = self.base_dir / "circuit_pattern.png"
            img.save(output_path)
            logger.info(f"✓ 生成电路板图案: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成电路板图案失败: {e}")
            return False
    
    def generate_noise_texture(self) -> bool:
        """生成噪点纹理 (512x512)"""
        try:
            size = (512, 512)
            
            # 生成随机噪声
            noise = np.random.randint(0, 50, (size[1], size[0], 3), dtype=np.uint8)
            img = Image.fromarray(noise)
            
            # 模糊处理
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            
            output_path = self.base_dir / "noise_texture.png"
            img.save(output_path)
            logger.info(f"✓ 生成噪点纹理: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成噪点纹理失败: {e}")
            return False
    
    def generate_radial_glow(self) -> bool:
        """生成径向光晕 (1920x1080)"""
        try:
            size = (1920, 1080)
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            center_x, center_y = size[0] // 2, size[1] // 2
            max_radius = int(math.sqrt(center_x**2 + center_y**2))
            
            # 绘制径向渐变
            for radius in range(max_radius, 0, -10):
                alpha = int(255 * (1 - radius / max_radius) * 0.5)
                color = (0, 200, 255, alpha)
                draw.ellipse([
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius
                ], fill=color)
            
            # 高斯模糊
            img = img.filter(ImageFilter.GaussianBlur(radius=50))
            
            output_path = self.effects_dir / "radial_glow.png"
            img.save(output_path)
            logger.info(f"✓ 生成径向光晕: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成径向光晕失败: {e}")
            return False
    
    def generate_edge_light(self) -> bool:
        """生成边缘光 (1920x1080)"""
        try:
            size = (1920, 1080)
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 边缘渐变宽度
            edge_width = 200
            
            # 顶部边缘光
            for i in range(edge_width):
                alpha = int(150 * (1 - i / edge_width))
                color = (0, 150, 255, alpha)
                draw.line([(0, i), (size[0], i)], fill=color, width=1)
            
            # 底部边缘光
            for i in range(edge_width):
                y = size[1] - i - 1
                alpha = int(150 * (1 - i / edge_width))
                color = (0, 150, 255, alpha)
                draw.line([(0, y), (size[0], y)], fill=color, width=1)
            
            # 模糊
            img = img.filter(ImageFilter.GaussianBlur(radius=30))
            
            output_path = self.effects_dir / "edge_light.png"
            img.save(output_path)
            logger.info(f"✓ 生成边缘光: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成边缘光失败: {e}")
            return False
    
    def generate_sparkle(self) -> bool:
        """生成星光闪烁 (512x512)"""
        try:
            size = (512, 512)
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 生成多个星光点
            for _ in range(50):
                x = random.randint(0, size[0])
                y = random.randint(0, size[1])
                star_size = random.randint(2, 8)
                
                # 十字星形
                color = (255, 255, 255, random.randint(100, 255))
                draw.line([(x - star_size, y), (x + star_size, y)], fill=color, width=2)
                draw.line([(x, y - star_size), (x, y + star_size)], fill=color, width=2)
            
            # 模糊
            img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
            
            output_path = self.effects_dir / "sparkle.png"
            img.save(output_path)
            logger.info(f"✓ 生成星光闪烁: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成星光闪烁失败: {e}")
            return False
    
    def generate_lens_flare(self) -> bool:
        """生成镜头光晕 (1920x1080)"""
        try:
            size = (1920, 1080)
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            center_x, center_y = size[0] // 3, size[1] // 3
            
            # 主光源
            for radius in range(200, 0, -5):
                alpha = int(100 * (1 - radius / 200))
                color = (255, 200, 100, alpha)
                draw.ellipse([
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius
                ], fill=color)
            
            # 次级光斑
            for i in range(5):
                offset_x = center_x + i * 150
                offset_y = center_y + i * 80
                if offset_x < size[0] and offset_y < size[1]:
                    for radius in range(50, 0, -2):
                        alpha = int(50 * (1 - radius / 50))
                        color = (150, 150, 255, alpha)
                        draw.ellipse([
                            offset_x - radius, offset_y - radius,
                            offset_x + radius, offset_y + radius
                        ], fill=color)
            
            # 强模糊
            img = img.filter(ImageFilter.GaussianBlur(radius=40))
            
            output_path = self.effects_dir / "lens_flare.png"
            img.save(output_path)
            logger.info(f"✓ 生成镜头光晕: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成镜头光晕失败: {e}")
            return False
    
    def generate_grid_overlay(self) -> bool:
        """生成网格叠加层 (512x512)"""
        try:
            size = (512, 512)
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            grid_size = 32
            line_color = (100, 100, 100, 50)
            
            # 绘制垂直线
            for x in range(0, size[0], grid_size):
                draw.line([(x, 0), (x, size[1])], fill=line_color, width=1)
            
            # 绘制水平线
            for y in range(0, size[1], grid_size):
                draw.line([(0, y), (size[0], y)], fill=line_color, width=1)
            
            output_path = self.patterns_dir / "grid_overlay.png"
            img.save(output_path)
            logger.info(f"✓ 生成网格叠加层: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成网格叠加层失败: {e}")
            return False
    
    def generate_corner_decorations(self) -> bool:
        """生成角落装饰 (256x256)"""
        try:
            size = (256, 256)
            img = Image.new('RGBA', size, color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            color = (0, 200, 255, 200)
            
            # 左上角装饰
            # L形线条
            draw.line([(0, 50), (50, 50)], fill=color, width=3)
            draw.line([(50, 0), (50, 50)], fill=color, width=3)
            
            # 小装饰线
            for i in range(3):
                offset = i * 15 + 10
                draw.line([(0, offset), (offset, offset)], fill=color, width=2)
                draw.line([(offset, 0), (offset, offset)], fill=color, width=2)
            
            output_path = self.patterns_dir / "corner_decorations.png"
            img.save(output_path)
            logger.info(f"✓ 生成角落装饰: {output_path}")
            return True
        except Exception as e:
            logger.error(f"✗ 生成角落装饰失败: {e}")
            return False
