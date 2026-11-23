import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

describe('Shongoti Application Shell & Bilingual Support', () => {
  it('renders landing page with Bangla title and brand identity by default', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    const elements = await screen.findAllByText(/সংগতি/i);
    expect(elements.length).toBeGreaterThan(0);
    expect(elements[0]).toBeInTheDocument();
  });

  it('supports seamless toggling between Bangla and English', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    // Initial state has Bangla navigation button "English" (to switch to English)
    const switchBtn = await screen.findByRole('button', { name: /english/i });
    expect(switchBtn).toBeInTheDocument();

    // Click to switch to English
    fireEvent.click(switchBtn);

    // Now English texts appear
    expect(screen.getByText(/Your shop\./i)).toBeInTheDocument();
    expect(screen.getByText(/Try it for yourself/i)).toBeInTheDocument();

    // Switch button now shows "বাংলা"
    const bnSwitchBtn = screen.getByRole('button', { name: /বাংলা/i });
    expect(bnSwitchBtn).toBeInTheDocument();

    // Click back to Bangla
    fireEvent.click(bnSwitchBtn);
    expect(document.documentElement.lang).toBe('bn');
  });
});
