import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

'''
Based on that article https://medium.com/@vince.shields913/
reading-google-sheets-into-a-pandas-dataframe-with-gspread-and-oauth2-375b932be7bf
'''

cred_file = 'delonghi-bot-87c30ebf5e52.json'


def connect_to_google_sheet():
    # Connects to Google Sheet API and returns the dataframe from first sheet

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # authorize in Google Sheet
    credentials = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
    gc = gspread.authorize(credentials)

    # Get the required sheet and parce all data as Pandas dataframe
    wks = gc.open("Delonghi_metrics").sheet1
    data = wks.get_all_values()
    headers = data.pop(0)
    df = pd.DataFrame(data, columns=headers)

    return df


if __name__=="__main__":
    connect_to_google_sheet()