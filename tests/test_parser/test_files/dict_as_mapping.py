from typing import List
from typing import Mapping
from typing import Set
from typing import Tuple
from typing import Union

NewClassList = List[float]

NewClassTuple = Tuple[float, int]

NewClassList_0 = List[str]

NewClassDict = Mapping[str, float]

NewClassSet = Set[str]

NewClassList_1 = List[Union[int, str]]

NewClassTuple_0 = Tuple[int, str]

NewClassDict_0 = Mapping[str, str]

NewClass = Mapping[str, Union[NewClassDict, NewClassDict_0, NewClassList, NewClassList_0, NewClassList_1, NewClassSet, NewClassTuple, NewClassTuple_0, int, str]]