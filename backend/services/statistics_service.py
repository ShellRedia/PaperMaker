"""数值统计服务 — 论文指标计算"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.schema import Document, DocumentStatistics


class StatisticsService:
    """文档统计计算"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def compute_statistics(self, doc_id: str) -> Dict[str, Any]:
        """计算并缓存文档统计数据"""
        # 获取文档
        q = select(Document).where(Document.id == doc_id)
        doc = (await self.db.execute(q)).scalar_one_or_none()
        if not doc:
            return {}

        content = doc.content

        # 计算基础指标
        words = self._tokenize_words(content)
        sentences = self._tokenize_sentences(content)
        paragraphs = [p for p in content.split("\n\n") if p.strip()]

        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)
        avg_sentence_length = word_count / max(sentence_count, 1)

        # 章节数
        section_count = len(re.findall(r'^#{1,6}\s', content, re.MULTILINE))
        if doc.file_type == "latex":
            section_count = len(re.findall(r'\\(section|subsection|subsubsection)\{', content))

        # 可读性 (简化版 Flesch-Kincaid)
        syllable_count = self._estimate_syllables(" ".join(words))
        flesch_ease = 206.835 - 1.015 * (word_count / max(sentence_count, 1)) \
                      - 84.6 * (syllable_count / max(word_count, 1))
        flesch_grade = 0.39 * (word_count / max(sentence_count, 1)) \
                       + 11.8 * (syllable_count / max(word_count, 1)) - 15.59

        # 术语频率
        term_freqs = self._compute_term_frequencies(words)

        # 保存/更新缓存
        stats = await self._get_or_create_stats(doc_id)
        stats.word_count = word_count
        stats.sentence_count = sentence_count
        stats.paragraph_count = paragraph_count
        stats.section_count = section_count
        stats.flesch_reading_ease = round(flesch_ease, 2)
        stats.flesch_kincaid_grade = round(flesch_grade, 2)
        stats.avg_sentence_length = round(avg_sentence_length, 2)
        stats.term_frequencies = dict(term_freqs.most_common(100))
        stats.computed_at = datetime.utcnow()

        await self.db.commit()

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "section_count": section_count,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "flesch_reading_ease": round(flesch_ease, 2),
            "flesch_kincaid_grade": round(flesch_grade, 2),
        }

    async def compute_readability(self, doc_id: str) -> Dict[str, Any]:
        """计算可读性指标"""
        stats = await self.compute_statistics(doc_id)
        if not stats:
            return {}
        return {
            "flesch_reading_ease": stats["flesch_reading_ease"],
            "flesch_kincaid_grade": stats["flesch_kincaid_grade"],
            "avg_sentence_length": stats["avg_sentence_length"],
            "interpretation": self._interpret_readability(
                stats["flesch_reading_ease"]
            ),
        }

    async def get_term_frequencies(self, doc_id: str, limit: int = 50) -> List[Dict]:
        """获取高频术语"""
        q = select(DocumentStatistics).where(
            DocumentStatistics.document_id == doc_id
        )
        stats = (await self.db.execute(q)).scalar_one_or_none()
        if not stats or not stats.term_frequencies:
            await self.compute_statistics(doc_id)
            # re-fetch
            stats = (await self.db.execute(q)).scalar_one_or_none()

        if not stats or not stats.term_frequencies:
            return []

        sorted_terms = sorted(
            stats.term_frequencies.items(), key=lambda x: x[1], reverse=True
        )
        return [{"term": t, "count": c} for t, c in sorted_terms[:limit]]

    # ── 内部方法 ──

    def _tokenize_words(self, text: str) -> List[str]:
        """简单分词"""
        return [w.lower().strip(".,;:!?\"'()[]{}") for w in text.split() if w.strip()]

    def _tokenize_sentences(self, text: str) -> List[str]:
        """分句"""
        return [s.strip() for s in re.split(r'[.!?]+\s+', text) if s.strip()]

    def _estimate_syllables(self, text: str) -> int:
        """粗略音节数估算 (英语)"""
        count = 0
        vowels = "aeiouy"
        for word in text.lower().split():
            word = word.strip(".,;:!?\"'()[]{}")
            if not word:
                continue
            word_syllables = 0
            prev_vowel = False
            for ch in word:
                if ch in vowels:
                    if not prev_vowel:
                        word_syllables += 1
                    prev_vowel = True
                else:
                    prev_vowel = False
            if word.endswith("e") and word_syllables > 1:
                word_syllables -= 1
            if word_syllables == 0:
                word_syllables = 1
            count += word_syllables
        return count

    def _compute_term_frequencies(self, words: List[str], min_len: int = 3) -> Counter:
        """计算术语频率（过滤短词）"""
        stopwords = {
            "the", "and", "for", "that", "this", "with", "from", "are", "was",
            "has", "have", "been", "can", "not", "but", "its", "also", "were",
            "had", "did", "each", "all", "any", "our", "may", "who", "which",
            "will", "more", "they", "than", "then", "into", "them",
        }
        filtered = [w for w in words if len(w) >= min_len and w not in stopwords]
        return Counter(filtered)

    def _interpret_readability(self, score: float) -> str:
        """解读可读性分数"""
        if score >= 90:
            return "非常容易阅读（相当于小学水平）"
        elif score >= 80:
            return "容易阅读（相当于初中水平）"
        elif score >= 70:
            return "比较容易阅读（相当于高中水平）"
        elif score >= 60:
            return "标准难度（相当于大学水平）"
        elif score >= 50:
            return "比较困难（相当于大学高年级水平）"
        elif score >= 30:
            return "困难（相当于研究生水平）"
        else:
            return "非常困难（相当于专业学术水平）"

    async def _get_or_create_stats(self, doc_id: str) -> DocumentStatistics:
        q = select(DocumentStatistics).where(
            DocumentStatistics.document_id == doc_id
        )
        stats = (await self.db.execute(q)).scalar_one_or_none()
        if not stats:
            stats = DocumentStatistics(document_id=doc_id)
            self.db.add(stats)
        return stats
