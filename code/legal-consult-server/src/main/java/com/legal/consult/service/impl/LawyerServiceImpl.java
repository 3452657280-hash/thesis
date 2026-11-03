package com.legal.consult.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.legal.consult.common.BizException;
import com.legal.consult.dto.LawyerRequests;
import com.legal.consult.entity.Appointment;
import com.legal.consult.entity.LawyerProfile;
import com.legal.consult.mapper.AppointmentMapper;
import com.legal.consult.mapper.LawyerProfileMapper;
import com.legal.consult.service.LawyerService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class LawyerServiceImpl implements LawyerService {

    private final LawyerProfileMapper profileMapper;
    private final AppointmentMapper appointmentMapper;

    @Override
    public LawyerProfile myProfile(Long uid) {
        return profileMapper.selectOne(new LambdaQueryWrapper<LawyerProfile>().eq(LawyerProfile::getUserId, uid));
    }

    @Override
    public void saveProfile(Long uid, LawyerRequests.Profile req) {
        LawyerProfile existing = myProfile(uid);
        if (existing == null) {
            LawyerProfile p = new LawyerProfile();
            p.setUserId(uid);
            p.setRealName(req.getRealName().trim());
            p.setLicenseNo(req.getLicenseNo().trim());
            p.setLawFirm(req.getLawFirm());
            p.setSpecialty(req.getSpecialty());
            p.setYears(req.getYears() == null ? 0 : req.getYears());
            p.setIntro(req.getIntro());
            p.setAuditStatus(0);
            profileMapper.insert(p);
            return;
        }
        profileMapper.update(null, new LambdaUpdateWrapper<LawyerProfile>()
                .eq(LawyerProfile::getId, existing.getId())
                .set(LawyerProfile::getRealName, req.getRealName().trim())
                .set(LawyerProfile::getLicenseNo, req.getLicenseNo().trim())
                .set(LawyerProfile::getLawFirm, req.getLawFirm())
                .set(LawyerProfile::getSpecialty, req.getSpecialty())
                .set(LawyerProfile::getYears, req.getYears() == null ? 0 : req.getYears())
                .set(LawyerProfile::getIntro, req.getIntro())
                .set(LawyerProfile::getAuditStatus, 0)
                .set(LawyerProfile::getAuditRemark, null));
    }

    @Override
    public List<Appointment> myReceivedAppointments(Long uid, Integer status) {
        LawyerProfile p = myProfile(uid);
        if (p == null) {
            return List.of();
        }
        return appointmentMapper.selectByLawyer(p.getId(), status);
    }

    @Override
    public void handleAppointment(Long uid, Long appointmentId, LawyerRequests.HandleAppointment req) {
        LawyerProfile p = myProfile(uid);
        Appointment a = appointmentMapper.selectById(appointmentId);
        if (p == null || a == null || !a.getLawyerId().equals(p.getId())) {
            throw new BizException(404, "预约不存在");
        }
        int target = req.getStatus();
        int current = a.getStatus() == null ? 0 : a.getStatus();
        boolean allowed = (current == 0 && (target == 1 || target == 2 || target == 3))
                || (current == 1 && (target == 3 || target == 1));
        if (!allowed) {
            throw new BizException("当前预约状态不允许该操作");
        }
        LambdaUpdateWrapper<Appointment> uw = new LambdaUpdateWrapper<Appointment>()
                .eq(Appointment::getId, appointmentId)
                .set(Appointment::getStatus, target)
                .set(Appointment::getUpdateTime, LocalDateTime.now());
        if (req.getReply() != null) {
            uw.set(Appointment::getReply, req.getReply().trim());
        }
        appointmentMapper.update(null, uw);
    }

    @Override
    public void createAppointment(Long uid, LawyerRequests.CreateAppointment req) {
        LawyerProfile p = profileMapper.selectById(req.getLawyerId());
        if (p == null || p.getAuditStatus() == null || p.getAuditStatus() != 1) {
            throw new BizException("该律师不存在或尚未通过审核");
        }
        if (p.getUserId().equals(uid)) {
            throw new BizException("不能预约自己");
        }
        if (req.getAppointTime() != null && req.getAppointTime().isBefore(LocalDateTime.now().minusMinutes(5))) {
            throw new BizException("期望咨询时间不能早于当前时间");
        }
        Appointment a = new Appointment();
        a.setUserId(uid);
        a.setLawyerId(p.getId());
        a.setQuestion(req.getQuestion().trim());
        a.setAppointTime(req.getAppointTime());
        a.setStatus(0);
        appointmentMapper.insert(a);
    }

    @Override
    public List<Appointment> myAppointments(Long uid) {
        return appointmentMapper.selectByUser(uid);
    }
}
