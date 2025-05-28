from __future__ import annotations
from typing import TYPE_CHECKING, Dict, cast
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin

from ._mixin import DataColumnMixin

if TYPE_CHECKING:
    from .data_view import DataView


class DataColumn(DataColumnMixin, ObservableMixin, ElementBindingMixin):
    def __init__(self, data_view: DataView, field: str) -> None:
        self._data_view = data_view
        self.__field = field

    @property
    def field(self) -> str:
        return self.__field

    def get_element_ref(self):
        return self._data_view._data_source_element._ele_ref

    def get_data_view(self) -> DataView:
        return self._data_view

    def _to_element_binding_config(self) -> Dict:
        return cast(
            ElementBindingMixin, self._data_view.flat_values()
        )._to_element_binding_config()

    def _to_observable_config(self):
        return cast(
            ObservableMixin, self._data_view.flat_values()
        )._to_observable_config()


class DataViewColumn(DataColumnMixin, ObservableMixin, ElementBindingMixin):
    def __init__(self, source_name: str, field: str) -> None:
        self._source_name = source_name
        self.__field = field

    @property
    def field(self) -> str:
        return self.__field

    @property
    def source_name(self) -> str:
        return self._source_name

    def _to_element_binding_config(self) -> Dict:
        raise NotImplementedError

    def _to_observable_config(self):
        raise NotImplementedError

    def get_element_ref(self) -> ElementRef:
        raise NotImplementedError

    def get_data_view(self) -> DataView:
        raise NotImplementedError

    def get_source_type(self):
        return "view"

    # def get_element_ref(self):
    #     return self._data_view._data_source_element._ele_ref

    # def get_data_view(self) -> DataView:
    #     return self._data_view

    # def _to_element_binding_config(self) -> Dict:
    #     return cast(
    #         ElementBindingMixin, self._data_view.flat_values()
    #     )._to_element_binding_config()

    # def _to_observable_config(self):
    #     return cast(
    #         ObservableMixin, self._data_view.flat_values()
    #     )._to_observable_config()
