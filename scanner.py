import numpy as np
import cv2
import math

def preprocessing(image):
    print(type(image))
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(grayscale_image, (5, 5), 0)
    thresh = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    _, otsu_thresholded = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((7,7), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
    return morph

def corner_get(morph):
    contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    area_thresh = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > area_thresh:
            area_thresh = area
            big_contour = c
    page = np.zeros_like(image)
    cv2.drawContours(page, [big_contour], 0, (255,255,255), -1)
    target_num_points = 4
    epsilon = 0.04 * cv2.arcLength(big_contour, True)
    corners = cv2.approxPolyDP(big_contour, epsilon, closed=True)
    while len(corners) != target_num_points:
        if len(corners) > target_num_points:
            epsilon *= 1.1
        else:
            epsilon *= 0.9
        corners = cv2.approxPolyDP(big_contour, epsilon, closed=True)
    return corners

def warp(image, corners):
    polygon = image.copy()
    cv2.polylines(polygon, [corners], True, (0,0,255), 1, cv2.LINE_AA)

    def calculate_distance(point1, point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    ab = calculate_distance(corners[0][0], corners[1][0])
    bc = calculate_distance(corners[1][0], corners[2][0])
    cd = calculate_distance(corners[2][0], corners[3][0])
    da = calculate_distance(corners[3][0], corners[0][0])
    max_length_pair1 = max(ab, cd)
    max_length_pair2 = max(bc, da)
    width = np.int0(max_length_pair1)
    height = np.int0(max_length_pair2)
    icorners = []
    for corner in corners:
        pt = [corner[0][0], corner[0][1]]
        icorners.append(pt)
    icorners = np.float32(icorners)
    ocorners = [[width, 0], [0, 0], [0, height], [width, height]]
    ocorners = np.float32(ocorners)
    M = cv2.getPerspectiveTransform(icorners, ocorners)
    warped = cv2.warpPerspective(image, M, (width, height))
    warped = np.flipud(np.transpose(warped, (1, 0, 2)))
    cv2.imwrite('scan.jpg', warped)
    return warped

def process_image(image_path):
    """
    Process an image using the provided image path.
    
    Parameters:
    - image_path: Path to the input image
    """
    image = cv2.imread(image_path)

    morph_image = preprocessing(image)
    corners_result = corner_get(morph_image)
    warped=warp(image, corners_result)
    return warped

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image processing and perspective transformation.")
    parser.add_argument("image_path", help="Path to the input image")
    args = parser.parse_args()

    image = cv2.imread(args.image_path)

    morph_image = preprocessing(image)
    corners_result = corner_get(morph_image)
    warp(image, corners_result)
