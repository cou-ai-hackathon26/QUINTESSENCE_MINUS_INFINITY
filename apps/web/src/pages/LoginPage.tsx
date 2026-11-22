import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useLanguage } from '../i18n/LanguageContext';

export default function LoginPage() {
  const { t } = useLanguage();
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const navigate = useNavigate();

  const handleSendOtp = (e: FormEvent) => {
    e.preventDefault();
    if (phone.length >= 11) {
      setStep('otp');
    }
  };

  const handleVerifyOtp = (e: FormEvent) => {
    e.preventDefault();
    navigate('/app');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem' }}>
        <Card style={{ width: '100%', maxWidth: '400px' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem', textAlign: 'center' }}>
            {t('login.title')}
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '1.5rem', textAlign: 'center' }}>
            {t('login.subtitle')}
          </p>

          {step === 'phone' ? (
            <form onSubmit={handleSendOtp} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                  {t('login.phone_label')}
                </label>
                <input
                  type="tel"
                  placeholder="017XXXXXXXX"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e1',
                    fontSize: '1rem',
                  }}
                  required
                />
              </div>
              <Button type="submit">{t('login.send_otp')}</Button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                  {t('login.otp_label')}
                </label>
                <input
                  type="text"
                  placeholder="123456"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.8rem',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e1',
                    fontSize: '1.1rem',
                    textAlign: 'center',
                    letterSpacing: '0.2rem'
                  }}
                  required
                />
              </div>
              <Button type="submit">{t('login.verify_otp')}</Button>
            </form>
          )}

          <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
            <Link to="/demo" style={{ color: '#0284c7', textDecoration: 'none', fontWeight: 600 }}>
              {t('login.demo_prompt')}
            </Link>
          </div>
        </Card>
      </main>
    </div>
  );
}
