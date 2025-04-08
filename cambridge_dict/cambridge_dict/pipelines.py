# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import os
from scrapy.exceptions import DropItem


class DictionaryValidationPipeline:
    """数据验证 Pipeline"""
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if not adapter.get('word'):
            raise DropItem(f"Missing word in {item}")
        if not adapter.get('letter'):
            raise DropItem(f"Missing letter in {item}")
        return item

class DictionaryPipeline:
    """数据存储 Pipeline"""
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.files = {}
        self.stats = {
            'total_items': 0,
            'items_by_letter': {}
        }

    @classmethod
    def from_crawler(cls, crawler):
        # 根据爬虫名称选择不同的配置
        if crawler.spider.name == 'dictionary_vi_4':
            data_dir = crawler.settings.get('CAMBRIDGE_DICT_VI', {}).get('DATA_DIR', 'data/v4')
        else:
            data_dir = crawler.settings.get('CAMBRIDGE_DICT', {}).get('DATA_DIR', 'data/v3')
        return cls(data_dir=data_dir)

    def open_spider(self, spider):
        """爬虫启动时确保目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def process_item(self, item, spider):
        """处理单个数据项"""
        self.stats['total_items'] += 1
        
        adapter = ItemAdapter(item)
        letter = adapter['letter']
        
        # 更新统计信息
        if letter not in self.stats['items_by_letter']:
            self.stats['items_by_letter'][letter] = 0
        self.stats['items_by_letter'][letter] += 1
        
        # 准备文件路径
        file_path = os.path.join(self.data_dir, f"{letter}.json")
        
        # 懒加载文件数据
        if file_path not in self.files:
            self.files[file_path] = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        self.files[file_path] = json.load(f)
                    except json.JSONDecodeError:
                        spider.logger.error(f"Error reading {file_path}")

        # 添加新数据
        self.files[file_path].append(adapter.asdict())
        
        # 定期保存数据（每100个词条保存一次）
        if self.stats['total_items'] % 100 == 0:
            self._save_file(file_path)
            
        return item

    def _save_file(self, file_path):
        """保存数据到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.files[file_path], f, ensure_ascii=False, indent=2)

    def close_spider(self, spider):
        """爬虫关闭时的清理工作"""
        # 保存所有未保存的数据
        for file_path in self.files:
            self._save_file(file_path)
            
        # 保存统计信息
        stats_file = os.path.join(self.data_dir, 'stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
