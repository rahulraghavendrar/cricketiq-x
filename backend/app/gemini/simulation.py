"""
Gemini simulation narrative for Page 3.
"""

from app.gemini.client import ask_gemini


def generate_simulation_narrative(
    batter_name: str,
    bowler_name: str,
    balls: int,
    simulated_sr: float,
    dismissal_prob: float,
    weakness_triggered: str,
    suggested_shot: str,
    shots_to_avoid: list,
    pitch_type: str,
    is_csk_batter: bool,
) -> str:
    context = f"""
Simulation: {batter_name} vs {bowler_name} — {balls} balls
Pitch type: {pitch_type}
Simulated strike rate: {simulated_sr:.0f}
Dismissal probability: {dismissal_prob:.0f}%
Weakness triggered: {weakness_triggered}
Suggested shot for CSK player: {suggested_shot}
Shots to avoid: {', '.join(shots_to_avoid) if shots_to_avoid else 'None'}
"""
    if is_csk_batter:
        prompt = f"Narrate this {balls}-ball simulation of {batter_name} vs {bowler_name} from CSK's perspective. Give specific advice for the CSK batter. Max 60 words."
    else:
        prompt = f"Narrate this {balls}-ball simulation of {batter_name} vs {bowler_name}. Give CSK bowling advice based on the weakness data. Max 60 words."

    return ask_gemini(prompt, context)