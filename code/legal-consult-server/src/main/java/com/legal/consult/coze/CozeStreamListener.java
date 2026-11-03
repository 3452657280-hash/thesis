package com.legal.consult.coze;

public interface CozeStreamListener {

    void onDelta(String content);

    void onConversationId(String conversationId);
}
