import io
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple
import pandas as pd
from app.services.connectors.base import BaseSourceConnector
from app.schemas.source import NormalizedRecord

logger = logging.getLogger(__name__)

class FileUploadConnector(BaseSourceConnector):
    @property
    def platform_name(self) -> str:
        return "FILE_UPLOAD"

    def is_configured(self) -> bool:
        return True

    def parse_file(
        self,
        file_bytes: bytes,
        filename: str,
        limit: int = 500
    ) -> Tuple[List[NormalizedRecord], str]:
        """Parses CSV or Excel file bytes into normalized opinion intelligence records."""
        records: List[NormalizedRecord] = []
        filename_lower = filename.lower()
        
        try:
            if filename_lower.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_bytes), nrows=limit)
            elif filename_lower.endswith((".xlsx", ".xls")):
                df = pd.read_excel(io.BytesIO(file_bytes), nrows=limit)
            else:
                return [], "Unsupported file format. Please upload a .csv or .xlsx file."

            if df.empty:
                return [], "Uploaded dataset is empty."

            # Find text column
            columns_lower = {col: str(col).lower().strip() for col in df.columns}
            text_col = None
            
            # Prioritized text column name candidates
            priority_candidates = ["review", "comment", "text", "feedback", "opinion", "content", "body", "message", "summary", "description", "post"]
            for cand in priority_candidates:
                for original_col, lower_col in columns_lower.items():
                    if cand == lower_col or cand in lower_col:
                        text_col = original_col
                        break
                if text_col:
                    break

            # If no priority column matches, pick the string column with highest average length
            if not text_col:
                str_cols = [c for c in df.columns if df[c].dtype == object or pd.api.types.is_string_dtype(df[c])]
                if str_cols:
                    text_col = max(str_cols, key=lambda c: df[c].astype(str).str.len().mean())
                else:
                    text_col = df.columns[0]

            # Find date column if available
            date_col = None
            date_candidates = ["date", "time", "timestamp", "created_at", "published_at"]
            for cand in date_candidates:
                for original_col, lower_col in columns_lower.items():
                    if cand in lower_col:
                        date_col = original_col
                        break
                if date_col:
                    break

            # Find author column if available
            author_col = None
            author_candidates = ["author", "user", "username", "reviewer", "name"]
            for cand in author_candidates:
                for original_col, lower_col in columns_lower.items():
                    if cand in lower_col:
                        author_col = original_col
                        break
                if author_col:
                    break

            # Find rating/engagement column if available
            score_col = None
            score_candidates = ["rating", "score", "likes", "upvotes", "stars"]
            for cand in score_candidates:
                for original_col, lower_col in columns_lower.items():
                    if cand in lower_col:
                        score_col = original_col
                        break
                if score_col:
                    break

            for idx, row in df.iterrows():
                val = row.get(text_col)
                if pd.isna(val) or not str(val).strip():
                    continue
                
                raw_text = str(val).strip()
                
                # Parse date
                pub_date = None
                if date_col and not pd.isna(row.get(date_col)):
                    try:
                        parsed_dt = pd.to_datetime(row.get(date_col))
                        pub_date = parsed_dt.to_pydatetime()
                        if pub_date.tzinfo is None:
                            pub_date = pub_date.replace(tzinfo=timezone.utc)
                    except Exception:
                        pub_date = datetime.now(timezone.utc)
                else:
                    pub_date = datetime.now(timezone.utc)

                author_val = str(row.get(author_col)) if author_col and not pd.isna(row.get(author_col)) else f"Record #{idx+1}"
                
                engagement_val = 0
                if score_col and not pd.isna(row.get(score_col)):
                    try:
                        engagement_val = int(float(row.get(score_col)))
                    except Exception:
                        engagement_val = 0

                records.append(NormalizedRecord(
                    platform=self.platform_name,
                    external_id=f"{filename}_{idx}",
                    raw_text=raw_text,
                    author=author_val,
                    published_at=pub_date,
                    engagement_score=engagement_val,
                    source_url=filename,
                    metadata={"source_file": filename, "row_index": idx}
                ))

            logger.info(f"File upload parser extracted {len(records)} records from {filename}.")
            return records, ""

        except Exception as e:
            logger.error(f"Error parsing uploaded file {filename}: {e}")
            return [], f"Failed to parse file: {str(e)}"

    async def collect(
        self,
        query: str,
        limit: int = 50,
        time_days: int = 30,
        url: Optional[str] = None
    ) -> List[NormalizedRecord]:
        return []

file_connector = FileUploadConnector()
