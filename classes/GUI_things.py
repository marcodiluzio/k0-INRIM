# -*- coding: utf-8 -*-

"""
Stores images data to be recalled as icons and modified tkinter Widgets Classes
"""

import tkinter
from tkinter import ttk
import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Button(tkinter.Button):
    """Modified version of a tkinter Button allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Button.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())

class Label(tkinter.Label):
    """Modified version of a tkinter Label allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Label.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())

class Entry(tkinter.Entry):
    """Modified version of a tkinter Entry allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Entry.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())

class Spinbox(tkinter.Spinbox):
    """Modified version of a tkinter Spinbox allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Spinbox.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())


class Checkbutton(tkinter.Checkbutton):
    """Modified version of a tkinter Checkbutton allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        tkinter.Checkbutton.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())


class Combobox(ttk.Combobox):
    """Modified version of a tkinter ttk.Combobox allowing to popup an hint while the widget is hovered with mouse."""
    def __init__(self, master, hint='', hint_xoffset=0, hint_destination=None, **kw):
        ttk.Combobox.__init__(self, master, **kw)
        if hint!='':
            self.hint_destination = hint_destination
            self.hint = str(hint)
            try:
                self.hint_xoffset = int(hint_xoffset)
            except ValueError:
                self.hint_xoffset = 0
            self.bind('<Enter>', lambda e='<Enter>' : self._showhint())

    def _showhint(self):
        if self.hint_destination is not None:
            self.hint_destination.configure(text=self.hint)
            self.bind('<Leave>', lambda e='<Leave>' : self.hint_destination.configure(text=''))
        else:
            if self.hint_xoffset > self.winfo_width():
                self.hint_xoffset = 0
            M = tkinter.Toplevel(self)
            M.overrideredirect(True)
            tkinter.Label(M, text=self.hint).pack()
            M.geometry(f'+{self.winfo_rootx()+self.hint_xoffset}+{self.winfo_rooty()+self.winfo_height()}')
            self.bind('<Leave>', lambda e='<Leave>' : M.destroy())

class Slider(tkinter.Frame):
    def __init__(self, master, percent=False, label_width=4, anchor_text=tkinter.CENTER, default=0, hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.IntVar(master)
        self.percent = percent
        if self.percent == True:
            self.text = f'{self.variable.get():d} %'
        else:
            self.text = f'{self.variable.get():d}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        self.from_ = kwargs.get('from_',1)
        self.to = kwargs.get('to',10)
        self.resolution = kwargs.get('resolution',1)
        self.anchor = anchor_text
        self.Label = Label(self, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, resolution=self.resolution, showvalue=False, variable=self.variable)
        self.Scale.pack(side=tkinter.RIGHT)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()

        self.variable.trace('w', lambda a,b,c : self._update())

    def _update(self):
        if self.percent == True:
            self.text = f'{self.variable.get():d} %'
        else:
            self.text = f'{self.variable.get():d}'
        self.Label.configure(text=self.text)

    def get(self):
        return self.variable.get()

class TSlider(tkinter.Frame):
    def __init__(self, master, label_width=4, anchor_text=tkinter.CENTER, default=0, hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.BooleanVar(master)
        self.text = f'{self.variable.get()}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        self.resolution = kwargs.get('resolution',1)
        self.anchor = anchor_text
        self.Label = Label(self, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=0, to=1, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, resolution=self.resolution, showvalue=False, variable=self.variable)
        self.Scale.pack(side=tkinter.RIGHT)

        if 0 <= default <= 1:
            self.variable.set(default)
        else:
            self.variable.set(True)
        self._update()

        self.variable.trace('w', lambda a,b,c : self._update())

    def _update(self):
        self.text = f'{self.variable.get()}'
        self.Label.configure(text=self.text)

    def get(self,asint=True):
        if asint == False:
            return self.variable.get()
        else:
            return int(self.variable.get())

class FSlider(tkinter.Frame):
    def __init__(self, master, percent=False, decimals=2, label_width=4, anchor_text=tkinter.CENTER, default=0, hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.DoubleVar(master)
        self.decimals = decimals
        fmt = f'.{self.decimals}f'
        self.percent = percent
        if self.percent == True:
            self.text = f'{format(self.variable.get(),fmt)} %'
        else:
            self.text = f'{format(self.variable.get(),fmt)}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        self.from_ = kwargs.get('from_',1)
        self.to = kwargs.get('to',10)
        self.resolution = kwargs.get('resolution',0.1)
        self.anchor = anchor_text
        self.Label = Label(self, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, resolution=self.resolution, showvalue=False, variable=self.variable)
        self.Scale.pack(side=tkinter.RIGHT, fill=tkinter.X, expand=True)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()

        self.variable.trace('w', lambda a,b,c : self._update())

    def _update(self):
        fmt = f'.{self.decimals}f'
        if self.percent == True:
            self.text = f'{format(self.variable.get(),fmt)} %'
        else:
            self.text = f'{format(self.variable.get(),fmt)}'
        self.Label.configure(text=self.text)

    def get(self):
        return self.variable.get()

class FDiscreteSlider(tkinter.Frame):
    def __init__(self, master, decimals=1, label_width=8, anchor_text=tkinter.CENTER, default=0, values=[], hint='', hint_destination=None, hint_xoffset=0, unit_format=' mm', **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.DoubleVar(master)
        self.decimals = decimals
        fmt = f'.{self.decimals}f'
        self.unit_format = unit_format
        self.text = f'{format(self.variable.get(),fmt)}{self.unit_format}'
        self.width = label_width
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        if values == []:
            values = [default]
        else:
            values = sorted(set(values))
        self.values = values
        self.from_ = min(values)# kwargs.get('from_',1)
        self.to = max(values)#kwargs.get('to',10)
        self.resolution = kwargs.get('resolution',0.1)
        self.anchor = anchor_text
        self.Label = Label(self, text=self.text, width=self.width, anchor=self.anchor, hint=hint, hint_xoffset=hint_xoffset, hint_destination=hint_destination)
        self.Label.pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, showvalue=False, variable=self.variable, resolution=self.resolution)
        self.Scale.configure(command=lambda e=None: self.change_value())
        self.Scale.pack(side=tkinter.RIGHT, fill=tkinter.X, expand=True)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()

        self.variable.trace('w', lambda a,b,c : self._update())

    def change_value(self):
        newvalue = min(self.values, key=lambda x:abs(x-float(self.Scale.get())))
        self.variable.set(newvalue)

    def _update(self):
        fmt = f'.{self.decimals}f'
        self.text = f'{format(self.variable.get(),fmt)}{self.unit_format}'
        self.Label.configure(text=self.text)

    def get(self):
        newvalue = min(self.values, key=lambda x:abs(x-float(self.Scale.get())))
        return newvalue

    def set_values(self, values, default=0):
        if values == []:
            values = [default]
        else:
            values = sorted(set(values))
        self.values = values
        self.from_ = min(values)# kwargs.get('from_',1)
        self.to = max(values)#kwargs.get('to',10)
        self.Scale.configure(from_=self.from_, to=self.to)
        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)
        self._update()


class IZoomSlider(tkinter.Frame):
    def __init__(self, master, default=0, values=[], hint='', hint_destination=None, hint_xoffset=0, **kwargs):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.IntVar(master)
        self.width_scale = kwargs.get('width',10)
        self.lenght = kwargs.get('length',150)
        if values == []:
            values = [default]
        else:
            values = sorted(set(values))
        self.values = values
        self.from_ = min(values)
        self.to = max(values)
        self.resolution = kwargs.get('resolution',1)
        Label(self, text='zoom\n+').pack(side=tkinter.LEFT)
        self.Scale = tkinter.Scale(self, from_=self.from_, to=self.to, width=self.width_scale, orient=tkinter.HORIZONTAL, length=self.lenght, showvalue=False, variable=self.variable)
        self.Scale.configure(command=lambda e=None: self.change_value())
        self.Scale.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)
        Label(self, text='zoom\n-').pack(side=tkinter.LEFT)

        if self.from_ <= default <= self.to:
            self.variable.set(default)
        else:
            self.variable.set(self.from_)

    def change_value(self):
        newvalue = min(self.values, key=lambda x:abs(x-int(self.Scale.get())))
        self.variable.set(newvalue)

    def get(self):
        newvalue = min(self.values, key=lambda x:abs(x-int(self.Scale.get())))
        return newvalue


class ScrollableListbox(tkinter.Frame):
    """A simple yet effective scrollable listbox"""
    def __init__(self,master,width=10, height=8, data=[], **kwargs):
        tkinter.Frame.__init__(self, master)
        self.listbox = tkinter.Listbox(self, width=width, height=height)
        self.scrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=tkinter.LEFT, anchor=tkinter.NW, fill=tkinter.BOTH, expand=True)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._update(data)

    def _update(self,data=[]):
        self.listbox.delete(0,tkinter.END)
        for item in data:
            self.listbox.insert(tkinter.END, item)

    def curselection(self):
        return self.listbox.curselection()


class PeriodicTable(tkinter.Frame):
    """A periodic table"""
    def __init__(self, master, possible_entries=None, already_selected=None, ptype='check', label=None):
        tkinter.Frame.__init__(self, master)
        #(Z, symbol, row, column, name)
        self.possible_entries = possible_entries
        self.global_variable = already_selected
        self.periodic_data = (
            (1,'H',0,0,'Hydrogen'),
            (2,'He',0,17,'Helium'),
            (3,'Li',1,0,'Lithium'),
            (4,'Be',1,1,'Beryllium'),
            (5,'B',1,12,'Boron'),
            (6,'C',1,13,'Carbon'),
            (7,'N',1,14,'Nitrogen'),
            (8,'O',1,15,'Oxygen'),
            (9,'F',1,16,'Fluorine'),
            (10,'Ne',1,17,'Neon'),
            (11,'Na',2,0,'Sodium'),
            (12,'Mg',2,1,'Magnesium'),
            (13,'Al',2,12,'Aluminium'),
            (14,'Si',2,13,'Silicon'),
            (15,'P',2,14,'Phosphorus'),
            (16,'S',2,15,'Sulfur'),
            (17,'Cl',2,16,'Chlorine'),
            (18,'Ar',2,17,'Argon'),
            (19,'K',3,0,'Potassium'),
            (20,'Ca',3,1,'Calcium'),
            (21,'Sc',3,2,'Scandium'),
            (22,'Ti',3,3,'Titanium'),
            (23,'V',3,4,'Vanadium'),
            (24,'Cr',3,5,'Chromium'),
            (25,'Mn',3,6,'Manganese'),
            (26,'Fe',3,7,'Iron'),
            (27,'Co',3,8,'Cobalt'),
            (28,'Ni',3,9,'Nickel'),
            (29,'Cu',3,10,'Copper'),
            (30,'Zn',3,11,'Zinc'),
            (31,'Ga',3,12,'Gallium'),
            (32,'Ge',3,13,'Germanium'),
            (33,'As',3,14,'Arsenic'),
            (34,'Se',3,15,'Selenium'),
            (35,'Br',3,16,'Bromine'),
            (36,'Kr',3,17,'Krypton'),
            (37,'Rb',4,0,'Rubidium'),
            (38,'Sr',4,1,'Strontium'),
            (39,'Y',4,2,'Yttrium'),
            (40,'Zr',4,3,'Zirconium'),
            (41,'Nb',4,4,'Niobium'),
            (42,'Mo',4,5,'Molybdenum'),
            (43,'Tc',4,6,'Technetium'),
            (44,'Ru',4,7,'Ruthenium'),
            (45,'Rh',4,8,'Rhodium'),
            (46,'Pd',4,9,'Palladium'),
            (47,'Ag',4,10,'Silver'),
            (48,'Cd',4,11,'Cadmium'),
            (49,'In',4,12,'Indium'),
            (50,'Sn',4,13,'Tin'),
            (51,'Sb',4,14,'Antimony'),
            (52,'Te',4,15,'Tellurium'),
            (53,'I',4,16,'Iodine'),
            (54,'Xe',4,17,'Xenon'),
            (55,'Cs',5,0,'Caesium'),
            (56,'Ba',5,1,'Barium'),
            (72,'Hf',5,3,'Hafnium'),
            (73,'Ta',5,4,'Tantalum'),
            (74,'W',5,5,'Tungsten'),
            (75,'Re',5,6,'Rhenium'),
            (76,'Os',5,7,'Osmium'),
            (77,'Ir',5,8,'Iridium'),
            (78,'Pt',5,9,'Platinum'),
            (79,'Au',5,10,'Gold'),
            (80,'Hg',5,11,'Mercury'),
            (81,'Tl',5,12,'Thallium'),
            (82,'Pb',5,13,'Lead'),
            (83,'Bi',5,14,'Bismuth'),
            (84,'Po',5,15,'Polonium'),
            (85,'At',5,16,'Astatine'),
            (86,'Rn',5,17,'Radon'),
            (87,'Fr',6,0,'Francium'),
            (88,'Ra',6,1,'Radium'),
            (104,'Rf',6,3,'Rutherfordium'),
            (105,'Db',6,4,'Dubnium'),
            (106,'Sg',6,5,'Seaborgium'),
            (107,'Bh',6,6,'Bohrium'),
            (108,'Hs',6,7,'Hassium'),
            (109,'Mt',6,8,'Meitnerium'),
            (110,'Ds',6,9,'Darmstadtium'),
            (111,'Rg',6,10,'Roentgenium'),
            (112,'Cn',6,11,'Copernicium'),
            (113,'Nh',6,12,'Nihonium'),
            (114,'Fl',6,13,'Flerovium'),
            (115,'Mc',6,14,'Moscovium'),
            (116,'Lv',6,15,'Livermorium'),
            (117,'Ts',6,16,'Tennessine'),
            (118,'Og',6,17,'Oganesson'),
            (57,'La',8,2,'Lanthanum'),
            (58,'Ce',8,3,'Cerium'),
            (59,'Pr',8,4,'Praseodymium'),
            (60,'Nd',8,5,'Neodymium'),
            (61,'Pm',8,6,'Promethium'),
            (62,'Sm',8,7,'Samarium'),
            (63,'Eu',8,8,'Europium'),
            (64,'Gd',8,9,'Gadolinium'),
            (65,'Tb',8,10,'Terbium'),
            (66,'Dy',8,11,'Dysprosium'),
            (67,'Ho',8,12,'Holmium'),
            (68,'Er',8,13,'Erbium'),
            (69,'Tm',8,14,'Thulium'),
            (70,'Yb',8,15,'Ytterbium'),
            (61,'Lu',8,16,'Lutetium'),
            (89,'Ac',9,2,'Actinium'),
            (90,'Th',9,3,'Thorium'),
            (91,'Pa',9,4,'Protoactinium'),
            (92,'U',9,5,'Uranium'),
            (93,'Np',9,6,'Neptunium'),
            (94,'Pu',9,7,'Plutonium'),
            (95,'Am',9,8,'Americium'),
            (96,'Cm',9,9,'Curium'),
            (97,'Bk',9,10,'Berkelium'),
            (98,'Cf',9,11,'Californium'),
            (99,'Es',9,12,'Einsteinium'),
            (100,'Fm',9,13,'Fermium'),
            (101,'Md',9,14,'Mendelevium'),
            (102,'No',9,15,'Nobelium'),
            (103,'Lr',9,16,'Lawrencium')
        )
        if self.possible_entries is None:
            self.possible_entries = []
        if self.global_variable is None:
            self.global_variable = []
        if ptype == 'check':
            self.place_check(label)
        elif ptype == 'button':
            self.place_button()

    def _select(self, cb, el_on, label=None):
        if cb.get() != '':
            self.global_variable.append(cb.get())
        else:
            self.global_variable.remove(el_on)
        if label is not None:
            label.configure(text=f'{len(self.global_variable)}')

    def place_check(self, label=None):
        tkinter.Frame(self).grid(row=7, column=0, pady=4)
        element_indicator = tkinter.Label(self, text='')
        element_indicator.grid(row=10, column=0, pady=3, columnspan=10, sticky=tkinter.W)
        for element in self.periodic_data:
            el_variable = tkinter.StringVar(self)
            CB = Checkbutton(self, text=element[1], variable=el_variable, state=tkinter.DISABLED, width=3, anchor=tkinter.W, offvalue='', onvalue=element[1], relief='solid', hint=element[4], hint_destination=element_indicator)
            CB.grid(row=element[2], column=element[3], ipadx=2, ipady=2, sticky=tkinter.W)
            CB.configure(command=lambda cb=el_variable, el_on=element[1]: self._select(cb, el_on, label))
            if element[1] in self.possible_entries:
                CB.configure(state=tkinter.NORMAL)
                CB.deselect()
                if element[1] in self.global_variable:
                    CB.select()

    def _set_command(self, el):
        EL = tkinter.Toplevel(self)
        EL.title(el)
        EL.resizable(False, False)
        local_variable = [item for item in self.global_variable if item[0] == el]
        iframe = tkinter.Frame(EL)
        uframe = tkinter.Frame(EL)

        tkinter.Label(iframe, text=f'{"emitter".ljust(20)}{"w / g g-1".ljust(11)}{"urw / %".ljust(9)}{"DL / g g-1".ljust(12)}{"z / 1".ljust(6)}', anchor=tkinter.W, font=('Courier', 11)).pack(anchor=tkinter.W)

        listframe = tkinter.Frame(iframe)
        scrollbar = tkinter.Scrollbar(listframe, orient="vertical")
        listbox = tkinter.Listbox(listframe, width=60, relief='flat', bg='#d9d9d9', font=('Courier', 11), heigh=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        listbox.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        listbox.delete(0, tkinter.END)
        for item in local_variable:
            listbox.insert(tkinter.END, f'{item[1].ljust(20)}{format(item[2][0],".2e").ljust(11)}{format(item[2][1]/item[2][0]*100,".1f").ljust(9)}{format(item[2][2],".1e").ljust(12)}{format(item[2][3],".1f").ljust(6)}')

        listframe.pack(anchor=tkinter.NW)
        bframe = tkinter.Frame(iframe)
        logo_graph = tkinter.PhotoImage(data=graph)
        B_general_view = Button(bframe, image=logo_graph)
        B_general_view.pack(side=tkinter.LEFT)
        B_general_view.image = logo_graph
        logo_pie = tkinter.PhotoImage(data=pie)
        B_pie_view = Button(bframe, image=logo_pie)
        B_pie_view.pack(side=tkinter.LEFT)
        B_pie_view.image = logo_pie
        bframe.pack(anchor=tkinter.W)

        f = Figure(figsize=(4.5, 4.5))
        ax_maj_contributions = f.add_subplot(111)
        Figur = tkinter.Frame(uframe)
        Figur.pack(anchor=tkinter.CENTER, fill=tkinter.BOTH, expand=True)
        canvas = FigureCanvasTkAgg(f, master=Figur)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        ydata, uydata = np.array([line[2][0] for line in local_variable]), np.array([line[2][1] for line in local_variable])
        ax_maj_contributions.errorbar(np.arange(1, len(ydata)+1), ydata, yerr=[uydata*2, uydata*2], linestyle='', marker='o', markerfacecolor='r', markersize=4, color='k', markeredgewidth=0.5, elinewidth=0.7)
        ax_maj_contributions.set_ylabel(r'$w$ / g g$^{-1}$ $(k=2)$')
        ax_maj_contributions.set_xticks(np.arange(1, len(ydata)+1))
        ax_maj_contributions.set_xlim(0.7, len(ydata)+0.3)
        ax_maj_contributions.grid(which='major', axis='y', linestyle='-.', linewidth=0.3)
        f.tight_layout(pad=1.03, rect=(0,0,1,1))
        canvas.draw()

        iframe.pack(side=tkinter.LEFT, anchor=tkinter.NW, fill=tkinter.Y, padx=5, pady=5, expand=True)
        uframe.pack(side=tkinter.LEFT, padx=5, pady=5)

        B_general_view.configure(command=lambda : self.command_graph(f, canvas, local_variable))
        B_pie_view.configure(command=lambda : self.command_pie(listbox, f, canvas, local_variable))
    
    def command_graph(self, f, canvas, local_variable):
        #clear axes
        f.clear()
        ax_maj_contributions = f.add_subplot(111)
        ydata, uydata = np.array([line[2][0] for line in local_variable]), np.array([line[2][1] for line in local_variable])
        ax_maj_contributions.errorbar(np.arange(1, len(ydata)+1), ydata, yerr=[uydata*2, uydata*2], linestyle='', marker='o', markerfacecolor='r', markersize=4, color='k', markeredgewidth=0.5, elinewidth=0.7)
        ax_maj_contributions.set_ylabel(r'$w$ / g g$^{-1}$ $(k=2)$')
        ax_maj_contributions.set_xticks(np.arange(1, len(ydata)+1))
        ax_maj_contributions.set_xlim(0.7, len(ydata)+0.3)
        ax_maj_contributions.grid(which='major', axis='y', linestyle='-.', linewidth=0.3)
        f.tight_layout(pad=1.03, rect=(0,0,1,1))
        canvas.draw()

    def command_pie(self, listbox, f, canvas, local_variable):
        idx = listbox.curselection()
        try:
            idx = idx[0]
        except:
            idx = -1
        if idx > -1:
            try:
                #clear axes
                f.clear()
                ax_maj_contributions = f.add_subplot(111)

                gdata = local_variable[idx][2]
                if gdata is not None:
                    x, label = [item[0] for item in gdata[4]], [item[1] for item in gdata[4]]
                    ax_maj_contributions.pie(x, labels=label, colors=['red', 'darkorange', 'gold', 'yellowgreen', 'palegreen'], autopct='%1.1f%%')
                    ax_maj_contributions.set_title(r'contributors to $u_\mathrm{c}^2$ for '+local_variable[idx][1])
                else:
                    ax_maj_contributions.pie(np.array([0]), labels=['None'])
                f.tight_layout(pad=1.03, rect=(0,0,1,1))
                canvas.draw()
            except ValueError:
                pass

    def place_button(self):
        tkinter.Frame(self).grid(row=7, column=0, pady=4)
        element_indicator = tkinter.Label(self, text='', anchor=tkinter.W)
        element_indicator.grid(row=10, column=0, pady=3, columnspan=10, sticky=tkinter.W)
        for element in self.periodic_data:
            CB = Button(self, text=element[1], state=tkinter.DISABLED, width=3, anchor=tkinter.W, relief='solid', hint=element[4], hint_destination=element_indicator)
            CB.grid(row=element[2], column=element[3], ipadx=2, ipady=2, sticky=tkinter.W)
            CB.configure(command= lambda el=element[1]: self._set_command(el))
            if element[1] in self.possible_entries:
                CB.configure(state=tkinter.NORMAL, bg='pale green')
                

    def get(self):
        return self.global_variable


class ScrollableText(tkinter.Frame):
    """A simple yet effective scrollable text"""
    def __init__(self,master, wrap=tkinter.WORD, state='disabled', width=30, height=8, data='', **kwargs):
        tkinter.Frame.__init__(self, master)
        self.text = tkinter.Text(self, width=width, height=height, state=state, wrap=wrap, **kwargs)
        self.scrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        self.text.pack(side=tkinter.LEFT, anchor=tkinter.NW, fill=tkinter.BOTH, expand=True)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._update(data)

    def _update(self,data=''):
        original_state = self.text.cget('state')
        self.text.configure(state='normal')
        self.text.delete('0.0',tkinter.END)
        self.text.insert(tkinter.END, data)
        self.text.configure(state=original_state)

    def get(self):
        return self.text.get('0.0',tkinter.END)


none = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHGSURBVFiF7dfNahNRGAbgZ5KloAtBiwpmUS3Vnb2BNv5Af9Rr6MK78iZqUwNW0tyEin/QgkpbcOHC5cy4mATKMDM5MxMQJe8yM/nycL7zZc6wyCL/YwasDVidc83VAWtl1ztFH+7zAIcYzQs0qTPC4aR+GKbDT/zCUsr4FffbQIas4C2W8Lub1Q7DbHMSsY7jiGsRo6agIStxtiI38C1mY4uvRfdGVYUOuJ0yRi/lPKX/jHdtIM/5UnZ/JWZSsBdzVBd0wN00+14QJAiTB+Es4WEVqAkkGFME6tDf4v28IJRs4KJschzzGN9xPWH0mnsVkFM8CYVQY2Wm2edOlP3gTRdWqADS3+FDndq1MSWg3YSXbSCNMQWgRNbyxhBq7Jl8nvI5ZhfxpE4S8aIphDmtTJpBOiqmLCSNVia/Z7rsuDBlTR+utTEl0zRM2ZiCNATValPZWOeujzWcqmDMLMg0bf5vgtq0x3IIBLb5FGUt+yE7vwS3bCZmSK+bnfpmQipAb/ZYboUpelqHjm0OdKvL0SxQ6Z5peo7Jp85TvBDT9oSXT+iJr7BNCVdxBacR620gsMlHPJJN16UOl2sV+BvvTYss8k/nD2pR1ed9VbnbAAAAAElFTkSuQmCC'

ggear = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAW/SURBVFiF1VhfTFpnFD8XQdCKosEriroLPlAkRgv3DtslXTFVLHVpTNpmWeJM13Wv7ZZmD8uWJXvqXvq016Zb+2Zi6mJjK8522o7BLhPU3CKjlQsqMsByuQqWtuJe1DG4CKPdsv0ez98f557zne8D4D8E5FWc5XL5YalUqhOLxRUsy7JPnz79dXl52favk+np6bl58uTJozKZbE8WCARgfHx86u7du+8XE5NXLJmmpiY0nQgAQENDA8jl8rpiY+YjU9Le3n4Ox/HuYhMAAOj1+p6Ojo4PAYC/b7JcCoVC8cbx48dvDA4Ovoui6NsbGxuBQCDgbm5uVmq12o/VanVHXV1deaZfPB5HeDxeA4IgNMMwDI7jp06cOHHFZDIZ+Xz+sc3NTQvDMDGunJw9g2EY1tXVddNoNDbvyiiKipEk6SAIQq/RaMr2+4U79gmSJG0EQWg1Gk3VrtxsNvvu3bs34PV6fYWQ4Z85c2bk9OnTbfkSFouhoaHZ4eHhfgDYSpdnfSadTvfBwMDAWT5/38/7SlAqlTK/3x9dXV11psuzGhhBEN+TJ0+Yf4wJANA0HSspKVnKlGdVJhAILLIsS1dXV7+Fomje3vi7WFhYiN2+ffsLu91+J1PHOdoOh+MOSZJOLl0mkskkEg6HS168eFHQAWq1Wh12u/17Lh1nY2AYhhEEod8vKEVRLEmSP/p8Ptv6+rpfLBY3KxQKPY7jx1pbWytz+REE8abL5cJomqYzdZznzKFDhz4xmUxEroCTk5P06OjoRzab7Xo4HJ5jWdYXDofnPB7PnVAoZEulUocVCoWEyxdFUYHH40F8Pt+Pmbq9ynR3d99EURQFAGhsbKzNRWR+fp59+PDhJY/Hw/kZXS7XDABckslk3+WqUGdnZ19jY2MnAEAoFApNTEwM7JHBMKyzr6/vaOau4YLD4bj/6NEjx342LpdrhiTJqdbW1ne49FqtVqrVaqUAAMFg8KDH4+mkadrKAwCoqanBCyGSTCYRr9db0BXB6/Xakslk3qaWyWRQU1ODA+xMU1lZmaiQBOvr67xIJLJYiG0sFlvc2Ngo6FYgEomEe2QSiUSyECexWJySSqUthdhWVVUpKyoqUoXYJhKJZ3tkotEoGQwG8zoJhcJtDMM6C0mgUCj0QqFwO59dIBCASCRiB9gZbYZhVra2trTLy8ubbrc7Eo/Hob6+Put6sEOofnV1lVxbWwvkSqBSqfDe3t6LtbW1Qi79zMzMGkmSfrfbHXE6nZTT6fwG4M/R3t4dLwAAg8HwlVarHeQKpFarKw0Gw1Uej/epy+WychExGAxX1Wp1zoPParWOTk1NfZkp5zz0UqmUTy6Xn0VRVMClVygUkvr6+t4DBw60CYXChvLychTDMKNOpztnNBovEgSB5iJCUVRienr6MsMwWcuYcx34/f5FkiR/0Wg0x3IFValUYpVKZUqlUqZEIsErtFlJkrRxrQKAHJVpa2s7ZTAY3qurq8s78giCQGlpad5G3YVIJKrZvcLmJYPjeHd/f/+V9Kvi64RUKhVJJJIjLMv+FgwGvem6rENpa2urCcMwziX3uqBUKiUIgjRnyrMqEwwG5/l8vkGj0RT9/smHkZGRucnJyc8A4C99xtUzqUQiYdne3u5qaWnZqxBFUbGxsbGfBQKBLNeUpYOiqMTY2NhPAoGgGkXRvd4zm80+i8VygWGYaKYPZwMzDMNEo9H7DMPoWlpaZG63OzY6Ovr5gwcPvvZ6vWOPHz8GoVDYxPVumpubiwwPDw9NT09fttvt38bj8YBEIjlSWVlZduvWrTmLxXKB65kCkP+tzW9vbx8oLS1dIknyh3TF+fPnx3t6eg5mOpjN5oVr164Z02V6vb77+fPnTQ6H4wYAvMyZLA+Zl7Ozs9fz2OSFzWabKMSu6If/0tJSKHO5BoNBWFlZ+b3YmK/j/xm8srJSxLLss1gsRtI0nbWv/pf4Az3SWHosWS4GAAAAAElFTkSuQmCC'

resulti = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAE1SURBVFiF7ZgxS8NAGEBfjkswtMVBUBG0g2M3iy4OToI4dXB26Obi4j/xd+gqOIrFQRycRFCRChYRBCENgSa9OInTxTvhJMO9+eXL4+4I4aBGBH94pgEsGXgjILUZLG1LmvPtnfbG3rGMYqVzikkmhtcnh+P34anTGEoRNOdWVBi3tDF5lkAprFddWMc4xMfo8DE6fIyOWsXYf/TsmTFwCqBwHTPb248uO93q1wzO85uLs7zvfGXWNqXc2g0bVc7j3VRBHc/MOhwsQKdK/AQxgCPnMcvQ7cN2lXgF6QAilzG12iYfo8PH6PAxOnyMDh+jw8foqFWMBEghfPglbPT9vxyocvzxImQUa91ikgkCVQK8Pit5fzutnJ0mZQg/9zOLQMsg/gmIMb+fyYBVAzcB3gy8/+MLuRpEoHbGzhYAAAAASUVORK5CYII='

magnif = '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'

magnifpeak = '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'

arrow_upplates = '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'

arrow_up = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAL8SURBVFiF3ZbPaxNREMdnd99LN0nNtjFtQ9tEabVosQipv6oVq/YiCCpFPXjToyBWDx6LB3+ACB78AzyJVBBBQfEiiChYKa2WYotSjGBqSVtofu/um/FQjSXtrnYTF3Hge9nZ+eaTmTcvAfgPY2slTJRyDThAp9fPgkTYhgifyvGSyylWAdY3rlW1kWudQx0tNdNexrrL8SunM8Fw0Lv78ZXYW0OR2dGuuvSLsWRkPmt4hICkE0OnneENQfXYw4H2IUMvqOyH7p7f9CFao8YAIOTEVHJS0xBUTw/2t7/SfEyUJg0Tpb4bY/viyfwdANBXY7zqMYUCnlPXT0YmozVVgkxkRkFwYWBRJIjt76j99nx84VA6Zw7/NZhGTe090xM2u1vXZISJXJjICYn9EmOEEvMpitzS4M2Ofk51pPJiouIwIR+PHYmF1p3orJsFlNlPMZSZXBQV1RzwIFdAm5oxtZRufqkYTL1W1XqgLbD37J5wQhbElgpstLneV0hmjI2JtJnKFsRc2TC1AFrXhkDfpZ7wV0Bki5IYIP2RdkT8mcmZ7K4ZPT9RKEDO7rN+t018Z9R/8ebh6JSjb7IkLjyKR15/ydwCANMRzPbm6nNXe5vSXo+0bIVXG7pOSv/TuG90Ond71TBBr3J8W5O/PcClfOnduKXOL/W2Vs9b1b6Mp7WR6Zyn9PlsTq8eTmTfzObEg5XqmJXhXE7cf/ZxYcUcl6TLB6Ney/m/T2T998bnBqzyVmEJYxcciYEuVKu8jMSd+DqCkQgY6mgJo5AzX0dFMhEHEyxhwM3OKAQMDSwefixZBIWc/TVxBANIXOhi2bYALO6dTESuwTAEBubKo0AAkNH6Yqs4DAhiZHOAZaK8azAyIrfbJslE9zojIzAyyBoGoeAaDCAyMm3GhJhxDUZC4HZnBtDNS88ERoZNZ0wXYSSBDOzGJNBNGPvVBuHmD6UAhjbbBMLdMXGS5BIYkpbmXYMhQRxReK1fIPc6807gYBzwiVV+HiDtxPefiu/s8nlxFhxgkQAAAABJRU5ErkJggg=='

arrow_downplates = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAU0SURBVFiFzZbPa1xVFMfPOffHm0ln5r00CWl+1QRjtJhUa1tw0WYhCt1Z0JUbQV3oTt36H+jChQsREXTjQnGThRREoT+R1tJSU7H2B9OM0yZNOr+Tee/dc+9zEVPbOjNpg45eOAy879z3PpxzvvcegP/Rwq1sOgj0VgYg205vANSPg/v4Yd8rtwKzX9Brs0i72+knEnfhuO0SDBIaFBS2051NGOzDv3dLMIkkRtUeBkzCYLoFI4BRYVuYxG0FZcswaDplJmHkLsIQ058wSSs9pu7BgPyrTC3PBtnFMjkCRt3BTQTdy4wjYpSivZuom2UiMHeV6W9t46iLZbJEBjU12+lOdjMzAjv3DHbR2paASWLbA99RS8f/OzAOkVGLljBuXRddg7EIDJKiVhqt617XYIDQUKeLkpC6BmMRGBS0hbEIumswTGg6ucki9vyjMNvT4qX9I9t2Z5VYu197oi8dkmp/Ak/0q/DFqeCd+59HnHhnbzauLTftV632dZyB945se/eDQ6MVj9B1+t+Drre/LQydKa6+D9B6DuxowZt1c3ahag4+91iuAoT8MEESDQrkjXjvu+LO3xYaH60BtHThpjAAYFdMdG2x5p49MBXcRkncKoQiQ4r47rhb//DE4sipfPT1beblTh/b9HCKY1hdjDlshm7qmbFMCRBZCDJEyBuB2D4+P700eORy9eRKPbq82bc2c9OA1nowCIYnfiiGexpnoxdG+7M1axNFUqWlFIbZekBCg7OxlCJitsqxaQqB5sZKPXvmuriV9odLevVGEsfxEgC0zc5GA4vh4eGXh4aGnuzt7R1Np9Mj6XS6LwgCLwiCnkwm47LZrD1/9nRu39QO3pZObdrQtfoa/fJ7hXbNPN2o1+uiXq9TtVpdq1QqUbPZvN1sNovlcvn35eXl+YWFhW8AwCIAwPT09BeHDx8OMpnMPXOIc04wszbGbDPGZBBRzZ873X9gz2RERC5JgABAEKJzSbJ+EyA4w1acu3RDTO6aKQNALKVcVUqtSiljIrrHSdVqVc3NzVUuXrz4KgIADAwMzPq+/0Yul3s0CILekZERLwgCLYRQnuepVCpFWmsnhABjDF699LPeOz3ZckxIEoAfz1+S00/tjYgIrLUQxzGFYeiiKDLWWlOpVOJisRjVarVSpVK5Vq1WP11eXj6+kZnPDh06NNjf3x+HYSjy+XxvpVLpgfV7TzKzh4ielFIaYySzwbBR8nYODVipVMLG4Mbv1YUl2Tsw1AQAUEoxM3OSJJGUMgIABgDn+/7axMREOZVK2ZWVFe/IkSOL8/PzryMAwODg4PNBELySzWYf7+vr80dHR3VPT49HREprrbTWyvO8RGt9Z05ZXLwp0DRx586RO/1z+Wpe+H07rO/7bj1LCcRxjHEcYxRFxhhjnHNmbW0tKhQKUalUqq2urv5aKpW+XFpa+h4BAGZmZj6ZnZ19ZGxsLKzVajqfz/eGYaidc4SIRETonKMkSUhK6YwxQkqZ3Lq11BPk0q6vN4iLN5fSCSr2/SBiZlRKWWYmInKI6JxzSZIkjohcKpWKx8fHy7lcLi4UCt7Ro0evz8/PvykBAEql0tyxY8cOZjKZYGxsDCYnJy94nvdAo+OpU6emkLxqsH1ATk/vLj7IniiK5JUrV4JCoQDNZrNULpdPArS+m8Yzmcy+VCoVeJ4nhBBaKaWllBIAlBBCSilja21Ka83MrKrV6rjv+3khBBtjhBAiZGZtrWUAMMzMxpjYWhtHUWTDMCw3Go2fAOD6g8D/J+sPcOensY1vV1cAAAAASUVORK5CYII='

arrow_down = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAL5SURBVFiFzZfPTxNREMdn5u22lB9SQaMWITEGQoghQYK/AGM8cSMBjZ69eRNPJv4HKvGgifFiPJkoBw8mauKBAyhBxSjqQTENPywtAk1LW7rbN7vrAYiN7i5txcVJvpf97r73yZs3894C/EeBpXzUDXSxEqDKyU8DpEbAvFPsuEopMB2CLpxEanXyRy1zcsTwCAYJJQrSnHzTsBiM4sctCcZSiFF1hgFpMUivYAQwqugIY5mloJQMg9JtZSxG9hCGmNZhLDs/R97BgPIrTba9QfEwTSYBo8+lmgi8WxmTiFERztVEXqaJQOal6Y9tY5KHaTKIJPoo6+SbipcrI9B9z6CHpW0QMCno2PBNsq34fwNjIjL6hC2MueYLz2AMBAaFdDuP1ny/ZzBAKMntoCQkz2AMBAYVHGEMBJ9nMEwo3arJQCzfUpiagOjvqKtorVLF6u9ec21AI9W5Ax/YpWq9TcGB35/rbPknounwYtZ4ZPed6x24va7i8vWe/Qk/oen2XqFx6encvjeRzDUA+3ugawlGU3JiNim7TzfuSAAhFyNSUKJA3tDVF5GGr7PpW6sAtlW4KQwAGEtSD8dWzGNdTcFlVIjtJFSSpBLnK9+/ORqrezWtDy0zL7pNtmlzyuUgE8uxltXMpsP1lXFAZCFIEiFvCNFZ918v7Hk+lXy5lNKnNpuroE6paeZCJMW1VWVKdUt9RTJ/+d305GN858N38floQh8vZJ6C23ZGN8LffmTbWhoqM6GgP4uE7KbxcKr89nBEjST0Z4XOUdQZktaNT+9n0j19R2pmVBUkCovtFFvJ4ZXHMw3f4/pQMeOX8ntb1ri37PyDgUNjdqY0LOy/8bk7GtfugUMJO0UppytrJi8Mf1g5eqYzNE0kOF/nBic755a0IXAp4a2EASkhndVzNP4lXt93fPe8IIsFWXx2cLJtPpkdY4alUsb9qwgElK5T7bXNb++2Vx8MBTp9PmjxHCI/hBC9oWB5m6LAiW0FWQ8EgK7thtjy+AmAJWiSVUCqYAAAAABJRU5ErkJggg=='

s_target = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAVISURBVFiF7ddtbJVnGQfwX0up7ekpVSZhGy2rbpSecvBlDNYWRhfKZhwsGw5wISbKS1s/aI0uEyOKcx+2Cu02vxhZzExQEzWarRo/mKDTZRkKRdkib4FQamlpAunaAm05a8/xQ3uah4dDabv5bf9Pz/O/r5f/cz/3fV33zYfIjKyZ+uVSEeHuhZR9jJI+/tvB6UHOJDj+fxczj1UreLqMNXcQHUUfiWGG88j7KLmz0M2V0/z1EHsv8uZMhN0UUSo20dZCqp7uGn4ym08jL2SaF+GzD/LTBi60kNrI4SixD0TICp5pIrmD7k/w6HR8S3msju4mksvZ/X50zK6htZnkSvYie4Zxspezdw+ph/gDZk87wlr++BwjMb44iVlWAbfnEivgdpOswRhPPs9ILa/dzCYnE3kvzzzM+lfYcpLfhMcfYEc5X09SnM3ljzB0jfwkc7LpPMWP3+CVoM8Jfv1LRrbx2wF2H+bZST5yDFEqmkjez57wWAVL6jn3FY5UUOvGX5cdY+02/lVPezzDwq2kpYlkIeW3FLOZI9u5EE5UxfpGeqvYcMsgqOaJRnqrWRcWXEf3Jg5NGmAeq5pJhXdNBUsa6a1gyVSEpBEj3kjv0tAslPJ4M6m5VN/UeR2t9XSH+XrOTXVGwqhmYz3tGWL2PMKrQS74K7LKWHMyZLCa7QkuHQzx8O2Skl37KyuPta5Z07G/svLYzpKS74Zt3uJ379FXw9Ygf4rWRawV2IETuymXijuJ7uNnQadyvvEm3wwneTEef712xYpVkWh0Ithn+vt/OL+trfZbx47VBm0PsvMB9vydn6e5w7y8nvpcYuleNjEzEe5JYJATgTjZIxQf5/XwjNQuX36dEIgUFWWtve++1TsXLvxOkD/JgVEWBvMNcnwEBXxyIln6oZSyyyQwnOYKmJfDAJLB4EuLi7dECgszFrhIUVHWkgULvhSikzkMRPl4gBsaIFESWNwTYuZw5zCDwQjvcVsOQ+GEBZFIYSYhaUQjkTlhLoehBLcFuSGGilhwg5g+uvKJBI1zuTRCfjjw1atXL08m5srgYH+YGyGS4FKQi5DfR+cNYjo5FSVXIPkVLo1SKFQA/9PV9avB/v5UJiGD/f2ptzs7fxGis0fG4gTFRArJ7eDkDWKucjZ3TG2wQCVn0RUfK/0T+FFn53MH2treCAsa7OtLHThy5G8t589f10rKeSibDkzYR4jlYDhQg2alH0a5GOeprDG1f0rzBVyLs+so+4IJ/nzx4v7Cd99NDA0MFPf39V073d7efeCdd178wZkzXw3P1qP8/gwvdfB2mlvJsxEWvcVTYXuwjtcaxvrSdainvZqNGZ1ugZVs3sHZMN9Az+czFNIJpHtTKY8F+TixRnpjxKcjpJyljfR+isVB/m42jPemqkkDbOTwDnqEFm0168a78JRmaCWbG+m9n0dCQ9kNXPgCB28ZJEqsiWQlzeGxOLF62rfy73IeDgtGdjmf28rRHZwNd2uo4qXx88zi8FhGLGN3C6k44UoKVrOtjqPb6a3j3Nc4Uce58fejq/lyJr8KNrWMHc6/NyUhaayl9fmxM/CTk9kVMH/8DDx/MrslbBk/A9980U6C2Q/y6l5SVbzgfdwOVvDC+O2g1U3O3VPCMr4/fm/qKeXx6fjexYY6eppI3suuGYsIIkpsE4eax26UPTXsi7DMjX0rP8KyGl5uoKeZ1BP8o5CyqeSZ1l17LtWVPL2Y2jsoHEU/iSGG88krIjcHXVw+xV/+yZ7eqWzhmYgJYnzR3lPMornc1UvHeU5f5XQi0Pw+xAeB/wGVhoz25sbBzwAAAABJRU5ErkJggg=='

p_target = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIeSURBVFiF7Ze/axNhGMc/9yZtUuNdSheDhc5Ce0FcHEQcOvUfkFIEFwenTm4Vhw6iKIK6ukkRnCtFl1LaQXAQKiJicdFgO4hJLzHJ5XKvw11KiB7v9U2uVskXjud473me+/D+et4X/jOlgfnQ/nWdAl6Hti+J/lkGpyFMlIYwUYoDYwPTff5nOszTN4wE7gJFTZBiGC8143+TDbwAzv3h2xhwL7SHiUsMaBD+iQFpgRgaQEXgGrA4l51ckqOFBV+cOCn8n1XD3V1Za5RuA4+AJ8B20jAAzOXOrP8wz16sps0UBLPT8pz2uPN2Y632cVYnZ0oLJDu5VM6fv1pNm6nuJeKKjGBkYsp2y+6n9v7WYfOmu6yq6paBGoAcLSw4PSAQ9E4lbabMbOEK7tc7YXMOGFfk3gO8DsxlYFERsAXcAPDFmBnlZABSZK2upmXggiL3Q+BZB+Y5sKEIKHdehF93onYwCRLZrHQ13SJezxwMkweUFAEHMtzdFctzlnuHygAsz/Fl/dvTruZa+CilNYF3PGfTlq1LcmRiqikyIlySMu/t+5azvf6q8fm6Tl4dmCJwc6f1fd52y02r7ZzOtSr1fONLKeN8ePAyAHlM0NN7OlBxlegOnARI4kCqqn2fI6raM8Aq0ecZ1VWlGMbPDAJGddKLc2+KddKLcwt8F8NHpfdxnP65A/mRaQgTpWMFo1Uoe9QkqMpvAH8A+Y6HfgGzI57jLS8lCgAAAABJRU5ErkJggg=='

following = 'iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD3SURBVEiJ7dUxSkNBFIXhj2CwEEFLUVFb7UypOxALe7G0tbR1C1lECsUFCLa2KVMJVhoEIZUogvFZDOIjTBDz7kuVA9Oen8u55w4zTag9NOqGDPCINnbrhBSl18MFNiIhl/gYARX4xA2OsRABWsIJbjHMAN9whUPMRQDXcIa7DKxAX8pvPwIG21I+92OAP/ltRQFb0gTPGdhQmvwUixGwJg7QwWsG2I+AlLUqLUsZMogwnscRrvEucJKGtE1tvGSMK2WyI23PQ8a4vF2b/zVel3rSHWP8ZMKeLPtt/FfGuHLjp3K7clf4HCtVjUchtf8nU/kZZ/pT3/NBcg+HB1L+AAAAAElFTkSuQmCC'

previous = 'iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD0SURBVEiJ7dW9SgNBFIbhx2AQSSkI0dIudmljaScWFnbWtt6Ct2BpK1gIdmkCaS1jaasgYrmICCIKa7EbWMIssnEGJPjCVAPvN2fO/PDPH6CFQSp5D6e4RxZT3MUJbpBXxq9DOjjCCF8z8hwfuJpH3MIOzvEaEOeYKKpabyrfVuzzQ434rpzfaireKFd0WyN+wllZWSNWcYghPgPiF1xgH8tN5VOeA+J3XOMAK/OKq2QzAWNsxhBXCVXyhkvsoR0j5KeeZIqe7GIpRuD0dE0CYTkeFaerHyOMhPckRNIbHyLZ21XHGo4leIXrSPafhEj6My4434gAcYQq80uSAAAAAElFTkSuQmCC'

info = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD0SURBVFiF7dYxSgRBEEDRp5hoJmikwibeQEMRvIORmffQQ7hGIngHo0UEQcVkk72KKEaKBrPCOtgzs3bLitSHomG6qP4UQ3fxj1jBGUY4x+osZe7wPhG3sxJZr4l8xtpPC85nyDzitfbtDU8ZNbM48rUrxznF5goI7WALQ9wXqBcEnenyAy/iEBsteQ+4zDZq4cD3l1s9TnIPWuiQc6V6f5YT+9vo5YqU4kKhzuQ8B8UJmRQhkyJkUoRMipBJETIpQibFn5JpmvSWsKeagZvojddN7LfkvuBmvE7FqW6z77TRTx3Y1Jlr7Ko6VIpnDArW+z0+AH/7QhQbUaHtAAAAAElFTkSuQmCC'

smallnone = 'iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGASURBVEiJ3dXNThNRFADg77YQSYHKhmfgGYgE0ZjYIj8JCx/DuHNHwhsQnsKUFWkdYeNPgvAOvoBhCSghkXZc2JKhU6aXohvuZiYzZ+6Xk3PPGR7calBusZlQvc8+CdUWmw3KvWel3k2Fd9jqsD8qlFDtsI+t7n43kZTtlE+YHwU6YLJDE/M4vGCn9y5kA5tU0Aw8x3GJ2jJnMcBvEix2gfprfuYygVUu/l58js3ogMkrPtwG5DLJZhRo4VlRRj0g5SkO2yyvc94fNxAZAB21qWU36AO+takPAgqRIqhbgxaWhgFDkUHQBBuXvI8FopB+KHCa8jgWiEYgYbbDd8yknI8zV+NHzLel4SHXjdbATOA0MH3F7h7T/wRpUskU+egRc/iCJ2U+xkCFSKYWS7qn6wUn46zcBbpXn8Qe45iOzwFZKKYhc0g/UKJeNCRjoNwUjplZQ6DcDLsu/KgAvOTXGK8CX7FQJmkwlUMCb0cBslBgDcdYqPAmF/Q///EPZ/0Bu1a3OjtclPkAAAAASUVORK5CYII='

plus = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD/SURBVFiF7ZZBCsIwEEVfU3HjzqXgyp0Xc+VtvIV7b+ApvEEFl6LWVhedQkgjajPgIP0wzLQkP3+SIRMYMOA7ZAocM/F3oEghGqVrYQVUwAnY/FpMHvje0BSTzKUpxqUSaYnJUDim5GxoEsoxVjOmxJipGd/3xt+JcYHvjVhvWgA74CZ29eKYTWTMBTh648vIXP97D5z9hWM7MwbmMjG024v/uXBN34wbe3FnJ2NiaskyJPQzLD1r7xhH07lrmsZZSdzaI7AONJ4QW1msANYpRKbagaYYM107w9AN7DByTCOaAjYhxmQBm6gZh7GdefBvYjTawVJ8CRwU+AYM+BhPSQtRKD1cP4sAAAAASUVORK5CYII='

smallinfo = 'iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAACpSURBVEiJ7dbNCQIxEEDhzz+wAr140CIEbcCL4M0urEfsQs82YQWWoA3IqoddUBYXdhb1lAc5ZMjMSyAJ0xFjgQ0eOAdzazFHVgjumNVNbAck07f1rWL+dca4yE9yKeY/YYgVBr8SJCrp44RrxVhEinUr4jccMSnFR/L30otIoqzlV3gZSYo8xsYkSZIkSZL8gZ1XVxIdGbblgp+++oO85ek02GCGfTn4BJ+CKBgiHkn1AAAAAElFTkSuQmCC'

smallnonek0 = 'iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAKZSURBVEiJ3dVLaFRXHMfxz2TSWJOaiSK+oFDowiBSFTQl2tYHbX1UiVZsu1Jc6kIllgYXWgQ30k1oN6WtIioWAgVjxmkG2hjBKHVjdkoaFStEAy6MjyiMyXVx59qbyUycbP2tDv/D+X85/ydvnNpIpjmUoTZmrsLuyfjJUJvmUBvJyFYRHappweFROmOgRdg8GcAonTic9zcWEtAa0IXGGKgBV8sBZKkZpQONuDTMj+MgmxjGpjgoxfJyIFlqcmTwSR6w/iueRPeJwgcdVCdIY/VNnp1j8d/0TQR4wfmAlcUARSERaITOSj7GlQrWbeBR/vobPMfZQsAIG5p4XOgvWWiA38l1M7iQz6czP2BlFZlefsFitGapjAF6SgGI5aRQ91l0kFZcwPIl9M/gBrZkeZEjHQOsLwWYEIJlQ/Rs58x1ht+n5iRr/2J2LszZqnIAlMhJXnfxDxrW0NjMKaxOMBSQKhcw0U/mYQ56EXTxQQVf42FAKuBxJdua+AwncExY7kVVWcLegDM4gmtT+TnHnSR1CYaQekBXHdmH7Mz7OYZnuFbuTxqEodLBhR94OxmW8+UpzEd3HfWnWdrOO8hhF74r5mwiyNWoMd9jVh+5PXz/KYPNtAzSjxVJ/mxnGp7igTBfr4UksHAXN6POx+Wj7L7FT5jSx7sH2Y/uAtC/qC8HUj+VO1/wRwQYYd0gv+WdtGDmAPfeYmOCixFodjhOakpE53+1kGrnYpogTU+R/VKLrfiScHadpztNcJzbC/iwWGheKT4cjZ9Zcc3Dt2iOQAUjZkz/vArXJAAwgJmYC2t5upcDA/wnDF2mLay6sZAE+8oERDqAX4U7pKmf/b1hqK7go2r2jHtRYse/TrXYIZwGVRTf8W+OXgLDgOWm47Xr+QAAAABJRU5ErkJggg=='

k0log = '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'

k0circle = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAbDSURBVFiFzZh7TBzXFYd/d57sMAOYBUwWG/ADPzD1qyEyL+NHEprGLSaui4pkgtS0alAoSkgdx2olR7KUREolVGw1ViFP1ZJNLTlKghMHCeymIig2JIIICpKLi01Yw3qxF3bZnZ05/QNYHvsAXKvqka40Gp0557vn3HvPuQP8HwlbihIRMcYYAcCePXuS7XZ7SU9Pz0oAmihy0aLIJEGAl+d5B8/LN2XZ0i2KSufAwMDkA8EQEccYMyPo7uR5/DYnhz9UVCSou3bx2LiRISGBgyAAHg9heJjQ22vi669NtLaK43fuWC7wfMKfenp6OoiIByAxxjyhJjl35ioRhYvSaosF5ysrRbOvL5qItCUNw9DoyhWFKiqizcwtSY3pm7anR/CxJDm0bx/v7O1dOsTCYZoaXb6sUOE+xWFdvbJ43ZO/ycLhw/yyKDgOx159VTL8/geDWDhGRlT61a8VI2X9I8cjOiYiNjeEHIejdXVRIY22tSmUl8fT5cuWZQN5PBodPaZQ2kbb75YalOLXXpONUMYcDpVsNkbbtnFUVSVRZ+fy0+fxaPRCtepPzlj79GIgj5SUCKOGEdpQdbVEq1YxcjjU/ypldrtKBw/H29V1W5PCkiQlcR8MDoZ2NDSkksUCOns2dPqWO1pbFdqZv7phrn9uznNmVZVYtmpV6N13+rQPmzbxKC0Vl5jtyFJQwGNvnqtcW7ttw0IYFhfH1Tz/vBhyy+k60NCg45VXJHBcKI3lC8cBpYd8QuYaV+U8mKqqKqmkhP+p1Ro6Kpcu+cFxwDPPCA+HZFq2buWxYY27dObc4QDgzJm69UVFfEK4j86e1XHkiAjx4WQoILIM5O/yJFu/vZURgJEkbM7NDT1rtxtoajJQWvpwozIj27J0pKyc2BKAsdm4VJstdIpaWvyIj2fYvn1qOdXW+pCf70Z/f3BNHR0lvPOOjlOnfOjujlRzZyUxkcGW7EsLwKSmciv4MNXis8/8eOIJHowB77+vo6fHRGwsw/Hj3nl6vb0msrIm0NCgo7nZQHb2BOrr9UVhVJUhRtVXBGBiYxF2NTQ3G9i7l0dXl4lLl/x4/XUZHR0GCgrm01dXe1FQwOPLLxVcvGjBmTNRePFFLxwOCmN5SgQBkKKYGIDx+WCEUrTbCX19JjSN4fHH3XjzTRkeD/DssyIqKmb5nU5Cc7Mfzz0ngk1nu6xMhCAAn37qjwhDBHAMngCMwyHoZogUt7UZSExk+OorA3fuEPr7CSkpDG+8ISMmZnaN9fWZME1g8+bZQ0gQgPXrOXz3XeS14/UCkz7JGYAZG5MwMhIczvZ2A6rK0NlpYv9+Hu++G3oNOJ0ExoDY2PmbIDYWGBuLnKbxccLgSOxgAEaSVox3dQXP4Pp1EwMDJt56S8bLL0u4cEHH7dvBxlmY/o0Ii57YN27K+NdQTF8A5sCBX1y7ds0cXWjom28MPPWUgMxMDkVFAh59lMfJk94gg1YrA1FwFMbGgPj48J2mYQDXumKGh6O9/5zjmOTiYvH0+PhsxZ6c1GjNGo7q62erdHu7QpIEunJFmVeBXS6VRBHU1GSZ972msYhVfmhIpbIXdtYGUe7fr2Y2Nlr8c5Xd7qlmaO67mhqJEhMZXb2q0K1bKtntUxM4eFCgoiKBfL4pvdpameLiGDmdoVsS09To/MVk3Zb3o41BMCdOnOAqKix/HRuL3Dh5vRrt3s0TY6DCQp50fer9wEA0rVvHUUYGR7m5PCkKqLExfGv6/fcq/bJmR0MQyHSquPLyLamnTllGTTNyY+RyqVRXJwd1fG63Rp98YqFz5ywUrkmbmdCf30uzr8wtCd/pAUB5uVb8+edKyB74YQzD0OiL1gT/7p/v/fFC34FSTFO3A44x9pGirH07Lm648rHHlne9WUyIgOudAt4+t+Ho1fMtTREUidHUFRRExL30UvIfWlqizcVSttSh6xr9vc1qHK7MORaOYca5BACMMYOIRADU3x/V39Fhv3v37sgPU1MpSpYf/GZ67x6hqXnFWN2HGUc+qv/HX8LpsWmYdACjjLFxWnAZP3kye3V09OAfs7PHf7ZjB5iiLB3K5SIMDVnJ5drzN7e7rKawsGgwkv4MjMAYC1leiUgAgNra3VstltHfp6ff+0la2j0hKYlB01igFSUCfD5gYoJw/z4Hp3PDpNf7gy+AAydycg51RIKg6T8gMzAMQDaAfwMYARAoVDNRIiKuvb1dvXHjW0nXP87g+aGsqCh/miybVlFkMsfJXp5XHDyfeBPI7xaE7O68vLyJhb9ZiIgDoDLG7s9kgYhSGGO3IwH/z+U/ksZm91WcOScAAAAASUVORK5CYII='

emission = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAQySURBVFiF7ZbLbxtVFMa/c8eJ8zDkUUIkHkpBpk0yjh9MbJOAkLuooqak5aGw4A8osKrEDlEQKBIUWVAEQkiUDQixCQQSGkFBrUIRleJJZDvJ2EobVUVUVRo3JFVrK4k9c9iQyE0djyePrvqtZu6c853fPXPn3gHuqbDobhTx+VqaJF10kEA92JiHLp1Xp6b+udswwu+VXwPwPMBrtQhkMPCDGtNOAuDVcWknSdo9rUeI8BLunDQBkB9ubJCuXkvF1sh3CiTocjUS6AWTsJcDgeZdOw7DEvwgLt55go2WbcrOw5BRU0qcAb1uW2F6eyH5fS3P+r0tR9dgwHMlJQueXb20bQUiEGjeZSxT9+ULopvBV0E0sPpMsmdHjeXyDICqjfIJuLWkl4/l3VtX0NvyBLN4kQlBBs6RLobUyclLd8B6XM8xGUcLeQCAYBEejU/9ZhlGUZQqSc/sY4jDANvAfLo6J4ZHNO1WsbyAR+5iwqsA37c2yHQDzF+oE4kz+bGmMH6X61GycRfAXcw0YbAxPD6RjCJvs1qv3l5If19oOdS0JznU3w/9gNNpv+6wu5n4AQGR+vfm0uTMzMzy+ryCMKFQyJa+ca2TWBxk8G4C/Z6l8sFoNJoygw+FQrb0QupNEFeqscRbxaDX67YF3CHL9TmbsT+zmDoMiDkmY6C6pvH8yMhIrhSzUChkyyzOHSNCWTpL71oBAfI60+6VnybGGyCcQY5+LnSQmYGkF+beJiJJlyreGx8fz+Y/Dz7pcuu57PLYxPT0Rh5rnXHUNoxWXrnyyi8F3qWZFEUpSy+k3gFopaq2oa9QJ1k3XmeIk1a9LemA02n3++Tjfo98rLe38MHr97TK7V75a5h8MFva9A44nfZ5h72PmBeb9iQ+7O+HXjBQUA8ZNAiTNbRpmFBod8X1xfI+EM+q0cTHkVjhQoryeA3rHLQv5T4389wUjNvtrk4v5N4n0OVITPsERWYsGZXdYJz7a3r6ppmv5YNSlmVHBeWOg/hSJF4cBAAx80Ei41Qp3pY6E5JlR6acP2DgohpNfmYCgoCv+Sk2MD8aT14sxb/kziiKUpMu44+YaVKNJj41AwEANsQhCAyVWqMkGK/XWyv0pTCBVDWmfVlKjs+39yEiODMr9Oe2wTzT1lZXhmyYgEgkpn1VqrFkSD0g/lXTtJVtgemQ5foVYYTB/IcVEKfTaSdgP9vEcKk5RWE63e4Hs2U4AcJZNZ741oppXZV9H0BJVdVmzaNNYIIuV2NO6GFiGozEtO+sGP7v2gMqfeFuCBN0uRpZ4jDY+EmNTw0USiompa2tmQCHGtPGzKOLwATd7kfYpp8wBL6PxJM/WjUDAJJyPQCfgsV/mdtgFEWpMkgPsyG+GYtqllsMAMGg836AOsm+cnoz+fmigHvvY1sx8HtaZb9XPrJVkHtar/8AQ7CXg0LBvDgAAAAASUVORK5CYII='

redsign = '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'

greensign = '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'

smallfind = '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'

plus_spectrum = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAActSURBVFiFzZdbbFxXFYb/tc9ln8uMz2Qc27EdfEmdxBJKiCqiNC2tBBEIIW5F4gEk1AoV3pAiFR6KQJUqkAAhIXhAvCIEDxVXpaKoIKVpYjcpUipAIk5jnCZ24mTs2DNzZubMuey9eJgZxzEex7hGYr3ty/r3d/59PcD/URjvVcCCdcIi8VMDlCrwld2A2kmQb8qvF2T+3aLbs7LHzS/lLOdnAHp2LLiTJCnlIceUL7mWfXKjVpJl11IVvxhG0YX/NQzlvNxXfdd71jbNfDcNpXTcaDb+UK5VvwNA7TqM67ojvue/kHdzxwS10vgh+bVG7UqUNL8fhuHMrsH0Fno/m8/nv+Q4Tn5d9bZy4ziu3yvf+021Wv3Fe4LxPG8wl8ud7t87cEgIoYGHu7GZvtZalCsr/6hUKj+p1Wqlbp3NLYSEbTtfsG3ndrlauQ0ARJSZptUUwjhaKASFbonl8kq12Uz+1Sl/+17pU/1Z9vln3NwqgB8B0F3J/9sYHR3/xtDQ8Gi39lu3Fm7evPnuDzrlKeAMgE8y0PMhIOyWt5UzXYMMSi1pbyZKACBMkWyozwOAAIYBdF3MYicwQojEkjK0pAxPLC0VXzp/7msnl+72mbYMTVuGQvwHTA8AMDC0pe5OYEiI1HZlaLsy3N+oeZZS/qOLi5O2a4e2a4ckRLohpbMLt4TZ0TQZQCwtJ2VmCuLEBgAvSTxpOWG7feMCzQMAAb27DpMJkQrbSAEDfhI7AOBmmW9IGQIAC2FtBsPAnl2H4YxTx/ZCAPCTxAcAM8sCx2vBZMxrh+PLrZeB2y7uPgxUEgvXCgFApmkOACyl9kirVYekNXUA0NdypXOEbAmzowWcMqeelKEnZWhmWQCiBMz2aKkES8ow1TpbN8D6K2T3nQmr1Z6/vPKKAQBfzLL+BtG8x/zIjTfeOHIuCG6FYeh1+tJ9mJWHrZkdncCdYICmgRjALwE8q4EPPwm8vr7PeeCEAC4CeJsA+Tjw/m56D0zTNPD4ReDodmHeAooALAb+3hbbt7GPed+Zmw9z5gEYBn6rgB9uFyYGBtoi/wSQ0SYwvA4G24W5AIwAGCBgYrswAhgFAAVcB1DiTWB0+yqgFowzfX+bd4ch4Hj7S0bOArlt8nwEwMKTwDsA7nScmQIemQL+egF4jFowWgPzbbiu7phtAHoTeIJbdYYNvDkFnCKgJwYWbOC7BJxNgb9ZwKAAbj8GLAD4GIA/t7XudJwh4CgDHyTg+VYRd0SrHQz0Abi9GQxNAT8GcAzAUwz8jlpvjxcBeAD2AqgDyDHwJwL6ATwKAG2wo1eB018GXv8j8C0fOFEFfl8EngEQrHP9UgY8bbQg3ibg5wxcAfAVACYB5xjopanW++IQAZ942nGu5oaHn/p0ln38M/Pzn4tsO675fiSY7X0rK4W656XvTE6W37ew0FMoly0Q4bXnnqugUNAHzp71JqenXQBYGBmJbg8OVsfm5nr6l5bcGwMDyy+fPPnW6TNnPmopZQGAJkoEc+ekXgVQoPPAgV8PDT0/c+TIyP79+wtjY2PKcRzFShGE4M7Xjb366khlfLyyOjlZ0VoLTlODTJOV1obWWgghdL5UsgcuX+5bOHVqXnleKrKMeq5dC+JCIY4GB6Ngdja/79KlodLx44t3h4cb2dTUnuLMjHzNtn/1zbm5OgHAxMTECwcOHJgcHx8Xruvu0VrvJSJXCGERkc3MUghho3XpmYZhsBCCiMgwDIPR2ghaKUXMrLTWrJQiABkApbVOiChm5kRrnTJzJIRYjqJo9fr163pubu7K7Ozs90wAsCyrnKZpYXZ2dtTzPF9KCSIS7UEEAPZ9P7JtG47jaK01ExEcx2GlFAkhoLUGEXEcx8TMUEpRs9kUSZKgXq8LZraIyAAgmdmL47i32WzWsyy7YVlWZW03KaX6fN8PDx8+fJmICnEc7xNCOERkE5EkIrvZbDrNZlPWajXEcSwAGFpr1lp3gLUQQgshCICSUmoA8DwvLhaLTWZOmbnjTlNKeYeZy1evXrWVUn1rMKZpLpTL5WMXL178QBAEnud5ICLRdocMw6B8Ph8HQRABgOu6mojYsiy2LGttXaVpSmmaEjNTFEUCAOr1ulhcXDSUUoKILK01M7NuNBoD1Wq1DuAaEc2vwWRZNjEwMBBNTk5Ou667dv13IkkSY2VlxV1eXnaZWaRpaiRJYgoh0Gg0JDMTEbHnebHWGrZtZ5ZlKSLSQRBEBw8ejGzbfuCfm4g4iiJzZmYmVyqVJtpHwFoMBUHwhO/7/blcrkdK6ZimKU3TNPP5fNrb25sUCoWG4zgZEXGxWGxshO7E6uqqy8zUbDbNcrnsLS8vyzAMrSzL0izLkjiOo1qtFtbr9buVSmUKwOJGmK1iL4A+13WDNE0D27YNZnaZ2TVNM2ZmSURxlmWSiCIiipIkUZZlVaIoqgBYArD8sEH+DWfKF2nWONe7AAAAAElFTkSuQmCC'

a_background = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALTSURBVFiF7dbPaxxlGAfwz7u73URpak3dxtTaFlssFRrSVqHYNtpURD0Ui5cqiHiwB3tTb1UUQQQpgn9ADx6E6EGhClo0hEI2qVXQWrD+1tYYloKhWBKTNpnXw0xIwN1ki2zqYZ/L7rvzzMxnv/POO0OzrmMN8UaZzxbryy0FJrIF+wZpu+4YGSLHbQs1/WfMILvLXBzivgXaVkBkTUMxOe5ACQcXaJu9PI3FJHRApHMxTGBVQzFYnX12LIaJ3NxQTJhD3Fpt+3vkcUM2bCzGXDJVMaU0lbBUmA5MoXWAlVVOMH9tWZJkvoWWKumEOcxYQ+dMTOMv4QzMLIw5n7sWzBD3nqKrXsxp2rEs8k12sH9hCnOYC9eUTOT9GY7Wi5nK7qRcepmmQxVMnIdRL2aQdegIbKoXk2M9zPArLsYqmCR7FIQU0zo0d5vXxgTuyf7JugGW1+npxcgefkBlNpkyG8t8McjOkGKShN8zXM10ChkgDLMrpr/liwyX2RdYMcVIkdcCA1c5s4zOHKM7GcGD+DQ7VmU2mUBX5O7A8+lQJZduF9MJP1oNE8q8hW70RD4IfIiXcSNuwTiWRz7JUYrsyPb9Uvr9iV30lTkmfXL34bB5a07g82kO5FPEV4G3I+fwDAqBk5FVhemi/YUr1v+yx7P9LxmeapU88qLXNww6Ggt+u9piJCSKLeMemin649Jab7ZV7C1M2ozLH79q9PEeXWNPmmg/byOOTN6k/9Iaw+0XPFwct2Nipb+OHVc6fL/LIbEtsi0GkyFqhSSnNyTawpFXHFr9o9LwIWfnR1acEa7kxdnxo885UNnqu1NPOwfFCfnpFkkyr+fOfp1bj9s98IKPxm73d3FCvvtdm//cYOznvSrdfTbddcID3/caOPuYn7a/Y8var3WdfsqJ7X16wsGT9teaUEtdS/XaWVc1MbWqialVTUytamJqVRNTq/5XmH8AMPPDdCOdg6AAAAAASUVORK5CYII='

r_background = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJmSURBVFiF7dZLaFRXGAfw37mZ2FhUfDTGByioCIKIoqLNy2JA7ap0o7XLgKsu265cuOpG3OjOhQu7kiziwk0hhaE4d9JWS9GFoqCixjS4EKEojWbmdHFvmAEnyYhM3My3mTn3fnPv7/zPfQzt+ohV5mzKrwv1JYuBiezAUInlHx0jRyRsnK/pgzEl+lOelzk0T9sKiGxoKSZhC7rxzTxts8vTWkyVHoisXwgTWNNSDNbmnz0LYSKrWooJNcS6RvtH6MDSfNhajFoyDTHdWSphsTA9mEZXkZUNTlD/bFmUZO7AJw3SCTXMi5ZeMzGLvxu3oDI/5nHyPpgyvb+zq1nMn6xGZ+R2frB3MIUa5sl7JRMZrXCuWcx0ficl2TLNhAaYWIfRLKbEJvQEtjWLSdgMFR7heWyAqeavgpBhusq123xuTGB/PpNNRZY16TmMiQHuY2o2mZStKTdKHAwZplrlaY6bM51CDgjj9MVsW8cSxlOGAiummVjCT4HiW251sj5h8iATOIKx/FhTs8kEdkX2Bb7PhqaSbL+YXfCTjTAh5Tx2YzByNXANZ/ApPsMrLIv8ktAd2Zv/9qbs+7d9XEm5JHtzX8F36p45gT9m+LojQ/wduBy5i1MoBH6LrCngKLYHvnzG2HEqKc8wgnt4gK7AMTwK/Bj5Cjvx8k3tH9xDDON0YLTKWOBkPsmng/yT8hJ7InvwOp+wmE1iZbjOlsDmfor1kUWSQHV2XOaHwPjnpFCk8AWVQKzr2RY5EbnQz7836fyPA5HJAR6WsqUbjvzcxV9v6K0ylHBRBm9Xu9rVrna1q11z1f9vrZ5nUohDqAAAAABJRU5ErkJggg=='

ddistance = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMKSURBVFiF5ZjLaxRZFIe/enUlndbGFybRgBiFKD4iisoIQVzFIQjiDIyjCx8LwUX+B1euxIW4EUFR8LVQERcKDvhCiegoiCL4ipmQztjGmK7uStete6tdtGKM6XRVaGM789tU3apfVX11zrmXOgVVJG30gfpZxq+1umkqKCgoACj19Vaq4jkpg39d138Y8lktwLNIMH+2z+jp3NpYpwpWLggMV2HmZGC4ShmuH5g5qTRXKD0nhOHuO9wVf979fk8IkHnAX0DzeCZz9IGGmWZ+zdJEDM320CwXPZZFsx0020G3HDTLQbcdsJ39R+41hQAB6ASagNXAvdAw5fTs1VDd4xeZhBBG0hOqLuRlvwAWsLuiMC96nfjt+/3TPJ+85wd+iEs2AMtHQJmArAhMR9vcdMf65ldgO0s6ToRJ006g5tP+IuA34MxYRj0qTETFKEajC+gGngLbS5kjw2QcYXb3ZWpe9mRqlSob2SSwF1gLnANWACdLmSOn6fy1Nw0XrvU2ConIZL0PZexp4OqIsQLOVgxmx+aF/+zYsuTp55rpe5uNeouS+t41E0llI3PzwfvE8UupOVJqwlea8BXC9xFCIgaHyqapsjBtK6dn21Y1pMZagf/TaaoqmMiz6fiF502fp/ak18xo/W+mdlXBRE7TuSuvGy5f713m+XgfHM/9oTDt6+akV7c29ihpZzv2XKyHytVMZJipU2JyatLOgz1sGGN/JE1UP3fNXO9KTb/xd7rJy2v5rOt/011MKkz9rLi3uHmaEMJwLVNPVBImcppa5idzv7cvSG3b1NJrx4xcGfsMoH3E2AC2ljJHjkxEDQGHgAFgNrAR6ANOTwimP+1ZT14PJZUyLD8wbam0uFB62L5JAjeBXZ/GAXCglLk8zIAw7z4aTPhKs32p1foST0gtH6FvOgr8AcQp9tqnJgzT2jJluHXRzLelPq5CwNwFHvGlZSn5ApO1ztyhmLJj45m+iUzqnazpepy1VMGzg8BQCrMgA0Mfq2aEX6gNCXOQYid5azxTVf2fqSp9BAy/bd226Jc9AAAAAElFTkSuQmCC'

#flask = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAUUSURBVFiF7ZZJiF3lEsf//6rv3NvdiUOnk+427ZCk44BGEBWMQxYP9SkqDokDTgR1YxbixgHBaeHKhS6MQwTFpygiT95TEBHEqBiHiCPOUxQlxrRD29jDPd+pKhc3HWNugjd9F0GwVufUOfXV7/yrvvoO8I/9DYwdxPbcc1Vau09vGAIQum/8CbLq7jgJwMRMFkwdwMiyhbXhWpH7GsgAgMG9OQJAZrpgJzDoQkI/utFAhV8xgYmoOlG6M5hRTGIPAHujB3UUKDGBGVaoc5gKxs0Ywzga6EENxcwr1DnMtI2jgXE0MMndCHPzy0NrTrliyfqae+7KZfXEfe8fDfy0e2DWj+zxc2PRim+EyDkzv/fdzQs6Wa8jGBEKwxOTugQdqeioTrsMU8yadYTs1bUs9dR7pEgFhZrdk0hySVIr5u15mY+XU5an1iPjvV1Zu925UOsanHNxfb+5B/UtO3xk/sqTP5da0aAhG6tMaEkgC5EreolcVZ+uuveQ0Q83LPaJyc1W2pPAlsnYCUx3/5zj6sMD5w/fcOFns4bnj4ZKCbNMIgu0NCKzqrIUWlYVMpmzIpVC5MYU8/cPPDn724fWnpbLyXXIeHPGMF0LBlfOX37CoUNX/HsDVUo6sgOZjJJgNkcWlZJb4AxaksySy1x1FaU0kEUmcwP18u0Tr13aGBmrw+x/O8u304brWjx06cJVZxw2dPmpm0hVWiQnlUKFS6JASSgiEgVqQkV4EoVmpcKqJIkqabayyunY1+54tXtgYDNUz9olmNpA75L+k486bu6ZS38hoUAkbEmMKhKFalUkRCQ6FKEJ4UmECvfE8CRKhVuaspy0EEVZpuOfvuUDnV0rABzcNkzPosHLF1511giiCUFSPSSR0CaUJxJKaQIaofQmSGVUSk0x5YlKlSRKK5IWouPdqkvfWP2cFHJiuzD79h2/ZK5zSxmmVdlaEqqTipBEUl3+DDetiii1NEtSUSVRY6xKqSZa1EXTnrM2AhjaPrG2qLJw4Pzh6y/olZ66MQAKw73Z6VQEIhAASAabt6BK0AmDQ8ggAJoACcHKQQSyIugOGTOUVmwae+vjExDx4ba5W3bTjavXPLvivEuPYSAQAIkAGACCZCACBGPa/8PG7+SLTz5K+8zfrzrwkMNyRAQpQfw5ntvFP/7I/W/ceM2Vl2ybu2UC982ZV9uL3b073fTb+F9f9yLuX307Tjl9Od559RWce+FlWLT44B2++4ev6Zw7r//d7R+1wASi7b+119etxdnnXoIzV1zUbsg21tquHR1syy9YicceXoOLzvkXHrj3DlT5Lyf+Vgu2fnQrDNm2MvsfsAiPP/US7n7wv/jqy0/x6H/uaxtmR9aRMl9+/gkmJyfQ29uHxQcdilyWHcG09Ez7ugAjmzdh9Z23QSiY1z+Iq6+7te3Y2EF7t8C89OYL3+CYBW+rSMUII8TYnBpG0oRSMWgKGI8atOVH3rTV/358bzKlJqQxwhLVlFIJxCRoSWgSYkra888/05K7xfHKu+t+/HnyiK8BZAJlABmBTGHpHpmcvkYmPRNSAsjuyNRo+2R/7Zknlv0lDAREIFHoHkiEB0n3iEREgHRYpKbScCCSO4JCZ0SyQIiKw5hAC1IcEQnhYaoO84RAQNooUzU6Mbrhrv//RncPD4PDw40IaHgw3BXu9fBwmHkEDG4WFu4WTjd3C6OHuZnDzL1yDwuDVe5mhsodZXTW7f/Y7rLfAfbBhA1z1njbAAAAAElFTkSuQmCC'

flask = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAUhSURBVFiF7Zbvi13lEce/35nn3Lu7WZPs5semWYUkq0bMRmwVTGO2VeNGMWLA4FqpIjVUzAtLX7QVQZT+A31TtbWlIFhoK6ghKGKxldomwfiDKFFRC2nQxpCtdru4P+55zsz0xd2I5iZ4d+8LEZxX58xhZj7PzDxzBvhavgLCDmx7Hr47vfCNvjAEIHQ/9hFk90NxNYDphThMHcDIyNraUK3IyxrIAIBVSzkOQBbqsBMYdCFhJbrRQIX/YRrTUXWS6c5gJjCDswAsRQ/qKFBiGgusUOcwFYwnMIkpNNCDGoqFV6hzmJMyhQam0MAMv0SY+18cfOSaXcMHa+65K5fV479+41Lgoy8H5uD4WR831u08KkTOmfn1D+5f04m/jmBEKAxPTOoSdKSiozrNG6ZYtOhiWdI1knrqPVKkgkLN7kkkuSSpFSsW/8CnylnLsweR8fp8fLc7F2pdq/q/Xz9n+fnLRjaOr7599D2pFQ0asrHKhJYEshC5opfIVfXO7l9dMPHmkXN9euaElfYEMDcZO4HpXtm/uT40MDZ07y3vLhpaPREqJcwyiSzQ0ojMqspSaFlVyGTOilQKkRuzzB/+7one9x994bpczuxDxssLhulas+r21TduuXBw17YjVCnpyA5kMkqC2RxZVErOwRm0JJkll7nqKkppIIvM5Abq5Wtbf7qpMT5Zh9lTZ4p3xobrOnfwtrW7r98weMe1x0lVWiQnlUKFS6JASSgiEgVqQkV4EoVmpcKqJIkqqVdZ5fTtA7/Y3z0wcAKqO+YFUxvoG145esnm5Tds+i8JBSJhLjCqSBSqVZEQkehQhCaEJxEq3BPDkygVbmnWctJCFGWZLt/7wGHtrRUA1rcN07Nu1R1r794xjmhCkFQPSSS0CeWJhFKagEYovQlSGZVSU8x6olIlidKKpIXoVLfqppcefE4K2douzNnLLh9e7pwrw8msfFoSqpOKkERSXT4PdzIrotTSLElFlUSNySqlmmhRF02LFx0DMHhqYG3JytqBsaF7bu6TnroxAArDvdnpVAQiEABIBpuvoErQCYNDyCAAmgAJwcpBBLIi6A6ZNJRWHJ989e0tiHjzs7FbbtN9Dz7y7M6bbruMgUAAJAJgAAiSgQgQjNnZGbz31mEd/ualpYrAzePwoVeK9RduLLu7e534vD1Psf/jY7956b6f3HXrZ2O3TOBl/StqS9jdd8ZLP6c/9v4/sWvnNfjt7/di88hW7D/wF/zw1huw588Hcd76DWc4KgA2lctXrDx06qeWnglE29valaPb8fSePwEA9j75B1w5ur1d09OF7mwbWtrXjypnHP/w33B3LFna17ZtsPXQrTDkvPbY63aM4Ud3fg/bd4zNx+y00tlqBmDkim3YPHIVtnx3tGOYlgZuNy+9vYuxYeO3oKr48c9+DgAYvugS9PYubss+TtPeLTB/e/mvR3HZmtdUpGKEEWJsTg0jaUKpGDTth60e+479feadT/XrxrbaBzA71jhqjLBENaVUAjEJWhKahJiS9vzzz7TEblH849C+/3w8c/G/AGQCZQAZgUxh6R6ZPPmMTHompASQ3ZGp0faf/cAzj498IQwERCBR6B5IhAdJ94hERIB0WKRmpuFAJHcEhc6IZIEQFYcxgRakOCISwsNUHeYJgYC0UaZqYnriyC/3fEJ3Dw+Dw8ONCGh4MNwV7vXwcJh5BAxuFhbuFk43dwujh7mZw8y9cg8Lg1XuZobKHWWULYn4Wr4K8n+Ghn5kMrtxIwAAAABJRU5ErkJggg=='

manygears = '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'

peakzoomin = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAUjSURBVFiF7Zd/TFVlGMc/77ncX8DlAldEcSIhOgpNFgMzSMPSlf2hOWtl6VybrabOleaamrr8w00lrYXLprmiOU1DRZdzTMHJvagYSZNS8xcKQwH54eVyf3HP6Y9zSX7ci9fdXGv5/eds7/M87/s5z/ue5zwvPNZ/UJFA4r8N0SM9cBk4Bkx4RGtIwHKgEoh9kPNXgAJ0AT8Dc/4hCB2wGDgNyMCRUIJMwA0/kAKcB6aGCfIecKnXnHYgI9Tgrf6ge8D0MEFA3Zp5qNlWgJ8COYkgwYmoezoHKAKWACd6jFlZWZEvvjp74pjUcelmS6wZRRi7Pe7Olo72O79WlF/Ytauwuvdku6FwBcyvh2XAKtRMHQsVBuB1YB8wCvXsLAFOrF5XMCMvf9q0sU+Ojw4U5Ov2ibOVJ2/ZKsr3F25ZXwskJsHlpRCTCzF5MBfYHihWMwjM7/5nh/8titasLzDNX7g0LyFxmC5YkCRJjBz1RMzY9IycCK3eeO7MqZ0fQsdUGCrB9zsDZCQUmN5q2/j5Du3cdxelS5LUx9B949ow97GSWSLK1CzFxXf2jEdGRYnMZ3JGNzU27JlXW5MNDAcOfAvXg75IKCSfrN700mtvLhgf0GjvMCler0G+cTW1vykqOpolK9bmOAzGnnqSNNg6ocBoJuVNeVkToVECGWWn0wggu52RgezJyak696QpFgABlrBgFnzwUXZGZpY5mF1xqTCK22MM5qOfkBUpAwrEhQWT8+zzaf3PSR8Yt0uF8LoDw8iySEpOiWi1WCBcmBiTKWhWAITXYwDA4wm4TbhdWgDJHBc+jIaIoJ8xgOJ2G4Uk+RRZ1uDsGuCruN1aAKHVhw/j9Djsg9llr8eIMbIdwGe/NzA7HhXG12W/F/aZaWpsaBjMLrxegxRjvgugOBwDzo3P7dI5HHZ0Lc110sPA2OC50/B077HSsiPVLU13Akd3OfSKokiSOa4VQOnqHJAZ4fFo2y7UEON0XnuozChQ7IPNvceOl5Tcqa4+80ugYKXTbgSQYuPahRAy/prTW16nU+e1lgPcJFSYCkgGEgWk9Xeylh4tvvLnJUf/cV9HuwkAc5xd0WpdPTWnt84f+rE5vr4OocIYbBC0Hv0NIyAbQIHkMujzRy4q+rrpyIE9O27VXevuA9PYkCR0eocmYWiHpNN3KS61CsstzTGug3tnHd66IWbVlxue8oIswy0AeZDsSH4AISDXP6bRQaUVhtogrQwMViio2rxu8dszclN+O7hXp7S3RQHId5tHSJYh6gHX6Z141MLX1VBnubL/hyEZG9foshVFLANvE7QCfAMTg8EIK3wBZAKTFTgg4DCwthWifRCfAI5DEF0MbYVQZxQiszU9A21ufmNCyujh5twXyrQZE666jh+d3HKxdlhr8+0qTfHunPjbjaaeRbbDzb1wdR/kLwJXEazUQi2wEIgQcFIBi7DCRWCsgBn1UPoG+KwwfQscdoFjONSXw8htEBul/v63KTATGNeu1XJy+iuzHWMyXFl7vps7qun2YoMsI6BYhlIBbwGTgf25UGWBDa0gfQzMVFvQnq+vDYjlFKRWQH6/jBlRG+hO4ApgssHyyvtbSRlEKP06RRukWWFVhdrUcw60FZCXo0KVqEcGJRpqzoHWBlMq4DMbjLCp15eAWsn9Tt4LnAVGBnMOQQnAJqDGP6cMvBNKoMT9q8ofQAEPqA8PIQNqBq4DVaEEvO+H+RT1hvkoJKFm5oHzpxBiO/pY/0v9BZIExkfXTYIxAAAAAElFTkSuQmCC'

calibcurve = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJ6SURBVFiF7ZRPSBRRHMe/vzfjSoUddndmRcVLpu7OOhIGkccQ6hREkAfpEAQdOtSha9cusgdPXRLskhGBhXawIPqDERHmuM6ulZciImdcESPSdef9uuTaKqXbzu5e9gPv8nvv934f3p8fUKNGjTLDACX1eG+6uTNUqZribxOzmjEK5oGNrHic1ONm1WRmdOMkGNku176sgPoly9vT4Y6mqsgIxiVFIAEAhmsvEMurKql33qKnrqIyNowAmNvjjm1txsyl+edEPFGvrQ1WVEaGqReCX22Px51UgsFNST16vmIyIO4D05MdYYD3edmLzOLKnG50V0SGmY9JmdtxMgBweHlhFUKck4zhpB6PlEOogFktltptjRUyTiS12Mv5cEeDn7ULTma6sU0DeHG3pO6M/ZSJE1lSx62IeaAsMgoHTIDm9pJoOukHAEZIemMfg20HfZchjw4xeGGvyaZrjxDJmz+VwKQfTbFQhtBKhE/FbNDlpMcE0TWVlAkrbJz2TUYyWlnic7GbxB17SlmnPiIesDTjlhUx9ZJliNC6EfCKlgEAY9VeNt1UPwkeJ7nxaDZsXC/2t23rMxw6+vXD0v/IbGIuph5m3MhxgJ0sKc8sLXbDCpote8mlvAYgklr0nemmfeuu9wAlqsXOMnABjDoG35W5+vtHVmZW/ikzE2pvVoQ63OWmTvkl8ye2ZjTmIPsJ4gwgmSCmJOONzNW92JRT81aq2iIlfSmHCAAYrv0NwBCAoflwR8OaEL0E7hH16w6A1wUy8EgXtHv39YPOpfffAUz+HnnyD1gQa8xU0uMtla3fRAiykJkqumxdk+flRtnb/6OaMjVq1PCLX3bU6YEOTTcqAAAAAElFTkSuQmCC'

peakzoomout = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAT4SURBVFiF7ZdpbFRVFMd/d9686c60HSgIUrGlBQRKQxcqlJaqGFAWo4QIKhKNGCFoJIYQJdGU+EVJDBAMJizGaHAB1EJArVIKM2VpFYyyCBRabEt3WtrpbJ13/fBaHOnM0DIh8UP/X15yzzvn/HLPfeeeB4MaVOgaC+Te4xzDgYj+vPgAcBYouEcgI4E/gLz+OvgCGYFNIQIs6XkOB84ACwYaoBdoJ9AAjL5LkHDgIrD8TiDGIEESgN+BZYACrAVWA2RkZETOnr8oOzU1bVxMbGys7JaR3m5XR1v7zYaKk4f/3LFty2mfOG8AKUbY2Q2bgQOBEoogMGuAxUAWYABqgXHvbdiUn5P/6OzU8ROj/Tl5u72i/NTRa7bSkr1bP9pwDqgApvYka5XwPfDSQGF67UuBFcDMCQ+lHS76+bcqxajIO/jR3NSorVn1vMd6pHhlJHTngGqBhd9AUSAf5U5B0U/+p7PnLBitqKa0Rc++WOVr7K66MsL1Y9FTIiqmyRAX39m7HhkVJRTFOO9aVWX5lsZ61wJIyIHtO+FqoETBzswtrVv/4WMvr3wTxaiU9jF2tMdIjydcq6pM4sHk676mJxcu/ik9c5rTnTspGacD9M86oAz9YFGm5c6cE6g0msMRAaC5HJF9HBVFS0xMMrkezrcACLCEBLP8tdVZk9OzzIHs0qnDSJc7YEc1pU2N9AIS4kKCycyYmWIwBH5Nupw6hMflH0bTxMjEMcZWiwVChYmJNscGswuPOxwAt7tPmQBwOVUhBMIcFzqMwaiowezS5YoQBoNXapqCo8vkx64CCNUUOozDae8IZtc87ggiItsAvB03++6OW4fR7J03Qz4zTTW1dcHswuMJNwwxtwBIu73PufG6nKbOzg5MLU3VhoHAlMH0E5Dmu1Z89MCvzY0N/r277GFSSoPBHNcKILs6++yMcLvV1rNnMDscVwa0MxL2eWGj79qRgwfrT58+VeHPWXZ2RAAYYuPahBAaPT3HVx6Hw+S1lQJco78wVkgEhgt90vuPjhws+u7ypb/st69729tiADDHdUhVdfb2nF6tWfVC5tEvd7XH11QjdJjwsiAT3q3rQOi3MxISSyC6AG7dM7t3b29AVb7Kys79ODl1fOfk9MwLAN7rtSOFKcyuDEtoN5jCuqRT78Jac9MQt/XwIxcqTtgPXL08by7IWeDIATR9dxwBd0aCEDCjZ00xwXEbJJTB2CwYXQAn93z2yaHC9a9P6Lp4rk623YgC0FqaRhksQ2sBMIU5cOuNr6u22nJpz+dDX/27qlKAsh/EOih8H9gaZL4WNn2kTAfyJHwrYD/wbjNEb4P4cqC5Z9SYBS2FQljaJkxCmVFwfdiY5PvM0/NL1IlTKp2/HMprvnh+RFtjfbnY+0V2fH1dDMA64JieS+aASIeaZbBRwnngFcAooFSCRdjgApAq4IkaKF4MXhs87oKvfwD7LjA3QdQQ4GOoSYJNEhYCk9pVFevc+U87J091TNmxben9jXWrwzUNAfs0KBawxAZ5b4PWDcezIPsDUHs6YxfQ+/XdAGI5BklWP38CUi/hCsAG2FLgzPF/S0kJGOVtw1kZjLXBO1aIAagA1Qq5EXoMNQU2p0D1XsirALUM8q1QWAajyuCtQOWjB+QYeuDn9CrdtXznprXAIfRBvV/yBbkXWsttzTWYngH8DtyDGtT/Sf8AJr270nwR+eUAAAAASUVORK5CYII='

renewpos = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMaSURBVFiF7dZbaBxVHMfxz0ySTU0vVGpo02JLGqNUIUqTWHwoEpFGQwVzaxAF6UPrBVFBUKHgrSqtUcEXFSuCxTyYbAxFS8EEFR8KUuoFL7XEoK0gvZAWk9Zstbvjw8zCEpTsllZf9gvD7Pn99/zO/P/nzDlDmTJlLg4Vl9h/MVI4d4nHmZNHkUHHhRrUJPc6VM2Kzcfqf9BrseRf/H7H0mIHDwvu7+A4tmAjvsV1SfxB7EQzPkejeIrfRifuxEezvFdhOvEsiso0jTna9pP9lYk+AviQowGvrODQD9xxF/0BdZ+RCXljOT99Tef1ZOs5Ms7xNTyRNz5M6zFm2niugte6mJzzYSKuQvMiWpr4M8neSpZXkZlhYwsnQtYGZOaxqIqZes6cZnyCvsPULONgyMm88UmuCPkZZ2bIFVudPGNoT37XYBzXYAR3J3oqTtoaPFDQd32iFzIqnu6SCXAKL6IHw+hLYrdiL27D6wX6CB5P4i9hQ6Ivxj3i1/nJpF0SDeKSVouzvmxWfEGipwq0VDLQtbP0BeK3Ln/VKJEt4rL+r4S4GlfigHiNlCHZU/5r0jRFdIXxbr4K27o5Es7V8WIzGC+F/ojt3WyLOIEdUFmsSZpHUB+yN2JdxPxpnt1MZoDL5/FwjkxAdQ07OziXpgXtAX9FnO5hV8A6zGwim1ivjpLduejKREygK2C8m+exYiGP7WFhNZ9EvN8bn191f3D/cHzYvptjRxf9aIVedn9HFwzThpsq2F5SZQLqAsY6+SVpH4poOM9DONDDj4l+NIoP2BSWhnyZZjTgrbzXM+QGaY54NWR93rOUNdMScTDfyLEW+9GErwoqeEPAF0FcsZURT4XUBuzL/yfNvSFbQ9rP81syncU/TBBnMglD3B6yLMd7+B71MMiNqJtiIMvTWZb0sifLyxGjIzQM8XGS2FhER8AHAceSMeZmkFTIqYCtaIyYyvHmJmY+pXKS+5AKODvF7s1khtgQxN89lZiuYeAsN4fcUugdMdHDrmKLYpjWNN8U3eECmXOaRmjI8QJq0/H6KFOmTJlS+Bvo9dDUHCc1ewAAAABJRU5ErkJggg=='

newpos = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGNSURBVFiF7dTPi49RFMfxV2b8+qaUIb+SMoPIz0IjjRSJNKJElhYoS3+ASbLwf7Dzo2xpJtYzNVNSNJLEwoKyICaxOOfR0+P5NguNLO67bj3nc8+959xzz30oFAqFQqFQsQDbcXQ2xw62znEy23AHo5XQ28VxCHvxvKZ10I/PWIaVeIKvOb8UB/ENY5hJfSADj+MLPqb+LMf7KsC8LsnswURD68cjXMN87MLDnNuXp3yN9biX+gVcwiQu4mRjz90tcRCVOJJjDOdrdk/6vMGG/O7gp6jINHamvhA/sDj3uYth9GFzI+YrbKyM+jUdygVEaavNZ/AYK7AkTy/tT6JiHUylvlpc5XdRmSu4gU2iWV+kX1+O6bbKVCzHgxb9mLimilu4ji21BGEEN3FK9FDFbRyv2SdEz/2mx58MiV562tDPidOtxVnRqCP4gDU4LHqtN5Nch9OieffjXSYk9aviIbzFy5Y8wAHsaNHv40y3Rf+SVeJJzvqD+hu6Pe0mg7iMRXOYS6FQKBQK/x2/AAD3QcpxtOBdAAAAAElFTkSuQmCC'

delpos = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAI8SURBVFiF7dVLiM1hGMfxz5mR+2JmMTNCJLcikw65JSwMZaGUGWUhpclCmo3FpNQs1CihUZJbOIXmPQrNzobGZcEYUi65hUQTzSSXxriMxf8spmPOOAdh8f/u3svze37v8z69LzExMTEx/yGBqkDxH9IqDlQNtKdooGDU4+ppKn/HSCb+Kup/+XC9JNKsC7xK05RiRCHxgWHNNAQ6AnUjGIUlmNjf/pyVgQS91aS+MLOX0qHcTrMsHyPNLEJ7gllI1tD0IZo7h8k58g3IaEzAHSyoZ1wyurpr2FQTrU/BTTyCBspLOFrGnDdsqeN4Vr7OTMzrfA7Vl114ixokcauClWl2pPhYS3oIk3AJi1OsPcqnfZyZwkJcyNKbgGe5kg36iZk2jEPIjM92sLya1mm0NzC+isNHeFgVVeBzI90PuIx32JylNxs3ciUbsGdE1WjrMy7HS6y8SyiLeqBzA+sH8+0zyQfUYj4uYk+W3qzfMdM3uAxLcQw9iyh/TetXynbwopTnPTw5FV3DasxARZbeAlF/FUwCXWjENpzCvBaG7+fgMbo30lxEE+bCKlpSvN/OlRJ2Y3pGazS2ipp2L8YWamYqHvadaGZF4GkghKhSP3CC0sCBwIvAqkKT5mIbrqP4JBWBVOBxIe9M4F6gJTAmn5hcPTMR94vZ2ciWQdxK0NVNZTXn8xFeQyuSvVHPtQfqGn7+yPZP5g85j5FF1K7mdj4m+uM0ld84hPdYVsPXgkX+9q8dExMTE/Ov+A5gVZxagQ9qAAAAAABJRU5ErkJggg=='

plist = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOGSURBVFiF1Zc7bCNVFIa/My8ntmMzmw1hZYFMRAUND0UhEpiO4AaJAhRRbhdHS9B22yDR0IUOBdFtkS0WaYsgIBQpIkVISKHaUKBIkXBFUNg8bDm253EobGfHSTayV+Ns+Ks7V3fufPPfM2fOgSsk6WVROp0em56evgXooEDK5fI9q5eF2Ww2t7CwcHN8fDwYFMz8/PyfxqA2fxr15ExUqvGelMjjSOkLZnFx8bm1tbVknDCu64bLy8t/9w0zOTlZz2QyYZwwqVTqZL++YAqFQr1QKNTjhInqSgXw/wNmA+78Ch9fCRjgM4Xbl0bCBQEscA3oCtbt7W17d3fXjBPAtm2dmppqPBFmA0YAB3g+Or+yspK69DzTdgUg+QukbrYvZmdnqzMzM7U4YSzLOknp58IYMNrJRBkY68zncjk/l8vFyXL6ueeq4wxhBGbQOhcmgNHOWJ81TCRmMOD6M4Wh5UwFaF6mM10BvAEPBPYFDhX+BRIacWZ1dTW5tbXlxAmQSqV0bm7usAvmPpgCH9DKLz8BjxQsI+LMzs6Ovbm5ORQnTDabPVtCvAQTAQwDKLwH/CZgRp0plUqHpVLpEFUhCEwsy48T7AQmhNceD8kAj9rXL565q1ZLa6XiSiJRw3X3nvrpqqIHB9fFcepdMNqCqQDbwJvAQ4UbAlNz+/sfEoYm+/suicQxvm8DqOclCAJTVFuFrGkGGoaGeJ5DZ65WG8E0fYaGaup5jgSBRRBYGoYmYWiiKtpoDH9ULn9ubcAXBryt8CrwB/C9wl8efJOAWwr5lz3vS+PgQNV1hUaj9W+yrCa+78je3g1V7foqz5TsnpegXk8holhWUz0vISKhqgrJ5JE4TmPY91+xpFUqjLY3uf0OPAC+BrgPX+XghWORt1zTfANwEFGGhytGKlVRz3PwfZtabQTL8sS2G+o4DQlDA9+31XEaYhiB1utJEVGx7aYmEnWpVjM4TgMRFcvyENF7ExN3rBBmzFY+ef8Ifoy+0CcQAPO5sbHXvxsZ+ZlMxsG2m2LbTW0dyzFwLOn0UeeeaIvaGYttH3Y51l5/up213oXf2+OHp93tst4wgm/v3jXX19evXbSuX7muGy4tLf0DfXYH+Xzeq1arPfXnvSqdTl9cQjxJxWKxViwWY61norpS3UHPzoRhSLPZjPWITqunzV3Xzebz+U8HCVKpVH4Y5P596z+4Azci5zvJHQAAAABJRU5ErkJggg=='

library = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJjSURBVFiF7ZffS1NhGMe/7/tunJ3t7Jc7GYayRWyl7GpObRChUJBodFXUVRcTdqES2k1Qd93kvVB30b8QdREFhgVL1Cg2KhoNzCzM1Xa26Rx6ztvNjDPhNK1kN+cD78V5z/Pj85yr8wAme4BzbmlmP6J/KJfLZzjXngKoAigCyNXOGsC/ATRFqbpot7tThJDqH5oI88kXJ5PXrt/ukGU3s9kcTBDEYotXOD81pQFwARAIoWclSXq2k6c3k0cTicnpe3cBQABwqHZ03hyaRqEoBS2dSuXfp1Nrc3OvVtPvPsyHuzp7+/r6WjvD4VZFKXgOt7XTaC6H2MrK7woPQ6E66dFEYhLAm9rAdTLBwtrqKaNp9TDGqD/g9/kDft+54eETrxcXuiPdUWkvuXpq/YI7MlT/0mFhG/st+C/s7keNAv8XHMCsKO4p9sBkOOcgnOOJ14svI3F8JqRhzoF+mYqmYfPSRVwYG8PLnmhzZR57POgfHwcAdE1M4G2l0hwZmyhi6NZNWK1WAEAwEsHxK5ebI+OQJPQODtbdDcXjzZH5G0wZI0wZI0wZI0wZI0wZI0wZI0wZI+o2umwms129P72gblRUUi5ucVXloIzA6bJaWmSBtAdcLHDUQ450eAljhj+1XFU5/7qc15ayeW15qbT9M1dFqbgFTeWEMcIll5XZRZbNZNr0efqCMTfFo6sOkmk0gc3pZsH+Aeex0wOu1p6Y/KO0vulzOmzf55O5T7MzxczzmdJmSVEb1XmwzoOKhmEAyd0ysgDcYRT73rdFt/djRcmHGkfWo2rYrgI3UFviTEz2yy9dKcogs0F3xwAAAABJRU5ErkJggg=='

fspectrum = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOmSURBVFiF7ddPaBxlGMfx7zszu9lkk91kkza1TUhiSBODRSmWRtCq4KVSQkvBPzcRLwX1qKAIVtCD1JsXr16siKeUHiL1D/bgn7QKkoTGtknTNInZ7GY32f/zvu/jYaxWkm3Tw5pC87sNPDCfeZ5n3mHUm8ecj/Z1O0nugXi9u5zMkcfUn1sNAXC2GnBrtjHVso2plvsPM/O+fmHqDf3WPYHxV9itUzKol4lsOQYtEYDCZWmpKSZ5VvZOvux/sjwiA9VqrKYeoLxga4sx83aH+DSt/WwOVqsRHYzHT9FcU0wlSxzAFG5zo78xNkdjTTEmLzEAW5R4tZqbYzJFidYUYwsEmAobYkwFB0sIwJaoLUZKAUbKG2MqKSKAArBlGmqKsUWJ46DFEiourL+ZXfn3bLHlGnfGVIi5jdwA8K+t3xs/I/UAyiNvK7XcGUGJT1OoWc0CVJJ2HUbngs44DSzj38WYUmelL/uDdG7WUrpOFMENtavrAP7y+tdb5W0EwG1QKfy7GFPyS/168ivz4qYxc8FYwh3MozA6u36JdSHojNdIyupNYvLjtNoKcZ2T9s1iKjdsK0B9l5NUIdbM2vqd0fngjPFiKiWWkM4SviNm7aLpAZASrZU7fF3/eYBJGXQipGMH1KITIWMLQWfWfpOdUyf899Kj0mtL1APiJkgD+EvV9ybACKp4RfYCiOBMv+O/W5gmlhuTdn+N0PRJ/dLSafNofoJE+mt5MD9BIuiMPBzaqcYBvIjK2mKAKYzbTr1KT3rUHC7PyoAKkw21OVmA0kJwYm8Ur2vEHJn6QhI6TX94l7oQ7Ve/rv5kj1476X8oPo3KpSyGiF5hT+Z7v0mv0g3gxZg2OTpiQ+oMgIqQ9ZMyMPOBPl6akmcBKgtyACAU50pkQC0CLH2uX81fdM7XdTCf/VGeVoIT7lSXTEEavfqU9OkirTuOOacSw+64G8Z6CVaSI/Y1N8qiE1VLYgj5Sdnn1JOM7XdOF6/a/SZHh+NRiD/jBp1pIVma5VBhQobDD6ixum41Xrxkh3SaftWg0o19ZByPglmla/UX28UFKthgf/xlGbCaBvXZsHfq8Trrtx11J//TM0GhkJuXcx+bw9GHnMstz6k/AGwZ1wljb63JjUl7+htzcPcr3qjXRsmWcVPnpDeyh5WmR1QyfU56Mt+ZQ81Puuebn1Iz6VHpy/1uBtuPe9+mzpgh9ekJ7+3nn1Bzt1vU/yv339/BZrONqZZtTLX8BTPLpTVHkBS5AAAAAElFTkSuQmCC'

delcal = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALTSURBVFiF7dVfiFVVFMfxz73jXLRRiMLRYcqiyahMM6+YMWJ/EBRSLMe5TYZIzhikoQ9BvURED1H0xyEysz8TZYzecydIDR8aqQezB8tmCskUSmSwwigUymGwmdPD2dmdyx3oj9TL+b6cvTdrr/Vbe619NikpKSkpKaOJmPBfxHmXq0o8W2Jr+Xq2wq47or/Iuj1cdCEFxGSKLI7YM8xnyA3zXLlNpnzyBNnruCPDA1iE0gidbRwZI0YWMzAF+8JaDYbRhFm72DfEvdiI2piuHNvu5vRfzmQnTSWejvgxordEa5QEKmcqPsaWML8Vn2D81ex+iO8izkT0FlkWj06+FX14vOrJVONNxk+kEPMw6mJeq+X1FfwUTN7Bh+iaQe5BVtTTfo7mLzk2j+UtnBjD/UfYjN1jibkTSzGAmZKS1aNjIbULaJ1JfU1Swufb2N7MpqWsvIT2cZycxDNrWDjICL7ATTiDDRWxvsdcnKymdD4O+rMcvZiDx8Im6GjkrSKPRpx6g5GIX4v05JMT+MPuMG4P4wyOI18WqzGIOU/lbdqE7ZIGhMX4HK/iZqyr5b7bGMmw7BzZE5zOcAgLrqdhMz+jDldgf/AT4zfkymLlJfvOM65CzBT8ULE2D9tWcf9y7jpLc5aGDE+t5eIhrsX6VayezAuNHHqFvi4GDiYC4IYg5NMyv3NDomOK6UZ72DQdU5cwew6X38iBAfq3cPZ40syHJc3bj4ndSYmP5WgZ5OUO5m/g6Nfs7SQ/SFs4nSyuxEr0SH60g1Rv4Fn1zH6EadMoYMJX7N/Be0fZG7KcjFPhS1L7hjA+grrLGFjC+jyFS7kmw9sxnYVk3y1l8b6R9NNoMTtpqmFjzGociHmpwAeZpOb/mB6mx7THdKAv5sUC71f6HSUmvBW/ZNnawrf/RkA1djFpiDXCFY958h52XOg4f4vwTi0qsvZ/FZKSkpKSEvgd+j3BjicFZ3EAAAAASUVORK5CYII='

renewcal = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAP/SURBVFiF7dZtbJ5jFAfw330/7To6nWFs3WzTzjbiZXQLE8Ma85bQrN2akCF8Id6WhQSRIJsgCAki+MCHyUz3dIxkBNGEYDZbsrGxeZ91XpbKdKw6fZ7bh+va9rS6IOOT/r9cb/c553+fc65zLgYwgAH8O8gdgOxpuByfYhdGoxvH4jJ04Yf9yCbx+50HYL8XGvAbyuN6JeoimW5M3o/ceCzGj39lIMEYHNpn/xDU6O3JaVhVsj44jgfh10iyGoP7sTMLr/bdTEvmE9GC6XgAN0aFT2M2zsLqEkKnYC0GYQnei/snoxPX4xK8jxl97J6INX3JlOWZ1M2Mxdx5Jk/VUrmezq1ccDJDNjGknvIC6RKOn8Nt5fS8zuxhbJnK/FVU7OD387j1A6Z18u1MKlCxmi+38+hFPJdShVwbTdWsm8DxzWzcS6bIuA4urKGilpEYeRJOYutuJvzCuM1c2UPFGLoGhTCq5JgatiSMLTCumh9ThhWoGUV7yjCo4NAqkj1rIYYjjuKNIlk/IXQBPixZl2OowPrcuHcFno/zg/BLDJEoe3qcr7MveXPxrL5E92hs749EWRzbhJtxMz4XkvUZIXGnCt44W0jsc3C+kG+ThPifKtyi9ZFAA06I4zN4K9o5DregKOTg26Vkkj7zWqFmbIt7QzAKX0QF4/E9jojnOyNh2C3UlcqooxZfC/VmD0YKXoUCvunPQwP4T7CCirZ9+bcXbZStCFf8b+FPCv4p8ly7i0e7QjJ/2cr9eKlIZQetGVdjWT9yV2aMSTg6ob2RBQdMJsdrBXY28lXceq+LjXPpzFNI+6m0ee5AxxwWtpBL+a6Vlf2SaQ1dt6bIwTkWNfJJC5NTzs6oStnRxGPQw4SEtUtJlzIfR8zl5RaGI8uYkg/eGZJj4Sx2ZNSnPB7NDUdVxq60HyILMiY2cU+OtiKPLKc65dkij89hYZHblnEkpNQlrGmmkIRrfzqUhQ6+vcjq2dyV0FngIdjAzCZejJ69N+OVObzTyzMtjMiYV2RE/OtVZdzUwLbFzBxMfSvHZFQN4yfIqMt4IaoYmcWwZExJWN7Mlni2QSic7g41y1IWZqQ/hUj06tpyoUJ+3RwLVTM/N7I5zw2DeLCH9gIfYcMMeqLYlJK8qEv2kalT0mIyzsh4N/700DxPJLQ3cdVhTF1BRS8yZWzCqOUcBXnOb2Us7sMju9mack0SvtMa2kZ1I189RXnG9IzNUd2pxfCusTQ8S+p383CeS1PaMj7O6FjGvJQbL6K7tB3sCdW0hIuxNce7jazLM1d4p6xNWVPkuoS3MiYmHI43BWI1+KzAopRmdGVMTugs58kGdrZyu9CEe5ltCm+jAQxgAAP4/+AP10QgYZI/OEoAAAAASUVORK5CYII='

neutrons = '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'

calendar = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOkSURBVFiF7ZdLbBtVFIbPnZfH8Xg8GKeJE0KEE8eNgbQhLXTR8BBKqUoKm3TRLosoiB2KhFRAFaISEkgskGDTHaggHgsvWCCEkJrSkiGNiaKgNpJLaJpGxk5jezwvz/OySJ04sQdKRRsW/pZzz/z3P3f+e2cGvf9UTN3nu8+GbSZjlSkq5uPthynB/vJGlvmlWKJXTBOFGQa/0N5qvhhtM2tvSJck6uxS1ndDrxB9gRbn1diDlS4/6wIA5A2T+Go5y6RLZUqyLBRlWfdYZ9TYH9lo9JqmExMrBfqKopAly0bvJfu0MENjAAAKEBAAAEt6hRCLJfpgW6v5ZqJHfyYStl6bvcx9kFnwV4WmihL13MVpvjfQ4pza2atZGMP+82Iob5gEAMCsJJMLqk4e6Wg33k706P3BgDMqpvlUNsdUNS6sFunJYolyMcCn15dZ2bFRbbPomwO7pVF2h7V12V6fmw/MlCTq3PATEgDA0enZoIMxfL13t1ytefTHC8Kxrqhxsq9Hb7T0h8V0MOrz4TODjyi11+ckhXx84mdhfmS42O33uwAAv1YKNNFIpGTa6PvcCj3SFll/TPOyQg4J/KZsPSaE7MuySjbSuKpo5FRR2qTxT9SZyRsmcVhM84NCyD4Zj613XLZsxJEUrq3lKBKXLAtt1ZiXVXJUTAdPdHdVjnS035mZOUkhh8+LoacjYevsngGFQBvzdLCsmzOMTfV5wyQ62bUAV/khv0ofuHiJfyP+kH46Gddu18gmM6lsjjk0Oc2/m4yrp5NxbWu7B9si5rd/5hkbry1OwbTQxM0C/Xx763rePvp9kX155jfu8z275OPdDxj/xgjArQBHKz785E9ToXigxUkEOac6GGFo95NdSRUAoGw56NDkJR4Bgn1hwfout8IMCrz92dCAggDgi6Ws76WZOW5I4O3OW6EEABjgOfutxFrAp4oS9eHVa/6yZaFzNwv0yI77TT9JwalEj2YwJoHOPNsv7yVCzoKi1+WHJhD08xvmXBfgiqyQy7pB9HItTozbmHTVMNGybtRpcBSFq3WSZaFFtVJXE+P87qKrkOjjd165Di7eOr4tIIzxxHabqNLwnNkumma8+F+ZQWNjY9m/K9A0jcD4v91tLMu6JFn/SmvuJi+aZrxomvGCSqVSgtcgy7IuTdP37C1KZTIZ9l5MpKqNv5VraZ4zXjTNeNE04wUaHx//424IEwSB/TW/LLdlRhTF6bth5k5onjNe/AUbV4G8RgqkcAAAAABJRU5ErkJggg=='

magnineutron = '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'

sparadrap = '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'

battery = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEiSURBVFiF7ZW/SsUwFIe/k5v0j15QNycvvoergoMgvoXP4ks4+hg6+gJugsgVHUVt06a9xqGtdHEoCOmQDzL8zjnh/EhOCEQikUgkDAKkwDGgA/R/B27HZnZPltxd7suqSoUq6VeKt6miTsCmQm0UNqXPCbURqkEnwsN1+fL52FYTzbwCZ4PQAAcGdbSUnSIXilwoMqHMxRe5osi6WJl18a8twWbi+5quNhPMnjwBxUQzzVioiZv/GwUcAitAQszJmAy4AUrgPPTJQDe3G0DmYOaXaOYvZmUm9GvywBqoARfajAUuBjG/a7q31Fdvfu20p0kEtwBnhEZ/0xrxToPTQqO7eNvnnYbWdPX2eaOA7Yn9P8ZCgAVwygx+7UgkEomE4gdsRValJ8R4/AAAAABJRU5ErkJggg=='

question = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJNSURBVFiF7de7axRRFMfxz83DJGpUghAfiNgpIig2gqIIFr4a81gEbRRE/QMEO0EEOxtFxEIFQ4q4CUZELcQ0NhY+QMVCSMAHFhJfEDGJzrXYFTeC2dmdtZH8mpl7uL+z3733zLkzzGhGlSlUY+phXhObAxsCSzA3kmAEjxPu5vjwT2H6WYwTkf2Ygx94h9HIokB7cer3QD5wsoMXafPXVQCyK/IschiPAh2jtHSxrIu13SxKWIkeNET2JjzKcyjtb6RamQG2J9xAIy52ciQQ/zY/z2kcLw4j9nbRlxlmkNYJXha3INbTtodP03lu0TTGcLGe4N1sVuxkfDpf2W2apLukFowVCnVa7WS8jlslocVf2V3Ol6ZmVpfch6ZC8abRcOkgsKoWMG/+GG9LCdNSOkhYkBlmnCt+/8skMJCGJE5dUYFX5TypnqY+5tezJTDcwbNy83tZOIvXaP4VS1iX40lmmEoUCf1cQ2dJ7E43O8p5Uze9NLpM8wBXS0EwUsfBNP6awfSxvpWHkX0l4duBjZ2FI6OsMm9TJAxwLHJKoUNP4GbgXCdDleTKDJPnPI5iDGcTzuR4X02uTDD9bI3cw5eETTmeZsmXqWYS9kDkQlaQzDCBpcVrqkb4T2EwCwJva8CiIYs58CDSPMbHWsD8PxqiYZDWWuWrumaucWCUj5N8ztM7lHHLob4a0yDtSaG/tCj0qjXfGOkrcyqXU1UrM1l4t238I7w8C0jVMAnPTf0emgxczwpT9XEwSPsEx+po+8GlHPezwsxoRpXqJ0Q1jdzvESQGAAAAAElFTkSuQmCC'

renewirr = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAPkSURBVFiF7dZbiJVVFAfw3/5mNI8zamqOmmaailpJ5ljaQ5IFanZRcbxmYVfKxKcICkkpIioleuhiiA+RpGdGYrrQhbIbhJCWYqWMZmYSmWLe73O+HvZ38sxRehroofnDB/uy9t7/b63/XmvThja0oXVQUdbvhQLOtOIZNZiOy9BUMt4B3XCsOJCULXwTo1uRCPHnFqJfydid2ILH/m1hx5J2e1TiYlSXzfd2zqvVuCKzLUWl6I1KbMCYsvlGzLwQiYCV2JX1H0EzlmATVqAeu7OxPzEBr+EBzM3sLsrWT8a7uA/P4ihyZWfuxKAW7BsYWmDsNzTv4cAMHvqDzh9wfA77c7wK6xh3gv2TOIFlB7lxG33HZD+whsG38cRxcl/x4O281IEeu6neyOGpLEyoQvtj5NZx6a1cPpsd/5Ap0B+1nRk1PAq39iz9ruavHMOLhl0Z0Y99IYZENe26062JO47R3Dl+HXYwug+7O8aDq44xuCf7E7oW99pLrxx7kxiRC+JTTMzaT2XuLcV3uK6kv0EUItRlYYHn8EKJ3RtYULbXIiwtJ1AU3RSMFUW1F3djvRjnk6ImRmAIvs3WdMFIXCKKsxNuwNvIi9c4lxE+WHLeLZiX7TMAvxTJFN00IGufFUNVFNtvopD7Z/3T2JO1q8Tb8nNmMwi/4lQ21xfbM5tUFH+lllf8IA6Ue6gN/yny55LnBVGeNTXwMA7VRSG2ChrpeZZ3RE3NbqTTaeaHmCSHpqyZTuN5ZApsrYiibDVMZm8DW9IoaGd4P+HeaexsYFTg6zzdWpBZy7wCI5t5sp7xGJ/wUYGJIV7xfSkDA6vwaEo+5cckXt/2KVUpz8ygeXlMivPRI8R0MSKwupFOZ7jqFIchMDDlVDWFFlW7mS2BWTM4eoDPQ6w7w9CY8GXK1sD0lFzKexU0JXzSjpV1vBgYF7Kq3523Us7UsSiwJmVkwveTOfIDNXPYn6dLyuLA45M41cIzgd4pG6GGqmbCFl5ZEp8B6rkn8FkdXxTX5Bl1mhH1DEoZUsnvaxmZUlvHLDhL14RdU7Pkt4RCnuqEBiydFot0y/dMQm3IyBS4FpuKRDKytUWyWVinJqxMOJnyYaByaiyco7A5xGSnglol6/JcmbAi5ek6VtZz03lkMC7NXmMFbg4tX2bF+e3FTsrilFXNbE5YUGK/DcPytM/To8D9gabltKvn+YTXQ6xlfRpYFrgmIx3RwJQQDwgzY3ofhkN30bSaI2uZEzgc4gHrYTo7AxMCNQVWB/rPJDeNj2dwKDA3UBX4KdCxIzsC14dYZnoGegUKBV6uj6WmDW1oQxv+P/gbj24ah5XnsIQAAAAASUVORK5CYII='

delirr = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALSSURBVFiF7dVfaJV1HMfx1zlHd47VRiERId2smrYUw38r2jDbYEWBOPEoqRW5FSF5kRJ0kWgXRRQx1JorKymw7cwTDLuISJBg1LJyCdWM0eomI4ykP+b+nD1dPM/gOYcFJaNunvfN8/x+v++fD9/f98uPhISEhISEcgrM+y/yFKnt4/k+uuL76Qq7IwWGeuk4xmWzKSAg1UtrgWMlPkVViRfiNqn4Yg/pOpozPJyiGX1TdG7i60sV0U/1n9w3ya6AXBUHquhex/lK29QM/vsx2kN/ho6AbRhK8UrAO3lK/0RED3UZtgc8OMHQQeYP8NEUHZHJrdiNKdz7d2Kuwq+ipG+Qu4J8wE5cHvDqXA618XOl4x7SN3FPih1YnuKtNC+u53u8jk9wMObyTKThyZnE7BJWYhWa8CyKaMGFBs42sm4FuUFKJ+kc4PR1LG3jlptZU82ZDC/v5sQwTwmFTGEr8jgZy1cMi6hvpuouwbex9S9oQBXm4w4MP07dIfYW+OkwFwv80cvRBobQiDn4QngVkMUF5CryfYfa6UXlNNXjs+h/AcYwiHHhtdRn+fA2ltbQHFCaZPAcP07QUkf9I/yGOyOfj6NYizGMi7FcV6Mao9MbcyrELI+JWSYcQVDk2g9ov50bApal2LeF+vEwYPNj3F3DkdWcWMhIkbGB8rifV+RagVMIZqrMAqyNDmuEdzz5GmsKFCYZybKom848Kzfw5njYV2fRtJ+mlxh9jrvSvLeFhsN8s5OueTwq7JvpfNfgoajyV04LiDfwqkiEhZxvY/Mi1mZDo+69nP6KiUjs8VjQRnyJEbRG3zM5atu4v5XGLCt/4HgNT7SH56sxN4pxTthr5dPUw/UZdgRhVQYCDuR5PxUr5aVwlBsDtgW041TAvjzvVsYtExO9Fb+n6VpfPlWzQj/VYzyA7RDw9Ebenu08/4ronWrpDfsmISEhIeF/5y/ylsmig8cmrQAAAABJRU5ErkJggg=='

result = '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'

beye = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAfYSURBVFiF7ZdtbFRVGsd/99yZO2On0+m0pU2dl7IdRNvu4G4qTIkSwQ0gEaKuyiaYuH5AP+wXQ9z9AiprcJeXsNnNJnyA1Zi4ysa4ooDELG8NRamtgAgtSKWF6Tu1dDpvnem9c+/ZD9MSV7EO67pmk/0nN7m55//c53efe87Jc+D/urHUfzOuCKgEfIADMAHju8IohRqDmtYQFmLNbCHmB1Q1UK4oHo8Q7rhlJUctK95vWX09uVx7J+zu1fXz3wtMFfzoHqfzuRWatqJR00ptM3hzwEldTx7S9YMt2ezzw3DlPwbTpGmrH9S0TSuczoAKfCGE0jtnjmqvrxf2igrFXlqKMT6OMToqjc5OK9jdbc6yLJkDDmSzvft1/bk2Xf/7d4b5mcPx7C8djl//VNM8MSGUrqYme/1TT4nGxYsVm+3r9cnlcpxsbpYXdu0yb29vz5ValvxE1+OvTk5ua56c/GMhMDecwAs17bEnnc6XGjXNc9nlEulnntFWb9umBkIhRQiBYRgM9vXR39XFpGFQ5HJht9vxh0LKnY8+Ks44HGri7FmrLpdzVAuxYFjKwX7TPHfTlamC2meKi99f5XQGeoqLhWfzZvuihx4SAAM9PZzbuROzrQ13Xx9uRSEpJQm/H9vChYSffhpfbS0Ax/bssdIbNhizUylrXzbb9+dU6v6rcPmmKrPM6fzT2qKihXEhlIl16xzLnnhCAHywezdX160jeOYMZckkLkXBrii4FIWyZJLSCxfo2b+fIbebYDjM7Lo6pdOyVLW11Wyw2Up6LKv8s1xub8Ewfk0Lr3U4NtaoqvNUJKL9YssWIYTg+BtvoG3axKxslqTTSfqBB1CffBJ19Wr0u+8m7nJhXrlCRTqN0dLClbIyguEwc+fPVw6fOEFwYMBygu+MlAcTpjnybb8LgBUOx9ZT5eUTRyorMx/u22eZmYyMdnTIf9TXy06/X7Y0NclLLS3SymS+dl06dky2NDXJTr9fvt/QIHvPn5dmJiM/ePdd60hlZeZUefnECk373Uz5xZfulRoh7tIUhSuhkNq4eLEC8OmuXfgTCZJOJ7du20bt/PkApGIxBj/+mFQsBkDtggVUb9lCyuEgGI9zZudOAO667z4lWluraopCwGZbUCiMu0ZVfQBafb2w2+3ouk6utRWAyWXLroNE9+6le8kS4mvW0L1kCb1781MhFImQXboUAPOjjzAMA7vdjr2+XgAEhfADxYXAlFYI4QGwVVQoAIP9/XgHBwEojkQASI6NEdu4ES2dBkBLpxnbuPF6haZ9nv5+hgYG+PL7KoUoAbyFwBS7hSgGEC4XAKmREYqkBEAtLc3DdHfjmAKZliOdJnHpUt5XVgaAS0oSV6/mkxTni1GiKG7AXQhMMmFZSQArlQLAXVVFWslvRebUl5fMmYM+BXvNsng+FiPqcOAOhfK+sTEAJoSgpKoKACuZBCAmZRJIFgIzPmpZcYDctWsS4Fa/n7jPl69SWxsAxV4v3hdfRHe5KBeCz02Tn/f18atnn+XY8ePXfeN+P9VTsbnRUTkFHwdihcCkoqY5AKB3dlrTk09tagLAcfAgPe3tAAQffJBQczOe3bvZ/PrrmFLy4YkTRM+exXnoEABqJML0IjDOn7cAopbVD6S+CeZfNr1ZQtQt1rQmZzwuR+bNUwOhkFJUW0v3vn3MmphgpK2NXH09Xp8P7ZZbcPt83DZ3Lh0dHax9+GHe2b6d5cBAaSnhrVsp8XppP3RIul97zbBLyZ5s9u1u0zxaEMykql69TYjH7hDCeXp4WLnzkUdEaXk5Q243xvHjeONx4gcOcPnSJWLxOGPDwwyePMm8sTF8b71FQNf5QzLJPS+8wLx778U0TY6sX2/O7e83PzKM8TcnJn6Tgi8KgkmY5oiqKOFFmtZQOjQkP7HZ1DsiESUYDtNbXs6106epSKcp6upCPXoU5b33UI8exfX552imiV5ejn/tWt49fZrlS5dyYMcOa/bbbxs24JWJiT0nTfOVbwL5GgxALJf7tEyIVT9RVU/y3DlrsLpazK6rUwLhMI6lS+nKZhlNJDDicQQwBgwHAiSWL+fHW7eyaOVKbp87lycef1w2NjcbfsOQ+7LZ3r9lMk9lIT4TzA0V0bRHXi0pGTpXUTGxv6Ymu2fLFlNPpaSZyUgzk5HZREJGL16UZ48dk9GLF2U2kbg+pqdS8p3t262XA4HJZZqW2+F2Dzeq6mOF5L1hczVgmhcSYFUrSuMdluVQW1utI62tTHq9SlUwqNjtdko8Hip9Pko8HlRVxTAM2g8flkfWrzdnv/mmETIMS5Eyvj6dvhq1rN8zwyqa1ow9cETTHn1I01663+kM2oBRRVGioZBqb2jI98BeL0Yslu+BOzqsmp4es0LK6R44ulfXN3ys6x8CbcDhKSBjKu9vvwr4raeDMggscjg2rHQ4VjVqmtc+g9cATul67KCuv/9BNrtpCKJTQy8D84CLwAhgAWlgP3CqYJhpVUNdo6atqbHZIn4h/BVCeDxClMQtK/GFZY0PWlb/5Vyu7RNd3z0In30lfAf5Jd0I9ACfTgGNAL1Ax03BfEW3AGXk24EU+UWVmcG/A+gChoC7gL9OxbqASeA4wExnspmUAQZuwn8GkIA+BXTDk4K40cPvQX8Bxsn/Gtd/Kee3ygNs/qEhvizfDw3wv6d/Agsvfd0HYmeXAAAAAElFTkSuQmCC'

xcell = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAP8SURBVFiF3ZZtaFtlFMd/t713pkmN0s12dRQXqLgpmbZOqpNNRBBKsQ5Fr0OUEPJBQRBF1xfwQwsVihSFTi1Sa/vJigjDaSZ0CuJg65hdbIrDdjHa2JSZVOtYck1vb+OHe2+95mW5tQWDB+6H/3nOOc95zjn/+zxQRlK5Sf9ngduBmS3IhYpN+h8C7t+KRGDzyWypXCuZSuB94HmLrgH4Amgu4vMcEALi6K07augPAEFgp8X2JeBdQLCb7H1A2ggmAqeBDyzrw8Axy4bLwEPAzcDdwJMW24+AU+gFeBBIXeNQReVV4GfgbeB7wFUkmaeAH4EbisRxA5eAt9Ar98JGEwG9jN8AGuDNWbMm4wbOAwpwAr29zhz7A0AW+LzQRnYGeC9wF/A7eguKyRXgHnSGfQu8AnzNP2fiCJA04t1UauMdwC4LrgLCwBvAA+h93m9Zt1YmV7zoVagx8GPAH8CtwHHgJCWG9xhwzoLfA84CkoFfQ++7u0AyAeAd4GngUeAT9LYB7Eav7BED16DPock2IP8PLAE/GQntBO4EuoAlY/00UA2sAVHD/hLwA3DVOPVBdJZcAF5En6GHjUOZTFSMWPsM/WqhyvynIoyPj0+ZYHV1VZiYmHC2tram7AYInvq0alr6cspRI16x67N99o79zzzuz7sXRVmW95hAVVUikciyLMsNdgPHl2IppXGK2n0u1a7P2psNoizLt+Xqy+puEsbGxn4xgaZpQjAYvK65uVmxGyAUvuC46kzEtjkqbfuIS+7dj7QezuYtZLPZtPmtrKyke3p64lZdqW9oaCgZj8f/3IhPb29vtJC+rNpUVsmIo6OjCRNomibMzs5WWXWlJBQKVWUymd/cbrdtNkUiEVehPUSfz7d+YamqysLCwrJVV0oymUy6vb29pr6+fs2uTywWu+zz+epy9WXVJqGvry9uAk3TKqanp8WmpqYVuwFmZma2eTyerMtl/6cXDoclr9ebZy+kUqm0CVRVFQYGBpY7OzuLvdbyZGRkRGlra3PV1dXZblN/f3+io6MjbxREp/Pvx5iqqllRFLNWXSmRJCnrcDjYiI8oimuF7MtqZsTh4eFfTaBpmvDVuZMVZ46eCNkNsHRRqVMUJVNdXW17Zubm5lzWfdeTCQQCtSZQVZXPQh9+d8vL6vlcw2KyNiDtlWX54Eaovbi4eDkQCJQ5tQcHBxdNoGmacHziY+X6Pdmo3QCJi5ldhw89UeNyuWw/HScnJytaWlryKin6/f51GquqKiSTSbq6uu61G/jfUDuRSCT8fn9pakuSVJB2xeR/S22hu7v7dRNomiZEo9HtjY2NSbsB5ufnb6ytrVUcDkfGrk80Gt3h8Xjy9vgL/bbOK4XiegoAAAAASUVORK5CYII='

dlimit = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAG2SURBVFiF7dfPS9tgHMfxT54nXZpoq5at4BSEHQqbu7iTu25eBiKinvwfdvOsF0/+F4LsuJ02BhsMZMj2B2wDhRJxrVTT2aY/zDd5nsSDKZRiDo60p+d1ecLzzcPzPuQSQFEURVGgAWAAsgCseDXidRYAj99zAJwBOB9qzMTc+jvGskx7kGdctzTGslzTLV6ovH++zP5ZAOBKEdalkBcy8B0pa3+pe9AMaB9AN80Y/dH8lgQgBweG841emro2sM0olDO/O/Xtr+3mlu3Thyp1dgE0Uom57wGD8XAhV7xeyBW14+7V5ifXWTsh8blK7g6Ay5HG9CtZU17JmkL5urH60c28KZN/aHutPQC/Rh7T88Sc9N6ak6iSu3TUbr468T23IcMKhdLuSO+PEwQ2br8vAuDFx9oARPysATBTiel5bORpw8gDgElSlJqCnrUErTRkAD+KIoEopEiLXBnwL9YLO3q4WOudZdzMpBrTz+B6WOS6XzTG/MHZKXUz33NPPT79utW/z4YV8z9UTBIVk0TFJFExSVRMEhWTRMUk0TvOz8Jdg4zvZn+I27+DtF3JgBOvjEcDd98A8+arcTfiXSkAAAAASUVORK5CYII='

periodic = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAUTSURBVFiF7ZhrbBRVFMf/987Mzj66LZ1uH6FQa1trhWoRqDw0IoZEExIw0fjBNFBB0DTRgE9iCDFEiQgkJKAgCFgCfjKRCBoS8MGroohEgZS+lu1rS7ftLt3ubvcxc48fhhrSbIvdUMSEfzLJnHvOPfObe+7cO7kMpuYCWIT/Tt8CqJMBQFX5kmkVtpWVM+w6ERMkGBGYIIKAYEIQE0RMEGD6BBMAzHZxow0QREwIASJiAgQhBIQAExDmPeGGX5BpExOXG/omtnUE0w1DmDCMAfPnpdHbq3INgOuMJB2M6wSuM+L6UBsx0w6FIT7Y0JQTDunysqr7vLNmuIJbd7TknjsfcKanK7EN6x5t1CZYo3QjDyOug7jOmKSbbcx8BjF9xerjszs6gjAA8FTG9LNdrVmV0zPC2zY/7Fm/saEQABY8nes/uGfOpcdmugKbt9Xfn0relGCCIV3K0iy6xcKp2xe19AUS8tSy9EEAaG0L2YuL0sJ3DGZl9eS+2gMdrprVFwsJAOcgAPj6ULurvXPQtqyq2JtKXjmVTpPzbYkDe6Zd9V8XtHTlH8WZGYpx6HuvduSo17Vn++yLqeRMGeZKY0jduNU9CcTEx+vL3QBw6HBnjiFAL9ecLX9iTo7v1erS1jsC81BZWqx2Z4WHIOkgrkMA+3ZUXmFDNmO6WbixKaU5M14a08js3teZ0dOT4AvmZ1+fPTNzYKS4k3W+jKPHvK6sTFvkrdcfaRoXmC++7NSaWyKq3SYnRoM5XefTdu5tKi+Y5OgfC8xdVaZ7MCPpHsxIugczkv7/MEKAjeY3buG/LTB2GxcA4OuNj7py+3qjVgCwWaXEuMFkuyw6AFzrjimjxXV3mzCapkbHDaZyRsYgAPx6LuBM6JS0FPG4YBf+6nMBwPQKV++4wSx5Ka/fqnLh64kr76ytz6dh/yzCILZqzfmyPn/cpqqS/lp1qWcs+ce0a+fmqsb6tSVda9Y15tce7Mg7cdqf8fgszZ+lWWO+3ph85myf1t4RSWMM9P6b5RfyJzpi4wYDAK9UTwrkZFtjH37SnNfsjtg9rZH8m/1FhWnB91ZNvfzic4Xe4SN322EAYNHC3ODihXn+ppao9OeloGVggJjDLscrpmrB0pKMgVR/O5PCXGkclMoedOh6guDxROUHSux6sriSYkespMgZhuAGMa6fqfPbXZpN1rLUpPG3UtIJ/PnuHgsADAwYvPbgNUe3LyG1d8Zk99WI0uyOWE7VBeyCgP7+hNTWEbGcOtvrJAKsNklwCXB7QlYAaHYHbQBQ33jd8cNJb1Y4nJBO1nVqXb6I+q9hhuubwz32/V91OYUB1DeELV3XosqGTc15v5wLOD7a1Dj5t98Dzl173XnHf+rWfD1RZcu2+iIA2LL9UikAVNeceNLTFnQ888KRZ5vc/c433v157phhdJ2gKIwA4PnF2aGCApt+7Mc+Z3NLWL3aar7dgqeyAyuWFna3todsQ/0EmWuQIUx7StmE3uVVZW1Fhen+5VVTWq1WKWkZk8JMzFdo336fdeunXsf8eZkxAGCMIRo1WMAfl7Jdqv7P/sTM6+YvJxEXfPuuhoLGluAEAJC4uY1IMhMAwDlPOr0ZAKgq3zn8fKY/KEhRmLBaJCMWI+KSZDAOMRgmJgiCMQjOJYMEhMS5iMYNMOKCcy4MIhEJGVyWJV1RpURs0GCKIiUG44JZZEmPRXUuy1L8pvOZ7wxD1Awt6XfFydXfWlmGDj458C8AAAAASUVORK5CYII='

pie = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAQvSURBVFiF7ZhbbBRlFMf/55tZd9vuWmwFS7cFl7baghCVprWXJYCa8MCLAaNSoqBi1OAlPBnDQ9VEE2Oi7dpWJQ2SoC94SZQY30wjVfoAWMAiKS21LqWXwNLttjvbnfmOT1233dtMd33j/zTfmXNOfnPOd8sAt5VctNxA30idRyq2GiHgAuCE5AgRXxck/JNHegdbWyH/VxjfWEM1JO0FwQvQ3SkdmaeYqQdE371edqo/pzDto40VQsHbDHrEbOL/uLhHJWp71d17OTsYBvmuNe8GybcAclgFiSMyQNT2mru3O52bkupFayvErqrG90B4BSB12SAAQCQANFTt3FrYN3f4dwyc4GRuIhVI8YuN74Loiawg4uT/p/Ta8aNPbnap+W8iRUeSwhQdaNiXS5Cp8eKpI10t01FDqCB4nU//uMsUTOdE8zoCHcwVSCBQGOjqeHYiGlVtCzYS9EzhnpPrMsIYujwMkD0XIKFQQbCrbf+opjmW5lMYvD8tTPvf3vUA1ecCRNMcc762fUOh2bz8ZO8ZtNH51MmalDBCkS25ANGjqtbR/tzFmVt3OtP5CYUfTQnD4KZsQQxD6J917u2/MVV0VyZfZqoHOLayYjC+8S0eEK3MBoQlZPfnLWfH/KuLTAUQXCv2/LQmAUZGjZrkEeZEEnz82O7TI1fLMlYkXgbL8gQYVVBhNjDffrOz79JAlfXKMsWqGNvmmaULZP1GQYCe1y9HvQMX7vcWXLAcX5w3fd8bS2EAhK0mshv6ZO3MUKlrVXhHQeicImaTHjlpZVQqfyTASBLXCeaSEXPUo03erJgdbxJgwTYg6hXS/rOR9HhJJ1bk+MJzDEYwRtlEl/J1zV8XGq626/Mb4u2ROuI7fiOmoJkscTCq+muMYeHhoPvUIDMmUgUJllp1aCzQfOuv7XZ9vjTBwQZEtglLfWIbhcvsoUQYEJiIe5IFrYjOTm0JDHjWapP16T57/mFiLjbZawBGCc5R3F15UY8VqXwfP1bBwYeCV8P104NNdqm7MmYXQGS7+eqQXXy4aLzUwedv7CCirasiwRsbZ0ZqFUjbUp+0YsDZaQgxnn7uGCtpyN2tVcXbEma/Q9c+rZ0eVB6cGW6wDAIABGiZqiPIEPeoLyWYlxoO3Hv2UlF0rtMyRJz0GmKjnFIC6R58tfr90C8ZYQCgalPIR8DX2QBFHk9eHb1EnHZ/rCVcrFLCEIErL88+z6Avlwuje4j1isXVMUpFX9ge3kZIvuLSTjJm0NDFgkNS4h0Alq+iqp8p7wtDkCBprMUx9yfaC+n8Te2Wg386N0Dnjxh4zCqQ4wd5nuaUQ+UfhJLuYZZhFnTlfP5mg8XLgngHM0rSJL0pmU8oAkcrN82dMZt/WX8hmEFXBpzrDUNWqiTWSMkOQRTUJQKKopypfGB6mMyeurdlQv8CBsaRE1kA2G8AAAAASUVORK5CYII='

graph = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMaSURBVFiF7ZZLSFRRGMf/31Wvr5kKQTLSIiFNR2cmcnz12rYICkRbFEIU+SaTWugirxG5ELGm8gHWomjjYEKrgtpICx/kKx+LpBILc9HDlEadufdrEzHeO3MnnGGy8L873/ed8/9xzj33O8Cm/gGROlBYWBg2Mz3ZA6YkQGGBSOobnnjyN+B+y2ZJf2mzZuSH0jM8lGa2/ZlHAdlCLBiIMNs/PP7QMy+EEkYgLIEpBcz5CuQZdT7gncm2ZnQR2ATi7wrjzuDI5CNftf1Dr1/ZzGnZLAg0ODzVq4H1bUNE5GZ/MAMj40UK8ywUoV4P5E8U0mPyJ80xNTVdjjUaDfUL3xYtYqTYfPZCZHVZmTQQNEcBBIbXHdfsjMFgvMuMS1u2GmOioiKzifCss/P67qDB6GgNTFeXJAJc6BljhsHtlk8Gw6ylRdp28HBWblau2WS3S4m6MMCETEQudREROwMF6eio2xEdTUMpacmnMy0pR0QRo62t1w74hCkqcsjM3KZCmXO5Vrr9eDGDNa3FU7Is1jBzkseELYKgNPiEAYDSUqkOQMnH2U9fFr4uOlwuzq+sbPzsB8avBAFJ6hgzdnmONbeJCAxI921W03lBUW71j0190DNpa5OOv3s7azLExhafKz8xVlJyY85bHTO9ALhAFX6+BtiXCTGTG6T702tvb6gC0LMneWdi/Pa4U8zigN1eG++tdn6e7wG4DcANEBOhWxR/1HvWBNQOmHFFNU6IiIgqBtCsrpUkSQFQk5djnYkg2tfbN1ymrln3H5gZBMDgJWPUm+dadsnLzhXNjQ0IhgjMzI9VMTeR0LPeNb3CZJnNqRAoJiyMUvNMpjhfk5lRDaDV6Vx1rqysTgMoKC29OqpvyMTw3g4038yvZ2clA2/AOOQWlfcANO0eACoqpCUAF23W9L1QyD44NvFUD8SfNDAOh0MGUBXIoutVSJ8QOdb0WgKVE+FYjtV0U50PyhuYAFZYvx0AQP/IZCOARl/5DfW42oTxpf8LxmbJOMOMBArnvCyzOTWQtYJymwTiB6zQMpM7JhjrbWpD6ydZphUo4DU9yQAAAABJRU5ErkJggg=='

mergemission = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAT3SURBVFiFzdb7U1RlHMfx9/fZZRcWEBQxlc0YZkVkC9QNrGnKbZouYtKM5dQf0Ew2ZZeZbtOAkTZaaWZiNV1+86eGaoouY7cZ8jIN0gpeFqYioyJKAlGBlYU959svgYqEu7Raz087z/P5fp/X2XPmOQf+X6Nm1n8tAMjbnucVqAqBREFfBGc91NiXTFCD8c6cc4eoPIGQYsBZBvISyNNgHYGqVZfC4a2dc6c3Z25YlKdUdfOvPV3lcm6k6hZgM0gf8ChsaE42Yt4rcwJq5GVgmiiP/fJQ15eja45zo7t/hMveglwn8DYsy4aivRD617fOX+N3pd7lWo+wWYVtnb1da04+2f/j2Rn5p2KomQ3Wm6B5wF3w3E9Thcx77bICLMd7Ch1OK7bmp0e6j02xVdVaqO6C6uunUu3dPnvZ5bVzf798R979UwSMH+tuhupjUHXbmbnHZ0+UzH81d2zeu8Nb4a2de2zejryb4tllkts0flRfC3wAcg+YfRALgRWETb2jiYI3CrJiw0P7MnunLzk1oy+owk7EVHY+2NmYZAxA9TLQ90DagXKP5/i9xb6GiBhmoHZv74qIY2TOyE5EmlAtFEPlLw907Y23u+PCkdGx7m5gC8gsIB+Q6VnHSrKzuvKBhYgsic20V43kxnIAr4Cg3JCxIuNU/6cDh+LZwcSPWf8OyFagZ3RmeDg19eyEnWl5Rn8rHLeV13978Ped8e6QAAZg/VvTPD1rXCmRQYChaHr62atWpu0BcETM6ZR+s7bzoa7tiXRPEANF8/dI8fyvQy5XZHB42HMGIxDLtDJMxJzO3pV+IPed7IFEeyeMUbGzUlyR4auKvmhMS+s/GY1mpAJY6ep2HnecmvXutG9S+hynbazpifZ2Tra4ejWOjvaF16EsbmppewVA0W5BMCZmFxd+dWA06xiQaE59Zmis2OgfScGUlxfl2FGp6PjeVCjahcj7Y5u6RxrtqCsCeCaqBRAYGLJc3yaKOeecWbpo4XxVs0qFpQq7xTL1TYcPHz0PW3rl7Sr2w//U1KjZ3HjwyOcJYwKBgMdhRW5UzB2gTlQ/S4+ZTxrC4UkfwPJS/60q3AeaOTapchLV15sOtX6VKARAyhb53xfskBjHR40Hjkx6OK1ejePn7xdWXlHYVl9Xh7Xc53P3ZLhLVHSmwfx5vH/ocHt7e3QqEACu9ftnxJMLBoPOslJ/ddmi4o0k/BqJb8TVNBgMOiMnuquAlMEReTYcDg9fDMwFz5lgMOgc7OuuBnFajrSa8ZClS64subpkwYKLjgkEAimDfX8+AxLzZOfWhEKhkfEZtez7FZM+UX3SMMt9PrexhzYA0fzC8MaGhobY+ExZabHfFvGEDrUl5cN9wkNvuc/n7s1wbxDVE1cUtr5QV4c1YbWRlWLLh4BeFEwwmJ/ac8K1AdE/mppbt+5vmXijQKAgSy1d6h6KvZoMyHmYkpKS9MG+2EZBOva3hLcxyRU77LQKlN37vvuuP1mYsWfG7/dnpErseUSP7j84OQQQVV0hYn+cLAj8/c8E/f6MiEs3KfzQ1NxWewEI5YuLrlGb3saDbT8kE2MCgUDWYIq+pCqHm5pbt18IAqC2qcRQn0wIgDHW0BZVGptawm/GU7B48YK5Ivgiw7In2Rinqr3724NtcX80O2zHSozuCodbk/5KMIlAfD6fW+BmdZpPkg0B+As7xdngJqxj6gAAAABJRU5ErkJggg=='

beta = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIYSURBVFiF7dc7a1RBGMbxn7psRNcUIgREtNRK8ZagCSagXyBg1JRWWvgNYhorsbXQELQTbCSloIKiiKB4LRQRJRglqGhM4Q3jrsXMsqu4e47ZTNLkgWXOmfMw73/n9s6wqH9ryRy3V8AudGEGj3AT5TmOk6l+vME0nuA1KniMjfMJcgpTOIxiXf2g0CvjWDkfICfwEdsbfL8u9NDR1CB78BPdTTxjEeZ8VmNLWwBZjlGcwe0mvo5Y/mghVqaO4DPam3ja8E3omWMpYR7gdIZnfwT5gjWpQHbGIJubeAoCcAXDqUBgCK/q3jdhHwbQJwzdaAQZ09rczNQVtdUxEoPW/8qxHMGyvI3OhrgoLOUb8f0DvtZ9fy+kANjmz01wztUt/Ov1f9WXhNVT1eXoO5kSZggvc/gORZhpOXtnNsPUpzZEzTQey3ZsTQFTxO6cMPWJsaOhqwWYTqzICbOh7nkqBUyvMF8mcni7YlnBi/+Mk0tXcSGHr4C3EeROCpCikGMu5vAeUNsA+1PA9MTGH2b4VgmpopoKkui4cMguY0cDT0lIFRXhjFNKBXMN54SVNIG9areLNhzEc/zCWeHwlUTV+TKI1bgk9NCnCDaD78J86pxtkLz3ph7cwlpMxrp12CLsO5O4L5zqkmsYz1IHybvp9QpXjgVXdb4MLDQI4W5UljPZtaI8w9SHp3iXFiXkkCzdxb3UIItqpt/5e3QUjfPQ7gAAAABJRU5ErkJggg=='

phi = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJ5SURBVFiF7ddLiI1hHAbwn8kMGTMWcp0GSZSsTCkrZW1BYUFsECtJJouRZGUlspDBQiEhKZRIzZQFsSCXcWmyoCiXccslzLF4z2m+8/qOme87w6Q8der8/+/zPe/zvbf/+/Ef/wCGVfHsNNREua/4FOXqUF/8/w6vq+gzFfNQyPE79zvR4TnN/MApfW9dj5ZinOTcwSt8xDccy9lfZpxUPgrz/1bHaehOGHmSRyBegHkxEdMT8ZU8IoNhpg6Lo1yX6nbqgDESS9COe8LCTNs5H9CBVmHkBhVN2IM3xc56cBxbi/+T66VV2MYlo1+xF2OqNVGHncJhVsBzrNW3jZuUj0h74tkZuJhoe1jM5cIU3EyI3fDrkK+IzKyM2kcUTSQNNWY10qx8u75IMQIHIjNNKZwdEWdrFiM16IwE1lXgPkhwHlfgrI+0OrKYWRY9/FrYRTEmRbyDFfTaIt7tNFKlc2ZZFF/ClxTegijurKDXEsVdWczMjuJbFXixmY4UTj0WRrmjWcy8ieKeAZjpxrMUzhrl58tlnK+gl4rNyue4LYUzHr0JzqEUzmR9h2QBjzAuixFoEOa1JHIXtRFnaWR4VdQ+UViopfbrmJDVSAkzhTcpiV3A1ET7vshMczE/ChuES1UB77E95WUyoxH7hdpSqjFnsSky2iPUo9PCPbdkYhfGVmsiRjO24apwhUyr0t+LBg9juTBCfxw12BgZ2SLUoKqFs6IXc6LcGWEKhwTJAvp0qEzAXOVTdGKwhPu7py7CamExjhDOiVnKv4++4T5e4rNQw3bj2mCZLOGIfF+Occ0aEPobmQZ9x3cBb6P2WoyOcrm/m/7jn8BPQNzhuKwup0EAAAAASUVORK5CYII='

ptauto = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAV9SURBVFiFzZhfTFNXHMe/t9TetpS2tmARKFgHRYhE1CVomI4wk81pYnmwA2VjZpvOueke5st8MFu2PWzJzOIMycIGMcYJ+1t12RjoYmp0BRnJRANdAYGWNkBbWvrv9rb37EGqVQuiteo3ucn9/c7vnPM599z7O+dc4CkSBQBi4FkCaBIFcABDAV4+cM0HTKYcZolUejIvX70tT61m7g5gmTDldrtJf3+/mBYIxmd8vk8D0eh3AEhKiHIUitaWb5sIIVEyPe0ibtfUrSscDhFCooTjIuTCX+dIRXn5jEomOwdAkHIYbUFBSEbTQblQGJALhQEJnx9elp3t/eD9AyGfz0sikTCp2brVnymVNqYcRrN0qZcGiuKK+TRQnCmRtK5fu8YXiYSJc2qCKNPTA+lA9qPk4C0gJsIAA1M+X+3w4JD5rOE0FEolnq+ujkSBTY8bJibi9Xp/6rlyJQIAa9aulvB4vKL7VUoVDDiOm3TY7WEAEInElICmM54YTLpYXL6yrEwEAHa7nWWCQfsTgaGBQgK8unnrFgoAOtvbgwQwPUoYfiInBbwiBCZm7yVSmWwty7K6I18fpYu0Wpzr6IR1zOoLAZdSClP/egNts9oOxmyFUiFcUVIieHHzS8hTq3Hp4kXs3K4PcT6fLxdUdzKdB0FCLqASAJcQZvfetwUsy97KrtFoFC6nE51/dqDt5PczJpMp4vP7Py8G79BR0JJkYDYjSDC7JCWEqX5uY8jtdgXTeLwoABCCSBqf7yEcd3V6evpMCPhBCKwPgaRdvzmge8QDsAeL4ADBL4jMx0PFG/fARFiWnZnxVTDAf3O1QACrE+TEYTCJPgDKB+zag0XUEDh8CMa9CPg5UTsCIBLE7RElfIHvJwYwM8DuOYrTRMCumCEGNT4O8uZC2n2gPJNqPdCTKS8vX5aVlVXg9XrHTSbTnNP4OGDo+vr6P9Rqtcjr9Ubdbvcms9k89NhgGhoatmg0mp1Go/GTrKyscrlcTgOARCJJKysrezkzM/P3qqqqj+12++nm5ubWlMHs2LFj44YNG77MyMgQqlQqg0KhuJV7eDwe9Hr9QZfLdUChUAi0Wu16QkigpaXlTDIwPABgGIbdv/ediCI9g3E4HBIAEIvFzwiFQhoA4kHiFfPTNJ0mEomS3k7wAMDp9++mwuElXCCwVECIkgEGm5qami0Wy7/xwRMTE26z2XzFbrdPxfstFstIY2PjkWRhYtMU8ACBmFOn01VFo9HVy5cvXxnzDQwM/N3R0fGu0WicLCwslOr1+q9WrVpVDQCFhYUFOp3uECHkH4PB0J4szB1at27dRxqNZlnMZlmWOn/+/BdGo3ESACwWi7e9vf2wRqPZKJVK+TweD3V1dW/ZbLZpg8HQ+bAwCZMen8+/Ywfn9/u53t7ewXhfT0+P1ePxBOJ9AoFAgiSOMAlhHA5H1+jo6GjMlsvlVE1NTU18TG1t7bbc3FxpzB4bG7ONjIyYAAQfFoaaq6C4uDhj3759F1QqlRIAPB6Pr6+vr9lms13NyckpKikpeUOpVCoAwOVyBY8fP/7C5cuXbbi5NrEBSKhLiGI7QtfGQVbO1U+85swzubm5UoZhvACUACCTySSVlZXvJYplWdazePHi9IV0OJ/mXChLS0vr8vPzE/4MuFsqlSq7tLT0tZTBdHd3f9Pf39/DcRy6u7vbBwcHLYTcPuvfuHFjpKur6wzLstzQ0ND13t7eo8nCzKu8vDyRXq/XzZqiY8eODba2to6cOHFiVKvVrgCA2traLRUVFdK4amkigPwIIfkMApIDqm+h/c27UFqt1mBbW9uvs2Z4eHj4rNPpzGFZdiIcDjsA4NSpU7/dVY0TAqf3g6EBIAjSu1CYp0r/AzB/UjDdn7PfAAAAAElFTkSuQmCC'

ptman = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAATCSURBVFiFzdd9bBNlHAfw73Xd3bVdO9aOssHKHLINMtCxseCGG2QxkUXEl+gwAV9meBmaoImSyEsyUeSPqfEPEEkQAwZRfCOiMUG2GBSIU3yLMucMLI47Ntj6wvXa691zd49/wHBhN7ax1vlNmvTp/Z5fP9e752kL/I/CAIATmE+BAqsCE1AZQLIDZ2SgL+UYv8dzMG964L68QEC9voCoGhMOh2lHR4eTY9kLUVl+JW4Y7wCgKRFN9XoP7dv7NqXUoJFIiIZD/dcempaglBrUNHV6/OtWuqC0NDolM7MVAJtyTFF+fiKT45RJPB+fxPPxDLtduyUnR3r+2WcSsixRXdfoA0uXxrI9nrdSjinIzZU4oHDQYTsHFGdnZByqLC+TdV2jwf5L1OdyxV1ATjIdtlHU6CrwZ78sP9J19lznF58dgdfnw6LaWt0A7vqvMQOhkiR98uPp0zoAlJXPy7DZbIUjTUoVBqZp9vX29GgA4HA4GZbj3BOGcTmdpXPmznUAQE9PD1EVpWdCMBwwkwKP1i29hwGAlqNHFQq0JRNjt3qRAZbzwKWrzzM8mZnlhJD739i5gyssKkLrsRYI5wU5AZxKKWblE49zoiBuGBh7fV5+1uzZ7N11S5AXCODUiRNY8XB9wpRleRqYH8bz5gpoIgQsBGBaYtasa2QJIdd2V8MwEAoG0fLVMXx48P1oW1ubLsdizcWwbd4BLmM8mDooFFe/kiwxtXfWJMLhkJJmsxkAQCn0NLv9MjXN3yKRyOcJ4CMeqEyAprVfOaEhsQFYi3T0guIw9Bt5mMGDIRidEBKNygtU4K/hOlBACIIeaIJqtQAYGWhYi3TmHExsghpOBz616sMCuoJ/z8jyBh4pKtCpAmuGOZzmABoGBk4wFy6ArhpN3zHtM9fFMY65lrkpTIGfva1qDv/T3EB6w8jVKcR4AG9pMfvu8f156tp618oZfvvrN9MnGZj0ijLX4b3b/ZydEuHper59WyNnTMvErmSAxtSgqsSxf1fT5Lwsp9kNQxOgE2FKFu3SdKjAMOt8rBhVVcn6dU/pXpdb7e3ttdzIKor4rVvW+RYUBZhuGESEQcSL/VrfY03xyr4YXhgv5BomGIutYTTNb8bjuSylPhU4O7jo9hnsgyuXeVbUVbG9MIgAkwgG0cXq1dGakISNAJRkYAb2mfhlIG5VMN3LliyucG1bv8IdunppRBhErFklzQ+FsUsBxGRABmMs4wG85SXse69t8BIYmgiDCKCa0PBSNOcPwfwmTPB9siDAjW9g+/x5rsN7XvbzdkY/D4MI0DVx54F4+pff6kpYwQfJhNwQU1ni2P/mluyAz2N2w9BEmEQ4+UsitnWfWnhJwavJhgDDXKb8HHfzkoX84lkFtk7oV5bwxT6tb/nGeE1/HI1I0b9Jy08my5czs+XXXOdzzZddMDTRMHSxenW0OiRhM4BEKiDDYkKhSMWyh+41/lbKbr3jSVK3aLU0LxTG7mSunFFhnMDUiCT79+w+4MnyZtGg7Jzc3mWeCZLk/vgeVSY5+RddHKf7PG7R53ZvsgKPkDQHQD8GT7eDpVPB/D7aiUNuYBuT9h1rUxcFpejJMSIGYvLAkfVQOQBQQH++yT4Tm38AG4sVssxMmLUAAAAASUVORK5CYII='

smallarrow = 'iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJISURBVEiJvZW7bxNBEMZn77Fr+0gOx7YMOCJBxCYgIkQQGCqniEQoeBUUqWhoEB0VEhL/AyUdFUoDDR0lNTSgCMUiQgEUhGODw5mz77EzFNhScmfBJhz5pE+nHe3cb2dnbw9gD6TvcP6IrusXicgBgM7/WJCZy6XmXz06Y0+W0ucBwFZN1BTnsUN5cen5/dPvND9lPbs3+/FIMVMDAK6SrLRd4zl+/eGt4+/3G5qOPnL0kV89m2+9XGlXvzlB/Z8hUwdStQc3yj8qY4IYEh/YADDnTmTd16vOTLMTrO4aUi6mq3fmS6OzB1MBSeQkkesSOevb0sCoFIS50nBLzU64tmPIdNGauXmuOFWbGOmxEPjAFHEhw1k2bRbWNv1MqxOsK0NKeVFZPJm9sFCxXZLEo5YhCpTIBz5scxQMJj45vtt2ZeuvkKmx9PiVsn352nTWxZD4MFPfWkic9V3OplBDOLbeo89tN9j2DRlRiDCg+tXxN5bebDgAAJ0eitIon1w4arvRlb344Fj1715zS3rXIpwDgKU/QpYb3afLje622O1T+bvkhdZgHPafjU2fnrxtPY6+I6oYZJg4EoeeFNG4ieSp5CtBmCSBHu2LxnXJVNLVIAaRiR5a0ThD8hODsBDE1p4MpEn8mRhEl2SSRzGIHpLSBakE0SRy9KUF9HtMBAwAgMn4Ydg1BAIpsCdjjddCNBODaCFwGtJ4LVT7n6hV4qGJmoxBIMDkIEyCGFpJkGQlgeQSIdYTSrLxX3xM1RlhLE6kBNkT/QK4qiiMBiwcnQAAAABJRU5ErkJggg=='

see_fit = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIWSURBVFiF7ZZNSBRhHIefmR2neVd3xnVZN23NCjtsgZhstzpYQpAaiXb1ltCtQ+ShS52MoEPdunbpAwKhCDrI1kGkICiRPsRArcjctiAW1mU/6vCul43VnR2nodjnNvD+/u/D+/GfF+rU+YfxuT3B6WZxc7hZXAxpauf79fwzt+eryEFDOzYba13LxKPJO/talgVENxuvuSnzvah+WcrmMz2Nuv9TrpjOQLqCwwUg6+o2pQuFb6lcYTXxM7v+Ip27vpLLvykb0gs8AsLANTddNsMALgNfgXFA8UrkCPAWeAjs8krCBG4An4GRqhJ9TfrIuXDj3QHLuLSNIieBZeA20FJtyJiMWnOZeDT5/EBktde/Y8ihRGtJ4ANwfKvBavm3pig+AENFUX/ldQciZ4DXwA+gG5i2XaHfNMbORwJTg5YxWaNEOzAFzAGHa6zhGAV5TVPAVcDJqjqiC0gAM0DMKwkNmECuxgR/nsG/Rg/wEngM7PZKQiDPRBJ5RjzjKPAOuI/8uXmCBdxCtvJhryQABoGVkoxpI+c/JHyjHbLvOCaCbOWLQJ/NrDIWEtML3W2pK+3mfMygs5pQpatY3soTdkwCEOo3xd4O3Vc8G2naGVQbTtjJb7AHeAK8AuK1FNhgNCjuPegKfRwP+2csCNrJqshruoZ8gTU4ESmhCNl/bNUKALPAU2D/Nkg4QgdO4eE7tE6d/4LfVNlwlDBRY2EAAAAASUVORK5CYII='

xel = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANrSURBVFiF7ddPaFxVFMfxz8zkT+lCKChYWly4qKVajdokpS4UN6b5Y6maGEWyELULceHKjZWAYHHhQvAfCFKQljaxSZrMREQXorZWI2iVUiKiVIRqwX8gJpOQPBf3TXnz8iYTS4IW+oO7mPvn3O+975xzz3BFl6MGyY/TupZ7jNM6SD7dX9URkdvBK3k+LfHQWoAUuS/PiR28mQbKJX+UaIk4hWbMo7+bkdUEwRE0opxjZxdfVcaryOKBPZiNFwwV6V8DkLmI3iQIqZupqERHxCjWYQGPdAdDqwKC3m7G0/MyYVYTaKUgy8KsBlASZJGFg4yN8J3gBoP/BmYn7ryfLQMMFGhYZOEIhw9zJmP+JziRAOnCMTSnQLZjA3alDRSWgenATWfZfZ5z7VxToLCN7TNE0+EgG+L2OD4WQyZBMJfjgf08jw9wC37Ge8vsXVPn0Faio8hMkajI3AR74/EG/IXrKiBFZuN55SL3pux9qEaELuszuDaGuQrlSXYvhryzDvMRfT18H59y4wSduTBeuZG+Lo4n7OXxB1qEdVVakpJTasXXKEMn7+aDU86iMcfQU/RieAUgsC229UPWZvVg2vB5sqOT9SUOxEYb7+GZCf5cAQi0x/aiS4GpLE7q6df5Jh98pizkj2dXAFKx91mdPTOVw2+YxheJVsYmmGR/7KjRRGgv1LH5pRClNTespS3CKZ5I9G3FPmyOnXlUuJGK5iIe7GEsw956wXk34tesDZf7TO2YwnCi/YSPUiDzQg4poynH0VJ4bNO6XYjMTJB6MK2W+svIQY4lQd7nQDfPRSHKymiKGMoAalPHX+rdTBXMJLuu5lAFZJKXXuZu6GGyDtCSyFwpTLOQtqcSIFWfJqLvtbD+4mnrANWNpFowLcL7cT4BUskjlcw7lnXaLKA3GBCyeVUxlVY6mu4SP5C4EUd7uP4x9hZoWGDxbY6/w7fx/Cdxs+qMuhn79rD10bCusMDii/x9kldT+52SiLz0q31rbOwCztQBgZOW1sibcNs0v8/wSws3FCjcQaHMhbMhd1V0Gj/WupmLShVW83H+GK01v5bS5YRlKr1Mn8mo8AYuBQS6KeFhIR81YTijrEDGzax2MV7RSmrh/+//ps7gUG+JP81qgkBsr1846KGpUCvV1uB/+F/7ii4L/QPkXkw+hn0x/wAAAABJRU5ErkJggg=='

tight_layout = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHrSURBVFiFzZixbtVAEEXPzGzWNkkTiBKUioKOj+CTET0NH0FHQZUKSENIvPHMUOQRXgwSQUJaX8kaa2VLR2dnVrJhQ5H7Op68JvUAcQddEHEQR5Zd1QVRp906orvLFpgdVUfM0e+OmXNZF5gcPjngQDwe5ujsVDzeivAOspHSIGdEZ4lsEA3R5iIzZENixrUh2tCYufWGlBktDV0aZW4cHs5cXMw7mH/I4emZTCdv/u2l/x8FQCQFrjuz7GCQJOWmL8q9GU0kNwKDJOhGYPRbkFsxI5IgG2lgkUToaUYewATZyczL4SHM147TdPxlfAiDJNLp0Gtl+glT7lY0iU5m3NZmLJFOPVNkglf7MJpo9DETywjzPkxJvJOZ9BGWFYxYHzMm0wpmSLR02iYdIfZhPiRLr22SCXx/tEnM+5jRGEH2zZDUpZMZJsgVzOWzPmZSRp7GCoaPcw8WRSZybaZXknEN0zH5m5l+ERmJI4UtwBDjepr6JWUkYyMwktsxk3DfwOVvD69inJ8PXF0NLEMlSiWWSi4DB1YJHcioWFRSB5BqmXdraE2VSsYAMiBZQWomz+8+lX79n3lMFDB4YXBtHLeCuxFPjHQjwmAw0gsZRoZRD2x3XyCNLHZX0yAKaYbELTef39PzrPtTfgBoTekEkhvsLAAAAABJRU5ErkJggg=='

legend = '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'

grid = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGNSURBVFiF7da9ThRRGMbx3woKgoA2UCgmFiR6H9YW1BbUJHIXW1iTcAXUXgE3oD1ZEjoSOhJ0+UiQxVCcPVmczA4zc45BhX8zn+/7njnPvM85PFBOZ3jcxtuaMU8xXbh3gfMGdWfx5Mb1Lj40iL9nRJk+403J8z6uEmvUkfAQm3Ewy1hMLArP8LhF3Am+Zqifjzgz7/GiYexPnGUYw/dhnt7k8MYrLFUEFFuxDZOYG/PsAN3E/HmJMs1jYnh+idO7HEwTBy4yIXxMkR/4VTPHHj62rH8PiDJtYaVmzJ9w5QN0y37gyCMsJBalniufo5ehVj7izKwJxnaZmK+tKx9jJzpwX3OHzenKh9hJzJWXKNNLTFW8NxCW+VQqOzHKtGG0uSrb4zZlnCuP48GBK8mxUBL+p0FC/D7WO7e+9jsdPE8oGim68oXQ3n8PcWY+Ce1d5FS6K9fZrB3hS2ztb3idWBRmVPvVv0OU6Z3wVU04ExbGFGIXXqEfZVpVLdOckVu3ZUHYI5Wxj/XE/P8x1+czQ09Wdy2/AAAAAElFTkSuQmCC'

newname = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANTSURBVFiF7dZRaFZ1GMfxzzmvbqbLbHOzuVxzmQpWmiOmLrEZlmlp4rslGsukq6ibIKSLwIvQiyyw0Mobw6xgbSDD0oSKEKKLCEocCy9SzNS1rFVG9rZzujj/5dsc1YXQRe8XXs7znnOe5/zO///wew4lSpQoccWoxi3/tQiYir14c+SFXDhOwEpUoRFr8AvOYSxWYynG4GvMwQpcxHpMws94WPbWx0PdJtyNSpwI535CPfrxcbGYMV3MLnBnD+sTxi6gZ4DJfbz+IDu72TSfg3V8u5+eNrYPUnGQzfN5rYb+99jWxN5Kzr/P1ja2fcrtvzF+ER+9w+Z5HJqWCS47wsp6jtaztJ0PhsXECQ05bqun9g7662io5ObZxGhayZdlNJ9hTS25iMYcNzYwMIs0prGa72YyGFNVxWBKVT/LJ1M4zsJGvppIOcrgAlNqOJdmzxiVXlSE+Fl0YAF6MAWL8Ua4nscLIW7D8yFux3Zcg8Gi2mVFcQX6RhMwrCyPG1CLmeF/JW7FVViIB0LRRdiEcUHkI7gaNSGemL28g3gq5N0VnnNdOJfDrJFionCcHuIfZE1agQJOYYaskS/Imvu8rGFhAJNHiU8gQQN+DDlwbfgJ9c6NtkIlSvxbon++5crTxUMRU9PMiU/mee5vE17NxsBfeDczrsvYQrwl2ERK1HlpzFxWq5s1XcGXOqnoItmT2cSllUmJutkVMTfhlZjpKQvzLO+mBfeknEpZl3IfZsTsxz6ZwT2GzajDkwkzyykv8EzK5xGrIp5GTcLENg6HFXpiLc0U2XFEimMph9qyqbo7uuQbVRE7qtgTUVlgXDtHEY9naz5z4/LxHMjzInLVJIXMjatjJkT8mtK8lk+CkDl4fIh1wxrGjFjxeSmdQdzchM/C8t+UUHees5i0ge87MzcdWMHFbmpTzhTFp1v5vYtVY2lazTfYXbRVrSkdCfcr2tKRg6ol5RgM0RLRO4cVCa15XpY5c29IbMEXw3lCXsriKNyDkwWmhf5Y0kllFzvQip05luV4tGh3Mt7m3pglEYcjTg7RETFwkbfKsr3uw5GIjSkfpsyLiCL2JWxALmZvwoaYeIhduWxsbEw4m3Ig5voo+1b6kyFeaue0EiVKlPi/8Qe5i+JZbRuoyAAAAABJRU5ErkJggg=='

ticks = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANjSURBVFiF7dZbaF1FFAbg7yQxNsYoVRNrW0pFNERbBS/RFkUJIkJFfFC8gPegILVWCj4oVLB4g6IFUQT1Qan4ICr4YEUFW4JakKAI0lZ8ELWtaAVFQio5MT6sfZLJnLOTTV5KIT9s2Gvtf8+sWbPWP8MijgPUpt+6eneY0n8MIjhg/I/N0DHt/K+2S23qu1nE+thG7V1vqLWNzztkfWyLju7t804+eXQQXdqX7CnmPVg17g9wagVeOz6tOObteLBskLkwgX2YrDDJv/i+Am8SvxXPgrACJ7fwd6Mz8y1vwTsB54ga7cEGrF5oMM/hqsw3jEP4BZsS/xcZrxOj2IvX8CXewgEMpsS27MeHxN7nz60tAtyIfpyHi4uASTs0cDVGcAX+wfu4C/fg/pTYkf3Yh934OPNvwlRi13C0GBzuxQ680CLobpFB+NFMrfyE3rmCGRErHc38e/BXYk9hHCvxa2E/gu04O/t3H64v3l9J/GuK4BaEPP1naF3UayuOt1QmG3nNNPBYZt8iKzYcEVm4LvG1476SMe/GaYndMwd3FrZiS/F+Mz7U3MLQhU9woVjYm6IJWuESfIQlYnv3YqBKMDW8LopyVzFpGXpF0e9MFlCGDXgXX+Gi/GOuwLdhvVjF73igmGRAFOpYwTsddxa8AaG+g0JDBpCecZfhhoJ7Ci4XRd2GE4VOobmbUkxgW8m3vJh/KJ4qeKcibxrLzC7u3E6DOmsOO0WPyExq91QJ5rPMfgrrWvAuNaO8DZSd3s+LrWrgfFGT0yhr7YnMPoQzW/D6zKhr+m++jUShp9zD+ZhlwdRxk2jnfnGWfN2CN4o7RNF2ikKtmX10NDAiJKMhdk8KZZ8Xy0UX7Rdte+0c3CF8XnDfFhrSCm14HN/g2yKwsmQce+R7u1Okb5vsRMXDYvXEYfoEnsVLGe+IuFo2MCy2rUOoeYr38GpZMKvEEb9MswYdFOJGiFWfEMYVGa+OnxO7cR7VNN+n/8af5sHTmT2MC1rw1grVTvFiyZibzc72KjyaEvLVd4rLUL+o+gZnSPN1sltkcHXC7RG3vhxLca44RuqFb70sU3kw1+AZcTVoiFddtPX+jLsVNxZBNWphHC9nvFox1kpcaUbDDssyU4ahKiQhWmsqctfhpIrcRSzi+MP/5oejZujkk9IAAAAASUVORK5CYII='

predict = 'iVBORw0KGgoAAAANSUhEUgAAACMAAAAjCAYAAAAe2bNZAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAI8SURBVFiF7da7axVBFMfxTx4Xo4UBMRhtQmxUbNVGsBAJgoVgoWJMpf4LguIfYAqRICqoKSSobZQQUFF8dj7S+YAgiDFqNKhpzPNa7Ky7LndzV0Rs9gfD7D3nzHfOnT0zs5QqVarUv1VDjn0terAdazCLNxjCFXwvwG5FN3ahExW8xx0MBN6iakYvplHNaZ9woA7nICYWYUzjZJivpioYTg2YxyP04zJeZoDHczgnMnEvwvh+PA7c2DeUl1BfKugh1teI2YmxELOA3Rn/nmCv4h26ajA2hD8Zz3UqG7ARc8F5D0tqZRvUgY+S1ZtMtdlg/xDi8rQED0LsbEjwl84Ex486kFjd8uuhiv0FGJ2S2uxLO14H42ABCNF7ngxjJvBEUrCfLVKYGd0IY15Bo2h7x6vxtCBkDiPh+Rk24Xn4PRL8RRTP14GGxpBQUzDOFoTATOgrmb5oImlGc5zMvKggYd0fgOLdNhb68b9gjIt2IaJTtYovWF4Ask1SrIeC7UjKtrUAo1VSdwNpR1cKdL4OZJmoLqr4hhXBvlJ0TVRFdbS0DudCas4dWefNlPM0WmoAVovOoTjuaMZ/LOW7i/YajBa/H7DDtTJtw2gq6K3onuoRvYpLmEr5B0XFn1YjrqdipnARhwOnN3Bj/6hoRWuqXXIy5rUFnJXsnqwqOCe5FvLafazKSyRWA/bhtmjrxYO/4io21wMEbcE1UV3FjBncwl75ny+5ahJ9z+QuZUG1BU5TvcBSpUqVKvU/9BO15MnuE+xpHwAAAABJRU5ErkJggg=='