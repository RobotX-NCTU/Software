from duckietown_msgs.msg import Segment, SegmentList
import numpy as np


__all__ = [
    'fuzzy_segment_list_image_space',
    
]

def fuzzy_segment_list_image_space(segment_list, n, intensity):
    S2 = SegmentList()
    
    for segment in segment_list.segments:
        for _ in range(n): 
            
            s2 = fuzzy_segment(segment, intensity) 
            S2.segments.append(s2)
    return S2

def fuzzy_color(segment_list):
    S2 = SegmentList()
    
    for segment in segment_list.segments:
        for color in [segment.YELLOW, segment.WHITE]:
            s2 = fuzzy_segment(segment, intensity=0.001)
            s2.color = color 
            S2.segments.append(s2)
    return S2

def fuzzy_segment(s1, intensity):
    s2 = Segment()
    def noise():
        return np.random.randn() * intensity
    for i in range(2):
        s2.pixels_normalized[i].x = s1.pixels_normalized[i].x + noise()
        s2.pixels_normalized[i].y = s1.pixels_normalized[i].y + noise()
    s2.color = s1.color
    return s2
