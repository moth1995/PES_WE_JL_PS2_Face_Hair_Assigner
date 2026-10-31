import pymem
import pymem.process
import pymem.exception
import psutil
import struct
import ctypes
from ctypes import wintypes
from editor import Player, Stat
from tkinter import Tk, messagebox, ttk, Button, Label, Menu, Spinbox, filedialog, IntVar
from pathlib import Path
from .config import Config
from pymem.ptypes import RemotePointer

class Gui(Tk):
    filename = ""
    appname='PES/WE/JL PS2 Face/Hair assigner'
    PCSX2_PROCESS_NAMES = {
        "pcsx2.exe",
        "pcsx2-qt.exe",
        "pcsx2-qt-avx2.exe",
        "pcsx2-avx2.exe",
        "pcsx2-sse4.exe",
    }
    PPSSPP_PROCESS_NAMES = {"ppssppwindows64.exe", "ppssppwindows.exe"}
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
            return
        self.apply_config()
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

    def apply_config(self):
        self.player_edit_mode = self.my_config.player_edit_mode
        self.platform = self.my_config.platform
        self.psp_pointer = self.my_config.psp_pointer
        self.psp_offset = self.my_config.psp_offset

    def refresh_gui(self):
        self.game_ver_lbl.config(text=f"Game version: {self.my_config.game_name}")
        self.face_type_dropdown.config(values=self.my_config.gui["face_type"])
        self.skin_spb.config(to=self.my_config.gui["skin_colour_max"])
        self.face_id_spb.config(to=self.my_config.gui["face_id_max"])
        self.hair_id_spb.config(to=self.my_config.gui["hair_id_max"])
        self.apply_config()

        try:
            if self.my_config.gui["pes2014_sh_2"]:
                self.sh2_cb.config(state='active')
        except KeyError:
            self.sh2_cb.config(state='disabled')

    def search_exe(self):
        self.filename = filedialog.askopenfilename(initialdir=".",title=self.appname, filetypes=([("PCSX2 Executable", ".exe"),]))
        if self.filename!="":
            if self.load_data():
                self.read_player()

    def get_by_process_name(self):
        if self.platform == 0:
            valid_processes = self.PCSX2_PROCESS_NAMES
        else:
            valid_processes = self.PPSSPP_PROCESS_NAMES

        for proc in psutil.process_iter(["name", "exe"]):
            try:
                process_name = proc.info["name"]
                if process_name and process_name.casefold() in valid_processes:
                    # Prefer the full executable path when psutil can provide it;
                    # otherwise its process name is still enough for pymem.
                    self.filename = proc.info["exe"] or process_name
                    if self.load_data():
                        self.read_player()
                    return
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

        emulator = "PCSX2" if self.platform == 0 else "PPSSPP"
        messagebox.showerror(
            title=self.appname,
            message=f"No compatible {emulator} process was found. Start the emulator and its game first.",
        )

    def show_help(self):
        messagebox.showinfo(title=self.appname,message=
        """
        Work in progress...
        """.replace('        ', ''))

    def show_thanks(self):
        messagebox.showinfo(title=self.appname,message="Developed by PES Indie")

    def check_version(self):
        executable_name = Path(self.filename).name.casefold()
        if executable_name in self.PCSX2_PROCESS_NAMES:
            """
            If we lay here it is pcsx2 emulator
            """
            return True
        elif executable_name in self.PPSSPP_PROCESS_NAMES:
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

    @staticmethod
    def get_export_rva(executable, export_name):
        """Return an exported PE symbol RVA without requiring an extra package.

        Modern 64-bit PCSX2 randomizes the location of its EE RAM but exports an
        ``EEmem`` pointer from its executable.  The RVA is constant for the
        running executable; adding it to the remote module base locates the
        exported pointer in the target process.
        """
        with open(executable, "rb") as file:
            image = file.read()

        pe_offset = struct.unpack_from("<I", image, 0x3C)[0]
        if image[pe_offset:pe_offset + 4] != b"PE\0\0":
            raise ValueError("not a PE executable")

        section_count = struct.unpack_from("<H", image, pe_offset + 6)[0]
        optional_offset = pe_offset + 24
        optional_magic = struct.unpack_from("<H", image, optional_offset)[0]
        if optional_magic == 0x10B:
            data_directory_offset = optional_offset + 96
            pointer_size = 4
        elif optional_magic == 0x20B:
            data_directory_offset = optional_offset + 112
            pointer_size = 8
        else:
            raise ValueError("unsupported PE optional header")

        export_rva = struct.unpack_from("<I", image, data_directory_offset)[0]
        if not export_rva:
            raise ValueError("executable has no exports")

        section_offset = optional_offset + struct.unpack_from("<H", image, pe_offset + 20)[0]
        sections = []
        for index in range(section_count):
            offset = section_offset + index * 40
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", image, offset + 8)
            sections.append((virtual_address, max(virtual_size, raw_size), raw_offset))

        def rva_to_offset(rva):
            for virtual_address, size, raw_offset in sections:
                if virtual_address <= rva < virtual_address + size:
                    return raw_offset + rva - virtual_address
            # Headers are stored at their RVA too.
            if rva < len(image):
                return rva
            raise ValueError("RVA outside executable")

        export_offset = rva_to_offset(export_rva)
        name_count = struct.unpack_from("<I", image, export_offset + 24)[0]
        functions_rva = struct.unpack_from("<I", image, export_offset + 28)[0]
        names_rva = struct.unpack_from("<I", image, export_offset + 32)[0]
        ordinals_rva = struct.unpack_from("<I", image, export_offset + 36)[0]
        for index in range(name_count):
            name_rva = struct.unpack_from("<I", image, rva_to_offset(names_rva) + index * 4)[0]
            name_offset = rva_to_offset(name_rva)
            end = image.index(b"\0", name_offset)
            if image[name_offset:end].decode("ascii") == export_name:
                ordinal = struct.unpack_from("<H", image, rva_to_offset(ordinals_rva) + index * 2)[0]
                return struct.unpack_from("<I", image, rva_to_offset(functions_rva) + ordinal * 4)[0], pointer_size
        raise ValueError(f"export {export_name} not found")

    def get_pcsx2_player_address(self):
        """Resolve the configured PS2 address in PCSX2's current EE RAM mapping."""
        # PS2 physical RAM is mirrored at 0x20000000 in the older configuration
        # files.  Only its lower 29 bits are an offset inside the 32 MiB EE RAM.
        guest_offset = self.my_config.player_edit_mode & 0x1FFFFFFF
        try:
            export_rva, pointer_size = self.get_export_rva(self.filename, "EEmem")
            ee_memory_base = int.from_bytes(
                self.pm.read_bytes(self.client + export_rva, pointer_size),
                byteorder="little",
            )
            if ee_memory_base:
                return ee_memory_base + guest_offset
        except (OSError, ValueError, struct.error, pymem.exception.MemoryReadError):
            # PCSX2 <= 1.6 used the fixed mapping. Keep it for compatibility.
            pass
        return self.my_config.player_edit_mode

    def get_ppsspp_memory_base(self):
        """Return PPSSPP's current emulated PSP memory base (PPSSPP 1.15+)."""
        # PPSSPP documents WM_APP + 0x3118 as the supported way to retrieve
        # this dynamic address.  The low and high 32-bit halves are returned
        # separately, so it also works with a 64-bit PPSSPP process.
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.FindWindowW.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR)
        user32.FindWindowW.restype = wintypes.HWND
        user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
        user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        user32.SendMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        user32.SendMessageW.restype = wintypes.LPARAM
        window = user32.FindWindowW("PPSSPPWnd", None)
        if not window:
            raise OSError("PPSSPP main window was not found")

        process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(window, ctypes.byref(process_id))
        if process_id.value != self.pm.process_id:
            raise OSError("the PPSSPP window does not belong to the selected process")

        message = 0xB118  # WM_APP + 0x3118
        lower = user32.SendMessageW(window, message, 0, 0) & 0xFFFFFFFF
        upper = user32.SendMessageW(window, message, 0, 1) & 0xFFFFFFFF
        memory_base = lower | (upper << 32)
        if not memory_base:
            raise OSError("PPSSPP has not initialized PSP memory; start the game first")
        return memory_base

    def get_ppsspp_player_address(self):
        if len(self.psp_offset) != 1:
            raise ValueError("this PPSSPP configuration requires one PSP address")
        return self.get_ppsspp_memory_base() + self.psp_offset[0]

    def load_data(self):
        if self.check_version()==0:
            return 0
        self.pes_we_exe = Path(self.filename).name
        self.player_bytes_size = 124
        try:
            self.pm = pymem.Pymem(self.pes_we_exe)
            if self.platform == 0:
                self.client = pymem.process.module_from_name(self.pm.process_handle, self.pes_we_exe).lpBaseOfDll
                self.player_edit_mode = self.get_pcsx2_player_address()
            else:
                self.player_edit_mode = self.get_ppsspp_player_address()
            return True

        except pymem.exception.ProcessNotFound as e:
            messagebox.showerror(title=self.appname, message=f"pymem error code {e}")
            return 0
        except (OSError, ValueError) as e:
            messagebox.showerror(title=self.appname, message=f"Could not locate emulator memory: {e}")
            return 0

    def read_player(self):
        if self.filename=="":
            messagebox.showerror(title=self.appname, message="You must select your exe file first or run your game\nbefore trying to read or set any data")
            return 0
        try:
            if self.platform == 0:
                self.player = Player(bytearray(self.pm.read_bytes(self.player_edit_mode, self.player_bytes_size)), self.my_config)
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
                self.pm.write_bytes(self.player_edit_mode,bytes(self.player.data),self.player_bytes_size)
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
