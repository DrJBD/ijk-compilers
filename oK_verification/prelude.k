/ oK prelude -- prepended to every .k file under test.
/ Confirmed by direct testing, 2026-09-14: `oK` alone parses fine but
/ is undefined by default ("the name 'oK' has not been defined").
/ Defining it here as a sentinel means any test file can end with a
/ bare `oK` line and get a clean, successful `1` back rather than an
/ error -- a real pun, not just a label: "oK" the interpreter's own
/ name, used as a bare statement, evaluates to the same thing the
/ English word "ok" means (affirmative, success).
oK:1
