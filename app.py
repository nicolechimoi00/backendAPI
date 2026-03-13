from flask import *
import pymysql
import pymysql.cursors
# step8-on add_product function 
import os

# create a flask app 
app=Flask(__name__)

# configure the upload folder
app.config['UPLOAD_FOLDER']='static/images'

# create the route of the api /endpoint
@app.route("/api/signup", methods=['POST'])

# Create a function to handle the signup process
def signup():
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form['email']
        passwrd=request.form['passwrd']
        phone=request.form['phone']

        # connect to the database for data storage
        connection=pymysql.connect(host='localhost', user='root', password='', database='SokoGarden')

        # insert the data to the database
        # cursor-allows run sql queries in python
        cursor=connection.cursor()
        cursor.execute('insert into users(username,email,passwrd,phone)values(%s,%s,%s,%s)',
        (username,email,passwrd,phone))

        # cursor the save or --commits the changes to the database
        connection.commit()







        

        return jsonify({
            'success':'Thank you for joining'
        })


# create function to handle sign in 

# step1-Define the route
@app.route('/api/signin',methods=['POST'])

# step 2 - create a function 
def signin():

    # step3-extract POST data 
    email=request.form.get('email')
    passwrd=request.form.get('passwrd')

    # step4-connect to the database
    connection=pymysql.connect(host='localhost', user='root',password='',database='SokoGarden')

    # step5-create a cursor to return results a dictionary,initialize connection
    cursor=connection.cursor(pymysql.cursors.DictCursor)

    # step6- sql query to select from the users table email and passwrd
    sql = 'select * from users where email=%s and passwrd=%s'

    # step7- prepare the data to replace the placeholders %s 
    data=(email,passwrd)

    # step8-use the cursor to exeute the sql providing the data to replace the placeholders
    cursor.execute(sql,data)

    # step9-check how rows are found
    count=cursor.rowcount

    # step -10 count if row are zero,invalid credentials-no users found
    if count==0:
        return jsonify({
            'message' : 'Login failed'
        })
    else:
        # else there is a user,return a message to say login success and all user details,fetch None() to get all user login details
        user=cursor.fetchone()

        # step 11-return the login success message with user details as dictionary
        return jsonify({
            'message':'Login success',
            'user': user
        })

 # ADD PRODUCTS FUNCTION
#  step1- define the route
@app.route('/api/add_product',methods=['POST'])

# step2-create a function to perform the act of adding the products
def add_product():
    if request.method=='POST':

        # step3-extract the data 
        product_name=request.form['product_name']
        product_description=request.form['product_description']
        product_cost=request.form['product_cost']

       # product_photo=request.form['product_photo']
       #    extract the image data 
        photo=request.files['product_photo']

        # get the image file name
        file_name=photo.filename

        # specify where the image will be saved(in static folder)-image path
        photo_path=os.path.join(app.config['UPLOAD_FOLDER'],file_name)
        
        # save the image
        photo.save(photo_path)


        # step4-connect to the database
        connection=pymysql.connect(host='localhost',user='root',password='',database='SokoGarden')

        # step5-prepare and execute query to insert the data into our database
        cursor=connection.cursor()

        cursor.execute('INSERT INTO product_details(product_name,product_description,product_cost,product_photo)' \
        'VALUES(%s,%s,%s,%s)',(product_name,product_description,product_cost,file_name))

        # step6-cursor saves or commits the changes to the database
        connection.commit()

        # step7-return the success message 
        return jsonify({
            'success' :'product added successfully'
        })


# get products function

# define the route
@app.route('/api/get_products_details',methods=['GET'])
def get_products_details():

    # connect to the database with Dictcursor for direct dictionary results
    connection=pymysql.connect(host='localhost',user='root',password='',database='SokoGarden')

    # create the cursor object and fetch all data from the product details table
    cursor=connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM product_details')
    product_details=cursor.fetchall()

    # close the database  connection
    connection.close()

    # return the fetched products
    return product_details


# mpesa stk push payment

import datetime
import base64
import requests
from requests.auth import HTTPBasicAuth

# define route
@app.route('/api/mpesa_payment',methods = ['POST'])
def mpesa_payment():
    if request.method =='POST':
        amount = request.form['amount']
        phone = request.form.get('phone')


        #credentials fro the daraja api
        consumer_key = 'GTWADFxIpUfDoNikNGqq1C3023evM6UH'
        consumer_secret = 'amFbAoUByPV2rM5A'


        # api_url token url
        api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type = client_credentials'

        # request access token
        r = requests.get(api_url, auth = HTTPBasicAuth(consumer_key,consumer_secret))

        data = r.json()
        access_token = 'Bearer' + '' + data['access_token']


        # generate the time stamp for the transaction
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        # 20260311125610 

        # the pass key from safaricom 
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'


        # business short code
        business_short_code = '174379'

        # create the password 
        data = business_short_code + passkey + timestamp

        # encode the password 
        encoded = base64.b64encode(data.encode())

        # convert the encoded password to a string
        password = encoded.decode('utf-8') 
        # this transforms the password to a readable text


        # create payment payload
        payload = {
            'business_short_code' : '174379',
            'password' : '{}'.format(password),
            'transactionType' : 'CustomerPaybillOnline',
            'amount' : '1',
            'PartyA' : '0725930279',
            'PartyB' : '174379',
            'PhoneNumber' : phone,
            'accountReference' : 'account',
            'transactionDesc' : 'account'

        }

        # HTTP headers
        headers = {
            'Authorization' : access_token,
            'Content-type' : 'application/json'
        }

        # stl push API endpoint
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

        # send the request to safaricom

        response = request.post(url, json = payload, headers = headers)


        # print the response
        print(response.text)


        # return response
        return jsonify({
            'message' : 'please complete the payment in your phone and we will deliver in minutes'
        })





# run the app
if __name__=='__main__':
    app.run(debug=True)
