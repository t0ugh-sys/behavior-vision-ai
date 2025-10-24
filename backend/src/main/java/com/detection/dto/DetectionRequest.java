package com.detection.dto;

import lombok.Data;

/**
 * 检测请求DTO
 */
@Data
public class DetectionRequest {
    
    private Long userId;
    private String sourceType; // VIDEO, IMAGE, REALTIME
    private String filePath; // 文件路径或URL
    private byte[] fileData; // 文件数据
}

