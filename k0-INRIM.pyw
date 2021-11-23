"""
k0-INRIM should allow to perform k0-standardization NAA analysis 
by returning results (concentration of target elements) together with
compiled uncertainty budgets aderent to the prescriptions reported in 
the Guide to the expression of uncertainty in Measurement (GUM)

@author: m.diluzio@inrim.it
"""

import os
import sys
import datetime
import tkinter as tk
from tkinter import Checkbutton, ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
import pickle
import classes.recovery as recovery_script
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np
    from scipy.optimize import minimize, curve_fit, fsolve

    import classes.GUI_things as gui_things
    import classes.naaobj as naaobject
except ModuleNotFoundError:
    recovery_script.recovery()


class MainWindow:
    # only one subwindow open at a time
    def __init__(self, M, NAA):
        M.title('Main')
        M.resizable(False, False)
        self.secondary_window = None
        M.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(M))

        greeting = f'k0-INRIM version {1.5}'
        M.infotask = tk.Label(M, text=greeting, anchor=tk.W)

        Logo_frame = tk.Frame(M)
        logo_k0main = tk.PhotoImage(data=gui_things.k0log)
        k0logo = gui_things.Label(Logo_frame, image=logo_k0main, hint=greeting, hint_destination=M.infotask)
        k0logo.pack(anchor=tk.W)
        k0logo.image = logo_k0main
        Logo_frame.pack(anchor=tk.W, padx=5, pady=5)

        Buttons_frame = tk.Frame(M)
        nln = 0
        #settings
        tk.Label(Buttons_frame, text='Utility', anchor=tk.W).grid(row=nln, column=0, columnspan=7, sticky=tk.W)
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=nln, column=7, rowspan=2, sticky=tk.NS, padx=10)
        tk.Label(Buttons_frame, text='Characterization', anchor=tk.W).grid(row=nln, column=8, columnspan=5, sticky=tk.W)
        nln += 1
        logo_settings = tk.PhotoImage(data=gui_things.ggear)
        B_settings = gui_things.Button(Buttons_frame, image=logo_settings, hint='Settings!', hint_destination=M.infotask, command=lambda: self.go_to_settings(M, NAA))
        B_settings.grid(row=nln, column=0)
        B_settings.image = logo_settings
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=nln, column=1, sticky=tk.NS, padx=3)
        #database
        logo_library = tk.PhotoImage(data=gui_things.library)
        B_browse_database = gui_things.Button(Buttons_frame, image=logo_library, hint='Browse database!', hint_destination=M.infotask,
                  command=lambda: self.go_to_browse_databases(M, NAA))
        B_browse_database.grid(row=nln, column=2)
        B_browse_database.image = logo_library
        logo_question = tk.PhotoImage(data=gui_things.question)
        B_credits = gui_things.Button(Buttons_frame, image=logo_question, hint='Credits!', hint_destination=M.infotask,
                  command=lambda: self.go_to_credits(M))
        B_credits.grid(row=nln, column=3)
        B_credits.image = logo_question
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=nln, column=4, sticky=tk.NS, padx=3)
        #save/load
        logo_save = tk.PhotoImage(data=gui_things.sparadrap)
        B_save_elaboration = gui_things.Button(Buttons_frame, image=logo_save, hint='Save!', hint_destination=M.infotask,
                  command=lambda: self.go_to_save(M, NAA, B_save_elaboration))
        B_save_elaboration.grid(row=nln, column=5)
        B_save_elaboration.image = logo_save
        logo_load = tk.PhotoImage(data=gui_things.battery)
        B_load_elaboration = gui_things.Button(Buttons_frame, image=logo_load, hint='Load!', hint_destination=M.infotask,
                  command=lambda: self.go_to_load(M, NAA, B_load_elaboration))
        B_load_elaboration.grid(row=nln, column=6)
        B_load_elaboration.image = logo_load
        
        #calibration
        logo_calibcurve = tk.PhotoImage(data=gui_things.calibcurve)
        B_new_detector_characterization = gui_things.Button(Buttons_frame, image=logo_calibcurve, hint='New detector characterization!', hint_destination=M.infotask, command=lambda: self.go_to_calibration(M, NAA))
        B_new_detector_characterization.grid(row=nln, column=8)
        B_new_detector_characterization.image = logo_calibcurve
        M.calibration_combobox = ttk.Combobox(Buttons_frame, width=25, state='readonly')
        M.calibration_combobox.grid(row=nln, column=9, padx=3)
        self.get_calibration_files(M.calibration_combobox,NAA)
        #check load
        if NAA.calibration is not None:
            M.calibration_combobox.set('#loaded: '+NAA.calibration.name)
        logo_deletecalib = tk.PhotoImage(data=gui_things.delcal)
        B_delete_calibration = gui_things.Button(Buttons_frame, image=logo_deletecalib, hint='Delete detector characterization!', hint_destination=M.infotask)
        B_delete_calibration.grid(row=nln, column=10)
        B_delete_calibration.image = logo_deletecalib
        logo_renamecalib = tk.PhotoImage(data=gui_things.renewcal)
        B_rename_calibration = gui_things.Button(Buttons_frame, image=logo_renamecalib, hint='Rename detector characterization!', hint_destination=M.infotask, command=lambda: self.rename_calibration_name(M.calibration_combobox, M, NAA))
        B_rename_calibration.grid(row=nln, column=11)
        B_rename_calibration.image = logo_renamecalib
        logo_displaycalib = tk.PhotoImage(data=gui_things.magnif)
        B_display_calibration = gui_things.Button(Buttons_frame, image=logo_displaycalib, hint='Display detector characterization!', hint_destination=M.infotask, command=lambda: self.go_to_display_calibration(M, NAA))
        B_display_calibration.grid(row=nln, column=12)
        B_display_calibration.image = logo_displaycalib
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=nln, column=13, sticky=tk.NS, padx=3)
        
        #f & a evaluation
        logo_phi = tk.PhotoImage(data=gui_things.phi)
        B_fluxevaluation = gui_things.Button(Buttons_frame, image=logo_phi, hint='Flux evaluation!', hint_destination=M.infotask, command=lambda: self.go_to_fluxevaluation(M, NAA))
        B_fluxevaluation.grid(row=nln, column=14)
        B_fluxevaluation.image = logo_phi

        #gradient evaluation
        logo_beta = tk.PhotoImage(data=gui_things.beta)
        B_gradientevaluation = gui_things.Button(Buttons_frame, image=logo_beta, hint='Gradient evaluation!', hint_destination=M.infotask, command=lambda: self.go_to_fluxgradientevaluation(M, NAA))
        B_gradientevaluation.grid(row=nln, column=15)
        B_gradientevaluation.image = logo_beta

        Buttons_frame.pack(anchor=tk.W, padx=5)

        ttk.Separator(M, orient="horizontal").pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        Buttons_frame = tk.Frame(M)
        nln = 0
        
        #analysis name
        tk.Label(Buttons_frame, text='Analysis name', anchor=tk.W).grid(row=nln, column=0, columnspan=3, sticky=tk.W)
        nln += 1
        logo_newanalysis_name = tk.PhotoImage(data=gui_things.newname)
        B_new_irradiation = gui_things.Button(Buttons_frame, image=logo_newanalysis_name, hint='Modify analysis name!', hint_destination=M.infotask, command=lambda: self.go_to_changeanalysisname(M, NAA))
        B_new_irradiation.grid(row=nln, column=0)
        B_new_irradiation.image = logo_newanalysis_name
        M.analysisname_combobox = ttk.Entry(Buttons_frame, width=30, state='readonly')
        M.analysisname_combobox.grid(row=nln, column=1, padx=3)
        #check load
        if NAA.analysis_name is not None:
            M.analysisname_combobox.configure(state='normal')
            M.analysisname_combobox.delete(0,tk.END)
            M.analysisname_combobox.insert(0, '#loaded: '+NAA.analysis_name)
            M.analysisname_combobox.configure(state='readonly')
        Buttons_frame.pack(anchor=tk.W, padx=5)

        ttk.Separator(M, orient="horizontal").pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        Buttons_frame = tk.Frame(M)
        nln = 0
        
        #irradiation
        tk.Label(Buttons_frame, text='Irradiation', anchor=tk.W).grid(row=nln, column=0, columnspan=3, sticky=tk.W)
        nln += 1
        logo_neutrons = tk.PhotoImage(data=gui_things.neutrons)
        B_new_irradiation = gui_things.Button(Buttons_frame, image=logo_neutrons, hint='New irradiation!', hint_destination=M.infotask, command=lambda: self.go_to_irradiation(M, NAA))
        B_new_irradiation.grid(row=nln, column=0)
        B_new_irradiation.image = logo_neutrons
        M.irradiation_combobox = ttk.Combobox(Buttons_frame, width=25, state='readonly')
        M.irradiation_combobox.grid(row=nln, column=1, padx=3)
        self.get_irradiation_files(M.irradiation_combobox, NAA)
        #check load
        if NAA.irradiation is not None:
            M.irradiation_combobox.set('#loaded: '+NAA.irradiation.irradiation_code)
        logo_delete_irradiation = tk.PhotoImage(data=gui_things.delirr)
        B_delete_irradiation = gui_things.Button(Buttons_frame, image=logo_delete_irradiation, hint='Delete irradiation!', hint_destination=M.infotask, command=lambda: self.delete_irradiation(M.irradiation_combobox, NAA, M.infotask))
        B_delete_irradiation.grid(row=nln, column=2)
        B_delete_irradiation.image = logo_delete_irradiation
        logo_rename_irradiation = tk.PhotoImage(data=gui_things.renewirr)
        B_rename_irradiation = gui_things.Button(Buttons_frame, image=logo_rename_irradiation, hint='Rename irradiation!', hint_destination=M.infotask, command=lambda: self.rename_irradiation_name(M.irradiation_combobox, M, NAA))
        B_rename_irradiation.grid(row=nln, column=3)
        B_rename_irradiation.image = logo_rename_irradiation
        logo_display_irradiation = tk.PhotoImage(data=gui_things.magnineutron)
        B_display_irradiation = gui_things.Button(Buttons_frame, image=logo_display_irradiation, hint='Display irradiation!', hint_destination=M.infotask, command=lambda: self.go_to_display_irradiation(M, NAA))
        B_display_irradiation.grid(row=nln, column=4)
        B_display_irradiation.image = logo_display_irradiation
        Buttons_frame.pack(anchor=tk.W, padx=5)

        ttk.Separator(M, orient="horizontal").pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        Buttons_frame = tk.Frame(M)
        nln = 0
        #background
        tk.Label(Buttons_frame, text='Background', anchor=tk.W).grid(row=nln, column=0, columnspan=3, sticky=tk.W)
        nln += 1
        logo_add_spectrum = tk.PhotoImage(data=gui_things.plus_spectrum)
        B_background_open = gui_things.Button(Buttons_frame, image=logo_add_spectrum, hint='Open background!', hint_destination=M.infotask, command=lambda: self.go_to_openspectra(M, NAA, 'background'))
        B_background_open.grid(row=nln, column=0)
        B_background_open.image = logo_add_spectrum
        M.background_combobox = ttk.Combobox(Buttons_frame, width=25, state='readonly')
        M.background_combobox.grid(row=nln, column=1, padx=3)
        M.background_combobox['values'] = []
        M.background_spectra = tk.Label(Buttons_frame, width=3, text='0')
        M.background_spectra.grid(row=nln, column=2)
        logo_peaklist = tk.PhotoImage(data=gui_things.plist)
        B_background_peaklist = gui_things.Button(Buttons_frame, image=logo_peaklist, hint='Background peaklist!', hint_destination=M.infotask, command=lambda: self.go_to_peaklist(M, NAA, 'background'))
        B_background_peaklist.grid(row=nln, column=3)
        B_background_peaklist.image = logo_peaklist
        logo_spdelete = tk.PhotoImage(data=gui_things.none)
        B_background_delete = gui_things.Button(Buttons_frame, image=logo_spdelete, hint='Delete background!', hint_destination=M.infotask)
        B_background_delete.grid(row=nln, column=4)
        B_background_delete.image = logo_spdelete

        #check load
        M.background_combobox['values'] = [spectrum.filename() for spectrum in NAA.background]
        if len(M.background_combobox['values']) > 0:
            M.background_combobox.set(M.background_combobox['values'][-1])
        else:
            M.background_combobox.set('')
        M.background_spectra.configure(text=f'{len(NAA.background)}')

        F_delete_selector_background = tk.Frame(Buttons_frame)
        M.delete_selector_background = tk.IntVar(M)
        R1 = tk.Radiobutton(F_delete_selector_background, text='selected', anchor=tk.W, value=0, variable=M.delete_selector_background)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_delete_selector_background, text='all', anchor=tk.W, value=1, variable=M.delete_selector_background)
        R2.pack(anchor=tk.W)
        M.delete_selector_background.set(0)
        F_delete_selector_background.grid(row=nln, column=5, padx=3)
        B_background_delete.configure(command=lambda : self.delete_spectrum_file(M.background_combobox, NAA.background, M.delete_selector_background, M.background_spectra, M.infotask))

        logo_dsample = tk.PhotoImage(data=gui_things.flask)
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=nln, column=6, sticky=tk.NS, padx=3)
        B_background_definesample = gui_things.Button(Buttons_frame, image=logo_dsample, hint='Define material!', hint_destination=M.infotask, command=lambda: self.go_to_sampledefinition(M, NAA, M.background_combobox, 'background'))
        B_background_definesample.grid(row=nln, column=7)
        B_background_definesample.image = logo_dsample

        Buttons_frame.pack(anchor=tk.W, padx=5)

        ttk.Separator(M, orient="horizontal").pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        M.regular_calibration_variable = tk.IntVar(M)
        Buttons_frame = tk.Frame(M)
        nln = 0
        #standard
        tk.Label(Buttons_frame, text='Standard', anchor=tk.W).grid(row=nln, column=0, columnspan=3, sticky=tk.W)
        nln += 1
        B_standard_open = gui_things.Button(Buttons_frame, image=logo_add_spectrum, hint='Open standard!', hint_destination=M.infotask, command=lambda: self.go_to_openspectra(M, NAA, 'standard'))
        B_standard_open.grid(row=nln, column=0)
        B_standard_open.image = logo_add_spectrum
        M.standard_combobox = ttk.Combobox(Buttons_frame, width=25, state='readonly')
        M.standard_combobox.grid(row=nln, column=1, padx=3)
        M.standard_combobox['values'] = []
        M.standard_spectra = tk.Label(Buttons_frame, width=3, text='0')
        M.standard_spectra.grid(row=nln, column=2)
        B_standard_peaklist = gui_things.Button(Buttons_frame, image=logo_peaklist, hint='Standard peaklist!', hint_destination=M.infotask, command=lambda: self.go_to_peaklist(M, NAA, 'standard'))
        B_standard_peaklist.grid(row=nln, column=3)
        B_standard_peaklist.image = logo_peaklist
        B_standard_delete = gui_things.Button(Buttons_frame, image=logo_spdelete, hint='Delete standard!', hint_destination=M.infotask)
        B_standard_delete.grid(row=nln, column=4)
        B_standard_delete.image = logo_spdelete

        #check load
        M.standard_combobox['values'] = [spectrum.filename() for spectrum in NAA.standard_spectra]
        if len(M.standard_combobox['values']) > 0:
            M.standard_combobox.set(M.standard_combobox['values'][-1])
        else:
            M.standard_combobox.set('')
        M.standard_spectra.configure(text=f'{len(NAA.standard_spectra)}')

        F_delete_selector_standard = tk.Frame(Buttons_frame)
        M.delete_selector_standard = tk.IntVar(M)
        R1 = tk.Radiobutton(F_delete_selector_standard, text='selected', anchor=tk.W, value=0, variable=M.delete_selector_standard)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_delete_selector_standard, text='all', anchor=tk.W, value=1, variable=M.delete_selector_standard)
        R2.pack(anchor=tk.W)
        M.delete_selector_standard.set(0)
        F_delete_selector_standard.grid(row=nln, column=5, padx=3)
        B_standard_delete.configure(command=lambda : self.delete_spectrum_file(M.standard_combobox, NAA.standard_spectra, M.delete_selector_standard, M.standard_spectra, M.infotask))
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=nln, column=6, sticky=tk.NS, padx=3)
        B_standard_definesample = gui_things.Button(Buttons_frame, image=logo_dsample, hint='Define material!', hint_destination=M.infotask, command=lambda: self.go_to_sampledefinition(M, NAA, M.standard_combobox, 'standard'))
        B_standard_definesample.grid(row=nln, column=7)
        B_standard_definesample.image = logo_dsample
        #ttk.Separator(Buttons_frame, orient="vertical").grid(
        #    row=nln, column=8, sticky=tk.NS, padx=3)
        #B_standard_otherparameters = gui_things.Button(Buttons_frame, image=logo_settings, hint='Other parameters sample!', hint_destination=M.infotask, command=lambda: self.go_to_otherparameters(M, NAA, M.standard_combobox, 'standard'))
        #B_standard_otherparameters.grid(row=nln, column=9)
        #B_standard_otherparameters.image = logo_settings
        nln += 1
        R1 = tk.Radiobutton(Buttons_frame, text='', anchor=tk.W, value=0, variable=M.regular_calibration_variable)
        R1.grid(row=nln, column=0)
        M.standard_position = gui_things.FDiscreteSlider(Buttons_frame, length=300, label_width=10)
        M.standard_position.grid(row=nln, column=1, columnspan=9, sticky=tk.EW)
        tk.Label(Buttons_frame, text='Δd / mm').grid(row=nln, column=10, padx=3)
        M.Deltad_standard_spinbox = tk.Spinbox(Buttons_frame, width=5, from_=-50.0, to=50.0, increment=0.1)
        M.Deltad_standard_spinbox.delete(0,tk.END)
        if NAA.standard_position[1] is not None:
            M.Deltad_standard_spinbox.insert(0,NAA.standard_position[1])
        else:
            M.Deltad_standard_spinbox.insert(0,0.0)
        M.Deltad_standard_spinbox.grid(row=nln, column=11)
        tk.Label(Buttons_frame, text='u(Δd) / mm').grid(row=nln, column=12, padx=3)
        M.uDeltad_standard_spinbox = tk.Spinbox(Buttons_frame, width=5, from_=0.0, to=25.0, increment=0.1)
        M.uDeltad_standard_spinbox.delete(0,tk.END)
        if NAA.standard_position[2] is not None:
            M.uDeltad_standard_spinbox.insert(0,NAA.standard_position[2])
        else:
            M.uDeltad_standard_spinbox.insert(0,0.0)
        M.uDeltad_standard_spinbox.grid(row=nln, column=13)

        Buttons_frame.pack(anchor=tk.W, padx=5)

        ttk.Separator(M, orient="horizontal").pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        Buttons_frame = tk.Frame(M)
        nln = 0
        #sample
        tk.Label(Buttons_frame, text='Sample', anchor=tk.W).grid(row=nln, column=0, columnspan=3, sticky=tk.W)
        nln += 1
        B_sample_open = gui_things.Button(Buttons_frame, image=logo_add_spectrum, hint='Open sample!', hint_destination=M.infotask, command=lambda: self.go_to_openspectra(M, NAA, 'sample'))
        B_sample_open.grid(row=nln, column=0)
        B_sample_open.image = logo_add_spectrum
        M.sample_combobox = ttk.Combobox(Buttons_frame, width=25, state='readonly')
        M.sample_combobox.grid(row=nln, column=1, padx=3)
        M.sample_combobox['values'] = []
        M.sample_spectra = tk.Label(Buttons_frame, width=3, text='0')
        M.sample_spectra.grid(row=nln, column=2)
        B_sample_peaklist = gui_things.Button(Buttons_frame, image=logo_peaklist, hint='Sample peaklist!', hint_destination=M.infotask, command=lambda: self.go_to_peaklist(M, NAA, 'sample'))
        B_sample_peaklist.grid(row=nln, column=3)
        B_sample_peaklist.image = logo_peaklist
        B_sample_delete = gui_things.Button(Buttons_frame, image=logo_spdelete, hint='Delete sample!', hint_destination=M.infotask)
        B_sample_delete.grid(row=nln, column=4)
        B_sample_delete.image = logo_spdelete

        #check load
        M.sample_combobox['values'] = [spectrum.filename() for spectrum in NAA.sample_spectra]
        if len(M.sample_combobox['values']) > 0:
            M.sample_combobox.set(M.sample_combobox['values'][-1])
        else:
            M.sample_combobox.set('')
        M.sample_spectra.configure(text=f'{len(NAA.sample_spectra)}')

        F_delete_selector_sample = tk.Frame(Buttons_frame)
        M.delete_selector_sample = tk.IntVar(M)
        R1 = tk.Radiobutton(F_delete_selector_sample, text='selected', anchor=tk.W, value=0, variable=M.delete_selector_sample)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_delete_selector_sample, text='all', anchor=tk.W, value=1, variable=M.delete_selector_sample)
        R2.pack(anchor=tk.W)
        M.delete_selector_sample.set(0)
        F_delete_selector_sample.grid(row=nln, column=5, padx=3)
        B_sample_delete.configure(command=lambda : self.delete_spectrum_file(M.sample_combobox, NAA.sample_spectra, M.delete_selector_sample, M.sample_spectra, M.infotask))
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=nln, column=6, sticky=tk.NS, padx=3)
        B_sample_definesample = gui_things.Button(Buttons_frame, image=logo_dsample, hint='Define material!', hint_destination=M.infotask, command=lambda: self.go_to_sampledefinition(M, NAA, M.sample_combobox,'sample'))
        B_sample_definesample.grid(row=nln, column=7)
        B_sample_definesample.image = logo_dsample
        #ttk.Separator(Buttons_frame, orient="vertical").grid(
        #    row=nln, column=8, sticky=tk.NS, padx=3)
        #logo_settings = tk.PhotoImage(data=gui_things.ggear)
        #B_sample_otherparameters = gui_things.Button(Buttons_frame, image=logo_settings, hint='Other parameters sample!', hint_destination=M.infotask, command=lambda: self.go_to_otherparameters(M, NAA, M.sample_combobox, 'sample'))
        #B_sample_otherparameters.grid(row=nln, column=9)
        #B_sample_otherparameters.image = logo_settings
        nln += 1
        R2 = tk.Radiobutton(Buttons_frame, text='', anchor=tk.W, value=1, variable=M.regular_calibration_variable)
        R2.grid(row=nln, column=0)
        M.sample_position = gui_things.FDiscreteSlider(Buttons_frame, length=300, label_width=10)
        M.sample_position.grid(row=nln, column=1, columnspan=9, sticky=tk.EW)
        tk.Label(Buttons_frame, text='Δd / mm').grid(row=nln, column=10, padx=3)
        M.Deltad_sample_spinbox = tk.Spinbox(Buttons_frame, width=5, from_=-50.0, to=50.0, increment=0.1)
        M.Deltad_sample_spinbox.delete(0,tk.END)
        if NAA.sample_position[1] is not None:
            M.Deltad_sample_spinbox.insert(0,NAA.sample_position[1])
        else:
            M.Deltad_sample_spinbox.insert(0,0.0)
        M.Deltad_sample_spinbox.grid(row=nln, column=11)
        tk.Label(Buttons_frame, text='u(Δd) / mm').grid(row=nln, column=12, padx=3)
        M.uDeltad_sample_spinbox = tk.Spinbox(Buttons_frame, width=5, from_=0.0, to=25.0, increment=0.1)
        M.uDeltad_sample_spinbox.delete(0,tk.END)
        if NAA.sample_position[2] is not None:
            M.uDeltad_sample_spinbox.insert(0,NAA.sample_position[2])
        else:
            M.uDeltad_sample_spinbox.insert(0,0.0)
        M.uDeltad_sample_spinbox.grid(row=nln, column=13)

        Buttons_frame.pack(anchor=tk.W, padx=5)

        #check load
        if NAA.calibration is not None:
            def_value = NAA.calibration.reference_calibration.distance
            distances_list = list(NAA.calibration.kedd_dict.keys()) + [def_value]
            if NAA.standard_position[0] is not None:
                M.standard_position.set_values(distances_list, NAA.standard_position[0])
            else:
                M.standard_position.set_values(distances_list, def_value)
            if NAA.sample_position[0] is not None:
                M.sample_position.set_values(distances_list, NAA.sample_position[0])
            else:
                M.sample_position.set_values(distances_list, def_value)

        ttk.Separator(M, orient="horizontal").pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        B_delete_calibration.configure(command=lambda: self.delete_calibration(M.calibration_combobox, NAA, M.infotask, M.standard_position, M.sample_position, M.regular_calibration_variable))

        Buttons_frame = tk.Frame(M)
        nln = 0
        #results
        M.detection_elements = [element for element in NAA.detection_elements]
        tk.Label(Buttons_frame, text='Limits', anchor=tk.W).grid(row=nln, column=0, columnspan=2, sticky=tk.W)
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=nln, column=2, rowspan=2, sticky=tk.NS, padx=10)
        tk.Label(Buttons_frame, text='Results', anchor=tk.W).grid(row=nln, column=3, columnspan=3, sticky=tk.W)
        nln += 1
        M.number_of_limits = tk.Label(Buttons_frame, text=f'{len(M.detection_elements)}', width=3)
        logo_dl = tk.PhotoImage(data=gui_things.dlimit)
        B_detectionlimit = gui_things.Button(Buttons_frame, image=logo_dl, hint='Detection limits!', hint_destination=M.infotask, command=lambda: self.go_to_detectionlimits(M, NAA))
        B_detectionlimit.grid(row=nln, column=0)
        B_detectionlimit.image = logo_dl
        M.number_of_limits.grid(row=nln, column=1)

        logo_elaborate_results = tk.PhotoImage(data=gui_things.result)
        B_elaborate_results = gui_things.Button(Buttons_frame, image=logo_elaborate_results, hint='Elaborate!', hint_destination=M.infotask, command=lambda: self.go_to_elaboration(M, NAA))
        B_elaborate_results.grid(row=nln, column=3)
        B_elaborate_results.image = logo_elaborate_results

        Buttons_frame.pack(anchor=tk.W, padx=5)

        ttk.Separator(M, orient="horizontal").pack(anchor=tk.W, padx=5, pady=5, fill=tk.X, expand=True)

        if NAA.position_selector is not None:
            if NAA.position_selector == 0:
                M.regular_calibration_variable.set(0)
            else:
                M.regular_calibration_variable.set(1)
        else:
            M.regular_calibration_variable.set(-1)
        self._update_regular_selection(NAA, M.regular_calibration_variable, M.standard_position, M.sample_position)
        M.irradiation_combobox.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : self.select_irradiation(M.irradiation_combobox,NAA))
        M.calibration_combobox.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : self.select_calibration(M.calibration_combobox,NAA, M.regular_calibration_variable, M.standard_position, M.sample_position))
        M.background_combobox.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : self._spectrum_selection())
        M.standard_combobox.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : self._spectrum_selection())
        M.sample_combobox.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : self._spectrum_selection())
        
        M.regular_calibration_variable.trace('w', lambda a,b,c : self._update_regular_selection(NAA, M.regular_calibration_variable, M.standard_position, M.sample_position))

        M.infotask.pack(fill=tk.X)
        M.progress = ttk.Progressbar(M, orient='horizontal')
        M.progress.pack(fill=tk.X)
        M.progress['value'] = 1
        M.progress['maximum'] = 1
        M.progress.update()

    def on_closing(self, M, title='Quit k0-INRIM', message='Unsaved data will be lost.\n\nDo you want to quit?'):
        if messagebox.askokcancel(title, message):
            M.destroy()

    def rename_irradiation_name(self, box, parent, NAA, folder=os.path.join('data','irradiation')):
        old_name = box.get()
        if old_name != '' and os.path.exists(os.path.join(folder,f'{old_name}.irr')):
            width, height, xpos, ypos = box.winfo_width(), box.winfo_height(), box.winfo_rootx(), box.winfo_rooty()
            Ins = tk.Toplevel(parent)
            Ins.resizable(False, False)
            Ins.geometry(f'{width}x{height}+{xpos}+{ypos+height}')
            if sys.platform != 'darwin':
                Ins.overrideredirect(True)
            E_name = tk.Entry(Ins)
            E_name.pack(fill=tk.X)
            E_name.delete(0, tk.END)
            E_name.insert(0, old_name)
            E_name.focus_force()

            if sys.platform != 'darwin':
                Ins.bind('<FocusOut>', lambda e='<FocusOut>': Ins.destroy())
            E_name.bind('<Return>', lambda e='<Return>': self.check_accept_irradiation_rename(E_name, box, Ins, NAA, parent))

    def check_accept_irradiation_rename(self, E_name, box, Ins, NAA, parent, folder=os.path.join('data','irradiation')):
        #make effective the name change of a position
        ext = '.irr'
        reserved_names = [filename[:-len(ext)] for filename in os.listdir(folder) if filename[-len(ext):] == ext]
        if E_name.get().replace(' ','') != '' and E_name.get() not in reserved_names:
            os.rename(os.path.join(folder,f'{box.get()}{ext}'), os.path.join(folder,f'{E_name.get()}{ext}'))
            box['values'] = [filename[:-len(ext)] for filename in os.listdir(folder) if filename[-len(ext):] == ext]
            box.set(E_name.get())
            NAA.irradiation.irradiation_code = E_name.get()
            Ins.destroy()
            parent.infotask.configure(text='irradiation name updated')
        else:
            parent.infotask.configure(text='invalid name, try another one')

    def rename_calibration_name(self, box, parent, NAA, folder=os.path.join('data','characterization')):
        old_name = box.get()
        if old_name != '' and os.path.exists(os.path.join(folder,f'{old_name}.pos')):
            width, height, xpos, ypos = box.winfo_width(), box.winfo_height(), box.winfo_rootx(), box.winfo_rooty()
            Ins = tk.Toplevel(parent)
            Ins.resizable(False, False)
            Ins.geometry(f'{width}x{height}+{xpos}+{ypos+height}')
            if sys.platform != 'darwin':
                Ins.overrideredirect(True)
            E_name = tk.Entry(Ins)
            E_name.pack(fill=tk.X)
            E_name.delete(0, tk.END)
            E_name.insert(0, old_name)
            E_name.focus_force()

            if sys.platform != 'darwin':
                Ins.bind('<FocusOut>', lambda e='<FocusOut>': Ins.destroy())
            E_name.bind('<Return>', lambda e='<Return>': self.check_accept_calibration_rename(E_name, box, Ins, NAA, parent))
    
    def check_accept_calibration_rename(self, E_name, box, Ins, NAA, parent, folder=os.path.join('data','characterization')):
        #make effective the name change of a calibration
        ext = '.pos'
        reserved_names = [filename[:-len(ext)] for filename in os.listdir(folder) if filename[-len(ext):] == ext]
        if E_name.get().replace(' ','') != '' and E_name.get() not in reserved_names:
            os.rename(os.path.join(folder,f'{box.get()}{ext}'), os.path.join(folder,f'{E_name.get()}{ext}'))
            os.rename(os.path.join(folder,f'{box.get()}_log.txt'), os.path.join(folder,f'{E_name.get()}_log.txt'))
            os.rename(os.path.join(folder,f'{box.get()}.pkl'), os.path.join(folder,f'{E_name.get()}.pkl'))
            box['values'] = [filename[:-len(ext)] for filename in os.listdir(folder) if filename[-len(ext):] == ext]
            box.set(E_name.get())
            NAA.calibration.name = E_name.get()
            for spectrum in NAA.background:
                if spectrum.calibration is not None:
                    spectrum.calibration.name = E_name.get()
            for spectrum in NAA.standard_spectra:
                if spectrum.calibration is not None:
                    spectrum.calibration.name = E_name.get()
            for spectrum in NAA.sample_spectra:
                if spectrum.calibration is not None:
                    spectrum.calibration.name = E_name.get()
            Ins.destroy()
            parent.infotask.configure(text='calibration name updated')
        else:
            parent.infotask.configure(text='invalid name, try another one')

    def go_to_changeanalysisname(self, parent, NAA):
        if NAA.analysis_name is not None:
            old_name = NAA.analysis_name
        else:
            old_name = ''

        width, height, xpos, ypos = parent.analysisname_combobox.winfo_width(), parent.analysisname_combobox.winfo_height(), parent.analysisname_combobox.winfo_rootx(), parent.analysisname_combobox.winfo_rooty()
        Ins = tk.Toplevel(parent)
        Ins.resizable(False, False)
        Ins.geometry(f'{width}x{height}+{xpos}+{ypos+height}')
        if sys.platform != 'darwin':
            Ins.overrideredirect(True)
        E_name = tk.Entry(Ins)
        E_name.pack(fill=tk.X)
        E_name.delete(0, tk.END)
        E_name.insert(0, old_name)
        E_name.focus_force()

        if sys.platform != 'darwin':
            Ins.bind('<FocusOut>', lambda e='<FocusOut>': Ins.destroy())
        E_name.bind('<Return>', lambda e='<Return>': self.check_accept_analysis_rename(E_name, Ins, NAA, parent))

    def check_accept_analysis_rename(self, E_name, Ins, NAA, parent):
        if E_name.get().replace(' ','') != '' and E_name.get().replace(' ','') != NAA.analysis_name:
            NAA.analysis_name = E_name.get()
            parent.analysisname_combobox.configure(state='normal')
            parent.analysisname_combobox.delete(0, tk.END)
            parent.analysisname_combobox.insert(0, NAA.analysis_name)
            parent.analysisname_combobox.configure(state='readonly')
            Ins.destroy()
            parent.infotask.configure(text='analysis name updated')
        else:
            parent.infotask.configure(text='invalid name, try another one')

    def _spectrum_selection(self):
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() not in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    self.secondary_window.destroy()
                    self.secondary_window = None
            except Exception:
                self.secondary_window.destroy()
                self.secondary_window = None

    def _update_regular_selection(self, NAA, regular, standard_scale, sample_scale):
        if NAA.calibration is not None:
            if regular.get() == 1:
                standard_scale.variable.set(NAA.calibration.reference_calibration.distance)
                standard_scale.Scale.configure(state=tk.DISABLED)
                sample_scale.Scale.configure(state=tk.ACTIVE)
            elif regular.get() == 0:
                sample_scale.variable.set(NAA.calibration.reference_calibration.distance)
                sample_scale.Scale.configure(state=tk.DISABLED)
                standard_scale.Scale.configure(state=tk.ACTIVE)

    def select_calibration(self, box, NAA, regular, standard_scale, sample_scale):
        #function to effectively accept the selected calibration
        filename = box.get()
        if filename != '':
            NAA.calibration = naaobject.DetectorCalibration(filename)
        def_value = NAA.calibration.reference_calibration.distance
        distances_list = list(NAA.calibration.kedd_dict.keys()) + [def_value]
        standard_scale.set_values(distances_list, def_value)
        sample_scale.set_values(distances_list, def_value)
        regular.set(1)
        for spectrum in NAA.background:
            spectrum.calibration = NAA.calibration
        for spectrum in NAA.standard_spectra:
            spectrum.calibration = NAA.calibration
        for spectrum in NAA.sample_spectra:
            spectrum.calibration = NAA.calibration
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() not in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    self.secondary_window.destroy()
                    self.secondary_window = None
            except Exception:
                self.secondary_window.destroy()
                self.secondary_window = None

    def delete_spectrum_file(self, box, spectrum_list, M_selector, snumber, infos):
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                        self.secondary_window = None
                    else:
                        return
                else:
                    self.secondary_window.destroy()
                    self.secondary_window = None
            except Exception:
                self.secondary_window.destroy()
                self.secondary_window = None
        if M_selector.get() == 0:
            if box.current() >= 0:
                if messagebox.askyesno(title='Remove spectrum', message=f'\nAre you sure to remove spectrum: {box.get()} from selection?\n'):
                    filename = box.get()
                    spectrum_list.pop(box.current())
                    box['values'] = [spectrum.filename() for spectrum in spectrum_list]
                    box.set('')
                    snumber.configure(text=f'{len(spectrum_list)}')
                    infos.configure(text=f'{filename} spectrum removed')
            else:
                infos.configure(text='no spectrum selected')
        else:
            if messagebox.askyesno(title='Remove spectra', message='\nAre you sure to remove all spectra from the selected type?\n'):
                lenght = len(spectrum_list)
                for _ in range(lenght):
                    spectrum_list.pop()
                box['values'] = [spectrum.filename() for spectrum in spectrum_list]
                box.set('')
                snumber.configure(text='0')
                infos.configure(text=f'{lenght} spectra removed')

    def delete_calibration(self, box, NAA, M_info, M_standard_pos, M_sample_pos, M_selector, folder=os.path.join('data','characterization')):
        #delete detector characterization entry
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                        self.secondary_window = None
                    else:
                        return
                else:
                    self.secondary_window.destroy()
                    self.secondary_window = None
            except Exception:
                self.secondary_window.destroy()
                self.secondary_window = None
        if box.get() != '' and os.path.exists(os.path.join(folder,f'{box.get()}.pos')):
            if messagebox.askyesno(title='Delete detector characterization', message=f'\nAre you sure to delete characterization: {box.get()}?\n'):
                try:
                    os.remove(os.path.join(folder, f'{box.get()}_log.txt'))
                except:
                    pass
                try:
                    os.remove(os.path.join(folder, f'{box.get()}.pkl'))
                except:
                    pass
                try:
                    os.remove(os.path.join(folder, f'{box.get()}.pos'))
                    box.set('')
                    NAA.calibration = None
                except:
                    NAA.calibration = None
                    M_info.configure(text='removed')
                else:
                    M_info.configure(text='removed from disk')
                self.get_calibration_files(box, NAA)
                box.set('')
                M_standard_pos.set_values([])
                M_sample_pos.set_values([])
                M_selector.set(-1)
        else:
            M_info.configure(text='no characterization selected')

    def get_calibration_files(self, box, NAA, folder=os.path.join('data', 'characterization')):
        #recall available detector characterization
        ext = '.pos'
        box['values'] = [filename[:-len(ext)] for filename in os.listdir(folder) if filename[-len(ext):] == ext]
        #box.set('')

    def select_irradiation(self, box, NAA):
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() not in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    self.secondary_window.destroy()
                    self.secondary_window = None
            except Exception:
                self.secondary_window.destroy()
                self.secondary_window = None
        if box.get() != '':
            NAA.irradiation = naaobject.Irradiation(filename=box.get())

    def delete_irradiation(self, box, NAA, M_info, folder=os.path.join('data','irradiation')):
        #delete irradiation entry
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                        self.secondary_window = None
                    else:
                        return
                else:
                    self.secondary_window.destroy()
                    self.secondary_window = None
            except Exception:
                self.secondary_window.destroy()
                self.secondary_window = None
        if box.get() != '' and os.path.exists(os.path.join(folder,f'{box.get()}.irr')):
            if messagebox.askyesno(title='Delete irradiation', message=f'\nAre you sure to delete irradiation: {box.get()}?\n'):
                try:
                    os.remove(os.path.join(folder, f'{box.get()}.irr'))
                    self.get_irradiation_files(box, NAA)
                    box.set('')
                    NAA.irradiation = None
                except:
                    NAA.irradiation = None
                    M_info.configure(text='removed')
                else:
                    M_info.configure(text='removed from disk')
        else:
            M_info.configure(text='no irradiation selected')

    def get_irradiation_files(self, box, NAA, folder=os.path.join('data', 'irradiation')):
        #recall available irradiation
        ext = '.irr'
        box['values'] = [filename[:-len(ext)] for filename in os.listdir(folder) if filename[-len(ext):] == ext]
        #box.set('')
        #NAA.irradiation = None

    def go_to_settings(self, M, NAA):
        #open the settings window
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        SettingsWindow(self.secondary_window, NAA, M)

    def go_to_browse_databases(self, M, NAA):
        #open the window to browse and manage k0, sample and hopefully other databases
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        DatabasesWindow(self.secondary_window, NAA, M)

    def go_to_display_irradiation(self, M, NAA):
        #open the window to display the irradiation information
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        if NAA.irradiation is not None:
            self.secondary_window = tk.Toplevel(M)
            DisplayIrradiationWindow(self.secondary_window, NAA)
        else:
            M.infotask.configure(text='no irradiation is selected!')

    def go_to_display_calibration(self, M, NAA):
        #open the window to display the calibration information
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        if NAA.calibration is not None:
            self.secondary_window = tk.Toplevel(M)
            DisplayCalibrationWindow(self.secondary_window, NAA, M)
        else:
            M.infotask.configure(text='no detector characterization is selected!')

    def go_to_sampledefinition(self, M, NAA, box, button='background'):
        #open the window to modify sample information
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        idx = box.current()
        if idx >= 0:
            self.secondary_window = tk.Toplevel(M)
            if button == 'background':
                SampleWindow(self.secondary_window, NAA.background, idx, NAA.settings_dict['non certified standard uncertainties'])
            elif button == 'sample':
                SampleWindow(self.secondary_window, NAA.sample_spectra, idx, NAA.settings_dict['non certified standard uncertainties'])
            elif button == 'standard':
                SampleWindow(self.secondary_window, NAA.standard_spectra, idx, NAA.settings_dict['non certified standard uncertainties'])
        else:
            M.infotask.configure(text='no spectrum selected')

    def go_to_openspectra(self, M, NAA, button):
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))#,('HyperLab ASC file','*.asc'),('CHN spectrum file','*.chn'))
        if button == 'background':
            limit_s = NAA.settings_dict['sample statistical uncertainty limit']
            try:
                output = askopenfilename(parent=M, title=f'Open {button}',filetypes=filetypes)
                output = tuple([output])
            except TypeError:
                output = ()
        elif button == 'standard':
            limit_s = NAA.settings_dict['standard statistical uncertainty limit']
            try:
                output = askopenfilename(parent=M, title=f'Open {button}',filetypes=filetypes)
                output = tuple([output])
            except TypeError:
                output = ()
        else:
            limit_s = NAA.settings_dict['sample statistical uncertainty limit']
            try:
                output = tuple(askopenfilenames(parent=M, title=f'Open {button}',filetypes=filetypes))
            except TypeError:
                output = ()
        notes = []
        efficiency = NAA.calibration
        if len(output) > 0:
            M.infotask.configure(text=f'importing {len(output)} {button} spectra')
            M.progress['value'] = 0
            M.progress['maximum'] = len(output)
            M.progress.update()
        for filename in output:
            if filename != '' and filename != ():
                peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=NAA.settings_dict['look for spectrum file'])
                if result == True:
                    Spectrum = naaobject.SpectrumAnalysis(identity=f'{button}', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=filename, source=source, efficiency=efficiency, energy_tolerance=NAA.settings_dict['energy tolerance'], database_k0=NAA.database)
                    NAA._add_spectrum(Spectrum, button)
                else:
                    notes.append(note)
            M.progress['value'] += 1
            M.progress.update()
        M.infotask.configure(text='imported')
        if button == 'background':
            M.background_combobox['values'] = [spectrum.filename() for spectrum in NAA.background]
            if len(M.background_combobox['values']) > 0:
                M.background_combobox.set(M.background_combobox['values'][-1])
            else:
                M.background_combobox.set('')
            M.background_spectra.configure(text=f'{len(NAA.background)}')
        elif button == 'standard':
            M.standard_combobox['values'] = [spectrum.filename() for spectrum in NAA.standard_spectra]
            if len(M.standard_combobox['values']) > 0:
                M.standard_combobox.set(M.standard_combobox['values'][-1])
            else:
                M.standard_combobox.set('')
            M.standard_spectra.configure(text=f'{len(NAA.standard_spectra)}')
        elif button == 'sample':
            M.sample_combobox['values'] = [spectrum.filename() for spectrum in NAA.sample_spectra]
            if len(M.sample_combobox['values']) > 0:
                M.sample_combobox.set(M.sample_combobox['values'][-1])
            else:
                M.sample_combobox.set('')
            M.sample_spectra.configure(text=f'{len(NAA.sample_spectra)}')
        if notes != []:
            self.secondary_window = tk.Toplevel(M)
            InformationWindow(self.secondary_window, notes)

    def go_to_peaklist(self, M, NAA, button):
        idx = -1
        spectrum = None
        background = None
        if button == 'background':
            idx = M.background_combobox.current()
            if idx >= 0:
                spectrum = NAA.background[idx]
        elif button == 'standard':
            idx = M.standard_combobox.current()
            if idx >= 0:
                spectrum = NAA.standard_spectra[idx]
            idx = M.background_combobox.current()
            if idx >= 0:
                background = NAA.background[idx]
        elif button == 'sample':
            idx = M.sample_combobox.current()
            if idx >= 0:
                spectrum = NAA.sample_spectra[idx]
            idx = M.background_combobox.current()
            if idx >= 0:
                background = NAA.background[idx]
        if spectrum is not None:
            local_peak_list = nest_list(spectrum.peak_list, NAA.settings_dict['page height'])
            local_suspected = nest_list(spectrum.suspected, NAA.settings_dict['page height'])
            if self.secondary_window is not None:
                try:
                    if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                        if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                            self.secondary_window.destroy()
                        else:
                            return
                    else:
                        self.secondary_window.destroy()
                except Exception:
                    self.secondary_window.destroy()
            self.secondary_window = tk.Toplevel(M)
            PeaklistWindow(self.secondary_window, spectrum, local_peak_list, local_suspected, NAA.settings_dict['page height'], background, NAA.database)

    def go_to_irradiation(self, M, NAA):
        #open the window for irradiation record
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        IrradiationWindow(self.secondary_window, NAA, M)

    def go_to_fluxevaluation(self, M, NAA):
        #open the window for flux measurements
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        FluxEvaluationWindow(self.secondary_window, NAA, M)

    def go_to_fluxgradientevaluation(self, M, NAA):
        #open the window for flux gradient measurements
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        FluxGradientEvaluationWindow(self.secondary_window, NAA, M)

    def go_to_calibration(self, M, NAA):
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        DetectorCharacterizationWindow(self.secondary_window, NAA, M)

    def go_to_maximum_effort(self, M, NAA):
        if self.secondary_window is not None:
            self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        EffortWindow(self.secondary_window, NAA, M)

    def go_to_detectionlimits(self, M, NAA):
        #open the window to select element for detection limit evaluation
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        DetectionLimitWindow(self.secondary_window, NAA, M)

    def go_to_elaboration(self, M, NAA):
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        ElaborationProcess(self.secondary_window, NAA, M)

    def go_to_credits(self, M):
        #maybe useful information
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        CreditsWindow(self.secondary_window)

    def go_to_workinprogress(self, M, NAA):
        if self.secondary_window is not None:
            self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        NotImplementedYet(self.secondary_window)

    def go_to_save(self, M, NAA, button):
        #save the current situation
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        position = button.winfo_width(), button.winfo_height(), button.winfo_rootx(), button.winfo_rooty()
        SaveWindow(self.secondary_window, NAA, M, position)

    def go_to_load(self, M, NAA, button):
        #load the current situation
        if self.secondary_window is not None:
            try:
                if self.secondary_window.title() in ('Detector characterization', 'Flux evaluation - Bare triple monitor', 'Flux gradient evaluation'):
                    if messagebox.askyesno(title='Open new window', message=f'This action will close the {self.secondary_window.title()} window.\nMake sure you saved your progresses.\nDo you want to continue?\n', parent=self.secondary_window):
                        self.secondary_window.destroy()
                    else:
                        return
                else:
                    self.secondary_window.destroy()
            except Exception:
                self.secondary_window.destroy()
        self.secondary_window = tk.Toplevel(M)
        position = button.winfo_width(), button.winfo_height(), button.winfo_rootx(), button.winfo_rooty()
        LoadWindow(self.secondary_window, NAA, M, position)


def retrieve_files(folder,ext):
    return [filename for filename in os.listdir(folder) if filename[-len(ext):].lower() == ext]


def nest_list(original_list, step):
    nested_list = []
    index = 0
    while index < len(original_list):
        try:
            p_list = original_list[index:index + step]
        except IndexError:
            p_list = original_list[index:]
        index += step
        if p_list != []:
            nested_list.append(p_list)
    if nested_list != []:
        return nested_list
    else:
        return [[]]


class InformationWindow:
    def __init__(self, parent, textlist):
        parent.title('Information')
        parent.resizable(False, False)
        tk.Label(parent, text='').pack()
        tk.Label(parent, text='\n'.join(textlist)).pack(anchor=tk.W, padx=5)
        tk.Label(parent, text='').pack()


class SaveWindow:
    def __init__(self, parent, NAA, M, position):
        parent.title('Save current situation')
        parent.resizable(False, False)
        width, height, xpos, ypos = position
        parent.geometry(f'{width*7}x{height*2}+{xpos}+{ypos+height}')
        tk.Label(parent, text='insert a filename for the save', anchor=tk.W).pack(anchor=tk.W, padx=5)
        mframe = tk.Frame(parent)
        self.filesavename = tk.Entry(mframe)
        self.filesavename.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if NAA.analysis_name is not None:
            self.filesavename.delete(0, tk.END)
            self.filesavename.insert(0, NAA.analysis_name)
        self.variable_date = tk.IntVar(parent)
        CB = tk.Checkbutton(mframe, text='date', variable=self.variable_date, onvalue=1, offvalue=0)
        CB.pack(side=tk.LEFT)
        self.variable_date.set(0)
        logo_save = tk.PhotoImage(data=gui_things.sparadrap)
        B_confirm_save_elaboration = tk.Button(mframe, image=logo_save, command=lambda: self.confirm_save(M, NAA, parent))
        B_confirm_save_elaboration.pack(side=tk.RIGHT)
        B_confirm_save_elaboration.image = logo_save
        mframe.pack(fill=tk.X, expand=True, padx=5)
        self.filesavename.focus()

        try:
            float(M.Deltad_standard_spinbox.get())
            dd_std = M.Deltad_standard_spinbox.get()
        except ValueError:
            dd_std = '0.0'
        try:
            float(M.uDeltad_standard_spinbox.get())
            udd_std = M.uDeltad_standard_spinbox.get()
        except ValueError:
            udd_std = '0.0'
        NAA.standard_position = (M.standard_position.get(), dd_std, udd_std)

        try:
            float(M.Deltad_sample_spinbox.get())
            dd_smp = M.Deltad_sample_spinbox.get()
        except ValueError:
            dd_smp = '0.0'
        try:
            float(M.uDeltad_sample_spinbox.get())
            udd_smp = M.uDeltad_sample_spinbox.get()
        except ValueError:
            udd_smp = '0.0'
        NAA.sample_position = (M.sample_position.get(), dd_smp, udd_smp)
        if M.regular_calibration_variable.get() >= 0:
            NAA.position_selector = M.regular_calibration_variable.get()
        NAA.detection_elements = M.detection_elements
        nbuds = len(NAA.budgets)
        for _ in range(nbuds):
            NAA.budgets.pop()

    def confirm_save(self, M, NAA, parent):
        if self.filesavename.get().replace(' ','') == '' and self.variable_date.get() == 0:
            M.infotask.configure(text='invalid name!')
        else:
            if self.variable_date.get() == 1:
                today = datetime.datetime.today()
                filename = f'{today.strftime("%Y%m%d")}_{self.filesavename.get()}'
            else:
                filename = f'{self.filesavename.get()}'
            with open(os.path.join(os.path.join('data','saves'),f'{filename}.sav'),'wb') as filesave:
                pickle.dump(NAA, filesave)
            parent.destroy()
            M.infotask.configure(text='saved!')


class LoadWindow:
    def __init__(self, parent, NAA, M, position, folder=os.path.join('data', 'saves')):
        parent.title('Load')
        parent.resizable(False, False)
        width, height, xpos, ypos = position
        parent.geometry(f'{width*7}x{int(height*2.5)}+{xpos}+{ypos+height}')
        loadable_files = [filename for filename in os.listdir(folder) if filename[-4:]== '.sav']
        infos = tk.Label(parent, text='', anchor=tk.W)
        CB_load = ttk.Combobox(parent, state='readonly')
        CB_load['values'] = loadable_files[::-1]
        CB_load.pack(anchor=tk.W, fill=tk.X, expand=True, padx=5)
        mframe = tk.Frame(parent)
        
        logo_explore_virtually = tk.PhotoImage(data=gui_things.battery)
        B_confirm_load_elaboration = gui_things.Button(mframe, image=logo_explore_virtually, hint='recall saved file', hint_destination=infos, command=lambda: self.how_to_solve_the_loading_problem(NAA, CB_load, M, parent))
        B_confirm_load_elaboration.pack(side=tk.LEFT)
        B_confirm_load_elaboration.image = logo_explore_virtually

        logo_delete = tk.PhotoImage(data=gui_things.none)
        B_delete_save = gui_things.Button(mframe, image=logo_delete, hint='delete saved file', hint_destination=infos, command=lambda: self.delete_savefile(CB_load, parent))
        B_delete_save.pack(side=tk.LEFT)
        B_delete_save.image = logo_delete
        mframe.pack(anchor=tk.W, padx=5, pady=5)

        infos.pack(anchor=tk.W)

    def delete_savefile(self, CB, parent, folder=os.path.join('data','saves')):
        if CB.get() != '':
            if messagebox.askyesno(title=f'Delete saved file', message=f'\nAre you sure to delete savefile {CB.get()}?\n', parent=parent):
                try:
                    os.remove(os.path.join(folder, f'{CB.get()}'))
                except:
                    pass
                else:
                    CB['values'] = [filename for filename in os.listdir(folder) if filename[-4:] == '.sav']
                    CB.set('')

    def _overwrite_settings(self, saved_NAA, NAA):
        with open(os.path.join('data','k0-set.cfg'), 'w') as settingsfile:
            settingsfile.write(f'database <#> {saved_NAA.settings_dict["database"]}\nenergy tolerance <#> {saved_NAA.settings_dict["energy tolerance"]}\npage height <#> {NAA.settings_dict["page height"]}\nmax allowed calibration uncertainty <#> {saved_NAA.settings_dict["max allowed calibration uncertainty"]}\ncalibs statistical uncertainty limit <#> {saved_NAA.settings_dict["calibs statistical uncertainty limit"]}\nstandard statistical uncertainty limit <#> {saved_NAA.settings_dict["standard statistical uncertainty limit"]}\nsample statistical uncertainty limit <#> {saved_NAA.settings_dict["sample statistical uncertainty limit"]}\nnon certified standard uncertainties <#> {saved_NAA.settings_dict["non certified standard uncertainties"]}\ndefault tc&tl uncertainties <#> {saved_NAA.settings_dict["default tc&tl uncertainties"]}\ndefault td uncertainty <#> {saved_NAA.settings_dict["default td uncertainty"]}\nlook for spectrum file <#> {int(saved_NAA.settings_dict["look for spectrum file"])}')

    def how_to_solve_the_loading_problem(self, NAA, CB, M, parent, folder=os.path.join('data','saves')):
        saved_NAA = None
        if CB.get() != '':
            with open(os.path.join(folder,f'{CB.get()}'), 'rb') as f:
                saved_NAA = pickle.load(f)
        #inspect saved_NAA
        if saved_NAA is not None:
            #irradiation, calibration
            if messagebox.askyesno(title='Load data', message=f'\nAre you sure to load data from {CB.get()} savefile?\nthe k0-INRIM will be restarted!\n', parent=parent):
                if saved_NAA.settings_dict != NAA.settings_dict:
                    self._overwrite_settings(saved_NAA, NAA)
                M.destroy()
                main_script(saved_NAA)


class ValidationWindow:
    def __init__(self, parent, dataset, analysis_name):
        parent.title(f'Validation of results for {analysis_name}')
        parent.resizable(False, False)

        self.subwindow = None
        self.color_scheme = ['#000000', '#FFFFFF', '#A80000', '#3342C4', '#FFC400', '#9362C4', '#62BA27', '#FB6400', '#733381', '#85582C', '#DE5283', '#A4DDED']
        self.show_legend = False
        self.legend_positions = ('center', 'upper right', 'upper center', 'upper left', 'center left', 'lower left', 'lower center', 'lower right', 'right')
        self.legend_position_index = 0
        self.show_ticklabels = True
        self.ticklabels = []
        self.x1_grid = True

        binfoline = tk.Label(parent, text='')

        finformation = tk.Frame(parent)
        tk.Label(finformation, text='end of irradiation:').grid(row=0, column=0, sticky=tk.W)
        tk.Label(finformation, text=dataset.iloc[0,0].strftime("%d/%m/%Y %H:%M:%S")).grid(row=0, column=1, sticky=tk.W)
        tk.Frame(finformation).grid(row=0, column=2, padx=15)
        tk.Label(finformation, text='channel:').grid(row=0, column=3, sticky=tk.W)
        tk.Label(finformation, text=dataset.iloc[0,1]).grid(row=0, column=4, sticky=tk.W)
        tk.Frame(finformation).grid(row=0, column=5, padx=15)
        tk.Label(finformation, text='duration:').grid(row=0, column=6, sticky=tk.W)
        tk.Label(finformation, text=self.readable_time(dataset.iloc[0,4])).grid(row=0, column=7, sticky=tk.W)
        tk.Frame(finformation).grid(row=0, column=8, padx=15)

        finformation.pack(anchor=tk.W, padx=5, pady=5)

        ftext = tk.Frame(parent)

        tk.Label(ftext, text=f'{"target".ljust(8)}{"emitter".ljust(20)}{"w / g g-1".ljust(13)}{"u(w) / g g-1".ljust(15)}{"z / 1".ljust(9)}{"reference".ljust(15)}', anchor=tk.W, font=('Courier', 11)).grid(row=0, column=0, columnspan=6, sticky=tk.EW)

        stext = gui_things.ScrollableText(ftext, data='\n'.join([f'{target.ljust(8)}{emitter.ljust(20)}{format(wvalue, ".2e").ljust(13)}{format(uwvalue, ".1e").ljust(15)}{format(zvalue, ".1f").ljust(9)}{self.shorten(reference_name).ljust(15)}' for target, emitter, wvalue, uwvalue, zvalue, reference_name in zip(dataset["target"], dataset["emitter"], dataset["value"], dataset["uncertainty"], dataset["z"], dataset["certificate"])]), height=20, width=80, font=('Courier', 11))
        stext.grid(row=1, column=0, columnspan=6, sticky=tk.EW)
        ftext.pack(anchor=tk.NW, padx=5, pady=5)

        bframe = tk.Frame(parent)
        logo_z_results = tk.PhotoImage(data=gui_things.resulti)
        B_z_results = gui_things.Button(bframe, image=logo_z_results, hint='plot z values for all results!', hint_destination=binfoline, command=lambda: self.which_to_plot(parent, dataset))
        B_z_results.pack(side=tk.LEFT)
        B_z_results.image = logo_z_results

        logo_elem_results = tk.PhotoImage(data=gui_things.graph)
        B_elem_results = gui_things.Button(bframe, image=logo_elem_results, hint='plot per element agreement with reference!', hint_destination=binfoline, command=lambda: self.which_to_plot(parent, dataset, which='S'))
        B_elem_results.pack(side=tk.LEFT)
        B_elem_results.image = logo_elem_results
        bframe.pack(anchor=tk.W, padx=5)

        binfoline.pack(anchor=tk.W, padx=5)

    def readable_time(self, time, LIMIT1=120000, LIMIT2=3500):
        if time > LIMIT1:
            return f'{time/86400:.2f} d'
        elif time > LIMIT2:
            return f'{time/3600:.2f} h'
        else:
            return f'{time:.0f} s'

    def shorten(self, item, limit=15):
        if len(item) >= limit:
            return f'{item[:limit-2]}..'
        else:
            return item

    def which_to_plot(self, parent, dataset, which='Z'):
        if self.subwindow is not None:
            self.subwindow.destroy()
        self.subwindow = tk.Toplevel(parent)
        if which == 'Z':
            self.subwindow.title('Plot of z values')
            self.plot_z(dataset)
        else:
            self.subwindow.title('Plot of agreements with reference')
            self.plot_s(dataset)

    def plot_z(self, dataset):
        visual_frame = tk.Frame(self.subwindow)
        fig = Figure(figsize=(8, 5.5), dpi=100)
        axes_Q = fig.add_subplot(111)
        ax2 = None
        Figur = tk.Frame(visual_frame)
        Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        canvas = FigureCanvasTkAgg(fig, master=Figur)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.draw_plotz(dataset, axes_Q, fig, canvas)
        visual_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        infolabel = tk.Label(self.subwindow)
        button_frame = tk.Frame(self.subwindow)

        ylimit_setter = gui_things.FSlider(button_frame, decimals=1, default=5, hint='move the limits of y axis', hint_destination=infolabel, from_=2.5, to=7.0, resolution=0.5)
        ylimit_setter.pack(side=tk.LEFT)
        logo_confirm = tk.PhotoImage(data=gui_things.beye)
        B_adjust_yaxis = gui_things.Button(button_frame, image=logo_confirm, hint='adjust left y axis', hint_destination=infolabel, command=lambda: self.adjust_ylim(axes_Q, fig, canvas, ylimit_setter))
        B_adjust_yaxis.pack(side=tk.LEFT)
        B_adjust_yaxis.image = logo_confirm
        logo_tight = tk.PhotoImage(data=gui_things.tight_layout)
        B_tight_axis = gui_things.Button(button_frame, image=logo_tight, hint='reset axes when resized', hint_destination=infolabel, command=lambda: self.tight(fig, canvas))
        B_tight_axis.pack(side=tk.LEFT)
        B_tight_axis.image = logo_tight
        logo_legend = tk.PhotoImage(data=gui_things.legend)
        B_show_legend = gui_things.Button(button_frame, image=logo_legend, hint='show/hide the legend', hint_destination=infolabel, command=lambda: self.legend(axes_Q, fig, canvas))
        B_show_legend.pack(side=tk.LEFT)
        B_show_legend.image = logo_legend
        logo_ticks = tk.PhotoImage(data=gui_things.ticks)
        B_show_ticks = gui_things.Button(button_frame, image=logo_ticks, hint='show/hide ticklabels', hint_destination=infolabel, command=lambda: self.tickinfos(axes_Q, fig, canvas))
        B_show_ticks.pack(side=tk.LEFT)
        B_show_ticks.image = logo_ticks
        logo_save_figure = tk.PhotoImage(data=gui_things.sparadrap)
        B_save = gui_things.Button(button_frame, image=logo_save_figure, hint='save figure', hint_destination=infolabel, command = lambda : self.savefigure(fig, self.subwindow, infolabel))
        B_save.pack(side=tk.LEFT)
        B_save.image = logo_save_figure

        button_frame.pack(anchor=tk.W, padx=5)
        infolabel.pack(anchor=tk.W, padx=5)

    def adjust_ylim(self, ax, fig, canvas, yslider):
        ax.set_ylim(-yslider.get(), yslider.get())
        self.tight(fig, canvas)

    def tight(self, fig, canvas):
        fig.tight_layout()
        canvas.draw()

    def legend(self, ax, fig, canvas):
        if self.show_legend:
            self.show_legend = False
            ax.legend().remove()
        else:
            self.show_legend = True
            try:
                self.legend_position_index += 1
                self.legend_positions[self.legend_position_index]
            except IndexError:
                self.legend_position_index = 0
            ax.legend(loc=self.legend_positions[self.legend_position_index])
        self.tight(fig, canvas)

    def tickinfos(self, ax, fig, canvas):
        if self.show_ticklabels:
            self.show_ticklabels = False
            ax.set_xticklabels(['' for item in self.ticklabels])
        else:
            self.show_ticklabels = True
            ax.set_xticklabels(self.ticklabels, rotation=90)
        self.tight(fig, canvas)

    def savefigure(self, fig, parent, infolabel):
        filetypes = (('PNG image','*.png'),)
        filename = asksaveasfilename(parent=parent, title='Save figure',filetypes=filetypes)
        if filename != '':
            fig.savefig(filename, dpi=1000)
        infolabel.configure(text='file saved')

    def draw_plotz(self, dataset, ax1, fig, canvas, ylim=5, ax2=None):
        ax1.clear()
        if ax2 is not None:
            ax2.clear()

        origins = set(dataset['certificate'])

        i_range = len(self.ticklabels)
        for i in range(i_range):
            self.ticklabels.pop(0)

        target_labels = []
        n_index = 0
        n_color = 0

        for orig in sorted(origins):
            s_origin = dataset['certificate'] == orig
            part_data = dataset[s_origin]
            if len(part_data.index) > 0:
                try:
                    facecolor = self.color_scheme[n_color]
                except IndexError:
                    n_color = 0
                    facecolor = self.color_scheme[n_color]
                x1 = np.arange(n_index, n_index + len(part_data['target']))
                ax1.bar(x1, part_data['z'], color=facecolor, edgecolor='#000000', linewidth=0.5, alpha=0.85, label=orig)
                n_color += 1
                try:
                    n_index = np.max(x1) + 1
                except TypeError:
                    pass
                self.ticklabels += list(part_data['emitter'].astype(str) + ' ' + part_data['sample'].astype(str))
                target_labels += list(part_data['target'])

        
        outliers = (dataset['z'] > 3) | (dataset['z'] < -3)
        questionable = np.sum(((dataset['z'] > 2) & (dataset['z'] < 3)) | ((dataset['z'] < -2) & (dataset['z'] > -3)))
        if len(dataset['z'].index) == 0:
            title = f"{len(dataset['z'])} data"
        else:
            title = f"{len(dataset['z'])} data, {np.sum(outliers)} outliers, {questionable} questionable values (" + r'$2\leq \left|x\right| \leq 3$' + f')'#, average = {np.average(dataset[~outliers]["z"]):.2f}'

        x_concat = np.arange(0, n_index)
        xmax = len(x_concat)
        if xmax == 0:
            xmax = 1
        xx = np.arange(-1,xmax+1)

        ax1.fill_between(xx, -3, -2, facecolor='green', alpha=0.3)
        ax1.fill_between(xx, 3, 2, facecolor='green', alpha=0.3)
        ax1.set_xlim(np.min(xx),np.max(xx))
        ax1.set_xticks(x_concat)
        ax1.set_xticklabels(self.ticklabels, rotation=90)

        rects = ax1.patches

        for rect, label in zip(rects, target_labels):
            height = rect.get_height()
            if height > ylim - ylim/10:
                where = (rect.get_x() + rect.get_width() / 2, ylim -0.5)
            elif height < -ylim + ylim/10:
                where = (rect.get_x() + rect.get_width() / 2, -ylim + 0.5)
            elif height > 0:
                where = (rect.get_x() + rect.get_width() / 2, height + 0.25)
            else:
                where = (rect.get_x() + rect.get_width() / 2, height - 0.5)
            ax1.text(where[0], where[1], label, ha="center", va="bottom", rotation=90)

        ax1.set_ylim(-ylim, ylim)
        ax1.fill_between(xx, -3, -7, facecolor='red', alpha=0.4)
        ax1.fill_between(xx, 3, 7, facecolor='red', alpha=0.4)
        ax1.set_title(title)
        ax1.set_ylabel(r'$z_\mathrm{score}$ / 1')

        self.tight(fig,canvas)

    def button_minus(self, element_list, dataset, axes_Q, ax2, fig, canvas, B_left, B_right):
        plus = element_list[self.element_index]
        if self.element_index == 0:
            self.element_index = len(element_list) - 1
        else:
            self.element_index -= 1
        element = element_list[self.element_index]
        self.draw_plots(element, dataset, axes_Q, ax2, fig, canvas)

        go_to_minus, go_to_plus = f'go to {element_list[self.element_index - 1]}', f'go to {plus}'

        B_left.hint = go_to_minus
        B_right.hint = go_to_plus
        B_left.event_generate("<Leave>")
        B_left.event_generate("<Enter>")

    def button_plus(self, element_list, dataset, axes_Q, ax2, fig, canvas, B_left, B_right):
        minus = element_list[self.element_index]
        if self.element_index + 1 == len(element_list):
            self.element_index = 0
        else:
            self.element_index += 1
        element = element_list[self.element_index]
        self.draw_plots(element, dataset, axes_Q, ax2, fig, canvas)

        try:
            plus = element_list[self.element_index + 1]
        except IndexError:
            plus = element_list[0]

        go_to_minus, go_to_plus = f'go to {minus}', f'go to {plus}'

        B_left.hint = go_to_minus
        B_right.hint = go_to_plus
        B_right.event_generate("<Leave>")
        B_right.event_generate("<Enter>")

    def switch_axis(self, ax1, ax2, fig, canvas):
        if self.x1_grid:
            self.x1_grid = False
            ax1.grid(False, axis='y')
            ax2.grid(True, axis='y')
        else:
            self.x1_grid = True
            ax1.grid(True, axis='y')
            ax2.grid(False, axis='y')
        self.tight(fig, canvas)

    def plot_s(self, dataset):
        self.show_ticklabels = True
        element_list = sorted(set(dataset['target']))
        self.element_index = 0
        element = element_list[self.element_index]

        visual_frame = tk.Frame(self.subwindow)
        fig = Figure(figsize=(8, 5.5), dpi=100)
        axes_Q = fig.add_subplot(111)
        ax2 = axes_Q.twinx()
        Figur = tk.Frame(visual_frame)
        Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        canvas = FigureCanvasTkAgg(fig, master=Figur)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.draw_plots(element, dataset, axes_Q, ax2, fig, canvas)
        visual_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=True)
        infolabel = tk.Label(self.subwindow)
        button_frame = tk.Frame(self.subwindow)
        try:
            plus = element_list[self.element_index + 1]
        except IndexError:
            plus = element_list[0]
        go_to_minus, go_to_plus = f'go to {element_list[self.element_index - 1]}', f'go to {plus}'

        logo_previous_plot = tk.PhotoImage(data=gui_things.previous)
        B_left = gui_things.Button(button_frame, image=logo_previous_plot, hint=go_to_minus, hint_destination=infolabel)
        B_left.pack(side=tk.LEFT)
        B_left.image = logo_previous_plot
        logo_following_plot = tk.PhotoImage(data=gui_things.following)
        B_right = gui_things.Button(button_frame, image=logo_following_plot, hint=go_to_plus, hint_destination=infolabel)
        B_right.pack(side=tk.LEFT)
        B_right.image = logo_following_plot

        logo_switch = tk.PhotoImage(data=gui_things.grid)
        B_switch_axis = gui_things.Button(button_frame, image=logo_switch, hint='switch axis of y grid', hint_destination=infolabel, command=lambda: self.switch_axis(axes_Q, ax2, fig, canvas))
        B_switch_axis.pack(side=tk.LEFT)
        B_switch_axis.image = logo_switch

        BF_opt = tk.Frame(button_frame)
        logo_tight_axis = tk.PhotoImage(data=gui_things.ddistance)
        B_tight_axis = gui_things.Button(button_frame, image=logo_tight_axis, hint='adjust right axis limits', hint_destination=infolabel, command = lambda : self.get_tight_axis(axes_Q, ax2, fig, canvas, BF_opt, infolabel))
        B_tight_axis.pack(side=tk.LEFT)
        B_tight_axis.image = logo_tight_axis
        BF_opt.pack(side=tk.LEFT)

        logo_tight = tk.PhotoImage(data=gui_things.tight_layout)
        B_tight_axis = gui_things.Button(button_frame, image=logo_tight, hint='reset axes when resized', hint_destination=infolabel, command=lambda: self.tight(fig, canvas))
        B_tight_axis.pack(side=tk.LEFT)
        B_tight_axis.image = logo_tight
        logo_legend = tk.PhotoImage(data=gui_things.legend)
        B_show_legend = gui_things.Button(button_frame, image=logo_legend, hint='show/hide the legend', hint_destination=infolabel, command=lambda: self.legend(axes_Q, fig, canvas))
        B_show_legend.pack(side=tk.LEFT)
        B_show_legend.image = logo_legend
        logo_ticks = tk.PhotoImage(data=gui_things.ticks)
        B_show_ticks = gui_things.Button(button_frame, image=logo_ticks, hint='show/hide ticklabels', hint_destination=infolabel, command=lambda: self.tickinfos(axes_Q, fig, canvas))
        B_show_ticks.pack(side=tk.LEFT)
        B_show_ticks.image = logo_ticks
        logo_save_figure = tk.PhotoImage(data=gui_things.sparadrap)
        B_save = gui_things.Button(button_frame, image=logo_save_figure, hint='save figure', hint_destination=infolabel, command = lambda : self.savefigure(fig, self.subwindow, infolabel))
        B_save.pack(side=tk.LEFT)
        B_save.image = logo_save_figure

        button_frame.pack(anchor=tk.SW, padx=5)
        infolabel.pack(anchor=tk.W, padx=5)

        B_left.configure(command = lambda : self.button_minus(element_list, dataset, axes_Q, ax2, fig, canvas, B_left, B_right))
        B_right.configure(command = lambda : self.button_plus(element_list, dataset, axes_Q, ax2, fig, canvas, B_left, B_right))

    def get_tight_axis(self, ax, ax2, fig, canvas, BF_opt, infolabel):
        cdn = BF_opt.winfo_children()
        for i in cdn:
            i.destroy()
        SP_up = tk.Entry(BF_opt, width=8)
        SP_up.grid(row=0, column=0, padx=3)
        SP_up.delete(0,tk.END)
        SP_up.insert(0,f'{ax2.get_ylim()[1]:.2f}')
        SP_down = tk.Entry(BF_opt, width=8)
        SP_down.grid(row=1, column=0, padx=3)
        SP_down.delete(0,tk.END)
        SP_down.insert(0,f'{ax2.get_ylim()[0]:.2f}')
        logo_axis_figure = tk.PhotoImage(data=gui_things.beye)
        BT_conf = gui_things.Button(BF_opt, image=logo_axis_figure, hint='set new axis limits', hint_destination=infolabel, command = lambda : self.set_new_axis(ax, ax2, fig, canvas, BF_opt, SP_up, SP_down))
        BT_conf.grid(row=0, column=1, rowspan=2)
        BT_conf.image = logo_axis_figure

    def set_new_axis(self, ax, ax2, fig, canvas, BF_opt, upE, dpwnE):
        try:
            new_up = float(upE.get())
        except TypeError:
            new_up = ax2.get_ylim()[1]
        try:
            new_down = float(dpwnE.get())
        except TypeError:
            new_up = ax2.get_ylim()[0]
        llow, lhigh = ax.get_ylim()
        rlow, rhigh = ax2.get_ylim()
        reference = llow / (rlow/100 + 1)
        ax2.set_ylim(new_down, new_up)
        ax2.set_yticklabels([f'{item:.1f} %' for item in ax2.get_yticks()])
        ax.set_ylim(reference*(new_down/100 +1), reference*(new_up/100 +1))
        self.tight(fig, canvas)
        cdn = BF_opt.winfo_children()
        for i in cdn:
            i.destroy()
        BF_opt.configure(width=1)

    def draw_plots(self, element, dataset, ax1, ax2, fig, canvas, how_many_sigma=2):
        ax1.clear()
        if ax2 is not None:
            ax2.clear()

        subzdata_filter = dataset['target'] == element
        subzdata = dataset[subzdata_filter]

        origins = set(dataset['certificate'])

        i_range = len(self.ticklabels)
        for i in range(i_range):
            self.ticklabels.pop(0)

        n_index = 0
        n_color = 0

        title = f'{element}'

        for orig in sorted(origins):
            s_origin = subzdata['certificate'] == orig
            part_data = subzdata[s_origin]
            if len(part_data.index) > 0:
                try:
                    markerfacecolor = self.color_scheme[n_color]
                except IndexError:
                    n_color = 0
                    markerfacecolor = self.color_scheme[n_color]
                x1 = np.arange(n_index, n_index + len(part_data['target']))
                ax1.errorbar(x1, part_data['value'], yerr=[part_data['uncertainty']*how_many_sigma, part_data['uncertainty']*how_many_sigma], linestyle='', marker='o', markersize=4, color='k', elinewidth=0.5, markerfacecolor=markerfacecolor, label=orig)

                x_comp = np.linspace(np.min(x1)-0.25, np.max(x1)+0.25, 2)
                yw, yuw = part_data.iloc[0,13], part_data.iloc[0,14]
                ax1.fill_between(x_comp, yw-how_many_sigma*yuw, yw+how_many_sigma*yuw, facecolor='#A7DB8C', alpha=0.3)

                n_color += 1
                try:
                    n_index = np.max(x1) + 1
                except TypeError:
                    pass
                self.ticklabels += list(part_data['emitter'].astype(str) + ' ' + part_data['sample'].astype(str))#list(part_data['emitter'])

        x_concat = np.arange(0, n_index)
        xmax = len(x_concat)
        if xmax == 0:
            xmax = 1
        xx = np.arange(-1,xmax+1)

        ax1.set_title(title)
        ax1.set_ylabel(r'$w$ / g g$^{-1}$ ($k=2$)')

        ax1.set_xlim(np.min(xx),np.max(xx))
        ax1.set_xticks(x_concat)
        if self.show_ticklabels:
            ax1.set_xticklabels(self.ticklabels, rotation=90)
        else:
            ax1.set_xticklabels(['' for item in self.ticklabels])

        if ax2 is not None:
            ref_data = subzdata.drop_duplicates(subset=['w', 'uw'])
            reference = np.average(ref_data['w'], weights=1/np.power(ref_data['uw'],2))
            low_lim, up_lim = ax1.get_ylim()
            ax2.set_ylim((low_lim/reference - 1)*100, (up_lim/reference - 1)*100)
            ax2.set_yticklabels([f'{item:.1f} %' for item in ax2.get_yticks()])
            ax2.set_ylabel(r'variability to $\bar{w}_\mathrm{reference}$ / 1')
        if self.x1_grid:
            ax1.grid(True, axis='y')
            ax2.grid(False, axis='y')
        else:
            ax1.grid(False, axis='y')
            ax2.grid(True, axis='y')

        self.tight(fig,canvas)


class CreditsWindow:
    def __init__(self, parent):
        parent.title('Credits')
        parent.resizable(False, False)
        bframe = tk.Frame(parent)
        logo_allinfo = tk.PhotoImage(data=gui_things.ggear)
        B_allinfo = gui_things.Button(bframe, image=logo_allinfo)
        B_allinfo.grid(row=0, column=0)
        B_allinfo.image = logo_allinfo
        ttk.Separator(bframe, orient="vertical").grid(row=0, column=1, sticky=tk.NS, padx=3)
        logo_manual = tk.PhotoImage(data=gui_things.ggear)
        B_manual = gui_things.Button(bframe, image=logo_manual)
        B_manual.grid(row=0, column=2)
        B_manual.image = logo_manual
        #bframe.pack(anchor=tk.NW, padx=5, pady=5)
        infoframe = tk.Frame(parent)
        left_side = tk.Frame(infoframe)

        logo_k0main = tk.PhotoImage(data=gui_things.k0log)
        k0logo = gui_things.Label(left_side, image=logo_k0main)
        k0logo.pack(anchor=tk.NW, pady=5, padx=5)
        k0logo.image = logo_k0main

        self.brief_text = "k0-INRIM software\nversion 1.5 (2021)\n\ncontacts:\nm.diluzio@inrim.it\n\nliterature:\nG D'Agostino et al 2020;\nMeas. Sci. Technol. 31 017002\ndoi: 10.1088/1361-6501/ab57c8\n\nM Di Luzio et al 2020;\nMeas. Sci. Technol. 31 074006\ndoi: 10.1088/1361-6501/ab7ca8"
        self.contact_info_panel = tk.Label(left_side, width=23, text=self.brief_text, anchor=tk.W, justify=tk.LEFT)
        self.contact_info_panel.pack(anchor=tk.NW, fill=tk.X)
        left_side.grid(row=0, column=0, sticky=tk.NW)

        self.right_side = tk.Frame(infoframe)
        try:
            with open('LICENSE') as license_file:
                license_text = license_file.read()
        except:
            license_text = 'License file corrupted or unavailable!'
        stext = gui_things.ScrollableText(self.right_side, width=72, height=40, data=license_text, font=('Courier', 9))
        stext.pack(anchor=tk.NW)
        self.right_side.grid(row=0, column=1, sticky=tk.NW)
        infoframe.pack(anchor=tk.NW, padx=5, pady=5)

        B_allinfo.configure(command=lambda : self.info_command(left_side, infoframe))
        B_manual.configure(command=lambda : self.manual_command(left_side, infoframe))

    def info_command(self, left_side, infoframe):
        self.contact_info_panel.destroy()
        self.contact_info_panel = tk.Label(left_side, width=20, text=self.brief_text, anchor=tk.W, justify=tk.LEFT)
        self.contact_info_panel.pack(anchor=tk.NW, fill=tk.X)

        self.right_side.destroy()
        self.right_side = tk.Frame(infoframe)
        try:
            with open('LICENSE') as license_file:
                license_text = license_file.read()
        except:
            license_text = 'License file corrupted or unavailable!'
        stext = gui_things.ScrollableText(self.right_side, width=73, height=40, data=license_text, font=('Courier', 9))
        stext.pack(anchor=tk.NW)
        self.right_side.grid(row=0, column=1, sticky=tk.NW)

    def manual_command(self, left_side, infoframe):
        self.indice = {'Introduction':0}#, 'chapter1':0, 'chapter2':4}
        self.manual_pages = [tk.PhotoImage(file='C:\\Users\\m.diluzio\\Documents\\Elaborazione\\k1.0 test\\Manual\\self_manual\\001.png')]
        self.page_index = 0
        self.contact_info_panel.destroy()
        self.contact_info_panel = tk.Frame(left_side)
        tk.Label(self.contact_info_panel, text='paragraph selection', anchor=tk.W).pack(anchor=tk.W, padx=5)
        chapter_selection = ttk.Combobox(self.contact_info_panel, width=20, state='readonly')
        chapter_selection.pack()
        items = sorted(self.indice.items(), key=lambda x : x[1])
        chapter_selection['values'] = [item[0] for item in items]
        bframe = tk.Frame(self.contact_info_panel)

        logo_minus = tk.PhotoImage(data=gui_things.previous)
        logo_goto = tk.PhotoImage(data=gui_things.smallarrow)
        logo_plus = tk.PhotoImage(data=gui_things.following)
        B_pageminus = tk.Button(bframe, image=logo_minus)
        B_pageminus.pack(side=tk.LEFT)
        B_pageminus.image = logo_minus
        B_pagegoto = tk.Button(bframe, image=logo_goto)
        B_pagegoto.pack(side=tk.LEFT)
        B_pagegoto.image = logo_goto
        B_pageplus = tk.Button(bframe, image=logo_plus)
        B_pageplus.pack(side=tk.LEFT)
        B_pageplus.image = logo_plus
        bframe.pack(pady=5)
        PageLabel = tk.Label(self.contact_info_panel, text=f'page {self.page_index+1} of {len(self.manual_pages)}')
        PageLabel.pack(pady=3)
        self.contact_info_panel.pack(anchor=tk.NW, fill=tk.X)

        self.right_side.destroy()
        self.right_side = tk.Frame(infoframe)
        file_page = tk.Label(self.right_side, image=self.manual_pages[0])
        file_page.pack(anchor=tk.NW, padx=5, pady=5)
        file_page.image = self.manual_pages[0]
        #
        #stext = gui_things.ScrollableText(self.right_side, width=73, height=40, data=license_text)
        #stext.pack(anchor=tk.NW)
        self.right_side.grid(row=0, column=1, sticky=tk.NW)


class IrradiationWindow:
    def __init__(self, parent, NAA, M):
        parent.title('Irradiation')
        parent.resizable(False, False)
        self.subselection_window = None
        hints = tk.Label(parent, anchor=tk.W)
        mframe = tk.Frame(parent)
        ch_list, ch_data = naaobject._get_channel_data(full_dataset=True)
        tk.Label(mframe, text='irradiation code', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        E_irradiation_code = ttk.Entry(mframe, width=20)
        E_irradiation_code.grid(row=0, column=1, columnspan=2, sticky=tk.EW)
        if NAA.irradiation is not None:
            E_irradiation_code.delete(0, tk.END)
            E_irradiation_code.insert(0, NAA.irradiation.irradiation_code)
        tk.Frame(mframe).grid(row=1, column=0, pady=5)
        tk.Label(mframe, text='channel name', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
        CB_channel_name = ttk.Entry(mframe, width=20)
        CB_channel_name.grid(row=2, column=1, columnspan=2, sticky=tk.EW)
        if NAA.irradiation is not None:
            CB_channel_name.delete(0, tk.END)
            CB_channel_name.insert(0, NAA.irradiation.channel_name)

        logo_flux = tk.PhotoImage(data=gui_things.phi)
        B_select_flux_params = gui_things.Button(mframe, image=logo_flux, hint='select flux parameters from database', hint_destination=hints)
        B_select_flux_params.grid(row=2, column=3, padx=5)
        B_select_flux_params.image = logo_flux

        tk.Label(mframe, text='x').grid(row=3, column=1, pady=3)
        tk.Label(mframe, text='u(x)').grid(row=3, column=2)
        tk.Label(mframe, text='f / 1', anchor=tk.W).grid(row=4, column=0, sticky=tk.W)
        SB_f_value = tk.Spinbox(mframe, from_=0.0, to=4000, increment=0.1, width=10)
        SB_f_value.grid(row=4, column=1)
        SB_unc_f_value = tk.Spinbox(mframe, from_=0.0, to=500, increment=0.1, width=10)
        SB_unc_f_value.grid(row=4, column=2)
        if NAA.irradiation is not None:
            SB_f_value.delete(0, tk.END)
            SB_f_value.insert(0, f'{NAA.irradiation.f_value:.3f}')
            SB_unc_f_value.delete(0, tk.END)
            SB_unc_f_value.insert(0, f'{NAA.irradiation.unc_f_value:.3f}')
        tk.Label(mframe, text='α / 1', anchor=tk.W).grid(row=5, column=0, sticky=tk.W)
        SB_a_value = tk.Spinbox(mframe, from_=-1.0000, to=1.0000, increment=0.0001, width=10)
        SB_a_value.grid(row=5, column=1)
        SB_a_value.delete(0, tk.END)
        SB_a_value.insert(tk.END, '0.0000')
        SB_unc_a_value = tk.Spinbox(mframe, from_=0.0000, to=1.0000, increment=0.0001, width=10)
        SB_unc_a_value.grid(row=5, column=2)
        SB_unc_a_value.delete(0, tk.END)
        SB_unc_a_value.insert(tk.END, '0.0000')
        if NAA.irradiation is not None:
            SB_a_value.delete(0, tk.END)
            SB_a_value.insert(0, f'{NAA.irradiation.a_value:.6f}')
            SB_unc_a_value.delete(0, tk.END)
            SB_unc_a_value.insert(0, f'{NAA.irradiation.unc_a_value:.6f}')
        tk.Label(mframe, text='ϕthermal / cm-2 s-1', anchor=tk.W).grid(row=6, column=0, sticky=tk.W)
        E_thermal = tk.Entry(mframe, width=10)
        E_thermal.grid(row=6, column=1, sticky=tk.EW)
        E_thermal.delete(0, tk.END)
        E_thermal.insert(tk.END, f'{0.0:.2e}')
        E_unc_thermal = tk.Entry(mframe, width=10)
        E_unc_thermal.grid(row=6, column=2, sticky=tk.EW)
        E_unc_thermal.delete(0, tk.END)
        E_unc_thermal.insert(tk.END, f'{0.0:.1e}')
        if NAA.irradiation is not None:
            E_thermal.delete(0, tk.END)
            E_thermal.insert(0, f'{NAA.irradiation.thermal_flux:.2e}')
            E_unc_thermal.delete(0, tk.END)
            E_unc_thermal.insert(0, f'{NAA.irradiation.unc_thermal_flux:.1e}')
        tk.Label(mframe, text='ϕepithermal / cm-2 s-1', anchor=tk.W).grid(row=7, column=0, sticky=tk.W)
        E_epithermal = tk.Entry(mframe, width=10)
        E_epithermal.grid(row=7, column=1, sticky=tk.EW)
        E_epithermal.delete(0, tk.END)
        E_epithermal.insert(tk.END, f'{0.0:.2e}')
        E_unc_epithermal = tk.Entry(mframe, width=10)
        E_unc_epithermal.grid(row=7, column=2, sticky=tk.EW)
        E_unc_epithermal.delete(0, tk.END)
        E_unc_epithermal.insert(tk.END, f'{0.0:.1e}')
        if NAA.irradiation is not None:
            E_epithermal.delete(0, tk.END)
            E_epithermal.insert(0, f'{NAA.irradiation.epithermal_flux:.2e}')
            E_unc_epithermal.delete(0, tk.END)
            E_unc_epithermal.insert(0, f'{NAA.irradiation.unc_epithermal_flux:.1e}')
        tk.Label(mframe, text='ϕfast / cm-2 s-1', anchor=tk.W).grid(row=8, column=0, sticky=tk.W)
        E_fast = tk.Entry(mframe, width=10)
        E_fast.grid(row=8, column=1, sticky=tk.EW)
        E_fast.delete(0, tk.END)
        E_fast.insert(tk.END, f'{0.0:.2e}')
        E_unc_fast = tk.Entry(mframe, width=10)
        E_unc_fast.grid(row=8, column=2, sticky=tk.EW)
        E_unc_fast.delete(0, tk.END)
        E_unc_fast.insert(tk.END, f'{0.0:.1e}')
        if NAA.irradiation is not None:
            E_fast.delete(0, tk.END)
            E_fast.insert(0, f'{NAA.irradiation.fast_flux:.2e}')
            E_unc_fast.delete(0, tk.END)
            E_unc_fast.insert(0, f'{NAA.irradiation.unc_fast_flux:.1e}')
        tk.Frame(mframe).grid(row=9, column=0, pady=5)
        
        tk.Label(mframe, text='position name', anchor=tk.W).grid(row=10, column=0, sticky=tk.W)
        CB_beta_list = naaobject._get_beta_data()
        CB_beta_key = ttk.Entry(mframe, width=20)
        CB_beta_key.grid(row=10, column=1, columnspan=2, sticky=tk.EW)

        logo_beta = tk.PhotoImage(data=gui_things.beta)
        B_select_beta_params = gui_things.Button(mframe, image=logo_beta, hint='select beta parameter from database', hint_destination=hints)
        B_select_beta_params.grid(row=10, column=3, padx=5)
        B_select_beta_params.image = logo_beta

        tk.Label(mframe, text='β / mm-1', anchor=tk.W).grid(row=12, column=0, sticky=tk.W)
        SB_beta = tk.Spinbox(mframe, from_=-1.0000, to=1.0000, increment=0.0001, width=10)
        SB_beta.grid(row=12, column=1)
        SB_beta.delete(0, tk.END)
        SB_beta.insert(tk.END, '0.0000')
        SB_unc_beta = tk.Spinbox(mframe, from_=0.0000, to=0.1000, increment=0.0001, width=10)
        SB_unc_beta.grid(row=12, column=2)
        if NAA.irradiation is not None:
            SB_beta.delete(0, tk.END)
            SB_beta.insert(0, f'{NAA.irradiation.beta:.6f}')
            SB_unc_beta.delete(0, tk.END)
            SB_unc_beta.insert(0, f'{NAA.irradiation.unc_beta:.6f}')

        tk.Frame(mframe).grid(row=13, column=0, pady=5)
        tk.Label(mframe, text='end of irradiation date', anchor=tk.W).grid(row=14, column=0, sticky=tk.W)
        #date and button
        if NAA.irradiation is not None:
            self.irr_date = NAA.irradiation.datetime
        else:
            self.irr_date = datetime.datetime.today()#None
        irradiation_date_label = gui_things.Label(mframe, text='', width=20)
        irradiation_date_label.grid(row=14, column=1, columnspan=2, sticky=tk.W)
        if self.irr_date is not None:
            irradiation_date_label.configure(text=self.irr_date.strftime("%d/%m/%Y %H:%M:%S"))
        logo_calendar = tk.PhotoImage(data=gui_things.calendar)
        B_modify_date = gui_things.Button(mframe, image=logo_calendar, command=lambda : self.change_end_irradiation_date(irradiation_date_label, hints))
        B_modify_date.grid(row=14, column=3, padx=5)
        B_modify_date.image = logo_calendar
        tk.Label(mframe, text='irradiation time / s', anchor=tk.W).grid(row=16, column=0, sticky=tk.W)
        SB_irradiation_time = tk.Spinbox(mframe, from_=0.0, to=1000000.0, increment=0.1, width=10)
        SB_irradiation_time.grid(row=16, column=1, sticky=tk.EW)
        SB_unc_irradiation_time = tk.Spinbox(mframe, from_=0.0, to=2000.0, increment=0.1, width=10)
        SB_unc_irradiation_time.grid(row=16, column=2, sticky=tk.EW, pady=3)
        if NAA.irradiation is not None:
            SB_irradiation_time.delete(0, tk.END)
            SB_irradiation_time.insert(0, f'{NAA.irradiation.irradiation_time:.1f}')
            SB_unc_irradiation_time.delete(0, tk.END)
            SB_unc_irradiation_time.insert(0, f'{NAA.irradiation.unc_irradiation_time:.1f}')
        mframe.pack(anchor=tk.NW, padx=5, pady=5)
        bframe = tk.Frame(parent)
        logo_confirm = tk.PhotoImage(data=gui_things.beye)
        B_confirm_irradiation = gui_things.Button(bframe, image=logo_confirm, hint='Confirm irradiation data', hint_destination=hints, command=lambda: self.confirm_irradiation_data(M, E_irradiation_code, CB_channel_name, SB_f_value, SB_unc_f_value, SB_a_value, SB_unc_a_value, E_thermal, E_unc_thermal, E_epithermal, E_unc_epithermal, E_fast, E_unc_fast, SB_beta, SB_unc_beta, SB_irradiation_time, SB_unc_irradiation_time, hints, NAA))
        B_confirm_irradiation.pack()
        B_confirm_irradiation.image = logo_confirm
        bframe.pack(fill=tk.X, pady=5)
        hints.pack(fill=tk.X, padx=5)

        B_select_flux_params.configure(command= lambda : self.select_facility(parent, ch_data, CB_channel_name, SB_f_value, SB_unc_f_value, SB_a_value, SB_unc_a_value, E_thermal, E_unc_thermal, E_epithermal, E_unc_epithermal, E_fast, E_unc_fast, CB_beta_key, SB_beta, SB_unc_beta))
        B_select_beta_params.configure(command= lambda : self.select_beta(parent, CB_beta_list, CB_channel_name, CB_beta_key, SB_beta, SB_unc_beta))

    def confirm_irradiation_data(self, M, E_irradiation_code, CB_channel_name, SB_f_value, SB_unc_f_value, SB_a_value, SB_unc_a_value, E_thermal, E_unc_thermal, E_epithermal, E_unc_epithermal, E_fast, E_unc_fast, SB_beta, SB_unc_beta, SB_irradiation_time, SB_unc_irradiation_time, hints, NAA, folder=os.path.join('data', 'irradiation')):
        #check of data
        try:
            f_value = float(SB_f_value.get())
        except:
            f_value = 0.0
        try:
            f_unc = float(SB_unc_f_value.get())
        except:
            f_unc = 0.0
        try:
            a_value = float(SB_a_value.get())
        except:
            a_value = 0.0
        try:
            a_unc = float(SB_unc_a_value.get())
        except:
            a_unc = 0.0
        try:
            thermal_value = float(E_thermal.get())
        except:
            thermal_value = 0.0
        try:
            thermal_unc = float(E_unc_thermal.get())
        except:
            thermal_unc = 0.0
        try:
            epithermal_value = float(E_epithermal.get())
        except:
            epithermal_value = 0.0
        try:
            epithermal_unc = float(E_unc_epithermal.get())
        except:
            epithermal_unc = 0.0
        try:
            fast_value = float(E_fast.get())
        except:
            fast_value = 0.0
        try:
            fast_unc = float(E_unc_fast.get())
        except:
            fast_unc = 0.0
        try:
            beta_value = float(SB_beta.get())
        except:
            beta_value = 0.0
        try:
            beta_unc = float(SB_unc_beta.get())
        except:
            beta_unc = 0.0
        try:
            irradiation_time_value = float(SB_irradiation_time.get())
        except:
            irradiation_time_value = 0.0
        try:
            irradiation_time_unc = float(SB_unc_irradiation_time.get())
        except:
            irradiation_time_unc = 0.0
        if f_value > 0.0 and irradiation_time_value > 0.0:
            if E_irradiation_code.get().replace(' ','') != '':
                filename = E_irradiation_code.get()
            else:
                filename = '_'
            if CB_channel_name.get().replace(' ','') != '':
                ch_name = CB_channel_name.get()
            else:
                ch_name = 'unknown'
            #irradiation object
            NAA.irradiation = naaobject.Irradiation(irradiation_code=filename, datetime=self.irr_date, channel_name=ch_name, f_value=f_value, unc_f_value=f_unc, a_value=a_value, unc_a_value=a_unc, thermal_flux=thermal_value, unc_thermal_flux=thermal_unc, epithermal_flux=epithermal_value, unc_epithermal_flux=epithermal_unc, fast_flux=fast_value, unc_fast_flux=fast_unc, beta=beta_value, unc_beta=beta_unc, irradiation_time=irradiation_time_value, unc_irradiation_time=irradiation_time_unc)
            #save
            NAA.irradiation._save_to_file()
            #recall available irradiation
            ext = '.irr'
            M.irradiation_combobox['values'] = [filename[:-len(ext)] for filename in os.listdir(folder) if filename[-len(ext):] == ext]
            M.irradiation_combobox.set(NAA.irradiation.irradiation_code)
            hints.configure(text='irradiation saved')
        else:
            hints.configure(text='check f and irradiation time values')

    def change_end_irradiation_date(self, irradiation_date_label, hints):

        def _confirm_change(DaySpin,MonthSpin,YearSpin,HourSpin,MinuteSpin,SecondSpin,irradiation_date_label,TempTL,hints):
            try:
                day, month, year, hour, minute, second = int(DaySpin.get()), int(MonthSpin.get()), int(YearSpin.get()), int(HourSpin.get()), int(MinuteSpin.get()), int(SecondSpin.get())
            except:
                hints.configure(text='invalid end of irradiation date')
            else:
                try:
                    datetime.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    hints.configure(text='invalid end of irradiation date')
                else:
                    self.irr_date = datetime.datetime(year, month, day, hour, minute, second)
                    irradiation_date_label.configure(text=self.irr_date.strftime("%d/%m/%Y %H:%M:%S"))
                    hints.configure(text='date updated')
                    TempTL.destroy()

        cwidth, xpos, ypos = irradiation_date_label.winfo_width(), irradiation_date_label.winfo_rootx(), irradiation_date_label.winfo_rooty()
        TempTL = tk.Toplevel(irradiation_date_label)
        TempTL.resizable(False, False)
        if sys.platform != 'darwin':
            TempTL.overrideredirect(True)
        day, month, year, hour, minute, second = self.irr_date.day, self.irr_date.month, self.irr_date.year, self.irr_date.hour, self.irr_date.minute, self.irr_date.second
        TempTLF = tk.Frame(TempTL, background='#A3A3A3', bd=3)
        DaySpin = tk.Spinbox(TempTLF, from_=1, to=31, width=3, increment=1)
        DaySpin.pack(side=tk.LEFT)
        DaySpin.delete(0, tk.END)
        DaySpin.insert(tk.END, day)
        MonthSpin = tk.Spinbox(TempTLF, from_=1, to=12, width=3, increment=1)
        MonthSpin.pack(side=tk.LEFT)
        MonthSpin.delete(0, tk.END)
        MonthSpin.insert(tk.END, month)
        YearSpin = tk.Spinbox(TempTLF, from_=1000, to=2999, width=5, increment=1)
        YearSpin.pack(side=tk.LEFT)
        YearSpin.delete(0, tk.END)
        YearSpin.insert(tk.END, year)
        tk.Frame(TempTLF, background='#A3A3A3').pack(side=tk.LEFT, padx=5)
        HourSpin = tk.Spinbox(TempTLF, from_=0, to=23, width=3, increment=1)
        HourSpin.pack(side=tk.LEFT)
        HourSpin.delete(0, tk.END)
        HourSpin.insert(tk.END, hour)
        MinuteSpin = tk.Spinbox(TempTLF, from_=0, to=59, width=3, increment=1)
        MinuteSpin.pack(side=tk.LEFT)
        MinuteSpin.delete(0, tk.END)
        MinuteSpin.insert(tk.END, minute)
        SecondSpin = tk.Spinbox(TempTLF, from_=0, to=59, width=3, increment=1)
        SecondSpin.pack(side=tk.LEFT)
        SecondSpin.delete(0, tk.END)
        SecondSpin.insert(tk.END, second)
        logo_new = tk.PhotoImage(data=gui_things.smallarrow)
        B_update_date = gui_things.Button(TempTLF, image=logo_new, hint='confirm new date', hint_xoffset=5, hint_destination=hints, command=lambda : _confirm_change(DaySpin,MonthSpin,YearSpin,HourSpin,MinuteSpin,SecondSpin,irradiation_date_label,TempTL,hints))
        B_update_date.image = logo_new
        B_update_date.pack(side=tk.LEFT)
        TempTLF.pack(fill=tk.X, expand=True)

        TempTL.update()
        width, height = TempTL.winfo_width(), TempTL.winfo_height()
        TempTL.geometry(f'{width}x{height}+{xpos+int((cwidth-width)/2)}+{ypos}')#+int((cwidth-width)/2)

        TempTLF.focus()
        if sys.platform != 'darwin':
            TempTLF.bind('<FocusOut>', lambda e='<FocusOut>': TempTL.destroy())

    def select_facility(self, parent, ch_data, CB, SB_f_value, SB_unc_f_value, SB_a_value, SB_unc_a_value, E_thermal, E_unc_thermal, E_epithermal, E_unc_epithermal, E_fast, E_unc_fast, CB_beta_key, SB_beta, SB_unc_beta):

        def text_cut(text,limit):
            if len(text) > limit - 1:
                return (text[:limit-3]+'..').ljust(limit," ")
            else:
                return text.ljust(limit," ")

        def _as_text_display(data, spaces=[15,8,12,12,10,10,10,10]):
            return [f'{text_cut(idx,spaces[0])}{text_cut(pos,spaces[1])}{mtime.strftime("%d/%m/%Y").rjust(spaces[2]," ")}{dtime.strftime("%d/%m/%Y").rjust(spaces[3]," ")}{format(ff,".2f").rjust(spaces[4]," ")}{format(aa,".5f").rjust(spaces[5]," ")}{format(thermal,".2e").rjust(spaces[6]," ")}{format(fast,".2e").rjust(spaces[7]," ")}' for idx, pos, mtime, dtime, ff, aa, thermal, fast in zip(data['channel_name'], data['pos'], data['m_datetime'], data['datetime'], data['f_value'], data['a_value'], data['thermal_flux'], data['fast_flux'])]

        def filter_list(ch_data, listbox, CB_channel):
            if CB_channel.get() != '':
                fl_data = _as_text_display(ch_data[ch_data['channel_name'] == CB_channel.get()])
            else:
                fl_data = _as_text_display(ch_data)
            listbox.delete(0, tk.END)
            for item in fl_data:
                listbox.insert(tk.END, item)

        if self.subselection_window is not None:
            self.subselection_window.destroy()
        self.subselection_window = tk.Toplevel(parent)
        self.subselection_window.title('Selection of flux parameters')
        self.subselection_window.resizable(False, False)
        tframe = tk.Frame(self.subselection_window)

        spaces = [15,8,12,12,10,10,10,10]
        header=['channel','position','meas date','eval date','f / 1', 'a / 1','thermal', 'fast']
        tk.Label(tframe, text=f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}{header[3].rjust(spaces[3]," ")}{header[4].rjust(spaces[4]," ")}{header[5].rjust(spaces[5]," ")}{header[6].rjust(spaces[6]," ")}{header[7].rjust(spaces[7]," ")}', anchor=tk.W, font=('Courier', 11)).pack(anchor=tk.W)

        listframe = tk.Frame(tframe)
        scrollbar = tk.Scrollbar(listframe, orient="vertical")
        listbox = tk.Listbox(listframe, width=90, font=('Courier', 11), heigh=25, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listframe.pack(anchor=tk.NW)
        fl_data = _as_text_display(ch_data)
        listbox.delete(0, tk.END)
        for item in fl_data:
            listbox.insert(tk.END, item)

        hint_label = tk.Label(tframe, text='')

        control_frame = tk.Frame(tframe)
        CB_channel_name = ttk.Combobox(control_frame, width=20, state='readonly')
        CB_channel_name['values'] = [''] + sorted(set(ch_data['channel_name']))
        CB_channel_name.pack(side=tk.LEFT)

        logo_confirm = tk.PhotoImage(data=gui_things.beye)
        B_confirm_selection = gui_things.Button(control_frame, image=logo_confirm, hint='select the current flux parameters!', hint_destination=hint_label, command=lambda: self.confirm_selected_facility(ch_data, listbox, CB_channel_name, CB, SB_f_value, SB_unc_f_value, SB_a_value, SB_unc_a_value, E_thermal, E_unc_thermal, E_epithermal, E_unc_epithermal, E_fast, E_unc_fast, CB_beta_key, SB_beta, SB_unc_beta))
        B_confirm_selection.pack(side=tk.LEFT, padx=5)
        B_confirm_selection.image = logo_confirm
        control_frame.pack(anchor=tk.NW, pady=3)

        hint_label.pack(anchor=tk.W)

        tframe.pack(anchor=tk.NW, padx=5, pady=5)

        CB_channel_name.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>': filter_list(ch_data, listbox, CB_channel_name))

    def confirm_selected_facility(self, ch_data, listbox, CB_channel_name, CB, SB_f_value, SB_unc_f_value, SB_a_value, SB_unc_a_value, E_thermal, E_unc_thermal, E_epithermal, E_unc_epithermal, E_fast, E_unc_fast, CB_beta_key, SB_beta, SB_unc_beta):
        idx = listbox.curselection()
        try:
            idx = idx[0]
        except:
            idx = -1
        if idx >= 0:
            if CB_channel_name.get() != '':
                filter_data = ch_data[ch_data['channel_name'] == CB_channel_name.get()]
            else:
                filter_data = ch_data[ch_data['channel_name'] != '']
            prov_index = list(filter_data.index)
            dataline = ch_data.loc[ch_data.index == prov_index[idx], ['channel_name', 'f_value', 'unc_f_value',
       'a_value', 'unc_a_value', 'thermal_flux', 'unc_thermal_flux',
       'epithermal_flux', 'unc_epithermal_flux', 'fast_flux', 'unc_fast_flux']]
            data_name, data_f, data_unc_f, data_a, data_unc_a, data_thermal, data_unc_thermal, data_epithermal, data_unc_epithermal, data_fast, data_unc_fast = [items for items in zip(dataline['channel_name'], dataline['f_value'], dataline['unc_f_value'], dataline['a_value'], dataline['unc_a_value'], dataline['thermal_flux'], dataline['unc_thermal_flux'], dataline['epithermal_flux'], dataline['unc_epithermal_flux'], dataline['fast_flux'], dataline['unc_fast_flux'])][0]

            CB.delete(0, tk.END)
            CB.insert(0, f'{data_name}')
            SB_f_value.delete(0, tk.END)
            SB_f_value.insert(0, f'{data_f:.3f}')
            SB_unc_f_value.delete(0, tk.END)
            SB_unc_f_value.insert(0, f'{data_unc_f:.3f}')
            SB_a_value.delete(0, tk.END)
            SB_a_value.insert(0, f'{data_a:.6f}')
            SB_unc_a_value.delete(0, tk.END)
            SB_unc_a_value.insert(0, f'{data_unc_a:.6f}')
            E_thermal.delete(0, tk.END)
            E_thermal.insert(0, f'{data_thermal:.2e}')
            E_unc_thermal.delete(0, tk.END)
            E_unc_thermal.insert(0, f'{data_unc_thermal:.1e}')
            E_epithermal.delete(0, tk.END)
            E_epithermal.insert(0, f'{data_epithermal:.2e}')
            E_unc_epithermal.delete(0, tk.END)
            E_unc_epithermal.insert(0, f'{data_unc_epithermal:.1e}')
            E_fast.delete(0, tk.END)
            E_fast.insert(0, f'{data_fast:.2e}')
            E_unc_fast.delete(0, tk.END)
            E_unc_fast.insert(0, f'{data_unc_fast:.1e}')

            CB_beta_key.delete(0, tk.END)
            SB_beta.delete(0, tk.END)
            SB_beta.insert(tk.END, '0.0000')
            SB_unc_beta.delete(0, tk.END)
            SB_unc_beta.insert(tk.END, '0.0000')

    def select_beta(self, parent, CB_beta_list, CB, CB_beta_key, SB_beta, SB_unc_beta):

        def text_cut(text,limit):
            if len(text) > limit - 1:
                return (text[:limit-3]+'..').ljust(limit," ")
            else:
                return text.ljust(limit," ")

        def _as_text_display(data, spaces=[20,12,12,10,13]):
            return [f'{text_cut(posit,spaces[0])}{mtime.strftime("%d/%m/%Y").rjust(spaces[1]," ")}{dtime.strftime("%d/%m/%Y").rjust(spaces[2]," ")}{format(beta,".5f").rjust(spaces[3]," ")}{format(unc_beta,".5f").rjust(spaces[4]," ")}' for mtime, dtime, posit, beta, unc_beta in zip(data['m_datetime'], data['datetime'], data['position'], data['beta'], data['unc_beta'])]

        if self.subselection_window is not None:
            self.subselection_window.destroy()
        self.subselection_window = tk.Toplevel(parent)
        self.subselection_window.title(f'Selection of β parameters for channel: {CB.get()}')
        self.subselection_window.resizable(False, False)
        tframe = tk.Frame(self.subselection_window)
        short_beta = CB_beta_list[CB_beta_list['channel_name'] == CB.get()]

        spaces = [20,12,12,10,13]
        header=['position', 'meas date', 'eval date', 'β / mm-1', 'u(β) / mm-1']
        tk.Label(tframe, text=f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}{header[3].rjust(spaces[3]," ")}{header[4].rjust(spaces[4]," ")}', anchor=tk.W, font=('Courier', 11)).pack(anchor=tk.W)

        listframe = tk.Frame(tframe)
        scrollbar = tk.Scrollbar(listframe, orient="vertical")
        listbox = tk.Listbox(listframe, width=68, font=('Courier', 11), heigh=25, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listframe.pack(anchor=tk.NW)
        fl_data = _as_text_display(short_beta)
        listbox.delete(0, tk.END)
        for item in fl_data:
            listbox.insert(tk.END, item)

        hint_label = tk.Label(tframe, text='')

        control_frame = tk.Frame(tframe)
        logo_confirm = tk.PhotoImage(data=gui_things.beye)
        B_confirm_selection = gui_things.Button(control_frame, image=logo_confirm, hint='select the current β parameter!', hint_destination=hint_label, command=lambda: self.confirm_selected_beta(short_beta, listbox, CB_beta_key, SB_beta, SB_unc_beta))
        B_confirm_selection.pack(side=tk.LEFT, padx=5)
        B_confirm_selection.image = logo_confirm
        control_frame.pack(anchor=tk.NW, pady=3)
        hint_label.pack(anchor=tk.W)

        if len(fl_data) == 0:
            hint_label.configure(text='no β parameters for this channel!')

        tframe.pack(anchor=tk.NW, padx=5, pady=5)

    def confirm_selected_beta(self, short_beta, listbox, CB_beta_key, SB_beta, SB_unc_beta):
        idx = listbox.curselection()
        try:
            idx = idx[0]
        except IndexError:
            idx = -1
        if idx >= 0:
            index_beta = list(short_beta.index)
            dataline = short_beta.loc[short_beta.index == index_beta[idx], ['position', 'beta', 'unc_beta']]
            data_position, data_beta, data_unc_beta = [items for items in zip(dataline['position'], dataline['beta'], dataline['unc_beta'])][0]

            CB_beta_key.delete(0, tk.END)
            CB_beta_key.insert(0, data_position)
            SB_beta.delete(0, tk.END)
            SB_beta.insert(0, f'{data_beta:.6f}')
            SB_unc_beta.delete(0, tk.END)
            SB_unc_beta.insert(0, f'{data_unc_beta:.6f}')


class DetectionLimitWindow:
    def __init__(self, parent, NAA, M):
        parent.title('Elements for detection limits')
        parent.resizable(False, False)
        available = set([line[1] for line in NAA.database])
        PTable = gui_things.PeriodicTable(parent, possible_entries=available, already_selected=M.detection_elements, label=M.number_of_limits)
        PTable.pack(fill=tk.BOTH, padx=5, pady=5)


class NotImplementedYet:
    def __init__(self, parent):
        parent.title('In progress')
        parent.resizable(False, False)
        tk.Label(parent, text='This functionality has not been implemented yet').pack(padx=10, pady=10)


class DatabasesWindow:
    def __init__(self, parent, NAA, M):
        parent.title('Databases manager')
        parent.resizable(False, False)

        self.information = tk.Label(parent, text='', anchor=tk.W)

        Buttons_frame = tk.Frame(parent)
        logo_k0database = tk.PhotoImage(data=gui_things.k0circle)
        B_k0_database = gui_things.Button(Buttons_frame, image=logo_k0database, hint='k0 database (read only)', hint_destination=self.information)
        B_k0_database.grid(row=0, column=0)
        B_k0_database.image = logo_k0database
        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=0, column=1, sticky=tk.NS, padx=3)

        logo_dsample = tk.PhotoImage(data=gui_things.flask)
        B_sample_database = gui_things.Button(Buttons_frame, image=logo_dsample, hint='material database', hint_destination=self.information)
        B_sample_database.grid(row=0, column=4)
        B_sample_database.image = logo_dsample

        ttk.Separator(Buttons_frame, orient="vertical").grid(
            row=0, column=5, sticky=tk.NS, padx=3)
        logo_sources = tk.PhotoImage(data=gui_things.emission)
        B_gammasources_database = gui_things.Button(Buttons_frame, image=logo_sources, hint='gamma source database', hint_destination=self.information)
        B_gammasources_database.grid(row=0, column=6)
        B_gammasources_database.image = logo_sources

        ttk.Separator(Buttons_frame, orient="vertical").grid(row=0, column=7, sticky=tk.NS, padx=3)

        logo_settings = tk.PhotoImage(data=gui_things.phi)
        B_channels_database = gui_things.Button(Buttons_frame, image=logo_settings, hint='flux evaluation history database', hint_destination=self.information)
        B_channels_database.grid(row=0, column=8)
        B_channels_database.image = logo_settings

        logo_beta = tk.PhotoImage(data=gui_things.beta)
        B_beta_database = gui_things.Button(Buttons_frame, image=logo_beta, hint='beta evaluation history database', hint_destination=self.information)
        B_beta_database.grid(row=0, column=9)
        B_beta_database.image = logo_beta

        Buttons_frame.pack(anchor=tk.W, padx=5, pady=5)
        Action_Frame = tk.Frame(parent)
        self.k0_database_management(NAA, Action_Frame)
        Action_Frame.pack(anchor=tk.W, padx=5, pady=5)
        #self.information = tk.Label(parent, text='', anchor=tk.W)
        self.information.pack(anchor=tk.W, padx=5)

        B_k0_database.configure(command=lambda : self.k0_database_management(NAA, Action_Frame))

        B_sample_database.configure(command=lambda : self.sample_database_management(NAA, Action_Frame))

        B_gammasources_database.configure(command=lambda : self.gammasource_database_management(NAA, Action_Frame))

        B_channels_database.configure(command=lambda : self.channel_database_management(NAA, Action_Frame))

        B_beta_database.configure(command=lambda : self.beta_database_management(NAA, Action_Frame))

    def beta_database_management(self, NAA, frame):
        def text_cut(text,limit):
            if len(text) > limit - 1:
                return (text[:limit-3]+'..').ljust(limit," ")
            else:
                return text.ljust(limit," ")

        def _as_text_display(data, spaces=[20,12,12,10,13]):
            return [f'{text_cut(posit,spaces[0])}{mtime.strftime("%d/%m/%Y").rjust(spaces[1]," ")}{dtime.strftime("%d/%m/%Y").rjust(spaces[2]," ")}{format(beta,".5f").rjust(spaces[3]," ")}{format(unc_beta,".5f").rjust(spaces[4]," ")}' for mtime, dtime, posit, beta, unc_beta in zip(data['m_datetime'], data['datetime'], data['position'], data['beta'], data['unc_beta'])]

        def _update(CB_channel_selector, listbox):
            filter_channel = self.bdata['channel_name'] == CB_channel_selector.get()
            fl_data = _as_text_display(self.bdata[filter_channel])
            listbox.delete(0, tk.END)
            for item in fl_data:
                listbox.insert(tk.END, item)

            if len(fl_data) == 0:
                self.information.configure(text='no β parameters for this channel!')
            else:
                self.information.configure(text='')

        def export_xcell(CB, parent):
            filetypes = (('Microsoft Excel file','*.xlsx'),)
            filename = asksaveasfilename(parent=parent, title='Save excel file',filetypes=filetypes)
            header = ['channel name', 'position', 'meas date', 'eval date', 'β / mm-1', 'u(β) / mm-1']
            if filename != '' and filename is not None:
                if filename[-len('.xlsx'):] != '.xlsx':
                    filename += '.xlsx'
                columns = ['channel_name', 'position', 'm_datetime', 'datetime', 'beta', 'unc_beta']
                if CB.get() != '':
                    self.bdata[self.bdata['channel_name'] == CB.get()].to_excel(filename, columns=columns, index=False, header=header)
                else:
                    self.bdata.to_excel(filename, columns=columns, index=False, header=header)
                self.information.configure(text='selection saved to file')
            else:
                self.information.configure(text='invalid filename')

        children = frame.winfo_children()
        for widget in children:
            widget.destroy()
        tk.Label(frame, text='beta evaluation history database', anchor=tk.W).pack(anchor=tk.W)

        df_channels = naaobject._get_channel_data()[1]
        df_channels = tuple(df_channels['channel_name'].unique())

        self.bdata = naaobject._get_beta_data()
        if len(df_channels) > 0:
            filter_channel = self.bdata['channel_name'] == df_channels[0]
        else:
            filter_channel = self.bdata['channel_name'] == ''
        spaces = [20,12,12,10,13]
        header=['position', 'meas date', 'eval date', 'β / mm-1', 'u(β) / mm-1']
        tk.Label(frame, text=f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}{header[3].rjust(spaces[3]," ")}{header[4].rjust(spaces[4]," ")}', anchor=tk.W, font=('Courier', 11)).pack(anchor=tk.W)

        listframe = tk.Frame(frame)
        scrollbar = tk.Scrollbar(listframe, orient="vertical")
        listbox = tk.Listbox(listframe, width=68, font=('Courier', 11), heigh=25, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listframe.pack(anchor=tk.NW)
        fl_data = _as_text_display(self.bdata[filter_channel])
        listbox.delete(0, tk.END)
        for item in fl_data:
            listbox.insert(tk.END, item)

        if len(fl_data) == 0:
            self.information.configure(text='no β parameters for this channel!')
        
        control_frame = tk.Frame(frame)
        CB_channel_selector = ttk.Combobox(control_frame, width=20, state='readonly')
        CB_channel_selector['values'] = df_channels
        if len(CB_channel_selector['values']) > 0:
            CB_channel_selector.set(CB_channel_selector['values'][0])
        CB_channel_selector.pack(side=tk.LEFT, padx=5)

        logo_export = tk.PhotoImage(data=gui_things.xcell)
        B_export_selection = gui_things.Button(control_frame, image=logo_export, hint='export selection as excel file!', hint_destination=self.information)
        B_export_selection.pack(side=tk.LEFT)
        B_export_selection.image = logo_export

        logo_delete = tk.PhotoImage(data=gui_things.none)
        B_delete_selection = gui_things.Button(control_frame, image=logo_delete, hint='delete selected β parameter!', hint_destination=self.information)
        B_delete_selection.pack(side=tk.LEFT)
        B_delete_selection.image = logo_delete
        control_frame.pack(anchor=tk.NW, pady=3)

        CB_channel_selector.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : _update(CB_channel_selector, listbox))
        B_export_selection.configure(command=lambda : export_xcell(CB_channel_selector, frame))

    def channel_database_management(self, NAA, frame):

        def delete_dat(CB, stext, parent):

            def rewrite_file(folder=os.path.join('data', 'facility')):
                with open(os.path.join(folder,'channels.csv'), 'w') as channel_file:
                    channel_file.write('mdatetime,datetime,channel_name,pos,f_value,unc_f_value,a_value,unc_a_value,thermal_flux,unc_thermal_flux,epithermal_flux,unc_epithermal_flux,fast_flux,unc_fast_flux\n')
                    for meas_time, save_time, CH_name, pos, result_f, result_f_unc, result_a, result_a_unc, result_thermal, result_thermal_unc, result_epithermal, result_epithermal_unc, result_fast, result_fast_unc in zip(self.fdata['m_datetime'], self.fdata['datetime'], self.fdata['channel_name'], self.fdata['pos'], self.fdata['f_value'], self.fdata['unc_f_value'], self.fdata['a_value'], self.fdata['unc_a_value'], self.fdata['thermal_flux'], self.fdata['unc_thermal_flux'], self.fdata['epithermal_flux'], self.fdata['unc_epithermal_flux'], self.fdata['fast_flux'], self.fdata['unc_fast_flux']):
                        channel_file.write(f'{meas_time.strftime("%d/%m/%Y %H:%M:%S")},{save_time.strftime("%d/%m/%Y %H:%M:%S")},{CH_name},{pos},{result_f},{result_f_unc},{result_a},{result_a_unc},{result_thermal},{result_thermal_unc},{result_epithermal},{result_epithermal_unc},{result_fast},{result_fast_unc}\n')
                #check on betas
                channels = self.fdata['channel_name'].unique()
                beta_data = naaobject._get_beta_data()
                newbeta = beta_data[beta_data['channel_name'].isin(channels)]
                if len(newbeta.index) < len(beta_data.index):
                    newbeta.to_csv(os.path.join(os.path.join('data','facility'),'beta.csv'), columns=['channel_name', 'm_datetime', 'datetime','position', 'beta', 'unc_beta'], header=['channel_name', 'mdatetime', 'datetime','position', 'beta', 'unc_beta'], index=False)

            if CB.get() != '':
                prov_data = self.fdata[self.fdata['channel_name'] == CB.get()]
            else:
                prov_data = self.fdata[self.fdata['channel_name'] != '']
            prov_index = list(prov_data.index)
            idx = stext.curselection()
            try:
                idx = idx[0]
            except IndexError:
                idx = -1
            if idx > -1:
                if messagebox.askyesno(title='Delete the selected measurement entry', message=f'Are you sure to remove the currently selected flux measurement entry?\nthis also deletes all β values for removed channels\n', parent=parent):
                    self.fdata = self.fdata.loc[self.fdata.index != prov_index[idx]]
                    rewrite_file()
                    CB['values'] = [''] + list(set(self.fdata['channel_name']))
                    _update(CB, stext)

        def export_xcell(CB, parent):
            filetypes = (('Microsoft Excel file','*.xlsx'),)
            filename = asksaveasfilename(parent=parent, title='Save excel file',filetypes=filetypes)
            header = ['meas datetime', 'datetime', 'channel', 'position', 'f / 1', 'u(f) / 1', 'a / 1', 'u(a) / 1', 'thermal flux / cm-2 s-1', 'u(thermal flux) / cm-2 s-1', 'epithermal flux / cm-2 s-1', 'u(epithermal flux) / cm-2 s-1', 'fast flux / cm-2 s-1', 'u(fast flux) / cm-2 s-1']
            if filename != '' and filename is not None:
                if filename[-len('.xlsx'):] != '.xlsx':
                    filename += '.xlsx'
                columns = self.fdata.columns
                if CB.get() != '':
                    self.fdata[self.fdata['channel_name'] == CB.get()].to_excel(filename, columns=columns, index=False, header=header)
                else:
                    self.fdata.to_excel(filename, columns=columns, index=False, header=header)
                self.information.configure(text='selection saved to file')
            else:
                self.information.configure(text='invalid filename')

        def _update(CB, stext):
            if CB.get() != '':
                fl_data = _as_text_display(self.fdata[self.fdata['channel_name'] == CB.get()])
            else:
                fl_data = _as_text_display(self.fdata)
            #stext._update(fl_data)
            stext.delete(0, tk.END)
            for item in fl_data:
                stext.insert(tk.END, item)

        def text_cut(text,limit):
            if len(text) > limit - 1:
                return (text[:limit-3]+'..').ljust(limit," ")
            else:
                return text.ljust(limit," ")#here

        def _as_text_display(data, channel=None, spaces=[15,8,12,12,10,10,10,10]):
            return [f'{text_cut(idx,spaces[0])}{text_cut(posx,spaces[1])}{mtime.strftime("%d/%m/%Y").rjust(spaces[2]," ")}{dtime.strftime("%d/%m/%Y").rjust(spaces[3]," ")}{format(ff,".2f").rjust(spaces[4]," ")}{format(aa,".5f").rjust(spaces[5]," ")}{format(thermal,".2e").rjust(spaces[6]," ")}{format(fast,".2e").rjust(spaces[7]," ")}' for idx, posx, mtime, dtime, ff, aa, thermal, fast in zip(data['channel_name'], data['pos'], data['m_datetime'], data['datetime'], data['f_value'], data['a_value'], data['thermal_flux'], data['fast_flux'])]
        
        children = frame.winfo_children()
        for widget in children:
            widget.destroy()
        tk.Label(frame, text='flux evaluation history database', anchor=tk.W).pack(anchor=tk.W)

        _, self.fdata = naaobject._get_channel_data(full_dataset=True)
        spaces = [15,8,12,12,10,10,10,10]
        header=['channel','position','meas date','eval date','f / 1', 'a / 1','thermal', 'fast']
        tk.Label(frame, text=f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}{header[3].rjust(spaces[3]," ")}{header[4].rjust(spaces[4]," ")}{header[5].rjust(spaces[5]," ")}{header[6].rjust(spaces[6]," ")}{header[7].rjust(spaces[7]," ")}', anchor=tk.W, font=('Courier', 11)).pack(anchor=tk.W)

        listframe = tk.Frame(frame)
        scrollbar = tk.Scrollbar(listframe, orient="vertical")
        listbox = tk.Listbox(listframe, width=90, font=('Courier', 11), heigh=25, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listframe.pack(anchor=tk.NW)
        fl_data = _as_text_display(self.fdata)
        listbox.delete(0, tk.END)
        for item in fl_data:
            listbox.insert(tk.END, item)

        #stext = gui_things.ScrollableText(frame, width=82, data=fl_data, #height=25, font=('Courier', 11))
        #stext.pack(anchor=tk.W)

        fl_subwindow = tk.Frame(frame)
        subchannel_CB = ttk.Combobox(fl_subwindow, width=20, state='readonly')
        subchannel_CB['values'] = [''] + list(set(self.fdata['channel_name']))
        subchannel_CB.grid(row=1, column=0, sticky=tk.W, padx=5)

        logo_xcell = tk.PhotoImage(data=gui_things.xcell)
        B_to_excel = gui_things.Button(fl_subwindow, image=logo_xcell, hint='export selection as .xlsx file', hint_destination=self.information, command=lambda : export_xcell(subchannel_CB, frame))
        B_to_excel.grid(row=1, column=1, sticky=tk.W)
        B_to_excel.image = logo_xcell

        logo_delete = tk.PhotoImage(data=gui_things.none)
        B_delete = gui_things.Button(fl_subwindow, image=logo_delete, hint='delete selected measurement', hint_destination=self.information, command=lambda : delete_dat(subchannel_CB, listbox, frame))
        B_delete.grid(row=1, column=3, sticky=tk.W)
        B_delete.image = logo_delete
        fl_subwindow.pack(anchor=tk.NW)

        subchannel_CB.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : _update(subchannel_CB, listbox))

    def k0_database_management(self, NAA, frame):

        def state(obj):
            if obj == 1.0:
                return ''
            else:
                return 'm'

        def _print_the_line(line):
            emis = f'{line[2]}-{int(line[3])}{state(line[4])}'
            return f'{line[1].ljust(5)}{emis.ljust(9)}{format(line[5],".1f").ljust(9)}{format(line[7],".2e").ljust(10)}{line[22].ljust(7)}{format(line[75],".2f").ljust(9)}{format(line[77],".1f").ljust(11)}{format(bool(line[10]),"").ljust(5)}'

        children = frame.winfo_children()
        for widget in children:
            widget.destroy()
        tk.Label(frame, text='k0 database (read only)', anchor=tk.W).pack(anchor=tk.W)

        k0print = [_print_the_line(line) for line in NAA.database]
        k0print = [f'{"".ljust(5)}{"emitter".ljust(9)}{"E / keV".ljust(9)}{"k0 / 1".ljust(10)}{"type".ljust(7)}{"Q0".ljust(9)}{"Er".ljust(11)}{"COI".ljust(5)}'] + k0print
        k0print = '\n'.join(k0print)

        k0_subwindow = tk.Frame(frame)

        stext = gui_things.ScrollableText(k0_subwindow, width=70, data=k0print, height=30)
        stext.grid(row=2, column=0, columnspan=4, sticky=tk.EW)

        k0_subwindow.pack(anchor=tk.NW)

    def gammasource_database_management(self, NAA, frame):
        #gamma sources

        def formatter_function(value, limit=1e6,fformat='.1f',eformat='.2e'):
            if value > -limit and value < limit:
                return format(value,fformat)
            else:
                return format(value,eformat)

        def _select_source(source_selection_CB,certificate_date_label,stext,newCB):
            self.actual_source = naaobject.GSource(source_selection_CB.get())
            certificate_date_label.configure(text=self.actual_source.readable_datetime())
            req_infos = ['energy', 'emitter','activity', 'yield','t_half','COIfree']
            part_data = self.actual_source.data[req_infos].copy(deep=True)
            part_data.loc[:,'t_half'] = part_data['t_half'] / 86400
            part_data.loc[:,'yield'] = part_data['yield'] * 100
            text = 'emissions present in the certified source\nenergy / keV\nactivity / Bq\ngamma yield / %\nt_half / d\n'
            text += part_data.to_string(columns=req_infos,col_space=10,header=True,float_format=lambda x:formatter_function(x),index=False)
            stext._update(text)
            if self.actual_source is not None:
                values_em = sorted(set(self.actual_source.data['reference']), key=lambda x:float(x.split()[0]))
            else:
                values_em = []
            newCB['values'] = values_em
            newCB.set('')

        def _modify_date(certificate_date_label):

            def _confim_change(DaySpin,MonthSpin,YearSpin,HourSpin,MinuteSpin,SecondSpin,certificate_date_label,TempTL):
                try:
                    day, month, year, hour, minute, second = int(DaySpin.get()), int(MonthSpin.get()), int(YearSpin.get()), int(HourSpin.get()), int(MinuteSpin.get()), int(SecondSpin.get())
                except:
                    self.information.configure(text='invalid date entered')
                else:
                    if self.actual_source._modify_date(day, month, year, hour, minute, second):
                        certificate_date_label.configure(text=self.actual_source.readable_datetime())
                        TempTL.destroy()
                        self.information.configure(text='date updated')
                    else:
                        self.information.configure(text='invalid date entered')

            if self.actual_source is not None:
                cwidth, xpos, ypos = certificate_date_label.winfo_width(), certificate_date_label.winfo_rootx(), certificate_date_label.winfo_rooty()
                TempTL = tk.Toplevel(certificate_date_label)
                TempTL.resizable(False, False)
                if sys.platform != 'darwin':
                    TempTL.overrideredirect(True)
                day, month, year, hour, minute, second = self.actual_source.datetime.day, self.actual_source.datetime.month, self.actual_source.datetime.year, self.actual_source.datetime.hour, self.actual_source.datetime.minute, self.actual_source.datetime.second
                TempTLF = tk.Frame(TempTL, background='#A3A3A3', bd=3)
                DaySpin = tk.Spinbox(TempTLF, from_=1, to=31, width=3, increment=1)
                DaySpin.pack(side=tk.LEFT)
                DaySpin.delete(0, tk.END)
                DaySpin.insert(tk.END, day)
                MonthSpin = tk.Spinbox(TempTLF, from_=1, to=12, width=3, increment=1)
                MonthSpin.pack(side=tk.LEFT)
                MonthSpin.delete(0, tk.END)
                MonthSpin.insert(tk.END, month)
                YearSpin = tk.Spinbox(TempTLF, from_=1000, to=2999, width=5, increment=1)
                YearSpin.pack(side=tk.LEFT)
                YearSpin.delete(0, tk.END)
                YearSpin.insert(tk.END, year)
                tk.Frame(TempTLF, background='#A3A3A3').pack(side=tk.LEFT, padx=5)
                HourSpin = tk.Spinbox(TempTLF, from_=0, to=23, width=3, increment=1)
                HourSpin.pack(side=tk.LEFT)
                HourSpin.delete(0, tk.END)
                HourSpin.insert(tk.END, hour)
                MinuteSpin = tk.Spinbox(TempTLF, from_=0, to=59, width=3, increment=1)
                MinuteSpin.pack(side=tk.LEFT)
                MinuteSpin.delete(0, tk.END)
                MinuteSpin.insert(tk.END, minute)
                SecondSpin = tk.Spinbox(TempTLF, from_=0, to=59, width=3, increment=1)
                SecondSpin.pack(side=tk.LEFT)
                SecondSpin.delete(0, tk.END)
                SecondSpin.insert(tk.END, second)
                logo_new = tk.PhotoImage(data=gui_things.smallarrow)
                B_update_date = gui_things.Button(TempTLF, image=logo_new, hint='confirm new date', hint_xoffset=5, hint_destination=self.information, command=lambda : _confim_change(DaySpin,MonthSpin,YearSpin,HourSpin,MinuteSpin,SecondSpin,certificate_date_label,TempTL))
                B_update_date.image = logo_new
                B_update_date.pack(side=tk.LEFT)
                TempTLF.pack(fill=tk.X, expand=True)

                TempTL.update()
                width, height = TempTL.winfo_width(), TempTL.winfo_height()
                TempTL.geometry(f'{width}x{height}+{xpos+int((cwidth-width)/2)}+{ypos}')

                TempTLF.focus()
                if sys.platform != 'darwin':
                    TempTLF.bind('<FocusOut>', lambda e='<FocusOut>': TempTL.destroy())


        def _new_source(source_selection_CB, certificate_date_label, stext, newCB):
            new_filename = 'new_source'
            self.actual_source = naaobject.DummyGSource(new_filename)
            source_selection_CB.set(new_filename)
            certificate_date_label.configure(text=self.actual_source.readable_datetime())
            req_infos = ['energy', 'emitter','activity', 'yield','t_half','COIfree']
            part_data = self.actual_source.data[req_infos].copy(deep=True)
            part_data.loc[:,'t_half'] = part_data['t_half'] / 86400
            part_data.loc[:,'yield'] = part_data['yield'] * 100
            text = 'emissions present in the certified source\nenergy / keV\nactivity / Bq\ngamma yield / %\nt_half / d\n'
            text += part_data.to_string(columns=req_infos,col_space=10,header=True,float_format=lambda x:formatter_function(x),index=False)
            stext._update(text)
            newCB['values'] = []
            newCB.set('')

        def _confirm_changes(source_selection_CB, mergeCB):
            if source_selection_CB.get() != '':
                self.actual_source.name = source_selection_CB.get()
                self.actual_source._save_source()
                self.information.configure(text='changes saved')
                values_em = [filename[:-len('.csv')] for filename in os.listdir(os.path.join('data','sources')) if filename[-len('.sce'):].lower()=='.sce']
                source_selection_CB['values'] = values_em
                mergeCB['values'] = values_em

        def _delete_emission(newCB, stext, E_yield, variable_check_COI):
            if self.actual_source is not None and newCB.get() != '':
                demis = newCB.get()
                filter_delete = self.actual_source.data['reference'] != newCB.get()
                self.actual_source.data = self.actual_source.data[filter_delete].copy(deep=True)
                req_infos = ['energy', 'emitter','activity', 'yield','t_half','COIfree']
                part_data = self.actual_source.data[req_infos].copy(deep=True)
                part_data.loc[:,'t_half'] = part_data['t_half'] / 86400
                part_data.loc[:,'yield'] = part_data['yield'] * 100
                text = 'emissions present in the certified source\nenergy / keV\nactivity / Bq\ngamma yield / %\nt_half / d\n'
                text += part_data.to_string(columns=req_infos,col_space=10,header=True,float_format=lambda x:formatter_function(x),index=False)
                stext._update(text)
                values_em = sorted(set(self.actual_source.data['reference']), key=lambda x:float(x.split()[0]))
                newCB['values'] = values_em
                newCB.set('')
                E_yield.delete(0, tk.END)
                variable_check_COI.set(False)
                self.information.configure(text=f'{demis} emission deleted')
            else:
                self.information.configure(text='no source or valid emission selected')

        def _delete_source(source_selection_CB, certificate_date_label, stext, newCB, mergeCB, parent):
            if self.actual_source is not None:
                if messagebox.askyesno(title='Delete current source', message=f'\nAre you sure to delete (from memory and disk) the current source?\n', parent=parent):
                    try:
                        os.remove(os.path.join(os.path.join('data','sources'), f'{self.actual_source.name}.sce'))
                        self.information.configure(text='deleted from disk')
                    except:
                        self.information.configure(text='deleted from memory')
                    self.actual_source = None
                    source_selection_CB['values'] = [filename[:-len('.csv')] for filename in os.listdir(os.path.join('data','sources')) if filename[-len('.sce'):].lower()=='.sce']
                    source_selection_CB.set('')
                    certificate_date_label.configure(text='')
                    stext._update()
                    newCB['values'] = []
                    newCB.set('')
                    mergeCB['values'] = [filename[:-len('.csv')] for filename in os.listdir(os.path.join('data','sources')) if filename[-len('.sce'):].lower()=='.sce']
                    mergeCB.set('')

        def _select_emission(CB, E_activity, E_half_life, master):
            part_master = master['emitter'] == CB.get()
            hlife = master[part_master].iloc[0]['t_half']
            E_half_life.delete(0, tk.END)
            E_half_life.insert(tk.END, f'{hlife:.1f}')
            if self.actual_source is not None:
                part = self.actual_source.data['emitter'] == CB.get()
                if len(self.actual_source.data[part]) > 0:
                    att = self.actual_source.data[part].iloc[0]['activity']
                    a_hlife = self.actual_source.data[part].iloc[0]['t_half']
                    E_activity.delete(0, tk.END)
                    E_activity.insert(tk.END, f'{att:.1f}')
                    E_half_life.delete(0, tk.END)
                    E_half_life.insert(tk.END, f'{a_hlife:.1f}')
                else:
                    E_activity.delete(0, tk.END)
                    E_activity.insert(tk.END, '')

        def _add_emission_to_source(CB, E_activity, E_half_life, master, stext, newCB):
            try:
                act = float(E_activity.get())
            except:
                act = 0.0
            try:
                hlife = float(E_half_life.get())
            except:
                hlife = 0.0
            if self.actual_source is not None and act > 0.0 and hlife > 0.0:
                part = master['emitter'] == CB.get()
                new_data = master[part].copy(deep=True)
                new_data.loc[:,'activity'] = act
                new_data.loc[:,'t_half'] = hlife
                new_data.loc[:,'COIfree'] = new_data['COIfree'].astype(bool)
                new_data['reference'] = [f'{energy} keV {emitter}' for energy, emitter in zip(new_data['energy'], new_data['emitter'])]
                update = self.actual_source.data['emitter'] == CB.get()
                idxs = self.actual_source.data[update].index
                self.actual_source.data.drop(labels=idxs, inplace=True)
                #regular
                self.actual_source.data = self.actual_source.merge(new_data, ignore_index=True)
                self.actual_source.data.sort_values(by=['energy'], ascending=True, inplace=True, key=lambda x : x.astype(float))
                #check integrity
                req_infos = ['energy', 'emitter','activity', 'yield','t_half','COIfree']
                part_data = self.actual_source.data[req_infos].copy(deep=True)
                part_data.loc[:,'t_half'] = part_data['t_half'] / 86400
                part_data.loc[:,'yield'] = part_data['yield'] * 100
                text = 'emissions present in the certified source\nenergy / keV\nactivity / Bq\ngamma yield / %\nt_half / d\n'
                text += part_data.to_string(columns=req_infos,col_space=10,header=True,float_format=lambda x:formatter_function(x),index=False)
                stext._update(text)
                if self.actual_source is not None:
                    values_em = sorted(set(self.actual_source.data['reference']), key=lambda x:float(x.split()[0]))
                else:
                    values_em = []
                newCB['values'] = values_em
                newCB.set('')
            else:
                self.information.configure(text='no source selected or invalid activity value')

        def _updata_data_single_emission(emitter_selection_CB, E_yield, variable_check_COI, stext):
            if emitter_selection_CB.get() != '':
                try:
                    e_yield = float(E_yield.get())
                except:
                    e_yield = 0.0
                try:
                    coif = variable_check_COI.get()
                except:
                    coif = None
                if 0.0 < e_yield <= 1.0 and coif is not None:
                    part = self.actual_source.data['reference'] == emitter_selection_CB.get()
                    new_data = self.actual_source.data[part].copy(deep=True)
                    new_data.loc[:,'yield'] = e_yield
                    new_data.loc[:,'COIfree'] = coif
                    new_data.loc[:,'COIfree'] = new_data['COIfree'].astype(bool)
                    idxs = self.actual_source.data[part].index
                    self.actual_source.data.drop(labels=idxs, inplace=True)
                    #regular
                    self.actual_source.data = self.actual_source.merge(new_data, ignore_index=True)
                    self.actual_source.data.sort_values(by=['energy'], ascending=True, inplace=True, key=lambda x : x.astype(float))
                    #check integrity
                    req_infos = ['energy', 'emitter','activity', 'yield','t_half','COIfree']
                    part_data = self.actual_source.data[req_infos].copy(deep=True)
                    part_data.loc[:,'t_half'] = part_data['t_half'] / 86400
                    part_data.loc[:,'yield'] = part_data['yield'] * 100
                    text = 'emissions present in the certified source\nenergy / keV\nactivity / Bq\ngamma yield / %\nt_half / d\n'
                    text += part_data.to_string(columns=req_infos,col_space=10,header=True,float_format=lambda x:formatter_function(x),index=False)
                    stext._update(text)
                else:
                    self.information.configure(text='no emission selected or invalid yield value')

        def _select_emission_deletion(emitter_selection_CB, E_yield, variable_check_COI):
            if self.actual_source is not None and emitter_selection_CB.get() != '':
                find_single = self.actual_source.data['reference'] == emitter_selection_CB.get()
                sdata = self.actual_source.data[find_single].iloc[0]
                e_yield, coif = sdata['yield'], bool(sdata['COIfree'])
                E_yield.delete(0, tk.END)
                E_yield.insert(tk.END, e_yield)
                variable_check_COI.set(coif)

        def _merge_sources(second_source_selection_CB, stext, newCB):
            if self.actual_source is not None and second_source_selection_CB.get() != '':
                if self.actual_source.name != second_source_selection_CB.get():
                    mergewithsource = naaobject.GSource(second_source_selection_CB.get())
                    datedelta = self.actual_source.datetime - mergewithsource.datetime
                    datedelta = datedelta.total_seconds()
                    mergewithsource.data.loc[:,'activity'] = mergewithsource.data['activity'] * np.exp(-mergewithsource.data['lambda'] * datedelta)
                    self.actual_source.data = self.actual_source.merge(mergewithsource.data, ignore_index=True)
                    self.actual_source.data.sort_values(by=['energy'], ascending=True, inplace=True, key=lambda x : x.astype(float))
                    #check integrity
                    self.actual_source.data.drop_duplicates(subset=['energy','emitter'], inplace=True)
                    req_infos = ['energy', 'emitter','activity', 'yield','t_half','COIfree']
                    part_data = self.actual_source.data[req_infos].copy(deep=True)
                    part_data.loc[:,'t_half'] = part_data['t_half'] / 86400
                    part_data.loc[:,'yield'] = part_data['yield'] * 100
                    text = 'emissions present in the certified source\nenergy / keV\nactivity / Bq\ngamma yield / %\nt_half / d\n'
                    text += part_data.to_string(columns=req_infos,col_space=10,header=True,float_format=lambda x:formatter_function(x),index=False)
                    stext._update(text)
                    if self.actual_source is not None:
                        values_em = sorted(set(self.actual_source.data['reference']), key=lambda x:float(x.split()[0]))
                    else:
                        values_em = []
                    newCB['values'] = values_em
                    newCB.set('')
                    if len(self.actual_source.data) != len(self.actual_source.data.value_counts(['reference'])):
                        self.information.configure(text='warning: same emission is replicated')

        children = frame.winfo_children()
        for widget in children:
            widget.destroy()
        tk.Label(frame, text='gamma source database', anchor=tk.W).pack(anchor=tk.W)

        self.actual_source = None
        self.information.configure(text='')
        master = naaobject._get_emission_data()

        source_subwindow = tk.Frame(frame)
        tk.Label(source_subwindow, text='source name', anchor=tk.W, width=17).grid(row=0, column=0, sticky=tk.W)
        source_selection_CB = gui_things.Combobox(source_subwindow, width=25)
        source_selection_CB.grid(row=0, column=1, sticky=tk.W)
        source_selection_CB['values'] = [filename[:-len('.csv')] for filename in os.listdir(os.path.join('data','sources')) if filename[-len('.sce'):].lower()=='.sce']

        tk.Label(source_subwindow, text='certificate date', anchor=tk.W, width=17).grid(row=1, column=0, sticky=tk.W)
        certificate_date_label = gui_things.Label(source_subwindow, text='', width=25)
        certificate_date_label.grid(row=1, column=1, sticky=tk.W)
        logo_calendar = tk.PhotoImage(data=gui_things.calendar)
        B_modify_date = gui_things.Button(source_subwindow, image=logo_calendar)
        B_modify_date.grid(row=1, column=2, padx=5)
        B_modify_date.image = logo_calendar

        stext = gui_things.ScrollableText(source_subwindow, width=70, height=25)
        stext.grid(row=2, column=0, columnspan=4, sticky=tk.EW)

        general_buttons = tk.Frame(source_subwindow)
        logo_new = tk.PhotoImage(data=gui_things.plus)
        B_new_source = gui_things.Button(general_buttons, image=logo_new, hint='add a new source', hint_xoffset=5, hint_destination=self.information)
        B_new_source.image = logo_new
        B_new_source.grid(row=0, column=0)
        logo_confirm = tk.PhotoImage(data=gui_things.beye)
        B_confirm_source = gui_things.Button(general_buttons, image=logo_confirm, hint='confirm changes to selected source', hint_xoffset=5, hint_destination=self.information)
        B_confirm_source.image = logo_confirm
        B_confirm_source.grid(row=0, column=2)
        logo_delete = tk.PhotoImage(data=gui_things.none)
        B_delete_source = gui_things.Button(general_buttons, image=logo_delete, hint='delete the selected source', hint_xoffset=5, hint_destination=self.information)
        B_delete_source.image = logo_delete
        B_delete_source.grid(row=0, column=4)
        general_buttons.grid(row=3, column=0, columnspan=4, sticky=tk.W)
        buttons_frame = tk.Frame(source_subwindow)
        second_source_selection_CB = gui_things.Combobox(buttons_frame, width=25, state='readonly', hint='merging source name', hint_destination=self.information)
        second_source_selection_CB.grid(row=3, column=2, columnspan=2)
        second_source_selection_CB['values'] = [filename[:-len('.csv')] for filename in os.listdir(os.path.join('data','sources')) if filename[-len('.sce'):].lower()=='.sce']
        logo_merge = tk.PhotoImage(data=gui_things.mergemission)
        B_merge_source = gui_things.Button(buttons_frame, image=logo_merge, hint='merge with selected source', hint_xoffset=5, hint_destination=self.information)
        B_merge_source.image = logo_merge
        B_merge_source.grid(row=3, column=4)
        ttk.Separator(buttons_frame, orient="vertical").grid(row=0, column=5, rowspan=4, sticky=tk.NS, padx=3)

        little_patch = tk.Frame(buttons_frame)
        tk.Label(little_patch, text='yield / 1').pack(side=tk.LEFT, padx=5)
        E_yield = tk.Entry(little_patch, width=10)
        E_yield.pack(side=tk.LEFT)
        variable_check_COI = tk.BooleanVar(buttons_frame)
        check_COI = tk.Checkbutton(little_patch, variable=variable_check_COI, text='COIfree', onvalue=True, offvalue=False)
        check_COI.pack(side=tk.LEFT, padx=5)
        variable_check_COI.set(False)
        little_patch.grid(row=1, column=6, sticky=tk.W)

        logo_update_single = tk.PhotoImage(data=gui_things.arrow_upplates)
        B_update_single_emission = gui_things.Button(buttons_frame, image=logo_update_single, hint='update data for the current emission', hint_xoffset=5, hint_destination=self.information)
        B_update_single_emission.image = logo_update_single
        B_update_single_emission.grid(row=1, column=7)
        
        B_new_emitter = gui_things.Button(buttons_frame, image=logo_update_single, hint='add or update an emitter', hint_xoffset=5, hint_destination=self.information)
        B_new_emitter.image = logo_update_single
        B_new_emitter.grid(row=2, column=4)
        tk.Label(buttons_frame, text='emitter').grid(row=0, column=2, sticky=tk.W)
        emitter_selection_CB = gui_things.Combobox(buttons_frame, width=12, state='readonly')
        emitter_selection_CB.grid(row=0, column=3)
        emitter_selection_CB['values'] = sorted(set(master['emitter']))
        tk.Label(buttons_frame, text='activity / Bq').grid(row=1, column=2, sticky=tk.W)
        E_activity = tk.Entry(buttons_frame, width=15)
        E_activity.grid(row=1, column=3)
        tk.Label(buttons_frame, text='half-life / s').grid(row=2, column=2, sticky=tk.W)
        E_half_life = tk.Entry(buttons_frame, width=15)
        E_half_life.grid(row=2, column=3)

        emitter_deletion_CB = gui_things.Combobox(buttons_frame, width=25, state='readonly')
        emitter_deletion_CB.grid(row=0, column=6)
        if self.actual_source is not None:
            values_em = sorted(set(self.actual_source.data['reference']), key=lambda x:float(x.split()[0]))
        else:
            values_em = []
        emitter_deletion_CB['values'] = values_em
        B_delete_emitter = gui_things.Button(buttons_frame, image=logo_delete, hint='delete emission', hint_xoffset=5, hint_destination=self.information)
        B_delete_emitter.image = logo_delete
        B_delete_emitter.grid(row=0, column=7)

        buttons_frame.grid(row=4, column=0, columnspan=4, sticky=tk.EW)
        source_subwindow.pack(anchor=tk.NW)

        source_selection_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': _select_source(source_selection_CB,certificate_date_label,stext,emitter_deletion_CB))
        emitter_selection_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': _select_emission(emitter_selection_CB, E_activity, E_half_life, master))
        B_modify_date.configure(command=lambda : _modify_date(certificate_date_label))
        B_merge_source.configure(command=lambda : _merge_sources(second_source_selection_CB, stext, emitter_deletion_CB))
        B_confirm_source.configure(command=lambda : _confirm_changes(source_selection_CB, second_source_selection_CB))
        B_delete_source.configure(command=lambda : _delete_source(source_selection_CB, certificate_date_label, stext, emitter_deletion_CB, second_source_selection_CB, source_subwindow))
        B_new_source.configure(command=lambda : _new_source(source_selection_CB, certificate_date_label, stext, emitter_deletion_CB))
        B_new_emitter.configure(command=lambda : _add_emission_to_source(emitter_selection_CB, E_activity, E_half_life, master, stext, emitter_deletion_CB))
        B_delete_emitter.configure(command=lambda : _delete_emission(emitter_deletion_CB, stext, E_yield, variable_check_COI))
        emitter_deletion_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': _select_emission_deletion(emitter_deletion_CB, E_yield, variable_check_COI))
        B_update_single_emission.configure(command=lambda : _updata_data_single_emission(emitter_deletion_CB, E_yield, variable_check_COI, stext))

    def sample_database_management(self, NAA, frame):

        def _update_changes_to_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,folder=os.path.join('data','samples')):
            #Save changes to current sample
            name, description, sample_type, pstate = sample_selection_CB.get().replace('\n',''),description_text.get().replace('\n',''),sample_type_selection_CB.get().replace('\n',''),physical_state_selection_CB.get().replace('\n','')
            if description == '':
                description = 'No description provided'
            if pstate == '':
                pstate = 'unknown'
            if sample_type == '':
                sample_type = 'unknown'
            if name == '':
                self.information.configure(text='invalid name!')
            elif self.actual_sample is None:
                self.information.configure(text='no material is selected!')
            else:
                self.actual_sample.name = name
                self.actual_sample.description = description
                self.actual_sample.sample_type = sample_type
                self.actual_sample.state = pstate
                try:
                    with open(os.path.join(folder,f'{self.actual_sample.name}.csv'),'w') as saved_sample:
                        saved_sample.write(f'{self.actual_sample.description}\n')
                        saved_sample.write(f'{self.actual_sample.sample_type}\n')
                        saved_sample.write(f'{self.actual_sample.state}\n')
                        saved_sample.write(f'{self.actual_sample._to_csv()}')
                except:
                    self.information.configure(text='some error occurred!')
                else:
                    self.information.configure(text='material saved')
                    sample_selection_CB['values'] = [filename[:-len('.csv')] for filename in os.listdir(folder) if filename[-len('.csv'):].lower()=='.csv']

        def _delete_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,stext,parent, folder=os.path.join('data','samples')):
            #Delete {also from disk} the current sample
            if messagebox.askyesno(title='Delete current material', message=f'\nAre you sure to delete (from memory and disk) the current material?\n', parent=parent):
                filename = sample_selection_CB.get()
                sample_selection_CB.set('')
                description_text._update()
                sample_type_selection_CB.set('')
                physical_state_selection_CB.set('')
                stext._update()
                self.actual_sample = None
                try:
                    os.remove(os.path.join(folder,f'{filename}.csv'))
                    sample_selection_CB['values'] = [filename[:-len('.csv')] for filename in os.listdir(folder) if filename[-len('.csv'):].lower()=='.csv']
                except:
                    self.information.configure(text='removed')
                else:
                    self.information.configure(text='removed from disk')
        
        def _select_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,stext,element_CB):
            #select an existing sample
            self.actual_sample = naaobject.Sample(f'{sample_selection_CB.get()}.csv', non_certified_uncertainty=None)
            description_text._update(self.actual_sample.description)
            sample_type_selection_CB.set(self.actual_sample.sample_type)
            physical_state_selection_CB.set(self.actual_sample.state)
            stext._update(self.actual_sample._as_text_display())#unit='ppm'
            element_CB.set('')

        def _delete_element(element_CB, stext):
            if element_CB.get() in element_CB['values'] and self.actual_sample is not None:
                self.actual_sample.certificate.pop(element_CB.get(),None)
                stext._update(self.actual_sample._as_text_display())
                self.information.configure(text='updated')
            else:
                if self.actual_sample is None:
                    self.information.configure(text='no material selected')
                else:
                    self.information.configure(text='invalid element')

        def _select_element(element_CB,value_Entry,uncertainty_Entry,unit_element_BT,unit_list,unit_conversions=(1,1000000,100)):
            #Select an element of the current sample
            if self.actual_sample is not None:
                values = self.actual_sample.certificate.get(element_CB.get(),('',''))
            else:
                values = ('','')
            idx = unit_list.index(unit_element_BT.cget('text'))
            convertion_factor = unit_conversions[idx] / unit_conversions[0]
            try:
                value = format(values[0] * convertion_factor,".3e")
            except (ValueError, TypeError):
                value = ''
            try:
                uncertainty = format(values[1] * convertion_factor,".2e")
            except (ValueError, TypeError):
                uncertainty = ''
            value_Entry.delete(0,tk.END)
            value_Entry.insert(0,value)
            uncertainty_Entry.delete(0,tk.END)
            uncertainty_Entry.insert(0,uncertainty)

        def _add_new_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,stext,element_CB):
            #create a new sample file
            self.actual_sample = naaobject.Sample('new.csv')
            self.actual_sample.name = 'new_material'
            self.actual_sample.description = 'No description provided'
            sample_selection_CB.set('new_material')
            description_text._update(self.actual_sample.description)
            sample_type_selection_CB.set(self.actual_sample.sample_type)
            physical_state_selection_CB.set(self.actual_sample.state)
            stext._update(self.actual_sample._as_text_display())#unit='ppm'
            element_CB.set('')

        def _update_element_values(element_CB,value_Entry,uncertainty_Entry,unit_element_BT,stext,unit_list,unit_conversions=(1,1000000,100)):
            #Yields effective changes to elemental composition
            if element_CB.get() not in element_CB['values']:
                self.information.configure(text='no element is selected!')
            elif self.actual_sample is None:
                self.information.configure(text='no material is selected!')
            else:
                idx = unit_list.index(unit_element_BT.cget('text'))
                convertion_factor = unit_conversions[0] / unit_conversions[idx]
                try:
                    value = float(value_Entry.get())
                    value = value * convertion_factor
                except ValueError:
                    value = np.nan
                try:
                    uncertainty = float(uncertainty_Entry.get())
                    uncertainty = uncertainty * convertion_factor
                except ValueError:
                    uncertainty = np.nan
                if 0 < value <= 1:
                    self.actual_sample.certificate[element_CB.get()] = (value,uncertainty)
                    stext._update(self.actual_sample._as_text_display())
                else:
                    self.information.configure(text='invalid value entered')

        def change_unit(unit_element_BT,unit_list,value_Entry,uncertainty_Entry,unit_conversions=(1,1000000,100)):
            idx = unit_list.index(unit_element_BT.cget('text'))
            try:
                unit_element_BT.configure(text=unit_list[idx+1])
                new_unit = idx + 1
            except IndexError:
                unit_element_BT.configure(text=unit_list[0])
                new_unit = 0
            convertion_factor = unit_conversions[new_unit] / unit_conversions[idx]
            try:
                uncorrected_value = float(value_Entry.get())
                value_Entry.delete(0,tk.END)
                value_Entry.insert(0,format(uncorrected_value*convertion_factor,".3e"))
            except ValueError:
                pass
            try:
                uncorrected_value_unc = float(uncertainty_Entry.get())
                uncertainty_Entry.delete(0,tk.END)
                uncertainty_Entry.insert(0,format(uncorrected_value_unc*convertion_factor,".2e"))
            except ValueError:
                pass
        
        children = frame.winfo_children()
        for widget in children:
            widget.destroy()
        tk.Label(frame, text='material database', anchor=tk.W).pack(anchor=tk.W)

        self.actual_sample = None
        self.information.configure(text='')

        sample_subwindow = tk.Frame(frame)
        tk.Label(sample_subwindow, text='material name', anchor=tk.W, width=17).grid(row=0, column=0, sticky=tk.W)
        sample_selection_CB = gui_things.Combobox(sample_subwindow, width=25)
        sample_selection_CB.grid(row=0, column=1, sticky=tk.W)
        sample_selection_CB['values'] = [filename[:-len('.csv')] for filename in os.listdir(os.path.join('data','samples')) if filename[-len('.csv'):].lower()=='.csv']

        tk.Label(sample_subwindow, text='description', anchor=tk.W, width=17).grid(row=1, column=0, sticky=tk.W)
        description_text = gui_things.ScrollableText(sample_subwindow, state='normal', width=60, height=3)
        description_text.grid(row=1, column=1, columnspan=3, sticky=tk.EW)

        tk.Label(sample_subwindow, text='material type', anchor=tk.W, width=17).grid(row=2, column=0, sticky=tk.W)
        sample_type_selection_CB = gui_things.Combobox(sample_subwindow, width=25)
        sample_type_selection_CB.grid(row=2, column=1, sticky=tk.W)
        sample_type_selection_CB['values'] = ['organic','soil', 'Reference Material']

        tk.Label(sample_subwindow, text='physical state', anchor=tk.W, width=17).grid(row=3, column=0, sticky=tk.W)
        physical_state_selection_CB = gui_things.Combobox(sample_subwindow, width=25)
        physical_state_selection_CB.grid(row=3, column=1, sticky=tk.W)
        physical_state_selection_CB['values'] = ['solid','solution']

        stext = gui_things.ScrollableText(sample_subwindow, width=60, height=25)
        stext.grid(row=4, column=0, columnspan=4, sticky=tk.EW)

        buttons_frame = tk.Frame(sample_subwindow)
        logo_new = tk.PhotoImage(data=gui_things.plus)
        B_new_sample = gui_things.Button(buttons_frame, image=logo_new, hint='add a new material', hint_xoffset=5, hint_destination=self.information)
        B_new_sample.image = logo_new
        B_new_sample.pack(side=tk.LEFT)

        logo_update = tk.PhotoImage(data=gui_things.beye)
        B_update = gui_things.Button(buttons_frame, image=logo_update, hint='update changes to this material', hint_xoffset=5, hint_destination=self.information)
        B_update.image = logo_update
        B_update.pack(side=tk.LEFT)

        logo_delete = tk.PhotoImage(data=gui_things.none)
        B_delete_sample = gui_things.Button(buttons_frame, image=logo_delete, hint='delete material', hint_xoffset=5, hint_destination=self.information)
        B_delete_sample.image = logo_delete
        B_delete_sample.pack(side=tk.LEFT)

        separator = ttk.Separator(buttons_frame, orient="vertical")
        separator.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        tk.Label(buttons_frame, text='element', width=10).pack(side=tk.LEFT)
        element_CB = gui_things.Combobox(buttons_frame, width=4)
        element_CB.pack(side=tk.LEFT)
        element_list = ('H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og')
        element_CB['values'] = element_list
        element_CB.set('')

        unit_list = ('g g-1','ppm','%')
        unit_element_BT = gui_things.Button(buttons_frame, text=unit_list[0], width=5, hint='choose unit, cycles among g g-1, ppm and %', hint_xoffset=5, hint_destination=self.information)
        unit_element_BT.pack(side=tk.LEFT)

        value_Entry = gui_things.Entry(buttons_frame, width=10, hint='enter value for selected element', hint_xoffset=5, hint_destination=self.information)
        value_Entry.pack(side=tk.LEFT, padx=5)

        uncertainty_Entry = gui_things.Entry(buttons_frame, width=10, hint='enter uncertainty (k=1) for selected element', hint_xoffset=5, hint_destination=self.information)
        uncertainty_Entry.pack(side=tk.LEFT)

        logo_update_element = tk.PhotoImage(data=gui_things.arrow_upplates)
        B_update_element_sample = gui_things.Button(buttons_frame, image=logo_update_element, hint="update element's values", hint_xoffset=5, hint_destination=self.information)
        B_update_element_sample.image = logo_update_element
        B_update_element_sample.pack(side=tk.LEFT)

        logo_delete_element = tk.PhotoImage(data=gui_things.xel)
        B_delete_element_sample = gui_things.Button(buttons_frame, image=logo_delete_element, hint="delete element's values", hint_xoffset=5, hint_destination=self.information)
        B_delete_element_sample.image = logo_delete_element
        B_delete_element_sample.pack(side=tk.LEFT)

        buttons_frame.grid(row=5, column=0, columnspan=4, sticky=tk.EW)
        sample_subwindow.pack(anchor=tk.NW)

        unit_element_BT.configure(command=lambda : change_unit(unit_element_BT,unit_list,value_Entry,uncertainty_Entry))
        sample_selection_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': _select_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,stext,element_CB))
        element_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': _select_element(element_CB,value_Entry,uncertainty_Entry,unit_element_BT,unit_list))
        B_update.configure(command=lambda : _update_changes_to_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB))
        B_delete_sample.configure(command=lambda : _delete_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,stext,sample_subwindow))
        B_update_element_sample.configure(command=lambda : _update_element_values(element_CB,value_Entry,uncertainty_Entry,unit_element_BT,stext,unit_list))
        B_new_sample.configure(command=lambda : _add_new_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,stext,element_CB))
        B_delete_element_sample.configure(command=lambda : _delete_element(element_CB, stext))


class ElaborationProcess:
    def __init__(self, parent, NAA, M, take_focus=True):
        parent.title('Elaboration')
        parent.resizable(False, False)
        text = []
        check_passed = True
        #check requirements
        sample_masses = [spectrum.filename() for spectrum in NAA.sample_spectra if spectrum.sample is None]
        standard_masses = [spectrum.filename() for spectrum in NAA.standard_spectra if spectrum.sample is None]
        k0_standards = []
        k0_standard_id = []
        missing_massfraction = []
        not_simple_decay = []
        if NAA.analysis_name is None:
            text.append('- analysis name is not defined')
            check_passed = False
        if NAA.irradiation is None:
            text.append('- irradiation data are missing')
            check_passed = False
        if NAA.calibration is None:
            text.append('- detector characterization is not selected')
            check_passed = False
        if NAA.standard_spectra == []:
            text.append('- spectra for standard are missing')
            check_passed = False
        for spct in NAA.standard_spectra:
            if spct.k0_monitor_index < 0:
                k0_standards.append(spct)
            else:
                if spct.assign_nuclide[spct.k0_monitor_index] < 0:
                    k0_standard_id.append(spct)
                else:
                    value, _ = spct.get_mass_of_k0_monitor()
                    if value is None:
                        missing_massfraction.append(spct)
                    if spct.get_k0_monitor().line[22] not in ['I', 'IIB', 'IVB', 'VI']:
                        not_simple_decay.append(spct)
        if NAA.sample_spectra == []:
            text.append('- spectra for sample are missing')
            check_passed = False
        if len(sample_masses) > 0:
            text.append('- mass information is missing in those sample spectra:\n('+', '.join([f'{item}' for item in sample_masses])+')')
            check_passed = False
        if len(standard_masses) > 0:
            text.append('- mass information is missing in those standard spectra:\n('+', '.join([f'{item}' for item in standard_masses])+')')
            check_passed = False
        if len(k0_standards) > 0:
            text.append(f'- k0 monitor not set in those standard spectra: ({", ".join([spct.filename() for spct in k0_standards])})')
            check_passed = False
        if len(k0_standard_id) > 0:
            text.append(f'- k0 monitor set to unidentified emission in those standard spectra: ({", ".join([spct.filename() for spct in k0_standard_id])})')
            check_passed = False
        if len(missing_massfraction) > 0:
            text.append(f'- mass fraction of selected k0 for monitor target is missing in those standard spectra: ({", ".join([f"{spct.get_k0_monitor().target} in {spct.filename()}" for spct in missing_massfraction])})')
            check_passed = False
        if len(not_simple_decay) > 0:
            text.append(f'- k0 monitor shows a complex activation/decay scheme in those standard spectra: ({", ".join([f"{spct.get_k0_monitor().emission} in {spct.filename()}" for spct in not_simple_decay])})')
            check_passed = False
        if check_passed:
            self._continue_to_output_frame(parent, NAA, text, M)
        else:
            self._requiremnts_not_met_frame(parent, text)

    def _continue_to_output_frame(self, parent, NAA, text, M):
        nbuds = len(NAA.budgets)
        for _ in range(nbuds):
            NAA.budgets.pop()
        nbuds = len(NAA.detection_limits)
        for _ in range(nbuds):
            NAA.detection_limits.pop()
        header = ['Input data are correctly inserted.\nAn overview of the analysis is reported\n']
        #other checks
        M.progress['maximum'] = 6
        M.progress['value'] = 0
        M.progress.update()
        #irradiation
        text.append(f'#Irradiation\ncode: {NAA.irradiation.irradiation_code}\nended on:    {NAA.irradiation.readable_datetime()}, lasted {NAA.irradiation.readable_irradiation_time()}\nchannel:     {NAA.irradiation.channel_name}\nf / 1:       {NAA.irradiation.f_value:.2f} ({naaobject._get_division(NAA.irradiation.unc_f_value,NAA.irradiation.f_value):.1f} %)\nα / 1:       {NAA.irradiation.a_value:.3f} ({naaobject._get_division(NAA.irradiation.unc_a_value,NAA.irradiation.a_value):.1f} %)\nfluxes / cm-2 s-1\nthermal:     {NAA.irradiation.thermal_flux:.2e} ({naaobject._get_division(NAA.irradiation.unc_thermal_flux,NAA.irradiation.thermal_flux):.1f} %)\nepithermal:  {NAA.irradiation.epithermal_flux:.2e} ({naaobject._get_division(NAA.irradiation.unc_epithermal_flux,NAA.irradiation.epithermal_flux):.1f} %)\nfast:        {NAA.irradiation.fast_flux:.2e} ({naaobject._get_division(NAA.irradiation.unc_fast_flux,NAA.irradiation.fast_flux):.1f} %)\nβ / mm-1:    {NAA.irradiation.beta:.5f} ({naaobject._get_division(NAA.irradiation.unc_beta,NAA.irradiation.beta):.1f} %)\n')
        M.progress['value'] += 1
        M.progress.update()
        #calibration
        text.append(f'#Detector calibration ({NAA.calibration.name})\ndetector: {NAA.calibration.detector}\nstandard counting position: {M.standard_position.get():.1f} mm\nsample counting position:   {M.sample_position.get():.1f} mm\n')
        M.progress['value'] += 1
        M.progress.update()
        #background
        if len(NAA.background) > 0:
            if NAA.background[0].sample is not None:
                blank = f'blank mass / g: {NAA.background[0].sample.mass:.2e} ({np.abs(NAA.background[0].sample.unc_mass / NAA.background[0].sample.mass * 100):.1f} %) including {len(NAA.background[0].sample.certificate)} quantified elements\n'
            else:
                blank = ''
            text.append(f'#background spectrum included\n'+ '\n'.join([f'{spc.filename()}' for spc in NAA.background])+'\n'+blank)
        else:
            text.append('#background spectrum not included\n')

        M.progress['value'] += 1
        M.progress.update()
        #standard & k0
        monitor = NAA.standard_spectra[0].get_k0_monitor()
        value, uncertainty = NAA.standard_spectra[0].get_mass_of_k0_monitor()
        NAA.standard_spectra[0].get_assigned()
        text.append(f'#standard spectrum: {NAA.standard_spectra[0].filename()}\nstart acquisition:     {NAA.standard_spectra[0].readable_datetime()}\nlive time / s:         {NAA.standard_spectra[0].live_time:.1f}, dead: {NAA.standard_spectra[0].deadtime()}\nmass / g:              {NAA.standard_spectra[0].sample.mass:.3e} ({np.abs(NAA.standard_spectra[0].sample.unc_mass / NAA.standard_spectra[0].sample.mass*100):.1f} %)\nk0 monitor:            {monitor.emission}\nmass fraction / g g-1: {value:.3e} ({uncertainty/value*100:.1f} %)\n')
        M.progress['value'] += 1
        M.progress.update()
        #samples

        text.append(f'#Sample')
        warnings = ['']
        for idx, smp_spectrum in enumerate(NAA.sample_spectra):
            assigned, indexes_assigned = smp_spectrum.get_assigned(indexes=True)
            for emiss, indexes in zip(assigned, indexes_assigned):
                unc_budget = naaobject.UncBudget(idx, NAA, M, smp_spectrum, emiss, indexes)
                if unc_budget not in NAA.budgets:
                    NAA.budgets.append(unc_budget)
                else:
                    warnings.append(f'warning: {unc_budget._get_code()} is already assigned to a peak')
            t_assigned = sorted(set([item.target for item in assigned]))
            text.append(f'#{idx+1}: {smp_spectrum.filename()}\nstart acquisition: {smp_spectrum.readable_datetime()}\nlive time / s:     {smp_spectrum.live_time:.1f}, dead: {smp_spectrum.deadtime()}\nmass / g:          {smp_spectrum.sample.mass:.3e} ({smp_spectrum.sample.unc_mass / smp_spectrum.sample.mass*100:.1f} %)\nidentified peaks:  {len(assigned)} (from {len(t_assigned)} target elements)\n')

        M.progress['value'] += 1
        M.progress.update()
        detections_lines = self.find_detections(NAA.database, M.detection_elements)
        for idx, smp_spectrum in enumerate(NAA.sample_spectra):
            for item in detections_lines:
                DetLim = naaobject.UncBudget(idx, NAA, M, smp_spectrum, item, None, detection_limit=True)
                if DetLim not in NAA.budgets:
                    NAA.detection_limits.append(DetLim)
        text.append(f'{len(NAA.budgets)+len(NAA.detection_limits)} items will be issued\n({len(NAA.budgets)} budgets of quantified elements & {len(NAA.detection_limits)} detection limits)\n')

        M.progress['value'] += 1
        M.progress.update()
        text = header + text + warnings
        tk.Label(parent, text='Report', anchor=tk.W).pack(anchor=tk.W, padx=5, pady=5)
        stext = gui_things.ScrollableText(parent, height=20, width=60, data='\n'.join(text))
        stext.pack(anchor=tk.NW, padx=5, pady=5)
        info_box = tk.Label(parent, text='', anchor=tk.W)
        main_button_frame = tk.Frame(parent)
        button_frame = tk.Frame(main_button_frame)
        logo_excel_output = tk.PhotoImage(data=gui_things.xcell)
        B_excel_output = gui_things.Button(button_frame, image=logo_excel_output, hint='Process Excel output!', hint_xoffset=5, hint_destination=info_box)
        B_excel_output.image = logo_excel_output
        B_excel_output.pack(side=tk.LEFT)

        F_group_by_selector = tk.Frame(button_frame)
        self.group_by_selector = tk.IntVar(parent)
        R1 = tk.Radiobutton(F_group_by_selector, text='group by targets', anchor=tk.W, value=0, variable=self.group_by_selector)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_group_by_selector, text='group by spectra', anchor=tk.W, value=1, variable=self.group_by_selector)
        R2.pack(anchor=tk.W)
        self.group_by_selector.set(0)
        F_group_by_selector.pack(side=tk.LEFT, padx=3)

        F_sort_selector = tk.Frame(button_frame)
        self.sort_selector = tk.IntVar(parent)
        R1 = tk.Radiobutton(F_sort_selector, text='sort alphabetically', anchor=tk.W, value=0, variable=self.sort_selector)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_sort_selector, text='sort by Z number', anchor=tk.W, value=1, variable=self.sort_selector)
        R2.pack(anchor=tk.W)
        self.sort_selector.set(0)
        F_sort_selector.pack(side=tk.LEFT, padx=3)
        ttk.Separator(button_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=3)

        logo_periodic_overview = tk.PhotoImage(data=gui_things.periodic)
        B_periodic_overview = gui_things.Button(button_frame, image=logo_periodic_overview, hint='Overview!', hint_xoffset=5, hint_destination=info_box)
        B_periodic_overview.image = logo_periodic_overview
        B_periodic_overview.pack(side=tk.LEFT)

        ttk.Separator(button_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=3)

        logo_store_periodically = tk.PhotoImage(data=gui_things.resulti)
        B_visualize_validation = gui_things.Button(button_frame, image=logo_store_periodically, hint='Perform a validation inspection!', hint_xoffset=5, hint_destination=info_box)
        B_visualize_validation.image = logo_store_periodically
        B_visualize_validation.pack(side=tk.LEFT)

        button_frame.pack(fill=tk.X, expand=True)
        option_frame = tk.Frame(main_button_frame)
        self.save_input_variable = tk.IntVar(parent)
        self.save_input_variable.set(0)
        CBO = tk.Checkbutton(option_frame, text='produce a software savefile alongside the excel output', variable=self.save_input_variable)
        CBO.pack(anchor=tk.W)
        option_frame.pack(fill=tk.X, expand=True)
        main_button_frame.pack(fill=tk.X, expand=True, pady=5, padx=5)
        info_box.pack(fill=tk.X, anchor=tk.W, expand=True, padx=5)

        B_excel_output.configure(command=lambda : self._excel_output(NAA, parent, M))
        B_periodic_overview.configure(command=lambda : self._periodic_overview(NAA, parent, M))
        B_visualize_validation.configure(command=lambda : self._store_data(NAA, M, info_box, parent))

    def find_detections(self, database_k0, element_list):
        try:
            f_k0 = [naaobject.Emission('k0',line) for line in database_k0 if line[1] in element_list]
        except TypeError:
            f_k0 = []
        found = f_k0# + f_rel
        return tuple(found)

    def _store_data(self, NAA, M, infobox, parent):
        df_zvalues = naaobject._store_analysis_data(NAA)
        if len(df_zvalues) > 0:
            validation_window = tk.Toplevel(parent)
            ValidationWindow(validation_window, df_zvalues, NAA.analysis_name)
        else:
            infobox.configure(text='not available data!')

    def _save_sample_form(self, sample_c, sample_name, Rsample):

        def _update_changes_to_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,infoline,folder=os.path.join('data','samples')):
            #Save changes to current sample
            name, description, sample_type, pstate = sample_selection_CB.get().replace('\n',''),description_text.get().replace('\n',''),sample_type_selection_CB.get().replace('\n',''),physical_state_selection_CB.get().replace('\n','')
            if description == '':
                description = 'No description provided'
            if pstate == '':
                pstate = 'unknown'
            if sample_type == '':
                sample_type = 'unknown'
            if name == '':
                infoline.configure(text='invalid name!')
            elif self.actual_sample is None:
                infoline.configure(text='no material is selected!')
            else:
                self.actual_sample.name = name
                self.actual_sample.description = description
                self.actual_sample.sample_type = sample_type
                self.actual_sample.state = pstate
                try:
                    with open(os.path.join(folder,f'{self.actual_sample.name}.csv'),'w') as saved_sample:
                        saved_sample.write(f'{self.actual_sample.description}\n')
                        saved_sample.write(f'{self.actual_sample.sample_type}\n')
                        saved_sample.write(f'{self.actual_sample.state}\n')
                        saved_sample.write(f'{self.actual_sample._to_csv()}')
                except:
                    infoline.configure(text='some error occurred!')
                else:
                    infoline.configure(text='material saved')

        def _delete_element(element_CB, stext, infoline):
            if element_CB.get() in element_CB['values']:
                self.actual_sample.certificate.pop(element_CB.get(),None)
                stext._update(self.actual_sample._as_text_display())
                infoline.configure(text='updated')
            else:
                infoline.configure(text='invalid element')

        def _select_element(element_CB,value_Entry,uncertainty_Entry,unit_element_BT,unit_list,unit_conversions=(1,1000000,100)):
            #Select an element of the current sample
            if self.actual_sample is not None:
                values = self.actual_sample.certificate.get(element_CB.get(),('',''))
            else:
                values = ('','')
            idx = unit_list.index(unit_element_BT.cget('text'))
            convertion_factor = unit_conversions[idx] / unit_conversions[0]
            try:
                value = format(values[0] * convertion_factor,".3e")
            except (ValueError, TypeError):
                value = ''
            try:
                uncertainty = format(values[1] * convertion_factor,".2e")
            except (ValueError, TypeError):
                uncertainty = ''
            value_Entry.delete(0,tk.END)
            value_Entry.insert(0,value)
            uncertainty_Entry.delete(0,tk.END)
            uncertainty_Entry.insert(0,uncertainty)

        def _update_element_values(element_CB,value_Entry,uncertainty_Entry,unit_element_BT,stext,unit_list,infoline,unit_conversions=(1,1000000,100)):
            #Yields effective changes to elemental composition
            if element_CB.get() not in element_CB['values']:
                infoline.configure(text='no element is selected!')
            elif self.actual_sample is None:
                infoline.configure(text='no material is selected!')
            else:
                idx = unit_list.index(unit_element_BT.cget('text'))
                convertion_factor = unit_conversions[0] / unit_conversions[idx]
                try:
                    value = float(value_Entry.get())
                    value = value * convertion_factor
                except ValueError:
                    value = np.nan
                try:
                    uncertainty = float(uncertainty_Entry.get())
                    uncertainty = uncertainty * convertion_factor
                except ValueError:
                    uncertainty = np.nan
                if 0 < value <= 1:
                    self.actual_sample.certificate[element_CB.get()] = (value,uncertainty)
                    stext._update(self.actual_sample._as_text_display())
                else:
                    infoline.configure(text='invalid value entered')

        def change_unit(unit_element_BT,unit_list,value_Entry,uncertainty_Entry,unit_conversions=(1,1000000,100)):
            idx = unit_list.index(unit_element_BT.cget('text'))
            try:
                unit_element_BT.configure(text=unit_list[idx+1])
                new_unit = idx + 1
            except IndexError:
                unit_element_BT.configure(text=unit_list[0])
                new_unit = 0
            convertion_factor = unit_conversions[new_unit] / unit_conversions[idx]
            try:
                uncorrected_value = float(value_Entry.get())
                value_Entry.delete(0,tk.END)
                value_Entry.insert(0,format(uncorrected_value*convertion_factor,".3e"))
            except ValueError:
                pass
            try:
                uncorrected_value_unc = float(uncertainty_Entry.get())
                uncertainty_Entry.delete(0,tk.END)
                uncertainty_Entry.insert(0,format(uncorrected_value_unc*convertion_factor,".2e"))
            except ValueError:
                pass


        # constructor
        self.actual_sample = naaobject.Sample(f'{sample_name}.csv')
        self.actual_sample.name = sample_name
        self.actual_sample.description = f'Material obtained from elaboration of spectrum {sample_name}'
        # make elaborations
        elements = set([line[0] for line in sample_c])
        for element in elements:
            working_list = [line[2][0:1] + line[2][1:2] for line in sample_c if line[0] == element and line[-1] == True]
            if len(working_list) == 1:
                self.actual_sample.certificate[element] = (working_list[0][0],working_list[0][1])
            elif len(working_list) > 1:
                data = naaobject._irq_data(working_list)
                if self.manage_outliers.get() == 0:
                    #IQR
                    data = naaobject._irq_data(working_list)
                    q3, q1 = np.percentile(data['value'], [75 ,25])
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    filter = (lower_bound <= data['value']) & (data['value'] <= upper_bound)
                    data = data[filter]
                if self.compute_mass_fraction_variable.get() == 0:
                    aaverage = np.average(data['value'])
                    std_uncertainty = np.std(data['value'])
                elif self.compute_mass_fraction_variable.get() == 1:
                    aaverage, sum_of_weights = np.average(data['value'], weights=1/np.power(data['uncertainty'],2), returned=True)
                    std_uncertainty = np.sqrt(1/sum_of_weights)
                self.actual_sample.certificate[element] = (aaverage,std_uncertainty)     

        #display the final window
        children = Rsample.winfo_children()
        for widget in children:
            widget.destroy()
        frame = tk.Frame(Rsample)
        tk.Label(frame, text='material database', anchor=tk.W).pack(anchor=tk.W)

        infoline = tk.Label(frame)

        sample_subwindow = tk.Frame(frame)
        tk.Label(sample_subwindow, text='material name', anchor=tk.W, width=17).grid(row=0, column=0, sticky=tk.W)
        sample_selection_CB = gui_things.Combobox(sample_subwindow, width=25)
        sample_selection_CB.grid(row=0, column=1, sticky=tk.W)
        sample_selection_CB.set(self.actual_sample.name)

        tk.Label(sample_subwindow, text='description', anchor=tk.W, width=17).grid(row=1, column=0, sticky=tk.W)
        description_text = gui_things.ScrollableText(sample_subwindow, data=self.actual_sample.description, state='normal', width=60, height=3)
        description_text.grid(row=1, column=1, columnspan=3, sticky=tk.EW)

        tk.Label(sample_subwindow, text='material type', anchor=tk.W, width=17).grid(row=2, column=0, sticky=tk.W)
        sample_type_selection_CB = gui_things.Combobox(sample_subwindow, width=25)
        sample_type_selection_CB.grid(row=2, column=1, sticky=tk.W)
        sample_type_selection_CB['values'] = ['organic','soil', 'Reference Material']
        sample_type_selection_CB.set(self.actual_sample.sample_type)

        tk.Label(sample_subwindow, text='physical state', anchor=tk.W, width=17).grid(row=3, column=0, sticky=tk.W)
        physical_state_selection_CB = gui_things.Combobox(sample_subwindow, width=25)
        physical_state_selection_CB.grid(row=3, column=1, sticky=tk.W)
        physical_state_selection_CB['values'] = ['solid','solution']
        physical_state_selection_CB.set(self.actual_sample.state)

        stext = gui_things.ScrollableText(sample_subwindow, data=self.actual_sample._as_text_display(), width=60, height=25)
        stext.grid(row=4, column=0, columnspan=4, sticky=tk.EW)

        buttons_frame = tk.Frame(sample_subwindow)
        logo_update = tk.PhotoImage(data=gui_things.beye)
        B_update = gui_things.Button(buttons_frame, image=logo_update, hint='update changes to this material', hint_xoffset=5, hint_destination=infoline)
        B_update.image = logo_update
        B_update.pack(side=tk.LEFT)

        separator = ttk.Separator(buttons_frame, orient="vertical")
        separator.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        tk.Label(buttons_frame, text='element', width=10).pack(side=tk.LEFT)
        element_CB = gui_things.Combobox(buttons_frame, width=4)
        element_CB.pack(side=tk.LEFT)
        element_list = ('H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og')
        element_CB['values'] = element_list
        element_CB.set('')

        unit_list = ('g g-1','ppm','%')
        unit_element_BT = gui_things.Button(buttons_frame, text=unit_list[0], width=5, hint='choose unit, cycles among g g-1, ppm and %', hint_xoffset=5, hint_destination=infoline)
        unit_element_BT.pack(side=tk.LEFT)

        value_Entry = gui_things.Entry(buttons_frame, width=10, hint='enter value for selected element', hint_xoffset=5, hint_destination=infoline)
        value_Entry.pack(side=tk.LEFT, padx=5)

        uncertainty_Entry = gui_things.Entry(buttons_frame, width=10, hint='enter uncertainty (k=1) for selected element', hint_xoffset=5, hint_destination=infoline)
        uncertainty_Entry.pack(side=tk.LEFT)

        logo_update_element = tk.PhotoImage(data=gui_things.arrow_upplates)
        B_update_element_sample = gui_things.Button(buttons_frame, image=logo_update_element, hint="update element's values", hint_xoffset=5, hint_destination=infoline)
        B_update_element_sample.image = logo_update_element
        B_update_element_sample.pack(side=tk.LEFT)

        logo_delete_element = tk.PhotoImage(data=gui_things.xel)
        B_delete_element_sample = gui_things.Button(buttons_frame, image=logo_delete_element, hint="delete element's values", hint_xoffset=5, hint_destination=infoline)
        B_delete_element_sample.image = logo_delete_element
        B_delete_element_sample.pack(side=tk.LEFT)

        buttons_frame.grid(row=5, column=0, columnspan=4, sticky=tk.EW)
        sample_subwindow.pack(anchor=tk.NW)
        infoline.pack(anchor=tk.W)

        frame.pack(anchor=tk.NW, padx=5, pady=5)

        unit_element_BT.configure(command=lambda : change_unit(unit_element_BT,unit_list,value_Entry,uncertainty_Entry))
        element_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': _select_element(element_CB,value_Entry,uncertainty_Entry,unit_element_BT,unit_list))
        B_update_element_sample.configure(command=lambda : _update_element_values(element_CB,value_Entry,uncertainty_Entry,unit_element_BT,stext,unit_list,infoline))
        B_update.configure(command=lambda : _update_changes_to_sample(sample_selection_CB,description_text,sample_type_selection_CB,physical_state_selection_CB,infoline))
        B_delete_element_sample.configure(command=lambda : _delete_element(element_CB, stext, infoline))


    def _save_results_to_sample(self, CB_spectrum, result_nested_list, parent):
        idx = CB_spectrum.current()
        sample_name = CB_spectrum.get()
        sample_c = sorted([list(item) + [True] for item in result_nested_list[idx] if 0 < item[2][0] <= 1], key=lambda x : x[1])
        Rsample = tk.Toplevel(parent)
        Rsample.title('Create material')
        Rsample.resizable(False, False)
        #options
        elements = set([item[0] for item in sample_c])
        foptions = tk.Frame(Rsample)
        infotask = tk.Label(foptions)
        tk.Label(foptions, text=f'the selected spectrum contains mass fraction information from {len(sample_c)} emissions for {len(elements)} elements', anchor=tk.W).pack(anchor=tk.W, pady=5)
        tk.Label(foptions, text='elements', anchor=tk.W).pack(anchor=tk.W, pady=5)
        stext = gui_things.ScrollableText(foptions, height=4, data=', '.join(elements), width=50)
        stext.pack(anchor=tk.W, fill=tk.X, expand=True)
        tk.Frame(foptions).pack(pady=5)
        tk.Label(foptions, text='compute mass fractions from multiple emissions', anchor=tk.W).pack(anchor=tk.W)
        self.compute_mass_fraction_variable = tk.IntVar(parent)
        R1 = tk.Radiobutton(foptions, text='arithmetic average', anchor=tk.W, value=0, variable=self.compute_mass_fraction_variable)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(foptions, text='weighted average', anchor=tk.W, value=1, variable=self.compute_mass_fraction_variable)
        R2.pack(anchor=tk.W)
        self.compute_mass_fraction_variable.set(0)
        #arithemtic average
        #weighted average
        tk.Frame(foptions).pack(pady=5)
        tk.Label(foptions, text='remove outliers based on', anchor=tk.W).pack(anchor=tk.W)

        self.manage_outliers = tk.IntVar(parent)
        R1O = tk.Radiobutton(foptions, text='IQR', anchor=tk.W, value=0, variable=self.manage_outliers)
        R1O.pack(anchor=tk.W)
        foption_line = tk.Frame(foptions)
        R2O = tk.Radiobutton(foption_line, text='manual selection', anchor=tk.W, value=1, variable=self.manage_outliers)
        R2O.pack(anchor=tk.W, side=tk.LEFT)
        self.manage_outliers.set(0)
        CB_elements = ttk.Combobox(foption_line, state='disabled', width=18)
        CB_elements['values'] = [element[1] for element in sample_c]
        CB_elements.set('')
        CB_elements.pack(side=tk.LEFT, padx=5)
        self.acccept_refuse_variable = tk.IntVar(parent)
        CBox_true = Checkbutton(foption_line, text='select', onvalue=1, offvalue=0, variable=self.acccept_refuse_variable, state='disabled')
        CBox_true.pack(side=tk.LEFT, padx=3)
        self.acccept_refuse_variable.set(0)
        foption_line.pack(anchor=tk.W)
        
        manual_element_selector = tk.Frame(foptions)
        manual_element_selector.pack(anchor=tk.W, fill=tk.X)

        tk.Frame(foptions).pack(pady=5)
        logo_sample = tk.PhotoImage(data=gui_things.flask)
        B_proceed = gui_things.Button(foptions, image=logo_sample, hint='Proceed to create sample!', hint_destination=infotask,
                  command=lambda: self._save_sample_form(sample_c, sample_name, Rsample))
        B_proceed.pack(anchor=tk.W)
        B_proceed.image = logo_sample

        infotask.pack(anchor=tk.W)
        foptions.pack(anchor=tk.W, pady=5, padx=5)
        self.manage_outliers.trace('w', lambda a,b,c : self._activate_manual_selection(CB_elements, CBox_true, sample_c))
        CB_elements.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._bring_selection_to_the_attention(CB_elements, sample_c))
        CBox_true.configure(command=lambda : self._change_state(CB_elements, sample_c))

    def _change_state(self, CB_elements, sample_c):
        idx = CB_elements.current()
        if self.acccept_refuse_variable.get():
            sample_c[idx][-1] = True
        else:
            sample_c[idx][-1] = False

    def _bring_selection_to_the_attention(self, CB_elements, sample_c):
        idx = CB_elements.current()
        if sample_c[idx][-1]:
            self.acccept_refuse_variable.set(1)
        else:
            self.acccept_refuse_variable.set(0)

    def _activate_manual_selection(self, CB_elements, CBox_true, sample_c):
        if self.manage_outliers.get() == 0:
            CB_elements.configure(state='disabled')
            CB_elements.set('')
            CBox_true.configure(state='disabled')
            self.acccept_refuse_variable.set(0)
            for idx in range(len(sample_c)):
                sample_c[idx][-1] = True
        if self.manage_outliers.get() == 1:
            CB_elements.configure(state='readonly')
            CB_elements.set('')
            CBox_true.configure(state='normal')
            self.acccept_refuse_variable.set(0)

    def _periodic_overview(self, NAA, parent, M):
        result_nested_list = [[budget for budget in NAA.budgets if budget.spectrum_code == f'#{num+1}'] for num in range(len(NAA.sample_spectra))]
        spectrum_name = [item.filename() for item in NAA.sample_spectra]
        result_nested_list = [[item._solve(full=True) for item in items if item._solve(full=True)[-1] is not None] for items in result_nested_list]
        PerTable = tk.Toplevel(parent)
        PerTable.title('Analysis overview (quantified only)')
        PerTable.resizable(False, False)
        bframe = tk.Frame(PerTable)
        pframe = tk.Frame(PerTable)
        tk.Label(bframe, text='spectrum').pack(side=tk.LEFT)
        CB_spectrum = ttk.Combobox(bframe, width=25, state='readonly')
        CB_spectrum.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        CB_spectrum['values'] = spectrum_name
        if len(CB_spectrum['values']) > 0:
            CB_spectrum.set(CB_spectrum['values'][0])
            possible_entries = set([item[0] for item in result_nested_list[0]])
            data_selection = result_nested_list[0]
        else:
            possible_entries = []
            data_selection = []    
        logo_sample = tk.PhotoImage(data=gui_things.flask)
        B_save_to_sample = gui_things.Button(bframe, image=logo_sample, command=lambda: self._save_results_to_sample(CB_spectrum, result_nested_list, parent))
        B_save_to_sample.pack(side=tk.LEFT, padx=5)
        B_save_to_sample.image = logo_sample
        pt_able = gui_things.PeriodicTable(pframe, possible_entries=possible_entries, already_selected=data_selection, ptype='button')
        pt_able.pack()

        bframe.pack(anchor=tk.NW, padx=5, pady=5)
        pframe.pack(anchor=tk.NW, padx=5, pady=5)

        CB_spectrum.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self._spectrum_selection(pframe, CB_spectrum, result_nested_list))

    def _spectrum_selection(self, pframe, CB_spectrum, result_nested_list):
        cdn = pframe.winfo_children()
        for i in cdn:
            i.destroy()
        idx = CB_spectrum.current()
        if idx >= 0:
            possible_entries = set([item[0] for item in result_nested_list[idx]])
            data_selection = result_nested_list[idx]
        else:
            possible_entries = []
            data_selection = []
        pt_able = gui_things.PeriodicTable(pframe, possible_entries=possible_entries, already_selected=data_selection, ptype='button')
        pt_able.pack()

    def _excel_output(self, NAA, parent, M):
        groupby = self.group_by_selector.get()
        sort = self.sort_selector.get()
        filetypes = (('Microsoft Excel file','*.xlsx'),)
        output = asksaveasfilename(parent=parent, title='Save excel file',filetypes=filetypes, initialfile=NAA.analysis_name)
        if output is not None and output != '':
            if output[-len('.xlsx'):] != '.xlsx':
                output = f'{output}.xlsx'
            M.infotask.configure(text=f'saving output to file ({output})')
            M.progress['maximum'] = len(NAA.budgets)
            M.progress['value'] = 0
            M.progress.update()
            #group by target
            total_budgets = NAA.budgets + NAA.detection_limits
            if groupby == 0:#sort alphabetically or by Z?
                btype = 'target'
                if sort == 0: #alphabetically
                    headline = sorted(set([item.target for item in total_budgets]))
                else: #by Z number
                    Z_number = []
                    for line in NAA.database:
                        if line[1] not in Z_number:
                            Z_number.append(line[1])
                    headline = set([item.target for item in total_budgets])
                    headline = [Z for Z in Z_number if Z in headline]
                result_nested_list = [[budget for budget in total_budgets if budget.target == element] for element in headline]
            #group by spectrum
            else:
                btype = 'spectrum'
                result_nested_list = [[budget for budget in total_budgets if budget.spectrum_code == f'#{num+1}'] for num in range(len(NAA.sample_spectra))]
                if sort == 0: #alphabetically
                    headline = sorted(set([item.target for item in total_budgets]))
                else: #by Z number
                    Z_number = []
                    for line in NAA.database:
                        if line[1] not in Z_number:
                            Z_number.append(line[1])
                    headline = set([item.target for item in total_budgets])
                    headline = [Z for Z in Z_number if Z in headline]
                for i in range(len(result_nested_list)):
                    result_nested_list[i] = [budget for element in headline for budget in result_nested_list[i] if budget.target==element]
            naaobject.ExcelOutput(output, NAA, M, result_nested_list, btype)
            if self.save_input_variable.get():
                if output[-5:].lower() == '.xlsx':
                    filename = output[:-5]
                else:
                    filename = output

                try:
                    float(M.Deltad_standard_spinbox.get())
                    dd_std = M.Deltad_standard_spinbox.get()
                except ValueError:
                    dd_std = '0.0'
                try:
                    float(M.uDeltad_standard_spinbox.get())
                    udd_std = M.uDeltad_standard_spinbox.get()
                except ValueError:
                    udd_std = '0.0'
                NAA.standard_position = (M.standard_position.get(), dd_std, udd_std)

                try:
                    float(M.Deltad_sample_spinbox.get())
                    dd_smp = M.Deltad_sample_spinbox.get()
                except ValueError:
                    dd_smp = '0.0'
                try:
                    float(M.uDeltad_sample_spinbox.get())
                    udd_smp = M.uDeltad_sample_spinbox.get()
                except ValueError:
                    udd_smp = '0.0'
                NAA.sample_position = (M.sample_position.get(), dd_smp, udd_smp)
                if M.regular_calibration_variable.get() >= 0:
                    NAA.position_selector = M.regular_calibration_variable.get()
                NAA.detection_elements = M.detection_elements
                with open(f'{filename}.sav','wb') as filesave:
                    pickle.dump(NAA, filesave)
                sentence = '.sav file: YES\n'
            else:
                sentence = '.sav file: NO\n'
            M.infotask.configure(text='success!')
            filepath_knowledge = os.path.split(output)
            messagebox.showinfo(title='Success!', message=f'Excel file successfully saved\nfilename: {filepath_knowledge[1]}\n{sentence}in folder: {os.path.split(filepath_knowledge[0])[1]}', parent=parent)

    def _requiremnts_not_met_frame(self, parent, text):
        header = ['Issues were identified while checking for consistency of the input data; error messages are reported\n']
        text = header + text
        tk.Label(parent, text='Report', anchor=tk.W).pack(anchor=tk.W, padx=5, pady=5)
        stext = gui_things.ScrollableText(parent, height=15, width=60, data='\n'.join(text))
        stext.pack(anchor=tk.NW, padx=5, pady=5)


class SettingsWindow:
    def __init__(self, parent, NAA, M, take_focus=True):
        parent.title('Settings')
        parent.resizable(False, False)
        explanation_bar = tk.Label(parent, text='', anchor=tk.W)
        gui_things.Label(parent, text='k0 database', hint='name of k0 database from which literature data are retrieved', hint_destination=explanation_bar).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        variable_database = ttk.Combobox(parent, width=35, state='readonly')
        variable_database.grid(row=0, column=1)
        variable_database['values'] = retrieve_files(folder='data/k0data', ext='.xls')
        if NAA.settings_dict['database'] in variable_database['values']:
            variable_database.set(NAA.settings_dict['database'])
        gui_things.Label(parent, text='ΔE / keV', hint='tolerance energy to find matching database entries', hint_destination=explanation_bar).grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        variable_energy_tolerance = gui_things.FSlider(parent, decimals=2, label_width=4, resolution=0.05, from_=0.1, to=2.0, default=NAA.settings_dict['energy tolerance'])
        variable_energy_tolerance.grid(row=1, column=1, sticky=tk.E)
        gui_things.Label(parent, text='items per page', hint='lines displayed in peaklists windows, depends on screen size', hint_destination=explanation_bar).grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        variable_page_height = gui_things.Slider(parent, resolution=1, label_width=4, from_=15, to=30, default=NAA.settings_dict['page height'])
        variable_page_height.grid(row=2, column=1, sticky=tk.E)
        gui_things.Label(parent, text='max uncertainty of calibration parameters', hint='drops fit parameters if their uncertainty is higher', hint_destination=explanation_bar).grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        variable_calib_uncertainty = gui_things.Slider(parent, resolution=1, label_width=6, from_=40, to=120, default=NAA.settings_dict['max allowed calibration uncertainty'], percent=True)
        variable_calib_uncertainty.grid(row=3, column=1, sticky=tk.E)
        gui_things.Label(parent, text='statistical limit for calibration spectra', hint='excludes peaks with higher uncertainty while importing peaklists', hint_destination=explanation_bar).grid(row=4, column=0, padx=5, pady=2, sticky=tk.W)
        variable_calib_limit = gui_things.Slider(parent, resolution=1, label_width=6, from_=3, to=20, default=NAA.settings_dict['calibs statistical uncertainty limit'], percent=True)
        variable_calib_limit.grid(row=4, column=1, sticky=tk.E)
        gui_things.Label(parent, text='statistical limit for standard spectra', hint='excludes peaks with higher uncertainty while importing peaklists', hint_destination=explanation_bar).grid(row=5, column=0, padx=5, pady=2, sticky=tk.W)
        variable_standard_limit = gui_things.Slider(parent, resolution=1, label_width=6, from_=5, to=50, default=NAA.settings_dict['standard statistical uncertainty limit'], percent=True)
        variable_standard_limit.grid(row=5, column=1, sticky=tk.E)
        gui_things.Label(parent, text='statistical limit for sample spectra', hint='excludes peaks with higher uncertainty while importing peaklists', hint_destination=explanation_bar).grid(row=6, column=0, padx=5, pady=2, sticky=tk.W)
        variable_sample_limit = gui_things.Slider(parent, resolution=1, label_width=6, from_=5, to=50, default=NAA.settings_dict['sample statistical uncertainty limit'], percent=True)
        variable_sample_limit.grid(row=6, column=1, sticky=tk.E)
        gui_things.Label(parent, text='non-certified target uncertainty', hint='assigns uncertainty to non-certified target elements', hint_destination=explanation_bar).grid(row=7, column=0, padx=5, pady=2, sticky=tk.W)
        variable_noncertified_uncertainty = gui_things.Slider(parent, resolution=1, label_width=6, from_=5, to=50, default=NAA.settings_dict['non certified standard uncertainties'], percent=True)
        variable_noncertified_uncertainty.grid(row=7, column=1, sticky=tk.E)
        gui_things.Label(parent, text='default uncertainty for tc and tl / s', hint='sets the default uncertainty for counting (real and live) times', hint_destination=explanation_bar).grid(row=8, column=0, padx=5, pady=2, sticky=tk.W)
        variable_tctl_default_uncetrainty = gui_things.FSlider(parent, decimals=1, label_width=4, resolution=0.1, from_=0.1, to=2.0, default=NAA.settings_dict['default tc&tl uncertainties'])
        variable_tctl_default_uncetrainty.grid(row=8, column=1, sticky=tk.E)
        gui_things.Label(parent, text='default uncertainty for td / s', hint='sets the default uncertainty for decay time', hint_destination=explanation_bar).grid(row=9, column=0, padx=5, pady=2, sticky=tk.W)
        variable_td_default_uncetrainty = gui_things.FSlider(parent, decimals=1, label_width=6, resolution=0.1, from_=0.5, to=300.0, default=NAA.settings_dict['default td uncertainty'])
        variable_td_default_uncetrainty.grid(row=9, column=1, sticky=tk.E)
        gui_things.Label(parent, text='always look for spectrum file', hint='looks for spectrum files (.chn or .asc) with same filenames of peaklist', hint_destination=explanation_bar).grid(row=10, column=0, padx=5, pady=2, sticky=tk.W)
        variable_find_spectrumfile = gui_things.TSlider(parent, label_width=6, default=NAA.settings_dict['look for spectrum file'])
        variable_find_spectrumfile.grid(row=10, column=1, sticky=tk.E)
        F_button = tk.Frame(parent)
        logo_settings = tk.PhotoImage(data=gui_things.beye)
        B_confirm = gui_things.Button(F_button, image=logo_settings, hint='apply changes and restart', hint_destination=explanation_bar, command=lambda : self.confirm(M, variable_database, variable_energy_tolerance, variable_page_height, variable_calib_uncertainty, variable_calib_limit, variable_standard_limit, variable_sample_limit, variable_noncertified_uncertainty, variable_tctl_default_uncetrainty, variable_td_default_uncetrainty, variable_find_spectrumfile))
        B_confirm.pack()
        B_confirm.image = logo_settings
        F_button.grid(row=11, column=0, pady=5, columnspan=2, sticky=tk.EW)
        explanation_bar.grid(row=12, column=0, pady=2, padx=5, columnspan=2, sticky=tk.W)

    def confirm(self, M, variable_database, variable_energy_tolerance, variable_page_height, variable_calib_uncertainty, variable_calib_limit, variable_standard_limit, variable_sample_limit, variable_noncertified_uncertainty, variable_tctl_default_uncetrainty, variable_td_default_uncetrainty, variable_find_spectrumfile):
        with open(os.path.join('data','k0-set.cfg'), 'w') as settingsfile:
            settingsfile.write(f'database <#> {variable_database.get()}\nenergy tolerance <#> {variable_energy_tolerance.get()}\npage height <#> {variable_page_height.get()}\nmax allowed calibration uncertainty <#> {variable_calib_uncertainty.get()}\ncalibs statistical uncertainty limit <#> {variable_calib_limit.get()}\nstandard statistical uncertainty limit <#> {variable_standard_limit.get()}\nsample statistical uncertainty limit <#> {variable_sample_limit.get()}\nnon certified standard uncertainties <#> {variable_noncertified_uncertainty.get()}\ndefault tc&tl uncertainties <#> {variable_tctl_default_uncetrainty.get()}\ndefault td uncertainty <#> {variable_td_default_uncetrainty.get()}\nlook for spectrum file <#> {variable_find_spectrumfile.get()}')
        M.destroy()
        main_script()


class SampleWindow:
    def __init__(self, parent, spectra_list, idx, limit=20):
        spectrum = spectra_list[idx]
        spectrum_title = 'Sample'
        if spectrum.define() == 'standard':
            spectrum_title = 'Standard'
        elif spectrum.define() == 'background':
            spectrum_title = 'Blank'
        if spectrum.define() != 'background':
            parent.title(f'{spectrum_title} ({spectrum.filename()})')
        else:
            parent.title(f'{spectrum_title}')
        parent.resizable(False,False)
        self.selected_sample = None
        if spectrum.sample is not None:
            sample_name = spectrum.sample.name
            def_mass, def_u_mass = spectrum.sample.weighted_mass, spectrum.sample.weighted_mass_unc
            def_moisture, def_u_moisture = spectrum.sample.moisture*100, spectrum.sample.moisture_unc*100
            def_th_selfshielding, def_uth_selfshielding = spectrum.sample.th_selfshielding, spectrum.sample.th_selfshielding_unc
            def_epi_selfshielding, def_uepi_selfshielding = spectrum.sample.epi_selfshielding, spectrum.sample.epi_selfshielding_unc
            def_dl, def_udl = spectrum.sample.dl, spectrum.sample.dl_unc
            def_dh, def_udh = spectrum.sample.dh, spectrum.sample.dh_unc
            def_density, def_udensity = spectrum.sample.density, spectrum.sample.density_unc
            total_mass, total_umass = spectrum.sample.mass, spectrum.sample.unc_mass
        else:
            sample_name = ''
            def_mass, def_u_mass = 0.0, 0.0
            def_moisture, def_u_moisture = 0.0, 0.0
            def_th_selfshielding, def_uth_selfshielding = 1.0, 0.0
            def_epi_selfshielding, def_uepi_selfshielding = 1.0, 0.0
            def_dl, def_udl = 0.0, 0.0
            def_dh, def_udh = 0.1, 0.0
            def_density, def_udensity = 0.001, 0.0
            total_mass, total_umass = 0.0, 0.0
        
        mframe = tk.Frame(parent)
        self.infobox = tk.Label(mframe, text='', anchor=tk.W)
        tk.Label(mframe, text='material', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        sample_type_CB = ttk.Combobox(mframe, width=20, state='readonly')
        sample_type_CB.grid(row=0, column=1, columnspan=2)
        sample_type_CB['values'] = ['']+[filename[:-len('.csv')] for filename in os.listdir(os.path.join('data','samples')) if filename[-len('.csv'):].lower()=='.csv']
        RM_label = tk.Label(mframe, text='', width=3)
        if spectrum.define() == 'sample':
            RM_label.grid(row=0, column=3, sticky=tk.W)
        stext = gui_things.ScrollableText(mframe, width=45, height=12)
        stext.grid(row=1, column=0, columnspan=5, pady=5)

        tk.Frame(mframe).grid(row=2, column=0, pady=5)
        tk.Label(mframe, text='mass', anchor=tk.W).grid(row=3, column=0, sticky=tk.W)
        tk.Label(mframe, text='x').grid(row=3, column=1)
        tk.Label(mframe, text='u(x)').grid(row=3, column=2)
        tk.Label(mframe, text='weighted mass / g', anchor=tk.W).grid(row=4, column=0, sticky=tk.W)
        massSpin = tk.Spinbox(mframe, from_=0.00000, to=1000.00000, increment=0.00001, width=10)
        massSpin.grid(row=4, column=1)
        massSpin.delete(0, tk.END)
        massSpin.insert(tk.END,def_mass)
        u_massSpin = tk.Spinbox(mframe, from_=0.00000, to=1.00000, increment=0.00001, width=10)
        u_massSpin.grid(row=4, column=2)
        u_massSpin.delete(0, tk.END)
        u_massSpin.insert(tk.END,def_u_mass)
        moistureSpin = tk.Spinbox(mframe, from_=0.00, to=100.00, increment=0.01, width=10)
        moistureSpin.delete(0, tk.END)
        moistureSpin.insert(tk.END,def_moisture)
        u_moistureSpin = tk.Spinbox(mframe, from_=0.00, to=10.00, increment=0.01, width=10)
        u_moistureSpin.delete(0, tk.END)
        u_moistureSpin.insert(tk.END,def_u_moisture)

        if spectrum.define() != 'background':
            tk.Label(mframe, text='moisture / %', anchor=tk.W).grid(row=5, column=0, sticky=tk.W)
            moistureSpin.grid(row=5, column=1)
            u_moistureSpin.grid(row=5, column=2)

        tk.Label(mframe, text='mass / g', anchor=tk.W).grid(row=6, column=0, sticky=tk.W)
        masslabel = tk.Label(mframe, text=f'{total_mass:.3e}')
        masslabel.grid(row=6, column=1)
        umasslabel = tk.Label(mframe, text=f'{total_umass:.1e}')
        umasslabel.grid(row=6, column=2)
        tk.Frame(mframe).grid(row=7, column=0, pady=5)

        GthSpin = tk.Spinbox(mframe, from_=0.0000, to=1.0000, increment=0.0001, width=10)
        GthSpin.delete(0, tk.END)
        GthSpin.insert(tk.END,def_th_selfshielding)
        u_GthSpin = tk.Spinbox(mframe, from_=0.0000, to=1.0000, increment=0.0001, width=10)
        u_GthSpin.delete(0, tk.END)
        u_GthSpin.insert(tk.END,def_uth_selfshielding)

        if spectrum.define() != 'background':
            tk.Label(mframe, text='Gth / 1', anchor=tk.W).grid(row=10, column=0, sticky=tk.W)
            GthSpin.grid(row=10, column=1)
            u_GthSpin.grid(row=10, column=2)

        GepiSpin = tk.Spinbox(mframe, from_=0.0000, to=1.0000, increment=0.0001, width=10)
        GepiSpin.delete(0, tk.END)
        GepiSpin.insert(tk.END,def_epi_selfshielding)
        u_GepiSpin = tk.Spinbox(mframe, from_=0.0000, to=1.0000, increment=0.0001, width=10)
        u_GepiSpin.delete(0, tk.END)
        u_GepiSpin.insert(tk.END,def_uepi_selfshielding)

        DLSpin = tk.Spinbox(mframe, from_=-50.0, to=50.0, increment=0.1, width=10)
        DLSpin.delete(0, tk.END)
        DLSpin.insert(tk.END,def_dl)
        u_DLSpin = tk.Spinbox(mframe, from_=0.0, to=10.0, increment=0.1, width=10)
        u_DLSpin.delete(0, tk.END)
        u_DLSpin.insert(tk.END,def_udl)
        
        if spectrum.define() == 'standard':
            tk.Label(mframe, text='Gepi / 1', anchor=tk.W).grid(row=11, column=0, sticky=tk.W)
            GepiSpin.grid(row=11, column=1)
            u_GepiSpin.grid(row=11, column=2)
        elif spectrum.define() == 'sample':
            tk.Frame(mframe).grid(row=11, column=0, pady=5)
            tk.Label(mframe, text='Δl / mm', anchor=tk.W).grid(row=12, column=0, sticky=tk.W)
            DLSpin.grid(row=12, column=1)
            u_DLSpin.grid(row=12, column=2)

        DHSpin = tk.Spinbox(mframe, from_=0.0, to=50.0, increment=0.1, width=10)
        DHSpin.delete(0, tk.END)
        DHSpin.insert(tk.END,def_dh)
        u_DHSpin = tk.Spinbox(mframe, from_=0.0, to=10.0, increment=0.1, width=10)
        u_DHSpin.delete(0, tk.END)
        u_DHSpin.insert(tk.END,def_udh)

        if spectrum.define() != 'background':
            tk.Frame(mframe).grid(row=13, column=0, pady=5)
            tk.Label(mframe, text='sample height / mm', anchor=tk.W).grid(row=14, column=0, sticky=tk.W)
            DHSpin.grid(row=14, column=1)
            u_DHSpin.grid(row=14, column=2)

        DensitySpin = tk.Spinbox(mframe, from_=0.000, to=30.0, increment=0.001, width=10)
        DensitySpin.delete(0, tk.END)
        DensitySpin.insert(tk.END,def_density)
        u_DensitySpin = tk.Spinbox(mframe, from_=0.000, to=10.0, increment=0.001, width=10)
        u_DensitySpin.delete(0, tk.END)
        u_DensitySpin.insert(tk.END,def_udensity)

        if spectrum.define() != 'background':
            tk.Frame(mframe).grid(row=15, column=0, pady=5)
            tk.Label(mframe, text='density / g cm-3', anchor=tk.W).grid(row=16, column=0, sticky=tk.W)
            DensitySpin.grid(row=16, column=1)
            u_DensitySpin.grid(row=16, column=2)

        butt_frame = tk.Frame(mframe)
        logo_confirm = tk.PhotoImage(data=gui_things.beye)
        B_confirm_information = tk.Button(butt_frame, image=logo_confirm)
        B_confirm_information.pack(side=tk.LEFT)
        B_confirm_information.image = logo_confirm
        F_delete_selector_background = tk.Frame(butt_frame)
        self.update_sample_information = tk.IntVar(parent)
        R1 = tk.Radiobutton(F_delete_selector_background, text='selected', anchor=tk.W, value=0, variable=self.update_sample_information)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_delete_selector_background, text='all undefined', anchor=tk.W, value=1, variable=self.update_sample_information)
        R2.pack(anchor=tk.W)
        R3 = tk.Radiobutton(F_delete_selector_background, text='all', anchor=tk.W, value=2, variable=self.update_sample_information)
        R3.pack(anchor=tk.W)
        self.update_sample_information.set(0)
        F_delete_selector_background.pack(side=tk.LEFT)

        option_frame = tk.Frame(butt_frame)

        self.check_find_for_peaks_variable = tk.IntVar(parent)
        check_find_for_peaks = tk.Checkbutton(option_frame, offvalue=0, onvalue=1, text='find peaks', variable=self.check_find_for_peaks_variable)
        if spectrum.define() == 'standard' or spectrum.define() == 'sample':
            check_find_for_peaks.pack(anchor=tk.W, padx=5)
        self.check_find_for_peaks_variable.set(0)

        self.check_clear_previous_selection_variable = tk.IntVar(parent)
        check_clear_for_peaks = tk.Checkbutton(option_frame, offvalue=0, onvalue=1, text='clear previous', variable=self.check_clear_previous_selection_variable)
        if spectrum.define() == 'standard' or spectrum.define() == 'sample':
            check_clear_for_peaks.pack(anchor=tk.W, padx=5)
        self.check_clear_previous_selection_variable.set(0)

        option_frame.pack(side=tk.LEFT)

        butt_frame.grid(row=17, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        self.infobox.grid(row=18, column=0, columnspan=4, sticky=tk.EW)
        mframe.pack(anchor=tk.NW, padx=5, pady=5)

        sample_type_CB.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>' : self.select_sample(sample_type_CB, stext, RM_label))
        B_confirm_information.configure(command=lambda : self.confirm_selection(spectra_list, idx, massSpin, u_massSpin, moistureSpin, u_moistureSpin, GthSpin, u_GthSpin, limit, masslabel, umasslabel, GepiSpin, u_GepiSpin, DLSpin, u_DLSpin, DHSpin, u_DHSpin, DensitySpin, u_DensitySpin))
        if spectrum.sample is not None:
            sample_type_CB.set(sample_name)
            self.selected_sample = spectrum.sample
            text = f'{self.selected_sample.description}\n\n{self.selected_sample._as_text_display()}'
            if self.selected_sample.sample_type == 'Reference Material':
                RM_label.configure(text='*RM')
            else:
                RM_label.configure(text='')
            stext._update(text)
        elif sample_name in sample_type_CB['values']:
            sample_type_CB.set(sample_name)
            self.select_sample(sample_type_CB, stext, RM_label)

    def select_sample(self, box, stext, label):
        if box.get() == '':
            self.selected_sample = None
            label.configure(text='')
            stext._update()
        else:
            self.selected_sample = naaobject.Sample(f'{box.get()}.csv', non_certified_uncertainty=None)
            if self.selected_sample.sample_type == 'Reference Material':
                label.configure(text='*RM')
            else:
                label.configure(text='')
            text = f'{self.selected_sample.description}\n\n{self.selected_sample._as_text_display()}'
            stext._update(text)

    def confirm_selection(self, spectra_list, idx, massSpin, u_massSpin, moistureSpin, u_moistureSpin, GthSpin, u_GthSpin, limit, masslabel, umasslabel, GepiSpin, u_GepiSpin, DLSpin, u_DLSpin, DHSpin, u_DHSpin, DensitySpin, u_DensitySpin):
        try:
            mass = float(massSpin.get())
        except:
            mass = 0.0
        try:
            u_mass = float(u_massSpin.get())
        except:
            u_mass = 0.0
        try:
            moisture = float(moistureSpin.get()) / 100
        except:
            moisture = 0.0
        try:
            u_moisture = float(u_moistureSpin.get()) / 100
        except:
            u_moisture = 0.0
        try:
            th_selfshield = float(GthSpin.get())
        except:
            th_selfshield = 1.0
        try:
            u_th_selfshield = float(u_GthSpin.get())
        except:
            u_th_selfshield = 0.0
        try:
            epi_selfshield = float(GepiSpin.get())
        except:
            epi_selfshield = 1.0
        try:
            u_epi_selfshield = float(u_GepiSpin.get())
        except:
            u_epi_selfshield = 0.0
        try:
            delta_l = float(DLSpin.get())
        except:
            delta_l = 0.0
        try:
            u_delta_l = float(u_DLSpin.get())
        except:
            u_delta_l = 0.0
        try:
            delta_h = float(DHSpin.get())
            if delta_h <= 0:
                delta_h = 0.1
        except:
            delta_h = 0.0
        try:
            u_delta_h = float(u_DHSpin.get())
        except:
            u_delta_h = 0.0
        try:
            density = float(DensitySpin.get())
            if density <= 0:
                density = 0.001
        except:
            density = 0.001
        try:
            u_density = float(u_DensitySpin.get())
        except:
            u_density = 0.0
        if mass > 0 and moisture >= 0.0 and moisture < 1:
            if self.selected_sample is not None:
                subsample = naaobject.Subsample(f'{self.selected_sample.name}.csv', non_certified_uncertainty=limit, weighted_mass=mass, weighted_mass_unc=u_mass, moisture=moisture, moisture_unc=u_moisture, th_selfshielding=th_selfshield, th_selfshielding_unc=u_th_selfshield, epi_selfshielding=epi_selfshield, epi_selfshielding_unc=u_epi_selfshield, delta_l=delta_l, delta_l_unc=u_delta_l, delta_h=delta_h, delta_h_unc=u_delta_h, old_sample=self.selected_sample, density=density, density_unc=u_density)
            else:
                subsample = naaobject.Subsample('_', weighted_mass=mass, weighted_mass_unc=u_mass, moisture=moisture, moisture_unc=u_moisture, th_selfshielding=th_selfshield, th_selfshielding_unc=u_th_selfshield, epi_selfshielding=epi_selfshield, epi_selfshielding_unc=u_epi_selfshield, delta_l=delta_l, delta_l_unc=u_delta_l, delta_h=delta_h, delta_h_unc=u_delta_h, density=density, density_unc=u_density)
            masslabel.configure(text=f'{subsample.mass:.3e}')
            umasslabel.configure(text=f'{subsample.unc_mass:.1e}')
            if self.update_sample_information.get() == 0:
                spectra_list[idx].update_sample(subsample)
                if self.check_clear_previous_selection_variable.get() == 1:
                    spectra_list[idx]._clear_emission_from_certificate()
                if self.check_find_for_peaks_variable.get() == 1:
                    spectra_list[idx]._select_emission_from_certificate()
                self.infobox.configure(text='material information updated to selected')
            elif self.update_sample_information.get() == 1:
                spectra_list[idx].update_sample(subsample)
                if self.check_clear_previous_selection_variable.get() == 1:
                    spectra_list[idx]._clear_emission_from_certificate()
                if self.check_find_for_peaks_variable.get() == 1:
                    spectra_list[idx]._select_emission_from_certificate()
                for spc in spectra_list:
                    if spc.sample is None:
                        spc.update_sample(subsample)
                        if self.check_clear_previous_selection_variable.get() == 1:
                            spc._clear_emission_from_certificate()
                        if self.check_find_for_peaks_variable.get() == 1:
                            spc._select_emission_from_certificate(self.check_clear_previous_selection_variable.get())
                self.infobox.configure(text='material information updated to undefined')
            else:
                for spc in spectra_list:
                    spc.update_sample(subsample)
                    if self.check_clear_previous_selection_variable.get() == 1:
                        spc._clear_emission_from_certificate()
                    if self.check_find_for_peaks_variable.get() == 1:
                        spc._select_emission_from_certificate()
                self.infobox.configure(text='material information updated to all')
        else:
            self.infobox.configure(text='mass value should be > 0')


class PeaklistWindow:
    def __init__(self, parent, spectrum, local_peak_list, local_suspected, nline, background=None, database=[]):
        self.SpectrumProfile = None
        self.active_state = False
        self.PeakInformation = None
        self.pageindex = 0
        self.nline = nline
        self.k0_monitor_index = tk.IntVar(parent)
        self.k0_monitor_index.set(spectrum.k0_monitor_index)
        logo_minus = tk.PhotoImage(data=gui_things.previous)
        logo_plus = tk.PhotoImage(data=gui_things.following)
        parent.title(f'{spectrum.filename()} spectrum ({spectrum.identity})')
        parent.resizable(False, False)
        info_frame = tk.Frame(parent)
        f_buttons = tk.Frame(info_frame)
        logo_sprofile = tk.PhotoImage(data=gui_things.fspectrum)
        B_show_spectrum_profile = tk.Button(f_buttons, image=logo_sprofile, command=lambda : self.show_spectrum(parent, spectrum, background))
        B_show_spectrum_profile.pack(side=tk.LEFT)
        B_show_spectrum_profile.image = logo_sprofile
        f_buttons.grid(row=0, column=0, columnspan=5, sticky=tk.W)
        tk.Label(info_frame, text='path:', anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{spectrum.spectrumpath}', anchor=tk.E, width=80).grid(row=1, column=1, columnspan=10)
        tk.Label(info_frame, text='files:', anchor=tk.W).grid(row=2, column=0, sticky=tk.W)
        name_of_files = [f'{os.path.basename(item[0])} ({item[1]})' for item in spectrum.source]
        tk.Label(info_frame, text=', '.join(name_of_files), anchor=tk.W, width=80).grid(row=2, column=1, columnspan=10, sticky=tk.W)
        tk.Label(info_frame, text='start:', width=6, anchor=tk.W).grid(row=3, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{spectrum.readable_datetime()}', width=18, anchor=tk.W).grid(row=3, column=1, sticky=tk.W)
        tk.Label(info_frame).grid(row=3, column=2, padx=3)
        tk.Label(info_frame, text='real / s:', width=8, anchor=tk.W).grid(row=3, column=3)
        tk.Label(info_frame, text=f'{spectrum.real_time:.0f}', width=9, anchor=tk.W).grid(row=3, column=4, sticky=tk.W)
        tk.Label(info_frame).grid(row=3, column=5, padx=3)
        tk.Label(info_frame, text='live / s:', width=8, anchor=tk.W).grid(row=3, column=6)
        tk.Label(info_frame, text=f'{spectrum.live_time:.0f}', width=9, anchor=tk.W).grid(row=3, column=7, sticky=tk.W)
        tk.Label(info_frame).grid(row=3, column=8, padx=3)
        tk.Label(info_frame, text='dead / %:', width=9, anchor=tk.W).grid(row=3, column=9)
        tk.Label(info_frame, text=f'{spectrum.deadtime(out="float"):.2f}', width=6, anchor=tk.W).grid(row=3, column=10, sticky=tk.W)

        info_frame.pack(anchor=tk.W, padx=5, pady=5)
        peak_frame = tk.Frame(parent)
        peaklist_frame = tk.Frame(peak_frame)
        scroll_pages_frame = tk.Frame(peak_frame)
        B_pageminus1 = tk.Button(scroll_pages_frame, image=logo_minus, command=lambda : self.previous_page(spectrum, local_peak_list, local_suspected, background, peaklist_frame, parent, database))
        B_pageminus1.grid(row=0, column=0)
        B_pageminus1.image = logo_minus
        self.page_selector = tk.Label(scroll_pages_frame, text=f'page {self.pageindex + 1} of {len(local_peak_list)}')
        self.page_selector.grid(row=0, column=1, padx=5)
        B_pageplus1 = tk.Button(scroll_pages_frame, image=logo_plus, command=lambda : self.following_page(spectrum, local_peak_list, local_suspected, background, peaklist_frame, parent, database))
        B_pageplus1.grid(row=0, column=2)
        B_pageplus1.image = logo_plus
        scroll_pages_frame.pack(pady=5)
        self.update_peaklist(parent, peaklist_frame, spectrum, local_peak_list[self.pageindex], local_suspected[self.pageindex], background, database)
        peak_frame.pack(anchor=tk.W, padx=5, pady=5)

    def update_peaklist(self, parent, pframe, spectrum, pag_local_peak_list, pag_local_suspected, background, database=[]):
        cdn = pframe.winfo_children()
        for i in cdn:
            i.destroy()
        tk.Label(pframe, text='channel', width=10).grid(row=0, column=0)
        tk.Label(pframe, text='E / keV', width=10).grid(row=0, column=1)
        tk.Label(pframe, text='net area / 1', width=10).grid(row=0, column=2)
        tk.Label(pframe, text='uncertainty', width=10).grid(row=0, column=3)
        tk.Label(pframe, text='FWHM / 1', width=10).grid(row=0, column=4)
        if spectrum.define() == 'standard':
            tk.Label(pframe, text='k0', width=3).grid(row=0, column=5)
        tk.Label(pframe, text='emitter', width=12).grid(row=0, column=6)
        tk.Label(pframe, text='n', width=4).grid(row=0, column=7)
        for idx, line in enumerate(pag_local_peak_list):
            #[0] canale
            #[1] inc. canale
            #[2] energia / keV
            #[3] inc. energia / keV
            #[4] area netta / 1
            #[5] inc. area netta / 1
            tk.Label(pframe, text=f'{line[0]:.2f}').grid(row=idx + 1, column=0)
            tk.Label(pframe, text=f'{line[2]:.2f}').grid(row=idx + 1, column=1)
            tk.Label(pframe, text=f'{line[4]:.0f}').grid(row=idx + 1, column=2, sticky=tk.E)
            tk.Label(pframe, text=f'{100*line[5]/line[4]:.1f} %').grid(row=idx + 1, column=3)
            tk.Label(pframe, text=f'{line[6]:.2f}').grid(row=idx + 1, column=4)
            if spectrum.define() == 'standard':
                Rb = tk.Radiobutton(pframe, text='', value=self.nline*self.pageindex + idx, variable=self.k0_monitor_index)
                Rb.grid(row=idx + 1, column=5)
                Rb.configure(command=lambda : self.check_k0_monitor(spectrum))
            sel_CB = ttk.Combobox(pframe, width=12, state='disabled')
            sel_CB.grid(row=idx + 1, column=6)
            sel_CB['values'] = [item.emission for item in pag_local_suspected[idx]]
            if len(sel_CB['values']) > 0:
                sel_CB.configure(state='readonly')
                tk.Label(pframe, text=f'({len(sel_CB["values"])})', width=4).grid(row=idx + 1, column=7)
                if spectrum.assign_nuclide[self.nline*self.pageindex + idx] >= 0:
                    sel_CB.set(sel_CB['values'][spectrum.assign_nuclide[self.nline*self.pageindex + idx]])

            sel_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>', CB=sel_CB, idx=idx : self.emission_selection(CB, spectrum, idx))
            
            logo_clear_selection = tk.PhotoImage(data=gui_things.smallnone)
            B_clear_selection = tk.Button(pframe, image=logo_clear_selection, command=lambda sel_CB=sel_CB, idx=idx: self.clear_selection_effect(sel_CB, spectrum, idx))
            B_clear_selection.grid(row=idx + 1, column=8)
            B_clear_selection.image = logo_clear_selection
            if spectrum.define() not in ('standard', 'sample', 'calibration', 'PT_spectrum'):
                B_clear_selection.configure(state=tk.DISABLED)
            logo_find_on_profile = tk.PhotoImage(data=gui_things.smallfind)
            B_find_on_spectrum_profile = tk.Button(pframe, image=logo_find_on_profile, command=lambda centroid=line[0]: self.show_spectrum(parent, spectrum, background, centroid))
            B_find_on_spectrum_profile.grid(row=idx + 1, column=9)
            B_find_on_spectrum_profile.image = logo_find_on_profile
            logo_info = tk.PhotoImage(data=gui_things.smallinfo)
            B_peak_info = tk.Button(pframe, image=logo_info, command=lambda idx=idx : self.display_emitter_info(spectrum, idx, pag_local_suspected, database))
            B_peak_info.grid(row=idx + 1, column=10)
            B_peak_info.image = logo_info
            if spectrum.define() != 'standard' and spectrum.define() != 'sample':
                B_peak_info.configure(state=tk.DISABLED)
        pframe.pack(anchor=tk.NW)

    def clear_selection_effect(self, sel_CB, spectrum, idx):
        spectrum.assign_nuclide[self.nline*self.pageindex + idx] = -1
        sel_CB.set('')
        if spectrum.k0_monitor_index == self.nline*self.pageindex + idx:
            self.k0_monitor_index.set(-1)
            spectrum.k0_monitor_index = self.k0_monitor_index.get()

    def emission_selection(self, sel_CB, spectrum, idx):
        spectrum.assign_nuclide[self.nline*self.pageindex + idx] = sel_CB.current()

    def check_k0_monitor(self, spectrum):
        spectrum.k0_monitor_index = self.k0_monitor_index.get()

    def previous_page(self, spectrum, local_peak_list, local_suspected, background, frame, parent, database):
        if self.pageindex > 0:
            self.pageindex -= 1
            self.page_selector.configure(text=f'page {self.pageindex + 1} of {len(local_peak_list)}')
            pag_local_peak_list, pag_local_suspected = local_peak_list[self.pageindex], local_suspected[self.pageindex]
            self.update_peaklist(parent, frame, spectrum, pag_local_peak_list, pag_local_suspected, background, database)

    def following_page(self, spectrum, local_peak_list, local_suspected, background, frame, parent, database):
        if self.pageindex < len(local_peak_list) - 1:
            self.pageindex += 1
            self.page_selector.configure(text=f'page {self.pageindex + 1} of {len(local_peak_list)}')
            pag_local_peak_list, pag_local_suspected = local_peak_list[self.pageindex], local_suspected[self.pageindex]
            self.update_peaklist(parent, frame, spectrum, pag_local_peak_list, pag_local_suspected, background, database)

    def _get_energy(self, spectrum, x):
        if spectrum.calibration is not None:
            return spectrum.calibration.reference_calibration.energy_fit(x)
        else:
            return np.nan

    def show_spectrum(self, parent, spectrum, background, centroid=None):
        if spectrum.counts is not None:
            if self.active_state == False and spectrum.counts is not None:
                self.SpectrumProfile = tk.Toplevel(parent)
                self.SpectrumProfile.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.SpectrumProfile))
                self.active_state = True
                zoom_range = (10, 15, 20, 30, 50, 75, 100, 150)
                self.SpectrumProfile.dx_zoom = 15
                self.SpectrumProfile.original_limit = len(spectrum.counts)
                self.SpectrumProfile.original_ylimit = (1,max(spectrum.counts)*3+2)
                self.SpectrumProfile.title(f'{spectrum.filename()} spectrum profile')
                self.SpectrumProfile.f = Figure(figsize=(7, 4.5))
                self.SpectrumProfile.ax = self.SpectrumProfile.f.add_subplot(111)
                self.SpectrumProfile.ax.format_coord = lambda x, y: f'channel={int(x)}, energy={self._get_energy(spectrum, x):.1f} keV, counts={int(y)}'
                Figur = tk.Frame(self.SpectrumProfile)
                Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
                self.SpectrumProfile.canvas = FigureCanvasTkAgg(self.SpectrumProfile.f, master=Figur)
                self.SpectrumProfile.canvas.draw()
                self.SpectrumProfile.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                self.SpectrumProfile.ax.plot(np.linspace(0.5,len(spectrum.counts)+0.5,num=len(spectrum.counts)), spectrum.counts, marker='o', linestyle='-', color='k', linewidth=0.5, markersize=3, markerfacecolor='r')
                self.SpectrumProfile.ax.set_ylabel('counts')
                self.SpectrumProfile.ax.set_xlabel(r'$E$ / keV')
                ticks=[line[0] for line in spectrum.peak_list]
                ticklabels=[f'{line[2]:.1f}' for line in spectrum.peak_list]
                self.SpectrumProfile.ax.set_xticks(ticks)
                self.SpectrumProfile.ax.set_xticklabels(ticklabels)
                self.SpectrumProfile.ax.grid(linestyle='-.')
                if centroid is not None:
                    self.SpectrumProfile.ax.set_xlim(centroid-self.SpectrumProfile.dx_zoom,centroid+self.SpectrumProfile.dx_zoom)
                else:
                    self.SpectrumProfile.ax.set_xlim(0,len(spectrum.counts))
                self.SpectrumProfile.ax.set_ylim(self.SpectrumProfile.original_ylimit)#1,max(spectrum.counts)*3+2)
                self.SpectrumProfile.ax.set_yscale('log', nonposy='clip')
                self.SpectrumProfile.f.tight_layout()
                self.SpectrumProfile.canvas.draw()
                F_buttons = tk.Frame(self.SpectrumProfile)

                logo_add_background = tk.PhotoImage(data=gui_things.a_background)
                logo_remove_background = tk.PhotoImage(data=gui_things.r_background)
                B_show_background = tk.Button(F_buttons, image=logo_add_background)
                B_show_background.configure(command=lambda : self.plus_background_or_not(B_show_background, spectrum, background, logo_add_background, logo_remove_background))
                B_show_background.pack(side=tk.LEFT)
                B_show_background.image = logo_add_background
                if background is None:
                    B_show_background.configure(state='disabled')
                elif background.counts is None:
                    B_show_background.configure(state='disabled')

                evx = gui_things.IZoomSlider(F_buttons, values=zoom_range, default=self.SpectrumProfile.dx_zoom)
                evx.pack(side=tk.LEFT)
                evx.variable.trace('w', lambda a,b,c : self._update_variable(evx))
                logo_zoom_plus = tk.PhotoImage(data=gui_things.peakzoomin)
                logo_zoom_reset = tk.PhotoImage(data=gui_things.peakzoomout)
                B_zoom_current = tk.Button(F_buttons, image=logo_zoom_plus)
                B_zoom_current.configure(command=lambda : self.zoom_on_peak(B_zoom_current, spectrum.counts, logo_zoom_plus, logo_zoom_reset))
                B_zoom_current.pack(side=tk.LEFT)
                B_zoom_current.image = logo_zoom_plus
                coordinates = tk.Label(F_buttons, text='', anchor=tk.E)
                coordinates.pack(anchor=tk.E, side=tk.LEFT, fill=tk.X, expand=True)
                F_buttons.pack(anchor=tk.W, fill=tk.X, padx=5)    
                
                cid = self.SpectrumProfile.canvas.mpl_connect('scroll_event', lambda event='scroll_event',ax=self.SpectrumProfile.ax,canvas=self.SpectrumProfile.canvas : self.on_scroll(event,ax,canvas))
                sid = self.SpectrumProfile.canvas.mpl_connect('motion_notify_event', lambda event='motion_notify_event', coordinates=coordinates : self.on_motion(event,coordinates))
                self.SpectrumProfile.update()
                width, height, xpos, ypos, xwidth = self.SpectrumProfile.winfo_width(), self.SpectrumProfile.winfo_height(), parent.winfo_rootx(), parent.winfo_rooty(), parent.winfo_width()
                self.SpectrumProfile.geometry(f'{width}x{height}+{xpos+xwidth}+{ypos}')
            else:
                self.SpectrumProfile.focus_force()
                if centroid is not None:
                    self.SpectrumProfile.ax.set_xlim(centroid-self.SpectrumProfile.dx_zoom,centroid+self.SpectrumProfile.dx_zoom)
                else:
                    self.SpectrumProfile.ax.set_xlim(0,len(spectrum.counts))
                self.SpectrumProfile.f.tight_layout()
                self.SpectrumProfile.canvas.draw()

    def plus_background_or_not(self, B, spectrum, background, add, remove):
        #add or remove background visualization from graph
        background_counts = (spectrum.live_time/background.live_time) * background.counts
        if len(self.SpectrumProfile.ax.lines) == 2:
            self.SpectrumProfile.ax.lines.pop()
            B.configure(image=add)
            B.image = add
        else:
            self.SpectrumProfile.ax.plot(np.linspace(0.5,len(background_counts)+0.5,num=len(background_counts)), background_counts, marker='', linestyle='-', color='g', linewidth=0.5)
            B.configure(image=remove)
            B.image = remove
        self.SpectrumProfile.canvas.draw()

    def _update_variable(self, evx):
        newvalue = min(evx.values, key=lambda x:abs(x-int(evx.Scale.get())))
        self.SpectrumProfile.dx_zoom = newvalue

    def on_motion(self, event, coordinates):
        #mouse motion on spectrum profile
        if event.xdata is not None and event.ydata is not None:
            if event.xdata > 0 and event.xdata < self.SpectrumProfile.original_limit:
                coordinates.configure(text=self.SpectrumProfile.ax.format_coord(event.xdata,event.ydata))

    def on_scroll(self, event, ax, canvas):
        #Scroll spectrum profile
        if event.xdata is not None and event.ydata is not None:
            if event.xdata > 0 and event.xdata < self.SpectrumProfile.original_limit:
                if ax.get_xlim()[0] == 0 and ax.get_xlim()[1] == self.SpectrumProfile.original_limit:
                    try:
                        ax.set_xlim(int(event.xdata-self.SpectrumProfile.dx_zoom+event.step*120/6),int(event.xdata+self.SpectrumProfile.dx_zoom+event.step*120/6))
                    except:
                        pass
                    else:
                        canvas.draw()
                else:
                    try:
                        centroid, diff = int(ax.get_xlim()[0]+(ax.get_xlim()[1]-ax.get_xlim()[0])/2), abs(int(event.xdata-(ax.get_xlim()[0]+(ax.get_xlim()[1]-ax.get_xlim()[0])/2)))
                        if diff == 0:
                            diff = 1
                        ax.set_xlim(int(centroid-self.SpectrumProfile.dx_zoom+event.step*diff),int(centroid+self.SpectrumProfile.dx_zoom+event.step*diff))
                    except:
                        pass
                    else:
                        canvas.draw()

    def zoom_on_peak(self, button, counts, logo_zoom_plus, logo_zoom_reset):
        if self.SpectrumProfile.ax.get_xlim() != (0, self.SpectrumProfile.original_limit):
            if self.SpectrumProfile.ax.get_ylim() == self.SpectrumProfile.original_ylimit:
                a, b = self.SpectrumProfile.ax.get_xlim()
                ymin, ymax = np.min(counts[int(a):int(b)])-1, np.max(counts[int(a):int(b)])+2
                if ymin < 1:
                    ymin = 1
                self.SpectrumProfile.ax.set_ylim(ymin, ymax)
                button.configure(image=logo_zoom_reset)
                button.image = logo_zoom_reset
            else:
                self.SpectrumProfile.ax.set_ylim(self.SpectrumProfile.original_ylimit)
                button.configure(image=logo_zoom_plus)
                button.image = logo_zoom_plus
            self.SpectrumProfile.f.tight_layout()
            self.SpectrumProfile.canvas.draw()
        elif self.SpectrumProfile.ax.get_xlim() == (0, self.SpectrumProfile.original_limit) and self.SpectrumProfile.ax.get_ylim() != self.SpectrumProfile.original_ylimit:
            self.SpectrumProfile.ax.set_ylim(self.SpectrumProfile.original_ylimit)
            button.configure(image=logo_zoom_plus)
            button.image = logo_zoom_plus
            self.SpectrumProfile.f.tight_layout()
            self.SpectrumProfile.canvas.draw()

    def display_emitter_info(self, spectrum, idx, pag_local_suspected, database):
        #emission information window
        m_index = spectrum.assign_nuclide[self.nline*self.pageindex + idx]
        if m_index >= 0:
            if self.PeakInformation is not None:
                self.PeakInformation.destroy()
            self.PeakInformation = tk.Toplevel()
            emitter = pag_local_suspected[idx][m_index]
            self.PeakInformation.title(f'Information - {emitter.emission}')
            self.PeakInformation.resizable(False, False)
            swidth = 10
            Info_header = tk.Frame(self.PeakInformation)
            tk.Label(Info_header, text='target', width=swidth).grid(row=0, column=0)
            tk.Label(Info_header, text='isotope', width=swidth).grid(row=0, column=1)
            tk.Label(Info_header, text='Q0', width=swidth).grid(row=0, column=2)
            tk.Label(Info_header, text='urQ0', width=swidth).grid(row=0, column=3)
            tk.Label(Info_header, text='Er', width=swidth).grid(row=0, column=4)
            tk.Label(Info_header, text='urEr', width=swidth).grid(row=0, column=5)
            tk.Label(Info_header, text=emitter.target, width=swidth).grid(row=1, column=0)
            tk.Label(Info_header, text=f'{emitter.line[68]}-{int(emitter.line[69])}', width=swidth).grid(row=1, column=1)
            tk.Label(Info_header, text=emitter.line[75], width=swidth).grid(row=1, column=2)
            tk.Label(Info_header, text=self.f_value(emitter.line[76],'Q0'), width=swidth).grid(row=1, column=3)
            tk.Label(Info_header, text=emitter.line[77], width=swidth).grid(row=1, column=4)
            tk.Label(Info_header, text=self.f_value(emitter.line[78],'Er'), width=swidth).grid(row=1, column=5)
            tk.Label(Info_header, text='', width=swidth).grid(row=2, column=0)
            tk.Label(Info_header, text='emitter', width=swidth).grid(row=3, column=0)
            tk.Label(Info_header, text='Eγ', width=swidth).grid(row=3, column=1)
            tk.Label(Info_header, text='k0', width=swidth).grid(row=3, column=2)
            tk.Label(Info_header, text='urk0', width=swidth).grid(row=3, column=3)
            tk.Label(Info_header, text='COI', width=swidth).grid(row=3, column=4)
            tk.Label(Info_header, text='γ yield', width=swidth).grid(row=3, column=5)
            tk.Label(Info_header, text=emitter.emission.split()[0], width=swidth).grid(row=4, column=0)
            tk.Label(Info_header, text=' '.join(emitter.emission.split()[1:]), width=swidth).grid(row=4, column=1)
            tk.Label(Info_header, text=f'{emitter.line[7]}', width=swidth).grid(row=4, column=2)
            tk.Label(Info_header, text=self.f_value(emitter.line[8],'k0'), width=swidth).grid(row=4, column=3)
            tk.Label(Info_header, text=str(bool(emitter.line[10])), width=swidth).grid(row=4, column=4)
            tk.Label(Info_header, text=self.f_value(emitter.line[12]), width=swidth).grid(row=4, column=5)
            Info_header.pack(anchor=tk.NW, padx=5, pady=5)
            Decay_header = tk.Frame(self.PeakInformation)
            tk.Label(Decay_header, text=f'decay type: {emitter.line[22]}').grid(row=0, column=0, columnspan=2, sticky=tk.W)
            tk.Label(Decay_header, text='nuclide', width=10).grid(row=1, column=1)
            tk.Label(Decay_header, text='state', width=6).grid(row=1, column=2)
            tk.Label(Decay_header, text='half-life', width=10).grid(row=1, column=3)

            cascade = [[emitter.line[53], emitter.line[54], emitter.line[55], emitter.line[57], emitter.line[58]],
                [emitter.line[40], emitter.line[41], emitter.line[42], emitter.line[44], emitter.line[45]],
                [emitter.line[27], emitter.line[28], emitter.line[29], emitter.line[31], emitter.line[32]]]

            #headers
            for idx, casc in enumerate(cascade):
                if casc[0] != '':
                    tk.Label(Decay_header, text='↓', width=4).grid(row=2+idx, column=0)
                    nucld = casc[0]+'-'+str(int(casc[1]))
                    tk.Label(Decay_header, text=nucld, width=10).grid(row=2+idx, column=1)
                    if casc[2] != 1:
                        gstate = 'm'
                    else:
                        gstate = 'g'
                    tk.Label(Decay_header, text=gstate, width=6).grid(row=2+idx, column=2)
                    tk.Label(Decay_header, text=f'{casc[3]} {casc[4]}', width=10).grid(row=2+idx, column=3)
            Decay_header.pack(anchor=tk.NW, padx=5, pady=5)

            if cascade[-1][2] != 1:
                GSTATE = 'm'
            else:
                GSTATE = ''
            Otheremission_header = tk.Frame(self.PeakInformation)
            tk.Label(Otheremission_header, text=f'further emissions {cascade[-1][0]}-{int(cascade[-1][1])}{GSTATE}').grid(row=0, column=0, sticky=tk.W)

            list_1, list_2 = self.find_other_emissions(cascade[-1][0], cascade[-1][1], cascade[-1][2], emitter.energy, emitter.target, database)
            flistbox_1 = tk.Frame(Otheremission_header)
            scrollbar_listbox_1 = tk.Scrollbar(flistbox_1, orient=tk.VERTICAL)
            listbox_further_emissions = tk.Listbox(flistbox_1, width=25, height=8, yscrollcommand=scrollbar_listbox_1.set)
            listbox_further_emissions.pack(side=tk.LEFT)
            scrollbar_listbox_1.config(command=listbox_further_emissions.yview)
            listbox_further_emissions.pack(side=tk.LEFT)
            scrollbar_listbox_1.pack(side=tk.RIGHT, fill=tk.Y)
            for item in list_1:
                listbox_further_emissions.insert(0, item)

            tk.Label(Otheremission_header, text=f'further emissions from {emitter.target}').grid(row=0, column=2, sticky=tk.W)
            tk.Frame(Otheremission_header).grid(row=1, column=1, padx=25)
            
            flistbox_1.grid(row=1, column=0)

            flistbox_2 = tk.Frame(Otheremission_header)
            scrollbar_listbox_2 = tk.Scrollbar(flistbox_2, orient=tk.VERTICAL)
            listbox_ulterior_emissions = tk.Listbox(flistbox_2, width=30, height=8, yscrollcommand=scrollbar_listbox_2.set)
            listbox_ulterior_emissions.pack(side=tk.LEFT)
            scrollbar_listbox_2.config(command=listbox_ulterior_emissions.yview)
            listbox_ulterior_emissions.pack(side=tk.LEFT)
            scrollbar_listbox_2.pack(side=tk.RIGHT, fill=tk.Y)
            for item in list_2:
                listbox_ulterior_emissions.insert(0, item)
            
            flistbox_2.grid(row=1, column=2)
            Otheremission_header.pack(anchor=tk.N, padx=5, pady=5)

            FinalInfo_header = tk.Frame(self.PeakInformation)
            tk.Label(FinalInfo_header, text=f'notes:\n{emitter.line[14]}\n\n{emitter.line[83]}', width=60, justify=tk.LEFT, anchor=tk.W).pack(anchor=tk.W, fill=tk.X)
            FinalInfo_header.pack(anchor=tk.NW, padx=5, pady=5)
    
    def find_other_emissions(self, I, Ai, S, energy, target, database):
        """Find other emissions"""
        other_emission_list = []
        other_isotope_list = []
        for line in database:
            if I == line[2] and Ai == line[3] and S == line[4] and energy != line[5]:
                try:
                    lineemiss = (line[5], float(line[12]))
                except ValueError:
                    lineemiss = (line[5], np.nan)
                other_emission_list.append(lineemiss)
            elif target == line[1] and Ai != line[3]:
                if line[4] == 1.0:
                    gstate = ''
                else:
                    gstate = 'm'
                try:
                    yeld = float(line[12])
                except:
                    yeld = np.nan
                lineemiss = f'{line[2]}-{int(line[3])}{gstate} {line[5]} keV, {format(yeld,".1f")} %'
                other_isotope_list.append(lineemiss)
            elif target == line[1] and Ai == line[3] and S != line[4]:
                if line[4] == 1.0:
                    gstate = ''
                else:
                    gstate = 'm'
                try:
                    yeld = float(line[12])
                except:
                    yeld = np.nan
                lineemiss = f'{line[2]}-{int(line[3])}{gstate} {line[5]} keV, {format(yeld,".1f")} %'
                other_isotope_list.append(lineemiss)
        other_emission_list.sort(reverse=False, key=lambda x: -1 if np.isnan(x[1]) else x[1])
        other_emission_list = [f'{line[0]} keV, {format(line[1],".1f")} %' for line in other_emission_list]
        return other_emission_list, other_isotope_list

    def f_value(self, value, par='yield'):
        try:
            return f'{value:.1f} %'
        except:
            if par == 'k0':
                return f'{2.0:.1f} %'
            elif par == 'Q0':
                return f'{20.0:.1f} %'
            elif par == 'Er':
                return f'{50.0:.1f} %'
            else:
                return f'{np.nan:.1f} %'

    def on_closing(self,window):
        window.destroy()
        window = None
        self.active_state = False
        

class EffortWindow:
    def __init__(self, parent, NAA, M, take_focus=True):
        parent.title('New window')
        if take_focus == True:
            parent.focus()
        M.infotask.configure(text='maximum effort!')
        effort = 2000
        M.progress['value'] = 0
        M.progress['maximum'] = effort
        for _ in range(effort):
            M.progress['value'] += 1
            M.progress.update()
        M.infotask.configure(text='')


class DisplayIrradiationWindow:
    def __init__(self, parent, NAA):
        parent.title(f'Display irradiation ({NAA.irradiation.irradiation_code})')
        parent.resizable(False,False)
        info_frame = tk.Frame(parent)
        nline = 0
        tk.Label(info_frame, text='end of irradiation', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=NAA.irradiation.readable_datetime(), anchor=tk.W).grid(row=nline, column=1, columnspan=3, padx=5, sticky=tk.W)
        nline += 1
        tk.Frame(info_frame).grid(row=nline, column=0, pady=3)
        nline += 1
        tk.Label(info_frame, text='x', anchor=tk.W).grid(row=nline, column=1)
        tk.Label(info_frame, text='u(x)', anchor=tk.W).grid(row=nline, column=2)
        tk.Label(info_frame, text='ur(x)', anchor=tk.W).grid(row=nline, column=3)
        nline += 1
        ttk.Separator(info_frame, orient="horizontal").grid(
            row=nline, column=1, columnspan=3, sticky=tk.EW, padx=5)
        nline += 1
        tk.Label(info_frame, text='flux exposure / s', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{NAA.irradiation.irradiation_time:.1f}', anchor=tk.W).grid(row=nline, column=1, padx=5)
        tk.Label(info_frame, text=f'{NAA.irradiation.unc_irradiation_time:.1f}', anchor=tk.W).grid(row=nline, column=2, padx=5)
        tk.Label(info_frame, text=f'{np.abs(NAA.irradiation.unc_irradiation_time / NAA.irradiation.irradiation_time *100):.1f} %', anchor=tk.W).grid(row=nline, column=3, padx=5)
        nline += 1
        tk.Frame(info_frame).grid(row=nline, column=0, pady=3)
        nline += 1
        tk.Label(info_frame, text='channel', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=NAA.irradiation.channel_name, anchor=tk.W).grid(row=nline, column=1, columnspan=3, sticky=tk.W, padx=5)
        nline += 1
        tk.Frame(info_frame).grid(row=nline, column=0, pady=3)
        nline += 1
        tk.Label(info_frame, text='x', anchor=tk.W).grid(row=nline, column=1)
        tk.Label(info_frame, text='u(x)', anchor=tk.W).grid(row=nline, column=2)
        tk.Label(info_frame, text='ur(x)', anchor=tk.W).grid(row=nline, column=3)
        nline += 1
        ttk.Separator(info_frame, orient="horizontal").grid(
            row=nline, column=1, columnspan=3, sticky=tk.EW, padx=5)
        nline += 1
        tk.Label(info_frame, text='f / 1', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{NAA.irradiation.f_value:.2f}', anchor=tk.W).grid(row=nline, column=1, padx=5)
        tk.Label(info_frame, text=f'{NAA.irradiation.unc_f_value:.2f}', anchor=tk.W).grid(row=nline, column=2, padx=5)
        tk.Label(info_frame, text=f'{np.abs(NAA.irradiation.unc_f_value / NAA.irradiation.f_value *100):.1f} %', anchor=tk.W).grid(row=nline, column=3, padx=5)
        nline += 1
        tk.Label(info_frame, text='α / 1', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{NAA.irradiation.a_value:.4f}', anchor=tk.W).grid(row=nline, column=1, padx=5)
        tk.Label(info_frame, text=f'{NAA.irradiation.unc_a_value:.4f}', anchor=tk.W).grid(row=nline, column=2, padx=5)
        tk.Label(info_frame, text=f'{naaobject._get_division(NAA.irradiation.unc_a_value,NAA.irradiation.a_value):.1f} %', anchor=tk.W).grid(row=nline, column=3, padx=5)
        nline += 1
        tk.Label(info_frame, text='thermal flux / cm-2 s-1', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{NAA.irradiation.thermal_flux:.2e}', anchor=tk.W).grid(row=nline, column=1, padx=5)
        tk.Label(info_frame, text=f'{NAA.irradiation.unc_thermal_flux:.1e}', anchor=tk.W).grid(row=nline, column=2, padx=5)
        tk.Label(info_frame, text=f'{naaobject._get_division(NAA.irradiation.unc_thermal_flux,NAA.irradiation.thermal_flux):.1f} %', anchor=tk.W).grid(row=nline, column=3, padx=5)
        nline += 1
        tk.Label(info_frame, text='epithermal flux / cm-2 s-1', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{NAA.irradiation.epithermal_flux:.2e}', anchor=tk.W).grid(row=nline, column=1, padx=5)
        tk.Label(info_frame, text=f'{NAA.irradiation.unc_epithermal_flux:.1e}', anchor=tk.W).grid(row=nline, column=2, padx=5)
        tk.Label(info_frame, text=f'{naaobject._get_division(NAA.irradiation.unc_epithermal_flux,NAA.irradiation.epithermal_flux):.1f} %', anchor=tk.W).grid(row=nline, column=3, padx=5)
        nline += 1
        tk.Label(info_frame, text='fast flux / cm-2 s-1', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{NAA.irradiation.fast_flux:.2e}', anchor=tk.W).grid(row=nline, column=1, padx=5)
        tk.Label(info_frame, text=f'{NAA.irradiation.unc_fast_flux:.1e}', anchor=tk.W).grid(row=nline, column=2, padx=5)
        tk.Label(info_frame, text=f'{naaobject._get_division(NAA.irradiation.unc_fast_flux,NAA.irradiation.fast_flux):.1f} %', anchor=tk.W).grid(row=nline, column=3, padx=5)
        nline += 1
        tk.Label(info_frame, text='β / mm-1', anchor=tk.W).grid(row=nline, column=0, sticky=tk.W)
        tk.Label(info_frame, text=f'{NAA.irradiation.beta:.4f}', anchor=tk.W).grid(row=nline, column=1, padx=5)
        tk.Label(info_frame, text=f'{NAA.irradiation.unc_beta:.4f}', anchor=tk.W).grid(row=nline, column=2, padx=5)
        tk.Label(info_frame, text=f'{naaobject._get_division(NAA.irradiation.unc_beta,NAA.irradiation.beta):.1f} %', anchor=tk.W).grid(row=nline, column=3, padx=5)

        info_frame.pack(anchor=tk.NW, padx=5, pady=5)


class DisplayCalibrationWindow:
    def __init__(self, parent, NAA, M, folder=os.path.join('data','characterization')):
        parent.title(f'Display detector characterization ({NAA.calibration.name})')
        parent.resizable(False,False)
        try:
            with open(os.path.join(folder,f'{NAA.calibration.name}_log.txt')) as f:
                text = f.read()
        except:
            text = 'File not found Error!'
        try:
            with open(os.path.join(folder,f'{NAA.calibration.name}.pkl'), 'rb') as f:
                data_to_plot = pickle.load(f)
        except FileNotFoundError:
            data_to_plot = naaobject.FitData_Base()

        LIMIT = 2000
        if np.max(NAA.calibration.x_data) > 2000:
            LIMIT = 3000

        things_to_do_frame = tk.Frame(parent)
        stext = gui_things.ScrollableText(things_to_do_frame, data=text, width=65, height=34)
        stext.pack(fill=tk.BOTH, expand=True)

        actions_frame = tk.Frame(things_to_do_frame)
        fit_box = ttk.Combobox(actions_frame, width=25, state='readonly')
        fit_box.pack(side=tk.LEFT)
        logo_open_plots = tk.PhotoImage(data=gui_things.see_fit)
        B_open_plots = gui_things.Button(actions_frame, image=logo_open_plots)
        B_open_plots.pack(side=tk.LEFT, padx=5)
        B_open_plots.image = logo_open_plots
        actions_frame.pack(anchor=tk.W)
        fit_box['values'] = [f'position {item}' for item in data_to_plot.positions.keys()] + [f'emission {item}' for item in data_to_plot.emissions.keys()]
        if len(fit_box['values']) > 0:
            fit_box.set(fit_box['values'][0])
        else:
            fit_box.set('')

        things_to_show = tk.Frame(parent)
        f = Figure(figsize=(4.5, 5.5))
        ax_plot = f.add_subplot(411)
        ax_res = f.add_subplot(412)
        ax_third = f.add_subplot(413)
        ax_qder = f.add_subplot(414)
        Figur = tk.Frame(things_to_show)
        Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        canvas = FigureCanvasTkAgg(f, master=Figur)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ax_plot.plot(NAA.calibration.x_data, NAA.calibration.y_data, marker='o', markersize=3, markeredgewidth=0.5, linestyle='', markerfacecolor='r', color='k')
        x_fit = np.linspace(np.min(NAA.calibration.x_data), LIMIT, 400)#np.max(NAA.calibration.x_data)
        y_fit = NAA.calibration.reference_calibration._display_efficiency_fit(x_fit)
        ax_plot.plot(x_fit, y_fit, marker='', linestyle='-', linewidth=0.75, color='k')
        ax_plot.set_ylim(0, np.max(NAA.calibration.y_data)*1.1)

        y_fit = NAA.calibration.reference_calibration._display_efficiency_fit(NAA.calibration.x_data)
        ax_res.plot(NAA.calibration.x_data, (NAA.calibration.y_data - y_fit) / y_fit * 100, marker='o', markersize=3, markeredgewidth=0.5, linestyle='', markerfacecolor='r', color='k')

        #kedds
        for kedd_item in NAA.calibration.kedd_dict.values():
            y_fit = NAA.calibration._display_kedd_fit(x_fit, kedd_item)
            ax_third.plot(x_fit, y_fit, marker='', linestyle='-', linewidth=0.75, color='k')

        #ders
        for der_item in NAA.calibration.der_dict.values():
            y_fit = NAA.calibration._display_der_fit(x_fit, der_item)
            ax_qder.plot(x_fit, y_fit, marker='', linestyle='-', linewidth=0.75, color='k')
        if NAA.calibration.reference_calibration.der_exponent is not None:
            y_fit = NAA.calibration._display_der_fit(x_fit, (NAA.calibration.reference_calibration.der_exponent, NAA.calibration.reference_calibration.der_parameters, None))
            ax_qder.plot(x_fit, y_fit, marker='', linestyle='-', linewidth=0.75, color='k')

        ax_plot.set_xlim(0, LIMIT)
        ax_plot.set_xticklabels([])
        ax_res.set_xlim(0, LIMIT)
        ax_res.set_xticklabels([])
        ax_third.set_xlim(0, LIMIT)
        ax_third.set_xticklabels([])
        ax_qder.set_xlim(0, LIMIT)
        ax_plot.set_ylabel(r'$\varepsilon$ / 1')
        ax_res.set_ylabel(r'residuals / $\%$')
        ax_third.set_ylabel(r'$k\varepsilon\Delta d$ / 1')
        ax_qder.set_ylabel(r"$d^{\:'}_0$ / mm")
        ax_qder.set_xlabel(r'$E$ / keV')
        f.tight_layout()
        canvas.draw()

        things_to_do_frame.grid(row=0, column=0, padx=5)
        things_to_show.grid(row=0, column=1, padx=5)

        B_open_plots.configure(command=lambda : self.display_fit(fit_box, parent, data_to_plot))

    def _delta(self, parameters):
        _delta = np.sqrt(np.power(parameters[1], 2) - 4*parameters[0]*parameters[2])
        x1 = (-parameters[1] + _delta) / (2*parameters[0])
        x2 = (-parameters[1] - _delta) / (2*parameters[0])
        if x1 < 0 and x1 > x2:
            return x1
        elif x2 < 0 and x2 > x1:
            return x2
        else:
            return np.nan

    def display_fit(self, CB, parent, data_to_plot):
        ttest = CB.get()
        if ttest != '':
            which, key = ttest.split()
            try:
                key = float(key)
            except ValueError:
                pass
            data = [None, None, None, None]
            if which == 'position':# in self.data_to_plot.positions:
                data = data_to_plot.positions.get(key, data)
                plotype = 'positions'
            if which == 'emission':# in self.data_to_plot.emissions:
                data = data_to_plot.emissions.get(key, data)
                plotype = 'emissions'
            TPlot = tk.Toplevel(parent)
            if plotype == 'positions':
                TPlot.title(ttest + f' mm (k='+f'{data_to_plot.K:.0f})')
                f = Figure(figsize=(6.5, 7))
                ax_0 = f.add_subplot(411)
                ax_1 = f.add_subplot(412)
                ax_2 = f.add_subplot(413)
                ax_3 = f.add_subplot(414)
                Figur = tk.Frame(TPlot)
                Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
                canvas = FigureCanvasTkAgg(f, master=Figur)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

                if data[0] is not None:
                    ax_0.errorbar(data[0].x * 1000, data[0].y, yerr=[data[0].uy * data_to_plot.K, data[0].uy * data_to_plot.K], **data_to_plot.plot_kwargs)
                    
                    #design
                    ax_0.set_xlim(0, None)
                    if key == 'reference':
                        ax_0.set_ylabel(r'$\varepsilon$ / 1')
                        ax_0.set_ylim(0, None)
                    else:
                        ax_0.set_ylabel(r'$k\varepsilon\Delta d$ / 1')

                    ax_1.errorbar(data[0].x * 1000, data[0].relres*100, yerr=[data[0].uy / data[0].y * 100 * data_to_plot.K, data[0].uy / data[0].y * 100 * data_to_plot.K], **data_to_plot.plot_kwargs)
                    mx = np.max(np.abs(data[0].relres*100))
                    ax_1.set_ylim(-mx*2.5, mx*2.5)

                if data[1] is not None:
                    x_fit = np.linspace(np.min(data[0].x), np.max(data[0].x), data_to_plot.ndata)
                    ax_0.plot(x_fit * 1000, data[1].fit(x_fit), **data_to_plot.line_kwargs)

                if data[2] is not None:
                    ax_2.errorbar(data[2].x * 1000, data[2].y, yerr=[data[2].uy * data_to_plot.K, data[2].uy * data_to_plot.K], **data_to_plot.plot_kwargs)

                    ax_3.errorbar(data[2].x * 1000, data[2].relres*100, yerr=[data[2].uy / data[2].y * 100 * data_to_plot.K, data[2].uy / data[2].y * 100 * data_to_plot.K], **data_to_plot.plot_kwargs)
                    mx = np.max(np.abs(data[2].relres*100))
                    ax_3.set_ylim(-mx*2.5, mx*2.5)

                if data[3] is not None:
                    x_fit = np.linspace(np.min(data[2].x), np.max(data[2].x), data_to_plot.ndata)
                    ax_2.plot(x_fit * 1000, data[3].fit(x_fit, der=True), **data_to_plot.line_kwargs)

                ax_1.set_ylabel(r'residuals / $\%$')
                ax_2.set_ylabel(r"$d^{\:'}_0$ / mm")
                ax_3.set_ylabel(r'residuals / $\%$')
                ax_3.set_xlabel(r'$E$ / keV')

                ax_0.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_1.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_2.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_3.grid(which='both', linestyle='-.', linewidth=0.3)

                ax_0.set_xticklabels([])
                ax_2.set_xticklabels([])
                ax_1.set_xlim(ax_0.set_xlim())
                ax_2.set_xlim(ax_0.set_xlim())
                ax_3.set_xlim(ax_0.set_xlim())

                f.tight_layout()
                canvas.draw()
            if plotype == 'emissions':
                TPlot.title(ttest + f' keV (k='+f'{data_to_plot.K:.0f})')
                f = Figure(figsize=(6.5, 7))
                ax_0 = f.add_subplot(411)
                ax_1 = f.add_subplot(412)
                ax_2 = f.add_subplot(413)
                ax_3 = f.add_subplot(414)
                Figur = tk.Frame(TPlot)
                Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
                canvas = FigureCanvasTkAgg(f, master=Figur)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

                if data[0] is not None:
                    ax_0.errorbar(data[0].x, data[0].y, yerr=[data[0].uy * data_to_plot.K, data[0].uy * data_to_plot.K], **data_to_plot.plot_kwargs)
                    
                    #design
                    ax_0.set_ylim(0, 1.1)

                    ax_1.errorbar(data[0].x, data[0].relres*100, yerr=[data[0].uy / data[0].y * 100 * data_to_plot.K, data[0].uy / data[0].y * 100 * data_to_plot.K], **data_to_plot.plot_kwargs)
                    mx = np.max(np.abs(data[0].relres*100))
                    ax_1.set_ylim(-mx*2.5, mx*2.5)

                if data[1] is not None:
                    d0 = self._delta(data[1].params)
                    x_fit = np.linspace(d0, np.max(data[0].x), data_to_plot.ndata)
                    ax_0.plot(x_fit, data[1].fit_sqrt(x_fit), **data_to_plot.line_kwargs)

                if data[2] is not None:
                    ax_2.errorbar(data[2].x, data[2].y, yerr=[data[2].uy * data_to_plot.K, data[2].uy * data_to_plot.K], **data_to_plot.plot_kwargs)

                    ax_3.errorbar(data[2].x, data[2].relres*100, yerr=[data[2].uy / data[2].y * 100 * data_to_plot.K, data[2].uy / data[2].y * 100 * data_to_plot.K], **data_to_plot.plot_kwargs)
                    mx = np.max(np.abs(data[2].relres*100))
                    ax_3.set_ylim(-mx*2.5, mx*2.5)

                if data[3] is not None:
                    ax_2.plot(data[3].x, data[3].y, **data_to_plot.line_kwargs)

                ax_0.set_ylabel(r'$\sqrt{\frac{C_0}{C_\mathrm{d}}}$ / 1')
                ax_1.set_ylabel(r'residuals / $\%$')
                ax_2.set_ylabel(r'$C_\mathrm{d}$ / s$^{-1}$')
                ax_3.set_ylabel(r'residuals / $\%$')
                ax_3.set_xlabel(r'$d$ / mm')


                ax_0.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_1.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_2.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_3.grid(which='both', linestyle='-.', linewidth=0.3)

                ax_0.set_xticklabels([])
                ax_2.set_xticklabels([])
                ax_1.set_xlim(ax_0.set_xlim())
                ax_2.set_xlim(ax_0.set_xlim())
                ax_3.set_xlim(ax_0.set_xlim())

                f.tight_layout()
                canvas.draw()


class DetectorCharacterizationWindow:
    #window to process data for detector characterization
    def __init__(self, parent, NAA, M):
        parent.title('Detector characterization')
        parent.resizable(False,False)
        parent.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(parent))
        self.spectra_list = {} #spectra_list dict of lists, key is the name of counting position : value is a list of spectum objects
        self.source = None
        self.position_list = {}
        self.PT_list = {}
        self.characterization_result = None # shound become a DetectorCharacterization object when a successful elaboration is completed
        self.fitplot_windows = []
        self.data_to_plot = None#{}
        self.selectemission_toplevel = None
        self.PT_evaluation_toplevel = None
        self.detector_values, detlistvalues = self.initialize_detectors()

        self.information_box = tk.Label(parent, text='')

        things_to_do_frame = tk.Frame(parent)
        things_to_show = tk.Frame(parent)

        introduction_frame = tk.Frame(things_to_do_frame)
        tk.Label(introduction_frame, text='name', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        filename_entry = tk.Entry(introduction_frame, width=20)
        filename_entry.grid(row=0, column=1, sticky=tk.EW)
        tk.Label(introduction_frame, text='detector', width=12, anchor=tk.W).grid(row=1, column=0)
        CB_detector = ttk.Combobox(introduction_frame, width=10)
        CB_detector['values'] = detlistvalues
        CB_detector.grid(row=1, column=1, sticky=tk.W)
        ttk.Separator(introduction_frame, orient="vertical").grid(
            row=1, column=2, rowspan=2, sticky=tk.NS, padx=3)
        tk.Label(introduction_frame, text='μ / 1', anchor=tk.W).grid(row=1, column=3)
        mu_value = tk.Spinbox(introduction_frame, from_=-1.0, to=1.0, increment=0.0001, width=6)
        mu_value.grid(row=1, column=4)
        mu_value.delete(0, tk.END)
        mu_value.insert(0, '0.0000')
        tk.Label(introduction_frame, text='').grid(row=1, column=5, padx=3)
        tk.Label(introduction_frame, text='u(μ) / 1', anchor=tk.W).grid(row=1, column=6)
        u_mu_value = tk.Spinbox(introduction_frame, from_=0.0, to=1.0, increment=0.0001, width=6)
        u_mu_value.grid(row=1, column=7)
        tk.Label(introduction_frame, text='source', width=12, anchor=tk.W).grid(row=2, column=0)
        CB_source = ttk.Combobox(introduction_frame, width=10, state='readonly')
        CB_source['values'] = [sourcename[:-len('.sce')] for sourcename in os.listdir(os.path.join('data','sources')) if sourcename[-len('.sce'):] == '.sce']
        CB_source.grid(row=2, column=1, sticky=tk.EW)
        logo_select_emissions = tk.PhotoImage(data=gui_things.emission)
        B_select_emissions = gui_things.Button(introduction_frame, image=logo_select_emissions, hint='Select emissions!', hint_destination=self.information_box, command=lambda : self.select_emissions_from_source(parent))
        B_select_emissions.grid(row=2, column=3)
        B_select_emissions.image = logo_select_emissions
        introduction_frame.pack(anchor=tk.W, pady=5)

        ttk.Separator(things_to_do_frame, orient="horizontal").pack(anchor=tk.W, pady=3, fill=tk.X, expand=True)

        spectra_frame = tk.Frame(things_to_do_frame)

        tk.Label(spectra_frame, text='positions', anchor=tk.W, width=12).grid(row=0, column=0, sticky=tk.W)
        values_positions = ['reference']
        CB_positions = ttk.Combobox(spectra_frame, width=12, values=values_positions, state='readonly')
        CB_positions.grid(row=0, column=1, columnspan=2, padx=3, sticky=tk.EW)
        CB_positions.set(values_positions[0])

        self.spectra_list[CB_positions.get()] = []
        self.position_list[CB_positions.get()] = 0.0
        self.PT_list[CB_positions.get()] = (None, np.array([0.0, 0.0]), np.array([0.0, 0.0, 0.0]), '')

        ttk.Separator(spectra_frame, orient="vertical").grid(
            row=0, column=3, sticky=tk.NS, padx=3)

        tk.Label(spectra_frame, text='d / mm', anchor=tk.E).grid(row=1, column=0, padx=3)
        distance_indicator = tk.Label(spectra_frame, text=f'{self.position_list[CB_positions.get()]:.1f}', width=7)
        distance_indicator.grid(row=1, column=1)

        logo_change_distance = tk.PhotoImage(data=gui_things.ddistance)
        B_change_distance = gui_things.Button(spectra_frame, image=logo_change_distance, hint='Modify distance!', hint_destination=self.information_box, command=lambda : self.modify_counting_distance(CB_positions, distance_indicator, parent))
        B_change_distance.grid(row=1, column=2)
        B_change_distance.image = logo_change_distance
        ttk.Separator(spectra_frame, orient="vertical").grid(
            row=1, column=3, sticky=tk.NS, padx=3)

        logo_add_positon = tk.PhotoImage(data=gui_things.newpos)
        B_add_positon = gui_things.Button(spectra_frame, image=logo_add_positon, hint='Add a counting position!', hint_destination=self.information_box)
        B_add_positon.grid(row=1, column=4)
        B_add_positon.image = logo_add_positon

        logo_rename_positon = tk.PhotoImage(data=gui_things.renewpos)
        B_rename_positon = gui_things.Button(spectra_frame, image=logo_rename_positon, hint='Rename a counting position!', hint_destination=self.information_box, command=lambda : self.rename_counting_position(CB_positions, parent))
        B_rename_positon.grid(row=1, column=5)
        B_rename_positon.image = logo_rename_positon

        logo_delete_positon = tk.PhotoImage(data=gui_things.delpos)
        B_delete_positon = gui_things.Button(spectra_frame, image=logo_delete_positon, hint='Delete a counting position!', hint_destination=self.information_box)
        B_delete_positon.grid(row=1, column=6)
        B_delete_positon.image = logo_delete_positon

        ListFrame = tk.Frame(spectra_frame)
        scrollbar = tk.Scrollbar(ListFrame, orient="vertical")
        listbox = tk.Listbox(ListFrame, heigh=7, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ListFrame.grid(row=4, column=0, rowspan=4, columnspan=7, sticky=tk.NSEW)

        tk.Label(spectra_frame, text='spectra', anchor=tk.W).grid(row=3, column=0, columnspan=4, sticky=tk.W)
        logo_add_spectra = tk.PhotoImage(data=gui_things.plus_spectrum)
        B_add_spectra = gui_things.Button(spectra_frame, image=logo_add_spectra, hint='Add spectra to the current counting position!', hint_destination=self.information_box, command=lambda : self.add_spectra_for_calibration(parent, NAA, CB_positions, listbox))
        B_add_spectra.grid(row=4, column=7)
        B_add_spectra.image = logo_add_spectra
        logo_peaklist_spectra = tk.PhotoImage(data=gui_things.plist)
        B_peaklist_spectra = gui_things.Button(spectra_frame, image=logo_peaklist_spectra, hint='Show the peaklist of selected spectrum!', hint_destination=self.information_box, command=lambda : self.see_calibration_peak_list(CB_positions, listbox, parent, NAA))
        B_peaklist_spectra.grid(row=5, column=7)
        B_peaklist_spectra.image = logo_peaklist_spectra
        logo_delete_spectra = tk.PhotoImage(data=gui_things.none)
        B_delete_spectra = gui_things.Button(spectra_frame, image=logo_delete_spectra, hint='Delete the selected spectra!', hint_destination=self.information_box, command=lambda : self.delete_selected_spectrum(CB_positions, listbox, parent))
        B_delete_spectra.grid(row=6, column=7)
        B_delete_spectra.image = logo_delete_spectra

        F_delete_selector_sample = tk.Frame(spectra_frame)
        self.delete_selector_sample = tk.IntVar(parent)
        R1 = tk.Radiobutton(F_delete_selector_sample, text='selected', anchor=tk.W, value=0, variable=self.delete_selector_sample)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_delete_selector_sample, text='all', anchor=tk.W, value=1, variable=self.delete_selector_sample)
        R2.pack(anchor=tk.W)
        self.delete_selector_sample.set(0)
        F_delete_selector_sample.grid(row=6, column=8, columnspan=3)
        spectra_frame.pack(anchor=tk.W, pady=5)

        PT_frame = tk.Frame(things_to_do_frame)

        tk.Label(PT_frame, text='P/T', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        logo_PT_eval = tk.PhotoImage(data=gui_things.ptauto)
        B_PT_eval = gui_things.Button(PT_frame, image=logo_PT_eval, hint='Evaluate PT for the current position!', hint_destination=self.information_box, command=lambda : None)
        B_PT_eval.grid(row=1, column=0)
        B_PT_eval.image = logo_PT_eval
        logo_PT_eval_manual = tk.PhotoImage(data=gui_things.ptman)
        B_PT_eval_manual = gui_things.Button(PT_frame, image=logo_PT_eval_manual, hint='Insert PT values for the current position!', hint_destination=self.information_box)
        B_PT_eval_manual.grid(row=1, column=1)
        B_PT_eval_manual.image = logo_PT_eval_manual
        logo_PT_indicator_red = tk.PhotoImage(data=gui_things.redsign)
        logo_PT_indicator_green = tk.PhotoImage(data=gui_things.greensign)
        B_PT_indicator = gui_things.Button(PT_frame, image=logo_PT_indicator_red, hint='Display PT values for the current position!', hint_destination=self.information_box)
        B_PT_indicator.grid(row=1, column=2)
        B_PT_indicator.image = logo_PT_indicator_red
        B_PT_eval_manual.configure(command=lambda : self.go_to_PT_visualization(parent, CB_positions, B_PT_indicator, logo_PT_indicator_red, logo_PT_indicator_green, vtype='insert'))
        B_PT_indicator.configure(command=lambda : self.go_to_PT_visualization(parent, CB_positions, B_PT_indicator, logo_PT_indicator_red, logo_PT_indicator_green, vtype='view'))

        PT_frame.pack(anchor=tk.W, pady=5)
        ttk.Separator(things_to_do_frame, orient="horizontal").pack(anchor=tk.W, pady=3, fill=tk.X, expand=True)

        Plot_frame = tk.Frame(things_to_do_frame)
        plot_header = tk.Frame(Plot_frame)
        tk.Label(plot_header, text='plot results').pack(anchor=tk.W)
        plot_header.pack(anchor=tk.W)
        actions_frame = tk.Frame(Plot_frame)
        fit_box = ttk.Combobox(actions_frame, width=25, state='readonly')
        fit_box.pack(side=tk.LEFT)
        logo_open_plots = tk.PhotoImage(data=gui_things.see_fit)
        B_open_plots = gui_things.Button(actions_frame, image=logo_open_plots, hint='See detail of fits!', hint_destination=self.information_box)
        B_open_plots.pack(side=tk.LEFT, padx=5)
        B_open_plots.image = logo_open_plots
        actions_frame.pack(anchor=tk.W)
        Plot_frame.pack(anchor=tk.W, pady=5)

        log_frame = tk.Frame(things_to_show)
        tk.Label(log_frame, text='log', anchor=tk.W).pack(anchor=tk.NW)
        logtext = gui_things.ScrollableText(log_frame, width=65, height=25)
        logtext.pack(anchor=tk.NW, fill=tk.Y, expand=True)
        log_frame.pack(anchor=tk.NW, pady=2, fill=tk.Y, expand=True)
        #last_button

        things_to_do_frame.grid(row=0, column=0, padx=5)
        things_to_show.grid(row=0, column=1, padx=5, sticky=tk.NS)

        ttk.Separator(parent, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky=tk.EW, pady=3)

        lowerbar_frame = tk.Frame(parent)

        logo_elaboration = tk.PhotoImage(data=gui_things.manygears)
        B_elaboration = gui_things.Button(lowerbar_frame, image=logo_elaboration, hint='Elaborate detector characterization!', hint_destination=self.information_box)
        B_elaboration.pack(side=tk.LEFT)
        B_elaboration.image = logo_elaboration

        ttk.Separator(lowerbar_frame, orient="vertical").pack(side=tk.LEFT, padx=3, fill=tk.Y)
        logo_save_calibration = tk.PhotoImage(data=gui_things.beye)
        B_save_calibration = gui_things.Button(lowerbar_frame, image=logo_save_calibration, hint='Save the current detector characterization!', hint_destination=self.information_box)
        B_save_calibration.pack(side=tk.LEFT)
        B_save_calibration.image = logo_save_calibration
        lowerbar_frame.grid(row=2, column=0, sticky=tk.W, padx=5)

        self.information_box.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        B_open_plots.configure(command=lambda : self.display_fit(fit_box, parent))

        B_add_positon.configure(command=lambda : self.add_counting_position(CB_positions, distance_indicator, listbox, B_PT_indicator,logo_PT_indicator_red,logo_PT_indicator_green))
        B_delete_positon.configure(command=lambda : self.delete_counting_position(CB_positions, distance_indicator, listbox, B_PT_indicator,logo_PT_indicator_red,logo_PT_indicator_green))
        B_elaboration.configure(command=lambda : self.elaborate_detector_characterization(NAA, logtext, CB_detector, mu_value, u_mu_value, parent, fit_box))
        B_PT_eval.configure(command=lambda : self.go_to_PT_elaboration(parent, CB_positions, NAA, B_PT_indicator, logo_PT_indicator_red, logo_PT_indicator_green))
        B_save_calibration.configure(command=lambda : self.save_calibration_data(filename_entry, logtext, M.calibration_combobox))

        CB_detector.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': self.select_detector(CB_detector,mu_value,u_mu_value))
        CB_source.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': self.select_source(CB_source,NAA.settings_dict['energy tolerance']))
        CB_positions.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': self.select_position(CB_positions,distance_indicator,listbox,B_PT_indicator,logo_PT_indicator_red,logo_PT_indicator_green))

    def on_closing(self, parent, title='Quit Detector characterization window', message='Save your elaboration before quitting.\n\nDo you want to quit the window?'):
        if messagebox.askokcancel(title, message, parent=parent):
            parent.destroy()

    def display_fit(self, CB, parent):
        ttest = CB.get()
        if ttest != '':
            which, key = ttest.split()
            try:
                key = float(key)
            except ValueError:
                pass
            data = [None, None, None, None]
            if which == 'position':# in self.data_to_plot.positions:
                data = self.data_to_plot.positions.get(key, data)
                plotype = 'positions'
            if which == 'emission':# in self.data_to_plot.emissions:
                data = self.data_to_plot.emissions.get(key, data)
                plotype = 'emissions'
            TPlot = tk.Toplevel(parent)
            self.fitplot_windows.append(TPlot)
            if plotype == 'positions':
                TPlot.title(ttest + f' mm (k='+f'{self.data_to_plot.K:.0f})')
                f = Figure(figsize=(6.5, 7))
                ax_0 = f.add_subplot(411)
                ax_1 = f.add_subplot(412)
                ax_2 = f.add_subplot(413)
                ax_3 = f.add_subplot(414)
                Figur = tk.Frame(TPlot)
                Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
                canvas = FigureCanvasTkAgg(f, master=Figur)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

                if data[0] is not None:
                    ax_0.errorbar(data[0].x * 1000, data[0].y, yerr=[data[0].uy * self.data_to_plot.K, data[0].uy * self.data_to_plot.K], **self.data_to_plot.plot_kwargs)
                    
                    #design
                    ax_0.set_xlim(0, None)
                    if key == 'reference':
                        ax_0.set_ylabel(r'$\varepsilon$ / 1')
                        ax_0.set_ylim(0, None)
                    else:
                        ax_0.set_ylabel(r'$k\varepsilon\Delta d$ / 1')

                    ax_1.errorbar(data[0].x * 1000, data[0].relres*100, yerr=[data[0].uy / data[0].y * 100 * self.data_to_plot.K, data[0].uy / data[0].y * 100 * self.data_to_plot.K], **self.data_to_plot.plot_kwargs)
                    mx = np.max(np.abs(data[0].relres*100))
                    ax_1.set_ylim(-mx*2.5, mx*2.5)

                if data[1] is not None:
                    x_fit = np.linspace(np.min(data[0].x), np.max(data[0].x), self.data_to_plot.ndata)
                    ax_0.plot(x_fit * 1000, data[1].fit(x_fit), **self.data_to_plot.line_kwargs)

                if data[2] is not None:
                    ax_2.errorbar(data[2].x * 1000, data[2].y, yerr=[data[2].uy * self.data_to_plot.K, data[2].uy * self.data_to_plot.K], **self.data_to_plot.plot_kwargs)

                    ax_3.errorbar(data[2].x * 1000, data[2].relres*100, yerr=[data[2].uy / data[2].y * 100 * self.data_to_plot.K, data[2].uy / data[2].y * 100 * self.data_to_plot.K], **self.data_to_plot.plot_kwargs)
                    mx = np.max(np.abs(data[2].relres*100))
                    ax_3.set_ylim(-mx*2.5, mx*2.5)

                if data[3] is not None:
                    x_fit = np.linspace(np.min(data[2].x), np.max(data[2].x), self.data_to_plot.ndata)
                    ax_2.plot(x_fit * 1000, data[3].fit(x_fit, der=True), **self.data_to_plot.line_kwargs)

                ax_1.set_ylabel(r'residuals / $\%$')
                ax_2.set_ylabel(r"$d^{\:'}_0$ / mm")
                ax_3.set_ylabel(r'residuals / $\%$')
                ax_3.set_xlabel(r'$E$ / keV')

                ax_0.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_1.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_2.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_3.grid(which='both', linestyle='-.', linewidth=0.3)

                ax_0.set_xticklabels([])
                ax_2.set_xticklabels([])
                ax_1.set_xlim(ax_0.set_xlim())
                ax_2.set_xlim(ax_0.set_xlim())
                ax_3.set_xlim(ax_0.set_xlim())

                f.tight_layout()
                canvas.draw()
            if plotype == 'emissions':
                TPlot.title(ttest + f' keV (k='+f'{self.data_to_plot.K:.0f})')
                f = Figure(figsize=(6.5, 7))
                ax_0 = f.add_subplot(411)
                ax_1 = f.add_subplot(412)
                ax_2 = f.add_subplot(413)
                ax_3 = f.add_subplot(414)
                Figur = tk.Frame(TPlot)
                Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
                canvas = FigureCanvasTkAgg(f, master=Figur)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

                if data[0] is not None:
                    ax_0.errorbar(data[0].x, data[0].y, yerr=[data[0].uy * self.data_to_plot.K, data[0].uy * self.data_to_plot.K], **self.data_to_plot.plot_kwargs)
                    
                    #design
                    ax_0.set_ylim(0, 1.1)

                    ax_1.errorbar(data[0].x, data[0].relres*100, yerr=[data[0].uy / data[0].y * 100 * self.data_to_plot.K, data[0].uy / data[0].y * 100 * self.data_to_plot.K], **self.data_to_plot.plot_kwargs)
                    mx = np.max(np.abs(data[0].relres*100))
                    ax_1.set_ylim(-mx*2.5, mx*2.5)

                if data[1] is not None:
                    d0 = self._delta(data[1].params)
                    x_fit = np.linspace(d0, np.max(data[0].x), self.data_to_plot.ndata)
                    ax_0.plot(x_fit, data[1].fit_sqrt(x_fit), **self.data_to_plot.line_kwargs)

                if data[2] is not None:
                    ax_2.errorbar(data[2].x, data[2].y, yerr=[data[2].uy * self.data_to_plot.K, data[2].uy * self.data_to_plot.K], **self.data_to_plot.plot_kwargs)

                    ax_3.errorbar(data[2].x, data[2].relres*100, yerr=[data[2].uy / data[2].y * 100 * self.data_to_plot.K, data[2].uy / data[2].y * 100 * self.data_to_plot.K], **self.data_to_plot.plot_kwargs)
                    mx = np.max(np.abs(data[2].relres*100))
                    ax_3.set_ylim(-mx*2.5, mx*2.5)

                if data[3] is not None:
                    ax_2.plot(data[3].x, data[3].y, **self.data_to_plot.line_kwargs)

                ax_0.set_ylabel(r'$\sqrt{\frac{C_0}{C_\mathrm{d}}}$ / 1')
                ax_1.set_ylabel(r'residuals / $\%$')
                ax_2.set_ylabel(r'$C_\mathrm{d}$ / s$^{-1}$')
                ax_3.set_ylabel(r'residuals / $\%$')
                ax_3.set_xlabel(r'$d$ / mm')


                ax_0.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_1.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_2.grid(which='both', linestyle='-.', linewidth=0.3)
                ax_3.grid(which='both', linestyle='-.', linewidth=0.3)

                ax_0.set_xticklabels([])
                ax_2.set_xticklabels([])
                ax_1.set_xlim(ax_0.set_xlim())
                ax_2.set_xlim(ax_0.set_xlim())
                ax_3.set_xlim(ax_0.set_xlim())

                f.tight_layout()
                canvas.draw()

    def save_calibration_data(self, name, stext, Cbox, folder=os.path.join('data', 'characterization')):
        if self.characterization_result is None:
            self.information_box.configure(text='Characterization is not performed yet!')
        elif name.get() == '':
            self.information_box.configure(text='A valid filename is required!')
        else:
            #save files
            # calibration
            with open(os.path.join(folder,f'{name.get()}.pos'), 'w') as savef:
                savef.write(f'detector: {self.characterization_result.detector}\n')
                savef.write(f'reference: {self.characterization_result.distance:.1f}\n')
                savef.write(f'detector_mu:\n{self.characterization_result.mu} {self.characterization_result.u_mu}\n')
                #energy
                savef.write(f'energy: {self.characterization_result.energy_model}\n{" ".join([f"{energy_n}" for energy_n in self.characterization_result.energy_parameters])}\n')
                #FWHM
                savef.write(f'fwhm: {self.characterization_result.fwhm_model}\n{" ".join([f"{fwhm_n}" for fwhm_n in self.characterization_result.fwhm_parameters])}\n')
                #efficiency
                savef.write(f'efficiency: {self.characterization_result.efficiency_model}\n{" ".join([f"{efficiency_n}" for efficiency_n in self.characterization_result.efficiency_parameters])}\n')
                #efficiency cov matrix
                cov = ''.join([f' '.join([f'{col}' for col in row])+'\n' for row in self.characterization_result.efficiency_cov])
                savef.write('cov matrix:\n'+cov)
                #reference position der
                if self.characterization_result.der_exponent is not None:
                    der = f'reference position der: {" ".join([f"{int(num)}" for num in self.characterization_result.der_exponent])}\n{" ".join([f"{num}" for num in self.characterization_result.der_parameters])}\n' + ''.join([f' '.join([f'{col}' for col in row])+'\n' for row in self.characterization_result.der_pcov])
                    savef.write(der)
                #print(self.characterization_result.PT_energy)
                if self.characterization_result.PT_energy is not None:
                    PTe = f'reference_PT: {self.characterization_result.PT_energy:.1f}\n{" ".join([f"{num}" for num in self.characterization_result.PT_linear])}\n{" ".join([f"{num}" for num in self.characterization_result.PT_polynomial])}\n'
                else:
                    PTe = 'reference_PT: None\n1 0\n1 0 0\n'
                savef.write(PTe)
                #positions
                for key, value in self.characterization_result.kedd_dict.items():
                    pos = f'position: {key:.1f} | {" ".join([f"{int(num)}" for num in value[0]])}\n{" ".join([f"{num}" for num in value[1]])}\n' + ''.join([f' '.join([f'{col}' for col in row])+'\n' for row in value[2]])
                    savef.write(pos)
                #der at positions 
                for key, value in self.characterization_result.der_dict.items():
                    pos = f'p_der: {key:.1f} | {" ".join([f"{int(num)}" for num in value[0]])}\n{" ".join([f"{num}" for num in value[1]])}\n' + ''.join([f' '.join([f'{col}' for col in row])+'\n' for row in value[2]])
                    savef.write(pos)
                #PT
                for key, value in self.characterization_result.PT_dict.items():
                    if value[0] is not None:
                        pos = f'p_PT: {key:.1f} | {value[0]:.1f}\n{" ".join([f"{num}" for num in value[1]])}\n{" ".join([f"{num}" for num in value[2]])}\n'
                        savef.write(pos)
                #d0 evaluation
                # if self.characterization_result.d0_evaluation is not None:
                #     d0_eval = f'd0: {" ".join([f"{int(num)}" for num in self.characterization_result.d0_evaluation[0]])}\n{" ".join([f"{num}" for num in self.characterization_result.d0_evaluation[1]])}\n' + ''.join([f' '.join([f'{col}' for col in row])+'\n' for row in self.characterization_result.d0_evaluation[2]])
                #     savef.write(d0_eval)
                #data points
                if self.characterization_result.x_data is not None and self.characterization_result.y_data is not None:
                    savef.write(f'x_points:\n{" ".join([f"{xp}" for xp in self.characterization_result.x_data])}\ny_points:\n{" ".join([f"{yp}" for yp in self.characterization_result.y_data])}\n')
            # log
            with open(os.path.join(folder,f'{name.get()}_log.txt'), 'w') as savef:
                savef.write(stext.get())
            #plots
            with open(os.path.join(folder,f'{name.get()}.pkl'), 'wb') as plot_file:
                # source, destination
                pickle.dump(self.data_to_plot, plot_file)
            ext = '.pos'
            Cbox['values'] = [filename[:-len(ext)] for filename in os.listdir(folder) if filename[-len(ext):] == ext]
            self.information_box.configure(text='Saved!')

    def add_spectra_for_calibration(self, parent, NAA, box, listbox):
        #add spectra for calibration calculations
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))#,('HyperLab ASC file','*.asc'),('CHN spectrum file','*.chn'))
        limit_s = NAA.settings_dict['calibs statistical uncertainty limit']
        try:
            output = tuple(askopenfilenames(parent=parent, title='Open calibration',filetypes=filetypes))
        except TypeError:
            output = ()
        for filename in output:
            if filename != '' and filename != ():
                peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=True)
                efficiency = NAA.calibration
                if result == True:
                    Spectrum = naaobject.SpectrumAnalysis(identity=f'calibration', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=filename, source=source, efficiency=efficiency, energy_tolerance=NAA.settings_dict['energy tolerance'], database_k0=NAA.database, database_source=self.source)
                    actual_spectra_list = self.spectra_list[box.get()]
                    actual_spectra_list.append(Spectrum)
                    self.spectra_list[box.get()] = actual_spectra_list
                else:
                    pass#notes.append(note)
        listbox.delete(0, tk.END)
        for spect in self.spectra_list[box.get()]:
            listbox.insert(tk.END, spect.filename())

    def delete_selected_spectrum(self, box, listbox, parent):
        #delete one or more spectra for detector calibration
        if self.PT_evaluation_toplevel is not None:
            self.PT_evaluation_toplevel.destroy()
        if self.delete_selector_sample.get() == 1:
            #all
            nlen = len(self.spectra_list[box.get()])
            if nlen > 0:
                if messagebox.askyesno(title='Remove spectrum', message='\nAre you sure to remove all spectra from selection?\n', parent=parent):
                    for _ in range(nlen):
                        self.spectra_list[box.get()].pop()
                    listbox.delete(0, tk.END)
                    for spect in self.spectra_list[box.get()]:
                        listbox.insert(tk.END, spect.filename())
        else:
            idx = listbox.curselection()
            try:
                idx = idx[0]
            except:
                idx = -1
            if idx >= 0:
                if messagebox.askyesno(title='Remove spectrum', message=f'\nAre you sure to remove spectrum: {self.spectra_list[box.get()][idx].filename()} from selection?\n', parent=parent):
                    self.spectra_list[box.get()].pop(idx)
                    listbox.delete(0, tk.END)
                    for spect in self.spectra_list[box.get()]:
                        listbox.insert(tk.END, spect.filename())

    def see_calibration_peak_list(self, box, listbox, parent, NAA):
        #display the peaklist for the selected spectrum
        if len(self.spectra_list[box.get()]) > 0:
            idx = listbox.curselection()
            try:
                if idx[0] < 0:
                    idx = 0
                else:
                    idx = idx[0]
            except:
                idx = 0
            if self.PT_evaluation_toplevel is not None:
                self.PT_evaluation_toplevel.destroy()
            self.PT_evaluation_toplevel = tk.Toplevel(parent)
            nline = NAA.settings_dict['page height']
            local_peak_list = nest_list(self.spectra_list[box.get()][idx].peak_list, nline)
            local_suspected = nest_list(self.spectra_list[box.get()][idx].suspected, nline)
            PeaklistWindow(self.PT_evaluation_toplevel, self.spectra_list[box.get()][idx], local_peak_list, local_suspected, nline)

    def select_source(self, box, energy_tolerance=0.3):
        self.source = naaobject.GSource(box.get())
        if self.selectemission_toplevel is not None:
            self.selectemission_toplevel.destroy()
        if self.PT_evaluation_toplevel is not None:
            self.PT_evaluation_toplevel.destroy()
        for key in self.spectra_list.keys():
            for item in self.spectra_list[key]:
                item.suspected = item._discriminate_source_peaks(energy_tolerance,self.source)
                item.assign_nuclide = [-1]*len(item.peak_list)

    def select_emissions_from_source(self, parent):
        def check_true_or_false(x):
            if x == True:
                return 'True'
            else:
                return ''

        if self.source is not None:
            if self.selectemission_toplevel is not None:
                self.selectemission_toplevel.destroy()

            self.selectemission_toplevel = tk.Toplevel(parent)
            self.selectemission_toplevel.resizable(False,False)
            self.selectemission_toplevel.title(f'Source ({self.source.name})')
            self.selectemission_toplevel.focus()
            F = tk.Frame(self.selectemission_toplevel)
            tk.Label(F, text=f'certificate date: {self.source.readable_datetime()}', anchor=tk.W).pack()
            F.pack(anchor=tk.W, padx=5, pady=5)
            F=tk.Frame(self.selectemission_toplevel)
            tk.Label(F, text='', width=6).pack(side=tk.LEFT)
            tk.Label(F, text='energy / keV', width=12).pack(side=tk.LEFT)
            tk.Label(F, text='nuclide', width=12).pack(side=tk.LEFT)
            tk.Label(F, text='activity / Bq', width=12).pack(side=tk.LEFT)
            tk.Label(F, text='γ yield / 1', width=12).pack(side=tk.LEFT)
            tk.Label(F, text='half-life / s', width=12).pack(side=tk.LEFT)
            tk.Label(F, text='COIfree', width=12).pack(side=tk.LEFT)
            F.pack(anchor=tk.W)
            
            container = tk.Frame(self.selectemission_toplevel)
            canvas = tk.Canvas(container, height=550)
            scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            for idx, item in enumerate(self.source.selection):
                F = tk.Frame(scrollable_frame)
                var = tk.StringVar(parent)
                var.set('')
                CB = tk.Checkbutton(F, width=3, variable=var, onvalue=f'{idx}', offvalue='')
                CB.configure(command=lambda CB=CB, var=var, idx=idx: self.check_pressed(CB, var, idx))
                CB.pack(side=tk.LEFT)
                if item == True:
                    CB.select()
                else:
                    CB.deselect()
                tk.Label(F, text=f'{self.source.data.iloc[idx]["energy"]}', width=12, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(F, text=f'{self.source.data.iloc[idx]["emitter"]}', width=12, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(F, text=f'{self.source.data.iloc[idx]["activity"]:.0f}', width=12, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(F, text=f'{self.source.data.iloc[idx]["yield"]:.4f}', width=12, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(F, text=f'{self.source.data.iloc[idx]["t_half"]:.3e}', width=12, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(F, text=f'{check_true_or_false(self.source.data.iloc[idx]["COIfree"])}', width=12, anchor=tk.W).pack(side=tk.LEFT)
                F.pack(anchor=tk.W, padx=5)

            container.pack(fill="both", expand=True)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

    def check_pressed(self, CB, var, idx):
        #select or deselect emission
        if self.source.selection[idx] == True:
            self.source.selection[idx] = False
            CB.deselect()
        else:
            self.source.selection[idx] = True
            CB.select()

    def select_position(self, box, distance_indicator, listbox, PT, red, green):
        #select counting position among available from the combobox
        listbox.delete(0, tk.END)
        for item in self.spectra_list[box.get()]:
            listbox.insert(tk.END,item.filename())
        distance_indicator.configure(text=f'{self.position_list[box.get()]:.1f}')
        if self.PT_list[box.get()][0] is None:
            PT.configure(image=red)
            PT.image = red
        else:
            PT.configure(image=green)
            PT.image = green

    def modify_counting_distance(self, box, distance_indicator, parent):
        #change the distance parameter for a position
        try:
            d_old = float(distance_indicator.cget('text'))
        except:
            d_old = 0.0
        width, height, xpos, ypos = distance_indicator.winfo_width(), distance_indicator.winfo_height(), distance_indicator.winfo_rootx(), distance_indicator.winfo_rooty()
        Ins = tk.Toplevel(parent)
        Ins.resizable(False, False)
        Ins.geometry(f'{width}x{height}+{xpos}+{ypos+height}')
        if sys.platform != 'darwin':
            Ins.overrideredirect(True)
        distance = tk.Spinbox(Ins, from_=0.0, to=300.0, increment=0.1)
        distance.pack(fill=tk.X)
        distance.delete(0, tk.END)
        distance.insert(0, d_old)
        distance.focus_force()

        if sys.platform != 'darwin':
            Ins.bind('<FocusOut>', lambda e='<FocusOut>': Ins.destroy())
        distance.bind('<Return>', lambda e='<Return>': self.check_confirm_distance(box, distance, distance_indicator, Ins))

    def check_confirm_distance(self, box, distance, distance_indicator, Ins):
        try:
            user_input = float(distance.get())
        except:
            user_input = -1
        if user_input >= 0:
            user_input = float(format(user_input,'.1f'))
            self.position_list[box.get()] = user_input
            distance_indicator.configure(text=f'{self.position_list[box.get()]:.1f}')
            Ins.destroy()

    def add_counting_position(self, box, distance_indicator, listbox, PT, red, green):
        #add a counting position
        n = 1
        position_name = f'position {n}'
        while position_name in self.spectra_list.keys():
            n += 1
            position_name = f'position {n}'
        self.spectra_list[position_name] = []
        self.position_list[position_name] = 0.0
        self.PT_list[position_name] = (None, np.array([0.0, 0.0]), np.array([0.0, 0.0, 0.0]), '')
        box['values'] = list(self.spectra_list.keys())
        box.set(position_name)
        self.select_position(box, distance_indicator, listbox, PT, red, green)

    def rename_counting_position(self, box, parent):
        #rename the currently selected counting position
        old_name = box.get()
        if old_name != 'reference':
            width, height, xpos, ypos = box.winfo_width(), box.winfo_height(), box.winfo_rootx(), box.winfo_rooty()
            Ins = tk.Toplevel(parent)
            Ins.resizable(False, False)
            Ins.geometry(f'{width}x{height}+{xpos}+{ypos+height}')
            Ins.overrideredirect(True)
            E_name = tk.Entry(Ins)
            E_name.pack(fill=tk.X)
            E_name.delete(0, tk.END)
            E_name.insert(0, old_name)
            E_name.focus_force()

            Ins.bind('<FocusOut>', lambda e='<FocusOut>': Ins.destroy())
            E_name.bind('<Return>', lambda e='<Return>': self.check_accept_rename(E_name, box, Ins))

    def check_accept_rename(self, E_name, box, Ins):
        #make effective the name change of a position
        if E_name.get() not in self.position_list.keys():
            self.spectra_list[E_name.get()] = self.spectra_list.pop(box.get())
            self.position_list[E_name.get()] = self.position_list.pop(box.get())
            self.PT_list[E_name.get()] = self.PT_list.pop(box.get())
            box['values'] = list(self.spectra_list.keys())
            box.set(E_name.get())
            Ins.destroy()
        else:
            self.information_box.configure(text='invalid name, try another one')

    def delete_counting_position(self, box, distance_indicator, listbox, PT, red, green):
        if box.get() != 'reference':
            self.spectra_list.pop(box.get())
            self.position_list.pop(box.get())
            self.PT_list.pop(box.get())
            box['values'] = list(self.spectra_list.keys())
            box.set('reference')
            self.select_position(box, distance_indicator, listbox, PT, red, green)

    def get_position(self, distance_spinbox):
        try:
            value = float(distance_spinbox.get())
        except:
            value = 0.0
        else:
            value = float(format(value, '.1f'))
        return value

    def initialize_detectors(self, file=os.path.join(os.path.join('data', 'facility'),'detlist.csv')):
        with open(file, 'r') as f:
            detector_info = [line.replace('\n', '').split(',') for line in f.readlines()]
        detector_list = [line[0] for line in detector_info]
        return detector_info, detector_list

    def select_detector(self, box, mu, umu):
        #retrieve information about the selected detector
        for line in self.detector_values:
            if box.get() == line[0]:
                try:
                    mu_value = float(line[1])
                except:
                    mu_value = 0.0
                try:
                    umu_value = float(line[2])
                except:
                    umu_value = 0.0
                mu.delete(0,tk.END)
                mu.insert(0,mu_value)
                umu.delete(0,tk.END)
                umu.insert(0,umu_value)
                break

    def go_to_PT_elaboration(self, parent, box, NAA, PT_button, red, green):
        #automatically evaluate PT fitting parameters
        if self.PT_evaluation_toplevel is not None:
            self.PT_evaluation_toplevel.destroy()
        if self.source is not None:
            self.PT_evaluation_toplevel = tk.Toplevel(parent)
            PTEvaluateWindow(self.PT_evaluation_toplevel, box.get(), self.PT_list, self.spectra_list[box.get()], NAA.background, self.source, NAA.settings_dict['energy tolerance'], PT_button, red, green, NAA.settings_dict['calibs statistical uncertainty limit'])
        else:
            self.information_box.configure(text='select a gamma source')

    def go_to_PT_visualization(self, parent, box, PT_button, red, green, vtype='view'):
        #display or manually modify PT fitting parameters
        if self.PT_evaluation_toplevel is not None:
            self.PT_evaluation_toplevel.destroy()
        self.PT_evaluation_toplevel = tk.Toplevel(parent)
        PTViewWindow(self.PT_evaluation_toplevel, box.get(), self.PT_list, PT_button, red, green, vtype=vtype)

    def elaborate_detector_characterization(self, NAA, logtext, CB_detector, mu, umu, parent, CB_graphs):
        self.characterization_result = None
        CB_graphs['values'] = []
        #get results for:
        # - calibration parameters at reference position
        # - d0 in every position
        # - keDd in every position other than reference
        # - PT should be already performed
        text = ['Warning: Incomplete input was provided\n']
        #clear graphics
        self.data_to_plot = naaobject.FitData_Base()
        hlen = len(self.fitplot_windows)
        for i in range(hlen):
            child_window = self.fitplot_windows.pop(0)
            try:
                child_window.destroy()
            except:
                pass
        try:
            mu = float(mu.get())
        except:
            mu = 0.0
        try:
            umu = float(umu.get())
        except:
            umu = 0.0
        #check detector
        if CB_detector.get() == '':
            text.append('- detector is not selected')
        #check source
        elif self.source is None:
            text.append('- emission source is not selected')
        elif self.source is not None and len(self.source.selection) < 7:
            text.append(f'- less than 7 emission are selected from emission source {len(self.source.selection)}')
        #check positions' distances
        elif len(self.position_list.keys()) != len(set(self.position_list.values())):
            text.append('- some positions share the same distance, positions must be unambiguous')
        elif self.position_list['reference'] != np.max(list(self.position_list.values())):
            text.append('- reference position should be the farthest distance from detector endcap')
        else:
            #update detlist
            head = [line[0] for line in self.detector_values]
            if CB_detector.get() in head:
                self.detector_values[head.index(CB_detector.get())][1] = f'{mu}'
                self.detector_values[head.index(CB_detector.get())][2] = f'{umu}'
            else:
                self.detector_values.append([f'{CB_detector.get()}', f'{mu}', f'{umu}'])
            #save file detectors
            dmanuscript = '\n'.join([','.join(ddline) for ddline in self.detector_values])
            with open(os.path.join(os.path.join('data','facility'),'detlist.csv'),'w') as detlist_file:
                detlist_file.write(dmanuscript)
            CB_detector['values'] = [line[0] for line in self.detector_values]
            #results initialization
            #preamble
            elaboration_day = datetime.date.today()
            text = [f'Characterization of detector {CB_detector.get()} performed on date {elaboration_day.strftime("%d/%m/%Y")}.\nThe used emission source is {self.source.name} ({len(self.source.data)} emissions reported at calibration date {self.source.readable_datetime()}).\nReference position is selected at {self.position_list["reference"]} mm distance from detector end-cap.\n']
            positional = [infospectrum.filename() for infospectrum in self.spectra_list['reference']]
            text.append(f'{len(positional)} spectra evaluated at reference position: ({", ".join(positional)}).\n')
            #spectra
            fit_ch, fit_en, fit_fw, fit_efy, nn, ur_efy, warnings_note = self.get_data_to_fit(NAA.settings_dict['energy tolerance'], mu)
            ref_emissions = self.source.data[self.source.selection].loc[nn,'reference']
            ref_emissions_warnings = [f'{line1} {line2}' for line1, line2 in zip(list(ref_emissions), warnings_note)]
            text.append(f'{len(fit_en)} emissions from the source are identified in the spectra of reference position:\n'+"\n".join(ref_emissions_warnings)+'\n')
            if len(fit_efy) < 7:
                text.append(f'Elaboration interrupted\n- not enough data points found in spectra to perform a fit! ({len(fit_efy)})')
            else:
                dummy_calibration = None
                #energy fit
                esp = [1, 0]
                energy_fit_parameters, energy_fit_covariance, energy_fit_resisuals, _ = self._fit_linear(fit_ch, fit_en, esp)
                energy_fit_uncertainties = np.sqrt(np.diag(energy_fit_covariance))
                energy_fit_correlation = np.identity(len(energy_fit_covariance))
                for ii in range(len(energy_fit_uncertainties)):
                    for jj in range(len(energy_fit_uncertainties)):
                        energy_fit_correlation[ii,jj] = energy_fit_covariance[ii,jj] / (energy_fit_uncertainties[ii] * energy_fit_uncertainties[jj])
                label = [f'p{i}:' for i in range(len(energy_fit_parameters))]
                text.append(f'#####\nEnergy fit: linear model (exponents: '+', '.join([f'{int(num)}' for num in esp])+f')\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{format(value,".2e").ljust(11)}{format(unc,".1e").ljust(11)}({format(abs(unc/value)*100,".2f")} %)' for lbl, value, unc in zip(label, energy_fit_parameters, energy_fit_uncertainties)])+'\n')
                text.append(f'Sum of squares of residuals: {np.sum(np.power(energy_fit_resisuals, 2)):.6f}\nAbsolute maximum excursion of residuals: {np.max(energy_fit_resisuals)-np.min(energy_fit_resisuals):.5f}\n')
                text.append(f'{"corr. M".ljust(9)}'+''.join([f'{lbl.ljust(9)}' for lbl in label])+'\n'+''.join([f'{lbl.ljust(9)}'+''.join([f'{format(col,".4f").ljust(9)}' for col in row])+'\n' for lbl, row in zip(label, energy_fit_correlation)]))
                
                #FWHM fit
                fwhm_fit_parameters, fwhm_fit_covariance, fwhm_fit_resisuals = self._fit_quadratic(fit_ch, fit_fw, esp)
                fwhm_fit_uncertainties = np.sqrt(np.diag(fwhm_fit_covariance))
                fwhm_fit_correlation = np.identity(len(fwhm_fit_covariance))
                for ii in range(len(fwhm_fit_uncertainties)):
                    for jj in range(len(fwhm_fit_uncertainties)):
                        fwhm_fit_correlation[ii,jj] = fwhm_fit_covariance[ii,jj] / (fwhm_fit_uncertainties[ii] * fwhm_fit_uncertainties[jj])
                label = [f'p{i}:' for i in range(len(fwhm_fit_parameters))]
                text.append(f'#####\nFWHM fit: squared linear model (exponents: '+', '.join([f'{int(num)}' for num in esp])+f')\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{format(value,".2e").ljust(11)}{format(unc,".1e").ljust(11)}({format(abs(unc/value)*100,".2f")} %)' for lbl, value, unc in zip(label, fwhm_fit_parameters, fwhm_fit_uncertainties)])+'\n')
                text.append(f'Sum of squares of residuals: {np.sum(np.power(fwhm_fit_resisuals, 2)):.6f}\nAbsolute maximum excursion of residuals: {np.max(fwhm_fit_resisuals)-np.min(fwhm_fit_resisuals):.5f}\n')
                text.append(f'{"corr. M".ljust(9)}'+''.join([f'{lbl.ljust(9)}' for lbl in label])+'\n'+''.join([f'{lbl.ljust(9)}'+''.join([f'{format(col,".4f").ljust(9)}' for col in row])+'\n' for lbl, row in zip(label, fwhm_fit_correlation)]))
                
                #efficiency fit
                efficiency_fit_parameters, efficiency_fit_covariance, efficiency_fit_resisuals = self._perform_efficiency_fit(fit_en,fit_efy, NAA.settings_dict['max allowed calibration uncertainty'])
                efficiency_fit_uncertainties = np.sqrt(np.diag(efficiency_fit_covariance))
                efficiency_fit_correlation = np.identity(len(efficiency_fit_covariance))
                self.data_to_plot.add_kedd('reference', fit_en/1000, fit_efy, efficiency_fit_resisuals, uy=ur_efy*fit_efy)
                self.data_to_plot.add_kedd_fit('reference', [1, 0, -1, -2, -3, -4], efficiency_fit_parameters)
                for ii in range(len(efficiency_fit_uncertainties)):
                    for jj in range(len(efficiency_fit_uncertainties)):
                        efficiency_fit_correlation[ii,jj] = self._safe_division(efficiency_fit_covariance[ii,jj],efficiency_fit_uncertainties[ii],efficiency_fit_uncertainties[jj])
                label = [f'p{i}:' for i in range(len(efficiency_fit_parameters))]
                text.append(f'#####\nEfficiency fit: polynomial model (exponents: '+', '.join([f'{int(num)}' for num in [1, 0, -1, -2, -3, -4]])+f')\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{format(value,".2e").ljust(11)}{format(unc,".1e").ljust(11)}({format(abs(unc/value)*100,".2f")} %)' for lbl, value, unc in zip(label, efficiency_fit_parameters, efficiency_fit_uncertainties)])+'\n')
                text.append(f'Sum of squares of residuals: {np.sum(np.power(efficiency_fit_resisuals, 2)):.6f}\nRelative maximum excursion of residuals: {(np.max(efficiency_fit_resisuals)-np.min(efficiency_fit_resisuals))*100:.3f} %\n')
                text.append(f'{"corr. M".ljust(9)}'+''.join([f'{lbl.ljust(9)}' for lbl in label])+'\n'+''.join([f'{lbl.ljust(9)}'+''.join([f'{format(col,".4f").ljust(9)}' for col in row])+'\n' for lbl, row in zip(label, efficiency_fit_correlation)]))
                #residuals
                ref_emissions = np.array(list(ref_emissions))
                xsort = np.argsort(np.abs(efficiency_fit_resisuals))
                xsort = xsort[::-1]
                text_res = [f'{"emission".ljust(20)}{"efficiency".ljust(12)}{"residual".ljust(12)}']
                for l_emission, l_effy, l_resid in zip(ref_emissions[xsort], fit_efy[xsort], efficiency_fit_resisuals[xsort]):
                    text_res += [f'{l_emission.ljust(20)}{format(l_effy,".3e").ljust(12)}{format(l_resid*100,"+.2f")} %']
                text_res = '\n'.join(text_res)+'\n'
                text.append(text_res)

                dummy_calibration = naaobject.DummyCalibration(CB_detector.get(), self.position_list['reference'], energy_fit_parameters, fwhm_fit_parameters, efficiency_fit_parameters, efficiency_fit_covariance, self.PT_list['reference'])
                dummy_calibration.mu = mu
                dummy_calibration.u_mu = umu
                dummy_calibration.x_data = fit_en
                dummy_calibration.y_data = fit_efy

                #only coincidence-free considered
                noCOI_filter = self.source.data[self.source.selection]['COIfree']
                coifree = self.source.data[self.source.selection][noCOI_filter]
                text.append(f'The selected reference source includes {len(coifree)} coincidence-free emissions ({", ".join(list(coifree["reference"]))}).')
                if len(coifree) < 6:
                    self.information_box.configure(text='Partial calibration performed')
                    text.append('Detector characterization in the other positions is not perfomed since a minimum number of 6 coincidence-free emission is required.\n')
                    energies = []
                else:
                    other_distances = [f'{value:.1f}' for pos_key, value in self.position_list.items() if pos_key != 'reference']
                    text.append(f'\n#####\nOther positions\n{len(other_distances)} more positions are investigated ({", ".join(other_distances)}) distances in mm.\n')
                    #count rate 2d array
                    C_values, keys, energies, C_values_absolute, rel_unc_C_values = self.get_coifree_data_to_fit(coifree, NAA.settings_dict['energy tolerance'], mu)
                    #d0 calculations
                    dummy_calibration = self._sqrtC_to_der(np.sqrt(C_values), keys, energies, dummy_calibration, C_values_absolute, rel_unc_C_values, NAA.settings_dict['max allowed calibration uncertainty'])
                    if dummy_calibration.der_parameters is not None:
                        label = [f'p{i}:' for i in range(len(dummy_calibration.der_parameters))]
                        der_fit_uncertainties = np.sqrt(np.diag(dummy_calibration.der_pcov))
                        text_message = 'polynomial model (exponents: '+', '.join([f'{int(num)}' for num in dummy_calibration.der_exponent])+f')\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{format(value,".2e").ljust(11)}{format(unc,".1e").ljust(11)}({format(abs(unc/value)*100,".2f")} %)' for lbl, value, unc in zip(label, dummy_calibration.der_parameters, der_fit_uncertainties)])+'\n'
                    else:
                        text_message = 'd0 evaluation not possible due to not enough data for d0 found in the specific position (at least 6 d0 values are needed that are calculated with a parabolic trend of the count rate for single emissions on at least 4 positions).\n'
                    text.append(f'#####\nd0 evaluation\n- {dummy_calibration.distance:.1f} mm (reference)\n{text_message}')
                    for dder_key, dder_value in dummy_calibration.der_dict.items():
                        if dder_value[1] is not None:
                            label = [f'p{i}:' for i in range(len(dder_value[1]))]
                            der_fit_uncertainties = np.sqrt(np.diag(dder_value[2]))
                            text_message = 'polynomial model (exponents: '+', '.join([f'{int(num)}' for num in dder_value[0]])+f')\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{format(value,".2e").ljust(11)}{format(unc,".1e").ljust(11)}({format(abs(unc/value)*100,".2f")} %)' for lbl, value, unc in zip(label, dder_value[1], der_fit_uncertainties)])+'\n'
                        else:
                            text_message = 'd0 evaluation not possible due to not enough data for d0 found in the specific position (at least 6 d0 values are needed that are calculated with a parabolic trend of the count rate for single emissions on at least 4 positions).\n'
                        text.append(f'\n- {dder_key:.1f} mm\n{text_message}')

                    text.append(f'#####\nkedd evaluation.\n')
                    #kedd calculations
                    rel_unc_C_values = C_values * np.sqrt(np.power(rel_unc_C_values[0],2) + np.power(rel_unc_C_values,2))
                    dummy_calibration = self._C_to_kedd(C_values[1:], keys[1:], energies, dummy_calibration, rel_unc_C_values[1:], NAA.settings_dict['max allowed calibration uncertainty'])
                    for kedd_key, kedd_value in dummy_calibration.kedd_dict.items():
                        if kedd_value[1] is not None:
                            label = [f'p{i}:' for i in range(len(kedd_value[1]))]
                            der_fit_uncertainties = np.sqrt(np.diag(kedd_value[2]))
                            text_message = 'polynomial model (exponents: '+', '.join([f'{int(num)}' for num in kedd_value[0]])+f')\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{format(value,".2e").ljust(11)}{format(unc,".1e").ljust(11)}({format(abs(unc/value)*100,".2f")} %)' for lbl, value, unc in zip(label, kedd_value[1], der_fit_uncertainties)])+'\n'
                        else:
                            text_message = 'kedd evaluation not possible due to not enough data for der found in the specific position (at least 5 der values are needed that are calculated with a linear trend of the count rate for single emissions on at least 2 positions).\n'
                        text.append(f'- reference to {kedd_key:.1f} mm\n{text_message}\n')

                dummy_calibration.PT_dict = {self.position_list[key]: value for key, value in self.PT_list.items() if key!='reference'}
                text.append(f'#####\nPT overview.\n')
                #PT overview
                if dummy_calibration.PT_energy is not None:
                    text_message = dummy_calibration.PT_text
                else:
                    text_message = 'PT evaluation not performed for this position\n'
                text.append(f'- PT at reference\n{text_message}\n')
                for PT_key, PT_value in dummy_calibration.PT_dict.items():
                    if PT_value[0] is not None:
                        text_message = PT_value[3]
                    else:
                        text_message = 'PT evaluation not performed for this position\n'
                    text.append(f'- PT at {PT_key:.1f} mm\n{text_message}\n')

                self.characterization_result = dummy_calibration
                self.information_box.configure(text='Successful calibration performed')
        logtext._update('\n'.join(text))
        CB_graphs['values'] = [f'position {item}' for item in self.data_to_plot.positions.keys()] + [f'emission {item}' for item in self.data_to_plot.emissions.keys()]
        CB_graphs.set('')
        messagebox.showinfo(title='Characterization performed!', message='Check the log and plots for information about the results', parent=parent)

    def get_coifree_data_to_fit(self, coifree_data, tolerance_energy, mu):
        #create an array of count rate ratios
        fit_C = []
        rel_unc_fit_C = []
        keys = sorted([(key, value) for key, value in self.position_list.items()], key=lambda x : x[1], reverse=True)
        energies = np.array(list(coifree_data['energy']))
        for position in keys:
            C_at_position = []
            unc_C_at_position = []
            for idx in list(coifree_data.index):
                emission_found = None
                for spectrum in self.spectra_list[position[0]]:
                    for plist_line in spectrum.peak_list:
                        if float(plist_line[2]) + float(tolerance_energy) > float(coifree_data.loc[idx,'energy']) and float(plist_line[2]) - float(tolerance_energy) < float(coifree_data.loc[idx,'energy']):
                            if emission_found is None:
                                emission_found = (self.calculate_efficiency_or_countrate(float(plist_line[4]), spectrum, coifree_data.loc[idx], self.source.datetime, mu, mode='CR'), float(plist_line[5])/float(plist_line[4]))
                            else:
                                idx_selection = spectrum.peak_list.index(plist_line)
                                show_selection = spectrum.assign_nuclide[idx_selection]
                                if show_selection == -1:
                                    if float(plist_line[5])/float(plist_line[4]) < emission_found[1]:
                                        emission_found = (self.calculate_efficiency_or_countrate(float(plist_line[4]), spectrum, coifree_data.loc[idx], self.source.datetime, mu, mode='CR'), float(plist_line[5])/float(plist_line[4]))
                                else:
                                    if spectrum.suspected[idx_selection][show_selection].reference == self.source.data[self.source.selection].loc[idx,'reference']:
                                        emission_found = (self.calculate_efficiency_or_countrate(float(plist_line[4]), spectrum, coifree_data.loc[idx], self.source.datetime, mu, mode='CR'), float(plist_line[5])/float(plist_line[4]))
                                        break
                        elif float(plist_line[2]) - float(tolerance_energy) > float(coifree_data.loc[idx,'energy']):
                            break
                if emission_found is not None:
                    C_at_position.append(emission_found[0])
                    unc_C_at_position.append(emission_found[1])
                else:
                    C_at_position.append(np.nan)
                    unc_C_at_position.append(np.nan)
            fit_C.append(C_at_position)
            rel_unc_fit_C.append(unc_C_at_position)
        fit_C_original = np.array(fit_C)
        rel_unc_fit_C = np.array(rel_unc_fit_C)
        fit_C = fit_C_original[0] / fit_C_original
        return fit_C, keys, energies, fit_C_original, rel_unc_fit_C

    def _sqrtC_to_der(self, Mvalues, okeys, energies, dummy_calibration, M_values_absolute, rel_unc_M_values, limit=50):
        #convert the matrix of squared count rate ratios to d0 values
        acceptable_limit = limit / 100 #provisional
        der_M = []
        unc_der_M = []
        keys, energies = np.array([float(item[1]) for item in okeys]), np.array([float(energy) for energy in energies])
        for idx, column in enumerate(Mvalues.T):
            delete_nan = ~np.isnan(column)
            if len(column[delete_nan]) >= 4:#for the moment
                parameters, mcov, residuals, relative_residuals = self._fit_linear(keys[delete_nan],column[delete_nan],[2,1,0])#weighted_here?
                #weighted
                #parameters_guess, _, _, _ = self._fit_linear(keys[delete_nan],column[delete_nan],[2,1,0])
                #parameters, mcov = curve_fit(self.linear_function_fit, keys[delete_nan], column[delete_nan], p0=parameters_guess, sigma=column[delete_nan] * rel_unc_M_values.T[idx][delete_nan], absolute_sigma=True)
                #relative_residuals = (column[delete_nan] - self.linear_function_fit(keys[delete_nan], *parameters)) / self.linear_function_fit(keys[delete_nan], *parameters)
                #end weighted
                self.data_to_plot.add_sqrtC(energies[idx], keys[delete_nan],column[delete_nan], relative_residuals, uy=column[delete_nan] * rel_unc_M_values.T[idx][delete_nan])
                self.data_to_plot.add_sqrtC_fit(energies[idx], [2,1,0], parameters)

                col_der = self.linear_d0(keys,parameters)
                unc_col_der = self.unc_linear_d0(keys,parameters,mcov)

                C_values_from_fit = self.linear_C(keys,parameters)
                C0 = M_values_absolute.T[idx][delete_nan][0]
                x_fit_range = np.linspace(np.min(keys[delete_nan]), np.max(keys[delete_nan]), 100)
                y_fit_range = C0 / np.power(self.linear_C(x_fit_range,parameters),2)
                relative_residuals_CD = (M_values_absolute.T[idx][delete_nan] - (C0 / np.power(C_values_from_fit,2))) / (C0 / np.power(C_values_from_fit,2))
                self.data_to_plot.add_linear_C(energies[idx], keys[delete_nan], M_values_absolute.T[idx][delete_nan], relative_residuals_CD, uy=M_values_absolute.T[idx][delete_nan] * rel_unc_M_values.T[idx][delete_nan])
                self.data_to_plot.add_linear_C_fit(energies[idx], x_fit_range, y_fit_range, relres=np.array([0.0] * len(x_fit_range)))
            else:
                col_der = np.array([np.nan for item in column])
                unc_col_der = np.array([np.nan for item in column])
            der_M.append(col_der)
            unc_der_M.append(unc_col_der)
        der_M = np.array(der_M).T
        unc_der_M = np.array(unc_der_M).T
        for idx, row in enumerate(der_M):
            delete_nan = ~np.isnan(row)
            popt, pcov = None, None
            x = energies[delete_nan] / 1000
            Y = row[delete_nan]
            EXP = [1, 0, -1, -2, -3]
            if len(Y) < 6:
                pass#f'warning: too few data points for der fit calculation at {data.name} mm distance!\n'
            else:
                Y_pre = np.log(np.abs(row[delete_nan]))
                popt_guess, _, _ = self.fit_multipoly(x, Y_pre, EXP)
                popt, pcov = curve_fit(self.der_function_fit, x, Y, p0=popt_guess, sigma=unc_der_M[idx][delete_nan], absolute_sigma=True)
                rel_res = (Y - self.der_function_fit(x, *popt)) / self.der_function_fit(x, *popt)
            if popt is not None:
                if okeys[idx][0] == 'reference':
                    dummy_calibration.der_exponent = EXP
                    dummy_calibration.der_parameters = popt
                    dummy_calibration.der_pcov = pcov
                    self.data_to_plot.add_der('reference', x, row[delete_nan], rel_res, uy=unc_der_M[idx][delete_nan])
                    self.data_to_plot.add_der_fit('reference', EXP, popt)
                else:
                    dummy_calibration.der_dict[okeys[idx][1]] = (EXP, popt, pcov)
                    self.data_to_plot.add_der(okeys[idx][1], x, row[delete_nan], rel_res, uy=unc_der_M[idx][delete_nan])
                    self.data_to_plot.add_der_fit(okeys[idx][1], EXP, popt)
        return dummy_calibration

    def der_function_fit(self, x, *p):
        return -np.exp(p[0]*x + p[1] + p[2]*x**-1 + p[3]*x**-2 + p[4]*x**-3)

    def linear_function_fit(self, x, *p):
        return p[0]*np.power(x,2) + p[1]*x + p[2]

    def _delta(self, parameters):
        _delta = np.sqrt(np.power(parameters[1], 2) - 4*parameters[0]*parameters[2])
        x1 = (-parameters[1] + _delta) / (2*parameters[0])
        x2 = (-parameters[1] - _delta) / (2*parameters[0])
        if x1 < 0 and x1 > x2:
            return x1
        elif x2 < 0 and x2 > x1:
            return x2
        else:
            return np.nan

    def _C_to_kedd(self, Mvalues, okeys, energies, dummy_calibration, unc_Mvalues, limit=50):
        acceptable_limit = limit/100
        keys, energies = np.array([float(item[1]) for item in okeys]), np.array([float(energy) for energy in energies])
        for idx, row in enumerate(Mvalues):
            delete_nan = ~np.isnan(row)
            popt, pcov = None, None
            x = energies[delete_nan] / 1000
            Y = np.log(row[delete_nan])
            EXP = [1, 0, -1, -2, -3, -4]
            if 5 <= len(Y) <= 6:
                EXP.pop(5)  # = [1, 0, -1, -2, -3, -4]
            if len(Y) < 5:
                pass#f'warning: too low data points for der fit calculation at {data.name} mm distance!\n'
            else:
                popt, pcov, rel_res = self.fit_multipoly(x, Y, EXP)
                perr = np.sqrt(np.diag(pcov))
                perrpopt = perr / popt
                agmax = np.argmax(np.abs(perrpopt))
                if np.abs(perrpopt[agmax]) > acceptable_limit and len(popt) > 4:
                    EXP.pop(agmax)
                    popt, pcov, rel_res = self.fit_multipoly(x, Y, EXP)
                    perr = np.sqrt(np.diag(pcov))
                    perrpopt = perr / popt
                    agmax = np.argmax(np.abs(perrpopt))
                    if np.abs(perrpopt[agmax]) > acceptable_limit and len(popt) > 4:
                        EXP.pop(agmax)
                        popt, pcov, rel_res = self.fit_multipoly(x, Y, EXP)
                        perr = np.sqrt(np.diag(pcov))
            if popt is not None:
                #print(rel_res)
                dummy_calibration.kedd_dict[okeys[idx][1]] = (EXP, popt, pcov)
                self.data_to_plot.add_kedd(okeys[idx][1], x, row[delete_nan], rel_res, uy=unc_Mvalues[idx][delete_nan])
                self.data_to_plot.add_kedd_fit(okeys[idx][1], EXP, popt)
        return dummy_calibration

    def fit_multipoly(self, x, Y, EXP):
        #calculate the polynomial fit and return parameters, covariance matrix and relative residuals
        W = x[:, np.newaxis] ** EXP
        I = np.identity(len(W))
        popt = np.linalg.inv(W.T@W)@(W.T@Y)
        ress = Y - popt@W.T
        n, k = Y.shape[0], W.shape[1]
        pcov = np.linalg.inv((W.T@np.linalg.inv(np.true_divide(1, n-k)*np.dot(ress, ress)*I))@W)
        #rel_ress = ress / (popt@W.T)
        return popt, pcov, ress

    def linear_C(self, X, p):
        #calculation of Count rate at positions X based on previous linear fit on sqrt(C0/Cx)
        return p[0]*np.power(X,2) + p[1]*X + p[2]

    def linear_d0(self, X, p):
        #this the original
        #return -(-p[0]*np.power(X,2) + p[2]) / (2*p[0]*X + p[1])
        
        #this the modified
        ret = -(-p[0]*np.power(X,2) + p[2]) / (2*p[0]*X + p[1])
        ret[ret >= 0.0] = np.nan
        return ret

    def unc_linear_d0(self, X, p, cov):
        uncertainty = []
        for distance in X:
            a2 = (p[1]*np.power(distance,2) + 2*p[2]*distance) / np.power(2*p[0]*distance + p[1], 2)
            a1 = (-p[0]*np.power(distance,2) + p[2]) / np.power(2*p[0]*distance + p[1], 2)
            a0 = -1 / (2*p[0]*distance + p[1])
            sensitivity_coefficient = np.array([a2, a1, a0])
            ui = np.sqrt((sensitivity_coefficient.T@cov)@sensitivity_coefficient)
            uncertainty.append(ui)
        return np.array(uncertainty)

    def linear_der(self, X, p):
        #calculation of der at positions X based on derivative of previous fit
        return (-2 * (2*p[0]*X + p[1])) / (p[0]*np.power(X,2) + p[1]*X + p[2])

    def unc_linear_der(self, X, p, cov):
        #uncertainty of der
        uncertainty = []
        for distance in X:
            a0 = (2 * np.power(distance,2)* (2*p[0]*distance + p[1])) / np.power(p[0]*np.power(distance,2) + p[1]*distance + p[2],2) - (4*distance) / (p[0]*np.power(distance,2) + p[1]*distance + p[2])
            a1 = (2 * distance* (2*p[0]*distance + p[1])) / np.power(p[0]*np.power(distance,2) + p[1]*distance + p[2],2) - 2 / (p[0]*np.power(distance,2) + p[1]*distance + p[2])
            a2 = (2 * (2*p[0]*distance + p[1])) / np.power(p[0]*np.power(distance,2) + p[1]*distance + p[2],2)
            sensitivity_coefficient = np.array([a0, a1, a2])
            ui = np.sqrt((sensitivity_coefficient.T@cov)@sensitivity_coefficient)
            uncertainty.append(ui)
        return np.array(uncertainty)

    def _safe_division(self, cov, errA, errB):
        if errA != 0.0 and errB != 0.0:
            return cov / (errA * errB)
        else:
            return 0.0

    def _perform_efficiency_fit(self, X, Y, limit):
        X = X / 1000
        Y = np.log(Y)
        esp = [1, 0, -1, -2, -3, -4]
        solution = False
        fparameters, fmcov = np.array([0.0]*6), np.zeros((6,6))
        while solution == False:
            parameters, mcov, residuals, _ = self._fit_linear(X, Y, esp)
            uncertainties = np.sqrt(np.diag(mcov))
            if np.max(np.abs(uncertainties / parameters)) > limit / 100 and len(parameters) > 4:
                idx = np.argmax(np.abs(uncertainties / parameters))
                try:
                    idx = idx[0]
                except:
                    pass
                esp.pop(idx)
            else:
                solution = True
        guide = [1, 0, -1, -2, -3, -4]
        for exponent, par, covline in zip(esp, parameters, mcov):
            fparameters[guide.index(exponent)] = par
            for exponent2, cov in zip(esp, covline):
                fmcov[guide.index(exponent),guide.index(exponent2)] = cov
        return fparameters, fmcov, residuals

    def _fit_linear(self, X, Y, esp):
        W = X[:, np.newaxis]**esp
        I = np.identity(W.shape[0])
        parameters = np.linalg.inv(W.T@W)@(W.T@Y)
        residuals = Y - parameters@W.T
        n, k = Y.shape[0], W.shape[1]
        mcov = np.linalg.inv((W.T@np.linalg.inv(np.true_divide(1, n-k)*np.dot(residuals, residuals)*I))@W)
        rel_res = residuals / (parameters@W.T)
        return parameters, mcov, residuals, rel_res

    def _fit_quadratic(self, X, Y, esp):
        Y = np.power(Y, 2)
        W = X[:, np.newaxis]**esp
        I = np.identity(W.shape[0])
        parameters = np.linalg.inv(W.T@W)@(W.T@Y)
        residuals = np.sqrt(Y) - np.sqrt(parameters@W.T)
        n, k = Y.shape[0], W.shape[1]
        mcov = np.linalg.inv((W.T@np.linalg.inv(np.true_divide(1, n-k)*np.dot(residuals, residuals)*I))@W)
        return parameters, mcov, residuals

    def calculate_efficiency_or_countrate(self, n_area, spectrum, source, s_datetime, mu, mode='efficiency'):
        _lbd = source['lambda']
        td = spectrum.datetime - s_datetime
        td = td.total_seconds()#td.days*86400 + td.seconds
        if mode == 'efficiency': #return efficiency value
            return (n_area*_lbd*spectrum.real_time*np.exp(mu*(1-spectrum.live_time/spectrum.real_time)))/(spectrum.live_time*np.exp(-_lbd*td)*(1-np.exp(-_lbd*spectrum.real_time))*source['yield']*source['activity'])
        else: #return count rate value
            return (n_area*_lbd*spectrum.real_time*np.exp(mu*(1-spectrum.live_time/spectrum.real_time)))/(spectrum.live_time*np.exp(-_lbd*td)*(1-np.exp(-_lbd*spectrum.real_time)))

    def get_data_to_fit(self, tolerance_energy, mu):
        #do something under the hood
        fit_ch = []  # mean(axis=1) #maybe single
        fit_en = []  # single       #maybe single
        fit_fw = []  # mean(axis=1) #maybe single
        fit_efy = []  # mean(axis=1)#maybe single
        u_efy = [] # statistical (relative) uncertainty of peak 
        index = []
        warnings = []
        for idx in list(self.source.data[self.source.selection].index):
            emission_found = None
            warning = False
            for spectrum in self.spectra_list['reference']:
                for plist_line in spectrum.peak_list:
                    if float(plist_line[2]) + float(tolerance_energy) > float(self.source.data[self.source.selection].loc[idx,'energy']) and float(plist_line[2]) - float(tolerance_energy) < float(self.source.data[self.source.selection].loc[idx,'energy']):
                        if emission_found is None:
                            emission_found = (float(self.source.data[self.source.selection].loc[idx,'energy']), float(plist_line[0]), float(plist_line[6]), self.calculate_efficiency_or_countrate(float(plist_line[4]), spectrum, self.source.data[self.source.selection].loc[idx], self.source.datetime, mu), float(plist_line[5])/float(plist_line[4]), spectrum.filename())
                        else:
                            idx_selection = spectrum.peak_list.index(plist_line)
                            show_selection = spectrum.assign_nuclide[idx_selection]
                            if show_selection == -1:
                                warning = True
                                if float(plist_line[5])/float(plist_line[4]) < emission_found[4]:
                                    emission_found = (float(self.source.data[self.source.selection].loc[idx,'energy']), float(plist_line[0]), float(plist_line[6]), self.calculate_efficiency_or_countrate(float(plist_line[4]), spectrum, self.source.data[self.source.selection].loc[idx], self.source.datetime, mu), float(plist_line[5])/float(plist_line[4]), spectrum.filename())
                            else:
                                if spectrum.suspected[idx_selection][show_selection].reference == self.source.data[self.source.selection].loc[idx,'reference']:
                                    emission_found = (float(self.source.data[self.source.selection].loc[idx,'energy']), float(plist_line[0]), float(plist_line[6]), self.calculate_efficiency_or_countrate(float(plist_line[4]), spectrum, self.source.data[self.source.selection].loc[idx], self.source.datetime, mu), float(plist_line[5])/float(plist_line[4]), spectrum.filename())
                                    break
                    elif float(plist_line[2]) - float(tolerance_energy) > float(self.source.data[self.source.selection].loc[idx,'energy']):
                        break
            if emission_found is not None:
                fit_ch.append(emission_found[1])
                fit_en.append(emission_found[0])
                fit_fw.append(emission_found[2])
                fit_efy.append(emission_found[3])
                u_efy.append(emission_found[4])
                index.append(idx)
                if warning:
                    warnings.append(f'multiple! (selected: {emission_found[5]} at channel {emission_found[1]:.1f})')#5
                else:
                    warnings.append(f' -> {emission_found[5]}')
        return np.array(fit_ch), np.array(fit_en), np.array(fit_fw), np.array(fit_efy), np.array(index), u_efy, warnings


class PTEvaluateWindow:
    def __init__(self, parent, key, PT_list, spectra_list, background, source, tolerance_energy, PT_button, red, green, tolerance_unc):
        parent.title(f'PT evaluation for {key}')
        parent.resizable(False, False)
        self.linear = None
        self.polynomial = None
        self.actual_background_list = [item for item in background]
        self.actual_spectra_list = [item for item in spectra_list]
        mframe = tk.Frame(parent)
        self.PT_peaklist = None
        self.data = None
        self.use_user_data = False
        self.information_box = tk.Label(mframe, anchor=tk.W)
        tk.Label(mframe, text='background', width=15, anchor=tk.W).grid(row=0, column=0)
        CB_background = ttk.Combobox(mframe, width=20, state='readonly')
        CB_background.grid(row=0, column=1)
        CB_background['values'] = [item.filename() for item in self.actual_background_list]
        if len(CB_background['values']) > 0:
            CB_background.set(CB_background['values'][0])

        logo_add_spectra = tk.PhotoImage(data=gui_things.plus_spectrum)
        B_add_background_spectra = gui_things.Button(mframe, image=logo_add_spectra, hint='Recall a background spectrum!', hint_destination=self.information_box)
        B_add_background_spectra.grid(row=0, column=2)
        B_add_background_spectra.image = logo_add_spectra
        logo_peaklist_spectra = tk.PhotoImage(data=gui_things.plist)

        visual_frame = tk.Frame(mframe)
        f = Figure(figsize=(4.5, 4))
        ax_PT = f.add_subplot(211)
        ax_resd = f.add_subplot(212)
        Figur = tk.Frame(visual_frame)
        Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        canvas = FigureCanvasTkAgg(f, master=Figur)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ax_PT.set_ylabel(r'$P/T$ / 1')
        ax_resd.set_xlabel(r'$E$ / keV')
        ax_resd.set_ylabel('residuals / %')
        f.tight_layout()
        canvas.draw()
        visual_frame.grid(row=0, column=4, rowspan=12, sticky=tk.NS)

        tk.Frame(mframe).grid(row=1, column=0, pady=5)
        tk.Label(mframe, text='spectra', width=15, anchor=tk.W).grid(row=2, column=0, sticky=tk.W)

        ListFrame = tk.Frame(mframe)
        scrollbar = tk.Scrollbar(ListFrame, orient="vertical")
        listbox = tk.Listbox(ListFrame, heigh=7, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        ListFrame.grid(row=3, column=0, rowspan=3, columnspan=2, sticky=tk.NSEW)
        listbox.delete(0,tk.END)
        for item in self.actual_spectra_list:
            listbox.insert(tk.END, item.filename())

        B_add_PT_spectra = gui_things.Button(mframe, image=logo_add_spectra, hint='Recall spectra for PT evaluation!', hint_destination=self.information_box)
        B_add_PT_spectra.grid(row=3, column=2)
        B_add_PT_spectra.image = logo_add_spectra

        B_peaklist_PT_spectra = gui_things.Button(mframe, image=logo_peaklist_spectra, hint='Show the peaklist of selected PT spectra!', hint_destination=self.information_box)
        B_peaklist_PT_spectra.grid(row=4, column=2)
        B_peaklist_PT_spectra.image = logo_peaklist_spectra

        logo_del_spectra = tk.PhotoImage(data=gui_things.none)
        B_delete_PT_spectra = gui_things.Button(mframe, image=logo_del_spectra, hint='Delete selected spectrum!', hint_destination=self.information_box)
        B_delete_PT_spectra.grid(row=5, column=2)
        B_delete_PT_spectra.image = logo_del_spectra

        F_delete_selector_PT = tk.Frame(mframe)
        self.delete_selector_PT = tk.IntVar(parent)
        R1 = tk.Radiobutton(F_delete_selector_PT, text='selected', anchor=tk.W, value=0, variable=self.delete_selector_PT)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_delete_selector_PT, text='all', anchor=tk.W, value=1, variable=self.delete_selector_PT)
        R2.pack(anchor=tk.W)
        self.delete_selector_PT.set(0)
        F_delete_selector_PT.grid(row=5, column=3, padx=3)

        tk.Frame(mframe).grid(row=6, column=0, pady=5)
        tk.Label(mframe, text='junction E / keV', anchor=tk.W).grid(row=7, column=0, sticky=tk.W)
        self.E_joint = gui_things.FSlider(mframe, decimals=1, label_width=5, default=170.0, from_=165.0, to=370.0, length=200, resolution=1.0)
        self.E_joint.grid(row=8, column=0, columnspan=4, sticky=tk.W)
        #stick

        sum_of_residuals = tk.Label(mframe, text=f'sum of residuals (< {self.E_joint.get():.1f} keV): {np.nan}', anchor=tk.W)
        sum_of_residuals.grid(row=12, column=4, sticky=tk.W)

        tk.Frame(mframe).grid(row=9, column=0, pady=5)
        tk.Label(mframe, text='log', anchor=tk.W).grid(row=10, column=0, sticky=tk.W)
        stext = gui_things.ScrollableText(mframe)
        stext.grid(row=11, column=0, columnspan=4, sticky=tk.EW)

        mbuttons = tk.Frame(mframe)
        logo_work = tk.PhotoImage(data=gui_things.manygears)
        B_perform_PT = gui_things.Button(mbuttons, image=logo_work, hint='Start elaboration!', hint_destination=self.information_box)
        B_perform_PT.pack(side=tk.LEFT)
        B_perform_PT.image = logo_work
        logo_manual = tk.PhotoImage(data=gui_things.ggear)
        B_insert_manual_data_PT = gui_things.Button(mbuttons, image=logo_manual, hint='Insert PT data!', hint_destination=self.information_box)
        B_insert_manual_data_PT.pack(side=tk.LEFT)
        B_insert_manual_data_PT.image = logo_manual
        logo_confirm = tk.PhotoImage(data=gui_things.beye)
        B_confirm_PT = gui_things.Button(mbuttons, image=logo_confirm, hint='Confirm elaboration!', hint_destination=self.information_box)
        B_confirm_PT.pack(side=tk.LEFT)
        B_confirm_PT.image = logo_confirm
        mbuttons.grid(row=12, column=0, columnspan=4, sticky=tk.EW, pady=5)

        self.information_box.grid(row=13, column=0, columnspan=4, sticky=tk.NSEW)
        mframe.pack(anchor=tk.NW, padx=5, pady=5)

        B_add_background_spectra.configure(command=lambda : self.add_background(parent, CB_background))
        B_add_PT_spectra.configure(command=lambda : self.add_spectra(parent, tolerance_unc, listbox, source))
        B_peaklist_PT_spectra.configure(command=lambda : self.see_PT_spectra_peak_list(CB_background, listbox, parent))
        B_delete_PT_spectra.configure(command=lambda : self.delete_PTspectrum_file(parent, listbox))

        B_perform_PT.configure(command=lambda : self.PT_elaboration(CB_background, source, stext, tolerance_energy, ax_PT, ax_resd, f, canvas, sum_of_residuals))
        B_insert_manual_data_PT.configure(command=lambda : self.PT_data_manual_insert(parent, stext, ax_PT, ax_resd, f, canvas, sum_of_residuals))
        B_confirm_PT.configure(command=lambda : self.confirm_elaboration(PT_list, key, PT_button, red, green, stext))

    def delete_PTspectrum_file(self, parent, listbox):
        if self.PT_peaklist is not None:
            self.PT_peaklist.destroy()
            self.PT_peaklist = None
        if self.delete_selector_PT.get() == 0:
            idx = listbox.curselection()
            try:
                idx = idx[0]
            except:
                idx = -1
            if idx >= 0:# and len(self.actual_spectra_list) > 0:
                filename = listbox.get(idx)
                if messagebox.askyesno(title='Remove spectrum', message=f'\nAre you sure to remove spectrum: {filename} from selection?\n', parent=parent):
                    self.actual_spectra_list.pop(idx)
                    self.data = None
                    self.use_user_data = False
                    listbox.delete(0, tk.END)
                    for spect in self.actual_spectra_list:
                        listbox.insert(tk.END, spect.filename())
                    self.information_box.configure(text=f'{filename} spectrum removed')
            else:
                self.information_box.configure(text='no spectrum selected')
        else:
            lenght = len(self.actual_spectra_list)
            if lenght > 0:
                if messagebox.askyesno(title='Remove spectrum', message='\nAre you sure to remove all spectra from selection?\n', parent=parent):
                    for _ in range(lenght):
                        self.actual_spectra_list.pop()
                        self.data = None
                        self.use_user_data = False
                    listbox.delete(0, tk.END)
                    for spect in self.actual_spectra_list:
                        listbox.insert(tk.END, spect.filename())
                    self.information_box.configure(text=f'{lenght} spectra removed')

    def add_background(self, parent, box):
        #add background for PT calculations
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))#,('HyperLab ASC file','*.asc'),('CHN spectrum file','*.chn'))
        limit_s = 1
        try:
            output = askopenfilename(parent=parent, title='Open PT background',filetypes=filetypes)
        except TypeError:
            output = ''
        if output != '' and output is not None:
            self.data = None
            self.use_user_data = False
            peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(output, limit=limit_s, look_for_peaklist_option=True)
            efficiency = None#NAA.calibration
            if result == True:
                Spectrum = naaobject.SpectrumAnalysis(identity=f'PT_background', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=output, source=source, efficiency=efficiency)
                for _ in range(len(self.actual_background_list)):
                    self.actual_background_list.pop()
                self.actual_background_list.append(Spectrum)
                box['values'] = [item.filename() for item in self.actual_background_list]
                if len(box['values']) > 0:
                    box.set(box['values'][0])
            else:
                self.information_box.configure(text='failed to import spectrum')

    def add_spectra(self, parent, tol, listbox, database_source):
        #add spectra for PT calculations
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))#,('HyperLab ASC file','*.asc'),('CHN spectrum file','*.chn'))
        limit_s = tol
        try:
            output = tuple(askopenfilenames(parent=parent, title='Open PT spectra',filetypes=filetypes))
        except TypeError:
            output = ()
        for filename in output:
            self.data = None
            self.use_user_data = False
            if filename != '' and filename != ():
                peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=True)
                efficiency = None#NAA.calibration
                if result == True:
                    Spectrum = naaobject.SpectrumAnalysis(identity=f'PT_spectrum', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=output, source=source, efficiency=efficiency, database_source=database_source)
                    self.actual_spectra_list.append(Spectrum)
                else:
                    self.information_box.configure(text='failed to import spectrum')
        listbox.delete(0, tk.END)
        for spect in self.actual_spectra_list:
            listbox.insert(tk.END, spect.filename())

    def see_PT_spectra_peak_list(self, box, listbox, parent):
        #display the peaklist for the selected spectrum
        self.actual_background_list
        self.actual_spectra_list
        if len(self.actual_background_list) > 0 and box.get() != '':
            background = self.actual_background_list[0]
        else:
            background = None
        if len(self.actual_spectra_list) > 0:
            idx = listbox.curselection()
            try:
                if idx[0] < 0:
                    idx = 0
                else:
                    idx = idx[0]
            except:
                idx = 0
            if self.PT_peaklist is not None:
                self.PT_peaklist.destroy()
            self.PT_peaklist = tk.Toplevel(parent)
            nline = 15
            local_peak_list = nest_list(self.actual_spectra_list[idx].peak_list, nline)
            local_suspected = nest_list(self.actual_spectra_list[idx].suspected, nline)
            PeaklistWindow(self.PT_peaklist, self.actual_spectra_list[idx], local_peak_list, local_suspected, nline, background=background)

    def confirm_elaboration(self, PT_list, key, PT_button, red, green, stext):
        if self.linear is not None and self.polynomial is not None:
            PT_list[key] = (self.E_joint.get(), self.linear, self.polynomial, stext.get())
            PT_button.configure(image=green)
            self.information_box.configure(text='PT evaluation saved')
        else:
            self.information_box.configure(text='PT evaluation failed')

    def PT_data_manual_insert(self, parent, stext, ax_PT, ax_resd, f, canvas, sum_of_residuals):
        if self.data is not None:
            if self.PT_peaklist is not None:
                self.PT_peaklist.destroy()
            self.PT_peaklist = tk.Toplevel(parent)
            self.PT_peaklist.title('PT data')
            self.PT_peaklist.resizable(False, False)
            mframe = tk.Frame(self.PT_peaklist)
            boxes = []
            tk.Label(mframe, text='emission', width=20, anchor=tk.W).grid(row=0,column=0, sticky=tk.W)
            tk.Label(mframe, text='PT value / 1', anchor=tk.W).grid(row=0,column=1, sticky=tk.W)
            for idx, line in enumerate(self.data):
                tk.Label(mframe, text=f'{line[3]}', width=20, anchor=tk.W).grid(row=idx+1,column=0, sticky=tk.W)
                SPB = tk.Spinbox(mframe, width=12, from_=0.0000, to=1.0000, increment=0.0001)
                SPB.grid(row=idx+1, column=1, padx=5)
                SPB.delete(0, tk.END)
                SPB.insert(tk.END, f'{line[2]:.4f}')
                boxes.append(SPB)

            mframe.pack(padx=5, pady=5, anchor=tk.NW)
            b_frame = tk.Frame(self.PT_peaklist)
            check_box_variable = tk.BooleanVar(self.PT_peaklist)
            check_box = tk.Checkbutton(b_frame, text='adopt user values', variable=check_box_variable, command=lambda : self.check_checkbox(check_box_variable))
            check_box.pack(side=tk.LEFT)
            check_box_variable.set(self.use_user_data)
            logo_confirm = tk.PhotoImage(data=gui_things.ggear)
            B_accept_manual_data_PT = gui_things.Button(b_frame, image=logo_confirm)
            B_accept_manual_data_PT.pack(side=tk.LEFT)
            B_accept_manual_data_PT.image = logo_confirm
            B_accept_manual_data_PT.configure(command=lambda : self.confirm_user_inserted_values(boxes, stext, ax_PT, ax_resd, f, canvas, sum_of_residuals))
            b_frame.pack(padx=5, pady=5, anchor=tk.NW)
        else:
            self.information_box.configure(text='perform an elaboration')

    def check_checkbox(self, variable):
        self.use_user_data = variable.get()

    def confirm_user_inserted_values(self, boxes, stext, ax_PT, ax_resd, f, canvas, sum_of_residuals):
        for idx,box in enumerate(boxes):
            try:
                self.data[idx][2] = float(box.get())
            except:
                pass
        if self.use_user_data == True:
            self.PT_elaboration(None, None, stext, None, ax_PT, ax_resd, f, canvas, sum_of_residuals)
        else:
            self.information_box.configure(text='check the checkbox to confirm')

    def PT_elaboration(self, box_background, source, stext, tolerance_energy, ax_PT, ax_resd, f, canvas, sum_of_residuals):
        nlines = len(ax_PT.lines)
        for _ in range(nlines):
            ax_PT.lines.pop()
        nlines = len(ax_resd.lines)
        for _ in range(nlines):
            ax_resd.lines.pop()
        lenght = True
        ttext = []
        if self.use_user_data == True and self.data is not None:
            data_values = self.data
            E = self.E_joint.get()
            ttext.append('PT values modified by the user\n')
        else:
            if box_background.current() >= 0:
                back = self.actual_background_list[box_background.current()]
                for spc in self.actual_spectra_list:
                    if spc.number_of_channels() != back.number_of_channels():
                        lenght = False
            else:
                back = None
                lenght = False
            coifree_filter = source.data[source.selection]['COIfree']
            energies, references = list(source.data[source.selection][coifree_filter]['energy']), list(source.data[source.selection][coifree_filter]['reference'])
            #coifree_filter = source.data['COIfree']
            #energies, references = list(source.data[coifree_filter]['energy']), list(source.data[coifree_filter]['reference'])
            if back is not None and lenght == True:
                data_values = []
                E = self.E_joint.get()
                for energy, ref in zip(energies, references):
                    for spectrum in self.actual_spectra_list:
                        #find the peak area
                        found, area = False, None
                        for plist_line in spectrum.peak_list:
                            if float(plist_line[2]) + float(tolerance_energy) > float(energy) and float(plist_line[2]) - float(tolerance_energy) < float(energy):
                                if area is None:
                                    found = True
                                    area = float(plist_line[4])
                                else:
                                    idx_selection = spectrum.peak_list.index(plist_line)
                                    show_selection = spectrum.assign_nuclide[idx_selection]
                                    if show_selection == -1:
                                        if float(plist_line[5])/float(plist_line[4]) < np.sqrt(area) / area:
                                            found = True
                                            area = float(plist_line[4])
                                    else:
                                        if spectrum.suspected[idx_selection][show_selection].reference == ref:
                                            found = True
                                            area = float(plist_line[4])
                                            break
                            elif float(plist_line[2]) - float(tolerance_energy) > float(energy):
                                break
                        if found == True:
                            #background correction
                            bkgcorr_counts = np.array(spectrum.counts) - np.array(back.counts)/back.live_time * spectrum.live_time

                            #low energies correction #+20
                            low_limit = np.where(bkgcorr_counts > 0)
                            try:
                                low_limit = low_limit[0][0]
                            except IndexError:
                                low_limit = 50
                            bkgcorr_counts[:low_limit] = np.max(bkgcorr_counts[low_limit:low_limit+20])
                            super_threshold_indices = bkgcorr_counts < 0
                            bkgcorr_counts[super_threshold_indices] = 0

                            #print(np.sum(bkgcorr_counts))
                            PT = area / np.sum(bkgcorr_counts)
                            if ref == '122.10 keV Co-57':
                                for pline in spectrum.peak_list:
                                    corr_136 = 0.0
                                    if float(pline[2]) + float(tolerance_energy) > 136.5 and float(pline[2]) - float(tolerance_energy) < 136.5:
                                        corr_136 = float(pline[4])
                                PT = area / (np.sum(bkgcorr_counts) - corr_136)
                            data_values.append([float(energy), area, PT, ref])
                            break
            else:
                ttext.append('Elaboration stopped.\n- background is required for background correction and must have a spectrum profile of same number of channels with respect to the spectra!')
                f.tight_layout()
                canvas.draw()
                stext._update('\n'.join(ttext))
        try:
            self.data = data_values
        except UnboundLocalError:
            self.data = None
        if self.data is not None:
            ttext.append(f'background: {back.filename()}\nsource spectra: {", ".join([spc.filename() for spc in self.actual_spectra_list])}\n')
            ttext.append(f'{"emitter".ljust(20)}{"area / 1".ljust(12)}{"PT / 1".ljust(12)}\n'+'\n'.join([f'{dataline[3].ljust(20)}{format(dataline[1],".0f").ljust(11)}{format(dataline[2],".4f").ljust(11)}' for dataline in self.data])+'\n')
            x, y = np.array([line[0] for line in self.data]), np.array([line[2] for line in self.data])
        else:
            x, y = np.array([]), np.array([])
        # fitting parameter
        DX = 200
        #initialization
        linp, polyp = None, None
        x_data_selector = x > E
        x_data, y_data = x[x_data_selector], y[x_data_selector]
        x_data, y_data = np.log10(x_data), np.log10(y_data)
        if len(x_data) > 1:
            linp, pcov = curve_fit(self.lin_p, x_data, y_data)
            logyE = self.lin_p(np.log10(E), *linp)
            yE = 10**logyE
            res = self.residual_sum_of_squares(y_data, self.lin_p(x_data, *linp)) #res lin
            res_lin_plot = (10**y_data - 10**self.lin_p(x_data, *linp)) / 10**self.lin_p(x_data, *linp)
            lin_data = 10**x_data
            #data in the polynomial part if len(y) > x continues
            x_data, y_data = x[~x_data_selector], y[~x_data_selector]
            x_data, y_data = np.log10(x_data), np.log10(y_data)
            if len(x_data) >= 2:
                root = minimize(self.residual_minimization_func, [0,1,1], args=(x_data, y_data), constraints=({'type': 'eq', 'fun': lambda x: 2*x[0]*np.log10(E)+x[1]-linp[0]}, {'type': 'eq', 'fun': lambda x: x[0]*np.power(np.log10(E),2) + x[1]*np.log10(E) + x[2] - logyE}))
                polyp = root.x
                resp = root.fun
                res_pol_plot = (10**y_data - 10**self.func(x_data, *polyp)) / 10**self.func(x_data, *polyp) #res poly
                pol_data = 10**x_data
            else:
                ttext.append(f'Elaboration stopped.\n- not enought data to fit in the low energy region: 0 - {E:.1f} keV\n')
        else:
            ttext.append(f'Elaboration stopped.\n- not enought data to fit in the high energy region: {E:.1f} - ∞ keV\n')
        if linp is not None and polyp is not None:
            #print results
            ttext.append(f'polynomial fit (exponents: 2, 1, 0)\np0: {polyp[0]:.3e}\np1: {polyp[1]:.3e}\np2: {polyp[2]:.3e}\n\njunction energy: {E:.1f} keV\n\nlinear fit (exponents: 1, 0)\nl0: {linp[0]:.3e}\nl1: {linp[1]:.3e}\n')
            ttext.append(f'sum of residuals (< {E:.1f} keV): {resp:.3e}\n')
            sum_of_residuals.configure(text=f'sum of residuals (< {E:.1f} keV): {resp:.3e}', anchor=tk.W)
            self.linear = linp
            self.polynomial = polyp

            #plot #ax_PT, f, canvas
            ax_PT.loglog(x, y, marker='o', linestyle='', markerfacecolor='r', markersize=4, markeredgewidth=0.5, color='k')
            ax_PT.loglog(E, yE, marker='x', linestyle='', color='y', markerfacecolor='y', markersize=6, zorder=7)
            #polynomial part
            x_fit = np.linspace(np.min(x), E, DX)
            y_fit = self.func(np.log10(x_fit), *polyp)
            ax_PT.loglog(x_fit, 10**y_fit, linestyle='-', linewidth=1, color='k')
            #linear part
            x_fit = np.linspace(E, np.max(x), DX)
            y_fit = self.lin_p(np.log10(x_fit), *linp)
            ax_PT.loglog(x_fit, 10**y_fit, linestyle='-', linewidth=1, color='k')
            #residuals
            ax_resd.semilogx(lin_data,100*res_lin_plot, marker='o', linestyle='', markerfacecolor='r', markersize=4, markeredgewidth=0.5, color='k')
            ax_resd.semilogx(pol_data,100*res_pol_plot, marker='o', linestyle='', markerfacecolor='r', markersize=4, markeredgewidth=0.5, color='k')
            ax_PT.set_ylim(None,1)
            ax_resd.set_xlim(ax_PT.get_xlim())
            abs_x_lim = np.max([np.max(np.abs(100*res_lin_plot)),np.max(np.abs(100*res_pol_plot))])
            ax_resd.set_ylim(-abs_x_lim*1.2, abs_x_lim*1.2)
        f.tight_layout()
        canvas.draw()
        stext._update('\n'.join(ttext))

    def func(self, x, a1, a2, a3):
        return a1*np.power(x,2) + a2*x + a3

    def residual_minimization_func(self, params, x, y):
        residuals = [y_data - self.func(x_data, *params) for x_data, y_data in zip(x,y)]
        return np.sum(np.power(residuals,2))
        
    def lin_p(self, x, a1, a2):
        return a1*x + a2

    def residual_sum_of_squares(self, values, fitted_values):
        return np.sum(np.power(values-fitted_values, 2))


class PTViewWindow:
    def __init__(self, parent, key, PT_list, PT_button, red, green, vtype='view', take_focus=True):
        parent.title('PT fit')
        parent.resizable(False, False)
        PT_values = PT_list[key]
        data_frame = tk.Frame(parent)
        self.infobox = tk.Label(data_frame, text='', anchor=tk.W)
        tk.Label(data_frame, text='poly (y = p0 x^2 + p1 x + p2)').grid(row=0, column=0, columnspan=3,  sticky=tk.W)
        tk.Label(data_frame, text='p0').grid(row=1, column=0, sticky=tk.W)
        tk.Label(data_frame, text='p1').grid(row=2, column=0, sticky=tk.W)
        tk.Label(data_frame, text='p2').grid(row=3, column=0, sticky=tk.W)
        E_p0 = tk.Entry(data_frame)
        E_p0.grid(row=1, column=1, sticky=tk.EW)
        E_p1 = tk.Entry(data_frame)
        E_p1.grid(row=2, column=1, sticky=tk.EW)
        E_p2 = tk.Entry(data_frame)
        E_p2.grid(row=3, column=1, sticky=tk.EW)
        tk.Label(data_frame, text='Eg / keV').grid(row=4, column=0, columnspan=3, sticky=tk.W)
        E_joint = gui_things.FSlider(data_frame, decimals=1, label_width=5, default=170.0, from_=165.0, to=270.0, resolution=1.0)
        E_joint.grid(row=5, column=0, columnspan=3)
        tk.Label(data_frame, text='linear (y = l0 x + l1)').grid(row=6, column=0, columnspan=3, sticky=tk.W)
        tk.Label(data_frame, text='l0').grid(row=7, column=0, sticky=tk.W)
        tk.Label(data_frame, text='l1').grid(row=8, column=0, sticky=tk.W)
        E_l0 = tk.Entry(data_frame)
        E_l0.grid(row=7, column=1, sticky=tk.EW)
        E_l1 = tk.Entry(data_frame)
        E_l1.grid(row=8, column=1, sticky=tk.EW)
        f_buttons = tk.Frame(data_frame)
        logo_update_values = tk.PhotoImage(data=gui_things.beye)
        B_update_values = gui_things.Button(f_buttons, image=logo_update_values, hint='Save PT evaluation', hint_destination=self.infobox)
        B_update_values.pack(side=tk.LEFT)
        B_update_values.image = logo_update_values
        logo_delete_values = tk.PhotoImage(data=gui_things.none)
        B_delete_values = gui_things.Button(f_buttons, image=logo_delete_values, hint='Delete PT evaluation', hint_destination=self.infobox)
        B_delete_values.pack(side=tk.LEFT)
        B_delete_values.image = logo_delete_values

        f_buttons.grid(row=9, column=0, columnspan=3, pady=5)
        self.infobox.grid(row=10, column=0, columnspan=3, sticky=tk.W)
        data_frame.grid(row=0, column=0, padx=5, pady=5)
        visual_frame = tk.Frame(parent)
        f = Figure(figsize=(4.5, 3))
        ax_PT = f.add_subplot(111)
        Figur = tk.Frame(visual_frame)
        Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        canvas = FigureCanvasTkAgg(f, master=Figur)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ax_PT.set_xlabel(r'$E$ / keV')
        ax_PT.set_ylabel(r'$P/T$ / 1')
        f.tight_layout()
        canvas.draw()
        visual_frame.grid(row=0, column=1)

        E_p0.delete(0, tk.END)
        E_p1.delete(0, tk.END)
        E_p2.delete(0, tk.END)
        E_l0.delete(0, tk.END)
        E_l1.delete(0, tk.END)
        if PT_values[0] is not None:
            p0, p1, p2 = PT_values[2]
            l0, l1 = PT_values[1]
            E_joint.variable.set(PT_values[0])
            E_p0.insert(tk.END, p0)
            E_p1.insert(tk.END, p1)
            E_p2.insert(tk.END, p2)
            E_l0.insert(tk.END, l0)
            E_l1.insert(tk.END, l1)

            fit_limits, DX = (50,3000), 150
            x_fit = np.linspace(np.min(fit_limits), PT_values[0], DX)
            y_fit = polynomial_function_PT(np.log10(x_fit), *PT_values[2])
            ax_PT.loglog(x_fit, 10**y_fit, linestyle='-', linewidth=1, color='k')
            x_fit = np.linspace(PT_values[0], np.max(fit_limits), DX)
            y_fit = linear_function_PT(np.log10(x_fit), *PT_values[1])
            ax_PT.loglog(x_fit, 10**y_fit, linestyle='-', linewidth=1, color='k')
            ax_PT.loglog(PT_values[0], 10**y_fit[0], marker='x', linestyle='', color='y', markerfacecolor='y', markersize=6, zorder=7)
            ax_PT.set_xlim(40, 3000)
            ax_PT.set_ylim(None, 1)
            f.tight_layout()
            canvas.draw()

        if vtype == 'view':
            E_p0.configure(state='readonly')
            E_p1.configure(state='readonly')
            E_p2.configure(state='readonly')
            E_joint.Scale.configure(state=tk.DISABLED)
            E_l0.configure(state='readonly')
            E_l1.configure(state='readonly')
            B_update_values.configure(state='disabled')
            B_delete_values.configure(state='disabled')

        B_update_values.configure(command = lambda : self.update_values(E_joint, E_p0, E_p1, E_p2, E_l0, E_l1, ax_PT, f, canvas, key, PT_list, PT_button, red, green))
        B_delete_values.configure(command = lambda : self.delete_values(key, PT_list, PT_button, red, green, E_p0, E_p1, E_p2, E_l0, E_l1, ax_PT, f, canvas, parent))

        if take_focus == True:
            parent.focus()

    def delete_values(self, key, PT_list, PT_button, red, green, E_p0, E_p1, E_p2, E_l0, E_l1, ax_PT, f, canvas, parent):
        if messagebox.askyesno(title='Remove PT evaluation', message='\nAre you sure to remove the current PT evaluation for this position?\n', parent=parent):
            PT_values = (None, np.array([0.0, 0.0]), np.array([0.0, 0.0, 0.0]), '')
            PT_list[key] = PT_values
            PT_button.configure(image=red)
            PT_button.image = red
            E_p0.delete(0,tk.END)
            E_p1.delete(0,tk.END)
            E_p2.delete(0,tk.END)
            E_l0.delete(0,tk.END)
            E_l1.delete(0,tk.END)
            nlines = len(ax_PT.lines)
            for _ in range(nlines):
                ax_PT.lines.pop()
            f.tight_layout()
            canvas.draw()
            self.infobox.configure(text='PT evaluation deleted')

    def update_values(self, E_joint, E_p0, E_p1, E_p2, E_l0, E_l1, ax_PT, f, canvas, key, PT_list, PT_button, red, green):
        try:
            Ejoint, Ep0, Ep1, Ep2, El0, El1 = float(E_joint.get()), float(E_p0.get()), float(E_p1.get()), float(E_p2.get()), float(E_l0.get()), float(E_l1.get())
        except:
            pass
        else:
            PT_values = (Ejoint, np.array([El0, El1]), np.array([Ep0, Ep1, Ep2]), f'PT fit manually defined by user:\npolynomial fit (exponents: 2, 1, 0)\np0: {Ep0:.3e}\np1: {Ep1:.3e}\np2: {Ep2:.3e}\n\njunction energy: {Ejoint:.1f} keV\n\nlinear fit (exponents: 1, 0)\nl0: {El0:.3e}\nl1: {El1:.3e}\n')
            PT_list[key] = PT_values
            nlines = len(ax_PT.lines)
            for _ in range(nlines):
                ax_PT.lines.pop()
            fit_limits, DX = (50,3000), 150
            x_fit = np.linspace(np.min(fit_limits), PT_values[0], DX)
            y_fit = polynomial_function_PT(np.log10(x_fit), *PT_values[2])
            ax_PT.loglog(x_fit, 10**y_fit, linestyle='-', linewidth=1, color='k')
            x_fit = np.linspace(PT_values[0], np.max(fit_limits), DX)
            y_fit = linear_function_PT(np.log10(x_fit), *PT_values[1])
            ax_PT.loglog(x_fit, 10**y_fit, linestyle='-', linewidth=1, color='k')
            ax_PT.loglog(PT_values[0], 10**y_fit[0], marker='x', linestyle='', color='y', markerfacecolor='y', markersize=6, zorder=7)
            ax_PT.set_xlim(40, 3000)
            ax_PT.set_ylim(None, 1)
            f.tight_layout()
            canvas.draw()
            PT_button.configure(image=green)
            PT_button.image = green
            self.infobox.configure(text='PT evaluation saved')

def polynomial_function_PT(x, a1, a2, a3):
    return a1*np.power(x,2) + a2*x + a3
    
def linear_function_PT(x, a1, a2):
    return a1*x + a2


class FluxEvaluationWindow:
    def __init__(self, parent, NAA, M):
        parent.title('Flux evaluation - Bare triple monitor')
        parent.resizable(False,False)
        parent.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(parent))
        self.sub_database = self.database_subset(NAA)
        self.fast_database = naaobject._get_fast_data()
        self.flux_spectra_list = []
        self.information_box = tk.Label(parent, text='', anchor=tk.W)
        self.display_window = None
        self.re_zero()
        info_frame = tk.Frame(parent)
        tk.Label(info_frame, text='channel', width=12, anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        channel_CB = ttk.Combobox(info_frame, width=15)
        channel_CB.grid(row=0, column=1, sticky=tk.W)
        channel_CB['values'] = list(naaobject._get_channel_data()[1]['channel_name'])
        ti_Spinbox = tk.Spinbox(info_frame, width=10, from_=0, to=1000000, increment=1)
        self.date = datetime.datetime.today()
        if NAA.irradiation is not None:
            channel_CB.set(NAA.irradiation.channel_name)
            ti_Spinbox.delete(0, tk.END)
            ti_Spinbox.insert(tk.END, f'{NAA.irradiation.irradiation_time:.0f}')
            self.date = NAA.irradiation.datetime

        tk.Frame(info_frame).grid(row=0, column=2, padx=5)
        tk.Label(info_frame, text='pos', width=6).grid(row=0, column=3, sticky=tk.W)
        pos_Spinbox = tk.Spinbox(info_frame, width=4, from_=0, to=10, increment=1)
        pos_Spinbox.grid(row=0, column=4, sticky=tk.W)

        irradiation_date_label = gui_things.Label(info_frame, text=self.date.strftime("%d/%m/%Y %H:%M:%S"), width=25)
        irradiation_date_label.grid(row=0, column=5, sticky=tk.W)
        logo_calendar = tk.PhotoImage(data=gui_things.calendar)
        B_modify_date = gui_things.Button(info_frame, image=logo_calendar, command=lambda : self.change_end_irradiation_date(irradiation_date_label, self.information_box))
        B_modify_date.grid(row=0, column=6, padx=5)
        B_modify_date.image = logo_calendar
        tk.Frame(info_frame).grid(row=0, column=7, padx=5)
        tk.Label(info_frame, text='ti / s', anchor=tk.W).grid(row=0, column=8)
        ti_Spinbox.grid(row=0, column=9)

        tk.Label(info_frame, text='calibration', width=12, anchor=tk.W).grid(row=1, column=0, sticky=tk.W)
        calibration_CB = ttk.Combobox(info_frame, width=25, state='readonly')
        calibration_CB.grid(row=1, column=1, columnspan=4, sticky=tk.EW)
        calibration_CB['values'] = M.calibration_combobox['values']
        if NAA.calibration is not None:
            self.calibration = naaobject.DetectorCalibration(NAA.calibration.name)
            calibration_CB.set(self.calibration.name)
            def_value = self.calibration.reference_calibration.distance
            distances_list = list(self.calibration.kedd_dict.keys()) + [def_value]
        else:
            self.calibration = None
            def_value = None
            distances_list = None

        values = [line[0] for line in self.sub_database]
        modetypes = ['lowest unc.', 'shortest', 'longest', 'earliest', 'latest']
        monitor_frame = tk.Frame(parent)
        tk.Label(monitor_frame, text='emitter', width=13).grid(row=0, column=1)
        tk.Label(monitor_frame, text='monitor', width=8).grid(row=0, column=2)
        tk.Label(monitor_frame, text='Q0 / 1', width=8).grid(row=0, column=3)
        tk.Label(monitor_frame, text='Er / eV', width=8).grid(row=0, column=4)
        tk.Label(monitor_frame, text='mass / g', width=10).grid(row=0, column=5)
        tk.Label(monitor_frame, text='u(mass) / g', width=10).grid(row=0, column=6)
        #tk.Label(monitor_frame, text='COI / 1', width=9).grid(row=0, column=7)
        #tk.Label(monitor_frame, text='u(COI) / 1', width=9).grid(row=0, column=8)
        tk.Label(monitor_frame, text='Gs / 1', width=9).grid(row=0, column=9)
        tk.Label(monitor_frame, text='u(Gs) / 1', width=9).grid(row=0, column=10)
        tk.Label(monitor_frame, text='Ge / 1', width=9).grid(row=0, column=11)
        tk.Label(monitor_frame, text='u(Ge) / 1', width=9).grid(row=0, column=12)
        tk.Label(monitor_frame, text='condition', width=9).grid(row=0, column=13)
        tk.Label(monitor_frame, text='1', width=2).grid(row=1, column=0)
        mon_1 = ttk.Combobox(monitor_frame, values=values, state='readonly', width=13)
        mon_1.grid(row=1, column=1)
        L_mon_1 = tk.Label(monitor_frame, text='')
        L_mon_1.grid(row=1, column=2)
        L_Q0_1 = tk.Label(monitor_frame, text='')
        L_Q0_1.grid(row=1, column=3)
        L_Er_1 = tk.Label(monitor_frame, text='')
        L_Er_1.grid(row=1, column=4)
        try:
            mon_1.set('Au-198 411.8')
            resp = self.check_label('Au-198 411.8')
            L_mon_1.configure(text=resp[0])
            L_Q0_1.configure(text=resp[1])
            L_Er_1.configure(text=resp[2])
        except:
            pass
        mon_1.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>', box=mon_1: self.update_date(box, L_mon_1, L_Q0_1, L_Er_1))
        mass_1 = tk.Spinbox(monitor_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        mass_1.grid(row=1, column=5)
        umass_1 = tk.Spinbox(monitor_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        umass_1.grid(row=1, column=6)
        #COI_1 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        #COI_1.grid(row=1, column=7)
        #COI_1.delete(0, tk.END)
        #COI_1.insert(tk.END, 1.000)
        #UCOI_1 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        #UCOI_1.grid(row=1, column=8)
        GS_1 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        GS_1.grid(row=1, column=9)
        GS_1.delete(0, tk.END)
        GS_1.insert(tk.END, 1.000)
        UGS_1 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        UGS_1.grid(row=1, column=10)
        GE_1 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        GE_1.grid(row=1, column=11)
        GE_1.delete(0, tk.END)
        GE_1.insert(tk.END, 1.000)
        UGE_1 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        UGE_1.grid(row=1, column=12)
        cond_1 = ttk.Combobox(monitor_frame, values=modetypes, state='readonly', width=13)
        cond_1.grid(row=1, column=13)
        cond_1.set(modetypes[0])

        tk.Label(monitor_frame, text='2', width=2).grid(row=2, column=0)
        mon_2 = ttk.Combobox(monitor_frame, values=values, state='readonly', width=13)
        mon_2.grid(row=2, column=1)
        L_mon_2 = tk.Label(monitor_frame, text='')
        L_mon_2.grid(row=2, column=2)
        L_Q0_2 = tk.Label(monitor_frame, text='')
        L_Q0_2.grid(row=2, column=3)
        L_Er_2 = tk.Label(monitor_frame, text='')
        L_Er_2.grid(row=2, column=4)
        try:
            mon_2.set('Nb-97m 743.4')
            resp = self.check_label('Nb-97m 743.4')
            L_mon_2.configure(text=resp[0])
            L_Q0_2.configure(text=resp[1])
            L_Er_2.configure(text=resp[2])
        except:
            pass
        mon_2.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>', box=mon_2: self.update_date(box, L_mon_2, L_Q0_2, L_Er_2))
        mass_2 = tk.Spinbox(monitor_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        mass_2.grid(row=2, column=5)
        umass_2 = tk.Spinbox(monitor_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        umass_2.grid(row=2, column=6)
        #COI_2 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        #COI_2.grid(row=2, column=7)
        #COI_2.delete(0, tk.END)
        #COI_2.insert(tk.END, 1.000)
        #UCOI_2 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        #UCOI_2.grid(row=2, column=8)
        GS_2 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        GS_2.grid(row=2, column=9)
        GS_2.delete(0, tk.END)
        GS_2.insert(tk.END, 1.000)
        UGS_2 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        UGS_2.grid(row=2, column=10)
        GE_2 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        GE_2.grid(row=2, column=11)
        GE_2.delete(0, tk.END)
        GE_2.insert(tk.END, 1.000)
        UGE_2 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        UGE_2.grid(row=2, column=12)
        cond_2 = ttk.Combobox(monitor_frame, values=modetypes, state='readonly', width=13)
        cond_2.grid(row=2, column=13)
        cond_2.set(modetypes[0])

        tk.Label(monitor_frame, text='3', width=2).grid(row=3, column=0)
        mon_3 = ttk.Combobox(monitor_frame, values=values, state='readonly', width=13)
        mon_3.grid(row=3, column=1)
        L_mon_3 = tk.Label(monitor_frame, text='')
        L_mon_3.grid(row=3, column=2)
        L_Q0_3 = tk.Label(monitor_frame, text='')
        L_Q0_3.grid(row=3, column=3)
        L_Er_3 = tk.Label(monitor_frame, text='')
        L_Er_3.grid(row=3, column=4)
        try:
            mon_3.set('Zr-95 756.7')
            resp = self.check_label('Zr-95 756.7')
            L_mon_3.configure(text=resp[0])
            L_Q0_3.configure(text=resp[1])
            L_Er_3.configure(text=resp[2])
        except:
            pass
        mon_3.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>', box=mon_3: self.update_date(box, L_mon_3, L_Q0_3, L_Er_3))
        mass_3 = tk.Spinbox(monitor_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        mass_3.grid(row=3, column=5)
        umass_3 = tk.Spinbox(monitor_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        umass_3.grid(row=3, column=6)
        #COI_3 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        #COI_3.grid(row=3, column=7)
        #COI_3.delete(0, tk.END)
        #COI_3.insert(tk.END, 1.000)
        #UCOI_3 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        #UCOI_3.grid(row=3, column=8)
        GS_3 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        GS_3.grid(row=3, column=9)
        GS_3.delete(0, tk.END)
        GS_3.insert(tk.END, 1.000)
        UGS_3 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        UGS_3.grid(row=3, column=10)
        GE_3 = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        GE_3.grid(row=3, column=11)
        GE_3.delete(0, tk.END)
        GE_3.insert(tk.END, 1.000)
        UGE_3 = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        UGE_3.grid(row=3, column=12)
        cond_3 = ttk.Combobox(monitor_frame, values=modetypes, state='readonly', width=13)
        cond_3.grid(row=3, column=13)
        cond_3.set(modetypes[0])

        tk.Label(monitor_frame, text='triple monitor counting distance').grid(row=4, column=0, columnspan=4, sticky=tk.W)
        triple_monitor_distance = gui_things.FDiscreteSlider(monitor_frame, length=300, label_width=10)
        triple_monitor_distance.grid(row=4, column=4, columnspan=10, sticky=tk.EW)

        tk.Frame(monitor_frame).grid(row=5, column=0, pady=4)

        fast_values = ['']+list(self.fast_database['emitter'])#update

        tk.Label(monitor_frame, text='emitter', width=13).grid(row=6, column=1)
        tk.Label(monitor_frame, text='monitor', width=8).grid(row=6, column=2)
        tk.Label(monitor_frame, text='reaction', width=8).grid(row=6, column=3)
        tk.Label(monitor_frame, text='mass / g', width=10).grid(row=6, column=5)
        tk.Label(monitor_frame, text='u(mass) / g', width=10).grid(row=6, column=6)
        #tk.Label(monitor_frame, text='COI / 1', width=9).grid(row=6, column=7)
        #tk.Label(monitor_frame, text='u(COI) / 1', width=9).grid(row=6, column=8)
        tk.Label(monitor_frame, text='condition', width=9).grid(row=6, column=13)

        tk.Label(monitor_frame, text='F', width=2).grid(row=7, column=0)
        mon_fast = ttk.Combobox(monitor_frame, values=fast_values, state='readonly', width=13)
        mon_fast.grid(row=7, column=1)
        L_mon_fast = tk.Label(monitor_frame, text='')
        L_mon_fast.grid(row=7, column=2)
        L_Reac_fast = tk.Label(monitor_frame, text='')
        L_Reac_fast.grid(row=7, column=3)
        mon_fast.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>', box=mon_fast: self.update_fast(box, L_mon_fast, L_Reac_fast))
        mass_fast = tk.Spinbox(monitor_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        mass_fast.grid(row=7, column=5)
        umass_fast = tk.Spinbox(monitor_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        umass_fast.grid(row=7, column=6)
        #COI_fast = tk.Spinbox(monitor_frame, from_=0.000, to=1.999, width=7, increment=0.001)
        #COI_fast.grid(row=7, column=7)
        #COI_fast.delete(0, tk.END)
        #COI_fast.insert(tk.END, 1.000)
        #UCOI_fast = tk.Spinbox(monitor_frame, from_=0.000, to=1.000, width=7, increment=0.001)
        #UCOI_fast.grid(row=7, column=8)
        cond_fast = ttk.Combobox(monitor_frame, values=modetypes, state='readonly', width=13)
        cond_fast.grid(row=7, column=13)
        cond_fast.set(modetypes[0])

        tk.Label(monitor_frame, text='fast monitor counting distance').grid(row=8, column=0, columnspan=4, sticky=tk.W)
        fast_monitor_distance = gui_things.FDiscreteSlider(monitor_frame, length=300, label_width=10)
        fast_monitor_distance.grid(row=8, column=4, columnspan=10, sticky=tk.EW)

        if distances_list is not None:
            triple_monitor_distance.set_values(distances_list, def_value)
            fast_monitor_distance.set_values(distances_list, def_value)

        splog_frame = tk.Frame(parent)
        spectra_frame = tk.Frame(splog_frame)
        tk.Label(spectra_frame, text='spectra').grid(row=0, column=0, sticky=tk.W)
        ListFrame = tk.Frame(spectra_frame)
        scrollbar = tk.Scrollbar(ListFrame, orient="vertical")
        listbox = tk.Listbox(ListFrame, heigh=8, width=40, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        ListFrame.grid(row=1, column=0, rowspan=4, sticky=tk.NSEW)
        logo_add_spectra = tk.PhotoImage(data=gui_things.plus_spectrum)
        B_add_spectra = gui_things.Button(spectra_frame, image=logo_add_spectra, hint='Add spectra for flux evaluation!', hint_destination=self.information_box, command=lambda : self._add_spectra(parent, NAA.settings_dict['calibs statistical uncertainty limit'], listbox))
        B_add_spectra.grid(row=1, column=4)
        B_add_spectra.image = logo_add_spectra
        logo_peaklist_spectra = tk.PhotoImage(data=gui_things.plist)
        B_peaklist_spectra = gui_things.Button(spectra_frame, image=logo_peaklist_spectra, hint='Show the peaklist of selected spectrum!', hint_destination=self.information_box, command=lambda : self.admire_spectra(listbox, parent))
        B_peaklist_spectra.grid(row=2, column=4)
        B_peaklist_spectra.image = logo_peaklist_spectra
        logo_delete_spectra = tk.PhotoImage(data=gui_things.none)
        B_delete_spectra = gui_things.Button(spectra_frame, image=logo_delete_spectra, hint='Delete the selected spectra!', hint_destination=self.information_box)
        B_delete_spectra.grid(row=3, column=4)
        B_delete_spectra.image = logo_delete_spectra
        F_delete_selector_flux = tk.Frame(spectra_frame)
        self.delete_selector_flux = tk.IntVar(parent)
        R1 = tk.Radiobutton(F_delete_selector_flux, text='selected', anchor=tk.W, value=0, variable=self.delete_selector_flux)
        R1.pack(anchor=tk.W)
        R2 = tk.Radiobutton(F_delete_selector_flux, text='all', anchor=tk.W, value=1, variable=self.delete_selector_flux)
        R2.pack(anchor=tk.W)
        self.delete_selector_flux.set(0)
        F_delete_selector_flux.grid(row=3, column=5, padx=3)
        B_delete_spectra.configure(command=lambda : self.delete_spectra(parent, listbox))

        log_frame = tk.Frame(splog_frame)
        tk.Label(log_frame, text='log', anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        stext = gui_things.ScrollableText(log_frame, width=50)
        stext.grid(row=1, column=0, sticky=tk.NS)

        spectra_frame.pack(side=tk.LEFT, anchor=tk.NW)
        log_frame.pack(side=tk.RIGHT, anchor=tk.NE, fill=tk.Y, expand=True)

        buttons_frame = tk.Frame(parent)
        logo_start_computation = tk.PhotoImage(data=gui_things.manygears)
        B_start_computation = gui_things.Button(buttons_frame, image=logo_start_computation, hint='Compute flux parameters!', hint_destination=self.information_box, command=lambda : self.compute_fluxes(channel_CB, ti_Spinbox, mon_1, mass_1, umass_1, GS_1,UGS_1, GE_1, UGE_1, cond_1, mon_2, mass_2, umass_2, GS_2, UGS_2, GE_2, UGE_2, cond_2, mon_3, mass_3, umass_3, GS_3, UGS_3, GE_3, UGE_3, cond_3, mon_fast, mass_fast, umass_fast, cond_fast, triple_monitor_distance, fast_monitor_distance, stext, NAA.settings_dict['energy tolerance']))
        B_start_computation.pack(side=tk.LEFT)
        B_start_computation.image = logo_start_computation
        logo_save_values = tk.PhotoImage(data=gui_things.beye)
        B_save_values = gui_things.Button(buttons_frame, image=logo_save_values, hint='Confirm obtained values!', hint_destination=self.information_box, command=lambda : self.save_fluxes(channel_CB, pos_Spinbox))
        B_save_values.pack(side=tk.LEFT)
        B_save_values.image = logo_save_values

        info_frame.pack(anchor=tk.NW, padx=5, pady=5)
        monitor_frame.pack(anchor=tk.NW, padx=5, pady=5)
        splog_frame.pack(anchor=tk.NW, padx=5, pady=5, fill=tk.X)
        buttons_frame.pack(anchor=tk.NW, padx=5, pady=5)
        self.information_box.pack(anchor=tk.NW, padx=5)

        calibration_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>' : self.calibration_selection(calibration_CB, triple_monitor_distance, fast_monitor_distance))

    def on_closing(self, parent, title='Quit Flux evaluation window', message='Save your elaboration before quitting.\n\nDo you want to quit the window?'):
        if messagebox.askokcancel(title, message, parent=parent):
            parent.destroy()

    def _add_spectra(self, parent, tol, listbox):
        #add spectra for flux measurement
        if self.display_window is not None:
            self.display_window.destroy()
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))#,('HyperLab ASC file','*.asc'),('CHN spectrum file','*.chn'))
        limit_s = tol
        try:
            output = tuple(askopenfilenames(parent=parent, title='Open spectra for flux measurement',filetypes=filetypes))
        except TypeError:
            output = ()
        for filename in output:
            if filename != '' and filename != ():
                peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=True)
                efficiency = None#NAA.calibration
                if result == True:
                    Spectrum = naaobject.SpectrumAnalysis(identity=f'flux_spectrum', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=output, source=source, efficiency=efficiency)
                    self.flux_spectra_list.append(Spectrum)
                else:
                    self.information_box.configure(text='failed to import spectrum')
        listbox.delete(0, tk.END)
        for spect in self.flux_spectra_list:
            listbox.insert(tk.END, spect.filename())

    def admire_spectra(self, listbox, parent):
        #display the peaklist for the selected spectrum
        if len(self.flux_spectra_list) > 0:
            idx = listbox.curselection()
            try:
                if idx[0] < 0:
                    idx = 0
                else:
                    idx = idx[0]
            except:
                idx = 0
            if self.display_window is not None:
                self.display_window.destroy()
            self.display_window = tk.Toplevel(parent)
            nline = 15
            local_peak_list = nest_list(self.flux_spectra_list[idx].peak_list, nline)
            local_suspected = nest_list(self.flux_spectra_list[idx].suspected, nline)
            PeaklistWindow(self.display_window, self.flux_spectra_list[idx], local_peak_list, local_suspected, nline, background=None)#background)#None for the moment

    def delete_spectra(self, parent, listbox):
        if self.display_window is not None:
            self.display_window.destroy()
            self.display_window = None
        if self.delete_selector_flux.get() == 0:
            idx = listbox.curselection()
            try:
                idx = idx[0]
            except:
                idx = -1
            if idx >= 0:# and len(self.flux_spectra_list) > 0:
                filename = listbox.get(idx)
                if messagebox.askyesno(title='Remove spectrum', message=f'\nAre you sure to remove spectrum: {filename} from selection?\n', parent=parent):
                    self.flux_spectra_list.pop(idx)
                    listbox.delete(0, tk.END)
                    for spect in self.flux_spectra_list:
                        listbox.insert(tk.END, spect.filename())
                    self.information_box.configure(text=f'{filename} spectrum removed')
            else:
                self.information_box.configure(text='no spectrum selected')
        else:
            lenght = len(self.flux_spectra_list)
            if lenght > 0:
                if messagebox.askyesno(title='Remove spectrum', message='\nAre you sure to remove all spectra from selection?\n', parent=parent):
                    for _ in range(lenght):
                        self.flux_spectra_list.pop()
                    listbox.delete(0, tk.END)
                    for spect in self.flux_spectra_list:
                        listbox.insert(tk.END, spect.filename())
                    self.information_box.configure(text=f'{lenght} spectra removed')

    def change_end_irradiation_date(self, irradiation_date_label, hints):

        def _confirm_change(DaySpin,MonthSpin,YearSpin,HourSpin,MinuteSpin,SecondSpin,irradiation_date_label,TempTL,hints):
            try:
                day, month, year, hour, minute, second = int(DaySpin.get()), int(MonthSpin.get()), int(YearSpin.get()), int(HourSpin.get()), int(MinuteSpin.get()), int(SecondSpin.get())
            except:
                hints.configure(text='invalid end of irradiation date')
            else:
                try:
                    datetime.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    hints.configure(text='invalid end of irradiation date')
                else:
                    self.date = datetime.datetime(year, month, day, hour, minute, second)
                    irradiation_date_label.configure(text=self.date.strftime("%d/%m/%Y %H:%M:%S"))
                    hints.configure(text='date updated')
                    TempTL.destroy()

        cwidth, xpos, ypos = irradiation_date_label.winfo_width(), irradiation_date_label.winfo_rootx(), irradiation_date_label.winfo_rooty()
        TempTL = tk.Toplevel(irradiation_date_label)
        TempTL.resizable(False, False)
        if sys.platform != 'darwin':
            TempTL.overrideredirect(True)
        day, month, year, hour, minute, second = self.date.day, self.date.month, self.date.year, self.date.hour, self.date.minute, self.date.second
        TempTLF = tk.Frame(TempTL, background='#A3A3A3', bd=3)
        DaySpin = tk.Spinbox(TempTLF, from_=1, to=31, width=3, increment=1)
        DaySpin.pack(side=tk.LEFT)
        DaySpin.delete(0, tk.END)
        DaySpin.insert(tk.END, day)
        MonthSpin = tk.Spinbox(TempTLF, from_=1, to=12, width=3, increment=1)
        MonthSpin.pack(side=tk.LEFT)
        MonthSpin.delete(0, tk.END)
        MonthSpin.insert(tk.END, month)
        YearSpin = tk.Spinbox(TempTLF, from_=1000, to=2999, width=5, increment=1)
        YearSpin.pack(side=tk.LEFT)
        YearSpin.delete(0, tk.END)
        YearSpin.insert(tk.END, year)
        tk.Frame(TempTLF, background='#A3A3A3').pack(side=tk.LEFT, padx=5)
        HourSpin = tk.Spinbox(TempTLF, from_=0, to=23, width=3, increment=1)
        HourSpin.pack(side=tk.LEFT)
        HourSpin.delete(0, tk.END)
        HourSpin.insert(tk.END, hour)
        MinuteSpin = tk.Spinbox(TempTLF, from_=0, to=59, width=3, increment=1)
        MinuteSpin.pack(side=tk.LEFT)
        MinuteSpin.delete(0, tk.END)
        MinuteSpin.insert(tk.END, minute)
        SecondSpin = tk.Spinbox(TempTLF, from_=0, to=59, width=3, increment=1)
        SecondSpin.pack(side=tk.LEFT)
        SecondSpin.delete(0, tk.END)
        SecondSpin.insert(tk.END, second)
        logo_new = tk.PhotoImage(data=gui_things.smallarrow)
        B_update_date = gui_things.Button(TempTLF, image=logo_new, hint='confirm new date', hint_xoffset=5, hint_destination=hints, command=lambda : _confirm_change(DaySpin,MonthSpin,YearSpin,HourSpin,MinuteSpin,SecondSpin,irradiation_date_label,TempTL,hints))
        B_update_date.image = logo_new
        B_update_date.pack(side=tk.LEFT)
        TempTLF.pack(fill=tk.X, expand=True)

        TempTL.update()
        width, height = TempTL.winfo_width(), TempTL.winfo_height()
        TempTL.geometry(f'{width}x{height}+{xpos}+{ypos}')

        TempTLF.focus()
        if sys.platform != 'darwin':
            TempTLF.bind('<FocusOut>', lambda e='<FocusOut>': TempTL.destroy())

    def calibration_selection(self, calibration_CB, triple_monitor_distance, fast_monitor_distance):
        self.calibration = naaobject.DetectorCalibration(calibration_CB.get())
        def_value = self.calibration.reference_calibration.distance
        distances_list = list(self.calibration.kedd_dict.keys()) + [def_value]
        triple_monitor_distance.set_values(distances_list, def_value)
        fast_monitor_distance.set_values(distances_list, def_value)
        self.re_zero()

    def re_zero(self):
        self.allow_save = False
        self.result_f, self.result_f_unc = 0.0, 0.0
        self.result_a, self.result_a_unc = 0.0, 0.0
        self.result_thermal, self.result_thermal_unc = 0.0, 0.0
        self.result_epithermal, self.result_epithermal_unc = 0.0, 0.0
        self.result_fast, self.result_fast_unc = 0.0, 0.0
        #self.result_beta, self.result_beta_unc = 0.0, 0.0

    def compute_fluxes(self, CH_name, ti_Spinbox, mon_1, mass_1, umass_1, GS_1, UGS_1, GE_1, UGE_1, cond_1, mon_2, mass_2, umass_2, GS_2, UGS_2, GE_2, UGE_2, cond_2, mon_3, mass_3, umass_3, GS_3, UGS_3, GE_3, UGE_3, cond_3, fast_1, mass_fast, umass_fast, cond_fast, triple_monitor_distance, fast_monitor_distance, stext, tolerance):
        #prerequisites
        self.re_zero()
        ttext = []
        start_elaboration = True
        try:
            ti_value = float(ti_Spinbox.get())
        except:
            ti_value = 0.0
        try:
            mass_1 = float(mass_1.get())
        except:
            mass_1 = 0.0
        try:
            umass_1 = float(umass_1.get())
        except:
            umass_1 = 0.0
        try:
            GS_1 = float(GS_1.get())
        except:
            GS_1 = 1.0
        try:
            UGS_1 = float(UGS_1.get())
        except:
            UGS_1 = 0.0
        try:
            GE_1 = float(GE_1.get())
        except:
            GE_1 = 1.0
        try:
            UGE_1 = float(UGE_1.get())
        except:
            UGE_1 = 0.0
        try:
            mass_2 = float(mass_2.get())
        except:
            mass_2 = 0.0
        try:
            umass_2 = float(umass_2.get())
        except:
            umass_2 = 0.0
        try:
            GS_2 = float(GS_2.get())
        except:
            GS_2 = 1.0
        try:
            UGS_2 = float(UGS_2.get())
        except:
            UGS_2 = 0.0
        try:
            GE_2 = float(GE_2.get())
        except:
            GE_2 = 1.0
        try:
            UGE_2 = float(UGE_2.get())
        except:
            UGE_2 = 0.0
        try:
            mass_3 = float(mass_3.get())
        except:
            mass_3 = 0.0
        try:
            umass_3 = float(umass_3.get())
        except:
            umass_3 = 0.0
        try:
            GS_3 = float(GS_3.get())
        except:
            GS_3 = 1.0
        try:
            UGS_3 = float(UGS_3.get())
        except:
            UGS_3 = 0.0
        try:
            GE_3 = float(GE_3.get())
        except:
            GE_3 = 1.0
        try:
            UGE_3 = float(UGE_3.get())
        except:
            UGE_3 = 0.0
        try:
            mass_fast = float(mass_fast.get())
        except:
            mass_fast = 0.0
        try:
            umass_fast = float(umass_fast.get())
        except:
            umass_fast = 0.0
        #channel name is not none
        if CH_name.get().replace(' ','') == '':
            ttext.append('- channel name is not valid')
            start_elaboration = False
        if self.calibration is None:
            ttext.append('- calibration is not selected')
            start_elaboration = False
        if ti_value <= 0.0:
            ttext.append('- irradiation time should be > 0')
            start_elaboration = False
        if len(self.flux_spectra_list) == 0:
            ttext.append('- no monitor spectra are selected')
            start_elaboration = False
        if mass_1 <= 0.0:
            ttext.append('- mass of monitor 1 should be > 0')
            start_elaboration = False
        if mass_2 <= 0.0:
            ttext.append('- mass of monitor 2 should be > 0')
            start_elaboration = False
        if mass_3 <= 0.0:
            ttext.append('- mass of monitor 3 should be > 0')
            start_elaboration = False
        if start_elaboration == True:
            triple_position = triple_monitor_distance.get()
            fast_position = fast_monitor_distance.get()
            correct_harvesting = True

            COND_1, COND_2, COND_3 = cond_1.get(), cond_2.get(), cond_3.get()
            COND_fast = cond_fast.get()
            cond_descriptors = {'lowest unc.': 'lowest statistical uncertainty', 'shortest': 'shortest live time', 'longest': 'longest live time', 'earliest': 'earliest acquisition', 'latest': 'latest acquisition'}

            monitor_1, correct_harvesting = self.harvest_monitor(mon_1, correct_harvesting, ti_value, mass_1, umass_1, GS_1, UGS_1, GE_1, UGE_1, tolerance, triple_position, COND_1)
            #evaluate coi_1
            monitor_2, correct_harvesting = self.harvest_monitor(mon_2, correct_harvesting, ti_value, mass_2, umass_2, GS_2, UGS_2, GE_2, UGE_2, tolerance, triple_position, COND_2)
            #evaluate coi_2
            monitor_3, correct_harvesting = self.harvest_monitor(mon_3, correct_harvesting, ti_value, mass_3, umass_3, GS_3, UGS_3, GE_3, UGE_3, tolerance, triple_position, COND_3)
            #evaluate coi_3
            monitor_fast = self.harvest_fast(fast_1, ti_value, mass_fast, umass_fast, tolerance, COND_fast)

            if monitor_1 is None:
                ttext.append(f'Invadid data are entered\n- {mon_1.get()} not found in any of the selected spectra')
            elif monitor_2 is None:
                ttext.append(f'Invadid data are entered\n- {mon_2.get()} not found in any of the selected spectra')
            elif monitor_3 is None:
                ttext.append(f'Invadid data are entered\n- {mon_3.get()} not found in any of the selected spectra')

            elif monitor_1[5] == monitor_2[5] and monitor_1[7] == monitor_2[7]:
                ttext.append(f'Invadid data are entered\n- Same target isotope selected for emitters {monitor_1[0]} and {monitor_2[0]}')
            elif monitor_1[5] == monitor_3[5] and monitor_1[7] == monitor_3[7]:
                ttext.append(f'Invadid data are entered\n- Same target isotope selected for emitters {monitor_1[0]} and {monitor_3[0]}')
            elif monitor_2[5] == monitor_3[5] and monitor_2[7] == monitor_3[7]:
                ttext.append(f'Invadid data are entered\n- Same target isotope selected for emitters {monitor_2[0]} and {monitor_3[0]}')
            elif correct_harvesting == True:
                ttext.append(f'Selected monitors\nmonitor 1: {monitor_1[0]} keV emission (found on spectrum {monitor_1[-1]} based on {cond_descriptors[COND_1]})\nmonitor 2: {monitor_2[0]} keV emission (found on spectrum {monitor_2[-1]} based on {cond_descriptors[COND_2]})\nmonitor 3: {monitor_3[0]} keV emission (found on spectrum {monitor_3[-1]} based on {cond_descriptors[COND_3]})\n')

                ttext = self.perform_flux_evalaution(monitor_1, monitor_2, monitor_3, monitor_fast, triple_position, fast_position, ttext)

            stext._update('\n'.join(ttext))
        else:
            ttext = ['Issues were identified while checking for consistency of the input data; error messages are reported\n'] + ttext
            stext._update('\n'.join(ttext))

    def perform_flux_evalaution(self, monitor_1, monitor_2, monitor_3, monitor_fast, triple_position, fast_position, ttext):

        def alpha_function(x):
            """Function to solve for alpha"""
            return ((1 / ((_Asp_1*_k0_2*_e2)/(_Asp_2*_k0_1*_e1) - 1)) - (1 / ((_Asp_1*_k0_3*_e3)/(_Asp_3*_k0_1*_e1) - 1)))*_Ge1*((_q01-0.429)/_Er1**x + 0.429/((2*x + 1)*0.55**x)) - (1 / (1 - (_Asp_2*_k0_1*_e1)/(_Asp_1*_k0_2*_e2)))*_Ge2*((_q02-0.429)/_Er2**x + 0.429/((2*x + 1)*0.55**x)) + (1 / (1 - (_Asp_3*_k0_1*_e1)/(_Asp_1*_k0_3*_e3)))*_Ge3*((_q03-0.429)/_Er3**x + 0.429/((2*x + 1)*0.55**x))

        def e_polynomial_model(aparameters, bparameters, energy):
            """6-terms polynomial efficiency fit"""
            energy = energy / 1000
            return np.exp(aparameters[0]*energy + aparameters[1] + aparameters[2]*np.power(energy, -1) + aparameters[3]*np.power(energy, -2) + aparameters[4]*np.power(energy, -3) + aparameters[5]*np.power(energy, -4)) / np.exp(bparameters[0]*energy + bparameters[1] + bparameters[2]*np.power(energy, -1) + bparameters[3]*np.power(energy, -2) + bparameters[4]*np.power(energy, -3) + bparameters[5]*np.power(energy, -4))

        def func_f(Asp1, k01, e1, Ge1, q01, Er1, Asp2, k02, e2, Ge2, q02, Er2, Gs, a):
            """Function that returns f"""
            return ((k01*e1)/(k02*e2)*Ge1*((q01-0.429)/Er1**a + 0.429/((2*a + 1)*0.55**a)) - Asp1/Asp2*Ge2*((q02-0.429)/Er2**a + 0.429/((2*a + 1)*0.55**a))) / (Gs*(Asp1/Asp2 - (k01*e1)/(k02*e2)))

        def func_thermal_f(Asp1, e1, Ge1, q01, Er1, Gs, f, a, MolarM, Theta, Gamma, Sg0):
            """Function that returns thermal flux"""
            NA = 6.02214086E23
            return (Asp1*MolarM)/(Theta*Gamma*e1*NA*Sg0*(Gs+Ge1/f*((q01-0.429)/Er1**a + 0.429/((2*a + 1)*0.55**a))))

        def func_epithermal_f(Asp1, e1, Ge1, q01, Er1, Gs, f, a, MolarM, Theta, Gamma, Sg0):
            """Function that returns thermal flux"""
            NA = 6.02214086E23
            return (Asp1*MolarM)/(Theta*Gamma*e1*NA*Sg0*(Gs*f+Ge1*((q01-0.429)/Er1**a + 0.429/((2*a + 1)*0.55**a))))

        def func_fast_f(Asp1, e1, MolarM, Theta, Gamma, Sgf):
            """Function that returns thermal flux"""
            NA = 6.02214086E23
            return (Asp1*MolarM)/(NA*Theta*Gamma*e1*Sgf)

        alpha, ualpha, f, uf, F_th, uF_th, F_epi, uF_epi, F_fast, uF_fast, beta, ubeta = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        self.allow_save = True

        try:
            Asp_1, uAsp_1 = self.get_specific(monitor_1)
            Asp_2, uAsp_2 = self.get_specific(monitor_2)
            Asp_3, uAsp_3 = self.get_specific(monitor_3)
            k0_1, uk0_1, k0_2, uk0_2, k0_3, uk0_3 = monitor_1[3], self.uncertainty_job(monitor_1[3], monitor_1[4]), monitor_2[3], self.uncertainty_job(monitor_2[3], monitor_2[4]), monitor_3[3], self.uncertainty_job(monitor_3[3], monitor_3[4])
            q01, uq01, q02, uq02, q03, uq03 = monitor_1[5], self.uncertainty_job(monitor_1[5], monitor_1[6], 0.2), monitor_2[5], self.uncertainty_job(monitor_2[5], monitor_2[6], 0.2), monitor_3[5], self.uncertainty_job(monitor_3[5], monitor_3[6], 0.2)
            Er1, uEr1, Er2, uEr2, Er3, uEr3 = monitor_1[7], self.uncertainty_job(monitor_1[7], monitor_1[8], 0.5), monitor_2[7], self.uncertainty_job(monitor_2[7], monitor_2[8], 0.5), monitor_3[7], self.uncertainty_job(monitor_3[7], monitor_3[8], 0.5)
            Ge1, uGe1, Ge2, uGe2, Ge3, uGe3 = monitor_1[25], monitor_1[26], monitor_2[25], monitor_2[26], monitor_3[25], monitor_3[26]
            e1, e2, e3 = self.calibration.evaluate_efficiency(np.array([monitor_1[2], monitor_2[2], monitor_3[2]]), triple_position)
            #print('es',e1, e2, e3)

            _Asp_1, _Asp_2, _Asp_3, _k0_1, _k0_2, _k0_3, _e1, _e2, _e3, _q01, _q02, _q03, _Er1, _Er2, _Er3, _Ge1, _Ge2, _Ge3 = Asp_1, Asp_2, Asp_3, k0_1, k0_2, k0_3, e1, e2, e3, q01, q02, q03, Er1, Er2, Er3, Ge1, Ge2, Ge3
            sol = fsolve(alpha_function, 0)
            alpha = float(sol)
            a1, a2, a3, a4, a5, a6 = self.calibration.reference_calibration.efficiency_parameters
            ua1, ua2, ua3, ua4, ua5, ua6 = np.sqrt(np.diag(self.calibration.reference_calibration.efficiency_cov))

            temp_kedd_exp, temp_kedd_par, temp_kedd_cov = self.calibration.kedd_dict.get(triple_position, ([1, 0, -1, -2, -3, -4], np.zeros(6), np.zeros((6,6))))
            kedd_exp = [1, 0, -1, -2, -3, -4]
            kedd_par = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            kedd_cov = np.zeros((6,6))
            for idx, value, line in zip(temp_kedd_exp,temp_kedd_par, temp_kedd_cov):
                kedd_par[kedd_exp.index(idx)] = value
                for ddx, linevalue in zip(temp_kedd_exp, line):
                    kedd_cov[kedd_exp.index(idx),kedd_exp.index(ddx)] = linevalue

            b1, b2, b3, b4, b5, b6 = kedd_par
            ub1, ub2, ub3, ub4, ub5, ub6 = np.sqrt(np.diag(kedd_cov))

            _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6 = a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6

            original_values = [Asp_1, Asp_2, Asp_3, k0_1, k0_2, k0_3, q01, q02, q03, Er1, Er2, Er3, Ge1, Ge2, Ge3, a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6]
            comput_values = [_Asp_1, _Asp_2, _Asp_3, _k0_1, _k0_2, _k0_3, _q01, _q02, _q03, _Er1, _Er2, _Er3, _Ge1, _Ge2, _Ge3, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6]
            uncertainties = [uAsp_1, uAsp_2, uAsp_3, uk0_1, uk0_2, uk0_3, uq01, uq02, uq03, uEr1, uEr2, uEr3, uGe1, uGe2, uGe3, ua1, ua2, ua3, ua4, ua5, ua6, ub1, ub2, ub3, ub4, ub5, ub6]
            res = []
            for idx in range(len(original_values)):
                comput_values[idx] = original_values[idx] + uncertainties[idx]
                _Asp_1, _Asp_2, _Asp_3, _k0_1, _k0_2, _k0_3, _q01, _q02, _q03, _Er1, _Er2, _Er3, _Ge1, _Ge2, _Ge3, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6 = comput_values
                _e1, _e2, _e3 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],[_b1, _b2, _b3, _b4, _b5, _b6], monitor_1[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],[_b1, _b2, _b3, _b4, _b5, _b6], monitor_2[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],[_b1, _b2, _b3, _b4, _b5, _b6], monitor_3[2])
                sol = fsolve(alpha_function, 0)
                solplus = (float(sol) - alpha) / (uncertainties[idx] + 1E-12)
                comput_values[idx] = original_values[idx] - uncertainties[idx]
                _Asp_1, _Asp_2, _Asp_3, _k0_1, _k0_2, _k0_3, _q01, _q02, _q03, _Er1, _Er2, _Er3, _Ge1, _Ge2, _Ge3, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6 = comput_values
                _e1, _e2, _e3 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],[_b1, _b2, _b3, _b4, _b5, _b6], monitor_1[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],[_b1, _b2, _b3, _b4, _b5, _b6], monitor_2[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],[_b1, _b2, _b3, _b4, _b5, _b6], monitor_3[2])
                sol = fsolve(alpha_function, 0)
                solminus = (float(sol) - alpha) / -(uncertainties[idx] + 1E-12)
                comput_values[idx] = original_values[idx]
                res.append((solplus+solminus)/2)
            res = np.array(res)
            uncertainties = np.array(uncertainties)
            uncertainties = np.power(uncertainties, 2)
            unc_cov_matrix = np.diag(uncertainties)
            unc_cov_matrix[-12:-6,-12:-6] = self.calibration.reference_calibration.efficiency_cov
            unc_cov_matrix[-6:,-6:] = kedd_cov
            ualpha = np.sqrt((res.T@unc_cov_matrix) @ res)
            limit = 0.15
            warning1, warning2 = '', ''
            if not -limit < alpha < limit:
                warning1 = f'warning: calculated α value is questionable since lies outside the range +-{limit}\n'
            if np.abs(ualpha / alpha) > 0.8:
                warning2 = 'warning: excessive evaluated uncertainty for α\n'
            indexes = []
            for row in range(len(unc_cov_matrix)):
                count = 0
                for colu in range(len(unc_cov_matrix)):
                    count += res[row] * res[colu] * unc_cov_matrix[row, colu]
                indexes.append(count)
            indexes = np.array(indexes[:-12]+[np.sum(indexes[-12:])])
            description = ['Specific count rate of monitor 1', 'Specific count rate of monitor 2', 'Specific count rate of monitor 3', 'k0 factor of monitor 1', 'k0 factor of monitor 2', 'k0 factor of monitor 3', 'Resonance integral on thermal cross section value of monitor 1', 'Resonance integral on thermal cross section value of monitor 2','Resonance integral on thermal cross section value of monitor 3', 'Effective resonance value of monitor 1', 'Effective resonance value of monitor 2', 'Effective resonance value of monitor 3', 'Epithermal self shielding value of monitor 1', 'Epithermal self shielding value of monitor 2', 'Epithermal self shielding value of monitor 3', 'Efficiency evaluation']
            indexes = [(idx_value / indexes.sum(), tag) for idx_value, tag in zip(indexes, description)]
            indexes.sort(key=lambda x: x[0], reverse=True)
            text_major_contributors = [f'{format(100*line[0],".1f").rjust(5, " ")} % - {line[1]}' for line in indexes[:5]]
            ttext.append(f'α value found by iteratively solving the α implicit equation\n{"".ljust(4)}{"value".ljust(10)}{"u (k=1)".ljust(9)}rel. u\n{"α".ljust(4)}{format(alpha,".4f").ljust(10)}{format(ualpha,".4f").ljust(9)}({np.abs(100 * ualpha / alpha):.1f} %)\n{warning1}{warning2}\nList of 5 major contributors to the combined uncertainty of α evaluation:\n'+'\n'.join(text_major_contributors)+'\n')

            f = func_f(Asp_2, k0_2, e2, Ge2, q02, Er2, Asp_3, k0_3, e3, Ge3, q03, Er3, monitor_2[23], alpha)
            original_values = [Asp_2, k0_2, Ge2, q02, Er2, Asp_3, k0_3, Ge3, q03, Er3, monitor_2[23], alpha, a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6]
            comput_values = [Asp_2, k0_2, Ge2, q02, Er2, Asp_3, k0_3, Ge3, q03, Er3, monitor_2[23], alpha, a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6]
            uncertainties = [uAsp_2, uk0_2, uGe2, uq02, uEr2, uAsp_3, uk0_3, uGe3, uq03, uEr3, monitor_2[24], ualpha, ua1, ua2, ua3, ua4, ua5, ua6, ub1, ub2, ub3, ub4, ub5, ub6]
            res = []
            for idx in range(len(original_values)):
                comput_values[idx] = original_values[idx] + uncertainties[idx]
                _Asp_1, _k0_1, _Ge1, _q01, _Er1, _Asp_2, _k0_2, _Ge2, _q02, _Er2, _Gs, _alpha, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6 = comput_values
                _e1, _e2 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6], [_b1, _b2, _b3, _b4, _b5, _b6], monitor_2[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6], [_b1, _b2, _b3, _b4, _b5, _b6], monitor_3[2])
                solplus = (func_f(_Asp_1, _k0_1, _e1, _Ge1, _q01, _Er1, _Asp_2, _k0_2, _e2, _Ge2, _q02, _Er2, _Gs, _alpha) - f) / (uncertainties[idx] + 1E-12)
                comput_values[idx] = original_values[idx] - uncertainties[idx]
                _Asp_1, _k0_1, _Ge1, _q01, _Er1, _Asp_2, _k0_2, _Ge2, _q02, _Er2, _Gs, _alpha, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6 = comput_values
                _e1, _e2 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6], [_b1, _b2, _b3, _b4, _b5, _b6], monitor_2[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6], [_b1, _b2, _b3, _b4, _b5, _b6], monitor_3[2])
                solminus = (func_f(_Asp_1, _k0_1, _e1, _Ge1, _q01, _Er1, _Asp_2, _k0_2, _e2, _Ge2, _q02, _Er2, _Gs, _alpha) - f) / -(uncertainties[idx] + 1E-12)
                comput_values[idx] = original_values[idx]
                res.append((solplus+solminus)/2)
            res = np.array(res)
            uncertainties = np.array(uncertainties)
            uncertainties = np.power(uncertainties, 2)
            unc_cov_matrix = np.diag(uncertainties)
            unc_cov_matrix[-12:-6,-12:-6] = self.calibration.reference_calibration.efficiency_cov
            unc_cov_matrix[-6:,-6:] = kedd_cov
            uf = np.sqrt((res.T@unc_cov_matrix) @ res)
            warning1, warning2 = '', ''
            if f <= 0:
                warning1 = f'warning: calculated f value is problematic since <= 0\n'
                self.allow_save = False
            if np.abs(uf / f) > 0.8:
                warning2 = 'warning: excessive evaluated uncertainty for f\n'
            indexes = []
            for row in range(len(unc_cov_matrix)):
                count = 0
                for colu in range(len(unc_cov_matrix)):
                    count += res[row] * res[colu] * unc_cov_matrix[row, colu]
                indexes.append(count)
            indexes = np.array(indexes[:-12]+[np.sum(indexes[-12:])])
            description = ['Specific count rate of monitor 2', 'k0 factor of monitor 2', 'Epithermal self shielding value of monitor 2', 'Resonance integral on thermal cross section value of monitor 2', 'Effective resonance value of monitor 2', 'Specific count rate of monitor 3', 'k0 factor of monitor 3', 'Epithermal self shielding value of monitor 3', 'Resonance integral on thermal cross section value of monitor 3', 'Effective resonance value of monitor 3', 'Thermal self shielding value', 'α', 'Efficiency evaluation']
            indexes = [(idx_value / indexes.sum(), tag) for idx_value, tag in zip(indexes, description)]
            indexes.sort(key=lambda x: x[0], reverse=True)
            text_major_contributors = [f'{format(100*line[0],".1f").rjust(5, " ")} % - {line[1]}' for line in indexes[:5]]
            ttext.append(f'f value evaluated through values related to monitors 2 and 3\n{"".ljust(4)}{"value".ljust(8)}{"u (k=1)".ljust(8)}rel. u\n{"f".ljust(4)}{format(f,".2f").ljust(8)}{format(uf,".2f").ljust(8)}({np.abs(100 * uf / f):.1f} %)\n{warning1}{warning2}\nList of 5 major contributors to the combined uncertainty of f evaluation:\n'+'\n'.join(text_major_contributors)+'\n')
            mon_Au = None
            for i in (monitor_1, monitor_2, monitor_3):
                if i[0] == 'Au-198 411.8':
                    # 9.87E-27 uncertainty of s0_Au
                    mon_Au = monitor_1 + [196.966569, 1, 0.9562, 9.87E-23, 9.87E-27]
                    break
            if mon_Au is not None:
                Asp1, uAsp1 = self.get_specific(mon_Au)
                q01, uq01 = mon_Au[5], self.uncertainty_job(mon_Au[5], mon_Au[6], 0.2)
                Er1, uEr1 = mon_Au[7], self.uncertainty_job(mon_Au[7], mon_Au[8], 0.5)
                Ge1, uGe1, Gs, uGs = mon_Au[25], mon_Au[26], mon_Au[23], mon_Au[24]
                e1 = self.calibration.evaluate_efficiency(np.array([mon_Au[2]]), triple_position)
                F_th = float(func_thermal_f(Asp1, e1, Ge1, q01, Er1, Gs, f, alpha, mon_Au[28], mon_Au[29], mon_Au[30], mon_Au[31]))
                F_epi = float(func_epithermal_f(Asp1, e1, Ge1, q01, Er1, Gs, f, alpha, mon_Au[28], mon_Au[29], mon_Au[30], mon_Au[31]))
                original_values = [Asp1, Ge1, q01, Er1, Gs, f, alpha, a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6, mon_Au[31]]
                comput_values = [Asp1, Ge1, q01, Er1, Gs, f, alpha, a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6, mon_Au[31]]
                uncertainties = [uAsp1, uGe1, uq01, uEr1, uGs, uf, ualpha, ua1, ua2, ua3, ua4, ua5, ua6, ub1, ub2, ub3, ub4, ub5, ub6, mon_Au[32]]
                res = []
                resepi = []
                for idx in range(len(original_values)):
                    comput_values[idx] = original_values[idx] + uncertainties[idx]
                    _Asp1, _Ge1, _q01, _Er1, _Gs, _f, _alpha, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6, _Sg0 = comput_values
                    _e1 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6], [_b1, _b2, _b3, _b4, _b5, _b6], mon_Au[2])
                    solplus = (func_thermal_f(_Asp1, _e1, _Ge1, _q01, _Er1, _Gs, _f, _alpha, mon_Au[28], mon_Au[29], mon_Au[30], _Sg0) - F_th) / (uncertainties[idx] + 1E-12)
                    solplusepi = (func_epithermal_f(_Asp1, _e1, _Ge1, _q01, _Er1, _Gs, _f, _alpha, mon_Au[28], mon_Au[29], mon_Au[30], _Sg0) - F_th) / (uncertainties[idx] + 1E-12)
                    comput_values[idx] = original_values[idx] - uncertainties[idx]
                    _Asp1, _Ge1, _q01, _Er1, _Gs, _f, _alpha, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6, _Sg0 = comput_values
                    _e1 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6], [_b1, _b2, _b3, _b4, _b5, _b6], mon_Au[2])
                    solminus = (func_thermal_f(_Asp1, _e1, _Ge1, _q01, _Er1, _Gs, _f, _alpha, mon_Au[28], mon_Au[29], mon_Au[30], _Sg0) - F_th) / -(uncertainties[idx] + 1E-12)
                    solminusepi = (func_epithermal_f(_Asp1, _e1, _Ge1, _q01, _Er1, _Gs, _f, _alpha, mon_Au[28], mon_Au[29], mon_Au[30], _Sg0) - F_th) / -(uncertainties[idx] + 1E-12)
                    comput_values[idx] = original_values[idx]
                    res.append((solplus+solminus)/2)
                    resepi.append((solplusepi+solminusepi)/2)
                res = np.array(res)
                resepi = np.array(resepi)
                uncertainties = np.array(uncertainties)
                uncertainties = np.power(uncertainties, 2)
                unc_cov_matrix = np.diag(uncertainties)

                unc_cov_matrix[-13:-7,-13:-7] = self.calibration.reference_calibration.efficiency_cov
                unc_cov_matrix[-7:-1,-7:-1] = kedd_cov
                uF_th = float(np.sqrt((res.T@unc_cov_matrix) @ res))
                uF_epi = float(np.sqrt((resepi.T@unc_cov_matrix) @ resepi))

                ttext.append(f'Conventional fluxes value evaluated through Au monitor\n{"".ljust(12)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n{"thermal".ljust(12)}{format(F_th,".2e").ljust(11)}{format(uF_th,".2e").ljust(11)}({np.abs(100 * uF_th / F_th):.1f} %)\n{"epithermal".ljust(12)}{format(F_epi,".2e").ljust(11)}{format(uF_epi,".2e").ljust(11)}({np.abs(100 * uF_epi / F_epi):.1f} %)'+'\n')
            else:
                ttext.append('thermal and epithermal fluxes were not evalauted since Au monitor was not found in the spectra of monitor set\n')
            #fast
            if monitor_fast is not None:
                ttext.append(f'Selected fast monitor: {monitor_fast[0]} keV emission (found on spectrum {monitor_fast[-1]})\n')
                Asp1, uAsp1 = self.get_specific_fast(monitor_fast)
                #print(Asp1, uAsp1)
                #a1, a2, a3, a4, a5, a6 = self.calibration.reference_calibration.efficiency_parameters
                #ua1, ua2, ua3, ua4, ua5, ua6 = np.sqrt(np.diag(self.calibration.reference_calibration.efficiency_cov))

                temp_kedd_exp, temp_kedd_par, temp_kedd_cov = self.calibration.kedd_dict.get(fast_position, ([1, 0, -1, -2, -3, -4], np.zeros(6), np.zeros((6,6))))
                kedd_exp = [1, 0, -1, -2, -3, -4]
                kedd_par = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                kedd_cov = np.zeros((6,6))
                for idx, value, line in zip(temp_kedd_exp,temp_kedd_par, temp_kedd_cov):
                    kedd_par[kedd_exp.index(idx)] = value
                    for ddx, linevalue in zip(temp_kedd_exp, line):
                        kedd_cov[kedd_exp.index(idx),kedd_exp.index(ddx)] = linevalue
                b1, b2, b3, b4, b5, b6 = kedd_par
                e1 = e_polynomial_model([a1, a2, a3, a4, a5, a6], [b1, b2, b3, b4, b5, b6], monitor_fast[9])
                F_fast = func_fast_f(Asp1, e1, monitor_fast[4], monitor_fast[5], monitor_fast[6], monitor_fast[7])

                original_values = [Asp1, a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6, monitor_fast[7]]
                comput_values = [Asp1, a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6, monitor_fast[7]]
                uncertainties = [uAsp1, ua1, ua2, ua3, ua4, ua5, ua6, ub1, ub2, ub3, ub4, ub5, ub6, monitor_fast[8]]
                res = []
                for idx in range(len(original_values)):
                    comput_values[idx] = original_values[idx] + uncertainties[idx]
                    _Asp1, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6, _Sgf = comput_values
                    _e1 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6], [_b1, _b2, _b3, _b4, _b5, _b6], monitor_fast[9])
                    solplus = (func_fast_f(_Asp1, _e1, monitor_fast[4], monitor_fast[5], monitor_fast[6], _Sgf) - F_fast) / (uncertainties[idx] + 1E-12)
                    comput_values[idx] = original_values[idx] - uncertainties[idx]
                    _Asp1, _a1, _a2, _a3, _a4, _a5, _a6, _b1, _b2, _b3, _b4, _b5, _b6, _Sgf = comput_values
                    _e1 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6], [_b1, _b2, _b3, _b4, _b5, _b6], monitor_fast[9])
                    solminus = (func_fast_f(_Asp1, _e1, monitor_fast[4], monitor_fast[5], monitor_fast[6], _Sgf) - F_fast) / -(uncertainties[idx] + 1E-12)
                    comput_values[idx] = original_values[idx]
                    res.append((solplus+solminus)/2)
                res = np.array(res)
                uncertainties = np.array(uncertainties)
                uncertainties = np.power(uncertainties, 2)
                unc_cov_matrix = np.diag(uncertainties)
                unc_cov_matrix[-13:-7,-13:-7] = self.calibration.reference_calibration.efficiency_cov
                unc_cov_matrix[-7:-1,-7:-1] = kedd_cov
                uF_fast = float(np.sqrt((res.T@unc_cov_matrix) @ res))
                ttext.append(f'Conventional fast flux value evaluated\n{"".ljust(12)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n{"fast".ljust(12)}{format(F_fast,".2e").ljust(11)}{format(uF_fast,".2e").ljust(11)}({np.abs(100 * uF_fast / F_fast):.1f} %)\n')
            else:
                ttext.append(f'fast flux was not evalauted since fast monitor was not found in the spectra of monitor set\n')

        except:
            self.allow_save = False
            ttext.append('elaboration interrupted due to an error\n')
        else:
            if self.allow_save == True:
                self.result_f, self.result_f_unc = f, uf
                self.result_a, self.result_a_unc = alpha, ualpha
                self.result_thermal, self.result_thermal_unc = F_th, uF_th
                self.result_epithermal, self.result_epithermal_unc = F_epi, uF_epi
                self.result_fast, self.result_fast_unc = F_fast, uF_fast
                #self.result_beta, self.result_beta_unc = 0.0, 0.0
            else:
                ttext.append('it is not possible to save the obtained values\n')

        return ttext

    def uncertainty_job(self, value, unc, default=0.02):
        try:
            return float(unc) / 100 * value
        except:
            return default * value

    def get_specific_fast(self, line):
        """Calculate specific count rate at saturation, only I type"""
        _l, _ti, _tr, _tl, _td, _np, _unp, _coi, _ucoi, _m, _um = line[3], line[10], line[11], line[12], line[13], line[14], line[15], line[16], line[17], line[18], line[19]
        Asp = (_np * _l * _tr * np.exp(self.calibration.mu*(1-_tl/_tr))) / (_tl * (1 - np.exp(-_l * _ti)) * np.exp(-_l * _td) * (1 - np.exp(-_l * _tr)) * _coi * _m)
        unc = Asp * np.sqrt(np.power(_unp / _np, 2) + np.power(_um / _m, 2) + np.power(_ucoi / _coi, 2))
        return Asp, unc

    def get_specific(self, line):
        """Calculate specific count rate at saturation"""
        if line[12] == 'IIA':
            _l2, _l3, _ti, _tr, _tl, _td, _np, _unp, _coi, _ucoi, _m, _um = line[9], line[10], line[13], line[14], line[15], line[16], line[17], line[18], line[19], line[20], line[21], line[22]
            Asp = (_np * _tr * (_l3 - _l2) * np.exp(self.calibration.mu*(1-_tl/_tr))) / (_tl * _coi * _m * (_l3/_l2*(1 - np.exp(-_l2 * _ti)) * np.exp(-_l2 * _td) * (1 - np.exp(-_l2 * _tr)) - _l2/_l3*(1 - np.exp(-_l3 * _ti)) * np.exp(-_l3 * _td) * (1 - np.exp(-_l3 * _tr))))
        else:
            _l, _ti, _tr, _tl, _td, _np, _unp, _coi, _ucoi, _m, _um = line[9], line[13], line[14], line[15], line[16], line[17], line[18], line[19], line[20], line[21], line[22]
            Asp = (_np * _l * _tr * np.exp(self.calibration.mu*(1-_tl/_tr))) / (_tl * (1 - np.exp(-_l * _ti)) * np.exp(-_l * _td) * (1 - np.exp(-_l * _tr)) * _coi * _m)
        unc = Asp * np.sqrt(np.power(_unp / _np, 2) + np.power(_um / _m, 2) + np.power(_ucoi / _coi, 2))
        return Asp, unc

    def harvest_fast(self, label, irrtime, mass, umass, tolerance_energy, strategy='low. unc.'):
        targetinfo = None
        lis = None
        if label.get() != '':
            f_found = self.fast_database['emitter'] == label.get()
            targetinfo = self.fast_database[f_found].copy(deep=True)
            targetinfo = targetinfo.iloc[0]
            best_match = None
            for i in self.flux_spectra_list:
                for line in i.peak_list:
                    if targetinfo['energy'] - float(tolerance_energy) < float(line[2]) < targetinfo['energy'] + float(tolerance_energy):
                        if best_match is None:
                            if strategy == 'lowest unc.':
                                best_match = float(line[5]) / float(line[4])
                            if strategy == 'shortest' or strategy == 'longest':
                                best_match = i.live_time
                            if strategy == 'earliest' or strategy == 'latest':
                                best_match = i.datetime
                            fa_td = i.datetime - self.date
                            fa_td = fa_td.total_seconds()
                            coi, ucoi = 1.0, 0.0
                            lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, i.filename()]
                        else:
                            if strategy == 'lowest unc.':
                                if float(line[5]) / float(line[4]) < best_match:
                                    best_match = float(line[5]) / float(line[4])
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    coi, ucoi = 1.0, 0.0
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, i.filename()]
                            if strategy == 'shortest':
                                if i.live_time < best_match:
                                    best_match = i.live_time
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    coi, ucoi = 1.0, 0.0
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, i.filename()]
                            if strategy == 'longest':
                                if i.live_time > best_match:
                                    best_match = i.live_time
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    coi, ucoi = 1.0, 0.0
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, i.filename()]
                            if strategy == 'earliest':
                                if i.datetime < best_match:
                                    best_match = i.datetime
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    coi, ucoi = 1.0, 0.0
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, i.filename()]
                            if strategy == 'latest':
                                if i.datetime > best_match:
                                    best_match = i.datetime
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    coi, ucoi = 1.0, 0.0
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, i.filename()]
        if targetinfo is not None and lis is not None:
            return [targetinfo['emitter'], targetinfo['target'], targetinfo['reaction'], np.log(2)/targetinfo['half_life'], targetinfo['M'], targetinfo['isotopic_fraction'], targetinfo['yield'], targetinfo['cross_section'], targetinfo['u_cross_section'], targetinfo['energy']] + lis
        else:
            return None

    def harvest_monitor(self, label, correct_harvesting, irrtime, mass, umass, gs, ugs, ge, uge, tolerance_energy, triple_position, strategy='low. unc.'):
        # retrieve target information
        targetinfo = None
        lis = None
        for i in self.sub_database:
            if i[0] == label.get():
                targetinfo = i
        if targetinfo is None:
            #print('Target not found')
            correct_harvesting = False
        # retrieve emissions
        else:
            best_match = None
            for i in self.flux_spectra_list:
                for line in i.peak_list:
                    if targetinfo[2] - float(tolerance_energy) < float(line[2]) < targetinfo[2] + float(tolerance_energy):
                        if best_match is None:
                            if strategy == 'low. unc.':
                                best_match = float(line[5]) / float(line[4])
                            if strategy == 'shortest' or strategy == 'longest':
                                best_match = i.live_time
                            if strategy == 'earliest' or strategy == 'latest':
                                best_match = i.datetime
                            fa_td = i.datetime - self.date
                            fa_td = fa_td.total_seconds()
                            #coi, ucoi = 1.0, 0.0
                            coi, ucoi = naaobject.coi_correction_sda(label.get(), self.calibration, triple_position)
                            lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, gs, ugs, ge, uge, i.filename()]
                        else:
                            if strategy == 'low. unc.':
                                if float(line[5]) / float(line[4]) < best_match:
                                    best_match = float(line[5]) / float(line[4])
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    #coi, ucoi = 1.0, 0.0
                                    coi, ucoi = naaobject.coi_correction_sda(label.get(), self.calibration, triple_position)
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, gs, ugs, ge, uge, i.filename()]
                            if strategy == 'shortest':
                                if i.live_time < best_match:
                                    best_match = i.live_time
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    #coi, ucoi = 1.0, 0.0
                                    coi, ucoi = naaobject.coi_correction_sda(label.get(), self.calibration, triple_position)
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, gs, ugs, ge, uge, i.filename()]
                            if strategy == 'longest':
                                if i.live_time > best_match:
                                    best_match = i.live_time
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    #coi, ucoi = 1.0, 0.0
                                    coi, ucoi = naaobject.coi_correction_sda(label.get(), self.calibration, triple_position)
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, gs, ugs, ge, uge, i.filename()]
                            if strategy == 'earliest':
                                if i.datetime < best_match:
                                    best_match = i.datetime
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    #coi, ucoi = 1.0, 0.0
                                    coi, ucoi = naaobject.coi_correction_sda(label.get(), self.calibration, triple_position)
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, gs, ugs, ge, uge, i.filename()]
                            if strategy == 'latest':
                                if i.datetime > best_match:
                                    best_match = i.datetime
                                    fa_td = i.datetime - self.date
                                    fa_td = fa_td.total_seconds()
                                    #coi, ucoi = 1.0, 0.0
                                    coi, ucoi = naaobject.coi_correction_sda(label.get(), self.calibration, triple_position)
                                    lis = [irrtime, i.real_time, i.live_time, fa_td, float(line[4]), float(line[5]), coi, ucoi, mass, umass, gs, ugs, ge, uge, i.filename()]
        if targetinfo is not None and lis is not None:
            return targetinfo + lis, correct_harvesting
        else:
            return None, False

    def save_fluxes(self, CH_name, pos_name, folder=os.path.join('data', 'facility')):
        #prerequisites
        if self.allow_save == True and CH_name.get().replace(' ','') != '':
            save_time = datetime.datetime.today()
            with open(os.path.join(folder,'channels.csv'), 'a') as channel_file:
                channel_file.write(f'{self.date.strftime("%d/%m/%Y %H:%M:%S")},{save_time.strftime("%d/%m/%Y %H:%M:%S")},{CH_name.get()},{pos_name.get()},{self.result_f},{self.result_f_unc},{self.result_a},{self.result_a_unc},{self.result_thermal},{self.result_thermal_unc},{self.result_epithermal},{self.result_epithermal_unc},{self.result_fast},{self.result_fast_unc}\n')
            self.information_box.configure(text='flux evaluation is correctly saved!')
        elif self.allow_save == False:
            self.information_box.configure(text='the elaboration needs to be updated')
        elif CH_name.get().replace(' ','') == '':
            self.information_box.configure(text='channel name is invalid')

    def update_date(self, box, LM, LQ, LE):
        resp = self.check_label(box.get())
        LM.configure(text=resp[0])
        LQ.configure(text=resp[1])
        LE.configure(text=resp[2])

    def update_fast(self, box, LT, LR):
        resp = self.check_label_fast(box.get())
        LT.configure(text=resp[0])
        LR.configure(text=resp[1])

    def check_label(self, label, extended=False):
        for i in self.sub_database:
            if i[0] == label:
                return (i[1], i[5], i[7])
        return ('', '', '')

    def check_label_fast(self, label):
        if label != '':
            filt_emit = self.fast_database['emitter'] == label
            line = self.fast_database[filt_emit].iloc[0]
            return (line['target'], line['reaction'])
        else:
            return ('', '')

    def database_subset(self, NAA, file='flux'):
        try:
            with open(os.path.join(os.path.join('data','monitor_elements'),f'{file}.txt')) as t_file:
                flux_monitors_entries = list(set(['Au', 'Zr'] + [item for item in t_file.read().split()]))
        except:
            flux_monitors_entries = ['Au', 'Zr']
        sub_A = [self.shrinked_line(aline) for aline in NAA.database if aline[1] in flux_monitors_entries and self.shrinked_line(aline) is not None]
        return sub_A

    def shrinked_line(self, aline):

        allowedtypes = ['I', 'IIA']

        def emission(nucl, AA, state, energy):
            def statetype(state):
                if state != 1.0:
                    return 'm'
                else:
                    return ''
            return f'{nucl}-{int(AA)}{statetype(state)} {energy}'

        def lambdatime(timezzi, unit):
            if unit.lower() == 'd':
                return np.log(2) / (timezzi * 86400)
            elif unit.lower() == 'h':
                return np.log(2) / (timezzi * 3600)
            elif unit.lower() == 'm':
                return np.log(2) / (timezzi * 60)
            elif unit.lower() == 's':
                return np.log(2) / (timezzi)
            else:
                return ''
        if aline[22] in allowedtypes:
            # change the last two lambdatime!
            return [emission(aline[2], aline[3], aline[4], aline[5]), aline[1], aline[5], aline[7], aline[8], aline[75], aline[76], aline[77], aline[78], lambdatime(aline[31], aline[32]), lambdatime(aline[31+13], aline[32+13]), lambdatime(aline[31+26], aline[32+26]), aline[22]]
        else:
            return None


class FluxGradientEvaluationWindow:
    def __init__(self, parent, NAA, M):
        parent.title('Flux gradient evaluation')
        parent.resizable(False,False)
        parent.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(parent))
        self.information_box = tk.Label(parent, text='', anchor=tk.W)
        self.display_window = None
        info_frame = tk.Frame(parent)
        tk.Label(info_frame, text='channel', width=12, anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        channel_CB = ttk.Combobox(info_frame, width=15, state='readonly')
        channel_CB.grid(row=0, column=1, sticky=tk.W)

        self.channel_data = naaobject._get_channel_data()[1]
        list_value = tuple(self.channel_data['channel_name'].unique())

        channel_CB['values'] = list_value
        f_value, unc_f_value = 0.0, 0.0
        a_value, unc_a_value = 0.0, 0.0
        self.date = datetime.datetime.today()
        self.beta, self.unc_beta = None, None
        if NAA.irradiation is not None:
            if NAA.irradiation.channel_name in channel_CB['values']:
                channel_CB.set(NAA.irradiation.channel_name)
                self.date = NAA.irradiation.datetime
                f_value, unc_f_value, a_value, unc_a_value = NAA.irradiation.f_value, NAA.irradiation.unc_f_value, NAA.irradiation.a_value, NAA.irradiation.unc_a_value

        irradiation_date_label = gui_things.Label(info_frame, text=self.date.strftime("%d/%m/%Y %H:%M:%S"), width=25)
        irradiation_date_label.grid(row=0, column=2, sticky=tk.W)
        logo_calendar = tk.PhotoImage(data=gui_things.calendar)
        B_modify_date = gui_things.Button(info_frame, image=logo_calendar, command=lambda : self.change_end_irradiation_date(irradiation_date_label, self.information_box))
        B_modify_date.grid(row=0, column=3, padx=5)
        B_modify_date.image = logo_calendar
        tk.Frame(info_frame).grid(row=0, column=4, padx=10)
        tk.Label(info_frame, text='f:').grid(row=0, column=5)
        f_label = tk.Label(info_frame, text=f'{f_value:.1f} ({naaobject._get_division(unc_f_value,f_value):.1f} %)')
        f_label.grid(row=0, column=6)
        tk.Frame(info_frame).grid(row=0, column=7, padx=10)
        tk.Label(info_frame, text='α:').grid(row=0, column=8)
        a_label = tk.Label(info_frame, text=f'{a_value:.4f} ({naaobject._get_division(unc_a_value,a_value):.1f} %)')
        a_label.grid(row=0, column=9)
        cframe = tk.Frame(parent)
        tk.Label(cframe, text='calibration', width=12, anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        calibration_CB = ttk.Combobox(cframe, width=25, state='readonly')
        calibration_CB.grid(row=0, column=1, sticky=tk.W)
        calibration_CB['values'] = M.calibration_combobox['values']
        if NAA.calibration is not None:
            self.calibration = naaobject.DetectorCalibration(NAA.calibration.name)
            calibration_CB.set(self.calibration.name)
            def_value = self.calibration.reference_calibration.distance
            distances_list = list(self.calibration.kedd_dict.keys()) + [def_value]
        else:
            self.calibration = None
            def_value = None
            distances_list = None
        tk.Label(cframe, text='', anchor=tk.W).grid(row=0, column=2, padx=10)
        tk.Label(cframe, text='monitor', width=10, anchor=tk.W).grid(row=0, column=3, sticky=tk.W)
        mon_values, self.sub_database = self.subset_database(NAA.database)
        monitor_CB = ttk.Combobox(cframe, width=15, state='readonly')
        monitor_CB.grid(row=0, column=4, sticky=tk.W)
        monitor_CB['values'] = mon_values
        if len(mon_values) > 0:
            monitor_CB.set(monitor_CB['values'][0])

        self.higher_spectrum, self.lower_spectrum = None, None
        spectra_frame = tk.Frame(parent)
        tk.Label(spectra_frame, text='position', anchor=tk.W).grid(row=0, column=0)
        tk.Label(spectra_frame, text='mass / g', anchor=tk.W).grid(row=0, column=4)
        tk.Label(spectra_frame, text='u(mass) / g', anchor=tk.W).grid(row=0, column=5)
        tk.Label(spectra_frame, text='Gs / 1', anchor=tk.W).grid(row=0, column=6)
        tk.Label(spectra_frame, text='u(Gs) / 1', anchor=tk.W).grid(row=0, column=7)
        tk.Label(spectra_frame, text='Ge / 1', anchor=tk.W).grid(row=0, column=8)
        tk.Label(spectra_frame, text='u(Ge) / 1', anchor=tk.W).grid(row=0, column=9)
        tk.Label(spectra_frame, text='u(Δd) / mm', anchor=tk.W).grid(row=0, column=10)
        tk.Label(spectra_frame, text='ΔL / mm', anchor=tk.W).grid(row=0, column=11)
        tk.Label(spectra_frame, text='u(ΔL) / mm', anchor=tk.W).grid(row=0, column=12)
        tk.Label(spectra_frame, text='↑', anchor=tk.W).grid(row=1, column=0)
        logo_add_spectrum = tk.PhotoImage(data=gui_things.plus_spectrum)
        B_higher_open = gui_things.Button(spectra_frame, image=logo_add_spectrum, hint='Open spectrum of higher monitor!', hint_destination=self.information_box)
        B_higher_open.grid(row=1, column=1)
        B_higher_open.image = logo_add_spectrum
        higher_spectrum_name = tk.Label(spectra_frame, text='', anchor=tk.W, width=20)
        higher_spectrum_name.grid(row=1, column=2)
        logo_peaklist = tk.PhotoImage(data=gui_things.plist)
        B_higher_peaklist = gui_things.Button(spectra_frame, image=logo_peaklist, hint='Higher monitor peaklist!', hint_destination=self.information_box)
        B_higher_peaklist.grid(row=1, column=3)
        B_higher_peaklist.image = logo_peaklist
        hi_mass = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        hi_mass.grid(row=1, column=4, padx=2)
        hi_unc_mass = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        hi_unc_mass.grid(row=1, column=5, padx=2)
        hi_Gs = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        hi_Gs.grid(row=1, column=6, padx=2)
        hi_Gs.delete(0, tk.END)
        hi_Gs.insert(tk.END, 1.0)
        hi_unc_Gs = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        hi_unc_Gs.grid(row=1, column=7, padx=2)
        hi_Ge = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        hi_Ge.grid(row=1, column=8, padx=2)
        hi_Ge.delete(0, tk.END)
        hi_Ge.insert(tk.END, 1.0)
        hi_unc_Ge = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        hi_unc_Ge.grid(row=1, column=9, padx=2)
        hi_dd = tk.Spinbox(spectra_frame, from_=0.0, to=10.0, width=6, increment=0.1)
        hi_dd.grid(row=1, column=10, padx=2)
        hi_deltal = tk.Spinbox(spectra_frame, from_=0.0, to=300.0, width=8, increment=0.1)
        hi_deltal.grid(row=1, column=11, padx=2)
        hi_unc_deltal = tk.Spinbox(spectra_frame, from_=0.0, to=300.0, width=8, increment=0.1)
        hi_unc_deltal.grid(row=1, column=12, padx=2)
        tk.Label(spectra_frame, text='-', anchor=tk.W).grid(row=2, column=0)
        B_lower_open = gui_things.Button(spectra_frame, image=logo_add_spectrum, hint='Open spectrum of lower monitor!', hint_destination=self.information_box)
        B_lower_open.grid(row=2, column=1)
        B_lower_open.image = logo_add_spectrum
        lower_spectrum_name = tk.Label(spectra_frame, text='', anchor=tk.W, width=20)
        lower_spectrum_name.grid(row=2, column=2)
        B_lower_peaklist = gui_things.Button(spectra_frame, image=logo_peaklist, hint='Lower monitor peaklist!', hint_destination=self.information_box)
        B_lower_peaklist.grid(row=2, column=3)
        B_lower_peaklist.image = logo_peaklist
        lo_mass = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        lo_mass.grid(row=2, column=4, padx=2)
        lo_unc_mass = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        lo_unc_mass.grid(row=2, column=5, padx=2)
        lo_Gs = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        lo_Gs.grid(row=2, column=6, padx=2)
        lo_Gs.delete(0, tk.END)
        lo_Gs.insert(tk.END, 1.0)
        lo_unc_Gs = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        lo_unc_Gs.grid(row=2, column=7, padx=2)
        lo_Ge = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        lo_Ge.grid(row=2, column=8, padx=2)
        lo_Ge.delete(0, tk.END)
        lo_Ge.insert(tk.END, 1.0)
        lo_unc_Ge = tk.Spinbox(spectra_frame, from_=0.0000, to=1.0000, width=8, increment=0.0001)
        lo_unc_Ge.grid(row=2, column=9, padx=2)
        lo_dd = tk.Spinbox(spectra_frame, from_=0.0, to=10.0, width=6, increment=0.1)
        lo_dd.grid(row=2, column=10, padx=2)
        tk.Label(spectra_frame, text='monitor counting distance').grid(row=3, column=0, columnspan=3, sticky=tk.W)
        deltal_monitor_distance = gui_things.FDiscreteSlider(spectra_frame, length=300, label_width=10)
        deltal_monitor_distance.grid(row=3, column=3, columnspan=8, sticky=tk.EW, pady=3)
        B_higher_open.configure(command=lambda : self._add_spectra(parent, NAA.settings_dict['calibs statistical uncertainty limit'], higher_spectrum_name, which='higher'))
        B_lower_open.configure(command=lambda : self._add_spectra(parent, NAA.settings_dict['calibs statistical uncertainty limit'], lower_spectrum_name, which='lower'))
        B_higher_peaklist.configure(command=lambda : self.admire_spectra(parent, self.higher_spectrum))
        B_lower_peaklist.configure(command=lambda : self.admire_spectra(parent, self.lower_spectrum))

        if distances_list is not None:
            deltal_monitor_distance.set_values(distances_list, def_value)

        show_frame = tk.Frame(parent)
        stext = gui_things.ScrollableText(show_frame, width=50, height=12)
        stext.pack(anchor=tk.W, side=tk.LEFT)

        F_grap = tk.Frame(show_frame)
        figg = Figure(figsize=(4, 2))
        ax_fit = figg.add_subplot(111)
        Figur = tk.Frame(F_grap)
        Figur.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        canvas = FigureCanvasTkAgg(figg, master=Figur)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ax_fit.set_xlim(0, None)
        ax_fit.set_ylim(0, 2)
        ax_fit.set_ylabel(r'$C_\mathrm{sp\:n}$ / 1 ($k=2$)')
        ax_fit.set_xlabel(r'$\Delta L$ / mm')
        ax_fit.grid(True, linestyle='-.')
        figg.tight_layout()
        canvas.draw()
        F_grap.pack(side=tk.RIGHT, anchor=tk.NE, padx=5, pady=5, fill=tk.BOTH, expand=True)

        bframe = tk.Frame(parent)
        logo_mgears = tk.PhotoImage(data=gui_things.manygears)
        B_beta_evaluation = gui_things.Button(bframe, image=logo_mgears, hint='Evaluate!', hint_destination=self.information_box, command=lambda: self.beta_elaboration(channel_CB, monitor_CB, hi_mass, hi_unc_mass, hi_Gs, hi_unc_Gs, hi_Ge, hi_unc_Ge, hi_dd, hi_deltal, hi_unc_deltal, lo_mass, lo_unc_mass, lo_Gs, lo_unc_Gs, lo_Ge, lo_unc_Ge, lo_dd, deltal_monitor_distance, stext, ax_fit, figg, canvas, NAA.settings_dict['energy tolerance']))
        B_beta_evaluation.pack(side=tk.LEFT)
        B_beta_evaluation.image = logo_mgears
        ttk.Separator(bframe, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=3)
        logo_confirm = tk.PhotoImage(data=gui_things.beye)
        B_beta_save = gui_things.Button(bframe, image=logo_confirm, hint='Save elaboration!', hint_destination=self.information_box)
        B_beta_save.pack(side=tk.LEFT)
        B_beta_save.image = logo_confirm
        F_save_selector = tk.Frame(bframe)
        #self.save_selector_variable = tk.IntVar(parent)
        tk.Label(F_save_selector, text='position name').pack(anchor=tk.W, padx=3)
        E_newname = tk.Entry(F_save_selector, width=20)
        E_newname.pack(anchor=tk.W, padx=5)
        F_save_selector.pack(side=tk.LEFT, padx=3)

        info_frame.pack(anchor=tk.NW, padx=5, pady=5)
        cframe.pack(anchor=tk.NW, padx=5, pady=5)
        spectra_frame.pack(anchor=tk.NW, padx=5, pady=5)
        show_frame.pack(anchor=tk.NW, padx=5, pady=5)
        bframe.pack(anchor=tk.NW, padx=5, pady=5)
        self.information_box.pack(anchor=tk.NW, padx=5)

        B_beta_save.configure(command=lambda : self.beta_save(E_newname, channel_CB))

        channel_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': self._select_channel(channel_CB, E_newname, f_label, a_label))
        calibration_CB.bind('<<ComboboxSelected>>', lambda e='<<ComboboxSelected>>': self._select_calibration(calibration_CB, deltal_monitor_distance))

    def on_closing(self, parent, title='Quit Flux gradient evaluation window', message='Save your elaboration before quitting.\n\nDo you want to quit the window?'):
        if messagebox.askokcancel(title, message, parent=parent):
            parent.destroy()

    def beta_save(self, E_name, channel_CB, folder=os.path.join('data','facility')):
        if self.beta is not None and self.unc_beta is not None:
            save_time = datetime.datetime.today()
            ch_name = E_name.get()
            if ch_name.replace(' ','') != '':
                with open(os.path.join(folder,'beta.csv'), 'a') as channel_file:
                    channel_file.write(f'{channel_CB.get()},{self.date.strftime("%d/%m/%Y %H:%M:%S")},{save_time.strftime("%d/%m/%Y %H:%M:%S")},{ch_name},{self.beta},{self.unc_beta}\n')
                    self.information_box.configure(text='saved!')
            else:
                self.information_box.configure(text='invalid name')
        else:
            self.information_box.configure(text='β evaluation not valid')

    def beta_elaboration(self, channel_CB, monitor_CB, hi_mass, hi_unc_mass, hi_Gs, hi_unc_Gs, hi_Ge, hi_unc_Ge, hi_dd, hi_deltal, hi_unc_deltal, lo_mass, lo_unc_mass, lo_Gs, lo_unc_Gs, lo_Ge, lo_unc_Ge, lo_dd, deltal_monitor_distance, stext, ax_fit, figg, canvas, tolerance_energy=0.3):
        #prerequisites
        self.beta, self.unc_beta = None, None
        ttext = []
        start_elaboration = True
        try:
            hi_mass_in = float(hi_mass.get())
        except:
            hi_mass_in = 0.0
        try:
            hi_unc_mass_in = abs(float(hi_unc_mass.get()))
        except:
            hi_unc_mass_in = 0.0
        try:
            hi_Gs_in = float(hi_Gs.get())
        except:
            hi_Gs_in = 1.0
        try:
            hi_unc_Gs_in = abs(float(hi_unc_Gs.get()))
        except:
            hi_unc_Gs_in = 0.0
        try:
            hi_Ge_in = float(hi_Ge.get())
        except:
            hi_Ge_in = 1.0
        try:
            hi_unc_Ge_in = abs(float(hi_unc_Ge.get()))
        except:
            hi_unc_Ge_in = 0.0
        try:
            hi_dd_in = abs(float(hi_dd.get()))
        except:
            hi_dd_in = 0.0
        try:
            hi_deltal_in = float(hi_deltal.get())
        except:
            hi_deltal_in = 0.0
        try:
            hi_unc_deltal_in = abs(float(hi_unc_deltal.get()))
        except:
            hi_unc_deltal_in = 0.0
        try:
            lo_mass_in = float(lo_mass.get())
        except:
            lo_mass_in = 0.0
        try:
            lo_unc_mass_in = abs(float(lo_unc_mass.get()))
        except:
            lo_unc_mass_in = 0.0
        try:
            lo_Gs_in = float(lo_Gs.get())
        except:
            lo_Gs_in = 1.0
        try:
            lo_unc_Gs_in = abs(float(lo_unc_Gs.get()))
        except:
            lo_unc_Gs_in = 0.0
        try:
            lo_Ge_in = float(lo_Ge.get())
        except:
            lo_Ge_in = 1.0
        try:
            lo_unc_Ge_in = abs(float(lo_unc_Ge.get()))
        except:
            lo_unc_Ge_in = 0.0
        try:
            lo_dd_in = abs(float(lo_dd.get()))
        except:
            lo_dd_in = 0.0
        if channel_CB.get() == '':
            ttext.append('- irradiation channel is not selected')
            start_elaboration = False
        if self.calibration is None:
            ttext.append('- calibration is not selected')
            start_elaboration = False
        if self.higher_spectrum is None:
            ttext.append('- spectrum for higher monitor is not selected')
            start_elaboration = False
        if self.lower_spectrum is None:
            ttext.append('- spectrum for lower monitor is not selected')
            start_elaboration = False
        if hi_mass_in <= 0.0:
            ttext.append('- mass of higher monitor should be > 0')
            start_elaboration = False
        if lo_mass_in <= 0.0:
            ttext.append('- mass of lower monitor should be > 0')
            start_elaboration = False
        if hi_deltal_in <= 0.0:
            ttext.append('- ΔL must be > 0 to maintain the convention')
            start_elaboration = False
        if start_elaboration == True:
            monitor = self._get_monitor_data(monitor_CB.get())
            lamb, ulamb = self.get_lamb(monitor[31], monitor[32], monitor[33])
            Q0, uQ0 = self.get_values(monitor[75], monitor[76])
            Er, uEr = self.get_values(monitor[77], monitor[78], 50)
            np_hi, unp_hi = self.get_netarea_unc(self.higher_spectrum, monitor[5], tolerance_energy)
            np_lo, unp_lo = self.get_netarea_unc(self.lower_spectrum, monitor[5], tolerance_energy)
            td_hi = self.higher_spectrum.datetime - self.date
            td_hi = td_hi.total_seconds()
            td_lo = self.lower_spectrum.datetime - self.date
            td_lo = td_lo.total_seconds()
            if deltal_monitor_distance.get() == self.calibration.reference_calibration.distance:
                der_exp, der_parm, der_cov = self.calibration.reference_calibration.der_exponent, self.calibration.reference_calibration.der_parameters, self.calibration.reference_calibration.der_pcov
            else:
                der_exp, der_parm, der_cov = self.calibration.der_dict.get(deltal_monitor_distance.get(),(None, None, None))
            if der_exp is not None:
                der, uder = self._der_calculation(der_exp, der_parm, der_cov, monitor[5])
            else:
                der, uder = 0.0, 0.0
            proceed = True
            if np_hi is None:
                proceed = False
                ttext.append(f'- {monitor_CB.get()} peak is not found in the higher monitor spectrum!')
            if np_lo is None:
                proceed = False
                ttext.append(f'- {monitor_CB.get()} peak is not found in the lower monitor spectrum!')
            if td_hi < 0:
                proceed = False
                ttext.append('- acquisition date of higher spectrum is before the end of irradiation!')
            if td_lo < 0:
                proceed = False
                ttext.append('- acquisition date of lower spectrum is before the end of irradiation!')
            if proceed == True:
                ttext.append(f'Irradiation performed on {self.date.strftime("%d/%m/%Y %H:%M:%S")}\nAdopted emission for monitor: {monitor_CB.get()} keV\nCalibration: {self.calibration.name}, counting distance {self.calibration.reference_calibration.distance} mm on {self.calibration.detector} detector (d0 = {format(der,".1f")} mm)\n')
                ttext.append(f'- Monitor found on higher spectrum "{self.higher_spectrum.filename()}" ({format(np_hi,".0f")} net area counts with {format(unp_hi/np_hi*100,".2f")} % relative uncertainty)\n- Monitor found on lower spectrum "{self.lower_spectrum.filename()}" ({format(np_lo,".0f")} net area counts with {format(unp_lo/np_lo*100,".2f")} % relative uncertainty)\n- Distance between two monitor positions (ΔL) is {format(hi_deltal_in,".1f")} mm\n')

                dref = deltal_monitor_distance.get()

                #ff, uuff, aa, uuaa = self.channel_data.loc[channel_CB.get(), ['f_value', 'unc_f_value', 'a_value', 'unc_a_value']]

                filter_data = self.channel_data[self.channel_data['channel_name'] == channel_CB.get()]
                dataline = filter_data.iloc[0]
                ff, uuff, aa, uuaa = dataline['f_value'], dataline['unc_f_value'], dataline['a_value'], dataline['unc_a_value']


                Asp_lo = self.specific_count_rate(np_lo, self.lower_spectrum.real_time, self.lower_spectrum.live_time, lamb, td_lo, lo_mass_in, der, 0.0, lo_Gs_in, lo_Ge_in, ff, Q0, Er, aa, dref)
                Asp_hi = self.specific_count_rate(np_hi, self.higher_spectrum.real_time, self.higher_spectrum.live_time, lamb, td_hi, hi_mass_in, der, 0.0, hi_Gs_in, hi_Ge_in, ff, Q0, Er, aa, dref)
                # beta evaluation
                self.beta = (Asp_hi / Asp_lo - 1) / hi_deltal_in

                original_values = [np_lo, self.lower_spectrum.real_time, self.lower_spectrum.live_time, lamb, td_lo, lo_mass_in, 0.0, lo_Gs_in, lo_Ge_in, np_hi, self.higher_spectrum.real_time, self.higher_spectrum.live_time, td_hi, hi_mass_in, der, 0.0, hi_Gs_in, hi_Ge_in, ff, Q0, Er, aa, hi_deltal_in]
                comput_values = [np_lo, self.lower_spectrum.real_time, self.lower_spectrum.live_time, lamb, td_lo, lo_mass_in, 0.0, lo_Gs_in, lo_Ge_in, np_hi, self.higher_spectrum.real_time, self.higher_spectrum.live_time, td_hi, hi_mass_in, der, 0.0, hi_Gs_in, hi_Ge_in, ff, Q0, Er, aa, hi_deltal_in]
                uncertainties = [unp_lo, 0.1, 0.1, ulamb, 1, lo_unc_mass_in, lo_dd_in, lo_unc_Gs_in, lo_unc_Ge_in, unp_hi, 0.1, 0.1, 1, hi_unc_mass_in, uder, hi_dd_in, hi_unc_Gs_in, hi_unc_Ge_in, uuff, uQ0, uEr, uuaa, hi_unc_deltal_in]
                res = []
                unc_posrelunc = [0.0, 0.0]
                low_positionals = []
                hi_positionals = []
                for idx in range(len(original_values)):
                    comput_values[idx] = original_values[idx] + uncertainties[idx]
                    _np_lo, _tr_lo, _tl_lo, _lamb, _td_lo, _mass_lo, _dd_lo, _gs_lo, _ge_lo, _np_hi, _tr_hi, _tl_hi, _td_hi, _mass_hi, _der, _dd_hi, _gs_hi, _ge_hi, _ff, _Q0, _Er, _aa, _dx = comput_values
                    solplus = (self.specific_count_rate(_np_hi, _tr_hi, _tl_hi, _lamb, _td_hi, _mass_hi, _der, _dd_hi, _gs_hi, _ge_hi, _ff, _Q0, _Er, _aa, dref) / Asp_lo - self.specific_count_rate(_np_lo, _tr_lo, _tl_lo, _lamb, _td_lo, _mass_lo, _der, _dd_lo, _gs_lo, _ge_lo, _ff, _Q0, _Er, _aa, dref) / Asp_lo) / _dx
                    if idx == 6:
                        low_positionals.append(self.specific_count_rate(_np_lo, _tr_lo, _tl_lo, _lamb, _td_lo, _mass_lo, _der, _dd_lo, _gs_lo, _ge_lo, _ff, _Q0, _Er, _aa, dref))
                    if idx == 15:
                        hi_positionals.append(self.specific_count_rate(_np_hi, _tr_hi, _tl_hi, _lamb, _td_hi, _mass_hi, _der, _dd_hi, _gs_hi, _ge_hi, _ff, _Q0, _Er, _aa, dref))
                    comput_values[idx] = original_values[idx] - uncertainties[idx]
                    _np_lo, _tr_lo, _tl_lo, _lamb, _td_lo, _mass_lo, _dd_lo, _gs_lo, _ge_lo, _np_hi, _tr_hi, _tl_hi, _td_hi, _mass_hi, _der, _dd_hi, _gs_hi, _ge_hi, _ff, _Q0, _Er, _aa, _dx = comput_values
                    solminus = (self.specific_count_rate(_np_hi, _tr_hi, _tl_hi, _lamb, _td_hi, _mass_hi, _der, _dd_hi, _gs_hi, _ge_hi, _ff, _Q0, _Er, _aa, dref) / Asp_lo - self.specific_count_rate(_np_lo, _tr_lo, _tl_lo, _lamb, _td_lo, _mass_lo, _der, _dd_lo, _gs_lo, _ge_lo, _ff, _Q0, _Er, _aa, dref) / Asp_lo) / _dx
                    if idx == 6:
                        low_positionals.append(self.specific_count_rate(_np_lo, _tr_lo, _tl_lo, _lamb, _td_lo, _mass_lo, _der, _dd_lo, _gs_lo, _ge_lo, _ff, _Q0, _Er, _aa, dref))
                    if idx == 15:
                        hi_positionals.append(self.specific_count_rate(_np_hi, _tr_hi, _tl_hi, _lamb, _td_hi, _mass_hi, _der, _dd_hi, _gs_hi, _ge_hi, _ff, _Q0, _Er, _aa, dref))
                    comput_values[idx] = original_values[idx]
                    res.append((solplus-solminus) / (2*uncertainties[idx] + 1E-14))
                res = np.array(res)
                uncertainties = np.array(uncertainties)
                unc_cov_matrix = np.diag(np.power(uncertainties, 2))
                self.unc_beta = np.sqrt((res.T@unc_cov_matrix) @ res)
                if np.abs(self.unc_beta / self.beta) > 1.0:
                    warning = 'warning: excessive evaluated uncertainty for β, value might be non-significant\n'
                else:
                    warning = ''
                indexes = np.power(np.array([x1*x2 for x1, x2 in zip(res, uncertainties)]), 2)
                description = ['net area of lower monitor', 'real time of acquisition of lower monitor', 'live time of acquisition of lower monitor', 'decay constant', 'decay time of lower monitor', 'mass of lower monitor', 'positioning of lower monitor', 'thermal self shielding correction of lower monitor', 'epithermal self shielding correction of lower monitor', 'net area of higher monitor', 'real time of acquisition of higher monitor', 'live time of acquisition of higher monitor', 'decay time of higher monitor', 'mass of the higher monitor', 'vertical variability on efficiency', 'positioning of higher monitor', 'thermal self shielding correction of higher monitor', 'epithermal self shielding correction of higher monitor', 'f', 'Q0', 'Er', 'α', 'vertical distance between monitors']
                indexes = [(idx_value / indexes.sum(), tag) for idx_value, tag in zip(indexes, description)]
                indexes.sort(key=lambda x: x[0], reverse=True)
                text_major_contributors = [f'{format(100*line[0],".1f").rjust(5, " ")} % - {line[1]}' for line in indexes[:5]]
                ttext.append(f'β value found by calculating the slope of the line through two points\n{"".ljust(4)}{"value".ljust(10)}{"u (k=1)".ljust(9)}rel. u\n{"β".ljust(4)}{format(self.beta,".5f").ljust(10)}{format(self.unc_beta,".5f").ljust(9)}({np.abs(100 * self.unc_beta / self.beta):.1f} %)\n{warning}\nList of 5 major contributors to the combined uncertainty of β evaluation:\n'+'\n'.join(text_major_contributors)+'\n')

                #plot data
                #((_dref-_der)/(_dref+_dd-_der))**2
                unc_posrelunc = [np.std(low_positionals) / np.average(low_positionals), np.std(hi_positionals) / np.average(hi_positionals)]
                X_OFFSET = 3
                x_plot = [0, hi_deltal_in]
                y_plot = [1, Asp_hi / Asp_lo]
                y_uncplot = np.array([y_plot[0]*np.sqrt(np.power(unp_lo/np_lo, 2)+np.power(lo_unc_mass_in/lo_mass_in, 2)+np.power(unc_posrelunc[0], 2)), y_plot[1]*np.sqrt(np.power(unp_hi/np_hi, 2)+np.power(hi_unc_mass_in/hi_mass_in, 2)+np.power(unc_posrelunc[1],2))])
                ax_fit.grid(False)
                h = len(ax_fit.lines)
                for times in range(h):
                    ax_fit.lines.pop(0)
                    try:
                        ax_fit.collections.pop(0)
                    except IndexError:
                        pass
                ax_fit.errorbar(x_plot, y_plot, yerr=[2*y_uncplot, 2*y_uncplot], marker='o', markersize=3, markerfacecolor='w', markeredgecolor='k', markeredgewidth=0.5, color='r', linestyle='-', linewidth=0.75, elinewidth=0.5, ecolor='k')
                ax_fit.set_xlim(-X_OFFSET, hi_deltal_in+X_OFFSET)
                ax_fit.set_ylim(np.min(y_plot)-np.max(y_uncplot) * 3, np.max(y_plot)+np.max(y_uncplot)*3)
                ax_fit.grid(True, linestyle='-.')
                figg.tight_layout()
                canvas.draw()
            else:
                ttext = ['Issues were identified while processing the data; error messages are reported\n'] + ttext
            stext._update('\n'.join(ttext))
        else:
            ttext = ['Issues were identified while checking for consistency of the input data; error messages are reported\n'] + ttext
            stext._update('\n'.join(ttext))

    def specific_count_rate(self, _np, _tr, _tl, _lb, _td, _m, _der, _dd, _Gth, _Ge, _f, _Q0, _Er, _a,_dref):
        return (_np * _tr * np.exp(self.calibration.mu*(1-_tl/_tr))) / (_tl * np.exp(-_lb*_td) * (1-np.exp(-_lb*_tr)) * _m * ((_dref-_der)/(_dref+_dd-_der))**2 * (_Gth + _Ge / _f * ((_Q0 - 0.429)/(_Er**_a) + 0.429/((2*_a + 1) * 0.55**_a))))

    def g_discr(self,i):
        if i == 2.0:
            return 'm'
        else:
            return ''

    def _der_calculation(self, der_exp, der_parm, der_cov, energy):
        E = np.array([energy]) / 1000
        W = E[:, np.newaxis]**der_exp
        derm = -np.exp(der_parm@W.T)
        d_pars = np.array(der_parm,copy=True)
        d_errs = np.sqrt(np.diag(der_cov))
        sensitivity_coefficient = []
        for idx in range(len(d_pars)):
            d_pars[idx] = d_pars[idx] + d_errs[idx]
            yp = np.exp(d_pars@W.T)
            d_pars[idx] = d_pars[idx] - 2*d_errs[idx]
            ym = np.exp(d_pars@W.T)
            sensitivity_coefficient.append((yp - ym)/(2 * d_errs[idx]) + 1E-14)
            d_pars[idx] = der_parm[idx]
        sensitivity_coefficient = np.array(sensitivity_coefficient)
        derm = float(derm)
        u_derm = np.sqrt((sensitivity_coefficient.T@der_cov)@sensitivity_coefficient)
        u_derm = float(u_derm[0])
        return derm, u_derm

    def get_netarea_unc(self, spectrum, monitor_energy, tolerance_energy=0.3):
        npp, unpp = None, None
        for line in spectrum.peak_list:
            if monitor_energy - float(tolerance_energy) < float(line[2]) < monitor_energy + float(tolerance_energy):
                npp, unpp = float(line[4]), float(line[5])
                break
        return npp, unpp

    def get_lamb(self, value, unit, uncertainty):
        units = {'d': 86400, 's': 1, 'm': 60, 'h': 3600, 'y': 86400*365.24}
        lamb = np.log(2)/(value*units[unit.lower()])
        unc = uncertainty/value * lamb
        return lamb, unc

    def get_values(self, value, relative_uncertainty, default=20):
        try:
            uncertainty = value * relative_uncertainty / 100
        except:
            uncertainty = value * default / 100
        return value, uncertainty

    def subset_database(self, full_database, file='gradient'):
        try:
            with open(os.path.join(os.path.join('data','monitor_elements'),f'{file}.txt')) as t_file:
                allowed = set(['Au', 'Co'] + [item for item in t_file.read().split()])
        except:
            allowed = {'Au', 'Co'}
        allowed_type = {'I', 'IIB', 'IVB', 'VI'}
        subset_database = [line for line in full_database if line[1] in allowed and line[22] in allowed_type]
        values = [f'{line[2]}-{int(line[3])}{self.g_discr(line[4])} {line[5]}' for line in subset_database]
        return values, subset_database

    def _get_monitor_data(self, label):
        emit, energy = label.split()
        target, isot = emit.split('-')
        energy = float(energy)
        try:
            isot = float(isot)
            state = 1.0
        except:
            isot = float(isot.replace('m', ''))
            state = 2.0
        for line in self.sub_database:
            if line[2] == target and line[3] == isot and line[4] == state and line[5] == energy:
                return line

    def _add_spectra(self, parent, tol, labelname, which='higher'):
        #add spectra for gradient measurement
        if self.display_window is not None:
            self.display_window.destroy()
        filetypes = (('HyperLab peak list','*.csv'),('GammaVision report file','*.rpt'))#,('HyperLab ASC file','*.asc'),('CHN spectrum file','*.chn'))
        limit_s = tol
        try:
            output = askopenfilename(parent=parent, title=f'Open spectrum for {which} monitor',filetypes=filetypes)
            output = tuple([output])
        except TypeError:
            output = ()
        for filename in output:
            if filename != '' and filename != ():
                peak_list, counts, start_acquisition, real_time, live_time, result, note, source = naaobject.manage_spectra_files_and_get_infos(filename, limit=limit_s, look_for_peaklist_option=True)
                efficiency = None#NAA.calibration
                if result == True:
                    Spectrum = naaobject.SpectrumAnalysis(identity=f'gradient_spectrum', start_acquisition=start_acquisition, real_time=real_time, live_time=live_time, peak_list=peak_list, counts=counts, path=output, source=source, efficiency=efficiency)
                    if which == 'higher':
                        self.higher_spectrum = Spectrum
                    else:
                        self.lower_spectrum = Spectrum
                    labelname.configure(text=Spectrum.filename())
                    self.information_box.configure(text=f'{which} spectrum imported')
                else:
                    self.information_box.configure(text='failed to import spectrum')
            self.beta, self.unc_beta = None, None
                
    def admire_spectra(self, parent, spectrum_set):
        #display the peaklist for the selected spectrum
        if spectrum_set is not None:
            if self.display_window is not None:
                self.display_window.destroy()
            self.display_window = tk.Toplevel(parent)
            nline = 15
            local_peak_list = nest_list(spectrum_set.peak_list, nline)
            local_suspected = nest_list(spectrum_set.suspected, nline)
            PeaklistWindow(self.display_window, spectrum_set, local_peak_list, local_suspected, nline, background=None)

    def _select_calibration(self, box, slider):
        if box.get() != '':
            self.calibration = naaobject.DetectorCalibration(box.get())
            def_value = self.calibration.reference_calibration.distance
            distances_list = list(self.calibration.kedd_dict.keys()) + [def_value]
            slider.set_values(distances_list, def_value)
            self.beta, self.unc_beta = None, None

    def _select_channel(self, box, entry, Lf, La):

        filter_data = self.channel_data[self.channel_data['channel_name'] == box.get()]
        dataline = filter_data.iloc[0]

        f_value, unc_f_value, a_value, unc_a_value = dataline['f_value'], dataline['unc_f_value'], dataline['a_value'], dataline['unc_a_value']

        Lf.configure(text=f'{f_value:.1f} ({naaobject._get_division(unc_f_value,f_value):.1f} %)')
        La.configure(text=f'{a_value:.4f} ({naaobject._get_division(unc_a_value,a_value):.1f} %)')
        self.beta, self.unc_beta = None, None

    def change_end_irradiation_date(self, irradiation_date_label, hints):

        def _confirm_change(DaySpin,MonthSpin,YearSpin,HourSpin,MinuteSpin,SecondSpin,irradiation_date_label,TempTL,hints):
            try:
                day, month, year, hour, minute, second = int(DaySpin.get()), int(MonthSpin.get()), int(YearSpin.get()), int(HourSpin.get()), int(MinuteSpin.get()), int(SecondSpin.get())
            except:
                hints.configure(text='invalid end of irradiation date')
            else:
                try:
                    datetime.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    hints.configure(text='invalid end of irradiation date')
                else:
                    self.date = datetime.datetime(year, month, day, hour, minute, second)
                    irradiation_date_label.configure(text=self.date.strftime("%d/%m/%Y %H:%M:%S"))
                    hints.configure(text='date updated')
                    TempTL.destroy()
                    self.beta, self.unc_beta = None, None

        cwidth, xpos, ypos = irradiation_date_label.winfo_width(), irradiation_date_label.winfo_rootx(), irradiation_date_label.winfo_rooty()
        TempTL = tk.Toplevel(irradiation_date_label)
        TempTL.resizable(False, False)
        if sys.platform != 'darwin':
            TempTL.overrideredirect(True)
        day, month, year, hour, minute, second = self.date.day, self.date.month, self.date.year, self.date.hour, self.date.minute, self.date.second
        TempTLF = tk.Frame(TempTL, background='#A3A3A3', bd=3)
        DaySpin = tk.Spinbox(TempTLF, from_=1, to=31, width=3, increment=1)
        DaySpin.pack(side=tk.LEFT)
        DaySpin.delete(0, tk.END)
        DaySpin.insert(tk.END, day)
        MonthSpin = tk.Spinbox(TempTLF, from_=1, to=12, width=3, increment=1)
        MonthSpin.pack(side=tk.LEFT)
        MonthSpin.delete(0, tk.END)
        MonthSpin.insert(tk.END, month)
        YearSpin = tk.Spinbox(TempTLF, from_=1000, to=2999, width=5, increment=1)
        YearSpin.pack(side=tk.LEFT)
        YearSpin.delete(0, tk.END)
        YearSpin.insert(tk.END, year)
        tk.Frame(TempTLF, background='#A3A3A3').pack(side=tk.LEFT, padx=5)
        HourSpin = tk.Spinbox(TempTLF, from_=0, to=23, width=3, increment=1)
        HourSpin.pack(side=tk.LEFT)
        HourSpin.delete(0, tk.END)
        HourSpin.insert(tk.END, hour)
        MinuteSpin = tk.Spinbox(TempTLF, from_=0, to=59, width=3, increment=1)
        MinuteSpin.pack(side=tk.LEFT)
        MinuteSpin.delete(0, tk.END)
        MinuteSpin.insert(tk.END, minute)
        SecondSpin = tk.Spinbox(TempTLF, from_=0, to=59, width=3, increment=1)
        SecondSpin.pack(side=tk.LEFT)
        SecondSpin.delete(0, tk.END)
        SecondSpin.insert(tk.END, second)
        logo_new = tk.PhotoImage(data=gui_things.smallarrow)
        B_update_date = gui_things.Button(TempTLF, image=logo_new, hint='confirm new date', hint_xoffset=5, hint_destination=hints, command=lambda : _confirm_change(DaySpin,MonthSpin,YearSpin,HourSpin,MinuteSpin,SecondSpin,irradiation_date_label,TempTL,hints))
        B_update_date.image = logo_new
        B_update_date.pack(side=tk.LEFT)
        TempTLF.pack(fill=tk.X, expand=True)

        TempTL.update()
        width, height = TempTL.winfo_width(), TempTL.winfo_height()
        TempTL.geometry(f'{width}x{height}+{xpos-int(width/5)}+{ypos}')

        TempTLF.focus()
        if sys.platform != 'darwin':
            TempTLF.bind('<FocusOut>', lambda e='<FocusOut>': TempTL.destroy())


def main_script(NAA=None):
    if NAA is None:
        NAA = naaobject.CoreAnalysis(naaobject._get_settings_k0())
    else:
        NAA.settings_dict['page height'] = naaobject._get_settings_k0()['page height']
    M = tk.Tk()
    MainWindow(M, NAA)
    M.mainloop()


if __name__ == '__main__':
    main_script()
