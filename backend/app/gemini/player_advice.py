"""
Gemini-powered player-specific advice for Page 2.
"""

from app.gemini.client import ask_gemini


def generate_batsman_advice(
    player_name: str,
    team: str,
    is_csk_player: bool,
    stats: dict,
    weakness_label: str,
    confidence: float,
    opponent_bowlers: list,
    pitch_type: str,
    venue: str,
) -> str:
    perspective = "CSK batting plan for" if is_csk_player else "How CSK should bowl to"
    context = f"""
Player: {player_name} ({team})
Pitch type: {pitch_type} at {venue}
Career IPL stats: SR {stats.get('strike_rate', 0):.1f}, Avg {stats.get('average', 0):.1f}
vs Spin SR: {stats.get('vs_spin_sr', 0):.1f} | vs Pace SR: {stats.get('vs_pace_sr', 0):.1f}
Powerplay SR: {stats.get('powerplay_sr', 0):.1f}
Death SR: {stats.get('death_sr', 0):.1f}
Primary weakness: {weakness_label} (confidence: {confidence:.0f}%)
Relevant opponent bowlers: {', '.join(opponent_bowlers[:3]) if opponent_bowlers else 'Unknown'}
"""
    if is_csk_player:
        prompt = f"Give specific batting advice for {player_name} today. Include: which bowler to attack, which to respect, one shot to play often, one shot to avoid. Max 60 words."
    else:
        prompt = f"Give CSK a specific bowling plan against {player_name} today. Include: which CSK bowler to use, exact delivery type, field setting. Reference the weakness data. Max 60 words."

    return ask_gemini(prompt, context)


def generate_bowler_advice(
    player_name: str,
    team: str,
    is_csk_player: bool,
    stats: dict,
    pitch_type: str,
    venue: str,
    key_opposition_batters: list,
) -> str:
    context = f"""
Bowler: {player_name} ({team})
Pitch type: {pitch_type} at {venue}
Bowling type: {stats.get('bowler_type', 'pace')}
Economy: {stats.get('economy', 0):.2f}
Wicket rate (balls per wicket): {stats.get('wicket_rate', 0):.1f}
PP economy: {stats.get('pp_economy', 0):.2f}
Death economy: {stats.get('death_economy', 0):.2f}
Dot ball %: {stats.get('dot_ball_pct', 0):.1f}%
Best dismissal type: {stats.get('best_dismissal_type', 'caught')}
Key opposition batters to face: {', '.join(key_opposition_batters[:3]) if key_opposition_batters else 'Unknown'}
"""
    if is_csk_player:
        prompt = f"Give {player_name} a specific bowling plan for today. Include: best phase to bowl, key delivery, one batter to target. Max 60 words."
    else:
        prompt = f"How should CSK batters approach {player_name} today? Include: which CSK player should face him most, what to attack, what to avoid. Max 60 words."

    return ask_gemini(prompt, context)