from shop import app,db,photos,search
from flask import render_template,request,session,flash,current_app,url_for,redirect
from flask_login import login_required
from .models import Brand,Category,Addproduct
from .forms import Addproducts
import secrets
import os

def get_brands():
    brands = Brand.query.join(Addproduct,(Brand.id==Addproduct.brand_id)).all()
    return brands

def get_categories():
    categories = Category.query.join(Addproduct,(Category.id==Addproduct.category_id)).all()
    return categories


@app.route('/')
def index():
    page=request.args.get('page',1,type=int)
    adds = Addproduct.query.filter(Addproduct.stock>0).order_by(Addproduct.id.desc()).paginate(page=page,per_page=4)
    return render_template('/products/index.html',adds=adds,categories=get_categories(),brands=get_brands())


@app.route('/result')
def result():
    searchword=request.args.get('q')
    products=Addproduct.query.msearch(searchword,fields=['name','desc'],limit=3)
    return render_template('products/result.html',products=products,brands=get_brands(),categories=get_categories())


@app.route('/single/page/<int:id>')
def single_page(id):
    product=Addproduct.query.get_or_404(id)
    return render_template('/products/single_page.html',product=product,categories=get_categories(),brands=get_brands())


@app.route('/products/addbrand',methods=['POST','GET'])
@login_required
def add_brand():
    if request.method=='POST':
        name=request.form.get('brand')
        name=Brand(name=name)
        db.session.add(name)
        db.session.commit()
        flash('Brand Added Successfully','success')
    return render_template('/products/add_brand.html')

@app.route('/products/viewbrand')
def view_brand():
    brands=Brand.query.all()
    return render_template('/products/view_brand.html',brands=brands)

@app.route('/products/editbrand/<int:id>',methods=['POST','GET'])
@login_required
def edit_brand(id):
    bands=Brand.query.get_or_404(id)
    if request.method=='POST':
        bands.name=request.form.get('brand')
        db.session.commit()
        flash(f'Brand {bands.name} updated successfully','success')
        return redirect(url_for('view_brand'))
    return render_template('/products/edit_brand.html',bands=bands)

@app.route('/products/deletebrand/<int:id>',methods=['POST','GET'])
@login_required
def delete_brand(id):
    delete=Brand.query.get_or_404(id)
    if delete:
        if request.method=='POST':
            db.session.delete(delete)
            db.session.commit()
            flash(f'Brand {delete.name} has been deleted successfully','success')
            return redirect(url_for('view_brand'))
    return render_template('/products/view_brand.html')

@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page',1,type=int)
    get_b = Brand.query.filter_by(id=id).first_or_404()
    brand = Addproduct.query.filter_by(brand=get_b).paginate(page=page,per_page=4)
    return render_template('products/index.html',brand=brand,brands=get_brands(),categories=get_categories(),get_b=get_b)



@app.route('/products/addcategory',methods=['POST','GET'])
@login_required
def add_category():
    if request.method=='POST':
        category=request.form.get('category')
        category=Category(name=category)
        db.session.add(category)
        db.session.commit()
        flash('Category Added Successfully','success')
    return render_template('/products/add_category.html')


@app.route('/products/viewcategory')
@login_required
def view_category():
    categories=Category.query.all()
    return render_template('/products/view_category.html',categories=categories)

@app.route('/products/editcategory/<int:id>',methods=['POST','GET'])
@login_required
def edit_category(id):
    cat=Category.query.get_or_404(id)
    if request.method=='POST':
        cat.name=request.form.get('category')
        db.session.commit()
        flash(f'Category {cat.name} updated successfully','success')
        return redirect(url_for('view_category'))
    return render_template('/products/edit_category.html',cat=cat)


@app.route('/products/deletecategory/<int:id>',methods=['POST','GET'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check for linked products before attempting to delete the category
    linked_products = Addproduct.query.filter_by(category_id=id).count()

    if linked_products > 0:
        # There are products linked to this category, so do not delete
        flash(f'The category {category.name} cannot be deleted because it is linked to existing products.', 'warning')
        return redirect(url_for('view_category'))
    
    # Proceed with deletion if no linked products
    if request.method == 'POST':
        try:
            db.session.delete(category)
            db.session.commit()
            flash(f'Category {category.name} has been deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting category: {str(e)}', 'danger')

    return redirect(url_for('view_category'))


@app.route('/categories/<int:id>')
def get_category(id):
    page=request.args.get('page',1,type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page,per_page=4)
    return render_template('products/index.html',get_cat_prod=get_cat_prod,categories=get_categories(),brands=get_brands(),get_cat=get_cat)




@app.route('/products/addproduct',methods=['POST','GET'])
@login_required
def add_product():
    form=Addproducts()
    brands=Brand.query.all()
    categories=Category.query.all()
    if form.validate_on_submit and request.method=='POST':
        name=form.name.data
        price=form.price.data
        discount=form.discount.data
        stock=form.stock.data
        category=request.form.get('category')
        brand=request.form.get('brand')
        colors=form.colors.data
        desc=form.description.data
        image_1=photos.save(request.files.get('image_1'),name=secrets.token_hex(10)+'.')
        image_2=photos.save(request.files.get('image_2'),name=secrets.token_hex(10)+'.')
        image_3=photos.save(request.files.get('image_3'),name=secrets.token_hex(10)+'.')
        addpro=Addproduct(name=name,price=price,discount=discount,stock=stock,brand_id=brand,category_id=category,colors=colors,desc=desc,image_1=image_1,image_2=image_2,image_3=image_3)
        db.session.add(addpro)
        db.session.commit()
        flash('Product Added successfully','success')


    return render_template('/products/add_product.html',form=form,brands=brands,categories=categories)


@app.route('/products/viewproduct')
@login_required
def view_product():
    addpro=Addproduct.query.all()
    return render_template('/products/view_product.html',addpro=addpro)

@app.route('/products/editproduct/<int:id>',methods=['POST','GET'])
@login_required
def edit_product(id):
    categories=Category.query.all()
    brands=Brand.query.all()
    addpro=Addproduct.query.get_or_404(id)
    category=request.form.get('category')
    brand=request.form.get('brand')
    form=Addproducts(request.form)
    if  request.method=='POST':
        addpro.name=form.name.data
        addpro.price=form.price.data
        addpro.discount=form.discount.data
        addpro.stock=form.stock.data
        addpro.colors=form.colors.data
        addpro.desc=form.description.data
        addpro.category_id=category
        addpro.brand_id=brand
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path,'static/images/' + addpro.image_1))
                addpro.image_1 = photos.save(request.files.get('image_1'),name=secrets.token_hex(10) + '.')
            except:
                addpro.image_1 = photos.save(request.files.get('image_1'),name=secrets.token_hex(10) + '.')
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path,'static/images/' + addpro.image_2))
                addpro.image_2 = photos.save(request.files.get('image_2'),name=secrets.token_hex(10) + '.')
            except:
                addpro.image_2 = photos.save(request.files.get('image_2'),name=secrets.token_hex(10) + '.')
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path,'static/images/' + addpro.image_3))
                addpro.image_3 = photos.save(request.files.get('image_3'),name=secrets.token_hex(10) + '.')
            except:
                addpro.image_3 = photos.save(request.files.get('image_3'),name=secrets.token_hex(10) + '.')
        db.session.commit()
    elif request.method=='GET':
        form.name.data=addpro.name
        form.price.data=addpro.price
        form.discount.data=addpro.discount
        form.stock.data=addpro.stock
        form.colors.data=addpro.colors
        form.description.data=addpro.desc
    return render_template('/products/edit_product.html',form=form,addpro=addpro,categories=categories,brands=brands)

@app.route('/products/deleteproduct/<int:id>',methods=['POST','GET'])
@login_required
def delete_product(id):
    addpro=Addproduct.query.get_or_404(id)
    if addpro:
        if request.method=='POST':
            if request.files.get('image_1'):
                try:
                    os.unlink(os.path.join(current_app.root_path,'static/images/' + addpro.image_1))
                    os.unlink(os.path.join(current_app.root_path,'static/images/' + addpro.image_2))
                    os.unlink(os.path.join(current_app.root_path,'static/images/' + addpro.image_3))
                except Exception as e:
                    print(e)
            db.session.delete(addpro)
            db.session.commit()
            return redirect(url_for('view_product'))
    return render_template('/products/view_product.html')

