"""
人体异常行为检测服务 - FastAPI主应用
"""
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
import cv2
import io
import numpy as np
from pathlib import Path

from detector import BehaviorDetector
from alert_notifier import notifier
from rtsp_handler import RTSPStreamHandler
import time

# 记录服务启动时间
start_time = time.time()

app = FastAPI(
    title="人体异常行为检测服务",
    description="基于YOLOv8的人体异常行为检测API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化检测器
detector = BehaviorDetector()

# 初始化RTSP流处理器
rtsp_handler = RTSPStreamHandler(detector, notifier)

# 创建必要的目录
UPLOAD_DIR = Path("uploads")
TEMP_DIR = Path("temp")
VISUALIZATIONS_DIR = Path("visualizations")
SNAPSHOT_DIR = Path("snapshots")

for directory in [UPLOAD_DIR, TEMP_DIR, VISUALIZATIONS_DIR, SNAPSHOT_DIR]:
    directory.mkdir(exist_ok=True)

# 挂载静态文件目录
app.mount("/visualizations", StaticFiles(directory=str(VISUALIZATIONS_DIR)), name="visualizations")
app.mount("/snapshots", StaticFiles(directory=str(SNAPSHOT_DIR)), name="snapshots")


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "人体异常行为检测服务正在运行"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    import psutil
    import time
    
    # 获取系统资源使用情况
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    return {
        "status": "UP",
        "service": "python-detection",
        "model_loaded": detector.model is not None,
        "model_name": "yolov8n-pose.pt",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - start_time),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_used_mb": memory.used / (1024 * 1024),
            "memory_total_mb": memory.total / (1024 * 1024),
            "memory_percent": memory.percent
        }
    }


@app.post("/detect")
async def detect_behavior(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    user_id: int = Form(None),
    record_id: int = Form(None),
    enable_alert: bool = Form(True)
):
    """
    检测异常行为
    
    参数:
        file: 上传的图片或视频文件
        source_type: 来源类型 (IMAGE, VIDEO, REALTIME)
        user_id: 用户ID（如果启用告警则必填）
        record_id: 记录ID（可选）
        enable_alert: 是否启用告警推送
    
    返回:
        检测结果JSON
    """
    try:
        # 保存上传的文件
        file_extension = os.path.splitext(file.filename)[1]
        temp_file_path = TEMP_DIR / f"temp_{file.filename}"
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 生成可视化文件路径（使用纯ASCII文件名避免编码问题）
        import time
        import uuid
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # 根据类型进行检测
        if source_type == "IMAGE":
            # 图片：保留原扩展名
            vis_filename = f"vis_{timestamp}_{unique_id}{file_extension}"
            vis_path = VISUALIZATIONS_DIR / vis_filename
            
            result = detector.detect_image(str(temp_file_path), visualize=True, output_path=str(vis_path))
            # 添加可视化图片URL（使用URL编码）
            from urllib.parse import quote
            result['visualization_url'] = f"http://localhost:5000/visualizations/{quote(vis_filename)}"
            
        elif source_type == "VIDEO":
            # 视频：统一使用.mp4扩展名
            vis_filename = f"vis_{timestamp}_{unique_id}.mp4"
            vis_path = VISUALIZATIONS_DIR / vis_filename
            
            # 使用OpenCV直接生成可视化视频
            result = detector.detect_video(str(temp_file_path), visualize=True, output_path=str(vis_path))
            
            # 添加可视化视频URL（使用URL编码）
            from urllib.parse import quote
            result['visualization_url'] = f"http://localhost:5000/visualizations/{quote(vis_filename)}"
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"不支持的源类型: {source_type}"}
            )
        
        # 如果检测到异常且启用告警，发送告警通知
        if enable_alert and result['has_abnormal'] and user_id is not None:
            try:
                # 保存快照
                import time
                import cv2
                import shutil
                snapshot_filename = f"{result['behavior_type']}_{int(time.time())}.jpg"
                snapshot_file_path = SNAPSHOT_DIR / snapshot_filename
                
                if source_type == "IMAGE":
                    # 图片直接复制
                    shutil.copy(str(temp_file_path), str(snapshot_file_path))
                elif source_type == "VIDEO":
                    # 视频提取第一帧作为快照
                    cap = cv2.VideoCapture(str(temp_file_path))
                    ret, frame = cap.read()
                    if ret:
                        cv2.imwrite(str(snapshot_file_path), frame)
                    cap.release()
                
                # 创建并发送告警
                alert_data = notifier.create_alert_from_detection(
                    user_id=user_id,
                    detection_result=result,
                    record_id=record_id,
                    snapshot_path=f"snapshots/{snapshot_filename}"
                )
                
                # 发送通知
                notifier.send_alert(alert_data)
            except Exception as alert_error:
                # 告警发送失败不影响检测结果返回
                print(f"告警发送失败: {alert_error}")
        
        # 清理临时文件
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        return JSONResponse(content=result)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"检测失败详细错误:\n{error_trace}")
        return JSONResponse(
            status_code=500,
            content={"error": f"检测失败: {str(e)}", "detail": error_trace}
        )


@app.post("/detect/realtime")
async def detect_realtime(
    file: UploadFile = File(...),
    user_id: int = Form(None)
):
    """
    实时检测（单帧）
    """
    try:
        # 读取图片
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return JSONResponse(
                status_code=400,
                content={"error": "无法读取图片"}
            )
        
        # 检测
        results = detector.model(frame)
        result = detector._analyze_results(results, frame.shape)
        
        # 可视化
        vis_frame = detector._visualize_frame(frame, results, result)
        
        # 编码为JPEG
        _, buffer = cv2.imencode('.jpg', vis_frame)
        
        return StreamingResponse(
            io.BytesIO(buffer.tobytes()),
            media_type="image/jpeg"
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"实时检测失败: {str(e)}"}
        )


# ==================== RTSP流处理API ====================

class RTSPConfig(BaseModel):
    rtsp_url: str
    detection_interval: int = 1
    enable_alert: bool = True
    user_id: int = None


@app.post("/rtsp/start")
async def start_rtsp(config: RTSPConfig):
    """启动RTSP流检测"""
    try:
        rtsp_handler.start(
            rtsp_url=config.rtsp_url,
            detection_interval=config.detection_interval,
            enable_alert=config.enable_alert,
            user_id=config.user_id
        )
        return {"status": "success", "message": "RTSP流检测已启动"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"启动RTSP流失败: {str(e)}"}
        )


@app.post("/rtsp/stop")
async def stop_rtsp():
    """停止RTSP流检测"""
    try:
        rtsp_handler.stop()
        return {"status": "success", "message": "RTSP流检测已停止"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"停止RTSP流失败: {str(e)}"}
        )


@app.get("/rtsp/frame")
async def get_rtsp_frame():
    """获取RTSP流的最新帧"""
    try:
        frame = rtsp_handler.get_latest_frame()
        if frame is None:
            return JSONResponse(
                status_code=404,
                content={"error": "暂无视频帧"}
            )
        
        _, buffer = cv2.imencode('.jpg', frame)
        return StreamingResponse(
            io.BytesIO(buffer.tobytes()),
            media_type="image/jpeg"
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"获取视频帧失败: {str(e)}"}
        )


@app.get("/rtsp/result")
async def get_rtsp_result():
    """获取RTSP流的最新检测结果"""
    try:
        result = rtsp_handler.get_latest_result()
        if result is None:
            return {"has_abnormal": False, "person_count": 0}
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"获取检测结果失败: {str(e)}"}
        )


@app.get("/rtsp/status")
async def get_rtsp_status():
    """获取RTSP流状态"""
    return {
        "is_running": rtsp_handler.is_running,
        "rtsp_url": rtsp_handler.rtsp_url if rtsp_handler.rtsp_url else None
    }


if __name__ == "__main__":
    print("\n" + "="*40)
    print("   Python Detection Service")
    print("   Conda Environment: ultralytics")
    print("="*40 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        reload=False  # 禁用热重载，避免启动两个进程
    )

