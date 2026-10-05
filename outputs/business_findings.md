# Supply Chain Delivery Performance Findings

## Executive Summary
- Overall on-time rate: 48.87%
- Late shipment rate: 51.13%
- Average delay among eligible deliveries: 3.68 days
- Lowest-performing high-volume carrier: Roadrunner
- Carrier with the worst late delay: Metrologix
- Lowest-performing high-volume route: North-West
- Lowest on-time destination region: West
- Most common late-delay reason: Warehouse Backlog
- Highest average delay reason: Weather
- Lowest on-time shipping mode: Rail
- Highest on-time shipping mode: Road

## Actionable Findings
From 2025-01 to 2026-01, the on-time rate decreased by 22.46 percentage points. Check monthly shipment counts and partial-month coverage before drawing conclusions.

Routes with the largest late-delay averages are: Central-North (3.94 average late days, 299 shipments), South-East (3.88 average late days, 312 shipments), Central-South (3.84 average late days, 289 shipments), East-Central (3.82 average late days, 295 shipments), North-Central (3.76 average late days, 303 shipments)

The relationship between distance and delay is -0.00 (higher values suggest stronger positive correlation).

## Data Quality Audit
```json
{
  "Rows_Without_Shipment_ID_Removed": 7,
  "Duplicate_Shipment_IDs_Removed": 65,
  "Invalid_Order_Date_Formats": 0,
  "Invalid_Ship_Date_Formats": 0,
  "Invalid_Expected_Delivery_Formats": 0,
  "Invalid_Actual_Delivery_Formats": 0,
  "Missing_Carrier": 28,
  "Missing_Route": 0,
  "Missing_Order_Date": 0,
  "Missing_Ship_Date": 0,
  "Missing_Expected_Delivery": 38,
  "Missing_Actual_Delivery": 437,
  "Actual_Delivery_Before_Ship_Date": 18,
  "Expected_Delivery_Before_Ship_Date": 12,
  "Delivery_Durations_Over_30_Days": 0,
  "Delays_Over_30_Days": 0,
  "Cancelled_Shipments_Kept": 163,
  "Undelivered_Shipments_Kept": 152,
  "Delivered_Shipments_Eligible_For_KPIs": 5866
}
```
