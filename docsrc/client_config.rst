Harvest Client Configuration File
=================================

configuration fields
--------------------

clients <list[dict]>
    Client Mappings that will match on the name of the client and provided
    value overrides.

    Name
        The name of the client.

    Hooks
        The endpoint that will receive this clients notifications.

    Hours
        The amount of hours this client has per month.

globalHooks <list[string]>
    The endpoints that are to receive all client notifications.

exceptionHook <list[string]>
    Array used to hold slack endpoints that will receive a strack trace
    on exception.

default_hours <int>
    The default hours per client if it is not provided in the client
    configuration array.
