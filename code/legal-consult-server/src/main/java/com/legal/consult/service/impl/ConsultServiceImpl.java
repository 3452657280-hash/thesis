package com.legal.consult.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.legal.consult.common.BizException;
import com.legal.consult.coze.CozeClient;
import com.legal.consult.coze.CozeStreamListener;
import com.legal.consult.dto.FavoriteVO;
import com.legal.consult.entity.ConsultMessage;
import com.legal.consult.entity.ConsultSession;
import com.legal.consult.entity.Favorite;
import com.legal.consult.entity.Feedback;
import com.legal.consult.mapper.ConsultMessageMapper;
import com.legal.consult.mapper.ConsultSessionMapper;
import com.legal.consult.mapper.FavoriteMapper;
import com.legal.consult.mapper.FeedbackMapper;
import com.legal.consult.service.ConsultService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.task.TaskExecutor;
import org.springframework.core.task.TaskRejectedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

@Slf4j
@Service
public class ConsultServiceImpl implements ConsultService {

    private static final long SSE_TIMEOUT_MS = 180_000L;
    private static final String DEFAULT_TITLE = "新的咨询";

    private final ConsultSessionMapper sessionMapper;
    private final ConsultMessageMapper messageMapper;
    private final FavoriteMapper favoriteMapper;
    private final FeedbackMapper feedbackMapper;
    private final CozeClient cozeClient;
    private final ObjectMapper objectMapper;
    private final TaskExecutor chatExecutor;
    private final Set<Long> runningSessions = ConcurrentHashMap.newKeySet();

    public ConsultServiceImpl(ConsultSessionMapper sessionMapper, ConsultMessageMapper messageMapper,
                              FavoriteMapper favoriteMapper, FeedbackMapper feedbackMapper,
                              CozeClient cozeClient, ObjectMapper objectMapper,
                              @Qualifier("chatExecutor") TaskExecutor chatExecutor) {
        this.sessionMapper = sessionMapper;
        this.messageMapper = messageMapper;
        this.favoriteMapper = favoriteMapper;
        this.feedbackMapper = feedbackMapper;
        this.cozeClient = cozeClient;
        this.objectMapper = objectMapper;
        this.chatExecutor = chatExecutor;
    }

    @Override
    public List<ConsultSession> listSessions(Long uid) {
        return sessionMapper.selectList(new LambdaQueryWrapper<ConsultSession>()
                .eq(ConsultSession::getUserId, uid)
                .orderByDesc(ConsultSession::getUpdateTime)
                .orderByDesc(ConsultSession::getId));
    }

    @Override
    public ConsultSession createSession(Long uid) {
        ConsultSession s = new ConsultSession();
        s.setUserId(uid);
        s.setTitle(DEFAULT_TITLE);
        sessionMapper.insert(s);
        return s;
    }

    @Override
    public void renameSession(Long uid, Long sessionId, String title) {
        ownedSession(uid, sessionId);
        sessionMapper.update(null, new LambdaUpdateWrapper<ConsultSession>()
                .eq(ConsultSession::getId, sessionId)
                .set(ConsultSession::getTitle, title.trim()));
    }

    @Override
    @Transactional
    public void deleteSession(Long uid, Long sessionId) {
        ownedSession(uid, sessionId);
        if (runningSessions.contains(sessionId)) {
            throw new BizException("该会话正在生成回答，请稍后再删除");
        }
        List<Long> ids = messageMapper.selectList(new LambdaQueryWrapper<ConsultMessage>()
                        .select(ConsultMessage::getId).eq(ConsultMessage::getSessionId, sessionId))
                .stream().map(ConsultMessage::getId).toList();
        if (!ids.isEmpty()) {
            favoriteMapper.delete(new LambdaQueryWrapper<Favorite>().in(Favorite::getMessageId, ids));
            feedbackMapper.delete(new LambdaQueryWrapper<Feedback>().in(Feedback::getMessageId, ids));
            messageMapper.delete(new LambdaQueryWrapper<ConsultMessage>().eq(ConsultMessage::getSessionId, sessionId));
        }
        sessionMapper.deleteById(sessionId);
    }

    @Override
    public List<ConsultMessage> listMessages(Long uid, Long sessionId) {
        ownedSession(uid, sessionId);
        List<ConsultMessage> list = messageMapper.selectList(new LambdaQueryWrapper<ConsultMessage>()
                .eq(ConsultMessage::getSessionId, sessionId)
                .orderByAsc(ConsultMessage::getCreateTime)
                .orderByAsc(ConsultMessage::getId));
        if (list.isEmpty()) {
            return list;
        }
        List<Long> ids = list.stream().map(ConsultMessage::getId).toList();
        Set<Long> favIds = favoriteMapper.selectList(new LambdaQueryWrapper<Favorite>()
                        .eq(Favorite::getUserId, uid).in(Favorite::getMessageId, ids))
                .stream().map(Favorite::getMessageId).collect(Collectors.toSet());
        Map<Long, Integer> scores = feedbackMapper.selectList(new LambdaQueryWrapper<Feedback>()
                        .eq(Feedback::getUserId, uid).in(Feedback::getMessageId, ids))
                .stream().collect(Collectors.toMap(Feedback::getMessageId, Feedback::getScore, (a, b) -> b));
        for (ConsultMessage m : list) {
            m.setFavorited(favIds.contains(m.getId()));
            m.setMyScore(scores.get(m.getId()));
        }
        return list;
    }

    @Override
    public SseEmitter chat(Long uid, Long sessionId, String content) {
        ConsultSession session = ownedSession(uid, sessionId);
        SseEmitter emitter = new SseEmitter(SSE_TIMEOUT_MS);
        if (!runningSessions.add(sessionId)) {
            sendQuietly(emitter, "error", Map.of("msg", "上一条回答尚未完成，请稍候"));
            emitter.complete();
            return emitter;
        }
        String question = content.trim();
        ConsultMessage userMsg;
        try {
            Long userCount = messageMapper.selectCount(new LambdaQueryWrapper<ConsultMessage>()
                    .eq(ConsultMessage::getSessionId, sessionId)
                    .eq(ConsultMessage::getRole, "user"));
            userMsg = new ConsultMessage();
            userMsg.setSessionId(sessionId);
            userMsg.setRole("user");
            userMsg.setContent(question);
            messageMapper.insert(userMsg);
            LambdaUpdateWrapper<ConsultSession> uw = new LambdaUpdateWrapper<ConsultSession>()
                    .eq(ConsultSession::getId, sessionId)
                    .set(ConsultSession::getUpdateTime, LocalDateTime.now());
            if (userCount == 0) {
                uw.set(ConsultSession::getTitle, buildTitle(question));
            }
            sessionMapper.update(null, uw);
        } catch (RuntimeException e) {
            runningSessions.remove(sessionId);
            throw e;
        }

        AtomicBoolean clientGone = new AtomicBoolean(false);
        emitter.onTimeout(() -> {
            clientGone.set(true);
            emitter.complete();
        });
        emitter.onError(e -> clientGone.set(true));
        emitter.onCompletion(() -> clientGone.set(true));

        Long userMsgId = userMsg.getId();
        String conversationId = session.getCozeConversationId();
        try {
            chatExecutor.execute(() -> runChat(uid, sessionId, conversationId, question, userMsgId, emitter, clientGone));
        } catch (TaskRejectedException e) {
            runningSessions.remove(sessionId);
            sendQuietly(emitter, "error", Map.of("msg", "系统繁忙，请稍后重试"));
            emitter.complete();
        }
        return emitter;
    }

    private void runChat(Long uid, Long sessionId, String conversationId, String question, Long userMsgId,
                         SseEmitter emitter, AtomicBoolean clientGone) {
        long start = System.currentTimeMillis();
        AtomicLong firstTokenAt = new AtomicLong(0);
        AtomicReference<String> newConversationId = new AtomicReference<>();
        try {
            String answer = cozeClient.chat(uid, conversationId, question, new CozeStreamListener() {
                @Override
                public void onDelta(String piece) {
                    firstTokenAt.compareAndSet(0, System.currentTimeMillis());
                    if (!clientGone.get()) {
                        if (!send(emitter, "delta", Map.of("content", piece))) {
                            clientGone.set(true);
                        }
                    }
                }

                @Override
                public void onConversationId(String cid) {
                    newConversationId.set(cid);
                }
            });
            long end = System.currentTimeMillis();
            int responseMs = (int) (end - start);
            Integer firstTokenMs = firstTokenAt.get() > 0 ? (int) (firstTokenAt.get() - start) : responseMs;

            ConsultMessage reply = new ConsultMessage();
            reply.setSessionId(sessionId);
            reply.setRole("assistant");
            reply.setContent(answer);
            reply.setResponseMs(responseMs);
            reply.setFirstTokenMs(firstTokenMs);
            messageMapper.insert(reply);
            updateSessionAfterChat(sessionId, newConversationId.get());

            Map<String, Object> done = new LinkedHashMap<>();
            done.put("messageId", reply.getId());
            done.put("userMessageId", userMsgId);
            done.put("responseMs", responseMs);
            done.put("firstTokenMs", firstTokenMs);
            if (!clientGone.get()) {
                send(emitter, "done", done);
            }
        } catch (Exception e) {
            log.warn("会话 {} 调用智能体失败：{}", sessionId, e.getMessage());
            try {
                updateSessionAfterChat(sessionId, newConversationId.get());
            } catch (Exception ex) {
                log.warn("更新会话失败", ex);
            }
            if (!clientGone.get()) {
                String msg = e instanceof com.legal.consult.coze.CozeException && e.getMessage() != null
                        ? e.getMessage() : "智能体响应异常，请稍后重试";
                send(emitter, "error", Map.of("msg", msg));
            }
        } finally {
            runningSessions.remove(sessionId);
            try {
                emitter.complete();
            } catch (Exception ignored) {
            }
        }
    }

    private void updateSessionAfterChat(Long sessionId, String cid) {
        LambdaUpdateWrapper<ConsultSession> uw = new LambdaUpdateWrapper<ConsultSession>()
                .eq(ConsultSession::getId, sessionId)
                .set(ConsultSession::getUpdateTime, LocalDateTime.now());
        if (cid != null && !cid.isBlank()) {
            uw.set(ConsultSession::getCozeConversationId, cid);
        }
        sessionMapper.update(null, uw);
    }

    private boolean send(SseEmitter emitter, String event, Object data) {
        try {
            emitter.send(SseEmitter.event().name(event).data(objectMapper.writeValueAsString(data)));
            return true;
        } catch (IOException | IllegalStateException e) {
            return false;
        }
    }

    private void sendQuietly(SseEmitter emitter, String event, Object data) {
        send(emitter, event, data);
    }

    private String buildTitle(String question) {
        String t = question.replaceAll("\\s+", " ").trim();
        if (t.isEmpty()) {
            return DEFAULT_TITLE;
        }
        int end = t.offsetByCodePoints(0, Math.min(20, t.codePointCount(0, t.length())));
        return t.substring(0, end);
    }

    private ConsultSession ownedSession(Long uid, Long sessionId) {
        ConsultSession s = sessionMapper.selectById(sessionId);
        if (s == null || !s.getUserId().equals(uid)) {
            throw new BizException(404, "会话不存在");
        }
        return s;
    }

    private ConsultMessage ownedMessage(Long uid, Long messageId) {
        Long id = messageMapper.selectOwnedMessageId(messageId, uid);
        if (id == null) {
            throw new BizException(404, "消息不存在");
        }
        return messageMapper.selectById(id);
    }

    @Override
    public void addFavorite(Long uid, Long messageId) {
        ownedMessage(uid, messageId);
        Long exists = favoriteMapper.selectCount(new LambdaQueryWrapper<Favorite>()
                .eq(Favorite::getUserId, uid).eq(Favorite::getMessageId, messageId));
        if (exists > 0) {
            return;
        }
        Favorite f = new Favorite();
        f.setUserId(uid);
        f.setMessageId(messageId);
        try {
            favoriteMapper.insert(f);
        } catch (org.springframework.dao.DuplicateKeyException ignored) {
        }
    }

    @Override
    public void removeFavorite(Long uid, Long messageId) {
        favoriteMapper.delete(new LambdaQueryWrapper<Favorite>()
                .eq(Favorite::getUserId, uid).eq(Favorite::getMessageId, messageId));
    }

    @Override
    public List<FavoriteVO> listFavorites(Long uid) {
        return messageMapper.selectFavorites(uid);
    }

    @Override
    public void feedback(Long uid, Long messageId, Integer score, String comment) {
        ConsultMessage m = ownedMessage(uid, messageId);
        if (!"assistant".equals(m.getRole())) {
            throw new BizException("只能评价智能体的回答");
        }
        Feedback existing = feedbackMapper.selectOne(new LambdaQueryWrapper<Feedback>()
                .eq(Feedback::getUserId, uid).eq(Feedback::getMessageId, messageId));
        if (existing != null) {
            feedbackMapper.update(null, new LambdaUpdateWrapper<Feedback>()
                    .eq(Feedback::getId, existing.getId())
                    .set(Feedback::getScore, score)
                    .set(Feedback::getComment, comment));
            return;
        }
        Feedback f = new Feedback();
        f.setUserId(uid);
        f.setMessageId(messageId);
        f.setScore(score);
        f.setComment(comment);
        feedbackMapper.insert(f);
    }
}
