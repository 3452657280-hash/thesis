package com.legal.consult.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.time.LocalDateTime;

public final class LawyerRequests {

    private LawyerRequests() {
    }

    @Data
    public static class Profile {
        @NotBlank(message = "真实姓名不能为空")
        @Size(max = 50, message = "真实姓名不能超过50个字符")
        private String realName;
        @NotBlank(message = "执业证号不能为空")
        @Size(max = 50, message = "执业证号不能超过50个字符")
        private String licenseNo;
        @Size(max = 100, message = "律所名称不能超过100个字符")
        private String lawFirm;
        @Size(max = 200, message = "擅长领域不能超过200个字符")
        private String specialty;
        @Min(value = 0, message = "执业年限不能为负数")
        @Max(value = 70, message = "执业年限不合理")
        private Integer years;
        @Size(max = 1000, message = "个人简介不能超过1000个字符")
        private String intro;
    }

    @Data
    public static class CreateAppointment {
        @NotNull(message = "请选择律师")
        private Long lawyerId;
        @NotBlank(message = "问题描述不能为空")
        @Size(max = 2000, message = "问题描述不能超过2000个字符")
        private String question;
        @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
        private LocalDateTime appointTime;
    }

    @Data
    public static class HandleAppointment {
        @NotNull(message = "处理状态不能为空")
        @Min(value = 1, message = "处理状态不正确")
        @Max(value = 3, message = "处理状态不正确")
        private Integer status;
        @Size(max = 2000, message = "回复内容不能超过2000个字符")
        private String reply;
    }
}
