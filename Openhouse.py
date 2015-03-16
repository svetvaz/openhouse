import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
from urllib import quote_plus
import sqlite3
import os


class OpenHouse:

	def __init__(self):
		self.trulia_url='http://trulia.com'
		self.url_arr=[]

	def get_soup(self,base_url, relative_url=''):
		sub_dir="cache"
		if not os.path.exists(sub_dir):
			os.makedirs(sub_dir)
		url = urljoin(base_url, relative_url)
		url_path = quote_plus(url)
		try:
			with open(os.path.join(sub_dir,url_path)) as f:
				return BeautifulSoup(f.read().decode('utf-8'))
		except:
			pass
		r = requests.get(url)
		if r.status_code == 200:
			with open(os.path.join(sub_dir,url_path), 'w') as f:
				f.write(r.text.encode('utf-8'))
			return BeautifulSoup(r.text)
		return None

	def retrieve_required_info_and_insert_to_db(self,cursor,db,s):
		cursor.execute('''
		    CREATE TABLE openhousedetail(id INTEGER PRIMARY KEY, url TEXT,
                       street_address TEXT, open_house_date TEXT)
			''')
		for url_tag in s.findAll('meta',itemprop="url"):
			self.url_arr.append(self.trulia_url+url_tag['content'])
		for url in self.url_arr:
			street_address=''
			open_house_date=''
			second_soup = self.get_soup(url)
			all_street_addr_spans = second_soup.find_all(itemprop = "streetAddress")
			for span in all_street_addr_spans:
				street_address = span.get_text()

			all_matching_divs = second_soup.find_all("div", class_= "col cols6 mls")
			if len(all_matching_divs)==0:
				all_matching_divs= second_soup.find("div", {"id": "openHouse"})
				for div in all_matching_divs:
					ul= div.find_next('ul')
					for li in ul:
						open_house_date=open_house_date+li.string
			else:
				for div in all_matching_divs:
					if div.text.lower()=='open house':
						open_house_date = div.find_next('div').text
			cursor.execute('''INSERT INTO openhousedetail(url, street_address, open_house_date) VALUES(?,?,?)''', (url, street_address, open_house_date))			
			db.commit()




	def run(self):
		soup_one = self.get_soup('http://www.trulia.com/for_sale/San_Jose,CA/p_oh/3p_beds/2p_baths/600000-800000_price/SINGLE-FAMILY_HOME_type/2000p_sqft')
		db = sqlite3.connect(':memory:')
		db = sqlite3.connect('openhouse.db')
		cursor = db.cursor()
		cursor.execute(''' Drop Table openhousedetail''')
		db.commit()
		self.retrieve_required_info_and_insert_to_db(cursor,db,soup_one)
		cursor.execute('''Select * from openhousedetail''');
		rows = cursor.fetchall()
		for row in rows:
			print row
		db.close()	



op = OpenHouse()
op.run()

			
			