"""
时序行为分析器
通过滑动窗口、多帧投票与置信度平滑减少单帧误报
"""
from collections import deque, Counter, defaultdict
from typing import Deque, Dict, Any, Tuple, Optional
import time


class TemporalBehaviorAnalyzer:
    """基于滑动窗口的时序分析器"""

    def __init__(
        self,
        window_size: int = 15,
        min_abnormal_ratio: float = 0.4,
        min_streak: int = 3,
        ema_alpha: float = 0.5,
        cooldown_seconds: int = 5,
    ) -> None:
        self.window_size = window_size
        self.min_abnormal_ratio = min_abnormal_ratio
        self.min_streak = min_streak
        self.ema_alpha = ema_alpha
        self.cooldown_seconds = cooldown_seconds

        self.frames: Deque[Dict[str, Any]] = deque(maxlen=window_size)
        self.ema_confidence: Dict[str, float] = defaultdict(float)
        self.current_streak_behavior: Optional[str] = None
        self.current_streak_count: int = 0
        self.last_alert_time: Dict[str, float] = {}

    def update(self, result: Dict[str, Any]) -> None:
        """更新滑动窗口与内部状态"""
        frame = {
            'ts': time.time(),
            'has_abnormal': bool(result.get('has_abnormal', False)),
            'behavior_type': result.get('behavior_type'),
            'confidence': float(result.get('confidence', 0.0)),
        }
        self.frames.append(frame)

        # 更新EMA（按行为类型）
        if frame['has_abnormal'] and frame['behavior_type']:
            b = frame['behavior_type']
            prev = self.ema_confidence[b]
            self.ema_confidence[b] = (
                self.ema_alpha * frame['confidence'] + (1 - self.ema_alpha) * prev
            )

        # 更新连续计数（按主导行为）
        if frame['has_abnormal'] and frame['behavior_type']:
            if self.current_streak_behavior == frame['behavior_type']:
                self.current_streak_count += 1
            else:
                self.current_streak_behavior = frame['behavior_type']
                self.current_streak_count = 1
        else:
            # 正常帧会减弱连续计数
            self.current_streak_behavior = None
            self.current_streak_count = 0

    def _window_stats(self) -> Tuple[float, Optional[str], float]:
        """返回窗口内：异常占比、主导行为、主导行为平均置信度"""
        if not self.frames:
            return 0.0, None, 0.0
        abnormal_frames = [f for f in self.frames if f['has_abnormal'] and f['behavior_type']]
        abnormal_ratio = len(abnormal_frames) / len(self.frames)
        if not abnormal_frames:
            return abnormal_ratio, None, 0.0
        counter = Counter([f['behavior_type'] for f in abnormal_frames])
        dominant_behavior, _ = counter.most_common(1)[0]
        avg_conf = (
            sum(f['confidence'] for f in abnormal_frames if f['behavior_type'] == dominant_behavior)
            / max(1, sum(1 for f in abnormal_frames if f['behavior_type'] == dominant_behavior))
        )
        return abnormal_ratio, dominant_behavior, avg_conf

    def should_alert(self, threshold: float = 0.7) -> Tuple[bool, Optional[str], float]:
        """根据窗口统计与冷却策略决定是否告警"""
        abnormal_ratio, behavior, avg_conf = self._window_stats()
        if behavior is None:
            return False, None, 0.0

        # 置信度取 EMA 与平均值的加权（更平滑）
        ema_conf = self.ema_confidence.get(behavior, 0.0)
        smoothed_conf = 0.6 * ema_conf + 0.4 * avg_conf

        # 条件：异常占比、连续帧、置信度
        if (
            abnormal_ratio >= self.min_abnormal_ratio
            and self.current_streak_behavior == behavior
            and self.current_streak_count >= self.min_streak
            and smoothed_conf >= threshold
        ):
            now = time.time()
            last = self.last_alert_time.get(behavior, 0)
            if now - last >= self.cooldown_seconds:
                self.last_alert_time[behavior] = now
                return True, behavior, smoothed_conf

        return False, None, smoothed_conf

    def reset(self) -> None:
        self.frames.clear()
        self.current_streak_behavior = None
        self.current_streak_count = 0
        # 不清 cooldown；冷却由时间控制


