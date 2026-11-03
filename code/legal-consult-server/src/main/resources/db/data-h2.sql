INSERT INTO notice (title, content, publish_time) VALUES
('欢迎使用法律咨询系统', '本系统基于Coze智能体提供法律问题初步咨询，智能体回答仅供参考，不构成正式法律意见；复杂问题请预约执业律师。', CURRENT_TIMESTAMP);

INSERT INTO doc_template (name, category, description, file_url, download_count) VALUES
('劳动仲裁申请书（示例）', '劳动', '示例模板，链接为占位地址，请管理员替换为真实文件', 'https://example.com/templates/labor-arbitration.docx', 0),
('房屋租赁合同（示例）', '合同', '示例模板，链接为占位地址，请管理员替换为真实文件', 'https://example.com/templates/house-lease.docx', 0);
