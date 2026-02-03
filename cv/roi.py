class ROI:
    def __init__(self, x, y, w, h, player_id):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.player_id = player_id

    def contains(self, bx, by, bw, bh):
        # Check if the center of the bounding box is within the ROI
        center_x = bx + bw / 2
        center_y = by + bh / 2
        return (self.x <= center_x <= self.x + self.w and
                self.y <= center_y <= self.y + self.h)

def get_default_rois(frame_width, frame_height):
    # Two boxes, one on left, one on right
    box_w = 400
    box_h = 600
    y_offset = (frame_height - box_h) // 2
    
    roi1 = ROI(50, y_offset, box_w, box_h, 1)
    roi2 = ROI(frame_width - box_w - 50, y_offset, box_w, box_h, 2)
    
    return [roi1, roi2]
