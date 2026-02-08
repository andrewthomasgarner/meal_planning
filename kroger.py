import urllib3
import json
from datetime import datetime, timezone
import csv


def get_circular_list():
    
    http = urllib3.PoolManager()

    base_url = "https://api.kroger.com/digitalads/v1/circulars"

    # Duplicate query parameters must be manually constructed
    query = "filter.tags=SHOPPABLE&filter.tags=CLASSIC_VIEW"
    url = f"{base_url}?{query}"

    # Build the X-Laf-Object header JSON
    x_laf_object = [
        {
            "modality": {
                "type": "PICKUP",
                "handoffLocation": {
                    "storeId": "",
                    "facilityId": ""
                },
                "handoffAddress": {
                    "address": {
                        "addressLines": [""],
                        "cityTown": "",
                        "name": "",
                        "postalCode": "90210",
                        "stateProvince": "CA",
                        "residential": False,
                        "countryCode": "US"
                    },
                    "location": {
                        "lat": 34.052235,
                        "lng": -118.243683
                    }
                }
            },
            "sources": [{"storeId": "", "facilityId": ""}],
            "assortmentKeys": ["8bed50f2-c6cb-4daf-9c3d-e3bb28a691e0"],
            "listingKeys": [""]
        }
    ]

    headers = {
        "Host": "api.kroger.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Laf-Object": json.dumps(x_laf_object),
        "X-Kroger-Channel": "WEB",
        "X-Call-Origin": '{"component":"weekly ad","page":"weekly ad"}',
        "X-Modality": '{"type":"PICKUP","locationId":""}',
        "X-Modality-Type": "PICKUP",
        "X-Facility-Id": "",
        "Origin": "https://www.fredmeyer.com",
        "Referer": "https://www.fredmeyer.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Te": "trailers"
    }

    response = http.request(
        "GET",
        url,
        headers=headers
    )

    data = json.loads(response.data.decode("utf-8"))["data"]

    today = datetime.now(timezone.utc)

    print(response.status)

    print(data)

    matching_ids = []

    for item in data:
        if item.get("circularType") != "weeklyAd":
            continue

        start_str = item.get("eventStartDate")
        if not start_str:
            continue

        start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))

        if start_dt > today:
            matching_ids.append(item["id"])
        else:
            end_str = item.get("eventEndDate")
            if not end_str:
                continue

            end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))

            if end_dt >= today:
                matching_ids.append(item["id"])
    
    set_cookie_headers = response.headers.getlist("Set-Cookie")

    print(matching_ids[0])
    return matching_ids[0], set_cookie_headers

def get_weeklyad(ad_id, cookies):

    http = urllib3.PoolManager()

    url = (
        "https://www.fredmeyer.com/atlas/v1/shoppable-weekly-deals/deals"
        "?filter.circularId=485bf749-4fda-4891-ac17-b64e5503db5b"
        "&filter.adGroupName.like="
        "&fields.ads="
    )

    headers = {
        "Host": "www.fredmeyer.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Laf-Object": '[{"modality":{"type":"PICKUP","handoffLocation":{"storeId":"70100457","facilityId":"5226"},"handoffAddress":{"address":{"addressLines":["21045 Bothell Everett Hwy"],"cityTown":"Bothell","name":"Bothell","postalCode":"98021","stateProvince":"WA","residential":false,"countryCode":"US"},"location":{"lat":47.807305,"lng":-122.205946}}},"sources":[{"storeId":"70100457","facilityId":"5226"}],"assortmentKeys":["8bed50f2-c6cb-4daf-9c3d-e3bb28a691e0"],"listingKeys":["70100457"]}]',
        "X-Kroger-Channel": "WEB",
        "X-Call-Origin": '{"component":"weekly ad","page":"weekly ad"}',
        "X-Modality": '{"type":"PICKUP","locationId":"70100457"}',
        "X-Modality-Type": "PICKUP",
        "X-Facility-Id": "70100457",
        
    }

    response = http.request("GET", url, headers=headers)

    data = json.loads(response.data.decode("utf-8"))['data']
    #print(data)
    deals = json.dumps(data['shoppableWeeklyDeals']['ads'], indent=2)
    with open("kroger_weeklyad.json", "w") as f:
        f.write(deals)

    fields = [
        "mainlineCopy",
        "underlineCopy",
        "salePrice",
        "disclaimer",
        "department",
        "price",
        "savings"
    ]

    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)

        for item in json.loads(deals):
        # Skip anything that isn't a dictionary
            if not isinstance(item, dict):
                continue

            # Safely extract department
            dept = ""
            depts = item.get("departments")

            if isinstance(depts, list) and len(depts) > 0:
                first = depts[0]
                if isinstance(first, dict):
                    dept = first.get("department", "")

            row = [
                item.get("mainlineCopy", ""),
                item.get("underlineCopy", ""),
                item.get("salePrice", ""),
                item.get("disclaimer", ""),
                dept,
                item.get("price", ""),
                item.get("savings", "")
            ]

            writer.writerow(row)

    print("CSV created successfully.")

if __name__ == "__main__":
    ad_id, cookies = get_circular_list()
    get_weeklyad(ad_id, cookies)