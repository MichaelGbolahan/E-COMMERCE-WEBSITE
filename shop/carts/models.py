from shop import db,login_manager
from datetime import datetime
import  json


class jsonEcodedDict(db.TypeDecorator):
    impl = db.Text
    def process_bind_param(self,value,dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)
    def process_result_value(self,value,dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)

class CustomerOrder(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    invoice = db.Column(db.String(20),unique=True,nullable=False)
    status = db.Column(db.String(20),default='pending',nullable=False)
    customer_id = db.Column(db.Integer,unique=False,nullable=False)
    invoice = db.Column(db.String(20),unique=True,nullable=False)
    date_created = db.Column(db.DateTime(20),default=datetime.utcnow,nullable=False)
    orders = db.Column(jsonEcodedDict)

    def __repr__(self):
        return '<CustomerOrder %r>' % self.invoice