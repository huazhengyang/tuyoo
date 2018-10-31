import functools
from dizhu.entity.wx_share_control import WxShareControlHelper
from freetime.core.timer import FTTimer



FTTimer(0, functools.partial(WxShareControlHelper.getUserShareControlInfo, 10001))
