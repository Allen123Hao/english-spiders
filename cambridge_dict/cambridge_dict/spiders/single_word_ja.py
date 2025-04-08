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

class SingleWordSpider4Ja(scrapy.Spider):
    """单词爬虫 - 用于抓取指定单词的数据"""
    name = 'single_word_ja'
    allowed_domains = ['dictionary.cambridge.org']
    
    def __init__(self, word_url=None, word=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.word_url = word_url
        self.word = word
        self.logger.info("Single word spider initialized")

    def start_requests(self):
        """开始请求"""
        if not self.word_url:
            self.logger.error("No word URL provided")
            return
            
        yield scrapy.Request(
            url=self.word_url,
            callback=self.parse_word_details,
            errback=self.errback_httpbin,
            meta={'letter': self.word_url.split('/')[-1][0].lower()},  # 从URL中的单词提取首字母并转为小写
            dont_filter=True
        )

    def parse_word_details(self, response):
        """解析单词详情页"""
        letter = response.meta['letter']
        # 从页面标题获取单词作为后备
        title_word = response.xpath('//div[contains(@class, "di-title")]//span[contains(@class, "hw")]/text() | //div[contains(@class, "di-title")]/text() | //div[contains(@class, "di-title")]//b/text()').get('').strip()
        
        # 获取所有可能的内容块
        pos_blocks = []
        
        # 获取普通词条内容
        entry_blocks = response.xpath('//div[contains(@class, "entry-body")]//div[contains(@class, "entry-body__el")]')
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
            block_word = ''.join(pos_block.xpath('.//div[contains(@class, "di-title")]//span[contains(@class, "hw")]/text() | .//div[contains(@class, "di-title")]//b//text()').getall()).strip()
            word = block_word if block_word else title_word
            
            # 为每个pos_block创建新的DictionaryItem实例
            item = DictionaryItem()
            item['word'] = word
            item['url'] = response.url
            item['letter'] = letter
            
            self._parse_pos_block(item, pos_block, response.url)
            items.append(item)
            
        # 返回所有解析到的items
        return items

    def _parse_pos_block(self, item, pos_block, url):
        """解析词性块"""
        item['part_of_speech'] = self._clean_text(pos_block.xpath('.//div[contains(@class, "posgram")]//span[contains(@class, "pos")]/text()').get(''))
        
        # 解析发音
        self._parse_pronunciation(item, pos_block, url)
        
        # 解析词义
        item['senses'] = self._parse_senses(pos_block)
        
        # 解析短语动词和习语
        self._parse_phrases(item, pos_block, url)

    def _parse_pronunciation(self, item, pos_block, url):
        """解析发音信息"""
        # 英式发音
        uk_pron = ''.join(pos_block.xpath('.//span[contains(@class, "uk dpron-i")]//span[contains(@class, "ipa")]/text()').getall()).strip()
        uk_mp3 = pos_block.xpath('.//span[contains(@class, "uk dpron-i")]//source[@type="audio/mpeg"]/@src').get('')
        if uk_pron:
            item['uk_pronunciation'] = PronunciationItem(
                pron=f"/{uk_pron}/",
                audio_url=urljoin(url, uk_mp3) if uk_mp3 else None
            )

        # 美式发音
        us_pron = ''.join(pos_block.xpath('.//span[contains(@class, "us dpron-i")]//span[contains(@class, "ipa")]/text()').getall()).strip()
        us_mp3 = pos_block.xpath('.//span[contains(@class, "us dpron-i")]//source[@type="audio/mpeg"]/@src').get('')
        if us_pron:
            item['us_pronunciation'] = PronunciationItem(
                pron=f"/{us_pron}/",
                audio_url=urljoin(url, us_mp3) if us_mp3 else None
            )

    def _parse_senses(self, pos_block):
        """解析词义信息"""
        senses = []
        for sense_block in pos_block.xpath('.//div[contains(@class, "def-block")]'):
            sense = SenseItem()
            
            # 获取指导词
            guide_word = self._clean_text(sense_block.xpath(
                './/ancestor::div[contains(@class, "pr dsense")]/h3[contains(@class, "dsense_h")]'
                '/span[contains(@class, "guideword dsense_gw")]/span/text()'
            ).get(''))
            if guide_word:
                sense['guide_word'] = guide_word.strip('()').strip()
            
            # 获取定义
            definitions = []
            def_parts = sense_block.xpath('.//div[contains(@class, "ddef_d")]//text()').getall()
            def_text = ' '.join([text.strip() for text in def_parts if text.strip()])
            # if def_text:
            definition = DefinitionItem(
                definition=def_text,
                def_translation=self._clean_text(''.join(
                    sense_block.xpath(
                        './/div[@class="def-body ddef_b"]//span[contains(@class, "dtrans-se") and not(contains(@class, "hdb"))]//text()').getall()
                )),
                level=self._clean_text(sense_block.xpath('.//span[contains(@class, "epp-xref")]/text()').get('')),
                attribute=self._clean_text(''.join(
                    sense_block.xpath(
                        './/div[contains(@class, "ddef_h")]//span[contains(@class, "gram dgram")]/a//text()').getall()
                )),
                examples=[]
            )

            # 获取例句
            for example in sense_block.xpath('.//div[contains(@class, "examp")]'):
                ex = ExampleItem(
                    text=self._clean_text(''.join(example.xpath('.//span[contains(@class, "eg")]//text()').getall())),
                    translation=self._clean_text(example.xpath('.//span[contains(@class, "trans")]/text()').get(''))
                )
                if ex['text'] or ex['translation']:
                    definition['examples'].append(dict(ex))

            definitions.append(dict(definition))
            
            if definitions:
                sense['definitions'] = definitions
                
            # 获取更多例句
            more_examples = []
            for more_example in sense_block.xpath('.//following-sibling::div[contains(@class, "daccord")][1]//ul[contains(@class, "hul-u")]//li'):
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

    def errback_httpbin(self, failure):
        """处理请求错误"""
        url = failure.request.url
        self.logger.error(f'Request failed: {url}')

if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    
    # 获取项目设置
    settings = get_project_settings()
    
    # 调试时的自定义设置
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': 'single_word_spider_debug_0.log',
        'LOG_ENABLED': True,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': True,
        'PYTHONPATH': project_root,
        'ITEM_PIPELINES': {
            'cambridge_dict.pipelines.DictionaryValidationPipeline': 100,
            'cambridge_dict.pipelines.DictionaryPipeline': 300,
        },
        # 设置输出
        'FEEDS': {
            'output/%(word)s.json': {
                'format': 'json',
                'encoding': 'utf-8',
                'indent': 2,
                'overwrite': True,
            },
        },
    }
    settings.update(custom_settings)
    
    try:
        # 确保输出目录存在
        os.makedirs('output', exist_ok=True)
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        # 启动爬虫（需要提供word_url参数）
        word_url = "https://dictionary.cambridge.org/us/dictionary/english-japanese/bank-on"  # 示例URL
        # word_url = "https://dictionary.cambridge.org/us/dictionary/english-japanese/repeatedly"
        word = word_url.split('/')[-1]  # 从URL中提取单词
        
        print(f"启动爬虫，单词: {word}, URL: {word_url}")
        process.crawl(SingleWordSpider4Ja, word_url=word_url, word=word)
        process.start()
    except KeyboardInterrupt:
        print("\n手动停止爬虫")
        sys.exit(0)
    except Exception as e:
        print(f"爬虫运行出错: {str(e)}")
        sys.exit(1) 