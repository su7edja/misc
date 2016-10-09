import httplib2
import oauth2client
import os

from apiclient import discovery
from datetime import datetime, timedelta
from oauth2client import client
from oauth2client import tools


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = {'all': 'https://www.googleapis.com/auth/calendar',
          'readonly': 'https://www.googleapis.com/auth/calendar.readonly'}
MISC_DIR = os.path.join(os.path.expanduser('~'), 'play', 'misc')
CLIENT_SECRET_FILE = os.path.join(MISC_DIR, 'client_secret.json')
APPLICATION_NAME = 'Google Calendar API Misc'

CALENDARS = {'marathon_n2': '66ujbe34jn577p627521491rkc@group.calendar.google.com', #existing
             'marathon_n1': 'lh6s97eg5634nuir81se2bcfi0@group.calendar.google.com',
             'half_endurance': 'pl56954i5pr3dsit6looq31ac8@group.calendar.google.com',}


def get_scope(scope_level):
    return SCOPES.get(scope_level, SCOPES['readonly'])

def get_credentials(scope_level):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-misc.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        scope = get_scope(scope_level)
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scope)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_calendar_service(scope_level):
    """
    Creates a Google Calendar API service object.
    """
    credentials = get_credentials(scope_level)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    # service._developerKey = credentials.access_token
    return service

def adjust_to_race_date(calendar_id, all_events, race_date_str):
    sorted_all_events = sorted(all_events, key=lambda x: datetime.strptime(x['start']['date'], '%Y-%m-%d'))
    race_date = datetime.strptime(race_date_str, '%Y-%m-%d')
    training_race_date = sorted_all_events[-1]['start']['date']
    difference = (race_date - training_race_date).days
    for e in sorted_all_events:
        new_start = e['start']['date'] + timedelta(days=difference)
        new_end = new_start + timedelta(days=1)
        updated = service.events().patch(
            calendarId=calendar_id,
            eventId=e['id'],
            body={'start': {'date': new_start.strftime('%Y-%m-%d')},
                  'end': {'date': new_end.strftime('%Y-%m-%d')}}).execute()

if __name__ == '__main__':
    service = get_calendar_service('all')
    calendar_id = CALENDARS.get('half_endurance')
    all_events = service.events().list(calendarId=calendar_id).execute()['items']
    mon_30_cross = {'summary': '30min cross',
                  'start': {'date': '2016-10-10'},
                  'end': {'date': '2016-10-11'},
                  'recurrence': ['RRULE:FREQ=WEEKLY;COUNT=2']}
    mon_40_cross = {'summary': '40min cross',
                    'start': {'date': '2016-10-24'},
                    'end': {'date': '2016-10-25'},
                    'recurrence': ['RRULE:FREQ=WEEKLY;COUNT=3']}
    mon_50_cross = {'summary': '50min cross',
                    'start': {'date': '2016-11-07'},
                    'end': {'date': '2016-11-08'},
                    'recurrence': ['RRULE:FREQ=WEEKLY;INTERVAL=2;COUNT=2']}
    mon_60_cross = {'summary': '60min cross',
                    'start': {'date': '2016-11-28'},
                    'end': {'date': '2016-11-29'},
                    'recurrence': ['RRULE:FREQ=WEEKLY;INTERVAL=2;COUNT=2']}

    for event in (mon_30_cross, mon_40_cross, mon_50_cross, mon_60_cross):
        service.events().insert(calendarId=calendar_id, body=event).execute()

    # race_date_str = '2017-01-09'
    # adjust_to_race_date(calendar_id, all_events, race_date_str)
