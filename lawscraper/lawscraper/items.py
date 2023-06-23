# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LawscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# class LawSection(crapy.Item):
#     section_title = scrapy.Field()
#     section_content = scrapy.Field()

class LawItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    committee = scrapy.Field()
    summary = scrapy.Field()
    # chapter = scrapy.Field()