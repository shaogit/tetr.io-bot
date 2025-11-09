"""
TETR.IO API 客户端
封装所有 TETR.IO API 调用
"""
import aiohttp
import asyncio
from typing import Optional, List, Dict, Any
from astrbot.api import logger
from .models import (
    UserInfo, LeagueData, RecordData, QuickPlayData,
    ServerStats, LeaderboardEntry
)


class TETRIOAPIClient:
    """TETR.IO API 客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 API 客户端
        
        Args:
            config: 配置字典
        """
        self.base_url = config.get('base_url', 'https://ch.tetr.io/api')
        self.timeout = config.get('timeout', 10)
        self.retry_times = config.get('retry_times', 3)
        self.user_agent = config.get('user_agent', 'AstrBot-TETRIO-Plugin/1.0')
        self.session_id = self._generate_session_id()
        self._session: Optional[aiohttp.ClientSession] = None
    
    def _generate_session_id(self) -> str:
        """生成唯一会话 ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    'User-Agent': self.user_agent,
                    'X-Session-ID': self.session_id
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session
    
    async def close(self):
        """关闭 HTTP 会话"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _request(self, endpoint: str, retry: int = 0) -> Dict[str, Any]:
        """
        发送 HTTP 请求
        
        Args:
            endpoint: API 端点
            retry: 当前重试次数
            
        Returns:
            API 响应数据
            
        Raises:
            Exception: 请求失败
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        return data
                    else:
                        error = data.get('error', {})
                        raise Exception(f"API 返回错误: {error.get('msg', 'Unknown error')}")
                elif response.status == 404:
                    raise Exception("资源不存在")
                elif response.status == 429:
                    if retry < self.retry_times:
                        # 等待后重试
                        wait_time = 2 ** retry
                        logger.warning(f"API 限流，{wait_time}秒后重试 ({retry + 1}/{self.retry_times})")
                        await asyncio.sleep(wait_time)
                        return await self._request(endpoint, retry + 1)
                    else:
                        raise Exception("API 请求频率过高，请稍后再试")
                else:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
        
        except aiohttp.ClientError as e:
            if retry < self.retry_times:
                wait_time = 2 ** retry
                logger.warning(f"网络错误，{wait_time}秒后重试 ({retry + 1}/{self.retry_times}): {e}")
                await asyncio.sleep(wait_time)
                return await self._request(endpoint, retry + 1)
            else:
                raise Exception(f"网络连接失败: {e}")
        except asyncio.TimeoutError:
            if retry < self.retry_times:
                logger.warning(f"请求超时，重试中 ({retry + 1}/{self.retry_times})")
                return await self._request(endpoint, retry + 1)
            else:
                raise Exception("请求超时")
    
    async def get_user_info(self, username: str) -> UserInfo:
        """
        获取用户基础信息
        
        Args:
            username: 用户名或用户ID
            
        Returns:
            UserInfo 对象
        """
        logger.debug(f"正在查询用户: {username}")
        data = await self._request(f"users/{username.lower()}")
        user_data = data.get('data', {}).get('user', {})
        return UserInfo.from_api(user_data)
    
    async def get_user_league(self, username: str) -> Optional[LeagueData]:
        """
        获取用户 TETRA LEAGUE 数据
        
        Args:
            username: 用户名或用户ID
            
        Returns:
            LeagueData 对象，如果没有数据则返回 None
        """
        logger.debug(f"正在查询用户 League 数据: {username}")
        data = await self._request(f"users/{username.lower()}/summaries/league")
        league_data = data.get('data', {})
        
        if not league_data or league_data.get('record') is None:
            return None
        
        return LeagueData.from_api(league_data)
    
    async def get_user_40l(self, username: str) -> Optional[RecordData]:
        """
        获取用户 40 LINES 数据
        
        Args:
            username: 用户名或用户ID
            
        Returns:
            RecordData 对象，如果没有数据则返回 None
        """
        logger.debug(f"正在查询用户 40L 数据: {username}")
        data = await self._request(f"users/{username.lower()}/summaries/40l")
        return RecordData.from_api('40l', data.get('data'))
    
    async def get_user_blitz(self, username: str) -> Optional[RecordData]:
        """
        获取用户 BLITZ 数据
        
        Args:
            username: 用户名或用户ID
            
        Returns:
            RecordData 对象，如果没有数据则返回 None
        """
        logger.debug(f"正在查询用户 Blitz 数据: {username}")
        data = await self._request(f"users/{username.lower()}/summaries/blitz")
        return RecordData.from_api('blitz', data.get('data'))
    
    async def get_user_quickplay(self, username: str) -> Optional[QuickPlayData]:
        """
        获取用户 QUICK PLAY 数据
        
        Args:
            username: 用户名或用户ID
            
        Returns:
            QuickPlayData 对象，如果没有数据则返回 None
        """
        logger.debug(f"正在查询用户 Quick Play 数据: {username}")
        data = await self._request(f"users/{username.lower()}/summaries/zenith")
        qp_data = data.get('data', {})
        
        if not qp_data:
            return None
        
        return QuickPlayData.from_api(qp_data)
    
    async def get_server_stats(self) -> ServerStats:
        """
        获取服务器统计数据
        
        Returns:
            ServerStats 对象
        """
        logger.debug("正在查询服务器统计")
        data = await self._request("general/stats")
        stats_data = data.get('data', {})
        return ServerStats.from_api(stats_data)
    
    async def get_leaderboard(self, mode: str, limit: int = 10) -> List[LeaderboardEntry]:
        """
        获取排行榜
        
        Args:
            mode: 游戏模式 (league/40l/blitz/xp/ar)
            limit: 返回条数
            
        Returns:
            LeaderboardEntry 列表
        """
        logger.debug(f"正在查询 {mode} 排行榜，限制 {limit} 条")
        
        # 验证模式
        valid_modes = ['league', '40l', 'blitz', 'xp', 'ar']
        if mode not in valid_modes:
            raise ValueError(f"不支持的游戏模式: {mode}")
        
        # 限制条数
        limit = min(max(1, limit), 25)
        
        data = await self._request(f"users/by/{mode}?limit={limit}")
        entries_data = data.get('data', {}).get('entries', [])
        
        entries = []
        for idx, entry in enumerate(entries_data, 1):
            entries.append(LeaderboardEntry.from_api(idx, entry, mode))
        
        return entries
    
    async def search_user(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索用户
        
        Args:
            query: 搜索关键词
            
        Returns:
            用户列表
        """
        logger.debug(f"正在搜索用户: {query}")
        data = await self._request(f"users/search/{query}")
        users_data = data.get('data', {}).get('results', [])
        return users_data
