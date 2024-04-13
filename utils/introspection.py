"""
Following is an adaptation of myhdl/_misc.py to provide more powerful tree-style introspection
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Iterable, Tuple

import myhdl
from myhdl import Cosimulation, delay
from myhdl._Signal import _Signal
from myhdl._block import _Block
from myhdl._extractHierarchy import _MemInfo
from myhdl._instance import _Instantiator, instance

from utils.colors import Colors
from utils.hdl import hdl_block


@dataclass
class BlockIntrospection:
    name: Optional[str] = None
    type: Optional[str] = None
    modules: Dict[str, _Block] = field(default_factory=dict)
    signals: Dict[str, _Signal] = field(default_factory=dict)
    memories: Dict[str, _MemInfo] = field(default_factory=dict)


# class IntrospectedValue:
#     def __init__(self, sig: _Signal):
#         super().__init__()
#         self.sig = sig
#
#     def __call__(self, *args, **kwargs):
#         return int(self.sig.val)


class IntrospectedMemory:
    def __init__(self, mem: _MemInfo):
        self._cells = mem.mem

    def __getitem__(self, item: int) -> _Signal:
        return self._cells[item]


@dataclass
class IntrospectionTree(BlockIntrospection):
    def __post_init__(self):
        self._children = {
            k: IntrospectionTree.build(v, is_root=False)
            for k, v in self.modules.items()
        }
        self._symbols = {
            **self.signals,
            **{k: IntrospectedMemory(s) for k, s in self.memories.items()},
        }

    def __getattr__(self, item: str):
        if item in self._children:
            return self._children.get(item)
        if item in self._symbols:
            return self._symbols.get(item)
        raise AttributeError(f"Symbol {item} not found in block {self}")

    def __repr__(self):
        return (f"<{self.name}: "
                f"c=[{','.join([str(i) for i in self._children])}]"
                f"; "
                f"s=[{','.join([str(i) for i in self._symbols])}]"
                f">")

    @staticmethod
    def build(blk: _Block, is_root: bool = True) -> 'IntrospectionTree':
        if not hasattr(blk, "introspection"):
            raise ValueError(f"Block {blk.name} should be introspected first")

        # noinspection PyUnresolvedReferences
        base: BlockIntrospection = blk.introspection
        name = base.type if is_root else base.name
        return IntrospectionTree(name, base.type, base.modules, base.signals, base.memories)

    def draw(self, level: int = 0):
        padding = "|  " * level

        if level == 0:
            print(f"\n{'=' * 20}\nTree:")

        print(
            f"{padding}"
            f"{Colors.RED}{Colors.BOLD}-{Colors.END}"
            f"{Colors.GREEN}{Colors.BOLD}{self.type}{Colors.END} as "
            f"{Colors.BLUE}{self.name}{Colors.END}"
            f"{':' if self._children else ''}"
            f"\n{padding} {Colors.PURPLE}sigs{Colors.END}=({', '.join(self._symbols.keys())})"
        )

        for i in sorted(self._children.values(), key=lambda x: str(x)):
            i.draw(level + 1)

        if level == 0:
            print(f"{'=' * 20}\n")


class TraceData:

    def __init__(self):
        self._run = True
        self._labels = []
        self._history: List[List[int]] = []

    def clear(self):
        self._history = []
        self._labels = []

    def set_labels(self, labels: Iterable[str]):
        self._labels = list(labels)

    def as_list(self) -> List[List[int]]:
        return self._history

    def as_list_front(self, front_val: int) -> List[List[int]]:
        return self._history[1 - front_val::2]

    def as_list_joined(self) -> List[Tuple[List[int], List[int]]]:
        return list(zip(self.as_list_front(1), self.as_list_front(0)))

    def as_dict(self) -> List[Dict[str, int]]:
        return [dict(zip(self._labels, i)) for i in self.as_list()]

    def stop(self):
        self._run = False

    def add(self, x: List[int]):
        if self._run:
            self._history.append(x)


@hdl_block
def Trace(clk: _Signal, data: TraceData, watches: Dict[str, _Signal]):
    data.clear()
    data.set_labels(watches.keys())

    def checkpoint():
        data.add([int(tp) for tp in watches.values()])

    @instance
    def pull():
        while True:
            yield clk.posedge
            yield delay(1)
            checkpoint()
            yield clk.negedge
            yield delay(1)
            checkpoint()

    return pull


def _is_hdl_runnable(obj: Any) -> bool:
    if isinstance(obj, (Cosimulation, _Instantiator, _Block)):
        return True
    if isinstance(obj, (list, tuple, set)):
        return all(map(_is_hdl_runnable, obj))
    return False


def _build_block_contents(block_locals: Dict[str, Any]) -> BlockIntrospection:
    data = BlockIntrospection()
    for name, val in block_locals.items():
        match val:
            case _Block():
                data.modules[name] = val
            case _Signal():
                data.signals[name] = val
    return data


def introspect():
    frame = inspect.currentframe()
    frames = inspect.getouterframes(frame)

    # frame of block definition-function at point of calling this function (return introspect())
    instance_call = frames[1]
    block_classname = instance_call.function
    block_locals = instance_call.frame.f_locals

    block_def = _build_block_contents(block_locals)

    # this is a call of block definition-function itself inside _Block.__init__ (which called by decorator)
    block_class_init_call = frames[2]
    block_instance: _Block = block_class_init_call.frame.f_locals['self']

    block_def.type = block_classname
    block_instance.introspection = block_def

    for sub_name, sub in block_def.modules.items():
        if not hasattr(sub, "introspection"):
            raise RuntimeError(f"""
                Block {sub_name} inside {block_classname} wasn't introspected, 
                however all children of {block_classname} should be at the moment.
                That could have happened because you use vanilla instances() or 
                just return submodules from function. Always use introspect(). 
            """)
        # variable names are only available on parent function had been executed till end
        intro: BlockIntrospection = sub.introspection
        intro.name = sub_name
        intro.memories.update(sub.memdict)

    # print(f"Registered {block_classname}")

    # mimic MyHDL instances() and return all submodules that should be evaluated (blocks and functions with decorators)
    return [
        blk
        for name, blk in block_locals.items()
        if _is_hdl_runnable(blk)
    ]


def use():
    myhdl.instances = introspect


# To prevent misuse, as there always should be either all instances() or all introspect()
use()
