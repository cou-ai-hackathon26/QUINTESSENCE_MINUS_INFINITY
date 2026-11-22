import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Card } from '../components/Card';
import { Button } from '../components/Button';

export default function LoginPage() {
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
            দোকানের অ্যাকাউন্টে প্রবেশ
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '1.5rem', textAlign: 'center' }}>
            আপনার রেজিস্টার্ড মোবাইল নম্বর দিয়ে ওটিপি কোড পান
          </p>

          {step === 'phone' ? (
            <form onSubmit={handleSendOtp} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                  মোবাইল নম্বর
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
              <Button type="submit">ওটিপি পাঠান</Button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                  ৬ সংখ্যার ওটিপি (OTP) কোড
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
              <Button type="submit">যাচাই করে প্রবেশ করুন</Button>
            </form>
          )}

          <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
            <Link to="/demo" style={{ color: '#0284c7', textDecoration: 'none', fontWeight: 600 }}>
              লগইন না করে ডেমো মোডে দেখতে চান?
            </Link>
          </div>
        </Card>
      </main>
    </div>
  );
}
