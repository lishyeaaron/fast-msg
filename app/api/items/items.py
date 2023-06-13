from typing import Optional
from pydantic import BaseModel


class ReportItem(BaseModel):
    desc: Optional[str]
    event: Optional[str]
    host: Optional[str]


class SqlTransformItem(BaseModel):
    query_str: str  # mongo query string
    pg_table_schema: str  # postgresql table schema
    is_strict: int = 0
