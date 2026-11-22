import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

describe('Shongoti Application Shell', () => {
  it('renders landing page with Bangla title and brand identity', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    const elements = screen.getAllByText(/সংগতি/i);
    expect(elements.length).toBeGreaterThan(0);
    expect(elements[0]).toBeInTheDocument();
  });
});
