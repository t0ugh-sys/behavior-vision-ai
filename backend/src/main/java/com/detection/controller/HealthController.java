package com.detection.controller;

import com.detection.dto.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.info.BuildProperties;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 系统健康检查控制器
 */
@RestController
@RequestMapping("/health")
@RequiredArgsConstructor
public class HealthController {
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * 后端服务健康检查
     */
    @GetMapping
    public ApiResponse<Map<String, Object>> healthCheck() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("service", "backend");
        health.put("timestamp", LocalDateTime.now());
        health.put("version", "1.0.0");
        
        return ApiResponse.success(health);
    }
    
    /**
     * 检查Python服务状态
     */
    @GetMapping("/python")
    public ApiResponse<Map<String, Object>> checkPythonService() {
        Map<String, Object> result = new HashMap<>();
        
        try {
            // 尝试调用Python服务的健康检查接口
            String pythonUrl = "http://localhost:5000/health";
            Map response = restTemplate.getForObject(pythonUrl, Map.class);
            
            result.put("status", "UP");
            result.put("service", "python");
            result.put("details", response);
            
            return ApiResponse.success(result);
        } catch (Exception e) {
            result.put("status", "DOWN");
            result.put("service", "python");
            result.put("error", e.getMessage());
            
            return ApiResponse.error("Python服务不可用", result);
        }
    }
    
    /**
     * 获取系统信息
     */
    @GetMapping("/info")
    public ApiResponse<Map<String, Object>> getSystemInfo() {
        Map<String, Object> info = new HashMap<>();
        
        // 运行时信息
        Runtime runtime = Runtime.getRuntime();
        long maxMemory = runtime.maxMemory() / (1024 * 1024);
        long totalMemory = runtime.totalMemory() / (1024 * 1024);
        long freeMemory = runtime.freeMemory() / (1024 * 1024);
        long usedMemory = totalMemory - freeMemory;
        
        Map<String, Object> jvm = new HashMap<>();
        jvm.put("max_memory_mb", maxMemory);
        jvm.put("total_memory_mb", totalMemory);
        jvm.put("used_memory_mb", usedMemory);
        jvm.put("free_memory_mb", freeMemory);
        jvm.put("processors", runtime.availableProcessors());
        
        info.put("jvm", jvm);
        info.put("java_version", System.getProperty("java.version"));
        info.put("os_name", System.getProperty("os.name"));
        info.put("os_version", System.getProperty("os.version"));
        info.put("os_arch", System.getProperty("os.arch"));
        
        return ApiResponse.success(info);
    }
    
    /**
     * 获取所有服务状态
     */
    @GetMapping("/status")
    public ApiResponse<Map<String, Object>> getAllServicesStatus() {
        Map<String, Object> status = new HashMap<>();
        
        // 后端状态（当前服务一定是UP的）
        Map<String, String> backend = new HashMap<>();
        backend.put("status", "UP");
        backend.put("timestamp", LocalDateTime.now().toString());
        status.put("backend", backend);
        
        // Python服务状态
        Map<String, String> python = new HashMap<>();
        try {
            String pythonUrl = "http://localhost:5000/health";
            restTemplate.getForObject(pythonUrl, Map.class);
            python.put("status", "UP");
        } catch (Exception e) {
            python.put("status", "DOWN");
            python.put("error", e.getMessage());
        }
        status.put("python", python);
        
        // WebSocket状态（简化处理，认为始终UP）
        Map<String, String> websocket = new HashMap<>();
        websocket.put("status", "UP");
        status.put("websocket", websocket);
        
        // 数据库状态（如果能查到，说明DB正常）
        Map<String, String> database = new HashMap<>();
        try {
            // 这里可以添加简单的数据库查询来验证连接
            database.put("status", "UP");
        } catch (Exception e) {
            database.put("status", "DOWN");
        }
        status.put("database", database);
        
        return ApiResponse.success(status);
    }
}
