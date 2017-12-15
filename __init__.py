import math, mmh3
import numpy as np

class QuotientFilter:
    # num_stored (n): the QF must be able to store this many elements
    # while maintaining the false positive rate.
    # error_rate (f): the theoretically expected probability of
    # returning false positives, default is 1%.
    # alpha: load factor, default is None, where we will use n and f
    # to calculate the quotient bit size (q) and remainder bit size (r).

    def __init__(self, num_stored, alpha=None, error_rate=0.01):
        """
        Initialize the QF, calculate the parameters and raise error
        if needed. Then, create a QF with a corresponding size.
        """
        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")
        if num_stored <= 0:
            raise ValueError("Number of elements stored must be > 0.")
        self.r = int(-math.log(error_rate, 2))
        if alpha is None:
            self.m = int(-num_stored / (math.log(1 - error_rate) * 2 ** self.r))
            self.q = int(math.log(self.m, 2))
        else:
            if not (0 < alpha <= 1):
                raise ValueError("Load factor must be between 0 and 1.")
            self.m = int(num_stored / alpha)
            self.q = int(math.ceil(math.log(self.m, 2)))

        if self.q + self.r > 64:
            raise ValueError("Fingerprint size must be 64bits or less.")
        # Create the filter, the three bits are is_occupied, is_continuation,
        # and is_shifted in order. The last element is to store the remainder
        self.array = np.array([[False, False, False, None] for _ in range(self.m)])

    def get_elem(self, elem):
        """Get the quotient and remainder of an element using a hash function"""
        quotient = mmh3.hash(elem) // (2 ** self.r) % self.m
        remainder = mmh3.hash(elem) % (2 ** self.r)
        return quotient, remainder

    def is_empty(self, index):
        """Return a boolean value stating whether the slot is empty"""
        return not any(self.array[index][:3])

    def is_run_start(self, index):
        """Return a boolean value stating whether the slot is the start of a run"""
        return not self.array[index][1] and (self.array[index][0] or self.array[index][2])

    def is_cluster_start(self, index):
        """Return a boolean value stating whether the slot is the start of a cluster"""
        # Actually not used in this implementation, but will be needed
        # when we expand the implementation to support deletion
        return self.array[index][0] and not any(self.array[index][1:3])

    def find_run_start(self, index):
        """Find the index of the start of the run containing the input index"""
        running_count = 0
        # Scan left and count the number of runs until encounter
        for i in range(index, -1, -1) + range(index, self.m)[::-1]:
            if not self.is_empty(i) and not self.array[i][2]:
                break
            if self.array[i][0]:
                running_count += 1
        # Scan right and countdown every time a new run starts until running_count == 0
        for j in range(i, self.m) + range(i):
            if not self.array[j][1]:
                running_count -= 1
            if running_count == 0:
                break
        return j

    def query(self, elem):
        """Perform a lookup operation"""
        quotient, remainder = self.get_elem(elem)
        # If is_occupied is False, element is not in QF
        if not self.array[quotient][0]:
            return False
        # Else, find the start of the run that should containing the element
        start = self.find_run_start(quotient)

        # Scan the run to see if any slot contain the remainder
        for index in range(start, self.m) + range(start):
            if remainder == self.array[index][3]:
                return True
            if not self.array[index][2] and index != start:
                return False
        return False

    def insert(self, elem):
        """
        Follow the same path as lookup until we are sure the element
        is not in the QF, then find the slot to insert the element,
        push back the remainders in any slots in the cluster at or
        after the insert slot and update the bits.
        """
        quotient, remainder = self.get_elem(elem)
        # If the canonical slot is not empty, insert into the slot
        if self.is_empty(quotient):
            self.array[quotient][3] = remainder
            self.array[quotient][0] = True
            return
        # If not is_occupied, set is_occupied
        if not self.array[quotient][0]:
            self.array[quotient][0] = True

        # Scan the run to see if the element has been inserted
        start = self.find_run_start(quotient)
        if self.array[quotient][0]:
            for slot in range(start, self.m) + range(start):
                if remainder < self.array[slot][3]:
                    break
                elif not self.array[slot][2] and slot != quotient:
                    break
                elif not self.array[slot][1] and slot != quotient:
                    break
        # If the slot does not contain a value, insert into the slot
        # and update bits
        if self.array[slot][3] is None:
            self.array[slot][3] = remainder
            if slot != quotient:
                self.array[slot][2] = True
            if not self.is_run_start(slot):
                self.array[slot][1] = True
            return

        # Else, switch the value and update bits
        self.array[slot][3], remainder = remainder, self.array[slot][3]
        if slot != quotient:
            self.array[slot][2] = True
        if not self.is_run_start(slot):
            self.array[slot][1] = True
        # Then push back the remainders in the cluster
        for index in range(slot + 1, self.m) + range(slot):
            if self.array[index][3] is None:
                self.array[index][3] = remainder
                if not self.array[index][2]:
                    self.array[index][2] = True
                if self.is_run_start(index - 1):
                    self.array[index][1] = True
                return
            self.array[index][3], remainder = remainder, self.array[index][3]
            if index == self.find_run_start(index):
                self.array[index][1] = True
            if not self.array[index][2]:
                self.array[index][2] = True