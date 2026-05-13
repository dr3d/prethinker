# Boundary Probe: Dense Implicit Set Difference Pair

## Probe A: Overlapping Review Sets

Set S-1 contains these tokens:

| Token | In set S-1 |
| --- | --- |
| T-01 | yes |
| T-02 | yes |
| T-03 | yes |
| T-04 | yes |
| T-05 | yes |
| T-06 | yes |

Set S-2 contains these tokens:

| Token | In set S-2 |
| --- | --- |
| T-03 | yes |
| T-04 | yes |
| T-05 | yes |
| T-06 | yes |
| T-07 | yes |
| T-08 | yes |

Notice N-A excludes tokens T-02 and T-05.
Notice N-B excludes tokens T-04 and T-07.

Review R-A starts from set S-1 and leaves out tokens excluded by notice N-A.
Review R-B starts from set S-2 and leaves out tokens excluded by notice N-B.

The review notes do not print either final remaining list or either final count.

## Probe B: Cross-Notice Distractor

Set S-3 contains these tokens:

| Token | In set S-3 |
| --- | --- |
| U-10 | yes |
| U-11 | yes |
| U-12 | yes |
| U-13 | yes |
| U-14 | yes |

Notice N-C excludes tokens U-10 and U-14.
Notice N-D excludes token U-12.

Review R-C starts from set S-3 and leaves out tokens excluded by notice N-C.
Notice N-D is present in the same packet but is not the exclusion notice for
review R-C.

The packet does not print the final R-C remaining list or count.
