import numpy as np
import torch

class CreateFadeMaskAdvanced:
    # FUNCTION = "createfademask"
    DESCRIPTION = """
    Create a batch of masks interpolated between given frames and values. 
    Uses same syntax as Fizz' BatchValueSchedule.
    First value is the frame index (not that this starts from 0, not 1) 
    and the second value inside the brackets is the float value of the mask in range 0.0 - 1.0  

    For example the default values:  
    0:(0.0)  
    7:(1.0)  
    15:(0.0)  

    Would create a mask batch fo 16 frames, starting from black, 
    interpolating with the chosen curve to fully white at the 8th frame, 
    and interpolating from that to fully black at the 16th frame.
    """

    # @classmethod
    # def INPUT_TYPES(s):
    #     return {
    #         "required": {
    #              "points_string": ("STRING", {"default": "0:(0.0),\n7:(1.0),\n15:(0.0)\n", "multiline": True}),
    #              "invert": ("BOOLEAN", {"default": False}),
    #              "frames": ("INT", {"default": 16,"min": 2, "max": 255, "step": 1}),
    #              "width": ("INT", {"default": 512,"min": 1, "max": 4096, "step": 1}),
    #              "height": ("INT", {"default": 512,"min": 1, "max": 4096, "step": 1}),
    #              "interpolation": (["linear", "ease_in", "ease_out", "ease_in_out"],),
    #     },
    # } 

    def createfademask(self, frames, width, height, invert, points_string, interpolation):
        def ease_in(t):
            return t * t

        def ease_out(t):
            return 1 - (1 - t) * (1 - t)

        def ease_in_out(t):
            return 3 * t * t - 2 * t * t * t

        # Parse the input string into a list of tuples
        points = []
        points_string = points_string.rstrip(',\n')
        for point_str in points_string.split(','):
            frame_str, color_str = point_str.split(':')
            frame = int(frame_str.strip())
            color = float(color_str.strip()[1:-1])  # Remove parentheses around color
            points.append((frame, color))

        # Check if the last frame is already in the points
        if len(points) == 0 or points[-1][0] != frames - 1:
            # If not, add it with the color of the last specified frame
            points.append((frames - 1, points[-1][1] if points else 0))

        # Sort the points by frame number
        points.sort(key=lambda x: x[0])

        batch_size = frames
        out = []
        image_batch = np.zeros((batch_size, height, width), dtype=np.float32)

        # Index of the next point to interpolate towards
        next_point = 1

        for i in range(batch_size):
            while next_point < len(points) and i > points[next_point][0]:
                next_point += 1

            # Interpolate between the previous point and the next point
            prev_point = next_point - 1
            t = (i - points[prev_point][0]) / (points[next_point][0] - points[prev_point][0])
            if interpolation == "ease_in":
                t = ease_in(t)
            elif interpolation == "ease_out":
                t = ease_out(t)
            elif interpolation == "ease_in_out":
                t = ease_in_out(t)
            elif interpolation == "linear":
                pass  # No need to modify `t` for linear interpolation

            color = points[prev_point][1] - t * (points[prev_point][1] - points[next_point][1])
            color = np.clip(color, 0, 255)
            image = np.full((height, width), color, dtype=np.float32)
            image_batch[i] = image

        output = torch.from_numpy(image_batch)
        mask = output
        out.append(mask)

        if invert:
            return (1.0 - torch.cat(out, dim=0),)
        return (torch.cat(out, dim=0),)

if __name__=="__main__":
    # Test node
    test_func = CreateFadeMaskAdvanced()
    fade_mask = test_func.createfademask(frames=96, width=512, height=512, invert=False, points_string="0:(1.0),\n20:(1.0),\n24:(0.0),\n92:(0.0),\n96:(1.0)\n", interpolation='linear')
    # print(fade_mask[0].shape, fade_mask[0].max(), fade_mask[0].min())
    fade_mask = fade_mask[0]
    from PIL import Image
    fade_mask = (fade_mask*255.0).unsqueeze(-1).repeat(1,1,1,3).chunk(12)
    fade_mask = [torch.cat(item.chunk(8), dim=2).squeeze(0) for item in fade_mask]
    fade_mask = torch.cat(fade_mask, dim=0)
    Image.fromarray(fade_mask.numpy().astype(np.uint8)).save("./test.png")