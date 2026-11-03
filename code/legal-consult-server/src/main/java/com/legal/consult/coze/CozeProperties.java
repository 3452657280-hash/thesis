package com.legal.consult.coze;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "coze")
public class CozeProperties {

    private String baseUrl = "https://api.coze.cn";
    private String botId;
    private String token;
    private boolean mock = true;
    private int timeoutSeconds = 120;

    public boolean isMockMode() {
        return mock || isBlank(token) || isBlank(botId);
    }

    private static boolean isBlank(String s) {
        return s == null || s.isBlank();
    }
}
