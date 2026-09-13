# Dart and Flutter

Use this note for Dart null safety, Flutter widgets, state, navigation,
networking, or async composition. Match the Dart/Flutter release and the state
library already used by the app.

- Prefer `?.`, `??`, promotion, and Dart 3 pattern matching over `!`. Use
  `late` only when initialization before first access is guaranteed.
- Model loading/success/failure as sealed states and keep state immutable with
  `copyWith` or the project's established generator. This prevents impossible
  combinations of flags and payloads.
- Scope asynchronous work to the widget/controller lifecycle. Use
  `Future.wait` for independent calls, check `mounted` before using
  `BuildContext` after an await, and propagate cancellation or stale-request
  behavior where the client supports it.
- Keep widgets small and `const` where possible; extract reusable UI into
  classes rather than methods when it needs its own lifecycle or rebuild scope.
- For GoRouter auth redirects, make refresh reactive to auth state. For Dio
  token refresh, guard the one-time retry and bound concurrent refreshes.
- Keep secure tokens in platform secure storage and use fakes/provider overrides
  for tests. Do not log request headers or raw credentials.

Source: ECC `dart-flutter-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
