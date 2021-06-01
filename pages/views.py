from django.shortcuts import render

# Create your views here.
from time import time
from pathlib import Path
import csv
import glob
import re

from bs4 import BeautifulSoup
import requests


def home_view(request):
	return render(request, 'pages/home.html')


def results_view(request):
	def check_by_class(web_page, class_name, search_content):
		try:
			web_link = requests.get(web_page)
			web_soup = BeautifulSoup(web_link.content, 'html.parser')

			if search_content != None:
				result = web_soup.find(class_='fsPageContent').find(class_=class_name)
			else:
				result = web_soup.find(class_=class_name)

			return result != None

		except:
			print('Page not working:', web_page)


	url = request.POST.get('search')
	class_name = request.POST.get('by_class')
	search_content = request.POST.get('search_content')
	print('>>', url, '>>', class_name, '>>', search_content)
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	urls = soup.find_all('loc')
	links = []
	counter = 0

	for link in urls:
		if link.get_text()[0] != 'h':
			news = check_by_class('https:' + link.get_text(), class_name, search_content)
		else:
			news = check_by_class(link.get_text(), class_name, search_content)

		if news:
			links.append(link.get_text())
			counter += 1

	context = {
		'links': links,
		'class_name': class_name,
		'counter': counter
	}

	return render(request, 'pages/results.html', context)


def custom_view(request):
	return render(request, 'pages/custom.html')


def results_custom_view(request):
	def clean_tags(tags):
		for tag in tags:
			tag.attrs.clear()

			if tag.contents == []:
				tag.decompose()


	def remove_tags(text):
		div = re.compile(r'<div[^>]+>')
		dive = re.compile(r'<div+>')
		divc = re.compile(r'</div+>')
		span = re.compile(r'<span+>')
		spane = re.compile(r'<span[^>]+>')
		spanc = re.compile(r'</span+>')
		font = re.compile(r'<font+>')
		fonte = re.compile(r'<font[^>]+>')
		fontc = re.compile(r'</font+>')

		text = div.sub('', text)
		text = dive.sub('', text)
		text = divc.sub('', text)
		text = span.sub('', text)
		text = spane.sub('', text)
		text = spanc.sub('', text)
		text = font.sub('', text)
		text = fonte.sub('', text)
		text = fontc.sub('', text)
		text = re.sub('<!--|-->', '', text)

		return text.strip()


	def get_column(col, splitter):
		col_images = col.find_all('img')
		col_anchors = col.find_all('a')
		col_tags = col.find_all(['article', 'b', 'br', 'button', 'col', 'colgroup', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'ul', 'ol', 'li', 'p', 'table', 'td', 'th', 'tr', 'strong', 'input', 'label', 'legend', 'fieldset'])
		clean_tags(col_tags)

		while col.link != None:
			col.link.decompose()

		while col.script != None:
			col.script.decompose()

		while col.style != None:
			col.style.decompose()

		while col.nav != None:
			col.nav.decompose()

		for image in col_images:
			try:
				if image.get('src') != None and image.get('src') != '':
					src = image['src']

					if 'alt' in image.attrs:
						alt = image['alt']
						image.attrs.clear()
						image['alt'] = alt
					else:
						image.attrs.clear()
						image['alt'] = 'alt-text'

					image['src'] = src

				else:
					image.attrs.clear()

				image['id'] = ''
				image['role'] = 'presentation'
				image['style'] = ''
				image['width'] = '250'

			except:
				print('Image:', image)

		for anchor in col_anchors:
			try:
				if anchor.get('href') != None and anchor.get('href') != '':
					href = anchor['href']
					anchor.attrs.clear()
					anchor['href'] = href

					if anchor.get('href')[:4] != 'http' and anchor.get('href').find('.pdf') == -1 and anchor.get('href').find('.txt') == -1\
					and anchor.get('href').find('.xls') == -1 and anchor.get('href').find('.xlsx') == -1\
					and anchor.get('href').find('.doc') == -1 and anchor.get('href').find('.docx') == -1\
					and anchor.get('href').find('.ppt') == -1 and anchor.get('href').find('.pptx') == -1:
						anchor.string = 'INTERNAL LINK ' + anchor.string

			except:
				print('Anchor:', anchor)

		col = remove_tags(str(col))

		return col


	def get_content(web_page, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news, splitter):
		col1 = 'Flagged'
		col2, col3, col4 = '', '', ''
		col_num = '1'
		page_nav = None
		meta_title = ''
		meta_keywords = ''
		meta_desc = ''
		form = ''
		embed = ''
		iframe = ''
		calendar = ''
		staff = ''
		news = ''
		issue_pages_counter = 0
		# print(web_page)

		# if web_page != '#':
		try:
			web_link = requests.get(web_page, timeout=10).content
			web_soup = BeautifulSoup(web_link, 'html.parser')

			if web_soup.find_all('meta', attrs={'name': 'title'}) != []:
				meta_title = str(web_soup.find_all('meta', attrs={'name': 'title'}))

			if web_soup.find_all('meta', attrs={'name': 'keywords'}) != []:
				meta_keywords = str(web_soup.find_all('meta', attrs={'name': 'keywords'}))

			if web_soup.find_all('meta', attrs={'name': 'description'}) != []:
				meta_desc = str(web_soup.find_all('meta', attrs={'name': 'description'}))

			if len(post_page_nav.split('=')[0]) > 3:
				if web_soup.find(class_=post_page_nav.split('=')[1]) != None:
					page_nav = web_soup.find(class_=post_page_nav.split('=')[1]).find_all('a')
			elif len(post_page_nav.split('=')[0]) > 0 and len(post_page_nav.split('=')[0]) < 4:
				if web_soup.find(id=post_page_nav.split('=')[1]) != None:
					page_nav = web_soup.find(id=post_page_nav.split('=')[1]).find_all('a')

			if len(post_main_content.split('=')[0]) > 3:
				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('form') != []:
					form = 'form'

				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('embed') != []:
					embed = 'embed'

				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('iframe') != []:
					iframe = 'iframe'

				if len(post_calendar.split('=')[0]) > 3:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_calendar.split('=')[1]) != []:
						calendar = 'calendar'
				elif len(post_calendar.split('=')[0]) > 0 and len(post_calendar.split('=')[0]) < 4:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_calendar.split('=')[1]) != []:
						calendar = 'calendar'

				if len(post_staff_dir.split('=')[0]) > 3:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_staff_dir.split('=')[1]) != []:
						staff = 'staff'
				elif len(post_staff_dir.split('=')[0]) > 0 and len(post_staff_dir.split('=')[0]) < 4:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_staff_dir.split('=')[1]) != []:
						staff = 'staff'

				if len(post_news.split('=')[0]) > 3:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_news.split('=')[1]) != []:
						news = 'news'
				elif len(post_news.split('=')[0]) > 0 and len(post_news.split('=')[0]) < 4:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_news.split('=')[1]) != []:
						news = 'news'

				if len(post_col1.split('=')[0]) > 3:
					if web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1]) != '':
						col1 = web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1])
						col1 = get_column(col1, splitter)
					else:
						issue_pages_counter = 1
				else:
					if web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1]) != '':
						col1 = web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1])
						col1 = get_column(col1, splitter)
					else:
						issue_pages_counter = 1

				if len(post_col2.split('=')[0]) > 3:
					if web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1]) != '':
						col4 = web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1])
						col4 = get_column(col4, splitter)
				else:
					if web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1]) != '':
						col4 = web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1])
						col4 = get_column(col4, splitter)

			else:
				if web_soup.find(id=post_main_content.split('=')[1]).find_all('form') != []:
					form = 'form'

				if web_soup.find(id=post_main_content.split('=')[1]).find_all('embed') != []:
					embed = 'embed'

				if web_soup.find(id=post_main_content.split('=')[1]).find_all('iframe') != []:
					iframe = 'iframe'

				if len(post_calendar.split('=')[0]) > 3:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_calendar.split('=')[1]) != []:
						calendar = 'calendar'
				elif len(post_calendar.split('=')[0]) > 0 and len(post_calendar.split('=')[0]) < 4:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_calendar.split('=')[1]) != []:
						calendar = 'calendar'

				if len(post_staff_dir.split('=')[0]) > 3:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_staff_dir.split('=')[1]) != []:
						staff = 'staff'
				elif len(post_staff_dir.split('=')[0]) > 0 and len(post_staff_dir.split('=')[0]) < 4:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_staff_dir.split('=')[1]) != []:
						staff = 'staff'

				if len(post_news.split('=')[0]) > 3:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_news.split('=')[1]) != []:
						news = 'news'
				elif len(post_news.split('=')[0]) > 0 and len(post_news.split('=')[0]) < 4:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_news.split('=')[1]) != []:
						news = 'news'

				if len(post_col1.split('=')[0]) > 3:
					if web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1]) != '':
						col1 = web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1])
						col1 = get_column(col1, splitter)
					else:
						issue_pages_counter = 1
				else:
					if web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1]) != '':
						col1 = web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1])
						col1 = get_column(col1, splitter)
					else:
						issue_pages_counter = 1

				if len(post_col2.split('=')[0]) > 3:
					if web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1]) != '':
						col4 = web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1])
						col4 = get_column(col4, splitter)
				else:
					if web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1]) != '':
						col4 = web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1])
						col4 = get_column(col4, splitter)

			col1 = str(col1)
			col4 = str(col4)

			if len(col1) > 150000:
				col1 = 'Flagged'
				col2 = 'This page has too much content'
				col3 = ''
				col4 = ''
				col_num = '2'
				issue_pages_counter = 1
			elif len(col1) > 100000:
				col2 = col1[50000:100000]
				col3 = col1[100000:]
				col1 = col1[:50000]
				col_num = '3'
			elif len(col1) > 50000:
				col2 = col1[50000:]
				col1 = col1[:50000]
				col_num = '2'

			if len(col4) > 50000:
				col1 = 'Flagged'
				col2 = 'This page has too much content'
				col3 = ''
				col4 = ''
				col_num = '2'
				issue_pages_counter = 1
			elif len(col4) > 0:
				col_num = '4'

			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter

		# else:
		except:
			issue_pages_counter = 1

			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter


	post_sites = request.POST.get('site')
	post_sitemap = request.POST.get('main_nav')
	post_list_items = request.POST.get('list_items')
	post_school = request.POST.get('school_title')
	post_main_content = request.POST.get('main_content')
	post_page_nav = request.POST.get('page_nav')
	post_col1 = request.POST.get('col1')
	post_col2 = request.POST.get('col2')
	post_calendar = request.POST.get('calendar')
	post_staff_dir = request.POST.get('staff_dir')
	post_news = request.POST.get('news')
	# extra_links = request.POST.get('extra')
	print('>>', post_sites, post_sitemap, post_list_items, post_school, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news)

	# Process inputs
	all_sites = post_sites.split(',')

	start_time = time()
	mainfolder = all_sites[0].split('.')[1]
	filepath = Path(f'static/files/{mainfolder}')
	filepath.mkdir(parents=True, exist_ok=True)
	files = {}

	with open('static/files/' + mainfolder + '/report.csv', 'w', encoding='utf-8') as csv_report:
		csv_report = csv.writer(csv_report)

		for site in all_sites:
			page_counter = 0
			issue_pages_counter = 0

			splitter = site.split('/')
			page = requests.get(site).content
			soup = BeautifulSoup(page, 'html.parser')

			if len(post_sitemap.split('=')[0]) > 3:
				sitemap = soup.find(class_=post_sitemap.split('=')[1])
				list_items = sitemap.select(post_list_items)
			elif len(post_sitemap.split('=')[0]) > 0 and len(post_sitemap.split('=')[0]) < 4:
				sitemap = soup.find(id=post_sitemap.split('=')[1])
				list_items = sitemap.select(post_list_items)
			else:
				list_items = soup.find_all(class_=post_list_items)

			if len(post_school.split('=')[0]) > 3:
				school = soup.find(class_=post_school.split('=')[1]).get_text()
			else:
				school = soup.find(id=post_school.split('=')[1]).get_text()

			if len(school) > 30:
				school_name = str(school[:30]).lower().replace(' ', '_').replace('.', '')
			else:
				school_name = str(school).lower().replace(' ', '_').replace('.', '')

			csv_report.writerow(['School name', school_name])

			with open('static/files/' + mainfolder + '/' + school_name + '.csv', 'w', encoding='utf-8') as csv_main:
				csv_writer = csv.writer(csv_main)
				csv_writer.writerow(['Link to page', 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Column Count', 'Column 1', 'Column 2', 'Column 3', 'Column 4', 'Meta title', 'Meta keywords', 'Meta description'])

				for item in list_items[1:]:
					group_links = item.find_all('a')

					for link in group_links:
						external_link = False

						if link.get('href')[0] == '#':
							page_link = '#'
						elif len(link.get('href')) > 1 and link.get('href')[:2] == '//':
							page_link = splitter[0] + link.get('href')
						elif link.get('href')[0] == '/':
							page_link = splitter[0] + '//' + splitter[2] + link.get('href')
						elif link.get('href')[:4] == 'http':
							page_link = link.get('href')

							if link.get('href').find(splitter[2].split('.')[1]) == -1:
								external_link = True
						else:
							page_link = splitter[0] + '//' + splitter[2] + '/' + link.get('href')

						if not external_link:
							page_counter += 1
							col1, col2, col3, col4, col_num, nav_sec, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news, splitter)
							issue_pages_counter += content_ipc

							if group_links[0].get_text() != link.get_text():
								csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), '', '', col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])
							else:
								csv_writer.writerow([str(page_link), str(group_links[0].get_text()), '', '', '', col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])

							if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
								csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])

							if nav_sec != None and nav_sec != '' and nav_sec != []:
								for nav_link in nav_sec:
									external_link = False

									if nav_link.get('href')[0] == '#':
										page_link = '#'
									elif len(nav_link.get('href')) > 1 and nav_link.get('href')[:2] == '//':
										page_link = splitter[0] + nav_link.get('href')
									elif nav_link.get('href')[0] == '/':
										page_link = splitter[0] + '//' + splitter[2] + nav_link.get('href')
									elif nav_link.get('href')[:4] == 'http':
										page_link = nav_link.get('href')

										if nav_link.get('href').find(splitter[2].split('.')[1]) == -1:
											external_link = True
									else:
										page_link = splitter[0] + '//' + splitter[2] + '/' + nav_link.get('href')

									if not external_link:
										page_counter += 1
										nav_col1, nav_col2, nav_col3, nav_col4, nav_col_num, _, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news, splitter)
										issue_pages_counter += content_ipc
										csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), str(nav_link.get_text()), '', nav_col_num, nav_col1, nav_col2, nav_col3, nav_col4, meta_title, meta_keywords, meta_desc])

										if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
											csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])
									else:
										csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), str(nav_link.get_text()), '', '1', 'Linked page', '', '', '', '', '', ''])
						else:
							csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), '', '', '1', 'Linked page', '', '', '', '', '', ''])

				csv_report.writerow([])
				csv_report.writerow(['Pages scraped', page_counter])
				csv_report.writerow(['Issues', issue_pages_counter])
				csv_report.writerow([])
				csv_report.writerow([])
				csv_report.writerow([])

			files[school_name + '.csv'] = 'static/files/' + mainfolder + '/' + school_name + '.csv'
			print('Finished:', site)

	files['report.csv'] = 'static/files/' + mainfolder + '/report.csv'
	print('Finished:', round((time() - start_time) / 3600, 2), 'h')

	context = {
		'files': files,
		'time': str(round((time() - start_time) / 3600, 2)) + ' hours'
	}

	return render(request, 'pages/export_page.html', context)


def blackboard_view(request):
	return render(request, 'pages/blackboard.html')


def results_blackboard_view(request):
	def clean_tags(tags):
		for tag in tags:
			tag.attrs.clear()

			if tag.contents == []:
				tag.decompose()


	def remove_tags(text):
		div = re.compile(r'<div[^>]+>')
		dive = re.compile(r'<div+>')
		divc = re.compile(r'</div+>')
		span = re.compile(r'<span+>')
		spane = re.compile(r'<span[^>]+>')
		spanc = re.compile(r'</span+>')
		font = re.compile(r'<font+>')
		fonte = re.compile(r'<font[^>]+>')
		fontc = re.compile(r'</font+>')

		text = div.sub('', text)
		text = dive.sub('', text)
		text = divc.sub('', text)
		text = span.sub('', text)
		text = spane.sub('', text)
		text = spanc.sub('', text)
		text = font.sub('', text)
		text = fonte.sub('', text)
		text = fontc.sub('', text)
		text = re.sub('<!--|-->', '', text)

		return text.strip()


	def get_column(col, splitter):
		col_images = col.find_all('img')
		col_anchors = col.find_all('a')
		col_tags = col.find_all(['article', 'b', 'br', 'button', 'col', 'colgroup', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'ul', 'ol', 'li', 'p', 'table', 'td', 'th', 'tr', 'strong', 'input', 'label', 'legend', 'fieldset'])
		clean_tags(col_tags)

		while col.link != None:
			col.link.decompose()

		while col.script != None:
			col.script.decompose()

		while col.style != None:
			col.style.decompose()

		while col.nav != None:
			col.nav.decompose()

		for image in col_images:
			try:
				if image.get('src') != None and image.get('src') != '':
					src = image['src']

					if 'alt' in image.attrs:
						alt = image['alt']
						image.attrs.clear()
						image['alt'] = alt
					else:
						image.attrs.clear()
						image['alt'] = 'alt-text'

					image['src'] = src

				else:
					image.attrs.clear()

				image['id'] = ''
				image['role'] = 'presentation'
				image['style'] = ''
				image['width'] = '250'

			except:
				print('Image:', image)

		for anchor in col_anchors:
			try:
				if anchor.get('href') != None and anchor.get('href') != '':
					href = anchor['href']
					anchor.attrs.clear()
					anchor['href'] = href

					if anchor.get('href')[:4] != 'http' and anchor.get('href').find('.pdf') == -1 and anchor.get('href').find('.txt') == -1\
					and anchor.get('href').find('.xls') == -1 and anchor.get('href').find('.xlsx') == -1\
					and anchor.get('href').find('.doc') == -1 and anchor.get('href').find('.docx') == -1\
					and anchor.get('href').find('.ppt') == -1 and anchor.get('href').find('.pptx') == -1:
						anchor.string = 'INTERNAL LINK ' + anchor.string

			except:
				print('Anchor:', anchor)

		col = remove_tags(str(col))

		return col


	def get_content(web_page, post_page_nav, splitter):
		col1 = 'Flagged'
		col2, col3, col4 = '', '', ''
		col_num = '1'
		page_nav = None
		meta_title = ''
		meta_keywords = ''
		meta_desc = ''
		form = ''
		embed = ''
		iframe = ''
		calendar = ''
		staff = ''
		news = ''
		issue_pages_counter = 0
		# print(web_page)

		# if web_page != '#':
		try:
			web_link = requests.get(web_page, timeout=10).content
			web_soup = BeautifulSoup(web_link, 'html.parser')

			if web_soup.find_all('meta', attrs={'name': 'title'}) != []:
				meta_title = str(web_soup.find_all('meta', attrs={'name': 'title'}))

			if web_soup.find_all('meta', attrs={'name': 'keywords'}) != []:
				meta_keywords = str(web_soup.find_all('meta', attrs={'name': 'keywords'}))

			if web_soup.find_all('meta', attrs={'name': 'description'}) != []:
				meta_desc = str(web_soup.find_all('meta', attrs={'name': 'description'}))

			if len(post_page_nav.split('=')[0]) > 3:
				if web_soup.find(class_=post_page_nav.split('=')[1]) != None:
					page_nav = web_soup.find(class_=post_page_nav.split('=')[1]).find_all('a')
			elif len(post_page_nav.split('=')[0]) > 0 and len(post_page_nav.split('=')[0]) < 4:
				if web_soup.find(id=post_page_nav.split('=')[1]) != None:
					page_nav = web_soup.find(id=post_page_nav.split('=')[1]).find_all('a')

			if web_soup.find(id='sw-content-layout-wrapper').find_all('form') != []:
				form = 'form'

			if web_soup.find(id='sw-content-layout-wrapper').find_all('embed') != []:
				embed = 'embed'

			if web_soup.find(id='sw-content-layout-wrapper').find_all('iframe') != []:
				iframe = 'iframe'

			if web_soup.find(id='sw-content-layout-wrapper').find_all(class_='calendar') != []:
				calendar = 'calendar'

			if web_soup.find(id='sw-content-layout-wrapper').find_all(class_='staffdirectorydiv') != []:
				staff = 'staff'

			if web_soup.find(id='sw-content-layout-wrapper').find_all(class_='headlines') != []:
				news = 'news'

			# First column
			if web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container1') != None and web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container1') != '':
				col1 = web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container1')
				col1 = get_column(col1, splitter)
			else:
				issue_pages_counter = 1

			if web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container2') != None and web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container2') != '':
				col2 = web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container2')
				col2 = get_column(col2, splitter)

			if web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container3') != None and web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container3') != '':
				col3 = web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container3')
				col3 = get_column(col3, splitter)

			if web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container4') != None and web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container4') != '':
				col4 = web_soup.find(id='sw-content-layout-wrapper').find(id='sw-content-container4')
				col4 = get_column(col4, splitter)

			col1 = str(col1)
			col4 = str(col4)

			if len(col1) > 150000:
				col1 = 'Flagged'
				col2 = 'This page has too much content'
				col3 = ''
				col4 = ''
				col_num = '2'
				issue_pages_counter = 1
			elif len(col1) > 100000:
				col2 = col1[50000:100000]
				col3 = col1[100000:]
				col1 = col1[:50000]
				col_num = '3'
			elif len(col1) > 50000:
				col2 = col1[50000:]
				col1 = col1[:50000]
				col_num = '2'

			if len(col4) > 50000:
				col1 = 'Flagged'
				col2 = 'This page has too much content'
				col3 = ''
				col4 = ''
				col_num = '2'
				issue_pages_counter = 1
			elif len(col4) > 0:
				col_num = '4'

			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter

		# else:
		except:
			issue_pages_counter = 1

			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter


	post_sites = request.POST.get('site')
	# post_sitemap = request.POST.get('main_nav')
	# post_list_items = request.POST.get('list_items')
	# post_school = request.POST.get('school_title')
	# post_main_content = request.POST.get('main_content')
	post_page_nav = request.POST.get('page_nav')
	# post_col1 = request.POST.get('col1')
	# post_col2 = request.POST.get('col2')
	# post_calendar = request.POST.get('calendar')
	# post_staff_dir = request.POST.get('staff_dir')
	# post_news = request.POST.get('news')
	# extra_links = request.POST.get('extra')
	# print('>>', post_sites, post_sitemap, post_list_items, post_school, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news)
	print('>>', post_sites, post_page_nav)

	# Process inputs
	all_sites = post_sites.split(',')

	start_time = time()
	mainfolder = all_sites[0].split('.')[1]
	filepath = Path(f'static/files/{mainfolder}')
	filepath.mkdir(parents=True, exist_ok=True)
	files = {}

	with open('static/files/' + mainfolder + '/report.csv', 'w', encoding='utf-8') as csv_report:
		csv_report = csv.writer(csv_report)

		for site in all_sites:
			page_counter = 0
			issue_pages_counter = 0

			splitter = site.split('/')
			page = requests.get(site).content
			soup = BeautifulSoup(page, 'html.parser')
			sitemap = soup.find(id='sw-sitemap')
			list_items = sitemap.select('li.sw-sitemap-channel-item')
			school = soup.find(id='sw-sitemap-sitelist').find('option', selected='selected').get_text()

			if len(school) > 30:
				school_name = str(school[:30]).lower().replace(' ', '_').replace('.', '')
			else:
				school_name = str(school).lower().replace(' ', '_').replace('.', '')

			csv_report.writerow(['School name', school_name])

			with open('static/files/' + mainfolder + '/' + school_name + '.csv', 'w', encoding='utf-8') as csv_main:
				csv_writer = csv.writer(csv_main)
				csv_writer.writerow(['Link to page', 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Column Count', 'Column 1', 'Column 2', 'Column 3', 'Column 4', 'Meta title', 'Meta keywords', 'Meta description'])

				for item in list_items[1:]:
					group_links = item.find_all('a')

					for link in group_links:
						external_link = False

						if link.get('href')[0] == '#':
							page_link = '#'
						elif len(link.get('href')) > 1 and link.get('href')[:2] == '//':
							page_link = splitter[0] + link.get('href')
						elif link.get('href')[0] == '/':
							page_link = splitter[0] + '//' + splitter[2] + link.get('href')
						elif link.get('href')[:4] == 'http':
							page_link = link.get('href')

							if link.get('href').find(splitter[2].split('.')[1]) == -1:
								external_link = True
						else:
							page_link = splitter[0] + '//' + splitter[2] + '/' + link.get('href')

						if not external_link:
							page_counter += 1
							col1, col2, col3, col4, col_num, nav_sec, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_page_nav, splitter)
							issue_pages_counter += content_ipc

							if group_links[0].get_text() != link.get_text():
								csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), '', '', col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])
							else:
								csv_writer.writerow([str(page_link), str(group_links[0].get_text()), '', '', '', col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])

							if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
								csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])

							if nav_sec != None and nav_sec != '' and nav_sec != []:
								for nav_link in nav_sec:
									external_link = False

									if nav_link.get('href')[0] == '#':
										page_link = '#'
									elif len(nav_link.get('href')) > 1 and nav_link.get('href')[:2] == '//':
										page_link = splitter[0] + nav_link.get('href')
									elif nav_link.get('href')[0] == '/':
										page_link = splitter[0] + '//' + splitter[2] + nav_link.get('href')
									elif nav_link.get('href')[:4] == 'http':
										page_link = nav_link.get('href')

										if nav_link.get('href').find(splitter[2].split('.')[1]) == -1:
											external_link = True
									else:
										page_link = splitter[0] + '//' + splitter[2] + '/' + nav_link.get('href')

									if not external_link:
										page_counter += 1
										nav_col1, nav_col2, nav_col3, nav_col4, nav_col_num, _, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_page_nav, splitter)
										issue_pages_counter += content_ipc
										csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), str(nav_link.get_text()), '', nav_col_num, nav_col1, nav_col2, nav_col3, nav_col4, meta_title, meta_keywords, meta_desc])

										if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
											csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])
									else:
										csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), str(nav_link.get_text()), '', '1', 'Linked page', '', '', '', '', '', ''])
						else:
							csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), '', '', '1', 'Linked page', '', '', '', '', '', ''])

				csv_report.writerow([])
				csv_report.writerow(['Pages scraped', page_counter])
				csv_report.writerow(['Issues', issue_pages_counter])
				csv_report.writerow([])
				csv_report.writerow([])
				csv_report.writerow([])

			files[school_name + '.csv'] = 'static/files/' + mainfolder + '/' + school_name + '.csv'
			print('Finished:', site)

	files['report.csv'] = 'static/files/' + mainfolder + '/report.csv'
	print('Finished:', round((time() - start_time) / 3600, 2), 'h')

	context = {
		'files': files,
		'time': str(round((time() - start_time) / 3600, 2)) + ' hours'
	}

	return render(request, 'pages/export_page.html', context)


def schoolpointe_view(request):
	return render(request, 'pages/schoolpointe.html')


# def results_schoolpointe_view(request):
# 	def clean_tags(tags):
# 		for tag in tags:
# 			tag.attrs.clear()
#
# 			if tag.contents == []:
# 				tag.decompose()
#
#
# 	def remove_tags(text):
# 		div = re.compile(r'<div[^>]+>')
# 		dive = re.compile(r'<div+>')
# 		divc = re.compile(r'</div+>')
# 		span = re.compile(r'<span+>')
# 		spane = re.compile(r'<span[^>]+>')
# 		spanc = re.compile(r'</span+>')
# 		font = re.compile(r'<font+>')
# 		fonte = re.compile(r'<font[^>]+>')
# 		fontc = re.compile(r'</font+>')
#
# 		text = div.sub('', text)
# 		text = dive.sub('', text)
# 		text = divc.sub('', text)
# 		text = span.sub('', text)
# 		text = spane.sub('', text)
# 		text = spanc.sub('', text)
# 		text = font.sub('', text)
# 		text = fonte.sub('', text)
# 		text = fontc.sub('', text)
# 		text = re.sub('<!--|-->', '', text)
#
# 		return text.strip()
#
#
# 	def get_column(col, splitter):
# 		col_images = col.find_all('img')
# 		col_anchors = col.find_all('a')
# 		col_tags = col.find_all(['article', 'b', 'br', 'button', 'col', 'colgroup', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'ul', 'ol', 'li', 'p', 'table', 'td', 'th', 'tr', 'strong', 'input', 'label', 'legend', 'fieldset'])
# 		clean_tags(col_tags)
#
# 		while col.link != None:
# 			col.link.decompose()
#
# 		while col.script != None:
# 			col.script.decompose()
#
# 		while col.style != None:
# 			col.style.decompose()
#
# 		while col.nav != None:
# 			col.nav.decompose()
#
# 		for image in col_images:
# 			try:
# 				if image.get('src') != None and image.get('src') != '':
# 					src = image['src']
#
# 					if 'alt' in image.attrs:
# 						alt = image['alt']
# 						image.attrs.clear()
# 						image['alt'] = alt
# 					else:
# 						image.attrs.clear()
# 						image['alt'] = 'alt-text'
#
# 					image['src'] = src
#
# 				else:
# 					image.attrs.clear()
#
# 				image['id'] = ''
# 				image['role'] = 'presentation'
# 				image['style'] = ''
# 				image['width'] = '250'
#
# 			except:
# 				print('Image:', image)
#
# 		for anchor in col_anchors:
# 			try:
# 				if anchor.get('href') != None and anchor.get('href') != '':
# 					href = anchor['href']
# 					anchor.attrs.clear()
# 					anchor['href'] = href
#
# 					if anchor.get('href')[:4] != 'http' and anchor.get('href').find('.pdf') == -1 and anchor.get('href').find('.txt') == -1\
# 					and anchor.get('href').find('.xls') == -1 and anchor.get('href').find('.xlsx') == -1\
# 					and anchor.get('href').find('.doc') == -1 and anchor.get('href').find('.docx') == -1\
# 					and anchor.get('href').find('.ppt') == -1 and anchor.get('href').find('.pptx') == -1:
# 						anchor.string = 'INTERNAL LINK ' + anchor.string
#
# 			except:
# 				print('Anchor:', anchor)
#
# 		col = remove_tags(str(col))
#
# 		return col
#
#
# 	def get_content(web_page, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news, splitter):
# 		col1 = 'Flagged'
# 		col2, col3, col4 = '', '', ''
# 		col_num = '1'
# 		page_nav = None
# 		meta_title = ''
# 		meta_keywords = ''
# 		meta_desc = ''
# 		form = ''
# 		embed = ''
# 		iframe = ''
# 		calendar = ''
# 		staff = ''
# 		news = ''
# 		issue_pages_counter = 0
# 		# print(web_page)
#
# 		# if web_page != '#':
# 		try:
# 			web_link = requests.get(web_page, timeout=10).content
# 			web_soup = BeautifulSoup(web_link, 'html.parser')
#
# 			if web_soup.find_all('meta', attrs={'name': 'title'}) != []:
# 				meta_title = str(web_soup.find_all('meta', attrs={'name': 'title'}))
#
# 			if web_soup.find_all('meta', attrs={'name': 'keywords'}) != []:
# 				meta_keywords = str(web_soup.find_all('meta', attrs={'name': 'keywords'}))
#
# 			if web_soup.find_all('meta', attrs={'name': 'description'}) != []:
# 				meta_desc = str(web_soup.find_all('meta', attrs={'name': 'description'}))
#
# 			if len(post_page_nav.split('=')[0]) > 3:
# 				if web_soup.find(class_=post_page_nav.split('=')[1]) != None:
# 					page_nav = web_soup.find(class_=post_page_nav.split('=')[1]).find_all('a')
# 			elif len(post_page_nav.split('=')[0]) > 0 and len(post_page_nav.split('=')[0]) < 4:
# 				if web_soup.find(id=post_page_nav.split('=')[1]) != None:
# 					page_nav = web_soup.find(id=post_page_nav.split('=')[1]).find_all('a')
#
# 			if len(post_main_content.split('=')[0]) > 3:
# 				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('form') != []:
# 					form = 'form'
#
# 				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('embed') != []:
# 					embed = 'embed'
#
# 				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('iframe') != []:
# 					iframe = 'iframe'
#
# 				if len(post_calendar.split('=')[0]) > 3:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_calendar.split('=')[1]) != []:
# 						calendar = 'calendar'
# 				elif len(post_calendar.split('=')[0]) > 0 and len(post_calendar.split('=')[0]) < 4:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_calendar.split('=')[1]) != []:
# 						calendar = 'calendar'
#
# 				if len(post_staff_dir.split('=')[0]) > 3:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_staff_dir.split('=')[1]) != []:
# 						staff = 'staff'
# 				elif len(post_staff_dir.split('=')[0]) > 0 and len(post_staff_dir.split('=')[0]) < 4:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_staff_dir.split('=')[1]) != []:
# 						staff = 'staff'
#
# 				if len(post_news.split('=')[0]) > 3:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_news.split('=')[1]) != []:
# 						news = 'news'
# 				elif len(post_news.split('=')[0]) > 0 and len(post_news.split('=')[0]) < 4:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_news.split('=')[1]) != []:
# 						news = 'news'
#
# 				if len(post_col1.split('=')[0]) > 3:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1]) != '':
# 						col1 = web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1])
# 						col1 = get_column(col1, splitter)
# 					else:
# 						issue_pages_counter = 1
# 				else:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1]) != '':
# 						col1 = web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1])
# 						col1 = get_column(col1, splitter)
# 					else:
# 						issue_pages_counter = 1
#
# 				if len(post_col2.split('=')[0]) > 3:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1]) != '':
# 						col4 = web_soup.find(class_=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1])
# 						col4 = get_column(col4, splitter)
# 				else:
# 					if web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1]) != '':
# 						col4 = web_soup.find(class_=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1])
# 						col4 = get_column(col4, splitter)
#
# 			else:
# 				if web_soup.find(id=post_main_content.split('=')[1]).find_all('form') != []:
# 					form = 'form'
#
# 				if web_soup.find(id=post_main_content.split('=')[1]).find_all('embed') != []:
# 					embed = 'embed'
#
# 				if web_soup.find(id=post_main_content.split('=')[1]).find_all('iframe') != []:
# 					iframe = 'iframe'
#
# 				if len(post_calendar.split('=')[0]) > 3:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_calendar.split('=')[1]) != []:
# 						calendar = 'calendar'
# 				elif len(post_calendar.split('=')[0]) > 0 and len(post_calendar.split('=')[0]) < 4:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_calendar.split('=')[1]) != []:
# 						calendar = 'calendar'
#
# 				if len(post_staff_dir.split('=')[0]) > 3:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_staff_dir.split('=')[1]) != []:
# 						staff = 'staff'
# 				elif len(post_staff_dir.split('=')[0]) > 0 and len(post_staff_dir.split('=')[0]) < 4:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_staff_dir.split('=')[1]) != []:
# 						staff = 'staff'
#
# 				if len(post_news.split('=')[0]) > 3:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_news.split('=')[1]) != []:
# 						news = 'news'
# 				elif len(post_news.split('=')[0]) > 0 and len(post_news.split('=')[0]) < 4:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_news.split('=')[1]) != []:
# 						news = 'news'
#
# 				if len(post_col1.split('=')[0]) > 3:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1]) != '':
# 						col1 = web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col1.split('=')[1])
# 						col1 = get_column(col1, splitter)
# 					else:
# 						issue_pages_counter = 1
# 				else:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1]) != '':
# 						col1 = web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col1.split('=')[1])
# 						col1 = get_column(col1, splitter)
# 					else:
# 						issue_pages_counter = 1
#
# 				if len(post_col2.split('=')[0]) > 3:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1]) != '':
# 						col4 = web_soup.find(id=post_main_content.split('=')[1]).find(class_=post_col2.split('=')[1])
# 						col4 = get_column(col4, splitter)
# 				else:
# 					if web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1]) != '':
# 						col4 = web_soup.find(id=post_main_content.split('=')[1]).find(id=post_col2.split('=')[1])
# 						col4 = get_column(col4, splitter)
#
# 			col1 = str(col1)
# 			col4 = str(col4)
#
# 			if len(col1) > 150000:
# 				col1 = 'Flagged'
# 				col2 = 'This page has too much content'
# 				col3 = ''
# 				col4 = ''
# 				col_num = '2'
# 				issue_pages_counter = 1
# 			elif len(col1) > 100000:
# 				col2 = col1[50000:100000]
# 				col3 = col1[100000:]
# 				col1 = col1[:50000]
# 				col_num = '3'
# 			elif len(col1) > 50000:
# 				col2 = col1[50000:]
# 				col1 = col1[:50000]
# 				col_num = '2'
#
# 			if len(col4) > 50000:
# 				col1 = 'Flagged'
# 				col2 = 'This page has too much content'
# 				col3 = ''
# 				col4 = ''
# 				col_num = '2'
# 				issue_pages_counter = 1
# 			elif len(col4) > 0:
# 				col_num = '4'
#
# 			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter
#
# 		# else:
# 		except:
# 			issue_pages_counter = 1
#
# 			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter
#
#
# 	post_sites = request.POST.get('site')
# 	post_sitemap = request.POST.get('main_nav')
# 	post_list_items = request.POST.get('list_items')
# 	post_school = request.POST.get('school_title')
# 	post_main_content = request.POST.get('main_content')
# 	post_page_nav = request.POST.get('page_nav')
# 	post_col1 = request.POST.get('col1')
# 	post_col2 = request.POST.get('col2')
# 	post_calendar = request.POST.get('calendar')
# 	post_staff_dir = request.POST.get('staff_dir')
# 	post_news = request.POST.get('news')
# 	# extra_links = request.POST.get('extra')
# 	print('>>', post_sites, post_sitemap, post_list_items, post_school, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news)
#
# 	# Process inputs
# 	all_sites = post_sites.split(',')
#
# 	start_time = time()
# 	mainfolder = all_sites[0].split('.')[1]
# 	filepath = Path(f'static/files/{mainfolder}')
# 	filepath.mkdir(parents=True, exist_ok=True)
# 	files = {}
#
# 	with open('static/files/' + mainfolder + '/report.csv', 'w', encoding='utf-8') as csv_report:
# 		csv_report = csv.writer(csv_report)
#
# 		for site in all_sites:
# 			page_counter = 0
# 			issue_pages_counter = 0
#
# 			splitter = site.split('/')
# 			page = requests.get(site).content
# 			soup = BeautifulSoup(page, 'html.parser')
#
# 			if len(post_sitemap.split('=')[0]) > 3:
# 				sitemap = soup.find(class_=post_sitemap.split('=')[1])
# 				list_items = sitemap.select(post_list_items)
# 			elif len(post_sitemap.split('=')[0]) > 0 and len(post_sitemap.split('=')[0]) < 4:
# 				sitemap = soup.find(id=post_sitemap.split('=')[1])
# 				list_items = sitemap.select(post_list_items)
# 			else:
# 				list_items = soup.find_all(class_=post_list_items)
#
# 			if len(post_school.split('=')[0]) > 3:
# 				school = soup.find(class_=post_school.split('=')[1]).get_text()
# 			else:
# 				school = soup.find(id=post_school.split('=')[1]).get_text()
#
# 			if len(school) > 30:
# 				school_name = str(school[:30]).lower().replace(' ', '_').replace('.', '')
# 			else:
# 				school_name = str(school).lower().replace(' ', '_').replace('.', '')
#
# 			csv_report.writerow(['School name', school_name])
#
# 			with open('static/files/' + mainfolder + '/' + school_name + '.csv', 'w', encoding='utf-8') as csv_main:
# 				csv_writer = csv.writer(csv_main)
# 				csv_writer.writerow(['Link to page', 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Column Count', 'Column 1', 'Column 2', 'Column 3', 'Column 4', 'Meta title', 'Meta keywords', 'Meta description'])
#
# 				for item in list_items[1:]:
# 					group_links = item.find_all('a')
#
# 					for link in group_links:
# 						external_link = False
#
# 						if link.get('href')[0] == '#':
# 							page_link = '#'
# 						elif len(link.get('href')) > 1 and link.get('href')[:2] == '//':
# 							page_link = splitter[0] + link.get('href')
# 						elif link.get('href')[0] == '/':
# 							page_link = splitter[0] + '//' + splitter[2] + link.get('href')
# 						elif link.get('href')[:4] == 'http':
# 							page_link = link.get('href')
#
# 							if link.get('href').find(splitter[2].split('.')[1]) == -1:
# 								external_link = True
# 						else:
# 							page_link = splitter[0] + '//' + splitter[2] + '/' + link.get('href')
#
# 						if not external_link:
# 							page_counter += 1
# 							col1, col2, col3, col4, col_num, nav_sec, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news, splitter)
# 							issue_pages_counter += content_ipc
#
# 							if group_links[0].get_text() != link.get_text():
# 								csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), '', '', col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])
# 							else:
# 								csv_writer.writerow([str(page_link), str(group_links[0].get_text()), '', '', '', col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])
#
# 							if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
# 								csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])
#
# 							if nav_sec != None and nav_sec != '' and nav_sec != []:
# 								for nav_link in nav_sec:
# 									external_link = False
#
# 									if nav_link.get('href')[0] == '#':
# 										page_link = '#'
# 									elif len(nav_link.get('href')) > 1 and nav_link.get('href')[:2] == '//':
# 										page_link = splitter[0] + nav_link.get('href')
# 									elif nav_link.get('href')[0] == '/':
# 										page_link = splitter[0] + '//' + splitter[2] + nav_link.get('href')
# 									elif nav_link.get('href')[:4] == 'http':
# 										page_link = nav_link.get('href')
#
# 										if nav_link.get('href').find(splitter[2].split('.')[1]) == -1:
# 											external_link = True
# 									else:
# 										page_link = splitter[0] + '//' + splitter[2] + '/' + nav_link.get('href')
#
# 									if not external_link:
# 										page_counter += 1
# 										nav_col1, nav_col2, nav_col3, nav_col4, nav_col_num, _, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_main_content, post_page_nav, post_col1, post_col2, post_calendar, post_staff_dir, post_news, splitter)
# 										issue_pages_counter += content_ipc
# 										csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), str(nav_link.get_text()), '', nav_col_num, nav_col1, nav_col2, nav_col3, nav_col4, meta_title, meta_keywords, meta_desc])
#
# 										if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
# 											csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])
# 									else:
# 										csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), str(nav_link.get_text()), '', '1', 'Linked page', '', '', '', '', '', ''])
# 						else:
# 							csv_writer.writerow([str(page_link), str(group_links[0].get_text()), str(link.get_text()), '', '', '1', 'Linked page', '', '', '', '', '', ''])
#
# 				csv_report.writerow([])
# 				csv_report.writerow(['Pages scraped', page_counter])
# 				csv_report.writerow(['Issues', issue_pages_counter])
# 				csv_report.writerow([])
# 				csv_report.writerow([])
# 				csv_report.writerow([])
#
# 			files[school_name + '.csv'] = 'static/files/' + mainfolder + '/' + school_name + '.csv'
# 			print('Finished:', site)
#
# 	files['report.csv'] = 'static/files/' + mainfolder + '/report.csv'
# 	print('Finished:', round((time() - start_time) / 3600, 2), 'h')
#
# 	context = {
# 		'files': files,
# 		'time': str(round((time() - start_time) / 3600, 2)) + ' hours'
# 	}
#
# 	return render(request, 'pages/export_page.html', context)


def results_schoolpointe_view(request):
	def clean_tags(tags):
		for tag in tags:
			tag.attrs.clear()

			if tag.contents == [] or (len(tag.contents) < 2 and tag.contents[0] == '\xa0'):
				tag.decompose()


	def remove_tags(text):
		div = re.compile(r'<div[^>]+>')
		dive = re.compile(r'<div+>')
		divc = re.compile(r'</div+>')
		link = re.compile(r'<link[^>]+>')
		section = re.compile(r'<section[^>]+>')
		sectione = re.compile(r'<section+>')
		sectionc = re.compile(r'</section+>')
		article = re.compile(r'<article[^>]+>')
		articlee = re.compile(r'<article+>')
		articlec = re.compile(r'</article+>')
		span = re.compile(r'<span+>')
		spane = re.compile(r'<span[^>]+>')
		spanc = re.compile(r'</span+>')
		font = re.compile(r'<font+>')
		fonte = re.compile(r'<font[^>]+>')
		fontc = re.compile(r'</font+>')

		text = div.sub('', text)
		text = dive.sub('', text)
		text = divc.sub('', text)
		text = link.sub('', text)
		text = section.sub('', text)
		text = sectione.sub('', text)
		text = sectionc.sub('', text)
		text = article.sub('', text)
		text = article.sub('', text)
		text = articlec.sub('', text)
		text = span.sub('', text)
		text = spane.sub('', text)
		text = spanc.sub('', text)
		text = font.sub('', text)
		text = fonte.sub('', text)
		text = fontc.sub('', text)
		text = re.sub('<!--|-->', '', text)

		return text.strip()


	def get_column(col):
		col_images = col.find_all('img')
		col_anchors = col.find_all('a')
		col_tags = col.find_all(['article', 'b', 'button', 'col', 'colgroup', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'ul', 'ol', 'li', 'p', 'table', 'td', 'th', 'tr', 'strong', 'input', 'label', 'legend', 'fieldset'])
		clean_tags(col_tags)

		while col.script != None:
			col.script.decompose()

		while col.style != None:
			col.style.decompose()

		while col.nav != None:
			col.nav.decompose()

		for image in col_images:
			try:
				if image.get('src') != None and image.get('src') != '':
					src = image['src']

					if 'alt' in image.attrs:
						alt = image['alt']
						image.attrs.clear()
						image['alt'] = alt
					else:
						image.attrs.clear()
						image['alt'] = 'alt-text'

					image['src'] = src

				else:
					image.attrs.clear()

				image['id'] = ''
				image['role'] = 'presentation'
				image['style'] = ''
				image['width'] = '250'

			except:
				pass
				# print('Image:', image)

		for anchor in col_anchors:
			try:
				if anchor.get('href') != None and anchor.get('href') != '':
					href = anchor['href']
					anchor.attrs.clear()
					anchor['href'] = href

					if anchor.get('href')[:4] != 'http' and anchor.get('href').find('.pdf') == -1 and anchor.get('href').find('.txt') == -1\
					and anchor.get('href').find('.xls') == -1 and anchor.get('href').find('.xlsx') == -1\
					and anchor.get('href').find('.doc') == -1 and anchor.get('href').find('.docx') == -1\
					and anchor.get('href').find('.ppt') == -1 and anchor.get('href').find('.pptx') == -1:
						anchor.string = f'INTERNAL LINK {anchor.string}'

			except:
				pass
				# print('Anchor:', anchor)

		col = remove_tags(str(col))

		return col


	def get_content(web_page, post_main_content, post_calendar, post_staff_dir, post_news):
		col1 = 'Flagged'
		col2, col3, col4 = '', '', ''
		col_num = '1'
		page_nav = None
		meta_title = ''
		meta_keywords = ''
		meta_desc = ''
		form = ''
		embed = ''
		iframe = ''
		calendar = ''
		staff = ''
		news = ''
		issue_pages_counter = 0
		# print(web_page)

		# if web_page != '#':
		try:
			web_link = requests.get(web_page, timeout=5).content
			web_soup = BeautifulSoup(web_link, 'html.parser')

			if web_soup.find_all('meta', attrs={'name': 'title'}) != []:
				meta_title = str(web_soup.find_all('meta', attrs={'name': 'title'}))

			if web_soup.find_all('meta', attrs={'name': 'keywords'}) != []:
				meta_keywords = str(web_soup.find_all('meta', attrs={'name': 'keywords'}))

			if web_soup.find_all('meta', attrs={'name': 'description'}) != []:
				meta_desc = str(web_soup.find_all('meta', attrs={'name': 'description'}))

			# if len(post_page_nav.split('=')[0]) > 3:
			# 	if web_soup.find(class_=post_page_nav.split('=')[1]) != None:
			# 		page_nav = web_soup.find(class_=post_page_nav.split('=')[1]).find_all('a')
			# elif len(post_page_nav.split('=')[0]) > 0 and len(post_page_nav.split('=')[0]) < 4:
			# 	if web_soup.find(id=post_page_nav.split('=')[1]) != None:
			# 		page_nav = web_soup.find(id=post_page_nav.split('=')[1]).find_all('a')

			if len(post_main_content.split('=')[0]) > 3:
				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('form') != []:
					form = 'form'

				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('embed') != []:
					embed = 'embed'

				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('iframe') != []:
					iframe = 'iframe'

				if len(post_calendar.split('=')[0]) > 3:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_calendar.split('=')[1]) != []:
						calendar = 'calendar'
				elif len(post_calendar.split('=')[0]) > 0 and len(post_calendar.split('=')[0]) < 4:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_calendar.split('=')[1]) != []:
						calendar = 'calendar'

				if len(post_staff_dir.split('=')[0]) > 3:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_staff_dir.split('=')[1]) != []:
						staff = 'staff'
				elif len(post_staff_dir.split('=')[0]) > 0 and len(post_staff_dir.split('=')[0]) < 4:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_staff_dir.split('=')[1]) != []:
						staff = 'staff'

				if len(post_news.split('=')[0]) > 3:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(class_=post_news.split('=')[1]) != []:
						news = 'news'
				elif len(post_news.split('=')[0]) > 0 and len(post_news.split('=')[0]) < 4:
					if web_soup.find(class_=post_main_content.split('=')[1]).find_all(id=post_news.split('=')[1]) != []:
						news = 'news'

				if web_soup.find(class_=post_main_content.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]) != '':
					col1 = web_soup.find(class_=post_main_content.split('=')[1])
					col1 = get_column(col1)
				else:
					issue_pages_counter = 1

			else:
				if web_soup.find(id=post_main_content.split('=')[1]).find_all('form') != []:
					form = 'form'

				if web_soup.find(id=post_main_content.split('=')[1]).find_all('embed') != []:
					embed = 'embed'

				if web_soup.find(id=post_main_content.split('=')[1]).find_all('iframe') != []:
					iframe = 'iframe'

				if len(post_calendar.split('=')[0]) > 3:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_calendar.split('=')[1]) != []:
						calendar = 'calendar'
				elif len(post_calendar.split('=')[0]) > 0 and len(post_calendar.split('=')[0]) < 4:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_calendar.split('=')[1]) != []:
						calendar = 'calendar'

				if len(post_staff_dir.split('=')[0]) > 3:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_staff_dir.split('=')[1]) != []:
						staff = 'staff'
				elif len(post_staff_dir.split('=')[0]) > 0 and len(post_staff_dir.split('=')[0]) < 4:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_staff_dir.split('=')[1]) != []:
						staff = 'staff'

				if len(post_news.split('=')[0]) > 3:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(class_=post_news.split('=')[1]) != []:
						news = 'news'
				elif len(post_news.split('=')[0]) > 0 and len(post_news.split('=')[0]) < 4:
					if web_soup.find(id=post_main_content.split('=')[1]).find_all(id=post_news.split('=')[1]) != []:
						news = 'news'

				if web_soup.find(id=post_main_content.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]) != '':
					col1 = web_soup.find(id=post_main_content.split('=')[1])
					col1 = get_column(col1)
				else:
					issue_pages_counter = 1

			col1 = str(col1)

			if len(col1) > 200000:
				col1 = 'Flagged'
				col2 = 'This page has too much content'
				col3 = ''
				col4 = ''
				col_num = '2'
				issue_pages_counter = 1
			elif len(col1) > 150000:
				col2 = col1[50000:100000]
				col3 = col1[100000:150000]
				col4 = col1[150000:]
				col1 = col1[:50000]
				col_num = '4'
				issue_pages_counter = 1
			elif len(col1) > 100000:
				col2 = col1[50000:100000]
				col3 = col1[100000:]
				col1 = col1[:50000]
				col_num = '3'
			elif len(col1) > 50000:
				col2 = col1[50000:]
				col1 = col1[:50000]
				col_num = '2'

			if len(col4) > 50000:
				col1 = 'Flagged'
				col2 = 'This page has too much content'
				col3 = ''
				col4 = ''
				col_num = '2'
				issue_pages_counter = 1
			elif len(col4) > 0:
				col_num = '4'

			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter

		# else:
		except:
			issue_pages_counter = 1

			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter


	post_sites = request.POST.get('site')
	post_sitemap = request.POST.get('main_nav')
	post_school = request.POST.get('school_title')
	post_main_content = request.POST.get('main_content')
	# post_page_nav = request.POST.get('page_nav')
	post_calendar = request.POST.get('calendar')
	post_staff_dir = request.POST.get('staff_dir')
	post_news = request.POST.get('news')
	print('>>', post_sites, post_sitemap, post_school, post_main_content, post_calendar, post_staff_dir, post_news)

	# Process inputs
	all_sites = post_sites.split(',')
	schools = post_school.split(',')

	start_time = time()
	mainfolder = all_sites[0].split('.')[1]
	filepath = Path(f'static/files/{mainfolder}')
	filepath.mkdir(parents=True, exist_ok=True)
	files = {}

	with open(f'static/files/{mainfolder}/report.csv', 'w', encoding='utf-8') as csv_report:
		csv_report = csv.writer(csv_report)
		s = 0

		for site in all_sites:
			s += 1
			page_counter = 0
			issue_pages_counter = 0
			split_slash = site.split('/')
			split_dot = site.split('.')
			split_mixed = site.split('/')[2].split('.')
			all_links = []

			page = requests.get(site).content
			soup = BeautifulSoup(page, 'html.parser')

			if len(post_sitemap.split('=')[0]) > 3:
				sitemap = soup.find(class_=post_sitemap.split('=')[1])
			else:
				sitemap = soup.find(id=post_sitemap.split('=')[1])

			list_items = sitemap.select('ul > li')
			school_name = f'{split_dot[1]}_{schools[s - 1]}'
			csv_report.writerow(['School name', school_name])

			with open(f'static/files/{mainfolder}/{school_name}.csv', 'w', encoding='utf-8') as csv_main:
				csv_writer = csv.writer(csv_main)
				csv_writer.writerow(['Link to page', 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Column Count', 'Column 1', 'Column 2', 'Column 3', 'Column 4', 'Meta title', 'Meta keywords', 'Meta description'])

				for i, item in enumerate(list_items):
					group_links = item.find_all('a')
					t1 = str(group_links[0].get_text()) if len(group_links) > 0 and len(group_links[0].get_text()) > 0 else f'No tier {i}'

					for link in group_links:
						href = link.get('href')

						if len(href) > 1 and href[:2] == '//':
							page_link = f'{split_slash[0]}{href}'
						elif len(href) > 0 and href[0] == '/':
							page_link = f'{split_slash[0]}//{split_slash[2]}{href}'
						elif len(href) > 4 and href[:4] == 'http':
							page_link = href
						else:
							page_link = f'{split_slash[0]}//{split_slash[2]}/{href}'

						if page_link not in all_links:
							all_links.append(page_link)

							if href.find('.pdf') > -1 or href.find('.mp3') > -1 or href.find('.wmv') > -1 or href.find('.mp4') > -1 or href.find('.docx') > -1 or href.find('.xlsx') > -1 or href.find('.pptx') > -1\
							or href.find('.doc') > -1 or href.find('.xls') > -1 or href.find('.ppt') > -1 or href.find('.jsp') > -1 or href.find('.m4v') > -1 or href.find('.mkv') > -1:
								csv_writer.writerow([str(page_link), t1, str(link.get_text()), '', '', '1', 'Linked file', '', '', '', '', '', ''])
							else:
								if href.find('http') > -1 and href.split('/')[2].find(split_dot[1]) == -1:
									csv_writer.writerow([str(page_link), t1, str(link.get_text()), '', '', '1', 'Linked page', '', '', '', '', '', ''])
								else:
									page_counter += 1
									col1, col2, col3, col4, col_num, nav_sec, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_main_content, post_calendar, post_staff_dir, post_news)
									issue_pages_counter += content_ipc

									if group_links[0].get_text() != link.get_text():
										csv_writer.writerow([str(page_link), t1, str(link.get_text()), '', '', col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])
									else:
										csv_writer.writerow([str(page_link), t1, '', '', '', col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])

									if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
										csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])

									if nav_sec != None and nav_sec != '' and nav_sec != []:
										for nav_link in nav_sec:
											href = nav_link.get('href')

											if len(href) > 1 and href[:2] == '//':
												page_link = f'{split_slash[0]}{href}'
											elif len(href) > 0 and href[0] == '/':
												page_link = f'{split_slash[0]}//{split_slash[2]}{href}'
											elif len(href) > 4 and href[:4] == 'http':
												page_link = href
											else:
												page_link = f'{split_slash[0]}//{split_slash[2]}/{href}'

											if href.find('.pdf') > -1 or href.find('.mp3') > -1 or href.find('.wmv') > -1 or href.find('.mp4') > -1 or href.find('.docx') > -1 or href.find('.xlsx') > -1 or href.find('.pptx') > -1\
											or href.find('.doc') > -1 or href.find('.xls') > -1 or href.find('.ppt') > -1 or href.find('.jsp') > -1 or href.find('.m4v') > -1 or href.find('.mkv') > -1:
												csv_writer.writerow([str(page_link), t1, str(link.get_text()), '', '', '1', 'Linked file', '', '', '', '', '', ''])
											else:
												if href.find('http') > -1 and href.split('/')[2].find(split_dot[1]) == -1:
													csv_writer.writerow([str(page_link), t1, str(link.get_text()), '', '', '1', 'Linked page', '', '', '', '', '', ''])
												else:
													page_counter += 1
													nav_col1, nav_col2, nav_col3, nav_col4, nav_col_num, _, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_main_content, post_calendar, post_staff_dir, post_news)
													issue_pages_counter += content_ipc
													csv_writer.writerow([str(page_link), t1, str(link.get_text()), str(nav_link.get_text()), '', nav_col_num, nav_col1, nav_col2, nav_col3, nav_col4, meta_title, meta_keywords, meta_desc])

													if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
														csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])

				csv_report.writerow([])
				csv_report.writerow(['Pages scraped', page_counter])
				csv_report.writerow(['Issues', issue_pages_counter])
				csv_report.writerow([])
				csv_report.writerow([])
				csv_report.writerow([])

			files[f'{school_name}.csv'] = f'static/files/{mainfolder}/{school_name}.csv'
			print('Finished:', site)

	files['report.csv'] = f'static/files/{mainfolder}/report.csv'
	print('Finished:', round((time() - start_time) / 60, 2), 'minutes')

	context = {
		'files': files,
		'time': f'{str(round((time() - start_time) / 60, 2))} minutes'
	}

	return render(request, 'pages/export_page.html', context)


def extra_links_view(request):
	return render(request, 'pages/schoolpointe.html')


def results_extra_links_view(request):
	def clean_tags(tags):
		for tag in tags:
			tag.attrs.clear()

			if tag.contents == [] or (len(tag.contents) < 2 and tag.contents[0] == '\xa0'):
				tag.decompose()


	def remove_tags(text):
		div = re.compile(r'<div[^>]+>')
		dive = re.compile(r'<div+>')
		divc = re.compile(r'</div+>')
		link = re.compile(r'<link[^>]+>')
		section = re.compile(r'<section[^>]+>')
		sectione = re.compile(r'<section+>')
		sectionc = re.compile(r'</section+>')
		article = re.compile(r'<article[^>]+>')
		articlee = re.compile(r'<article+>')
		articlec = re.compile(r'</article+>')
		span = re.compile(r'<span+>')
		spane = re.compile(r'<span[^>]+>')
		spanc = re.compile(r'</span+>')
		font = re.compile(r'<font+>')
		fonte = re.compile(r'<font[^>]+>')
		fontc = re.compile(r'</font+>')

		text = div.sub('', text)
		text = dive.sub('', text)
		text = divc.sub('', text)
		text = link.sub('', text)
		text = section.sub('', text)
		text = sectione.sub('', text)
		text = sectionc.sub('', text)
		text = article.sub('', text)
		text = article.sub('', text)
		text = articlec.sub('', text)
		text = span.sub('', text)
		text = spane.sub('', text)
		text = spanc.sub('', text)
		text = font.sub('', text)
		text = fonte.sub('', text)
		text = fontc.sub('', text)
		text = re.sub('<!--|-->', '', text)

		return text.strip()


	def get_column(col):
		col_images = col.find_all('img')
		col_anchors = col.find_all('a')
		col_tags = col.find_all(['article', 'b', 'button', 'col', 'colgroup', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'ul', 'ol', 'li', 'p', 'table', 'td', 'th', 'tr', 'strong', 'input', 'label', 'legend', 'fieldset'])
		clean_tags(col_tags)

		while col.script != None:
			col.script.decompose()

		while col.style != None:
			col.style.decompose()

		while col.nav != None:
			col.nav.decompose()

		for image in col_images:
			try:
				if image.get('src') != None and image.get('src') != '':
					src = image['src']

					if 'alt' in image.attrs:
						alt = image['alt']
						image.attrs.clear()
						image['alt'] = alt
					else:
						image.attrs.clear()
						image['alt'] = 'alt-text'

					image['src'] = src

				else:
					image.attrs.clear()

				image['id'] = ''
				image['role'] = 'presentation'
				image['style'] = ''
				image['width'] = '250'

			except:
				pass
				# print('Image:', image)

		for anchor in col_anchors:
			try:
				if anchor.get('href') != None and anchor.get('href') != '':
					href = anchor['href']
					anchor.attrs.clear()
					anchor['href'] = href

					if anchor.get('href')[:4] != 'http' and anchor.get('href').find('.pdf') == -1 and anchor.get('href').find('.txt') == -1\
					and anchor.get('href').find('.xls') == -1 and anchor.get('href').find('.xlsx') == -1\
					and anchor.get('href').find('.doc') == -1 and anchor.get('href').find('.docx') == -1\
					and anchor.get('href').find('.ppt') == -1 and anchor.get('href').find('.pptx') == -1:
						anchor.string = f'INTERNAL LINK {anchor.string}'

			except:
				pass
				# print('Anchor:', anchor)

		col = remove_tags(str(col))

		return col


	def get_content(web_page, post_main_content):
		col1 = 'Flagged'
		col2, col3, col4 = '', '', ''
		col_num = '1'
		page_nav = None
		meta_title = ''
		meta_keywords = ''
		meta_desc = ''
		form = ''
		embed = ''
		iframe = ''
		calendar = ''
		staff = ''
		news = ''
		issue_pages_counter = 0
		# print(web_page)

		# if web_page != '#':
		try:
			web_link = requests.get(web_page, timeout=5).content
			web_soup = BeautifulSoup(web_link, 'html.parser')

			if web_soup.find_all('meta', attrs={'name': 'title'}) != []:
				meta_title = str(web_soup.find_all('meta', attrs={'name': 'title'}))

			if web_soup.find_all('meta', attrs={'name': 'keywords'}) != []:
				meta_keywords = str(web_soup.find_all('meta', attrs={'name': 'keywords'}))

			if web_soup.find_all('meta', attrs={'name': 'description'}) != []:
				meta_desc = str(web_soup.find_all('meta', attrs={'name': 'description'}))

			if len(post_main_content.split('=')[0]) > 3:
				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('form') != []:
					form = 'form'

				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('embed') != []:
					embed = 'embed'

				if web_soup.find(class_=post_main_content.split('=')[1]).find_all('iframe') != []:
					iframe = 'iframe'

				if web_soup.find(class_=post_main_content.split('=')[1]) != None and web_soup.find(class_=post_main_content.split('=')[1]) != '':
					col1 = web_soup.find(class_=post_main_content.split('=')[1])
					col1 = get_column(col1)
				else:
					issue_pages_counter = 1

			else:
				if web_soup.find(id=post_main_content.split('=')[1]).find_all('form') != []:
					form = 'form'

				if web_soup.find(id=post_main_content.split('=')[1]).find_all('embed') != []:
					embed = 'embed'

				if web_soup.find(id=post_main_content.split('=')[1]).find_all('iframe') != []:
					iframe = 'iframe'

				if web_soup.find(id=post_main_content.split('=')[1]) != None and web_soup.find(id=post_main_content.split('=')[1]) != '':
					col1 = web_soup.find(id=post_main_content.split('=')[1])
					col1 = get_column(col1)
				else:
					issue_pages_counter = 1

			col1 = str(col1)

			if len(col1) > 200000:
				col1 = 'Flagged'
				col2 = 'This page has too much content'
				col3 = ''
				col4 = ''
				col_num = '2'
				issue_pages_counter = 1
			elif len(col1) > 150000:
				col2 = col1[50000:100000]
				col3 = col1[100000:150000]
				col4 = col1[150000:]
				col1 = col1[:50000]
				col_num = '4'
				issue_pages_counter = 1
			elif len(col1) > 100000:
				col2 = col1[50000:100000]
				col3 = col1[100000:]
				col1 = col1[:50000]
				col_num = '3'
			elif len(col1) > 50000:
				col2 = col1[50000:]
				col1 = col1[:50000]
				col_num = '2'

			if len(col4) > 50000:
				col1 = 'Flagged'
				col2 = 'This page has too much content'
				col3 = ''
				col4 = ''
				col_num = '2'
				issue_pages_counter = 1
			elif len(col4) > 0:
				col_num = '4'

			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter

		# else:
		except:
			issue_pages_counter = 1

			return col1, col2, col3, col4, col_num, page_nav, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, issue_pages_counter


	post_sites = request.POST.get('site')
	post_school = request.POST.get('school_title')
	post_main_content = request.POST.get('main_content')
	print('>>', post_sites, post_school, post_main_content)

	# Process inputs
	all_sites = post_sites.split(',')

	start_time = time()
	mainfolder = all_sites[0].split('.')[1]
	filepath = Path(f'static/files/{mainfolder}')
	filepath.mkdir(parents=True, exist_ok=True)
	files = {}

	with open(f'../f_web_interface/static/files/{mainfolder}/report.csv', 'w', encoding='utf-8') as csv_report:
		csv_report = csv.writer(csv_report)

		page_counter = 0
		issue_pages_counter = 0
		split_slash = all_sites[0].split('/')
		split_dot = all_sites[0].split('.')
		split_mixed = all_sites[0].split('/')[2].split('.')
		school_name = post_school

		csv_report.writerow(['School name', school_name])

		with open(f'../f_web_interface/static/files/{mainfolder}/{school_name}.csv', 'w', encoding='utf-8') as csv_main:
			csv_writer = csv.writer(csv_main)
			csv_writer.writerow(['Link to page', 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5', 'Column Count', 'Column 1', 'Column 2', 'Column 3', 'Column 4', 'Meta title', 'Meta keywords', 'Meta description'])

			for link in all_sites:
				tiers = link.split('/')
				t1, t2, t3, t4, t5 = '', '', '', '', ''
				if len(tiers) == 4:
					t1 = tiers[-1].capitalize()
				elif len(tiers) == 5:
					t1 = tiers[-2].capitalize()
					t2 = tiers[-1].capitalize()
				elif len(tiers) == 6:
					t1 = tiers[-3].capitalize()
					t2 = tiers[-2].capitalize()
					t3 = tiers[-1].capitalize()
				elif len(tiers) == 7:
					t1 = tiers[-4].capitalize()
					t2 = tiers[-3].capitalize()
					t3 = tiers[-2].capitalize()
					t4 = tiers[-1].capitalize()
				elif len(tiers) == 8:
					t1 = tiers[-5].capitalize()
					t2 = tiers[-4].capitalize()
					t3 = tiers[-3].capitalize()
					t4 = tiers[-2].capitalize()
					t5 = tiers[-1].capitalize()
				else:
					print(len(tiers))

				page_link = link

				page_counter += 1
				col1, col2, col3, col4, col_num, nav_sec, meta_title, meta_keywords, meta_desc, form, embed, iframe, calendar, staff, news, content_ipc = get_content(page_link, post_main_content)
				issue_pages_counter += content_ipc

				csv_writer.writerow([str(page_link), t1, t2, t3, t4, t5, col_num, col1, col2, col3, col4, meta_title, meta_keywords, meta_desc])

				if form != '' or embed != '' or iframe != '' or calendar != '' or staff != '' or news != '':
					csv_report.writerow([str(page_link), form, embed, iframe, calendar, staff, news])

			csv_report.writerow([])
			csv_report.writerow(['Pages scraped', page_counter])
			csv_report.writerow(['Issues', issue_pages_counter])
			csv_report.writerow([])
			csv_report.writerow([])
			csv_report.writerow([])

			files[f'{school_name}.csv'] = f'static/files/{mainfolder}/{school_name}.csv'
			print('Finished:', site)

	files['report.csv'] = f'static/files/{mainfolder}/report.csv'
	print('Finished:', round((time() - start_time) / 60, 2), 'minutes')

	context = {
		'files': files,
		'time': f'{str(round((time() - start_time) / 60, 2))} minutes'
	}

	return render(request, 'pages/export_page.html', context)


def vpn_view(request):
	return render(request, 'pages/vpn.html')


def files_view(request):
	file_paths = glob.glob(f'static/files/**/*.csv')
	file_names = [x.split('/')[-2] + ' - ' + x.split('/')[-1] for x in file_paths]
	files = {}

	for index, path in enumerate(file_paths):
		files[path] = file_names[index]

	context = {
		'files': files
	}

	return render(request, 'pages/files.html', context)
