package com.legal.consult.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class FavoriteVO {

    private Long messageId;
    private String content;
    private Long sessionId;
    private LocalDateTime createTime;
}
