import numpy as np
import cv2

def check_object_status(tracking_data_list):
  debug = True
  # debug = False
  detect_image_count = 5
  if len(tracking_data_list) > detect_image_count:
    angle_list = [abs(tracking_data_list[i].get('angle')-45) for i in xrange(detect_image_count)]
    angle_list.remove(max(angle_list))
    angle_list.remove(min(angle_list))
    mean_angle = np.mean(angle_list)

    height_width_ratio_list = [tracking_data_list[i].get('height_width_ratio') for i in xrange(detect_image_count)]
    height_width_ratio_list.remove(max(height_width_ratio_list))
    height_width_ratio_list.remove(min(height_width_ratio_list))
    height_width_ratio = np.mean(height_width_ratio_list)

    # contour_list = [tracking_data_list[i].get('contour') for i in xrange(detect_image_count)]
    # moment_y_list = []
    # for contour in contour_list:
    #   moment = cv2.moments(contour)
    #   moment_y_list.append(int(moment['m01']/moment['m00']))

    rectangle_list = [tracking_data_list[i].get('rectangle') for i in xrange(detect_image_count)]
    hight_list = []
    for rect in rectangle_list:
      hight_list.append(rect[-1])
    hight_list.remove(max(hight_list))
    hight_list.remove(min(hight_list))

    if max(hight_list) > 0:
      height_change_ratio = float(max(hight_list) - min(hight_list))/float(max(hight_list))
    else:
      height_change_ratio = 0

    if debug:
      print("height_width_ratio is %f"%(height_width_ratio))
      print("mean_angle is %f"%(mean_angle))
      print("height_change_ratio is %f"%(height_change_ratio))

    if (np.mean(angle_list) < 15 and height_width_ratio < 0.7) or (height_change_ratio > 0.5):
      print('the robot is falling down')
      return False

  return True
