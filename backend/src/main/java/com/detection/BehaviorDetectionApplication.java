package com.detection;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 人体异常行为检测系统 - 主启动类
 */
@SpringBootApplication
public class BehaviorDetectionApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(BehaviorDetectionApplication.class, args);
    }
}

