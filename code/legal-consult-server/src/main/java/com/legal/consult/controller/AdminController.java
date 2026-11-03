package com.legal.consult.controller;

import com.legal.consult.common.PageResult;
import com.legal.consult.common.Result;
import com.legal.consult.dto.AdminConsultVO;
import com.legal.consult.dto.AdminRequests;
import com.legal.consult.entity.DocTemplate;
import com.legal.consult.entity.LawArticle;
import com.legal.consult.entity.LawyerProfile;
import com.legal.consult.entity.Notice;
import com.legal.consult.entity.SysUser;
import com.legal.consult.security.SecurityUtil;
import com.legal.consult.service.AdminService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {

    private final AdminService adminService;

    @GetMapping("/users")
    public Result<PageResult<SysUser>> users(@RequestParam(required = false) String keyword,
                                             @RequestParam(required = false) String role,
                                             @RequestParam(required = false) Integer page,
                                             @RequestParam(required = false) Integer size) {
        return Result.ok(adminService.pageUsers(keyword, role, page, size));
    }

    @PutMapping("/users/{id}/status")
    public Result<Void> userStatus(@PathVariable Long id, @Valid @RequestBody AdminRequests.UserStatus req) {
        adminService.updateUserStatus(SecurityUtil.uid(), id, req.getStatus());
        return Result.ok();
    }

    @PutMapping("/users/{id}/reset-password")
    public Result<Void> resetPassword(@PathVariable Long id) {
        adminService.resetPassword(id);
        return Result.ok();
    }

    @GetMapping("/lawyers")
    public Result<List<LawyerProfile>> lawyers(@RequestParam(required = false) Integer auditStatus) {
        return Result.ok(adminService.listLawyers(auditStatus));
    }

    @PutMapping("/lawyers/{id}/audit")
    public Result<Void> audit(@PathVariable Long id, @Valid @RequestBody AdminRequests.Audit req) {
        adminService.audit(id, req);
        return Result.ok();
    }

    @GetMapping("/laws")
    public Result<PageResult<LawArticle>> laws(@RequestParam(required = false) String keyword,
                                               @RequestParam(required = false) String lawName,
                                               @RequestParam(required = false) Integer page,
                                               @RequestParam(required = false) Integer size) {
        return Result.ok(adminService.pageLaws(keyword, lawName, page, size));
    }

    @GetMapping("/laws/{id}")
    public Result<LawArticle> law(@PathVariable Long id) {
        return Result.ok(adminService.getLaw(id));
    }

    @PostMapping("/laws")
    public Result<Void> createLaw(@Valid @RequestBody AdminRequests.Law req) {
        adminService.saveLaw(null, req);
        return Result.ok();
    }

    @PutMapping("/laws/{id}")
    public Result<Void> updateLaw(@PathVariable Long id, @Valid @RequestBody AdminRequests.Law req) {
        adminService.saveLaw(id, req);
        return Result.ok();
    }

    @DeleteMapping("/laws/{id}")
    public Result<Void> deleteLaw(@PathVariable Long id) {
        adminService.deleteLaw(id);
        return Result.ok();
    }

    @GetMapping("/templates")
    public Result<PageResult<DocTemplate>> templates(@RequestParam(required = false) String keyword,
                                                     @RequestParam(required = false) String category,
                                                     @RequestParam(required = false) Integer page,
                                                     @RequestParam(required = false) Integer size) {
        return Result.ok(adminService.pageTemplates(keyword, category, page, size));
    }

    @GetMapping("/templates/{id}")
    public Result<DocTemplate> template(@PathVariable Long id) {
        return Result.ok(adminService.getTemplate(id));
    }

    @PostMapping("/templates")
    public Result<Void> createTemplate(@Valid @RequestBody AdminRequests.Template req) {
        adminService.saveTemplate(null, req);
        return Result.ok();
    }

    @PutMapping("/templates/{id}")
    public Result<Void> updateTemplate(@PathVariable Long id, @Valid @RequestBody AdminRequests.Template req) {
        adminService.saveTemplate(id, req);
        return Result.ok();
    }

    @DeleteMapping("/templates/{id}")
    public Result<Void> deleteTemplate(@PathVariable Long id) {
        adminService.deleteTemplate(id);
        return Result.ok();
    }

    @GetMapping("/notices")
    public Result<List<Notice>> notices() {
        return Result.ok(adminService.listNotices());
    }

    @GetMapping("/notices/{id}")
    public Result<Notice> notice(@PathVariable Long id) {
        return Result.ok(adminService.getNotice(id));
    }

    @PostMapping("/notices")
    public Result<Void> createNotice(@Valid @RequestBody AdminRequests.NoticeReq req) {
        adminService.saveNotice(null, req);
        return Result.ok();
    }

    @PutMapping("/notices/{id}")
    public Result<Void> updateNotice(@PathVariable Long id, @Valid @RequestBody AdminRequests.NoticeReq req) {
        adminService.saveNotice(id, req);
        return Result.ok();
    }

    @DeleteMapping("/notices/{id}")
    public Result<Void> deleteNotice(@PathVariable Long id) {
        adminService.deleteNotice(id);
        return Result.ok();
    }

    @GetMapping("/consults")
    public Result<PageResult<AdminConsultVO>> consults(@RequestParam(required = false) Integer page,
                                                       @RequestParam(required = false) Integer size) {
        return Result.ok(adminService.pageConsults(page, size));
    }

    @GetMapping("/stats")
    public Result<Map<String, Object>> stats() {
        return Result.ok(adminService.stats());
    }
}
