"""Programming assignment for ACT.md software engineering position.

Your task is to implement the function evaluate below to the specification
provided in the documentation string. If the documentation is in any
way ambiguous, please email Patrick Schmid (prschmid@act.md) for clarification.
If you feel that auxiliary helper functions would be helpful, feel free to
write them. You may change anything in this file except you are not permitted
to alter the name or function signature of evaluate().

Although we provide you with some test cases, do not assume that these cover
all corner cases, and we may use a different set of inputs to validate your
solution. We will be looking at your solution both for correctness and for
style.

Best of luck!
"""

# =============================================================================
#
# Implement this function
#
# =============================================================================
import string
import re


def evaluate(m):
    """Evaluate all of the values in the spreadsheet.

    Given a matrix m of arbitrary size, evaluate all of the cells in the
    spreadsheet and return the matrix with everything computed. We will assume
    that columns are denoted using a letter while rows are denoted by numbers.
    E.g "A1" is equivalent to ``m[0][0]`` while "C23" is ``m[22][2]``.

    As such, here are some examples, assume we have the matrix:

        1   2
        3   4

    This, obviously, should just return the same matrix. Now, let's add some
    functions:

        1   =A1
        2   =A2 + 1

    This should evaluate to:

        1   1
        2   3

    Now, let's take this one step further and add in a second level of
    reference:

        1           =A1 + 1
        =B1 + 1     =A2 + B1

    This should evaluate to:

        1   2
        3   5

    If you are given a reference to a cell that has not been defined, you
    should raise a ReferenceError. For example, this should not work:

        1           =A5 + 2
        =B1 + 1     =A2 + 1

    If you find circular references, you should raise a ValueError. For example:

        =B1 + 1     =A1 + 1

    You can assume the following:
        - All "functions" will have = as the first character
        - The only operations that will be performed are +, -, *, /
        - All input numbers will be integers (you may have some floats as a
          result of division, however)
        - Each "function" will only be a direct reference or binary operation.
          I.e. It'll either be something like "=A1" or "=A1 + 1" but not
          "=A1 + 1 + 2"
        - Spaces in "functions" are meaningless. I.e. "=A1 + 1" is the same as
          "=A1+1" or "= A1  +   1"

    :param m: The matrix to be evaluated. Each of the entries in the matrix
              will either be numbers or strings.
    :returns: A matrix of the same dimensions as :attr:`m` with all of the
              functions evaluated. All of the entries in this returned matrix
              should be numeric and not strings.
    :raises:
        :ReferenceError: If a cell is referenced that has not been defined
        :ValueError: If there is a circular reference


    The main idea: at first group cells into two categories:
    category 1: cells that contain a function (list1)
    category 2: cells that do not contain a function (list2)

    1. pop an element A from list2
    2. iterate over elements in list1. if any of the formulas in these elements contain A, replace A with A's value
    3. If that element doesn't have any more excel representations, remove it from list1 and put it in list2
    4. when list2 is empty, we are done. At this point, m is either done or it contains either:
    out of bound elements or circular dependencies.

    """

    function_cells_left_to_evaluate = []
    value_cells_left_to_evaluate = []

    initialize_cells_to_explore(m, value_cells_left_to_evaluate, function_cells_left_to_evaluate)
    evaluate_functions(m, value_cells_left_to_evaluate, function_cells_left_to_evaluate)

    return m


def evaluate_functions(m, value_cells_left_to_evaluate, function_cells_left_to_evaluate):
    """
    :param m:
    :param value_cells_left_to_evaluate:
    :param function_cells_left_to_evaluate:
    :return:
    """
    while len(value_cells_left_to_evaluate) > 0:
        current_cell = value_cells_left_to_evaluate.pop(0)
        replace_current_cell_in_formulas(m, current_cell, value_cells_left_to_evaluate, function_cells_left_to_evaluate)
    if len(function_cells_left_to_evaluate) > 0:
        if has_circular_dependencies(function_cells_left_to_evaluate, m):
            raise ValueError
        raise ReferenceError
    for row_idx in range(len(m)):
        for col_idx in range(len(m[0])):
            m[row_idx][col_idx] = eval(str(m[row_idx][col_idx]))


def has_circular_dependencies(function_cells_left_to_evaluate, m):
    """
    Looks for circular dependencies
    :param function_cells_left_to_evaluate:
    :param m:
    :return:
    """
    dependency_dict = {}
    for cell in function_cells_left_to_evaluate:
        cell_excel_representation = cell_idx_to_excel_representation(cell)
        excel_representations = re.findall("[a-zA-Z]\d\d*", m[cell[0]][cell[1]])
        dependency_dict[cell_excel_representation] = []
        for excel_representation in excel_representations:
            if excel_representation in dependency_dict:
                if cell_excel_representation in dependency_dict[excel_representation]:
                    raise ValueError
            dependency_dict[cell_excel_representation].append(excel_representation)


def replace_current_cell_in_formulas(m, current_cell, value_cells_left_to_evaluate, function_cells_left_to_evaluate):
    """
    Given a cell, we get its excel representation and then we look at cells which contain functions and replace
    the current cell's excel representation with its value
    :param m: matrix
    :param current_cell: the cell we are looking at now, from the matrix
    :param value_cells_left_to_evaluate: cells which do not contain functions, that are still left
    :param function_cells_left_to_evaluate: cells which do contain functions, that are still left
    :return:
    """
    cell_excel_representation = cell_idx_to_excel_representation(current_cell)
    cells_to_remove = []
    for function_cell in function_cells_left_to_evaluate:
        print cell_excel_representation
        print m[function_cell[0]][function_cell[1]].upper()
        if cell_excel_representation in m[function_cell[0]][function_cell[1]].upper():
            m[function_cell[0]][function_cell[1]] = string.replace(m[function_cell[0]][function_cell[1]].upper(),
                cell_excel_representation,
                str(m[current_cell[0]][current_cell[1]]))
            remaining_excel_representations = re.search('[a-zA-Z]', m[function_cell[0]][function_cell[1]])
            if remaining_excel_representations is None:
                m[function_cell[0]][function_cell[1]] = m[function_cell[0]][function_cell[1]][1:]
                value_cells_left_to_evaluate.append(function_cell)
                cells_to_remove.append(function_cell)
    for cell_to_remove in cells_to_remove:
        function_cells_left_to_evaluate.remove(cell_to_remove)


def cell_idx_to_excel_representation(cell):
    """
    Converts index of the cell to its excel representation. For example, if cell is (0,0), it will return A1
    :param cell: cell in the matrix
    :return: excel representation of the cell
    """
    return chr(ord('A') + cell[1]) + str(cell[0] + 1)


def initialize_cells_to_explore(m, initial_value_cells, initial_function_cells):
    """
    :param m: matrix
    :param initial_value_cells: list of cells which do not contain functions
    :param initial_function_cells: list of cells which do contain functions
    :return:
    """
    for row_idx in range(len(m)):
        for col_idx in range(len(m[0])):
            cell = m[row_idx][col_idx]
            if type(cell) is str:
                if is_a_function(cell):
                    initial_function_cells.append((row_idx, col_idx))
                else:
                    m[row_idx][col_idx] = int(cell)
                    initial_value_cells.append((row_idx, col_idx))
            else:
                initial_value_cells.append((row_idx, col_idx))


def is_a_function(cell):
    """
    :param cell: cell in the matrix
    :return: true if the cell contains a function, false otherwise
    """
    return cell[0] == "="

# =============================================================================
#
# Some example inputs and solutions to test against
#
# =============================================================================

m1 = [
    [1, "2"],
    ["3", 4]
]

solution1 = [
    [1, 2],
    [3, 4]
]

m2 = [
    [1, "=A1+1"],
    [3, "=A2+1"]
]

solution2 = [
    [1, 2],
    [3, 4]
]

m3 = [
    [1, "=A1+1", "=A1 + B1"],
    ["=B1", "3", "=C1 + B2"]
]

solution3 = [
    [1, 2, 3],
    [2, 3, 6]
]

m4 = [
    [1, "=A5 + 2"],
    ["=B1 + 1", "=A2 + 1"]
]

m5 = [
    ["=B1 + 1", "=A1 + 1"]
]

m6 = [
    ["=C1+5", "=A3/2", "=c2-1"],
    ["=b3+7", 1, "=B1*4"],
    ["=B2+5", "=a1/5", "=A2-2"]
]

solution6 = [
    [13, 3, 8],
    [16, 1, 9],
    [6, 9, 14]
]


def validate(proposed, actual):
    """Check if the proposed solution is the same as the actual solution.

    Feel free to modify this function as we will be testing your code with
    our copy of this function.

    :param proposed: The proposed solution
    :param actual: The actual solution
    :return: True if they are the same. Else, return False.
    """
    if proposed is None:
        print "Oops! Looks like your proposed result is None."
        return False
    proposed_items = [item for sublist in proposed for item in sublist]
    actual_items = [item for sublist in actual for item in sublist]
    if len(proposed_items) != len(actual_items):
        print "Oops! There don't seem to be the same number of elements."
        return False
    if proposed_items != actual_items:
        print "Oops! Looks like your proposed solution is not right..."
        return False
    return True


# =============================================================================
#
# A simple main function for you to run. You should be able to test your
# implementation by simply running this module. E.g.
# python spreadsheet.py
#
# =============================================================================

if __name__ == '__main__':
    """The main entry point for this module.

    The main entry point for the function that runs a couple tests to validate
    the implementation of evaluate().
    """

    # The number of test cases that are correct
    correct = 0

    print "Test 1."
    if validate(evaluate(m1), solution1):
        print "    OK."
        correct += 1

    print "Test 2."
    if validate(evaluate(m2), solution2):
        print "    OK."
        correct += 1

    print "Test 3."
    if validate(evaluate(m3), solution3):
        print "    OK."
        correct += 1

    print "Test 4."
    try:
        evaluate(m4)
    except ReferenceError:
        print "    OK."
        correct += 1

    print "Test 5."
    try:
        evaluate(m5)
    except ValueError:
        print "    OK."
        correct += 1

    if validate(evaluate(m6), solution6):
        print "    OK."
        correct += 1

    print "------------------------------------------------------"
    print "You got {0} out of 6 correct.".format(correct)
