from enum import Enum, IntEnum


class OpcodeGroupEnum(IntEnum):
    pass


class OpcodeEnum(Enum):
    @property
    def group(self) -> OpcodeGroupEnum:
        return self.value[0]

    @property
    def alt(self) -> int:
        return self.value[1]

    @property
    def identifier(self) -> int:
        return self.alt | (self.group << 8)

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        if not last_values:
            raise ValueError(
                "In OpcodeEnum each group should start with explicitly defined (group,alt)"
            )
        grp, alt = last_values[-1]
        return grp, alt + 1

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return str(self)
