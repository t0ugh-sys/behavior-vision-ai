package com.detection.controller;

import com.detection.entity.DetectionRecord;
import com.detection.entity.BehaviorData;
import com.detection.dto.ApiResponse;
import com.detection.service.DetectionService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 检测控制器
 */
@RestController
@RequestMapping("/detections")
@RequiredArgsConstructor
public class DetectionController {
    
    private final DetectionService detectionService;
    
    @Value("${file.upload.path}")
    private String uploadDir;
    
    /**
     * 上传文件并进行检测
     */
    @PostMapping("/upload")
    public ApiResponse<DetectionRecord> uploadAndDetect(
            @RequestParam("file") MultipartFile file,
            @RequestParam("userId") Long userId,
            @RequestParam("sourceType") String sourceType) {
        
        try {
            // 保存文件
            String fileName = UUID.randomUUID().toString() + "_" + file.getOriginalFilename();
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }
            
            String filePath = uploadPath.resolve(fileName).toString();
            file.transferTo(new File(filePath));
            
            // 创建检测记录
            DetectionRecord record = detectionService.createDetectionRecord(userId, sourceType, filePath);
            
            // 异步调用Python服务进行检测
            new Thread(() -> {
                try {
                    System.out.println("开始调用Python服务检测，记录ID: " + record.getId() + ", 用户ID: " + userId);
                    Map<String, Object> result = detectionService.detectBehavior(filePath, sourceType, userId, record.getId());
                    System.out.println("Python服务返回结果: " + result);
                    detectionService.updateDetectionRecord(record.getId(), result);
                    System.out.println("检测记录更新成功，记录ID: " + record.getId());
                } catch (Exception e) {
                    System.err.println("检测失败，记录ID: " + record.getId() + ", 错误: " + e.getMessage());
                    e.printStackTrace();
                    detectionService.markDetectionFailed(record.getId(), e.getMessage());
                }
            }).start();
            
            return ApiResponse.success("文件上传成功，正在检测中...", record);
            
        } catch (IOException e) {
            return ApiResponse.error("文件上传失败: " + e.getMessage());
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取用户的检测记录列表
     */
    @GetMapping("/user/{userId}")
    public ApiResponse<Page<DetectionRecord>> getUserDetectionRecords(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        try {
            PageRequest pageRequest = PageRequest.of(page, size, Sort.by("createdAt").descending());
            Page<DetectionRecord> records = detectionService.getUserDetectionRecords(userId, pageRequest);
            return ApiResponse.success(records);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取检测记录详情
     */
    @GetMapping("/{recordId}")
    public ApiResponse<DetectionRecord> getDetectionRecord(@PathVariable Long recordId) {
        try {
            DetectionRecord record = detectionService.getDetectionRecord(recordId);
            return ApiResponse.success(record);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取检测记录的行为数据
     */
    @GetMapping("/{recordId}/behaviors")
    public ApiResponse<List<BehaviorData>> getRecordBehaviorData(@PathVariable Long recordId) {
        try {
            List<BehaviorData> behaviorData = detectionService.getRecordBehaviorData(recordId);
            return ApiResponse.success(behaviorData);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取用户统计数据
     */
    @GetMapping("/statistics/{userId}")
    public ApiResponse<Map<String, Object>> getUserStatistics(@PathVariable Long userId) {
        try {
            Map<String, Object> statistics = detectionService.getUserStatistics(userId);
            return ApiResponse.success(statistics);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 获取全局统计数据
     */
    @GetMapping("/statistics/global")
    public ApiResponse<Map<String, Object>> getGlobalStatistics() {
        try {
            Map<String, Object> statistics = detectionService.getGlobalStatistics();
            return ApiResponse.success(statistics);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 删除检测记录
     */
    @DeleteMapping("/{recordId}")
    public ApiResponse<Void> deleteRecord(@PathVariable Long recordId) {
        try {
            detectionService.deleteDetectionRecord(recordId);
            return ApiResponse.success("删除成功", null);
        } catch (Exception e) {
            return ApiResponse.error(e.getMessage());
        }
    }
    
    /**
     * 批量删除检测记录
     */
    @DeleteMapping("/batch")
    public ApiResponse<Void> batchDeleteRecords(@RequestBody List<Long> recordIds) {
        try {
            detectionService.batchDeleteRecords(recordIds);
            return ApiResponse.success("批量删除成功", null);
        } catch (Exception e) {
            return ApiResponse.error("批量删除失败: " + e.getMessage());
        }
    }
    
    /**
     * 直接创建检测记录（用于实时检测）
     */
    @PostMapping("/create")
    public ApiResponse<DetectionRecord> createRecord(@RequestBody Map<String, Object> recordData) {
        try {
            DetectionRecord record = new DetectionRecord();
            record.setUserId(Long.valueOf(recordData.get("userId").toString()));
            record.setSourceType(recordData.get("sourceType").toString());
            record.setHasAbnormal((Boolean) recordData.get("hasAbnormal"));
            record.setBehaviorType((String) recordData.get("behaviorType"));
            
            if (recordData.get("confidence") != null) {
                record.setConfidence(Float.valueOf(recordData.get("confidence").toString()));
            }
            
            if (recordData.get("detectionResult") != null) {
                record.setDetectionResult(recordData.get("detectionResult").toString());
            }
            
            if (recordData.get("imagePath") != null) {
                record.setImagePath(recordData.get("imagePath").toString());
            }
            
            if (recordData.get("videoPath") != null) {
                record.setVideoPath(recordData.get("videoPath").toString());
            }
            
            record.setStatus(recordData.getOrDefault("status", "COMPLETED").toString());
            
            DetectionRecord savedRecord = detectionService.saveDetectionRecord(record);
            return ApiResponse.success("记录创建成功", savedRecord);
        } catch (Exception e) {
            return ApiResponse.error("创建记录失败: " + e.getMessage());
        }
    }
}

