const BASE_URL = 'http://localhost:8000'

async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

// ── Match report endpoints ───────────────────────────────────
export const api = {

  // Page 1
  getMatchSummary: (team2, venue) =>
    get(`/api/report/page1/CSK/${encodeURIComponent(team2)}?venue=${encodeURIComponent(venue)}`),

  getLiveScore: () =>
    get('/api/report/live-score'),

  getUpcomingMatch: () =>
    get('/api/report/upcoming'),

  // Page 2
  getSquad: (team) =>
    get(`/api/report/page2/squad/${team}`),

  getPlayerProfile: (playerId, opponent, pitchType, venue) =>
    get(`/api/report/page2/player/${playerId}?opponent=${opponent}&pitch_type=${pitchType}&venue=${encodeURIComponent(venue)}`),

  // Page 3 — Digital twin
  runMatchup: (batterId, bowlerId) =>
    get(`/api/analysis/matchup?batter_id=${batterId}&bowler_id=${bowlerId}`),

  getMLMatchup: (batterId, bowlerId, phase) =>
    get(`/api/analysis/ml/matchup-predict?batter_id=${batterId}&bowler_id=${bowlerId}&phase=${phase}`),

  getWeakness: (playerId) =>
    get(`/api/analysis/ml/weakness/${playerId}`),

  // Page 4
  getMatchPlan: (opponent, venue, pitchType) =>
    get(`/api/report/page4/${encodeURIComponent(opponent)}?venue=${encodeURIComponent(venue)}&pitch_type=${pitchType}`),

  // Head to head
  getHeadToHead: (opponent) =>
    get(`/api/analysis/csk/head-to-head/${encodeURIComponent(opponent)}`),

  // Players
  searchPlayers: (limit = 50) =>
    get(`/api/players/?limit=${limit}`),
}