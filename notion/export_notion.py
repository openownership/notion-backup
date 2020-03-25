import os
import shutil
from zipfile import ZipFile
import time

import requests
from notion.client import NotionClient


def exportTask():
    return {
        'task': {
            'eventName': "exportSpace",
            'request': {
                'spaceId': os.environ['NOTION_SPACE_ID'],
                'exportOptions': {
                    'exportType': 'markdown',
                    'timeZone': os.environ['NOTION_TIMEZONE'],
                    'locale': os.environ['NOTION_LOCALE']
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
    client = NotionClient(token_v2=os.environ['NOTION_TOKEN'])
    taskId = client.post('enqueueTask', exportTask()).json().get('taskId')
    url = exportUrl(client, taskId)
    downloadFile(url, 'export.zip')
    extractFile('export.zip', 'backup')


if __name__ == "__main__":
    main()
