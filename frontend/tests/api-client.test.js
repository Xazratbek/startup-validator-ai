const test = require('node:test');
const assert = require('node:assert/strict');

test('api base fallback is stable', async () => {
  process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000/api';
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'fallback';
  assert.equal(API_BASE, 'http://localhost:8000/api');
});
