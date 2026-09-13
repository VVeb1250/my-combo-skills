# Modern C++

Use this note for C++17/20/23 design, review, or refactoring. Embedded or
bare-metal constraints may require deliberate deviations; record the hardware
invariant before applying a desktop guideline.

## Ownership and interfaces

- Bind resource lifetime to scope with RAII. Prefer value semantics and the Rule
  of Zero. If a type must own a raw resource and define one copy/move/destructor
  operation, reason through all special members or make copying/moving explicit.
- Start with `const` and `constexpr`. Use strong types for units and identifiers,
  `enum class` for closed choices, and explicit constructors for conversions.
- Make ownership visible. A raw pointer or reference is a view unless the API
  says otherwise; use `std::unique_ptr` for exclusive ownership and
  `std::shared_ptr` only for a real shared lifetime.
- Keep interfaces small and precise. Pass cheap values by value, read-only
  expensive values by `const&`, and use a value/struct return instead of output
  parameters where practical.

```cpp
struct ParseResult { std::string token; std::size_t position; };
ParseResult parse(std::string_view input);
```

## Functions and concurrency

- Keep one logical operation per function, return by value, and mark a function
  `constexpr` or `noexcept` only when the semantics support that promise.
- Do not return a reference/pointer to a local, capture a local by reference in
  work that can outlive it, or use C-style variadics where a typed interface is
  possible.
- Prefer standard mutex/lock guards and scoped thread ownership. A shared
  mutable object needs a documented synchronization policy; a channel or value
  handoff may be simpler than a lock.
- Use sanitizers, warnings, and a focused lifetime/concurrency test at the seam
  where the risk exists. Do not treat a clean compile as proof of lifetime safety.

Source: ECC `cpp-coding-standards`, pinned and mapped in [source-map.md](../references/source-map.md).
