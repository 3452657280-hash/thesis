package com.legal.consult.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

public final class AuthRequests {

    private AuthRequests() {
    }

    @Data
    public static class Register {
        @NotBlank(message = "用户名不能为空")
        @Pattern(regexp = "^[A-Za-z0-9_]{3,20}$", message = "用户名须为3-20位字母、数字或下划线")
        private String username;
        @NotBlank(message = "密码不能为空")
        @Size(min = 6, max = 32, message = "密码长度须为6-32位")
        private String password;
        @Size(max = 50, message = "昵称不能超过50个字符")
        private String nickname;
        @Pattern(regexp = "^$|^1\\d{10}$", message = "手机号格式不正确")
        private String phone;
        @Pattern(regexp = "^(USER|LAWYER)?$", message = "注册角色只能是USER或LAWYER")
        private String role;
    }

    @Data
    public static class Login {
        @NotBlank(message = "用户名不能为空")
        private String username;
        @NotBlank(message = "密码不能为空")
        private String password;
    }

    @Data
    public static class UpdateMe {
        @Size(max = 50, message = "昵称不能超过50个字符")
        private String nickname;
        @Pattern(regexp = "^$|^1\\d{10}$", message = "手机号格式不正确")
        private String phone;
        @Email(message = "邮箱格式不正确")
        @Size(max = 100, message = "邮箱不能超过100个字符")
        private String email;
    }

    @Data
    public static class ChangePassword {
        @NotBlank(message = "原密码不能为空")
        private String oldPassword;
        @NotBlank(message = "新密码不能为空")
        @Size(min = 6, max = 32, message = "新密码长度须为6-32位")
        private String newPassword;
    }
}
