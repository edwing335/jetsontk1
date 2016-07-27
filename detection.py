import numpy as np
import time
import cv2

def check_object_status(tracking_data_list):
  debug = True
  # debug = False
  detect_image_count = 7
  if len(tracking_data_list) > detect_image_count:
    # angle_list = [abs(tracking_data_list[i].get('angle')-45) for i in xrange(detect_image_count)]
    # angle_list.remove(max(angle_list))
    # angle_list.remove(min(angle_list))
    # mean_angle = np.mean(angle_list)
    mean_angle = np.mean([abs(tracking_data_list[0].get('angle') % 90),abs(tracking_data_list[1].get('angle') % 90)])

    # height_width_ratio_list = [tracking_data_list[i].get('height_width_ratio') for i in xrange(detect_image_count)]
    # height_width_ratio_list.remove(max(height_width_ratio_list))
    # height_width_ratio_list.remove(min(height_width_ratio_list))
    # height_width_ratio = np.mean(height_width_ratio_list)
    height_width_ratio = tracking_data_list[0].get('height_width_ratio')

    contour_list = [tracking_data_list[i].get('contour') for i in xrange(detect_image_count)]
    moment_y_list = []
    for contour in contour_list:
      moment = cv2.moments(contour)
      moment_y_list.append(float(moment['m01']/moment['m00']))
    moment_change_rate = float((max(moment_y_list) - min(moment_y_list))/min(moment_y_list))

    rectangle_list = [tracking_data_list[i].get('rectangle') for i in xrange(detect_image_count)]
    hight_list = []
    for rect in rectangle_list:
      hight_list.append(rect[-1])
    # hight_list.remove(max(hight_list))
    # hight_list.remove(min(hight_list))
    height_change_ratio = float((max(hight_list) - min(hight_list))/min(hight_list))

    if debug:
      print("height_width_ratio is %f"%(height_width_ratio))
      print("mean_angle is %f"%(mean_angle))
      print("height_change_ratio is %f"%(height_change_ratio))
      print("moment_change_rate is %f"%(moment_change_rate))

    if debug:
      image = tracking_data_list[0].get('image')
      print('falling down...')
      cv2.putText(image, "hwd is %f,ma: %f, mcr: %f"%(height_width_ratio, mean_angle, moment_change_rate), (0, 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,0), 1, 8, False)
      cv2.imwrite('./pics/' + 'falling' + time.strftime("-%Y-%m-%d-%H-%M-%S", time.localtime())  + '.png', image)
    if (mean_angle > 50) or (height_width_ratio < 0.9 and moment_change_rate > 0.5):
      return False

  return True
