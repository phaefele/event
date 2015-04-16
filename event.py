class Event:
    """
    Event class that can be used to signal between objects when an object changes state. Each event maintains a list of
    handlers that Event users can register. When the Event owner fires the event, all the Event listeners are notified.
    This makes for simpler programming by decoupling listeners and publishers. No message bus (etc) is used - this is
    simply an in-memory, Python only decoupling device.

    Event raisers will pass the raising object as the first parameter to event handler methods. Event handlers (when registered)
    can also provide arguments that they want the callback method (when raised) to provide to the call-back method. This
    makes it simple for those registering for events to pass additional information that the handler may need when handling
    the event.

    Handlers are processed in the order that they where registered. As framework developers may want to handle certain
    events before user code, they can register handlers via the add_sys_handler method. User code should *not* call this method.
    """

    def __init__(self, owner):
        """

        :param owner:
        :return:
        """
        self.handlers = list()
        self.owner = owner

    def add_sys_handler(self, handler, **kwargs):
        '''
        The system wants to handle this event before user code. We call this event handler first. It is added to the front
        of the handler list.

        :return:
        '''
        self.__assert_no_duplicate_handler(handler)
        self.handlers.insert(0, (handler, kwargs))
        return self

    def __assert_no_duplicate_handler(self, handler):
        """
        Will raise an error if a particular handler is registered more than once.

        :param handler:
        :return:
        """
        for h, k in self.handlers:
            if handler == h:
                logger.eror('Handlers should not be added twice - saw %s / %s twice. event=%s, owner=%s', h, handler, self, self.owner)

    def has_handler(self, handler):
        """
        Does this event already have the supplied handler attached?
        """
        for h, k in self.handlers:
            if handler == h:
                return True
        return False

    def add_handler(self, handler, **handle_kwargs):
        """
        Add the handler, with args to be passed back, to the event.

        :param handler:
        :param handle_kwargs: Will be passed back to handler method when event fires
        :return:
        """
        self.__assert_no_duplicate_handler(handler)
        self.handlers.append((handler, handle_kwargs))
        return self

    def remove_handler(self, handler):
        """
        Removes the provided handler. Will log an error message if the handler was not registered earlier.

        :param handler:
        :return:
        """
        removed = False
        for h, k in self.handlers:
            if handler == h:
                self.handlers.remove((h, k))
                removed = True
                break
        if removed is False:
            logger.error("Handler is not handling this event, so cannot unhandle it. No handler was removed, but will continue. handler=%s, event=%s, owner=%s", handler, self, self.owner)
        return self

    def fire(self, **fire_kargs):
        """
        Call the handler method (with args they provided) with the set of arguments provided here. Will raise
        an error if the arguments provided during registration overlap with those provided during firing.

        :param fire_kargs: \*\*kwarg dict of parameters to provide to handler methods
        :return:
        """
        for handler, handle_kwargs in self.handlers[:]:    # iterate copy ([:]) so handlers can be removed during iteration
            intersect_keys = set(fire_kargs.keys()) & set(handle_kwargs.keys())
            if len(intersect_keys) > 0:
                logger.error('Event has duplicate args to handlers. intersect_keys=%s, event=%s', intersect_keys, self)
            # Merge keys
            all_args = handle_kwargs.copy()
            all_args.update(fire_kargs)
            # Call handlers with all keys
            if len(all_args) == 0:
                handler(self.owner)
            else:
                handler(self.owner, **all_args)

    def get_handler_count(self):
        """
        Returns number of handlers

        :return:
        """
        return len(self.handlers)

    __iadd__ = add_handler
    __isub__ = remove_handler
    __call__ = fire
    __len__ = get_handler_count