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
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  username    VARCHAR(50)  NOT NULL UNIQUE,
  password    VARCHAR(100) NOT NULL,
  nickname    VARCHAR(50),
  phone       VARCHAR(20),
  email       VARCHAR(100),
  role        VARCHAR(20)  NOT NULL DEFAULT 'USER',
  status      TINYINT      NOT NULL DEFAULT 1,
  create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lawyer_profile (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id      BIGINT       NOT NULL UNIQUE,
  real_name    VARCHAR(50)  NOT NULL,
  license_no   VARCHAR(50)  NOT NULL,
  law_firm     VARCHAR(100),
  specialty    VARCHAR(200),
  years        INT          DEFAULT 0,
  intro        VARCHAR(1000),
  audit_status TINYINT      NOT NULL DEFAULT 0,
  audit_remark VARCHAR(255),
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_lawyer_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
);

CREATE TABLE consult_session (
  id                   BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id              BIGINT       NOT NULL,
  title                VARCHAR(100) NOT NULL DEFAULT '新的咨询',
  coze_conversation_id VARCHAR(64),
  create_time          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
);
CREATE INDEX idx_session_user ON consult_session(user_id);

CREATE TABLE consult_message (
  id             BIGINT PRIMARY KEY AUTO_INCREMENT,
  session_id     BIGINT      NOT NULL,
  role           VARCHAR(16) NOT NULL,
  content        CLOB        NOT NULL,
  category       VARCHAR(32),
  response_ms    INT,
  first_token_ms INT,
  create_time    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_msg_session FOREIGN KEY (session_id) REFERENCES consult_session(id) ON DELETE CASCADE
);
CREATE INDEX idx_msg_session ON consult_message(session_id);

CREATE TABLE law_article (
  id             BIGINT PRIMARY KEY AUTO_INCREMENT,
  law_name       VARCHAR(100) NOT NULL,
  chapter        VARCHAR(100),
  article_no     VARCHAR(20)  NOT NULL,
  content        CLOB         NOT NULL,
  effective_date DATE,
  create_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_law_name ON law_article(law_name);

CREATE TABLE doc_template (
  id             BIGINT PRIMARY KEY AUTO_INCREMENT,
  name           VARCHAR(100) NOT NULL,
  category       VARCHAR(50),
  description    VARCHAR(500),
  file_url       VARCHAR(255) NOT NULL,
  download_count INT          NOT NULL DEFAULT 0,
  create_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointment (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id      BIGINT        NOT NULL,
  lawyer_id    BIGINT        NOT NULL,
  question     VARCHAR(2000) NOT NULL,
  appoint_time DATETIME,
  status       TINYINT       NOT NULL DEFAULT 0,
  reply        VARCHAR(2000),
  create_time  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  update_time  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_appt_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
  CONSTRAINT fk_appt_lawyer FOREIGN KEY (lawyer_id) REFERENCES lawyer_profile(id)
);
CREATE INDEX idx_appt_user ON appointment(user_id);
CREATE INDEX idx_appt_lawyer ON appointment(lawyer_id);

CREATE TABLE feedback (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  message_id  BIGINT   NOT NULL,
  user_id     BIGINT   NOT NULL,
  score       TINYINT  NOT NULL,
  comment     VARCHAR(500),
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_fb UNIQUE (message_id, user_id),
  CONSTRAINT fk_fb_msg FOREIGN KEY (message_id) REFERENCES consult_message(id) ON DELETE CASCADE,
  CONSTRAINT fk_fb_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
);

CREATE TABLE favorite (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id     BIGINT   NOT NULL,
  message_id  BIGINT   NOT NULL,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_fav UNIQUE (user_id, message_id),
  CONSTRAINT fk_fav_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
  CONSTRAINT fk_fav_msg FOREIGN KEY (message_id) REFERENCES consult_message(id) ON DELETE CASCADE
);

CREATE TABLE notice (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  title        VARCHAR(200) NOT NULL,
  content      CLOB         NOT NULL,
  publish_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);
