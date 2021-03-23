import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import RegionsItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class RegionsSpider(scrapy.Spider):
	name = 'regions'
	start_urls = ['https://doingmoretoday.com/category/news/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="w-full mb-8 sm:px-2 md:px-4 sm:w-1/2 lg:w-1/3"]//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//span[@class="ml-4"]/a[@class="btn"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//time/text()').get()
		try:
			title = response.xpath('//h1/text()').get() + response.xpath('//p[@class="text-3xl font-light leading-tight"]/text()').get()
		except TypeError:
			title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="mb-16 text-lg entry-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=RegionsItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
