import pymem
import pymem.process
import pymem.exception
import psutil
from editor import Player, Stat
from tkinter import Tk, messagebox, ttk, Button, Label, Menu, Spinbox, filedialog, IntVar
from pathlib import Path
from .config import Config
from pymem.ptypes import RemotePointer

class Gui(Tk):
    filename = ""
    appname='PES/WE/JL PS2 Face/Hair assigner'
    def __init__(self):
        super().__init__()
        #self.master = master
        self.title(self.appname)
        w = 350 # width for the Tk root
        h = 250 # height for the Tk root
        # get screen width and height
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen 
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        try:
            self.create_config()
        except FileNotFoundError as e:
            messagebox.showerror(title=self.appname, message=f"No config files found code error {e}")
            self.destroy()
        self.my_menu=Menu(self)
        self.config(menu=self.my_menu)
        self.file_menu = Menu(self.my_menu, tearoff=0)
        self.edit_menu = Menu(self.my_menu, tearoff=0)
        self.help_menu = Menu(self.my_menu, tearoff=0)
        self.my_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.search_exe)
        self.file_menu.add_command(label="Search process", command=self.get_by_process_name)
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.my_menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_submenu = Menu(self.my_menu, tearoff=0)
        # Dinamically loading game versions as sub menu
        for i in range(len(self.my_config.games_config)):
            self.edit_submenu.add_command(label=self.my_config.games_config[i],command= lambda i=i: self.change_config(self.my_config.filelist[i]))
        self.edit_menu.add_cascade(label="Game Version", menu=self.edit_submenu)

        self.my_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Manual", command=self.show_help)
        self.help_menu.add_command(label="About", command=self.show_thanks)

        self.game_ver_lbl = Label(self, text=f"Game version: {self.my_config.game_name}")
        self.game_ver_lbl.pack()
        self.player_lbl = Label(self, text="Player Name: ")
        self.player_lbl.pack()

        self.face_type_lbl = Label(self, text="Face Type").pack()
        self.face_type_dropdown = ttk.Combobox(self,values=self.my_config.gui["face_type"],state="readonly")
        self.face_type_dropdown.current(0)
        self.face_type_dropdown.bind('<<ComboboxSelected>>', lambda event: self.set_param())
        self.face_type_dropdown.pack()

        self.skin_lbl = Label(self,text="Skin Colour").pack()
        self.skin_spb_var = IntVar()
        self.skin_spb_var.set(1)
        self.skin_spb = Spinbox(self, textvariable=self.skin_spb_var, from_=1, to=self.my_config.gui["skin_colour_max"],command = self.set_param)
        self.skin_spb.bind('<Return>', lambda event: self.set_param())
        self.skin_spb.pack()


        self.face_id_lbl = Label(self,text="Face ID").pack()
        self.face_spb_var = IntVar()
        self.face_spb_var.set(1)
        self.face_id_spb = Spinbox(self, textvariable=self.face_spb_var, from_=1, to=self.my_config.gui["face_id_max"],command = self.set_param)
        self.face_id_spb.bind('<Return>', lambda event: self.set_param())
        self.face_id_spb.pack()

        self.sh2_var = IntVar()
        self.sh2_var.set(0)
        self.sh2_cb = ttk.Checkbutton(self,text = "Special Hairstyles 2", variable = self.sh2_var, command=self.set_param, state='disabled')
        self.sh2_cb.pack()
        try:
            if self.my_config.gui["pes2014_sh_2"]:
                self.sh2_cb.config(state='active')
        except KeyError:
            pass
        self.hair_id_lbl = Label(self,text="Special Hairstyle ID").pack()
        self.hair_spb_var = IntVar()
        self.hair_spb_var.set(0)
        self.hair_id_spb = Spinbox(self, textvariable=self.hair_spb_var, from_=0, to=self.my_config.gui["hair_id_max"],command = self.set_param)
        self.hair_id_spb.bind('<Return>', lambda event: self.set_param())
        self.hair_id_spb.pack()
        self.read_values = Button(self,text="Read data", command=self.read_player).pack()

    def create_config(self):
        self.my_config = Config()

    def change_config(self, file):
        self.my_config = Config(file)
        self.refresh_gui()

    def refresh_gui(self):
        self.game_ver_lbl.config(text=f"Game version: {self.my_config.game_name}")
        self.face_type_dropdown.config(values=self.my_config.gui["face_type"])
        self.skin_spb.config(to=self.my_config.gui["skin_colour_max"])
        self.face_id_spb.config(to=self.my_config.gui["face_id_max"])
        self.hair_id_spb.config(to=self.my_config.gui["hair_id_max"])
        self.player_edit_mode = self.my_config.player_edit_mode

        self.platform = self.my_config.platform
        self.psp_pointer = self.my_config.psp_pointer
        self.psp_offset = self.my_config.psp_offset

        try:
            if self.my_config.gui["pes2014_sh_2"]:
                self.sh2_cb.config(state='active')
        except KeyError:
            self.sh2_cb.config(state='disabled')

    def search_exe(self):
        self.filename = filedialog.askopenfilename(initialdir=".",title=self.appname, filetypes=([("PCSX2 Executable", ".exe"),]))
        if self.filename!="":
            self.load_data()
            self.read_player()

    def get_by_process_name(self):
        if self.platform == 0:
            PROCNAME = "pcsx2.exe"
        else:
            PROCNAME = "PPSSPPWindows64.exe"
        for proc in psutil.process_iter():
            if proc.name() == PROCNAME:
                self.filename = proc.name()
                self.load_data()
                self.read_player()

    def show_help(self):
        messagebox.showinfo(title=self.appname,message=
        """
        Work in progress...
        """.replace('        ', ''))

    def show_thanks(self):
        messagebox.showinfo(title=self.appname,message="Developed by PES Indie")

    def check_version(self):
        if Path(self.filename).name == "pcsx2.exe":
            """
            If we lay here it is pcsx2 emulator
            """
            return True
        elif Path(self.filename).name == "PPSSPPWindows64.exe":
            return True

        else:
            """
            We shouldn't be here
            """
            messagebox.showerror(title=self.appname,message="Emulator Version")
            return 0

    def getPointerAddress(self, base, offsets):
        remote_pointer = RemotePointer(self.pm.process_handle, base)
        for offset in offsets:
            if offset != offsets[-1]:
                remote_pointer = RemotePointer(self.pm.process_handle, remote_pointer.value + offset)
            else:
                return remote_pointer.value + offset

    def load_data(self):
        if self.check_version()==0:
            return 0
        self.pes_we_exe = Path(self.filename).name
        self.player_bytes_size = 124
        try:
            self.pm = pymem.Pymem(self.pes_we_exe)
            if self.platform == 0:
                self.client = pymem.process.module_from_name(self.pm.process_handle, self.pes_we_exe).lpBaseOfDll
                self.player_edit_mode = self.my_config.player_edit_mode  - self.client
            else:
                self.player_edit_mode = self.getPointerAddress(self.pm.base_address + self.psp_pointer, offsets=self.psp_offset)

        except pymem.exception.ProcessNotFound as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
            return 0

    def read_player(self):
        if self.filename=="":
            messagebox.showerror(title=self.appname, message="You must select your exe file first or run your game\nbefore trying to read or set any data")
            return 0
        try:
            if self.platform == 0:
                self.player = Player(bytearray(self.pm.read_bytes(self.client + self.player_edit_mode, self.player_bytes_size)), self.my_config)
            else:
                self.player = Player(bytearray(self.pm.read_bytes(self.player_edit_mode, self.player_bytes_size)), self.my_config)

        except pymem.exception.MemoryReadError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
            return 0
        except pymem.exception.ProcessError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
            return 0
        self.player_lbl.config(text=f"Player Name: {self.player.name}")
        self.face_type_dropdown.current(self.player.face_type.get_value())
        self.skin_spb_var.set(self.player.skin_colour.get_value() + 1)
        self.hair_spb_var.set(self.player.hair_id.get_value())
        try:
            if self.my_config.gui["pes2014_sh_2"]:
                self.sh2_var.set(self.player.sh_2.get_value())
                self.face_spb_var.set(self.player.face_id.get_value())
        except KeyError:
            self.face_spb_var.set(self.player.face_id.get_value() + 1)


        #self.test()

    def test(self):
        #218911CD
        pm = pymem.Pymem(self.pes_we_exe)
        client = pymem.process.module_from_name(self.pm.process_handle, self.pes_we_exe).lpBaseOfDll
        test_pl = [1, 2, 3, 4, 5, 6]
        pl_list = []
        for i in test_pl:
            pl_list.append(bytearray(self.pm.read_bytes(0x21891168 + (self.player_bytes_size * i), self.player_bytes_size)))
        print(pl_list)
        #data = self.player.data
        #validate=[*range(0, 8, 1)]#+[*range(0, 6, 1)]
        #validate = [0,1,2,3,4,5,6]
        #validate = [6,5,4,3,2,1,0]
        #validate = [122,933,309,97,145,2]
        validate = [121,932,308,141,144,1]
        #print(validate)
        test=[]
        print(Stat(self.player.data,101, 5, 511, "face").get_value())
        print(Stat(self.player.data,102, 0, 511, "face").get_value())
        """
        for shift in range(0,65536):
            #print (f"the mask is {mask}")
            for mask in range(0,65536):
                #if mask==2047:
                #    print("llegamos al punto conocido")
                #mask=4095
                offset = 101
                stat_name = ""
                test.append(Stat(pl_list[0],offset, shift, mask, stat_name).get_value())
                test.append(Stat(pl_list[1],offset, shift, mask, stat_name).get_value())
                test.append(Stat(pl_list[2],offset, shift, mask, stat_name).get_value())
                test.append(Stat(pl_list[3],offset, shift, mask, stat_name).get_value())
                test.append(Stat(pl_list[4],offset, shift, mask, stat_name).get_value())
                test.append(Stat(pl_list[5],offset, shift, mask, stat_name).get_value())
                #test.append((get_value(of,690,offset, shift, mask, stat_name) ))
                #test.append((get_value(of,4473,offset, shift, mask, stat_name) ))
                #test.append((get_value(of,1485,offset, shift, mask, stat_name) ))
                #print (test)
                #test.append((get_value(of,4521,offset, shift, mask, stat_name) ))
                #test.append((get_value(of,1229,offset, shift, mask, stat_name) ))
                #test.append((get_value(of,690,offset, shift, mask, stat_name) ))
                #test.append((get_value(of,4029,offset, shift, mask, stat_name) ))

                if test == validate:
                    print(shift, mask)
                test=[]
            """
        print("END")

    def set_param(self):
        if self.filename=="":
            messagebox.showerror(title=self.appname, message="You must select your exe file first or run your game\nbefore trying to read or set any data")
            return 0

        if self.check_val(self.face_type_dropdown.current(),0,len(self.my_config.gui["face_type"])-1):
            self.player.face_type.set_value(self.face_type_dropdown.current())
        else:
            messagebox.showerror(title=self.appname, message=f"Value for {self.player.face_type.name} out of range, check Help-> Manual")

        if self.check_val(self.skin_spb_var.get()-1, 0, self.my_config.gui["skin_colour_max"]):
            self.player.skin_colour.set_value(self.skin_spb_var.get()-1)
        else:
            messagebox.showerror(title=self.appname, message=f"Value for {self.player.skin_colour.name} out of range, check Help-> Manual")

        if self.check_val(self.hair_spb_var.get(), 0, self.my_config.gui["hair_id_max"]):
            self.player.hair_id.set_value(self.hair_spb_var.get())
        else:
            messagebox.showerror(title=self.appname, message=f"Value for {self.player.hair_id.name} out of range, check Help-> Manual")

        try:
            if self.my_config.gui["pes2014_sh_2"]:
                self.player.sh_2.set_value(self.sh2_var.get())
        
                if self.check_val(self.face_spb_var.get(), 1, self.my_config.gui["face_id_max"]):
                    self.player.face_id.set_value(self.face_spb_var.get())
                else:
                    messagebox.showerror(title=self.appname, message=f"Value for {self.player.face_id.name} out of range, check Help-> Manual")
        except KeyError:
            if self.check_val(self.face_spb_var.get()-1, 0, self.my_config.gui["face_id_max"]):
                self.player.face_id.set_value(self.face_spb_var.get()-1)
            else:
                messagebox.showerror(title=self.appname, message=f"Value for {self.player.face_id.name} out of range, check Help-> Manual")

        # Here we set the values to memory
        try:
            if self.platform == 0:
                self.pm.write_bytes(self.client + self.player_edit_mode,bytes(self.player.data),self.player_bytes_size)
            else:
                self.pm.write_bytes(self.player_edit_mode,bytes(self.player.data),self.player_bytes_size)

        except pymem.exception.MemoryWriteError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
        except pymem.exception.ProcessError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
        except pymem.exception.TypeError as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")

    def check_val(self, val, min, max): 
        return min<=val<=max

    def start(self):
        self.resizable(False, False)
        self.mainloop()
