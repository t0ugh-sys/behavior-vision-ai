"""
配置文件
"""
import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
SNAPSHOT_DIR = BASE_DIR / "snapshots"
UPLOADS_DIR = BASE_DIR / "uploads"

# 创建必要的目录
TEMP_DIR.mkdir(exist_ok=True)
SNAPSHOT_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# Spring Boot后端配置
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080/api")
ALERT_ENDPOINT = f"{BACKEND_URL}/alerts/notify"

# 模型配置
MODEL_PATH = os.getenv("MODEL_PATH", "yolov8n-pose.pt")
MODEL_CONFIDENCE_THRESHOLD = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.5"))
MODEL_DEVICE = os.getenv("MODEL_DEVICE", "cpu")  # "cpu" or "cuda"
MODEL_HALF = os.getenv("MODEL_HALF", "false").lower() == "true"  # 半精度，仅CUDA
MODEL_IOU = float(os.getenv("MODEL_IOU", "0.45"))

# 检测配置
DETECTION_FRAME_SKIP = int(os.getenv("DETECTION_FRAME_SKIP", "5"))  # 视频检测跳帧数
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # MB

# 告警配置
ALERT_ENABLED = os.getenv("ALERT_ENABLED", "true").lower() == "true"
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "0.7"))
ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "5"))  # 秒

# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# 支持的文件格式
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

# 异常行为类型映射
BEHAVIOR_TYPE_NAMES = {
    "FALL": "跌倒",
    "FIGHT": "打架",
    "INTRUSION": "入侵",
    "ABNORMAL_POSE": "异常姿态"
}

# 告警级别映射
ALERT_LEVELS = {
    "CRITICAL": (0.9, 1.0),   # 0.9-1.0
    "HIGH": (0.75, 0.9),      # 0.75-0.9
    "MEDIUM": (0.6, 0.75),    # 0.6-0.75
    "LOW": (0.0, 0.6)         # 0.0-0.6
}

def get_alert_level(confidence: float) -> str:
    """根据置信度获取告警级别"""
    for level, (min_conf, max_conf) in ALERT_LEVELS.items():
        if min_conf <= confidence < max_conf:
            return level
    return "LOW"

