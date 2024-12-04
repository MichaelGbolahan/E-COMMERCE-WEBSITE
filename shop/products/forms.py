from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,DecimalField,TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField,FileAllowed


class Addproducts(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    price = DecimalField('Price',validators=[DataRequired()])
    discount = IntegerField('Discount',default=0)
    stock = IntegerField('Stock',validators=[DataRequired()])
    description = TextAreaField('Description',validators=[DataRequired()])
    colors = TextAreaField('Colors',validators=[DataRequired()])
    image_1 = FileField('Image_1',validators=[FileAllowed(['jpg','jpeg','png','gif'])])
    image_2 = FileField('Image_2',validators=[FileAllowed(['jpg','jpeg','png','gif'])])
    image_3 = FileField('Image_3',validators=[FileAllowed(['jpg','jpeg','png','gif'])])