package com.legal.consult.dto;

import com.legal.consult.entity.LawyerProfile;
import lombok.Data;

@Data
public class PublicLawyerVO {

    private Long id;
    private String realName;
    private String lawFirm;
    private String specialty;
    private Integer years;
    private String intro;

    public static PublicLawyerVO of(LawyerProfile p) {
        PublicLawyerVO vo = new PublicLawyerVO();
        vo.setId(p.getId());
        vo.setRealName(p.getRealName());
        vo.setLawFirm(p.getLawFirm());
        vo.setSpecialty(p.getSpecialty());
        vo.setYears(p.getYears());
        vo.setIntro(p.getIntro());
        return vo;
    }
}
