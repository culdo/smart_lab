import time


class TrackingState:
    buff_uid = -1
    is_uid_inited = False

    def __init__(self):
        self.uid = -1
        self.spawn_time = None
        self.stay_time = 0
        self.notify_time = 300

    def new_state(self):
        TrackingState.buff_uid += 1
        self.uid = TrackingState.buff_uid
        self.spawn_time = time.time()
