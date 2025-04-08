# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CambridgeDictItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class PronunciationItem(scrapy.Item):
    """发音数据结构"""
    pron = scrapy.Field()
    audio_url = scrapy.Field()

class ExampleItem(scrapy.Item):
    """例句数据结构"""
    text = scrapy.Field()
    translation = scrapy.Field()

class DefinitionItem(scrapy.Item):
    """释义数据结构"""
    definition = scrapy.Field()
    def_translation = scrapy.Field()
    level = scrapy.Field()
    attribute = scrapy.Field()
    examples = scrapy.Field(serializer=list)  # 存储 ExampleItem 列表

class SenseItem(scrapy.Item):
    """词义数据结构"""
    guide_word = scrapy.Field()
    definitions = scrapy.Field(serializer=list)  # 存储 DefinitionItem 列表
    more_examples = scrapy.Field(serializer=list)  # 存储 ExampleItem 列表

class PhraseItem(scrapy.Item):
    """短语数据结构"""
    text = scrapy.Field()
    link = scrapy.Field()

class DictionaryItem(scrapy.Item):
    """词典条目数据结构"""
    word = scrapy.Field()
    url = scrapy.Field()
    letter = scrapy.Field()  # 用于分类存储
    part_of_speech = scrapy.Field()
    uk_pronunciation = scrapy.Field()  # PronunciationItem
    us_pronunciation = scrapy.Field()  # PronunciationItem
    senses = scrapy.Field(serializer=list)  # 存储 SenseItem 列表
    phrasal_verbs = scrapy.Field(serializer=list)  # 存储 PhraseItem 列表
    idioms = scrapy.Field(serializer=list)  # 存储 PhraseItem 列表
