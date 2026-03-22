from sqlalchemy import Column, String, BigInteger, Float, Date, DateTime, Integer, Boolean
from src.database import Base
from sqlalchemy.sql import func

class Stock(Base):
    __tablename__ = "stocks"
    symbol = Column(String(10), primary_key=True)
    listed_shares = Column(BigInteger, nullable=False, default=0)
    sector = Column(String(50))
    is_active = Column(Boolean, default=True)

class MarketPrice(Base):
    __tablename__ = "market_prices"
    symbol = Column(String(10), primary_key=True)
    trading_date = Column(Date, primary_key=True)
    price = Column(Float, nullable=False, default=0)
    ref_price = Column(Float, nullable=False, default=0)
    change_percent = Column(Float)
    volume = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), default=func.now())

class ForeignTrading(Base):
    __tablename__ = "foreign_trading"
    symbol = Column(String(10), primary_key=True)
    trading_date = Column(Date, primary_key=True)
    f_buy_val = Column(Float, nullable=False, default=0)
    f_sell_val = Column(Float, nullable=False, default=0)
    net_val = Column(Float)
    updated_at = Column(DateTime(timezone=True), default=func.now())

class IndexSnapshot(Base):
    __tablename__ = "index_snapshot"
    symbol = Column(String(10), primary_key=True)
    trading_date = Column(Date, primary_key=True)
    point = Column(Float)
    change_point = Column(Float)
    change_percent = Column(Float)
    total_volume = Column(BigInteger)
    total_value = Column(Float)
    breadth_green = Column(Integer)
    breadth_red = Column(Integer)
    breadth_yellow = Column(Integer)
    breadth_ceiling = Column(Integer)
    breadth_floor = Column(Integer)
    updated_at = Column(DateTime(timezone=True), default=func.now())
