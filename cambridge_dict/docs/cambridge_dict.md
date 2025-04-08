剑桥词典数据存储
==============

## 1. 背景目标

刺猬英语应用程序最初使用有道词典作为单词释义和翻译的数据源。随着我们进行国际化战略的推进，需要更加权威、正规的词典数据源来支持全球用户的使用需求。经过评估，我们选择了剑桥词典（Cambridge Dictionary）作为新的数据源，原因如下：

- **国际权威性**：剑桥词典是全球公认的权威英语词典，由剑桥大学出版社出版，具有较高的学术和教育价值
- **多语言支持**：提供英语到多种语言的翻译，有利于我们的国际化战略
- **详细的语言级别**：标注了词汇的CEFR语言级别（如A1、B2、C1等），便于教育应用中的词汇分级
- **丰富的语言信息**：包含发音、词性、例句、用法说明等全面的语言资源

本项目的目标是：
1. 通过爬虫获取剑桥词典英语-简体中文版的数据
2. 设计合适的数据存储结构，支持高效的词典查询和全文搜索
3. 为刺猬英语应用提供API接口，支持单词查询、例句获取、语音播放等功能
4. 为未来扩展到其他语言版本的词典做好准备

## 2. 爬虫数据

我们使用Scrapy框架开发了爬虫，从剑桥词典官网抓取英语-简体中文版的词典数据。爬虫从字母索引页开始，逐层深入到具体单词页面，提取所需信息。

### 2.1 数据示例

以下是爬虫获取的数据示例（data.json格式）：

```json
[
    {
        "url": "https://dictionary.cambridge.org/dictionary/english-chinese-simplified/b-and-b",
        "data":
        [
            {
                "word": "B and B",
                "part_of_speech": "noun",
                "uk_pronunciation":
                {
                    "pron": "/ˌbiː en ˈbiː/",
                    "audio_url": "https://dictionary.cambridge.org/media/english-chinese-simplified/uk_pron/e/epd/epd02/epd02729.mp3"
                },
                "us_pronunciation":
                {
                    "pron": "/ˌbiː en ˈbiː/",
                    "audio_url": "https://dictionary.cambridge.org/media/english-chinese-simplified/us_pron/e/eus/eus02/eus02658.mp3"
                },
                "senses":
                [
                    {
                        "definitions":
                        [
                            {
                                "definition": "abbreviation for bed and breakfast",
                                "def_translation": "（私人住宅或小旅馆提供的）住宿和早餐（bed and breakfast的缩写）",
                                "level": "",
                                "attribute": "",
                                "examples":
                                []
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        "url": "https://dictionary.cambridge.org/dictionary/english-chinese-simplified/b",
        "data":
        [
            {
                "word": "B, b",
                "part_of_speech": "noun",
                "uk_pronunciation":
                {
                    "pron": "/biː/",
                    "audio_url": "https://dictionary.cambridge.org/media/english-chinese-simplified/uk_pron/u/uka/ukazt/ukazt__003.mp3"
                },
                "us_pronunciation":
                {
                    "pron": "/biː/",
                    "audio_url": "https://dictionary.cambridge.org/media/english-chinese-simplified/us_pron/b/b__/b____/b.mp3"
                },
                "senses":
                [
                    {
                        "guide_word": "LETTER",
                        "definitions":
                        [
                            {
                                "definition": "the second letter of the English alphabet",
                                "def_translation": "（英语字母表的第二个字母）",
                                "level": "",
                                "attribute": "[ C or U ]",
                                "examples":
                                []
                            }
                        ]
                    },
                    {
                        "guide_word": "MUSIC",
                        "definitions":
                        [
                            {
                                "definition": "a note in Western music",
                                "def_translation": "B 调，B 音",
                                "level": "",
                                "attribute": "[ C or U ]",
                                "examples":
                                [
                                    {
                                        "text": "Bach's Mass in B minor",
                                        "translation": "巴赫B小调弥撒曲"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "guide_word": "MARK",
                        "definitions":
                        [
                            {
                                "definition": "a mark in an exam or for a piece of work that shows that your work is good but not excellent",
                                "def_translation": "（学业成绩、工作表现的）良好，第二等",
                                "level": "",
                                "attribute": "[ C or U ]",
                                "examples":
                                [
                                    {
                                        "text": "I was a little disappointed just to be given a B, as I was hoping for an A.",
                                        "translation": "得了"良好"我感到有点沮丧，我一直希望得"优秀"。"
                                    },
                                    {
                                        "text": "I got B for physics last term.",
                                        "translation": "上学期我的物理成绩得了"良好"。"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "word": "B, b",
                "part_of_speech": "",
                "senses":
                [
                    {
                        "definitions":
                        [
                            {
                                "definition": "written abbreviation for billion",
                                "def_translation": "十亿（billion的缩写）",
                                "level": "",
                                "attribute": "",
                                "examples":
                                []
                            }
                        ]
                    }
                ]
            },
            {
                "word": "b.",
                "part_of_speech": "",
                "senses":
                [
                    {
                        "definitions":
                        [
                            {
                                "definition": "written abbreviation for born",
                                "def_translation": "出生（born的缩写）",
                                "level": "",
                                "attribute": "",
                                "examples":
                                [
                                    {
                                        "text": "John Winston Lennon (b. 9 October 1940, Liverpool, d. 8 December 1980, New York).",
                                        "translation": "约翰‧温斯顿‧列侬（1940年10月9日生于利物浦，1980年12月8日卒于纽约）"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
]
```

### 2.2 数据字段说明

爬虫获取的数据包含以下主要字段：

- **url**: 单词在剑桥词典网站上的URL
- **data**: 包含单词详细信息的数组，可能包含同形异义词
  - **word**: 单词本身
  - **part_of_speech**: 词性（noun、verb、adjective等）
  - **uk_pronunciation**: 英式发音信息
    - **pron**: 音标
    - **audio_url**: 音频文件URL
  - **us_pronunciation**: 美式发音信息
    - **pron**: 音标
    - **audio_url**: 音频文件URL
  - **senses**: 词义数组
    - **guide_word**: 指导词，用于区分不同语境下的词义
    - **definitions**: 定义数组
      - **definition**: 英文定义
      - **def_translation**: 中文翻译
      - **level**: CEFR语言级别（A1、A2、B1、B2、C1、C2）
      - **attribute**: 附加属性（如可数/不可数）
      - **examples**: 例句数组
        - **text**: 例句英文
        - **translation**: 例句中文翻译

## 3. 数据结构设计

为了高效存储和查询剑桥词典数据，我们采用了混合存储方案：MySQL作为主数据存储，Elasticsearch作为全文搜索引擎。这种方案结合了关系型数据库的事务管理能力和Elasticsearch的高级搜索功能。

### 3.1 MySQL数据结构

MySQL用于存储规范化的词典数据，作为系统的主要数据源。

#### 3.1.1 表结构设计

```sql
-- 词典类型表
CREATE TABLE dictionary_types (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,  -- 如 'english-chinese-simplified', 'english-chinese-traditional'
    description VARCHAR(255),
    UNIQUE(name)
);

-- 单词表
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    word VARCHAR(100) NOT NULL,  -- 单词本身
    url VARCHAR(255),  -- 词条URL
    dictionary_type_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dictionary_type_id) REFERENCES dictionary_types(id),
    UNIQUE(word, dictionary_type_id)
);

-- 词条表
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    word_id INTEGER NOT NULL,
    part_of_speech VARCHAR(50),  -- 词性
    uk_pronunciation VARCHAR(100),  -- 英式音标
    uk_audio_url VARCHAR(255),  -- 英式发音URL
    us_pronunciation VARCHAR(100),  -- 美式音标
    us_audio_url VARCHAR(255),  -- 美式发音URL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id),
    INDEX idx_word_id (word_id),
    INDEX idx_part_of_speech (part_of_speech)
);

-- 词义表
CREATE TABLE senses (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    entry_id INTEGER NOT NULL,
    guide_word VARCHAR(100),  -- 引导词，如 'LETTER', 'MUSIC'
    definition TEXT NOT NULL,  -- 英文定义
    translation TEXT,  -- 翻译
    level VARCHAR(50),  -- 级别，如 'B1', 'C2'
    attribute VARCHAR(100),  -- 属性，如 '[ C or U ]'
    sense_order INTEGER NOT NULL DEFAULT 0,  -- 词义顺序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES entries(id),
    INDEX idx_entry_id (entry_id),
    INDEX idx_level (level)
);

-- 例句表
CREATE TABLE examples (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    sense_id INTEGER NOT NULL,
    text TEXT NOT NULL,  -- 例句
    translation TEXT,  -- 例句翻译
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sense_id) REFERENCES senses(id),
    INDEX idx_sense_id (sense_id),
    FULLTEXT INDEX ft_example (text, translation)
);

-- 全文搜索索引
ALTER TABLE words ADD FULLTEXT INDEX ft_word (word);
ALTER TABLE senses ADD FULLTEXT INDEX ft_definition (definition, translation);

-- 视图：完整词条信息（方便查询）
CREATE VIEW word_complete_view AS
SELECT 
    w.id AS word_id,
    w.word,
    w.url,
    dt.name AS dictionary_type,
    e.id AS entry_id,
    e.part_of_speech,
    e.uk_pronunciation,
    e.uk_audio_url,
    e.us_pronunciation,
    e.us_audio_url,
    s.id AS sense_id,
    s.guide_word,
    s.definition,
    s.translation,
    s.level,
    s.attribute,
    s.sense_order
FROM words w
JOIN dictionary_types dt ON w.dictionary_type_id = dt.id
JOIN entries e ON w.id = e.word_id
JOIN senses s ON e.id = s.entry_id
ORDER BY w.word, e.part_of_speech, s.sense_order;
```

#### 3.1.2 数据插入示例

以下是将爬虫数据插入到MySQL数据库的示例：

```sql
-- 示例：插入单词 "B and B"
START TRANSACTION;

-- 1. 插入词典类型（如果尚未存在）
INSERT INTO dictionary_types (name, description) 
VALUES ('english-chinese-simplified', '英语-简体中文词典')
ON DUPLICATE KEY UPDATE description = '英语-简体中文词典';

-- 2. 插入单词
INSERT INTO words (word, url, dictionary_type_id) 
VALUES ('B and B', 'https://dictionary.cambridge.org/dictionary/english-chinese-simplified/b-and-b', 
        (SELECT id FROM dictionary_types WHERE name = 'english-chinese-simplified'));
SET @word_id = LAST_INSERT_ID();

-- 3. 插入词条
INSERT INTO entries (word_id, part_of_speech, uk_pronunciation, uk_audio_url, us_pronunciation, us_audio_url) 
VALUES (@word_id, 'noun', '/ˌbiː en ˈbiː/', 
        'https://dictionary.cambridge.org/media/english-chinese-simplified/uk_pron/e/epd/epd02/epd02729.mp3',
        '/ˌbiː en ˈbiː/', 
        'https://dictionary.cambridge.org/media/english-chinese-simplified/us_pron/e/eus/eus02/eus02658.mp3');
SET @entry_id = LAST_INSERT_ID();

-- 4. 插入词义
INSERT INTO senses (entry_id, guide_word, definition, translation, level, attribute, sense_order) 
VALUES (@entry_id, NULL, 'abbreviation for bed and breakfast', 
        '（私人住宅或小旅馆提供的）住宿和早餐（bed and breakfast的缩写）', '', '', 1);

COMMIT;
```

### 3.2 Elasticsearch数据结构

Elasticsearch用于提供高性能的全文搜索功能，支持复杂的词典搜索需求。

#### 3.2.1 索引映射设计

```json
{
  "settings": {
    "analysis": {
      "analyzer": {
        "english_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "english_stop", "english_stemmer"]
        },
        "chinese_analyzer": {
          "type": "custom",
          "tokenizer": "smartcn_tokenizer",
          "filter": ["lowercase"]
        }
      },
      "filter": {
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        }
      }
    },
    "number_of_shards": 3,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "word": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          },
          "english": {
            "type": "text",
            "analyzer": "english_analyzer"
          }
        }
      },
      "url": {
        "type": "keyword"
      },
      "dictionary_type": {
        "type": "keyword"
      },
      "entries": {
        "type": "nested",
        "properties": {
          "part_of_speech": {
            "type": "keyword"
          },
          "uk_pronunciation": {
            "type": "text"
          },
          "uk_audio_url": {
            "type": "keyword"
          },
          "us_pronunciation": {
            "type": "text"
          },
          "us_audio_url": {
            "type": "keyword"
          },
          "senses": {
            "type": "nested",
            "properties": {
              "guide_word": {
                "type": "text"
              },
              "definition": {
                "type": "text",
                "analyzer": "english_analyzer",
                "fields": {
                  "keyword": {
                    "type": "keyword"
                  }
                }
              },
              "translation": {
                "type": "text",
                "analyzer": "chinese_analyzer",
                "fields": {
                  "keyword": {
                    "type": "keyword"
                  }
                }
              },
              "level": {
                "type": "keyword"
              },
              "attribute": {
                "type": "keyword"
              },
              "sense_order": {
                "type": "integer"
              },
              "examples": {
                "type": "nested",
                "properties": {
                  "text": {
                    "type": "text",
                    "analyzer": "english_analyzer"
                  },
                  "translation": {
                    "type": "text",
                    "analyzer": "chinese_analyzer"
                  }
                }
              }
            }
          }
        }
      },
      "suggestField": {
        "type": "completion",
        "analyzer": "english_analyzer"
      },
      "created_at": {
        "type": "date"
      },
      "updated_at": {
        "type": "date"
      }
    }
  }
}
```

#### 3.2.2 文档示例

```json
{
  "word": "B and B",
  "url": "https://dictionary.cambridge.org/dictionary/english-chinese-simplified/b-and-b",
  "dictionary_type": "english-chinese-simplified",
  "entries": [
    {
      "part_of_speech": "noun",
      "uk_pronunciation": "/ˌbiː en ˈbiː/",
      "uk_audio_url": "https://dictionary.cambridge.org/media/english-chinese-simplified/uk_pron/e/epd/epd02/epd02729.mp3",
      "us_pronunciation": "/ˌbiː en ˈbiː/",
      "us_audio_url": "https://dictionary.cambridge.org/media/english-chinese-simplified/us_pron/e/eus/eus02/eus02658.mp3",
      "senses": [
        {
          "guide_word": null,
          "definition": "abbreviation for bed and breakfast",
          "translation": "（私人住宅或小旅馆提供的）住宿和早餐（bed and breakfast的缩写）",
          "level": "",
          "attribute": "",
          "sense_order": 1,
          "examples": []
        }
      ]
    }
  ],
  "suggestField": {
    "input": ["B and B", "B & B", "bed and breakfast"]
  },
  "created_at": "2023-09-15T12:00:00Z",
  "updated_at": "2023-09-15T12:00:00Z"
}
```

#### 3.2.3 查询示例

精确查询单词：
```json
GET /cambridge_dictionary/_search
{
  "query": {
    "match": {
      "word.keyword": "B and B"
    }
  }
}
```

按语言级别查询词汇：
```json
GET /cambridge_dictionary/_search
{
  "query": {
    "nested": {
      "path": "entries.senses",
      "query": {
        "term": { "entries.senses.level": "B1" }
      }
    }
  }
}
```

全文搜索定义和例句：
```json
GET /cambridge_dictionary/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "nested": {
            "path": "entries.senses",
            "query": {
              "match": { "entries.senses.definition": "abbreviation" }
            },
            "score_mode": "avg"
          }
        },
        {
          "nested": {
            "path": "entries.senses.examples",
            "query": {
              "match": { "entries.senses.examples.text": "abbreviation" }
            },
            "score_mode": "avg"
          }
        }
      ]
    }
  }
}
```

### 3.3 数据同步策略

为了保持MySQL和Elasticsearch数据的一致性，我们采用以下同步策略：

1. **初始加载**：将MySQL中的所有词典数据批量导入到Elasticsearch
2. **增量同步**：
   - 使用MySQL的binlog捕获数据变更
   - 通过Logstash或自定义同步程序将变更实时同步到Elasticsearch
3. **定期全量同步**：每周进行一次全量数据同步，确保数据完全一致

### 3.4 数据访问层设计

我们为应用程序提供统一的数据访问层，屏蔽底层存储细节：

1. **基本词典查询**：直接使用MySQL数据
   - 精确查词
   - 获取单词发音
   - 获取词义和例句

2. **高级搜索功能**：使用Elasticsearch
   - 模糊搜索
   - 全文搜索
   - 按级别筛选
   - 自动补全

3. **缓存策略**：
   - 使用Redis缓存热门词条
   - 对Elasticsearch查询结果进行缓存
   - 为音频URL设置CDN加速

## 4. 性能与扩展性考虑

### 4.1 性能优化

1. **索引优化**：
   - MySQL中对常用查询字段建立索引
   - Elasticsearch中优化分片数量和副本策略

2. **查询优化**：
   - 使用预编译查询
   - 对复杂查询进行缓存
   - 使用分页减少返回数据量

3. **硬件资源**：
   - MySQL和Elasticsearch部署在独立服务器上
   - 针对读写比例配置适当的资源

### 4.2 扩展性设计

1. **多语言扩展**：
   - 数据结构已考虑多语言支持
   - 只需添加新的dictionary_type记录即可支持新语言

2. **水平扩展**：
   - MySQL可使用读写分离和分库分表
   - Elasticsearch天然支持集群扩展

3. **功能扩展**：
   - 预留了level字段支持词汇分级
   - 可扩展支持专业领域词汇标记

## 5. 部署与监控

### 5.1 部署架构

1. **生产环境**：
   - 主MySQL服务器 + 读副本
   - 3节点Elasticsearch集群
   - Redis缓存集群
   - 应用服务器集群

2. **测试环境**：
   - 单节点MySQL
   - 单节点Elasticsearch
   - 应用服务器

### 5.2 监控与告警

1. **数据库监控**：
   - 查询性能监控
   - 资源使用率监控
   - 数据同步状态监控

2. **应用监控**：
   - API响应时间
   - 错误率统计
   - 用户查询模式分析

## 6. 结论与后续计划

剑桥词典数据存储方案采用MySQL + Elasticsearch的混合架构，既保证了数据的完整性和事务性，又提供了强大的搜索能力。这一方案能够满足刺猬英语国际化后对权威词典数据的需求，为用户提供高质量的词典服务。

### 后续计划：

1. **扩展更多语言**：支持英语到法语、西班牙语、日语等语言的词典数据
2. **增强语义搜索**：集成更高级的NLP功能，提供语义层面的搜索能力
3. **离线词典**：支持移动端离线词典功能，提升用户体验
4. **用户个性化**：根据用户的学习历史和级别，提供个性化的词典内容