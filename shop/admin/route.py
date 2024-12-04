from shop import app,bcrypt,db
from flask import render_template,session,flash,redirect,url_for,request
from .forms import RegisterUser,LoginAdmin
from .models import Register
from flask_login import login_user,login_required,logout_user

@app.route('/admin/register',methods=['POST','GET'])
def register():
    form=RegisterUser()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        name=form.name.data
        username=form.username.data
        email=form.email.data
        password=form.password.data
        register=Register(name=name,username=username,email=email,password=hashed_password)
        db.session.add(register)
        db.session.commit()
        flash('Account register successfully','success')
    else:
        if form.errors:
            print('form errors:',form.errors)
        
    return render_template('/admin/register.html',form=form)


@app.route('/admin/login',methods=['POST','GET'])
def admin_login():
    form=LoginAdmin()
    if form.validate_on_submit():
        user=Register.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                session['username']=user.username
                flash('Login Successfully','success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Wrong Password Try again','danger')
        else:
            flash('That user does not exist','danger')
    return render_template('/admin/login.html',form=form)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('/admin/show.html')


@app.route('/admin/profile')
@login_required
def admin_profile():
    return render_template('/admin/profile.html')

@app.route('/admin/edit_profile/<int:id>',methods=['POST','GET'])
def edit_profile(id):
    register=Register.query.get_or_404(id)
    form=RegisterUser()
    if request.method=='POST':
        register.name=form.name.data
        register.username=form.username.data
        db.session.commit()
        flash('Account Updated Successfully','success')
    elif request.method=='GET':
        form.name.data=register.name
        form.username.data=register.username

    return render_template('/admin/edit_profile.html',form=form)


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

