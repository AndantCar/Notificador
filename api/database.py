#!/usr/bin/python3
# -*- encoding:utf-8 -*-

from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Time, Integer, Numeric, Date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Instrument(Base):
    __tablename__ = 'CAT_Instruments'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    date = Column(Date)
    time = Column(Time)
    value = Column(Numeric(precision=20, scale=10))

    def __repr__(self):
        return "Instrument {}: {}".format(self.name, self.value)

#
# class Intraday(Base):
#     __tablename__ = 'TB_Intraday'
#     id = Column(BigInteger(), autoincrement=True, primary_key=True)
#     idInstrument = Column(BigInteger(), ForeignKey('CAT_Instruments.id'))
#     date = Column(Date())
#     startTime = Column(Time())
#     endTime = Column(Time())
#     majorVolume = Column(BigInteger())
#     minorVolume = Column(BigInteger())
#     highValue = Column(Numeric(precision=20, scale=10))
#     lowValue = Column(Numeric(precision=20, scale=10))
#     openValue = Column(Numeric(precision=20, scale=10))
#     closeValue = Column(Numeric(precision=20, scale=10))
#     instrument = relationship('Instrument', back_populates='CAT_Instruments')
#
#     def __repr__(self):
#         return "Instrument {}: <Close: {}, End: {:%H:%M:%S.%f}>".format(self.instrument.name,
#                                                                         self.closeValue, self.endTime)
#
