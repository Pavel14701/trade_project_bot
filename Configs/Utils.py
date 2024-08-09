class UnpackDict:
    def unpack(self):
        for key, value in self.param_dict.items():
            if isinstance(value, (int, float, str)):
                setattr(self, key, value)
            elif isinstance(value, (list, dict, tuple, set)):
                setattr(self, key, value)


def unpack_dict(param_dict:dict):
    for key, value in param_dict.items():
        if isinstance(value, (int, float, str)):
            locals()[key] = value
        elif isinstance(value, (list, dict, tuple, set)):
            locals()[key] = value