from .yolo_position import YoloPos
from .tracking_state import TrackingState


class YoloObj:
    max_buff_times = 150

    def __init__(self, ini_dict):
        self.__dict__.update(ini_dict)
        self.relative_coordinates = YoloPos(self.relative_coordinates)

        self.state = TrackingState()
        if not TrackingState.is_uid_inited:
            self.state.new_state()
            print("New %s uid: %s" % (self.name, self.state.uid))
        self.buff_times = 0
        self.max_IOU = 0
        self.best_prev_idx = None

    @staticmethod
    def calcIOU(old_coord, new_coord):
        x1 = old_coord.center_x
        y1 = old_coord.center_y
        w1 = old_coord.width + 0.05
        h1 = old_coord.height + 0.05
        x2 = new_coord.center_x
        y2 = new_coord.center_y
        w2 = new_coord.width + 0.05
        h2 = new_coord.height + 0.05

        if (abs(x1 - x2) < ((w1 + w2) / 2.0)) and (abs(y1 - y2) < ((h1 + h2) / 2.0)):
            left = max((x1 - (w1 / 2.0)), (x2 - (w2 / 2.0)))
            upper = max((y1 - (h1 / 2.0)), (y2 - (h2 / 2.0)))

            right = min((x1 + (w1 / 2.0)), (x2 + (w2 / 2.0)))
            bottom = min((y1 + (h1 / 2.0)), (y2 + (h2 / 2.0)))

            inter_w = abs(left - right)
            inter_h = abs(upper - bottom)
            inter_square = inter_w * inter_h
            union_square = (w1 * h1) + (w2 * h2) - inter_square

            calcIOU = inter_square / union_square * 1.0
            # print("calcIOU:", calcIOU)
        else:
            calcIOU = 0.0

        return calcIOU