from typing import List
from typing import Mapping
from typing import Set
from typing import Tuple
from typing import Union

NewClassList = List[float]
NewClassTuple = Tuple[float, int]
NewClassList_0 = List[str]
NewClassSet = Set[str]
NewClassList_1 = List[Union[int, str]]
NewClassTuple_0 = Tuple[int, str]
NewClassDict = Mapping[str, str]
NewClass = Mapping[str, Union[NewClassDict, NewClassList, NewClassList_0, NewClassList_1, NewClassSet, NewClassTuple, NewClassTuple_0, int, str]]