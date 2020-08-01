import scrapy
import json
import re

# scrapy crawl product

class ProductSpider(scrapy.Spider):
	name = "product"

	def start_requests(self):
		with open('links.json') as json_data:
			link_array = json.load(json_data)
			for index, link_json in enumerate(link_array):
				if index > 6515:
					yield scrapy.Request(url=link_json['href'], meta={'index': index})

	def parse(self, response):
		
		filename = 'products/product_{}.html'.format(response.meta['index'])
		with open(filename, 'wb') as f:
			f.write(response.body)

		description_link = response.css('iframe#desc_ifr::attr(src)').extract_first()
		if description_link:
			yield scrapy.Request(url=description_link, callback=self.parse_iframe, meta={'index': response.meta['index']})

	def parse_iframe(self, response):
		
		filename = 'iframes/iframe_{}.html'.format(response.meta['index'])
		with open(filename, 'wb') as f:
			f.write(response.body)

		"""
		filename = 'descriptions/description_{}.html'.format(response.meta['index'])
		with open(filename, 'w') as f:
			for t in response.css('span::text').extract():
				t_squeezed = re.sub('[ \t\n]+', ' ', t)
				if len(t_squeezed) > 1:
					f.write('{} '.format(t_squeezed.encode('utf8')))
		"""
