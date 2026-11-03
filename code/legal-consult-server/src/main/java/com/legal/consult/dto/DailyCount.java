package com.legal.consult.dto;

import lombok.Data;

import java.time.LocalDate;

@Data
public class DailyCount {

    private LocalDate statDate;
    private Long cnt;
}
