package com.legal.consult.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.legal.consult.entity.Appointment;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface AppointmentMapper extends BaseMapper<Appointment> {

    @Select("SELECT a.*, l.real_name AS lawyer_name, l.law_firm FROM appointment a"
            + " JOIN lawyer_profile l ON a.lawyer_id = l.id WHERE a.user_id = #{userId} ORDER BY a.id DESC")
    List<Appointment> selectByUser(@Param("userId") Long userId);

    @Select("<script>SELECT a.*, u.username, u.nickname, u.phone FROM appointment a"
            + " JOIN sys_user u ON a.user_id = u.id WHERE a.lawyer_id = #{lawyerId}"
            + "<if test='status != null'> AND a.status = #{status}</if>"
            + " ORDER BY a.id DESC</script>")
    List<Appointment> selectByLawyer(@Param("lawyerId") Long lawyerId, @Param("status") Integer status);
}
