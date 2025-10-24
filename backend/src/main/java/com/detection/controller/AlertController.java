package com.detection.controller;

import com.detection.entity.Alert;
import com.detection.dto.ApiResponse;
import com.detection.service.AlertService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 告警控制器
 */
@RestController
@RequestMapping("/alerts")
@RequiredArgsConstructor
public class AlertController {
    
    private final AlertService alertService;
    
    /**
     * 接收Python服务的告警通知
     */
    @PostMapping("/notify")
    public ApiResponse<Alert> receiveAlert(@RequestBody Map<String, Object> alertData) {
        try {
            Alert alert = new Alert();
            alert.setUserId(Long.valueOf(alertData.get("user_id").toString()));
            alert.setRecordId(Long.valueOf(alertData.getOrDefault("record_id", 0L).toString()));
            alert.setAlertType(alertData.get("alert_type").toString());
            alert.setAlertLevel(alertData.getOrDefault("alert_level", "MEDIUM").toString());
            alert.setConfidence(Float.valueOf(alertData.get("confidence").toString()));
            alert.setDescription(alertData.getOrDefault("description", "").toString());
            alert.setDetailData(alertData.getOrDefault("detail_data", "{}").toString());
            alert.setSnapshotPath(alertData.getOrDefault("snapshot_path", "").toString());
            
            Alert savedAlert = alertService.createAlert(alert);
            
            return ApiResponse.success("告警已记录并推送", savedAlert);
        } catch (Exception e) {
            return ApiResponse.error("处理告警失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取用户的告警列表
     */
    @GetMapping("/user/{userId}")
    public ApiResponse<Page<Alert>> getUserAlerts(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        try {
            PageRequest pageRequest = PageRequest.of(page, size, Sort.by("createdAt").descending());
            Page<Alert> alerts = alertService.getUserAlerts(userId, pageRequest);
            return ApiResponse.success(alerts);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取未处理的告警
     */
    @GetMapping("/user/{userId}/unhandled")
    public ApiResponse<List<Alert>> getUnhandledAlerts(@PathVariable Long userId) {
        try {
            List<Alert> alerts = alertService.getUnhandledAlerts(userId);
            return ApiResponse.success(alerts);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 处理告警
     */
    @PutMapping("/{alertId}/handle")
    public ApiResponse<Alert> handleAlert(
            @PathVariable Long alertId,
            @RequestBody Map<String, String> handleData) {
        
        try {
            String handledBy = handleData.get("handled_by");
            String handleNote = handleData.getOrDefault("handle_note", "");
            
            Alert alert = alertService.handleAlert(alertId, handledBy, handleNote);
            return ApiResponse.success("告警已处理", alert);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取告警统计
     */
    @GetMapping("/statistics/{userId}")
    public ApiResponse<Map<String, Object>> getAlertStatistics(@PathVariable Long userId) {
        try {
            Map<String, Object> statistics = alertService.getAlertStatistics(userId);
            return ApiResponse.success(statistics);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取时间范围内的告警
     */
    @GetMapping("/user/{userId}/range")
    public ApiResponse<List<Alert>> getAlertsByTimeRange(
            @PathVariable Long userId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        
        try {
            List<Alert> alerts = alertService.getAlertsByTimeRange(userId, start, end);
            return ApiResponse.success(alerts);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 标记告警为已读
     */
    @PutMapping("/{alertId}/read")
    public ApiResponse<Alert> markAsRead(@PathVariable Long alertId) {
        try {
            Alert alert = alertService.markAsRead(alertId);
            return ApiResponse.success("已标记为已读", alert);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 批量标记所有告警为已读
     */
    @PutMapping("/user/{userId}/read-all")
    public ApiResponse<Void> markAllAsRead(@PathVariable Long userId) {
        try {
            alertService.markAllAsRead(userId);
            return ApiResponse.success("所有告警已标记为已读", null);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取未读告警数量
     */
    @GetMapping("/user/{userId}/unread-count")
    public ApiResponse<Long> getUnreadCount(@PathVariable Long userId) {
        try {
            Long count = alertService.getUnreadCount(userId);
            return ApiResponse.success(count);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 删除告警
     */
    @DeleteMapping("/{alertId}")
    public ApiResponse<Void> deleteAlert(@PathVariable Long alertId) {
        try {
            alertService.deleteAlert(alertId);
            return ApiResponse.success("告警删除成功", null);
        } catch (Exception e) {
            return ApiResponse.error("删除告警失败: " + e.getMessage());
        }
    }
    
    /**
     * 批量删除告警
     */
    @DeleteMapping("/batch")
    public ApiResponse<Void> batchDeleteAlerts(@RequestBody List<Long> alertIds) {
        try {
            alertService.batchDeleteAlerts(alertIds);
            return ApiResponse.success("批量删除成功", null);
        } catch (Exception e) {
            return ApiResponse.error("批量删除失败: " + e.getMessage());
        }
    }
}

