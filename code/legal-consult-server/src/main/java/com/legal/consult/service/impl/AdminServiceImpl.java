package com.legal.consult.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.legal.consult.common.BizException;
import com.legal.consult.common.PageQuery;
import com.legal.consult.common.PageResult;
import com.legal.consult.dto.AdminConsultVO;
import com.legal.consult.dto.AdminRequests;
import com.legal.consult.dto.DailyCount;
import com.legal.consult.dto.ScoreCount;
import com.legal.consult.entity.ConsultMessage;
import com.legal.consult.entity.ConsultSession;
import com.legal.consult.entity.DocTemplate;
import com.legal.consult.entity.LawArticle;
import com.legal.consult.entity.LawyerProfile;
import com.legal.consult.entity.Notice;
import com.legal.consult.entity.SysUser;
import com.legal.consult.mapper.ConsultMessageMapper;
import com.legal.consult.mapper.ConsultSessionMapper;
import com.legal.consult.mapper.DocTemplateMapper;
import com.legal.consult.mapper.FeedbackMapper;
import com.legal.consult.mapper.LawArticleMapper;
import com.legal.consult.mapper.LawyerProfileMapper;
import com.legal.consult.mapper.NoticeMapper;
import com.legal.consult.mapper.SysUserMapper;
import com.legal.consult.service.AdminService;
import com.legal.consult.service.PublicService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AdminServiceImpl implements AdminService {

    private final SysUserMapper userMapper;
    private final LawyerProfileMapper lawyerProfileMapper;
    private final LawArticleMapper lawMapper;
    private final DocTemplateMapper templateMapper;
    private final NoticeMapper noticeMapper;
    private final ConsultSessionMapper sessionMapper;
    private final ConsultMessageMapper messageMapper;
    private final FeedbackMapper feedbackMapper;
    private final PasswordEncoder passwordEncoder;
    private final PublicService publicService;

    @Override
    public PageResult<SysUser> pageUsers(String keyword, String role, Integer page, Integer size) {
        LambdaQueryWrapper<SysUser> qw = new LambdaQueryWrapper<SysUser>()
                .eq(StringUtils.hasText(role), SysUser::getRole, role);
        if (StringUtils.hasText(keyword)) {
            String k = keyword.trim();
            qw.and(w -> w.like(SysUser::getUsername, k).or().like(SysUser::getNickname, k).or().like(SysUser::getPhone, k));
        }
        qw.orderByDesc(SysUser::getId);
        return PageResult.of(userMapper.selectPage(PageQuery.of(page, size), qw));
    }

    @Override
    public void updateUserStatus(Long operatorId, Long userId, Integer status) {
        SysUser u = requireUser(userId);
        if ("ADMIN".equals(u.getRole()) && status == 0) {
            throw new BizException("不能禁用管理员账号");
        }
        if (u.getId().equals(operatorId)) {
            throw new BizException("不能修改自己的状态");
        }
        userMapper.update(null, new LambdaUpdateWrapper<SysUser>()
                .eq(SysUser::getId, userId)
                .set(SysUser::getStatus, status)
                .set(SysUser::getUpdateTime, LocalDateTime.now()));
    }

    @Override
    public void resetPassword(Long userId) {
        requireUser(userId);
        userMapper.update(null, new LambdaUpdateWrapper<SysUser>()
                .eq(SysUser::getId, userId)
                .set(SysUser::getPassword, passwordEncoder.encode("123456"))
                .set(SysUser::getUpdateTime, LocalDateTime.now()));
    }

    private SysUser requireUser(Long userId) {
        SysUser u = userMapper.selectById(userId);
        if (u == null) {
            throw new BizException(404, "用户不存在");
        }
        return u;
    }

    @Override
    public List<LawyerProfile> listLawyers(Integer auditStatus) {
        return lawyerProfileMapper.selectWithUser(auditStatus);
    }

    @Override
    public void audit(Long profileId, AdminRequests.Audit req) {
        if (lawyerProfileMapper.selectById(profileId) == null) {
            throw new BizException(404, "律师资质信息不存在");
        }
        if (req.getAuditStatus() == 2 && !StringUtils.hasText(req.getAuditRemark())) {
            throw new BizException("驳回时请填写审核意见");
        }
        lawyerProfileMapper.update(null, new LambdaUpdateWrapper<LawyerProfile>()
                .eq(LawyerProfile::getId, profileId)
                .set(LawyerProfile::getAuditStatus, req.getAuditStatus())
                .set(LawyerProfile::getAuditRemark, req.getAuditRemark()));
    }

    @Override
    public PageResult<LawArticle> pageLaws(String keyword, String lawName, Integer page, Integer size) {
        return publicService.pageLaws(keyword, lawName, page, size);
    }

    @Override
    public LawArticle getLaw(Long id) {
        LawArticle a = lawMapper.selectById(id);
        if (a == null) {
            throw new BizException(404, "法条不存在");
        }
        return a;
    }

    @Override
    public void saveLaw(Long id, AdminRequests.Law req) {
        if (id == null) {
            LawArticle a = new LawArticle();
            a.setLawName(req.getLawName().trim());
            a.setChapter(req.getChapter());
            a.setArticleNo(req.getArticleNo().trim());
            a.setContent(req.getContent());
            a.setEffectiveDate(req.getEffectiveDate());
            lawMapper.insert(a);
            return;
        }
        getLaw(id);
        lawMapper.update(null, new LambdaUpdateWrapper<LawArticle>()
                .eq(LawArticle::getId, id)
                .set(LawArticle::getLawName, req.getLawName().trim())
                .set(LawArticle::getChapter, req.getChapter())
                .set(LawArticle::getArticleNo, req.getArticleNo().trim())
                .set(LawArticle::getContent, req.getContent())
                .set(LawArticle::getEffectiveDate, req.getEffectiveDate()));
    }

    @Override
    public void deleteLaw(Long id) {
        getLaw(id);
        lawMapper.deleteById(id);
    }

    @Override
    public PageResult<DocTemplate> pageTemplates(String keyword, String category, Integer page, Integer size) {
        LambdaQueryWrapper<DocTemplate> qw = new LambdaQueryWrapper<DocTemplate>()
                .eq(StringUtils.hasText(category), DocTemplate::getCategory, category)
                .like(StringUtils.hasText(keyword), DocTemplate::getName, keyword)
                .orderByDesc(DocTemplate::getId);
        return PageResult.of(templateMapper.selectPage(PageQuery.of(page, size), qw));
    }

    @Override
    public DocTemplate getTemplate(Long id) {
        DocTemplate t = templateMapper.selectById(id);
        if (t == null) {
            throw new BizException(404, "模板不存在");
        }
        return t;
    }

    @Override
    public void saveTemplate(Long id, AdminRequests.Template req) {
        if (id == null) {
            DocTemplate t = new DocTemplate();
            t.setName(req.getName().trim());
            t.setCategory(req.getCategory());
            t.setDescription(req.getDescription());
            t.setFileUrl(req.getFileUrl().trim());
            t.setDownloadCount(0);
            templateMapper.insert(t);
            return;
        }
        getTemplate(id);
        templateMapper.update(null, new LambdaUpdateWrapper<DocTemplate>()
                .eq(DocTemplate::getId, id)
                .set(DocTemplate::getName, req.getName().trim())
                .set(DocTemplate::getCategory, req.getCategory())
                .set(DocTemplate::getDescription, req.getDescription())
                .set(DocTemplate::getFileUrl, req.getFileUrl().trim()));
    }

    @Override
    public void deleteTemplate(Long id) {
        getTemplate(id);
        templateMapper.deleteById(id);
    }

    @Override
    public List<Notice> listNotices() {
        return publicService.notices();
    }

    @Override
    public Notice getNotice(Long id) {
        Notice n = noticeMapper.selectById(id);
        if (n == null) {
            throw new BizException(404, "公告不存在");
        }
        return n;
    }

    @Override
    public void saveNotice(Long id, AdminRequests.NoticeReq req) {
        if (id == null) {
            Notice n = new Notice();
            n.setTitle(req.getTitle().trim());
            n.setContent(req.getContent());
            n.setPublishTime(LocalDateTime.now());
            noticeMapper.insert(n);
            return;
        }
        getNotice(id);
        noticeMapper.update(null, new LambdaUpdateWrapper<Notice>()
                .eq(Notice::getId, id)
                .set(Notice::getTitle, req.getTitle().trim())
                .set(Notice::getContent, req.getContent()));
    }

    @Override
    public void deleteNotice(Long id) {
        getNotice(id);
        noticeMapper.deleteById(id);
    }

    @Override
    public PageResult<AdminConsultVO> pageConsults(Integer page, Integer size) {
        return PageResult.of(messageMapper.selectAdminConsults(PageQuery.of(page, size)));
    }

    @Override
    public Map<String, Object> stats() {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("userCount", userMapper.selectCount(new LambdaQueryWrapper<SysUser>().eq(SysUser::getRole, "USER")));
        m.put("lawyerCount", userMapper.selectCount(new LambdaQueryWrapper<SysUser>().eq(SysUser::getRole, "LAWYER")));
        m.put("sessionCount", sessionMapper.selectCount(new LambdaQueryWrapper<ConsultSession>()));
        m.put("questionCount", messageMapper.selectCount(new LambdaQueryWrapper<ConsultMessage>().eq(ConsultMessage::getRole, "user")));
        m.put("avgScore", round1(feedbackMapper.selectAvgScore()));
        m.put("avgResponseMs", round1(messageMapper.selectAvgResponseMs()));

        LocalDate today = LocalDate.now();
        LocalDate first = today.minusDays(13);
        Map<LocalDate, Long> counts = new HashMap<>();
        for (DailyCount dc : messageMapper.selectDailyQuestions(first.atStartOfDay())) {
            if (dc.getStatDate() != null) {
                counts.merge(dc.getStatDate(), dc.getCnt() == null ? 0 : dc.getCnt(), Long::sum);
            }
        }
        List<Map<String, Object>> daily = new ArrayList<>();
        for (int i = 0; i < 14; i++) {
            LocalDate d = first.plusDays(i);
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("date", d.toString());
            item.put("count", counts.getOrDefault(d, 0L));
            daily.add(item);
        }
        m.put("dailyQuestions", daily);

        Map<Integer, Long> scoreMap = new HashMap<>();
        for (ScoreCount sc : feedbackMapper.selectScoreCounts()) {
            if (sc.getScore() != null) {
                scoreMap.put(sc.getScore(), sc.getCnt() == null ? 0 : sc.getCnt());
            }
        }
        List<Map<String, Object>> dist = new ArrayList<>();
        for (int s = 1; s <= 5; s++) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("score", s);
            item.put("count", scoreMap.getOrDefault(s, 0L));
            dist.add(item);
        }
        m.put("scoreDistribution", dist);
        return m;
    }

    private static double round1(Double v) {
        if (v == null || v.isNaN()) {
            return 0.0;
        }
        return BigDecimal.valueOf(v).setScale(1, RoundingMode.HALF_UP).doubleValue();
    }
}
