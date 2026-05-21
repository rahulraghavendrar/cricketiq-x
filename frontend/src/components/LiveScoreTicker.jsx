import { useState, useEffect } from 'react'

// Mock live score — will connect to backend WebSocket later
const mockScore = {
  status: 'live',        // 'pre' | 'live' | 'completed'
  batting: 'CSK',
  score: '124/3',
  overs: '14.2',
  batsmen: ['RG 67*', 'SD 28*'],
  bowler: 'J Bumrah 3-0-24-1',
  rrr: '9.8',
  crr: '8.6',
}

export default function LiveScoreTicker() {
  const [score] = useState(mockScore)

  if (score.status === 'pre') {
    return (
      <div className="flex items-center gap-2 bg-white/80 border border-csk-border/40
                      rounded-xl px-3 py-1.5 backdrop-blur-sm">
        <span className="w-2 h-2 rounded-full bg-gray-400" />
        <span className="text-xs font-semibold text-gray-500">Match not started</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 bg-csk-navy/90 border border-csk-gold/40
                    rounded-xl px-3 py-1.5 backdrop-blur-sm shadow-gold-sm">
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
        <span className="text-csk-gold text-[10px] font-bold uppercase tracking-wider">Live</span>
      </div>
      <div className="h-3 w-px bg-white/20" />
      <div className="flex items-center gap-1">
        <span className="text-csk-gold font-black text-sm">{score.score}</span>
        <span className="text-white/40 text-[10px]">({score.overs})</span>
      </div>
      <div className="h-3 w-px bg-white/20" />
      <div className="flex flex-col">
        <span className="text-white/80 text-[9px] leading-none">{score.batsmen[0]}</span>
        <span className="text-white/50 text-[9px] leading-none">{score.batsmen[1]}</span>
      </div>
      <div className="h-3 w-px bg-white/20" />
      <div className="flex flex-col">
        <span className="text-white/50 text-[9px] leading-none">CRR {score.crr}</span>
        <span className="text-red-300 text-[9px] leading-none">RRR {score.rrr}</span>
      </div>
    </div>
  )
}