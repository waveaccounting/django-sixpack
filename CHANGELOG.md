## 1.0.4

Bug Fix:

  - When the server isn't available or returns an error, participate will return the forced bucket (if it exists) and otherwise return the first alternative.

Test Fix:

  - Updated ParticipateTest.test_convert_calls_library to not check for the kpi in the call as it is currently nor supported.

Documentation:

  - Added Changelog
