from multiprocessing.pool import ThreadPool
from pathlib import Path
from tqdm import tqdm
from urllib.parse import urljoin

from .base import Crawler
from .utils import make_valid_windows_filename, mass_download_url_list, uniq, write_dict_as_csv

import re
import os
import json

class PortfolioCrawler(Crawler):
	"""
	Implements mass downloading and uploading functionality for eMed portfolio
	"""
	emed_cats = {
		1: "Assignment",
		2: "Category 2",
		3: "Category 3",
		4: "Evidence of Achievement",
		5: "Exempted Assignment",
		6: "Group Project",
		7: "ILP",
		8: "Learning Plan",
		9: "Negotiated Assignment",
		10: "Category 10",
		11: "Portfolio Examination",
		12: "Category 12",
		13: "Report",
		14: "Supplementary Assignment",
		15: "Supportive Evidence",
		16: "Upload Assessment"
	}

	def __init__(self, url="https://emed.med.unsw.edu.au") -> None:
		login_settings = json.load(open("login_settings.json"))
		self._username, self._password = login_settings["username"], login_settings["password"]
		super(PortfolioCrawler, self).__init__(url, self._username, self._password)

	def _login(self, url, username, password):
		# first find the login form on the page
		self.navigate(url)
		prespecified_vals = {"Username": username, "Password": password,
			"RedirectTo": "/Portfolio.nsf/My%20Submissions%20-%20By%20Type?OpenView"}
		self.fill_first_form_on_current_page(**prespecified_vals)

	def download_all(self):
		print("Requesting portfolio submissions...")
		# so as it turns out you don't even need to go through their stupid-ass interface
		# you can just query the backend directly and it will answer
		# expand all is too slow so just query them individually
		download_paths = []
		self.navigate(urljoin(self.url, "/Portfolio.nsf/ViewAgent?OpenAgent&view=MySubsByType&entryNum=0&showCollapse=&restrictToCategory="))
		numcatdivs = self.current_page.html.find("div[id^='numCat']")
		catnums = [int(i.attrs.get("id", "-1").strip("numCatHTML")) for i in numcatdivs]
		# skip 17 (uncategorised) as there doesn't seem to be anything in it
		catnums = [i for i in catnums if i not in set([5, 17, -1])]
		cat_progress = tqdm(catnums, position=0)
		for cat in cat_progress:
			cat_progress.set_description(f"Now processing '{self.emed_cats.get(cat, 'Category {0}'.format(cat))}'")
			self.navigate(urljoin(self.url, "/Portfolio.nsf/ViewAgent?OpenAgent&view=MySubsByType&entryNum={0}&showCollapse=&restrictToCategory=".format(cat)))
			links = set([a.attrs["href"] for a in self.current_page.html.find("a")])
			links_progress = tqdm(links, position=1, leave=False)
			for l in links_progress:
				self.navigate(urljoin(self.url, l+"&AutoFramed&BaseTarget=NotesView"))
				title = self.current_page.html.xpath("//td[contains(.,'Title')]/following-sibling::*", first=True).text
				links_progress.set_description(title.replace("\n", ""))
				file_dl_links = [a for a in self.current_page.html.find("a")[2:] if re.match(r"^/?portfolio", a.attrs.get("href", "").lower())]
				save_folder = os.path.join("downloaded", 
					make_valid_windows_filename(self.emed_cats[cat]),
					make_valid_windows_filename(title))
				for file_dl_link in file_dl_links:
					dl_path = urljoin(self.url, file_dl_link.attrs["href"])
					Path(save_folder).mkdir(parents=True, exist_ok=True)
					save_path = os.path.join(save_folder, file_dl_link.text)
					download_paths.append((save_path, dl_path))
				# get metadata as a json file
				csv_path = os.path.join(save_folder, "metadata.csv")
				metadata = dict()
				for data_row in self.current_page.html.find("table tr"):
					# why tf do you have to do this, like seriously can't requests_html get their shit together already
					tds = data_row.xpath("./*/td")
					# i prefer to use a continue statement here but it screws up tqdm if you do
					# nope tqdm is still fucked
					if len(tds) == 2:
						k_cell, v_cell = tds
						k = k_cell.text.strip()
						v = v_cell.text.strip()
						if k.lower() != "assessment file":
							metadata[k] = v
				write_dict_as_csv(metadata, csv_path)
		download_paths = uniq(download_paths)
		with open("dl_list.txt", "w") as dl_ofp:
			for save_path, dl_url in download_paths:
				print(save_path, dl_url, file=dl_ofp)
		self.mass_download_url_list(download_paths)

	def mass_download_url_list(self, url_list: "list[tuple[str, str]]"):
		return mass_download_url_list(url_list, session=self.session)

	def upload_all(self, path):
		raise NotImplementedError