from flask_mysqldb import MySQL
from flask import render_template, request, redirect, url_for, session, flash
import pandas as pd
import datetime

class Dataset:
    def __init__(self, id, date, items):
        self.id = id
        self.date = date
        self.items = items

    def __repr__(self):
        return '<Dataset %r>' % self.id

    @classmethod
    def get_all(cls, conn):
        cursor = conn.connection.cursor()        
        cursor.execute('''SELECT datasets.* FROM datasets ORDER BY date ASC''')                
        datasets = cursor.fetchall()
        cursor.close()
        return datasets

    @classmethod
    def get_by_id(cls, conn, id):
        cursor = conn.connection.cursor()
        cursor.execute('''SELECT * FROM datasets WHERE id = %s''', (id,))
        dataset = cursor.fetchone()
        cursor.close()
        return dataset

    @classmethod
    def update(cls, conn, id, code, date, items, total):
        cursor = conn.connection.cursor()
        cursor.execute('''UPDATE datasets SET code = %s, date = %s, items = %s, total = %s WHERE id = %s''', 
                      (code, date, items, total, id))
        conn.connection.commit()
        cursor.close()

    @classmethod
    def store(cls, conn, date, items):
        cursor = conn.connection.cursor()
        cursor.execute('''INSERT INTO datasets (date, items) VALUES (%s, %s)''', (date, items))
        conn.connection.commit()
        cursor.close()

    @classmethod
    def delete(cls, conn, id):
        cursor = conn.connection.cursor()
        cursor.execute('''DELETE FROM datasets WHERE id = %s''', (id,))
        conn.connection.commit()
        cursor.close()

    @classmethod
    def get_by_date(cls, conn, date):
        cursor = conn.connection.cursor()
        cursor.execute('''SELECT * FROM datasets WHERE date = %s  ORDER BY date ASC''', (date,))
        dataset = cursor.fetchone()
        cursor.close()
        return dataset

    @classmethod
    def get_by_date_range(cls, conn, start_date, end_date):
        cursor = conn.connection.cursor()
        cursor.execute('''SELECT * FROM datasets WHERE date BETWEEN %s AND %s ORDER BY date ASC''', (start_date, end_date))
        datasets = cursor.fetchall()
        cursor.close()
        return datasets
        
    @classmethod
    def store_csv(cls, conn, file):
        cursor  = conn.connection.cursor()
        data    = pd.read_csv(file)
        df      = pd.DataFrame(data, columns= ['date', 'code', 'items', 'payment_method', 'total', 'total_qty', 'raw_data'])

        for index, row in df.iterrows():
            date    = row['date']
            date    = datetime.datetime.strptime(date, '%d/%m/%Y')
            date    = date.strftime('%Y-%m-%d')            
            code    = row['code']
            items   = row['items']
            payment_method = row['payment_method']       
            total   = row['total']
            total_items = row['total_qty']
            detail = row['raw_data']
            created_by = session['user']['id']

            # sort items before insert
            items = items.split(',')
            items.sort()
            items = ','.join(items)            

            cursor.execute('''INSERT INTO datasets (date, code, items, payment, total, total_items, detail_data, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (date, code, items, payment_method, total, total_items, detail, created_by))
            conn.connection.commit()
            
        cursor.close()

    @classmethod
    def delete_all(cls, conn):
        cursor = conn.connection.cursor()
        cursor.execute('''DELETE FROM datasets''')
        conn.connection.commit()
        cursor.close()
