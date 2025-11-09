"""
API 模块
提供 TETR.IO API 客户端和数据模型
"""
from .client import TETRIOAPIClient
from .models import (
    UserInfo, LeagueData, RecordData, QuickPlayData,
    ServerStats, LeaderboardEntry, Badge, Connections
)

__all__ = [
    'TETRIOAPIClient',
    'UserInfo',
    'LeagueData',
    'RecordData',
    'QuickPlayData',
    'ServerStats',
    'LeaderboardEntry',
    'Badge',
    'Connections'
]
