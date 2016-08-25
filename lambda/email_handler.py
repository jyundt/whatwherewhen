#! /usr/bin/env python
from __future__ import print_function
import boto3
import os
import sys
import email
import errno
import mimetypes
import hashlib
import magic
import datetime
import piexif

from PIL import Image
import PIL.Image
from PIL.ExifTags import TAGS, GPSTAGS


s3_client = boto3.client('s3')

get_float = lambda x: float(x[0]) / float(x[1])
def convert_to_degrees(value):
    d = get_float(value[0])
    m = get_float(value[1])
    s = get_float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def convert_to_time(value):
    h = int(value[0][0])
    m = int(value[1][0])
    s = int(value[2][0])
    return "%s:%s:%s" %(h, m, s)
     

def generate_thumbnail(original):
    with Image.open(original) as image:
        image.thumbnail(tuple(x / 2 for x in image.size))
        image.save(original)


def extract_images(mailfile):
    fh = open(mailfile, 'rb')
    mail = email.message_from_file(fh)
    fh.close()
    images = []
    for part in mail.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        mime = magic.Magic(mime=True)
        raw_part = part.get_payload(decode=True)
        if mime.from_buffer(raw_part) == 'image/jpeg':
            fh = open('/tmp/raw.jpg', 'w+b')
            fh.write(raw_part)
            i = Image.open(fh)
            exif_info = i._getexif()
            i.close()
            fh.close()
            if 34853 in exif_info:
                gps_lat = exif_info[34853][2]
                gps_lat_ref = exif_info[34853][1]
                gps_lon = exif_info[34853][4]
                gps_lon_ref = exif_info[34853][3]
                lat = convert_to_degrees(gps_lat)
                if gps_lat_ref != "N":
                    lat *= -1
                lon = convert_to_degrees(gps_lon)
                if gps_lon_ref != "E":
                    lon *= -1
                
                gps_date = exif_info[34853][29]
                gps_time = convert_to_time(exif_info[34853][7])
                timestamp = datetime.datetime.strptime(gps_date + ' ' + gps_time, "%Y:%m:%d %H:%M:%S")
                piexif.remove('/tmp/raw.jpg')
                fh = open('/tmp/raw.jpg', 'rb')
                filehashname = '/tmp/' + hashlib.sha256(fh.read()).hexdigest() + '.jpg'
                fh.close()
                os.rename('/tmp/raw.jpg',filehashname)
                images.append((filehashname, timestamp, lat, lon))
            
    return(images)
def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        mailfile = '/tmp/' + os.path.basename(key)

        s3_client.download_file(bucket,key,mailfile)
        images = extract_images(mailfile)
        for image in images:
            s3_client.upload_file(image[0],bucket,'images/'+os.path.basename(image[0]), ExtraArgs={'ContentType': 'image/jpeg'})
            generate_thumbnail(image)
            s3_client.upload_file(image[0],bucket,'thumbnails/'+os.path.basename(image[0]), ExtraArgs={'ContentType': 'image/jpeg'})

