# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LawscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class LawItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    committee = scrapy.Field()
    summary = scrapy.Field()
    type = scrapy.Field()
    chapters = scrapy.Field()
    # sections = scrapy.Field()
    # clauses = scrapy.Field()