"""
缓存管理器
实现多级缓存策略，减少 API 请求频率
"""
import time
from typing import Optional, Any, Dict
from collections import OrderedDict


class CacheManager:
    """内存缓存管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化缓存管理器
        
        Args:
            config: 缓存配置
        """
        self.enabled = config.get('enabled', True)
        self.user_info_ttl = config.get('user_info_ttl', 300)
        self.summary_ttl = config.get('summary_ttl', 300)
        self.leaderboard_ttl = config.get('leaderboard_ttl', 600)
        self.server_stats_ttl = config.get('server_stats_ttl', 60)
        self.max_memory_mb = config.get('max_memory_mb', 100)
        
        # LRU 缓存存储
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._max_items = 1000  # 最大缓存项数
    
    def _is_expired(self, cache_data: Dict[str, Any]) -> bool:
        """检查缓存是否过期"""
        if 'expire_time' not in cache_data:
            return True
        return time.time() > cache_data['expire_time']
    
    def _get_cache_key(self, cache_type: str, key: str) -> str:
        """生成缓存键"""
        return f"{cache_type}:{key}"
    
    def _evict_if_needed(self):
        """如果缓存过多，驱逐最旧的项"""
        while len(self._cache) > self._max_items:
            self._cache.popitem(last=False)  # 删除最旧的项
    
    def get(self, cache_type: str, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            cache_type: 缓存类型 (user/league/40l/blitz/leaderboard/stats)
            key: 缓存键
            
        Returns:
            缓存的值，如果不存在或已过期则返回 None
        """
        if not self.enabled:
            return None
        
        cache_key = self._get_cache_key(cache_type, key)
        
        if cache_key not in self._cache:
            return None
        
        cache_data = self._cache[cache_key]
        
        # 检查是否过期
        if self._is_expired(cache_data):
            del self._cache[cache_key]
            return None
        
        # 移到末尾（LRU）
        self._cache.move_to_end(cache_key)
        
        return cache_data.get('value')
    
    def set(self, cache_type: str, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存
        
        Args:
            cache_type: 缓存类型
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），如果不指定则使用默认值
        """
        if not self.enabled:
            return
        
        # 根据类型确定 TTL
        if ttl is None:
            if cache_type == 'user':
                ttl = self.user_info_ttl
            elif cache_type in ['league', '40l', 'blitz', 'qp']:
                ttl = self.summary_ttl
            elif cache_type == 'leaderboard':
                ttl = self.leaderboard_ttl
            elif cache_type == 'stats':
                ttl = self.server_stats_ttl
            else:
                ttl = 300  # 默认 5 分钟
        
        cache_key = self._get_cache_key(cache_type, key)
        expire_time = time.time() + float(ttl)
        
        self._cache[cache_key] = {
            'value': value,
            'expire_time': expire_time,
            'created_time': time.time()
        }
        
        # 移到末尾
        self._cache.move_to_end(cache_key)
        
        # 检查是否需要驱逐
        self._evict_if_needed()
    
    def delete(self, cache_type: str, key: str):
        """
        删除缓存
        
        Args:
            cache_type: 缓存类型
            key: 缓存键
        """
        cache_key = self._get_cache_key(cache_type, key)
        if cache_key in self._cache:
            del self._cache[cache_key]
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
    
    def clear_expired(self):
        """清除所有过期的缓存"""
        expired_keys = []
        for key, data in self._cache.items():
            if self._is_expired(data):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            包含缓存统计的字典
        """
        total = len(self._cache)
        expired = sum(1 for data in self._cache.values() if self._is_expired(data))
        
        return {
            'total_items': total,
            'expired_items': expired,
            'active_items': total - expired,
            'max_items': self._max_items,
            'enabled': self.enabled
        }
