from celery import Celery, Task, current_app

import base64
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap
import json
import requests
from celery.contrib import rdb

app = Celery('tasks', CELERY_RESULT_BACKEND="rpc://", broker='amqp://')

addr = 'http://127.0.0.1:5000'
result_url = addr + '/result'

# prepare headers for http request
content_type = 'image/jpg'
headers = {'content-type': content_type}


def check_text_size_fit(text_desc, text_size, font_family, rect_width, rect_height):
    """ Check if the text will fit inside the rectangle """
    #Create text font
    text_font = ImageFont.truetype(font_family, size=text_size)

    #Wrap text based on width of the rectangle
    avg_char_width = sum(text_font.getsize(char)[0] for char in text_desc) / len(text_desc)
    max_char_count = int((rect_width) / avg_char_width)

    if max_char_count < 1:
        return 0

    wrapped_text = textwrap.fill(text=text_desc, width=max_char_count)
    text_lines_num = wrapped_text.count('\n')+1

    #Text fits inside rectangle
    if( text_size*text_lines_num <= rect_height):
        return 1

def image_rectangle_text(img, text, coords, position, text_color, text_size, font_family):
    draw = ImageDraw.Draw(img)

    #Grab text and rectangle info
    text_description = text
    rectangle = coords

    #Get rectangle width and height
    rect_width = rectangle[2]-rectangle[0]
    rect_height = rectangle[3]-rectangle[1]

    #Check if text fits rectangle, lower text size if it doesn't
    text_size_fits = False
    while(not(text_size_fits)):
        try:
            result = check_text_size_fit(text_description,text_size,font_family,rect_width,rect_height)
        except Exception as e:
            print(str(e))
            result = 0
        if( result != 1):
            text_size -= 1
        else:
            text_size_fits = True

    #Create text font
    text_font = ImageFont.truetype(font_family, size=text_size)

    #Split text if there are newlines
    text_description = text_description.split('\n')

    line_pos = 0    #Keep track of line position

    #Go through each text segment
    for text_desc in text_description:
        #Wrap text based on width of the rectangle
        print(text_font.getsize(text_desc[0]))
        avg_char_width = text_font.getsize(text_desc)[0] / len(text_desc)
        max_char_count = int((rect_width) / avg_char_width)
        wrapped_text = textwrap.fill(text=text_desc, width=max_char_count)
        text_lines_num = wrapped_text.count('\n')+1

        #Get the width of text box
        text_width = text_font.getsize(wrapped_text.split('\n')[0])[0]

        #Draw Rectangle for Debugging Only
        # draw.rectangle([(rectangle[0],rectangle[1]),(rectangle[2],rectangle[3])],outline="red") # Uncomment to see rectangle

        #Draw the text based on position
        if position == "top-left":
            draw.text((rectangle[0], rectangle[1]+(text_size*line_pos)), wrapped_text, fill =text_color, font=text_font)
        if position == "top-center":
            draw.text((rectangle[0]+int(rect_width/2)-int(text_width/2), rectangle[1]+(text_size*line_pos)), wrapped_text, fill =text_color, font=text_font)
        if position == "top-right":
            draw.text((rectangle[2]-text_width, rectangle[1]+(text_size*line_pos)), wrapped_text, fill =text_color, font=text_font)

        if position == "center-left":
            draw.text((rectangle[0], rectangle[1]+int(rect_height/2)-int(text_size*text_lines_num/2)+(text_size*line_pos)), wrapped_text, fill =text_color, font=text_font)
        if position == "center":
            draw.text((rectangle[0]+int(rect_width/2)-int(text_width/2), rectangle[1]+int(rect_height/2)-int(text_size*text_lines_num/2)+(text_size*line_pos)), wrapped_text, fill=text_color, font=text_font)
        if position == "center-right":
            draw.text((rectangle[2]-text_width, rectangle[1]+int(rect_height/2)-int(text_size*text_lines_num/2)+(text_size*line_pos)), wrapped_text, fill =text_color, font=text_font)

        if position == "below-left":
            draw.text(((rectangle[0], rectangle[3]-(text_size*text_lines_num)+(text_size*line_pos))), wrapped_text, fill =text_color, font=text_font)
        if position == "below-center":
            draw.text((rectangle[0]+int(rect_width/2)-int(text_width/2), rectangle[3]-(text_size*text_lines_num)+(text_size*line_pos)), wrapped_text, fill =text_color, font=text_font)
        if position == "below-right":
            draw.text((rectangle[2]-text_width, rectangle[3]-(text_size*text_lines_num)+(text_size*line_pos)), wrapped_text, fill =text_color, font=text_font)

        line_pos+=text_lines_num
    
    return img

@app.task
def process_image_text(image_string, text, coords, position, color, text_size, font):
    processed_image_str = ""
    try:
        image = io.BytesIO(base64.b64decode(image_string.encode('utf-8')))
        img = Image.open(image)

        img = image_rectangle_text(img, text, coords, position, tuple(color), text_size, font)

        byte_io = io.BytesIO()
        img.save(byte_io,'PNG')
        processed_image_str = base64.b64encode(byte_io.getvalue()).decode('utf-8')

    except Exception as e:
        print(str(e))

    # send http request with image and receive response
    requests.post(result_url, data=processed_image_str, headers=headers)
    return 1