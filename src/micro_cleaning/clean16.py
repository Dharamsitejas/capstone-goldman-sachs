import pandas as pd
import numpy as np
import re
import os
import utils 
import string

data_dir = "data/"

files = ["H-1B_Disclosure_Data_FY16.xlsx", 
            "H-1B_Disclosure_Data_FY15_Q4.xlsx", 
            "H-1B_FY14_Q4.xlsx", 
            "LCA_FY2013.xlsx"]

data = pd.read_excel(data_dir + files[0])

data.VISA_CLASS = data.VISA_CLASS.replace('Select Visa Classification', 'H-1B')

data['CASE_SUBMITTED'] = data['CASE_SUBMITTED'].dt.strftime('%Y-%m-%d')
data['DECISION_DATE'] = data['DECISION_DATE'].dt.strftime('%Y-%m-%d')

data['EMPLOYER_ADDRESS'] = data['EMPLOYER_ADDRESS'].apply(utils.emp_address)

data.EMPLOYER_POSTAL_CODE = data['EMPLOYER_POSTAL_CODE'].apply(utils.update_fix_zip)

data.WORKSITE_POSTAL_CODE = data['WORKSITE_POSTAL_CODE'].apply(utils.update_fix_zip)


data["EMPLOYER_CITY"]=data.EMPLOYER_CITY.apply(utils.uppercase_nopunct)
data["EMPLOYER_STATE"]=data.EMPLOYER_STATE.apply(utils.uppercase_nopunct)
data["WORKSITE_CITY"]=data.WORKSITE_CITY.apply(utils.uppercase_nopunct)
data["WORKSITE_STATE"]=data.WORKSITE_STATE.apply(utils.uppercase_nopunct)


data.EMPLOYER_STATE = data[['CASE_NUMBER','EMPLOYER_STATE', 'EMPLOYER_POSTAL_CODE']].apply(utils.update_fix_states, axis =1)
data.WORKSITE_STATE = data[['CASE_NUMBER','WORKSITE_STATE', 'WORKSITE_POSTAL_CODE']].apply(utils.worksite_fix_states, axis =1)

data.JOB_TITLE = data['JOB_TITLE'].apply(utils.emp_address)
data['DOT_CODE'] = None

data.SOC_CODE = data.SOC_CODE.apply(utils.update_fix_socCode)


data.EMPLOYER_PHONE = data.EMPLOYER_PHONE.apply(utils.emp_address)
data['EMPLOYER_AREA_CODE'] = [
    str(i)[:3] if len(str(i)) == 10 else np.nan for i in data['EMPLOYER_PHONE']
]

data['WAGE_UNIT_OF_PAY'] = data['WAGE_UNIT_OF_PAY'].apply(utils.fix_unitOfPay)
data['PW_UNIT_OF_PAY'] = data['PW_UNIT_OF_PAY'].apply(utils.fix_unitOfPay)

data['WAGE_RATE_OF_PAY_FROM'] = data['WAGE_RATE_OF_PAY_FROM'].replace(0, np.nan)
data['WAGE_RATE_OF_PAY_TO'] = data['WAGE_RATE_OF_PAY_TO'].replace(0, np.nan)
data['WAGE_RATE_OF_PAY'] = data[['WAGE_RATE_OF_PAY_FROM', 'WAGE_RATE_OF_PAY_TO']].apply(utils.calc_wage, axis =1)



cdata = data[['CASE_SUBMITTED', 'CASE_NUMBER', 'CASE_STATUS', 'DECISION_DATE', 'VISA_CLASS',
    			'JOB_TITLE', 'DOT_CODE', 'SOC_CODE', 'SOC_NAME', 'FULL_TIME_POSITION',
    			'EMPLOYER_NAME', 'EMPLOYER_ADDRESS', 'EMPLOYER_CITY', 'EMPLOYER_STATE',
    			'EMPLOYER_POSTAL_CODE', 'EMPLOYER_AREA_CODE', 'NAIC_CODE', 'TOTAL_WORKERS', 
    			'WORKSITE_CITY', 'WORKSITE_STATE', 'WORKSITE_POSTAL_CODE', 'WAGE_RATE_OF_PAY', 
    			'WAGE_UNIT_OF_PAY', 'PREVAILING_WAGE', 'PW_UNIT_OF_PAY']]


if not os.path.exists('clean'):
        os.mkdir('clean')
        
new_filename="2016.csv"
cdata.to_csv("../clean/{}".format(new_filename), encoding='utf-8', index = False)
