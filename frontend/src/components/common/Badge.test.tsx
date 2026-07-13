import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge, IntentBadge, SuccessBadge, ToolBadge } from './Badge';

describe('Badge', () => {
  it('renders its children', () => {
    render(<Badge>hello</Badge>);
    expect(screen.getByText('hello')).toBeInTheDocument();
  });

  it('applies the muted variant by default', () => {
    render(<Badge>muted</Badge>);
    expect(screen.getByText('muted').className).toContain('text-secondary');
  });

  it('applies the requested variant styles', () => {
    render(<Badge variant="success">ok</Badge>);
    expect(screen.getByText('ok').className).toContain('text-success');
  });
});

describe('IntentBadge', () => {
  it('renders the intent text', () => {
    render(<IntentBadge intent="CONTROL_CLIMATE" />);
    expect(screen.getByText('CONTROL_CLIMATE')).toBeInTheDocument();
  });

  it('uses the warning variant for UNKNOWN intents', () => {
    render(<IntentBadge intent="UNKNOWN" />);
    expect(screen.getByText('UNKNOWN').className).toContain('text-warning');
  });

  it('uses the primary variant for known intents', () => {
    render(<IntentBadge intent="SET_NAVIGATION" />);
    expect(screen.getByText('SET_NAVIGATION').className).toContain('text-primary');
  });
});

describe('SuccessBadge', () => {
  it('renders "Success" for a passing result', () => {
    render(<SuccessBadge success />);
    expect(screen.getByText('Success').className).toContain('text-success');
  });

  it('renders "Failed" for a failing result', () => {
    render(<SuccessBadge success={false} />);
    expect(screen.getByText('Failed').className).toContain('text-danger');
  });
});

describe('ToolBadge', () => {
  it('renders the tool name', () => {
    render(<ToolBadge name="setClimate" />);
    expect(screen.getByText('setClimate')).toBeInTheDocument();
  });
});
