from apis.models.model import db


class OperationOrder(db.Model):
    __tablename__ = 'operation_order'

    id = db.Column(db.BigInteger, primary_key=True)
    equipment_id = db.Column(db.BigInteger, db.ForeignKey('equipments.id'))
    type = db.Column(db.String(64))
    cost = db.Column(db.Float(2))
