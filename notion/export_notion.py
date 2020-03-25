import os
import shutil
from zipfile import ZipFile
import time
from pathlib import Path

import requests
from notion.client import NotionClient
from dotenv import load_dotenv


load_dotenv()


def notionToken():
    loginData = {
        'email': os.getenv('NOTION_EMAIL'),
        'password': os.getenv('NOTION_PASSWORD')
    }
    headers = {
        # Notion obviously check this as some kind of (bad) test of CSRF
        'host': 'www.notion.so'
    }
    response = requests.post('https://notion.so/api/v3/loginWithEmail', json=loginData, headers=headers)
    response.raise_for_status()
    return response.cookies['token_v2']


def exportTask():
    return {
        'task': {
            'eventName': "exportSpace",
            'request': {
                'spaceId': os.getenv('NOTION_SPACE_ID'),
                'exportOptions': {
                    'exportType': 'markdown',
                    'timeZone': os.getenv('NOTION_TIMEZONE'),
                    'locale': os.getenv('NOTION_LOCALE')
                }
            }
        }
    }



def exportUrl(client, taskId):
    url = False
    print('Polling for export task: {}'.format(taskId))
    while True:
        tasks = client.post('getTasks', {'taskIds': [taskId]}).json().get('results')
        task = next(t for t in tasks if t['id'] == taskId)
        if task['state'] == 'success':
            url = task['status']['exportURL']
            print()
            print(url)
            break
        else:
            print('.', end="", flush=True)
            time.sleep(10)
    return url



def downloadFile(url, filename):
    with requests.get(url, stream=True) as r:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def extractFile(filename, folder):
    ZipFile(filename).extractall(folder)
    os.remove(filename)


def main():
    token = notionToken()
    client = NotionClient(token_v2=token)
    taskId = client.post('enqueueTask', exportTask()).json().get('taskId')
    url = exportUrl(client, taskId)
    downloadFile(url, 'export.zip')
    extractFile('export.zip', 'backup')


if __name__ == "__main__":
    main()
