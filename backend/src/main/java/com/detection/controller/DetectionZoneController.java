package com.detection.controller;

import com.detection.dto.ApiResponse;
import com.detection.entity.DetectionZone;
import com.detection.service.DetectionZoneService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 检测区域控制器
 */
@RestController
@RequestMapping("/zones")
@RequiredArgsConstructor
public class DetectionZoneController {
    
    private final DetectionZoneService zoneService;
    
    /**
     * 创建检测区域
     */
    @PostMapping
    public ApiResponse<DetectionZone> createZone(@RequestBody DetectionZone zone) {
        try {
            DetectionZone created = zoneService.createZone(zone);
            return ApiResponse.success("区域创建成功", created);
        } catch (Exception e) {
            return ApiResponse.error("创建失败: " + e.getMessage());
        }
    }
    
    /**
     * 更新检测区域
     */
    @PutMapping("/{zoneId}")
    public ApiResponse<DetectionZone> updateZone(
            @PathVariable Long zoneId,
            @RequestBody DetectionZone zone) {
        try {
            DetectionZone updated = zoneService.updateZone(zoneId, zone);
            return ApiResponse.success("区域更新成功", updated);
        } catch (Exception e) {
            return ApiResponse.error("更新失败: " + e.getMessage());
        }
    }
    
    /**
     * 删除检测区域
     */
    @DeleteMapping("/{zoneId}")
    public ApiResponse<Void> deleteZone(@PathVariable Long zoneId) {
        try {
            zoneService.deleteZone(zoneId);
            return ApiResponse.success("区域删除成功", null);
        } catch (Exception e) {
            return ApiResponse.error("删除失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取用户的所有区域
     */
    @GetMapping("/user/{userId}")
    public ApiResponse<List<DetectionZone>> getUserZones(@PathVariable Long userId) {
        try {
            List<DetectionZone> zones = zoneService.getUserZones(userId);
            return ApiResponse.success(zones);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取用户的启用区域
     */
    @GetMapping("/user/{userId}/active")
    public ApiResponse<List<DetectionZone>> getActiveZones(@PathVariable Long userId) {
        try {
            List<DetectionZone> zones = zoneService.getActiveZones(userId);
            return ApiResponse.success(zones);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取指定区域
     */
    @GetMapping("/{zoneId}")
    public ApiResponse<DetectionZone> getZone(@PathVariable Long zoneId) {
        try {
            DetectionZone zone = zoneService.getZone(zoneId);
            return ApiResponse.success(zone);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 切换区域状态
     */
    @PutMapping("/{zoneId}/toggle")
    public ApiResponse<DetectionZone> toggleZoneStatus(@PathVariable Long zoneId) {
        try {
            DetectionZone zone = zoneService.toggleZoneStatus(zoneId);
            return ApiResponse.success("状态已切换", zone);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
}

