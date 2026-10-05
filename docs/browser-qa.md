# Browser QA — 5 October 2026

Verified in the connected Chrome browser at `http://127.0.0.1:8765`, using the frozen public exports. Default desktop viewport: 1470 × 747. Mobile viewport: 375 × 812; the temporary override was reset afterwards.

| Check | Observed result |
|---|---|
| Loaded default | 8,142 casualty events / 3,407 serious events / 4,079 serious casualties; 20 rows and 20 selected cells |
| 2024 description | 1,688 / 695 / 818 |
| 2024 Fatal description | 17 / 17 / 27 |
| Filter independence | Descriptive filters preserved the frozen 55/695 shortlist comparison |
| 10 / 20 / 40 cells | 10 / 20 / 40 map cells and table rows; capture 30 / 55 / 82 of 695 respectively |
| Training point layer | 2,086 points with labels; 1,109 noise points; cluster 0 had 16 correctly labelled points |
| Accessible keyboard area path | Enter on the second table button selected rank 2, updated details and highlighted the same cell; Enter on the first restored rank 1 |
| Skip link | Enter moved to #main; next Tab reached the decision-brief link inside main |
| Desktop layout | Readable map, evidence table and comparison; no page-width overflow |
| Mobile layout | Area selector initially caused a 1.5 px overflow. Added min-width:0 to the grid item; selector now fits 331 px and document width equals 375 px |
| Mobile interactions | 40 rows / 2,086 points displayed without page-width overflow; reset to default afterwards |
| Actual CSV downloads | Both downloaded through browser controls and matched canonical files byte for byte |

The native select arrow-key sequence did not change its value through this automation interface, so that specific input path is **unverified**. The accessible keyboard table alternative was verified. This is a focused browser check, not a full screen-reader or WCAG certification. Direct focus on the main element was not asserted; the browser's sequential focus point moved correctly after the skip link.

Console inspection captured 16 earlier repeated message-channel listener errors at 20:33:24 AEST. No new application-script error or warning was recorded during the QA checks. Their exact extension/source attribution was not established; do not describe the entire console as error-free. The complete observations remain in `evidence/platforms/browser-qa-observations.json`.

Downloads:
- monthly.csv: 10,201 bytes; SHA-256 `848a629ed8e761d0b70bba23e1734378b233d5f3fc6d736a010a6467539fa9a8`.
- shortlist.csv: 1,927 bytes; SHA-256 `18e150f4bfe8b6659a6adbc5abe9c1644583a3dec98c1b45c54fc30452a94d93`.

Screenshots: [desktop](../evidence/platforms/dashboard-desktop.jpg), [labelled training clusters](../evidence/platforms/dashboard-clusters.jpg), [mobile](../evidence/platforms/dashboard-mobile.jpg). No public deployment or logged-out hosted access was tested.
