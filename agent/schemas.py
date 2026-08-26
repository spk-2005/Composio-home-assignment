from typing import List, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    claim: str
    url: str
    source_type: str
    quote_or_summary: str


class APIInfo(BaseModel):
    public: bool
    type: str
    breadth: str


class MCPInfo(BaseModel):
    available: bool
    source: Optional[str] = None
    url: Optional[str] = None


class AppResearch(BaseModel):
    app: str
    category: str
    description: str

    auth_methods: List[str]

    credential_access: str

    api: APIInfo

    mcp: MCPInfo

    buildability: str

    blocker: Optional[str]

    evidence: List[Evidence]

    confidence: float

    uncertainty: List[str] = Field(default_factory=list)
