from marshmallow import Schema, fields
from marshmallow.validate import Length

from apis.models.model import ma


class CreateVesselInputSchema(Schema):
    code = fields.Str(required=True, validate=Length(1, 8))

class CreateEquipmentInputSchema(Schema):
    vessel_code = fields.Str(required=True, validate=Length(1, 8))
    code = fields.Str(required=True, validate=Length(1, 8))
    name = fields.Str(required=True, validate=Length(1, 256))
    location = fields.Str(required=True, validate=Length(1, 256))

class UpdateEquipmentInputSchema(Schema):
    codes = fields.List(
        fields.Str(
            validate=Length(1, 8)
        ),
        validate=Length(1, 10_000), 
        required=True
    )

class ActiveEquipmentInputSchema(Schema):
    vessel_code = fields.Str(required=True, validate=Length(1, 8))

class EquipmentOutputSchema(ma.Schema):
    class Meta:
        fields = 'id vessel_id name code location'.split()

class CreateOperationOrderInputSchema(Schema):
    code = fields.Str(required=True, validate=Length(1, 8))
    type = fields.Str(required=True, validate=Length(1, 64))
    cost = fields.Decimal(required=True, places=2)

class TotalCostOperationInputSchema(Schema):
    code = fields.Str(required=False, validate=Length(1, 8))
    name = fields.Str(required=False, validate=Length(1, 256))