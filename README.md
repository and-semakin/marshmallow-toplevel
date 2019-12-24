# marshmallow-toplevel
Load and validate top-level lists with all the power of
[marshmallow](https://github.com/marshmallow-code/marshmallow).

## Installation

```sh
pip install marshmallow-toplevel
```

## Usage

```python
from marshmallow import fields
from marshmallow_toplevel import TopLevelSchema


class BatchOfSomething(TopLevelSchema):
    _toplevel = fields.Nested(
        SomethingSchema,
        required=True,
        many=True,
        validate=any_validation_logic_applied_to_list
    )
```

## Rationale

Imagine that you have an API endpoint (or any other program that
accepts user input), which is intended to accept multiple blog articles
and save them to a database. Semantically, your data is a list of dictionaries:

```python
[
    {"id": 1, "title": "Hello World!"},
    {"id": 2, "title": "Yet another awesome article."},
    ...
]
```

You describe article object schema and put constraints on your data:

```python
from marshmallow import Schema, fields, validate


class ArticleSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=2, max=256))
```

But you also want to put some constraints onto outer list itself, for example,
you want it to have length between 1 and 10. How do you describe it in
terms of `marshmallow`?

### Obvious solution: nest your data

```python
class BatchOfArticles(Schema):
    articles = fields.Nested(
        ArticleSchema,
        required=True,
        many=True,
        validate=validate.Length(1, 10)
    )
```

But now a client have to send data this way, with this extra dictionary around:

```python
{
    "articles": [
        {"id": 1, "title": "Hello World!"},
        {"id": 2, "title": "Yet another awesome article."},
        ...
    ]
}
```

It makes your API not so beautiful and user-friendly.

### Good solution: use marshmallow-toplevel

With `marshmallow-toplevel` you can describe you data this way:

```python
from marshmallow_toplevel import TopLevelSchema


class BatchOfArticles(TopLevelSchema):
    _toplevel = fields.Nested(
        ArticleSchema,
        required=True,
        many=True,
        validate=validate.Length(1, 10)
    )
```

Notice that schema inherits from `TopLevelSchema` and uses this
special `_toplevel` key. It means that the field under this key
describes top level object. You can define any constrains that
you can define in `marshmallow` and it will just work:

```python
schema = BatchOfArticles()

# validation should fail
errors = schema.validate([])
assert errors  # length < 1
errors = schema.validate([{"id": i, "title": "title"} for i in range(100)])
assert errors  # length > 10

# validation should succeed
errors = schema.validate([{"id": i, "title": "title"} for i in range(5)])
assert not errors
```

You can also use `load` for this schema as usual:

```python
data = schema.load([{"id": "10", "title": "wow!"}])
print(data)
# [{"id": 10, "title": "wow!"}]
```

Now a client can send data as a list without redundancy.
