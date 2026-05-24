"""
CricketIQ X - Pitch Report Scraper
Scrapes ESPNcricinfo and Cricbuzz for pre-match pitch reports.
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

VENUE_TO_PITCH_TYPE = {
    'MA Chidambaram Stadium':          {'type': 'turner',      'spin': 0.82, 'pace': 0.28},
    'MA Chidambaram Stadium, Chepauk': {'type': 'turner',      'spin': 0.82, 'pace': 0.28},
    'Wankhede Stadium':                {'type': 'flat',        'spin': 0.25, 'pace': 0.55},
    'M Chinnaswamy Stadium':           {'type': 'flat',        'spin': 0.22, 'pace': 0.52},
    'Eden Gardens':                    {'type': 'variable',    'spin': 0.45, 'pace': 0.45},
    'Narendra Modi Stadium':           {'type': 'flat',        'spin': 0.30, 'pace': 0.50},
    'Rajiv Gandhi International Stadium': {'type': 'flat',     'spin': 0.28, 'pace': 0.58},
    'Sawai Mansingh Stadium':          {'type': 'turner',      'spin': 0.65, 'pace': 0.35},
    'Punjab Cricket Association Stadium': {'type': 'flat',     'spin': 0.30, 'pace': 0.60},
    'Arun Jaitley Stadium':            {'type': 'flat',        'spin': 0.35, 'pace': 0.55},
    'Himachal Pradesh Cricket Association Stadium': {'type': 'green_seamer', 'spin': 0.20, 'pace': 0.72},
    'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium': {'type': 'flat', 'spin': 0.32, 'pace': 0.55},
    'Maharashtra Cricket Association Stadium': {'type': 'flat','spin': 0.30, 'pace': 0.55},
}

SPIN_KEYWORDS  = ['turn', 'spin', 'off-spin', 'leg-spin', 'dusty', 'dry', 'cracks', 'deteriorat', 'rough']
PACE_KEYWORDS  = ['seam', 'swing', 'green', 'grass', 'moisture', 'pace', 'bounce', 'carry', 'nip']
FLAT_KEYWORDS  = ['flat', 'batting', 'high score', 'run fest', 'true', 'even', 'good surface']


def classify_pitch_from_text(text: str) -> dict:
    """Classify pitch type from curator report text."""
    text_lower = text.lower()

    spin_score = sum(1 for k in SPIN_KEYWORDS  if k in text_lower)
    pace_score = sum(1 for k in PACE_KEYWORDS  if k in text_lower)
    flat_score = sum(1 for k in FLAT_KEYWORDS  if k in text_lower)

    if spin_score > pace_score and spin_score > flat_score:
        pitch_type = 'turner'
        spin_idx   = min(0.9, 0.5 + spin_score * 0.08)
        pace_idx   = max(0.1, 0.5 - spin_score * 0.06)
    elif pace_score > spin_score and pace_score > flat_score:
        pitch_type = 'green_seamer'
        spin_idx   = max(0.1, 0.4 - pace_score * 0.05)
        pace_idx   = min(0.9, 0.5 + pace_score * 0.08)
    else:
        pitch_type = 'flat'
        spin_idx   = 0.30
        pace_idx   = 0.50

    return {
        'pitch_type':      pitch_type,
        'spin_assistance': round(spin_idx, 2),
        'pace_assistance': round(pace_idx, 2),
        'raw_text':        text[:500],
        'source':          'text_analysis',
    }


def get_historical_pitch_profile(venue: str) -> dict:
    """Return historical pitch profile for a venue."""
    for venue_key, profile in VENUE_TO_PITCH_TYPE.items():
        if venue_key.lower() in venue.lower() or venue.lower() in venue_key.lower():
            return {
                'pitch_type':      profile['type'],
                'spin_assistance': profile['spin'],
                'pace_assistance': profile['pace'],
                'raw_text':        f'Historical profile for {venue}',
                'source':          'historical_database',
            }
    return {
        'pitch_type':      'flat',
        'spin_assistance': 0.35,
        'pace_assistance': 0.50,
        'raw_text':        'No historical data — using default profile',
        'source':          'default',
    }


def scrape_espncricinfo_pitch(match_url: str = None) -> Optional[dict]:
    """Scrape pitch report from ESPNcricinfo."""
    if not match_url:
        return None
    try:
        resp = requests.get(match_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        pitch_keywords = ['pitch', 'surface', 'curator', 'track', 'condition']
        for para in soup.find_all(['p', 'div', 'span']):
            text = para.get_text(strip=True).lower()
            if any(kw in text for kw in pitch_keywords) and len(text) > 50:
                return classify_pitch_from_text(para.get_text(strip=True))
        return None
    except Exception:
        return None


def get_pitch_report(venue: str, match_url: str = None) -> dict:
    """
    Get pitch report — tries live scraping first, falls back to historical.
    """
    # Try live scrape
    if match_url:
        live = scrape_espncricinfo_pitch(match_url)
        if live:
            live['venue']      = venue
            live['scraped_at'] = datetime.now().isoformat()
            live['is_live']    = True
            return live

    # Fall back to historical profile
    profile = get_historical_pitch_profile(venue)
    profile['venue']      = venue
    profile['scraped_at'] = datetime.now().isoformat()
    profile['is_live']    = False
    return profile


def get_weather(venue: str, date: str = None) -> dict:
    """Fetch weather forecast from Open-Meteo API."""
    VENUE_COORDS = {
        'Chennai':   (13.0827, 80.2707),
        'Mumbai':    (19.0760, 72.8777),
        'Bengaluru': (12.9716, 77.5946),
        'Kolkata':   (22.5726, 88.3639),
        'Delhi':     (28.7041, 77.1025),
        'Hyderabad': (17.3850, 78.4867),
        'Ahmedabad': (23.0225, 72.5714),
        'Jaipur':    (26.9124, 75.7873),
        'Chandigarh':(30.7333, 76.7794),
        'Lucknow':   (26.8467, 80.9462),
        'Pune':      (18.5204, 73.8567),
        'Dharamsala':(32.2190, 76.3234),
    }

    lat, lon = 20.5937, 78.9629  # India center default
    for city, coords in VENUE_COORDS.items():
        if city.lower() in venue.lower():
            lat, lon = coords
            break

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
            f"&daily=precipitation_sum,temperature_2m_max"
            f"&timezone=Asia/Kolkata&forecast_days=1"
        )
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data    = resp.json()
            current = data.get('current', {})
            temp    = current.get('temperature_2m', 28)
            humidity= current.get('relative_humidity_2m', 60)
            wind    = current.get('wind_speed_10m', 10)
            precip  = current.get('precipitation', 0)

            dew_factor = 'high' if humidity > 75 else 'medium' if humidity > 55 else 'low'

            return {
                'temperature':  temp,
                'humidity':     humidity,
                'wind_speed':   wind,
                'precipitation':precip,
                'dew_factor':   dew_factor,
                'source':       'open-meteo',
            }
    except Exception:
        pass

    return {
        'temperature':  28,
        'humidity':     60,
        'wind_speed':   10,
        'precipitation':0,
        'dew_factor':   'medium',
        'source':       'default',
    }