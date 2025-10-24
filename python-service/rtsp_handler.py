"""
RTSP流处理模块
"""
import cv2
import threading
import time
import numpy as np
from typing import Optional, Dict, Any
from detector import BehaviorDetector


class RTSPStreamHandler:
    """RTSP流处理器"""
    
    def __init__(self, detector: BehaviorDetector, notifier=None):
        self.detector = detector
        self.notifier = notifier
        
        self.rtsp_url: Optional[str] = None
        self.user_id: Optional[int] = None
        self.enable_alert: bool = True
        self.detection_interval: float = 2.0
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running: bool = False
        self.thread: Optional[threading.Thread] = None
        
        self.latest_frame: Optional[np.ndarray] = None
        self.latest_result: Optional[Dict[str, Any]] = None
        self.frame_lock = threading.Lock()
        self.result_lock = threading.Lock()
        
    def start(self, rtsp_url: str, user_id: int, enable_alert: bool = True, detection_interval: float = 2.0):
        """
        启动RTSP流处理
        
        参数:
            rtsp_url: RTSP流地址
            user_id: 用户ID
            enable_alert: 是否启用告警
            detection_interval: 检测间隔（秒）
        """
        if self.is_running:
            raise RuntimeError("RTSP流已在运行中")
        
        self.rtsp_url = rtsp_url
        self.user_id = user_id
        self.enable_alert = enable_alert
        self.detection_interval = detection_interval
        
        # 尝试连接RTSP流
        self.cap = cv2.VideoCapture(rtsp_url)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法连接到RTSP流: {rtsp_url}")
        
        # 设置缓冲区大小
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.is_running = True
        self.thread = threading.Thread(target=self._process_stream, daemon=True)
        self.thread.start()
        
        print(f"✓ RTSP流已启动: {rtsp_url}")
        
    def stop(self):
        """停止RTSP流处理"""
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        with self.frame_lock:
            self.latest_frame = None
        
        with self.result_lock:
            self.latest_result = None
        
        print("✓ RTSP流已停止")
        
    def _process_stream(self):
        """处理RTSP流的主循环"""
        last_detection_time = 0
        frame_count = 0
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("⚠ 无法读取RTSP流帧，尝试重新连接...")
                    time.sleep(1)
                    # 尝试重新连接
                    if self.cap:
                        self.cap.release()
                    self.cap = cv2.VideoCapture(self.rtsp_url)
                    if not self.cap.isOpened():
                        print("✗ 重新连接失败")
                        break
                    continue
                
                frame_count += 1
                
                # 更新最新帧
                with self.frame_lock:
                    self.latest_frame = frame.copy()
                
                # 检测间隔控制
                current_time = time.time()
                if current_time - last_detection_time >= self.detection_interval:
                    last_detection_time = current_time
                    
                    # 调整帧大小以加快检测速度
                    detect_frame = cv2.resize(frame, (640, 480))
                    
                    # 保存临时图片
                    temp_path = "temp/rtsp_frame.jpg"
                    cv2.imwrite(temp_path, detect_frame)
                    
                    # 进行检测
                    try:
                        result = self.detector.detect_image(temp_path, visualize=False)
                        
                        # 更新最新结果
                        with self.result_lock:
                            self.latest_result = result
                        
                        # 如果检测到异常且启用告警
                        if result['has_abnormal'] and self.enable_alert:
                            print(f"⚠ 检测到异常: {result['behavior_type']} (置信度: {result['confidence']:.2f})")
                            
                            # 保存快照
                            snapshot_path = f"snapshots/{result['behavior_type']}_{int(time.time())}.jpg"
                            cv2.imwrite(snapshot_path, frame)
                            
                            # 发送告警（如果notifier可用）
                            if self.notifier:
                                try:
                                    alert_data = self.notifier.create_alert_from_detection(
                                        user_id=self.user_id,
                                        detection_result=result,
                                        record_id=None,
                                        snapshot_path=snapshot_path
                                    )
                                    self.notifier.send_alert(alert_data)
                                except Exception as e:
                                    print(f"✗ 发送告警失败: {e}")
                    
                    except Exception as e:
                        print(f"✗ 检测失败: {e}")
                        
            except Exception as e:
                print(f"✗ RTSP流处理错误: {e}")
                time.sleep(1)
        
        print(f"✓ RTSP流处理线程已退出 (共处理 {frame_count} 帧)")
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """获取最新帧"""
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None
    
    def get_latest_result(self) -> Optional[Dict[str, Any]]:
        """获取最新检测结果"""
        with self.result_lock:
            return self.latest_result.copy() if self.latest_result is not None else None

