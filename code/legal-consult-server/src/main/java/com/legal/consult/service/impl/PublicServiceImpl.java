package com.legal.consult.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.legal.consult.common.BizException;
import com.legal.consult.common.PageQuery;
import com.legal.consult.common.PageResult;
import com.legal.consult.dto.PublicLawyerVO;
import com.legal.consult.entity.DocTemplate;
import com.legal.consult.entity.LawArticle;
import com.legal.consult.entity.LawyerProfile;
import com.legal.consult.entity.Notice;
import com.legal.consult.mapper.DocTemplateMapper;
import com.legal.consult.mapper.LawArticleMapper;
import com.legal.consult.mapper.LawyerProfileMapper;
import com.legal.consult.mapper.NoticeMapper;
import com.legal.consult.service.PublicService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
@RequiredArgsConstructor
public class PublicServiceImpl implements PublicService {

    private final LawArticleMapper lawMapper;
    private final DocTemplateMapper templateMapper;
    private final NoticeMapper noticeMapper;
    private final LawyerProfileMapper lawyerProfileMapper;

    @Override
    public PageResult<LawArticle> pageLaws(String keyword, String lawName, Integer page, Integer size) {
        LambdaQueryWrapper<LawArticle> qw = new LambdaQueryWrapper<LawArticle>()
                .eq(StringUtils.hasText(lawName), LawArticle::getLawName, lawName);
        if (StringUtils.hasText(keyword)) {
            String k = keyword.trim();
            qw.and(w -> w.like(LawArticle::getContent, k)
                    .or().like(LawArticle::getLawName, k)
                    .or().like(LawArticle::getArticleNo, k)
                    .or().like(LawArticle::getChapter, k));
        }
        qw.orderByAsc(LawArticle::getLawName).orderByAsc(LawArticle::getId);
        IPage<LawArticle> p = lawMapper.selectPage(PageQuery.of(page, size), qw);
        return PageResult.of(p);
    }

    @Override
    public List<String> lawNames() {
        return lawMapper.selectLawNames();
    }

    @Override
    public PageResult<DocTemplate> pageTemplates(String category, Integer page, Integer size) {
        LambdaQueryWrapper<DocTemplate> qw = new LambdaQueryWrapper<DocTemplate>()
                .eq(StringUtils.hasText(category), DocTemplate::getCategory, category)
                .orderByDesc(DocTemplate::getId);
        return PageResult.of(templateMapper.selectPage(PageQuery.of(page, size), qw));
    }

    @Override
    public String download(Long templateId) {
        DocTemplate t = templateMapper.selectById(templateId);
        if (t == null) {
            throw new BizException(404, "模板不存在");
        }
        templateMapper.increaseDownload(templateId);
        return t.getFileUrl();
    }

    @Override
    public List<Notice> notices() {
        return noticeMapper.selectList(new LambdaQueryWrapper<Notice>()
                .orderByDesc(Notice::getPublishTime).orderByDesc(Notice::getId));
    }

    @Override
    public PageResult<PublicLawyerVO> pageLawyers(String specialty, Integer page, Integer size) {
        LambdaQueryWrapper<LawyerProfile> qw = new LambdaQueryWrapper<LawyerProfile>()
                .eq(LawyerProfile::getAuditStatus, 1)
                .like(StringUtils.hasText(specialty), LawyerProfile::getSpecialty, specialty)
                .orderByDesc(LawyerProfile::getYears).orderByAsc(LawyerProfile::getId);
        IPage<LawyerProfile> p = lawyerProfileMapper.selectPage(PageQuery.of(page, size), qw);
        return PageResult.of(p.getRecords().stream().map(PublicLawyerVO::of).toList(), p.getTotal());
    }
}
