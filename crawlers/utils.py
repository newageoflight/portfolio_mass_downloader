from functools import partial
from multiprocessing.pool import ThreadPool
from pathlib import Path
from tqdm import tqdm

import csv
import os
import re
import requests

def make_valid_windows_filename(s):
    """
    Make a string into a valid Windows filename
    """
    return re.sub(r"[^\w\-_\. ]", "_", s)

def write_dict_as_csv(d, outfile_dest):
    # sometimes it fails to create the save path in the main function, so create it here again just for safety
    if not os.path.exists(outfile_dest):
        if not os.path.exists(os.path.dirname(outfile_dest)):
            Path(os.path.dirname(outfile_dest)).mkdir(parents=True, exist_ok=True)
    with open(outfile_dest, "w") as ofp:
        writer = csv.writer(ofp)
        for k, v in d.items():
            writer.writerow([k, v])

# Thanks to
# https://markhneedham.com/blog/2018/07/15/python-parallel-download-files-requests/
# https://gist.github.com/wy193777/0e2a4932e81afc6aa4c8f7a2984f34e2
def download_url(pair: "tuple[str, str]", session=None):
    """
    Download a file from a URL. Takes a pair of strings (save_path, download_url)
    """
    if not session:
        session = requests.session()
    save_path, url = pair
    if not os.path.exists(save_path):
        if not os.path.exists(os.path.dirname(save_path)):
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
        r = session.get(url, stream=True)
        filesize = int(r.headers.get("content-length", 0))
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                pbar = tqdm(r.iter_content(chunk_size=1024), leave=False, desc=os.path.basename(save_path),
                    unit="B", unit_scale=True, total=filesize)
                for chunk in pbar:
                    f.write(chunk)
                    pbar.update(1024)
    return save_path

def mass_download_url_list(url_list: "list[tuple[str, str]]", session=None):
    print("Downloading files...")
    if not session:
        session = requests.session()
    dl_func = partial(download_url, session=session)
    return list(tqdm(ThreadPool(8).imap_unordered(dl_func, url_list), total=len(url_list)))

def uniq(seq):
    """
    Based on speed optimisations from here:
    https://www.peterbe.com/plog/fastest-way-to-uniquify-a-list-in-python-3.6
    """
    return list(dict.fromkeys(seq))