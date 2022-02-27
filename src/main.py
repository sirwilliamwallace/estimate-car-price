from bs4 import BeautifulSoup
import requests
import mysql.connector
from getpass import getpass
from sklearn import tree
#CONFIG
car_name = input("Input the car name and model you want to search  >>> ").strip()   #car name and model
car_year = int(input('Input the car production year >>>  '))                   #car production year
car_miles = int(input('Input kilometer for used of the car >>> '))            #car used kilometer
# Scraping 
page_num = int(input('Input the page number you want to search >>> '))        #page number
page = 1                                                              
price = []  # list of prices    
mileage = []    # list of mileage
year = []       # list of year
name = []    # list of name
while page != page_num:                                              #while page is not 2
    url = f"https://www.truecar.com/used-cars-for-sale/listings/{car_name}/location-beverly-hills-ca/?page={page}"      #url
    response = requests.get(url)                         #response
    res = requests.get(url + car_name)          
    soup = BeautifulSoup(res.text, 'html.parser')    #soup
    for div in soup.find_all('div', attrs={'data-test': 'vehicleListingPriceAmount'}):  #for div in soup
        price.append(div.get_text(strip=True))  #append price
    for div in soup.find_all('div', attrs={'data-test': 'vehicleMileage'}):
        mileage.append(div.get_text(strip=True))    
    for span in soup.find_all('span', attrs={'class': 'vehicle-card-year font-size-1'}):    
        year.append(span.get_text(strip=True))  
    for span in soup.find_all('span', attrs={'class': 'vehicle-header-make-model text-truncate'}):  
        name.append(span.get_text(strip=True))  
    page += 1   

# Making the scraped data clear
mileage_list = []   
price_list = [] 
for item in mileage:    
    this = item.replace(',', '').replace('miles', '').replace('les', '')        
    mileage_list.append(this)   #append mileage

for item in price:
    this = item.replace(',', '').replace('$', '')
    price_list.append(this) #append price

db_name = 'final' # db name
tablename = 'machinelearning' # table name
db_pass = getpass("Input your database password >>> ") # db password
config = {
    "user" : 'root',
    "password" : db_pass ,
    "host" : '127.0.0.1',
    "database" :db_name,
}
cnx = mysql.connector.connect(**config) #connect to database
cursor = cnx.cursor()   #cursor

for x, y, z, u in zip(name, year, mileage_list, price_list):    
    cursor.execute('INSERT INTO %s VALUES (\'%s\',\'%i\',\'%i\',\'%i\')' % (tablename, x, int(y), int(z), int(u)))  #insert data

cnx.commit()    #commit
cursor.execute('SELECT * FROM %s WHERE name = (\'%s\')' % (tablename ,car_name))  #select data
lines = cursor.fetchall()   #fetch data
# print (lines) 
x = []  
y = []
if lines != []:  #if lines is not empty
    for line in lines:  
        x.append(line[1:3])  #append year and mileage
        y.append(line[3])   #append price
    clf = tree.DecisionTreeClassifier() #decision tree
    clf = clf.fit(x,y)  #fit
    new_data = [[car_year, car_miles]]  #new data
    answer = clf.predict(new_data)  #predict
    print('Estimated Price is >>> \t$', answer[0])  #print answer

else:   #if lines is empty
    print ("No car found with name %s" % (car_name))    #print no car found

cnx.close()
