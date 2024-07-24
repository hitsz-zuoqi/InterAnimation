class IPAdapterBatch(IPAdapterAdvanced):
    def __init__(self):
        self.unfold_batch = True
    # @classmethod
    # def INPUT_TYPES(s):
    #     return {
    #         "required": {
    #             "model": ("MODEL", ),
    #             "ipadapter": ("IPADAPTER", ),
    #             "image": ("IMAGE",),
    #             "weight": ("FLOAT", { "default": 1.0, "min": -1, "max": 5, "step": 0.05 }),
    #             "weight_type": (WEIGHT_TYPES, ),
    #             "start_at": ("FLOAT", { "default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001 }),
    #             "end_at": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001 }),
    #             "embeds_scaling": (['V only', 'K+V', 'K+V w/ C penalty', 'K+mean(V) w/ C penalty'], ),
    #         },
    #         "optional": {
    #             "image_negative": ("IMAGE",),
    #             "attn_mask": ("MASK",),
    #             "clip_vision": ("CLIP_VISION",),
    #         }
    #     }