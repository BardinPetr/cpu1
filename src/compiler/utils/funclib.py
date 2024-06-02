from typing import Dict, Optional, List, Set, Union

from compiler.utils.models import ForthFunction, Instructions


class FunctionLibrary:
    def __init__(self, allow_redefine=False):
        self.__function_predef_lock = False
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

    def __iadd__(self, other: "FunctionLibrary"):
        if isinstance(other, FunctionLibrary):
            for f in other:
                self[f.name] = f
        return self

    def add_ext(self, name: str, code: Instructions):
        if self.__function_predef_lock:
            raise RuntimeError("Not called add_ext_end after add_ext_begin")
        self.__functions[name] = ForthFunction.external(name, self.__cur_mem_pos, code)
        self.__cur_mem_pos += self[name].size_slots

    def add_ext_begin(self, name: str):
        """
        Only register name and start pos to preallocate function with stub.
        Should be used with add_ext_end
        """
        self.__function_predef_lock = True
        self.__functions[name] = ForthFunction.external(name, self.__cur_mem_pos, [])

    def add_ext_end(self, name: str, code: Instructions):
        """
        Replace temporary function stub created with add_ext_begin with real function.
        """
        self.__function_predef_lock = False
        del self.__functions[name]
        self.add_ext(name, code)

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
        return [
            f
            for name, f in self.__functions.items()
            if not f.is_inline and (not usages or f.name in usages)
        ]
