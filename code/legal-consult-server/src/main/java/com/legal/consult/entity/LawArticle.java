package com.legal.consult.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("law_article")
public class LawArticle {

    @TableId(type = IdType.AUTO)
    private Long id;
    private String lawName;
    private String chapter;
    private String articleNo;
    private String content;
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate effectiveDate;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
