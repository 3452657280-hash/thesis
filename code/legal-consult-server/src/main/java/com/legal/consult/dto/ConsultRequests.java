package com.legal.consult.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

public final class ConsultRequests {

    private ConsultRequests() {
    }

    @Data
    public static class Title {
        @NotBlank(message = "标题不能为空")
        @Size(max = 100, message = "标题不能超过100个字符")
        private String title;
    }

    @Data
    public static class Chat {
        @NotBlank(message = "提问内容不能为空")
        @Size(max = 2000, message = "提问内容不能超过2000个字符")
        private String content;
    }

    @Data
    public static class FeedbackReq {
        @NotNull(message = "请选择评分")
        @Min(value = 1, message = "评分须为1-5分")
        @Max(value = 5, message = "评分须为1-5分")
        private Integer score;
        @Size(max = 500, message = "评价内容不能超过500个字符")
        private String comment;
    }
}
