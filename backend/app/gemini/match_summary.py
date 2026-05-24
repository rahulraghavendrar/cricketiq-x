"""
Gemini-powered match summary generator for Page 1.
"""

from app.gemini.client import ask_gemini


def generate_match_summary(
    team1: str,
    team2: str,
    venue: str,
    pitch_type: str,
    spin_index: float,
    pace_index: float,
    dew_factor: str,
    avg_first_innings: float,
    csk_win_pct: float,
    key_matchups: list,
) -> str:
    context = f"""
Match: {team1} vs {team2}
Venue: {venue}
Pitch type: {pitch_type}
Spin assistance index: {spin_index}
Pace assistance index: {pace_index}
Dew factor: {dew_factor}
Average first innings score at this venue: {avg_first_innings}
CSK historical win % vs opponent: {csk_win_pct}%
Key matchups: {', '.join(key_matchups) if key_matchups else 'None identified'}
"""
    prompt = f"""
Write a 3-sentence pre-match intelligence summary for CSK's analyst.
Focus on: pitch conditions impact on CSK's strategy, toss importance,
and the single most important tactical factor today.
Use the data above. Be specific, not generic.
"""
    return ask_gemini(prompt, context)


def generate_toss_advice(
    venue: str,
    pitch_type: str,
    dew_factor: str,
    avg_first_innings: float,
    csk_form: float,
    opponent_form: float,
) -> str:
    context = f"""
Venue: {venue}
Pitch type: {pitch_type}
Dew factor: {dew_factor}
Average first innings: {avg_first_innings}
CSK recent form rating: {csk_form}/10
Opponent form rating: {opponent_form}/10
"""
    prompt = "If CSK wins the toss, should they bat or field first? Give a direct recommendation with one key reason. Max 2 sentences."
    return ask_gemini(prompt, context)