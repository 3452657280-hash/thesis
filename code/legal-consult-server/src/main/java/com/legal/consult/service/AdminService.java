package com.legal.consult.service;

import com.legal.consult.common.PageResult;
import com.legal.consult.dto.AdminConsultVO;
import com.legal.consult.dto.AdminRequests;
import com.legal.consult.entity.DocTemplate;
import com.legal.consult.entity.LawArticle;
import com.legal.consult.entity.LawyerProfile;
import com.legal.consult.entity.Notice;
import com.legal.consult.entity.SysUser;

import java.util.List;
import java.util.Map;

public interface AdminService {

    PageResult<SysUser> pageUsers(String keyword, String role, Integer page, Integer size);

    void updateUserStatus(Long operatorId, Long userId, Integer status);

    void resetPassword(Long userId);

    List<LawyerProfile> listLawyers(Integer auditStatus);

    void audit(Long profileId, AdminRequests.Audit req);

    PageResult<LawArticle> pageLaws(String keyword, String lawName, Integer page, Integer size);

    LawArticle getLaw(Long id);

    void saveLaw(Long id, AdminRequests.Law req);

    void deleteLaw(Long id);

    PageResult<DocTemplate> pageTemplates(String keyword, String category, Integer page, Integer size);

    DocTemplate getTemplate(Long id);

    void saveTemplate(Long id, AdminRequests.Template req);

    void deleteTemplate(Long id);

    List<Notice> listNotices();

    Notice getNotice(Long id);

    void saveNotice(Long id, AdminRequests.NoticeReq req);

    void deleteNotice(Long id);

    PageResult<AdminConsultVO> pageConsults(Integer page, Integer size);

    Map<String, Object> stats();
}
