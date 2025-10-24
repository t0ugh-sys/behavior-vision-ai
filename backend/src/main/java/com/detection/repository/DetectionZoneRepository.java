package com.detection.repository;

import com.detection.entity.DetectionZone;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/**
 * 检测区域数据访问层
 */
@Repository
public interface DetectionZoneRepository extends JpaRepository<DetectionZone, Long> {
    
    List<DetectionZone> findByUserId(Long userId);
    
    List<DetectionZone> findByUserIdAndIsActive(Long userId, Boolean isActive);
    
    List<DetectionZone> findByUserIdAndCameraId(Long userId, String cameraId);
}

