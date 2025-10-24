"""
告警通知器
负责将检测到的异常行为推送到Spring Boot后端
"""
import requests
import json
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertNotifier:
    """告警通知器"""
    
    def __init__(self, backend_url: str = "http://localhost:8080/api"):
        """
        初始化通知器
        
        参数:
            backend_url: Spring Boot后端地址
        """
        self.backend_url = backend_url
        self.alert_endpoint = f"{backend_url}/alerts/notify"
    
    def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        发送告警到后端
        
        参数:
            alert_data: 告警数据字典，包含以下字段：
                - user_id: 用户ID
                - record_id: 检测记录ID（可选）
                - alert_type: 告警类型（FALL, FIGHT, INTRUSION等）
                - alert_level: 告警级别（LOW, MEDIUM, HIGH, CRITICAL）
                - confidence: 置信度
                - description: 描述
                - detail_data: 详细数据（JSON字符串）
                - snapshot_path: 快照图片路径（可选）
        
        返回:
            是否发送成功
        """
        try:
            response = requests.post(
                self.alert_endpoint,
                json=alert_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"告警发送成功: {alert_data['alert_type']}")
                return True
            else:
                logger.error(f"告警发送失败: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"发送告警时发生错误: {str(e)}")
            return False
    
    def create_alert_from_detection(
        self,
        user_id: int,
        detection_result: Dict[str, Any],
        record_id: int = None,
        snapshot_path: str = None
    ) -> Dict[str, Any]:
        """
        从检测结果创建告警数据
        
        参数:
            user_id: 用户ID
            detection_result: 检测结果
            record_id: 记录ID
            snapshot_path: 快照路径
        
        返回:
            告警数据字典
        """
        behavior_type = detection_result.get('behavior_type', 'UNKNOWN')
        confidence = detection_result.get('confidence', 0.0)
        description = detection_result.get('description', '检测到异常行为')
        
        # 根据置信度确定告警级别
        if confidence >= 0.9:
            alert_level = "CRITICAL"
        elif confidence >= 0.75:
            alert_level = "HIGH"
        elif confidence >= 0.6:
            alert_level = "MEDIUM"
        else:
            alert_level = "LOW"
        
        alert_data = {
            'user_id': user_id,
            'alert_type': behavior_type,
            'alert_level': alert_level,
            'confidence': confidence,
            'description': description,
            'detail_data': json.dumps(detection_result),
        }
        
        if record_id is not None:
            alert_data['record_id'] = record_id
        
        if snapshot_path:
            alert_data['snapshot_path'] = snapshot_path
        
        return alert_data


# 全局通知器实例
notifier = AlertNotifier()

