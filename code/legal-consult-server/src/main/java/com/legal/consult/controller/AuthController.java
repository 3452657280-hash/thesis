package com.legal.consult.controller;

import com.legal.consult.common.Result;
import com.legal.consult.dto.AuthRequests;
import com.legal.consult.dto.LoginResponse;
import com.legal.consult.entity.SysUser;
import com.legal.consult.security.SecurityUtil;
import com.legal.consult.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class AuthController {

    private final UserService userService;

    @PostMapping("/auth/register")
    public Result<Void> register(@Valid @RequestBody AuthRequests.Register req) {
        userService.register(req);
        return Result.ok();
    }

    @PostMapping("/auth/login")
    public Result<LoginResponse> login(@Valid @RequestBody AuthRequests.Login req) {
        return Result.ok(userService.login(req));
    }

    @GetMapping("/user/me")
    public Result<SysUser> me() {
        return Result.ok(userService.getById(SecurityUtil.uid()));
    }

    @PutMapping("/user/me")
    public Result<Void> updateMe(@Valid @RequestBody AuthRequests.UpdateMe req) {
        userService.updateMe(SecurityUtil.uid(), req);
        return Result.ok();
    }

    @PutMapping("/user/password")
    public Result<Void> changePassword(@Valid @RequestBody AuthRequests.ChangePassword req) {
        userService.changePassword(SecurityUtil.uid(), req);
        return Result.ok();
    }
}
