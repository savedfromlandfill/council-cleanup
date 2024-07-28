import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from collections import OrderedDict

url = "https://www.brisbane.qld.gov.au/clean-and-green/rubbish-tips-and-bins/rubbish-collections/kerbside-large-item-collection-service"

# get suburbs
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
suburbs = soup.find(id="edit-suburb").find_all("option")

# get dates
querystring = "?ajax_form=1&_wrapper_format=drupal_ajax"
xmlheader = {"x-requested-with": "XMLHttpRequest"}
formdata = {
    "suburb": "",
    "form_id": "webform_submission_kerbside_collection_search_node_28246_add_form",
}

kerbside = {}  # dictionary/list to store dates and suburbs in

# loop through each suburb and pull the date from council website
for suburb in suburbs:
    if suburb.text[0] != "-":
        formdata["suburb"] = suburb.text.strip()

        response = requests.post(url + querystring, headers=xmlheader, data=formdata)

        data = json.loads(response.content)
        soup = BeautifulSoup(data[3]["data"], "html.parser")


        dateStr = (soup.text.replace("Collection starts week commencing:", "")
                .replace("\n", "")
                .strip())
        
        # council starting add " and " in some date texts and including two years of collection for some suburbs
        dates = dateStr.split(" and ")
        
        for date in dates:
            kdate = datetime.strptime(
                str(date),
                "%d %B %Y",
            )

            print(suburb.text.strip() + ", " + kdate.strftime("%Y-%m-%d"))

            if kerbside and kdate in kerbside:
                kerbside[kdate].append(suburb.text.strip())
            else:
                kerbside[kdate] = [suburb.text.strip()]

# sort by date instead of suburb
kerbside = OrderedDict(sorted(kerbside.items()))

with open("kerbside.csv", "w") as f:
    for item in kerbside:
        for suburb in kerbside[item]:
            line = item.strftime("%Y-%m-%d") + ", " + suburb
            f.write(line + "\n")
            print(line)
