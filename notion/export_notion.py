import os
import shutil
import time
import json
import datetime

import requests
from notion.client import NotionClient
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession


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
    response = requests.post(
        'https://notion.so/api/v3/loginWithEmail',
        json=loginData,
        headers=headers
    )
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
        response = client.post('getTasks', {'taskIds': [taskId]})
        tasks = response.json().get('results')
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
        with open('backup/{}'.format(filename), 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def createFolder(session):
    metadata = {
        'name': datetime.datetime.utcnow().isoformat(),
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [os.getenv('GDRIVE_ROOT_FOLDER_ID')]
    }
    response = session.post(
        'https://www.googleapis.com/drive/v3/files?supportsAllDrives=true',
        json=metadata
    )
    response.raise_for_status()
    return response.json()['id']


def upload(name, session, folderId, mimeType):
    file_metadata = {
        'name': name,
        'mimeType': mimeType,
        'parents': [folderId]
    }
    start_response = session.post(
        'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true',
        json=file_metadata
    )
    start_response.raise_for_status()
    resumable_uri = start_response.headers.get('Location')
    file = open('backup/{}'.format(name), 'rb')
    upload_response = session.put(resumable_uri, data=file)
    upload_response.raise_for_status()


def main():
    token = notionToken()
    client = NotionClient(token_v2=token)
    taskId = client.post('enqueueTask', exportTask()).json().get('taskId')
    url = exportUrl(client, taskId)
    downloadFile(url, 'export.zip')

    service_account_info = json.loads(os.getenv('GDRIVE_SERVICE_ACCOUNT'))
    google_credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    authed_session = AuthorizedSession(google_credentials)
    folderId = createFolder(authed_session)
    upload('export.zip', authed_session, folderId, 'application/zip')


if __name__ == "__main__":
    main()
