package com.detection.repository;

import com.detection.entity.Alert;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 告警数据访问层
 */
@Repository
public interface AlertRepository extends JpaRepository<Alert, Long> {
    
    Page<Alert> findByUserId(Long userId, Pageable pageable);
    
    List<Alert> findByUserIdAndIsHandled(Long userId, Boolean isHandled);
    
    List<Alert> findByUserIdAndIsRead(Long userId, Boolean isRead);
    
    List<Alert> findByUserIdAndCreatedAtBetween(Long userId, LocalDateTime start, LocalDateTime end);
    
    Long countByUserIdAndIsHandled(Long userId, Boolean isHandled);
    
    Long countByUserIdAndIsRead(Long userId, Boolean isRead);
    
    Page<Alert> findByAlertTypeAndIsHandled(String alertType, Boolean isHandled, Pageable pageable);
}

