package com.legal.consult.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.legal.consult.dto.AdminConsultVO;
import com.legal.consult.dto.DailyCount;
import com.legal.consult.dto.FavoriteVO;
import com.legal.consult.entity.ConsultMessage;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDateTime;
import java.util.List;

public interface ConsultMessageMapper extends BaseMapper<ConsultMessage> {

    @Select("SELECT m.id, m.session_id, u.username, u.nickname, m.content AS answer, m.response_ms, m.create_time,"
            + " (SELECT q.content FROM consult_message q WHERE q.session_id = m.session_id AND q.role = 'user'"
            + " AND q.id < m.id ORDER BY q.id DESC LIMIT 1) AS question,"
            + " (SELECT MAX(f.score) FROM feedback f WHERE f.message_id = m.id) AS score"
            + " FROM consult_message m JOIN consult_session s ON m.session_id = s.id"
            + " JOIN sys_user u ON s.user_id = u.id WHERE m.role = 'assistant' ORDER BY m.id DESC")
    IPage<AdminConsultVO> selectAdminConsults(IPage<AdminConsultVO> page);

    @Select("SELECT f.message_id, m.content, m.session_id, f.create_time FROM favorite f"
            + " JOIN consult_message m ON f.message_id = m.id WHERE f.user_id = #{userId} ORDER BY f.id DESC")
    List<FavoriteVO> selectFavorites(@Param("userId") Long userId);

    @Select("SELECT CAST(create_time AS DATE) AS stat_date, COUNT(*) AS cnt FROM consult_message"
            + " WHERE role = 'user' AND create_time >= #{start} GROUP BY CAST(create_time AS DATE)")
    List<DailyCount> selectDailyQuestions(@Param("start") LocalDateTime start);

    @Select("SELECT AVG(response_ms) FROM consult_message WHERE role = 'assistant' AND response_ms IS NOT NULL")
    Double selectAvgResponseMs();

    @Select("SELECT m.id FROM consult_message m JOIN consult_session s ON m.session_id = s.id"
            + " WHERE m.id = #{messageId} AND s.user_id = #{userId}")
    Long selectOwnedMessageId(@Param("messageId") Long messageId, @Param("userId") Long userId);
}
