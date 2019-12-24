import typing

from marshmallow import Schema, types


class TopLevelSchema(Schema):
    _toplevel_field = "_toplevel"

    def __init__(
        self,
        *,
        only: types.StrSequenceOrSet = None,
        exclude: types.StrSequenceOrSet = (),
        many: bool = False,
        context: typing.Dict = None,
        load_only: types.StrSequenceOrSet = (),
        dump_only: types.StrSequenceOrSet = (),
        partial: typing.Union[bool, types.StrSequenceOrSet] = False,
        unknown: str = None,
    ):
        super().__init__(
            only=only,
            exclude=exclude,
            many=many,
            context=context,
            load_only=load_only,
            dump_only=dump_only,
            partial=partial,
            unknown=unknown,
        )
        if not self.declared_fields:
            raise TypeError(
                f"TopLevelSchema should have exactly one field with name: "
                f"{self._toplevel_field}"
            )
        if len(self.declared_fields) > 1:
            raise TypeError("TopLevelSchema can contain only one field")
        field = list(self.declared_fields.keys())[0]
        if field != self._toplevel_field:
            raise TypeError(
                f"The only field in TopLevelSchema should have name: "
                f""
                f"{self._toplevel_field}"
            )

    def validate(
        self,
        data: typing.Union[typing.Mapping, typing.Sequence],
        *,
        many: bool = None,
        partial: typing.Union[bool, types.StrSequenceOrSet] = None,
    ) -> typing.Dict[str, typing.List[str]]:
        data = {self._toplevel_field: data}
        return super().validate(data, many=many, partial=partial)
