import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import LiveScoreTicker from '../components/LiveScoreTicker'
import ReportBg, { EventOverlay } from '../components/ReportBg'

const tabs = [
  { id:'summary', label:'Match Summary', icon:'📊' },
  { id:'players', label:'Players',       icon:'👥' },
  { id:'twin',    label:'Digital Twin',  icon:'⚡' },
  { id:'plan',    label:'Match Plan',    icon:'🎯' },
  { id:'chat',    label:'Live Chat',     icon:'💬' },
]

// Mock event — change to 'W','6','4','NB','FH','WD','1','2','3' to test
const DEMO_EVENT = null

export default function ReportPage() {
  const [active, setActive] = useState('summary')
  const [event,  setEvent]  = useState(DEMO_EVENT)
  const navigate = useNavigate()

  // Demo: cycle events every 8s for testing
  useEffect(() => {
    const events = ['6','W','4','FH','NB']
    let idx = 0
    const t = setInterval(() => {
      setEvent(events[idx % events.length])
      idx++
      setTimeout(() => setEvent(null), 3000)
    }, 8000)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="min-h-screen relative" style={{ background:'#FFFBEA' }}>
      <ReportBg />
      <EventOverlay event={event} />

      <div className="relative z-10">
        {/* ── Header ── */}
        <header style={{ background:'rgba(255,251,234,0.92)', backdropFilter:'blur(12px)',
                         borderBottom:'1px solid rgba(232,200,74,0.4)' }}
                className="sticky top-0 z-20">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
            <button onClick={() => navigate('/')}
              className="text-csk-dark/50 hover:text-csk-dark text-sm transition-colors flex items-center gap-1">
              ← Back
            </button>
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full flex items-center justify-center"
                style={{ background:'linear-gradient(135deg,#F9A825,#FFD600)' }}>
                <span className="text-csk-navy font-black text-[10px]">CSK</span>
              </div>
              <span className="text-csk-dark font-bold text-sm">CSK vs RCB · Match Analysis</span>
            </div>
            <LiveScoreTicker />
          </div>

          {/* Tabs */}
          <div className="max-w-7xl mx-auto px-6 flex gap-1 overflow-x-auto">
            {tabs.map(t => (
              <button key={t.id} onClick={() => setActive(t.id)}
                className={`flex items-center gap-1.5 px-4 py-3 text-sm font-semibold
                  whitespace-nowrap border-b-2 transition-all duration-200
                  ${active === t.id
                    ? 'border-csk-yellow text-csk-amber'
                    : 'border-transparent text-csk-dark/40 hover:text-csk-dark/70'}`}>
                <span>{t.icon}</span>{t.label}
              </button>
            ))}
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-8">
          {active === 'summary' && <SummaryPage />}
          {active === 'players' && <PlayersPage />}
          {active === 'twin'    && <TwinPage />}
          {active === 'plan'    && <PlanPage />}
          {active === 'chat'    && <ChatPage />}
        </main>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────
   PAGE 1 — MATCH SUMMARY
───────────────────────────────────────── */
function SummaryPage() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label:'CSK win probability', value:'58%',  sub:'Based on pitch + form',      color:'text-green-600' },
          { label:'Pitch type',          value:'Flat', sub:'Low bowling assistance',      color:'text-csk-amber' },
          { label:'Predicted avg score', value:'174',  sub:'1st innings benchmark',       color:'text-csk-dark'  },
          { label:'Dew factor',          value:'High', sub:'Evening session impact',      color:'text-blue-600'  },
        ].map((m,i) => (
          <div key={i} className="bg-white border border-csk-border/30 rounded-2xl p-5 shadow-card">
            <p className="text-csk-dark/40 text-xs uppercase tracking-wider mb-2">{m.label}</p>
            <p className={`font-black text-3xl ${m.color} mb-1`}>{m.value}</p>
            <p className="text-csk-dark/40 text-xs">{m.sub}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-csk-border/30 rounded-2xl p-6 shadow-card">
          <h3 className="font-bold text-csk-dark mb-4">Pitch conditions</h3>
          {[
            { label:'Spin assistance', val:31, color:'#f97316' },
            { label:'Pace assistance', val:48, color:'#3b82f6' },
            { label:'Batting ease',    val:72, color:'#22c55e' },
          ].map((b,i) => (
            <div key={i} className="mb-3">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-csk-dark/60">{b.label}</span>
                <span className="font-semibold text-csk-dark">{b.val}%</span>
              </div>
              <div className="h-2 bg-csk-warm rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-1000"
                  style={{ width:`${b.val}%`, background:b.color }} />
              </div>
            </div>
          ))}
        </div>

        <div className="bg-white border border-csk-border/30 rounded-2xl p-6 shadow-card">
          <h3 className="font-bold text-csk-dark mb-4">Head to head — IPL history</h3>
          <div className="flex items-center gap-3 mb-3">
            <div className="flex-1">
              <div className="flex justify-between text-sm mb-1">
                <span className="font-bold text-csk-amber">CSK</span>
                <span className="text-csk-dark/50">19 wins</span>
              </div>
              <div className="h-3 bg-csk-warm rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width:'54%', background:'linear-gradient(90deg,#F9A825,#FFD600)' }} />
              </div>
            </div>
            <span className="text-csk-dark/30 text-xs font-bold">vs</span>
            <div className="flex-1">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-csk-dark/50">16 wins</span>
                <span className="font-bold text-red-500">RCB</span>
              </div>
              <div className="h-3 bg-red-50 rounded-full overflow-hidden flex justify-end">
                <div className="h-full bg-red-400 rounded-full" style={{ width:'46%' }} />
              </div>
            </div>
          </div>
          <p className="text-csk-dark/40 text-xs text-center">35 matches played · CSK lead 54–46%</p>

          <div className="mt-4 border-t border-csk-border/20 pt-4 space-y-2">
            <p className="text-xs font-bold text-csk-dark/50 uppercase tracking-wider">Key matchups today</p>
            {[
              { a:'Jadeja', b:'Kohli', edge:'CSK', note:'Jadeja has dismissed Kohli 4× in IPL' },
              { a:'Pathirana', b:'Maxwell', edge:'CSK', note:'Maxwell averages 18 vs slinger' },
              { a:'Chahar', b:'Virat Kohli', edge:'CSK', note:'Away swing — Kohli dismissed 3×' },
            ].map((m,i) => (
              <div key={i} className="flex items-center gap-2 text-xs bg-csk-warm rounded-lg px-3 py-2">
                <span className="font-semibold text-csk-dark">{m.a}</span>
                <span className="text-csk-dark/30">vs</span>
                <span className="font-semibold text-red-600">{m.b}</span>
                <span className="ml-auto text-green-600 font-bold">{m.edge} edge</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-card"
        style={{ borderLeft:'4px solid #F9A825', border:'1px solid rgba(232,200,74,0.4)' }}>
        <div className="flex items-center gap-2 mb-3">
          <span>✨</span>
          <span className="text-xs font-bold text-csk-amber uppercase tracking-wider">Gemini AI Match Summary</span>
        </div>
        <p className="text-csk-dark/70 leading-relaxed italic text-sm">
          "Chinnaswamy is a flat surface with short boundaries — batting paradise but high dew risk
          in evening sessions. CSK's spin attack (Jadeja, Ashwin) will be significantly less effective
          in the 2nd innings due to dew, making toss crucial. If CSK wins toss, bowl first and defend
          a target of 175–185. Kohli's weakness against left-arm pace makes Siraj a watchout — use
          Ngidi early against Kohli. Ruturaj's cover drive will be key against RCB's seam attack in the powerplay."
        </p>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────
   PAGE 2 — PLAYERS (BOTH TEAMS)
───────────────────────────────────────── */
const cskSquad = [
  { name:'Ruturaj Gaikwad',     role:'BAT',  risk:'LOW', type:'bat',  hand:'RHB' },
  { name:'Devon Conway',        role:'BAT',  risk:'MED', type:'bat',  hand:'LHB' },
  { name:'Moeen Ali',           role:'AR',   risk:'LOW', type:'bat',  hand:'RHB' },
  { name:'Shivam Dube',         role:'AR',   risk:'MED', type:'bat',  hand:'LHB' },
  { name:'MS Dhoni',            role:'WK',   risk:'LOW', type:'bat',  hand:'RHB' },
  { name:'Ravindra Jadeja',     role:'AR',   risk:'LOW', type:'bowl', hand:'LHB' },
  { name:'Deepak Chahar',       role:'BOWL', risk:'MED', type:'bowl', hand:'RHB' },
  { name:'Matheesha Pathirana', role:'BOWL', risk:'LOW', type:'bowl', hand:'RHB' },
  { name:'Shardul Thakur',      role:'AR',   risk:'MED', type:'bowl', hand:'RHB' },
  { name:'Mitchell Santner',    role:'AR',   risk:'LOW', type:'bowl', hand:'LHB' },
  { name:'Tushar Deshpande',    role:'BOWL', risk:'HIGH',type:'bowl', hand:'RHB' },
]

const rcbSquad = [
  { name:'Virat Kohli',    role:'BAT',  risk:'HIGH', type:'bat',  hand:'RHB' },
  { name:'Faf du Plessis', role:'BAT',  risk:'MED',  type:'bat',  hand:'RHB' },
  { name:'Glenn Maxwell',  role:'AR',   risk:'MED',  type:'bat',  hand:'RHB' },
  { name:'Rajat Patidar',  role:'BAT',  risk:'LOW',  type:'bat',  hand:'RHB' },
  { name:'Dinesh Karthik', role:'WK',   risk:'MED',  type:'bat',  hand:'RHB' },
  { name:'Jasprit Bumrah', role:'BOWL', risk:'HIGH', type:'bowl', hand:'RHB' },
  { name:'Mohammed Siraj', role:'BOWL', risk:'MED',  type:'bowl', hand:'RHB' },
  { name:'Josh Hazlewood', role:'BOWL', risk:'MED',  type:'bowl', hand:'RHB' },
  { name:'Wanindu Hasaranga',role:'AR', risk:'LOW',  type:'bowl', hand:'RHB' },
  { name:'Shahbaz Ahmed',  role:'AR',   risk:'LOW',  type:'bat',  hand:'LHB' },
  { name:'Anuj Rawat',     role:'WK',   risk:'LOW',  type:'bat',  hand:'LHB' },
]

function PlayersPage() {
  const [selected, setSelected] = useState(null)
  const [team, setTeam]         = useState('csk')

  const squad = team === 'csk' ? cskSquad : rcbSquad
  const riskColor = { LOW:'bg-green-100 text-green-700', MED:'bg-yellow-100 text-yellow-700', HIGH:'bg-red-100 text-red-700' }
  const roleColor = { BAT:'bg-blue-100 text-blue-700', BOWL:'bg-purple-100 text-purple-700', AR:'bg-orange-100 text-orange-700', WK:'bg-teal-100 text-teal-700' }

  return (
    <div className="space-y-4">
      {/* Team toggle */}
      <div className="flex gap-2 mb-2">
        {[{id:'csk',label:'CSK Playing XI'},{id:'rcb',label:'RCB Playing XI'}].map(t => (
          <button key={t.id} onClick={() => { setTeam(t.id); setSelected(null) }}
            className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all
              ${team === t.id
                ? 'text-csk-navy shadow-gold-sm'
                : 'bg-white border border-csk-border/40 text-csk-dark/60 hover:text-csk-dark'}`}
            style={team === t.id
              ? { background:'linear-gradient(135deg,#F9A825,#FFD600)' }
              : {}}>
            {t.label}
          </button>
        ))}
      </div>
      <p className="text-csk-dark/40 text-sm">Click any player to view full profile, weaknesses, and today's advice</p>

      <div className="space-y-2">
        {squad.map((p,i) => (
          <div key={i}>
            <button onClick={() => setSelected(selected === i ? null : i)}
              className={`w-full flex items-center gap-4 p-4 rounded-2xl border text-left transition-all
                ${selected === i
                  ? 'shadow-gold-sm'
                  : 'bg-white border-csk-border/30 shadow-card hover:shadow-card-hover'}`}
              style={selected === i ? { background:'#FFFBEA', borderColor:'#F9A825' } : {}}>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{ background:'linear-gradient(135deg,#F9A825,#FFD600)' }}>
                <span className="text-csk-navy font-black text-xs">
                  {p.name.split(' ').map(n=>n[0]).join('').slice(0,2)}
                </span>
              </div>
              <p className="font-semibold text-csk-dark text-sm flex-1">{p.name}</p>
              <span className="text-csk-dark/40 text-xs">{p.hand}</span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${roleColor[p.role]}`}>{p.role}</span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${riskColor[p.risk]}`}>{p.risk} RISK</span>
              <span className="text-csk-dark/30">{selected === i ? '▲' : '▼'}</span>
            </button>

            {selected === i && (
              <div className="bg-white border border-csk-yellow/40 border-t-0 rounded-b-2xl p-6">
                {p.type === 'bat'
                  ? <BatsmanProfile name={p.name} isCsk={team==='csk'} />
                  : <BowlerProfile  name={p.name} isCsk={team==='csk'} />}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function BatsmanProfile({ name, isCsk }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-csk-warm rounded-xl p-3">
          <p className="text-csk-dark/50 text-xs font-semibold mb-2 uppercase tracking-wider">Wagon Wheel (predicted)</p>
          <WagonWheel />
        </div>
        <div className="bg-csk-warm rounded-xl p-3">
          <p className="text-csk-dark/50 text-xs font-semibold mb-2 uppercase tracking-wider">Ball Map (predicted)</p>
          <BallMap />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {[
          { label:'vs Spin SR',   value:'112' },
          { label:'vs Pace SR',   value:'134' },
          { label:'Powerplay SR', value:'118' },
          { label:'Middle SR',    value:'124' },
          { label:'Death SR',     value:'142' },
          { label:'Pressure idx', value:'0.72'},
        ].map((s,i) => (
          <div key={i} className="bg-csk-light rounded-xl p-3 text-center border border-csk-border/30">
            <p className="text-csk-dark/40 text-[10px] uppercase tracking-wider mb-1">{s.label}</p>
            <p className="text-csk-dark font-black text-lg">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-red-50 border border-red-200 rounded-xl p-4">
        <p className="text-red-700 font-bold text-sm mb-1">⚠ Primary weakness — 87% confidence</p>
        <p className="text-red-600 text-sm">Short ball outside off stump. Dismissed 4× this way vs RCB bowlers. Siraj's bouncer is key threat today on this surface.</p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-xl p-4">
        <p className="text-green-700 font-bold text-sm mb-1">✅ Primary strength</p>
        <p className="text-green-700 text-sm">Cover drive and flick — exploits width on off side and any deviation to leg. Attack Chahal through covers in middle overs.</p>
      </div>

      {isCsk ? (
        <div className="rounded-xl p-4" style={{ background:'#FFFBEA', border:'1px solid #F9A825' }}>
          <p className="text-csk-amber font-bold text-xs uppercase tracking-wider mb-2">✨ Gemini · Batting advice for today</p>
          <p className="text-csk-dark/70 text-sm leading-relaxed italic">
            "Play through covers freely against Siraj in the powerplay. Avoid the pull shot against Bumrah.
            Attack Chahal with the sweep in middle overs. Watch for Siraj's 3rd-over bouncer — he's bowled it 6× and gotten you twice.
            Today's pitch favours driving — stay on the front foot."
          </p>
        </div>
      ) : (
        <div className="rounded-xl p-4" style={{ background:'#FEF2F2', border:'1px solid #FECACA' }}>
          <p className="text-red-600 font-bold text-xs uppercase tracking-wider mb-2">🎯 CSK bowling plan vs this batsman</p>
          <p className="text-red-700 text-sm leading-relaxed">
            "Bowl Chahar from pavilion end — away swing, 4th stump line, full length. Set slip + gully.
            Follow up with Jadeja over the wicket, targeting the rough outside off.
            Avoid full tosses — this batter punishes anything in the slot."
          </p>
        </div>
      )}
    </div>
  )
}

function BowlerProfile({ name, isCsk }) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-csk-warm rounded-xl p-3">
          <p className="text-csk-dark/50 text-xs font-semibold mb-2 uppercase tracking-wider">Pitch map (predicted)</p>
          <PitchMap />
        </div>
        <div className="bg-csk-warm rounded-xl p-3">
          <p className="text-csk-dark/50 text-xs font-semibold mb-2 uppercase tracking-wider">Economy by phase</p>
          <PhaseChart />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {[
          { label:'PP Economy',  value:'7.2' },
          { label:'Mid Economy', value:'8.1' },
          { label:'Death Eco',   value:'9.4' },
          { label:'Yorker %',    value:'38%' },
          { label:'Wicket rate', value:'1/18'},
          { label:'Predictab.',  value:'Low' },
        ].map((s,i) => (
          <div key={i} className="bg-csk-light rounded-xl p-3 text-center border border-csk-border/30">
            <p className="text-csk-dark/40 text-[10px] uppercase tracking-wider mb-1">{s.label}</p>
            <p className="text-csk-dark font-black text-lg">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-red-50 border border-red-200 rounded-xl p-4">
        <p className="text-red-700 font-bold text-sm mb-1">⚠ Weakness — length to avoid</p>
        <p className="text-red-600 text-sm">Back of length on flat pitches leaks boundaries. Economy goes to 11+ when bowling short of good length at Chinnaswamy.</p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-xl p-4">
        <p className="text-green-700 font-bold text-sm mb-1">✅ Best length today</p>
        <p className="text-green-700 text-sm">Full-pitched yorker and good-length deliveries. Gets 74% of wickets when landing in the good-length zone (6–8 metres).</p>
      </div>

      {isCsk ? (
        <div className="rounded-xl p-4" style={{ background:'#FFFBEA', border:'1px solid #F9A825' }}>
          <p className="text-csk-amber font-bold text-xs uppercase tracking-wider mb-2">✨ Gemini · Bowling plan for today</p>
          <p className="text-csk-dark/70 text-sm leading-relaxed italic">
            "Bowl fuller lengths on this flat surface. Use your yorker in death overs — this pitch rewards it.
            Target the stumps against left-handers. Against Kohli specifically: full, 4th stump,
            away swing from pavilion end. Avoid anything that could be driven through covers."
          </p>
        </div>
      ) : (
        <div className="rounded-xl p-4" style={{ background:'#FEF2F2', border:'1px solid #FECACA' }}>
          <p className="text-red-600 font-bold text-xs uppercase tracking-wider mb-2">🎯 CSK batting plan vs this bowler</p>
          <p className="text-red-700 text-sm leading-relaxed">
            "Ruturaj should drive through covers off any full delivery outside off.
            Dhoni and Dube must look to attack the 5th or 6th ball of any over.
            Watch for the yorker — play it late and dig it out, don't premeditate."
          </p>
        </div>
      )}
    </div>
  )
}

/* ─────────────────────────────────────────
   PAGE 3 — DIGITAL TWIN
───────────────────────────────────────── */
function TwinPage() {
  const [ran,    setRan]    = useState(false)
  const [batter, setBatter] = useState('Ruturaj Gaikwad')
  const [bowler, setBowler] = useState('Jasprit Bumrah')
  const [balls,  setBalls]  = useState(12)
  const [seed,   setSeed]   = useState(0)

  const simulate = () => { setSeed(Math.random()); setRan(true) }

  // Different outputs based on seed
  const sr   = Math.round(80  + seed * 80)
  const disp = Math.round(15  + seed * 40)
  const bdry = Math.round(15  + seed * 25)
  const dot  = Math.round(25  + seed * 30)

  const ballOutcomes = Array.from({ length: balls }, (_, i) => {
    const r = Math.random()
    if (r < 0.35) return 'dot'
    if (r < 0.55) return '1'
    if (r < 0.65) return '2'
    if (r < 0.80) return '4'
    if (r < 0.88) return '6'
    return 'W'
  })

  const outcomeStyle = {
    dot: 'bg-gray-100 text-gray-500',
    '1': 'bg-yellow-100 text-yellow-700',
    '2': 'bg-yellow-200 text-yellow-800',
    '4': 'bg-green-100 text-green-700',
    '6': 'bg-green-200 text-green-800 font-black',
    'W': 'bg-red-100 text-red-700 font-black',
  }

  return (
    <div className="space-y-6">
      <div className="bg-white border border-csk-border/30 rounded-2xl p-6 shadow-card">
        <h2 className="font-bold text-csk-dark text-lg mb-1">Digital Twin Simulator</h2>
        <p className="text-csk-dark/40 text-sm mb-6">Simulate any matchup — every run gives a different result</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-csk-dark/60 text-xs font-semibold uppercase tracking-wider mb-1.5 block">CSK Player</label>
            <select value={batter} onChange={e => setBatter(e.target.value)}
              className="w-full bg-csk-warm border border-csk-border/50 rounded-xl px-4 py-3
                         text-csk-dark font-medium text-sm focus:outline-none focus:border-csk-yellow">
              {cskSquad.filter(p=>p.type==='bat').map(p=><option key={p.name}>{p.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-csk-dark/60 text-xs font-semibold uppercase tracking-wider mb-1.5 block">Opponent Bowler</label>
            <select value={bowler} onChange={e => setBowler(e.target.value)}
              className="w-full bg-csk-warm border border-csk-border/50 rounded-xl px-4 py-3
                         text-csk-dark font-medium text-sm focus:outline-none focus:border-csk-yellow">
              {rcbSquad.filter(p=>p.type==='bowl').map(p=><option key={p.name}>{p.name}</option>)}
            </select>
          </div>
        </div>

        <div className="mb-5">
          <label className="text-csk-dark/60 text-xs font-semibold uppercase tracking-wider mb-1.5 block">
            Balls to simulate: {balls}
          </label>
          <input type="range" min="6" max="30" step="1" value={balls}
            onChange={e => setBalls(+e.target.value)}
            className="w-full accent-csk-yellow" />
        </div>

        <button onClick={simulate}
          className="w-full font-black text-lg py-4 rounded-2xl transition-all active:scale-[0.98]
                     text-csk-navy shadow-gold-md hover:shadow-gold-lg"
          style={{ background:'linear-gradient(135deg,#F9A825,#FFD600,#FF8F00)' }}>
          ⚡ Run Simulation
        </button>
      </div>

      {ran && (
        <div className="bg-white border border-csk-border/30 rounded-2xl p-6 shadow-card space-y-5">
          <h3 className="font-bold text-csk-dark">{batter} vs {bowler} — {balls} balls</h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label:'Simulated SR',    value:sr,    unit:'',  color:'text-csk-dark' },
              { label:'Dismissal prob',  value:disp,  unit:'%', color:'text-red-500'  },
              { label:'Boundary prob',   value:bdry,  unit:'%', color:'text-green-600'},
              { label:'Dot ball prob',   value:dot,   unit:'%', color:'text-csk-amber'},
            ].map((m,i) => (
              <div key={i} className="bg-csk-warm rounded-xl p-4 text-center border border-csk-border/30">
                <p className="text-csk-dark/40 text-[10px] uppercase tracking-wider mb-1">{m.label}</p>
                <p className={`font-black text-2xl ${m.color}`}>{m.value}{m.unit}</p>
              </div>
            ))}
          </div>

          {/* Ball timeline */}
          <div>
            <p className="text-csk-dark/50 text-xs font-semibold uppercase tracking-wider mb-2">Ball-by-ball simulation</p>
            <div className="flex flex-wrap gap-1.5">
              {ballOutcomes.map((o,i) => (
                <div key={i} className={`w-8 h-8 rounded-lg flex items-center justify-center
                  text-xs font-bold ${outcomeStyle[o]}`}>
                  {o === 'dot' ? '·' : o}
                </div>
              ))}
            </div>
          </div>

          {/* Simulation visuals */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-csk-warm rounded-xl p-3">
              <p className="text-csk-dark/50 text-xs font-semibold mb-2 uppercase tracking-wider">
                {batter} — Wagon Wheel
              </p>
              <WagonWheel seed={seed} />
            </div>
            <div className="bg-csk-warm rounded-xl p-3">
              <p className="text-csk-dark/50 text-xs font-semibold mb-2 uppercase tracking-wider">
                {bowler} — Pitch Map
              </p>
              <PitchMap seed={seed} />
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-xl p-4">
            <p className="text-green-700 font-bold text-sm mb-2">✅ CSK advice for this matchup</p>
            <p className="text-green-800 text-sm leading-relaxed">
              <strong>Shots to play:</strong> Cover drive, flick off pads on full deliveries.<br/>
              <strong>Shots to avoid:</strong> Pull shot — {bowler}'s bouncer gets extra pace.<br/>
              <strong>Best ball to attack:</strong> Full delivery on middle stump — drive through covers.
            </p>
          </div>

          <div className="rounded-xl p-4" style={{ background:'#FFFBEA', border:'1px solid #F9A825' }}>
            <p className="text-csk-amber font-bold text-xs uppercase tracking-wider mb-2">✨ Gemini simulation summary</p>
            <p className="text-csk-dark/70 text-sm italic leading-relaxed">
              "In {balls} balls, {batter} would score approximately {Math.round(sr*balls/100)} runs at a strike rate of {sr}.
              Dismissal probability is {disp < 25 ? 'low' : disp < 40 ? 'moderate' : 'high'} at {disp}% —
              primarily through {disp > 35 ? 'caught behind off the short ball' : 'LBW on the fuller length'}.
              The safest approach is to attack the {sr > 120 ? 'full deliveries and drive aggressively' : 'wider deliveries and rotate strike'}
              while respecting {bowler}'s best ball."
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

/* ─────────────────────────────────────────
   PAGE 4 — MATCH PLAN
───────────────────────────────────────── */
function PlanPage() {
  const [tab, setTab] = useState('bat')

  return (
    <div className="space-y-5">
      <div className="flex gap-2">
        {[{id:'bat',label:'🏏 If CSK bats first'},{id:'bowl',label:'🎳 If CSK bowls first'}].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all
              ${tab === t.id
                ? 'text-csk-navy shadow-gold-sm'
                : 'bg-white border border-csk-border/40 text-csk-dark/60 hover:text-csk-dark'}`}
            style={tab === t.id ? { background:'linear-gradient(135deg,#F9A825,#FFD600)' } : {}}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'bat' && (
        <div className="space-y-5">
          <div className="bg-white border border-csk-border/30 rounded-2xl p-6 shadow-card">
            <h3 className="font-bold text-csk-dark mb-4">Recommended batting order</h3>
            {[
              { pos:1, name:'Ruturaj Gaikwad', note:'Attack powerplay — cover drive vs Siraj' },
              { pos:2, name:'Devon Conway',    note:'Build platform — left-right combination with Ruturaj' },
              { pos:3, name:'Moeen Ali',       note:'Attack spin — sweep and slog-sweep Hasaranga' },
              { pos:4, name:'Shivam Dube',     note:'Power hitter — exploit leg side short boundary' },
              { pos:5, name:'MS Dhoni',        note:'Finisher — back yourself, helicopter shot in death' },
            ].map((b,i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-csk-warm rounded-xl mb-2">
                <span className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 text-sm font-black text-csk-navy"
                  style={{ background:'linear-gradient(135deg,#F9A825,#FFD600)' }}>
                  {b.pos}
                </span>
                <div>
                  <p className="text-csk-dark font-semibold text-sm">{b.name}</p>
                  <p className="text-csk-dark/50 text-xs">{b.note}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-4">
            {[
              { phase:'Powerplay', target:'50-60', overs:'Overs 1-6',   bg:'#EFF6FF' },
              { phase:'Middle',    target:'70-80', overs:'Overs 7-15',  bg:'#FFFBEA' },
              { phase:'Death',     target:'55-65', overs:'Overs 16-20', bg:'#F0FDF4' },
            ].map((p,i) => (
              <div key={i} className="rounded-2xl p-4 text-center border border-csk-border/30"
                style={{ background:p.bg }}>
                <p className="text-xs font-semibold text-csk-dark/50 uppercase tracking-wider">{p.overs}</p>
                <p className="text-csk-dark font-black text-2xl my-1">{p.target}</p>
                <p className="text-csk-dark/50 text-xs">{p.phase} target</p>
              </div>
            ))}
          </div>

          {/* Bowler to watch / attack */}
          <div className="bg-white border border-csk-border/30 rounded-2xl p-6 shadow-card">
            <h3 className="font-bold text-csk-dark mb-4">Bowler strategy</h3>
            <div className="space-y-3">
              {[
                { bowler:'Jasprit Bumrah',  action:'Respect',  reason:'0.92 dot ball rate — rotate strike, no big shots', color:'text-red-600', bg:'bg-red-50', border:'border-red-200' },
                { bowler:'Josh Hazlewood',  action:'Neutral',  reason:'Bowl him out in middle overs — punish width',       color:'text-yellow-600', bg:'bg-yellow-50', border:'border-yellow-200' },
                { bowler:'Mohammed Siraj',  action:'Attack',   reason:'Economy 9.4 vs left-handers — Dube and Conway go',  color:'text-green-600', bg:'bg-green-50', border:'border-green-200' },
                { bowler:'Wanindu Hasaranga',action:'Attack',  reason:'Sweep and slog-sweep — Moeen Ali should target him', color:'text-green-600', bg:'bg-green-50', border:'border-green-200' },
              ].map((b,i) => (
                <div key={i} className={`flex items-center gap-3 p-3 rounded-xl border ${b.bg} ${b.border}`}>
                  <div className="flex-1">
                    <p className="font-semibold text-csk-dark text-sm">{b.bowler}</p>
                    <p className="text-csk-dark/50 text-xs">{b.reason}</p>
                  </div>
                  <span className={`text-xs font-bold ${b.color}`}>{b.action}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl p-5 text-center shadow-gold-sm"
            style={{ background:'white', border:'2px solid #F9A825' }}>
            <p className="text-csk-dark/50 text-xs uppercase tracking-wider mb-1">Recommended target score</p>
            <p className="font-black text-6xl text-csk-yellow">178</p>
            <p className="text-csk-dark/40 text-sm mt-1">Venue avg + dew + RCB bowling strength</p>
          </div>

          <div className="rounded-2xl p-6 shadow-card"
            style={{ background:'white', borderLeft:'4px solid #F9A825', border:'1px solid rgba(232,200,74,0.4)' }}>
            <p className="text-csk-amber font-bold text-xs uppercase tracking-wider mb-3">✨ Gemini batting plan</p>
            <p className="text-csk-dark/70 text-sm italic leading-relaxed">
              "Chinnaswamy's short boundaries make aggressive batting from ball one the right approach.
              Ruturaj must dominate the powerplay — he averages 142 SR here. Avoid Bumrah's first spell
              by rotating strike. Dube is the match-winner if CSK are 100/3 at over 14 —
              let him bat through and target the leg-side boundary. Death target: 55+ in last 5."
            </p>
          </div>
        </div>
      )}

      {tab === 'bowl' && (
        <div className="space-y-5">
          {/* Key matchups — specific bowler vs batsman */}
          <div className="bg-white border border-csk-border/30 rounded-2xl p-6 shadow-card">
            <h3 className="font-bold text-csk-dark mb-4">Key bowling matchups — who bowls to whom</h3>
            <div className="space-y-3">
              {[
                { bowler:'Deepak Chahar',      batter:'Virat Kohli',    plan:'Away swing, pavilion end, 4th stump, full length. Dismissed him 3× this way.', edge:'High' },
                { bowler:'Matheesha Pathirana', batter:'Glenn Maxwell',  plan:'Slinger angle from around the wicket. Maxwell averages 18 vs this action.', edge:'High' },
                { bowler:'Ravindra Jadeja',     batter:'Faf du Plessis', plan:'Arm ball, over the wicket, targeting middle stump. Faf struggles vs left-arm spin.', edge:'Med'  },
                { bowler:'Mitchell Santner',    batter:'Rajat Patidar',  plan:'Toss it up, invite the drive. Patidar holes out to long-on vs spin (3×).', edge:'Med'  },
                { bowler:'Shardul Thakur',      batter:'Dinesh Karthik', plan:'Short of length, angled in. DK averages 21 vs pace moving in.', edge:'Med'  },
              ].map((m,i) => (
                <div key={i} className="p-4 bg-csk-warm rounded-xl border border-csk-border/30">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-bold text-csk-dark text-sm">{m.bowler}</span>
                    <span className="text-csk-dark/30 text-xs">→ bowl to →</span>
                    <span className="font-bold text-red-600 text-sm">{m.batter}</span>
                    <span className={`ml-auto text-xs font-bold ${m.edge === 'High' ? 'text-green-600' : 'text-yellow-600'}`}>
                      {m.edge} edge
                    </span>
                  </div>
                  <p className="text-csk-dark/60 text-xs">{m.plan}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border border-csk-border/30 rounded-2xl p-6 shadow-card">
            <h3 className="font-bold text-csk-dark mb-4">Over-by-over bowling rotation</h3>
            <div className="space-y-1.5">
              {[
                { overs:'1-2',   bowler:'Deepak Chahar',       plan:'New ball swing — target Kohli and Faf with away movement' },
                { overs:'3-4',   bowler:'Matheesha Pathirana',  plan:'Pace and bounce — restrict scoring rate' },
                { overs:'5-6',   bowler:'Shardul Thakur',       plan:'Back of length — dot ball pressure to finish powerplay' },
                { overs:'7-10',  bowler:'Ravindra Jadeja',      plan:'Contain — flat on length, no width outside off' },
                { overs:'11-13', bowler:'Mitchell Santner',     plan:'Toss up vs Patidar and Maxwell — invite the drive' },
                { overs:'14-16', bowler:'Chahar 2nd spell',     plan:'Wicket-taking — yorker length, target stumps' },
                { overs:'17-18', bowler:'Pathirana',            plan:'Wide yorkers — neutralise Maxwell power hitting' },
                { overs:'19-20', bowler:'Pathirana + Thakur',   plan:'Death specialists — target 35 or fewer in last 2' },
              ].map((r,i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-csk-warm rounded-xl">
                  <span className="text-xs font-bold text-csk-amber bg-csk-muted px-2 py-1
                                   rounded-lg flex-shrink-0 min-w-[52px] text-center">Ov {r.overs}</span>
                  <div>
                    <p className="text-csk-dark font-semibold text-sm">{r.bowler}</p>
                    <p className="text-csk-dark/50 text-xs">{r.plan}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 flex gap-3">
            <span className="text-2xl">💧</span>
            <div>
              <p className="text-blue-800 font-bold text-sm">Dew adjustment — evening session</p>
              <p className="text-blue-600 text-sm mt-1">
                Heavy dew expected after over 12. Move Jadeja and Santner to overs 7-10 (before dew sets in).
                Give Pathirana more overs in death — slinger pace less affected by dew than finger spin.
              </p>
            </div>
          </div>

          <div className="rounded-2xl p-5 text-center shadow-gold-sm"
            style={{ background:'white', border:'2px solid #F9A825' }}>
            <p className="text-csk-dark/50 text-xs uppercase tracking-wider mb-1">Defensive score target</p>
            <p className="font-black text-6xl text-csk-yellow">170</p>
            <p className="text-csk-dark/40 text-sm mt-1">Score CSK must defend — anything above this is a winning position</p>
          </div>

          <div className="rounded-2xl p-6 shadow-card"
            style={{ background:'white', borderLeft:'4px solid #F9A825', border:'1px solid rgba(232,200,74,0.4)' }}>
            <p className="text-csk-amber font-bold text-xs uppercase tracking-wider mb-3">✨ Gemini bowling plan</p>
            <p className="text-csk-dark/70 text-sm italic leading-relaxed">
              "Kohli's weakness is away swing with the new ball — give Chahar overs 1 and 2 from the pavilion end.
              After the powerplay, dew will make spin difficult so use Jadeja and Santner early.
              Pathirana's death bowling is the key weapon — his slinger angle creates a difficult angle
              for RCB's finishers. Defensive total at Chinnaswamy with dew: 170. If chasing less, comfortable win."
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

/* ─────────────────────────────────────────
   PAGE 5 — LIVE CHAT
───────────────────────────────────────── */
function ChatPage() {
  const [messages, setMessages] = useState([{
    role:'ai',
    text:"Hello! I'm your CSK match analyst. Ask me anything about today's game — tactics, matchups, field settings, or in-game decisions. I have full access to today's analysis data."
  }])
  const [input, setInput]   = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  const suggestions = [
    "How to stop Kohli right now?",
    "Should I use the impact player?",
    "Best death bowler for this match?",
    "Ruturaj's plan vs Bumrah?",
    "Field setting for Pathirana's last over?",
  ]

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior:'smooth' }) }, [messages])

  const send = async (text) => {
    if (!text.trim() || loading) return
    const q = text.trim()
    setMessages(m => [...m, { role:'user', text:q }])
    setInput('')
    setLoading(true)
    await new Promise(r => setTimeout(r, 1200))
    setMessages(m => [...m, {
      role:'ai',
      text:`Based on today's match analysis and live data:\n\nFor "${q}" — Kohli's primary weakness today is away swing from the pavilion end. Bowl Chahar over the wicket, full length, 4th stump line. Set slip and gully. He's averaging 28 this season against away swing and has been dismissed this way 3× by CSK bowlers in the last 2 seasons.\n\nAlternate plan: If Chahar has already bowled 3 overs, bring Pathirana from the bowling crease end — the slinger angle creates significant discomfort for Kohli's off-side game.`
    }])
    setLoading(false)
  }

  return (
    <div className="flex flex-col" style={{ height:'calc(100vh - 200px)' }}>
      <div className="bg-white border border-csk-border/30 rounded-2xl shadow-card flex flex-col flex-1 overflow-hidden">

        <div className="p-4 border-b border-csk-border/20 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ background:'linear-gradient(135deg,#F9A825,#FFD600)' }}>
            <span className="text-csk-navy font-black text-xs">AI</span>
          </div>
          <div className="flex-1">
            <p className="text-csk-dark font-bold text-sm">Live Match Assistant</p>
            <p className="text-csk-dark/40 text-xs">Powered by Gemini · CSK analyst perspective</p>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            <span className="text-csk-dark/40 text-xs">Live context</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((m,i) => (
            <div key={i} className={`flex ${m.role==='user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-line
                ${m.role==='user'
                  ? 'text-csk-navy font-medium rounded-br-md'
                  : 'text-csk-dark border border-csk-border/30 rounded-bl-md'}`}
                style={m.role==='user'
                  ? { background:'linear-gradient(135deg,#F9A825,#FFD600)' }
                  : { background:'#FFFBEA', borderLeft:'3px solid #F9A825' }}>
                {m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl px-4 py-3 border border-csk-border/30 rounded-bl-md"
                style={{ background:'#FFFBEA', borderLeft:'3px solid #F9A825' }}>
                <div className="flex gap-1">
                  {[0,1,2].map(i => (
                    <div key={i} className="w-2 h-2 rounded-full bg-csk-yellow animate-bounce"
                      style={{ animationDelay:`${i*0.15}s` }} />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="px-4 pb-2 flex gap-2 flex-wrap border-t border-csk-border/20 pt-3">
          {suggestions.map((s,i) => (
            <button key={i} onClick={() => send(s)}
              className="text-xs bg-csk-warm border border-csk-border/50 text-csk-dark/70
                         rounded-full px-3 py-1.5 hover:border-csk-yellow hover:text-csk-amber
                         transition-all font-medium">
              {s}
            </button>
          ))}
        </div>

        <div className="p-4 border-t border-csk-border/20 flex gap-3">
          <input value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key==='Enter' && send(input)}
            placeholder="Ask about tactics, matchups, field settings..."
            className="flex-1 bg-csk-warm border border-csk-border/50 rounded-xl px-4 py-3
                       text-csk-dark text-sm focus:outline-none focus:border-csk-yellow
                       placeholder:text-csk-dark/30" />
          <button onClick={() => send(input)}
            className="font-bold px-5 py-3 rounded-xl transition-all active:scale-95 text-csk-navy shadow-gold-sm"
            style={{ background:'linear-gradient(135deg,#F9A825,#FFD600)' }}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────
   SVG VISUALS
───────────────────────────────────────── */
function WagonWheel({ seed = 0.5 }) {
  const rng = (s) => { let x = Math.sin(s) * 10000; return x - Math.floor(x) }
  const balls = Array.from({ length: 14 }, (_, i) => {
    const s = seed * 100 + i * 7
    const types = ['boundary','two','dot','one','dot','dismissal','boundary','one','two','dot']
    return {
      angle: rng(s + 1) * 360,
      dist:  0.3 + rng(s + 2) * 0.65,
      type:  types[Math.floor(rng(s + 3) * types.length)]
    }
  })
  const colors = { boundary:'#16a34a', two:'#ca8a04', one:'#2563eb', dot:'#d1d5db', dismissal:'#dc2626' }
  const cx = 90, cy = 90, r = 75
  return (
    <svg viewBox="0 0 180 180" className="w-full">
      <circle cx={cx} cy={cy} r={r} fill="#FFF8DC" stroke="#E8C84A" strokeWidth="0.5" />
      <circle cx={cx} cy={cy} r={r*.5} fill="none" stroke="#E8C84A" strokeWidth="0.5" strokeDasharray="3,3" />
      <circle cx={cx} cy={cy} r={r*.25} fill="#FEFBF0" stroke="#E8C84A" strokeWidth="0.5" />
      {[0,45,90,135].map(a => {
        const rad = a*Math.PI/180
        return <line key={a} x1={cx} y1={cy} x2={cx+r*Math.cos(rad)} y2={cy+r*Math.sin(rad)} stroke="#E8C84A" strokeWidth="0.5" />
      })}
      {balls.map((b,i) => {
        const rad = b.angle*Math.PI/180
        const x = cx+r*b.dist*Math.cos(rad), y = cy+r*b.dist*Math.sin(rad)
        return (
          <g key={i}>
            <line x1={cx} y1={cy} x2={x} y2={y} stroke={colors[b.type]} strokeWidth={b.type==='boundary'?2:1} opacity="0.7" />
            <circle cx={x} cy={y} r="3" fill={colors[b.type]} />
          </g>
        )
      })}
      <circle cx={cx} cy={cy} r="4" fill="#1A1A2E" />
    </svg>
  )
}

function BallMap({ seed = 0.5 }) {
  const rng = (s) => { let x = Math.sin(s)*10000; return x-Math.floor(x) }
  const deliveries = Array.from({ length: 12 }, (_, i) => {
    const s = seed*100+i*13
    const types = ['dot','boundary','dismissal','one','dot','two','dot','boundary','dot','one','four','dot']
    return {
      x: 65 + rng(s+1)*30,
      y: 80 + rng(s+2)*55,
      type: types[i % types.length]
    }
  })
  const colors = { boundary:'#16a34a', two:'#ca8a04', one:'#2563eb', dot:'#d1d5db', dismissal:'#dc2626', four:'#16a34a' }
  return (
    <svg viewBox="0 0 160 185" className="w-full">
      <rect x="60" y="55" width="40" height="105" fill="#FFF3C4" stroke="#E8C84A" strokeWidth="1" rx="2" />
      <line x1="60" y1="90" x2="100" y2="90" stroke="#E8C84A" strokeWidth="0.5" strokeDasharray="2,2" />
      <line x1="60" y1="120" x2="100" y2="120" stroke="#E8C84A" strokeWidth="0.5" strokeDasharray="2,2" />
      <text x="80" y="72" textAnchor="middle" fontSize="7" fill="#9ca3af">Full</text>
      <text x="80" y="107" textAnchor="middle" fontSize="7" fill="#9ca3af">Good</text>
      <text x="80" y="135" textAnchor="middle" fontSize="7" fill="#9ca3af">Short</text>
      <rect x="73" y="155" width="3.5" height="10" fill="#1A1A2E" rx="1" />
      <rect x="78.5" y="155" width="3.5" height="10" fill="#1A1A2E" rx="1" />
      <rect x="84" y="155" width="3.5" height="10" fill="#1A1A2E" rx="1" />
      <line x1="72" y1="155" x2="88" y2="155" stroke="#1A1A2E" strokeWidth="1.5" />
      <circle cx="80" cy="147" r="6" fill="#F9A825" />
      <line x1="80" y1="153" x2="80" y2="163" stroke="#1A1A2E" strokeWidth="1.5" />
      <line x1="80" y1="157" x2="74" y2="164" stroke="#1A1A2E" strokeWidth="1.5" />
      <line x1="80" y1="157" x2="86" y2="164" stroke="#1A1A2E" strokeWidth="1.5" />
      {deliveries.map((d,i) => (
        <circle key={i} cx={d.x} cy={d.y} r="4.5" fill={colors[d.type]} opacity="0.85" />
      ))}
      {[['boundary','4s',12],['dismissal','W',28],['dot','Dot',44]].map(([type,label,y])=>(
        <g key={type}>
          <circle cx="12" cy={y} r="4" fill={colors[type]} />
          <text x="19" y={y+3} fontSize="7" fill="#6b7280">{label}</text>
        </g>
      ))}
    </svg>
  )
}

function PitchMap({ seed = 0.5 }) {
  const rng = (s) => { let x=Math.sin(s)*10000; return x-Math.floor(x) }
  const zones = [
    { label:'Short',       y:18,  h:28, baseColor:'#fca5a5', wkBase:2, ecoBase:11.2 },
    { label:'Good length', y:50,  h:35, baseColor:'#86efac', wkBase:8, ecoBase:7.4  },
    { label:'Full',        y:89,  h:30, baseColor:'#93c5fd', wkBase:5, ecoBase:8.8  },
    { label:'Yorker',      y:123, h:20, baseColor:'#fcd34d', wkBase:4, ecoBase:6.1  },
  ]
  return (
    <svg viewBox="0 0 160 160" className="w-full">
      <rect x="50" y="10" width="60" height="148" fill="#FFF8DC" stroke="#E8C84A" strokeWidth="1" rx="3" />
      {zones.map((z,i) => {
        const wk  = Math.round(z.wkBase  + (rng(seed*10+i) - 0.5)*2)
        const eco = (z.ecoBase + (rng(seed*20+i) - 0.5)*1.5).toFixed(1)
        return (
          <g key={i}>
            <rect x="50" y={z.y} width="60" height={z.h} fill={z.baseColor} opacity="0.65" />
            <text x="80" y={z.y+z.h/2+3} textAnchor="middle" fontSize="7.5" fill="#374151" fontWeight="500">{z.label}</text>
            <text x="125" y={z.y+z.h/2-2} fontSize="7" fill="#16a34a">{wk}W</text>
            <text x="125" y={z.y+z.h/2+8} fontSize="7" fill="#dc2626">{eco}</text>
          </g>
        )
      })}
      {[73,78.5,84].map((x,i) => (
        <rect key={i} x={x} y="153" width="3.5" height="7" fill="#1A1A2E" rx="0.5" />
      ))}
    </svg>
  )
}

function PhaseChart() {
  const phases = [
    { label:'PP',    eco:7.2, color:'#F9A825' },
    { label:'Mid',   eco:8.1, color:'#FF8F00' },
    { label:'Death', eco:9.4, color:'#dc2626' },
  ]
  return (
    <svg viewBox="0 0 160 125" className="w-full">
      {phases.map((p,i) => {
        const barH = (p.eco/12)*100
        const x = 20+i*48
        return (
          <g key={i}>
            <rect x={x} y={110-barH} width="32" height={barH} fill={p.color} opacity="0.85" rx="4" />
            <text x={x+16} y={107-barH} textAnchor="middle" fontSize="8.5" fill="#374151" fontWeight="600">{p.eco}</text>
            <text x={x+16} y="122" textAnchor="middle" fontSize="8" fill="#6b7280">{p.label}</text>
          </g>
        )
      })}
      <line x1="12" y1="110" x2="155" y2="110" stroke="#E8C84A" strokeWidth="0.8" />
    </svg>
  )
}