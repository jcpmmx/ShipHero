# coding=utf-8


from enum import Enum, IntEnum, auto


class Priority(IntEnum):
    """
    Enum that represents all possible priority options: from 1 (top priority) to 5 (least priority).
    """
    ONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()

    @classmethod
    def choices(cls):
        return [e.value for e in cls]


class BoxType(Enum):
    """
    Enum that represents all possible box type options that can be used in shipment options.
    """
    SMALL = 'small'
    MEDIUM = 'medium'
    BIG = 'big'

    @classmethod
    def choices(cls):
        return [e.value for e in cls]