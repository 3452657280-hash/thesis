package com.legal.consult.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AdminConsultVO {

    private Long id;
    private Long sessionId;
    private String username;
    private String nickname;
    private String question;
    private String answer;
    private Integer responseMs;
    private Integer score;
    private LocalDateTime createTime;

    public String getAnswerSummary() {
        if (answer == null) {
            return null;
        }
        return answer.length() > 100 ? answer.substring(0, 100) : answer;
    }
}
