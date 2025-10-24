package com.detection.controller;

import com.detection.dto.ApiResponse;
import com.detection.entity.User;
import com.detection.service.UserService;
import com.detection.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 认证控制器
 * 处理登录、注册等认证相关操作
 */
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {
    
    private final UserService userService;
    private final JwtUtil jwtUtil;
    
    /**
     * 用户登录
     * 返回JWT token
     */
    @PostMapping("/login")
    public ApiResponse<Map<String, Object>> login(@RequestBody Map<String, String> loginData) {
        try {
            String username = loginData.get("username");
            String password = loginData.get("password");
            
            // 验证用户
            User user = userService.login(username, password);
            
            // 生成JWT token
            String token = jwtUtil.generateToken(user.getUsername(), user.getRole(), user.getId());
            
            // 构造返回数据
            Map<String, Object> responseData = new HashMap<>();
            responseData.put("token", token);
            responseData.put("user", Map.of(
                "id", user.getId(),
                "username", user.getUsername(),
                "email", user.getEmail(),
                "role", user.getRole()
            ));
            
            return ApiResponse.success("登录成功", responseData);
        } catch (Exception e) {
            return ApiResponse.error("登录失败: " + e.getMessage());
        }
    }
    
    /**
     * 用户注册
     */
    @PostMapping("/register")
    public ApiResponse<User> register(@RequestBody Map<String, String> registerData) {
        try {
            String username = registerData.get("username");
            String password = registerData.get("password");
            String email = registerData.get("email");
            
            // 创建用户DTO
            com.detection.dto.UserDTO userDTO = new com.detection.dto.UserDTO();
            userDTO.setUsername(username);
            userDTO.setPassword(password);
            userDTO.setEmail(email);
            userDTO.setRole("USER");
            
            User user = userService.register(userDTO);
            user.setPassword(null); // 清除密码
            
            return ApiResponse.success("注册成功", user);
        } catch (Exception e) {
            return ApiResponse.error("注册失败: " + e.getMessage());
        }
    }
    
    /**
     * 验证token是否有效
     */
    @GetMapping("/validate")
    public ApiResponse<Map<String, Object>> validateToken(@RequestHeader("Authorization") String authHeader) {
        try {
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return ApiResponse.error("无效的token格式");
            }
            
            String token = authHeader.substring(7);
            String username = jwtUtil.extractUsername(token);
            
            if (jwtUtil.validateToken(token, username)) {
                Map<String, Object> data = new HashMap<>();
                data.put("valid", true);
                data.put("username", username);
                data.put("role", jwtUtil.extractRole(token));
                return ApiResponse.success("Token有效", data);
            } else {
                return ApiResponse.error("Token已过期或无效");
            }
        } catch (Exception e) {
            return ApiResponse.error("Token验证失败: " + e.getMessage());
        }
    }
}

