# Sample Application

Minimal Android application used to integration-test [premex-ab/setup-android-cli](https://github.com/premex-ab/setup-android-cli).

The active integration fixture is `sdk-20` (API 35, AGP 8.7.3, Java 17). CI installs the required SDK packages with the published v1.1.0 action, pinned to its commit SHA.

## Structure

The other `sdk-*` folders are historical fixtures from the archived `setup-android` action. They are retained for reference; CI no longer tests every legacy command-line tools version:

<!-- BEGIN SDK TABLE -->
| Folder | cmdline-tools | AGP | Gradle | Java |
|--------|--------------|-----|--------|------|
| sdk-1 | 1.0 (6200805) | 7.2.2 | 7.5.1 | 11 |
| sdk-2 | 2.1 (6609375) | 7.2.2 | 7.5.1 | 11 |
| sdk-3 | 3.0 (6858069) | 7.2.2 | 7.5.1 | 11 |
| sdk-4 | 4.0 (7302050) | 7.2.2 | 7.5.1 | 11 |
| sdk-5 | 5.0 (7583922) | 7.2.2 | 7.5.1 | 11 |
| sdk-6 | 6.0 (8092744) | 7.2.2 | 7.5.1 | 11 |
| sdk-7 | 7.0 (8512546) | 7.4.2 | 7.6.4 | 11 |
| sdk-8 | 8.0 (9123335) | 7.4.2 | 7.6.4 | 11 |
| sdk-9 | 9.0 (9477386) | 7.4.2 | 7.6.4 | 11 |
| sdk-10 | 10.0 (9862592) | 8.1.4 | 8.4 | 17 |
| sdk-11 | 11.0 (10406996) | 8.1.4 | 8.4 | 17 |
| sdk-12 | 12.0 (11076708) | 8.5.2 | 8.7 | 17 |
| sdk-13 | 13.0 (11479570) | 8.5.2 | 8.7 | 17 |
| sdk-16 | 16.0 (12266719) | 8.7.3 | 8.12 | 17 |
| sdk-17 | 17.0 (12700392) | 8.7.3 | 8.12 | 17 |
| sdk-19 | 19.0 (13114758) | 8.7.3 | 8.12 | 17 |
| sdk-20 | 20.0 (14742923) | 8.7.3 | 8.12 | 17 |
<!-- END SDK TABLE -->

## CI

Pull requests from this repository and pushes to `main` build `sdk-20` on our own runners:

- macOS: Tart (`tart`)
- Linux: baremetal (`self-hosted`, `linux`, `x64`)
- Windows: baremetal (`self-hosted`, `windows`, `x64`)

Fork pull requests do not execute repository code on these runners. The required CI gate fails when builds are skipped.

The former weekly command-line tools matrix generator has been retired. `scripts/sync-sdk-versions.py` remains as a historical utility and is not run by CI.
