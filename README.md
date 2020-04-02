# Notion Backup

This repo makes a backup of OpenOwnership's Notion workspace.

The code runs via a Github Action, which is scheduled to run at 4:05am every
day, as well as whenever code is pushed to the repository.

## Running the code locally

The code to run the backup lives in /notion/export_notion.py. To run it:

1. Install requirements

   ```shell
   git clone git@github.com:openownership/notion-backup.git
   cd notion-backup
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   touch .env
   ```

2. Set your credentials in the `.env` file:

   ```shell
   NOTION_SPACE_ID=1234-56789-abcdef
   NOTION_EMAIL=notion@example.com
   NOTION_PASSWORD=password
   GDRIVE_ROOT_FOLDER_ID=<get-the-folder-id-from-gdrive>
   GDRIVE_SERVICE_ACCOUNT=<get-the-service-account-info-from-1password>
   ```

3. Run the python module: `python notion`

You can find the space id by logging into Notion as the tech+notion user and then
inspecting one of the ajax requests that notion's front end makes in the
chrome dev console. It's often found in the body of responses from Notion.

Note that this assumes you have a email/password user account, not one through
Google SSO.

## Github Action config

The Github Action is configured via secrets set up in [the repo settings](https://github.com/openownership/notion-backup/settings/secrets).
These are then set as env vars for the python script to use.
