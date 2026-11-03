package com.legal.consult.service;

import com.legal.consult.common.PageResult;
import com.legal.consult.dto.PublicLawyerVO;
import com.legal.consult.entity.DocTemplate;
import com.legal.consult.entity.LawArticle;
import com.legal.consult.entity.Notice;

import java.util.List;

public interface PublicService {

    PageResult<LawArticle> pageLaws(String keyword, String lawName, Integer page, Integer size);

    List<String> lawNames();

    PageResult<DocTemplate> pageTemplates(String category, Integer page, Integer size);

    String download(Long templateId);

    List<Notice> notices();

    PageResult<PublicLawyerVO> pageLawyers(String specialty, Integer page, Integer size);
}
