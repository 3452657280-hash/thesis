-- 基于Coze智能体的法律咨询系统 数据库脚本
-- MySQL 8.0, utf8mb4
CREATE DATABASE IF NOT EXISTS legal_consult DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE legal_consult;

DROP TABLE IF EXISTS favorite;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS appointment;
DROP TABLE IF EXISTS consult_message;
DROP TABLE IF EXISTS consult_session;
DROP TABLE IF EXISTS lawyer_profile;
DROP TABLE IF EXISTS law_article;
DROP TABLE IF EXISTS doc_template;
DROP TABLE IF EXISTS notice;
DROP TABLE IF EXISTS sys_user;

CREATE TABLE sys_user (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  username    VARCHAR(50)  NOT NULL UNIQUE COMMENT '登录名',
  password    VARCHAR(100) NOT NULL COMMENT 'BCrypt加密密码',
  nickname    VARCHAR(50)  COMMENT '昵称',
  phone       VARCHAR(20)  COMMENT '手机号',
  email       VARCHAR(100) COMMENT '邮箱',
  role        VARCHAR(20)  NOT NULL DEFAULT 'USER' COMMENT '角色 USER/LAWYER/ADMIN',
  status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1正常 0禁用',
  create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '用户表';

CREATE TABLE lawyer_profile (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id      BIGINT       NOT NULL UNIQUE COMMENT '关联用户',
  real_name    VARCHAR(50)  NOT NULL COMMENT '真实姓名',
  license_no   VARCHAR(50)  NOT NULL COMMENT '执业证号',
  law_firm     VARCHAR(100) COMMENT '所在律所',
  specialty    VARCHAR(200) COMMENT '擅长领域，逗号分隔',
  years        INT          DEFAULT 0 COMMENT '执业年限',
  intro        VARCHAR(1000) COMMENT '个人简介',
  audit_status TINYINT      NOT NULL DEFAULT 0 COMMENT '0待审核 1通过 2驳回',
  audit_remark VARCHAR(255) COMMENT '审核意见',
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_lawyer_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
) COMMENT '律师信息表';

CREATE TABLE consult_session (
  id                   BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id              BIGINT       NOT NULL,
  title                VARCHAR(100) NOT NULL DEFAULT '新的咨询' COMMENT '会话标题',
  coze_conversation_id VARCHAR(64)  COMMENT 'Coze会话ID，用于多轮上下文',
  create_time          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_session_user (user_id),
  CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
) COMMENT '咨询会话表';

CREATE TABLE consult_message (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  session_id  BIGINT      NOT NULL,
  role        VARCHAR(16) NOT NULL COMMENT 'user/assistant',
  content     MEDIUMTEXT  NOT NULL,
  category    VARCHAR(32) COMMENT '问题类别（智能体识别结果，可为空）',
  response_ms INT         COMMENT '智能体完整响应耗时(ms)',
  first_token_ms INT      COMMENT '首字响应耗时(ms)',
  create_time DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_msg_session (session_id),
  CONSTRAINT fk_msg_session FOREIGN KEY (session_id) REFERENCES consult_session(id) ON DELETE CASCADE
) COMMENT '咨询消息表';

CREATE TABLE law_article (
  id             BIGINT PRIMARY KEY AUTO_INCREMENT,
  law_name       VARCHAR(100) NOT NULL COMMENT '法律名称',
  chapter        VARCHAR(100) COMMENT '编/章',
  article_no     VARCHAR(20)  NOT NULL COMMENT '条号，如 第五百七十七条',
  content        TEXT         NOT NULL,
  effective_date DATE         COMMENT '施行日期',
  create_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_law_name (law_name),
  FULLTEXT KEY ft_content (content) WITH PARSER ngram
) COMMENT '法条表';

CREATE TABLE doc_template (
  id             BIGINT PRIMARY KEY AUTO_INCREMENT,
  name           VARCHAR(100) NOT NULL,
  category       VARCHAR(50)  COMMENT '类别：劳动/合同/婚姻家庭/消费维权/交通事故',
  description    VARCHAR(500),
  file_url       VARCHAR(255) NOT NULL,
  download_count INT          NOT NULL DEFAULT 0,
  create_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) COMMENT '法律文书模板表';

CREATE TABLE appointment (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id      BIGINT       NOT NULL,
  lawyer_id    BIGINT       NOT NULL COMMENT 'lawyer_profile.id',
  question     VARCHAR(2000) NOT NULL,
  appoint_time DATETIME     COMMENT '期望咨询时间',
  status       TINYINT      NOT NULL DEFAULT 0 COMMENT '0待处理 1已接受 2已拒绝 3已完成',
  reply        VARCHAR(2000) COMMENT '律师回复',
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_appt_user (user_id),
  KEY idx_appt_lawyer (lawyer_id),
  CONSTRAINT fk_appt_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
  CONSTRAINT fk_appt_lawyer FOREIGN KEY (lawyer_id) REFERENCES lawyer_profile(id)
) COMMENT '律师预约表';

CREATE TABLE feedback (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  message_id  BIGINT       NOT NULL,
  user_id     BIGINT       NOT NULL,
  score       TINYINT      NOT NULL COMMENT '1-5分',
  comment     VARCHAR(500),
  create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_fb (message_id, user_id),
  CONSTRAINT fk_fb_msg FOREIGN KEY (message_id) REFERENCES consult_message(id) ON DELETE CASCADE,
  CONSTRAINT fk_fb_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
) COMMENT '回答评价表';

CREATE TABLE favorite (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id     BIGINT   NOT NULL,
  message_id  BIGINT   NOT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_fav (user_id, message_id),
  CONSTRAINT fk_fav_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
  CONSTRAINT fk_fav_msg FOREIGN KEY (message_id) REFERENCES consult_message(id) ON DELETE CASCADE
) COMMENT '收藏表';

CREATE TABLE notice (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  title        VARCHAR(200) NOT NULL,
  content      TEXT         NOT NULL,
  publish_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) COMMENT '公告表';

-- 初始管理员：admin / admin123（BCrypt 由后端首次启动时初始化，见 DataInitializer）
