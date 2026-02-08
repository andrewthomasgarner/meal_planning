import requests
import base64
import json
import ollama

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:27b"   # or any model you have pulled

def encode_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

file_path = "/Path/To/Ads Shopping/safeway_flipp_weekly_ad.csv"   # your file here
encoded = encode_file(file_path)
#print(encoded[:100])

csv_text = open(file_path).read()

OLLAMA_CONTEXT_LEN = 32768

payload = {
    "model": MODEL,
    "prompt": f"""We are a family of 4 looking to plan our meals for the week. 
        Can you suggest some meal ideas based on the items in this ad? 
        Suggest meals that provide leftovers. 
        Go easy on meat and onions. 
        Skip fish and pork. 
        When reasonable, prefer raw ingredients over processed foods.
        We can make bread and dough from scratch.
        Pantry staples we have include: rice, pasta, flour, sugar, salt, pepper, olive oil, Black Beans, refried beans, frozen whole kernel corn, tomatoe sauce, tomate paste, enchilada sauce, spaghetti sauce and a variety of spices.
        We have the following weekly ad from our local grocery store. Here is the ad: {csv_text}""",
    "options": {
        "max_tokens": OLLAMA_CONTEXT_LEN,
        "temperature": 0.1,
        "context_len": OLLAMA_CONTEXT_LEN,
        "num_ctx": OLLAMA_CONTEXT_LEN
    },
    "files": [
        {
            "name": "output.csv",
            "data": encoded
        }
    ],
    "stream": False
}

response = requests.post(OLLAMA_URL, json=payload)
print(response.json()["response"])
