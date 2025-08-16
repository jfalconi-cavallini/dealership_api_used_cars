from marshmallow import Schema, fields

class CarSchema(Schema):
    id = fields.Int(dump_only=True)
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year = fields.Int(required=True)
    price = fields.Float(required=True)
    mileage = fields.Int(load_default=0)  # default 0 if not provided
    status = fields.Str(load_default='available')
    vin = fields.Str()
    image_url = fields.Str()
    link = fields.Str()
    exterior_color = fields.Str()
    interior_color = fields.Str()
