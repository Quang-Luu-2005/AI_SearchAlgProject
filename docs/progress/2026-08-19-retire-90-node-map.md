# Retire the 90-node processed map

## Scope

- Removed the processed `thu_duc_market_v1.0.0` release from the active registry.
- Kept `thu_duc_landmarks_v1.0.0` as the only selectable processed map (65 nodes,
  178 directed road-path edges).
- Preserved all immutable `data/raw/` sources.

## Compatibility updates

- Search benchmark cases now use 10 deterministic landmark origin-destination
  pairs under `LANDMARK_HISTORICAL_BASELINE`.
- Cost-profile and search regression evidence no longer depends on the retired
  processed release; route-change examples remain explicitly `SIMULATED` in the
  toy fixture.
- API/catalog tests and dataset validation assert the active landmark release.

## Verification

Verified: `npm run test:data` passed, `npm run test:backend` passed (89 tests),
both benchmark artifacts were regenerated, and the final active-reference scan
contains no deleted processed graph target.
