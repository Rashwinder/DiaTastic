from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime as dt

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = Credentials.from_authorized_user_file('../tp08_website/attachments/19/token.json', SCOPES)
if creds:
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(calendarId='primary',
                                          timeMin=dt.utcnow().isoformat() + 'Z',
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    if events:
        for event in events:
            print(event['summary'], event['description'], event['location'])
            eventId = event['id']
        # service.events().delete(calendarId='primary', eventId=eventId).execute()