"""
Policy Document Ingestion Module.

This module handles the ingestion of policy documents, debate transcripts,
and official statements from various sources.
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Iterator
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class DebateDocument:
    """Represents a debate document with metadata."""
    ext_id: str
    title: str
    source: str
    session_date: datetime
    jurisdiction: str
    url: Optional[str]
    media_type: str  # text, audio, video
    content: str
    hash: str
    created_at: datetime


@dataclass
class DebateSegment:
    """Represents a segment within a debate document."""
    speaker: str
    party: Optional[str]
    start_ts: Optional[float]
    end_ts: Optional[float]
    text: str
    asr_confidence: Optional[float]
    turn_index: int


class PolicyIngestion:
    """Handles ingestion of policy documents and debate transcripts."""
    
    def __init__(self):
        self.supported_sources = {
            'parliamentary': self._parse_parliamentary_transcript,
            'central_bank': self._parse_central_bank_statement,
            'regulator': self._parse_regulator_notice,
            'press_release': self._parse_press_release,
            'jsonl': self._parse_jsonl_file
        }
    
    def ingest_from_file(self, file_path: str, source_type: str = 'jsonl') -> List[DebateDocument]:
        """
        Ingest documents from a file.
        
        Args:
            file_path: Path to the file
            source_type: Type of source (parliamentary, central_bank, etc.)
            
        Returns:
            List of debate documents
        """
        if source_type not in self.supported_sources:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        parser = self.supported_sources[source_type]
        return parser(file_path)
    
    def ingest_from_jsonl(self, file_path: str) -> List[DebateDocument]:
        """
        Ingest documents from a JSONL file.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of debate documents
        """
        documents = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    doc = self._create_document_from_dict(data)
                    documents.append(doc)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON on line {line_num}: {e}")
                except Exception as e:
                    logger.error(f"Error processing line {line_num}: {e}")
        
        return documents
    
    def _create_document_from_dict(self, data: Dict[str, Any]) -> DebateDocument:
        """Create a DebateDocument from a dictionary."""
        # Generate hash from content
        content = data.get('content', '')
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Parse date
        session_date = datetime.fromisoformat(data.get('session_date', datetime.now().isoformat()))
        
        return DebateDocument(
            ext_id=data.get('ext_id', ''),
            title=data.get('title', ''),
            source=data.get('source', ''),
            session_date=session_date,
            jurisdiction=data.get('jurisdiction', ''),
            url=data.get('url'),
            media_type=data.get('media_type', 'text'),
            content=content,
            hash=content_hash,
            created_at=datetime.now()
        )
    
    def _parse_jsonl_file(self, file_path: str) -> List[DebateDocument]:
        """Parse JSONL file format."""
        return self.ingest_from_jsonl(file_path)
    
    def _parse_parliamentary_transcript(self, file_path: str) -> List[DebateDocument]:
        """Parse parliamentary transcript format (stub implementation)."""
        # This would be implemented to parse specific parliamentary formats
        logger.info(f"Parsing parliamentary transcript: {file_path}")
        return []
    
    def _parse_central_bank_statement(self, file_path: str) -> List[DebateDocument]:
        """Parse central bank statement format (stub implementation)."""
        # This would be implemented to parse central bank statement formats
        logger.info(f"Parsing central bank statement: {file_path}")
        return []
    
    def _parse_regulator_notice(self, file_path: str) -> List[DebateDocument]:
        """Parse regulator notice format (stub implementation)."""
        # This would be implemented to parse regulator notice formats
        logger.info(f"Parsing regulator notice: {file_path}")
        return []
    
    def _parse_press_release(self, file_path: str) -> List[DebateDocument]:
        """Parse press release format (stub implementation)."""
        # This would be implemented to parse press release formats
        logger.info(f"Parsing press release: {file_path}")
        return []
    
    def segment_document(self, document: DebateDocument) -> List[DebateSegment]:
        """
        Segment a document into debate segments.
        
        Args:
            document: Debate document to segment
            
        Returns:
            List of debate segments
        """
        segments = []
        
        # Simple segmentation by paragraphs (stub implementation)
        paragraphs = document.content.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                # Extract speaker information (simple heuristic)
                speaker = self._extract_speaker(paragraph)
                
                segment = DebateSegment(
                    speaker=speaker,
                    party=None,  # Would be extracted in full implementation
                    start_ts=None,
                    end_ts=None,
                    text=paragraph.strip(),
                    asr_confidence=None,
                    turn_index=i
                )
                segments.append(segment)
        
        return segments
    
    def _extract_speaker(self, text: str) -> str:
        """Extract speaker name from text (stub implementation)."""
        # Simple heuristic: look for patterns like "Speaker: " or "Mr. Smith: "
        lines = text.split('\n')
        if lines:
            first_line = lines[0]
            if ':' in first_line:
                return first_line.split(':')[0].strip()
        return "Unknown Speaker"
    
    def validate_document(self, document: DebateDocument) -> bool:
        """
        Validate a debate document.
        
        Args:
            document: Document to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not document.title or not document.content:
            return False
        
        if not document.ext_id:
            return False
        
        if not document.source or not document.jurisdiction:
            return False
        
        return True























