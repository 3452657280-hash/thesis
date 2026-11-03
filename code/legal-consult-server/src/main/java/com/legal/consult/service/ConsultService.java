package com.legal.consult.service;

import com.legal.consult.dto.FavoriteVO;
import com.legal.consult.entity.ConsultMessage;
import com.legal.consult.entity.ConsultSession;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;

public interface ConsultService {

    List<ConsultSession> listSessions(Long uid);

    ConsultSession createSession(Long uid);

    void renameSession(Long uid, Long sessionId, String title);

    void deleteSession(Long uid, Long sessionId);

    List<ConsultMessage> listMessages(Long uid, Long sessionId);

    SseEmitter chat(Long uid, Long sessionId, String content);

    void addFavorite(Long uid, Long messageId);

    void removeFavorite(Long uid, Long messageId);

    List<FavoriteVO> listFavorites(Long uid);

    void feedback(Long uid, Long messageId, Integer score, String comment);
}
