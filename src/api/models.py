"""
TETR.IO API 数据模型
定义所有 API 响应的数据结构
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Badge:
    """徽章数据"""
    id: str
    label: str
    desc: str
    group: Optional[str] = None
    ts: Optional[str] = None


@dataclass
class Connections:
    """社交连接数据"""
    discord: Optional[Dict[str, str]] = None
    twitch: Optional[Dict[str, str]] = None
    twitter: Optional[Dict[str, str]] = None
    reddit: Optional[Dict[str, str]] = None
    youtube: Optional[Dict[str, str]] = None
    steam: Optional[Dict[str, str]] = None


@dataclass
class UserInfo:
    """用户基础信息"""
    user_id: str
    username: str
    role: str
    country: Optional[str] = None
    xp: float = 0.0
    gametime: float = 0.0
    gamesplayed: int = -1
    gameswon: int = -1
    badges: List[Badge] = field(default_factory=list)
    supporter: bool = False
    supporter_tier: int = 0
    avatar_revision: Optional[int] = None
    banner_revision: Optional[int] = None
    bio: Optional[str] = None
    connections: Optional[Connections] = None
    friend_count: int = 0
    ar: int = 0
    ar_counts: Dict[str, int] = field(default_factory=dict)
    ts: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'UserInfo':
        """从 API 响应构建对象"""
        badges = [Badge(**b) for b in data.get('badges', [])]
        connections_data = data.get('connections', {})
        connections = Connections(**connections_data) if connections_data else None
        
        return cls(
            user_id=data.get('_id', ''),
            username=data.get('username', ''),
            role=data.get('role', 'user'),
            country=data.get('country'),
            xp=data.get('xp', 0.0),
            gametime=data.get('gametime', 0.0),
            gamesplayed=data.get('gamesplayed', -1),
            gameswon=data.get('gameswon', -1),
            badges=badges,
            supporter=data.get('supporter', False),
            supporter_tier=data.get('supporter_tier', 0),
            avatar_revision=data.get('avatar_revision'),
            banner_revision=data.get('banner_revision'),
            bio=data.get('bio'),
            connections=connections,
            friend_count=data.get('friend_count', 0),
            ar=data.get('ar', 0),
            ar_counts=data.get('ar_counts', {}),
            ts=data.get('ts')
        )


@dataclass
class LeagueData:
    """TETRA LEAGUE 数据"""
    rank: str
    tr: float = 0.0
    glicko: float = 0.0
    rd: float = 0.0
    apm: float = 0.0
    pps: float = 0.0
    vs: float = 0.0
    wins: int = 0
    losses: int = 0
    percentile: float = 0.0
    global_rank: int = -1
    local_rank: int = -1
    standing: int = -1
    standing_local: int = -1
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'LeagueData':
        """从 API 响应构建对象"""
        return cls(
            rank=data.get('rank', 'z'),
            tr=data.get('tr', 0.0) or 0.0,
            glicko=data.get('glicko', 0.0) or 0.0,
            rd=data.get('rd', 0.0) or 0.0,
            apm=data.get('apm', 0.0) or 0.0,
            pps=data.get('pps', 0.0) or 0.0,
            vs=data.get('vs', 0.0) or 0.0,
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            percentile=data.get('percentile', 0.0) or 0.0,
            global_rank=data.get('standing', -1) or -1,
            local_rank=data.get('standing_local', -1) or -1,
            standing=data.get('standing', -1) or -1,
            standing_local=data.get('standing_local', -1) or -1
        )
    
    @property
    def winrate(self) -> float:
        """计算胜率"""
        total = self.wins + self.losses
        if total == 0:
            return 0.0
        return (self.wins / total) * 100


@dataclass
class RecordData:
    """游戏记录数据 (40L, Blitz等)"""
    mode: str
    value: float = 0.0  # 时间(秒) 或 分数
    rank: int = -1
    local_rank: int = -1
    pieces: int = 0
    pps: float = 0.0
    finesse: Optional[float] = None
    kpp: Optional[float] = None
    kps: Optional[float] = None
    level: Optional[int] = None
    spp: Optional[float] = None
    timestamp: Optional[str] = None
    
    @classmethod
    def from_api(cls, mode: str, data: Optional[Dict[str, Any]], rank_data: Optional[Dict[str, Any]] = None) -> Optional['RecordData']:
        """从 API 响应构建对象"""
        if not data or not data.get('record'):
            return None
        
        record = data['record']
        endctx = record.get('endcontext', {})
        
        # 40L 和 Blitz 的主要值不同
        if mode == '40l':
            value = endctx.get('finalTime', 0) / 1000  # 毫秒转秒
        elif mode == 'blitz':
            value = endctx.get('score', 0)
        else:
            value = 0.0
        
        return cls(
            mode=mode,
            value=value,
            rank=data.get('rank', -1) or -1,
            local_rank=data.get('rank_local', -1) or -1,
            pieces=endctx.get('piecesplaced', 0),
            pps=endctx.get('pps', 0.0) or 0.0,
            finesse=endctx.get('finesse', {}).get('percentage'),
            kpp=endctx.get('kpp'),
            kps=endctx.get('kps'),
            level=endctx.get('level'),
            spp=endctx.get('spp'),
            timestamp=record.get('ts')
        )


@dataclass
class QuickPlayData:
    """QUICK PLAY 数据"""
    record: Optional[Dict[str, Any]] = None
    rank: int = -1
    local_rank: int = -1
    best_record: Optional[Dict[str, Any]] = None
    best_rank: int = -1
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'QuickPlayData':
        """从 API 响应构建对象"""
        best = data.get('best', {})
        return cls(
            record=data.get('record'),
            rank=data.get('rank', -1) or -1,
            local_rank=data.get('rank_local', -1) or -1,
            best_record=best.get('record'),
            best_rank=best.get('rank', -1) or -1
        )


@dataclass
class ServerStats:
    """服务器统计数据"""
    usercount: int = 0
    usercount_delta: float = 0.0
    anoncount: int = 0
    totalaccounts: int = 0
    rankedcount: int = 0
    recordcount: int = 0
    gamesplayed: int = 0
    gamesplayed_delta: float = 0.0
    gamesfinished: int = 0
    gametime: float = 0.0
    inputs: int = 0
    piecesplaced: int = 0
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'ServerStats':
        """从 API 响应构建对象"""
        return cls(
            usercount=data.get('usercount', 0),
            usercount_delta=data.get('usercount_delta', 0.0),
            anoncount=data.get('anoncount', 0),
            totalaccounts=data.get('totalaccounts', 0),
            rankedcount=data.get('rankedcount', 0),
            recordcount=data.get('recordcount', 0),
            gamesplayed=data.get('gamesplayed', 0),
            gamesplayed_delta=data.get('gamesplayed_delta', 0.0),
            gamesfinished=data.get('gamesfinished', 0),
            gametime=data.get('gametime', 0.0),
            inputs=data.get('inputs', 0),
            piecesplaced=data.get('piecesplaced', 0)
        )


@dataclass
class LeaderboardEntry:
    """排行榜条目"""
    rank: int
    username: str
    user_id: str
    country: Optional[str] = None
    tr: Optional[float] = None
    value: Optional[float] = None  # 时间或分数
    rank_label: Optional[str] = None  # 段位标识
    
    @classmethod
    def from_api(cls, rank: int, data: Dict[str, Any], mode: str) -> 'LeaderboardEntry':
        """从 API 响应构建对象"""
        # 根据模式提取不同的值
        if mode == 'league':
            value = data.get('tr', 0.0)
            rank_label = data.get('rank', 'z')
        elif mode == '40l':
            record = data.get('record', {})
            endctx = record.get('endcontext', {})
            value = endctx.get('finalTime', 0) / 1000
            rank_label = None
        elif mode == 'blitz':
            record = data.get('record', {})
            endctx = record.get('endcontext', {})
            value = endctx.get('score', 0)
            rank_label = None
        elif mode == 'xp':
            value = data.get('xp', 0.0)
            rank_label = None
        elif mode == 'ar':
            value = data.get('ar', 0)
            rank_label = None
        else:
            value = None
            rank_label = None
        
        return cls(
            rank=rank,
            username=data.get('username', ''),
            user_id=data.get('_id', ''),
            country=data.get('country'),
            tr=data.get('tr'),
            value=value,
            rank_label=rank_label
        )
