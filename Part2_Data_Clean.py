from bs4 import BeautifulSoup
import re
import datetime
import json
import numpy as np
import os
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import pylab as plb


#location for file downloaded
HOME_DIR = "/Users/xinmiaotan/PycharmProjects/PythonBerkeley/data"

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
#load content
def load_content():
    files = os.listdir(HOME_DIR)
    result=[]
    for f in files:
        if os.path.isfile(os.path.join(HOME_DIR, f)) and f.find("meta") == -1:
            result.append(f)
    return result

#read in content and return to meta_data
def read_from_content(key):
    content_path = "%s/%s" % (HOME_DIR, key)
    with open(content_path) as f:
        data = f.read()
        meta_data = pull_info(data)
    return meta_data

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

#pull useful information from content: geo position need to regenerate
def pull_info(content):
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
        metadata["sale_price"] = float(sale_price)
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

#save meta_data
def persist_to_file(key, meta_data):
    meta_data_path = "%s/%s*meta" % (HOME_DIR, key)
    with open(meta_data_path, "w") as f:
        json.dump(meta_data, f)

def read_from_meta(key):
    meta_data_path = "%s/%s*meta" % (HOME_DIR, key)
    meta_data = None
    if os.path.isfile(meta_data_path):
        with open(meta_data_path) as f:
            meta_data = json.load(f)
        return meta_data

record_list = load_content()
if record_list[-1] == ".DS_Store":
    record_list.remove(".DS_Store")

for item in record_list:
    metadata=read_from_content(item)
    metadata["key"] = item
    #save to xxx*mata
    persist_to_file(item, metadata)

metadata_map = {}
metadata_map_for_analysis = {}
#read from metadata
#exclude data without geo_position, last-sold price, last-sold date, property type
for item in record_list:
    #read meta data
    metadata_map[item] = read_from_meta(item)
    if 'sale_price' in metadata_map[item] and \
                    metadata_map[item]['sale_price'] >0 and \
                    'sale_date' in metadata_map[item] and \
                    metadata_map[item]['city'] == 'Fremont' and \
                    metadata_map[item]['sqft'] != '-' and \
                    'zipcode' in metadata_map[item] and \
                    'geo_position' in metadata_map[item] and \
                    metadata_map[item]['sale_date'][:4] in {'2013','2014','2015','2016','2017'} and \
                    metadata_map[item]['style'] in {'Single Family Residential', 'Townhouse', 'Condo/Co-op'}:
        #create metadata_map_for_analysis
        metadata_map_for_analysis[item]=metadata_map[item]
        metadata_map_for_analysis[item]["year"]=metadata_map[item]['sale_date'][:4]
        metadata_map_for_analysis[item]["month"] = metadata_map[item]['sale_date'][5:7]
        metadata_map_for_analysis[item]["year_month"] = metadata_map[item]['sale_date'][:7]
        metadata_map_for_analysis[item]['price_per_sqft'] = metadata_map[item]['sale_price'] / metadata_map[item]['sqft']
        sep = metadata_map_for_analysis[item]['geo_position'].index(';')
        metadata_map_for_analysis[item]['lat'] = float(metadata_map[item]['geo_position'][0:sep])
        metadata_map_for_analysis[item]['lon'] = float(metadata_map[item]['geo_position'][sep+1:])

def save_metadata(dataname, data):
    meta_data_path = "%s/all*%s" % (HOME_DIR, dataname)
    with open(meta_data_path, "w") as f:
        json.dump(data, f)

save_metadata('metadata_map',metadata_map)
save_metadata('metadatamap_for_analysis',metadata_map_for_analysis)
