import time
import cv2
import numpy as np

class ImageCalculater(object):
  """docstring for ImageCalculater"""
  def __init__(self, width, height):
    self.frame_width = width
    self.frame_height = height

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
      self.custom_wait_key('frame', current_img, prvs_img)

  def isTrackedPerson(self, rect_w, rect_h, area):
      if area > 800:
          if float(rect_h)/float(rect_w) > 2:
              self.is_get_object = True
              print("get tracking object...")
              print("current area is %d, %f"%(area, float(rect_h)/float(rect_w)) )
              return True
          elif float(rect_h)/float(rect_w) < 1.25:
              print("object is down...")
              return False

      else:
          return False

  def calculate_walk_data(self, rect, area, frame):
    if rect == -1:
        return

    (rect_x, rect_y, rect_w, rect_h) = rect

    if self.isTrackedPerson(rect_w, rect_h, area):
        self.display_track_image(rect, area, frame)

  def calculate_optical_flow(self, prvs_gray, current_gray):
    flow = cv2.calcOpticalFlowFarneback(prvs_gray, current_gray, 0.5, 3, 15, 3, 5, 1.2, 0)
    binary_pic = np.zeros(current_gray.shape, np.uint8)

    h, w = current_gray.shape
    total_threshold=0
    for i in xrange(0,h,5):
        for j in xrange(0,w,5):
            fx, fy = flow[i, j]
            total_threshold += abs(fx) + abs(fy)
            if abs(fx) + abs(fy) > 0.4:
                binary_pic[i, j] = 255;
    print('mean threshold is %f'%(total_threshold/(h*w)))

    binary_pic_translated = self.conduct_translation(binary_pic)
    contours, hierarchy = cv2.findContours(binary_pic_translated,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    print('contours is %d'%(len(contours)))
    largest_area = 0
    largest_contour_index = 0
    bounding_rect_x, bounding_rect_y, bounding_rect_w, bounding_rect_h = 0, 0, 0, 0
    if len(contours) > 0:
        for k in xrange(0, len(contours)):
            area = cv2.contourArea(contours[k])
            if largest_area < area:
                largest_area = area
                largest_contour_index = k
                bounding_rect_x, bounding_rect_y, bounding_rect_w, bounding_rect_h = cv2.boundingRect(contours[k])
        return ((bounding_rect_x, bounding_rect_y, bounding_rect_w, bounding_rect_h), largest_area)
    else:
        print("contours is not found...")
        return (-1, -1)

  def search_by_optical_flow(self, camera):
    ret, prvs_frame = camera.read()
    count = intervel = 2

    while(1):
      ret, current_frame = camera.read()
      current_gray = cv2.resize(current_frame,(self.frame_width, self.frame_height), interpolation=cv2.INTER_LINEAR)
      # self.custom_wait_key('origin_frame', current_gray, current_gray)
      current_gray = cv2.cvtColor(current_gray, cv2.COLOR_BGR2GRAY)
      prvs_gray = cv2.resize(prvs_frame,(self.frame_width, self.frame_height), interpolation=cv2.INTER_LINEAR)
      prvs_gray = cv2.cvtColor(prvs_gray, cv2.COLOR_BGR2GRAY)

      count = count - 1
      if count == 1:
          count = intervel
          rect, area = self.calculate_optical_flow(prvs_gray, current_gray)
          self.calculate_walk_data(rect, area, current_gray)

          prvs_frame = current_frame

      print("current area %d"%(area))



if __name__ == "__main__":
  pass
else:
  pass
