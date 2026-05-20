import { useState } from 'react'

const upcomingMatch = {
  team1: 'CSK',
  team2: 'RCB',
  team2Color: 'bg-red-700',
  venue: 'M. Chinnaswamy Stadium, Bengaluru',
  date: 'Sunday, 25 May 2025',
  time: '7:30 PM IST',
  tournament: 'IPL 2025',
}

const loadSteps = [
  'Scraping pitch report from ESPNcricinfo...',
  'Cross-referencing Cricbuzz pitch report...',
  'Fetching weather forecast...',
  'Loading player profiles for both XIs...',
  'Running ML weakness detection models...',
  'Running matchup predictor...',
  'Generating Gemini match insights...',
  '✅ Report ready!',
]

export default function HomePage() {
  const [loading, setLoading] = useState(false)
  const [loadStep, setLoadStep] = useState(-1)
  const [done, setDone] = useState(false)

  const handleStartAnalysis = async () => {
    setLoading(true)
    for (let i = 0; i < loadSteps.length; i++) {
      setLoadStep(i)
      await new Promise(r => setTimeout(r, 700))
    }
    setDone(true)
  }

  return (
    <div className="min-h-screen bg-csk-dark flex flex-col">

      {/* ── Header ── */}
      <header className="border-b border-csk-yellow/20 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-11 h-11 rounded-full bg-csk-yellow flex items-center justify-center shadow-[0_0_16px_rgba(249,168,37,0.5)]">
            <span className="text-csk-navy font-black text-sm">CSK</span>
          </div>
          <div>
            <div className="text-csk-yellow font-black text-lg tracking-tight leading-none">CricketIQ X</div>
            <div className="text-white/40 text-xs mt-0.5">Chennai Super Kings — AI Analyst Platform</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-white/40 text-xs">IPL 2025 · Live</span>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-16 gap-10">

        {/* Hero */}
        <div className="text-center">
          <h1 className="text-5xl font-black text-white tracking-tight mb-2">
            Thala for a <span className="text-csk-yellow">Reason</span>
          </h1>
          <p className="text-white/40 text-base max-w-md mx-auto">
            AI-powered tactical intelligence. Every match. Every decision. CSK's perspective only.
          </p>
        </div>

        {/* ── Match card ── */}
        {!loading && (
          <div className="w-full max-w-xl">
            <p className="text-white/30 text-xs uppercase tracking-widest text-center mb-3">Next Match</p>

            <div className="bg-csk-navy border border-csk-yellow/25 rounded-2xl p-8
                            shadow-[0_0_60px_rgba(249,168,37,0.07)]
                            hover:shadow-[0_0_80px_rgba(249,168,37,0.14)] transition-all duration-300">

              {/* Teams row */}
              <div className="flex items-center justify-center gap-8 mb-7">
                {/* CSK */}
                <div className="flex flex-col items-center gap-2">
                  <div className="w-16 h-16 rounded-full bg-csk-yellow flex items-center justify-center
                                  shadow-[0_0_24px_rgba(249,168,37,0.45)]">
                    <span className="text-csk-navy font-black text-base">CSK</span>
                  </div>
                  <span className="text-white text-xs font-semibold">Chennai Super Kings</span>
                </div>

                {/* VS */}
                <div className="flex flex-col items-center gap-2">
                  <span className="text-white/20 text-3xl font-black">VS</span>
                  <span className="text-csk-yellow text-[10px] font-bold border border-csk-yellow/40
                                   rounded px-2 py-0.5 tracking-wider">UPCOMING</span>
                </div>

                {/* RCB */}
                <div className="flex flex-col items-center gap-2">
                  <div className="w-16 h-16 rounded-full bg-red-800 flex items-center justify-center">
                    <span className="text-white font-black text-base">RCB</span>
                  </div>
                  <span className="text-white text-xs font-semibold">Royal Challengers</span>
                </div>
              </div>

              {/* Match info */}
              <div className="border-t border-white/8 pt-5 mb-7 space-y-1.5 text-center">
                <p className="text-white/45 text-sm">📍 {upcomingMatch.venue}</p>
                <p className="text-white/45 text-sm">📅 {upcomingMatch.date} &nbsp;·&nbsp; ⏰ {upcomingMatch.time}</p>
                <p className="text-white/45 text-sm">🏆 {upcomingMatch.tournament}</p>
              </div>

              {/* CTA */}
              <button
                onClick={handleStartAnalysis}
                className="w-full bg-csk-yellow hover:bg-csk-gold active:scale-95
                           text-csk-navy font-black text-lg py-4 rounded-xl
                           transition-all duration-200
                           shadow-[0_4px_24px_rgba(249,168,37,0.35)]
                           hover:shadow-[0_4px_36px_rgba(249,168,37,0.55)]"
              >
                🏏 &nbsp;Start Analysis
              </button>
            </div>
          </div>
        )}

        {/* ── Loading state ── */}
        {loading && !done && (
          <div className="w-full max-w-xl">
            <div className="bg-csk-navy border border-csk-yellow/25 rounded-2xl p-10 text-center">

              <div className="w-14 h-14 rounded-full border-2 border-csk-yellow bg-csk-yellow/10
                              flex items-center justify-center mx-auto mb-6 animate-spin">
                <span className="text-2xl">🏏</span>
              </div>

              <h2 className="text-white font-bold text-lg mb-8">Preparing match intelligence...</h2>

              <div className="space-y-3 text-left">
                {loadSteps.map((step, i) => (
                  <div key={i}
                    className={`flex items-center gap-3 transition-all duration-500
                      ${i <= loadStep ? 'opacity-100' : 'opacity-20'}`}>
                    <div className={`w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center
                      transition-all duration-300
                      ${i < loadStep
                        ? 'bg-csk-yellow'
                        : i === loadStep
                          ? 'bg-csk-yellow/40 animate-pulse'
                          : 'bg-white/10'}`}>
                      {i < loadStep && (
                        <span className="text-csk-navy text-[10px] font-black">✓</span>
                      )}
                    </div>
                    <span className={`text-sm ${i <= loadStep ? 'text-white' : 'text-white/30'}`}>
                      {step}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── Done state ── */}
        {done && (
          <div className="w-full max-w-xl">
            <div className="bg-csk-navy border border-green-500/40 rounded-2xl p-10 text-center">
              <div className="w-14 h-14 rounded-full bg-green-500/20 border-2 border-green-400
                              flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">✅</span>
              </div>
              <h2 className="text-white font-bold text-xl mb-2">Analysis Ready</h2>
              <p className="text-white/40 text-sm mb-8">
                CSK vs RCB · Full 5-page intelligence report generated
              </p>
              <button
                className="w-full bg-green-500 hover:bg-green-400 active:scale-95
                           text-white font-black text-lg py-4 rounded-xl
                           transition-all duration-200"
              >
                📊 &nbsp;Open Match Report
              </button>
            </div>
          </div>
        )}

      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-white/5 px-8 py-3 flex items-center justify-between">
        <span className="text-white/20 text-xs">CricketIQ X v1.0 · CSK Analyst Edition</span>
        <span className="text-white/20 text-xs">ML + Gemini AI · Built for CSK</span>
      </footer>

    </div>
  )
}