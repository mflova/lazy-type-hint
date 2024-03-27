from dynamic_pyi_generator.utils.ordered_set import OrderedSet


def test_ordered_set() -> None:
    # Create an instance of OrderedSet
    ordered_set = OrderedSet()

    # Add elements to the ordered set
    ordered_set.add(1)
    ordered_set.add(2)
    ordered_set.add(3)

    # Check the elements as a tuple
    assert ordered_set.as_tuple() == (1, 2, 3)

    # Check the elements as a list
    assert ordered_set.as_list() == [1, 2, 3]

    # Add a duplicate element
    ordered_set.add(2)

    # Check that the duplicate element is not added again
    assert ordered_set.as_tuple() == (1, 2, 3)
    assert ordered_set.as_list() == [1, 2, 3]
