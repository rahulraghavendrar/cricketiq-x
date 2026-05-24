"""
Gemini-powered match plan generator for Page 4.
"""

from app.gemini.client import ask_gemini


def generate_batting_plan(
    venue: str,
    pitch_type: str,
    dew_factor: str,
    batting_order: list,
    phase_targets: dict,
    bowlers_to_attack: list,
    bowlers_to_respect: list,
    target_score: int,
) -> str:
    context = f"""
Venue: {venue} | Pitch: {pitch_type} | Dew: {dew_factor}
CSK batting order: {', '.join(batting_order[:6])}
Phase targets: PP {phase_targets.get('powerplay', '45-55')}, Middle {phase_targets.get('middle', '70-80')}, Death {phase_targets.get('death', '55-65')}
Bowlers to attack: {', '.join(bowlers_to_attack[:3])}
Bowlers to respect: {', '.join(bowlers_to_respect[:2])}
Target score: {target_score}
"""
    prompt = """Write a 4-sentence CSK batting plan. Cover:
1. Powerplay approach
2. Middle overs strategy
3. Death overs instructions
4. Impact player timing
Be specific to the players and conditions. Max 120 words."""
    return ask_gemini(prompt, context)


def generate_bowling_plan(
    venue: str,
    pitch_type: str,
    dew_factor: str,
    bowling_rotation: list,
    key_matchups: list,
    defensive_target: int,
) -> str:
    context = f"""
Venue: {venue} | Pitch: {pitch_type} | Dew: {dew_factor}
Bowling rotation: {', '.join(bowling_rotation[:6])}
Key matchups: {'; '.join(key_matchups[:4])}
Score to defend: {defensive_target}
"""
    prompt = """Write a 4-sentence CSK bowling plan. Cover:
1. Powerplay bowling approach
2. Middle overs spin/pace balance
3. Dew adjustment if relevant
4. Death overs execution
Be specific to the players and conditions. Max 120 words."""
    return ask_gemini(prompt, context)


def generate_impact_player_advice(
    match_situation: str,
    available_players: list,
    pitch_type: str,
    current_score: str = None,
) -> str:
    context = f"""
Match situation: {match_situation}
Pitch: {pitch_type}
Available impact options: {', '.join(available_players[:4])}
Current score: {current_score or 'Pre-match'}
"""
    prompt = "Should CSK use their impact player substitution now? If yes, who and why. If no, when is the ideal time. Max 40 words."
    return ask_gemini(prompt, context)