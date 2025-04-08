import json
import os
from datetime import datetime

class SpiderState:
    def __init__(self, state_dir='spider_state'):
        self.state_dir = state_dir
        self.url_state_file = os.path.join(state_dir, 'failed_urls.json')
        self.progress_file = os.path.join(state_dir, 'progress.json')
        self._ensure_state_dir()
        self._load_state()

    def _ensure_state_dir(self):
        """确保状态目录存在"""
        # 确保父目录存在
        parent_dir = os.path.dirname(self.state_dir)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
            
        # 确保状态目录存在
        if not os.path.exists(self.state_dir):
            os.makedirs(self.state_dir)

    def _load_state(self):
        """加载状态数据"""
        # 加载失败URL状态
        if os.path.exists(self.url_state_file):
            with open(self.url_state_file, 'r', encoding='utf-8') as f:
                self.url_state = json.load(f)
        else:
            self.url_state = {
                'first_level': {},
                'second_level': {},
                'word_level': {}
            }

        # 加载进度信息
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'total_words': 0,
                'processed_words': 0,
                'current_letter': None,
                'start_time': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            }

    def save_state(self):
        """保存状态数据"""
        with open(self.url_state_file, 'w', encoding='utf-8') as f:
            json.dump(self.url_state, f, ensure_ascii=False, indent=2)

        self.progress['last_update'] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def mark_url_status(self, url, level, status='success', retry_count=0):
        """标记URL状态，只记录失败状态"""
        state_dict = self.url_state[f'{level}_level']
        
        if status == 'success':
            # 如果请求成功，删除之前的失败记录（如果存在）
            if url in state_dict:
                del state_dict[url]
        else:
            # 只记录失败状态
            state_dict[url] = {
                'status': status,
                'retry_count': retry_count,
                'last_update': datetime.now().isoformat()
            }
        
        # 只有状态发生变化时才保存
        self.save_state()

    def get_url_status(self, url, level):
        """获取URL状态，如果没有记录说明成功或未访问"""
        return self.url_state[f'{level}_level'].get(url, {})

    def update_progress(self, letter=None, processed_words=None, total_words=None):
        """更新进度信息"""
        if letter:
            self.progress['current_letter'] = letter
        if processed_words is not None:
            self.progress['processed_words'] = processed_words
        if total_words is not None:
            self.progress['total_words'] = total_words
        self.save_state()

    def get_progress(self):
        """获取进度信息"""
        return self.progress 