# Presentation Notes

## Opening (4-5 min)

- Problem statement and goal
- Constraints and expected output

## Approach (8-10 min)

- Pipeline stages:
  1. Data model/validation
  2. Parsing
  3. Aggregation
  4. Gap detection
  5. Alerts
- Explain what was built and why

## Decisions and Trade-offs (6-7 min)

- Why Pydantic
- Why invalid status -> `UNKNOWN`
- Why counts-based status distribution
- Why `2x avg interval` gap rule

## Results (6-7 min)

- JSON output structure
- Example summary, gap, and alerts
- Mention tests

## Wrap-up (3-4 min)

- What is complete
- What to extend next:
  - configurable thresholds
  - streaming large files
  - additional alert types
  - alternate outputs

## Notes

- Focus on clean structure and clarity.
- The data model is the foundation that makes later processing simpler and safer.
