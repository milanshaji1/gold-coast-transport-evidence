# Where should road-safety investigation start on the Gold Coast?

Start with the 20-square count shortlist, and split it by who manages each road. Clustering did not improve on simple counts, and the data cannot identify the riskiest roads per trip.

The 2020–2024 source contains 8,142 casualty crashes, including 3,407 serious crashes and 4,079 people killed or hospitalised. A serious crash is one classified as Fatal or Hospitalisation. A fixed 500 m grid covers the current Gold Coast boundary. Squares are ranked on serious crashes in 2021–2023, and the ranking is checked against 2024, which was kept aside.

| 2024 evaluation | Top 10 squares | Top 20 squares | Top 40 squares |
|---|---:|---:|---:|
| Simple counts | 30 / 695 (4.32%) | 55 / 695 (7.91%) | 82 / 695 (11.80%) |
| DBSCAN clustering | 30 / 695 (4.32%) | 54 / 695 (7.77%) | 83 / 695 (11.94%) |

The top 20 squares cover 4.82 km², or 0.35% of the city, but held 55 of the 695 serious crashes in 2024 (7.9%). That is about 23 times their share by area; spread evenly, the same area would hold about 2.4. Clustering caught one fewer crash at 20 squares, and the small differences at all three sizes do not show that either method is better. Thirteen of the 20 squares were also in the previous three-year fit's top 20. Most serious crashes in 2024 still happened outside the shortlist.

Fourteen of the top 20 squares are mostly on state-controlled roads, nine of them on the Pacific Motorway (M1) between Coomera and Nerang. In 2021–2023, 66% of the serious crashes in these squares were on state-controlled roads, against 50% citywide. TMR manages those roads, not the City. Ranking council roads separately gives the City a list it can act on: its top 20 squares caught 40 of the 384 serious crashes on council roads in 2024, against 24 for the combined list. This split was added after the 2024 evaluation and does not change the original result.

The Gamma-Poisson experiment was rejected for decisions about individual sites. In the training period, 84.85% of grid squares had no serious crashes. Pooling road and non-road land can give high overall interval coverage without reliable estimates for individual sites. Using the same prior for every square also leaves the ranking unchanged.

Two serious crashes fall just outside the present boundary but stay in the totals and the 2024 denominator. Both are in squares that touch the boundary. No crashes are missing coordinates in this snapshot.

Next steps: refer the state-road squares to TMR. For the council squares, add traffic volumes, road and intersection layout, existing treatments, an engineering inspection and community input. Counts do not measure risk per trip, establish causes or choose a treatment. This independent study is not commissioned or endorsed by the City.

Source: Queensland Government open crash and boundary data, CC BY 4.0. Data snapshot `8c293a52745057c4`; DBSCAN settings were frozen on 2023 before the 2024 evaluation. Pandemic effects, reporting gaps, the current boundary and later source revisions limit interpretation.
