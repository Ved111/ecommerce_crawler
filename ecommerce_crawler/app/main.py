from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
from app.crawler import ProductURLCrawler

app = FastAPI()

# In-memory storage for results
crawl_results = {}

# Input model for API
class CrawlRequest(BaseModel):
    domains: List[str]
    max_depth: int = 2

@app.post("/start-crawl/")
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    global crawl_results

    # Start the crawler in the background
    crawler = ProductURLCrawler(domains=request.domains, max_depth=request.max_depth)
    background_tasks.add_task(crawler.start_crawling)  

  # You may want to store results in a non-callable way (i.e., list or dict)
    # If the `crawler.results` is not directly callable, you can just store it as a dictionary
    crawl_results = dict()  # Initializing it in a safer manner for async handling.
    return {"message": "Crawling started for the provided domains"}

@app.get("/results/")
async def get_results():
    return crawl_results

@app.get("/status/")
async def get_status():
    return {"total_domains": len(crawl_results), 
            "total_urls_found": sum(len(urls) for urls in crawl_results.values())}
