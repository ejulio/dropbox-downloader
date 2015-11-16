#! /bin/env python3

import argparse
import sys
import os
import mechanicalsoup
import pickle
import requests
from urllib.parse import unquote_plus
import queue
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("dropbox_url")
parser.add_argument("output_dir")
parser.add_argument("-c" , "--cookies")
args = parser.parse_args()

session = requests.Session()
if args.cookies:
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for c in cookies:
        session.cookies.set(c["name"], c["value"])
browser = mechanicalsoup.Browser(session)

pages = queue.Queue()
pages.put((args.dropbox_url, args.output_dir))

while not pages.empty():
    (url, path) = pages.get()
    page = browser.get(url)

    password_input = page.soup.find("form", id="password-form")
    if password_input:
        print("Password form detected. Use the get-cookies.py script to",
            "generate cookies for your password then rerun this script with",
            "the --cookies flag.", file=sys.stderr)
        sys.exit(1)

    download_button = page.soup.find(id="default_content_download_button")
    preview_box = page.soup.find(class_="preview-box")

    if download_button or preview_box:
        print("Downloading", path, file=sys.stderr)
        download_url = url.rsplit("?", 1)[0] + "?dl=1"
        r = browser.session.get(download_url, stream=True)
        with open(path, "wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        continue

    print("Creating and entering directory", path, file=sys.stderr)
    if not os.path.exists(path):
        os.mkdir(path)
    nodes = list(set([n.attrs["href"] for n in
            page.soup.find_all("a", class_="file-link")]))
    for n in nodes:
        pages.put((n, "%s/%s"
                % (path, unquote_plus(n.rsplit("/", 1)[1].rsplit("?", 1)[0]))))
