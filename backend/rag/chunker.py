"""
LabhArth AI — Document Chunker
=================================
Split scheme documents into semantic chunks for embedding.
"""

from pathlib import Path
from typing import Dict, List, Optional
from pypdf import PdfReader

from backend.utils.logger import logger

# Namespace/Namespace helper for point ID mapping
NAMESPACE_LABHARTH_STR = "3c7b2e3d-d19a-4f51-b0db-6a7f85e493cc"


class DocumentChunker:
    """
    Split government scheme documents into meaningful chunks.

    Chunk types:
    - overview: Scheme details/description
    - eligibility: Eligibility criteria (and exclusions)
    - benefits: Benefits description
    - documents: Required documents
    - application: Application process
    - combined: All sections combined
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(
            f"DocumentChunker initialized: size={chunk_size}, overlap={chunk_overlap}"
        )

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract raw text from a PDF file.
        """
        try:
            reader = PdfReader(pdf_path)
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            full_text = "\n".join(text_parts)
            return full_text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            raise

    def parse_sections(self, text: str) -> Dict[str, str]:
        """
        Parse raw text into semantic sections using keywords.
        """
        lines = text.split("\n")
        
        # Clean lines
        cleaned_lines = [line.strip() for line in lines]

        # Standard MyScheme Section headers (case-insensitive keyword matching)
        headers = {
            "overview": ["details", "description", "about the scheme", "scheme overview"],
            "benefits": ["benefits", "benefits offered", "what benefits are offered", "benefit"],
            "eligibility": ["eligibility", "eligibility criteria", "who is eligible", "eligibility check"],
            "exclusions": ["exclusions", "exclusion", "who is not eligible", "ineligible"],
            "documents": ["documents required", "required documents", "documents", "what documents are required", "documents checklists"],
            "application": ["application process", "how to apply", "process", "steps to apply", "application step", "how to apply?"]
        }

        # Initialize sections with empty lists
        sections_list: Dict[str, List[str]] = {
            "overview": [],
            "benefits": [],
            "eligibility": [],
            "exclusions": [],
            "documents": [],
            "application": []
        }

        current_section = "overview"  # default section starts at the top of the file

        for line in cleaned_lines:
            if not line:
                continue

            # Strip numbering/formatting (e.g. "1. Details" -> "details", "* Benefits *" -> "benefits")
            normalized = line.lower().strip(":-*#[] ")
            # Remove leading numbers like "1. ", "2. ", "a) "
            if len(normalized) > 2 and normalized[0].isdigit() and normalized[1] in (".", " "):
                normalized = normalized[2:].strip(":-*#[] ")
            
            # Match section boundaries
            header_found = False
            for sec_name, keywords in headers.items():
                if normalized in keywords:
                    current_section = sec_name
                    header_found = True
                    break
            
            if header_found:
                continue
            
            sections_list[current_section].append(line)

        # Merge exclusions into eligibility
        if sections_list["exclusions"]:
            sections_list["eligibility"].append("\nExclusions / Ineligibility:")
            sections_list["eligibility"].extend(sections_list["exclusions"])

        # Convert lists to strings
        sections: Dict[str, str] = {}
        for k, v in sections_list.items():
            if k != "exclusions":
                sections[k] = "\n".join(v).strip()

        return sections

    def chunk_scheme(self, name: str, category: str, state: Optional[str], ministry: Optional[str], parsed_sections: Dict[str, str]) -> List[Dict]:
        """
        Split parsed scheme sections into contextualized chunks.

        Args:
            name: Scheme Name
            category: Scheme Category
            state: Central or State name
            ministry: Ministry name
            parsed_sections: Dictionary containing key -> text section

        Returns:
            List of chunk dictionaries containing text, type, index, metadata
        """
        chunks = []
        state_str = state if state else "Central"
        ministry_str = ministry if ministry else "Unknown Ministry"

        # Build each section chunk
        for section_type, text in parsed_sections.items():
            if not text:
                continue

            # If section text is too long, split it into smaller paragraph chunks
            # A section under 1200 words (~1500 tokens) will remain a single chunk
            paragraphs = text.split("\n\n")
            current_chunk_parts = []
            current_len = 0
            chunk_index = 0

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                para_len = len(para.split())
                if current_len + para_len > 600:  # ~750 tokens boundary
                    if current_chunk_parts:
                        chunk_text = "\n\n".join(current_chunk_parts)
                        chunks.append(self._create_chunk_dict(
                            name, category, state_str, ministry_str, section_type, chunk_index, chunk_text
                        ))
                        chunk_index += 1
                    current_chunk_parts = [para]
                    current_len = para_len
                else:
                    current_chunk_parts.append(para)
                    current_len += para_len

            if current_chunk_parts:
                chunk_text = "\n\n".join(current_chunk_parts)
                chunks.append(self._create_chunk_dict(
                    name, category, state_str, ministry_str, section_type, chunk_index, chunk_text
                ))

        # Generate "combined" holistic chunk (capping text length to prevent context blowup)
        combined_parts = []
        for sect_type, text in parsed_sections.items():
            if text:
                # Add section title and snippet
                combined_parts.append(f"[{sect_type.upper()}]\n{text}")
        
        combined_text = "\n\n".join(combined_parts)
        # Cap combined text at roughly 1200 words to ensure it fits in ~1500 tokens
        words = combined_text.split()
        if len(words) > 1200:
            combined_text = " ".join(words[:1200]) + "..."

        chunks.append(self._create_chunk_dict(
            name, category, state_str, ministry_str, "combined", 0, combined_text
        ))

        return chunks

    def _create_chunk_dict(self, name: str, category: str, state: str, ministry: str, section_type: str, index: int, text: str) -> Dict:
        """Helper to structure chunk content with grounding metadata prefix."""
        # Grounding prefix to feed into Qdrant/Gemini
        prefix = f"Scheme Name: {name}\nCategory: {category}\nState/Level: {state}\nMinistry: {ministry}\nSection: {section_type.upper()}\n\n"
        full_chunk_text = prefix + text
        
        # Approximate token count (1 token ~= 4 chars or 0.75 words, we do a conservative word-based estimate)
        approx_token_count = int(len(full_chunk_text.split()) * 1.3)

        return {
            "chunk_type": section_type,
            "chunk_index": index,
            "chunk_text": full_chunk_text,
            "token_count": approx_token_count,
        }
