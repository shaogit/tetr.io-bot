"""
TETR.IO AstrBot 插件
提供 TETR.IO 游戏数据查询功能
"""
import yaml
from pathlib import Path
from typing import Optional

# AstrBot imports (这些在实际插件环境中可用)
try:
    from astrbot.api.event import filter, AstrMessageEvent
    from astrbot.api.star import Context, Star, register
    from astrbot.api import logger
    from astrbot.api import message_components as Comp
except ImportError:
    # 开发环境下的模拟
    class logger:
        @staticmethod
        def info(msg): print(f"[INFO] {msg}")
        @staticmethod
        def warning(msg): print(f"[WARNING] {msg}")
        @staticmethod
        def error(msg): print(f"[ERROR] {msg}")
        @staticmethod
        def debug(msg): print(f"[DEBUG] {msg}")
    
    # 模拟装饰器
    def register(*args, **kwargs):
        def decorator(cls):
            return cls
        return decorator
    
    class filter:
        @staticmethod
        def command(name):
            def decorator(func):
                return func
            return decorator
        
        @staticmethod
        def command_group(name):
            def decorator(func):
                return func
            return decorator

# 导入本地模块
from src.api import TETRIOAPIClient
from src.cache import CacheManager
from src.render import ImageRenderer
from src.utils import I18n, validate_username, validate_mode


@register(
    "astrbot_plugin_tetrio",
    "AstrBot Community",
    "TETR.IO 数据查询插件 - 查询用户信息、排行榜、游戏记录等",
    "1.0.0",
    "https://github.com/yourusername/astrbot-plugin-tetrio"
)
class TETRIOPlugin(Star):
    """TETR.IO 插件主类"""
    
    def __init__(self, context: Context):
        """初始化插件"""
        super().__init__(context)
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化组件
        self.api_client = TETRIOAPIClient(self.config.get('api', {}))
        self.cache_manager = CacheManager(self.config.get('cache', {}))
        self.renderer = ImageRenderer(self.config.get('render', {}))
        self.i18n = I18n(self.config.get('display', {}).get('language', 'zh_CN'))
        
        logger.info("TETR.IO 插件初始化成功")
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        config_file = Path("config/default_config.yaml")
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # 返回默认配置
        return {
            'api': {
                'base_url': 'https://ch.tetr.io/api',
                'timeout': 10,
                'retry_times': 3
            },
            'cache': {
                'enabled': True
            },
            'render': {
                'default_width': 800,
                'image_format': 'png',
                'image_quality': 85
            }
        }
    
    # ========== 用户查询指令 ==========
    
    @filter.command("tetr")
    async def tetr_help(self, event: AstrMessageEvent):
        """TETR.IO 插件帮助信息"""
        help_text = """
🎮 TETR.IO 数据查询插件

📋 可用指令：
/tetr user <用户名> - 查询用户完整信息
/tetr league <用户名> - 查询 TETRA LEAGUE 数据
/tetr 40l <用户名> - 查询 40 LINES 数据
/tetr blitz <用户名> - 查询 BLITZ 数据
/tetr lb <模式> [条数] - 查询排行榜
/tetr stats - 查询服务器统计
/tetr search <关键词> - 搜索用户

示例：
/tetr user folx
/tetr lb league 10
        """
        yield event.plain_result(help_text.strip())
    
    @filter.command("tetr user")
    async def query_user(self, event: AstrMessageEvent, username: str):
        """
        查询用户完整信息
        
        用法: /tetr user <用户名>
        """
        try:
            # 验证用户名
            if not validate_username(username):
                yield event.plain_result("❌ 用户名格式不正确（3-16个字符，仅限字母数字下划线）")
                return
            
            logger.info(f"查询用户: {username}")
            
            # 检查缓存
            cached_user = self.cache_manager.get('user', username.lower())
            cached_league = self.cache_manager.get('league', username.lower())
            
            if cached_user and cached_league is not None:
                user_info = cached_user
                league_data = cached_league
                logger.debug(f"使用缓存数据: {username}")
            else:
                # 从 API 获取
                user_info = await self.api_client.get_user_info(username)
                league_data = await self.api_client.get_user_league(username)
                
                # 缓存数据
                self.cache_manager.set('user', username.lower(), user_info)
                self.cache_manager.set('league', username.lower(), league_data)
            
            # 渲染图片
            img_bytes = self.renderer.render_user_card(user_info, league_data)
            
            # 发送图片
            yield event.message_result([
                Comp.Plain(f"✅ 用户 {user_info.username} 的数据：\n"),
                Comp.Image(file=img_bytes)
            ])
        
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            error_msg = str(e)
            if "资源不存在" in error_msg or "404" in error_msg:
                yield event.plain_result(f"❌ 未找到用户 {username}")
            else:
                yield event.plain_result(f"❌ 查询失败: {error_msg}")
    
    @filter.command("tetr u")
    async def query_user_short(self, event: AstrMessageEvent, username: str):
        """
        查询用户信息（简化指令）
        
        用法: /tetr u <用户名>
        """
        async for result in self.query_user(event, username):
            yield result
    
    # ========== 游戏模式查询指令 ==========
    
    @filter.command("tetr league")
    async def query_league(self, event: AstrMessageEvent, username: str):
        """
        查询 TETRA LEAGUE 数据
        
        用法: /tetr league <用户名>
        """
        try:
            logger.info(f"查询 League 数据: {username}")
            
            # 获取数据
            user_info = await self.api_client.get_user_info(username)
            league_data = await self.api_client.get_user_league(username)
            
            if not league_data:
                yield event.plain_result(f"❌ 用户 {username} 没有 TETRA LEAGUE 数据")
                return
            
            # 渲染并发送
            img_bytes = self.renderer.render_user_card(user_info, league_data)
            yield event.message_result([
                Comp.Plain(f"✅ {user_info.username} 的 TETRA LEAGUE 数据：\n"),
                Comp.Image(file=img_bytes)
            ])
        
        except Exception as e:
            logger.error(f"查询 League 失败: {e}")
            yield event.plain_result(f"❌ 查询失败: {str(e)}")
    
    # ========== 排行榜查询指令 ==========
    
    @filter.command("tetr lb")
    async def query_leaderboard(self, event: AstrMessageEvent, mode: str, limit: int = 10):
        """
        查询排行榜
        
        用法: /tetr lb <模式> [条数]
        模式: league, 40l, blitz, xp, ar
        """
        try:
            # 验证模式
            if not validate_mode(mode):
                yield event.plain_result("❌ 不支持的游戏模式\n支持的模式: league, 40l, blitz, xp, ar")
                return
            
            # 限制条数
            limit = max(1, min(limit, 25))
            
            logger.info(f"查询排行榜: {mode}, 限制 {limit} 条")
            
            # 检查缓存
            cache_key = f"{mode}_{limit}"
            cached_lb = self.cache_manager.get('leaderboard', cache_key)
            
            if cached_lb:
                entries = cached_lb
                logger.debug(f"使用缓存的排行榜数据: {cache_key}")
            else:
                # 从 API 获取
                entries = await self.api_client.get_leaderboard(mode, limit)
                self.cache_manager.set('leaderboard', cache_key, entries)
            
            # 渲染图片
            img_bytes = self.renderer.render_leaderboard(entries, mode, limit)
            
            # 发送
            yield event.message_result([
                Comp.Plain(f"✅ {mode.upper()} 排行榜 - 前 {limit} 名：\n"),
                Comp.Image(file=img_bytes)
            ])
        
        except Exception as e:
            logger.error(f"查询排行榜失败: {e}")
            yield event.plain_result(f"❌ 查询失败: {str(e)}")
    
    @filter.command("tetr leaderboard")
    async def query_leaderboard_long(self, event: AstrMessageEvent, mode: str, limit: int = 10):
        """查询排行榜（完整指令）"""
        async for result in self.query_leaderboard(event, mode, limit):
            yield result
    
    # ========== 服务器统计指令 ==========
    
    @filter.command("tetr stats")
    async def query_stats(self, event: AstrMessageEvent):
        """
        查询服务器统计
        
        用法: /tetr stats
        """
        try:
            logger.info("查询服务器统计")
            
            # 检查缓存
            cached_stats = self.cache_manager.get('stats', 'server')
            
            if cached_stats:
                stats = cached_stats
                logger.debug("使用缓存的统计数据")
            else:
                stats = await self.api_client.get_server_stats()
                self.cache_manager.set('stats', 'server', stats)
            
            # 渲染图片
            img_bytes = self.renderer.render_server_stats(stats)
            
            # 发送
            yield event.message_result([
                Comp.Plain("✅ TETR.IO 服务器统计：\n"),
                Comp.Image(file=img_bytes)
            ])
        
        except Exception as e:
            logger.error(f"查询统计失败: {e}")
            yield event.plain_result(f"❌ 查询失败: {str(e)}")
    
    # ========== 搜索指令 ==========
    
    @filter.command("tetr search")
    async def search_user(self, event: AstrMessageEvent, query: str):
        """
        搜索用户
        
        用法: /tetr search <关键词>
        """
        try:
            logger.info(f"搜索用户: {query}")
            
            results = await self.api_client.search_user(query)
            
            if not results:
                yield event.plain_result(f"❌ 未找到匹配 '{query}' 的用户")
                return
            
            # 格式化结果
            result_text = f"🔍 找到 {len(results)} 个匹配的用户：\n\n"
            
            for i, user in enumerate(results[:10], 1):
                username = user.get('username', 'Unknown')
                xp = user.get('xp', 0)
                country = user.get('country', '')
                
                result_text += f"{i}. {username}"
                if country:
                    result_text += f" [{country}]"
                result_text += f" - XP: {xp:,.0f}\n"
            
            yield event.plain_result(result_text.strip())
        
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            yield event.plain_result(f"❌ 搜索失败: {str(e)}")
    
    # ========== 插件生命周期 ==========
    
    async def terminate(self):
        """插件卸载时调用"""
        logger.info("正在关闭 TETR.IO 插件...")
        
        # 关闭 API 客户端
        await self.api_client.close()
        
        # 清理缓存
        self.cache_manager.clear()
        
        logger.info("TETR.IO 插件已关闭")
