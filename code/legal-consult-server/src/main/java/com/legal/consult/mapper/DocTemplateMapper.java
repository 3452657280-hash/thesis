package com.legal.consult.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.legal.consult.entity.DocTemplate;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

public interface DocTemplateMapper extends BaseMapper<DocTemplate> {

    @Update("UPDATE doc_template SET download_count = download_count + 1 WHERE id = #{id}")
    int increaseDownload(@Param("id") Long id);
}
