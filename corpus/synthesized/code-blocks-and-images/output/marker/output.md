# Code, Quotation, and Imagery in Body Text

legible-pdf synthesized corpus

## 1 Source Code

The following Python function implements binary search over a sorted sequence, returning the index of the target value or −1 when no match is found.

```
def binary_search(arr, target):
lo, hi = 0, len(arr) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1
return -1
```

The implementation uses zero-based indexing and the floor-division operator, which are conventional in Python source.

## 2 Quotation

A frequently quoted observation about software construction comes from Donald Knuth's writing on optimization.

Premature optimization is the root of all evil. We should forget about small efficiencies, say about ninety-seven percent of the time.

The full passage from Knuth continues with a qualifier that is often omitted from popular paraphrases.

## 3 Imagery

A sample bar chart accompanies the text in Figure 1, illustrating how visual elements appear within a document body.

![](_page_1_Figure_2.jpeg)

Figure 1: A sample bar chart with five vertical bars.

As shown in Figure 1, bars of varying heights occupy a plotted region bounded by axis lines.

## 4 Glossary

The document mentions: a Python function named binary search, the operators floordivision and equality, the integer return value −1, the author Donald Knuth, the phrase premature optimization, and a bar chart figure with five bars.