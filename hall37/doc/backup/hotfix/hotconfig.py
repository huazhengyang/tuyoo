# -*- coding: utf-8 -*-
from hall.entity import hallconf, hallpromote
import freetime.util.log as ftlog
import time
from hall.servers.util.promotion_loc_handler import PromotionHelper

clientIds = ['Android_3.75_360.360.0-hall21.360.tu', 'Android_3.75_360.360.0-hall21.360.baiwang']
for clientId in clientIds :
    templateName = hallconf.getPromoteTemplateName(clientId)
    template = hallpromote._templateMap.get(templateName)
    ftlog.info('HOTCONFIG', templateName, template)
    promoteList = hallpromote.getPromotes(21, 156648285, clientId, int(time.time()))
    mo = PromotionHelper.makePromotionUpdateResponse(21, 156648285, clientId, promoteList)
    ftlog.info('HOTCONFIG', mo)
