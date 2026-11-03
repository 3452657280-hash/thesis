package com.legal.consult.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.legal.consult.entity.LawArticle;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface LawArticleMapper extends BaseMapper<LawArticle> {

    @Select("SELECT DISTINCT law_name FROM law_article ORDER BY law_name")
    List<String> selectLawNames();
}
