"""Vision pipeline: webcam -> screen region -> template matching + OCR.

PRD chain: Logitech C920 watches the target machine's screen; the agent reads
it back via template matching (find UI elements) and OCR (read text).

Campsite-testable: camera_index=0 uses the MacBook's built-in camera. Point it
at anything with text to exercise capture -> deskew -> OCR without the C920.

Install:  pip install opencv-python pytesseract numpy
          brew install tesseract          (macOS)
"""

import time

import cv2
import numpy as np

try:
    import pytesseract
except ImportError:
    pytesseract = None


class Vision:
    def __init__(self, camera_index=0, warm_up_frames=10):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"camera {camera_index} not available")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)   # C920 native
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.screen_quad = None        # 4 corners of the monitor in camera space
        for _ in range(warm_up_frames):                # let auto-exposure settle
            self.cap.read()

    # ---- capture ---------------------------------------------------------------
    def frame(self):
        ok, img = self.cap.read()
        if not ok:
            raise RuntimeError("frame grab failed")
        return img

    # ---- screen rectification -----------------------------------------------------
    def calibrate_screen(self, quad=None):
        """Lock the monitor's 4 corners (TL, TR, BR, BL) in camera coords.

        If quad is None, auto-detect: the screen is usually the largest bright
        4-sided contour in view. Show a white fullscreen page on the target
        machine while calibrating for best results.
        """
        if quad is not None:
            self.screen_quad = np.array(quad, dtype=np.float32)
            return self.screen_quad
        img = self.frame()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255,
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        best = None
        for c in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
            approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
            if len(approx) == 4 and cv2.contourArea(approx) > 0.1 * img.size / 3:
                best = approx.reshape(4, 2).astype(np.float32)
                break
        if best is None:
            raise RuntimeError("screen not found -- show a bright fullscreen "
                               "page, or pass corners manually")
        self.screen_quad = _order_quad(best)
        return self.screen_quad

    def screen(self, out_w=1920, out_h=1080):
        """Rectified screen image (perspective-corrected to out_w x out_h)."""
        img = self.frame()
        if self.screen_quad is None:
            return img                                  # uncalibrated: raw frame
        dst = np.array([[0, 0], [out_w, 0], [out_w, out_h], [0, out_h]],
                       dtype=np.float32)
        m = cv2.getPerspectiveTransform(self.screen_quad, dst)
        return cv2.warpPerspective(img, m, (out_w, out_h))

    # ---- template matching -----------------------------------------------------------
    def find(self, template_path, threshold=0.80):
        """Find a UI element. Returns (x, y, confidence) of its center in
        rectified screen coords, or None. Multi-scale to absorb camera drift."""
        screen = cv2.cvtColor(self.screen(), cv2.COLOR_BGR2GRAY)
        tmpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if tmpl is None:
            raise FileNotFoundError(template_path)
        best = (None, -1)
        for scale in (0.9, 0.95, 1.0, 1.05, 1.1):
            t = cv2.resize(tmpl, None, fx=scale, fy=scale)
            if t.shape[0] > screen.shape[0] or t.shape[1] > screen.shape[1]:
                continue
            res = cv2.matchTemplate(screen, t, cv2.TM_CCOEFF_NORMED)
            _, conf, _, loc = cv2.minMaxLoc(res)
            if conf > best[1]:
                cx = loc[0] + t.shape[1] // 2
                cy = loc[1] + t.shape[0] // 2
                best = ((cx, cy, conf), conf)
        found, conf = best
        return found if conf >= threshold else None

    # ---- OCR ------------------------------------------------------------------------------
    def read_text(self, region=None, psm=6):
        """OCR the screen (or a (x, y, w, h) region of it). psm 6 = text block,
        psm 7 = single line, psm 11 = sparse."""
        if pytesseract is None:
            raise RuntimeError("pytesseract missing: pip install pytesseract "
                               "&& brew install tesseract")
        img = self.screen()
        if region:
            x, y, w, h = region
            img = img[y:y + h, x:x + w]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2)       # upscale helps webcam OCR
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 11)
        return pytesseract.image_to_string(gray, config=f"--psm {psm}").strip()

    def wait_for(self, template_path, timeout_s=15, poll_s=0.5, threshold=0.80):
        """Block until a template appears (e.g. wait for a window to open)."""
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            hit = self.find(template_path, threshold)
            if hit:
                return hit
            time.sleep(poll_s)
        return None

    def save_frame(self, path="frame.png", rectified=True):
        cv2.imwrite(path, self.screen() if rectified else self.frame())
        return path

    def close(self):
        self.cap.release()


def _order_quad(pts):
    """Order 4 points TL, TR, BR, BL."""
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)],
                     pts[np.argmax(s)], pts[np.argmax(d)]], dtype=np.float32)


if __name__ == "__main__":
    # campsite smoke test on the built-in camera
    v = Vision(camera_index=0)
    print("frame:", v.frame().shape)
    print("saved:", v.save_frame("test_frame.png", rectified=False))
    if pytesseract:
        print("OCR says:", repr(v.read_text()[:200]))
    v.close()
