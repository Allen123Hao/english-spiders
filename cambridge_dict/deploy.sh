#!/bin/bash

# 确保在脚本所在目录下执行
cd "$(dirname "$0")"
echo "当前工作目录: $(pwd)"

# 安装依赖
pip3 install -r requirements.txt

# 创建日志目录
mkdir -p logs
mkdir -p spider_state/v3

# 设置 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 获取命令行参数
START_URL=${1:-"https://dictionary.cambridge.org/browse/english-chinese-simplified/"}

# 运行爬虫（不指定起始URL）
# nohup python3 -m scrapy crawl dictionary_3 > logs/spider.log 2>&1 &
# 运行爬虫（指定起始URL）
nohup python3 -m scrapy crawl dictionary_3 -a start_url="$START_URL" > logs/spider.log 2>&1 &

echo "爬虫已在后台启动，日志文件位于 logs/spider.log"
echo "使用的起始URL: $START_URL" 