#!/usr/bin/env python3

import requests, os, json, glob, csv, psycopg2, sys, smtplib, ssl, imaplib, time, email, re, fuzzywuzzy, itertools, geopy, datetime, logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from jinja2 import Environment
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# Printing the output to file for debugging
sys.stdout = open('Process.log', 'w')

# API Request strategy
print("Setting API Request strategy")
retry_strategy = Retry(
total=3,
status_forcelist=[429, 500, 502, 503, 504],
allowed_methods=["HEAD", "GET", "OPTIONS"],
backoff_factor=10
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Set current directory
print("Setting current directory")
os.chdir(os.getcwd())

from dotenv import load_dotenv

load_dotenv()

# Retrieve contents from .env file
DB_IP = os.getenv("DB_IP")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
RE_API_KEY = os.getenv("RE_API_KEY")
MAIL_USERN = os.getenv("MAIL_USERN")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
IMAP_URL = os.getenv("IMAP_URL")
IMAP_PORT = os.getenv("IMAP_PORT")
SMTP_URL = os.getenv("SMTP_URL")
SMTP_PORT = os.getenv("SMTP_PORT")
ERROR_EMAILS_TO  = os.getenv("ERROR_EMAILS_TO")
WORKFLOW_1_LIST_ID = os.getenv("WORKFLOW_1_LIST_ID")
WORKFLOW_2_LIST_ID = os.getenv("WORKFLOW_2_LIST_ID")
WORKFLOW_3_LIST_ID = os.getenv("WORKFLOW_3_LIST_ID")
CORPORATE_FUNDRAISING_TEAM_IDS = os.getenv("CORPORATE_FUNDRAISING_TEAM_IDS")
WORKFLOW_4_LIST_ID = os.getenv("WORKFLOW_4_LIST_ID")

def connect_db():
    global conn, cur
    
    # PostgreSQL DB Connection
    conn = psycopg2.connect(host=DB_IP, dbname=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD)

    # Open connection
    print("Creating connection with SQL database")
    cur = conn.cursor()
    
def disconnect_db():
    
    print("Closing connection with SQL database")
     
    # Close DB connection
    if conn:
        cur.close()
        conn.close()
        
    # Close writing to Process.log
    sys.stdout.close()
        
    exit()

def get_access_token():
    global access_token
    
    # Retrieve access_token from file
    print("Retrieve token from API connections")
    with open('access_token_output.json') as access_token_output:
        data = json.load(access_token_output)
        access_token = data["access_token"]
  
def get_request_re():
    print("Running GET Request from RE function")
    time.sleep(5)
    # Request Headers for Blackbaud API request
    headers = {
        # Request headers
        'Bb-Api-Subscription-Key': RE_API_KEY,
        'Authorization': 'Bearer ' + access_token
    }
    
    global re_api_response
    re_api_response = http.get(url, params=params, headers=headers).json()
    
    check_for_errors()
    print_json(re_api_response)

def post_request_re():
    print("Running POST Request to RE function")
    time.sleep(5)
    headers = {
        # Request headers
        'Bb-Api-Subscription-Key': RE_API_KEY,
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    
    global re_api_response
    re_api_response = http.post(url, params=params, headers=headers, json=params).json()
    
    print_json(re_api_response)
    
    check_for_errors()
    
def check_for_errors():
    print("Checking for errors")
    error_keywords = ["invalid", "error", "bad", "Unauthorized", "Forbidden", "Not Found", "Unsupported Media Type", "Too Many Requests", "Internal Server Error", "Service Unavailable", "Unexpected", "error_code", "400"]
    
    if any(x in re_api_response for x in error_keywords):
        # Send emails
        print ("Will send email now")
        send_error_emails()
        
def send_error_emails():
    print("Sending email for an error")
    
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = MAIL_USERN
    message["To"] = ERROR_EMAILS_TO

    # Adding Reply-to header
    message.add_header('reply-to', MAIL_USERN)
        
    TEMPLATE="""
    <table style="background-color: #ffffff; border-color: #ffffff; width: auto; margin-left: auto; margin-right: auto;">
    <tbody>
    <tr style="height: 127px;">
    <td style="background-color: #363636; width: 100%; text-align: center; vertical-align: middle; height: 127px;">&nbsp;
    <h1><span style="color: #ffffff;">&nbsp;Raiser's Edge Automation: {{job_name}} Failed</span>&nbsp;</h1>
    </td>
    </tr>
    <tr style="height: 18px;">
    <td style="height: 18px; background-color: #ffffff; border-color: #ffffff;">&nbsp;</td>
    </tr>
    <tr style="height: 18px;">
    <td style="width: 100%; height: 18px; background-color: #ffffff; border-color: #ffffff; text-align: center; vertical-align: middle;">&nbsp;<span style="color: #455362;">This is to notify you that execution of Auto-updating Alumni records has failed.</span>&nbsp;</td>
    </tr>
    <tr style="height: 18px;">
    <td style="height: 18px; background-color: #ffffff; border-color: #ffffff;">&nbsp;</td>
    </tr>
    <tr style="height: 61px;">
    <td style="width: 100%; background-color: #2f2f2f; height: 61px; text-align: center; vertical-align: middle;">
    <h2><span style="color: #ffffff;">Job details:</span></h2>
    </td>
    </tr>
    <tr style="height: 52px;">
    <td style="height: 52px;">
    <table style="background-color: #2f2f2f; width: 100%; margin-left: auto; margin-right: auto; height: 42px;">
    <tbody>
    <tr>
    <td style="width: 50%; text-align: center; vertical-align: middle;">&nbsp;<span style="color: #ffffff;">Job :</span>&nbsp;</td>
    <td style="background-color: #ff8e2d; width: 50%; text-align: center; vertical-align: middle;">&nbsp;{{job_name}}&nbsp;</td>
    </tr>
    <tr>
    <td style="width: 50%; text-align: center; vertical-align: middle;">&nbsp;<span style="color: #ffffff;">Failed on :</span>&nbsp;</td>
    <td style="background-color: #ff8e2d; width: 50%; text-align: center; vertical-align: middle;">&nbsp;{{current_time}}&nbsp;</td>
    </tr>
    </tbody>
    </table>
    </td>
    </tr>
    <tr style="height: 18px;">
    <td style="height: 18px; background-color: #ffffff;">&nbsp;</td>
    </tr>
    <tr style="height: 18px;">
    <td style="height: 18px; width: 100%; background-color: #ffffff; text-align: center; vertical-align: middle;">Below is the detailed error log,</td>
    </tr>
    <tr style="height: 217.34375px;">
    <td style="height: 217.34375px; background-color: #f8f9f9; width: 100%; text-align: left; vertical-align: middle;">{{error_log_message}}</td>
    </tr>
    </tbody>
    </table>
    """
    
    # Create a text/html message from a rendered template
    emailbody = MIMEText(
        Environment().from_string(TEMPLATE).render(
            job_name = "Running Workflows for Raisers Edge",
            current_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            error_log_message = Argument
        ), "html"
    )
    
    # Add HTML parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(emailbody)
    attach_file_to_email(message, 'Process.log')
    emailcontent = message.as_string()
    
    # Create secure connection with server and send email
    context = ssl._create_unverified_context()
    with smtplib.SMTP_SSL(SMTP_URL, SMTP_PORT, context=context) as server:
        server.login(MAIL_USERN, MAIL_PASSWORD)
        server.sendmail(
            MAIL_USERN, ERROR_EMAILS_TO, emailcontent
        )

    # Save copy of the sent email to sent items folder
    with imaplib.IMAP4_SSL(IMAP_URL, IMAP_PORT) as imap:
        imap.login(MAIL_USERN, MAIL_PASSWORD)
        imap.append('Sent', '\\Seen', imaplib.Time2Internaldate(time.time()), emailcontent.encode('utf8'))
        imap.logout()
        
    # Close DB connection
    disconnect_db()
    
def attach_file_to_email(message, filename):
    # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
    with open(filename, "rb") as f:
        file_attachment = MIMEApplication(f.read())
    # Add header/name to the attachments    
    file_attachment.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    # Attach the file to the message
    message.attach(file_attachment)
    
def print_json(d):
    print(json.dumps(d, indent=4))
    
def housekeeping():
    # Read multiple files
    multiple_files = glob.glob("List_from_RE_*.json")
    
    # Housekeeping
    print("Remove List_from_RE_*.json files")
    for each_file in multiple_files:
        try:
            os.remove(each_file)
        except:
            pass

def get_list_from_re():
    global url
    housekeeping()
    
    # Blackbaud API URL
    url = f"{url_prefix}?list_id={list_id}&limit=5000"
    print(url)
    
    # Pagination request to retreive list
    while url:
        # Blackbaud API GET request
        get_request_re()

        # Incremental File name
        i = 1
        while os.path.exists("List_from_RE_%s.json" % i):
            i += 1
        with open("List_from_RE_%s.json" % i, "w") as list_output:
            json.dump(re_api_response, list_output,ensure_ascii=False, sort_keys=True, indent=4)
        
        # Check if a variable is present in file
        with open("List_from_RE_%s.json" % i) as list_output_last:
            if 'next_link' in list_output_last.read():
                url = re_api_response["next_link"]
            else:
                break

def add_constituent_code():
    global url, params, constituent_code, fundraising_team_id
    print(f"Adding constituent codes - {constituent_code} to record")
    
    url = "https://api.sky.blackbaud.com/constituent/v1/constituentcodes"
    
    params = {
        "constituent_id": constituent_id,
        "description": constituent_code
    }
    
    post_request_re()
    
def assign_fundraisers():
    print(f"Assigning constituents to {fundraising_team}")
    
    global url, params
    
    url = "https://api.sky.blackbaud.com/fundraising/v1/fundraisers/assignments"
    
    params = {
        "constituent_id": constituent_id,
        "fundraiser_id": fundraising_team_id
    }
    
    post_request_re()

def workflow_1():
    global constituent_id
    
    get_access_token()

    get_list_from_re()
    
    print("Parsing content from List_from_RE_*.json files")
    multiple_files = glob.glob("List_from_RE_*.json")
    
    for each_file in multiple_files:

        # Open JSON file
        with open(each_file, 'r') as json_file:
            json_content = json.load(json_file)
            
            for results in json_content['value']:
                constituent_id = results['id']
                
                add_constituent_code()

def workflow_2():
    global constituent_id, fundraising_team
    
    get_access_token()
    
    print(f"Getting list of constituents not assigned to {fundraising_team}")
    
    get_list_from_re()
    
    print("Parsing content from List_from_RE_*.json files")
    multiple_files = glob.glob("List_from_RE_*.json")
    
    for each_file in multiple_files:

        # Open JSON file
        with open(each_file, 'r') as json_file:
            json_content = json.load(json_file)
            
            for results in json_content['value']:
                constituent_id = results['id']
                
                assign_fundraisers()
                
def workflow_3():
    global constituent_id, fundraising_team
    
    get_access_token()
    
    print(f"Getting list of constituents not assigned to {fundraising_team}")
    
    get_list_from_re()
    
    print("Parsing content from List_from_RE_*.json files")
    multiple_files = glob.glob("List_from_RE_*.json")
    
    for each_file in multiple_files:

        # Open JSON file
        with open(each_file, 'r') as json_file:
            json_content = json.load(json_file)
            
            for results in json_content['value']:
                constituent_id = results['id']
                
                assign_fundraisers()

def workflow_4():
    global url, constituent_id, params
    
    get_access_token()
    
    get_list_from_re()
    
    # Parse from JSON and write to CSV file
    # Header of CSV file
    header = ['gift_id', 'amount', 'constituent_id', 'date', 'date_added', 'date_modified', 'lookup_id']
    
    with open('Corporate_Gifts.csv', 'w', encoding='UTF8') as csv_file:
        writer = csv.writer(csv_file, delimiter = ";")

        # Write the header
        writer.writerow(header)
    
    print("Parsing content from List_from_RE_*.json files")
    multiple_files = glob.glob("List_from_RE_*.json")
    
    for each_file in multiple_files:

        # Open JSON file
        with open(each_file, 'r') as json_file:
            json_content = json.load(json_file)
            
            for results in json_content['value']:
                data = (results['id'], results['amount']['value'], results['constituent_id'], results['date'], results['date_added'], results['date_modified'], results['lookup_id'])
                
                with open('Corporate_Gifts.csv', 'a', encoding='UTF8') as csv_file:
                    writer = csv.writer(csv_file, delimiter = ";")
                    writer.writerow(data)
                    
    # Delete rows in table
    cur.execute("truncate corporate_gifts;")
    
    # Copying contents of CSV file to PostgreSQL DB
    with open('Corporate_Gifts.csv', 'r') as input_csv:
        # Skip the header row.
        next(input_csv)
        cur.copy_from(input_csv, 'corporate_gifts', sep=';')
    
    # Commit changes
    conn.commit()
    
    extract_sql =  """
    SELECT * FROM corporate_gifts WHERE NOT EXISTS (SELECT 1 FROM actions_tagged_for_corporate_gifts WHERE actions_tagged_for_corporate_gifts.gift_id = corporate_gifts.gift_id) FETCH FIRST 1 ROW ONLY;
    """
    
    cur.execute(extract_sql)
    result = cur.fetchall()
    
    print(result)
    
    while result:
        # Ensure no comma or brackets in output
        result_list = list(result[0])
        gift_id = result_list[0]
        amount = result_list[1]
        constituent_id = result_list[2]
        date_str = result_list[3]
        date_added = result_list[4]
        date_modified = result_list[5]
        lookup_id = result_list[6]
        
        print(gift_id)
        print(amount)
        print(constituent_id)
        print(date_str)
        print(date_added)
        print(date_modified)
        print(lookup_id)
        
        date = datetime.strptime(date_str, '%Y-%m-%dT00:00:00')
        print(date)
        day = int(date.strftime("%d"))
        month = int(date.strftime("%m"))
        year = int(date.strftime("%Y"))
        next_year = int(date.strftime("%Y")) + 1
        print(day)
        print(month)
        print(year)
        print(next_year)
        
        print(list(CORPORATE_FUNDRAISING_TEAM_IDS.split(',')))
        
        # Create Action for Acknowledgement
        params = {
            'category': 'Task/Other',
            'constituent_id': constituent_id,
            'date': str(year) + '-' + str(month) + '-' + str(day) + 'T00:00:00',
            'description': 'This task is for donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'fundraisers': list(CORPORATE_FUNDRAISING_TEAM_IDS.split(',')),
            'summary': 'Acknowledgement of Gift for donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'type': 'Action Items'
        }
        
        print_json(params)
        
        add_action()

        # Create Action for Form 10B
        params = {
            'category': 'Task/Other',
            'constituent_id': constituent_id,
            'date': str(next_year) + '-' + '05' + '-' + '15' + 'T00:00:00',
            'description': 'This task is for donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'fundraisers': list(CORPORATE_FUNDRAISING_TEAM_IDS.split(',')),
            'summary': 'Send Form 10B to Donor for donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'type': 'Action Items'
        }
        
        print_json(params)
        
        add_action()
        
        # Create Action for FUR
        params = {
            'category': 'Task/Other',
            'constituent_id': constituent_id,
            'date': str(next_year) + '-' + '06' + '-' + '15' + 'T00:00:00',
            'description': 'This task is for donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'fundraisers': list(CORPORATE_FUNDRAISING_TEAM_IDS.split(',')),
            'summary': 'Send Fund Utilization Report (FUR) to Donor for donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'type': 'Action Items'
        }
        
        print_json(params)
        
        add_action()
        
        # Create Action for Updating the Donors
        # For Jan 10
        params = {
            'category': 'Task/Other',
            'constituent_id': constituent_id,
            'date': str(next_year) + '-' + '01' + '-' + '10' + 'T00:00:00',
            'description': 'This task is for donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'fundraisers': list(CORPORATE_FUNDRAISING_TEAM_IDS.split(',')),
            'summary': 'Send Update to Donor for their donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'type': 'Action Items'
        }
        
        print_json(params)
        
        add_action()
        
        # For July 15
        params = {
            'category': 'Task/Other',
            'constituent_id': constituent_id,
            'date': str(next_year) + '-' + '07' + '-' + '15' + 'T00:00:00',
            'description': 'This task is for donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'fundraisers': list(CORPORATE_FUNDRAISING_TEAM_IDS.split(',')),
            'summary': 'Send a second Update to Donor for their donation received on ' + str(day) + " " + datetime.strptime(str(month), "%m").strftime("%b") + ", " + str(year),
            'type': 'Action Items'
        }
        
        print_json(params)
        
        add_action()
        
        # Will update in PostgreSQL
        insert_updates = """
                        INSERT INTO actions_tagged_for_corporate_gifts (gift_id, amount, constituent_id, date, date_added, date_modified, lookup_id, acknowledgement_added, form_10b_added, fur_added, update_added)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'TRUE', 'TRUE', 'TRUE', 'TRUE')
                        """
        cur.execute(insert_updates, [gift_id, amount, constituent_id, date_str, date_added, date_modified, lookup_id])
        conn.commit()
        print(f"Successfully added actions for Gift ID: {gift_id}")
        
        extract_sql =  """
        SELECT * FROM corporate_gifts WHERE NOT EXISTS (SELECT 1 FROM actions_tagged_for_corporate_gifts WHERE actions_tagged_for_corporate_gifts.gift_id = corporate_gifts.gift_id) FETCH FIRST 1 ROW ONLY;
        """
        
        cur.execute(extract_sql)
        result = cur.fetchall()

        print(result)
        
        if result == []:
            break

def add_action():
    global url
    url = "https://api.sky.blackbaud.com/constituent/v1/actions"
    
    post_request_re()

try:
    connect_db()
    
    # WorkFlow #1
    print(f"Running WorkFlow #1 -> To tag constituents as Major Donor -> Getting list of constituents in RE from list - https://host.nxt.blackbaud.com/lists/shared-list/{WORKFLOW_1_LIST_ID}?envid=p-dzY8gGigKUidokeljxaQiA")
    
    list_id = WORKFLOW_1_LIST_ID
    url_prefix = "https://api.sky.blackbaud.com/constituent/v1/constituents"
    params = ""
    constituent_code = "Major Donor"
    
    workflow_1()
    
    # Workflow #2
    print(f"Running Workflow #2 -> To assign constituents to Major Donor Team -> Getting list of constituents in RE from list - https://host.nxt.blackbaud.com/lists/shared-list/{WORKFLOW_2_LIST_ID}?envid=p-dzY8gGigKUidokeljxaQiA")
    list_id = WORKFLOW_2_LIST_ID
    params = ""
    fundraising_team = "Major Donor Team"
    fundraising_team_id = "397314"
    url_prefix = "https://api.sky.blackbaud.com/constituent/v1/constituents"
    
    workflow_2()
    
    # Workflow #3
    print(f"Running Workflow #3 -> To assign constituents to Corporate Team -> Getting list of constituents in RE from list - https://host.nxt.blackbaud.com/lists/shared-list/{WORKFLOW_3_LIST_ID}?envid=p-dzY8gGigKUidokeljxaQiA")
    list_id = WORKFLOW_3_LIST_ID
    params = ""
    fundraising_team = "Corporate Team"
    fundraising_team_id = "397340"
    
    # Blackbaud API URL
    url_prefix = "https://api.sky.blackbaud.com/constituent/v1/constituents"
    
    workflow_3()   
    
    # Workflow #4
    print(f"Running Workflow #3 -> To assign custom actions to Corporate Team -> Getting list of gifts in RE from list - https://host.nxt.blackbaud.com/lists/shared-list/{WORKFLOW_4_LIST_ID}?envid=p-dzY8gGigKUidokeljxaQiA")
    list_id = WORKFLOW_4_LIST_ID
    params = ""
    # Blackbaud API URL
    url_prefix = "https://api.sky.blackbaud.com/gift/v1/gifts"
    workflow_4()
    
    # Close DB connection and exit
    housekeeping()
    
    disconnect_db()

except Exception as Argument:
    print("Error while running workflows for Raisers Edge")
    subject = "Error while running workflows for Raisers Edge"
    
    housekeeping()
    
    send_error_emails()