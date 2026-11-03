package com.legal.consult.common;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;

public final class PageQuery {

    private PageQuery() {
    }

    public static <T> Page<T> of(Integer page, Integer size) {
        long p = page == null || page < 1 ? 1 : page;
        long s = size == null || size < 1 ? 10 : Math.min(size, 100);
        return new Page<>(p, s);
    }
}
