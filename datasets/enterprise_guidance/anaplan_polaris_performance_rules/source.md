# Polaris Performance Tuning And Debugging Rules

Polaris model builders should treat performance tuning as part of the normal build lifecycle, not as a final cleanup task. Successful teams monitor performance from the beginning of a project and continue checking it throughout implementation.

When building in Polaris, teams should use ALM from the start. They should monitor Calculation Effort, Memory, and Populated Cell Count frequently, especially when building large and highly dimensionalized modules such as output modules, reporting modules, and input modules. Complex modules should be tested in stages. As model complexity increases, the risk of performance problems also increases.

This guide should be used when actions are slow, model open time is latent, cell data entry feels sluggish, or the team is performing a routine health check.

A periodic performance review should examine integrations, long-running processes, UX rendering speed, model open time, and key formulas. Scheduled data flows should be monitored. Long-running processes should be audited. Boards, pages, and input views should be checked for rendering speed. Calculation effort should be reviewed within the first ten minutes after model opening.

If performance degrades, the team should export the Line Items tab to identify formulas that need optimization. The model should be tested at scale by pushing frequently to a fully loaded test model and testing the features used most often.

Optimization opportunities should be prioritized as follows.

First priority: line items with high Calculation Effort, high Complexity, and high GB should be optimized first, because they usually offer the largest performance improvement opportunity.

Second priority: line items with high Calculation Effort that use computationally intensive functions should be reviewed. Computationally intensive functions include FINDITEM, ISFIRSTOCCURRENCE, RANK, RANKCUMULATE, and CUMULATE.

Third priority: summary methods should be reviewed when cell counts are very high. Teams should ask whether the summary method can be moved to the end of the calculation chain so that On-Demand Calculation can apply. Teams should also ask whether all hierarchy summary levels are truly needed.

Fourth priority: line items with high Complexity and high Cell Count should be reviewed even when Populated Cell Count and Calculation Effort are small, because high addressable cell count and high complexity can still create performance risk.

Fifth priority: line items whose calculation complexity equals All Cells should be reviewed when cell counts are high, because All Cells calculations are fully dense and may pose performance risk.

GB represents the size equivalent of populated cells. GB does not directly determine performance, but very high GB can validate high complexity or high calculation effort. If complexity is low but populated cells or memory use are high, the line item may be optimized by making it end-of-chain so it can use On-Demand Calculation.

Optimization and debugging are necessary steps in a Polaris build timeline.

Guards should be used effectively. Builders should review whether all dimensions are required. If dimensions are required, builders should favor zero, FALSE, or BLANK guarded by an IF/THEN statement. A guard introduces new information into the line item, increases sparsity, and helps ensure math is only performed where needed.

For high-complexity one-to-many line items or All Cells line items, builders should review the dimensionality difference between the source and the target. The more cells that populate, the more space and time the calculation may require.

Builders should avoid formulas that result in All Cells when the formula applies to a substantial number of cells.

When testing an optimization, builders may need to revert the formula if calculation effort at model open time or complexity does not improve.

For complex formulas and long-running processes, builders should create a SYS Calculate? Boolean master switch. The master switch can be used in high-effort formulas and to pause real-time data flows. For example, calculations can be disabled during a multi-step data load and then enabled as the final step of the process.

Unnecessary memory should be avoided. Summary cell counts and summary memory can be large multiples of leaf-level cell counts and memory. Aggregation by SUM is fast. Aggregation by Formula, Ratio, Any, All, First Non-Blank, and Last Non-Blank requires more calculation effort.

LOOKUP against very large data sources requires more calculation effort. Multiple LOOKUPs tend to use additional calculation effort, so builders should attempt to use SUMs instead of multiple LOOKUPs when possible.

For complex nested IF statements, builders should use an iterative approach. They should compare populated cell counts and complexity across multiple approaches. They may split nested IF formulas if the formulas are non-performant. However, splitting a formula can accidentally force the engine to calculate more cells than it otherwise would, which can outweigh the benefit of greater parallelization.

If a line item is slow and has already been optimized as much as possible, builders should inspect upstream and downstream formulas for high calculation effort or high complexity and attempt to optimize those related formulas.

User-based filters on rows do not perform well at high dimensionality. They can create dense and large filter line items. Builders should model at natural dimensionality or use a native UX filter when possible.

When debugging a non-winding cyclic calculation error, builders should split the formula to identify which piece causes the circular reference. Then they should test whether staging line items can fix the issue, such as moving the lookup into a separate line item.

Specific Time Ranges and calculation Booleans can help ensure calculations populate cells only during relevant time periods. For example, a rolling twenty-four-month Boolean can restrict calculations to the needed time window.

All dimensions in a DEV model should have at least one list item so that Polaris can reject invalid formulas such as non-winding cyclic calculations.

Line items whose populated cell counts are much higher than other line items in the same module should be investigated, because they may use memory unnecessarily and may not be able to take advantage of On-Demand Calculation.

Filters, Dynamic Cell Access, and Conditional Formatting can use excess memory. Memory can be reduced by biasing formulas toward majority FALSE instead of majority TRUE. Filters should be centralized and reused whenever possible.

For export actions, Tabular Multiple Column Export is especially important in Polaris because datasets can be much larger.

Models should be separated by business process when natural process breakpoints exist. This can shorten calculation chains, reduce unnecessary recalculations, and separate security requirements by business function. The downside is that it adds integration complexity and can break real-time views.

No more than one Polaris model should be placed in a workspace.

Very large grids should not allow users both to pivot and export, because the default pivot with all levels of all dimensions can be extremely large and can lock the model during export. Combined Grids are preferred for efficient and compact leaf-level exports.

For intraday updates to reporting models, teams should not rely on full clear-and-reload. Instead, they should load deltas only. The recommended pattern is to stage upstream input-model data into an intermediate flat model with a Current / Previous dimension. The incremental load view should filter data where Current is not equal to Previous. A full unfiltered load option should also exist as a recovery path if the incremental load fails.

To debug Dynamic Cell Access formulas that may cause performance problems, builders should determine whether Selective Access can replace Dynamic Cell Access. They should ask whether the DCA driver truly needs every dimension in Applies To. They should use early exit where possible. They should avoid text operations such as string comparisons and FINDITEM. They should avoid ISFIRSTOCCURRENCE on large lists.

For Conditional Formatting, tiny-but-not-quite-zero values can consume memory without providing useful formatting benefit. Builders should use ROUND to empty those tiny values.

Adding list members can create very large numbers of cells and require recalculation during loading. To reduce load-time impact, builders should consider decoupling downstream modules from modules that immediately need the new list member, running the action less frequently, or creating dummy members so calculation upon list item creation is not needed.

