# 异常行为检测算法说明

## 概述

本系统使用 **YOLOv8-Pose** 模型进行人体姿态估计，然后基于关键点位置关系判断异常行为。

## 检测流程

```
输入图片/视频帧
    ↓
YOLOv8-Pose提取人体关键点（17个COCO关键点）
    ↓
分析关键点位置关系
    ↓
判断是否存在异常行为
    ↓
输出检测结果
```

## YOLOv8-Pose模型

### 为什么使用YOLOv8-Pose而不是普通YOLOv8？

| 特性 | YOLOv8（目标检测） | YOLOv8-Pose（姿态估计） |
|------|-------------------|------------------------|
| 输出 | 边界框 + 类别 | 边界框 + 17个关键点 |
| 适用场景 | 识别物体类别 | 识别人体姿态 |
| 异常行为检测 | 只能检测人的存在 | 可以分析人体姿态判断行为 |

**结论**：异常行为检测需要分析人体姿态，因此必须使用YOLOv8-Pose。

### 17个COCO关键点

```
0: nose (鼻子)
1: left_eye (左眼)          2: right_eye (右眼)
3: left_ear (左耳)          4: right_ear (右耳)
5: left_shoulder (左肩)     6: right_shoulder (右肩)
7: left_elbow (左肘)        8: right_elbow (右肘)
9: left_wrist (左腕)        10: right_wrist (右腕)
11: left_hip (左髋)         12: right_hip (右髋)
13: left_knee (左膝)        14: right_knee (右膝)
15: left_ankle (左踝)       16: right_ankle (右踝)
```

每个关键点包含：`[x坐标, y坐标, 置信度]`

## 异常行为检测算法

### 1. 跌倒检测 (FALL)

#### 检测原理

人体正常站立时，躯干应该接近垂直；跌倒时躯干会接近水平。

#### 检测步骤

```python
# 1. 提取关键点
nose = 鼻子位置
left_shoulder, right_shoulder = 左右肩膀位置
left_hip, right_hip = 左右髋部位置

# 2. 计算中心点
shoulder_center = (left_shoulder + right_shoulder) / 2
hip_center = (left_hip + right_hip) / 2

# 3. 计算躯干角度（相对于垂直方向）
dx = shoulder_center.x - hip_center.x
dy = shoulder_center.y - hip_center.y
angle = abs(atan2(dx, dy) * 180 / π)

# 4. 判断跌倒
if angle > 60°:  # 躯干倾斜超过60度
    # 5. 检查头部高度
    head_ratio = nose.y / 图片高度
    
    if head_ratio > 0.6:  # 头部在图片下半部分
        # 确认为跌倒
        is_fall = True
        confidence = min(0.95, (angle - 60) / 30 * 0.5 + 0.45)
```

#### 判断条件

| 条件 | 阈值 | 说明 |
|------|------|------|
| 躯干倾斜角度 | > 60° | 相对于垂直方向 |
| 头部位置 | > 0.6 | 在图片下60%的位置 |
| 关键点置信度 | > 0.5 | 确保关键点准确 |

#### 置信度计算

```
confidence = min(0.95, (angle - 60) / 30 * 0.5 + 0.45)
```

- angle = 60°时，confidence ≈ 0.45
- angle = 90°时，confidence ≈ 0.95
- 角度越大，置信度越高

#### 示例场景

✅ **会被检测为跌倒**：
- 人躺在地上
- 人侧倒在地
- 人趴在地上

❌ **不会被检测为跌倒**：
- 正常站立
- 坐着（头部位置较高）
- 蹲着（角度通常 < 60°）

---

### 2. 异常姿态检测 (ABNORMAL_POSE)

#### 检测原理

如果检测到的有效关键点过少，可能表示：
- 人体姿态异常
- 人体部分被遮挡
- 非正常姿势

#### 检测步骤

```python
# 1. 统计有效关键点
valid_keypoints = count(置信度 > 0.5的关键点)
total_keypoints = 17

# 2. 计算比例
valid_ratio = valid_keypoints / total_keypoints

# 3. 判断异常
if valid_ratio < 0.4:  # 有效关键点 < 40%
    is_abnormal = True
    confidence = 0.6
```

#### 判断条件

| 条件 | 阈值 | 说明 |
|------|------|------|
| 有效关键点比例 | < 40% | 少于7个有效关键点 |

#### 示例场景

✅ **会被检测为异常姿态**：
- 蜷缩在角落
- 扭曲的姿势
- 大部分身体被遮挡

❌ **不会被检测为异常姿态**：
- 正常站立、行走
- 正常坐姿
- 大部分关键点可见

---

### 3. 打架检测 (FIGHT)

#### 检测原理

打架时通常两人距离很近，身体接触或靠近。

#### 检测步骤

```python
# 1. 检查人数
if 检测到的人数 < 2:
    return 无法检测

# 2. 提取两人关键点
person1_keypoints = 第一个人的关键点
person2_keypoints = 第二个人的关键点

# 3. 计算身体中心点
center1 = mean(person1有效关键点的坐标)
center2 = mean(person2有效关键点的坐标)

# 4. 计算距离
distance = ||center1 - center2||  # 欧氏距离

# 5. 判断打架
if distance < 100像素:
    is_fight = True
    confidence = 0.7
```

#### 判断条件

| 条件 | 阈值 | 说明 |
|------|------|------|
| 人数 | ≥ 2 | 至少两个人 |
| 身体距离 | < 100像素 | 身体中心点距离 |

#### 示例场景

✅ **会被检测为打架**：
- 两人紧密接触
- 两人拥抱（会误报）
- 两人推搡

❌ **不会被检测为打架**：
- 两人相距较远
- 单人场景
- 两人并排站立

⚠️ **局限性**：
- 当前算法较简单，仅基于距离
- 可能误报：拥抱、亲密接触等
- 需要改进：结合动作分析、手臂位置等

---

## 检测优先级

系统按以下优先级检测异常行为：

1. **跌倒检测**（最高优先级）
2. **异常姿态检测**
3. **打架检测**
4. 正常（无异常）

一旦检测到任何异常，立即返回结果，不再检测其他类型。

## 算法改进建议

### 当前算法的优点

✅ 简单高效，实时性好
✅ 无需训练，基于规则
✅ 可解释性强
✅ 计算量小

### 当前算法的局限性

❌ 规则固定，灵活性差
❌ 容易误报和漏报
❌ 无法检测复杂行为
❌ 对角度和距离依赖较强

### 改进方向

#### 1. 短期改进（规则优化）

**跌倒检测改进**：
```python
# 增加更多判断条件
def _detect_fall_advanced(keypoints, image_shape):
    # 1. 躯干角度
    trunk_angle = calculate_trunk_angle(keypoints)
    
    # 2. 四肢角度
    limb_angle = calculate_limb_angle(keypoints)
    
    # 3. 身体宽高比
    aspect_ratio = calculate_body_aspect_ratio(keypoints)
    
    # 4. 综合判断
    if trunk_angle > 60 and aspect_ratio > 1.5:
        return True
```

**打架检测改进**：
```python
def _detect_fight_advanced(persons):
    # 1. 距离判断
    distance = calculate_distance(persons)
    
    # 2. 手臂动作分析
    arm_movement = analyze_arm_movement(persons)
    
    # 3. 身体接触检测
    is_contact = detect_body_contact(persons)
    
    # 4. 综合判断
    if distance < threshold and arm_movement > threshold:
        return True
```

#### 2. 中期改进（时序分析）

使用时间序列分析，而不是单帧检测：

```python
# 分析多帧数据
def detect_with_temporal(frame_sequence):
    # 1. 提取多帧关键点
    keypoints_sequence = [extract_keypoints(frame) for frame in frames]
    
    # 2. 分析动作轨迹
    trajectory = analyze_trajectory(keypoints_sequence)
    
    # 3. 检测异常模式
    # 例如：突然倒地、快速位移等
    if detect_sudden_fall(trajectory):
        return 'FALL'
```

#### 3. 长期改进（深度学习）

训练专门的动作识别模型：

```python
# 使用深度学习模型
class ActionRecognitionModel:
    def __init__(self):
        # 加载预训练的动作识别模型
        # 如：ST-GCN, I3D, SlowFast等
        self.model = load_pretrained_model()
    
    def predict(self, keypoints_sequence):
        # 输入：时间序列的关键点
        # 输出：行为类别 + 置信度
        return self.model(keypoints_sequence)
```

推荐的动作识别模型：
- **ST-GCN**（Spatial Temporal Graph Convolutional Networks）
- **I3D**（Inflated 3D ConvNets）
- **SlowFast**
- **TimeSformer**

## 性能指标

### 当前算法性能

| 行为类型 | 准确率（估计） | 召回率（估计） | 处理速度 |
|---------|--------------|--------------|---------|
| 跌倒检测 | 70-80% | 60-70% | ~30 FPS |
| 异常姿态 | 50-60% | 40-50% | ~30 FPS |
| 打架检测 | 40-50% | 30-40% | ~30 FPS |

⚠️ **注意**：以上数据为估计值，实际性能取决于场景、光照、角度等因素。

### 性能测试方法

```bash
# 测试检测速度
python test_performance.py --input test_video.mp4

# 测试准确率（需要标注数据）
python test_accuracy.py --dataset labeled_data/
```

## 配置参数

可以通过修改配置文件调整检测参数：

```python
# config.py

# 跌倒检测参数
FALL_ANGLE_THRESHOLD = 60      # 角度阈值（度）
FALL_HEAD_RATIO_THRESHOLD = 0.6  # 头部位置阈值

# 异常姿态参数
ABNORMAL_POSE_RATIO = 0.4      # 有效关键点比例阈值

# 打架检测参数
FIGHT_DISTANCE_THRESHOLD = 100  # 距离阈值（像素）

# 关键点置信度阈值
KEYPOINT_CONFIDENCE_THRESHOLD = 0.5
```

## 调试和可视化

### 可视化关键点

```python
import cv2

def visualize_keypoints(image, keypoints):
    """在图片上绘制关键点"""
    for i, kp in enumerate(keypoints):
        x, y, conf = kp
        if conf > 0.5:
            cv2.circle(image, (int(x), int(y)), 3, (0, 255, 0), -1)
            cv2.putText(image, str(i), (int(x), int(y)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    return image
```

### 可视化骨架

```python
# 定义骨架连接
SKELETON = [
    [5, 6],   # 左肩-右肩
    [5, 7],   # 左肩-左肘
    [7, 9],   # 左肘-左腕
    [6, 8],   # 右肩-右肘
    [8, 10],  # 右肘-右腕
    [5, 11],  # 左肩-左髋
    [6, 12],  # 右肩-右髋
    [11, 12], # 左髋-右髋
    [11, 13], # 左髋-左膝
    [13, 15], # 左膝-左踝
    [12, 14], # 右髋-右膝
    [14, 16]  # 右膝-右踝
]

def draw_skeleton(image, keypoints):
    """绘制骨架"""
    for connection in SKELETON:
        pt1, pt2 = connection
        if keypoints[pt1][2] > 0.5 and keypoints[pt2][2] > 0.5:
            cv2.line(image, 
                    (int(keypoints[pt1][0]), int(keypoints[pt1][1])),
                    (int(keypoints[pt2][0]), int(keypoints[pt2][1])),
                    (0, 255, 0), 2)
```

## 总结

本系统使用**基于规则的姿态分析方法**检测异常行为：

1. **YOLOv8-Pose**提取人体关键点
2. **几何计算**分析关键点位置关系
3. **规则判断**识别异常行为模式

**优点**：简单、快速、可解释
**缺点**：准确率有限、容易误报

建议根据实际应用场景调整参数或采用更高级的算法。

