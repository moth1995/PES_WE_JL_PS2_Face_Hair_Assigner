import yaml
from pathlib import Path

class Config:
    config_dir = "config"
    
    def __init__(self,file="default.yaml"):
        self.file = file
        self.load_config()
        self.get_config_files()

    def load_config(self):
        with open(Path(self.config_dir) / self.file) as stream:
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
        self.games_by_platform = {}
        config_root = Path(self.config_dir)
        for path in sorted(config_root.rglob("*.yaml")):
            if path.name.casefold() == "default.yaml":
                continue

            relative_path = path.relative_to(config_root)
            platform = relative_path.parts[0] if len(relative_path.parts) > 1 else "PS2"
            self.games_by_platform.setdefault(platform, []).append((path.stem, str(relative_path)))
            self.filelist.append(str(relative_path))
            self.games_config.append(path.stem)

