import json
import os
from typing import Dict, List, Optional
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import ijson

from ..config import DBConfig
from .models import Base, DictWord, DictEntry, DictSense

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cambridge_dict_import.log')
    ]
)
logger = logging.getLogger(__name__)

class CambridgeDictImporter:
    def __init__(self, dict_uuid: str):
        if not dict_uuid:
            raise ValueError("必须提供词典UUID")
            
        logger.info(f"初始化导入器，词典UUID: {dict_uuid}")
        self.engine = create_engine(DBConfig.get_connection_url(), pool_recycle=3600)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.dict_uuid = dict_uuid
        logger.info("数据库连接已建立")

    def _get_or_create_dict_uuid(self) -> str:
        """获取英语-简体中文词典的UUID"""
        with self.SessionLocal() as session:
            # 直接从数据库查询
            result = session.execute(
                text("SELECT uuid FROM dict WHERE name = 'English–Chinese (Simplified)'")
            ).fetchone()
            if result:
                return result[0]
            raise ValueError("Dictionary 'English–Chinese (Simplified)' not found in database")

    def _process_pronunciation(self, pron_data: Optional[Dict]) -> tuple:
        """处理发音数据"""
        if not pron_data:
            return '', ''
        return pron_data.get('pron', '').strip('/'), pron_data.get('audio_url', '')

    def _create_word(self, session: Session, word_data: Dict) -> DictWord:
        """创建或获取单词记录"""
        word = session.query(DictWord).filter_by(
            word=word_data['word'],
            dict_uuid=self.dict_uuid
        ).first()
        
        if not word:
            word = DictWord(
                dict_uuid=self.dict_uuid,
                word=word_data['word'],
                url=word_data.get('url', '')
            )
            session.add(word)
            session.flush()
        
        return word

    def _create_entry(self, session: Session, word: DictWord, entry_data: Dict) -> DictEntry:
        """创建词条记录"""
        uk_pron, uk_audio = self._process_pronunciation(entry_data.get('uk_pronunciation'))
        us_pron, us_audio = self._process_pronunciation(entry_data.get('us_pronunciation'))
        
        entry = DictEntry(
            word_uuid=word.uuid,
            part_of_speech=entry_data.get('part_of_speech', ''),
            uk_pronunciation=uk_pron,
            uk_audio_url=uk_audio,
            us_pronunciation=us_pron,
            us_audio_url=us_audio
        )
        session.add(entry)
        session.flush()
        return entry

    def _create_senses(self, session: Session, entry: DictEntry, senses_data: List[Dict]) -> None:
        """创建词义记录"""
        for idx, sense_data in enumerate(senses_data):
            for definition_data in sense_data.get('definitions', []):
                sense = DictSense(
                    entry_uuid=entry.uuid,
                    guide_word=sense_data.get('guide_word', ''),
                    definition=definition_data.get('definition', ''),
                    translation=definition_data.get('def_translation', ''),
                    cefr_level=definition_data.get('level', ''),
                    attribute=definition_data.get('attribute', ''),
                    examples=definition_data.get('examples', []),
                    more_examples=sense_data.get('more_examples'),
                    sense_order=idx
                )
                session.add(sense)

    def import_file(self, file_path: str, batch_size: int = 100) -> None:
        """导入单个JSON文件
        
        Args:
            file_path: JSON文件路径
            batch_size: 批处理大小，默认100条记录提交一次
        """
        logger.info(f"开始导入文件: {file_path}")
        total_words = 0
        try:
            with open(file_path, 'rb') as f:
                # 使用ijson流式解析JSON数组
                parser = ijson.items(f, 'item')
                
                with self.SessionLocal() as session:
                    batch_count = 0
                    for word_data in parser:
                        try:
                            self._process_word_data(session, word_data)
                            batch_count += 1
                            total_words += 1
                            
                            # 达到批处理大小时提交
                            if batch_count >= batch_size:
                                session.commit()
                                logger.info(f"已提交批次数据，本批次处理了 {batch_count} 个单词，总计处理: {total_words} 个单词")
                                batch_count = 0
                                
                        except Exception as e:
                            session.rollback()
                            logger.error(f"导入单词 {word_data.get('word', 'unknown')} 时发生错误: {str(e)}")
                            continue
                    
                    # 处理剩余的记录
                    if batch_count > 0:
                        session.commit()
                        logger.info(f"已提交最后一批数据，本批次处理了 {batch_count} 个单词")
                        
            logger.info(f"文件 {file_path} 导入完成，总共处理了 {total_words} 个单词")
                        
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时发生错误: {str(e)}")

    def _process_word_data(self, session: Session, word_data: Dict) -> None:
        """处理单个单词的数据"""
        word_text = word_data.get('word', 'unknown')
        logger.debug(f"正在处理单词: {word_text}")
        
        # 创建单词
        word = self._create_word(session, word_data)
        
        # 如果数据结构是完整的词条
        if 'part_of_speech' in word_data:
            entry = self._create_entry(session, word, word_data)
            if 'senses' in word_data:
                self._create_senses(session, entry, word_data['senses'])
        
        logger.debug(f"单词 {word_text} 处理完成")

    def import_directory(self, directory_path: str) -> None:
        """导入目录下的所有JSON文件"""
        logger.info(f"开始导入目录: {directory_path}")
        total_files = len([f for f in os.listdir(directory_path) if f.endswith('.json')])
        processed_files = 0
        
        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                processed_files += 1
                file_path = os.path.join(directory_path, filename)
                logger.info(f"正在处理第 {processed_files}/{total_files} 个文件: {filename}")
                self.import_file(file_path)
                logger.info(f"完成处理文件: {filename}")
        
        logger.info(f"目录 {directory_path} 导入完成，共处理了 {processed_files} 个文件")
