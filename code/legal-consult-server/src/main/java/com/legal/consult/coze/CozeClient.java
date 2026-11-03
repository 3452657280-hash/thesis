package com.legal.consult.coze;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.util.HexFormat;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

@Slf4j
@Component
@RequiredArgsConstructor
public class CozeClient {

    private static final String MOCK_ANSWER = """
            【演示模式：未连接Coze智能体】

            以下为系统演示用的示例回答结构，并非针对您问题的真实法律意见。

            ### 一、问题分析
            您描述的情况涉及当事人之间的权利义务关系。真实模式下，智能体会先识别问题类别（如劳动、合同、婚姻家庭、消费维权、交通事故等），再结合知识库检索结果进行分析。

            ### 二、法律依据
            演示模式不提供法条。连接Coze智能体后，此处将列出知识库中检索到的相关法律条文及出处。

            ### 三、处理建议
            1. 整理并保存与事件相关的书面材料、聊天记录、票据等证据；
            2. 优先尝试与对方协商解决，并保留协商记录；
            3. 协商不成时，可向有关部门投诉、申请调解或仲裁，或依法提起诉讼。

            ### 四、风险提示
            - 法律程序通常存在时效限制，请及时主张权利；
            - 本回答仅供参考，不构成正式法律意见，复杂问题建议预约执业律师。
            """;

    private final CozeProperties properties;
    private final ObjectMapper objectMapper;
    private HttpClient httpClient;
    private ScheduledExecutorService watchdog;

    @PostConstruct
    public void init() {
        httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(15))
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        watchdog = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "coze-watchdog");
            t.setDaemon(true);
            return t;
        });
        if (properties.isMockMode()) {
            log.warn("Coze 运行于演示(mock)模式：不会访问 Coze API。如需接入真实智能体，请配置 COZE_TOKEN、COZE_BOT_ID 并设置 COZE_MOCK=false");
        } else {
            log.info("Coze 真实模式已启用，bot_id={}", properties.getBotId());
        }
    }

    @PreDestroy
    public void destroy() {
        watchdog.shutdownNow();
    }

    public boolean isMock() {
        return properties.isMockMode();
    }

    public String chat(Long userId, String conversationId, String content, CozeStreamListener listener) {
        if (properties.isMockMode()) {
            return mockChat(listener);
        }
        return realChat(userId, conversationId, content, listener);
    }

    private String mockChat(CozeStreamListener listener) {
        String text = MOCK_ANSWER.strip();
        int step = 6;
        try {
            Thread.sleep(300);
            for (int i = 0; i < text.length(); i += step) {
                listener.onDelta(text.substring(i, Math.min(text.length(), i + step)));
                Thread.sleep(40);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new CozeException("请求已中断");
        }
        return text;
    }

    private String realChat(Long userId, String conversationId, String content, CozeStreamListener listener) {
        String url = trimSlash(properties.getBaseUrl()) + "/v3/chat";
        if (conversationId != null && !conversationId.isBlank()) {
            url += "?conversation_id=" + URLEncoder.encode(conversationId, StandardCharsets.UTF_8);
        }
        ObjectNode body = objectMapper.createObjectNode();
        body.put("bot_id", properties.getBotId());
        body.put("user_id", cozeUserId(userId));
        body.put("stream", true);
        body.put("auto_save_history", true);
        ArrayNode messages = body.putArray("additional_messages");
        ObjectNode msg = messages.addObject();
        msg.put("role", "user");
        msg.put("content", content);
        msg.put("content_type", "text");

        int timeout = Math.max(10, properties.getTimeoutSeconds());
        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .timeout(Duration.ofSeconds(timeout))
                .header("Authorization", "Bearer " + properties.getToken())
                .header("Content-Type", "application/json")
                .header("Accept", "text/event-stream")
                .POST(HttpRequest.BodyPublishers.ofString(body.toString(), StandardCharsets.UTF_8))
                .build();

        HttpResponse<InputStream> response;
        try {
            response = httpClient.send(request, HttpResponse.BodyHandlers.ofInputStream());
        } catch (HttpTimeoutException e) {
            throw new CozeException("连接智能体超时，请稍后重试", e);
        } catch (IOException e) {
            throw new CozeException("无法连接智能体服务：" + e.getMessage(), e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new CozeException("请求已中断", e);
        }

        AtomicBoolean timedOut = new AtomicBoolean(false);
        InputStream in = response.body();
        ScheduledFuture<?> guard = watchdog.schedule(() -> {
            timedOut.set(true);
            closeQuietly(in);
        }, timeout, TimeUnit.SECONDS);
        try {
            if (response.statusCode() != 200) {
                String err = new String(in.readAllBytes(), StandardCharsets.UTF_8);
                log.warn("Coze HTTP {}: {}", response.statusCode(), err);
                throw new CozeException("智能体服务返回错误（HTTP " + response.statusCode() + "）：" + extractMsg(err));
            }
            String contentType = response.headers().firstValue("Content-Type").orElse("");
            if (contentType.contains("application/json")) {
                String err = new String(in.readAllBytes(), StandardCharsets.UTF_8);
                log.warn("Coze 返回非流式错误: {}", err);
                throw new CozeException("智能体服务返回错误：" + extractMsg(err));
            }
            return readStream(in, listener);
        } catch (IOException e) {
            if (timedOut.get()) {
                throw new CozeException("智能体响应超时（超过" + timeout + "秒）", e);
            }
            throw new CozeException("读取智能体响应失败：" + e.getMessage(), e);
        } finally {
            guard.cancel(false);
            closeQuietly(in);
        }
    }

    private String readStream(InputStream in, CozeStreamListener listener) throws IOException {
        StreamState state = new StreamState();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
            String line;
            String event = null;
            StringBuilder data = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                if (Thread.currentThread().isInterrupted()) {
                    throw new CozeException("请求已中断");
                }
                if (line.isEmpty()) {
                    if (event != null || data.length() > 0) {
                        handleEvent(event, data.toString(), state, listener);
                        event = null;
                        data.setLength(0);
                        if (state.finished) {
                            break;
                        }
                    }
                    continue;
                }
                if (line.startsWith(":")) {
                    continue;
                }
                if (line.startsWith("event:")) {
                    if (data.length() > 0) {
                        handleEvent(event, data.toString(), state, listener);
                        data.setLength(0);
                        if (state.finished) {
                            break;
                        }
                    }
                    event = stripLeadingSpace(line.substring(6)).trim();
                } else if (line.startsWith("data:")) {
                    if (data.length() > 0) {
                        data.append('\n');
                    }
                    data.append(stripLeadingSpace(line.substring(5)));
                }
            }
            if (!state.finished && (event != null || data.length() > 0)) {
                handleEvent(event, data.toString(), state, listener);
            }
        }
        if (state.error != null) {
            throw new CozeException(state.error);
        }
        String answer = state.completedAnswer != null && !state.completedAnswer.isEmpty()
                ? state.completedAnswer : state.deltaBuffer.toString();
        if (answer.isBlank()) {
            throw new CozeException("智能体未返回有效回答");
        }
        return answer;
    }

    private void handleEvent(String event, String data, StreamState state, CozeStreamListener listener) {
        if (event == null) {
            event = "";
        }
        JsonNode node = null;
        if (!data.isEmpty()) {
            try {
                node = objectMapper.readTree(data);
            } catch (IOException ignored) {
            }
        }
        if (node != null && node.isObject()) {
            String cid = text(node, "conversation_id");
            if (cid != null && !cid.isEmpty() && !cid.equals(state.conversationId)) {
                state.conversationId = cid;
                listener.onConversationId(cid);
            }
        }
        switch (event) {
            case "conversation.message.delta" -> {
                if (node != null && "answer".equals(text(node, "type")) && "assistant".equals(text(node, "role"))) {
                    String piece = text(node, "content");
                    if (piece != null && !piece.isEmpty()) {
                        state.deltaBuffer.append(piece);
                        listener.onDelta(piece);
                    }
                }
            }
            case "conversation.message.completed" -> {
                if (node != null && "answer".equals(text(node, "type"))) {
                    String full = text(node, "content");
                    if (full != null && !full.isEmpty()) {
                        state.completedAnswer = full;
                    }
                }
            }
            case "conversation.chat.failed" -> {
                String msg = null;
                if (node != null && node.has("last_error")) {
                    msg = text(node.get("last_error"), "msg");
                }
                state.error = "智能体处理失败：" + (msg == null || msg.isEmpty() ? "未知错误" : msg);
                state.finished = true;
            }
            case "error" -> {
                String msg = node != null ? text(node, "msg") : null;
                state.error = "智能体返回错误：" + (msg == null || msg.isEmpty() ? data : msg);
                state.finished = true;
            }
            case "conversation.chat.completed", "done" -> state.finished = true;
            default -> {
            }
        }
    }

    public static String cozeUserId(Long userId) {
        try {
            byte[] hash = MessageDigest.getInstance("SHA-256")
                    .digest(String.valueOf(userId).getBytes(StandardCharsets.UTF_8));
            return "lc_" + HexFormat.of().formatHex(hash).substring(0, 16);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    private String extractMsg(String body) {
        try {
            JsonNode node = objectMapper.readTree(body);
            String msg = text(node, "msg");
            if (msg != null && !msg.isEmpty()) {
                return msg;
            }
        } catch (IOException ignored) {
        }
        return body.length() > 200 ? body.substring(0, 200) : body;
    }

    private static String text(JsonNode node, String field) {
        if (node == null) {
            return null;
        }
        JsonNode v = node.get(field);
        return v == null || v.isNull() ? null : v.asText();
    }

    private static String stripLeadingSpace(String s) {
        return s.startsWith(" ") ? s.substring(1) : s;
    }

    private static String trimSlash(String s) {
        return s.endsWith("/") ? s.substring(0, s.length() - 1) : s;
    }

    private static void closeQuietly(InputStream in) {
        try {
            in.close();
        } catch (IOException ignored) {
        }
    }

    private static class StreamState {
        final StringBuilder deltaBuffer = new StringBuilder();
        String completedAnswer;
        String conversationId;
        String error;
        boolean finished;
    }
}
