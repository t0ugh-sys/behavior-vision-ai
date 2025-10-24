package com.detection.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 行为数据实体类
 */
@Data
@Entity
@Table(name = "behavior_data")
public class BehaviorData {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private Long recordId; // 关联检测记录ID
    
    @Column(nullable = false)
    private Long userId;
    
    @Column(length = 50, nullable = false)
    private String behaviorType; // 行为类型
    
    @Column(nullable = false)
    private Float confidence; // 置信度
    
    @Column
    private Integer frameNumber; // 帧号（视频）
    
    @Column
    private Float timestamp; // 时间戳（秒）
    
    @Column(columnDefinition = "TEXT")
    private String boundingBox; // 边界框坐标JSON: [x, y, width, height]
    
    @Column(columnDefinition = "TEXT")
    private String keypoints; // 关键点坐标JSON
    
    @Column(columnDefinition = "TEXT")
    private String additionalInfo; // 额外信息JSON
    
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}

