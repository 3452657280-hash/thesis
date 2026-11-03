package com.legal.consult.config;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.legal.consult.entity.LawyerProfile;
import com.legal.consult.entity.SysUser;
import com.legal.consult.mapper.LawyerProfileMapper;
import com.legal.consult.mapper.SysUserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.env.Environment;
import org.springframework.core.env.Profiles;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class DataInitializer implements ApplicationRunner {

    private final SysUserMapper userMapper;
    private final LawyerProfileMapper lawyerProfileMapper;
    private final PasswordEncoder passwordEncoder;
    private final Environment environment;

    @Override
    public void run(ApplicationArguments args) {
        Long adminCount = userMapper.selectCount(new LambdaQueryWrapper<SysUser>().eq(SysUser::getRole, "ADMIN"));
        if (adminCount == 0) {
            createUser("admin", "admin123", "系统管理员", "ADMIN");
            log.info("已创建默认管理员账号 admin / admin123");
        }
        if (environment.acceptsProfiles(Profiles.of("dev"))) {
            if (findUser("user1") == null) {
                createUser("user1", "123456", "演示用户", "USER");
            }
            SysUser lawyer = findUser("lawyer1");
            if (lawyer == null) {
                lawyer = createUser("lawyer1", "123456", "演示律师", "LAWYER");
            }
            Long exists = lawyerProfileMapper.selectCount(
                    new LambdaQueryWrapper<LawyerProfile>().eq(LawyerProfile::getUserId, lawyer.getId()));
            if (exists == 0) {
                LawyerProfile p = new LawyerProfile();
                p.setUserId(lawyer.getId());
                p.setRealName("张律师（演示）");
                p.setLicenseNo("DEMO-0000000001");
                p.setLawFirm("演示律师事务所");
                p.setSpecialty("劳动纠纷,合同纠纷,婚姻家庭");
                p.setYears(8);
                p.setIntro("本条为演示数据，非真实律师信息。");
                p.setAuditStatus(1);
                p.setAuditRemark("演示数据");
                lawyerProfileMapper.insert(p);
            }
            log.info("dev 环境演示账号：user1/123456（USER）、lawyer1/123456（LAWYER）");
        }
    }

    private SysUser findUser(String username) {
        return userMapper.selectOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
    }

    private SysUser createUser(String username, String password, String nickname, String role) {
        SysUser u = new SysUser();
        u.setUsername(username);
        u.setPassword(passwordEncoder.encode(password));
        u.setNickname(nickname);
        u.setRole(role);
        u.setStatus(1);
        userMapper.insert(u);
        return u;
    }
}
