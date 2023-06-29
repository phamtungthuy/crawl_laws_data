import scrapy
from lawscraper.items import LawItem


class LawspiderSpider(scrapy.Spider):
    name = "lawspider"
    allowed_domains = ["thuvienphapluat.vn"]
    start_urls = ["https://thuvienphapluat.vn/page/tim-van-ban.aspx"]
    chapters = []
    sections = []
    custom_settings = {
        'FEEDS': {
            'vanbanphapluat1.json': {
                'format': 'json',
                'overwrite': True
            }
        }
    }
    
    def int_to_roman(self, num):
    # Mảng chứa các giá trị và ký hiệu của số La Mã
        roman_map = [
            (1000, 'M'),
            (900, 'CM'),
            (500, 'D'),
            (400, 'CD'),
            (100, 'C'),
            (90, 'XC'),
            (50, 'L'),
            (40, 'XL'),
            (10, 'X'),
            (9, 'IX'),
            (5, 'V'),
            (4, 'IV'),
            (1, 'I')
        ]

        roman_num = ''
        for value, symbol in roman_map:
            while num >= value:
                roman_num += symbol
                num -= value

        return roman_num
    
    def handleClauses(self, law_item, text_arrays, start, end):
        count = 1
        clauses = []
        current_clause_title = ''
        current_clause_content = []
        for i in range(start, end):
            if text_arrays[i].find(f'{count}.') == 0:
                if current_clause_title != '':
                    clauses.append({current_clause_title: current_clause_content})
                current_clause_title = text_arrays[i]
                current_clause_content = []
                count += 1
            else:
                current_clause_content.append(text_arrays[i])
        if current_clause_title != '':
            clauses.append({current_clause_title: current_clause_content})
        elif clauses == [] and current_clause_content != []:
          clauses.append(current_clause_content)  
        return clauses     
               
    def handleSections(self, law_item, text_arrays, start, end):
        arr = []
        check = False
        count = 1
        for i in range(start, end):
            if text_arrays[i].find('Điều') == 0 or text_arrays[i].find(f'{self.int_to_roman(count)}.') == 0:
                # if(len(text_arrays[i].split()) == 2):
                #     arr.append(((text_arrays[i] + text_arrays[i + 1]), i))
                #     check = True
            # else: 
                arr.append((text_arrays[i], i))
                count += 1
        sections = []
        if arr == []:
            sections = self.handleClauses(law_item, text_arrays, start, end)
        else:
            sections = []
            for i in range(len(arr)):
                if i < len(arr) - 1:
                    sections.append({arr[i][0]: self.handleClauses(law_item, text_arrays, arr[i][1] + (2 if check == True else 1), arr[i + 1][1])})
                else:
                    sections.append({arr[i][0]: self.handleClauses(law_item, text_arrays, arr[i][1] + (2 if check == True else 1), end)})
        return sections
    
    def handleChapters(self, law_item, text_arrays, start, end):
        chapters = []
        for i in range(start, end):
            if text_arrays[i].find('Chương') == 0:
                chapters.append(i)
        if chapters == []:
            law_item['chapters'] = self.handleSections(law_item, text_arrays, start, end)
        else:
            law_item['chapters'] = []
            for i in range(len(chapters)):
                if i < len(chapters) - 1:
                    law_item['chapters'].append({f'Chương {i + 1}': self.handleSections(law_item, text_arrays, chapters[i], chapters[i + 1])})
                else:
                    law_item['chapters'].append({f'Chương {i + 1}': self.handleSections(law_item, text_arrays, chapters[i], end)})
        
    
    def handleQuyetDinh(self, law_item, text_arrays):
        content_index = 0;
        for i in range(3, len(text_arrays)):
            if 'QUYẾT ĐỊNH' in text_arrays[i]:
                content_index = i + 1
                break
            law_item['summary'].append(text_arrays[i])
        self.handleChapters(law_item, text_arrays, content_index, len(text_arrays))
    
    def handleNghiDinh(self, law_item, text_arrays):
        content_index = 0;
        for i in range(2, len(text_arrays)):
            if 'QUY ĐỊNH CHUNG' in text_arrays[i]:
                content_index = i + 1
                break
            elif text_arrays[i].find('Điều') == 0 or text_arrays[i].find('Chương') == 0 or text_arrays[i].find('I. ') == 0:
               content_index = i 
               break 
            law_item['summary'].append(text_arrays[i])
        self.handleChapters(law_item, text_arrays, content_index, len(text_arrays))
    
    def parse(self, response):
        laws = response.css('p.nqTitle')
        
        for law in laws:
            law_url = law.css("a ::attr('href')").get()
            yield response.follow(law_url, callback = self.parse_law_page, 
                                  meta ={"proxy": "http://phamtungthuy-rotate:tungthuy47@p.webshare.io:80"})

        next_page_text = response.css('.cmPager a:last-child ::text').get()
        next_page_url = response.css('.cmPager a:last-child ::attr(href)').get()
        if int(next_page_url.split('=')[-1]) > 10:
            return
        if next_page_url is not None and next_page_text is not None and 'Trang sau' in next_page_text:
            next_page_url = 'https://thuvienphapluat.vn/page/' + next_page_url
            yield response.follow(next_page_url, callback = self.parse, 
                                  meta ={"proxy": "http://phamtungthuy-rotate:tungthuy47@p.webshare.io:80"})
    
    
    
    
    def parse_law_page(self, response):
        value = response.css(".content1 div:first-child b:nth-of-type(1)").get()
        if value is not None and 'Văn bản này đang cập nhật Nội dung' in value:
            return
        tmp = response.xpath("//div[@id='tab1']//div[@class='content1']/div/div/div/p")
        if tmp == []: tmp = response.xpath("//div[@id='tab1']//div[@class='content1']/div/div/p")
        law_item = LawItem()
        law_item['url'] = response.url
        # law_item['title'] = response.xpath("//div[@id='tab1']//div[@class='content1']//p[3]//text()").get().replace('\r\n', ' ')
        law_item['committee'] =  ''.join(map(str, response.xpath("//div[@id='tab1']//div[@class='content1']//table[1]/tr[2]/td[1]//text()").extract()[:2])).strip().replace('\r\n', ' ')
        text_arrays = []
        for p in tmp:
            arrays = p.xpath(".//text()").extract()
            arrays = [text.replace('\r\n', ' ') for text in arrays if text.strip().strip() != '']
            p_string = ' '.join(arrays)
            if p_string != '':
                text_arrays.append(' '.join(arrays))
        if text_arrays != []:
            print('Test: ', text_arrays[0])
            law_item['type'] = text_arrays[0]
            law_item['title'] = text_arrays[1]
            law_item['summary'] = [];
            if law_item['type']== "QUYẾT ĐỊNH":
                self.handleQuyetDinh(law_item, text_arrays)
            elif law_item['type'] == 'NGHỊ ĐỊNH' or law_item['type'] == 'KẾ HOẠCH' or law_item['type'] == 'THÔNG TƯ':
                self.handleNghiDinh(law_item, text_arrays)
        yield law_item
        
