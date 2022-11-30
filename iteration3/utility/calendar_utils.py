# ================================================= Libraries =========================================================


import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ================================================= Calendar Views ====================================================


SCOPES = ['https://www.googleapis.com/auth/calendar']

# Building the service.
def build_service():
    if os.path.exists('../tp08_website/attachments/19/token.json'):
        creds = Credentials.from_authorized_user_file('../tp08_website/attachments/19/token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8999)

        # Save the credentials for the next run
        with open('../tp08_website/attachments/19/token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


# Creating an event on the calendar.
def create_event():
    service = build_service()

    event = {
        'summary': 'Test run',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'Test run',
        'start': {
            'dateTime': '2022-11-23T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2022-11-23T09:00:00-08:00',
            'timeZone': 'America/Los_Angeles',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    # Retrieve all the events that start at the given time slot.
    event_results = service.events().list(calendarId='primary',
                                          timeMin=event['start']['dateTime'],
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    ev_list = event_results.get('items', [])

    # Verifier.
    match = False

    # Iterate through the events. If a match exists: do not create the event.
    for e in ev_list:
        if e['summary'] == event['summary']:
            print('The event already exists!')
            match = True
            break

    # If the verifier says match is False, create the event.
    if not match:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))


# ================================================= Calendar Views ====================================================
