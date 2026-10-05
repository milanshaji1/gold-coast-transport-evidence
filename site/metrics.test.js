import test from 'node:test';
import assert from 'node:assert/strict';
import {summarise, comparison} from './metrics.js';
test('filters retain the distinction between crashes and casualties',()=>{
const rows=[{year:2024,severity:'Fatal',crashes:2,serious_crashes:2,serious_casualties:3},{year:2023,severity:'Minor injury',crashes:5,serious_crashes:0,serious_casualties:0}];
assert.deepEqual(summarise(rows,'2024','All'),{crashes:2,serious_crashes:2,serious_casualties:3});
assert.deepEqual(summarise(rows,'2024','Minor injury'),{crashes:0,serious_crashes:0,serious_casualties:0});
});
test('comparison never silently uses another budget',()=>{
assert.equal(comparison([{k:10,method:'count',numerator:2}],20,'count'),null);
});
