import scrapy
import os
import urllib.parse


class ArxivSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = os.environ.get("CATEGORIES", "cs.CV")
        categories = categories.split(",")
        categories = list(map(str.strip, categories))
        
        # 获取搜索关键词
        self.keywords = os.environ.get("KEYWORDS", "")
        
        # 如果有关键词，构建搜索URL
        if self.keywords:
            # 构建查询字符串：关键词 AND (分类1 OR 分类2 OR ...)
            categories_query = " OR ".join([f"cat:{cat}" for cat in categories])
            if categories_query:
                query = f"{self.keywords} AND ({categories_query})"
            else:
                query = self.keywords
                
            encoded_query = urllib.parse.quote(query)
            self.start_urls = [f"https://arxiv.org/search/?query={encoded_query}&searchtype=all&source=header"]
        else:
            # 无关键词时保持原来的行为：获取各分类的最新论文
            self.start_urls = [
                f"https://arxiv.org/list/{cat}/new" for cat in categories
            ]
        
        # 获取论文数量限制
        self.max_papers = os.environ.get("MAX_PAPERS")
        if self.max_papers:
            self.max_papers = int(self.max_papers)

    name = "arxiv"
    allowed_domains = ["arxiv.org"]

    def parse(self, response):
        papers_count = 0
        
        # 检查我们是在搜索结果页面还是分类列表页面
        if "/search/" in response.url:
            # 搜索结果页面的解析
            for paper in response.css("li.arxiv-result"):
                # 提取论文ID
                paper_id = paper.css("p.list-title a::text").get()
                if paper_id:
                    paper_id = paper_id.strip()
                    
                # 如果达到了最大论文数，停止
                if self.max_papers and papers_count >= self.max_papers:
                    break
                
                papers_count += 1
                yield {
                    "id": paper_id,
                }
        else:
            # 原始的分类列表页面解析
            anchors = []
            for li in response.css("div[id=dlpage] ul li"):
                anchors.append(int(li.css("a::attr(href)").get().split("item")[-1]))

            for paper in response.css("dl dt"):
                if (
                    int(paper.css("a[name^='item']::attr(name)").get().split("item")[-1])
                    >= anchors[-1]
                ):
                    continue
                    
                # 如果达到了最大论文数，停止
                if self.max_papers and papers_count >= self.max_papers:
                    break
                    
                papers_count += 1
                yield {
                    "id": paper.css("a[title='Abstract']::attr(href)")
                    .get()
                    .split("/")[-1],
                }
