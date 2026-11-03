package com.legal.consult.controller;

import com.legal.consult.common.Result;
import com.legal.consult.dto.LawyerRequests;
import com.legal.consult.entity.Appointment;
import com.legal.consult.security.SecurityUtil;
import com.legal.consult.service.LawyerService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/appointments")
@RequiredArgsConstructor
public class AppointmentController {

    private final LawyerService lawyerService;

    @PostMapping
    public Result<Void> create(@Valid @RequestBody LawyerRequests.CreateAppointment req) {
        lawyerService.createAppointment(SecurityUtil.uid(), req);
        return Result.ok();
    }

    @GetMapping("/my")
    public Result<List<Appointment>> my() {
        return Result.ok(lawyerService.myAppointments(SecurityUtil.uid()));
    }
}
