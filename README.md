# Notion Backup

This repo stores a backup of OpenOwnership's Notion workspace:
https://www.notion.so/openownership/OpenOwnership-Home-e6298eada76f4535bc2ea177ba79413e
and the code which makes that backup and regularly updates it.

The backup itself is in [/backup](https://github.com/openownership/notion-backup/tree/master/backup)
this is a copy of Notion's 'workspace export' in the 'markdown + csv' format.

The code runs via a Github Action, which is scheduled to run at 4:05am every
day, as well as whenever code is pushed to the repository.

## Running the code locally

The code to run the backup lives in [/notion/export_notion.py]. To run it:

```
pip install -r requirements.txt
export NOTION_LOCALE=en
export NOTION_TIMEZONE=Europe/London
export NOTION_SPACE_ID=<our-notion-space-id>
export NOTION_TOKEN=<tech+notion@openownership.org's token_v2>
python notion
```

You can find the space id and token by logging into Notion (as the tech+notion
user ideally, if you use your personal account it will also export files in your
personal workspace) and then inspecting one of the ajax requests that notion's
front end makes. `token_v2` is a cookie, `spaceId` is often found in the body
of responses from Notion.

## Github Action config

The Github Action is configured via some secrets set up in the repo:
https://github.com/openownership/notion-backup/settings/secrets. These are then
set as env vars for the python script to use.
