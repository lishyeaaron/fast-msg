SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for events
-- ----------------------------
DROP TABLE IF EXISTS `events`;
CREATE TABLE `events` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '事件 ID，自增主键',
  `host` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '事件所在主机名',
  `type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '事件类型',
  `event` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '事件名称',
  `desc` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '事件描述',
  `severity` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '事件的严重程度，无符号整型',
  `handling_time` int(10) unsigned NOT NULL COMMENT '事件处理时间，无符号整型',
  `count` int(11) NOT NULL COMMENT '事件发生次数，11位整数',
  `created_at` datetime NOT NULL COMMENT '事件创建时间，日期时间类型',
  `updated_at` datetime NOT NULL COMMENT '事件更新时间，日期时间类型',
  `end_at` datetime DEFAULT NULL COMMENT '事件结束时间，日期时间类型',
  `status` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT 'INIT' COMMENT '事件状态，默认为 INIT，字符串类型',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for sentinel_issues
-- ----------------------------
DROP TABLE IF EXISTS `sentinel_issues`;
CREATE TABLE `sentinel_issues` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `issue_id` varchar(255) NOT NULL COMMENT '哨兵issue id',
  `issue_type` varchar(255) NOT NULL COMMENT '问题类型',
  `title` varchar(255) NOT NULL COMMENT '标题',
  `assigned_to` varchar(255) NOT NULL COMMENT '处理人',
  `date` date NOT NULL COMMENT '日期',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime NOT NULL COMMENT '结束时间',
  `handling_time` int(11) NOT NULL COMMENT '规定处理时间（秒）',
  `total_time` int(11) NOT NULL COMMENT '总耗时',
  `raw_data` text NOT NULL COMMENT '保存原始数据',
  `comment` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `issue_id_UNIQUE` (`issue_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='哨兵问题记录表';

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------
-- Table structure for hosts
-- ----------------------------
DROP TABLE IF EXISTS `hosts`;
CREATE TABLE hosts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    hostname VARCHAR(64)  NOT NULL DEFAULT ''  COMMENT '主机名',
    ip_address VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'IP地址',
    mac_address VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'MAC地址',
    tags VARCHAR(64) NOT NULL DEFAULT '' COMMENT '标签',
    token VARCHAR(64) NOT NULL DEFAULT '' COMMENT '主机token',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ssh_status TINYINT NOT NULL DEFAULT 0 COMMENT 'ssh状态，0：未激活，1：已激活',
    UNIQUE KEY `hostname` (`hostname`),
    UNIQUE KEY `mac_address` (`mac_address`),
    UNIQUE KEY `token` (`token`)
);
