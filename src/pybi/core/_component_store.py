from ._types import TComponentId


class ComponentStore:
    def __init__(self):
        self.__counter = -1

    def gen_component_id(self) -> TComponentId:
        self.__counter += 1
        return f"c{self.__counter}"
