package com.detection.repository;

import com.detection.entity.DetectionRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/**
 * 检测记录数据访问层
 */
@Repository
public interface DetectionRecordRepository extends JpaRepository<DetectionRecord, Long> {
    
    Page<DetectionRecord> findByUserId(Long userId, Pageable pageable);
    
    List<DetectionRecord> findByUserId(Long userId);
    
    List<DetectionRecord> findByUserIdAndHasAbnormal(Long userId, Boolean hasAbnormal);
    
    Long countByUserId(Long userId);
    
    Long countByUserIdAndHasAbnormal(Long userId, Boolean hasAbnormal);
    
    Long countByHasAbnormal(Boolean hasAbnormal);
}

