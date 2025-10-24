"""
人体异常行为检测器
基于YOLOv8 Pose模型
"""
import cv2
import numpy as np
import math
from typing import Dict, List, Any, Tuple, Optional
from ultralytics import YOLO
from zone_detector import ZoneDetector

# 配置参数
MODEL_PATH = "yolov8n-pose.pt"
CONFIDENCE_THRESHOLD = 0.3
IOU_THRESHOLD = 0.5
MODEL_DEVICE = "cpu"  # 或 "cuda:0"
DETECTION_FRAME_SKIP = 1  # 视频检测时每隔几帧检测一次

# 关键点索引映射
KEYPOINT_DICT = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_wrist': 9,
    'right_wrist': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16
}


class BehaviorDetector:
    """人体异常行为检测器"""
    
    def __init__(self, model_path: str = MODEL_PATH, 
                 conf_threshold: float = CONFIDENCE_THRESHOLD,
                 iou_threshold: float = IOU_THRESHOLD):
        """
        初始化检测器
        
        参数:
            model_path: YOLO模型路径
            conf_threshold: 置信度阈值
            iou_threshold: IOU阈值
        """
        # 初始化区域检测器
        self.zone_detector = ZoneDetector()
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.KEYPOINT_DICT = KEYPOINT_DICT
        
        # 加载模型
        try:
            self.model = YOLO(model_path)
            print(f"成功加载模型: {model_path}")
        except Exception as e:
            print(f"加载模型失败: {e}")
            self.model = None
    
    def detect_image(self, image_path: str, visualize: bool = False, output_path: str = None) -> Dict[str, Any]:
        """
        检测图片中的异常行为
        
        参数:
            image_path: 图片路径
            visualize: 是否生成可视化图片
            output_path: 可视化图片保存路径
        
        返回:
            检测结果字典
        """
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 进行检测
        results = self.model(
            image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=MODEL_DEVICE,
        )
        
        # 分析结果
        result = self._analyze_results(results, image.shape)
        
        # 生成可视化图片
        if visualize and output_path:
            vis_image = self._visualize_detection(image, results, result)
            cv2.imwrite(output_path, vis_image)
            result['visualization_path'] = output_path
        
        return result
    
    def _visualize_detection(self, image, results, detection_result):
        """
        可视化检测结果（图片）
        
        参数:
            image: 原始图片
            results: YOLO检测结果
            detection_result: 分析后的检测结果
        
        返回:
            可视化后的图片
        """
        try:
            # 使用ultralytics内置的plot方法生成可视化图像
            if results and len(results) > 0 and detection_result['person_count'] > 0:
                try:
                    vis_image = results[0].plot(
                        conf=False,
                        line_width=2,
                        font_size=0.5,
                        pil=False,
                        labels=False,
                        boxes=True,
                        kpt_radius=5
                    )
                except Exception as plot_error:
                    print(f"使用内置plot方法失败: {plot_error}")
                    vis_image = image.copy()
            else:
                vis_image = image.copy()
            
            # 添加检测结果文本
            if detection_result['has_abnormal']:
                behavior_text = f"ABNORMAL: {detection_result['behavior_type']}"
                conf_text = f"Confidence: {detection_result['confidence']:.2f}"
                
                # 添加半透明背景
                overlay = vis_image.copy()
                cv2.rectangle(overlay, (10, 10), (350, 70), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, vis_image, 0.4, 0, vis_image)
                
                # 添加文字
                cv2.putText(vis_image, behavior_text, (18, 33),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
                cv2.putText(vis_image, conf_text, (18, 55),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            else:
                # 正常状态
                overlay = vis_image.copy()
                cv2.rectangle(overlay, (10, 10), (200, 50), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, vis_image, 0.4, 0, vis_image)
                
                cv2.putText(vis_image, "Status: NORMAL", (18, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
            
            # 添加人数统计
            person_count_text = f"Persons: {detection_result['person_count']}"
            text_size = cv2.getTextSize(person_count_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            text_x = 18
            text_y = vis_image.shape[0] - 22
            
            overlay = vis_image.copy()
            cv2.rectangle(overlay, 
                         (text_x - 8, text_y - text_size[1] - 8),
                         (text_x + text_size[0] + 8, text_y + 8),
                         (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, vis_image, 0.4, 0, vis_image)
            
            cv2.putText(vis_image, person_count_text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            return vis_image
            
        except Exception as e:
            print(f"可视化失败: {e}")
            return image.copy()
    
    def _visualize_frame(self, frame, results, detection_result):
        """
        可视化单个视频帧
        
        参数:
            frame: 原始视频帧
            results: YOLO检测结果
            detection_result: 分析后的检测结果
        
        返回:
            可视化后的帧
        """
        try:
            # 使用ultralytics内置的plot方法生成可视化图像
            if results and len(results) > 0 and detection_result['person_count'] > 0:
                try:
                    vis_frame = results[0].plot(
                        conf=False,
                        line_width=2,
                        font_size=0.5,
                        pil=False,
                        labels=False,
                        boxes=True,
                        kpt_radius=5
                    )
                except Exception as plot_error:
                    vis_frame = frame.copy()
            else:
                vis_frame = frame.copy()
            
            # 添加检测结果文本
            if detection_result['has_abnormal']:
                behavior_text = f"ABNORMAL: {detection_result['behavior_type']}"
                conf_text = f"Confidence: {detection_result['confidence']:.2f}"
                
                overlay = vis_frame.copy()
                cv2.rectangle(overlay, (10, 10), (350, 70), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, vis_frame, 0.4, 0, vis_frame)
                
                cv2.putText(vis_frame, behavior_text, (18, 33),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
                cv2.putText(vis_frame, conf_text, (18, 55),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            else:
                overlay = vis_frame.copy()
                cv2.rectangle(overlay, (10, 10), (200, 50), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, vis_frame, 0.4, 0, vis_frame)
                
                cv2.putText(vis_frame, "Status: NORMAL", (18, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
            
            # 添加人数统计
            person_count_text = f"Persons: {detection_result['person_count']}"
            text_size = cv2.getTextSize(person_count_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            text_x = 18
            text_y = vis_frame.shape[0] - 22
            
            overlay = vis_frame.copy()
            cv2.rectangle(overlay, 
                         (text_x - 8, text_y - text_size[1] - 8),
                         (text_x + text_size[0] + 8, text_y + 8),
                         (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, vis_frame, 0.4, 0, vis_frame)
            
            cv2.putText(vis_frame, person_count_text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            return vis_frame
            
        except Exception as e:
            print(f"帧可视化失败: {e}")
            return frame.copy()
    
    def detect_video(self, video_path: str, visualize: bool = False, output_path: str = None) -> Dict[str, Any]:
        """
        检测视频中的异常行为
        
        参数:
            video_path: 视频路径
            visualize: 是否生成可视化视频
            output_path: 可视化视频保存路径
        
        返回:
            检测结果字典
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")
        
        # 获取视频属性
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 创建视频写入器（使用浏览器兼容的H.264编码）
        video_writer = None
        if visualize and output_path:
            # 尝试使用不同的编码器，优先使用浏览器兼容的H.264
            codecs_to_try = [
                ('avc1', 'H.264 (avc1)'),
                ('H264', 'H.264 (H264)'),
                ('X264', 'H.264 (X264)'),
                ('mp4v', 'MPEG-4 (mp4v)')  # 备用方案
            ]
            
            for fourcc_str, codec_name in codecs_to_try:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
                    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                    if video_writer.isOpened():
                        print(f"✓ 成功创建视频写入器: {output_path}")
                        print(f"  编码器: {codec_name}, fps={fps}, size={width}x{height}")
                        break
                    else:
                        video_writer.release()
                        video_writer = None
                except Exception as e:
                    print(f"× 尝试编码器 {codec_name} 失败: {e}")
                    continue
            
            if video_writer is None or not video_writer.isOpened():
                raise RuntimeError("无法创建视频写入器，请检查OpenCV和编码器支持")
        
        frame_count = 0
        abnormal_frames = []  # 异常行为帧
        person_detected_frames = []  # 检测到人的帧
        all_detections = []  # 所有检测结果
        detection_segments = []  # 检测片段（连续检测到人的时间段）
        
        current_segment = None  # 当前检测片段
        
        # 检查VideoWriter是否成功创建
        if visualize and video_writer is None:
            print(f"× 警告：VideoWriter未创建，跳过可视化")
            visualize = False
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # 进行检测（不跳帧，确保视频完整）
                results = self.model(
                    frame,
                    conf=self.conf_threshold,
                    iou=self.iou_threshold,
                    device=MODEL_DEVICE,
                )
                frame_result = self._analyze_results(results, frame.shape)
                
                # 记录异常帧
                if frame_result['has_abnormal']:
                    abnormal_frames.append({
                        'frame_number': frame_count,
                        'timestamp': frame_count / fps,
                        'behavior_type': frame_result['behavior_type'],
                        'confidence': frame_result['confidence'],
                        'person_count': frame_result['person_count']
                    })
                
                # 记录检测到人的帧
                if frame_result['person_count'] > 0:
                    person_detected_frames.append({
                        'frame_number': frame_count,
                        'timestamp': frame_count / fps,
                        'person_count': frame_result['person_count'],
                        'has_abnormal': frame_result['has_abnormal'],
                        'behavior_type': frame_result['behavior_type'],
                        'confidence': frame_result['confidence']
                    })
                    
                    # 检测片段管理
                    if current_segment is None:
                        # 开始新片段
                        current_segment = {
                            'start_frame': frame_count,
                            'end_frame': frame_count,
                            'start_time': frame_count / fps,
                            'end_time': frame_count / fps,
                            'person_count_max': frame_result['person_count'],
                            'has_abnormal': frame_result['has_abnormal'],
                            'abnormal_count': 1 if frame_result['has_abnormal'] else 0,
                            'total_frames': 1
                        }
                    else:
                        # 继续当前片段
                        current_segment['end_frame'] = frame_count
                        current_segment['end_time'] = frame_count / fps
                        current_segment['person_count_max'] = max(
                            current_segment['person_count_max'],
                            frame_result['person_count']
                        )
                        current_segment['has_abnormal'] = current_segment['has_abnormal'] or frame_result['has_abnormal']
                        if frame_result['has_abnormal']:
                            current_segment['abnormal_count'] += 1
                        current_segment['total_frames'] += 1
                else:
                    # 未检测到人，结束当前片段
                    if current_segment is not None:
                        # 保存片段
                        current_segment['duration'] = current_segment['end_time'] - current_segment['start_time']
                        detection_segments.append(current_segment)
                        print(f"保存检测片段: 帧{current_segment['start_frame']}-{current_segment['end_frame']}, "
                              f"时长{current_segment['duration']:.1f}s, "
                              f"最多{current_segment['person_count_max']}人, "
                              f"异常帧{current_segment['abnormal_count']}帧")
                        current_segment = None
                
                all_detections.append(frame_result)
                
                # 生成可视化帧并写入
                if video_writer is not None and video_writer.isOpened():
                    vis_frame = self._visualize_frame(frame, results, frame_result)
                    # 确保帧尺寸正确
                    if vis_frame.shape[1] == width and vis_frame.shape[0] == height:
                        video_writer.write(vis_frame)
                    else:
                        # 如果尺寸不匹配，resize
                        vis_frame = cv2.resize(vis_frame, (width, height))
                        video_writer.write(vis_frame)
                
                # 每100帧打印一次进度
                if frame_count % 100 == 0:
                    print(f"  已处理 {frame_count} 帧...")
            
            # 处理最后一个片段
            if current_segment is not None:
                current_segment['duration'] = current_segment['end_time'] - current_segment['start_time']
                detection_segments.append(current_segment)
                print(f"保存最后检测片段: 帧{current_segment['start_frame']}-{current_segment['end_frame']}, "
                      f"时长{current_segment['duration']:.1f}s")
                    
        finally:
            cap.release()
            if video_writer is not None:
                video_writer.release()
                print(f"✓ 视频处理完成，共 {frame_count} 帧")
                if visualize and output_path:
                    import os
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path) / (1024 * 1024)
                        print(f"✓ 视频可视化完成: {output_path} ({file_size:.2f} MB)")
                    else:
                        print(f"× 警告：输出文件未生成: {output_path}")
        
        # 汇总结果（时序平滑：投票 + 平均置信度）
        has_abnormal = len(abnormal_frames) > 0
        if has_abnormal:
            behavior_types = [f['behavior_type'] for f in abnormal_frames]
            # 投票：最常出现的行为类型
            from collections import Counter
            behavior_type = Counter(behavior_types).most_common(1)[0][0]
            
            # 平均置信度
            confidence = np.mean([f['confidence'] for f in abnormal_frames])
            
            description = f"视频中检测到{len(abnormal_frames)}帧异常行为: {behavior_type}"
        else:
            behavior_type = None
            confidence = 0.0
            description = "未检测到异常行为"
        
        # 统计信息
        total_person_frames = len(person_detected_frames)
        total_segments = len(detection_segments)
        
        if total_person_frames > 0:
            description += f"，共{total_person_frames}帧检测到人，{total_segments}个检测片段"
        
        print(f"\n检测统计:")
        print(f"  总帧数: {frame_count}")
        print(f"  检测到人的帧数: {total_person_frames}")
        print(f"  异常帧数: {len(abnormal_frames)}")
        print(f"  检测片段数: {total_segments}")
        
        return {
            'has_abnormal': has_abnormal,
            'behavior_type': behavior_type,
            'confidence': float(confidence),
            'person_count': max([d['person_count'] for d in all_detections]) if all_detections else 0,
            'description': description,
            'frame_count': frame_count,
            'abnormal_frames': abnormal_frames,
            'person_detected_frames': person_detected_frames,  # 检测到人的所有帧
            'detection_segments': detection_segments,  # 检测片段
            'total_person_frames': total_person_frames,  # 检测到人的总帧数
            'total_segments': total_segments  # 检测片段总数
        }
    
    def _analyze_results(self, results, image_shape) -> Dict[str, Any]:
        """
        分析检测结果
        
        参数:
            results: YOLO检测结果
            image_shape: 图片尺寸
        
        返回:
            分析结果字典
        """
        result = results[0]
        
        # 提取关键点
        persons = []
        if result.keypoints is not None and result.keypoints.data is not None:
            keypoints = result.keypoints.data.cpu().numpy()
            boxes = result.boxes.data.cpu().numpy() if result.boxes is not None else []
            
            # 确保keypoints数组不为空且有正确的维度
            if keypoints.size > 0 and len(keypoints.shape) >= 2:
                for i, kps in enumerate(keypoints):
                    person_data = {
                        'keypoints': kps.tolist(),
                        'box': boxes[i][:4].tolist() if i < len(boxes) else None
                    }
                    persons.append(person_data)
            else:
                print(f"关键点数组为空或维度不正确: shape={keypoints.shape}")
        
        # 检测异常行为
        abnormal_behavior = self._detect_abnormal_behavior(persons, image_shape)
        
        return {
            'has_abnormal': abnormal_behavior['is_abnormal'],
            'behavior_type': abnormal_behavior['behavior_type'],
            'confidence': abnormal_behavior['confidence'],
            'person_count': len(persons),
            'persons': persons,
            'description': abnormal_behavior['description']
        }
    
    def _detect_abnormal_behavior(self, persons: List[Dict], image_shape) -> Dict[str, Any]:
        """
        检测异常行为
        
        参数:
            persons: 检测到的人员列表
            image_shape: 图片尺寸
        
        返回:
            {
                'is_abnormal': bool,
                'behavior_type': str,
                'confidence': float,
                'description': str
            }
        """
        if len(persons) == 0:
            return {
                'is_abnormal': False,
                'behavior_type': None,
                'confidence': 0.0,
                'description': '未检测到人员'
            }
        
        # 1. 检测跌倒
        for person in persons:
            fall_result = self._detect_fall(person['keypoints'], image_shape)
            if fall_result['is_fall']:
                return {
                    'is_abnormal': True,
                    'behavior_type': 'FALL',
                    'confidence': fall_result['confidence'],
                    'description': fall_result['description']
                }
        
        # 2. 检测打架（需要多人）
        if len(persons) >= 2:
            fight_result = self._detect_fight(persons, image_shape)
            if fight_result['is_fight']:
                return {
                    'is_abnormal': True,
                    'behavior_type': 'FIGHT',
                    'confidence': fight_result['confidence'],
                    'description': fight_result['description']
                }
        
        # 3. 检测异常姿态
        for person in persons:
            abnormal_pose_result = self._detect_abnormal_pose(person['keypoints'], image_shape)
            if abnormal_pose_result['is_abnormal']:
                return {
                    'is_abnormal': True,
                    'behavior_type': 'ABNORMAL_POSE',
                    'confidence': abnormal_pose_result['confidence'],
                    'description': abnormal_pose_result['description']
                }
        
        # 未检测到异常行为
        # 计算正常行为的置信度（基于平均关键点置信度）
        normal_confidence = self._calculate_normal_confidence(persons)
        
        return {
            'is_abnormal': False,
            'behavior_type': None,
            'confidence': normal_confidence,
            'description': '未检测到异常行为'
        }
    
    def _calculate_normal_confidence(self, persons: List[Dict]) -> float:
        """
        计算正常行为的置信度
        基于检测到的人体关键点的平均置信度
        """
        if not persons:
            return 0.0
        
        total_confidence = 0.0
        total_keypoints = 0
        
        for person in persons:
            keypoints = np.array(person['keypoints'])
            if keypoints.size == 0 or len(keypoints.shape) < 2:
                continue
            
            # 提取置信度（第三列）
            confidences = keypoints[:, 2] if keypoints.shape[1] >= 3 else []
            valid_confidences = [c for c in confidences if c > 0]
            
            if valid_confidences:
                total_confidence += sum(valid_confidences)
                total_keypoints += len(valid_confidences)
        
        if total_keypoints > 0:
            avg_confidence = total_confidence / total_keypoints
            return float(avg_confidence)
        
        return 0.0
    
    def _detect_fall(self, keypoints, image_shape) -> Dict[str, Any]:
        """
        检测跌倒行为
        
        策略：
        1. 检查身体重心高度
        2. 检查头部位置
        3. 检查身体宽高比
        4. 检查身体角度
        5. 检查膝盖位置
        
        参数:
            keypoints: 人体关键点 (17, 3) [x, y, confidence]
            image_shape: 图片尺寸 (height, width, channels)
        
        返回:
            检测结果字典
        """
        try:
            keypoints = np.array(keypoints)
            
            # 添加检查：确保keypoints不为空
            if keypoints.size == 0 or len(keypoints.shape) < 2:
                print(f"跌倒检测: 关键点数据无效: shape={keypoints.shape}")
                return {
                    'is_fall': False,
                    'confidence': 0.0,
                    'description': '关键点数据不足'
                }
            
            # 提取关键点
            nose = keypoints[self.KEYPOINT_DICT['nose']]
            left_shoulder = keypoints[self.KEYPOINT_DICT['left_shoulder']]
            right_shoulder = keypoints[self.KEYPOINT_DICT['right_shoulder']]
            left_hip = keypoints[self.KEYPOINT_DICT['left_hip']]
            right_hip = keypoints[self.KEYPOINT_DICT['right_hip']]
            left_knee = keypoints[self.KEYPOINT_DICT['left_knee']]
            right_knee = keypoints[self.KEYPOINT_DICT['right_knee']]
            left_ankle = keypoints[self.KEYPOINT_DICT['left_ankle']]
            right_ankle = keypoints[self.KEYPOINT_DICT['right_ankle']]
            left_wrist = keypoints[self.KEYPOINT_DICT['left_wrist']]
            right_wrist = keypoints[self.KEYPOINT_DICT['right_wrist']]
            left_elbow = keypoints[self.KEYPOINT_DICT['left_elbow']]
            right_elbow = keypoints[self.KEYPOINT_DICT['right_elbow']]
            
            # 检查关键点是否可见（置信度 > 0.3）
            if nose[2] < 0.3 or (left_shoulder[2] < 0.3 and right_shoulder[2] < 0.3):
                return {
                    'is_fall': False,
                    'confidence': 0.0,
                    'description': '关键点不可见'
                }
            
            # 计算肩膀和臀部中心点
            shoulder_center = ((left_shoulder + right_shoulder) / 2) if (left_shoulder[2] > 0.3 and right_shoulder[2] > 0.3) else left_shoulder if left_shoulder[2] > 0.3 else right_shoulder
            hip_center = ((left_hip + right_hip) / 2) if (left_hip[2] > 0.3 and right_hip[2] > 0.3) else left_hip if left_hip[2] > 0.3 else right_hip
            
            # 初始化检测结果
            fall_detected = False
            confidence = 0.0
            detection_reason = ""
            
            # 检查是否是坐姿或运动姿态（避免误判）
            is_sitting = False
            is_exercise_pose = False
            
            # 坐姿判断：臀部在膝盖上方，且膝盖弯曲
            if (left_hip[2] > 0.3 and left_knee[2] > 0.3 and left_ankle[2] > 0.3):
                # 检查臀部是否明显在膝盖上方（y坐标较小）
                if left_hip[1] < left_knee[1] - image_shape[0] * 0.1:
                    # 检查膝盖弯曲（膝盖到脚踝的水平距离小）
                    knee_ankle_horiz_dist = abs(left_knee[0] - left_ankle[0])
                    if knee_ankle_horiz_dist < image_shape[1] * 0.1:
                        is_sitting = True
                        print(f"检测到坐姿（左侧）")
            
            if (right_hip[2] > 0.3 and right_knee[2] > 0.3 and right_ankle[2] > 0.3):
                if right_hip[1] < right_knee[1] - image_shape[0] * 0.1:
                    knee_ankle_horiz_dist = abs(right_knee[0] - right_ankle[0])
                    if knee_ankle_horiz_dist < image_shape[1] * 0.1:
                        is_sitting = True
                        print(f"检测到坐姿（右侧）")
            
            # 运动姿态判断（俯卧撑、平板支撑等）
            # 更严格的条件：双手都可见、在身体两侧支撑、身体相对水平
            if (left_shoulder[2] > 0.3 and right_shoulder[2] > 0.3 and 
                left_wrist[2] > 0.5 and right_wrist[2] > 0.5):
                
                # 计算身体中心点
                body_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
                body_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
                
                # 检查双手是否在身体两侧（左右分开）
                left_wrist_left = left_wrist[0] < body_center_x - image_shape[1] * 0.1
                right_wrist_right = right_wrist[0] > body_center_x + image_shape[1] * 0.1
                
                # 检查双手是否在肩膀下方支撑
                hands_below_shoulder = (left_wrist[1] > body_center_y and 
                                       right_wrist[1] > body_center_y)
                
                # 检查身体是否相对水平（肩膀和臀部高度差不大）
                if hip_center[2] > 0.3:
                    shoulder_hip_height = abs(shoulder_center[1] - hip_center[1])
                    body_horizontal = shoulder_hip_height < image_shape[0] * 0.2
                else:
                    body_horizontal = False
                
                # 同时满足：双手分开支撑 + 在肩膀下方 + 身体水平
                if left_wrist_left and right_wrist_right and hands_below_shoulder and body_horizontal:
                    is_exercise_pose = True
                    print(f"检测到运动姿态：双手支撑平板姿态")
                else:
                    print(f"支撑条件不满足: 左手在左={left_wrist_left}, 右手在右={right_wrist_right}, "
                          f"手在下方={hands_below_shoulder}, 身体水平={body_horizontal}")
            
            # 方法1：计算人体重心高度
            # 头部、肩部、臀部的平均高度
            body_center_y = (nose[1] + shoulder_center[1] + hip_center[1]) / 3
            body_height_ratio = body_center_y / image_shape[0]
            
            print(f"身体重心比例: {body_height_ratio:.3f} (图片高度: {image_shape[0]}px)")
            
            # 降低阈值，更容易检测到跌倒
            # 如果是坐姿或运动姿态，不判定为跌倒
            if not is_sitting and not is_exercise_pose and body_height_ratio > 0.5:
                # 重心过低，可能是跌倒
                confidence = min(0.95, (body_height_ratio - 0.5) / 0.4 * 0.6 + 0.35)
                fall_detected = True
                detection_reason = f"重心过低(ratio={body_height_ratio:.2f})"
                print(f"✓ 检测到跌倒：{detection_reason}, confidence={confidence:.2f}")
            
            # 方法2：计算头部位置（如果头部可见）
            if nose[2] > 0.3:
                nose_y_ratio = nose[1] / image_shape[0]
                print(f"头部位置比例: {nose_y_ratio:.3f}")
                
                # 降低阈值到0.55
                if not is_sitting and not is_exercise_pose and nose_y_ratio > 0.55:
                    head_confidence = min(0.92, (nose_y_ratio - 0.55) / 0.35 * 0.6 + 0.32)
                    if head_confidence > confidence:
                        confidence = head_confidence
                        fall_detected = True
                        detection_reason = f"头部过低(ratio={nose_y_ratio:.2f})"
                    print(f"✓ 检测到跌倒：{detection_reason}, confidence={confidence:.2f}")
            else:
                print(f"头部不可见，跳过头部位置检测")
            
            # 方法3：计算人体宽高比（重要指标）
            # 计算身体的垂直跨度和水平跨度
            all_x = [kpt[0] for kpt in keypoints if kpt[2] > 0.3]
            all_y = [kpt[1] for kpt in keypoints if kpt[2] > 0.3]
            
            if len(all_x) > 0 and len(all_y) > 0:
                body_width = max(all_x) - min(all_x)
                body_height = max(all_y) - min(all_y)
                
                # 计算宽高比
                if body_height > 0:
                    aspect_ratio = body_width / body_height
                    print(f"身体宽高比: {aspect_ratio:.2f} (width={body_width:.1f}, height={body_height:.1f})")
                    
                    # 降低阈值到1.2，站立时宽高比约0.3-0.5，躺下时>1.0
                    if not is_sitting and not is_exercise_pose and aspect_ratio > 1.2:
                        aspect_confidence = min(0.90, (aspect_ratio - 1.2) / 1.2 * 0.5 + 0.40)
                        if aspect_confidence > confidence:
                            confidence = aspect_confidence
                            fall_detected = True
                            detection_reason = f"身体横向(ratio={aspect_ratio:.2f})"
                        print(f"✓ 检测到跌倒：{detection_reason}, confidence={confidence:.2f}")
            
            # 方法4：计算人体角度（相对于垂直方向）
            if hip_center[2] > 0.3:
                dx = shoulder_center[0] - hip_center[0]
                dy = shoulder_center[1] - hip_center[1]
                
                if abs(dy) > 1:  # 避免除零
                    angle = abs(math.atan2(dx, dy) * 180 / math.pi)
                    print(f"身体角度: {angle:.1f}°")
                    
                    # 降低角度阈值到45度（站立时接近0度，躺下时接近90度）
                    if not is_sitting and not is_exercise_pose and angle > 45:
                        angle_confidence = min(0.88, (angle - 45) / 45 * 0.6 + 0.28)
                        if angle_confidence > confidence:
                            confidence = angle_confidence
                            fall_detected = True
                            detection_reason = f"角度异常({angle:.1f}°)"
                        print(f"✓ 检测到跌倒：{detection_reason}, confidence={confidence:.2f}")
            
            # 方法5：检查膝盖位置
            # 如果膝盖在身体下部，且不是坐姿或运动姿态，可能是躺着
            if not is_sitting and not is_exercise_pose and (left_knee[2] > 0.3 or right_knee[2] > 0.3):
                knee_y = max(left_knee[1] if left_knee[2] > 0.3 else 0,
                            right_knee[1] if right_knee[2] > 0.3 else 0)
                knee_y_ratio = knee_y / image_shape[0]
                
                print(f"膝盖位置比例: {knee_y_ratio:.3f}")
                
                # 提高阈值到0.7，避免误判
                if knee_y_ratio > 0.7:
                    knee_confidence = min(0.86, (knee_y_ratio - 0.7) / 0.25 * 0.4 + 0.46)
                    if knee_confidence > confidence:
                        confidence = knee_confidence
                        fall_detected = True
                        detection_reason = f"膝盖过低(ratio={knee_y_ratio:.2f})"
                    print(f"✓ 检测到跌倒：{detection_reason}, confidence={confidence:.2f}")
            
            if fall_detected:
                print("=" * 40)
                print(f"最终判定：跌倒检测成功！")
                print(f"原因：{detection_reason}")
                print(f"置信度：{confidence:.2f}")
                print("=" * 40)
            else:
                print("未检测到跌倒")
            
            return {
                'is_fall': fall_detected,
                'confidence': float(confidence),
                'description': f'检测到跌倒行为: {detection_reason}' if fall_detected else '未检测到跌倒'
            }
            
        except Exception as e:
            print(f"跌倒检测错误: {e}")
            import traceback
            traceback.print_exc()
            return {
                'is_fall': False,
                'confidence': 0.0,
                'description': f'检测失败: {str(e)}'
            }
    
    def _detect_abnormal_pose(self, keypoints, image_shape) -> Dict[str, Any]:
        """
        检测异常姿态
        """
        try:
            keypoints = np.array(keypoints)
            
            # 添加检查：确保keypoints不为空
            if keypoints.size == 0 or len(keypoints.shape) < 2:
                print(f"异常姿态检测: 关键点数据无效: shape={keypoints.shape}")
                return {
                    'is_abnormal': False,
                    'confidence': 0.0,
                    'description': '关键点数据不足'
                }
            
            # 这里可以添加其他异常姿态检测逻辑
            # 例如：蹲下、爬行、倒挂等
            
            return {
                'is_abnormal': False,
                'confidence': 0.0,
                'description': '姿态正常'
            }
        except Exception as e:
            print(f"异常姿态检测错误: {e}")
            return {
                'is_abnormal': False,
                'confidence': 0.0,
                'description': f'检测失败: {str(e)}'
            }
    
    def _detect_fight(self, persons: List[Dict], image_shape) -> Dict[str, Any]:
        """
        检测打架行为
        
        策略：
        1. 两人距离很近
        2. 身体有交叠
        3. 手臂有挥动动作（手腕位置异常）
        4. 身体姿态不稳定
        """
        try:
            if len(persons) < 2:
                return {
                    'is_fight': False,
                    'confidence': 0.0,
                    'description': '人数不足'
                }
            
            # 打架检测：检查每对人
            for i in range(len(persons)):
                for j in range(i + 1, len(persons)):
                    person1_kps = np.array(persons[i]['keypoints'])
                    person2_kps = np.array(persons[j]['keypoints'])
                    
                    # 添加检查：确保关键点数组不为空
                    if person1_kps.size == 0 or len(person1_kps.shape) < 2:
                        continue
                    if person2_kps.size == 0 or len(person2_kps.shape) < 2:
                        continue
                    
                    # 提取有效关键点
                    p1_valid_kps = person1_kps[person1_kps[:, 2] > 0.3][:, :2]
                    p2_valid_kps = person2_kps[person2_kps[:, 2] > 0.3][:, :2]
                    
                    if len(p1_valid_kps) == 0 or len(p2_valid_kps) == 0:
                        continue
                    
                    # 计算两人中心点距离
                    person1_center = np.mean(p1_valid_kps, axis=0)
                    person2_center = np.mean(p2_valid_kps, axis=0)
                    
                    center_distance = np.linalg.norm(person1_center - person2_center)
                    distance_ratio = center_distance / image_shape[1]
                    
                    print(f"两人距离: {center_distance:.1f}px, 比例: {distance_ratio:.3f}")
                    
                    # 条件1：两人距离很近（小于图片宽度的25%）
                    if distance_ratio > 0.25:
                        continue
                    
                    # 条件2：检查手臂位置（是否有挥动或推搡动作）
                    # 提取手腕关键点
                    p1_left_wrist = person1_kps[self.KEYPOINT_DICT['left_wrist']]
                    p1_right_wrist = person1_kps[self.KEYPOINT_DICT['right_wrist']]
                    p2_left_wrist = person2_kps[self.KEYPOINT_DICT['left_wrist']]
                    p2_right_wrist = person2_kps[self.KEYPOINT_DICT['right_wrist']]
                    
                    # 检查是否有手腕朝向对方（可能是推搡或击打）
                    arms_engaged = False
                    if p1_left_wrist[2] > 0.3 and p1_right_wrist[2] > 0.3:
                        # 检查手腕是否在肩膀前方且靠近对方
                        p1_shoulder_center = (person1_kps[self.KEYPOINT_DICT['left_shoulder']][:2] + 
                                            person1_kps[self.KEYPOINT_DICT['right_shoulder']][:2]) / 2
                        
                        # 检查任一手腕是否在向对方方向移动
                        wrist_to_p2_left = np.linalg.norm(p1_left_wrist[:2] - person2_center)
                        wrist_to_p2_right = np.linalg.norm(p1_right_wrist[:2] - person2_center)
                        shoulder_to_p2 = np.linalg.norm(p1_shoulder_center - person2_center)
                        
                        if wrist_to_p2_left < shoulder_to_p2 or wrist_to_p2_right < shoulder_to_p2:
                            arms_engaged = True
                            print(f"检测到person1手臂朝向person2")
                    
                    # 条件3：检查两人是否有身体接触（关键点重叠）
                    has_overlap = False
                    for kp1 in p1_valid_kps:
                        for kp2 in p2_valid_kps:
                            kp_distance = np.linalg.norm(kp1 - kp2)
                            if kp_distance < image_shape[1] * 0.05:  # 关键点距离很近
                                has_overlap = True
                                break
                        if has_overlap:
                            break
                    
                    # 综合判断
                    fight_confidence = 0.0
                    if distance_ratio < 0.15:  # 非常近
                        fight_confidence += 0.4
                    elif distance_ratio < 0.25:  # 很近
                        fight_confidence += 0.2
                    
                    if arms_engaged:
                        fight_confidence += 0.3
                    
                    if has_overlap:
                        fight_confidence += 0.3
                        print(f"检测到身体接触")
                    
                    print(f"打架置信度: {fight_confidence:.2f}")
                    
                    # 如果置信度超过0.6，判定为打架
                    if fight_confidence >= 0.6:
                        return {
                            'is_fight': True,
                            'confidence': min(0.95, fight_confidence),
                            'description': f'检测到打架行为（距离={distance_ratio:.2f}, 置信度={fight_confidence:.2f}）'
                        }
            
            return {
                'is_fight': False,
                'confidence': 0.0,
                'description': '未检测到打架'
            }
        except Exception as e:
            print(f"打架检测错误: {e}")
            import traceback
            traceback.print_exc()
            return {
                'is_fight': False,
                'confidence': 0.0,
                'description': f'检测失败: {str(e)}'
            }

