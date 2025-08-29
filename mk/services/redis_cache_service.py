import json
import redis
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RedisCacheService:
    """Redis缓存服务，用于管理Etsy数据的缓存和同步"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.cache_timeout = 3600 * 24  # 24小时缓存过期时间
        self.batch_size = 1000  # 批量操作大小
    
    def get_cache_key(self, model_name: str, action: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = ['etsy', model_name, action]
        for key, value in kwargs.items():
            if value is not None:
                key_parts.append(f"{key}:{value}")
        return ":".join(key_parts)
    
    def set_cache(self, key: str, data: Any, timeout: int = None) -> bool:
        """设置缓存"""
        try:
            if timeout is None:
                timeout = self.cache_timeout
            
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data, ensure_ascii=False, default=str)
            else:
                serialized_data = str(data)
            
            return self.redis_client.setex(key, timeout, serialized_data)
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def get_cache(self, key: str) -> Any:
        """获取缓存"""
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def clear_model_cache(self, model_name: str) -> bool:
        """清除指定模型的所有缓存"""
        try:
            pattern = f"etsy:{model_name}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except Exception as e:
            logger.error(f"清除模型缓存失败: {e}")
            return False
    
    def set_list_cache(self, model_name: str, filters: Dict = None, data: List = None, 
                      page: int = 1, page_size: int = 20) -> bool:
        """设置列表缓存"""
        key = self.get_cache_key(model_name, 'list', page=page, page_size=page_size, **filters or {})
        return self.set_cache(key, data)
    
    def get_list_cache(self, model_name: str, filters: Dict = None, 
                      page: int = 1, page_size: int = 20) -> Optional[List]:
        """获取列表缓存"""
        key = self.get_cache_key(model_name, 'list', page=page, page_size=page_size, **filters or {})
        return self.get_cache(key)
    
    def set_detail_cache(self, model_name: str, obj_id: int, data: Dict) -> bool:
        """设置详情缓存"""
        key = self.get_cache_key(model_name, 'detail', id=obj_id)
        return self.set_cache(key, data)
    
    def get_detail_cache(self, model_name: str, obj_id: int) -> Optional[Dict]:
        """获取详情缓存"""
        key = self.get_cache_key(model_name, 'detail', id=obj_id)
        return self.set_cache(key, data)
    
    def set_statistics_cache(self, model_name: str, data: Dict) -> bool:
        """设置统计缓存"""
        key = self.get_cache_key(model_name, 'statistics')
        return self.set_cache(key, data, timeout=3600)  # 统计缓存1小时过期
    
    def get_statistics_cache(self, model_name: str) -> Optional[Dict]:
        """获取统计缓存"""
        key = self.get_cache_key(model_name, 'statistics')
        return self.get_cache(key)
    
    def invalidate_cache_on_update(self, model_name: str, obj_id: int = None) -> bool:
        """更新时使缓存失效"""
        try:
            # 清除列表缓存
            self.clear_model_cache(model_name)
            
            # 如果有具体对象ID，清除详情缓存
            if obj_id:
                detail_key = self.get_cache_key(model_name, 'detail', id=obj_id)
                self.delete_cache(detail_key)
            
            # 清除统计缓存
            stats_key = self.get_cache_key(model_name, 'statistics')
            self.delete_cache(stats_key)
            
            return True
        except Exception as e:
            logger.error(f"使缓存失效失败: {e}")
            return False
    
    def batch_set_cache(self, model_name: str, data_list: List[Dict], 
                       action: str = 'list') -> bool:
        """批量设置缓存"""
        try:
            pipe = self.redis_client.pipeline()
            
            for i, data in enumerate(data_list):
                if i % self.batch_size == 0:
                    pipe.execute()
                    pipe = self.redis_client.pipeline()
                
                key = self.get_cache_key(model_name, action, id=data.get('id', i))
                serialized_data = json.dumps(data, ensure_ascii=False, default=str)
                pipe.setex(key, self.cache_timeout, serialized_data)
            
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"批量设置缓存失败: {e}")
            return False
    
    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        try:
            info = self.redis_client.info()
            return {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"获取缓存信息失败: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """计算缓存命中率"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return False


# 全局缓存服务实例
redis_cache = RedisCacheService()
