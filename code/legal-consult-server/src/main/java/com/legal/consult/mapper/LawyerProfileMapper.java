package com.legal.consult.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.legal.consult.entity.LawyerProfile;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface LawyerProfileMapper extends BaseMapper<LawyerProfile> {

    @Select("<script>SELECT l.*, u.username FROM lawyer_profile l JOIN sys_user u ON l.user_id = u.id"
            + "<if test='auditStatus != null'> WHERE l.audit_status = #{auditStatus}</if>"
            + " ORDER BY l.id DESC</script>")
    List<LawyerProfile> selectWithUser(@Param("auditStatus") Integer auditStatus);
}
