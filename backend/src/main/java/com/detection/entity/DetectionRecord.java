package com.detection.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 检测记录实体类
 */
@Data
@Entity
@Table(name = "detection_records")
public class DetectionRecord {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private Long userId;
    
    @Column(length = 500)
    private String videoPath; // 视频文件路径
    
    @Column(length = 500)
    private String imagePath; // 图片文件路径
    
    @Column(length = 500)
    private String visualizationUrl; // 可视化结果图片URL
    
    @Column(length = 20, nullable = false)
    private String sourceType; // VIDEO, IMAGE, REALTIME
    
    @Column(nullable = false)
    private Boolean hasAbnormal = false; // 是否检测到异常行为
    
    @Column(length = 100)
    private String behaviorType; // 异常行为类型：FALL, FIGHT, INTRUSION, etc.
    
    @Column(columnDefinition = "TEXT")
    private String detectionResult; // 检测结果JSON
    
    @Column
    private Float confidence; // 置信度
    
    @Column(length = 20)
    private String status = "PROCESSING"; // PROCESSING, COMPLETED, FAILED
    
    @Column(columnDefinition = "TEXT")
    private String errorMessage; // 错误信息
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(nullable = false)
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}

