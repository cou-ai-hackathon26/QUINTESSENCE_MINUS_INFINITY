import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useLanguage } from '../i18n/LanguageContext';

export default function OnboardingPage() {
  const { t } = useLanguage();
  const [shopName, setShopName] = useState('');
  const [cashBalance, setCashBalance] = useState('');
  const [bkashBalance, setBkashBalance] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    navigate('/app');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem' }}>
        <Card style={{ width: '100%', maxWidth: '480px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
            {t('onboarding.title')}
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '1.5rem' }}>
            {t('onboarding.subtitle')}
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                {t('onboarding.shop_name')}
              </label>
              <input
                type="text"
                placeholder={t('onboarding.shop_placeholder')}
                value={shopName}
                onChange={(e) => setShopName(e.target.value)}
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                {t('onboarding.cash_opening')}
              </label>
              <input
                type="number"
                placeholder="0"
                value={cashBalance}
                onChange={(e) => setCashBalance(e.target.value)}
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                {t('onboarding.digital_opening')}
              </label>
              <input
                type="number"
                placeholder="0"
                value={bkashBalance}
                onChange={(e) => setBkashBalance(e.target.value)}
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}
              />
            </div>

            <Button type="submit">{t('onboarding.submit')}</Button>
          </form>
        </Card>
      </main>
    </div>
  );
}
