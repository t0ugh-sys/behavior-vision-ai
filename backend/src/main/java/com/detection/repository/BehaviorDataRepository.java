package com.detection.repository;

import com.detection.entity.BehaviorData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

/**
 * 行为数据访问层
 */
@Repository
public interface BehaviorDataRepository extends JpaRepository<BehaviorData, Long> {
    
    List<BehaviorData> findByRecordId(Long recordId);
    
    List<BehaviorData> findByUserId(Long userId);
    
    List<BehaviorData> findByUserIdAndBehaviorType(Long userId, String behaviorType);
    
    void deleteByRecordId(Long recordId);
}

