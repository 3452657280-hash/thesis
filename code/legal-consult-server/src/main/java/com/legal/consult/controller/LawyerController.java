package com.legal.consult.controller;

import com.legal.consult.common.Result;
import com.legal.consult.dto.LawyerRequests;
import com.legal.consult.entity.Appointment;
import com.legal.consult.entity.LawyerProfile;
import com.legal.consult.security.SecurityUtil;
import com.legal.consult.service.LawyerService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/lawyer")
@RequiredArgsConstructor
public class LawyerController {

    private final LawyerService lawyerService;

    @GetMapping("/profile")
    public Result<LawyerProfile> profile() {
        return Result.ok(lawyerService.myProfile(SecurityUtil.uid()));
    }

    @PostMapping("/profile")
    public Result<Void> saveProfile(@Valid @RequestBody LawyerRequests.Profile req) {
        lawyerService.saveProfile(SecurityUtil.uid(), req);
        return Result.ok();
    }

    @GetMapping("/appointments")
    public Result<List<Appointment>> appointments(@RequestParam(required = false) Integer status) {
        return Result.ok(lawyerService.myReceivedAppointments(SecurityUtil.uid(), status));
    }

    @PutMapping("/appointments/{id}")
    public Result<Void> handle(@PathVariable Long id, @Valid @RequestBody LawyerRequests.HandleAppointment req) {
        lawyerService.handleAppointment(SecurityUtil.uid(), id, req);
        return Result.ok();
    }
}
