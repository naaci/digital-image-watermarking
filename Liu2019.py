"""
Liu, J., Huang, J., Luo, Y., Cao, L., Yang, S., Wei, D., & Zhou, R. (2019). 
An Optimized Image Watermarking Method Based on HD and SVD in DWT Domain. 
IEEE Access, 7, 80849–80860. 
https://doi.org/10.1109/ACCESS.2019.2915596
"""

from numpy import log2
from pywt import wavedec2, waverec2
from scipy.linalg import hessenberg

from Chandra2002 import Watermarker as chandraWatermarker


class Watermarker:
    IMAGE_TO_WATERMARK_RATIO = 2

    def __init__(self, scale_factor=2**(-4)) -> None:
        self.sf = scale_factor

    def add_watermark(self, host, watermark):
        self.svd_watermarker = chandraWatermarker(self.sf)

        # Step 1. Based on R-level DWT,C is decomposed into the components of LL,LH,HL,HH, where R=log_2(M/N)
        self.level = int(log2(host.shape[0] // watermark.shape[0]))
        LL, *HH = wavedec2(host, wavelet='haar', level=self.level)

        # Step 2. HD is performed on LL
        H, P = hessenberg(LL, calc_q=True)

        H_ = self.svd_watermarker.add_watermark(H, watermark)

        # # Step 3. Apply SVD to H
        # HU, self.Hs, HVh = svd(H)

        # # Step 4. W is applied with SVD
        # self.U_w, s_w, self.Vh_w = svd(watermark_image)

        # # Step 5. Compute an embedded singular value HS_w* by adding HS_w and S_w with a scaling factor α
        # Hs_w_ = self.Hs + self.sf * s_w

        # # Step 6. The watermarked sub-band H∗ is generated byusing the inverse SVD
        # H_ = HU @ diag(Hs_w_) @ HVh

        # Step 7. A new low-frequency approximate sub-band LL∗ is reconstructed based on the inverse HD which is given by
        LL_ = P @ H_ @ P.T.conj()

        # Step 8. The watermarked image C∗ is obtained by performing the inverse R-level DWT
        return waverec2((LL_, *HH), wavelet='haar')

    def extract_watermark(self, watermarked_image):

        # Step 1.The watermarked host image C∗ is decomposedinto four sub-bands by R-level DWT
        LL_, *_ = wavedec2(watermarked_image, wavelet='haar', level=self.level)

        # Step 2.HD is performed on LL
        H_ = hessenberg(LL_)

        return self.svd_watermarker.extract_watermark(H_)

        # # Step 3.Apply SVD to H
        # Hs_w_ = svd(H_, compute_uv=False)

        # # Step 4.The extracted singular value S_w* is gained by
        # s_w = (Hs_w_ - self.Hs) / self.sf

        # # Step 5.The extracted watermark W∗ is reconstructed by inverse SVD
        # return self.U_w @ diag(s_w) @ self.Vh_w


if __name__ == "__main__":
    from numpy import asarray, isclose, random
    watermarker = Watermarker(.01)
    host = random.random((512, 512))
    watermark = random.random(
        asarray(host.shape) // watermarker.IMAGE_TO_WATERMARK_RATIO)
    watermark[watermark >= .5] = 1
    watermark[watermark < .5] = 0
    watermarked = watermarker.add_watermark(host, watermark)
    watermark_ = watermarker.extract_watermark(watermarked)
    c = isclose(watermark, watermark_)
    print("max err:", abs(watermark - watermark_).max())
    print(c.all() or f"{watermark[c].size / watermark.size:>.2%} True")
