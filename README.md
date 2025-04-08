# 剑桥词典数据采集与导入系统

本项目是一个完整的剑桥词典数据采集与导入系统，包含两个主要模块：
1. 数据采集模块：用于抓取剑桥词典的多语言数据（支持英文-中文、英文-越南语等多种语言）
2. 数据导入模块：用于将采集的数据导入到数据库

## 项目特点

### 数据采集模块
- 基于 Scrapy 框架开发，提供高性能的异步爬虫能力
- 支持多语言版本（通过start_url参数配置）
- 自动处理词性映射
- 支持断点续传
- 自动处理异常情况
- 支持自定义起始URL
- 支持多种词典类型（如英汉、英越等）

### 数据导入模块
- 支持批量处理数据，提高性能
- 自动处理词性映射
- 保持数据关联关系
- 支持断点续传

## 项目结构

```
.
├── cambridge_dict/          # 数据采集模块
│   ├── scrapy.cfg          # Scrapy 配置文件
│   ├── cambridge_dict/     # 项目主目录
│   │   ├── items.py       # 数据模型定义
│   │   ├── middlewares.py # 中间件
│   │   ├── pipelines.py   # 数据处理管道
│   │   ├── settings.py    # 项目设置
│   │   ├── utils/         # 工具类
│   │   └── spiders/       # 爬虫实现
│   │       ├── cambridge.py    # 英文-中文爬虫
│   │       └── cambridge_vi.py # 英文-越南语爬虫
│   └── data/              # 数据存储目录
│
└── dict_data_importer/    # 数据导入模块
    ├── data_importer/     # 数据导入实现
    └── requirements.txt   # 依赖包列表
```

## 安装与部署

### 1. 安装依赖

```bash
# 数据采集模块依赖
cd cambridge_dict
pip install -r requirements.txt

# 数据导入模块依赖
cd ../dict_data_importer
pip install -r requirements.txt
```

### 2. 部署说明

#### 方法一：直接上传目录
```bash
# 1. 将代码上传到服务器
scp -r ./ root@your-server:/app/english-spiders/

# 2. SSH 登录到服务器
ssh root@your-server

# 3. 进入项目目录
cd /app/english-spiders/cambridge_dict

# 4. 给部署脚本添加执行权限
chmod +x deploy.sh

# 5. 执行部署脚本
./deploy.sh
```

#### 方法二：压缩后上传（推荐）
```bash
# 1. 在本地压缩项目
tar -czf english-spiders.tar.gz ./

# 2. 上传压缩包
scp english-spiders.tar.gz root@your-server:/app/

# 3. SSH到服务器
ssh root@your-server

# 4. 进入目标目录并解压
cd /app/
tar -xzf english-spiders.tar.gz

# 5. 进入项目目录
cd english-spiders/cambridge_dict

# 6. 给部署脚本添加执行权限
chmod +x deploy.sh

# 7. 执行部署脚本
./deploy.sh
```

## 使用方法

### 1. 数据采集

```bash
# 前台运行
cd cambridge_dict
# 英文-中文词典
scrapy crawl cambridge -a start_url="https://dictionary.cambridge.org/browse/english-chinese-simplified/"
# 英文-越南语词典
scrapy crawl cambridge -a start_url="https://dictionary.cambridge.org/browse/english-vietnamese/"
# 其他语言词典（根据实际URL配置）
scrapy crawl cambridge -a start_url="https://dictionary.cambridge.org/browse/english-{language}/"

# 后台运行
nohup scrapy crawl cambridge -a start_url="https://dictionary.cambridge.org/browse/english-chinese-simplified/" > spider.log 2>&1 &
```

支持的词典类型（示例）：
- 英文-中文简体：`english-chinese-simplified`
- 英文-中文繁体：`english-chinese-traditional`
- 英文-越南语：`english-vietnamese`
- 英文-韩语：`english-korean`
- 英文-日语：`english-japanese`
- 英文-法语：`english-french`
- 英文-德语：`english-german`
- 英文-西班牙语：`english-spanish`
- 英文-葡萄牙语：`english-portuguese`
- 英文-俄语：`english-russian`
- 英文-阿拉伯语：`english-arabic`
- 英文-意大利语：`english-italian`

### 2. 数据导入

```bash
# 前台运行
cd dict_data_importer
python3 data_importer/main.py <JSON文件或目录路径> --dict-uuid <词典UUID>

# 后台运行
nohup python3 data_importer/main.py <JSON文件或目录路径> --dict-uuid <词典UUID> > data_importer.log 2>&1 &
```

## 监控与维护

### 数据采集监控
```bash
# 查看爬虫日志
tail -f cambridge_dict/logs/spider.log

# 检查爬虫进程
ps aux | grep scrapy
```

### 数据导入监控
```bash
# 查看导入日志
tail -f dict_data_importer/data_importer.log
```

## 技术支持

如有问题，请联系项目维护人员。 