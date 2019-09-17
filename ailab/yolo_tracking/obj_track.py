import json
import requests
import time
from ailab.yolo_tracking.yolo_frame import YoloFrame, YoloObj

prev_frame = YoloFrame(None)
# buff_time = time.time()
iter_IOU = None
iter_idx = None


def object_track(predict_json, ns, state_q, is_5m, is_open=None, is_indoor=False, is_outdoor=False):
    """
    keys: ["class_id", "name", "relative_coordinates":{"center_x", "center_y", "width",
     "height"}, "confidence"]
    """
    global iter_IOU, iter_idx
    predict_result = json.loads(predict_json)
    curr_frame = YoloFrame(predict_result)
    orginal_len = len(curr_frame.objects)
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
            for i, obj in enumerate(curr_frame.objects):
                if prev_obj.class_id == obj.class_id and i < orginal_len:
                    present_IOU = YoloObj.calcIOU(prev_obj.relative_coordinates, obj.relative_coordinates)
                    # Update IOU and save(append) the object which is not found

                    if present_IOU > iter_IOU and present_IOU > obj.max_IOU:
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
                best_obj.best_prev_idx = prev_i

                best_obj.state = prev_obj.state

        for prev_obj in prev_frame.objects:
            # if the previous object is not found in current frame,
            # we save the object used to first add the buff_times then append to curr_frame
            if prev_obj.max_IOU == 0:
                if prev_obj.buff_times < YoloObj.max_buff_times:
                    prev_obj.buff_times += 1
                    curr_frame.objects.append(prev_obj)
                    # if prev_obj.name == "person":
                    # print("Appended %s.uid: %s" % (prev_obj.name, prev_obj.uid))

        is_stay_5m = False
        global is_stay_5m
        for i, obj in enumerate(curr_frame.objects):
            if i < orginal_len:
                if obj.max_IOU == 0:
                    obj.state.new_state()
                    # if curr_obj.name == "person":
                    print("New %s uid: %s" % (obj.name, obj.state.uid))
                else:
                    obj.state.stay_time = time.time() - obj.state.spawn_time

            # Count objects
            if obj.name not in curr_frame.objects_count:
                curr_frame.objects_count[obj.name] = 1
            else:
                curr_frame.objects_count[obj.name] += 1

            # Cast stay time
            if obj.state.stay_time > obj.state.notify_time:
                state_q.put(obj.state)
                obj.state.notify_time += 60

            # Open door
            if obj.state.stay_time > 300:
                is_stay_5m = True

        # indoor condition
        if is_indoor:
            if is_stay_5m:
                is_5m.value = 1
            else:
                is_5m.value = 0

        # outdoor condition
        if is_outdoor:
            if curr_frame.objects_count["person"] > 0 and is_5m.value == 1:
                is_open.value = 1
            else:
                is_open.value = 0

    print(curr_frame.objects_count)

    prev_frame.__dict__.update(curr_frame.__dict__)

    ns.curr_frame = curr_frame
    # try:
    #     q.put_nowait(curr_frame)
    # except queue.Full:
    #     q.get()
    # if q is not None:
    #     q.put(curr_frame)


def handle_yolo_result(json_url, ns, state_q):
    r = requests.get(json_url, stream=True)
    predict_json = ""
    is_append = False

    for c_bin in r.iter_lines(chunk_size=512):
        if c_bin:
            c = c_bin.decode("ascii")
            if c == "{":
                is_append = True
                predict_json = ""
            if c == "}, ":
                predict_json += "}"

                object_track(predict_json, ns, state_q)
                is_append = False
            if is_append:
                predict_json += c


if __name__ == "__main__":
    # For test
    handle_yolo_result(None)
