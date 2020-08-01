import scrapy
import threading

# scrapy crawl link -o links.json

class LinkSpider(scrapy.Spider):
	name = "link"

	PAGE_NUM_LAST = 50
	count = 0
	count_lock = threading.Lock()

	start_urls = [
		'https://www.ebay.com/sch/TShirts-/63869/i.html?_ipg=192&_pgn=1', # Tops
		'https://www.ebay.com/sch/TShirts-/11514/i.html?_ipg=192&_pgn=1', # Intimates & Sleepwear
	]

	def parse(self, response):
		
		with self.count_lock: 
			filename = 'links/link_{}.html'.format(self.count)
			self.count += 1
		with open(filename, 'wb') as f:
			f.write(response.body)
		
		for link in response.css('.s-item__link'):
			yield {
				'href': link.css('a::attr(href)').extract_first(),
			}

		next_page = response.css('.x-pagination__control[rel="next"]::attr(href)').extract_first()
		if next_page is not None:
			next_page_num = next_page.split("/")[-1].split('=')[-1]
			if int(next_page_num) <= self.PAGE_NUM_LAST:
				yield response.follow(next_page, callback=self.parse)
