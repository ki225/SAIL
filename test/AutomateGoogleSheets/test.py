#!pip3 install gspread
#!pip3 install --upgrade google-api-python-client oauth2client

#importing the required libraries

# import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread


# define the scope of the application and add the JSON file with the credentials to access the API.
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('test\AutomateGoogleSheets\service_acc_key.json', scope)

# authorize the clientsheet 
client = gspread.authorize(creds)

# get the instance of the Spreadsheet
sheet = client.open('sc0003r-1')

# get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)


# get the total number of columns
print(sheet_instance.col_count)

# get the value at the specific cell
# print(sheet_instance.cell(col=3,row=2))
## >> <Cell R2C3 '63881'>

# print cell A1:G1
print(sheet_instance.row_values(1))

# print cell A1:G6
print(sheet_instance.get_all_values())


# get all the records of the data
records_data = sheet_instance.get_all_records()

# # view the data
# print(records_data)

# # convert the json to dataframe
# records_df = pd.DataFrame.from_dict(records_data)

# # view the top records
# print(records_df.head())
