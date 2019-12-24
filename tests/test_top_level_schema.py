import pytest
from marshmallow import Schema, fields, validate

from marshmallow_toplevel import TopLevelSchema


class ArticleSchema(Schema):
    id = fields.Int(required=True, strict=True)
    timestamp = fields.DateTime(required=True)
    author = fields.Str(required=True, validate=validate.Length(min=2, max=64))
    text = fields.Str(required=True, validate=validate.Length(min=10, max=100_000))


class ArticlesSchema(TopLevelSchema):
    _toplevel = fields.Nested(
        ArticleSchema, many=True, required=True, validate=validate.Length(min=1, max=10)
    )


class TestTopLevelSchema:
    def test_doesnt_allow_empty(self) -> None:
        class WrongSchema(TopLevelSchema):
            pass

        with pytest.raises(
            TypeError,
            match="TopLevelSchema should have exactly one field with name: _toplevel",
        ):
            WrongSchema()

    def test_doesnt_allow_wrong_name(self) -> None:
        class WrongSchema(TopLevelSchema):
            _toplevel_field = "_toplevel"

            wrong_name = fields.List(
                fields.Int(strict=True, validate=validate.Range(min=0, max=100))
            )

        with pytest.raises(
            TypeError,
            match="The only field in TopLevelSchema should have name: _toplevel",
        ):
            WrongSchema()

    def test_doesnt_allow_any_other_fields(self) -> None:
        class WrongSchema(TopLevelSchema):
            _toplevel = fields.List(
                fields.Int(strict=True, validate=validate.Range(min=0, max=100))
            )
            other_field = fields.Bool()

        with pytest.raises(
            TypeError, match="TopLevelSchema can contain only one field"
        ):
            WrongSchema()

    def test_validate_empty_list(self) -> None:
        schema = ArticlesSchema()
        errors = schema.validate([])
        assert errors
