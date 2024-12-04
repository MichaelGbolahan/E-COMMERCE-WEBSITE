from shop import app,bcrypt,db
from flask import render_template,session,flash,redirect,url_for,request,make_response
from flask_login import login_required,current_user
from shop.products.models import Addproduct
from shop.products.models import Brand
from shop.products.models import Category
from shop.customer.models import RegisterCustomer
from .models import CustomerOrder
import secrets
import pdfkit
import stripe

publishable_key= 'pk_test_51Q4jySI3MbFSz1adXLSMUT1cNoOpBHRf6TKDdV3yh1SnofULE4SyPsmE1slDqAWJsS9PtcIJ7BpQLlqUCSo8I32200m66AYL8e'

stripe.api_key= 'sk_test_51Q4jySI3MbFSz1ad5qT5bXEgiU6eUDXewHr9L9cuW6KMbVJFiVMDtoXeHxRGSYbyVe5RezFmfPLEEEbqmHL080EJ00WM0WJ7Kj'

@app.route('/payment',methods=['POST'])
def payment():
    invoice=request.form.get('invoice')
    amount=request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description='Shopnow',
        amount=amount,
        currency='usd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status='Paid'
    db.session.commit()
    return redirect(url_for('thanks'))


@app.route('/thanks')
def thanks():
    return render_template('/customer/thank.html')

def MagerDicts(dict1,dict2):
    if isinstance(dict1,list) and isinstance(dict2,list):
        return dict1 + dict2
    elif isinstance(dict1,dict) and isinstance(dict2,dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

def get_brands():
    brands = Brand.query.join(Addproduct,(Brand.id==Addproduct.brand_id)).all()
    return brands

def get_categories():
    categories = Category.query.join(Addproduct,(Category.id==Addproduct.category_id)).all()
    return categories

@app.route('/addcart',methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        colors = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()
        if request.method=='POST':
            DictItems = {product_id:{'name':product.name,'price':float(product.price),'discount':float(product.discount),'color':colors,'quantity':quantity,'image':product.image_1,'colors':product.colors}}

            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key,item in session['Shoppingcart'].items():
                        if int(key)==int(product_id):
                            session.modified=True
                            item['quantity']+=1
                else:
                    session['Shoppingcart']=MagerDicts(session['Shoppingcart'],DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)

@app.route('/carts')
def getCarts():
    if 'Shoppingcart' not in session or len(session['Shoppingcart'])<=0:
        return redirect(url_for('index'))
        
    subtotal = 0
    grandtotal = 0
    tax = 0
    for key, product in session['Shoppingcart'].items():
        price = float(product['price'])
        quantity = int(product['quantity'])
        discount = (product['discount'] / 100) * price
        subtotal += price * quantity
        subtotal -= discount
        tax = round(0.06 * subtotal, 2)  # 6% tax calculation
        grandtotal = round(1.06 * subtotal, 2)  # Including tax in grand total
    
    return render_template('products/carts.html', tax=tax, grandtotal=grandtotal,brands=get_brands(),categories=get_categories())


@app.route('/updatecart/<int:code>',methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart'])<=0:
        return redirect(url_for('home'))
    if request.method=='POST':
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified=True
            for key,item in session['Shoppingcart'].items():
                if int(key)==code:
                    item['quantity']=quantity
                    item['color']=color
                    flash('Item is updated')
                    return redirect(url_for('getCarts'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCarts'))


@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart'])<=0:
        return redirect(url_for('home'))

    try:
        session.modified =True
        for key,item in session['Shoppingcart'].items():
            if int(key)==id:
                session['Shoppingcart'].pop(key,None)
                return redirect(url_for('getCarts'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCarts'))

@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart',None)
        return redirect(url_for('index'))
    except Exception as e:
        print(e)



@app.route('/getorder')
def get_order():
    if 'username' not in session:
        flash('please Login first','danger')
        return redirect(url_for('customer_login'))
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully','success')
            return redirect(url_for('orders',invoice=invoice))

        except Exception as e:
            print(e)
            flash('some thing went wrong while getting order','danger')
            return redirect(url_for('getCarts'))


@app.route('/orders/<invoice>')
def orders(invoice):
    if 'username' not in session:
        flash('please Login first','danger')
        return redirect(url_for('customer_login'))
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = RegisterCustomer.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
        tax = float('%.2f' % (.06 * subTotal))
        grandTotal = ('%.2f' % (1.06 * float(subTotal)))

    else:
        return redirect(url_for('customer_login'))
    
    return render_template('customer/order.html', invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders,categories=get_categories(),brands=get_brands())



@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method == 'POST':
            customer = RegisterCustomer.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount'] / 100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = float('%.2f' % (.06 * subTotal))
                grandTotal = float('%.2f' % (1.06 * subTotal))
            
            # Render HTML to be converted into a PDF
            rendered = render_template('/customer/pdf.html', invoice=invoice, tax=tax, grandTotal=grandTotal, customer=customer, orders=orders)
            
            # Path to wkhtmltopdf executable if necessary
            path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
            
            # Generate the PDF from the rendered HTML template
            pdf = pdfkit.from_string(rendered, False, configuration=config)  # Change to from_string to use the rendered HTML

            # Check if PDF generation succeeded
            if pdf:
                response = make_response(pdf)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'inline; filename={invoice}.pdf'
                return response
            else:
                # Handle PDF generation failure
                return "Failed to generate PDF", 500

    return redirect(url_for('orders'))
