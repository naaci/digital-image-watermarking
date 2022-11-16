"""
Niu, Y., Cui, X., Li, Q., & Ding, J. (2016). 
A SVD-Based Color Image Watermark Algorithm in DWT Domain
Advanced Graphic Communications, Packaging Technology and Materials (pp. 303–309). 
https://doi.org/10.1007/978-981-10-0072-0_39
"""

from pywt import dwt2, idwt2

from Chandra2002 import Watermarker as chandraWatermark


class Watermarker:
    IMAGE_TO_WATERMARK_RATIO = 2

    def __init__(self, scale_factor=2**(-4)) -> None:
        self.sf = scale_factor

    def add_watermark(self, host, watermark):
        LL, (HL, LH, HH) = dwt2(host, wavelet='haar')

        self.svd_watermarker = chandraWatermark(self.sf)

        LL_ = self.svd_watermarker.add_watermark(LL, watermark)

        return idwt2((LL_, (HL, LH, HH)), 'haar')

    def extract_watermark(self, watermarked_image):
        LL, (HL, LH, HH) = dwt2(watermarked_image, wavelet='haar')

        return self.svd_watermarker.extract_watermark(LL)


if __name__ == "__main__":
    from numpy import asarray, isclose, random
    watermarker = Watermarker(.01)
    host = random.random((500, 600))
    watermark = random.random(
        asarray(host.shape) // watermarker.IMAGE_TO_WATERMARK_RATIO)
    watermark[watermark >= .5] = 1
    watermark[watermark < .5] = 0
    watermarked = watermarker.add_watermark(host, watermark)
    watermark_ = watermarker.extract_watermark(watermarked)
    c = isclose(watermark, watermark_)
    print("max err:", abs(watermark - watermark_).max())
    print(c.all() or f"{watermark[c].size / watermark.size:>.2%} True")
