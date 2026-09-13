# React Native and Expo

Use this note for React Native/Expo navigation, state, data fetching, lists,
native APIs, or token storage. Match the Expo/React Native release and routing
library in the project.

- Keep feature code separated from navigation and platform adapters. Validate
  route parameters at the screen boundary before using them in a fetch or native
  operation.
- Use a cache-aware data library for server state and a schema validator at the
  network boundary. Keep local UI state separate from cache state and persisted
  auth state.
- Virtualize large lists with `FlatList`/the project's equivalent. Do not map a
  large collection into a `ScrollView` when rows can be recycled.
- Wrap native APIs in hooks or small adapters, clean up listeners/subscriptions
  in effect cleanup, and handle foreground/background transitions explicitly.
- Keep tokens in platform secure storage through the established adapter. Do
  not put long-lived credentials in plain AsyncStorage or log them while
  diagnosing a request.
- Pick one styling system already used by the app and keep platform-specific
  behavior explicit. Test keyboard, safe-area, screen-reader, and offline/error
  states at the screen seam.

Source: ECC `react-native-patterns`, pinned and mapped in [source-map.md](../references/source-map.md).
