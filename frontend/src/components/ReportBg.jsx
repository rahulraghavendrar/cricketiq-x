import { useState, useEffect, useRef } from 'react'

/* Floating background elements for report pages */
const SYMBOLS = ['🏏','⚡','🔥','★','◆']

function FloatingSymbol({ x, y, size, duration, delay, symbol }) {
  return (
    <div
      style={{
        position:'absolute', left:`${x}%`, top:`${y}%`,
        fontSize: size, opacity: 0.06,
        animation: `floatBall ${duration}s ease-in-out ${delay}s infinite`,
        pointerEvents:'none', userSelect:'none',
        filter:'sepia(1) saturate(3) hue-rotate(10deg)'
      }}
    >
      {symbol}
    </div>
  )
}

/* Event overlay — W's falling, 4s/6s floating up */
export function EventOverlay({ event }) {
  const [particles, setParticles] = useState([])

  useEffect(() => {
    if (!event) return
    const count = event === 'W' ? 12 : event === '6' ? 8 : 6
    const p = Array.from({ length: count }, (_, i) => ({
      id: i,
      x: 5 + Math.random() * 90,
      delay: Math.random() * 0.8,
      scale: 0.8 + Math.random() * 0.8,
    }))
    setParticles(p)
    const t = setTimeout(() => setParticles([]), 3500)
    return () => clearTimeout(t)
  }, [event])

  if (!particles.length) return null

  const configs = {
    'W':  { emoji:'W', color:'#EF4444', anim:'wFall',   size:60 },
    '6':  { emoji:'6', color:'#16a34a', anim:'numFloat', size:56 },
    '4':  { emoji:'4', color:'#F9A825', anim:'numFloat', size:52 },
    'NB': { emoji:'NB',color:'#8B5CF6', anim:'numFloat', size:44 },
    'WD': { emoji:'WD',color:'#6B7280', anim:'numFloat', size:44 },
    'FH': { emoji:'FREE HIT!', color:'#EC4899', anim:'numFloat', size:36 },
    '1':  { emoji:'1', color:'#F9A825', anim:'numFloat', size:40 },
    '2':  { emoji:'2', color:'#F9A825', anim:'numFloat', size:44 },
    '3':  { emoji:'3', color:'#F9A825', anim:'numFloat', size:48 },
  }

  const cfg = configs[event] || configs['1']

  return (
    <div style={{ position:'fixed', inset:0, pointerEvents:'none', zIndex:50, overflow:'hidden' }}>
      {particles.map(p => (
        <div key={p.id} style={{
          position:'absolute',
          left:`${p.x}%`,
          top: cfg.anim === 'wFall' ? '-10%' : '110%',
          fontSize: cfg.size,
          fontWeight: 900,
          color: cfg.color,
          animation: `${cfg.anim} 2.5s ${p.delay}s cubic-bezier(0.25,0.46,0.45,0.94) forwards`,
          textShadow: `0 0 20px ${cfg.color}60`,
          userSelect:'none',
          fontFamily:'Inter,sans-serif',
        }}>
          {cfg.emoji}
        </div>
      ))}
    </div>
  )
}

export default function ReportBg() {
  const symbols = Array.from({ length: 18 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: `${20 + Math.random() * 40}px`,
    duration: 5 + Math.random() * 8,
    delay: Math.random() * 5,
    symbol: SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)]
  }))

  return (
    <div style={{
      position:'fixed', inset:0, overflow:'hidden',
      pointerEvents:'none', zIndex:0
    }}>
      {/* Soft radial glows */}
      <div style={{
        position:'absolute', top:'-20%', right:'-10%',
        width:'60vw', height:'60vw', borderRadius:'50%',
        background:'radial-gradient(circle,rgba(249,168,37,0.06) 0%,transparent 70%)',
      }} />
      <div style={{
        position:'absolute', bottom:'-20%', left:'-10%',
        width:'50vw', height:'50vw', borderRadius:'50%',
        background:'radial-gradient(circle,rgba(255,214,0,0.05) 0%,transparent 70%)',
      }} />
      {/* Floating symbols */}
      {symbols.map(s => <FloatingSymbol key={s.id} {...s} />)}
    </div>
  )
}