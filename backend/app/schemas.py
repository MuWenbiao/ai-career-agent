from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class SkillBase(BaseModel):
    skill_name: str
    level: str  # beginner, intermediate, advanced, expert
    years: Optional[float] = None
    source: str = "manual"


class SkillCreate(SkillBase):
    pass


class Skill(SkillBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ExperienceBase(BaseModel):
    title: str
    company: str
    description: str
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False


class ExperienceCreate(ExperienceBase):
    pass


class Experience(ExperienceBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    current_title: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    skills: List[Skill] = []
    experiences: List[Experience] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    title: str
    company: str
    location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_description: str
    source: str  # lagou, boss, maimai, etc.
    source_url: str
    required_skills: Optional[List[str]] = None
    experience_required: Optional[str] = None
    job_type: Optional[str] = None


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    job_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeBase(BaseModel):
    title: str
    content: str
    template: str = "standard"
    is_default: bool = False


class ResumeCreate(ResumeBase):
    pass


class Resume(ResumeBase):
    id: int
    user_id: int
    target_job_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillExtraction(BaseModel):
    """技能提取结果"""
    technical_skills: List[str]
    tools: List[str]
    soft_skills: List[str]
    languages: List[str]
    frameworks: List[str]


class JobAnalysis(BaseModel):
    """职位分析结果"""
    required_skills: List[str]
    nice_to_have_skills: List[str]
    experience_required: str
    hidden_requirements: List[str]
    key_responsibilities: List[str]
    career_growth: str
    salary_range_assessment: str
    company_culture_hints: str


class MatchResult(BaseModel):
    """匹配结果"""
    match_score: float
    match_percentage: str
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    improvement_areas: List[str]
    recommendation: str


class JobEvaluation(BaseModel):
    """职位评估结果"""
    salary_assessment: Dict[str, Any]
    growth_potential: Dict[str, Any]
    company_outlook: Dict[str, Any]
    work_life_balance: Dict[str, Any]
    industry_trend: Dict[str, Any]
    overall_score: float
    rating: str
    pros: List[str]
    cons: List[str]
    recommendation: str
