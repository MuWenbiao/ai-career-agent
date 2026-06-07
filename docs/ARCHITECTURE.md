# AI Career Agent - 架构设计文档

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    API 层 (FastAPI)                     │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │ Users    │ Jobs     │ Resumes  │ AI Agents        │ │
│  │ 用户管理 │ 职位管理 │ 简历管理 │ 智能分析         │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Agent 层 (AI 智能代理)                      │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │Skill Gen │Job       │Resume    │Job Evaluator    │ │
│  │eration  │Matcher   │Analyzer  │                  │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│             Services 层 (业务逻辑)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │        LLM Service (OpenAI / DeepSeek)           │  │
│  │  - generate_text()                               │  │
│  │  - generate_json()                               │  │
│  │  - extract_skills_from_experience()              │  │
│  │  - analyze_job_description()                     │  │
│  │  - match_user_to_job()                           │  │
│  │  - generate_resume()                             │  │
│  │  - generate_cover_letter()                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│            Data 层 (数据存储与访问)                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │        SQLite Database                           │  │
│  │  - Users                                         │  │
│  │  - Experiences                                   │  │
│  │  - Skills                                        │  │
│  │  - Jobs                                          │  │
│  │  - Resumes                                       │  │
│  │  - Applications                                  │  │
│  │  - Evaluations                                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📦 核心模块

### 1. LLM Service
**位置**: `app/services/llm_service.py`

**职责**：
- 与 OpenAI/DeepSeek API 通信
- 生成文本和 JSON 格式的响应
- 错误处理和重试机制

**关键方法**：
```python
- generate_text(prompt, temperature, max_tokens) -> str
- generate_json(prompt, temperature) -> Dict
- extract_skills_from_experience(experience_text) -> Dict
- analyze_job_description(job_description) -> Dict
- match_user_to_job(user_skills, job_description, user_experience) -> Dict
- generate_resume(user_profile, target_job_description) -> str
- generate_cover_letter(user_profile, job_description, company_name) -> str
```

### 2. SkillGenerator Agent
**位置**: `app/agents/skill_generator.py`

**职责**：
- 从工作经历提取技能
- 生成完整的技能档案
- 推荐学习路径

**关键方法**：
```python
- extract_skills_from_experience(experience_text) -> Dict[str, List[str]]
- generate_skill_profile(experiences: List[Dict]) -> Dict[str, Any]
- infer_missing_skills(current_skills, target_role) -> Dict[str, Any]
```

### 3. JobMatcher Agent
**位置**: `app/agents/job_matcher.py`

**职责**：
- 双向职位匹配（简历→职位，职位→简历）
- 查找技能差距
- 生成匹配报告

**关键方法**：
```python
- match_user_to_jobs(user_skills, user_experience, user_preferences, jobs) -> List[Dict]
- match_user_to_single_job(user_skills, user_experience, job_description, job_title) -> Dict
- match_jobs_to_user_reverse(job_descriptions, user_profile) -> List[Dict]
- find_skill_gaps(user_skills, target_job_description) -> Dict
```

### 4. ResumeAnalyzer Agent
**位置**: `app/agents/resume_analyzer.py`

**职责**：
- 分析简历并提出优化建议
- 针对职位定制化简历
- 对比不同简历版本

**关键方法**：
```python
- analyze_resume(resume_content) -> Dict
- tailor_resume_for_job(resume_content, job_description, company_name) -> str
- compare_resumes(resume1, resume2) -> Dict
```

### 5. JobEvaluator Agent
**位置**: `app/agents/job_evaluator.py`

**职责**：
- 综合评估职位优劣
- 对比多个 Offer
- 评估职业目标契合度

**关键方法**：
```python
- evaluate_job(job_title, job_description, company_name, salary_range, location) -> Dict
- compare_job_offers(offers: list) -> Dict
- assess_career_fit(job_description, user_career_goals, user_values) -> Dict
```

## 🗄️ 数据模型

### User
用户基本信息和个人资料

```python
{
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "full_name": "张三",
    "phone": "13800138000",
    "current_title": "Python 工程师",
    "created_at": "2024-01-01",
    "updated_at": "2024-01-01"
}
```

### Experience
工作经历

```python
{
    "id": 1,
    "user_id": 1,
    "title": "后端工程师",
    "company": "字节跳动",
    "description": "...",
    "start_date": "2022-01",
    "end_date": "2024-01",
    "is_current": false,
    "created_at": "2024-01-01"
}
```

### Skill
技能记录

```python
{
    "id": 1,
    "user_id": 1,
    "skill_name": "Python",
    "level": "advanced",  # beginner, intermediate, advanced, expert
    "years": 3.5,
    "source": "auto_generated",  # auto_generated, manual, inferred
    "created_at": "2024-01-01"
}
```

### Job
职位信息

```python
{
    "id": 1,
    "job_id": "lagou_12345",
    "title": "高级 Python 工程师",
    "company": "字节跳动",
    "location": "北京",
    "salary_min": 30,
    "salary_max": 50,
    "job_description": "...",
    "source": "lagou",
    "source_url": "https://...",
    "required_skills": ["Python", "Go", "Kubernetes"],
    "experience_required": "5+",
    "job_type": "full-time",
    "created_at": "2024-01-01"
}
```

### Resume
简历记录

```python
{
    "id": 1,
    "user_id": 1,
    "title": "通用简历",
    "content": "# 张三...",  # Markdown 格式
    "template": "standard",
    "target_job_id": null,
    "is_default": true,
    "created_at": "2024-01-01"
}
```

## 🔄 数据流

### 流程 1：从经历生成技能

```
用户输入经历描述
    ↓
SkillGenerator.extract_skills_from_experience()
    ↓
LLMService.generate_json()
    ↓
调用 LLM API（OpenAI/DeepSeek）
    ↓
解析返回的技能数据
    ↓
保存到数据库
    ↓
返回给用户
```

### 流程 2：匹配职位

```
用户查询职位
    ↓
JobMatcher.match_user_to_single_job()
    ↓
提取用户技能 + 职位 JD
    ↓
LLMService.match_user_to_job()
    ↓
调用 LLM API
    ↓
返回匹配度评分和详细分析
    ↓
用户查看结果
```

### 流程 3：生成定制化简历

```
用户选择目标职位
    ↓
获取用户个人资料
    ↓
获取职位描述
    ↓
ResumeAnalyzer.tailor_resume_for_job()
    ↓
LLMService.generate_resume()
    ↓
调用 LLM API
    ↓
返回定制化简历（Markdown）
    ↓
用户可编辑或下载
```

## 🔐 安全性考虑

1. **API Key 管理**
   - 环境变量存储 API Key
   - 不在代码中硬编码 Key
   - `.env` 文件添加到 `.gitignore`

2. **数据隐私**
   - 本地存储所有用户数据
   - 使用加密连接与 LLM API 通信
   - 支持数据导出和删除

3. **输入验证**
   - 所有用户输入都经过验证
   - 防止 SQL 注入（ORM 自动保护）
   - 限制请求大小

## 🚀 性能优化

1. **缓存策略**
   - 职位分析结果缓存
   - 技能提取结果缓存
   - 减少重复的 LLM 调用

2. **异步处理**
   - 使用 FastAPI 异步端点
   - 支持后台任务处理
   - 并发处理多个请求

3. **数据库优化**
   - 合理的索引设计
   - 查询优化
   - 连接池管理

## 📈 未来扩展

1. **Web 前端**
   - React + TypeScript
   - 实时预览
   - 拖拽式简历编辑

2. **职位爬虫**
   - 支持拉勾、BOSS、脉脉
   - 定时爬虫任务
   - 数据去重

3. **高级功能**
   - 面试题库
   - 薪资数据库
   - 公司评价聚合
   - 职业路径推荐
   - 本地 LLM 支持

4. **集成**
   - Slack 集成
   - 日历同步
   - 邮件提醒

---

更新时间：2024-01-01
