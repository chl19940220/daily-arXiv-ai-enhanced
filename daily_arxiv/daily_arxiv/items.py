# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DailyArxivItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    institution = scrapy.Field()
    summary = scrapy.Field()
    abs = scrapy.Field()
    categories = scrapy.Field()