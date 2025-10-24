"""
实时视频流处理
支持从摄像头或视频流中实时检测异常行为并发送告警
"""
import cv2
import time
from typing import Optional
from detector import BehaviorDetector
from alert_notifier import notifier
from temporal import TemporalBehaviorAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeStreamProcessor:
    """实时视频流处理器"""
    
    def __init__(
        self,
        user_id: int,
        alert_threshold: float = 0.7,
        alert_cooldown: int = 5
    ):
        """
        初始化处理器
        
        参数:
            user_id: 用户ID
            alert_threshold: 告警阈值，置信度超过此值才发送告警
            alert_cooldown: 告警冷却时间（秒），避免频繁告警
        """
        self.user_id = user_id
        self.alert_threshold = alert_threshold
        self.alert_cooldown = alert_cooldown
        self.last_alert_time = {}  # 记录每种告警类型的最后告警时间
        self.detector = BehaviorDetector()
        # 时序分析器：15帧窗口，至少40%异常、连续3帧满足
        self.temporal = TemporalBehaviorAnalyzer(
            window_size=15,
            min_abnormal_ratio=0.4,
            min_streak=3,
            ema_alpha=0.5,
            cooldown_seconds=alert_cooldown,
        )
    
    def process_stream(
        self,
        source: int = 0,
        save_snapshots: bool = True,
        snapshot_dir: str = "snapshots"
    ):
        """
        处理视频流
        
        参数:
            source: 视频源（0为默认摄像头，或视频文件路径，或RTSP流地址）
            save_snapshots: 是否保存告警快照
            snapshot_dir: 快照保存目录
        """
        import os
        if save_snapshots:
            os.makedirs(snapshot_dir, exist_ok=True)
        
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            logger.error(f"无法打开视频源: {source}")
            return
        
        logger.info(f"开始处理视频流，用户ID: {self.user_id}")
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("无法读取视频帧")
                    break
                
                frame_count += 1
                
                # 每3帧检测一次（提高性能）
                if frame_count % 3 != 0:
                    continue
                
                # 保存临时帧
                temp_frame_path = "temp/current_frame.jpg"
                os.makedirs("temp", exist_ok=True)
                cv2.imwrite(temp_frame_path, frame)
                
                # 检测异常行为
                try:
                    result = self.detector.detect_image(temp_frame_path)
                    # 更新时序分析
                    self.temporal.update(result)
                    should, dominant_behavior, smoothed_conf = self.temporal.should_alert(
                        threshold=self.alert_threshold
                    )
                    # 满足多帧稳定异常再告警
                    if should and dominant_behavior:
                        snapshot_path = None
                        if save_snapshots:
                            timestamp = int(time.time())
                            snapshot_filename = f"{dominant_behavior}_{timestamp}.jpg"
                            snapshot_path = os.path.join(snapshot_dir, snapshot_filename)
                            cv2.imwrite(snapshot_path, frame)

                        # 创建并发送告警（使用平滑后的置信度覆盖）
                        result_to_send = dict(result)
                        result_to_send['behavior_type'] = dominant_behavior
                        result_to_send['confidence'] = float(smoothed_conf)

                        alert_data = notifier.create_alert_from_detection(
                            user_id=self.user_id,
                            detection_result=result_to_send,
                            snapshot_path=snapshot_path
                        )
                        success = notifier.send_alert(alert_data)
                        if success:
                            logger.info(
                                f"[时序] 告警已发送: {dominant_behavior}, 平滑置信度: {smoothed_conf:.2f}"
                            )
                    
                    # 在帧上绘制检测结果（可选）
                    self._draw_detection_result(frame, result)
                    
                    # 显示视频流（可选，用于调试）
                    # cv2.imshow('Realtime Detection', frame)
                    
                except Exception as e:
                    logger.error(f"检测帧时出错: {str(e)}")
                
                # 按'q'键退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
            logger.info("视频流处理结束")
    
    def _should_send_alert(self, behavior_type: str, confidence: float) -> bool:
        """
        判断是否应该发送告警
        
        参数:
            behavior_type: 行为类型
            confidence: 置信度
        
        返回:
            是否发送告警
        """
        # 检查置信度是否达到阈值
        if confidence < self.alert_threshold:
            return False
        
        # 检查冷却时间
        current_time = time.time()
        last_time = self.last_alert_time.get(behavior_type, 0)
        
        if current_time - last_time < self.alert_cooldown:
            return False
        
        return True
    
    def _draw_detection_result(self, frame, result):
        """
        在帧上绘制检测结果
        
        参数:
            frame: 视频帧
            result: 检测结果
        """
        # 绘制检测到的人数
        person_count = result.get('person_count', 0)
        cv2.putText(
            frame,
            f"Persons: {person_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        
        # 如果有异常行为，显示警告
        if result['has_abnormal']:
            behavior_type = result['behavior_type']
            confidence = result['confidence']
            
            cv2.putText(
                frame,
                f"ALERT: {behavior_type}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )
            
            cv2.putText(
                frame,
                f"Confidence: {confidence:.2f}",
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )


def start_realtime_detection(
    user_id: int,
    camera_index: int = 0,
    alert_threshold: float = 0.7
):
    """
    启动实时检测
    
    参数:
        user_id: 用户ID
        camera_index: 摄像头索引或视频源
        alert_threshold: 告警阈值
    """
    processor = RealtimeStreamProcessor(
        user_id=user_id,
        alert_threshold=alert_threshold
    )
    processor.process_stream(source=camera_index)


if __name__ == "__main__":
    # 示例：启动实时检测
    # 用户ID=1，使用默认摄像头（索引0），告警阈值0.7
    start_realtime_detection(user_id=1, camera_index=0, alert_threshold=0.7)

