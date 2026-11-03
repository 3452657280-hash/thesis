package com.legal.consult.service;

import com.legal.consult.dto.LawyerRequests;
import com.legal.consult.entity.Appointment;
import com.legal.consult.entity.LawyerProfile;

import java.util.List;

public interface LawyerService {

    LawyerProfile myProfile(Long uid);

    void saveProfile(Long uid, LawyerRequests.Profile req);

    List<Appointment> myReceivedAppointments(Long uid, Integer status);

    void handleAppointment(Long uid, Long appointmentId, LawyerRequests.HandleAppointment req);

    void createAppointment(Long uid, LawyerRequests.CreateAppointment req);

    List<Appointment> myAppointments(Long uid);
}
