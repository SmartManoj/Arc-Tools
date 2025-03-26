from arc_tools.extract_knowledge import extract_knowledge_lshape
def test_extract_knowledge_lshape():
    a = [
        [5, 6, 1, 0],
        [7, 8, 1, 0],
        [5, 6, 1, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0]
    ]
    b = [
        [5, 6, 9, 1, 0, 0],
        [7, 8, 9, 1, 0, 0],
        [1, 1, 1, 1, 0, 0],
        [0, 0, 9, 0, 0, 0]
    ]
    c = [
        [5, 6, 1, 0, 0, 0],
        [7, 8, 1, 0, 0, 0],
        [1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0]
    ]
    # extract the content inside the L shape ;
    expected_output_a = [[5,6],[7,8],[5,6]] 
    expected_output_b = [[5,6,9],[7,8,9]] 
    expected_output_c = [[5,6],[7,8]]

    assert extract_knowledge_lshape(a) == expected_output_a, "Test case failed"

    assert extract_knowledge_lshape(b) == expected_output_b, "Test case failed"

    assert extract_knowledge_lshape(c) == expected_output_c, "Test case failed"


if __name__ == "__main__":
    test_extract_knowledge_lshape()
    print("All test cases passed")
