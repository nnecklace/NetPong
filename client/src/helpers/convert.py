import math

def frac_to_px(frac, scale):
  return frac * scale

def px_to_frac(px, scale):
  return px / scale

def mag(vec):
  return math.sqrt((math.pow(vec[0], 2)+ math.pow(vec[1], 2)))

def normalize(vec):
  magnitude = mag(vec)
  return [vec[0]/magnitude, vec[1]/magnitude]