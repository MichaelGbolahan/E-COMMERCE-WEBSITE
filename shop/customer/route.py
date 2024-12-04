from shop import app,bcrypt,db
from flask_login import login_required,login_user
from flask import render_template,flash,session,url_for,redirect
from .forms import CustomerRegistrationForm,LoginCustomer
from .models import RegisterCustomer
from flask_login import logout_user

@app.route('/customer/register',methods=['POST','GET'])
def customer_register():
    form=CustomerRegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        name=form.name.data
        username=form.username.data
        email=form.email.data
        country=form.country.data
        city=form.city.data
        address=form.address.data
        zipcode=form.zipcode.data
        register=RegisterCustomer(name=name,username=username,email=email,password=hashed_password,country=country,city=city,address=address,zipcode=zipcode)
        db.session.add(register)
        db.session.commit()
        flash('Account register successfully','success')
    else:
        if form.errors:
            print('form errors:',form.errors)
    return render_template('/customer/register.html',form=form)


@app.route('/customer/login',methods=['POST','GET'])
def customer_login():
    form=LoginCustomer()
    if form.validate_on_submit():
        user=RegisterCustomer.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                session['username']=user.username
                flash('Login Successfully','success')
                return redirect(url_for('index'))
            else:
                flash('Wrong Password Try again','danger')
        else:
            flash('That user does not exist','danger')
    return render_template('/customer/login.html',form=form)

@app.route('/customer/logout')
def customer_logout():
    if 'username' not in session:
        flash('please Login first','danger')
        return redirect(url_for('customer_login'))
    logout_user()
    return redirect(url_for('index'))