from requests_html import HTMLSession
from lxml import html
from tqdm import tqdm
from urllib.parse import urljoin

import traceback

class Crawler(object):
	"""Fundamental crawler class for scraping webpages"""
	def __init__(self, url, username=None, password=None):
		super(Crawler, self).__init__()
		self.url = url
		self._username = username
		self._password = password
		self.session = HTMLSession()
		self.current_page = None
		# if for some reason the HTML will not render correctly
		# then lxml is used to render the tree as a backup
		self.current_tree = None

	def __enter__(self):
		if self._username and self._password:
			self._login(self.url, self._username, self._password)
		else:
			self.navigate(self.url)

	def __exit__(self, exc_type, exc_val, tb):
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_val, tb)
		self.session.close()

	def _login(self, url, username, password):
		raise NotImplementedError

	def _referer(self):
		return {
			"Referer": self.url,
   			"Accept": "image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*",
   			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-AU",
			"Connection": "Keep-Alive",
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
		}

	def navigate(self, url, render=False, *args, **kwargs):
		self.url = url
		self.current_page = self.session.get(self.url, headers=self._referer(), *args, **kwargs)
		self.current_page.encoding = "utf-8"
		if render:
			self.current_page.html.render()
		self.current_tree = html.fromstring(self.current_page.text)

	def navigate_post(self, url, render=False, *args, **kwargs):
		self.url = url
		self.current_page = self.session.post(self.url, headers=self._referer(), *args, **kwargs)
		self.current_page.encoding = "utf-8"
		if render:
			self.current_page.html.render()
		self.current_tree = html.fromstring(self.current_page.text)

	def browse(self, url, render=False, *args, **kwargs):
		result = self.session.get(url, headers=self._referer(), *args, **kwargs)
		result.encoding = 'utf-8'
		if render:
			result.html.render()
		tree = html.fromstring(result.text)
		return (result, tree)

	def browse_post(self, url, render=False, *args, **kwargs):
		result = self.session.post(url, headers=self._referer(), *args, **kwargs)
		result.encoding = 'utf-8'
		if render:
			result.html.render()
		tree = html.fromstring(result.text)
		return (result, tree)

	def render(self, *args, **kwargs):
		return self.current_page.html.render(*args, **kwargs)

	def fill_first_form_on_current_page(self, **prespecified_vals):
		form = self.current_page.html.find("form", first=True)
		inputs = form.find("input")
		form_data = {}
		for i in inputs:
			if prespecified_vals.get(i.attrs.get("name")):
				form_data[i.attrs["name"]] = prespecified_vals[i.attrs["name"]]
			elif i.attrs.get("type") == "hidden":
				form_data[i.attrs["name"]] = i.attrs["value"]
			elif i.attrs.get("type") != "submit":
				value = input(f"Enter value of '{i.attrs['name']}': ")
				form_data[i.attrs["name"]] = value

		if form.attrs["method"] == "post":
			self.navigate_post(urljoin(self.url, form.attrs["action"]), data=form_data)
		elif form.attrs["method"] == "get":
			self.navigate(urljoin(self.url, form.attrs["action"]), params=form_data)
