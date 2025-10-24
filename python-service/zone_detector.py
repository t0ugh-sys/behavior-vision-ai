"""
区域入侵检测模块
"""
import numpy as np
import cv2
from typing import List, Tuple, Dict, Any


class ZoneDetector:
    """区域入侵检测器"""
    
    def __init__(self):
        self.zones = []
    
    def set_zones(self, zones: List[Dict[str, Any]]):
        """
        设置检测区域
        
        Args:
            zones: 区域列表，每个区域包含：
                - id: 区域ID
                - name: 区域名称
                - type: 区域类型 (RESTRICTED, MONITORED, SAFE)
                - coordinates: 坐标列表 [[x1,y1], [x2,y2], ...]
                - shape: 形状类型 (RECTANGLE, POLYGON, CIRCLE)
                - enable_alert: 是否启用告警
                - alert_level: 告警级别
        """
        self.zones = zones
        print(f"✓ 已加载 {len(zones)} 个检测区域")
    
    def check_intrusion(self, persons: List[Dict[str, Any]], 
                       image_width: int, image_height: int) -> Dict[str, Any]:
        """
        检查人体是否入侵区域
        
        Args:
            persons: 检测到的人体列表
            image_width: 图像宽度
            image_height: 图像高度
            
        Returns:
            检测结果字典
        """
        intrusions = []
        zone_stats = {}
        
        if not self.zones or not persons:
            return {
                'has_intrusion': False,
                'intrusions': [],
                'zone_stats': {},
                'total_persons': len(persons)
            }
        
        # 遍历每个区域
        for zone in self.zones:
            if not zone.get('is_active', True):
                continue
            
            zone_id = zone['id']
            zone_name = zone.get('name', f'Zone {zone_id}')
            zone_type = zone.get('type', 'MONITORED')
            enable_alert = zone.get('enable_alert', True)
            
            # 转换区域坐标
            coordinates = self._normalize_coordinates(
                zone['coordinates'], 
                image_width, 
                image_height
            )
            
            intruders_in_zone = []
            
            # 检查每个人是否在区域内
            for person_idx, person in enumerate(persons):
                # 获取人体中心点（使用边界框中心）
                if 'box' in person:
                    box = person['box']
                    center_x = (box[0] + box[2]) / 2
                    center_y = (box[1] + box[3]) / 2
                    
                    # 判断是否在区域内
                    is_inside = self._point_in_zone(
                        (center_x, center_y),
                        coordinates,
                        zone.get('shape', 'POLYGON')
                    )
                    
                    if is_inside:
                        intruders_in_zone.append({
                            'person_id': person_idx,
                            'center': [int(center_x), int(center_y)],
                            'box': box,
                            'confidence': person.get('confidence', 0.0)
                        })
            
            # 统计该区域的入侵情况
            person_count = len(intruders_in_zone)
            zone_stats[zone_id] = {
                'zone_id': zone_id,
                'zone_name': zone_name,
                'zone_type': zone_type,
                'person_count': person_count,
                'has_intrusion': person_count > 0
            }
            
            # 如果有入侵且启用告警
            if person_count > 0 and enable_alert:
                intrusions.append({
                    'zone_id': zone_id,
                    'zone_name': zone_name,
                    'zone_type': zone_type,
                    'alert_level': zone.get('alert_level', 'MEDIUM'),
                    'person_count': person_count,
                    'intruders': intruders_in_zone,
                    'description': f'{zone_name}检测到{person_count}人入侵'
                })
        
        has_intrusion = len(intrusions) > 0
        
        return {
            'has_intrusion': has_intrusion,
            'intrusions': intrusions,
            'zone_stats': zone_stats,
            'total_persons': len(persons),
            'total_zones': len(self.zones),
            'affected_zones': len([z for z in zone_stats.values() if z['has_intrusion']])
        }
    
    def _normalize_coordinates(self, coordinates: List[List[float]], 
                              img_width: int, img_height: int) -> np.ndarray:
        """
        标准化坐标（支持百分比和绝对坐标）
        
        Args:
            coordinates: 坐标列表
            img_width: 图像宽度
            img_height: 图像高度
            
        Returns:
            标准化后的坐标数组
        """
        coords = np.array(coordinates, dtype=np.float32)
        
        # 如果坐标值都小于1，认为是百分比坐标，需要转换为绝对坐标
        if np.all(coords <= 1.0):
            coords[:, 0] *= img_width
            coords[:, 1] *= img_height
        
        return coords.astype(np.int32)
    
    def _point_in_zone(self, point: Tuple[float, float], 
                      zone_coords: np.ndarray, shape: str) -> bool:
        """
        判断点是否在区域内
        
        Args:
            point: 点坐标 (x, y)
            zone_coords: 区域坐标
            shape: 形状类型
            
        Returns:
            是否在区域内
        """
        if shape == 'RECTANGLE' and len(zone_coords) >= 2:
            # 矩形：使用左上角和右下角两个点
            x1, y1 = zone_coords[0]
            x2, y2 = zone_coords[1]
            return (min(x1, x2) <= point[0] <= max(x1, x2) and 
                   min(y1, y2) <= point[1] <= max(y1, y2))
        
        elif shape == 'CIRCLE' and len(zone_coords) >= 2:
            # 圆形：第一个点是圆心，第二个点用于计算半径
            center = zone_coords[0]
            radius_point = zone_coords[1]
            radius = np.sqrt((radius_point[0] - center[0])**2 + 
                           (radius_point[1] - center[1])**2)
            dist = np.sqrt((point[0] - center[0])**2 + 
                          (point[1] - center[1])**2)
            return dist <= radius
        
        else:  # POLYGON
            # 多边形：使用OpenCV的pointPolygonTest
            result = cv2.pointPolygonTest(zone_coords, point, False)
            return result >= 0
    
    def draw_zones(self, image: np.ndarray, intrusion_result: Dict[str, Any] = None) -> np.ndarray:
        """
        在图像上绘制区域和入侵情况
        
        Args:
            image: 原始图像
            intrusion_result: 入侵检测结果
            
        Returns:
            绘制后的图像
        """
        if not self.zones:
            return image
        
        img = image.copy()
        h, w = img.shape[:2]
        
        # 创建半透明叠加层
        overlay = img.copy()
        
        zone_stats = intrusion_result.get('zone_stats', {}) if intrusion_result else {}
        
        for zone in self.zones:
            if not zone.get('is_active', True):
                continue
            
            zone_id = zone['id']
            zone_name = zone.get('name', f'Zone {zone_id}')
            zone_type = zone.get('type', 'MONITORED')
            
            # 转换坐标
            coords = self._normalize_coordinates(zone['coordinates'], w, h)
            
            # 判断是否有入侵
            has_intrusion = zone_stats.get(zone_id, {}).get('has_intrusion', False)
            
            # 根据区域类型和入侵状态选择颜色
            if has_intrusion:
                color = (0, 0, 255)  # 红色 - 有入侵
                alpha = 0.3
            elif zone_type == 'RESTRICTED':
                color = (0, 165, 255)  # 橙色 - 禁区
                alpha = 0.2
            elif zone_type == 'SAFE':
                color = (0, 255, 0)  # 绿色 - 安全区
                alpha = 0.15
            else:
                color = (255, 255, 0)  # 黄色 - 监控区
                alpha = 0.2
            
            # 绘制区域
            shape = zone.get('shape', 'POLYGON')
            if shape == 'RECTANGLE' and len(coords) >= 2:
                cv2.rectangle(overlay, tuple(coords[0]), tuple(coords[1]), color, -1)
                cv2.rectangle(img, tuple(coords[0]), tuple(coords[1]), color, 2)
            elif shape == 'CIRCLE' and len(coords) >= 2:
                center = tuple(coords[0])
                radius = int(np.linalg.norm(coords[1] - coords[0]))
                cv2.circle(overlay, center, radius, color, -1)
                cv2.circle(img, center, radius, color, 2)
            else:  # POLYGON
                cv2.fillPoly(overlay, [coords], color)
                cv2.polylines(img, [coords], True, color, 2)
            
            # 混合透明度
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
            
            # 添加区域标签
            label_pos = tuple(coords[0])
            person_count = zone_stats.get(zone_id, {}).get('person_count', 0)
            
            if has_intrusion:
                label = f"{zone_name}: {person_count} person(s)"
                bg_color = (0, 0, 255)
            else:
                label = zone_name
                bg_color = color
            
            # 绘制标签背景
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(img, 
                         (label_pos[0], label_pos[1] - text_h - 8),
                         (label_pos[0] + text_w + 8, label_pos[1]),
                         bg_color, -1)
            cv2.putText(img, label,
                       (label_pos[0] + 4, label_pos[1] - 4),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return img

