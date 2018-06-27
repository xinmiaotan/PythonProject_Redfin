import requests
from bs4 import BeautifulSoup
import re
import os
import random
import time
import datetime
from collections import deque
import json

#location for file downloaded
HOME_DIR = "/Users/xinmiaotan/PycharmProjects/PythonBerkeley/data"

#URL
BASE_URL = "https://www.redfin.com"
SEED_URL = "https://www.redfin.com/CA/Fremont/35451-Eden-Ct-94536/home/1063545"
#INSERT_URL ="/CA/Fremont/468-Pomo-Ct-94539/home/1694984"
#INSERT_URL ="/CA/Fremont/45445-Potawatami-Dr-94539/home/1093415"

#Variable needed for analysis
valid_attributes = {"geo_position":"geo.position",
                    "geo_region":"geo.region",
                    "state":"twitter:text:state_code",
                    "city":"twitter:text:city",
                    "zipcode":"twitter:text:zip",
                    "beds":"twitter:text:beds",
                    "baths":"twitter:text:baths",
                    "sqft":"twitter:text:sqft",
                    "url":"twitter:url:landing_url",
                    "title":"twitter:title",
                    "description":"description",
                    "street_address":"twitter:text:street_address"}

DELAY_RANGE = (1, 3)

#download redfin content, return content
def download_content(url):
    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Mozilla/5.0',})
    response = requests.get(url, headers=headers)
    content = response.text.encode("utf8")
    return content

#get url link
def get_key_from_url(url):
    m = re.match("https://www.redfin.com(.*)", url)
    if m is not None:
        return m.groups()[0]
    return None

def get_price_and_date(soup):
    try:
        for sale_record in soup.body.findAll('tr', {"class": "sold-row PropertyHistoryEventRow"}):
            date_col, _, price_col, _ = sale_record.children
            sale_date = datetime.datetime.strptime(date_col.text, "%b %d, %Y").strftime("%Y-%m-%d")
            sale_price = re.sub(r'[^\d.]', '', price_col.text)
            return sale_date, sale_price
    except Exception:
        return None, None
    return None, None

#extract useful data -- return matadata
def parse_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    metadata = {}

    for attribute, tag_name in valid_attributes.items():
        attribute_value = soup.find("meta", {"name": tag_name})
        if attribute_value is not None:
            metadata[attribute] = attribute_value["content"]
    if "geo_position" not in metadata:
        lat_and_long = soup.body.findAll(text=re.compile('latLong'), limit=1)
        if lat_and_long is not None and len(lat_and_long) >= 1:
            data = lat_and_long[0]
            data = data.replace("\n", "")
            m = re.match(r'.*?latLong.*?:({.*?}),', data)
            if m is not None:
                lat_long_value = m.groups()[0]
                n = re.match(r'.*latitude.*:(.*?),.*longitude.*:(.*?)}', lat_long_value)
                if n is not None:
                    latitude = n.groups()[0]
                    longitude = n.groups()[1]
                    metadata['geo_position'] = "%s;%s" % (latitude, longitude)

    neighbours = []
    for neighbour in soup.find_all('a', {"class": "nearby-home-address"}):
        neighbours.append(neighbour['href'])
    metadata["neighbours"] = neighbours
    sale_date, sale_price = get_price_and_date(soup)
    if sale_price is not None and sale_date is not None:
        metadata["sale_price"] = sale_price
        metadata["sale_date"] = sale_date
    # Otherwise falls back to other way
    else:
        price_and_date = soup.body.findAll(text=re.compile('salePrice'), limit=1)
        if price_and_date is not None and len(price_and_date) >= 1:
            data = price_and_date[0]
            data = data.replace("\n", "")
            m = re.match(r'.*?salePrice.*?:(\d+)', data)
            if m is not None:
                metadata["sale_price"] = int(m.groups()[0])
            m = re.match(r'.*?saleDate.*?:(\d+)', data)
            if m is not None:
                ts = int(float(m.groups()[0]) / 1000.0)
                metadata["sale_date"] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

    key = get_key_from_url(metadata['url'])
    if key is not None:
        metadata["key"] = key
    estimate = soup.find("p", {"class": "AvmGraphLegend-activeValue"})
    if estimate is not None:
        metadata["estimate_price"] = int(re.sub(r'[^\d.]', '', estimate.text))

    for element in soup.find_all("div", {"class": "table-row"}):
        children_data = list(element.children)
        if children_data is not None and len(children_data) == 2:
            label_name, label_value = list(element.children)
            if label_name.text == "Style":
                metadata['style'] = label_value.text
            if label_name.text == 'Year Built':
                metadata['year_built'] = label_value.text

    # clean up and convert string to int for a few attributes
    if "beds" in metadata and metadata["beds"] != "-":
        metadata['beds'] = float(metadata["beds"])
    if "baths" in metadata and metadata["baths"] != "-":
        metadata['baths'] = float(metadata["baths"])
    if "zipcode" in metadata:
        metadata['zipcode'] = int(metadata["zipcode"])
    if "sqft" in metadata and metadata["sqft"] != "-":
        metadata['sqft'] = int(re.sub(r'[^\d.]', '', metadata['sqft']))

    return metadata

#save metadata in home dir
def persist_to_file(key, content_data, meta_data):
    k = key.replace("/", "*")
    meta_data_path = "%s/%s*meta" % (HOME_DIR, k)
    with open(meta_data_path, "w") as f:
        json.dump(meta_data, f)
    content_path = "%s/%s" % (HOME_DIR, k)
    with open(content_path, "w") as f:
        f.write(str(content_data))


def load_recorded():
    files = os.listdir(HOME_DIR)
    result=[]
    for f in files:
        if os.path.isfile(os.path.join(HOME_DIR, f)) and f.find("meta") == -1:
            f_url=f.replace("*", "/")
            result.append(f_url)
    return result

def read_from_file(key):
    k = key.replace("/", "*")
    meta_data_path = "%s/%s*meta" % (HOME_DIR, k)
    if os.path.isfile(meta_data_path):
        with open(meta_data_path) as f:
            meta_data = json.load(f)
        return meta_data
    content_path = "%s/%s" % (HOME_DIR, k)
    with open(content_path) as f:
        data = f.read()
        meta_data = parse_content(data)
    return meta_data

def get_url_from_key(key):
    return "%s/%s" % (BASE_URL, key)


#start
record_list = load_recorded()
if record_list[-1] == ".DS_Store":
    record_list.remove(".DS_Store")
current_queue =  deque()
metadata_map = {}
for item in record_list:
     if item != '.DS_Store':
         metadata_map[item] = read_from_file(item)

if len(record_list) == 0:
    content = download_content(SEED_URL)
    metadata = parse_content(content)
    key = metadata["key"]
    persist_to_file(key, content, metadata)
    current_queue.extend([neighbour for neighbour in metadata["neighbours"] if neighbour not in metadata_map and metadata["city"] == "Fremont"])
    metadata_map[key] = metadata
    print("Start processing")
else:
    i = 0
    while i < len(record_list):
        key = record_list[i]
        metadata = read_from_file(key)
        current_queue.extend([neighbour for neighbour in metadata["neighbours"] if neighbour not in metadata_map and metadata["city"] == "Fremont"])
        i = i + 1

#current_queue.extendleft([INSERT_URL])
while len(current_queue) >= 1:
    current_key = current_queue.popleft()
    if current_key in metadata_map:
        continue
    content = download_content(get_url_from_key(current_key))
    metadata = parse_content(content)
    persist_to_file(current_key, content, metadata)
    metadata_map[current_key] = metadata
    current_queue.extendleft([neighbour for neighbour in metadata["neighbours"] if neighbour not in metadata_map and metadata["city"] == "Fremont"])
    delay = random.randint(DELAY_RANGE[0], DELAY_RANGE[1])
    print("Finished processing %s , waitting for %d seconds" % (current_key, delay))
    time.sleep(delay)





