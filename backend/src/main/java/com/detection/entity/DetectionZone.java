package com.detection.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 检测区域实体类
 */
@Data
@Entity
@Table(name = "detection_zones")
public class DetectionZone {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private Long userId;
    
    @Column(length = 100, nullable = false)
    private String zoneName; // 区域名称
    
    @Column(length = 50)
    private String zoneType; // 区域类型：RESTRICTED(禁区), MONITORED(监控区), SAFE(安全区)
    
    @Column(columnDefinition = "TEXT", nullable = false)
    private String coordinates; // 区域坐标JSON: [[x1,y1],[x2,y2],...]
    
    @Column(length = 20)
    private String shape; // 形状类型：RECTANGLE(矩形), POLYGON(多边形), CIRCLE(圆形)
    
    @Column(nullable = false)
    private Boolean isActive = true; // 是否启用
    
    @Column(nullable = false)
    private Boolean enableAlert = true; // 是否启用告警
    
    @Column(length = 20)
    private String alertLevel = "MEDIUM"; // 告警级别
    
    @Column(columnDefinition = "TEXT")
    private String description; // 区域描述
    
    @Column(length = 500)
    private String cameraId; // 关联摄像头ID/RTSP地址
    
    @Column
    private Integer imageWidth; // 图像宽度（用于坐标转换）
    
    @Column
    private Integer imageHeight; // 图像高度
    
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

