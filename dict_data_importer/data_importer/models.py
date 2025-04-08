from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, BigInteger, JSON, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class DictWord(Base):
    __tablename__ = 'dict_word'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    dict_uuid = Column(String(36), nullable=False)
    word = Column(String(100), nullable=False)
    url = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime)

    entries = relationship("DictEntry", back_populates="word")

class DictEntry(Base):
    __tablename__ = 'dict_entry'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    word_uuid = Column(String(36), ForeignKey('dict_word.uuid'), nullable=False)
    part_of_speech = Column(String(50), nullable=False, default='')
    uk_pronunciation = Column(String(100), nullable=False, default='')
    uk_audio_url = Column(String(255), nullable=False, default='')
    us_pronunciation = Column(String(100), nullable=False, default='')
    us_audio_url = Column(String(255), nullable=False, default='')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime)

    word = relationship("DictWord", back_populates="entries")
    senses = relationship("DictSense", back_populates="entry")

class DictSense(Base):
    __tablename__ = 'dict_sense'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    entry_uuid = Column(String(36), ForeignKey('dict_entry.uuid'), nullable=False)
    guide_word = Column(String(100), nullable=False, default='')
    definition = Column(String(1000), nullable=False, default='')
    translation = Column(String(500), nullable=False, default='')
    cefr_level = Column(String(30), nullable=False, default='')
    attribute = Column(String(100), nullable=False, default='')
    examples = Column(JSON, nullable=False, default=list)
    more_examples = Column(JSON)
    sense_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime)

    entry = relationship("DictEntry", back_populates="senses")
