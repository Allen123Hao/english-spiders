-- 词典表
CREATE TABLE `dict` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '数据库自增id',
  `uuid` varchar(36) NOT NULL COMMENT 'uuid',
  `name` varchar(100) NOT NULL COMMENT '名称',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='字典';

-- 单词表
CREATE TABLE `dict_word` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '数据库自增id',
  `uuid` varchar(36) NOT NULL COMMENT 'uuid',
  `dict_uuid` varchar(36) NOT NULL COMMENT '词典uuid',
  `word` varchar(100) NOT NULL COMMENT '单词或短语',
  `url` varchar(255) DEFAULT NULL COMMENT '词条URL',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  UNIQUE KEY `uk_word_dict` (`word`, `dict_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='词典单词表';

-- 词条表
CREATE TABLE `dict_entry` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '数据库自增id',
  `uuid` varchar(36) NOT NULL COMMENT 'uuid',
  `word_uuid` varchar(36) NOT NULL COMMENT '单词uuid',
  `part_of_speech` varchar(50) NOT NULL DEFAULT '' COMMENT '词性',
  `uk_pronunciation` varchar(100) NOT NULL DEFAULT '' COMMENT '英式音标',
  `uk_audio_url` varchar(255) NOT NULL DEFAULT '' COMMENT '英式发音URL',
  `us_pronunciation` varchar(100) NOT NULL DEFAULT '' COMMENT '美式音标',
  `us_audio_url` varchar(255) NOT NULL DEFAULT '' COMMENT '美式发音URL',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  KEY `idx_word_uuid` (`word_uuid`),
  KEY `idx_word_pos` (`word_uuid`, `part_of_speech`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='词典词条表';

-- 词义表
CREATE TABLE `dict_sense` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '数据库自增id',
  `uuid` varchar(36) NOT NULL COMMENT 'uuid',
  `entry_uuid` varchar(36) NOT NULL COMMENT '词条uuid',
  `guide_word` varchar(100) NOT NULL DEFAULT '' COMMENT '引导词',
  `definition` varchar(1000) NOT NULL DEFAULT '' COMMENT '英文定义',
  `translation` varchar(500) NOT NULL DEFAULT '' COMMENT '翻译',
  `cefr_level` varchar(30) NOT NULL DEFAULT '' COMMENT '级别',
  `attribute` varchar(100) NOT NULL DEFAULT '' COMMENT '属性',
  `examples` json NOT NULL COMMENT '例句JSON数组',
  `more_examples` json DEFAULT NULL COMMENT '更多例句JSON数组',
  `sense_order` int NOT NULL DEFAULT 0 COMMENT '词义顺序',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  KEY `idx_entry_uuid` (`entry_uuid`),
  KEY `idx_cefr_level` (`cefr_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='词典释义表';

-- 全文搜索索引
ALTER TABLE dict_word ADD FULLTEXT INDEX ft_word (word);
ALTER TABLE dict_sense ADD FULLTEXT INDEX ft_definition (definition, translation);

-- 视图：完整词条信息
drop view if exists dict_word_complete_view;

CREATE VIEW dict_word_complete_view AS
SELECT 
    d.uuid AS dict_uuid,
    d.name AS dict_name,
    w.uuid AS word_uuid,
    w.word,
    w.url,
    e.uuid AS entry_uuid,
    e.part_of_speech,
    e.uk_pronunciation,
    e.uk_audio_url,
    e.us_pronunciation,
    e.us_audio_url,
    s.uuid AS sense_uuid,
    s.guide_word,
    s.definition,
    s.translation,
    s.cefr_level,
    s.attribute,
    s.examples,
    s.more_examples,
    s.sense_order
FROM dict_word w
JOIN dict d ON w.dict_uuid = d.uuid
JOIN dict_entry e ON w.uuid = e.word_uuid
JOIN dict_sense s ON e.uuid = s.entry_uuid
WHERE w.deleted_at IS NULL 
  AND d.deleted_at IS NULL 
  AND e.deleted_at IS NULL 
  AND s.deleted_at IS NULL
ORDER BY w.word, e.part_of_speech, s.sense_order;

-- 数据初始化
INSERT INTO dict (uuid, name, description) VALUES 
(UUID(), 'english-chinese-simplified', '英语-简体中文词典'),
(UUID(), 'english-chinese-traditional', '英语-繁体中文词典'),
(UUID(), 'english-english', '英英词典'); 