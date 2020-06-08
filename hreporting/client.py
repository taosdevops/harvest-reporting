class HarvestClient(object):
    def __init__(
        self,
        clientId,
        hooks,
        hoursLeft,
        hoursTotal,
        hoursUsed,
        name,
        percent,
        templateId,
    ):

        self.client_id = clientId
        self.hooks = hooks
        self.hours_left = hoursLeft
        self.hours_total = hoursTotal
        self.hours_used = hoursUsed
        self.name = name
        self.percent = percent
        self.template_id = templateId
