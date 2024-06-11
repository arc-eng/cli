import unittest

# Assuming the quicksort function is defined in a module named `quicksort_module`
from quicksort_module import quicksort

class TestQuicksort(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(quicksort([]), [])

    def test_single_element_list(self):
        self.assertEqual(quicksort([1]), [1])

    def test_two_element_list(self):
        self.assertEqual(quicksort([2, 1]), [1, 2])

if __name__ == '__main__':
    unittest.main()