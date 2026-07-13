import { describe, expect, it } from 'vitest';
import {
  formatLatency,
  formatPercent,
  formatDateTime,
  formatNumber,
  truncateText,
} from './format';

describe('formatLatency', () => {
  it('renders sub-second values in milliseconds', () => {
    expect(formatLatency(0)).toBe('0ms');
    expect(formatLatency(42)).toBe('42ms');
    expect(formatLatency(999)).toBe('999ms');
  });

  it('rounds fractional milliseconds', () => {
    expect(formatLatency(42.4)).toBe('42ms');
    expect(formatLatency(42.6)).toBe('43ms');
  });

  it('renders values >= 1000ms in seconds with two decimals', () => {
    expect(formatLatency(1000)).toBe('1.00s');
    expect(formatLatency(1500)).toBe('1.50s');
    expect(formatLatency(2340)).toBe('2.34s');
  });
});

describe('formatPercent', () => {
  it('multiplies by 100 and appends a percent sign', () => {
    expect(formatPercent(0)).toBe('0.0%');
    expect(formatPercent(1)).toBe('100.0%');
    expect(formatPercent(0.874)).toBe('87.4%');
  });

  it('honors the decimals argument', () => {
    expect(formatPercent(0.8746, 2)).toBe('87.46%');
    expect(formatPercent(0.5, 0)).toBe('50%');
  });
});

describe('formatNumber', () => {
  it('formats integers with locale grouping', () => {
    expect(formatNumber(1234)).toBe('1,234');
    expect(formatNumber(1000000)).toBe('1,000,000');
  });

  it('respects the decimals argument', () => {
    expect(formatNumber(12.345, 2)).toBe('12.35');
  });
});

describe('formatDateTime', () => {
  it('returns the original string when the input is not a valid date', () => {
    expect(formatDateTime('not-a-date')).toBe('not-a-date');
  });

  it('formats a valid ISO string into a non-empty localized string', () => {
    const result = formatDateTime('2026-07-13T09:30:00Z');
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
    expect(result).not.toBe('2026-07-13T09:30:00Z');
  });
});

describe('truncateText', () => {
  it('leaves short text unchanged', () => {
    expect(truncateText('hello', 10)).toBe('hello');
    expect(truncateText('hello', 5)).toBe('hello');
  });

  it('truncates and appends an ellipsis when over the limit', () => {
    expect(truncateText('hello world', 5)).toBe('hello…');
  });
});
