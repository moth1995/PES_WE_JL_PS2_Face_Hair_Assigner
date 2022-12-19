import yaml
from pathlib import Path

class Config:
    config_dir = "config"
    
    def __init__(self,file="default.yaml"):
        self.file = file
        self.load_config()
        self.get_config_files()

    def load_config(self):
        with open(self.config_dir + "/" +self.file) as stream:
            self.file = yaml.safe_load(stream)
        self.game_name = self.file["game_name"]
        self.gui = self.file["gui"]
        self.player_edit_mode = self.file["player_edit_mode"]
        self.player = self.file["player"]


        try:
            self.platform = self.file["platform"]
            self.psp_pointer = self.file["psp_pointer"]
            self.psp_offset = self.file["psp_offset"]
        except:
            self.platform = 0
            self.psp_pointer = 0
            self.psp_offset = []

    def get_config_files(self):
        self.filelist = []
        self.games_config = []
        for p in Path(self.config_dir).iterdir():
            if p.is_file():
                self.filelist.append(p.name)
                self.games_config.append(p.stem)
