import scrapy
from lawscraper.items import LawItem


class LawspiderSpider(scrapy.Spider):
    name = "lawspider"
    allowed_domains = ["thuvienphapluat.vn"]
    start_urls = ["https://thuvienphapluat.vn/page/tim-van-ban.aspx"]
    
    custom_settings = {
        'FEEDS': {
            'vanbanphapluat.json': {
                'format': 'json',
                'overwrite': True
            }
        }
    }
    
    def parse(self, response):
        laws = response.css('p.nqTitle')
        
        for law in laws:
            law_url = law.css("a ::attr('href')").get()
            yield response.follow(law_url, callback = self.parse_law_page)

        next_page_text = response.css('.cmPager a:last-child ::text').get()
        next_page_url = response.css('.cmPager a:last-child ::attr(href)').get()
        if int(next_page_url.split('=')[-1]) > 1:
            return
        if next_page_url is not None and next_page_text is not None and 'Trang sau' in next_page_text:
            next_page_url = 'https://thuvienphapluat.vn/page/' + next_page_url
            print('*********next_page*************')
            print(next_page_text, next_page_url, int(next_page_url.split('=')[-1]))
            yield response.follow(next_page_url, callback = self.parse)
            
    def parse_law_page(self, response):
        value = response.css(".content1 div:first-child b:nth-of-type(1)").get()
        if value is not None and 'Văn bản này đang cập nhật Nội dung' in value:
            return
        law_item = LawItem()
        law_item['url'] = response.url
        law_item['title'] = response.xpath("//div[@id='tab1']//div[@class='content1']//p[3]//text()").get()
        law_item['committee'] =  ''.join(map(str, response.xpath("//div[@id='tab1']//div[@class='content1']//table[1]/tr[2]/td[1]//text()").extract()[:2])).strip()
        
        yield law_item