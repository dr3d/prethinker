# Challenge Strategy — The Festival Permit Maze

## Primary Attack Surface
**Rule activation and deadline families**: Five permits with five different clocks, violation triggers, suspension durations, renewal windows, and appeal procedures. Questions require computing exact suspension end times, distinguishing between expired and active licenses, and tracking which rules belong to which permit type.

## Secondary Surfaces
- **Parallel regulatory states**: Multiple permits in different states simultaneously
- **Deadline arithmetic**: 72-hour extension windows, 48-hour reinspection windows, 24-hour suspensions from specific times, 5-day inspection windows, 5-business-day appeal windows
- **Authority boundaries**: Burr can't override automatic suspensions. The Licensing Authority can restrict without a hearing. The Town Council controls sound exemptions.
- **Appeal timing futility**: The alcohol appeal hearing is scheduled after the festival ends

## Expected Failure Modes
- Treating the sound permit as active on October 16 afternoon (it's suspended until 22:15)
- Confusing the October 18 exemption validity with the suspension state
- Treating the fireworks inspection deadline as October 13 instead of October 17
- Asserting the meeting changed permit terms when it explicitly did not
