package com.detection.config;

import com.detection.util.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

/**
 * JWT认证过滤器
 * 在每个请求前验证JWT token
 */
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                    HttpServletResponse response, 
                                    FilterChain filterChain) throws ServletException, IOException {
        
        // 获取请求路径
        String path = request.getRequestURI();
        
        // 允许的公开路径（不需要JWT验证）
        if (path.startsWith("/api/auth/") || 
            path.startsWith("/users/login") ||
            path.startsWith("/users/register") ||
            path.startsWith("/api/health") ||
            path.startsWith("/visualizations/") ||
            path.startsWith("/snapshots/")) {
            logger.debug("公开路径，跳过JWT验证: " + path);
            filterChain.doFilter(request, response);
            return;
        }

        // 从请求头获取token
        String authHeader = request.getHeader("Authorization");
        String token = null;
        String username = null;

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            token = authHeader.substring(7);
            try {
                username = jwtUtil.extractUsername(token);
            } catch (Exception e) {
                logger.warn("JWT token解析失败: " + e.getMessage());
            }
        }

        // 验证token并设置认证信息
        if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
            if (jwtUtil.validateToken(token, username)) {
                // 从token获取角色信息
                String role = jwtUtil.extractRole(token);
                
                UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                    username, 
                    null, 
                    Collections.singletonList(new SimpleGrantedAuthority(role))
                );
                
                SecurityContextHolder.getContext().setAuthentication(authToken);
                logger.debug("用户 " + username + " 认证成功");
            } else {
                logger.warn("JWT token验证失败");
            }
        }

        filterChain.doFilter(request, response);
    }
}

