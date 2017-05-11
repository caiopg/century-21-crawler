import requests
from bs4 import BeautifulSoup
import re
import ast
import pandas


path = input("Please enter search path. Example: /real-estate/washington-nj/LCNJWASHINGTON\n")

base_url = "http://www.century21.com"

main_request = requests.get(base_url + path)
main_content = main_request.content

main = BeautifulSoup(main_content, "html.parser")
total_results = main.find("div", {"class":"results-label"}).find("strong").text.strip()
number_results = int(re.sub("[^0-9]", "", total_results))

prop_list = []
item_number = 0
for res in range(0,  number_results, 20):
    page_site = base_url +  path + "/?s=" + str(res) + "&o=listingdate-desc"
    print(page_site)

    main_request = requests.get(page_site)
    main_content = main_request.content

    main = BeautifulSoup(main_content, "html.parser")

    regex = re.compile('infinite-item property-card*')
    all_properties = main.find_all("div", {"class":regex})

    for item in all_properties:
        dict = {}
        address = item.find("div", {"class":"property-address"})
        if address != None:
            dict["Address"] = address.text.strip()
        else:
            dict["Address"] = None

        locality = item.find("div", {"class":"property-city"})
        if locality != None:
            dict["Locality"] = locality.text.strip()
        else:
            dict["Locality"] = None

        price = item.find("a", {"class":"listing-price"})
        if price != None:
            dict["Price"] =  price.text.strip()
        else:
            dict["Price"] = None

        beds = item.find("div", {"class":"property-beds"})
        if beds != None:
            dict["Beds"] = beds.find("strong").text.strip()
        else:
            dict["Beds"] = None

        square_feet = item.find("div", {"class":"property-sqft"})
        if square_feet != None:
            dict["Area"] = square_feet.find("strong").text.strip()
        else:
            dict["Area"] = None

        baths = item.find("div", {"class":"property-baths"})
        if baths != None:
            dict["Baths"] = baths.find("strong").text.strip()
        else:
            dict["Baths"] = None

        half_baths = item.find("div", {"class":"property-half-baths"})
        if half_baths != None:
            dict["Half Baths"] = half_baths.find("strong").text.strip()
        else:
            dict["Half Baths"] = None

        features_link = price["href"]
        features_request = requests.get(base_url + features_link)
        features_content = features_request.content

        features = BeautifulSoup(features_content, "html.parser")
        feature_group = features.find("ul", {"class":"property-features"})

        for feature_item in feature_group.find_all("li"):
            feature_name = feature_item.find("b").text.strip()
            if(feature_name == "Lot Size"):
                dict["Lot Size"] =feature_item.text.strip().split(": ")[1]

        prop_list.append(dict)

        item_number += 1
        print("Item " + str(item_number) + " finished.")

df = pandas.DataFrame(prop_list)
df.to_excel("Output.xlsx")
print("End")
