SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for stock_messages
-- ----------------------------
DROP TABLE IF EXISTS `stock_messages`;
"""
CREATE TABLE IF NOT EXISTS stock_messages (
    `id` int(11)  NOT NULL AUTO_INCREMENT PRIMARY KEY,
    unkey VARCHAR(64) NOT NULL COMMENT '去重值',
    content_type INT NOT NULL DEFAULT 0 COMMENT '内容类型',
    trade VARCHAR(64) NOT NULL DEFAULT '' COMMENT '交易类型',
    main_content VARCHAR(255)  NOT NULL DEFAULT '' COMMENT '主要内容',
    attached_content VARCHAR(255) NOT NULL DEFAULT '' COMMENT '附加内容',
    stock_code VARCHAR(10) NOT NULL DEFAULT '' COMMENT '股票代码',
    sec_id VARCHAR(20) NOT NULL DEFAULT '' COMMENT '证券 ID',
    company VARCHAR(64) NOT NULL DEFAULT '' COMMENT '公司简称',
    board_type VARCHAR(64) NOT NULL DEFAULT '' COMMENT '板块类型',
    key_word VARCHAR(64) NOT NULL DEFAULT '' COMMENT '关键字',
    update_date DATETIME  COMMENT '更新时间',
    pub_date DATETIME  COMMENT '发布时间',
    remind_status TINYINT(1) NOT NULL DEFAULT 0 FALSE COMMENT '提醒状态1已提醒0未提醒'
    index unkey (unkey)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票消息信息表';
"""
