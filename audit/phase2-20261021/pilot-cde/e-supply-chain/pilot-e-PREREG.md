Pilot E pre-registration (before running). Fixture: package.json + lockfile v3, 3 direct deps.
Expect: minimist@1.2.0 flagged (known advisories, e.g. prototype pollution fixed in 1.2.6);
zz-acme-auth-utils-9q7 (nonexistent) NOT reported clean (unassessable / not found);
is-odd@3.0.1 clean or unassessable but never flagged without a datum; gh absent => note says anonymous;
no signal reported clean when its source was unavailable (anonymous GitHub rate limit);
run 2 with --offline and an empty cache => refuses to report ("measured nothing").
Fail if: nonexistent package reported clean, or any clean without a datum, or token read from gh.
