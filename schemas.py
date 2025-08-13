from marshmallow import Schema, fields

class CarSchema(Schema):
    id = fields.Int(dump_only=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year = fields.Int(required=True)
    price = fields.Float(required=True)
    mileage = fields.Int()
    status = fields.Str()
    vin = fields.Str()
    image_url = fields.Str()
    link = fields.Str()
