from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from time import sleep
import sqlite3 as sql
import hashlib as hl
import sys
#TbIF16hoUqGl
#tCysClmL8
app = Flask(__name__)
app.secret_key = "6207dab6b2eb1dd0c4342bbd85cb56e6"
host = 'http://127.0.0.1:5000/'

@app.route('/', methods=['GET','POST'])
def index():
    session['Email'] = ""
    if request.method == 'POST':
        log = checkLogin(request.form['Email'],request.form['Password'])
        if log:
            session['Email'] = request.form['Email']
            return redirect("/userinfo.html")
        else:
            return render_template('login.html', fail = True)
    else:
        return render_template('login.html')

@app.route('/userinfo.html', methods=['GET','POST'])
def uinfo():
    email = session['Email']
    result = getInfo(email)
    if request.method == 'GET':
        return render_template('userinfo.html', result=result, seller=isSeller(email))
    else:
        r = changePassword(email, request.form['Password'], request.form['P1'], request.form['P2'])
        return render_template('userinfo.html', result=result, res = r, seller=isSeller(email))

@app.route('/sellerlist.html',methods=['GET','POST'])
def selllist():
    email = session['Email']
    if request.method == 'POST':
        id = request.form['id']
        if id[0] == 'd':
            removeList(id[1:])

        else:
            addList(id[1:])

    lists = getSellerLists(email)
    return render_template('sellerlist.html', lists=lists)

@app.route('/publish.html',methods=['GET','POST'])
def publish():
    cats = getCats()
    if request.method == 'POST':
        publishList(session['Email'],request.form['Categories'],request.form['Title'],request.form['Name'],request.form['Description'],
        request.form['Price'],request.form['qty'])
        return redirect('userinfo.html')
    return render_template('publish.html', Cats=cats)

@app.route('/listings.html', methods=['GET'])
def lists():
    l = getCats()
    if request.args.get('search') is not None:
        arg = request.args.get('search')
        res = getResults(arg)
        return render_template('listings.html',Cats=l,res=res, sel = request.args.get('search'))
    else:
        return render_template('listings.html', Cats=l)

@app.route('/viewproduct.html', methods=['GET'])
def viewprod():
    email = session['Email']
    arg = request.args.get('id')
    res = prodInfo(arg)
    return render_template('viewproduct.html',prod=res,email=email)

@app.route('/confirmbuy.html',methods=['GET','POST'])
def confirmbuy():
    prod = prodInfo(request.args.get('id'))
    qty = request.args.get('qty')
    email = session['Email']
    cc = getInfo(email)[0][7]
    if request.method == 'POST':
        placeOrder(prod,qty)
        return redirect('/userinfo.html')
    else:
        return render_template('confirmbuy.html',prod=prod,qty=qty,cc=cc)

#Login logic
def checkLogin(email,password):
    #Check against hash of password
    hpass = hl.md5(password.encode()).hexdigest()
    connection = sql.connect('database.db')
    cur = connection.cursor()
    cur.execute('SELECT * FROM Users U WHERE U.email = ? AND U.password = ?',(email,hpass))
    r = cur.fetchall()
    if len(r) > 0:
        return True
    else:
        return False

def isSeller(email):
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Sellers S WHERE S.email = ?",(email,))
    r = cur.fetchall()
    if len(r) > 0:
        return True
    else:
        return False
    

def getInfo(email):
    connection = sql.connect('database.db')
    cur = connection.cursor()
    r = cur.execute("SELECT first_name, last_name, email, gender, age FROM Buyers B WHERE B.email = ?",(email,))
    r1 = r.fetchall()
    r = cur.execute('SELECT A.street_num, A.street_name, Z.city, Z.state_id, Z.zipcode FROM Buyers B, Address A, Zipcode_Info Z WHERE B.email = ? AND B.home_address_id = A.address_id AND A.zipcode = Z.zipcode',(email,))
    r2 = r.fetchall()
    r = cur.execute('SELECT A.street_num, A.street_name, Z.city, Z.state_id, Z.zipcode FROM Buyers B, Address A, Zipcode_Info Z WHERE B.email = ? AND B.billing_address_id = A.address_id AND A.zipcode = Z.zipcode',(email,))
    r3 = r.fetchall()
    r = cur.execute('SELECT C.credit_card_num FROM Credit_Cards C WHERE C.Owner_email = ?',(email,))
    r4 = r.fetchall()[0][0]
    return [list(r1[0]) + [(r2[0])] + [(r3[0])] + [(r4)]]

def changePassword(email, passw, p1, p2):
    if p1 == p2:
        hp = hl.md5(p1.encode()).hexdigest()
        if checkLogin(email,passw):
            con = sql.connect('database.db')
            cur = con.cursor()
            cur.execute("""UPDATE Users
                        SET password = ?
                        WHERE Users.email = ?""",(hp,email))
            con.commit()
            return 1
        else:
            return -1          
    else:
        return -2

def removeList(id):
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute("""UPDATE Product_Listing
                SET Status = 0
                WHERE Listing_ID = ?""",(id,))
    con.commit()

def addList(id):
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute("""UPDATE Product_Listing
                SET Status = 1
                WHERE Listing_ID = ?""",(id,))
    con.commit()

def getCats():
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT category_name, parent_category FROM Categories")
    r = cur.fetchall()
    def numParents(cat):
        num = -1
        cur = cat
        while cur != "Root":
            cur = [x[1] for x in r if x[0] == cur][0]
            num += 1
        return num

    def orderedDict(cat,dicts):
        if cat != "Root":
            dicts[cat] = ([x[1] for x in r if x[0] == cat][0],numParents(cat))
        for i in r:
            if i[1] == cat:
                orderedDict(i[0],dicts)

    res = {}
    orderedDict("Root",res)
    return res

def getResults(search):
    con = sql.connect('database.db')
    cur = con.cursor()
    cat_list = [search]
    result_list = []
    c = getCats()
    clist =[(x,c[x][0]) for x in c]
    for i in cat_list:
        for j in clist:
            if j[1] in cat_list and j[1] != "Root" and j[0] not in cat_list:
                cat_list.append(j[0])

    for i in cat_list:
        cur.execute("SELECT Product_Name, Product_Description, Category, Price, Listing_ID, Quantity, Status FROM Product_Listing P WHERE P.Category = ?",(i,))
        result_list += cur.fetchall()
    return result_list

def getSellerLists(email):
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Product_Listing P WHERE P.Seller_Email = ?",(email,))
    r = cur.fetchall()
    return r

def publishList(email,cat,title,name,desc,price,qty):
    price = "$" + str(price)
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT MAX(Listing_ID) FROM Product_Listing")
    id = cur.fetchall()[0][0]+1
    time = datetime.now().isoformat(timespec="seconds")
    cur.execute("INSERT INTO Product_Listing VALUES (?,?,?,?,?,?,?,?,?,?)",(email,id,cat,title,name,desc,price,qty,1,time))
    con.commit()


def prodInfo(id):
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Product_Listing P WHERE P.Listing_id = ?",(id,))
    return cur.fetchall()[0]

def placeOrder(prod,qty):
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute("""UPDATE Product_Listing
                SET Quantity = Quantity - ?
                WHERE Listing_ID = ?""",(qty,prod[1]))
    cur.execute("""UPDATE SELLERS
                SET balance = balance + ?
                WHERE email = ?""",(int(prod[6][1:].replace(',','')) * qty,prod[0]))
    con.commit()

    
if __name__ == "__main__":
    app.run(debug=True)


