import cv2
import numpy as np

def to_binarize(matlike, threshold):
    if len(matlike.shape) == 3 and matlike.shape[2] == 3:
        matlike = cv2.cvtColor(matlike, cv2.COLOR_BGR2GRAY)
    
    _, binary_image = cv2.threshold(matlike, threshold, 255, cv2.THRESH_BINARY)
    
    return binary_image


def load_and_binarize(image_path, threshold):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Unable to load the image: {image_path}")
    _, binary_img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return binary_img


def is_significant_white_area(binary_img: np.ndarray, threshold: float = 0.5):
    white_pixel = np.count_nonzero(binary_img)
    total_pixel = binary_img.size
    ratio = white_pixel / total_pixel
    return ratio > threshold


def split_img_vertical(image: np.ndarray):
    height, _ = image.shape[:2]
    
    upper = image[:height // 2, :]
    lower = image[height // 2:, :]
    
    return upper, lower


def split_img_horizon(image: np.ndarray):
    _, width = image.shape[:2]
    
    left = image[:, :width // 2]
    right = image[:, width // 2:]
    
    return left, right


def calc_match_rate(binary_img1, binary_img2):
    if binary_img1.shape != binary_img2.shape:
        raise ValueError("Image sizes do not match.")

    difference = cv2.absdiff(binary_img1, binary_img2)
    match_count = np.count_nonzero(difference == 0)
    return  match_count / binary_img1.size * 100


def calc_highest_match(binary_img, compare_binary_imgs):
    higehest_match_idx = None
    highest_match_rate = 0

    for idx, compare_binary_img in enumerate(compare_binary_imgs):
        match_rate = calc_match_rate(binary_img, compare_binary_img)

        if match_rate > highest_match_rate:
            highest_match_rate = match_rate
            higehest_match_idx = idx
            
    return higehest_match_idx, highest_match_rate


def is_color_detected(image: np.ndarray, target_color: tuple, tolerance=50):
    """
    - image (ndarray)  
    - target_color (tuple): チェックする色 (B, G, R) の順
    - tolerance (int): 許容する色の差

    """
    lower_bound = np.array([max(c - tolerance, 0) for c in target_color])
    upper_bound = np.array([min(c + tolerance, 255) for c in target_color])

    mask = cv2.inRange(image, lower_bound, upper_bound)
    return np.any(mask == 255)


def crop_image(img, x, y, width, height):
    cropped_img = img[y:y+height, x:x+width]
    return cropped_img


def is_contain_template(src: np.ndarray, image_path, threshold=0.7, use_gray=True, x=None, y=None, width=None, height=None):
    src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) if use_gray else src
    if all(v is not None for v in [x, y, width, height]):
        src = src[y : y + height, x : x + width]

    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE if use_gray else cv2.IMREAD_COLOR)
    res = cv2.matchTemplate(src, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    return max_val > threshold