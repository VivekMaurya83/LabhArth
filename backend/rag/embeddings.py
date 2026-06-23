"""
LabhArth AI — Gemini API Integration
=======================================
Handles vector embeddings and structured data extraction with multi-key rotation and rate-limiting.
"""

import os
import time
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import errors
from google.genai import types

from backend.utils.logger import logger


class MultiKeyGeminiClient:
    """
    Manages a pool of Google API keys to avoid quota limitations.
    Rotates to the next key when a 429 Quota Exceeded / Resource Exhausted error is met.
    """

    def __init__(self):
        self.api_keys = self._load_keys()
        self.current_key_idx = 0
        
        if not self.api_keys:
            logger.warning("No GOOGLE_API_KEY or GEMINI_API_KEYS set. Attempting default initialization.")
            self.api_keys = [""]  # Will fall back to default client behavior/env vars

        self.client = self._create_client()

    def _load_keys(self) -> List[str]:
        """Loads API keys from GEMINI_API_KEYS or GOOGLE_API_KEY."""
        # Try custom comma-separated keys first
        keys_str = os.environ.get("GEMINI_API_KEYS", "")
        if not keys_str:
            keys_str = os.environ.get("GOOGLE_API_KEY", "")
        
        if keys_str:
            return [k.strip() for k in keys_str.split(",") if k.strip()]
        return []

    def _create_client(self) -> genai.Client:
        """Create a genai Client using the current key index."""
        current_key = self.api_keys[self.current_key_idx]
        if current_key:
            masked_key = f"...{current_key[-4:]}" if len(current_key) > 4 else "valid_key"
            logger.info(f"Initializing Gemini Client with key index {self.current_key_idx} ({masked_key})")
            return genai.Client(api_key=current_key)
        else:
            logger.info("Initializing Gemini Client with standard environment configurations.")
            return genai.Client()

    def rotate_key(self) -> bool:
        """Rotates the client to the next key. Returns True if successfully rotated."""
        if len(self.api_keys) <= 1:
            return False
        
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
        self.client = self._create_client()
        return True

    def execute(self, method_path: str, *args, **kwargs) -> Any:
        """
        Executes a method on the client with automated key rotation on 429 errors.
        
        Args:
            method_path: Attribute path on client (e.g. 'models.embed_content')
            *args: Arguments passed to the target method
            **kwargs: Keyword arguments passed to the target method
        """
        max_attempts = len(self.api_keys) * 2  # Cycle through keys twice max
        attempt = 0

        while attempt < max_attempts:
            try:
                # Resolve method (e.g., self.client.models.embed_content)
                parts = method_path.split(".")
                method = self.client
                for part in parts:
                    method = getattr(method, part)

                return method(*args, **kwargs)

            except Exception as exc:
                err_msg = str(exc).lower()
                is_quota_error = (
                    "429" in err_msg or 
                    "quota" in err_msg or 
                    "exhausted" in err_msg or 
                    "resource_exhausted" in err_msg
                )

                if is_quota_error:
                    logger.warning(
                        f"Quota exceeded on key index {self.current_key_idx} (Attempt {attempt+1}/{max_attempts}): {exc}"
                    )
                    attempt += 1
                    
                    if self.rotate_key():
                        logger.info("Retrying API execution with the next rotated key...")
                        continue
                    else:
                        # Only 1 key is set; wait 30 seconds before retrying
                        wait_time = 30
                        logger.warning(f"Single key pool active. Sleeping {wait_time} seconds before retrying...")
                        time.sleep(wait_time)
                else:
                    # Non-quota error, raise immediately
                    logger.error(f"Unrecoverable Gemini API error: {exc}")
                    raise exc

        raise RuntimeError("All configured Gemini API keys have exhausted their quotas.")


# =============================================================================
# Structured Pydantic Models for Extraction
# =============================================================================

class RuleSchema(BaseModel):
    field: str = Field(description="User profile field (e.g. 'age', 'gender', 'state', 'district', 'category', 'income_annual', 'occupation', 'is_bpl', 'is_disabled', 'is_farmer', 'is_student')")
    operator: str = Field(description="Operator (eq, neq, gt, gte, lt, lte, in, not_in, exists)")
    value: Any = Field(description="Value to compare against. For boolean fields, use true/false. For in/not_in, list of strings/numbers. For numbers, numeric type.")
    label: str = Field(description="Natural language instruction for this rule (e.g. 'Annual income should not exceed ₹2,00,000')")


class StructuredEligibility(BaseModel):
    rules: List[RuleSchema] = Field(description="List of parsed rules.")
    additional_notes: str = Field(description="Nuances/notes that cannot be parsed as structured logic rules.")
    raw_text: str = Field(description="The original eligibility text passed in.")


class RequiredDocument(BaseModel):
    name: str = Field(description="Name of the document (e.g., 'Aadhaar Card', 'Income Certificate')")
    mandatory: bool = Field(description="Is this document strictly mandatory (True) or optional (False)?")
    alternatives: List[str] = Field(description="Alternatives list if the document is missing.")


class StructuredSchemeMetadata(BaseModel):
    name: str = Field(description="The formal title/name of the government scheme.")
    category: str = Field(description="The canonical category of the scheme. Must be exactly one of: 'agriculture', 'education', 'health', 'housing', 'social_welfare', 'employment', 'women_children', 'minority', 'disability', 'financial_inclusion', 'other'")
    level: str = Field(description="The level of the scheme. Must be exactly 'central' or 'state'.")
    state: Optional[str] = Field(default=None, description="The name of the state (e.g. 'Uttar Pradesh', 'Madhya Pradesh') if level is 'state', otherwise null.")
    ministry: Optional[str] = Field(default=None, description="The government ministry or department in charge of this scheme.")
    eligibility: StructuredEligibility
    required_documents: List[RequiredDocument]


# =============================================================================
# Services
# =============================================================================

class EmbeddingService:
    """
    Generate vector representations of text using gemini-embedding-001.
    """

    def __init__(self, model_name: str = "gemini-embedding-001"):
        self.model_name = model_name
        self.pool = MultiKeyGeminiClient()
        logger.info(f"EmbeddingService initialized with model: {self.model_name}")

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single text segment."""
        # Use task_type=RETRIEVAL_DOCUMENT for document ingestion
        import asyncio
        response = await asyncio.to_thread(
            self.pool.execute,
            "models.embed_content",
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
        )
        return response.embeddings[0].values

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of text segments."""
        if not texts:
            return []
        
        # models.embed_content accepts lists of strings
        import asyncio
        response = await asyncio.to_thread(
            self.pool.execute,
            "models.embed_content",
            model=self.model_name,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
        )
        return [emb.values for emb in response.embeddings]


class ExtractionService:
    """
    Parses unstructured text fields into structured Pydantic Schemas using Gemini.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", delay_seconds: int = 10):
        self.model_name = model_name
        self.delay_seconds = delay_seconds
        self.pool = MultiKeyGeminiClient()
        logger.info(f"ExtractionService initialized with model: {self.model_name}, delay: {delay_seconds}s")

    def extract_scheme_metadata(self, filename: str, full_raw_text: str) -> StructuredSchemeMetadata:
        """
        Processes raw text and returns structured eligibility criteria rules, documents, and general scheme metadata.
        Enforces a delay to protect rate limits on Gemini calls.
        """
        # Rate limit safety delay
        if self.delay_seconds > 0:
            logger.debug(f"Rate limiting safety: sleeping for {self.delay_seconds} seconds before structuring...")
            time.sleep(self.delay_seconds)

        prompt = f"""
        You are an expert AI systems architect extracting metadata for a government scheme.
        Below is the raw extracted text from a PDF file named "{filename}".
        
        Analyze the text to parse the scheme's general information, eligibility criteria, and required documents into the required JSON structure.
        
        ---
        RAW SCHEME DOCUMENT TEXT:
        {full_raw_text}
        ---
        
        Rules for extraction:
        1. Extract the formal name, category, level, state, and ministry from the text.
           - 'category' must be exactly one of: 'agriculture', 'education', 'health', 'housing', 'social_welfare', 'employment', 'women_children', 'minority', 'disability', 'financial_inclusion', 'other'.
           - 'level' must be exactly 'central' or 'state'.
           - 'state' must be the name of the state (e.g. 'Uttar Pradesh', 'Madhya Pradesh') if level is 'state', otherwise null.
        2. Parse the rules into comparison rules where possible:
           - Use the fields: 'age' (int), 'gender' (string), 'state' (string), 'district' (string), 'category' (SC/ST/OBC/General), 'income_annual' (float), 'occupation' (string), 'is_bpl' (bool), 'is_disabled' (bool), 'is_farmer' (bool), 'is_student' (bool).
           - Use operators: eq, neq, gt, gte, lt, lte, in, not_in, exists.
           - Ensure the labels describe the rules exactly.
        3. Put any guidelines, conditions, or exclusions that are not fit for structured rules in 'additional_notes'.
        4. Match required documents, mark whether they are mandatory, and list alternative files.
        """
        
        logger.info(f"Extracting structured metadata from file: {filename}")

        response = self.pool.execute(
            "models.generate_content",
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StructuredSchemeMetadata,
                temperature=0.1
            )
        )

        # Parse JSON string from response
        try:
            structured_data = StructuredSchemeMetadata.model_validate_json(response.text)
            logger.info(f"Successfully structured metadata for {structured_data.name}")
            return structured_data
        except Exception as e:
            logger.error(f"Failed to validate structured metadata for {filename}: {e}. Raw response: {response.text}")
            raise
