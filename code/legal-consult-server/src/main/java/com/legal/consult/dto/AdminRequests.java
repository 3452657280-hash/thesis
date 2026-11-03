package com.legal.consult.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.time.LocalDate;

public final class AdminRequests {

    private AdminRequests() {
    }

    @Data
    public static class UserStatus {
        @NotNull(message = "状态不能为空")
        @Min(value = 0, message = "状态只能为0或1")
        @Max(value = 1, message = "状态只能为0或1")
        private Integer status;
    }

    @Data
    public static class Audit {
        @NotNull(message = "审核结果不能为空")
        @Min(value = 1, message = "审核结果只能为1或2")
        @Max(value = 2, message = "审核结果只能为1或2")
        private Integer auditStatus;
        @Size(max = 255, message = "审核意见不能超过255个字符")
        private String auditRemark;
    }

    @Data
    public static class Law {
        @NotBlank(message = "法律名称不能为空")
        @Size(max = 100, message = "法律名称不能超过100个字符")
        private String lawName;
        @Size(max = 100, message = "编/章不能超过100个字符")
        private String chapter;
        @NotBlank(message = "条号不能为空")
        @Size(max = 20, message = "条号不能超过20个字符")
        private String articleNo;
        @NotBlank(message = "条文内容不能为空")
        private String content;
        @JsonFormat(pattern = "yyyy-MM-dd")
        private LocalDate effectiveDate;
    }

    @Data
    public static class Template {
        @NotBlank(message = "模板名称不能为空")
        @Size(max = 100, message = "模板名称不能超过100个字符")
        private String name;
        @Size(max = 50, message = "分类不能超过50个字符")
        private String category;
        @Size(max = 500, message = "说明不能超过500个字符")
        private String description;
        @NotBlank(message = "文件地址不能为空")
        @Size(max = 255, message = "文件地址不能超过255个字符")
        private String fileUrl;
    }

    @Data
    public static class NoticeReq {
        @NotBlank(message = "标题不能为空")
        @Size(max = 200, message = "标题不能超过200个字符")
        private String title;
        @NotBlank(message = "内容不能为空")
        private String content;
    }
}
