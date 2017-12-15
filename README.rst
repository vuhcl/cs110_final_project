Final Project - CS110 Fall 2017
===============================
Vu H. Chu-Le

----

Overview
========

In Assignment 3, we implemented Bloom filter (BL), which is a data structure
representing a set of data using an array of m bits, initially all set to 0.
It is used to test whether an element is a member of a set. The filter uses k
independent hash functions that map each element in the data set to one of the
m array positions, generating a uniform random distribution. ("Bloom filter",
n.d.) We also implemented counting Bloom filter, an extension of BL that
supports deletion.

For this project, we explore Quotient filters (QF), which maintain many of the
same guarantees as BL, but are much more cache-friendly and therefore work
faster in memory-constrained conditions.

Design
======

In this section, we will go through the structure of QF as outlined by Bender
et. al. (2011). Some words that will appear in this section or the
implementation are:

- canonical slot: The slot in which a fingerprint’s remainder would be stored
if there were no collisions.
- run: a group of the remainders with the same quotient stored contiguously
- cluster: a maximal sequence of occupied slots whose first element is the
only element of the cluster stored in its canonical slot. A cluster may
contain one or more runs.

The QF stores p-bit fingerprints of elements. The QF is a compact hash table
that employs quotienting, a technique in which the fingerprint is partitioned
into the q most significant bits (the quotient) and the r least significant
bits (the remainder). The remainder is stored in the bucket indexed by the
quotient, hence the name of the data structure.

A QF has m slots (m = 2^q), containing the remainder and three additional bits.
The three additional bits in each slot are:
- is_occupied: specifies whether a slot is the canonical slot for some value
stored in the filter.
- is_continuation: specifies whether a slot holds a remainder that is part of
a run (but not the first).
- is_shifted specifies whether a slot holds a remainder that is not in its
canonical slot.

The QF employs linear probing as a collision-resolution strategy, and stores
the remainders in sorted order.

Behaviour
=========

Parameters
----------

Similar to BL, QL guarantees that there is no false negatives, but trades memory
efficiency for a small false positive rate. A false positive can occur only when
two elements map to the same fingerprint (Bender et. al., 2011).

Let the load factor of the hash table be α = n/m, where n is the number of
elements, and m = 2^q is the number of slots. Then the false positive rate is:
1 − e^(−α/2^r) <= 2^(-r). Therefore, given a false positive rate (f) and a
capacity (n), we can calculate q, r as follows:

r = -log_2(f)

α = -ln(1 - f) * 2^r <=> m = -n/(ln(1 - f) * 2^r)

Or if α is given: m = n/α

q = log_2(m)

Scaling
-------

According to Bender et. al. (2011), for a QF and a BL that can hold the same
number of elements and with the same false positive rate, a QF with α = 3/4
requires 1.2 times as much space as a BL with 10 hash functions. The ratio
will change as parameters vary.

The paper also argues that since lookups and inserts in a QF all require
decoding an entire cluster, clusters are small. If we assume that the hash
function generates uniformly distributed independent outputs, then with high
probability, a QF with m slots has all runs of length O(log m); most runs
have length O(1).

Because m depends on false positive rate (f) and capacity (n), if we hold n
constant, we can rewrite the time complexity as a function of f: O(f/(log f))

Or if we hold α and f constant, time complexity according to n is O(log n).

As measured, our implementation runtime scales accordingly (see:
http://bit.ly/2BovSJj and http://bit.ly/2BmqWox ).

Pros and cons
=============

Pros
----

As mentioned above, QF is expected to be faster than BL as it only checks one
hash function. Moreover, QF also supports deletions and merge without affecting
the false positive rate.

Cons
----

QF requires more space than BL. However, QF is still more space-efficient
compared to other alternatives that support deletions such as counting BF. Still,
as we implement the QF, we find that it is much harder to implement, debug, and
maintain.

Bugs & Future improvements
==========================
(Note: Our implementation supports both python2 and python3)

Bugs
----

Given the time constraint and complexity of the data structure, there may be bugs
that we have not found and fixed. One major bug we have found but have not been
able to fix, however, is that our implementation has a small false negative rate
approximately equal to the false positive rate. As this can be circumvented by
lowering the load factor, we put this error down to a bug in shifting the
remainders when inserting if the cluster is not small.

Future improvements
-------------------

While the implementation scales as expected, it is much slower practically than
theoretically. Instead of using a numpy array, we can use an ordered dict to
improve practical runtime. Furthermore, the current algorithm is rather convoluted,
which makes it harder to debug. To solve this problem, we can create a cell class
for each slot, with functions to set and clear the three additional bits as well
as a function to set the element into a cell separated from the insertion operation
of the QF class. This would allow for more readability and ease of maintenance.

Moreover, while QF supports deletion and merge, these operations are not yet
implemented and will be looked into once we made the aforementioned improvements
and fix current bugs.

References
==========

[1] Bender et. al. (2011). Don’t Thrash: How to Cache Your Hash on Flash.
Proceedings of the 3rd USENIX conference on Hot topics in storage and file
systems (HotStorage'11). Retrieved from
http://static.usenix.org/events/hotstorage11/tech/final_files/Bender.pdf

[2] Quotient filter (n.d.) In Wikipedia. Retrieved from
https://en.wikipedia.org/wiki/Quotient_filter

[3] Bloom filter (n.d.) In Wikipedia. Retrieved from
https://en.wikipedia.org/wiki/Bloom_filter
