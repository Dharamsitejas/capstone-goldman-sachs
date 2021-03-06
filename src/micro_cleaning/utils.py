# Utils for cleaning data

import cleanco
import zipcode
import pandas as pd
import numpy as np
import re
import string

#CLEANCO employer name and change to uppercase
def employer_name_uppercase_cleanco(x):
    if pd.isnull(x):
        return x
    else:
        return cleanco(str(x).upper()).clean_name()

#Remove basic punctuation and change to upper case
def uppercase_nopunct(x): 
    if pd.isnull(x):
        return x
    else:
        return str(x).upper().replace('[^\w\s]','').replace('/',' ').replace('  ',' ').strip()

#List of approved state values
state_values = ['TX', 'MA', 'MI', 'CA', 'VA', 'NJ', 'NY', 'PA', 'FL', 'MN', 'IL',
       'MD', 'CT', 'WA', 'IA', 'CO', 'AZ', 'GA', 'OK', 'LA', 'WI', 'ND',
       'UT', 'IN', 'OH', 'KY', 'NC', 'NH', 'MO', 'TN', 'ID', 'VT', 'DC',
       'SD', 'AL', 'OR', 'AR', 'NM', 'SC', 'NE', 'DE', 'WY', 'HI', 'KS',
       'WV', 'ME', 'RI', 'NV', 'MS', 'AK','MT','PR','GU','VI', 'MP']

#Get a list of noncompliant employer state and worksite state values
def check_states(x):
    if pd.isnull(x['EMPLOYER_STATE']):
        print("Null Employer State: {}".format(x.EMPLOYER_NAME))
    elif x['EMPLOYER_STATE'] not in state_values:
        print("Wrong Employer State: {}, {}, {}".format(x.EMPLOYER_NAME, x.EMPLOYER_CITY, x.EMPLOYER_STATE))
    if pd.isnull(x['WORKSITE_STATE']):
        print("Null Worksite State: {}".format(x.EMPLOYER_NAME))
    elif x['WORKSITE_STATE'] not in state_values:
        print("Wrong Worksite State: {}, {}, {}".format(x.EMPLOYER_NAME, x.WORKSITE_CITY, x.WORKSITE_STATE))

#Set up standardization for date fields
right_pattern = '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
long_format = '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}$'
slash_format = '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$'
slash_format_2 = '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}$'
slash_format_long = '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}$'

#Date cleaning function to return YYYY-MM-DD, or None if it doesn't match anything
def check_apply_date_pattern(x):
    if pd.isnull(x):
        return x
    else:
        x=x.replace(" ",'')
    if re.match(right_pattern,x):
        return x
    elif re.match(long_format, x):
        return x[:10].strip()
    elif re.match(slash_format, x):
        month = x[:x.index('/')]
        day = x[x.index('/')+1:x.index('/',x.index('/')+1)]
        year = x[x.index('/',x.index('/')+1)+1:]
        return "{}-{}-{}".format(year.strip(), month.zfill(2).strip(), day.zfill(2).strip())
    elif re.match(slash_format_2, x):
        month = x[:x.index('/')]
        day = x[x.index('/')+1:x.index('/',x.index('/')+1)]
        year = x[x.index('/',x.index('/')+1)+1:]
        return "20{}-{}-{}".format(year.strip(), month.zfill(2).strip(), day.zfill(2).strip())
    elif re.match(slash_format_long, x):
        month = x[:x.index('/')]
        day = x[x.index('/')+1:x.index('/',x.index('/')+1)]
        year = x[x.index('/',x.index('/')+1)+1:x.index('/',x.index('/')+1)+5]
        return "{}-{}-{}".format(year.strip(), month.zfill(2).strip(), day.zfill(2).strip())
    else:
        print("ERROR: x is",x,"returning None")
        return None

#Set up standardization for zipcodes
right_zip = '^[0-9]{5}$'
long_zip = '^[0-9]{5}[\s-]'
fourDigit_zip = '^[0-9]{4}$'
state_zip ='^[A-Z]{2}\s[0-9]{5}$'

#Function for fixing zipcodes into right format
def fix_zip(x):
    x = str(x).strip()
    if pd.isnull(x):
        return x
    if re.match(right_zip,x):
        return x
    elif re.match(long_zip,x):
        return x[:5]
    elif re.match(fourDigit_zip,x):
        return '0' + x
    else:
        print("zip code error: ",x)
        return None

def fix_socCode(x):
    soc = str(x).strip()
    soc = re.sub('[\.]+[0-9]{2}$', '', soc)
    
    if(re.match('^[0-9]{2}-[0-9]{4}$', soc)):
        return soc
    elif(re.match('^[0-9]{2}\.[0-9]{4}$', soc)):
        return re.sub('\.', '-', soc)
    elif(re.match('^[0-9]{6}$', soc)):
        return soc[:2] + '-' + soc[2:]
    else:
        print('SOC code error: ', x, '|', soc)
        return soc

def fix_unitOfPay(x):
    if(x in ['Bi-Weekly', 'BI']):
        return 'B'
    elif(x in ['Hour', 'HR']):
        return 'H'
    elif(x in ['Month', 'MTH']):
        return 'M'
    elif(x in ['Week', 'WK']):
        return 'W'
    elif(x in ['Year', 'YR']):
        return 'Y'
    else:
        return None

#Fix states based on zipcode
def fix_states(x):
    if pd.isnull(x['EMPLOYER_STATE']):
        return x.EMPLOYER_STATE
    elif x['EMPLOYER_STATE'] not in state_values and x.EMPLOYER_POSTAL_CODE.isdigit():
        newzip = zipcode.isequal(x.EMPLOYER_POSTAL_CODE)
        if newzip is not None:
            print("Old state was",x.EMPLOYER_STATE,"and new state is",newzip.state)
            return newzip.state
        else:
            return x.EMPLOYER_STATE
    else:
        return x.EMPLOYER_STATE


 # Set up function to standardize unit of pay
def standard_unit(x):
    if(pd.isnull(x)):
        return x
    elif x in ['Y','H','M','W','B']:
        return x
    elif x=='Year':
        return 'Y'
    elif x=='Hour':
        return 'H'
    elif x=='Month':
        return 'M'
    elif x=='Week':
        return 'W'
    elif x=='2 weeks':
        return 'B'
    else:
        print("Error,",x)
        return x

 #Set up function to go from part time to full time position
def part_to_full(x):
    if pd.isnull(x):
        return x
    elif x=="N":
        return 1
    elif x=="Y":
        return 0
    else:
        print("Error,",x)
        return None

#Create function to clean up WAGE_RATE_OF_PAY
def calc_wage_rate_of_pay(x):
    if pd.isnull(x.WAGE_RATE_OF_PAY_FROM) and pd.isnull(x.WAGE_RATE_OF_PAY_TO):
        return float(x.WAGE_RATE_OF_PAY_FROM)
    elif pd.isnull(x.WAGE_RATE_OF_PAY_TO) or x.WAGE_RATE_OF_PAY_TO=='0' or x.WAGE_RATE_OF_PAY_TO=='.':
        return float(x.WAGE_RATE_OF_PAY_FROM)
    else:
        return (float(x.WAGE_RATE_OF_PAY_FROM)+float(x.WAGE_RATE_OF_PAY_TO))/2

def emp_address(x):
    if pd.isnull(x):
        return x
    else:
        a = str.maketrans('','', string.punctuation)
        return re.sub('\s+', ' ', str(x).strip().translate(a)).upper()

def update_fix_zip(x):
    a = str.maketrans('','', string.punctuation)
    x = re.sub('\s+', ' ', str(x).strip().translate(a))
    x = x.replace('O', '0').strip()
    x = x.replace('NBSP', '').strip()
    x = x.replace('NA', '').strip()
    if pd.isnull(x):
        return x
    if re.match(right_zip,x):
        return x
    elif re.match(long_zip,x):
        return x[:5]
    elif re.match(state_zip,x):
        return x[-5:]
    elif re.match(fourDigit_zip,x):
        return '0' + x
    else:
        try:
            int(x)
            if len(x) == 9 or len(x) == 8:
                return x[:5]
            else:
                print("zip code error: ",x)
                return None
        except:
            print("Not a number: ", x)
            return None

def update_fix_states(x):
    if pd.isnull(x['EMPLOYER_STATE']):
        if x.EMPLOYER_POSTAL_CODE:
            newzip = zipcode.isequal(x.EMPLOYER_POSTAL_CODE)
            if newzip is not None:
                print("Old state was",x.EMPLOYER_STATE,"and new state is",newzip.state, "Case Number:", x.CASE_NUMBER)
                return newzip.state
            else:
                return x.EMPLOYER_STATE
    elif x['EMPLOYER_STATE'] not in state_values and x.EMPLOYER_POSTAL_CODE.isdigit():
        newzip = zipcode.isequal(x.EMPLOYER_POSTAL_CODE)
        if newzip is not None:
            print("Old state was",x.EMPLOYER_STATE,"and new state is",newzip.state, "Case Number:", x.CASE_NUMBER)
            return newzip.state
        else:
            return x.EMPLOYER_STATE
    else:
        return x.EMPLOYER_STATE

def worksite_fix_states(x):
    if pd.isnull(x['WORKSITE_STATE']):
        if x.WORKSITE_POSTAL_CODE:
            newzip = zipcode.isequal(x.WORKSITE_POSTAL_CODE)
            if newzip is not None:
                print("Old state was",x.WORKSITE_STATE,"and new state is",newzip.state, "Case Number:", x.CASE_NUMBER)
                return newzip.state
            else:
                return x.WORKSITE_STATE
    elif x['WORKSITE_STATE'] not in state_values and x.WORKSITE_POSTAL_CODE.isdigit():
        newzip = zipcode.isequal(x.WORKSITE_POSTAL_CODE)
        if newzip is not None:
            print("Old state was",x.WORKSITE_STATE,"and new state is",newzip.state, "Case Number:", x.CASE_NUMBER)
            return newzip.state
        else:
            return x.WORKSITE_STATE
    else:
        return x.WORKSITE_STATE

def update_fix_socCode(x):
    soc = str(x).strip()
    soc = re.sub('\s', '', soc)
    if(re.match('^[0-9]{2}[\.\-][0-9]{4}[\.\-][0-9]{2}$', soc)):
        return soc[:2] + '-' + soc[3:7] + '.' + soc[8:]
    if(re.match('^[0-9]{2}-[0-9]{4}$', soc)):
        return soc
    elif(re.match('^[0-9]{2}\.[0-9]{4}$', soc)):
        return re.sub('\.', '-', soc)
    elif(re.match('^[0-9]{2}\/[0-9]{4}$', soc)):
        return re.sub('\/', '-', soc)
    elif(re.match('^[0-9]{6}$', soc)):
        return soc[:2] + '-' + soc[2:]
    elif(re.match('^[0-9]{6}\.[0-9]{2}$', soc)):
        return soc[:2] + '-' + soc[2:]
    else:
        print('SOC code error: ', x, '|', soc)
        return soc

def calc_wage(x):
    wf = x.WAGE_RATE_OF_PAY_FROM
    wt = x.WAGE_RATE_OF_PAY_TO
    if pd.isnull(wt):
        return wf

    if wf <=wt:
        return (wf + wt)/2
    else:
        return wf