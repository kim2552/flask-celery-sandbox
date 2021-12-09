import base64
import requests
import json
import pandas as pd

# URL for flask app
addr = 'http://127.0.0.1:5000'
submit_url = addr + '/submit'

# prepare headers for http request
content_type = 'image/jpg'
headers = {'content-type': content_type}

coords = [50,50,500,500]
position = "top-center"
color = (0,0,0)
text_size = 20
font="arial.ttf"

with open("image.jpg", "rb") as image2string:
    image_string = base64.b64encode(image2string.read()).decode('utf-8')

entries = [
{
    "column": "Name",
    "coords": coords,
    "position": position,
    "color": color,
    "text_size": text_size,
    "font": font
},
{
    "column": "Date",
    "coords": coords,
    "position": position,
    "color": color,
    "text_size": text_size,
    "font": font
}]

def format_entries(column, entry):
    new_jobs = []
    for text in column:
        new_job = {
            "text": str(text),
            "coords": entry['coords'],
            "position": entry['position'],
            "color": entry['color'],
            "text_size": entry['text_size'],
            "font": entry['font']
        }
        new_jobs.append(new_job)
    return new_jobs

df = pd.read_excel('excel_file.xlsx')

jobs = []
for entry in entries:
    new_jobs = format_entries(df[entry["column"]],entry)
    jobs = jobs + new_jobs

data = {
    "image_string": image_string,
    "jobs": jobs
}

json_object = json.dumps(data, indent=4)

# send http request with image and receive response
response = requests.post(submit_url, data=json_object, headers=headers)

# decode response
print(json.loads(response.text))