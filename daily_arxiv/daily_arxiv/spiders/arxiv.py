import scrapy
import os
import urllib.parse
from datetime import datetime, timedelta
from daily_arxiv.items import DailyArxivItem


class ArxivSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 计算前一天的日期
        yesterday = datetime.now() - timedelta(days=1)
        self.yesterday_str = yesterday.strftime('%Y%m%d')
        self.date_query_filter = f"announced_date_first:[{self.yesterday_str} TO {self.yesterday_str}]"

        categories = os.environ.get("CATEGORIES", "cs.CV")
        categories = categories.split(",") if categories else []
        categories = list(map(str.strip, categories))
        self.categories_query_part = " OR ".join(
            [f"cat:{cat}" for cat in categories])
        if self.categories_query_part:
            self.categories_query_part = f"({self.categories_query_part})"

        keywords_str = os.environ.get("KEYWORDS", "")
        self.keywords = [k.strip() for k in keywords_str.split(
            ',') if k.strip()] if keywords_str else []

        self.start_urls = []
        self.current_keyword_map = {}

        if self.keywords:
            for keyword in self.keywords:
                search_terms = [f"ti:\"{keyword}\" OR abs:\"{keyword}\""]
                if self.categories_query_part:
                    search_terms.append(self.categories_query_part)
                search_terms.append(self.date_query_filter)

                query = " AND ".join(search_terms)
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term={encoded_query}&terms-0-field=all&classification-include_archive_aliases=include&date-filter_by=date_range&date-year=&date-from_date={self.yesterday_str}&date-to_date={self.yesterday_str}&date-date_type=submitted_date_first&abstracts=show&size=50&order=-announced_date_first"
                self.start_urls.append(search_url)
                self.current_keyword_map[search_url] = keyword
        elif self.categories_query_part:
            search_terms = [self.categories_query_part, self.date_query_filter]
            query = " AND ".join(search_terms)
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term={encoded_query}&terms-0-field=all&classification-include_archive_aliases=include&date-filter_by=date_range&date-year=&date-from_date={self.yesterday_str}&date-to_date={self.yesterday_str}&date-date_type=submitted_date_first&abstracts=show&size=50&order=-announced_date_first"
            self.start_urls.append(search_url)
            self.current_keyword_map[search_url] = ""
        else:
            query = self.date_query_filter
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=all&classification-include_archive_aliases=include&date-filter_by=date_range&date-year=&date-from_date={self.yesterday_str}&date-to_date={self.yesterday_str}&date-date_type=submitted_date_first&abstracts=show&size=50&order=-announced_date_first"
            self.start_urls.append(search_url)
            self.current_keyword_map[search_url] = ""

        self.max_papers_per_keyword = os.environ.get("MAX_PAPERS_PER_KEYWORD")
        if self.max_papers_per_keyword:
            self.max_papers_per_keyword = int(self.max_papers_per_keyword)
        else:
            self.max_papers_per_keyword = float('inf')

    name = "arxiv"
    allowed_domains = ["arxiv.org"]

    def parse(self, response):
        papers_count = 0
        current_keyword = self.current_keyword_map.get(response.url, "")

        for paper_item in response.css("li.arxiv-result"):
            paper_link_tag = paper_item.css("p.list-title a[href*='/abs/']")
            paper_link = paper_link_tag.attrib.get('href')

            if not paper_link:
                self.logger.warning(
                    f"Could not find paper link in item: {paper_item.get()}")
                continue

            paper_id = paper_link.split('/')[-1]

            title = paper_item.css("p.title.is-5 ::text").get()
            if title:
                title = title.strip()
            else:
                self.logger.warning(
                    f"Could not find title for paper ID {paper_id}")
                title = "N/A"

            authors_list = paper_item.css("p.authors a ::text").getall()
            # Limit to two authors
            authors = [author.strip() for author in authors_list[:2]]

            # Attempt to extract institution (often not directly available on search page)
            # This is a placeholder and might need more advanced parsing or visiting abstract page
            institution = "N/A" 
            # A more robust solution would involve visiting the abstract page or using a library like scholarly

            summary = paper_item.css("span.abstract-full.has-text-grey-darker::text").get()
            if summary:
                summary = summary.strip()
            else:
                self.logger.warning(
                    f"Could not find summary for paper ID {paper_id}")
                summary = "N/A"

            primary_category_tag = paper_item.css(
                "div.tags span.tag.is-primary ::text")
            primary_category = primary_category_tag.get(
            ).strip() if primary_category_tag else "N/A"

            all_categories_tags = paper_item.css("div.tags span.tag ::text")
            all_categories = [tag.get().strip(
            ) for tag in all_categories_tags if tag.get().strip() != primary_category]
            if primary_category != "N/A" and primary_category not in all_categories:
                all_categories.insert(0, primary_category)

            if papers_count >= self.max_papers_per_keyword:
                self.logger.info(
                    f"Reached max_papers_per_keyword ({self.max_papers_per_keyword}) for keyword/query: '{current_keyword if current_keyword else 'general date query'}'")
                break

            papers_count += 1
            item = DailyArxivItem()
            item['id'] = paper_id
            item['title'] = title
            item['authors'] = authors
            item['institution'] = institution
            item['summary'] = summary
            item['abs'] = paper_link
            item['categories'] = all_categories
            # item['keyword'] = current_keyword # This is not part of DailyArxivItem
            yield item

        next_page_url_suffix = response.css(
            "a.pagination-next ::attr(href)").get()
        if next_page_url_suffix and papers_count < self.max_papers_per_keyword:
            next_page_url = response.urljoin(next_page_url_suffix)
            self.current_keyword_map[next_page_url] = current_keyword
            yield scrapy.Request(next_page_url, callback=self.parse)