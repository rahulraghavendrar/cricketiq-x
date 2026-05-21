import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const images = ['/images/csk1.png','/images/csk2.png','/images/csk3.png','/images/csk4.png']

const match = {
  team1:'CSK', team1Full:'Chennai Super Kings',
  team2:'RCB', team2Full:'Royal Challengers Bengaluru',
  venue:'M. Chinnaswamy Stadium, Bengaluru',
  date:'Sunday, 25 May 2025', time:'7:30 PM IST',
  tournament:'TATA IPL 2025 · Match 58',
}

const steps = [
  { label:'Fetching pitch report from ESPNcricinfo', icon:'🌐' },
  { label:'Cross-referencing Cricbuzz conditions',   icon:'🔄' },
  { label:'Loading weather forecast',                icon:'🌤️' },
  { label:'Loading player profiles for both XIs',   icon:'👥' },
  { label:'Running weakness detection models',       icon:'🧠' },
  { label:'Running matchup predictor',               icon:'⚡' },
  { label:'Generating Gemini tactical insights',     icon:'✨' },
]

export default function HomePage() {
  const [phase, setPhase]   = useState('idle')
  const [step,  setStep]    = useState(-1)
  const [imgIdx, setImgIdx] = useState(0)
  const navigate = useNavigate()

  /* Image carousel — 15s per slide */
  useEffect(() => {
    const t = setInterval(() => setImgIdx(i => (i+1) % images.length), 15000)
    return () => clearInterval(t)
  }, [])

  const startAnalysis = async () => {
    setPhase('loading')
    for (let i = 0; i < steps.length; i++) {
      setStep(i)
      await new Promise(r => setTimeout(r, 750))
    }
    setPhase('ready')
  }

  return (
    <div className="min-h-screen relative overflow-hidden" style={{ background:'#0A0D1A' }}>

      {/* ── Sliding background images ── */}
      <div className="absolute inset-0 z-0">
        {images.map((src, i) => (
          <div key={i} style={{
            position:'absolute', inset:0,
            backgroundImage:`url(${src})`,
            backgroundSize:'cover', backgroundPosition:'center',
            transition:'opacity 2s ease-in-out',
            opacity: i === imgIdx ? 1 : 0,
          }} />
        ))}
        {/* Dark overlay so text is readable */}
        <div className="absolute inset-0"
          style={{ background:'linear-gradient(to bottom,rgba(10,13,26,0.65) 0%,rgba(10,13,26,0.80) 100%)' }} />
      </div>

      {/* ── Header ── */}
      <header className="relative z-10 border-b border-white/10 px-8 py-4 flex items-center justify-between backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center shadow-gold-md"
            style={{ background:'linear-gradient(135deg,#F9A825,#FFD600)' }}>
            <span className="text-csk-navy font-black text-xs">CSK</span>
          </div>
          <div>
            <p className="text-csk-gold font-black text-lg leading-none tracking-tight">CricketIQ X</p>
            <p className="text-white/40 text-[10px] mt-0.5">CSK Analyst Edition</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          <span className="text-white/40 text-xs">IPL 2025 · Season active</span>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="relative z-10 flex flex-col items-center justify-center px-6 py-16 min-h-[calc(100vh-70px)]">

        {/* Hero text */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 border border-csk-gold/30 rounded-full
                          px-4 py-1.5 mb-5 backdrop-blur-sm"
            style={{ background:'rgba(249,168,37,0.1)' }}>
            <span className="text-csk-gold text-xs font-bold uppercase tracking-widest">
              IPL 2025 · Match Analysis Platform
            </span>
          </div>
          <h1 className="font-display text-6xl font-black text-white leading-tight mb-3 drop-shadow-lg">
            Win the match<br/>
            <span className="text-csk-gold">before it starts.</span>
          </h1>
          <p className="text-white/50 text-lg max-w-md mx-auto">
            AI-powered tactical intelligence. Every player. Every matchup. Built for CSK.
          </p>
        </div>

        {/* ── Match card ── */}
        <div className="w-full max-w-xl">

          {phase === 'idle' && (
            <div className="rounded-3xl overflow-hidden shadow-gold-lg backdrop-blur-sm"
              style={{ background:'rgba(255,251,234,0.95)', border:'1px solid rgba(248,168,37,0.4)' }}>
              <div className="h-1" style={{ background:'linear-gradient(90deg,#F9A825,#FFD600,#FF8F00)' }} />
              <div className="p-8">

                <div className="flex items-center justify-between mb-7">
                  <span className="text-csk-dark/40 text-xs font-bold uppercase tracking-widest">Next match</span>
                  <span className="text-xs font-bold text-csk-amber bg-csk-muted border border-csk-border/50
                                   px-3 py-1 rounded-full">{match.tournament}</span>
                </div>

                {/* Teams */}
                <div className="flex items-center justify-center gap-10 mb-7">
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-20 h-20 rounded-2xl flex items-center justify-center shadow-gold-md"
                      style={{ background:'linear-gradient(135deg,#F9A825,#FFD600)' }}>
                      <span className="text-csk-navy font-black text-xl">CSK</span>
                    </div>
                    <p className="text-csk-dark font-bold text-sm">Chennai Super Kings</p>
                  </div>
                  <div className="w-12 h-12 rounded-full border-2 border-csk-border/40 bg-csk-warm
                                  flex items-center justify-center">
                    <span className="text-csk-dark/30 font-black text-sm">VS</span>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-20 h-20 rounded-2xl flex items-center justify-center"
                      style={{ background:'linear-gradient(135deg,#B91C1C,#7F1D1D)' }}>
                      <span className="text-white font-black text-xl">RCB</span>
                    </div>
                    <p className="text-csk-dark font-bold text-sm">Royal Challengers</p>
                  </div>
                </div>

                {/* Details */}
                <div className="bg-csk-warm rounded-2xl p-4 mb-6 space-y-1.5">
                  <p className="text-csk-dark/60 text-sm flex items-center gap-2">📍 {match.venue}</p>
                  <p className="text-csk-dark/60 text-sm flex items-center gap-4">
                    <span>📅 {match.date}</span><span>⏰ {match.time}</span>
                  </p>
                </div>

                <button onClick={startAnalysis}
                  className="w-full font-black text-lg py-4 rounded-2xl transition-all duration-200
                             active:scale-[0.98] text-csk-navy shadow-gold-md hover:shadow-gold-lg"
                  style={{ background:'linear-gradient(135deg,#F9A825,#FFD600,#FF8F00)' }}>
                  🏏 &nbsp;Start Match Analysis
                </button>
                <p className="text-center text-csk-dark/30 text-xs mt-3">
                  Scrapes live pitch report · Runs 6 ML models · Generates full tactical plan
                </p>
              </div>
            </div>
          )}

          {phase === 'loading' && (
            <div className="rounded-3xl overflow-hidden shadow-gold-lg backdrop-blur-sm"
              style={{ background:'rgba(255,251,234,0.95)', border:'1px solid rgba(248,168,37,0.4)' }}>
              <div className="h-1" style={{ background:'linear-gradient(90deg,#F9A825,#FFD600,#FF8F00)' }} />
              <div className="p-8">
                <div className="flex items-center gap-3 mb-8">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center animate-spin"
                    style={{ background:'linear-gradient(135deg,#F9A825,#FFD600)' }}>
                    <span className="text-csk-navy font-black">🏏</span>
                  </div>
                  <div>
                    <p className="text-csk-dark font-bold">Preparing intelligence report</p>
                    <p className="text-csk-dark/40 text-sm">CSK vs RCB · Bengaluru</p>
                  </div>
                </div>
                <div className="space-y-3">
                  {steps.map((s,i) => (
                    <div key={i} className={`flex items-center gap-3 transition-all duration-400
                        ${i <= step ? 'opacity-100' : 'opacity-25'}`}>
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-sm
                          ${i < step ? '' : i === step ? 'animate-pulse' : ''}`}
                        style={{
                          background: i < step ? 'linear-gradient(135deg,#F9A825,#FFD600)'
                            : i === step ? 'rgba(249,168,37,0.3)' : '#F3F4F6',
                          border: i === step ? '2px solid #F9A825' : 'none'
                        }}>
                        {i < step
                          ? <span className="text-csk-navy text-xs font-black">✓</span>
                          : <span>{s.icon}</span>}
                      </div>
                      <span className={`text-sm ${i <= step ? 'text-csk-dark font-medium' : 'text-csk-dark/40'}`}>
                        {s.label}
                      </span>
                      {i === step && <span className="ml-auto text-csk-amber text-xs font-semibold animate-pulse">Running...</span>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {phase === 'ready' && (
            <div className="rounded-3xl overflow-hidden shadow-gold-lg backdrop-blur-sm"
              style={{ background:'rgba(255,251,234,0.95)', border:'1px solid rgba(248,168,37,0.4)' }}>
              <div className="h-1" style={{ background:'linear-gradient(90deg,#F9A825,#FFD600,#FF8F00)' }} />
              <div className="p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-green-50 border-2 border-green-400
                                flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">✅</span>
                </div>
                <h2 className="text-csk-dark font-black text-2xl mb-1">Analysis Ready</h2>
                <p className="text-csk-dark/40 text-sm mb-6">CSK vs RCB · Full 5-page intelligence report</p>
                <div className="grid grid-cols-3 gap-3 mb-6">
                  {[
                    { label:'Win probability', value:'58%', color:'text-green-600' },
                    { label:'Pitch type',       value:'Flat', color:'text-csk-amber' },
                    { label:'Avg 1st innings',  value:'174', color:'text-csk-dark' },
                  ].map((m,i) => (
                    <div key={i} className="bg-csk-warm rounded-xl p-3 border border-csk-border/40">
                      <p className="text-csk-dark/40 text-[10px] uppercase tracking-wider mb-1">{m.label}</p>
                      <p className={`font-black text-xl ${m.color}`}>{m.value}</p>
                    </div>
                  ))}
                </div>
                <button onClick={() => navigate('/report')}
                  className="w-full font-black text-lg py-4 rounded-2xl transition-all active:scale-[0.98]
                             text-csk-navy shadow-gold-md hover:shadow-gold-lg"
                  style={{ background:'linear-gradient(135deg,#F9A825,#FFD600,#FF8F00)' }}>
                  📊 &nbsp;Open 5-Page Report
                </button>
              </div>
            </div>
          )}

          {/* Stats strip */}
          <div className="grid grid-cols-4 gap-3 mt-5">
            {[
              { label:'IPL seasons', value:'17' },
              { label:'Ball events', value:'1.5M' },
              { label:'ML models',   value:'6' },
              { label:'CSK vs RCB',  value:'54%' },
            ].map((s,i) => (
              <div key={i} className="rounded-2xl p-3 text-center backdrop-blur-sm"
                style={{ background:'rgba(255,251,234,0.15)', border:'1px solid rgba(255,255,255,0.15)' }}>
                <p className="text-white font-black text-lg">{s.value}</p>
                <p className="text-white/40 text-[10px] mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}