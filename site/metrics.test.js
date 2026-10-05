import test from "node:test";
import assert from "node:assert/strict";
import { summarise, comparison, managerText, shortlistRows } from "./metrics.js";
test("filters retain the distinction between crashes and casualties", () => {
  const rows = [
    { year: 2024, severity: "Fatal", crashes: 2, serious_crashes: 2, serious_casualties: 3 },
    { year: 2023, severity: "Minor injury", crashes: 5, serious_crashes: 0, serious_casualties: 0 },
  ];
  assert.deepEqual(summarise(rows, "2024", "All"), {
    crashes: 2,
    serious_crashes: 2,
    serious_casualties: 3,
  });
  assert.deepEqual(summarise(rows, "2024", "Minor injury"), {
    crashes: 0,
    serious_crashes: 0,
    serious_casualties: 0,
  });
});
test("comparison never silently uses another budget", () => {
  assert.equal(comparison([{ k: 10, method: "count", numerator: 2 }], 20, "count"), null);
});
test("road manager text reports coded crash counts", () => {
  assert.equal(
    managerText({ manager: "state", authority_counts: { state: 16, council: 1, not_coded: 0 } }),
    "State: 16 of 17 crashes",
  );
  assert.equal(
    managerText({ manager: "mixed", authority_counts: { state: 4, council: 3, not_coded: 1 } }),
    "Mixed: 4 state, 3 council",
  );
  assert.equal(
    managerText({ manager: "mixed", authority_counts: { state: 0, council: 0, not_coded: 2 } }),
    "Not coded",
  );
});
test("council list uses council-road counts, the original list keeps the frozen ranking", () => {
  const results = {
    shortlist: [
      { rank: 1, cell_id: "a", serious_count: 9, holdout_serious_count: 2, suburbs: "Nerang" },
    ],
  };
  const roads = {
    cells: { b: { suburbs: ["Southport"] } },
    by_manager: [
      {
        manager: "council",
        own_shortlist: [{ rank: 1, cell_id: "b", training_serious: 4, holdout_serious: 1 }],
      },
    ],
  };
  assert.deepEqual(shortlistRows(results, roads, "all", 20), [
    { rank: 1, cell_id: "a", train: 9, holdout: 2, suburbs: "Nerang" },
  ]);
  assert.deepEqual(shortlistRows(results, roads, "council", 20), [
    { rank: 1, cell_id: "b", train: 4, holdout: 1, suburbs: "Southport" },
  ]);
  assert.throws(() => shortlistRows(results, roads, "other", 20));
});
