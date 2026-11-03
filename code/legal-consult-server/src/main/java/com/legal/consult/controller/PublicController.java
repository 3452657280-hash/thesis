package com.legal.consult.controller;

import com.legal.consult.common.PageResult;
import com.legal.consult.common.Result;
import com.legal.consult.dto.PublicLawyerVO;
import com.legal.consult.entity.DocTemplate;
import com.legal.consult.entity.LawArticle;
import com.legal.consult.entity.Notice;
import com.legal.consult.service.PublicService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/public")
@RequiredArgsConstructor
public class PublicController {

    private final PublicService publicService;

    @GetMapping("/laws")
    public Result<PageResult<LawArticle>> laws(@RequestParam(required = false) String keyword,
                                               @RequestParam(required = false) String lawName,
                                               @RequestParam(required = false) Integer page,
                                               @RequestParam(required = false) Integer size) {
        return Result.ok(publicService.pageLaws(keyword, lawName, page, size));
    }

    @GetMapping("/laws/names")
    public Result<List<String>> lawNames() {
        return Result.ok(publicService.lawNames());
    }

    @GetMapping("/templates")
    public Result<PageResult<DocTemplate>> templates(@RequestParam(required = false) String category,
                                                     @RequestParam(required = false) Integer page,
                                                     @RequestParam(required = false) Integer size) {
        return Result.ok(publicService.pageTemplates(category, page, size));
    }

    @GetMapping("/templates/{id}/download")
    public ResponseEntity<Void> download(@PathVariable Long id) {
        String url = publicService.download(id);
        return ResponseEntity.status(HttpStatus.FOUND).header(HttpHeaders.LOCATION, url).build();
    }

    @GetMapping("/notices")
    public Result<List<Notice>> notices() {
        return Result.ok(publicService.notices());
    }

    @GetMapping("/lawyers")
    public Result<PageResult<PublicLawyerVO>> lawyers(@RequestParam(required = false) String specialty,
                                                      @RequestParam(required = false) Integer page,
                                                      @RequestParam(required = false) Integer size) {
        return Result.ok(publicService.pageLawyers(specialty, page, size));
    }
}
