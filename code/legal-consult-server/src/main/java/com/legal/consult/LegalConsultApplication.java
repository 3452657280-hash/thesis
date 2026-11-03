package com.legal.consult;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration;

@SpringBootApplication(exclude = UserDetailsServiceAutoConfiguration.class)
@MapperScan("com.legal.consult.mapper")
public class LegalConsultApplication {

    public static void main(String[] args) {
        SpringApplication.run(LegalConsultApplication.class, args);
    }
}
