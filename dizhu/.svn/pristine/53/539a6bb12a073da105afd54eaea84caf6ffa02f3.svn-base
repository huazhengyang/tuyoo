from dizhucomm.core.playmode import GameRound
from dizhucomm.core.table import DizhuSeat


class GameRoundMix(GameRound):
    def __init__(self):
        super(GameRoundMix, self).__init__()
        self.baseScores = []
        self.slamMultis = []
        self.slams = []
        self.winnerTaxMultis = []

    def init(self, table, roundNum, seats):
        assert(seats)
        self.table = table
        self.roundNum = roundNum
        self.roundId = '%s_%s' % (table.roomId, roundNum)
        self.seats = []
        self.callList = []
        self.effectiveCallList = []
        self.kickoutCards = []
        self.baseScores = []
        self.slamMultis = []
        self.winnerTaxMultis = []
        for seat in seats:
            self.baseScores.append(seat.player.mixConf.get('tableConf').get('baseScore') or
                                   seat.player.mixConf.get('tableConf').get('basebet') * seat.player.mixConf.get('tableConf').get('basemulti') * seat.player.mixConf.get('roomMutil'))
            self.slamMultis.append(seat.player.mixConf.get('tableConf').get('gslam'))
            self.winnerTaxMultis.append(seat.player.mixConf.get('winnerTaxMulti'))
            seat._state = DizhuSeat.ST_PLAYING
            seat._status = self._newSeatStatus(seat)
            if seat.player and seat.player.isQuit:
                seat._status.giveup = True
            if self.seats:
                self.seats[-1]._next = seat
            self.seats.append(seat)

        if len(self.seats) > 1:
            self.seats[-1]._next = self.seats[0]
        return self
