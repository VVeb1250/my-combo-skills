# Commander

## Contract

- Explicit `hold` keeps the vehicle stationary. Explicit `move` wins over automatic retreat.
- Only `free` at risk >= 70 chooses automatic retreat. A retreating vehicle does not fire. Other vehicles fire if loaded.
- Smoke is a cover signal, not permission to override manual orders.

## Ownership

`src/arbitration.py:decide` is the final owner of movement and firing. Callers consume its action; they must not independently override it. Keep the input/result interface stable.

## Verification

`tests/test_arbitration.py` exercises the public decision. A pure action test does not establish real-time game behavior; this fixture has no runtime renderer.
