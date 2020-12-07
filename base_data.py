from faker import Faker
import pandas as pd
import numpy as np
import random

fake = Faker(locale='sv_SE')
fake.seed(27543)
random.seed(27543)

def create_transactions(rows=500):
    
    transactions = pd.DataFrame()

    transaction_id, transaction_date, product_id, supplier_id, customer_id, manufacturing_line_id = [], [], [], [], [], []
    for i in range(rows):
        transaction_id.append(int(fake.bothify(text=f'########')))
        transaction_date.append(fake.date_between(start_date=f'-{rows}d'))
        product_id.append(fake.bothify(text=f'P{i%6+1}-{i%6+1}######'))
        customer_id.append(fake.bothify(text=f'CU{i%5+1}-{i%5+1}######'))
        supplier_id.append(fake.bothify(text=f'SU{i%4+1}-{i%4+1}######'))
        manufacturing_line_id.append(fake.bothify(text=f'MFG{i%2+1}'))

    transactions['Transaction id'] = transaction_id
    transactions['Transaction date'] = transaction_date
    #transactions['Transaction date'] = transactions['Transaction date'].apply(lambda d: pd.to_datetime(d))
    transactions['Product id'] = product_id
    transactions['Transaction quantity'] = [round(max(0,x)) for x in np.random.triangular(left=-50, mode=50, right=120, size=rows)]
    transactions['Transaction type'] = np.random.choice(a=['Purchase order', 'Manufacturing order', 'Sales order'], size=rows)
    transactions['Customer id'] = np.where(transactions['Transaction type'] == 'Sales order', customer_id, 0)
    transactions['Supplier id'] = np.where(transactions['Transaction type'] == 'Purchase order', supplier_id, 0)
    transactions['Manufacturing group id'] = np.where(transactions['Transaction type'] == 'Manufacturing order', manufacturing_line_id, 0)

    transactions = transactions.sort_values(by=['Transaction date'])
    
    #transactions.to_csv('Transactions.csv', index=False)

    return transactions

# create_transactions(50)
