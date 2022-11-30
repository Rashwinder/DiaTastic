from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Initialise necessities
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = Credentials.from_authorized_user_file('../tp08_website/attachments/19/token.json', SCOPES)

# def create_event(request):
#   # If credentials exist:
#   if creds:
#     # Initialise Google's Calendar API.
#     service = build('calendar', 'v3', credentials=creds)
#
#     # Register the event.
#     event = {
#       'summary': request.POST.get('summary'),
#       'location': request.POST.get('summary'),
#       'description': request.GET.get('summary'),
#       'start': {
#         'dateTime': str(request.GET.get('summary')) + 'T' + str(request.GET.get('summary')),
#         'timeZone': 'America/Los_Angeles',
#       },
#       'end': {
#         'dateTime': str(request.GET.get('summary')) + 'T' + str(request.GET.get('summary')),
#         'timeZone': 'America/Los_Angeles',
#       },
#       'recurrence': [
#         'RRULE:FREQ=DAILY;COUNT=2'
#       ],
#       'attendees': [],
#       'reminders': {
#         'useDefault': True,
#       }
#     }

if creds:
  # Initialise Google's Calendar API.
  service = build('calendar', 'v3', credentials=creds)
  # Register the event.
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
  events_result = service.events().list(calendarId='primary',
                                        timeMin=event['start']['dateTime'],
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
  ev_list = events_result.get('items',[])

  # Verifier.
  match = False

  # Iterate through the events. If a match exists: do not create the event.
  for e in ev_list:
    if e['summary'] == event['summary']:
      print('The event already exists!')
      match = True
      break

  # If the verifier says match is False, create the event.
  if match == False:
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
