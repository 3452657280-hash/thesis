package com.legal.consult.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class LoginResponse {

    private String token;
    private UserBrief user;

    @Data
    @AllArgsConstructor
    public static class UserBrief {
        private Long id;
        private String username;
        private String nickname;
        private String role;
    }
}
