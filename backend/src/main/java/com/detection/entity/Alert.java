package com.detection.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 告警记录实体类
 */
@Data
@Entity
@Table(name = "alerts")
public class Alert {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private Long userId;
    
    @Column(nullable = false)
    private Long recordId; // 关联检测记录ID
    
    @Column(length = 50, nullable = false)
    private String alertType; // 告警类型：FALL, FIGHT, INTRUSION等
    
    @Column(nullable = false)
    private String alertLevel = "MEDIUM"; // 告警级别：LOW, MEDIUM, HIGH, CRITICAL
    
    @Column(nullable = false)
    private Float confidence; // 置信度
    
    @Column(columnDefinition = "TEXT")
    private String description; // 告警描述
    
    @Column(columnDefinition = "TEXT")
    private String detailData; // 详细数据JSON
    
    @Column(length = 500)
    private String snapshotPath; // 告警快照图片路径
    
    @Column(nullable = false)
    private Boolean isRead = false; // 是否已读
    
    @Column(nullable = false)
    private Boolean isHandled = false; // 是否已处理
    
    @Column
    private String handledBy; // 处理人
    
    @Column
    private LocalDateTime handledAt; // 处理时间
    
    @Column(columnDefinition = "TEXT")
    private String handleNote; // 处理备注
    
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

