from typing import Dict, Optional, List, Set, Union

from src.compiler.translator.models import ForthFunction, Instructions


class FunctionLibrary:
    def __init__(self, allow_redefine=False):
        self.__allow_redefine = allow_redefine
        self.__functions: Dict[str, ForthFunction] = {}
        self.__cur_mem_pos = 0

    """SETTERS"""

    def __setitem__(self, name: str, body: Union[ForthFunction, Instructions]):
        if name in self and not self.__allow_redefine:
            raise Exception(f"Function {name} redefined")

        if not isinstance(body, ForthFunction):
            self.add_inl(name, body)
            return

        self.__functions[name] = body

    def __iadd__(self, other: 'FunctionLibrary'):
        if isinstance(other, FunctionLibrary):
            for f in other:
                self[f.name] = f
        return self

    def add_ext(self, name: str, code: Instructions):
        self.__functions[name] = ForthFunction.external(name, self.__cur_mem_pos, code)
        self.__cur_mem_pos += self[name].size_slots

    def add_inl(self, name: str, code: Instructions):
        self.__functions[name] = ForthFunction.inline(name, code)

    """GETTERS"""

    def __getitem__(self, name: str) -> Optional[ForthFunction]:
        return self.__functions.get(name, None)

    def __len__(self):
        return len(self.__functions)

    def __contains__(self, item: str) -> bool:
        return item in self.__functions

    def __iter__(self):
        return self.__functions.values().__iter__()

    """OUTPUT"""

    def to_memory(self, usages: Optional[Set[str]] = None) -> List[ForthFunction]:
        return [f for name, f in self.__functions.items()
                if not f.is_inline and (not usages or f.name in usages)]
