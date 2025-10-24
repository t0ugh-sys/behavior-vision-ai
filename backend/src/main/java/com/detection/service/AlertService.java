package com.detection.service;

import com.detection.entity.Alert;
import com.detection.repository.AlertRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 告警服务
 */
@Service
@RequiredArgsConstructor
public class AlertService {
    
    private final AlertRepository alertRepository;
    private final SimpMessagingTemplate messagingTemplate;
    
    /**
     * 创建告警并推送到前端
     */
    @Transactional
    public Alert createAlert(Alert alert) {
        // 保存告警记录
        Alert savedAlert = alertRepository.save(alert);
        
        // 通过WebSocket推送到前端
        pushAlertToFrontend(savedAlert);
        
        return savedAlert;
    }
    
    /**
     * 通过WebSocket推送告警到前端
     */
    private void pushAlertToFrontend(Alert alert) {
        Map<String, Object> message = new HashMap<>();
        message.put("id", alert.getId());
        message.put("userId", alert.getUserId());
        message.put("alertType", alert.getAlertType());
        message.put("alertLevel", alert.getAlertLevel());
        message.put("confidence", alert.getConfidence());
        message.put("description", alert.getDescription());
        message.put("snapshotPath", alert.getSnapshotPath());
        message.put("createdAt", alert.getCreatedAt());
        
        // 推送到指定用户的告警通道
        messagingTemplate.convertAndSend("/topic/alerts/" + alert.getUserId(), message);
        
        // 推送到全局告警通道（管理员）
        messagingTemplate.convertAndSend("/topic/alerts/all", message);
    }
    
    /**
     * 获取用户的告警列表
     */
    public Page<Alert> getUserAlerts(Long userId, Pageable pageable) {
        return alertRepository.findByUserId(userId, pageable);
    }
    
    /**
     * 获取未处理的告警
     */
    public List<Alert> getUnhandledAlerts(Long userId) {
        return alertRepository.findByUserIdAndIsHandled(userId, false);
    }
    
    /**
     * 处理告警
     */
    @Transactional
    public Alert handleAlert(Long alertId, String handledBy, String handleNote) {
        Alert alert = alertRepository.findById(alertId)
                .orElseThrow(() -> new RuntimeException("告警记录不存在"));
        
        alert.setIsHandled(true);
        alert.setHandledBy(handledBy);
        alert.setHandledAt(LocalDateTime.now());
        alert.setHandleNote(handleNote);
        
        Alert updatedAlert = alertRepository.save(alert);
        
        // 推送告警处理通知
        Map<String, Object> message = new HashMap<>();
        message.put("action", "handled");
        message.put("alertId", alertId);
        message.put("handledBy", handledBy);
        message.put("handledAt", updatedAlert.getHandledAt());
        
        messagingTemplate.convertAndSend("/topic/alerts/" + alert.getUserId(), message);
        
        return updatedAlert;
    }
    
    /**
     * 获取告警统计
     */
    public Map<String, Object> getAlertStatistics(Long userId) {
        Long totalAlerts = alertRepository.countByUserIdAndIsHandled(userId, false) 
                         + alertRepository.countByUserIdAndIsHandled(userId, true);
        Long unhandledAlerts = alertRepository.countByUserIdAndIsHandled(userId, false);
        Long handledAlerts = alertRepository.countByUserIdAndIsHandled(userId, true);
        
        Map<String, Object> statistics = new HashMap<>();
        statistics.put("total_alerts", totalAlerts);
        statistics.put("unhandled_alerts", unhandledAlerts);
        statistics.put("handled_alerts", handledAlerts);
        
        return statistics;
    }
    
    /**
     * 获取时间范围内的告警
     */
    public List<Alert> getAlertsByTimeRange(Long userId, LocalDateTime start, LocalDateTime end) {
        return alertRepository.findByUserIdAndCreatedAtBetween(userId, start, end);
    }
    
    /**
     * 标记告警为已读
     */
    @Transactional
    public Alert markAsRead(Long alertId) {
        Alert alert = alertRepository.findById(alertId)
                .orElseThrow(() -> new RuntimeException("告警记录不存在"));
        
        alert.setIsRead(true);
        return alertRepository.save(alert);
    }
    
    /**
     * 批量标记告警为已读
     */
    @Transactional
    public void markAllAsRead(Long userId) {
        List<Alert> unreadAlerts = alertRepository.findByUserIdAndIsRead(userId, false);
        unreadAlerts.forEach(alert -> alert.setIsRead(true));
        alertRepository.saveAll(unreadAlerts);
    }
    
    /**
     * 获取未读告警数量
     */
    public Long getUnreadCount(Long userId) {
        return alertRepository.countByUserIdAndIsRead(userId, false);
    }
    
    /**
     * 删除告警及相关文件
     */
    @Transactional
    public void deleteAlert(Long alertId) {
        Alert alert = alertRepository.findById(alertId)
                .orElseThrow(() -> new RuntimeException("告警记录不存在"));
        
        // 删除快照文件
        if (alert.getSnapshotPath() != null && !alert.getSnapshotPath().isEmpty()) {
            deleteFileIfExists(alert.getSnapshotPath());
        }
        
        // 删除告警记录
        alertRepository.delete(alert);
    }
    
    /**
     * 批量删除告警
     */
    @Transactional
    public void batchDeleteAlerts(List<Long> alertIds) {
        for (Long alertId : alertIds) {
            deleteAlert(alertId);
        }
    }
    
    /**
     * 删除文件（如果存在）
     */
    private void deleteFileIfExists(String filePath) {
        if (filePath == null || filePath.isEmpty()) {
            return;
        }
        
        try {
            // 处理可能的相对路径
            String actualPath = filePath;
            if (!filePath.startsWith("/") && !filePath.contains(":")) {
                // 相对路径，添加python-service前缀
                actualPath = "python-service/" + filePath;
            }
            
            java.io.File file = new java.io.File(actualPath);
            if (file.exists()) {
                if (file.delete()) {
                    System.out.println("✓ 已删除告警快照: " + actualPath);
                } else {
                    System.err.println("✗ 删除告警快照失败: " + actualPath);
                }
            }
        } catch (Exception e) {
            System.err.println("✗ 删除告警快照异常: " + filePath + " - " + e.getMessage());
        }
    }
}

