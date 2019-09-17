from .yolo_object import YoloObj, TrackingState


class YoloFrame:
    def __init__(self, ini_dict, confidence_threshold=0.5, class_id=0, obj_filter=None):
        if ini_dict is not None:
            self.objects_count = {}
            self.__dict__.update(ini_dict)
            if obj_filter is not None:
                self.objects = [YoloObj(obj) for obj in self.objects if obj_filter(obj)]
            else:
                self.objects = [YoloObj(obj) for obj in self.objects if
                                obj["confidence"] > confidence_threshold and obj["class_id"] == class_id]
            TrackingState.is_uid_inited = True
