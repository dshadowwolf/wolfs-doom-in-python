import math

def deg_to_bam16(deg):
    return math.floor((deg/24)*4369)

def bam16_to_deg(bam):
    return math.floor((bam/4369)*24)

def deg_to_rad(deg):
    return deg * (math.pi/180)

def rad_to_deg(rad):
    return rad / (math.pi/180)

def bam16_to_rad(bam):
    return deg_to_rad(bam16_to_deg(bam))

def rad_to_bam16(rad):
    return deg_to_bam16(rad_to_deg(rad))

def dot_product(vec1, vec2):
    return (vec1[0]*vec2[0]+vec1[1]*vec2[1])