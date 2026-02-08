import json
import csv
import requests

POSTAL_CODE = "90210"  # your ZIP

def get_flyers(zipcode):
    url = f"https://backflipp.wishabi.com/flipp/flyers?postal_code={zipcode}"
    r = requests.get(url)
    r.raise_for_status()
    print(r)
    return r.json().get("flyers", "[]") 

def get_safeway_flyer(flyers):
    flyer_list = []
    for f in flyers:
        with open("flyers.json", "w") as f_out:
            json.dump(flyers, f_out, indent=2)
        try:
            if f.get("merchant", "").lower() == "safeway":
                flyer_list.append(f.get("id"))
        except:
            continue
    return flyer_list

def get_items(items_url):
    base_url = "dam.flippenterprise.net"
    deals = []
    for u in items_url:
        r = requests.get(f"https://{base_url}/flyerkit/publication/{u}/products?display_type=all&locale=en&access_token=7749fa974b9869e8f57606ac9477decf")
        r.raise_for_status()
        deals.append(r.json())
    return deals

def export_csv(items, filename="safeway_flipp_weekly_ad.csv"):
    with open("items.json", "w") as f_out:
        json.dump(items, f_out, indent=2)
    counter = 0
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "description", "category", "price", "price detail", "valid from", "valid to", "store"])
        for flyers in items:
            for item in flyers:
                w.writerow([
                    item.get("name"),
                    item.get("description"),                    
                    item.get("categories", ""),
                    item.get("price_text"),
                    item.get("post_price_text"),
                    item.get("valid_from"),
                    item.get("valid_to"),
                    "Safeway"
                ])
                counter += 1
    print(f"Exported {counter} items to {filename}")

def main():
    flyers = get_flyers(POSTAL_CODE)
    safeway = get_safeway_flyer(flyers)
    print(safeway)
    items = get_items(safeway)
    export_csv(items)

if __name__ == "__main__":
    main()