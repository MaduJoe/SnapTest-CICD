# utils.py

import re

def slugify(text):
    """
    공백, 특수문자 제거 → 파일명 안전한 형식으로 변경
    ex) "Addition Test #1" → "Addition_Test_1"
    """
    return re.sub(r'\W+', '_', text).strip('_')
