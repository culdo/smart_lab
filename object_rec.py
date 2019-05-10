import json
import queue
import time


class YoloFrame:
    def __init__(self, ini_dict):
        if ini_dict is not None:
            self.__dict__.update(ini_dict)
            self.objects = [YoloObj(obj) for obj in self.objects]
            YoloObj.is_uid_init = False


class YoloObj:
    buff_uid = -1
    is_uid_init = True
    max_buff_times = 150

    def __init__(self, ini_dict):
        self.uid = -1
        if YoloObj.is_uid_init:
            YoloObj.buff_uid += 1
            self.uid = YoloObj.buff_uid
        self.__dict__.update(ini_dict)
        self.relative_coordinates = YoloPos(self.relative_coordinates)
        self.buff_times = 0
        self.max_IOU = 0
        self.best_prev_idx = None
        # self.search_times = 0

    @staticmethod
    def obj_tracking_iou(objs):
        for obj in objs:
            YoloObj.calcIOU(obj.relative_coord)
        pass

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


class YoloPos:
    def __init__(self, ini_dict):
        self.__dict__.update(ini_dict)


prev_frame = YoloFrame(None)
# buff_time = time.time()
iter_IOU = None
iter_idx = None


def object_recognize(predict_json, q):
    """
    keys: ["class_id", "name", "relative_coordinates":{"center_x", "center_y", "width",
     "height"}, "confidence"]
    """
    global iter_IOU, iter_idx
    predict_result = json.loads(predict_json)
    person_num = 0
    curr_frame = YoloFrame(predict_result)
    orginal_len = len(curr_frame.objects)
    confidence_threshold = 0.5
    print("\n[Frame]")
    # print("fps: %d" % (1/(time.time() - buff_time)))
    # buff_time = time.time()

    if prev_frame.__dict__:
        # First iterate prev_frame and then curr_obj
        # because we want to save(append) the previous object which is not found
        for prev_i, prev_obj in enumerate(prev_frame.objects):
            prev_obj.max_IOU = 0
            iter_IOU = 0
            iter_idx = None
            # we use original_len to prevent to iterate the appended one
            for i, curr_obj in enumerate(curr_frame.objects):
                if prev_obj.confidence > confidence_threshold and curr_obj.confidence > confidence_threshold:
                    if prev_obj.class_id == curr_obj.class_id and i < orginal_len:
                        present_IOU = YoloObj.calcIOU(prev_obj.relative_coordinates, curr_obj.relative_coordinates)
                        # Update IOU and save(append) the object which is not found

                        if present_IOU > iter_IOU and present_IOU > curr_obj.max_IOU:
                            iter_IOU = present_IOU
                            iter_idx = i

            if iter_idx is not None:
                best_obj = curr_frame.objects[iter_idx]
                # if best_obj.name == "person":
                #     print("UID updated person.uid = %d" % best_obj.uid)
                if best_obj.best_prev_idx is not None:
                    prev_frame.objects[best_obj.best_prev_idx].max_IOU = 0
                prev_obj.max_IOU = iter_IOU

                best_obj.max_IOU = iter_IOU
                best_obj.uid = prev_obj.uid
                best_obj.best_prev_idx = prev_i

        for prev_obj in prev_frame.objects:
            # if the previous object is not found in current frame,
            # we save the object used to first add the buff_times then append to curr_frame
            if prev_obj.max_IOU == 0 and prev_obj.confidence > confidence_threshold:
                if prev_obj.buff_times < YoloObj.max_buff_times:
                    prev_obj.buff_times += 1
                    curr_frame.objects.append(prev_obj)
                    # if prev_obj.name == "person":
                    # print("Appended %s.uid: %s" % (prev_obj.name, prev_obj.uid))

        for i, curr_obj in enumerate(curr_frame.objects):
            if curr_obj.confidence > confidence_threshold:
                if i < orginal_len:
                    if curr_obj.max_IOU == 0:
                        YoloObj.buff_uid += 1
                        curr_obj.uid = YoloObj.buff_uid
                        # if curr_obj.name == "person":
                        print("New obj %s.uid: %s" % (curr_obj.name, curr_obj.uid))
                if curr_obj.name == "person":
                    print(curr_obj.uid)

    prev_frame.__dict__.update(curr_frame.__dict__)

    try:
        q.put_nowait(person_num)
    except queue.Full:
        q.get()
