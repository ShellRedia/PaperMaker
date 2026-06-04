"""ORM 模型定义"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def generate_uuid():
    return str(uuid.uuid4())


class Document(Base):
    """论文文档"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False, default="Untitled")
    content = Column(Text, default="")
    file_type = Column(String(20), default="markdown")  # markdown / latex
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    annotations = relationship("Annotation", back_populates="document", cascade="all, delete-orphan")
    polish_records = relationship("PolishRecord", back_populates="document", cascade="all, delete-orphan")
    statistics = relationship("DocumentStatistics", back_populates="document", cascade="all, delete-orphan")


class Annotation(Base):
    """数据标注"""
    __tablename__ = "annotations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    type = Column(String(20), nullable=False)  # bbox / polygon / relation / text_span
    label = Column(String(100), nullable=False)
    color = Column(String(20), default="#3B82F6")
    page_index = Column(Integer, default=0)
    data = Column(JSON, default=dict)  # 标注坐标/属性数据
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="annotations")


class PolishRecord(Base):
    """文本润色记录"""
    __tablename__ = "polish_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    original_text = Column(Text, nullable=False)
    polished_text = Column(Text, default="")
    style = Column(String(50), default="academic")  # academic / concise / expanded
    model_name = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="polish_records")


class DocumentStatistics(Base):
    """文档统计数据"""
    __tablename__ = "document_statistics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    word_count = Column(Integer, default=0)
    sentence_count = Column(Integer, default=0)
    paragraph_count = Column(Integer, default=0)
    section_count = Column(Integer, default=0)
    flesch_reading_ease = Column(Float, default=0.0)
    flesch_kincaid_grade = Column(Float, default=0.0)
    avg_sentence_length = Column(Float, default=0.0)
    term_frequencies = Column(JSON, default=dict)
    computed_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="statistics")


class ModelCache(Base):
    """模型推理缓存"""
    __tablename__ = "model_cache"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cache_key = Column(String(256), unique=True, nullable=False, index=True)
    input_hash = Column(String(64), nullable=False)
    output_data = Column(Text, nullable=False)
    model_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ttl_seconds = Column(Integer, default=3600)


class AppSettings(Base):
    """应用全局设置（键值对存储）"""
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TranslationHistory(Base):
    """翻译对话历史 — 持久化到文档粒度"""
    __tablename__ = "translation_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    role = Column(String(16), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)  # JSON: 用户文本 或 {english, chinese}
    usage_json = Column(Text, default="")  # JSON: {prompt_tokens, completion_tokens, total_tokens}
    created_at = Column(DateTime, default=datetime.utcnow)
