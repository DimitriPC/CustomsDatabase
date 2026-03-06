from enum import auto, IntEnum, Enum
from typing import List
from sqlalchemy import ForeignKey,ForeignKeyConstraint, UniqueConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from HelloFlask import app, db
from flask_login import UserMixin
from decimal import Decimal
from datetime import date, time, datetime
import os

class User(db.Model, UserMixin):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    real_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(60), nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    mu: Mapped[float] = mapped_column(server_default='25.0')
    sigma: Mapped[float] = mapped_column(server_default='8.333')
    games: Mapped[int | None]
    wins: Mapped[int | None]
    losses: Mapped[int | None]

    player_match_participations: Mapped[List["MatchParticipant"]] = relationship(back_populates="user")

    def get_id(self):
        return str(self.user_id)

class Result(IntEnum):
    win_reg = 3
    win_over = 2
    loss_over = 1
    loss_reg = 0

class Match(db.Model):
    __tablename__ = "match"

    match_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)
    first_to: Mapped[int]
    date_match: Mapped[datetime | None]
    status: Mapped[str] #Ongoing or Completed    

    match_teams: Mapped[List["MatchTeam"]] = relationship(back_populates="match", cascade='all, delete-orphan')
    games: Mapped[List["Game"]] = relationship(cascade='all, delete-orphan', back_populates="match")

class TeamSide(Enum):
    HOME = "home"
    AWAY = "away"

class MatchTeam(db.Model):
    __tablename__ = "team"

    match_team_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("match.match_id"), nullable=False)
    score: Mapped[int | None]
    side: Mapped[TeamSide]

    match: Mapped["Match"] = relationship(back_populates="match_teams")

    home_games: Mapped[List["Game"]] = relationship(back_populates="home_team",
                                        foreign_keys="[Game.home_team_id]")
    away_games: Mapped[List["Game"]] = relationship(back_populates="away_team",
                                        foreign_keys="[Game.away_team_id]")

    participants: Mapped[List["MatchParticipant"]] = relationship(cascade='all, delete-orphan', back_populates="match_team")


    
class Game(db.Model):
    __tablename__ = "game"

    game_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_to: Mapped[int]
    r6_map: Mapped[str]
    photo_url: Mapped[str | None]

    match_id: Mapped[int] = mapped_column(ForeignKey("match.match_id"), nullable=False)

    home_team_id: Mapped[int] = mapped_column(ForeignKey("team.match_team_id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("team.match_team_id"), nullable=False)

    score_home_team: Mapped[int | None]
    score_away_team: Mapped[int | None]

    winner_team_id: Mapped[int] = mapped_column(ForeignKey("team.match_team_id"), nullable=True)

    match: Mapped["Match"] = relationship(back_populates="games")
    game_stats: Mapped[List["GameParticipantStats"]] = relationship(cascade='all, delete-orphan', back_populates="game")

    home_team: Mapped["MatchTeam"] = relationship(
                                    back_populates="home_games",
                                    foreign_keys=[home_team_id]
                                    )
    away_team: Mapped["MatchTeam"] = relationship(
                                    back_populates="away_games",
                                    foreign_keys=[away_team_id]
                                    )
    winner: Mapped["MatchTeam"] = relationship(
        foreign_keys=[winner_team_id]
    )

class MatchParticipant(db.Model):
    __tablename__ = "team_player"

    match_participant_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    match_team_id: Mapped[int] = mapped_column(ForeignKey("team.match_team_id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="player_match_participations")
    match_team: Mapped["MatchTeam"] = relationship(back_populates="participants")
    game_stats: Mapped[List["GameParticipantStats"]] = relationship(cascade='all, delete-orphan', back_populates="match_participant")

class GameParticipantStats(db.Model):
    __tablename__ = "game_participant_stats"

    participant_stats_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    match_participant_id: Mapped[int] = mapped_column(ForeignKey("team_player.match_participant_id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.game_id"), nullable=False)

    kills: Mapped[int | None]
    assists: Mapped[int | None]
    deaths: Mapped[int | None]
    score: Mapped[int | None]
    position: Mapped[int | None]

    game: Mapped["Game"] = relationship(back_populates="game_stats")
    match_participant: Mapped["MatchParticipant"] = relationship(back_populates="game_stats")