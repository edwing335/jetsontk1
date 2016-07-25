import time
import cv2
import numpy as np
from shapely.geometry import Polygon

class ImageCalculater(object):
  """docstring for ImageCalculater"""
  def __init__(self, width, height):
    cv2.namedWindow("origin_frame")
    # cv2.namedWindow("frame")
    # self.debug = False
    self.debug = True
    self.camera = None
    self.frame_width = width
    self.frame_height = height
    self.tracking_data_list = []
    self.prvs_image = None

  def save_image(self, frame, path='./', prefix='opticalfb'):
    cv2.imwrite(path + prefix + time.strftime("-%Y-%m-%d-%H-%M-%S", time.localtime())  + '.png', frame)

  def custom_wait_key(self, window_name, frame, saved_frame):
    cv2.imshow(window_name, frame)
    k = cv2.waitKey(1) & 0xff
    if k == ord('s'):
        cv2.imwrite('opticalfb' + time.strftime("-%Y-%m-%d-%H-%M-%S", time.localtime())  + '.png',saved_frame)

  def conduct_translation(self, frame):
    # ret, binary_pic_after_threshold = cv2.threshold(binary_pic,127,255,cv2.THRESH_BINARY)
    # binary_pic_median_blur = cv2.medianBlur(frame, 5)
    # binary_pic_dilation = cv2.dilate(binary_pic_median_blur ,np.ones((10,10),np.uint8),iterations = 1)
    binary_pic_dilation = cv2.dilate(frame ,np.ones((5,5),np.uint8),iterations = 1)
    binary_pic_erosion = cv2.erode(binary_pic_dilation, np.ones((10,10),np.uint8),iterations = 1)
    binary_pic_median_blur = cv2.medianBlur(binary_pic_erosion, 5)
    return binary_pic_median_blur

  def display_track_image(self, rect, area, frame):
      prvs_img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
      current_img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
      bounding_rect_x, bounding_rect_y, bounding_rect_w, bounding_rect_h = rect

      center_point = (bounding_rect_x+bounding_rect_w/2, bounding_rect_y+bounding_rect_h/2)
      # cv2.drawContours(current_img, contours, largest_contour_index, (255,255,255), 1, 8, hierarchy)
      cv2.rectangle(current_img, (bounding_rect_x, bounding_rect_y), (bounding_rect_x+bounding_rect_w, bounding_rect_y+bounding_rect_h), (0,255,0), 1, 8, 0);
      cv2.circle(current_img, center_point, 2, (0,0,255), -1, 8, 0)
      cv2.putText(current_img, "center at (%d, %d), width: %d, height: %d, %d"%(bounding_rect_w/2, bounding_rect_h/2, bounding_rect_w, bounding_rect_h, area), (0, 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,0), 1, 8, False)
      # self.custom_wait_key('frame', current_img, prvs_img)
      cv2.imwrite('object-image' + time.strftime("-%Y-%m-%d-%H-%M-%S", time.localtime())  + '.png',current_img)

  def calculate_optical_flow(self, current_img, prvs_img):
    current_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
    prvs_gray = cv2.cvtColor(prvs_img, cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(prvs_gray, current_gray, 0.5, 3, 15, 3, 5, 1.2, 0)
    binary_pic = np.zeros(current_gray.shape, np.uint8)

    h, w = current_gray.shape
    total_threshold=0
    for i in xrange(0,h,5):
        for j in xrange(0,w,5):
            fx, fy = flow[i, j]
            total_threshold += abs(fx) + abs(fy)
            if abs(fx) + abs(fy) > 0.5:
                binary_pic[i, j] = 255;
    # print('mean threshold is %f'%(total_threshold/(h*w)))

    binary_pic_translated = self.conduct_translation(binary_pic)
    contours, hierarchy = cv2.findContours(binary_pic_translated,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # print('contours is %d'%(len(contours)))
    largest_area = 0
    largest_contour_index = 0
    if len(contours) > 0:
        for k in xrange(0, len(contours)):
            area = cv2.contourArea(contours[k])
            if largest_area < area:
                largest_area = area
                largest_contour_index = k

        return contours[largest_contour_index];
    else:
        print("contours is not found...")
        return False

  def add_contour_to_list(self, contour):
    if len(self.tracking_data_list) > 50:
      del self.tracking_data_list[-1]

    rect = cv2.minAreaRect(contour)
    (vx, vy), (width, height), angle = rect

    self.tracking_data_list.insert(0, {'contour': contour, 'angle': abs(angle), 'rectangle': (vx, vy, width, height), 'height_width_ratio': float(height)/float(width)})

  def got_tracking_object(self, contour):
    if type(contour) is bool:
      return

    area = cv2.contourArea(contour)
    rect = cv2.minAreaRect(contour)
    (vx, vy), (x, y), angle = rect
    image_ratio = (x * y)/(self.frame_width*self.frame_height)
    print('area: %d, angle: %f, y/x: %f'%(area, abs(angle), float(y)/ float(x) ))
    if (area > 1500 and (abs(angle) < 10) and (float(y)/float(x) > 1.5) and image_ratio < 0.8):
      return True
    else:
      return False

  def estimate_object_by_countor(self, contour):
    if type(contour) is bool:
      return

    area = cv2.contourArea(contour)
    current_rect = cv2.minAreaRect(contour)
    current_box = cv2.cv.BoxPoints(current_rect)
    (vx, vy), (x, y), angle = current_rect

    prvs_rect = cv2.minAreaRect(self.tracking_data_list[-1].get('contour'))
    prvs_box = cv2.cv.BoxPoints(prvs_rect)

    p1 = Polygon(prvs_box)
    p2 = Polygon(current_box)
    overlap_ratio = p1.intersection(p2).area/(p1.area + p2.area - p1.intersection(p2).area)

    image_ratio = (x * y)/(self.frame_width*self.frame_height)
    if (area > 2000 and overlap_ratio > 0.1 and image_ratio < 0.8):
      print('area: %d, angle: %f, y/x: %f, overlap_ratio: %f'%(area, abs(angle), float(y)/float(x), overlap_ratio))
      return True
    else:
      return False

    # area = cv2.contourArea(contour)
    # if area > 1000:
    #   ellipse = cv2.fitEllipse(contour)
    #   print(ellipse)
    #   print('end cllipse')
    #   im = cv2.ellipse(frame,ellipse,(0,255,0),2)
    # self.custom_wait_key('origin_frame', frame, frame)

    # [vx,vy,x,y] = cv2.fitLine(contour, cv2.cv.CV_DIST_L2,0,0.01,0.01)
    # lefty = int((-x*vy/vx) + y)
    # righty = int(((self.frame_width-x)*vy/vx)+y)
    # img = cv2.line(frame,(self.frame_width-1,righty),(0,lefty),(0,255,0),2)
    # self.custom_wait_key('frame', frame, frame)
    # im = cv2.drawContours(im,[box],0,(0,0,255),2)

  def tracking_by_optical_flow(self):
    tracking_times = 5
    counter = intervel = 4
    grabbed, prvs_frame = self.camera.read()
    if not grabbed:
      return
    prvs_image = cv2.resize(prvs_frame,(self.frame_width, self.frame_height), interpolation=cv2.INTER_LINEAR)

    while(1):
      grabbed, current_frame = self.camera.read()
      if not grabbed:
        return

      if counter is 1:
        counter = intervel
      else:
        counter = counter - 1
        continue

      if tracking_times < 0:
        return 'lost'

      current_image = cv2.resize(current_frame,(self.frame_width, self.frame_height), interpolation=cv2.INTER_LINEAR)
      current_image_bak = current_image.copy()
      # if self.debug:
        # self.custom_wait_key('origin_frame', current_image, current_image)

      contour = self.calculate_optical_flow(current_image, prvs_image)
      if self.estimate_object_by_countor(contour):
        if self.debug and type(contour) is not bool:
          cv2.drawContours(current_image, [contour], 0, (255,255,255), 1, 8)
          # current_rect = cv2.minAreaRect(contour)
          # cv2.drawContours(current_image, [np.int0(cv2.cv.BoxPoints(current_rect))], 0, (255,255,255), 1, 8)
          self.custom_wait_key('origin_frame', current_image, current_image)
          # self.save_image(current_image, 'pics/')
          print('got tracking object and save it...')

        self.add_contour_to_list(contour)
        return True
      else:
        prvs_image = current_image_bak
        tracking_times = tracking_times - 1

  def search_by_optical_flow(self):
    counter = intervel = 2
    for i in xrange(1,20):
      grabbed, prvs_frame = self.camera.read()
      if not grabbed:
        return
    prvs_image = cv2.resize(prvs_frame,(self.frame_width, self.frame_height), interpolation=cv2.INTER_LINEAR)

    while(1):
      grabbed, current_frame = self.camera.read()
      if not grabbed:
        return

      if counter is 0:
        counter = intervel
      else:
        counter = counter - 1
        continue

      current_image = cv2.resize(current_frame,(self.frame_width, self.frame_height), interpolation=cv2.INTER_LINEAR)
      current_image_bak = current_image.copy()
      contour = self.calculate_optical_flow(current_image, prvs_image)

      if self.debug and type(contour) is not bool:
        current_rect = cv2.minAreaRect(contour)
        cv2.drawContours(current_image, [contour], 0, (255,255,255), 1, 8)
        cv2.drawContours(current_image, [np.int0(cv2.cv.BoxPoints(current_rect))], 0, (255,255,255), 1, 8)
        self.custom_wait_key('origin_frame', current_image, current_image)

      if self.got_tracking_object(contour):
        if self.debug:
          self.save_image(current_image, 'pics/')

        del self.tracking_data_list[:]
        self.add_contour_to_list(contour)
        print('got object')
        break
      else:
        prvs_image = current_image_bak

  def track_by_camshif(self, frame, contour):
    area = cv2.contourArea(contour)
    rect = cv2.minAreaRect(contour)
    (vx, vy), (x, y), angle = rect
    vx, vy, x, y = np.int0((vx, vy, x, y))

    roi = frame[vy:(vy+y), vx:(x+vx)]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)

    # compute a HSV histogram for the ROI and store the
    # bounding box
    roiHist = cv2.calcHist([roi], [0], None, [16], [0, 180])
    roiHist = cv2.normalize(roiHist, roiHist, 0, 255, cv2.NORM_MINMAX)
    roiBox = (vx, vy, x, y)
    termination = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

    while(1):
      ret, current_frame = self.camera.read()
      current_image = cv2.resize(current_frame,(self.frame_width, self.frame_height), interpolation=cv2.INTER_LINEAR)
      self.custom_wait_key('origin_frame', current_image, current_image)

      hsv = cv2.cvtColor(current_image, cv2.COLOR_BGR2HSV)
      backProj = cv2.calcBackProject([hsv], [0], roiHist, [0, 180], 1)

      # apply cam shift to the back projection, convert the
      # points to a bounding box, and then draw them
      (r, roiBox) = cv2.CamShift(backProj, roiBox, termination)
      pts = np.int0(cv2.cv.BoxPoints(r))
      cv2.polylines(current_image, [pts], True, (0, 255, 0), 2)
      self.custom_wait_key('frame', current_image, current_image)

    # (150.5, 127.5), (45.0, 91.0), -0.0)
    # image = cv2.imread("./pics/opticalfb-2016-07-23-21-12-53.png")
    # vx, vy, x, y, angle = np.int0((150.5, 127.5, 45.0, 91.0, -0.0))
    # ((163.0, 137.5), (40.0, 101.0), -0.0) 'opticalfb-2016-07-23-21-12-22.png'

  def check_object_postion(self):
    #     self.tracking_data_list.insert(0, {'contour': contour, 'angle': abs(angle), 'rectangle': (vx, vy, width, height), 'height_width_ratio': float(height)/float(width)})

    if self.debug:
      print("check_object_postion")
      print("len self.tracking_data_list %d"%(len(self.tracking_data_list)))

    current_data = self.tracking_data_list[0]
    (x, y, width, height) = current_data.get('rectangle')
    image_ratio = (width * height)/(self.frame_width*self.frame_height)
    position, distance = None, None
    if image_ratio < 0.2:
      distance = 'far'
    elif image_ratio > 0.9:
      distance = 'close'
    else:
      distance = 'ok'

    if (x+width) > 320*0.7:
      position = 'right'
    elif x > 320*0.3 and (x+width) < 320*0.7:
      position = 'ok'
    else:
      position = 'left'

    return position, distance

  def check_object_status(self):
    if self.debug:
      print("check_object_status")
      print("len self.tracking_data_list %d"%(len(self.tracking_data_list)))

    if len(self.tracking_data_list) > 8:
      angle_list = [abs(self.tracking_data_list[i].get('angle') - 45) for i in xrange(8)]
      angle_list.remove(max(angle_list))
      angle_list.remove(min(angle_list))
      mean_angle = np.mean(angle_list)

      height_width_ratio_list = [self.tracking_data_list[i].get('height_width_ratio') for i in xrange(8)]
      height_width_ratio_list.remove(max(height_width_ratio_list))
      height_width_ratio_list.remove(min(height_width_ratio_list))
      height_width_ratio = np.mean(height_width_ratio_list)

      if self.debug:
        print("height_width_ratio is %f"%(height_width_ratio))
        print("mean_angle is %f"%(mean_angle))

      if np.mean(angle_list) < 15 and height_width_ratio>1.25:
        print('the robot is falling down')
        return False

    return True


if __name__ == "__main__":
  pass
else:
  pass


