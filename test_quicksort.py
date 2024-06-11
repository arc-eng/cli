import unittest

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

class TestQuicksort(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(quicksort([]), [])

    def test_single_element_list(self):
        self.assertEqual(quicksort([1]), [1])

    def test_two_element_list(self):
        self.assertEqual(quicksort([2, 1]), [1, 2])

if __name__ == '__main__':
    unittest.main()