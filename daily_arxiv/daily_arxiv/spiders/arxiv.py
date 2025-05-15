import scrapy
import os
import urllib.parse


class ArxivSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = os.environ.get("CATEGORIES", "cs.CV")
        categories = categories.split(",")
        categories = list(map(str.strip, categories))
        self.categories_query = " OR ".join([f"cat:{cat}" for cat in categories]) if categories else ""
        
        # 获取搜索关键词列表
        keywords_str = os.environ.get("KEYWORDS", "")
        self.keywords = [k.strip() for k in keywords_str.split(',') if k.strip()] if keywords_str else []
        
        # 构建起始URLs
        self.start_urls = []
        
        # 如果有关键词，为每个关键词构建独立的搜索URL
        if self.keywords:
            for keyword in self.keywords:
                # 如果同时有分类限制，就在分类内搜索关键词
                if self.categories_query:
                    query = f"{keyword} AND ({self.categories_query})"
                else:
                    query = keyword
                    
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://arxiv.org/search/?query={encoded_query}&searchtype=all&source=header"
                self.start_urls.append(search_url)
        else:
            # 无关键词时保持原来的行为：获取各分类的最新论文
        self.start_urls = [
            f"https://arxiv.org/list/{cat}/new" for cat in categories
            ]
        
        # 获取论文数量限制 (针对每个关键词)
        self.max_papers_per_keyword = os.environ.get("MAX_PAPERS_PER_KEYWORD")
        if self.max_papers_per_keyword:
            self.max_papers_per_keyword = int(self.max_papers_per_keyword)

        # 记录当前正在处理的关键词
        self.current_keyword = {}
        for i, url in enumerate(self.start_urls):
            if i < len(self.keywords):
                self.current_keyword[url] = self.keywords[i]
            else:
                # 对于分类URLs，关键词为空
                self.current_keyword[url] = ""

    name = "arxiv"
    allowed_domains = ["arxiv.org"]

    def parse(self, response):
        papers_count = 0
        
        # 判断当前URL对应的关键词
        current_keyword = self.current_keyword.get(response.url, "")
        
        # 检查我们是在搜索结果页面还是分类列表页面
        if "/search/" in response.url:
            # 搜索结果页面的解析
            for paper in response.css("li.arxiv-result"):
                # 提取论文ID和链接
                paper_link = paper.css("p.list-title a::attr(href)").get()
                if paper_link:
                    paper_id = paper_link.split('/')[-1]
                else:
                    continue
                    
                # 如果达到了每个关键词的最大论文数，停止
                if self.max_papers_per_keyword and papers_count >= self.max_papers_per_keyword:
                    break
                
                papers_count += 1
                yield {
                    "id": paper_id,
                    "keyword": current_keyword  # 添加关键词信息
                }
                
            # 检查是否有下一页，如果有且没有达到论文数量限制，则继续抓取
            next_page = response.css('a.pagination-next::attr(href)').get()
            if next_page and (not self.max_papers_per_keyword or papers_count < self.max_papers_per_keyword):
                next_url = response.urljoin(next_page)
                self.current_keyword[next_url] = current_keyword  # 记录下一页的关键词
                yield scrapy.Request(next_url, callback=self.parse)
                
        else:
            # 原始的分类列表页面解析
        anchors = []
        for li in response.css("div[id=dlpage] ul li"):
                anchor_href = li.css("a::attr(href)").get()
                if anchor_href:
                    anchors.append(int(anchor_href.split("item")[-1]))

            if not anchors:
                return

        for paper in response.css("dl dt"):
                item_name = paper.css("a[name^='item']::attr(name)").get()
                if not item_name:
                    continue
                    
                if int(item_name.split("item")[-1]) >= anchors[-1]:
                continue

                # 如果达到了最大论文数，停止
                if self.max_papers_per_keyword and papers_count >= self.max_papers_per_keyword:
                    break
                    
                papers_count += 1
                paper_id = paper.css("a[title='Abstract']::attr(href)").get()
                if paper_id:
                    paper_id = paper_id.split("/")[-1]
            yield {
                        "id": paper_id,
                        "category": response.url.split("/")[-2]  # 添加分类信息
            }
