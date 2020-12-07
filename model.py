#%%
from sdv import Metadata
from sdv.relational import HMA1
from sdv.tabular import GaussianCopula
from sdv.timeseries import PAR
import numpy as np
import pandas as pd
from base_data import *

data = create_transactions(50)
base_model = GaussianCopula()
base_model.fit(data)
transactions = base_model.sample(1000)

transactions.to_csv('Transactions.csv', index=False)

#Products
products = pd.DataFrame(transactions['Product id'].drop_duplicates())
products['Product group'] = products['Product id'].apply(lambda x: x.split('-')[0])
products['Product cost'] = [round(x, 3) for x in np.random.gamma(shape=10, scale=5, size=products.shape[0])]
products['Product inventory unit'] = 'st'
products['Product available in stock'] = [round(max(0, x)) for x in np.random.triangular(left=-50, mode=50, right=120, size=products.shape[0])]

products.to_csv('Products.csv', index=False)

#Purchase orders
purchase_orders = transactions[(transactions['Transaction type']=='Purchase order') & (transactions['Supplier id']!=0)].copy()
purchase_orders = purchase_orders.drop(columns=['Customer id', 'Transaction type', 'Manufacturing group id'])
purchase_orders = purchase_orders.rename(columns={'Transaction id': 'Purchase order id', 'Transaction date': 'Reception date', 'Transaction quantity': 'Received quantity'})
purchase_orders = pd.merge(purchase_orders, products[['Product id', 'Product cost']], how='left', on='Product id')
purchase_orders = purchase_orders.rename(columns={'Product cost': 'Purchase price'})
purchase_orders['Cost of goods received'] = purchase_orders['Purchase price'] * purchase_orders['Received quantity']

purchase_orders.to_csv('Purchase orders.csv', index=False)

#Sales orders
sales_orders = transactions[(transactions['Transaction type']=='Sales order') & (transactions['Customer id']!=0)].copy()
sales_orders = sales_orders.drop(columns=['Supplier id', 'Transaction type', 'Manufacturing group id'])
sales_orders = sales_orders.rename(columns={'Transaction id': 'Sales order id', 'Transaction date': 'Delivery date', 'Transaction quantity': 'Delivered quantity'})
sales_orders = pd.merge(sales_orders, products[['Product id', 'Product cost']], how='left', on='Product id')
sales_orders = sales_orders.rename(columns={'Product cost': 'Sales price'})
sales_orders['Cost of goods sold'] = sales_orders['Sales price'] * sales_orders['Delivered quantity']
sales_orders['Sales amount'] = sales_orders['Cost of goods sold'] * np.array([x for x in np.random.triangular(left=1.05, mode=1.15, right=1.6, size=sales_orders.shape[0])])

sales_orders.to_csv('Sales orders.csv', index=False)

#Customers
customers = pd.DataFrame(transactions['Customer id'].dropna().drop_duplicates())
customers['Customer group'] = customers['Customer id'].apply(lambda x: x.split('-')[0])
customers['Customer responsible'] = [fake.name() for _ in range(customers.shape[0])]
customers['Customer address'] = [fake.address().replace('\n', '') for _ in range(customers.shape[0])]

customers.to_csv('Customers.csv', index=False)

#Suppliers
suppliers = pd.DataFrame(transactions['Supplier id'].dropna().drop_duplicates())
suppliers['Supplier group'] = suppliers['Supplier id'].apply(lambda x: x.split('-')[0])
suppliers['Supplier responsible'] = [fake.name() for _ in range(suppliers.shape[0])]
suppliers['Supplier address'] = [fake.address().replace('\n', '') for _ in range(suppliers.shape[0])]

suppliers.to_csv('Suppliers.csv', index=False)

tables = {'Products': products,
          'Suppliers': suppliers,
          'Customers': customers,
          'Sales orders': sales_orders,
          'Purchase orders': purchase_orders}

metadata = Metadata()
metadata.add_table(
        name='Products',
        data=tables['Products'],
        primary_key='Product id'
)
metadata.add_table(
        name='Sales orders',
        data=tables['Sales orders'],
        primary_key='Sales order id',
        foreign_key='Product id',
        parent='Products'
)
metadata.add_table(
        name='Purchase orders',
        data=tables['Purchase orders'],
        primary_key='Purchase order id',
        foreign_key='Product id',
        parent='Products'
)
metadata.add_table(
        name='Customers',
        data=tables['Customers'],
        primary_key='Customer id'
)
metadata.add_relationship(
        parent='Customers',
        child='Sales orders',
        foreign_key='Customer id'
)
metadata.add_table(
        name='Suppliers',
        data=tables['Suppliers'],
        primary_key='Supplier id'
)
metadata.add_relationship(
        parent='Suppliers',
        child='Purchase orders',
        foreign_key='Supplier id'
)

metadata.visualize('Schema2.png')

# %%
