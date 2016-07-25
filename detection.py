import numpy as np

def check_object_status(tracking_data_list):
  debug = False
  if debug:
    print("start to detect object %d"%(len(tracking_data_list)))

  if len(tracking_data_list) > 5:
    angle_list = [abs(tracking_data_list[i].get('angle') - 45) for i in xrange(5)]
    angle_list.remove(max(angle_list))
    angle_list.remove(min(angle_list))
    mean_angle = np.mean(angle_list)

    height_width_ratio_list = [tracking_data_list[i].get('height_width_ratio') for i in xrange(5)]
    height_width_ratio_list.remove(max(height_width_ratio_list))
    height_width_ratio_list.remove(min(height_width_ratio_list))
    height_width_ratio = np.mean(height_width_ratio_list)

    if debug:
      print("height_width_ratio is %f"%(height_width_ratio))
      print("mean_angle is %f"%(mean_angle))

    if np.mean(angle_list) < 15 and height_width_ratio>1.25:
      print('the robot is falling down')
      return False

  return True
