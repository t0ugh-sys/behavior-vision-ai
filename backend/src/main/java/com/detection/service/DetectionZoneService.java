package com.detection.service;

import com.detection.entity.DetectionZone;
import com.detection.repository.DetectionZoneRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 检测区域服务
 */
@Service
@RequiredArgsConstructor
public class DetectionZoneService {
    
    private final DetectionZoneRepository zoneRepository;
    
    /**
     * 创建检测区域
     */
    @Transactional
    public DetectionZone createZone(DetectionZone zone) {
        return zoneRepository.save(zone);
    }
    
    /**
     * 更新检测区域
     */
    @Transactional
    public DetectionZone updateZone(Long zoneId, DetectionZone zone) {
        DetectionZone existingZone = zoneRepository.findById(zoneId)
                .orElseThrow(() -> new RuntimeException("区域不存在"));
        
        existingZone.setZoneName(zone.getZoneName());
        existingZone.setZoneType(zone.getZoneType());
        existingZone.setCoordinates(zone.getCoordinates());
        existingZone.setShape(zone.getShape());
        existingZone.setIsActive(zone.getIsActive());
        existingZone.setEnableAlert(zone.getEnableAlert());
        existingZone.setAlertLevel(zone.getAlertLevel());
        existingZone.setDescription(zone.getDescription());
        existingZone.setCameraId(zone.getCameraId());
        existingZone.setImageWidth(zone.getImageWidth());
        existingZone.setImageHeight(zone.getImageHeight());
        
        return zoneRepository.save(existingZone);
    }
    
    /**
     * 删除检测区域
     */
    @Transactional
    public void deleteZone(Long zoneId) {
        zoneRepository.deleteById(zoneId);
    }
    
    /**
     * 获取用户的所有区域
     */
    public List<DetectionZone> getUserZones(Long userId) {
        return zoneRepository.findByUserId(userId);
    }
    
    /**
     * 获取用户的启用区域
     */
    public List<DetectionZone> getActiveZones(Long userId) {
        return zoneRepository.findByUserIdAndIsActive(userId, true);
    }
    
    /**
     * 获取指定区域
     */
    public DetectionZone getZone(Long zoneId) {
        return zoneRepository.findById(zoneId)
                .orElseThrow(() -> new RuntimeException("区域不存在"));
    }
    
    /**
     * 切换区域状态
     */
    @Transactional
    public DetectionZone toggleZoneStatus(Long zoneId) {
        DetectionZone zone = getZone(zoneId);
        zone.setIsActive(!zone.getIsActive());
        return zoneRepository.save(zone);
    }
}

