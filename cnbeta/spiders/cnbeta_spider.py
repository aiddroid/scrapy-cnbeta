# -*- coding: utf-8 -*-

# Define here the spiders
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spiders.html

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, FormRequest
from scrapy.contrib.spiders import CrawlSpider, Rule
from cnbeta.items import CnbetaItem


class CnbetaSpider(scrapy.Spider):
    name = "cnbeta"
    allowed_domains = ["cnbeta.com"]
    start_urls = ["http://m.cnbeta.com/mobile/wap"]
    meta = {'cookiejar':1}
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    }

    def parse(self, response):
        print '===length:%s===' % len(response.body)
        print '===message:%s===' % response.status
        listItems = self.parse_list_page(response)
        for item in listItems:
            print item
            yield scrapy.Request(item['url'], meta = self.meta, headers = self.headers, callback = self.parse_article)

        for href in response.xpath('//div[@class="pages"]/a[@class="page-next"]/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, meta = self.meta, headers = self.headers, callback = self.parse)

    def parse_list_page(self,response):
        items = []
        for sel in response.xpath('//div[@class="list"]/a'):
            title = sel.xpath('span[1]/text() | text()').extract()[0].encode('utf-8')
            url = sel.xpath('@href').extract()[0].encode('utf-8')
            url = response.urljoin(url)
            items.append({'title':title,'url':url})
        return items

    def parse_article(self,response):
        title = response.xpath('//div[@class="title"]/b[1]/text()').extract()[0].encode('utf-8').strip()
        time = response.xpath('//div[@class="time"]/span[1]/text()').extract()[0].encode('utf-8').replace('发布日期:','').strip()
        source = response.xpath('//div[@class="time"]/span[2]/a[1]/text() | //div[@class="time"]/span[2]/text()').extract()
        source = ''.join(source).encode('utf-8').replace('稿源：','').strip()
        content = response.xpath('//div[@class="content"]').extract()[0].encode('utf-8')
        
        article = CnbetaItem()
        article['url'] = response.url
        article['title'] = title
        article['time'] = time
        article['source'] = source
        article['content'] = content

        print time + ' ' + source + ' ' + title
        return article
