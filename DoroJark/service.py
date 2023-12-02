import time
from .model import ApiStatusError


class Service:
    def __init__(self):
        pass

    """ Inin Service"""

    def InitService(self, DeviceId, AppVersionString):
        raise NotImplementedError

    """ Login Service"""

    def Login(self, token, oneSignalId):
        raise NotImplementedError

    def CreateUserAndLoginAsync(self, oneSignalId: str = None):
        raise NotImplementedError

    """ Music Service"""

    def GetHiddenMusicAsync(self, musicIds: list):
        loginRsp, baseRsp = self.MakeMainServiceReq(
            "/IMusicService/GetHiddenMusicAsync", musicIds
        )
        return loginRsp

    def GetMusicInfoAsync(self, musicId: int):
        loginRsp, baseRsp = self.MakeMainServiceReq(
            "/IMusicService/GetMusicInfoAsync", musicId
        )
        return loginRsp

    """ DJBoothServiceClient"""

    def AddScoreLog(self, playIdx: int, stampId: int, comment: str):
        raise NotImplementedError

    def GetScoreLog(self, playIdx: int):
        raise NotImplementedError

    def GetUserClub(self, targetUserIdx: int):
        raise NotImplementedError

    """ Friend Service"""

    def GetUserIdFromPlayerId(self, playerId: str):
        loginRsp, baseRsp = self.MakeMainServiceReq(
            "/IFriendService/GetUserIdFromPlayerIdAsync", playerId
        )
        return loginRsp

    def GetUserDetailProfile(self, targetUserIdx: int):
        raise NotImplementedError

    """ User Service"""

    def GetFullUserInfo(self):
        raise NotImplementedError

    def ProcessTutorialPhaseAsync(self, phase: int = 1010):
        infoRsp, baseRsp = self.MakeMainServiceReq(
            "/IUserService/ProcessTutorialPhaseAsync", phase
        )
        return infoRsp

    """ Event Service"""

    def GetEventInfo(self, eventId: int = 1):
        raise NotImplementedError

    def GetEventRankings(self, eventId: int = 1):
        raise NotImplementedError

    def GetActiveBossesAsync(self, eventId: int):
        raise NotImplementedError

    def GetRaidBossRankingAsync(self, bossId: int, number: int):
        raise NotImplementedError

    def GetParticipatedBossesAsync(self, eventId: int):
        raise NotImplementedError

    """ Home Service"""

    def GetHomeData(self):
        raise NotImplementedError

    def GetAllInformation(self):
        raise NotImplementedError

    def GetInformationAsync(self, id: int):
        raise NotImplementedError

    """ Rave Service"""

    def GetRaveEventRanking(self, eventId: int = 88):
        raise NotImplementedError

    def GetShiftInfo(self, eventId: int, shiftId: int):
        raise NotImplementedError

    """ Gacha Service"""

    def GetGachaStatusAsync(self):
        infoRsp, baseRsp = self.MakeMainServiceReq(
            "/IGachaService/GetStatusAsync", None
        )
        return infoRsp
