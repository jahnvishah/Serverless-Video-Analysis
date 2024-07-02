#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

# from boto3 import client as boto3_client


# def handler(event, context):	
# 	print("Hello")

import os
import subprocess
import boto3
import ffmpeg
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')

def handler(event, context):
    input_bucket = '1230683898-input'
    output_bucket = '1230683898-stage-1'

    for record in event['Records']:
        if record['s3']['bucket']['name'] == input_bucket:
            object_key = unquote_plus(record['s3']['object']['key'])
            
            download_path = f'/tmp/{object_key}'
            output_folder = object_key.split('.')[0]  
            output_path = f'/tmp/{output_folder}'
            
            if not os.path.exists(output_path):
                os.makedirs(output_path)
    
            s3_client.download_file(input_bucket, object_key, download_path)
            
            ffmpeg_cmd = f"/usr/bin/ffmpeg -ss 0 -r 1 -i {download_path} -vf fps=1/10 -start_number 0 -vframes 10 {output_path}/output_%02d.jpg -y"
            
            try:
                subprocess.check_call(ffmpeg_cmd, shell=True)
                uploadFrames(output_path, output_bucket, output_folder)
            except subprocess.CalledProcessError as e:
                print(f"Error executing FFmpeg: {e}")
                return

def uploadFrames(folder_path, bucket_name, output_folder):
    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg'):
            s3_client.upload_file(
                Filename=os.path.join(folder_path, filename),
                Bucket=bucket_name,
                Key=f'{output_folder}/{filename}'
            )
