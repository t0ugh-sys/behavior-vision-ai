-- ================================================
-- 人体异常行为检测系统 - 数据库架构
-- MySQL 8.0+
-- ================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS behavior_detection 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE behavior_detection;

-- ================================================
-- 用户表
-- ================================================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    email VARCHAR(50) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    real_name VARCHAR(50) COMMENT '真实姓名',
    role VARCHAR(20) NOT NULL DEFAULT 'USER' COMMENT '角色: USER, ADMIN',
    active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ================================================
-- 检测记录表
-- ================================================
CREATE TABLE IF NOT EXISTS detection_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    video_path VARCHAR(500) COMMENT '视频文件路径',
    image_path VARCHAR(500) COMMENT '图片文件路径',
    source_type VARCHAR(20) NOT NULL COMMENT '来源类型: VIDEO, IMAGE, REALTIME',
    has_abnormal BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否检测到异常行为',
    behavior_type VARCHAR(100) COMMENT '异常行为类型: fall, fight, abnormal_pose',
    detection_result TEXT COMMENT '检测结果JSON',
    confidence FLOAT COMMENT '置信度 (0-1)',
    status VARCHAR(20) NOT NULL DEFAULT 'PROCESSING' COMMENT '状态: PROCESSING, COMPLETED, FAILED',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_source_type (source_type),
    INDEX idx_behavior_type (behavior_type),
    INDEX idx_has_abnormal (has_abnormal),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    
    CONSTRAINT fk_detection_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检测记录表';

-- ================================================
-- 行为数据表（详细的帧级别数据）
-- ================================================
CREATE TABLE IF NOT EXISTS behavior_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '行为数据ID',
    record_id BIGINT NOT NULL COMMENT '检测记录ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    behavior_type VARCHAR(50) NOT NULL COMMENT '行为类型',
    confidence FLOAT NOT NULL COMMENT '置信度 (0-1)',
    frame_number INT COMMENT '帧号',
    timestamp FLOAT COMMENT '时间戳(秒)',
    bounding_box TEXT COMMENT '边界框坐标JSON [x1, y1, x2, y2]',
    keypoints TEXT COMMENT '关键点坐标JSON',
    additional_info TEXT COMMENT '额外信息JSON',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_record_id (record_id),
    INDEX idx_user_id (user_id),
    INDEX idx_behavior_type (behavior_type),
    INDEX idx_frame_number (frame_number),
    INDEX idx_created_at (created_at),
    
    CONSTRAINT fk_behavior_record FOREIGN KEY (record_id) 
        REFERENCES detection_records(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_behavior_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行为数据表';

-- ================================================
-- 告警表
-- ================================================
CREATE TABLE IF NOT EXISTS alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '告警ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    record_id BIGINT COMMENT '检测记录ID',
    alert_type VARCHAR(50) NOT NULL COMMENT '告警类型: fall, fight, abnormal_pose',
    alert_level VARCHAR(20) NOT NULL DEFAULT 'MEDIUM' COMMENT '告警级别: LOW, MEDIUM, HIGH, CRITICAL',
    confidence FLOAT NOT NULL COMMENT '置信度 (0-1)',
    description TEXT COMMENT '告警描述',
    detail_data TEXT COMMENT '详细数据JSON',
    snapshot_path VARCHAR(500) COMMENT '快照图片路径',
    is_read BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已读',
    is_handled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已处理',
    handled_by VARCHAR(50) COMMENT '处理人',
    handled_at DATETIME COMMENT '处理时间',
    handle_note TEXT COMMENT '处理备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_record_id (record_id),
    INDEX idx_alert_type (alert_type),
    INDEX idx_alert_level (alert_level),
    INDEX idx_is_read (is_read),
    INDEX idx_is_handled (is_handled),
    INDEX idx_created_at (created_at),
    
    CONSTRAINT fk_alert_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_alert_record FOREIGN KEY (record_id) 
        REFERENCES detection_records(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='告警表';

-- ================================================
-- 初始化数据
-- ================================================

-- 插入默认管理员用户
INSERT INTO users (username, password, email, real_name, role, active) 
VALUES ('admin', 'admin123', 'admin@example.com', '系统管理员', 'ADMIN', TRUE)
ON DUPLICATE KEY UPDATE username=username;

-- 插入测试用户（可选）
-- INSERT INTO users (username, password, email, real_name, role, active) 
-- VALUES ('test', 'test123', 'test@example.com', '测试用户', 'USER', TRUE)
-- ON DUPLICATE KEY UPDATE username=username;

-- ================================================
-- 数据库视图（可选）
-- ================================================

-- 用户统计视图
CREATE OR REPLACE VIEW v_user_statistics AS
SELECT 
    u.id AS user_id,
    u.username,
    u.real_name,
    COUNT(DISTINCT dr.id) AS total_detections,
    SUM(CASE WHEN dr.has_abnormal = TRUE THEN 1 ELSE 0 END) AS abnormal_count,
    COUNT(DISTINCT a.id) AS total_alerts,
    SUM(CASE WHEN a.is_read = FALSE THEN 1 ELSE 0 END) AS unread_alerts,
    SUM(CASE WHEN a.is_handled = FALSE THEN 1 ELSE 0 END) AS unhandled_alerts,
    MAX(dr.created_at) AS last_detection_time
FROM users u
LEFT JOIN detection_records dr ON u.id = dr.user_id
LEFT JOIN alerts a ON u.id = a.user_id
GROUP BY u.id, u.username, u.real_name;

-- 告警统计视图
CREATE OR REPLACE VIEW v_alert_statistics AS
SELECT 
    alert_type,
    alert_level,
    COUNT(*) AS alert_count,
    AVG(confidence) AS avg_confidence,
    SUM(CASE WHEN is_handled = FALSE THEN 1 ELSE 0 END) AS unhandled_count,
    DATE(created_at) AS alert_date
FROM alerts
GROUP BY alert_type, alert_level, DATE(created_at);

-- ================================================
-- 数据库完成
-- ================================================
