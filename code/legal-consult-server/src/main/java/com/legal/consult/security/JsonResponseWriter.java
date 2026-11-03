package com.legal.consult.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.legal.consult.common.Result;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;

public final class JsonResponseWriter {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private JsonResponseWriter() {
    }

    public static void write(HttpServletResponse response, int status, String msg) throws IOException {
        if (response.isCommitted()) {
            return;
        }
        response.setStatus(status);
        response.setCharacterEncoding("UTF-8");
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write(MAPPER.writeValueAsString(Result.fail(status, msg)));
    }
}
