import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import re
import ast
import pandas

global base_url


def get_properties_by_page(page):
    main_request = requests.get(page)
    print("FETCHED: " + page)
    main_content = main_request.content

    main = BeautifulSoup(main_content, "html.parser")

    regex = re.compile('infinite-item property-card*')
    all_properties = main.find_all("div", {"class": regex})

    prop_list = []
    for item in all_properties:
        dict = {}
        address = item.find("div", {"class": "property-address"})
        if address is not None:
            dict["Address"] = address.text.strip()
        else:
            dict["Address"] = None

        locality = item.find("div", {"class": "property-city"})
        if locality is not None:
            dict["Locality"] = locality.text.strip()
        else:
            dict["Locality"] = None

        price = item.find("a", {"class": "listing-price"})
        if price is not None:
            dict["Price"] = price.text.strip()
        else:
            dict["Price"] = None

        beds = item.find("div", {"class": "property-beds"})
        if beds is not None:
            dict["Beds"] = beds.find("strong").text.strip()
        else:
            dict["Beds"] = None

        square_feet = item.find("div", {"class": "property-sqft"})
        if square_feet is not None:
            dict["Area"] = square_feet.find("strong").text.strip()
        else:
            dict["Area"] = None

        baths = item.find("div", {"class": "property-baths"})
        if baths is not None:
            dict["Baths"] = baths.find("strong").text.strip()
        else:
            dict["Baths"] = None

        half_baths = item.find("div", {"class": "property-half-baths"})
        if half_baths is not None:
            dict["Half Baths"] = half_baths.find("strong").text.strip()
        else:
            dict["Half Baths"] = None

        features_link = price["href"]
        features_request = requests.get(base_url + features_link)
        print("FETCHED: " + features_link)
        features_content = features_request.content

        features = BeautifulSoup(features_content, "html.parser")
        feature_group = features.find("ul", {"class": "property-features"})

        for feature_item in feature_group.find_all("li"):
            feature_name = feature_item.find("b").text.strip()
            if (feature_name == "Lot Size"):
                dict["Lot Size"] = feature_item.text.strip().split(": ")[1]

        print("Finished: " + features_link)
        prop_list.append(dict)

    print("Finished: " + page)
    return prop_list


path = input("Please enter search path. Example: /real-estate/washington-nj/LCNJWASHINGTON\n")

t0 = datetime.now()
base_url = "http://www.century21.com"

main_request = requests.get(base_url + path)
main_content = main_request.content

main = BeautifulSoup(main_content, "html.parser")
total_results = main.find("div", {"class": "results-label"}).find("strong").text.strip()
number_results = int(re.sub("[^0-9]", "", total_results))

pages = []
for res in range(0, number_results, 20):
    pages.append(base_url + path + "/?s=" + str(res) + "&o=listingdate-desc")

pool = ThreadPool(16)
properties_list = pool.map(get_properties_by_page, pages)
pool.close()
pool.join()

flattened = [val for sublist in properties_list for val in sublist]
print("Number of properties: " + str(len(flattened)))

df = pandas.DataFrame(flattened)
df.to_excel("Output.xlsx")

t1 = datetime.now()

delta = t1 - t0
print("Finished crawling! Total time: " + str(delta.total_seconds()) + " seconds")
