'''
CAPP 30122 W'20: Markov models and hash tables

Tetsuo Fujino
Takayuki Kitamura
'''

TOO_FULL = 0.5
GROWTH_RATIO = 2


class HashTable:
    '''
    Class for representing a hashtable.
    '''
    def __init__(self, cells, defval):
        '''
        Construct a new hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted
        '''
        self.table_size = cells
        self.defval = defval
        self.hash_table = [defval] * self.table_size

    def _hash_func(self, key):
        '''
        Given a set of strings, compute a integer, "hash value".
        If the hash table is full and the imput, "key",
        does not exist as a first element in the hash table,
        return None.
        '''
        sum_ord = 0
        for string in key:
            sum_ord += ord(string)

        for i in range(self.table_size):
            h_value = (sum_ord + i) % self.table_size
            if self.hash_table[h_value] == self.defval or \
                self.hash_table[h_value][0] == key:
                return h_value

        return None

    def lookup(self, key):
        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.
        '''
        n = self._hash_func(key)
        if n is None or self.hash_table[n] == self.defval:
            return self.defval

        return self.hash_table[n][1]

    def update(self, key, val):
        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table,  insert it with
        value "val".
        '''
        if self.defval in self.hash_table:
            n = self._hash_func(key)
            self.hash_table[n] = (key, val)
        # in cases that the table is full.
        else:
            # Expand the hash table.
            copy_hash_table = self.hash_table
            self.table_size = GROWTH_RATIO * self.table_size
            self.hash_table = [self.defval] * self.table_size
            for k, v in copy_hash_table:
                self.update(k, v)

            self.update(key, val)
