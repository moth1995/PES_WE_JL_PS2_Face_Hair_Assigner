from .stat import Stat

class Player:
    def __init__(self,data:bytearray,config):
        self.data = data
        self.config = config
        self.name = self.data[:32].decode('utf-16-le')
        self.face_type = Stat(
            self.data, 
            self.config.player["face_type"]["offset"], 
            self.config.player["face_type"]["shift"],
            self.config.player["face_type"]["mask"],
            "Face type"
            )
        self.skin_colour = Stat(
            self.data,
            self.config.player["skin_colour"]["offset"], 
            self.config.player["skin_colour"]["shift"], 
            self.config.player["skin_colour"]["mask"], 
            "Skin Colour"
            )
        self.face_id = Stat(
            self.data, 
            self.config.player["face_id"]["offset"], 
            self.config.player["face_id"]["shift"], 
            self.config.player["face_id"]["mask"], 
            "Face ID"
            )
        self.hair_id = Stat(
            self.data, 
            self.config.player["hair_id"]["offset"], 
            self.config.player["hair_id"]["shift"], 
            self.config.player["hair_id"]["mask"], 
            "Hair ID"
            )
        try:
            if self.config.gui["pes2014_sh_2"]:
                self.sh_2 = Stat(
                    self.data, 
                    self.config.player["sh_2"]["offset"], 
                    self.config.player["sh_2"]["shift"], 
                    self.config.player["sh_2"]["mask"], 
                    "SH 2"
                    )
        except KeyError:
            pass