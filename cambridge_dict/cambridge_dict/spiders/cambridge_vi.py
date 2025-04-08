import scrapy
from urllib.parse import urljoin
import logging
import os
import sys

# 添加项目根目录到 Python 路径
file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from cambridge_dict.utils.spider_state import SpiderState
    from cambridge_dict.items import (
        DictionaryItem, PronunciationItem, ExampleItem,
        DefinitionItem, SenseItem, PhraseItem
    )
except ImportError:
    from ..utils.spider_state import SpiderState
    from ..items import (
        DictionaryItem, PronunciationItem, ExampleItem,
        DefinitionItem, SenseItem, PhraseItem
    )

class DictionarySpiderVi(scrapy.Spider):
    name = 'dictionary_vi'
    start_urls = ['https://dictionary.cambridge.org/browse/english-vietnamese/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化状态管理器
        from scrapy.utils.project import get_project_settings
        settings = get_project_settings()
        self.state_manager = SpiderState(
            state_dir=settings.get('CAMBRIDGE_DICT_VI', {}).get('STATE_DIR', 'spider_state/v4')
        )
        self.logger.info("Spider initialized")

    def start_requests(self):
        """开始请求，支持断点续传"""
        progress = self.state_manager.get_progress()
        current_letter = progress.get('current_letter')
        
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse_first_level,
            errback=self.errback_httpbin,
            meta={
                'dont_merge_cookies': True,
                'current_letter': current_letter
            },
            dont_filter=True
        )

    def parse_first_level(self, response):
        """解析一级页面"""
        links = response.xpath('//div[@class="hfl-s lt2b lmt-10 lmb-25 lp-s_r-20"]//ul[@class="hul-i hul-ib lm-0"]/li/a/@href').getall()
        
        # 获取当前处理的字母
        current_letter = response.meta.get('current_letter')
        
        # 如果有断点，从断点处继续
        if current_letter:
            start_index = next((i for i, link in enumerate(links) if current_letter in link), 0)
            links = links[start_index:]
        # else:
        #     links = links[:20]  # 跳过数字部分
            
        self.logger.info(f"Found {len(links)} first-level URLs")
        
        for link in links:
            letter = link.split('/')[-2]  # 获取字母
            url_status = self.state_manager.get_url_status(link, 'first')
            
            if url_status.get('status') == 'success':
                continue
                
            yield scrapy.Request(
                url=link,
                callback=self.parse_second_level,
                errback=self.errback_httpbin,
                meta={'letter': letter},
                dont_filter=True
            )

    def parse_second_level(self, response):
        """解析二级页面"""
        letter = response.meta['letter']
        self.state_manager.update_progress(letter=letter)
        
        links = response.xpath('//div[@class="hdf ff-50 lmt-15 i-browse"]//a[@class="hlh32 hdb dil tcbd"]/@href').getall()
        self.logger.info(f"Found {len(links)} second-level URLs for letter {letter}")
        
        for link in links:
            full_url = urljoin(response.url, link)
            url_status = self.state_manager.get_url_status(full_url, 'second')
            
            if url_status.get('status') == 'success':
                continue
                
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_word_links,
                errback=self.errback_httpbin,
                meta={'letter': letter},
                dont_filter=True
            )

    def parse_word_links(self, response):
        """解析单词链接列表页"""
        letter = response.meta['letter']
        word_links = response.xpath('//div[contains(@class, "hlh32 han")]/a[@class="tc-bd"]/@href').getall()
        
        for link in word_links:
            full_url = urljoin(response.url, link)
            url_status = self.state_manager.get_url_status(full_url, 'word')
            
            if url_status.get('status') == 'success':
                continue
                
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_word_details,
                errback=self.errback_httpbin,
                meta={'letter': letter},
                dont_filter=True
            )

    def parse_word_details(self, response):
        """解析单词详情页"""
        letter = response.meta['letter']
        # 从页面标题获取单词作为后备
        title_word = response.xpath('//h2[contains(@class, "di-title")]/text()').get('').strip()
        
        # 获取所有可能的内容块
        pos_blocks = []
        
        # 获取普通词条内容
        entry_blocks = response.xpath('//div[contains(@class, "entry-body")]//div[contains(@class, "english-vietnamese")]')
        if entry_blocks:
            pos_blocks.extend(entry_blocks)
            
        # 获取习语内容
        idiom_blocks = response.xpath('//div[contains(@class, "pr idiom-block")]')
        if idiom_blocks:
            pos_blocks.extend(idiom_blocks)
            
        # 获取短语内容
        phrase_blocks = response.xpath('//span[contains(@class, "phrase-di-block dphrase-di-block")]')
        if phrase_blocks:
            pos_blocks.extend(phrase_blocks)
            
        # 获取短语动词内容
        phrasal_verb_blocks = response.xpath('//div[contains(@class, "pv-block")]')
        if phrasal_verb_blocks:
            pos_blocks.extend(phrasal_verb_blocks)
            
        # 如果没有找到任何内容块，记录警告
        if not pos_blocks:
            self.logger.warning(f"No content blocks found for URL: {response.url}")
            return []
        
        # 解析词条内容
        items = []  # 创建列表存储所有items

        for pos_block in pos_blocks:
            # 尝试从pos_block获取单词，如果获取不到则使用title_word
            block_word = ''.join(pos_block.xpath('.//h2[contains(@class, "di-title")]/text()').getall()).strip()
            word = block_word if block_word else title_word
            
            # 为每个pos_block创建新的DictionaryItem实例
            item = DictionaryItem()
            item['word'] = word
            item['url'] = response.url
            item['letter'] = letter
            
            self._parse_pos_block(item, pos_block, response.url)
            items.append(item)
            
        # 更新URL状态
        self.state_manager.mark_url_status(response.url, 'word', 'success')
        
        # 更新进度
        progress = self.state_manager.get_progress()
        self.state_manager.update_progress(
            processed_words=progress['processed_words'] + 1
        )
        
        return items  # 返回所有解析到的items

    def _parse_pos_block(self, item, pos_block, url):
        """解析词性块"""
        item['part_of_speech'] = self._clean_text(pos_block.xpath('.//div[contains(@class, "dpos-g")]//span[contains(@class, "pos")]/text()').get(''))
        
        # 解析发音
        self._parse_pronunciation(item, pos_block, url)
        
        # 解析词义
        item['senses'] = self._parse_senses(pos_block)
        
        # 解析短语动词和习语
        self._parse_phrases(item, pos_block, url)

    def _parse_pronunciation(self, item, pos_block, url):
        """解析发音信息"""
        # 英式发音
        item['uk_pronunciation'] = PronunciationItem(
            pron='',
            audio_url=''
        )

        # 美式发音
        item['us_pronunciation'] = PronunciationItem(
            pron='',
            audio_url=''
        )

    def _parse_senses(self, pos_block):
        """解析词义信息"""
        senses = []
        for sense_block in pos_block.xpath('.//div[contains(@class, "sense-block")]//div[contains(@class, "sense-body")]'):
            sense = SenseItem()
            
            # 获取指导词
            sense['guide_word'] = ''
            
            # 获取定义
            definitions = []
            def_parts = sense_block.xpath('.//div[contains(@class, "ddef_h")]//div[contains(@class, "ddef_d db")]//text()').getall()
            def_text = ' '.join([text.strip() for text in def_parts if text.strip()])
            if def_text:
                definition = DefinitionItem(
                    definition=def_text,
                    def_translation=self._clean_text(''.join(
                        sense_block.xpath('.//div[contains(@class, "def-body")]//span[contains(@class, "dtrans")]/text()').getall()
                    )),
                    level='',
                    attribute='',
                    examples=[]
                )
                
                # 获取例句
                for example in sense_block.xpath('.//div[contains(@class, "def-body")]//div[contains(@class, "examp dexamp")]'):
                    ex = ExampleItem(
                        text=self._clean_text(''.join(example.xpath('.//span[contains(@class, "eg deg")]//text()').getall())),
                        translation=''
                    )
                    if ex['text'] or ex['translation']:
                        definition['examples'].append(dict(ex))
                
                definitions.append(dict(definition))
            
            if definitions:
                sense['definitions'] = definitions
                
            # 获取更多例句
            more_examples = []
            for more_example in sense_block.xpath('.//div[contains(@class, "daccord")]//div[contains(@class, "deg")]'):
                ex = ExampleItem(
                    text=self._clean_text(''.join(more_example.xpath('.//text()').getall())),
                    translation=''
                )
                if ex['text']:
                    more_examples.append(dict(ex))
            
            if more_examples:
                sense['more_examples'] = more_examples
                
            if sense.get('definitions') or sense.get('more_examples'):
                senses.append(dict(sense))
                
        return senses

    def _parse_phrases(self, item, pos_block, url):
        """解析短语动词和习语"""
        # 解析短语动词
        phrasal_verbs = []
        for phrasal_verb in pos_block.xpath('//div[contains(@class, "xref phrasal_verbs")]//div[contains(@class, "lcs")]//a'):
            pv = PhraseItem(
                text=self._clean_text(' '.join(phrasal_verb.xpath('.//text()').getall())),
                link=urljoin(url, phrasal_verb.xpath('.//@href').get(''))
            )
            if pv['text']:
                phrasal_verbs.append(dict(pv))
        if phrasal_verbs:
            item['phrasal_verbs'] = phrasal_verbs
            
        # 解析习语
        idioms = []
        for idiom in pos_block.xpath('//div[contains(@class, "xref idioms")]//div[contains(@class, "lcs")]//a'):
            id = PhraseItem(
                text=self._clean_text(' '.join(idiom.xpath('.//text()').getall())),
                link=urljoin(url, idiom.xpath('.//@href').get(''))
            )
            if id['text']:
                idioms.append(dict(id))
        if idioms:
            item['idioms'] = idioms

    def _clean_text(self, text):
        """清理文本"""
        if not text:
            return ''
        return text.strip().rstrip('，；').strip()

    def _get_level(self, url):
        """根据URL判断层级"""
        parts = url.split('/')
        if 'browse' in parts:
            return 'first'
        elif len(parts) == 8:  # 二级目录URL特征
            return 'second'
        else:
            return 'word'

    def errback_httpbin(self, failure):
        """处理请求错误"""
        url = failure.request.url
        self.logger.error(f'Request failed: {url}')
        self.state_manager.mark_url_status(
            url,
            self._get_level(url),
            'failed'
        )

# 修改 main 方法
if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    
    # 获取项目设置
    settings = get_project_settings()
    
    # 调试时的自定义设置
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': 'dictionary_spider_v4_debug.log',
        'LOG_ENABLED': True,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': True,
        'PYTHONPATH': project_root,
        # V4 特有的设置
        'ITEM_PIPELINES': {
            'cambridge_dict.pipelines.DictionaryValidationPipeline': 100,
            'cambridge_dict.pipelines.DictionaryPipeline': 300,
        },
        'SPIDER_MIDDLEWARES': {
            'cambridge_dict.middlewares.SpiderProgressMiddleware': 543,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'cambridge_dict.middlewares.CustomDownloaderMiddleware': 543,
            'cambridge_dict.middlewares.CustomRetryMiddleware': 550,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        },
    }
    settings.update(custom_settings)
    
    try:
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        # 启动爬虫
        process.crawl(DictionarySpiderVi)
        process.start()  # 阻塞，直到爬虫完成
    except KeyboardInterrupt:
        print("\n手动停止爬虫")
        sys.exit(0)
    except Exception as e:
        print(f"爬虫运行出错: {str(e)}")
        sys.exit(1) 