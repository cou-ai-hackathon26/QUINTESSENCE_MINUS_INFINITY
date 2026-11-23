import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Volume2, 
  Play, 
  Pause, 
  RotateCcw, 
  X, 
  Sparkles, 
  AlertTriangle, 
  Wallet, 
  Package, 
  ArrowRight,
  Radio
} from 'lucide-react';
import { useResource } from './ui';
import { useLanguage } from '../i18n/LanguageContext';
import './voice-orb.css';

interface DailyBrief {
  date: string;
  liquid_cash_bdt: number;
  open_notifications_count: number;
  high_priority_count: number;
  unapplied_credit_amount_bdt: number;
  voice_script_bn: string;
  voice_script_en: string;
}

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  category: string;
  priority: string;
  status: string;
  target_entity_type?: string;
  target_entity_id?: string;
  created_at: string;
}

type CategoryKey = 'overview' | 'urgent' | 'cash' | 'receiving';
type VoiceKey = 'bn-BD-PradeepNeural' | 'bn-BD-NabanitaNeural' | 'en-US-GuyNeural' | 'en-US-JennyNeural';

export function VoiceNotificationOrb() {
  const navigate = useNavigate();
  const { language } = useLanguage();
  
  const [isOpen, setIsOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState<CategoryKey>('overview');
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState<string>('+0%');
  const [audioLoading, setAudioLoading] = useState(false);
  const [playbackError, setPlaybackError] = useState<string | null>(null);

  // Initialize voice based on language context
  const [voice, setVoice] = useState<VoiceKey>(
    language === 'en' ? 'en-US-GuyNeural' : 'bn-BD-PradeepNeural'
  );

  // Determine if current voice is English
  const isEnglish = voice.startsWith('en-US');

  // Audio element reference and playback session ID to prevent ghost plays or overlapping audio
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playbackSessionRef = useRef<number>(0);
  const isOpenRef = useRef<boolean>(isOpen);

  // Keep isOpenRef synchronized and immediately silence audio when modal closes
  useEffect(() => {
    isOpenRef.current = isOpen;
    if (!isOpen) {
      stopAudio();
    }
  }, [isOpen]);

  // Synchronize default voice if global language changes while closed
  useEffect(() => {
    if (!isOpen) {
      setVoice(language === 'en' ? 'en-US-GuyNeural' : 'bn-BD-PradeepNeural');
    }
  }, [language, isOpen]);

  // Fetch real authenticated brief and notifications
  const { data: brief } = useResource<DailyBrief>('/api/v1/notifications/brief');
  const { data: notifications } = useResource<NotificationItem[]>('/api/v1/notifications');

  // Count unread or urgent alerts
  const urgentCount = notifications?.filter(n => n.priority === 'high' && n.status !== 'resolved').length ?? 0;
  const totalOpenCount = brief?.open_notifications_count ?? (notifications?.filter(n => n.status !== 'resolved').length ?? 0);

  // Compute category scripts and targets dynamically based on voice language
  const getCategoryDetails = (cat: CategoryKey, englishMode: boolean) => {
    switch (cat) {
      case 'overview':
        return {
          title: englishMode ? 'Daily Executive Brief' : 'আজকের সার্বিক ব্রিফিং',
          subtitle: englishMode 
            ? 'Cash liquidity, critical blockers & receivables' 
            : 'দোকানের ক্যাশ, সতর্কতা ও গুরুত্বপূর্ণ খাতা',
          icon: Sparkles,
          targetUrl: '/app/planner',
          targetLabel: englishMode ? 'Go to Cash Planner' : 'ক্যাশ প্ল্যানারে যান',
          text: englishMode
            ? (brief?.voice_script_en || 'Good morning. Total liquid cash in your shop is 25,400 Taka with 3 active workflow alerts to review.')
            : (brief?.voice_script_bn || 'শুভ সকাল। আপনার দোকানে বর্তমানে মোট লিকুইড ক্যাশ রয়েছে ২৫ হাজার টাকা। আজকের জন্য ৩টি গুরুত্বপূর্ণ কাজের সতর্কতা রয়েছে।')
        };
      case 'urgent': {
        const urgentItems = notifications?.filter(n => n.priority === 'high' && n.status !== 'resolved') || [];
        const textEn = urgentItems.length > 0
          ? `Urgent alert. Your shop has ${urgentItems.length} high priority issues requiring attention. Specifically: ${urgentItems[0].title}. Prompt resolution is recommended.`
          : 'All high-priority issues are currently resolved. Shop operations are running smoothly.';
        const textBn = urgentItems.length > 0
          ? `জরুরি সতর্কবার্তা। আপনার দোকানে ${urgentItems.length}টি উচ্চ অগ্রাধিকারের সমস্যা রয়েছে। বিশেষ করে: ${urgentItems[0].title}। দ্রুত সমাধান প্রয়োজন।`
          : 'বর্তমানে কোনো উচ্চ ঝুঁকির জরুরি সমস্যা নেই। সব কিছু স্বাভাবিক ও নিয়ন্ত্রণে রয়েছে।';
        return {
          title: englishMode ? 'Urgent Alerts & Blockers' : 'জরুরি সতর্কবার্তা',
          subtitle: englishMode 
            ? `${urgentCount} high priority items pending` 
            : `${urgentCount}টি অগ্রাধিকার বিষয় সমাধান বাকি`,
          icon: AlertTriangle,
          targetUrl: '/app/cases',
          targetLabel: englishMode ? 'View in Agent Workspace' : 'Agent Workspace-এ দেখুন',
          text: englishMode ? textEn : textBn
        };
      }
      case 'cash': {
        const cashAmount = brief?.liquid_cash_bdt ?? 25400;
        const textEn = `Liquidity analysis. Total available liquid cash is approximately ${Math.round(cashAmount)} Taka. Verify required reserves before committing to new expenditures.`;
        const textBn = `তারল্য হিসাব। আপনার দোকানে বর্তমান মোট তরল তহবিল প্রায় ${Math.round(cashAmount)} টাকা। কোনো খরচ করার আগে রিজার্ভ নিশ্চিত করুন।`;
        return {
          title: englishMode ? 'Cash & Liquidity Risk' : 'টাকা ও তারল্য ঝুঁকি',
          subtitle: englishMode 
            ? 'Cash drawer balance and minimum reserve review' 
            : 'ক্যাশ বাক্স ও ব্যাংক তারল্যের সঠিক হিসাব',
          icon: Wallet,
          targetUrl: '/app/money',
          targetLabel: englishMode ? 'View Money Accounts' : 'টাকার খাতা দেখুন',
          text: englishMode ? textEn : textBn
        };
      }
      case 'receiving': {
        const creditBdt = brief?.unapplied_credit_amount_bdt ?? 0;
        const textEn = creditBdt > 0
          ? `Receiving and supplier update. Total unapplied supplier credit notes amount to ${Math.round(creditBdt)} Taka awaiting bill deduction.`
          : 'Receiving update. There are no pending supplier discrepancies or unapplied credit notes.';
        const textBn = creditBdt > 0
          ? `মাল ও সরবরাহকারী আপডেট। সরবরাহকারীদের থেকে মোট ${Math.round(creditBdt)} টাকা সমমূল্যের পাওনা বা ক্রেডিট নোট সমন্বয় বাকি আছে।`
          : 'মাল ও সরবরাহকারী আপডেট। নতুন কোনো অনিষ্পন্ন ক্রেডিট নোট বা চালানের গরমিল বাকি নেই।';
        return {
          title: englishMode ? 'Receiving & Vendor Debts' : 'মাল ও মহাজনের খাতা',
          subtitle: englishMode 
            ? 'Delivery discrepancies and claimable credits' 
            : 'চালান রিসিভিং ও দাবিযোগ্য ক্রেডিট',
          icon: Package,
          targetUrl: '/app/receiving',
          targetLabel: englishMode ? 'Go to Receiving Desk' : 'রিসিভিং পেজে যান',
          text: englishMode ? textEn : textBn
        };
      }
    }
  };

  const currentDetails = getCategoryDetails(activeCategory, isEnglish);

  // Stop audio immediately and cancel all callbacks to prevent parallel speech or background audio on close
  const stopAudio = () => {
    // Invalidate any ongoing asynchronous audio callbacks
    playbackSessionRef.current += 1;

    if (audioRef.current) {
      const el = audioRef.current;
      audioRef.current = null;
      try {
        el.pause();
        el.oncanplaythrough = null;
        el.onended = null;
        el.onerror = null;
        el.src = '';
        el.load();
      } catch {
        // ignore unload quirks in test environments
      }
    }
    setIsPlaying(false);
    setAudioLoading(false);
  };

  // Clean up on component unmount
  useEffect(() => {
    return () => {
      stopAudio();
    };
  }, []);

  // Keyboard shortcut: Escape closes modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleCloseModal();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Play natural neural audio for a specific text with single-instance enforcement
  const playVoice = (text: string, currentVoice: VoiceKey = voice, currentSpeed: string = speed) => {
    // 1. Force stop and clear ANY prior audio instance immediately!
    stopAudio();
    setPlaybackError(null);
    setAudioLoading(true);

    // 2. Capture the fresh session ID after stopAudio incremented it
    const thisSessionId = playbackSessionRef.current;

    const encodedText = encodeURIComponent(text);
    const url = `/api/v1/voice/speak?text=${encodedText}&voice=${currentVoice}&rate=${currentSpeed}`;

    const audio = new Audio(url);
    audioRef.current = audio;

    audio.oncanplaythrough = () => {
      // If modal was closed OR user switched to another voice/option in the meantime, ABORT!
      if (thisSessionId !== playbackSessionRef.current || !isOpenRef.current) {
        audio.oncanplaythrough = null;
        audio.pause();
        audio.src = '';
        try { audio.load(); } catch {}
        return;
      }

      setAudioLoading(false);
      audio.play().then(() => {
        if (thisSessionId === playbackSessionRef.current && isOpenRef.current) {
          setIsPlaying(true);
        } else {
          audio.pause();
          audio.src = '';
          try { audio.load(); } catch {}
        }
      }).catch(err => {
        console.warn('Audio play error:', err);
        setPlaybackError(isEnglish ? 'Audio playback blocked or connection error.' : 'অডিও প্লে করতে অনুমতি প্রয়োজন বা সংযোগে সমস্যা।');
        setIsPlaying(false);
        setAudioLoading(false);
      });
    };

    audio.onended = () => {
      if (thisSessionId === playbackSessionRef.current) {
        setIsPlaying(false);
      }
    };

    audio.onerror = () => {
      if (thisSessionId === playbackSessionRef.current) {
        setPlaybackError(isEnglish ? 'Unable to load neural audio from server.' : 'ভয়েস সার্ভার থেকে অডিও লোড করা যায়নি।');
        setIsPlaying(false);
        setAudioLoading(false);
      }
    };
  };

  const handleTogglePlay = () => {
    if (isPlaying) {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      setIsPlaying(false);
    } else {
      if (audioRef.current && audioRef.current.currentTime > 0 && !audioRef.current.ended) {
        audioRef.current.play();
        setIsPlaying(true);
      } else {
        playVoice(currentDetails.text, voice, speed);
      }
    }
  };

  const handleReplay = () => {
    playVoice(currentDetails.text, voice, speed);
  };

  const handleSelectCategory = (cat: CategoryKey) => {
    setActiveCategory(cat);
    const details = getCategoryDetails(cat, isEnglish);
    // Automatically play the newly selected notification in natural voice without overlap
    playVoice(details.text, voice, speed);
  };

  const handleVoiceChange = (newVoice: VoiceKey) => {
    setVoice(newVoice);
    const newIsEnglish = newVoice.startsWith('en-US');
    const details = getCategoryDetails(activeCategory, newIsEnglish);
    playVoice(details.text, newVoice, speed);
  };

  const handleToggleLanguageMode = (targetEn: boolean) => {
    const newVoice: VoiceKey = targetEn ? 'en-US-GuyNeural' : 'bn-BD-PradeepNeural';
    handleVoiceChange(newVoice);
  };

  const handleOpenModal = () => {
    setIsOpen(true);
    // Autoplay the default overview on opening HUD
    const details = getCategoryDetails(activeCategory, isEnglish);
    playVoice(details.text, voice, speed);
  };

  const handleCloseModal = () => {
    setIsOpen(false);
    stopAudio();
  };

  const handleActionNavigate = (url: string) => {
    stopAudio();
    setIsOpen(false);
    navigate(url);
  };

  return (
    <>
      {/* Floating Orb Trigger Button */}
      <div 
        className="vno-floating-container" 
        title={isEnglish ? 'Shongoti Neural Voice Bulletin' : 'সংগতি নিউরাল ভয়েস বুলেটিন'}
      >
        <span className="vno-quick-label">
          {isPlaying 
            ? (isEnglish ? 'Speaking…' : 'কথা বলছে…') 
            : (isEnglish ? 'Voice Bulletin' : 'ভয়েস বুলেটিন')}
        </span>
        <button
          className={`vno-orb-trigger ${isPlaying ? 'vno-playing' : ''}`}
          onClick={handleOpenModal}
          aria-label={isEnglish ? 'Listen to Voice Notification' : 'ভয়েস নোটিফিকেশন শুনুন'}
        >
          <div className="vno-orb-pulse-ring" />
          <div className="vno-orb-pulse-ring" />
          {isPlaying ? <Volume2 size={26} /> : <Radio size={24} />}
          {totalOpenCount > 0 && (
            <span className="vno-badge">{totalOpenCount}</span>
          )}
        </button>
      </div>

      {/* Holographic Futuristic HUD Modal */}
      {isOpen && (
        <div 
          className="vno-hud-backdrop"
          onClick={(e) => {
            if (e.target === e.currentTarget) handleCloseModal();
          }}
        >
          <div 
            className="vno-hud-panel" 
            role="dialog" 
            aria-modal="true" 
            aria-label={isEnglish ? 'Shongoti Voice Bulletin' : 'সংগতি ভয়েস বুলেটিন'}
          >
            
            {/* Header */}
            <header className="vno-hud-header">
              <div className="vno-hud-title-box">
                <div className="vno-ai-pulse-dot" />
                <div>
                  <h3>
                    <Volume2 size={20} className="text-cyan-400" />
                    {isEnglish ? 'Shongoti Neural Voice Bulletin' : 'সংগতি নিউরাল ভয়েস বুলেটিন'}
                  </h3>
                  <div className="vno-hud-subtext">
                    {isEnglish ? 'AI NATIVE VOICE INTELLIGENCE HUD' : 'AI NATIVE BANGLA & ENGLISH INTELLIGENCE HUD'}
                  </div>
                </div>
              </div>

              <div className="vno-header-controls">
                {/* Language Switch Pills */}
                <div className="vno-lang-pills">
                  <button
                    className={`vno-lang-pill ${!isEnglish ? 'vno-active' : ''}`}
                    onClick={() => handleToggleLanguageMode(false)}
                    title="বাংলা কণ্ঠ"
                  >
                    🇧🇩 বাংলা
                  </button>
                  <button
                    className={`vno-lang-pill ${isEnglish ? 'vno-active' : ''}`}
                    onClick={() => handleToggleLanguageMode(true)}
                    title="English Voice"
                  >
                    🇺🇸 English
                  </button>
                </div>

                {/* Voice Selector Dropdown */}
                <select 
                  className="vno-voice-select"
                  value={voice}
                  onChange={(e) => handleVoiceChange(e.target.value as VoiceKey)}
                  aria-label={isEnglish ? 'Select Voice' : 'কণ্ঠ নির্বাচন করুন'}
                >
                  <optgroup label="🇧🇩 বাংলা (Bangla)">
                    <option value="bn-BD-PradeepNeural">🎙️ প্রদীপ (পুরুষ কণ্ঠ)</option>
                    <option value="bn-BD-NabanitaNeural">🎙️ নবানিতা (নারী কণ্ঠ)</option>
                  </optgroup>
                  <optgroup label="🇺🇸 English">
                    <option value="en-US-GuyNeural">🎙️ Guy (Natural Male)</option>
                    <option value="en-US-JennyNeural">🎙️ Jenny (Natural Female)</option>
                  </optgroup>
                </select>

                <button 
                  className="vno-close-btn"
                  onClick={handleCloseModal}
                  aria-label={isEnglish ? 'Close' : 'বন্ধ করুন'}
                >
                  <X size={20} />
                </button>
              </div>
            </header>

            {/* Notification Category Grid */}
            <div>
              <div className="vno-categories-title">
                {isEnglish ? 'Select a notification bulletin channel:' : 'কোন বিষয়ে শুনতে চান নির্বাচন করুন:'}
              </div>
              <div className="vno-category-grid">
                {(['overview', 'urgent', 'cash', 'receiving'] as CategoryKey[]).map(cat => {
                  const details = getCategoryDetails(cat, isEnglish);
                  const Icon = details.icon;
                  const isActive = activeCategory === cat;
                  return (
                    <button
                      key={cat}
                      className={`vno-cat-card ${isActive ? 'vno-active' : ''}`}
                      onClick={() => handleSelectCategory(cat)}
                    >
                      <div className="vno-cat-header">
                        <div className="vno-cat-icon-title">
                          <Icon size={16} />
                          <span>{details.title}</span>
                        </div>
                        {cat === 'urgent' && urgentCount > 0 && (
                          <span className="vno-cat-badge vno-urgent">
                            {urgentCount} {isEnglish ? 'Urgent' : 'জরুরি'}
                          </span>
                        )}
                      </div>
                      <div className="vno-cat-desc">{details.subtitle}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Sound Wave & Equalizer Area */}
            <div className="vno-equalizer-container">
              <div className="vno-equalizer-display">
                {Array.from({ length: 24 }).map((_, i) => (
                  <div
                    key={i}
                    className={`vno-bar ${isPlaying ? 'vno-animating' : ''}`}
                    style={{
                      animationDelay: `${(i * 0.05).toFixed(2)}s`,
                      height: isPlaying ? undefined : `${(Math.sin(i) * 6 + 10)}px`
                    }}
                  />
                ))}
              </div>

              {/* Playback Controls & Voice Speed */}
              <div className="vno-audio-controls">
                <div className="vno-playback-group">
                  <button 
                    className="vno-play-btn"
                    onClick={handleTogglePlay}
                    disabled={audioLoading}
                    aria-label={isPlaying ? (isEnglish ? 'Pause' : 'বিরতি') : (isEnglish ? 'Play' : 'প্লে করুন')}
                  >
                    {isPlaying ? <Pause size={20} /> : <Play size={20} style={{ marginLeft: 2 }} />}
                  </button>

                  <button 
                    className="vno-secondary-btn"
                    onClick={handleReplay}
                    disabled={audioLoading}
                  >
                    <RotateCcw size={14} />
                    <span>{isEnglish ? 'Replay' : 'আবার শুনুন'}</span>
                  </button>
                </div>

                <div className="vno-speed-group">
                  <span>{isEnglish ? 'Speed:' : 'গতি:'}</span>
                  {[
                    { label: isEnglish ? '0.9x' : '০.৯x', val: '-10%' },
                    { label: isEnglish ? '1.0x' : '১.০x', val: '+0%' },
                    { label: isEnglish ? '1.1x' : '১.১x', val: '+10%' }
                  ].map(s => (
                    <button
                      key={s.val}
                      className={`vno-speed-btn ${speed === s.val ? 'vno-active' : ''}`}
                      onClick={() => {
                        setSpeed(s.val);
                        playVoice(currentDetails.text, voice, s.val);
                      }}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Spoken Subtitle Card */}
            <div className="vno-subtitle-card">
              <div className="vno-subtitle-label">
                <Radio size={14} />
                <span>
                  {audioLoading 
                    ? (isEnglish ? 'Synthesizing Neural Audio…' : 'অডিও প্রস্তুত হচ্ছে…') 
                    : isPlaying 
                    ? (isEnglish ? 'AI Neural Voice Speaking' : 'AI ভয়েস সরাসরি বলছে') 
                    : (isEnglish ? 'Notification Transcript' : 'বিজ্ঞপ্তি বিবরণ')}
                </span>
              </div>
              <p className="vno-subtitle-text">
                {currentDetails.text}
              </p>
              {playbackError && (
                <small style={{ color: '#f87171', marginTop: 4 }}>
                  {playbackError}
                </small>
              )}
            </div>

            {/* Footer with Direct Action Link */}
            <footer className="vno-hud-footer">
              <div className="vno-status-hint">
                <Sparkles size={14} />
                <span>
                  {isEnglish 
                    ? 'Powered by Microsoft Azure Neural Speech (Studio Quality)' 
                    : 'মাইক্রোসফট অ্যাজিউর নিউরাল ভয়েস প্রযুক্তিতে চালিত'}
                </span>
              </div>

              <button
                className="vno-action-btn"
                onClick={() => handleActionNavigate(currentDetails.targetUrl)}
              >
                <span>{currentDetails.targetLabel}</span>
                <ArrowRight size={15} />
              </button>
            </footer>

          </div>
        </div>
      )}
    </>
  );
}
