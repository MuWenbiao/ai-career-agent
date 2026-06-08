"""
职位爬虫模块
支持拉勾、BOSS直聘、脉脉、智联招聘等国内主流招聘平台
"""
import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from loguru import logger
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import json


class JobScraper:
    """通用职位爬虫基类"""

    # User-Agent 列表（防反爬）
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    ]

    # 代理池（需要实际的代理服务）
    PROXIES = [
        # 格式: 'http://ip:port' 或 'http://user:pass@ip:port'
        # 您可以使用免费代理或付费代理服务
    ]

    def __init__(self):
        self.session = None
        self.scraped_jobs = set()  # 用于去重
        self.errors = []

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def get_headers(self) -> Dict[str, str]:
        """获取随机 User-Agent 的请求头"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_proxy(self) -> Optional[str]:
        """获取随机代理"""
        if self.PROXIES:
            return random.choice(self.PROXIES)
        return None

    async def fetch(self, url: str, **kwargs) -> Optional[str]:
        """获取页面内容"""
        try:
            headers = self.get_headers()
            proxy = self.get_proxy()
            
            # 随机延迟（避免被检测）
            await asyncio.sleep(random.uniform(1, 3))
            
            async with self.session.get(
                url,
                headers=headers,
                proxy=proxy,
                timeout=aiohttp.ClientTimeout(total=10),
                **kwargs
            ) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}, status: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            self.errors.append(f"Timeout: {url}")
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching {url}: {e}")
            self.errors.append(f"Client error: {url}, {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            self.errors.append(f"Error: {url}, {str(e)}")
        
        return None

    def normalize_job(self, job: Dict[str, Any], source: str) -> Dict[str, Any]:
        """标准化职位数据"""
        job_hash = f"{job.get('title', '')}_{job.get('company', '')}_{job.get('location', '')}"
        
        if job_hash in self.scraped_jobs:
            return None  # 去重
        
        self.scraped_jobs.add(job_hash)
        
        return {
            'job_id': job.get('job_id', ''),
            'title': job.get('title', '').strip(),
            'company': job.get('company', '').strip(),
            'location': job.get('location', '').strip(),
            'salary_min': job.get('salary_min'),
            'salary_max': job.get('salary_max'),
            'job_description': job.get('job_description', '').strip(),
            'source': source,
            'source_url': job.get('source_url', ''),
            'experience_required': job.get('experience_required', ''),
            'education_required': job.get('education_required', ''),
            'job_type': job.get('job_type', ''),
            'posted_date': job.get('posted_date'),
            'created_at': datetime.now().isoformat(),
        }

    async def scrape(self, keyword: str, **kwargs) -> List[Dict[str, Any]]:
        """爬虫方法 - 由子类实现"""
        raise NotImplementedError


class LagouScraper(JobScraper):
    """拉勾网职位爬虫"""

    async def scrape(self, keyword: str, city: str = "全国", pages: int = 5) -> List[Dict[str, Any]]:
        """
        爬取拉勾网职位
        
        Args:
            keyword: 职位关键词
            city: 城市
            pages: 爬取页数
        
        Returns:
            职位列表
        """
        jobs = []
        logger.info(f"Starting to scrape Lagou: {keyword} in {city}")
        
        for page in range(1, pages + 1):
            try:
                # 拉勾网使用 API 接口（更稳定）
                url = "https://api.lagou.com/jobs/list_pc"
                
                data = {
                    'city': city,
                    'needAddtionalResult': False,
                    'pageNo': page,
                    'pageSize': 15,
                    'positionAdvantage': '',
                    'positionExp': '',
                    'positionLables': [],
                    'positionName': keyword,
                    'salary': '',
                    'workYear': '',
                }
                
                headers = self.get_headers()
                headers['X-Requested-With'] = 'XMLHttpRequest'
                headers['Referer'] = 'https://www.lagou.com/jobs/list_'
                
                # 发送 POST 请求
                async with self.session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        try:
                            result = await response.json()
                            if result.get('success'):
                                job_list = result.get('content', {}).get('pageResults', [])
                                
                                for job_item in job_list:
                                    job = {
                                        'job_id': f"lagou_{job_item.get('positionId', '')}",
                                        'title': job_item.get('positionName', ''),
                                        'company': job_item.get('companyFullName', ''),
                                        'location': f"{job_item.get('city', '')}-{job_item.get('district', '')}",
                                        'salary_min': self.parse_salary(job_item.get('salary', ''))[0],
                                        'salary_max': self.parse_salary(job_item.get('salary', ''))[1],
                                        'job_description': job_item.get('positionAdvantage', ''),
                                        'source_url': f"https://www.lagou.com/jobs/{job_item.get('positionId', '')}.html",
                                        'experience_required': job_item.get('workYear', ''),
                                        'education_required': job_item.get('education', ''),
                                        'job_type': job_item.get('jobNature', ''),
                                        'posted_date': datetime.fromtimestamp(job_item.get('createTime', 0) / 1000).isoformat() if job_item.get('createTime') else None,
                                    }
                                    
                                    normalized = self.normalize_job(job, 'lagou')
                                    if normalized:
                                        jobs.append(normalized)
                            else:
                                logger.warning(f"Lagou API returned success=false on page {page}")
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON from Lagou page {page}")
                    else:
                        logger.warning(f"Lagou returned status {response.status} on page {page}")
                
                # 随机延迟
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"Error scraping Lagou page {page}: {e}")
                self.errors.append(f"Lagou page {page}: {str(e)}")
                continue
        
        logger.info(f"Scraped {len(jobs)} jobs from Lagou")
        return jobs

    @staticmethod
    def parse_salary(salary_str: str) -> tuple:
        """解析薪资范围"""
        try:
            if not salary_str or '万' not in salary_str:
                return (None, None)
            
            salary_str = salary_str.replace('k', '').replace('K', '')
            parts = salary_str.split('-')
            
            if len(parts) == 2:
                salary_min = float(parts[0].replace('万', '')) * 10
                salary_max = float(parts[1].replace('万', '')) * 10
                return (salary_min, salary_max)
        except:
            pass
        
        return (None, None)


class BOSSScraper(JobScraper):
    """BOSS直聘职位爬虫"""

    async def scrape(self, keyword: str, city: str = "全国", pages: int = 5) -> List[Dict[str, Any]]:
        """爬取 BOSS 直聘职位"""
        jobs = []
        logger.info(f"Starting to scrape BOSS: {keyword} in {city}")
        
        # BOSS 直聘使用前端渲染，需要使用 Playwright 或 Selenium
        logger.warning("BOSS direct scraping requires browser automation (Playwright/Selenium)")
        logger.info("Recommended: Use Playwright for dynamic content")
        
        # 这里返回空列表，实际使用需要集成 Playwright
        return jobs


class MaimaiScraper(JobScraper):
    """脉脉职位爬虫"""

    async def scrape(self, keyword: str, city: str = "全国", pages: int = 5) -> List[Dict[str, Any]]:
        """爬取脉脉职位"""
        jobs = []
        logger.info(f"Starting to scrape Maimai: {keyword} in {city}")
        
        # 脉脉使用 GraphQL API
        logger.warning("Maimai uses GraphQL API and requires authentication")
        
        # 这里返回空列表，实际实现需要处理认证
        return jobs


class Zhilian Scraper(JobScraper):
    """智联招聘职位爬虫"""

    async def scrape(self, keyword: str, city: str = "全国", pages: int = 5) -> List[Dict[str, Any]]:
        """爬取智联招聘职位"""
        jobs = []
        logger.info(f"Starting to scrape Zhilian: {keyword} in {city}")
        
        for page in range(1, pages + 1):
            try:
                # 智联招聘 API
                url = f"https://api.zhaopin.com/jobs/search"
                
                params = {
                    'keyword': keyword,
                    'city': city,
                    'pageNo': page,
                    'pageSize': 30,
                }
                
                content = await self.fetch(url, params=params)
                if content:
                    try:
                        result = json.loads(content)
                        # 解析响应数据
                        # 根据实际 API 格式调整
                        logger.info(f"Fetched page {page} from Zhilian")
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON from Zhilian")
                
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"Error scraping Zhilian page {page}: {e}")
                self.errors.append(f"Zhilian page {page}: {str(e)}")
        
        return jobs


class JobScraperManager:
    """职位爬虫管理器 - 协调多个爬虫"""

    def __init__(self):
        self.scrapers = {
            'lagou': LagouScraper(),
            'boss': BOSSScraper(),
            'maimai': MaimaiScraper(),
            'zhilian': Zhilian Scraper(),
        }

    async def scrape_all(
        self,
        keyword: str,
        cities: List[str] = None,
        sources: List[str] = None,
        pages: int = 3,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        从多个源并发爬取职位
        
        Args:
            keyword: 职位关键词
            cities: 城市列表
            sources: 爬虫源列表 (lagou, boss, maimai, zhilian)
            pages: 每个源的爬取页数
        
        Returns:
            {source: [jobs]}
        """
        if cities is None:
            cities = ["北京", "上海", "杭州", "深圳"]
        
        if sources is None:
            sources = list(self.scrapers.keys())
        
        results = {}
        tasks = []
        
        logger.info(f"Starting to scrape {len(sources)} sources for keyword: {keyword}")
        
        for source in sources:
            if source not in self.scrapers:
                logger.warning(f"Unknown source: {source}")
                continue
            
            scraper = self.scrapers[source]
            
            for city in cities:
                task = scraper.scrape(
                    keyword=keyword,
                    city=city,
                    pages=pages,
                )
                tasks.append((source, city, task))
        
        # 并发执行所有爬虫任务
        for source, city, task in tasks:
            try:
                jobs = await task
                if source not in results:
                    results[source] = []
                results[source].extend(jobs)
                logger.info(f"Scraped {len(jobs)} jobs from {source} ({city})")
            except Exception as e:
                logger.error(f"Error scraping {source} ({city}): {e}")
        
        return results

    async def scrape_continuous(
        self,
        keyword: str,
        interval_hours: int = 24,
        max_iterations: int = None,
    ):
        """
        持续爬虫（定时任务）
        
        Args:
            keyword: 职位关键词
            interval_hours: 爬虫间隔（小时）
            max_iterations: 最大迭代次数
        """
        iteration = 0
        
        while max_iterations is None or iteration < max_iterations:
            logger.info(f"Starting scraping iteration {iteration + 1} at {datetime.now()}")
            
            results = await self.scrape_all(keyword)
            
            # 保存结果到数据库
            total_jobs = sum(len(jobs) for jobs in results.values())
            logger.info(f"Scraped {total_jobs} total jobs")
            
            iteration += 1
            
            if max_iterations is None or iteration < max_iterations:
                logger.info(f"Next scraping in {interval_hours} hours")
                await asyncio.sleep(interval_hours * 3600)
