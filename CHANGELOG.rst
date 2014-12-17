1.0.5
-----
This version fixes the tests to work with Django 1.6+, which (as a side-effect)
means they will no longer work for Django 1.5.* - the code should still work, however.

Feature:

- Adds better logging when `convert` fails (thanks @robinedwards)

Test Fix:

- Fixes the test running to work on Django 1.6+

1.0.4
-----

Bug Fix:

-  When the server isn't available or returns an error, participate will
   return the forced bucket (if it exists) and otherwise return the
   first alternative.

Test Fix:

-  Updated ParticipateTest.test\_convert\_calls\_library to not check
   for the kpi in the call as it is currently nor supported.

Documentation:

-  Added Changelog

