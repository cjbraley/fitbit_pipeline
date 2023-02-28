import os
import dotenv
from datetime import datetime
import configparser


import fitbit
import fitbit_api.gather_keys_oauth2 as Oauth2
import pandas as pd


# load all existing env
dotenv.load_dotenv(override=True)  # use .env file

ROOT_DIR = os.environ.get('ROOT_DIR')
CLIENT_ID = os.environ.get('FITBIT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('FITBIT_CLIENT_SECRET')

# load config
config = configparser.ConfigParser()
config.read(f'{ROOT_DIR}/fitbit_api/.config')

API_ENDPOINT = config['FITBIT']['API_ENDPOINT']
API_VERSION = config['FITBIT']['API_VERSION']


def get_auth_token():

    # Never completes if wrapped by task
    server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()  # get access token

    ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

    # print(f"Access Token: {ACCESS_TOKEN}")
    # print(f"Refresh Token: {REFRESH_TOKEN}")

    # Write changes to .env file.
    dotenv_path = dotenv.find_dotenv()
    dotenv.set_key(dotenv_path, "FITBIT_ACCESS_TOKEN", ACCESS_TOKEN)
    dotenv.set_key(dotenv_path,
                   "FITBIT_REFRESH_TOKEN", REFRESH_TOKEN)

    # Always write to root, even from tmp folder
    dotenv.set_key(f"{ROOT_DIR}/.env", "FITBIT_ACCESS_TOKEN", ACCESS_TOKEN)
    dotenv.set_key(f"{ROOT_DIR}/.env",
                   "FITBIT_REFRESH_TOKEN", REFRESH_TOKEN)


def get_authd_client():

    # Make sure the updated env is present
    dotenv.load_dotenv(override=True)
    ACCESS_TOKEN = os.environ.get('FITBIT_ACCESS_TOKEN')
    REFRESH_TOKEN = os.environ.get('FITBIT_REFRESH_TOKEN')

    # generate client
    return fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True,
                         access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)


def intraday_request(client,  date, frequency, resource, datatype):

    # CREATE URL
    url = f"{API_ENDPOINT}/{API_VERSION}/user/-/activities/{resource}/date/{date.year}-{date.month:02d}-{date.day}/1d/{frequency}.json"
    print(url)

    # FETCH
    data = client.make_request(url)

    # TRANSFORM
    df = pd.DataFrame(data[f"activities-{resource}-intraday"]["dataset"])

    # create datetime
    df.insert(0, 'activity_datetime', df['time'].map(lambda time: datetime.combine(
        date, datetime.strptime(time, '%H:%M:%S').time())))

    # drop time
    df.drop(['time'], axis=1, inplace=True)

    # set types
    df['value'] = df['value'].astype(datatype)

    print(df.info())

    return df


def sleep_request(client, date):

    # Sleep data
    url = f"{API_ENDPOINT}/{API_VERSION}/user/-/sleep/date/{date.year}-{date.month:02d}-{date.day:02d}.json"
    sleep_data = client.make_request(url)

    if sleep_data['summary']['totalTimeInBed'] == 0:
        return pd.DataFrame()

    # Goal data
    url = f"{API_ENDPOINT}/{API_VERSION}/user/-/sleep/goal.json"
    goal_data = client.make_request(url)

    # Create df
    sleep_dict = sleep_data["summary"]["stages"]
    sleep_dict['activity_date'] = date.date()
    sleep_dict['startTime'] = sleep_data["sleep"][0]["startTime"]
    sleep_dict['endTime'] = sleep_data["sleep"][0]["endTime"]
    sleep_dict['minutesToFallAsleep'] = sleep_data["sleep"][0]["minutesToFallAsleep"]

    sleep_dict['bedtime'] = goal_data["goal"]["bedtime"]
    sleep_dict['minDuration'] = goal_data["goal"]["minDuration"]

    # Fix types
    df = pd.DataFrame({key: [value] for key, value in sleep_dict.items()})
    df = df.astype({
        'activity_date': 'object',
        'bedtime': 'object',
        'deep': 'int32',
        'light': 'int32',
        'rem': 'int32',
        'wake': 'int32',
        'minutesToFallAsleep': 'int32',
        'minDuration': 'int32',
        'startTime': 'datetime64',
        'endTime': 'datetime64',
    })
    print(df.info())

    return df


if __name__ == "__main__":

    # Testing
    request_date = pd.datetime(year=2023, month=2, day=24)
    # get_auth_token()
    authd_client = get_authd_client()

    # data = intraday_request(authd_client, request_date,'15min', 'steps', 'int32')
    # data = sleep_request(authd_client, request_date)
