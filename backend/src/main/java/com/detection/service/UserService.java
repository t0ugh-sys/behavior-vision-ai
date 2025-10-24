package com.detection.service;

import com.detection.entity.User;
import com.detection.dto.UserDTO;
import com.detection.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Optional;

/**
 * 用户服务
 */
@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    
    /**
     * 用户注册
     */
    @Transactional
    public User register(UserDTO userDTO) {
        // 检查用户名是否已存在
        if (userRepository.existsByUsername(userDTO.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }
        
        // 检查邮箱是否已存在
        if (userDTO.getEmail() != null && userRepository.existsByEmail(userDTO.getEmail())) {
            throw new RuntimeException("邮箱已被注册");
        }
        
        User user = new User();
        user.setUsername(userDTO.getUsername());
        user.setPassword(userDTO.getPassword()); // 实际项目中应加密
        user.setEmail(userDTO.getEmail());
        user.setPhone(userDTO.getPhone());
        user.setRealName(userDTO.getRealName());
        
        return userRepository.save(user);
    }
    
    /**
     * 用户登录
     */
    public User login(String username, String password) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户名或密码错误"));
        
        if (!user.getPassword().equals(password)) { // 实际项目中应验证加密密码
            throw new RuntimeException("用户名或密码错误");
        }
        
        if (!user.getActive()) {
            throw new RuntimeException("账号已被禁用");
        }
        
        return user;
    }
    
    /**
     * 获取用户信息
     */
    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
    }
    
    /**
     * 获取所有用户
     */
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    /**
     * 更新用户信息
     */
    @Transactional
    public User updateUser(Long id, UserDTO userDTO) {
        User user = getUserById(id);
        
        if (userDTO.getEmail() != null) {
            user.setEmail(userDTO.getEmail());
        }
        if (userDTO.getPhone() != null) {
            user.setPhone(userDTO.getPhone());
        }
        if (userDTO.getRealName() != null) {
            user.setRealName(userDTO.getRealName());
        }
        
        return userRepository.save(user);
    }
    
    /**
     * 删除用户
     */
    @Transactional
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}

