from datetime import datetime

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
        ArticleSchema,
        many=True,
        required=True,
        validate=validate.Length(min=1, max=10),
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
        assert schema._toplevel_field in errors
        assert errors[schema._toplevel_field][0] == "Length must be between 1 and 10."

    def test_validate_too_long_list(self) -> None:
        schema = ArticlesSchema()
        errors = schema.validate(
            [
                {
                    "id": i,
                    "timestamp": datetime.now().isoformat(),
                    "author": f"author_{i}",
                    "text": "qweqwertyasdg",
                }
                for i in range(100)
            ]
        )
        assert errors
        assert schema._toplevel_field in errors
        assert errors[schema._toplevel_field][0] == "Length must be between 1 and 10."

    def test_validate_broken_item(self) -> None:
        schema = ArticlesSchema()
        errors = schema.validate(
            [
                {
                    "id": 1,
                    "timestamp": datetime.now().isoformat(),
                    "author": "",
                    "text": "qweqwertyasdg",
                }
            ]
        )
        assert errors
        assert schema._toplevel_field in errors
        assert errors[schema._toplevel_field][0] == {
            "author": ["Length must be between 2 and 64."]
        }

    def test_validate_works(self) -> None:
        schema = ArticlesSchema()
        errors = schema.validate(
            [
                {
                    "id": 1,
                    "timestamp": datetime.now().isoformat(),
                    "author": "author",
                    "text": "qweqwertyasdg",
                }
            ]
        )
        assert not errors

    def test_load(self) -> None:
        schema = ArticlesSchema()
        data = schema.load(
            [
                {
                    "id": 1,
                    "timestamp": datetime.now().isoformat(),
                    "author": "author",
                    "text": "qweqwertyasdg",
                }
            ]
        )
        assert isinstance(data, list)
        assert len(data) == 1
        assert isinstance(data[0]["timestamp"], datetime)
