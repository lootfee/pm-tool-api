from marshmallow import validate, validates, validates_schema, \
    ValidationError, post_dump, post_load
from app import ma
from app.database import Database
from app.auth import token_auth
from app.models import User

paginated_schema_cache = {}


class EmptySchema(ma.Schema):
    pass


class DateTimePaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.DateTime(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')


class StringPaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.String(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')


def PaginatedCollection(schema, pagination_schema=StringPaginationSchema):
    if schema in paginated_schema_cache:
        return paginated_schema_cache[schema]

    class PaginatedSchema(ma.Schema):
        class Meta:
            ordered = True

        pagination = ma.Nested(pagination_schema)
        data = ma.Nested(schema, many=True)

    PaginatedSchema.__name__ = 'Paginated{}'.format(schema.__class__.__name__)
    paginated_schema_cache[schema] = PaginatedSchema
    return PaginatedSchema


class UserSchema(ma.Schema):   
    print('schema')     
    id = ma.String(dump_only=True)
    name = ma.String(required=True,
                             validate=validate.Length(min=3, max=64))
    email = ma.String(required=True, validate=[validate.Length(max=120),
                                                   validate.Email()])
    password = ma.String(required=True, load_only=True,
                         validate=validate.Length(min=8))

    @validates('name')
    def validate_name(self, value):
        if not value[0].isalpha():
            raise ValidationError('Username must start with a letter')
        user = token_auth.current_user()
        old_username = user.username if user else None
        users_db = Database('users')
        if value != old_username and users_db.load_one({'name': value}):
            raise ValidationError('Use a different username.')

    @validates('email')
    def validate_email(self, value):
        user = token_auth.current_user()
        old_email = user.email if user else None
        users_db = Database('users')
        if value != old_email and users_db.load_one({'email': value}):
            raise ValidationError('Use a different email.')
        
    @post_load
    def make_user(self, data, **kwargs):
        print('load data')
        print(data)
        return User(**data)

    # @post_dump
    # def fix_datetimes(self, data, **kwargs):
    #     data['first_seen'] += 'Z'
    #     data['last_seen'] += 'Z'
    #     return data


class UpdateUserSchema(UserSchema):
    old_password = ma.String(load_only=True, validate=validate.Length(min=3))

    @validates('old_password')
    def validate_old_password(self, value):
        if not token_auth.current_user().verify_password(value):
            raise ValidationError('Password is incorrect')



class TokenSchema(ma.Schema):
    class Meta:
        ordered = True

    access_token = ma.String(required=True)
    refresh_token = ma.String()


class PasswordResetRequestSchema(ma.Schema):
    class Meta:
        ordered = True

    email = ma.String(required=True, validate=[validate.Length(max=120),
                                               validate.Email()])


class PasswordResetSchema(ma.Schema):
    class Meta:
        ordered = True

    token = ma.String(required=True)
    new_password = ma.String(required=True, validate=validate.Length(min=3))
