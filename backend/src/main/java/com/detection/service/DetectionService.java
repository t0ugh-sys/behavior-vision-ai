package com.detection.service;

import com.detection.entity.DetectionRecord;
import com.detection.entity.BehaviorData;
import com.detection.repository.DetectionRecordRepository;
import com.detection.repository.BehaviorDataRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;

import java.util.List;
import java.util.Map;

/**
 * 检测服务
 */
@Service
@RequiredArgsConstructor
public class DetectionService {
    
    private final DetectionRecordRepository detectionRecordRepository;
    private final BehaviorDataRepository behaviorDataRepository;
    private final WebClient.Builder webClientBuilder;
    private final ObjectMapper objectMapper;
    
    @Value("${python.service.url}")
    private String pythonServiceUrl;
    
    /**
     * 创建检测记录
     */
    @Transactional
    public DetectionRecord createDetectionRecord(Long userId, String sourceType, String filePath) {
        DetectionRecord record = new DetectionRecord();
        record.setUserId(userId);
        record.setSourceType(sourceType);
        
        if ("VIDEO".equals(sourceType)) {
            record.setVideoPath(filePath);
        } else if ("IMAGE".equals(sourceType)) {
            record.setImagePath(filePath);
        }
        
        record.setStatus("PROCESSING");
        return detectionRecordRepository.save(record);
    }
    
    /**
     * 调用Python服务进行检测
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> detectBehavior(String filePath, String sourceType, Long userId, Long recordId) {
        try {
            WebClient webClient = webClientBuilder.baseUrl(pythonServiceUrl).build();
            
            MultipartBodyBuilder builder = new MultipartBodyBuilder();
            builder.part("file", new FileSystemResource(filePath));
            builder.part("source_type", sourceType);
            
            // 添加可选参数
            if (userId != null) {
                builder.part("user_id", userId.toString());
            }
            if (recordId != null) {
                builder.part("record_id", recordId.toString());
            }
            builder.part("enable_alert", "true");
            
            System.out.println("调用Python服务: filePath=" + filePath + ", sourceType=" + sourceType + ", userId=" + userId + ", recordId=" + recordId);
            
            Map<String, Object> response = webClient.post()
                    .uri("/detect")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .bodyValue(builder.build())
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            
            System.out.println("Python服务响应: " + response);
            
            return response;
        } catch (Exception e) {
            System.err.println("调用Python检测服务异常: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("调用检测服务失败: " + e.getMessage(), e);
        }
    }
    
    /**
     * 更新检测记录
     */
    @Transactional
    public DetectionRecord updateDetectionRecord(Long recordId, Map<String, Object> detectionResult) {
        DetectionRecord record = detectionRecordRepository.findById(recordId)
                .orElseThrow(() -> new RuntimeException("检测记录不存在"));
        
        record.setStatus("COMPLETED");
        
        // 使用ObjectMapper将Map转换为正确的JSON字符串
        try {
            record.setDetectionResult(objectMapper.writeValueAsString(detectionResult));
        } catch (Exception e) {
            throw new RuntimeException("序列化检测结果失败: " + e.getMessage());
        }
        
        Boolean hasAbnormal = (Boolean) detectionResult.get("has_abnormal");
        record.setHasAbnormal(hasAbnormal != null && hasAbnormal);
        
        if (detectionResult.containsKey("behavior_type")) {
            record.setBehaviorType((String) detectionResult.get("behavior_type"));
        }
        
        if (detectionResult.containsKey("confidence")) {
            Object confidence = detectionResult.get("confidence");
            if (confidence instanceof Number) {
                record.setConfidence(((Number) confidence).floatValue());
            }
        }
        
        // 保存可视化图片URL
        if (detectionResult.containsKey("visualization_url")) {
            record.setVisualizationUrl((String) detectionResult.get("visualization_url"));
        }
        
        return detectionRecordRepository.save(record);
    }
    
    /**
     * 标记检测失败
     */
    @Transactional
    public DetectionRecord markDetectionFailed(Long recordId, String errorMessage) {
        DetectionRecord record = detectionRecordRepository.findById(recordId)
                .orElseThrow(() -> new RuntimeException("检测记录不存在"));
        
        record.setStatus("FAILED");
        record.setErrorMessage(errorMessage);
        
        return detectionRecordRepository.save(record);
    }
    
    /**
     * 获取用户的检测记录
     */
    public Page<DetectionRecord> getUserDetectionRecords(Long userId, Pageable pageable) {
        return detectionRecordRepository.findByUserId(userId, pageable);
    }
    
    /**
     * 获取检测记录详情
     */
    public DetectionRecord getDetectionRecord(Long recordId) {
        return detectionRecordRepository.findById(recordId)
                .orElseThrow(() -> new RuntimeException("检测记录不存在"));
    }
    
    /**
     * 保存行为数据
     */
    @Transactional
    public BehaviorData saveBehaviorData(BehaviorData behaviorData) {
        return behaviorDataRepository.save(behaviorData);
    }
    
    /**
     * 获取记录的行为数据
     */
    public List<BehaviorData> getRecordBehaviorData(Long recordId) {
        return behaviorDataRepository.findByRecordId(recordId);
    }
    
    /**
     * 获取用户统计数据
     */
    public Map<String, Object> getUserStatistics(Long userId) {
        Long totalRecords = detectionRecordRepository.countByUserId(userId);
        Long abnormalRecords = detectionRecordRepository.countByUserIdAndHasAbnormal(userId, true);
        
        // 获取按行为类型分组的统计
        List<DetectionRecord> allRecords = detectionRecordRepository.findByUserId(userId);
        Map<String, Long> behaviorTypeStats = new java.util.HashMap<>();
        behaviorTypeStats.put("FALL", 0L);
        behaviorTypeStats.put("ABNORMAL_POSE", 0L);
        behaviorTypeStats.put("FIGHT", 0L);
        
        for (DetectionRecord record : allRecords) {
            if (record.getBehaviorType() != null) {
                behaviorTypeStats.merge(record.getBehaviorType(), 1L, Long::sum);
            }
        }
        
        // 获取最近7天的检测趋势（默认）
        List<Map<String, Object>> trend7Days = getTrendData(userId, 7);
        List<Map<String, Object>> trend30Days = getTrendData(userId, 30);
        
        Map<String, Object> stats = new java.util.HashMap<>();
        stats.put("total_records", totalRecords);
        stats.put("abnormal_records", abnormalRecords);
        stats.put("normal_records", totalRecords - abnormalRecords);
        stats.put("behavior_type_stats", behaviorTypeStats);
        stats.put("trend_7_days", trend7Days);
        stats.put("trend_30_days", trend30Days);
        
        return stats;
    }
    
    /**
     * 获取检测趋势数据
     */
    public List<Map<String, Object>> getTrendData(Long userId, int days) {
        List<DetectionRecord> allRecords = detectionRecordRepository.findByUserId(userId);
        List<Map<String, Object>> trendData = new java.util.ArrayList<>();
        java.time.LocalDate today = java.time.LocalDate.now();
        
        for (int i = days - 1; i >= 0; i--) {
            java.time.LocalDate date = today.minusDays(i);
            java.time.LocalDateTime startOfDay = date.atStartOfDay();
            java.time.LocalDateTime endOfDay = date.plusDays(1).atStartOfDay();
            
            // 计算当天的总检测次数
            long dayCount = allRecords.stream()
                .filter(r -> r.getCreatedAt() != null && 
                            !r.getCreatedAt().isBefore(startOfDay) && 
                            r.getCreatedAt().isBefore(endOfDay))
                .count();
            
            // 计算当天的异常检测次数
            long abnormalCount = allRecords.stream()
                .filter(r -> r.getCreatedAt() != null && 
                            !r.getCreatedAt().isBefore(startOfDay) && 
                            r.getCreatedAt().isBefore(endOfDay) &&
                            r.getHasAbnormal() != null &&
                            r.getHasAbnormal())
                .count();
            
            Map<String, Object> dayData = new java.util.HashMap<>();
            dayData.put("date", String.format("%02d/%02d", date.getMonthValue(), date.getDayOfMonth()));
            dayData.put("total_count", dayCount);
            dayData.put("abnormal_count", abnormalCount);
            dayData.put("normal_count", dayCount - abnormalCount);
            trendData.add(dayData);
        }
        
        return trendData;
    }
    
    /**
     * 获取全局统计数据（管理员）
     */
    public Map<String, Object> getGlobalStatistics() {
        long totalRecords = detectionRecordRepository.count();
        long abnormalRecords = detectionRecordRepository.countByHasAbnormal(true);
        long totalUsers = detectionRecordRepository.findAll().stream()
            .map(DetectionRecord::getUserId)
            .distinct()
            .count();
        
        Map<String, Object> stats = new java.util.HashMap<>();
        stats.put("total_records", totalRecords);
        stats.put("abnormal_records", abnormalRecords);
        stats.put("normal_records", totalRecords - abnormalRecords);
        stats.put("total_users", totalUsers);
        
        return stats;
    }
    
    /**
     * 删除检测记录及相关文件
     */
    @Transactional
    public void deleteDetectionRecord(Long recordId) {
        DetectionRecord record = detectionRecordRepository.findById(recordId)
                .orElseThrow(() -> new RuntimeException("检测记录不存在"));
        
        // 删除关联的行为数据
        behaviorDataRepository.deleteByRecordId(recordId);
        
        // 删除相关文件
        deleteRelatedFiles(record);
        
        // 删除记录
        detectionRecordRepository.delete(record);
    }
    
    /**
     * 删除检测记录相关的文件
     */
    private void deleteRelatedFiles(DetectionRecord record) {
        try {
            // 1. 删除上传的原始文件（视频或图片）
            if (record.getVideoPath() != null && !record.getVideoPath().isEmpty()) {
                deleteFileIfExists(record.getVideoPath());
            }
            if (record.getImagePath() != null && !record.getImagePath().isEmpty()) {
                deleteFileIfExists(record.getImagePath());
            }
            
            // 2. 删除可视化结果文件
            if (record.getVisualizationUrl() != null && !record.getVisualizationUrl().isEmpty()) {
                // 从URL提取文件路径
                String visualizationPath = extractPathFromUrl(record.getVisualizationUrl());
                if (visualizationPath != null) {
                    deleteFileIfExists(visualizationPath);
                }
            }
            
            // 3. 尝试删除可能的快照文件（根据命名规则）
            String snapshotPattern = "snapshots/*_" + record.getId() + "_*";
            // 这里可以根据实际需求扩展快照删除逻辑
            
        } catch (Exception e) {
            // 文件删除失败不应该影响记录删除，只记录日志
            System.err.println("删除记录关联文件失败: " + e.getMessage());
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
            java.io.File file = new java.io.File(filePath);
            if (file.exists()) {
                if (file.delete()) {
                    System.out.println("✓ 已删除文件: " + filePath);
                } else {
                    System.err.println("✗ 删除文件失败: " + filePath);
                }
            }
        } catch (Exception e) {
            System.err.println("✗ 删除文件异常: " + filePath + " - " + e.getMessage());
        }
    }
    
    /**
     * 从URL提取本地文件路径
     */
    private String extractPathFromUrl(String url) {
        if (url == null || url.isEmpty()) {
            return null;
        }
        
        try {
            // 如果是完整URL（如 http://localhost:5000/visualizations/xxx.jpg）
            if (url.startsWith("http://") || url.startsWith("https://")) {
                // 提取路径部分
                java.net.URL urlObj = new java.net.URL(url);
                String path = urlObj.getPath();
                
                // 移除前导斜杠并构建实际文件路径
                if (path.startsWith("/")) {
                    path = path.substring(1);
                }
                
                // 假设Python服务在项目根目录的python-service文件夹
                // visualizations/xxx.jpg -> python-service/visualizations/xxx.jpg
                return "python-service/" + path;
            } else {
                // 如果是相对路径，直接使用
                return url;
            }
        } catch (Exception e) {
            System.err.println("解析URL失败: " + url + " - " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 批量删除检测记录
     */
    @Transactional
    public void batchDeleteRecords(List<Long> recordIds) {
        for (Long recordId : recordIds) {
            deleteDetectionRecord(recordId);
        }
    }
    
    /**
     * 保存检测记录（用于实时检测）
     */
    @Transactional
    public DetectionRecord saveDetectionRecord(DetectionRecord record) {
        return detectionRecordRepository.save(record);
    }
}

