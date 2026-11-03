package com.legal.consult.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.legal.consult.common.BizException;
import com.legal.consult.common.Result;
import com.legal.consult.dto.ConsultRequests;
import com.legal.consult.dto.FavoriteVO;
import com.legal.consult.entity.ConsultMessage;
import com.legal.consult.entity.ConsultSession;
import com.legal.consult.security.SecurityUtil;
import com.legal.consult.service.ConsultService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/consult")
@RequiredArgsConstructor
public class ConsultController {

    private final ConsultService consultService;
    private final ObjectMapper objectMapper;

    @GetMapping("/sessions")
    public Result<List<ConsultSession>> sessions() {
        return Result.ok(consultService.listSessions(SecurityUtil.uid()));
    }

    @PostMapping("/sessions")
    public Result<Map<String, Object>> create() {
        ConsultSession s = consultService.createSession(SecurityUtil.uid());
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("id", s.getId());
        data.put("title", s.getTitle());
        data.put("createTime", s.getCreateTime());
        data.put("updateTime", s.getUpdateTime());
        return Result.ok(data);
    }

    @PutMapping("/sessions/{id}")
    public Result<Void> rename(@PathVariable Long id, @Valid @RequestBody ConsultRequests.Title req) {
        consultService.renameSession(SecurityUtil.uid(), id, req.getTitle());
        return Result.ok();
    }

    @DeleteMapping("/sessions/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        consultService.deleteSession(SecurityUtil.uid(), id);
        return Result.ok();
    }

    @GetMapping("/sessions/{id}/messages")
    public Result<List<ConsultMessage>> messages(@PathVariable Long id) {
        return Result.ok(consultService.listMessages(SecurityUtil.uid(), id));
    }

    @PostMapping(value = "/sessions/{id}/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chat(@PathVariable Long id, @RequestBody(required = false) ConsultRequests.Chat req) {
        Long uid = SecurityUtil.uid();
        String content = req == null ? null : req.getContent();
        try {
            if (content == null || content.isBlank()) {
                throw new BizException("提问内容不能为空");
            }
            if (content.length() > 2000) {
                throw new BizException("提问内容不能超过2000个字符");
            }
            return consultService.chat(uid, id, content);
        } catch (BizException e) {
            SseEmitter emitter = new SseEmitter(10_000L);
            try {
                emitter.send(SseEmitter.event().name("error")
                        .data(objectMapper.writeValueAsString(Map.of("msg", e.getMessage()))));
            } catch (IOException ignored) {
            }
            emitter.complete();
            return emitter;
        }
    }

    @PostMapping("/messages/{id}/favorite")
    public Result<Void> favorite(@PathVariable Long id) {
        consultService.addFavorite(SecurityUtil.uid(), id);
        return Result.ok();
    }

    @DeleteMapping("/messages/{id}/favorite")
    public Result<Void> unfavorite(@PathVariable Long id) {
        consultService.removeFavorite(SecurityUtil.uid(), id);
        return Result.ok();
    }

    @GetMapping("/favorites")
    public Result<List<FavoriteVO>> favorites() {
        return Result.ok(consultService.listFavorites(SecurityUtil.uid()));
    }

    @PostMapping("/messages/{id}/feedback")
    public Result<Void> feedback(@PathVariable Long id, @Valid @RequestBody ConsultRequests.FeedbackReq req) {
        consultService.feedback(SecurityUtil.uid(), id, req.getScore(), req.getComment());
        return Result.ok();
    }
}
