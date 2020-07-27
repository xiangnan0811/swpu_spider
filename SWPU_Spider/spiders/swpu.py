# -*- coding: utf-8 -*-
import re
import scrapy
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from SWPU_Spider.items import SwpuSpiderItem


class SwpuSpider(CrawlSpider):
    name = 'swpu'
    allowed_domains = ['www.swpu.edu.cn']
    start_urls = ['http://www.swpu.edu.cn/jgsz/xysz.htm']

    rules = (
        Rule(LinkExtractor(allow=r'swpu.edu.cn/[a-zA-Z]+/?'), callback='parse_link', follow=True),
        Rule(LinkExtractor(allow=r'swpu.edu.cn/[a-zA-Z]+/[a-zA-Z]+/\d+/\d+\.htm'), callback='parse_item', follow=True),
    )

    def parse_link(self, response):
        urls = re.findall(r'href="([a-zA-Z]+/\d+/\d+\.htm)"', response.text, re.S)
        for url in urls:
            item_url = response.urljoin(url)
            yield scrapy.Request(url=item_url, callback=self.parse_item)

    def parse_item(self, response):
        item = SwpuSpiderItem()
        time = None
        item['title'] = response.xpath('//h3[@align="center"]/text()').get()
        if not item['title']:
            item['title'] = response.xpath('//h1[@align="center"]/text()').get()
        if not item['title']:
            item['title'] = response.xpath('//h2[@align="center"]/text()').get()
        if not item['title']:
            item['title'] = response.xpath('//h3/text()').get()
        if not item['title']:
            item['title'] = response.xpath('//dic[@style="height:60px;line-height:30px;font-size:18px;text-align:center;margin-top:30px;"]/text()').get()
        if not item['title']:
            item['title'] = response.xpath('//div[@id="neititle"]/text()').get()
        if not item['title']:
            item['title'] = response.xpath('//div[@class="detailTitle"]/span/text()').get()
        if not item['title']:
            item['title'] = response.xpath('//div[@class="title_2"]/b/text()').get()
        
        infos = response.xpath('//td[@align="center"]/text()').get()
        if not infos:
            infos = response.xpath('''//p[@style="font-family:'微软雅黑'"]/text()''').get()
        if not infos:
            infos = response.xpath('//div[@id="neititle"]/span/text()').get()
        if not infos:
            infos = response.xpath('//div[@class="attr"]/text()').get()
        try:
            infos = infos.strip().split('\xa0\xa0')
            if len(infos) == 1:
                infos = infos.strip().split('    ')
            if len(infos) == 5:
                infos = infos.strip().split('\xa0\xa0 \xa0\xa0')
            for info in infos:
                if '供稿' in info:
                    item['author'] = info.split('：')[-1]
                elif '发布' in info:
                    time = info.split('：')[-1]
        except AttributeError:
            item['author'] = None
            item['time'] = None
        if not time:
            time = response.xpath('//div[@class="date"]/text()').get()
        if not time:
            time = response.xpath('//span[@id="lbDate"]/text()').get()
            if time:
                time = time.split('：')
            else:
                time = None
        if not time:
            time = response.xpath('//td[@align="center"]/span[1]/text()').get()
            if time:
                time = time.strip()
                time = time.split(' ')[0]
            else:
                time = None
        if time:
            if '-' in time:
                time = time.strip('[').strip(']')
                item['time'] = datetime.strptime(time, "%Y-%m-%d")
            elif '/' in time:
                item['time'] = datetime.strptime(time, "%Y/%m/%d")
            elif '年' in time:
                time = time.split(' ')[0]
                item['time'] = datetime.strptime(time, "%Y年%m月%d日")

        item['content'] = ''.join(response.xpath('//div[@id="vsb_content"]//span/text()').getall())
        if not item['content']:
            item['content'] = ''.join(response.xpath('//div[@id="vsb_content"]/div/p/text()').getall())
        item['url'] = response.url

        yield  item
