import base64
import requests
import json
import pandas as pd
from operator import itemgetter

# URL for flask app
addr = 'http://127.0.0.1:5000'
submit_url = addr + '/submit'

# prepare headers for http request
content_type = 'image/jpg'
headers = {'content-type': content_type}

###### INPUTS FROM THE FRONT-END #########
image_name = "image.jpg"
entries = [
{
    "column": "Name",
    "coords": [50,50,500,500],
    "position": "top-center",
    "color": (0,0,0),
    "text_size": 20,
    "font": "arial.ttf"
},
{
    "column": "Date",
    "coords": [300,50,800,400],
    "position": "center",
    "color": (75,200,50),
    "text_size": 40,
    "font": "arial.ttf"
}]
##########################################

def format_entries(df, all_columns, entries):
    new_jobs = []
    last_row = df.count().max()
    for row in range(0,last_row):
        text_and_rects = []
        for col in all_columns:
            i = next((index for (index, d) in enumerate(entries) if d["column"] == col), None)
            new_text_and_rect = {
                "text": str(df[col][row]),
                "coords": entries[i]['coords'],
                "position": entries[i]['position'],
                "color": entries[i]['color'],
                "text_size": entries[i]['text_size'],
                "font": entries[i]['font']
            }
            text_and_rects.append(new_text_and_rect)
        new_jobs.append(text_and_rects)
    return new_jobs

with open(image_name, "rb") as image2string:
    image_string = base64.b64encode(image2string.read()).decode('utf-8')

df = pd.read_excel('excel_file.xlsx')

jobs = []
all_columns = []
for entry in entries:
    all_columns.append(entry["column"])

jobs = format_entries(df,all_columns,entries)

data = {
    "image_string": image_string,
    "jobs": jobs
}

json_object = json.dumps(data, indent=4)

# send http request with image and receive response
response = requests.post(submit_url, data=json_object, headers=headers)

# decode response
print(json.loads(response.text))