import scrapy
import os
import datetime
import re

NULL_CONSTANT = 'null'

def extract_attrs(response):

	# PRICE $
	price_text = response.css('.actPanel span:contains("US $")::text').extract_first()
	price = price_text.split("US $")[-1] if price_text else NULL_CONSTANT

	# SOLD pcs
	sold_text = response.css('.nonActPanel a:contains("sold")::text').extract_first()
	sold = int(sold_text.split(" ")[0].replace(',', '')) if sold_text else NULL_CONSTANT

	# LAST UPDATED
	last_updated_block = response.css('.vi-desc-revHistory:contains("Last updated on")').extract_first()
	last_updated = NULL_CONSTANT
	if last_updated_block:
		last_updated_str = last_updated_block.split("\xa0")[1] # \xa0 to split by &nbsp;
		if last_updated_str:
			last_updated = datetime.datetime.strptime(last_updated_str[:-4], "%b %d, %Y %H:%M:%S") # 'Sep 20, 2018 18:15:36 PDT'

	# SELLER NAME
	seller_name = response.css('#mbgLink span::text').extract_first()

	# SELLER FEEDBACK %
	seller_feedback_text = response.css('#si-fb::text').extract_first()
	seller_feedback = seller_feedback_text.split("%")[0] if seller_feedback_text else NULL_CONSTANT

	# CONDITION https://www.ebay.com/pages/help/sell/contextual/condition_2.html
	condition = response.css('.nonActPanel #vi-itm-cond::text').extract_first()

	# MATERIAL
	material_row_tds = response.css('#viTabs_0_is tr:contains("Material:") td')
	material = NULL_CONSTANT
	for i in range(0, len(material_row_tds), 2):
		if material_row_tds[i].css(':contains("Material:")'):
			material = material_row_tds[i+1].css('span::text').extract_first()

	# SLEEVE STYLE
	sleeve_row_tds = response.css('#viTabs_0_is tr:contains("Sleeve Style:") td')
	sleeve_style = NULL_CONSTANT
	for i in range(0, len(sleeve_row_tds), 2):
		if sleeve_row_tds[i].css(':contains("Sleeve Style:")'):
			sleeve_style = sleeve_row_tds[i+1].css('span::text').extract_first()

	# COUNTRY
	country_row_tds = response.css('#viTabs_0_is tr:contains("Country/Region of Manufacture:") td')
	country = NULL_CONSTANT
	for i in range(0, len(country_row_tds), 2):
		if country_row_tds[i].css(':contains("Country/Region of Manufacture:")'):
			country = country_row_tds[i+1].css('span::text').extract_first()

	# TITLE
	title = response.css('#itemTitle::text').extract_first()

	return {
		"price": price,
		"sold": sold,
		"last_updated": last_updated,
		"seller_name": seller_name,
		"seller_feedback": seller_feedback,
		"condition": condition,
		"material": material,
		"sleeve_style": sleeve_style,
		"country": country,
		"title": title
	}

def extract_description(response):
	# DESCRIPTION
	description = ''
	for t in response.css('span::text').extract():
		t_squeezed = re.sub('[ \t\n\"\'"]+', ' ', t)
		if len(t_squeezed) > 1:
			description = '{} {}'.format(description, t_squeezed)
	return description


def export_bulk():
	tr = scrapy.http.TextResponse('')

	with open('bulk.json', 'wb') as f:

		for index, filename_product in enumerate(os.listdir('products')):
			#if index >= 50: break

			with open('products/{}'.format(filename_product), 'rb') as f_source:
				tr = tr.replace(body=f_source.read())
			product_id = (filename_product.split('_')[-1]).split('.')[0]
			product_attrs = extract_attrs(tr)
		
			filename = 'iframes/iframe_{}.html'.format(product_id)
			try:
				with open(filename, 'rb') as f_source:
					tr = tr.replace(body=f_source.read())
				product_attrs["description"] = extract_description(tr)
				if product_attrs["description"] == '':
					product_attrs["description"] = NULL_CONSTANT
			except FileNotFoundError as e:
				print(e)
				product_attrs["description"] = NULL_CONSTANT

			f.write('{{"index":{{"_index":"product","_type":"_doc","_id":{}}}}}\n'
				.format(product_id)
				.encode('utf8'))
			f.write('{{"price":{},"sold":{},"last_updated":"{}","seller":{{"name":"{}","feedback":{}}},"condition":"{}","material":"{}","sleeve_style":"{}","country":"{}","title":"{}","description":"{}"}}\n'
				.format(product_attrs['price'], product_attrs['sold'], product_attrs['last_updated'], \
					product_attrs['seller_name'], product_attrs['seller_feedback'], product_attrs['condition'], \
					product_attrs['material'], product_attrs['sleeve_style'], product_attrs['country'], \
					product_attrs['title'], product_attrs['description'])
				.replace("\"null\"","null")
				.encode('utf8'))


export_bulk()

