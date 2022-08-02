# Workflow-for-Raisers-Edge

### Pre-requisites
- Install below packages

```bash

sudo apt install python3-pip
sudo apt install git
pip3 install python-dotenv
pip3 install psycopg2

```

- If you encounter error on installing **pyscopg2**, then try:
```bash

pip3 install psycopg2-binary

```

- Install **PostgreSQL** using the steps mentioned [here](https://www.postgresql.org/download/linux/ubuntu/).
```bash

sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt -y install postgresql

```

- Create required **Databases**
```sql

CREATE DATABASE "re-workflows"

CREATE TABLE corporate_gifts
(
    gift_id character varying,
    amount character varying,
    constituent_id character varying,
    date character varying,
    date_added character varying,
    date_modified character varying,
    lookup_id character varying
);

CREATE TABLE actions_tagged_for_corporate_gifts
(
    gift_id character varying,
    amount character varying,
    constituent_id character varying,
    date character varying,
    date_added character varying,
    date_modified character varying,
    lookup_id character varying,
    acknowledgement_added character varying,
    form_10b_added character varying,
    fur_added character varying,
    update_added character varying
);

- Create a **.env** file with below parameters. ***`Replace # ... with appropriate values`***

```bash

DB_IP= # IP of SQL Database
DB_NAME= # Name of SQL Database
DB_USERNAME= # Login for SQL Database
DB_PASSWORD= # Password for SQL Database
AUTH_CODE= # Raiser's Edge NXT Auth Code (encode Client 
REDIRECT_URL= # Redirect URL of application in Raiser's Edge NXT
CLIENT_ID= # Client ID of application in Raiser's Edge NXT
RE_API_KEY= # Raiser's Edge NXT Developer API Key
MAIL_USERN= # Email Username
MAIL_PASSWORD= # Email password
IMAP_URL= # IMAP web address
IMAP_PORT= # IMAP Port
SMTP_URL= # SMTP web address
SMTP_PORT= # SMTP Port
SEND_TO='email_1, email_2' # Email ID of users who needs to receive the report
CC_TO='email_3, email_4' # Email ID of users who will be CC'd for the report
ERROR_EMAILS_TO= # Email ID of user who needs to receive error emails (if any)
WORKFLOW_1_LIST_ID= # RE List ID
WORKFLOW_2_LIST_ID= # RE List ID
WORKFLOW_3_LIST_ID= # RE List ID
CORPORATE_FUNDRAISING_TEAM_IDS='' # Fundraising Team's System ID
WORKFLOW_4_LIST_ID= # RE List ID

```
# Usage
```bash

python3 Request Access Token.py

```
- Copy and paste the link in a browser to get the **TOKEN**
- Copy the **TOKEN** in the terminal and press ENTER
- Set a CRON job to refresh token and start the program
```bash

crontab -e

```
- Set below CRON jobs
```bash

*/42 * * * * cd Raisers-Edge-to-AlmaBase-Sync/ && python3 Refresh\ Access\ Token.py > /dev/null 2>&1

```
- Monitor emails for any errors and take appropriate action.