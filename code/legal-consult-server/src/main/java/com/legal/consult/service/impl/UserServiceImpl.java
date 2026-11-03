package com.legal.consult.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.legal.consult.common.BizException;
import com.legal.consult.dto.AuthRequests;
import com.legal.consult.dto.LoginResponse;
import com.legal.consult.entity.SysUser;
import com.legal.consult.mapper.SysUserMapper;
import com.legal.consult.security.JwtUtil;
import com.legal.consult.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final SysUserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Override
    public void register(AuthRequests.Register req) {
        Long count = userMapper.selectCount(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, req.getUsername()));
        if (count > 0) {
            throw new BizException("用户名已存在");
        }
        SysUser u = new SysUser();
        u.setUsername(req.getUsername());
        u.setPassword(passwordEncoder.encode(req.getPassword()));
        u.setNickname(StringUtils.hasText(req.getNickname()) ? req.getNickname() : req.getUsername());
        u.setPhone(StringUtils.hasText(req.getPhone()) ? req.getPhone() : null);
        u.setRole(StringUtils.hasText(req.getRole()) ? req.getRole() : "USER");
        u.setStatus(1);
        userMapper.insert(u);
    }

    @Override
    public LoginResponse login(AuthRequests.Login req) {
        SysUser u = userMapper.selectOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, req.getUsername()));
        if (u == null || !passwordEncoder.matches(req.getPassword(), u.getPassword())) {
            throw new BizException("用户名或密码错误");
        }
        if (u.getStatus() == null || u.getStatus() != 1) {
            throw new BizException("账号已被禁用");
        }
        String token = jwtUtil.generate(u.getId(), u.getRole());
        return new LoginResponse(token,
                new LoginResponse.UserBrief(u.getId(), u.getUsername(), u.getNickname(), u.getRole()));
    }

    @Override
    public SysUser getById(Long id) {
        SysUser u = userMapper.selectById(id);
        if (u == null) {
            throw new BizException("用户不存在");
        }
        return u;
    }

    @Override
    public void updateMe(Long uid, AuthRequests.UpdateMe req) {
        getById(uid);
        userMapper.update(null, new LambdaUpdateWrapper<SysUser>()
                .eq(SysUser::getId, uid)
                .set(SysUser::getNickname, req.getNickname())
                .set(SysUser::getPhone, StringUtils.hasText(req.getPhone()) ? req.getPhone() : null)
                .set(SysUser::getEmail, StringUtils.hasText(req.getEmail()) ? req.getEmail() : null)
                .set(SysUser::getUpdateTime, LocalDateTime.now()));
    }

    @Override
    public void changePassword(Long uid, AuthRequests.ChangePassword req) {
        SysUser u = getById(uid);
        if (!passwordEncoder.matches(req.getOldPassword(), u.getPassword())) {
            throw new BizException("原密码错误");
        }
        u.setPassword(passwordEncoder.encode(req.getNewPassword()));
        userMapper.updateById(u);
    }
}
