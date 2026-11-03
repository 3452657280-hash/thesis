package com.legal.consult.service;

import com.legal.consult.dto.AuthRequests;
import com.legal.consult.dto.LoginResponse;
import com.legal.consult.entity.SysUser;

public interface UserService {

    void register(AuthRequests.Register req);

    LoginResponse login(AuthRequests.Login req);

    SysUser getById(Long id);

    void updateMe(Long uid, AuthRequests.UpdateMe req);

    void changePassword(Long uid, AuthRequests.ChangePassword req);
}
