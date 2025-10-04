from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ResearchPlan(BaseModel):
    """Research plan created by LeadResearcher"""
    tasks: List[str] = Field(description="List of research tasks for subagents")
    rationale: str = Field(description="Why this decomposition makes sense")
    estimated_duration: Optional[int] = Field(
        default=None, description="Estimated duration in seconds"
    )


class SubagentResult(BaseModel):
    """Result from a single research subagent"""
    agent_id: str
    task: str
    summary: str
    findings: str
    sources: List[str] = Field(default_factory=list)
    confidence: str = "medium"
    duration: Optional[float] = None


class Citation(BaseModel):
    """Single citation entry"""
    index: int
    title: str
    url: str
    accessed_date: str
    excerpt: Optional[str] = None


class ResearchResult(BaseModel):
    """Final research output"""
    query: str
    plan: ResearchPlan
    subagent_results: List[SubagentResult]
    synthesis: str
    cited_report: str
    bibliography: List[Citation]
    metadata: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)


class ProgressUpdate(BaseModel):
    """Progress update structure"""
    phase: str
    message: str
    percent: int
    details: Optional[Dict[str, Any]] = None
