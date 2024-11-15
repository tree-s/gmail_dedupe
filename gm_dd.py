import os
import time
import pickle
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/spreadsheets']

# Load credentials from 'token.json', refresh or authenticate if needed
def authenticate_services():
    creds = None
    # Check if token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # Attempt to refresh the token
            except Exception as e:
                print(f"Error refreshing token: {e}. Re-authenticating.")
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the new credentials for future runs
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    
    return creds

# Load configuration from config.json
def load_config():
    config_file = 'config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
            return config
    else:
        print("Configuration file not found.")
        return None

# Initialize the Gmail API and Sheets API
def initialize_apis():
    creds = authenticate_services()

    try:
        gmail_service = build('gmail', 'v1', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        return gmail_service, sheets_service
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None, None

# Move email to the "Duplicates" label (only if testing=False)
def move_to_label(gmail_service, message_id, label_id, testing):
    if testing:
        print(f"Testing mode: Skipping movement of message ID {message_id}.")
    else:
        try:
            gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id], 'removeLabelIds': ['INBOX']}
            ).execute()
            print(f"Moved message ID {message_id} to label.")
        except HttpError as error:
            print(f"Error moving message: {error}")

# Find or create the label "Duplicates"
def get_or_create_label(gmail_service, label_name="Duplicates"):
    try:
        results = gmail_service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        label_id = None

        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break
        
        if not label_id:
            label = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            new_label = gmail_service.users().labels().create(userId='me', body=label).execute()
            label_id = new_label['id']

        return label_id

    except HttpError as error:
        print(f"Error finding or creating label: {error}")
        return None

# Log duplicate emails to a Google Sheet
def log_to_sheet(sheets_service, spreadsheet_id, data):
    try:
        body = {
            'values': data
        }
        sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A1', 
            valueInputOption='RAW',
            body=body
        ).execute()
        print("Logged duplicate emails to the spreadsheet.")
    except HttpError as error:
        print(f"Error logging to sheet: {error}")

# Main function to find and move duplicate emails
def process_emails(testing=False):
    gmail_service, sheets_service = initialize_apis()
    
    if not gmail_service or not sheets_service:
        print("Error initializing APIs.")
        return

    # Load configuration and get spreadsheet ID
    config = load_config()
    if not config or 'spreadsheet_id' not in config:
        print("Spreadsheet ID not found in configuration.")
        return

    search_query = 'in:all'  # Modify the search query if necessary
    label_id = get_or_create_label(gmail_service)
    spreadsheet_id = config['spreadsheet_id']

    if not label_id and not testing:
        print("Error creating or finding the label.")
        return

    email_hash = {}
    page_token = None
    delay = 0.01

    while True:
        try:
            results = gmail_service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=500,
                pageToken=page_token
            ).execute()
            
            messages = results.get('messages', [])
            page_token = results.get('nextPageToken')

            if not messages:
                break

            for msg in messages:
                message = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = message['payload'].get('headers', [])
                
                # Safely get the sender or provide a default value if not found
                sender = next((header['value'] for header in headers if header['name'] == 'From'), '(Unknown Sender)')
                
                # Safely get the subject or provide a default value if not found
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), '(No Subject)')
                
                date = message.get('internalDate', 'Unknown Date')

                unique_key = f"{subject}-{sender}-{date}"

                if unique_key in email_hash:
                    if not testing:
                        move_to_label(gmail_service, message['id'], label_id, testing)
                    
                    # Log the duplicate email to Google Sheets
                    log_to_sheet(sheets_service, spreadsheet_id, [[subject, sender, date, message['id']]])

                    time.sleep(delay)  # Delay to avoid rate limits
                else:
                    email_hash[unique_key] = True

            if not page_token:
                break

        except HttpError as error:
            print(f"An error occurred: {error}")

if __name__ == '__main__':
    testing_mode = False  # Set to False for production, True for testing without moving emails
    process_emails(testing=testing_mode)
