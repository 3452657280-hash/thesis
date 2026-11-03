package com.legal.consult.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.legal.consult.dto.ScoreCount;
import com.legal.consult.entity.Feedback;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface FeedbackMapper extends BaseMapper<Feedback> {

    @Select("SELECT AVG(score * 1.0) FROM feedback")
    Double selectAvgScore();

    @Select("SELECT score, COUNT(*) AS cnt FROM feedback GROUP BY score")
    List<ScoreCount> selectScoreCounts();
}
