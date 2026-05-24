"""
CricketIQ X - Live Score Scraper
Scrapes Cricbuzz for live match scores.
"""

import requests
import re
from bs4 import BeautifulSoup
from typing import Optional
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}


def get_upcoming_csk_match() -> dict:
    """
    Get the next upcoming CSK fixture.
    Returns match details for the homepage card.
    """
    try:
        url  = "https://www.cricbuzz.com/cricket-team/india/2/schedules"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return _default_upcoming_match()

        soup   = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('div', class_=re.compile('cb-series-matches'))

        for table in tables:
            text = table.get_text()
            if 'CSK' in text or 'Chennai' in text:
                return _parse_match_from_element(table)

    except Exception:
        pass

    return _default_upcoming_match()


def get_live_csk_score() -> dict:
    """
    Get live score for CSK match if one is in progress.
    Returns score data for Page 1 ticker.
    """
    try:
        url  = "https://www.cricbuzz.com/cricket-match/live-scores"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return {'status': 'pre', 'message': 'Match not started'}

        soup    = BeautifulSoup(resp.text, 'html.parser')
        matches = soup.find_all('div', class_=re.compile('cb-mtch-lst'))

        for match in matches:
            text = match.get_text()
            if 'CSK' in text or 'Chennai' in text:
                return _parse_live_score(match)

    except Exception:
        pass

    return {'status': 'pre', 'message': 'Match not started'}


def _parse_live_score(element) -> dict:
    """Parse live score from HTML element."""
    try:
        text  = element.get_text(separator=' ', strip=True)
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        score_pattern = re.search(r'(\d+)/(\d+)', text)
        over_pattern  = re.search(r'\((\d+\.?\d*)\s*ov', text)

        score   = score_pattern.group(0) if score_pattern else '0/0'
        overs   = over_pattern.group(1)  if over_pattern  else '0.0'

        crr_match = re.search(r'CRR[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
        rrr_match = re.search(r'RRR[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)

        return {
            'status':  'live',
            'score':   score,
            'overs':   overs,
            'crr':     crr_match.group(1) if crr_match else '0.0',
            'rrr':     rrr_match.group(1) if rrr_match else '0.0',
            'raw':     text[:300],
            'updated': datetime.now().isoformat(),
        }
    except Exception:
        return {'status': 'pre', 'message': 'Parse error'}


def _parse_match_from_element(element) -> dict:
    """Parse upcoming match details from element."""
    try:
        text = element.get_text(separator=' ', strip=True)
        return {
            'team1':      'CSK',
            'team2':      'TBD',
            'venue':      'TBD',
            'date':       'Upcoming',
            'tournament': 'IPL 2025',
            'raw':        text[:200],
        }
    except Exception:
        return _default_upcoming_match()


def _default_upcoming_match() -> dict:
    """Default match data when scraping fails."""
    return {
        'team1':      'CSK',
        'team1_full': 'Chennai Super Kings',
        'team2':      'RCB',
        'team2_full': 'Royal Challengers Bengaluru',
        'venue':      'M Chinnaswamy Stadium, Bengaluru',
        'date':       'Upcoming',
        'time':       '7:30 PM IST',
        'tournament': 'IPL 2025',
        'status':     'upcoming',
    }