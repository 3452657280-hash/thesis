package com.legal.consult.security;

import com.legal.consult.entity.SysUser;
import com.legal.consult.mapper.SysUserMapper;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;
    private final SysUserMapper userMapper;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            String token = header.substring(7).trim();
            Long uid = null;
            try {
                Claims claims = jwtUtil.parse(token);
                Object raw = claims.get("uid");
                if (raw instanceof Number n) {
                    uid = n.longValue();
                }
            } catch (JwtException | IllegalArgumentException ignored) {
            }
            if (uid != null) {
                SysUser user = userMapper.selectById(uid);
                if (user != null) {
                    if (user.getStatus() == null || user.getStatus() != 1) {
                        JsonResponseWriter.write(response, 401, "账号已被禁用");
                        return;
                    }
                    LoginUser principal = new LoginUser(user.getId(), user.getUsername(), user.getRole());
                    UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                            principal, null, List.of(new SimpleGrantedAuthority("ROLE_" + user.getRole())));
                    SecurityContextHolder.getContext().setAuthentication(auth);
                }
            }
        }
        chain.doFilter(request, response);
    }
}
