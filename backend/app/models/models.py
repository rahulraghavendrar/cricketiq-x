from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, JSON, ForeignKey, Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Player(Base):
    __tablename__ = "players"

    id            = Column(Integer, primary_key=True, index=True)
    player_id     = Column(String(100), unique=True, index=True)  # cricsheet registry ID
    name          = Column(String(200), index=True)
    country       = Column(String(100))
    role          = Column(String(50))   # batter / bowler / allrounder / wk-batter
    batting_style = Column(String(50))   # Right hand / Left hand
    bowling_style = Column(String(100))  # Right arm fast / Left arm spin / etc
    ipl_team      = Column(String(100))
    created_at    = Column(DateTime, server_default=func.now())


class Match(Base):
    __tablename__ = "matches"

    id            = Column(Integer, primary_key=True, index=True)
    match_id      = Column(String(100), unique=True, index=True)
    venue         = Column(String(200))
    city          = Column(String(100))
    date          = Column(Date)
    season        = Column(String(20))
    team1         = Column(String(100))
    team2         = Column(String(100))
    toss_winner   = Column(String(100))
    toss_decision = Column(String(20))   # bat / field
    winner        = Column(String(100))
    result        = Column(String(50))   # runs / wickets / tie / no result
    margin        = Column(Integer)
    format        = Column(String(20), default="T20")
    created_at    = Column(DateTime, server_default=func.now())

    ball_events   = relationship("BallEvent", back_populates="match")


class BallEvent(Base):
    __tablename__ = "ball_events"

    id             = Column(Integer, primary_key=True, index=True)
    match_id       = Column(Integer, ForeignKey("matches.id"), index=True)
    innings        = Column(Integer)
    over           = Column(Integer)
    ball           = Column(Integer)
    batter_id      = Column(Integer, ForeignKey("players.id"), index=True)
    bowler_id      = Column(Integer, ForeignKey("players.id"), index=True)
    non_striker_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    runs_batter    = Column(Integer, default=0)
    runs_extras    = Column(Integer, default=0)
    runs_total     = Column(Integer, default=0)
    extras_type    = Column(String(20), nullable=True)  # wide/noball/bye/legbye
    is_wicket      = Column(Boolean, default=False)
    dismissal_type = Column(String(50), nullable=True)  # caught/bowled/lbw/etc
    fielder_id     = Column(Integer, ForeignKey("players.id"), nullable=True)
    # NLP-derived fields (populated after commentary processing)
    shot_type      = Column(String(50), nullable=True)  # drive/pull/cut/sweep/etc
    delivery_type  = Column(String(50), nullable=True)  # yorker/bouncer/good_length/etc
    line           = Column(String(30), nullable=True)  # outside_off/off_stump/middle/leg

    match          = relationship("Match", back_populates="ball_events")


class Partnership(Base):
    __tablename__ = "partnerships"

    id          = Column(Integer, primary_key=True, index=True)
    match_id    = Column(Integer, ForeignKey("matches.id"), index=True)
    innings     = Column(Integer)
    batter1_id  = Column(Integer, ForeignKey("players.id"), index=True)
    batter2_id  = Column(Integer, ForeignKey("players.id"), index=True)
    runs        = Column(Integer, default=0)
    balls       = Column(Integer, default=0)
    run_rate    = Column(Float, default=0.0)
    wicket_fell = Column(Boolean, default=False)


class Commentary(Base):
    __tablename__ = "commentary"

    id             = Column(Integer, primary_key=True, index=True)
    match_id       = Column(Integer, ForeignKey("matches.id"), index=True)
    over           = Column(Integer)
    ball           = Column(Integer)
    text           = Column(Text)
    shot_type      = Column(String(50), nullable=True)
    delivery_type  = Column(String(50), nullable=True)
    pressure_flag  = Column(Boolean, default=False)
    sentiment_score= Column(Float, nullable=True)
    source         = Column(String(30))  # cricbuzz / espncricinfo


class CareerStat(Base):
    __tablename__ = "career_stats"

    id              = Column(Integer, primary_key=True, index=True)
    player_id       = Column(Integer, ForeignKey("players.id"), index=True)
    season          = Column(String(20))
    runs            = Column(Integer, default=0)
    balls_faced     = Column(Integer, default=0)
    avg             = Column(Float, default=0.0)
    sr              = Column(Float, default=0.0)
    wickets         = Column(Integer, default=0)
    balls_bowled    = Column(Integer, default=0)
    economy         = Column(Float, default=0.0)
    bowling_avg     = Column(Float, default=0.0)
    venue_id        = Column(Integer, ForeignKey("pitch_profiles.id"), nullable=True)


class PitchProfile(Base):
    __tablename__ = "pitch_profiles"

    id                = Column(Integer, primary_key=True, index=True)
    venue_name        = Column(String(200), unique=True, index=True)
    city              = Column(String(100))
    spin_wicket_pct   = Column(Float, default=0.0)
    pace_wicket_pct   = Column(Float, default=0.0)
    avg_first_innings = Column(Float, default=0.0)
    dew_factor        = Column(String(20), default="low")  # low/medium/high
    bounce_index      = Column(Float, default=0.5)
    sample_matches    = Column(Integer, default=0)
    last_updated      = Column(DateTime, server_default=func.now())


class MatchDayPitch(Base):
    __tablename__ = "match_day_pitch"

    id                    = Column(Integer, primary_key=True, index=True)
    match_id              = Column(Integer, ForeignKey("matches.id"), unique=True)
    surface_type          = Column(String(50), nullable=True)
    grass_cover_pct       = Column(Float, nullable=True)
    weather_json          = Column(JSON, nullable=True)
    dew_expected          = Column(Boolean, default=False)
    toss_result           = Column(String(20), nullable=True)
    pitch_type_label      = Column(String(30), nullable=True)
    spin_assistance_index = Column(Float, nullable=True)
    pace_assistance_index = Column(Float, nullable=True)
    phase_difficulty_curve= Column(JSON, nullable=True)
    raw_pitch_report_text = Column(Text, nullable=True)
    scraped_at            = Column(DateTime, nullable=True)