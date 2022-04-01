# -*- coding: utf-8 -*-

"""
Classes to perform Neutron Analysis
"""

from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
import datetime
import numpy as np
import pandas as pd
import xlrd
import csv
import os
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

class Spectrum:
    """define a spectrum with all attached information."""
    def __init__(self,identity='Test',start_acquisition=datetime.datetime.today(),real_time=1000,live_time=999,peak_list=None,counts=None,path=None):
        self.identity = identity#Identity(Background,Comparator,Analytes) -> str
        self.datetime = start_acquisition#StartAcquisition -> datetime
        self.real_time = real_time#Real time -> float
        self.live_time = live_time#Live time -> float
        self.peak_list = peak_list#HyperLab_peaklist ->list
        self.counts = counts#spectrum -> np.array of ints
        self.spectrumpath = path
        self.assign_nuclide = None
        
    def deadtime(self,out='str'):
        try:
            deadtime=(self.real_time-self.live_time)/self.real_time
            deadtime=deadtime*100
            if out=='str':
                deadtime=str(deadtime.__round__(2))+' %'
        except:
            if out=='str':
                deadtime='Invalid'
            else:
                deadtime=None
        return deadtime
    
    def readable_datetime(self):
        return self.datetime.strftime("%d/%m/%Y %H:%M:%S")
    
    def number_of_channels(self):
        try:
            len(self.counts)
        except:
            return 0
        else:
            return len(self.counts)
        
    def defined_spectrum_integral(self,start,width):
        if start>0 and start<len(self.counts) and start+width<len(self.counts):
            integr=0
            for i in range(width):
                integr += self.counts[start+i]
            return integr
        else:
            return None
        
    def define(self):
        return self.identity
    
    def filename(self):
        filename=str(self.spectrumpath)
        filename=str.split(filename,'/')
        return filename[-1]


class SpectrumAnalysis(Spectrum):
	"""Defines a spectrum class suitable for NAA analysis wich includes
	calibration and peak evaluation features."""
	def __init__(self,identity,start_acquisition,real_time,live_time,peak_list=None,counts=None,path='',filepath_efficiency=None,prompt_peaksearch=True,prompt_peak_identification=True,w_mass=0,moisture_pc=0,source=None,sample=None,monitor=None,energy_tolerance=0.3,database_k0=None,database_relative=None,efficiency=None,database_source=None):
		Spectrum.__init__(self,identity,start_acquisition,real_time,live_time,peak_list,counts,path)
		self.calibration = efficiency
		self.k0_monitor_index = -1

		if self.peak_list is None:
			self.peak_list = []

		self.sample = sample#Subsample Class -> Inheritance from Sample Class
		if self.identity in ('sample', 'standard'):
			self.suspected = self._discriminate_peaks(energy_tolerance,database_k0,database_relative)
		elif self.identity in ('calibration', 'PT_spectrum'):
			self.suspected = self._discriminate_source_peaks(energy_tolerance,database_source)
		else:
			self.suspected = [()]*len(self.peak_list)
		if prompt_peak_identification:
			self.assign_nuclide = self._assign_peaks()#still inactive
		else:
			self.assign_nuclide = [-1]*len(self.peak_list)
		self.source = source
		self.spectrumpath = os.path.dirname(self.source[0][0])

	def filename(self):
		name = os.path.basename(self.source[0][0])
		return os.path.splitext(name)[0]

	def _discriminate_peaks(self,energy_tolerance,database_k0,database_relative=None):
		emissions = [self._emission_tuple(line[2],energy_tolerance,database_k0,database_relative) for line in self.peak_list]
		return emissions

	def _discriminate_source_peaks(self,energy_tolerance,database_source):
		if database_source is not None:
			emissions = [self._emission_tuple_source(line[2],energy_tolerance,database_source.data) for line in self.peak_list]
		else:
			emissions = [()]*len(self.peak_list)
		return emissions

	def get_k0_monitor(self):
		if self.k0_monitor_index > -1:
			sel = self.assign_nuclide[self.k0_monitor_index]
			if sel > -1:
				return self.suspected[self.k0_monitor_index][sel]

	def get_assigned(self,indexes=False):
		assigned = [self.suspected[idx][item] for idx, item in enumerate(self.assign_nuclide) if item > -1]
		if indexes == False:
			return assigned
		else:
			indexes = [idx for idx, item in enumerate(self.assign_nuclide) if item > -1]
			return assigned, indexes

	def get_mass_of_k0_monitor(self):
		value = (None, None)
		monitor = self.get_k0_monitor()
		if self.sample is not None:
			return self.sample.certificate.get(monitor.target, value)
		else:
			return None, None

	def _clear_emission_from_certificate(self):
		for ii in range(len(self.assign_nuclide)):
			self.assign_nuclide[ii] = -1

	def _select_emission_from_certificate(self,clear=False):
		#if clear:
		#	for ii in range(len(self.assign_nuclide)):
		#		self.assign_nuclide[ii] = -1
		element_list = list(self.sample.certificate.keys())
		if len(element_list) > 0:
			for idx, item in enumerate(self.suspected):
				if len(item) == 1 and self.assign_nuclide[idx] == -1:
					if item[0].target in element_list:
						self.assign_nuclide[idx] = 0
				elif len(item) > 0 and self.assign_nuclide[idx] == -1:
					found = []
					for index, possible in enumerate(item):
						if possible.target in element_list:
							found.append(index)
					if len(found) > 0:
					#if len(found) == 1:
						self.assign_nuclide[idx] = found[0]
		else:
			for idx, item in enumerate(self.suspected):
				if len(item) == 1 and self.assign_nuclide[idx] == -1:
					self.assign_nuclide[idx] = 0
				# elif len(item) > 0 and self.assign_nuclide[idx] == -1:
				# 	found = []
				# 	for index, possible in enumerate(item):
				# 		if possible.target in element_list:
				# 			found.append(index)
				# 	if len(found) > 0:
				# 	#if len(found) == 1:
				# 		self.assign_nuclide[idx] = found[0]

	def _select_emission_from_certificate_deprecated(self):#deprecated!
		element_list = list(self.sample.certificate.keys())
		if len(element_list) > 0:
			for idx, item in enumerate(self.suspected):
				if len(item) == 1 and self.assign_nuclide[idx] == -1:
					if item[0].target in element_list:
						self.assign_nuclide[idx] = 0
				elif len(item) > 0 and self.assign_nuclide[idx] == -1:
					found = []
					for index, possible in enumerate(item):
						if possible.target in element_list:
							found.append(index)
					if len(found) > 0:
					#if len(found) == 1:
						self.assign_nuclide[idx] = found[0]
		else:
			for idx, item in enumerate(self.suspected):
				if len(item) == 1 and self.assign_nuclide[idx] == -1:
					self.assign_nuclide[idx] = 0
				# elif len(item) > 0 and self.assign_nuclide[idx] == -1:
				# 	found = []
				# 	for index, possible in enumerate(item):
				# 		if possible.target in element_list:
				# 			found.append(index)
				# 	if len(found) > 0:
				# 	#if len(found) == 1:
				# 		self.assign_nuclide[idx] = found[0]

	def _emission_tuple(self,energy,energy_tolerance,database_k0,database_relative):#budgets should be the main, then emissions computed from it
		try:
			f_k0 = [Emission('k0',line) for line in database_k0 if energy - energy_tolerance < float(line[5]) < energy + energy_tolerance]
		except TypeError:
			f_k0 = []
		found = f_k0# + f_rel
		return tuple(found)

	def _emission_tuple_source(self,energy,energy_tolerance,database_source):#budgets should be the main, then emissions computed from it
		filter_source = (energy - energy_tolerance < database_source['energy'].astype(float)) & (database_source['energy'].astype(float) < energy + energy_tolerance)
		subdatabase = database_source[filter_source]
		try:
			f_source = [GSourceEmission(ene, emitt, ref) for ene, emitt, ref in zip(subdatabase['energy'], subdatabase['emitter'], subdatabase['reference'])]
		except TypeError:#TypeError:#FilenotFoundError
			f_source = []
		return tuple(f_source)
		
	def _state(self,identifier):
		if int(float(identifier)) == 2:
			return 'm'
		else:
			return ''

	def _choice(self,item,database):
		return -1

	def _assign_peaks(self):
		return [self._choice(item,None) for item in self.suspected]

	def set_calibration(self,calibration):
		self.calibration = calibration

	def update_sample(self, sample):
		self.sample = sample


class FitData_Base:
	def __init__(self, ndata=300, K=2., **kwargs):
		self.ndata = ndata
		self.K = K
		self.plot_kwargs = {'marker':'o', 'markersize':3, 'markeredgewidth':0.5, 'linestyle':'', 'markerfacecolor':'r', 'color':'k', 'elinewidth':0.5}#, **kwargs}
		self.line_kwargs = {'marker':'', 'linestyle':'-', 'linewidth':0.75, 'color':'k'}#, **kwargs}
		#self.reference = None #({DataPoints, DataFit, Residuals-> still DataPoints} -> kedd, {DataPoints, DataFit, Residuals-> still DataPoints} -> der)
		self.positions = {}
		self.emissions = {}

	def add_kedd(self, position, x, y, relres, uy=None):
		data = self.positions.get(position, [None, None, None, None])
		data[0] = DataPoints(x, y, relres, uy)
		self.positions[position] = data

	def add_kedd_fit(self, position, esp, parameters, cov=None):
		data = self.positions.get(position, [None, None, None, None])
		data[1] = DataPolyFit(esp, parameters, cov)
		self.positions[position] = data

	def add_der(self, position, x, y, relres, uy=None):
		data = self.positions.get(position, [None, None, None, None])
		data[2] = DataPoints(x, y, relres, uy)
		self.positions[position] = data

	def add_der_fit(self, position, esp, parameters, cov=None):
		data = self.positions.get(position, [None, None, None, None])
		data[3] = DataPolyFit(esp, parameters, cov)
		self.positions[position] = data

	def add_sqrtC(self, emitter, x, y, relres=None, uy=None):
		data = self.emissions.get(emitter, [None, None, None, None])
		data[0] = DataPoints(x, y, relres, uy)
		self.emissions[emitter] = data

	def add_sqrtC_fit(self, emitter, esp, parameters, cov=None):
		data = self.emissions.get(emitter, [None, None, None, None])
		data[1] = DataPolyFit(esp, parameters, cov)
		self.emissions[emitter] = data

	def add_linear_C(self, emitter, x, y, relres=None, uy=None):
		data = self.emissions.get(emitter, [None, None, None, None])
		data[2] = DataPoints(x, y, relres, uy)
		self.emissions[emitter] = data

	def add_linear_C_fit(self, emitter, x, y, relres=None, uy=None):
		data = self.emissions.get(emitter, [None, None, None, None])
		data[3] = DataPoints(x, y, relres, uy)
		self.emissions[emitter] = data


class DataPoints:
	def __init__(self, x, y, relres, uy=None):
		self.x = np.array(x)
		self.y = np.array(y)
		self.relres = np.array(relres)
		if uy is not None:
			self.uy = uy
		else:
			self.uy = np.array([0.0] * len(self.y))

	
class DataPolyFit:
	def __init__(self, esp, parameters, cov=None, keV=False):
		self.esp = esp
		self.params = parameters
		self.keV = keV

	def fit(self, x, der=False):
		if self.keV:
			x = x / 1000
		W = x[:, np.newaxis] ** self.esp
		if der:
			return -np.exp(self.params@W.T)
		else:
			return np.exp(self.params@W.T)

	def fit_sqrt(self, x, der=False):
		if self.keV:
			x = x / 1000
		W = x[:, np.newaxis] ** self.esp
		return self.params@W.T


class PartSpectr:#deprecated
	def __init__(self,start,stop,limit):
		self.start, self.stop = self._adjust_length(start,stop,limit)
		self._DX = 100
		self._model = None
		self.parameters = None
		self.residuals = None
		self.peak_results = (None,)

	def _adjust_length(self,start,stop,limit):
		if start<0:
			start = 0
		if stop>limit:
			stop = limit
		if stop<start:
			raise IndexError('stop index must be greater than start index')
		return start, stop

	def change_length(self,limit,newstart=None,newstop=None):
		if newstart==None and newstop==None:
			newstart, newstop = self.start, self.stop
		elif newstart==None:
			newstart = self.start
		elif newstop==None:
			newstop = self.stop
		self.start, self.stop = self._adjust_length(newstart,newstop,limit)

	def _create_peak_list(self,line,calibration):
		if calibration != None:
			energy = str(calibration.energy_converter(line.centroid))
		else:
			energy = ''
		return ['', '', '', '', str(line.centroid), '', energy, '', str(line.net_area), str(line.uncertainty_net_area), str(line.sigma*2.35), '', '', '', '', '', '', '', '', '', '']

class FittingResult:
	"""Stores the results of the fitting procedures"""
	def __init__(self,net_area,u_net_area,centroid,sigma):
		self.net_area = net_area
		self.uncertainty_net_area = u_net_area
		self.centroid = centroid
		self.sigma = sigma


class DummyCalibration:
    def __init__(self, detector, distance, energy_parameters, fwhm_parameters, efficiency_parameters, efficiency_cov, reference_PT):
        self.name = None#filename
        self.detector = detector
        self.geometry = distance
        self.energy_model = 'linear'#None#energy_model
        self.energy_parameters = energy_parameters
        self.fwhm_model = 'quadratic'
        self.fwhm_parameters = fwhm_parameters
        self.efficiency_model = '6term-polynomial'#efficiency_model
        self.efficiency_parameters = efficiency_parameters
        self.efficiency_cov = efficiency_cov
        self.der_exponent = None#der_exponents
        self.der_parameters = None#der_parameters
        self.der_pcov = None#der_pcov
        self.PT_energy, self.PT_linear, self.PT_polynomial, self.PT_text = reference_PT
        self.distance = float(self.geometry)
        self.d0_evaluation = None

        self.kedd_dict, self.der_dict, self.PT_dict, self.mu, self.u_mu, self.x_data, self.y_data = {}, {}, {}, 0.0, 0.0, None, None

    def _display_efficiency_fit(self, X):
        X = X / 1000
        esp = [1, 0, -1, -2, -3, -4]
        W = X[:, np.newaxis]**esp
        return np.exp(self.efficiency_parameters@W.T)

    def _display_kedd_fit(self, X, key):
        X = X / 1000
        esp, parameters, _ = self.kedd_dict[key]
        W = X[:, np.newaxis]**esp
        return np.exp(parameters@W.T)

    def _display_der_fit(self, X, key):
        X = X / 1000
        esp, parameters, _ = self.der_dict.get(key,(None, None, None))
        if esp is None:
            esp, parameters = self.der_exponent, self.der_parameters
        W = X[:, np.newaxis]**esp
        return -np.exp(parameters@W.T)

class ReferenceCalibration:
    def __init__(self, filename, detector, distance, energy_model, energy_parameters, fwhm_model, fwhm_parameters, efficiency_model, efficiency_parameters, efficiency_cov, der_exponents, der_parameters, der_pcov, reference_PT):
        self.name = filename
        self.detector = detector
        self.geometry = distance
        self.energy_model = energy_model
        self.energy_parameters = energy_parameters
        self.fwhm_model = fwhm_model
        self.fwhm_parameters = fwhm_parameters
        self.efficiency_model = efficiency_model
        self.efficiency_parameters = efficiency_parameters
        self.efficiency_cov = efficiency_cov
        self.der_exponent = der_exponents
        self.der_parameters = der_parameters
        self.der_pcov = der_pcov
        self.PT_energy, self.PT_linear, self.PT_polynomial = reference_PT
        self.distance = float(self.geometry)
        self.f_parameters = {'energy': self.energy_parameters,
                             'fwhm': self.fwhm_parameters, 'efficiency': self.efficiency_parameters}
        self.fits = {'linear': self.linear_model,
                     'quadratic': self.quadratic_model}#, '6term-polynomial': self.polynomial_model}

    def linear_model(self, pars, channel):
        parameters = self.f_parameters[pars]
        return parameters[0] * channel + parameters[1]

    def reverse_linear_model(self, pars, energy):
        parameters = self.f_parameters[pars]
        return (energy - parameters[1]) / parameters[0]

    def energy_fit(self, channel):
        fit = self.fits.get(self.energy_model, self.linear_model)
        return fit('energy', channel)

    def energy_fit_reversed(self, energy):
        return self.reverse_linear_model('energy', energy)

    def quadratic_model(self, pars, channel):
        parameters = self.f_parameters[pars]
        return np.sqrt(parameters[0] * channel + parameters[1])

    def fwhm_fit(self, channel):
        fit = self.fits.get(self.fwhm_model, self.linear_model)
        return fit('fwhm', channel)

    def _display_efficiency_fit(self, X):
        X = X / 1000
        esp = [1, 0, -1, -2, -3, -4]
        W = X[:, np.newaxis]**esp
        return np.exp(self.efficiency_parameters@W.T)


class DetectorCalibration:
    def __init__(self, filename):
        self.name = filename
        self.detector, self.reference_calibration, self.kedd_dict, self.der_dict, self.PT_dict, self.mu, self.u_mu, self.d0_evaluation, datapoints = self.get_detector_characterization(os.path.join(os.path.join('data','characterization'),f'{filename}.pos'))
        self.x_data, self.y_data = datapoints

    def get_distance(self, monitor, sample):
        data = set([monitor, sample])
        if len(data) == 1:
            return f'm & a: {monitor:.1f}'
        else:
            return f'm: {monitor:.1f}, a: {sample:.1f}'

    def evaluate_efficiency(self, energy, pos):
        X = np.array(energy / 1000)
        W = X[:, np.newaxis]**[1, 0, -1, -2, -3, -4]
        try:
            esp = self.kedd_dict[pos]
            esp = esp[0]
            Q = X[:, np.newaxis]**self.kedd_dict[pos][0]
            return np.exp(self.reference_calibration.efficiency_parameters@W.T) / np.exp(self.kedd_dict[pos][1]@Q.T)
        except KeyError:
            return np.exp(self.reference_calibration.efficiency_parameters@W.T)

    def _display_kedd_fit(self, X, kedd):
        X = X / 1000
        esp = kedd[0]
        W = X[:, np.newaxis]**esp
        return np.exp(kedd[1]@W.T)

    def _display_der_fit(self, X, der):
        X = X / 1000
        esp, parameters, _ = der
        W = X[:, np.newaxis]**esp
        return -np.exp(parameters@W.T)

    def evaluate_PT(self, energy, pos):
        Ej, linp, curvep = self.PT_dict[pos]
        PT = []
        for eng in energy:
            if eng > Ej:
                leng = np.log10(eng)
                PT.append(10**(linp[0] * leng + linp[1]))
            else:
                PT.append(10**(curvep[0] * np.power(leng,2) + curvep[1] * leng + curvep[2]))
        return np.array(PT)

    def get_detector_characterization(self, filename):
        mu_value, u_mu_value = 0.0, 0.0
        x_points, y_points = None, None
        reference_position_der, reference_der_parameters, reference_der_pcov = None, 0.0, 0.0
        d0_evaluation = None
        kedd = {}
        ders = {}
        PT = {}
        with open(filename, 'r') as f:
            r = [line.replace('\n', '') for line in f.readlines()]
        for line in range(len(r)):
            if 'detector: ' in r[line]:
                detector = r[line].replace('detector: ', '')
            if 'detector_mu:' in r[line]:
                mu_value, u_mu_value = np.array([float(num) for num in r[line+1].split()])
            if 'reference: ' in r[line]:
                reference_position = float(r[line].replace('reference: ', ''))
            if 'energy: ' in r[line]:
                reference_energy_model = r[line].replace('energy: ', '')
                reference_energy_parameters = np.array(
                    [float(num) for num in r[line+1].split()])
            if 'fwhm: ' in r[line]:
                reference_fwhm_model = r[line].replace('fwhm: ', '')
                reference_fwhm_parameters = np.array(
                    [float(num) for num in r[line+1].split()])
            if 'efficiency: ' in r[line]:
                reference_efficiency_model = r[line].replace(
                    'efficiency: ', '')
                reference_efficiency_parameters = np.array(
                    [float(num) for num in r[line+1].split()])
                reference_eff_cov = np.array([[float(num) for num in r[line+3+o].split()]
                                              for o in range(len(reference_efficiency_parameters))])
            if 'reference position der: ' in r[line]:
                reference_position_der = [int(num)
                                          for num in r[line].replace('reference position der: ', '').split()]
                reference_der_parameters = np.array([float(num)
                                                     for num in r[line+1].split()])
                reference_der_pcov = np.array([[float(num) for num in r[line+2+o].split()]
                                               for o in range(len(reference_position_der))])
            if 'reference_PT: ' in r[line]:
                #energy, linear, polynomial
                try:
                    energy_joint = float(r[line].replace('reference_PT: ',''))
                except (ValueError, TypeError):
                    energy_joint = None
                reference_PT = (energy_joint, np.array([float(num) for num in r[line+1].split()]), np.array([float(num) for num in r[line+2].split()]))
            if 'position: ' in r[line]:
                psline = r[line].replace('position: ', '')
                psdistance, psexponents = psline.split('|')
                psdistance = float(psdistance)
                psexponents = [int(item) for item in psexponents.split()]
                pos_kedd_parameters = np.array([float(num)
                                                for num in r[line+1].split()])
                pos_kedd_pcov = np.array([[float(num) for num in r[line+2+o].split()]
                                          for o in range(len(psexponents))])
                kedd[psdistance] = (
                    psexponents, pos_kedd_parameters, pos_kedd_pcov)
            if 'p_der: ' in r[line]:
                psline = r[line].replace('p_der: ', '')
                psdistance, psexponents = psline.split('|')
                psdistance = float(psdistance)
                psexponents = [int(item) for item in psexponents.split()]
                pos_kedd_parameters = np.array([float(num)
                                                for num in r[line+1].split()])
                pos_kedd_pcov = np.array([[float(num) for num in r[line+2+o].split()]
                                          for o in range(len(psexponents))])
                ders[psdistance] = (
                    psexponents, pos_kedd_parameters, pos_kedd_pcov)
            if 'p_PT: ' in r[line]:
                psline = r[line].replace('p_PT: ', '')
                psdistance, psexponents = psline.split('|')
                psdistance = float(psdistance)
                try:
                    psjoin = float(psexponents)
                except (ValueError, TypeError):
                    psjoin = None
                pos_linear_parameters = np.array([float(num)
                                                for num in r[line+1].split()])
                pos_polynomial_parameters = np.array([float(num)
                                                for num in r[line+2].split()])
                PT[psdistance] = (
                    psjoin, pos_linear_parameters, pos_polynomial_parameters)
            if 'x_points:' in r[line]:
                x_points = np.array([float(num) for num in r[line+1].split()])
            if 'y_points:' in r[line]:
                y_points = np.array([float(num) for num in r[line+1].split()])
        ref_calib = ReferenceCalibration('', detector, reference_position, reference_energy_model, reference_energy_parameters, reference_fwhm_model, reference_fwhm_parameters,reference_efficiency_model, reference_efficiency_parameters, reference_eff_cov, reference_position_der, reference_der_parameters, reference_der_pcov, reference_PT)
        return detector, ref_calib, kedd, ders, PT, mu_value, u_mu_value, d0_evaluation, (x_points, y_points)


class DummyGSource:
	def __init__(self, filename):
		self.datetime, self.data = self._open_source(filename)
		self.name = filename
		self.selection = [True]*len(self.data)

	def readable_datetime(self):
		return self.datetime.strftime("%d/%m/%Y %H:%M:%S")

	def _open_source(self, filename):
		dtime = datetime.datetime.today()
		datas = pd.DataFrame([], columns=['energy','emitter','activity','yield','t_half','COIfree'])
		datas['activity'] = datas['activity'].astype(float)
		datas['yield'] = datas['yield'].astype(float)
		datas['t_half'] = datas['t_half'].astype(float)
		datas['COIfree'] = datas['COIfree'].astype(int).astype(bool)
		datas['lambda'] = np.log(2)/datas['t_half']
		datas['reference'] = [f'{energy} keV {emitter}' for energy, emitter in zip(datas['energy'], datas['emitter'])]
		return dtime, datas

	def _modify_date(self,day,month,year,hour,minute,second):
		try:
			new_date = datetime.datetime(year, month, day, hour, minute, second)
		except ValueError:
			return 0
		else:
			self.datetime = new_date
			return 1

	def merge(self,other,ignore_index=True):
		return pd.concat([self.data,other], ignore_index=ignore_index)

	def _save_source(self):
		with open(os.path.join(os.path.join('data','sources'),f'{self.name}.sce'), 'w') as f:
			self.data['COIfree'] = self.data['COIfree'].astype(int)
			f.write(f'{self.readable_datetime()}\n')
			f.write(self.data.to_string(columns=['energy','emitter','activity','yield','t_half','COIfree'], header=False, index=False, show_dimensions=False, decimal='.'))
		self.data['COIfree'] = self.data['COIfree'].astype(bool)


class GSource:
	def __init__(self, filename):
		self.datetime, self.data = self._open_source(filename)
		self.name = filename
		self.selection = [True]*len(self.data)

	def readable_datetime(self):
		return self.datetime.strftime("%d/%m/%Y %H:%M:%S")

	def _open_source(self, filename):
		with open(os.path.join(os.path.join('data','sources'),f'{filename}.sce'), 'r') as f:
			filelines = [line.replace('\n','') for line in f.readlines()]
		dtime = datetime.datetime.strptime(filelines[0], "%d/%m/%Y %H:%M:%S")
		filelines = [line.split() for line in filelines[1:]]
		datas = pd.DataFrame(filelines, columns=['energy','emitter','activity','yield','t_half','COIfree'])
		datas['activity'] = datas['activity'].astype(float)
		datas['yield'] = datas['yield'].astype(float)
		datas['t_half'] = datas['t_half'].astype(float)
		datas['COIfree'] = datas['COIfree'].astype(int).astype(bool)
		datas['lambda'] = np.log(2)/datas['t_half']
		datas['reference'] = [f'{energy} keV {emitter}' for energy, emitter in zip(datas['energy'], datas['emitter'])]
		return dtime, datas

	def _modify_date(self,day,month,year,hour,minute,second):
		try:
			new_date = datetime.datetime(year, month, day, hour, minute, second)
		except ValueError:
			return 0
		else:
			self.datetime = new_date
			return 1

	def merge(self,other,ignore_index=True):
		return pd.concat([self.data,other], ignore_index=ignore_index)

	def _save_source(self):
		with open(os.path.join(os.path.join('data','sources'),f'{self.name}.sce'), 'w') as f:
			self.data['COIfree'] = self.data['COIfree'].astype(int)
			f.write(f'{self.readable_datetime()}\n')
			f.write(self.data.to_string(columns=['energy','emitter','activity','yield','t_half','COIfree'], header=False, index=False, show_dimensions=False, decimal='.'))
		self.data['COIfree'] = self.data['COIfree'].astype(bool)


class Irradiation:
	def __init__(self, filename=None, irradiation_code = '_', datetime = datetime.datetime.today(), channel_name = '_', f_value = 1.0, unc_f_value = 0.0, a_value = 0.0, unc_a_value = 0.0, thermal_flux = 1.0, unc_thermal_flux = 0.0, epithermal_flux = 0.0, unc_epithermal_flux = 0.0, fast_flux = 0.0, unc_fast_flux = 0.0, beta = 0.0, unc_beta = 0.0, irradiation_time = 0.0, unc_irradiation_time = 0.0):
		if filename is not None:
			self.irradiation_code, self.datetime, self.irradiation_time, self.unc_irradiation_time, self.channel_name, self.f_value, self.unc_f_value, self.a_value, self.unc_a_value, self.thermal_flux, self.unc_thermal_flux, self.epithermal_flux, self.unc_epithermal_flux, self.fast_flux, self.unc_fast_flux, self.beta, self.unc_beta = self._get_data_from_file(filename)
		else:
			self.irradiation_code = irradiation_code
			self.datetime = datetime#end of irradiation datetime object
			self.irradiation_time = irradiation_time#in seconds
			self.unc_irradiation_time = unc_irradiation_time
			self.channel_name = channel_name
			self.f_value = f_value
			self.unc_f_value = unc_f_value
			self.a_value = a_value
			self.unc_a_value = unc_a_value
			self.thermal_flux = thermal_flux
			self.unc_thermal_flux = unc_thermal_flux
			self.epithermal_flux = epithermal_flux
			self.unc_epithermal_flux = unc_epithermal_flux
			self.fast_flux = fast_flux
			self.unc_fast_flux = unc_fast_flux
			self.beta = beta
			self.unc_beta = unc_beta

	def readable_datetime(self):
		return self.datetime.strftime("%d/%m/%Y %H:%M:%S")

	def readable_irradiation_time(self):
		LIMIT1, LIMIT2 = 150000, 7200
		if self.irradiation_time > LIMIT1:
			return f'{self.irradiation_time/86400:.2f} d'
		elif self.irradiation_time > LIMIT2:
			return f'{self.irradiation_time/3600:.2f} h'
		else:
			return f'{self.irradiation_time:.0f} s'

	def _get_data_from_file(self, filename, folder=os.path.join('data','irradiation')):
		with open(os.path.join(folder,f'{filename}.irr')) as f:
			filelines = [line.replace('\n','') for line in f.readlines()]
		for line in filelines:
			if 'datetime: ' in line:
				dtime = datetime.datetime.strptime(line.replace('datetime: ',''), "%d/%m/%Y %H:%M:%S")
			if '#irradiation_time: ' in line:
				irradiation_time = float(line.replace('#irradiation_time: ',''))
			if 'unc_irradiation_time: ' in line:
				unc_irradiation_time = float(line.replace('unc_irradiation_time: ',''))
			if 'channel_name: ' in line:
				channel_name = line.replace('channel_name: ','')
			if '#f_value: ' in line:
				f_value = float(line.replace('#f_value: ',''))
			if 'unc_f_value: ' in line:
				unc_f_value = float(line.replace('unc_f_value: ',''))
			if '#a_value: ' in line:
				a_value = float(line.replace('#a_value: ',''))
			if 'unc_a_value: ' in line:
				unc_a_value = float(line.replace('unc_a_value: ',''))
			if '#thermal_flux: ' in line:
				thermal_flux = float(line.replace('#thermal_flux: ',''))
			if 'unc_thermal_flux: ' in line:
				unc_thermal_flux = float(line.replace('unc_thermal_flux: ',''))
			if '#epithermal_flux: ' in line:
				epithermal_flux = float(line.replace('#epithermal_flux: ',''))
			if 'unc_epithermal_flux: ' in line:
				unc_epithermal_flux = float(line.replace('unc_epithermal_flux: ',''))
			if '#fast_flux: ' in line:
				fast_flux = float(line.replace('#fast_flux: ',''))
			if 'unc_fast_flux: ' in line:
				unc_fast_flux = float(line.replace('unc_fast_flux: ',''))
			if '#beta: ' in line:
				beta = float(line.replace('#beta: ',''))
			if 'unc_beta: ' in line:
				unc_beta = float(line.replace('unc_beta: ',''))
		return filename, dtime, irradiation_time, unc_irradiation_time, channel_name, f_value, unc_f_value, a_value, unc_a_value, thermal_flux, unc_thermal_flux, epithermal_flux, unc_epithermal_flux, fast_flux, unc_fast_flux, beta, unc_beta

	def _save_to_file(self, folder=os.path.join('data','irradiation')):
		with open(os.path.join(folder,f'{self.irradiation_code}.irr'),'w') as irradiation_file:
			irradiation_file.write(f'datetime: {self.datetime.strftime("%d/%m/%Y %H:%M:%S")}\n#irradiation_time: {self.irradiation_time}\nunc_irradiation_time: {self.unc_irradiation_time}\nchannel_name: {self.channel_name}\n#f_value: {self.f_value}\nunc_f_value: {self.unc_f_value}\n#a_value: {self.a_value}\nunc_a_value: {self.unc_a_value}\n#thermal_flux: {self.thermal_flux}\nunc_thermal_flux: {self.unc_thermal_flux}\n#epithermal_flux: {self.epithermal_flux}\nunc_epithermal_flux: {self.unc_epithermal_flux}\n#fast_flux: {self.fast_flux}\nunc_fast_flux: {self.unc_fast_flux}\n#beta: {self.beta}\nunc_beta: {self.unc_beta}')


def bool_int(x):
	return bool(int(x))

def _get_correct_datatype(datum,datatype=str,default=None):
	datatypes = {'str':str, 'int':int, 'float':float, 'bool':bool_int}
	func = datatypes[datatype]
	return func(datum)

def _write_missing_setting_file(settings_file,master_settings):
	with open(settings_file, 'w') as missing_setting_file:
		for line in master_settings:
			missing_setting_file.write(f'{line[0]} <#> {line[2]}\n')

def _get_database_names(folder,extension):
	return [filename for filename in os.listdir(folder) if filename[-len(extension):].lower() == extension.lower()]

def _get_settings_k0(settings_file='data/k0-set.cfg'):
	"""Get settings information from configuration file"""
	#master settings list
	#descriptor, datatype, default_value
	master_settings = [
		['database', 'str', 'k0_database_2019_04_04_m.xls'], 
		['energy tolerance', 'float', 0.3],
		['page height', 'int', 25],
		['max allowed calibration uncertainty', 'int', 80],
		['calibs statistical uncertainty limit', 'int', 5],
		['standard statistical uncertainty limit', 'int', 15],
		['sample statistical uncertainty limit', 'int', 40],
		['non certified standard uncertainties', 'int', 10],
		['default tc&tl uncertainties', 'float', 0.1],
		['default td uncertainty', 'float', 10.0],
		['look for spectrum file', 'bool', 1]]
	try:
		with open(settings_file, 'r') as k0_settings_file:
			information = {line.replace('\n','').split(' <#> ')[0]:_get_correct_datatype(line.replace('\n','').split(' <#> ')[-1], traceline[1], traceline[2]) for line,traceline in zip(k0_settings_file.readlines(), master_settings)}
	except (FileNotFoundError, ValueError, IndexError):
		information = {line[0]:line[2] for line in master_settings}
		_write_missing_setting_file(settings_file,master_settings)
	return information

def _get_efficiency_file(folder='efficiencies'):
	return [file[:-4] for file in os.listdir(os.path.join('data',folder)) if file[-4:].lower()=='.efs']

def _findoutexceltable(wb,sheet):
	"""a list with the values of the database's worksheet"""
	fs=wb.sheet_by_name(sheet)
	table = []
	for r in range(1,fs.nrows):
		line = []
		for coln in range(fs.ncols):
			try:
				line.append(float(fs.cell(r,coln).value))
			except:
				line.append(fs.cell(r,coln).value)
		table.append(line)
	return table

def _totalk0tables(wb,sssh):
	"""Return a list of lists representing the worksheets composing the database"""
	tablesk0databases = []
	for index in sssh:
		tablesk0databases.append(_findoutexceltable(wb,index))
	return tablesk0databases

def _openselected_database(database):
	"""Open k0 database from file xls"""
	try:
		wb=xlrd.open_workbook(os.path.join(os.path.join('data','k0data'),database))
	except:
		pass
	else:
		sssh = wb.sheet_names()
		A = _totalk0tables(wb,sssh)
		return A

def _lineacumulata(database_table):
	"""Arrange k0 database on memory"""
	keyline = []
	for i in range(len(database_table[0])-1):
		key = database_table[0][i][0]
		emission = database_table[0][i][:18]
		for decay in range(len(database_table[4])):
			if database_table[4][decay][0] == key:
				emiss, fath, grandfa = database_table[4][decay][0], database_table[4][decay][5], database_table[4][decay][6]
				decaycode = database_table[4][decay][:8]
				break
		for nuclide in range(len(database_table[3])-1):
			if database_table[3][nuclide][0] == emiss:
				daught = database_table[3][nuclide][:13]
				break
		father = ['','','','','','','','','','','','','']
		for nuclide in range(len(database_table[3])-1):
			if database_table[3][nuclide][0] == fath:
				father = database_table[3][nuclide][:13]
				break
		grandfather = ['','','','','','','','','','','','','']
		for nuclide in range(len(database_table[3])-1):
			if database_table[3][nuclide][0] == grandfa:
				grandfather = database_table[3][nuclide][:13]
				break
		newkey = daught[0]
		capture = []
		for capt in range(len(database_table[1])-2):
			if database_table[1][capt][14] == newkey:
				capture = database_table[1][capt][:27]
				break
		if capture == []:
			newkey = father[0]
			for capt in range(len(database_table[1])-2):
				if database_table[1][capt][14] == newkey:
					capture = database_table[1][capt][:27]
					break
		if capture == []:
			newkey = grandfather[0]
			for capt in range(len(database_table[1])-2):
				if database_table[1][capt][14] == newkey:
					capture = database_table[1][capt][:27]
					break
		if grandfather[0] != '':
			keyline.append(emission+decaycode+daught+grandfather+father+capture)
		else:
			keyline.append(emission+decaycode+daught+father+grandfather+capture)
	return keyline

def _save_irradiation_database(df,filename='irradiation.csv'):
	#column_names = ['irradiation_code','datetime','irradiation_time','unc_irradiation_time','channel_name','f_value','unc_f_value','a_value','unc_a_value','thermal_flux','unc_thermal_flux','epithermal_flux','unc_epithermal_flux','fast_flux','unc_fast_flux','beta','unc_beta']
	df.to_csv(os.path.join(os.path.join('data','facility'),filename), sep=',')

def _open_irradiation_database(filename='irradiation.csv',items=15):
	column_names = ['irradiation_code','datetime','irradiation_time','unc_irradiation_time','channel_name','f_value','unc_f_value','a_value','unc_a_value','thermal_flux','unc_thermal_flux','epithermal_flux','unc_epithermal_flux','fast_flux','unc_fast_flux','beta','unc_beta']
	irradiation_df = pd.read_csv(os.path.join(os.path.join('data','facility'),filename), sep=',',index_col=column_names[0], names=column_names, header=0)
	irradiation_df['datetime'] = pd.to_datetime(irradiation_df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
	sorted_list = irradiation_df.sort_values('datetime', ascending=False, inplace=False)
	sorted_list = list(sorted_list.index)
	if items < len(sorted_list):
		sorted_list = sorted_list[:items]

	#df = pd.DataFrame(columns=column_names)
	#df.set_index(column_names[0], drop=True, inplace=True)
	#df.to_csv(os.path.join(os.path.join('data','facility'),filename), sep=',')
	return sorted_list, irradiation_df

def _open_channels_database(filename='channels.csv'):#only_last_update
	column_names = ['datetime','channel_name','f_value','unc_f_value','a_value','unc_a_value','thermal_flux','unc_thermal_flux','epithermal_flux','unc_epithermal_flux','fast_flux','unc_fast_flux','beta','unc_beta']
	channel_df = pd.read_csv(os.path.join(os.path.join('data','facility'),filename), sep=',', names=column_names, header=0)
	channel_df['datetime'] = pd.to_datetime(channel_df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
	channel_df.sort_values('datetime', ascending=False, inplace=True)
	channel_df.drop_duplicates(subset=column_names[1], inplace=True)

	#df = pd.DataFrame(columns=column_names)
	#df.set_index(column_names[0], drop=True, inplace=True)
	#df.to_csv(os.path.join(os.path.join('data','facility'),filename), index=False, sep=',')
	return list(channel_df[column_names[1]]), channel_df

class CoreAnalysis:
	def __init__(self,settings_dict):
		self.settings_dict = settings_dict
		self.analysis_name = None
		self.irradiation = None
		self.calibration = None
		self.background = []
		self.standard_spectra = []
		self.sample_spectra = []
		self.database = self._get_database()
		self.budgets = []
		self.detection_limits = []
		self.COI_database = self._get_COI_database()
		self.absorption_database = self._get_absorption_database()
		self.standard_position = (None, None, None)
		self.sample_position = (None, None, None)
		self.position_selector = None
		self.detection_elements = []

	def _get_database(self):
		filename = self.settings_dict['database']
		return _lineacumulata(_openselected_database(filename))

	def _get_absorption_database(self):
		absorption_df = pd.read_csv(os.path.join(os.path.join('data','literaturedata'), 'self_absorption_database.csv'), index_col=0)
		return absorption_df

	def _get_COI_database(self):
		coi_df = pd.read_excel(os.path.join(os.path.join('data','coincidences'), 'COI_database.xlsx'), skiprows=1, names=['target','emitter','E','line','a','c','g','type'])
		coi_df['target'].fillna(method='ffill', inplace=True)
		coi_df['type'].fillna(value='', inplace=True)
		coi_df['line'].fillna(value=0.0, inplace=True)
		coi_df['line'] = coi_df['line'].astype(int)
		return coi_df

	def _add_spectrum(self,Spectrum,button):
		if button == 'background':
			#clear background list
			for _ in range(len(self.background)):
				self.background.pop(0)
			self.background.append(Spectrum)
		elif button == 'standard':
			#clear standard list
			for ii in range(len(self.standard_spectra)):
				self.standard_spectra.pop(0)
			self.standard_spectra.append(Spectrum)
		elif button == 'sample':
			self.sample_spectra.append(Spectrum)

class Sample:
	"""
	Define macroscopic sample types to be irradiated
	"""
	def __init__(self,filename,folder=os.path.join('data','samples'),non_certified_uncertainty=20, old_sample=None):
		name, description, stype, physical_state, certificate, index = self._get_sample_information(filename,folder,non_certified_uncertainty,old_sample)
		self.name = name
		self.description = description.replace('\n','')
		self.sample_type = stype.replace('\n','')
		self.state = physical_state.replace('\n','')
		self.certificate = certificate
		self.non_certified = index

	def _to_csv(self):
		text = [f'{key},{item[0]},{item[1]}' for key,item in self.certificate.items() if key not in self.non_certified]
		text_non = [f'{key},{item[0]},{""}' for key,item in self.certificate.items() if key in self.non_certified]
		text += text_non
		return '\n'.join(text)

	def _get_sample_information(self,filename,folder,non_certified_uncertainty,old_sample=None):
		nfile = os.path.join(folder,filename)
		try:
			with open(nfile, 'r') as samplefile:
				description = samplefile.readline()
				stype = samplefile.readline()
				physical_state = samplefile.readline()
				elements = pd.read_csv(samplefile, header=None, names=['element','value','uncertainty'], index_col=0)
				index = list(elements['uncertainty'].index[elements['uncertainty'].isnull()])
				certificate = {key : self._fillna(key,elements.loc[key,'value'], elements.loc[key,'uncertainty'],non_certified_uncertainty,index) for key in elements.index}
				name = os.path.splitext(filename)[0]
		except FileNotFoundError:
			if old_sample is None:
				name, description, stype, physical_state, certificate, index = 'Unknown', '', 'unknown', 'unknown', {}, []
			else:
				name, description, stype, physical_state, certificate, index = old_sample.name, old_sample.description, old_sample.sample_type, old_sample.state, old_sample.certificate, old_sample.non_certified
		return name, description, stype, physical_state, certificate, index

	def _fillna(self,key,value,uncertainty,default,index):
		if key in index:
			if default is not None:
				return (value,value*default/100)
			else:
				return (value,np.nan)
		else:
			return (value,uncertainty)

	def _as_text_display(self,preamble='Elemental components of the sample listed in decreasing value of mass fraction, relative uncertainty (k=1) is reported while non certified values are indicated as "nan"\n\n', header=['El','x / g g-1','urx / %'],unit=None):
		spaces = [4,11,11]
		head = f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}\n'
		lines = sorted([(key,value[0],value[1]/value[0]) for key,value in self.certificate.items()], key=lambda x:x[1], reverse=True)
		if unit == 'ppm':
			astext = '\n'.join([f'{line[0].ljust(spaces[0]," ")}{format(line[1]*1000000,".3e").rjust(spaces[1]," ")}{format(line[2]*100,".1f").rjust(spaces[2]," ")}' for line in lines])
			header[1] = 'x / ppm'
		else:
			astext = '\n'.join([f'{line[0].ljust(spaces[0]," ")}{format(line[1],".3e").rjust(spaces[1]," ")}{format(line[2]*100,".1f").rjust(spaces[2]," ")}' for line in lines])
			header[1] = 'x / g g-1'
		return preamble+head+astext

	def _update_uncertainties(self,non_certified_uncertainty=20):
		certificate_updated = {key : (self.certificate[key][0], self.certificate[key][0]*non_certified_uncertainty/100) for key in self.non_certified}

		self.certificate = {**self.certificate, **certificate_updated}

#maybe a good idea?
class Subsample(Sample):
	"""
	Define a subsample with corresponding mass, moisture and shielding information
	"""
	def __init__(self,filename,weighted_mass=0.0,weighted_mass_unc=0.0,moisture=0.0,moisture_unc=0.0,th_selfshielding=1.0,th_selfshielding_unc=0.0,epi_selfshielding=1.0,epi_selfshielding_unc=0.0,delta_l=0.0,delta_l_unc=0.0,delta_h=0.1,delta_h_unc=0.0, density=0.001, density_unc=0.0, old_sample=None, **kwargs):
		non_certified_uncertainty = kwargs.get('non_certified_uncertainty',20)
		Sample.__init__(self,filename, non_certified_uncertainty=non_certified_uncertainty, old_sample=old_sample)
		self.weighted_mass, self.weighted_mass_unc = weighted_mass, weighted_mass_unc
		self.moisture, self.moisture_unc = moisture, moisture_unc
		self.mass, self.unc_mass = self._calculate_mass()
		self.th_selfshielding, self.th_selfshielding_unc = th_selfshielding, th_selfshielding_unc
		self.epi_selfshielding, self.epi_selfshielding_unc = epi_selfshielding, epi_selfshielding_unc
		self.dl, self.dl_unc = delta_l,delta_l_unc
		self.dh, self.dh_unc = delta_h,delta_h_unc
		self.density, self.density_unc = density, density_unc

	def _calculate_mass(self):
		try:
			value = self.weighted_mass * (1-self.moisture)
			unc = value * np.sqrt((self.weighted_mass_unc/self.weighted_mass)**2 + (self.moisture_unc/(1-self.moisture))**2)
		except ZeroDivisionError:
			value, unc = 0.0, 0.0
		return value, unc

class UncBudget:
	"""
	Store information to calculate results and return uncertainty budgets of k0 and relative NAA.
	All uncertainties have to be entered (and are returned) as absolute standard uncertainties
	"""
	def __init__(self, idx, NAA, M, sample_spectrum, emission_line, indexes, std_idx=0, detection_limit=False):
		#
		if 'Use the Westcott formalism' in emission_line.line[83]:
			self.westcott_warning = True
		else:
			self.westcott_warning = False
		self.cert_name = ''
		self.bkg_counts, self.bkg_ucounts = 0.0, 0.0
		self.background_correction = False
		self.blank_mass, self.blank_umass, self.blank_w, self.blank_uw = 0.0, 0.0, 0.0, 0.0
		if len(NAA.background) > 0:
			self.background = NAA.background[0]
			if self.background.sample is not None:
				self.blank_mass, self.blank_umass = self.background.sample.mass, self.background.sample.unc_mass
				self.blank_w, self.blank_uw = self.background.sample.certificate.get(emission_line.target, (0.0, 0.0))
			for line in self.background.peak_list:
				if float(line[2]) + float(NAA.settings_dict['energy tolerance']) > emission_line.energy and float(line[2]) - float(NAA.settings_dict['energy tolerance']) < emission_line.energy:
					self.bkg_counts, self.bkg_ucounts = float(line[4])/self.background.live_time * sample_spectrum.live_time , float(line[5])
					self.bkg_ucounts = float(line[5]) / float(line[4]) * self.bkg_counts
					break
		else:
			self.background = None
		#irradiation - calibration
		self.irradiation = NAA.irradiation
		self.calibration = NAA.calibration
		#detection limit
		self.currie_limit = self._get_currie_limit(detection_limit, emission_line, sample_spectrum, indexes)
		self.detection_limit = detection_limit
		self.nf_p, self.unc_nf_p = self._get_fast_correction_area()
		
		#counting positions #densities
		self.standard_pos, self.standard_dd, self.standard_udd, self.sample_pos, self.sample_dd, self.sample_udd, self.regular_kedd = self._get_positional_info(M.standard_position, M.Deltad_standard_spinbox, M.uDeltad_standard_spinbox, M.sample_position, M.Deltad_sample_spinbox, M.uDeltad_sample_spinbox, M.regular_calibration_variable)
		standard_spectrum = NAA.standard_spectra[std_idx]
		self.std_real = standard_spectrum.real_time
		self.std_live = standard_spectrum.live_time
		self.std_start_counting = standard_spectrum.datetime
		self.std_mass, self.std_umass = standard_spectrum.sample.weighted_mass, standard_spectrum.sample.weighted_mass_unc
		self.std_moisture, self.std_umoisture = standard_spectrum.sample.moisture, standard_spectrum.sample.moisture_unc
		self.std_w, self.std_uw = standard_spectrum.get_mass_of_k0_monitor()
		self.std_np, self.std_unp = standard_spectrum.peak_list[standard_spectrum.k0_monitor_index][4], standard_spectrum.peak_list[standard_spectrum.k0_monitor_index][5]
		self.std_Gth, self.std_uGth = standard_spectrum.sample.th_selfshielding, standard_spectrum.sample.th_selfshielding_unc
		self.std_Gepi, self.std_uGepi = standard_spectrum.sample.epi_selfshielding, standard_spectrum.sample.epi_selfshielding_unc
		self.std_Dh, self.std_uDh = standard_spectrum.sample.dh, standard_spectrum.sample.dh_unc
		self.std_density, self.std_udensity = standard_spectrum.sample.density/1000, standard_spectrum.sample.density_unc/1000 
		e_assigned = standard_spectrum.get_k0_monitor()
		self._get_standard_emission_info(e_assigned)
		self.std_murho, self.std_umurho = self.get_mu_value(NAA.absorption_database, self.std_energy/1000, standard_spectrum.sample)
		self.std_murho, self.std_umurho = self.std_murho*100, self.std_umurho*100
		if self.std_true_coincidence == True:
			std_PT = self.calibration.PT_dict.get(self.standard_pos, (None, [1,1], [1,1,1]))
			if std_PT[0] is not None:
				self.std_COI, self.std_uCOI = self.coi_correction(NAA.COI_database, e_assigned.emission, self.standard_pos)
			else:
				self.std_COI, self.std_uCOI = 1.0, 0.0
		else:
			self.std_COI, self.std_uCOI = 1.0, 0.0
		#print(self.std_COI, self.std_uCOI)
		#sample spectrum things
		self.smp_real = sample_spectrum.real_time
		self.smp_live = sample_spectrum.live_time
		self.smp_start_counting = sample_spectrum.datetime
		self.smp_mass, self.smp_umass = sample_spectrum.sample.weighted_mass, sample_spectrum.sample.weighted_mass_unc
		self.smp_moisture, self.smp_umoisture = sample_spectrum.sample.moisture, sample_spectrum.sample.moisture_unc
		if detection_limit == False:
			self.smp_np, self.smp_unp = sample_spectrum.peak_list[indexes][4], sample_spectrum.peak_list[indexes][5]
		else:
			self.smp_np, self.smp_unp = np.nan, np.nan
		self.smp_Gth, self.smp_uGth = sample_spectrum.sample.th_selfshielding, sample_spectrum.sample.th_selfshielding_unc
		self.smp_Gepi, self.smp_uGepi = 1.0, 0.0
		self.smp_Dl, self.smp_uDl = sample_spectrum.sample.dl, sample_spectrum.sample.dl_unc
		self.smp_Dh, self.smp_uDh = sample_spectrum.sample.dh, sample_spectrum.sample.dh_unc
		self.smp_density, self.smp_udensity = sample_spectrum.sample.density/1000, sample_spectrum.sample.density_unc/1000
		self._get_emission_info(emission_line)
		self.smp_murho, self.smp_umurho = self.get_mu_value(NAA.absorption_database, self.smp_energy/1000, sample_spectrum.sample)
		self.smp_murho, self.smp_umurho = self.smp_murho*100, self.smp_umurho*100
		if self.smp_true_coincidence == True:
			smp_PT = self.calibration.PT_dict.get(self.sample_pos, (None, [1,1], [1,1,1]))
			if smp_PT[0] is not None:
				self.smp_COI, self.smp_uCOI = self.coi_correction(NAA.COI_database, emission_line.emission, self.sample_pos)
			else:
				self.smp_COI, self.smp_uCOI = 1.0, 0.0
		else:
			self.smp_COI, self.smp_uCOI = 1.0, 0.0
		#print(self.smp_COI, self.smp_uCOI)
		#efficiencies
		self.keDe, self.ukeDe = self._keDe()
		self.keDd, self.ukeDd = self._keDd()
		self.std_der, self.std_uder, self.smp_der, self.smp_uder = self._der()
		self.spectrum_code, self.target, self.emission = f'#{idx+1}', emission_line.target, emission_line.emission
		self.emitter = '' #what was that for?
		self.z_score = self._get_z_score_info(sample_spectrum)
		#defaults
		self.dafault_times = NAA.settings_dict['default tc&tl uncertainties']
		self.default_td = NAA.settings_dict['default td uncertainty']

	def _get_code(self):
		return f'{self.spectrum_code}_{self.target}_{self.emission.replace(" keV", "")}'

	def __eq__(self, other):
		return self._get_code() == other._get_code()

	def get_mu_value(self, database, energy, sample):
		murho = np.sum([sample.certificate[element][0] * self.find_mu_value(database, energy, element) for element in sample.certificate.keys()])
		if murho > 0:
			return murho, murho*0.1
		else:
			return 1E-6, 0.0

	def find_mu_value(self, database, value, element, default_value = 1E-6):
		try:
			df = database[element]
			df.dropna(inplace=True)
		except:
			return default_value
		dix = np.array(df.index)
		filt = dix < value
		x, y = [], []

		try:
			x.append(df[filt].index[-1])
			y.append(df[filt].iloc[-1])
		except IndexError:
			pass
		try:
			x.append(df[~filt].index[0])
			y.append(df[~filt].iloc[0])
		except IndexError:
			pass
		if len(y) == 2:
			#linear approximation
			m = (y[1] - y[0]) / (x[1] - x[0])
			yy = y[0] + (value - x[0]) * m
			return yy
		elif len(y) == 1:
			return y[0]
		else:
			return default_value

	def _get_currie_limit(self, detection_limit, emission_line, sample_spectrum, indexes):
		if detection_limit == True:#no peak only background
			#calculate background!
			try:
				channel_position = self.calibration.reference_calibration.energy_fit_reversed(emission_line.energy)
				detectionlimitrange = int(self.calibration.reference_calibration.fwhm_fit(channel_position) * 3) + 1
				return sample_spectrum.defined_spectrum_integral(int(channel_position-detectionlimitrange/2), detectionlimitrange)
			except:
				return None
		else:#there is the peak
			#get data from the peaklist!
			try:
				if np.isnan(sample_spectrum.peak_list[indexes][-1]):#True
					channel_position = sample_spectrum.peak_list[indexes][0]
					detectionlimitrange = sample_spectrum.peak_list[indexes][6] * 3
					lenght = 3
					low = sample_spectrum.defined_spectrum_integral(int(channel_position-detectionlimitrange/2 - lenght), lenght)
					high = sample_spectrum.defined_spectrum_integral(int(channel_position+detectionlimitrange/2), lenght)
					BKG_mean = (low + high) / (2 * lenght)
					return BKG_mean * detectionlimitrange
				else:
					return sample_spectrum.peak_list[indexes][-1]
			except:
				return None
			
	def _get_fast_correction_area(self):#think about it
		return 0.0, 0.0

	def _get_z_score_info(self, sample_spectrum):
		z, uz, RM = None, None, False
		if sample_spectrum.sample is not None:
			self.cert_name = sample_spectrum.sample.name
			if sample_spectrum.sample.sample_type == 'Reference Material':
				RM = True
			y = sample_spectrum.sample.certificate.get(self.target)
			if y is not None:
				return y[0], y[1], RM
		return z, uz, RM

	def manage_sum(self, emitter_df, Xindex, idxs):
		correction = 0.0
		if len(idxs) == 3:
			aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD = self.sum_type_I(emitter_df, idxs, Xindex)
			correction = gB/gA*aC*cC*epB*epC/epA
		elif len(idxs) == 4:
			aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD = self.sum_type_II(emitter_df, idxs, Xindex)
			correction = gB/gA*aC*cC*aD*cD*epB*epC*epD/epA
		return correction

	def sum_type_I(self, emitter_df, idxs, Xindex):
		# (*A=B+C)
		aA, cA, gA, epA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, epB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, epC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, epD = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, epA = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 1:
				aB, cB, gB, epB = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 2:
				aC, cC, gC, epC = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 3:
				aD, cD, gD, epD = emitter_df.loc[idx, ['a','c','g','ep']]
		return aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD

	def sum_type_II(self, emitter_df, idxs, Xindex):
		# (*A=B+C+D)
		aA, cA, gA, epA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, epB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, epC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, epD = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, epA = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 1:
				aB, cB, gB, epB = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 2:
				aC, cC, gC, epC = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 3:
				aD, cD, gD, epD = emitter_df.loc[idx, ['a','c','g','ep']]
		return aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD

	def manage_losses(self, emitter_df, Xindex, idxs):
		correction = 0.0
		if idxs.index('X') == 0:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_I(emitter_df, idxs, Xindex)
			F1 = aB*cB*etB+aB*aC*cC*etC+aB*aC*aD*cD*etD+aB*aC*aD*aE*cE*etE 
			F2 = aB*aC*cB*cC*etB*etC+aB*aC*aD*cB*cD*etB*etD+aB*aC*aD*aE*cB*cE*etB*etE+aB*aC*aD*cC*cD*etC*etD+aB*aC*aD*aE*cC*cE*etC*etE+aB*aC*aD*aE*cD*cE*etD*etE
			F3 = aB*aC*aD*cB*cC*cD*etB*etC*etD+aB*aC*aD*aE*cB*cC*cE*etB*etC*etE+aB*aC*aD*aE*cB*cD*cE*etB*etD*etE+aB*aC*aD*aE*cC*cD*cE*etC*etD*etE
			F4 = aB*aC*aD*aE*cB*cC*cD*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 1:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_II(emitter_df, idxs, Xindex)
			F1 = gB/gA*aA*cA*etB+aC*cC*etC+aC*aD*cD*etD+aC*aD*aE*cE*etE
			F2 = gB/gA*aA*aC*cA*cC*etB*etC+gB/gA*aA*aC*aD*cA*cD*etB*etD+gB/gA*aA*aC*aD*aE*cA*cE*etB*etE+aC*aD*cC*cD*etC*etD+aC*aD*aE*cC*cE*etC*etE+aC*aD*aE*cD*cE*etD*etE
			F3 = gB/gA*aA*aC*aD*cA*cC*cD*etB*etC*etD+gB/gA*aA*aC*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+aC*aD*aE*cC*cD*cE*etC*etD*etE
			F4 = gB/gA*aA*aC*aD*aE*cA*cC*cD*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 2:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_III(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aA*cA*etB+gC/gA*aA*cA*etC+aD*cD*etD+aD*aE*cE*etE
			F2 = gB/gA*aC*aA*cC*cA*etB*etC+gB/gA*aC*aA*aD*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cA*cE*etB*etE+gC/gA*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+aD*aE*cD*cE*etD*etE
			F3 = gB/gA*aC*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 3:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_IV(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aD*aA*cA*etB+gC/gA*aD*aA*cA*etC+gD/gA*aA*cA*etD+aE*cE*etE
			F2 = gB/gA*aC*aD*aA*cC*cA*etB*etC+gB/gA*aC*aA*aD*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cA*cE*etB*etE+gC/gA*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+gD/gA*aA*aE*cA*cE*etD*etE
			F3 = gB/gA*aC*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*cC*cD*cA*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 4:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_V(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aD*aE*aA*cA*etB+gC/gA*aD*aE*aA*cA*etC+gD/gA*aE*aA*cA*etD+gE/gA*aA*cA*etE
			F2 = gB/gA*aC*aD*aE*aA*cE*cA*etB*etE+gB/gA*aC*aD*aE*aA*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cC*cA*etB*etC+gC/gA*aE*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+gD/gA*aA*aE*cA*cE*etD*etE
			F3 = gB/gA*aC*aE*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aE*aA*aC*aD*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*cC*cD*cA*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		return correction

	def loss_type_I(self, emitter_df, idxs, Xindex):
		# (*A-B-C-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_II(self, emitter_df, idxs, Xindex):
		# (B-*A-C-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 1:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_III(self, emitter_df, idxs, Xindex):
		# (B-C-*A-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 2:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_IV(self, emitter_df, idxs, Xindex):
		# (B-C-D-*A-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 3:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_V(self, emitter_df, idxs, Xindex):
		# (B-C-D-E-*A)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 4:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def coi_correction(self, coi_df, emission, pos, R=0.2):
		emit, energy = emission.replace(' keV','').split()
		#print(emit, pos)
		filt_emission = coi_df['emitter'] == emit
		emitter_df = coi_df[filt_emission].copy(deep=True)
		emitter_df.set_index('line', drop=True, append=False, inplace=True, verify_integrity=False)

		filt_X = (float(energy) - 0.2 < emitter_df['E']) & (emitter_df['E'] < float(energy) + 0.2)
		#print(emitter_df[filt_X])
		try:
			Xindex = int(emitter_df[filt_X].index[0])
			scheme = emitter_df.loc[Xindex, 'type']
			emitter_df['ep'] = self.calibration.evaluate_efficiency(emitter_df['E'], pos)
			emitter_df['et'] = emitter_df['ep'] / self.calibration.evaluate_PT(emitter_df['E'], pos)

			coincidences = scheme.split(' : ')
			corrections_loss = []
			corrections_sum = []
			#print(emitter_df)
			for item in coincidences:
				if '-' in item:
					#print(item, ': Coincidence LOSS')
					if '*' in item:
						nn, item = item.split('*')
						nn = int(nn)
						#print(nn, item)
						item = item.replace('(','').replace(')','')
						idxs = [int(idx) if idx!='X' else idx for idx in item.split('-')]
						corrections_loss.append(nn * self.manage_losses(emitter_df, Xindex, idxs))
					else:
						idxs = [int(idx) if idx!='X' else idx for idx in item.split('-')]
						corrections_loss.append(self.manage_losses(emitter_df, Xindex, idxs))
				else:
					#print(item, ': Coincidence SUM')
					item = item.replace('=',' ').replace('+',' ')
					idxs = [int(idx) if idx!='X' else idx for idx in item.split()]
					corrections_sum.append(self.manage_sum(emitter_df, Xindex, idxs))
			#print('sum loss',np.sum(corrections_loss))
			coi = (1-np.sum(corrections_loss)) * (1+np.sum(corrections_sum))
			ucoi = coi * np.sqrt(np.power((np.sum(corrections_loss)*R)/(1-np.sum(corrections_loss)),2) + np.power((np.sum(corrections_sum)*R)/(1-np.sum(corrections_sum)),2))
			#print('coi',coi)
		except:
			coi, ucoi = 1.0, 0.0
		return coi, ucoi

	def _keDe(self):
		Em, Ea = np.array([self.std_energy]) / 1000, np.array([self.smp_energy]) / 1000
		esp = [1, 0, -1, -2, -3, -4]
		Wm = Em[:, np.newaxis]**esp
		Wa = Ea[:, np.newaxis]**esp
		W = (Wm - Wa)
		y = np.exp(self.calibration.reference_calibration.efficiency_parameters@W.T)
		d_pars = np.array(self.calibration.reference_calibration.efficiency_parameters,copy=True)
		d_errs = np.sqrt(np.diag(self.calibration.reference_calibration.efficiency_cov))
		sensitivity_coefficient = []
		for idx in range(len(d_pars)):
			d_pars[idx] = d_pars[idx] + d_errs[idx]
			yp = np.exp(d_pars@W.T)
			d_pars[idx] = d_pars[idx] - 2*d_errs[idx]
			ym = np.exp(d_pars@W.T)
			sensitivity_coefficient.append((yp - ym)/(2 * d_errs[idx]) + 1E-14)
			d_pars[idx] = self.calibration.reference_calibration.efficiency_parameters[idx]
		sensitivity_coefficient = np.array(sensitivity_coefficient)
		y = float(y)
		uy = np.sqrt((sensitivity_coefficient.T@self.calibration.reference_calibration.efficiency_cov)@sensitivity_coefficient)
		uy = float(uy[0])
		return y, uy

	def _keDd(self):
		if self.regular_kedd == True:
			kedd_file = self.calibration.kedd_dict.get(self.sample_pos, (None, None, None))
			if kedd_file[0] is not None:
				Eg = np.array([self.smp_energy]) / 1000
				Wm = Eg[:, np.newaxis]**kedd_file[0]
				y = np.exp(kedd_file[1]@Wm.T)
				d_pars = np.array(kedd_file[1],copy=True)
				d_errs = np.sqrt(np.diag(kedd_file[2]))
				sensitivity_coefficient = []
				for idx in range(len(d_pars)):
					d_pars[idx] = d_pars[idx] + d_errs[idx]
					yp = np.exp(d_pars@Wm.T)
					d_pars[idx] = d_pars[idx] - 2*d_errs[idx]
					ym = np.exp(d_pars@Wm.T)
					sensitivity_coefficient.append((yp - ym)/(2 * d_errs[idx]) + 1E-14)
					d_pars[idx] = kedd_file[1][idx]
				sensitivity_coefficient = np.array(sensitivity_coefficient)
				y = float(y)
				uy = np.sqrt((sensitivity_coefficient.T@kedd_file[2])@sensitivity_coefficient)
				uy = float(uy[0])
				return y, uy
			else:
				return 1.0, 0.0
		else:
			kedd_file = self.calibration.kedd_dict.get(self.standard_pos, (None, None, None))
			if kedd_file[0] is not None:
				Eg = np.array([self.std_energy]) / 1000
				Wm = Eg[:, np.newaxis]**kedd_file[0]
				y = np.exp(kedd_file[1]@Wm.T)
				d_pars = np.array(kedd_file[1],copy=True)
				d_errs = np.sqrt(np.diag(kedd_file[2]))
				sensitivity_coefficient = []
				for idx in range(len(d_pars)):
					d_pars[idx] = d_pars[idx] + d_errs[idx]
					yp = np.exp(d_pars@Wm.T)
					d_pars[idx] = d_pars[idx] - 2*d_errs[idx]
					ym = np.exp(d_pars@Wm.T)
					sensitivity_coefficient.append((yp - ym)/(2 * d_errs[idx]) + 1E-14)
					d_pars[idx] = kedd_file[1][idx]
				sensitivity_coefficient = np.array(sensitivity_coefficient)
				y = float(y)
				uy = np.sqrt((sensitivity_coefficient.T@kedd_file[2])@sensitivity_coefficient)
				uy = float(uy[0])
				ruy = uy / y
				#print(ruy)
				y = 1 / y
				return y, ruy * y
			else:
				return 1.0, 0.0

	def _der(self):
		derm, u_derm, dera, u_dera = 0.0, 0.0, 0.0 ,0.0
		if self.calibration.reference_calibration.distance == self.standard_pos:
			standard_der_file = self.calibration.reference_calibration.der_exponent, self.calibration.reference_calibration.der_parameters, self.calibration.reference_calibration.der_pcov
		else:
			standard_der_file = self.calibration.der_dict.get(self.standard_pos, (None, None, None))
		if self.calibration.reference_calibration.distance == self.sample_pos:
			sample_der_file = self.calibration.reference_calibration.der_exponent, self.calibration.reference_calibration.der_parameters, self.calibration.reference_calibration.der_pcov
		else:
			sample_der_file = self.calibration.der_dict.get(self.sample_pos, (None, None, None))
		if standard_der_file[0] is not None:
			E = np.array([self.std_energy]) / 1000
			W = E[:, np.newaxis]**standard_der_file[0]
			derm = -np.exp(standard_der_file[1]@W.T)
			d_pars = np.array(standard_der_file[1],copy=True)
			d_errs = np.sqrt(np.diag(standard_der_file[2]))
			sensitivity_coefficient = []
			for idx in range(len(d_pars)):
				d_pars[idx] = d_pars[idx] + d_errs[idx]
				yp = -np.exp(d_pars@W.T)
				d_pars[idx] = d_pars[idx] - 2*d_errs[idx]
				ym = -np.exp(d_pars@W.T)
				sensitivity_coefficient.append((yp - ym)/(2 * d_errs[idx]) + 1E-14)
				d_pars[idx] = standard_der_file[1][idx]
			sensitivity_coefficient = np.array(sensitivity_coefficient)
			derm = float(derm)
			u_derm = np.sqrt((sensitivity_coefficient.T@standard_der_file[2])@sensitivity_coefficient)
			u_derm = float(u_derm[0])
		if sample_der_file[0] is not None:
			E = np.array([self.smp_energy]) / 1000
			W = E[:, np.newaxis]**sample_der_file[0]
			dera = -np.exp(sample_der_file[1]@W.T)
			d_pars = np.array(sample_der_file[1],copy=True)
			d_errs = np.sqrt(np.diag(sample_der_file[2]))
			sensitivity_coefficient = []
			for idx in range(len(d_pars)):
				d_pars[idx] = d_pars[idx] + d_errs[idx]
				yp = -np.exp(d_pars@W.T)
				d_pars[idx] = d_pars[idx] - 2*d_errs[idx]
				ym = -np.exp(d_pars@W.T)
				sensitivity_coefficient.append((yp - ym)/(2 * d_errs[idx]) + 1E-14)
				d_pars[idx] = sample_der_file[1][idx]
			sensitivity_coefficient = np.array(sensitivity_coefficient)
			dera = float(dera)
			u_dera = np.sqrt((sensitivity_coefficient.T@sample_der_file[2])@sensitivity_coefficient)
			u_dera = float(u_dera[0])
		return derm, u_derm, dera, u_dera

	def _get_positional_info(self, standard_position, Deltad_standard_spinbox, uDeltad_standard_spinbox, sample_position, Deltad_sample_spinbox, uDeltad_sample_spinbox, regular_calibration_variable):
		stdp = float(standard_position.get())
		try:
			std_dd = float(Deltad_standard_spinbox.get())
		except:
			std_dd = 0.0
		try:
			std_udd = float(uDeltad_standard_spinbox.get())
		except:
			std_udd = 0.0
		smpp = sample_position.get()
		try:
			smp_dd = float(Deltad_sample_spinbox.get())
		except:
			smp_dd = 0.0
		try:
			smp_udd = float(uDeltad_sample_spinbox.get())
		except:
			smp_udd = 0.0
		reg = bool(regular_calibration_variable.get())
		return stdp, std_dd, std_udd, smpp, smp_dd, smp_udd, reg

	def _get_emission_info(self, emission):
		self.dtype = emission.dtype
		if emission.dtype == 'k0':
			self.smp_energy = emission.line[5]
			self.smp_k0, self.smp_uk0 = self._convert_relative_to_absolute(emission.line[7], emission.line[8])
			self.smp_true_coincidence = bool(emission.line[10])
			self.smp_decay_type = emission.line[22]
			self.smp_lambda1, self.smp_ulambda1 = self._convert_to_lambda(emission.line[31], emission.line[32], emission.line[33])
			self.smp_lambda2, self.smp_ulambda2 = self._convert_to_lambda(emission.line[44], emission.line[45], emission.line[46])
			self.smp_lambda3, self.smp_ulambda3 = self._convert_to_lambda(emission.line[57], emission.line[58], emission.line[59])
			self.smp_Q0, self.smp_uQ0 = self._convert_relative_to_absolute(emission.line[75], emission.line[76], 'Q0')
			self.smp_Er, self.smp_uEr = self._convert_relative_to_absolute(emission.line[77], emission.line[78], 'Er')

	def _get_standard_emission_info(self, emission):
		if emission.dtype == 'k0':
			self.std_energy = emission.line[5]
			self.std_k0, self.std_uk0 = self._convert_relative_to_absolute(emission.line[7], emission.line[8])
			self.std_true_coincidence = bool(emission.line[10])
			self.std_decay_type = emission.line[22]
			self.std_lambda1, self.std_ulambda1 = self._convert_to_lambda(emission.line[31], emission.line[32], emission.line[33])
			#self.smp_lambda2, self.smp_ulambda2 = self._convert_to_lambda(emission.line[44], emission.line[45], emission.line[46])
			#self.smp_lambda3, self.smp_ulambda3 = self._convert_to_lambda(emission.line[57], emission.line[58], emission.line[59])
			self.std_Q0, self.std_uQ0 = self._convert_relative_to_absolute(emission.line[75], emission.line[76], 'Q0')
			self.std_Er, self.std_uEr = self._convert_relative_to_absolute(emission.line[77], emission.line[78], 'Er')

	def _convert_relative_to_absolute(self, value, uncertainty, which='k0'):
		if which == 'Q0':
			default = 0.2
		elif which == 'Er':
			default = 0.5
		else:
			default = 0.02
		try:
			ur = float(uncertainty) / 100
			unc = value * ur
		except ValueError:
			unc = value * default
		return value, unc

	def _convert_to_lambda(self, value, unit, unc):
		#convert half-lives to decay constants in s-1
		if unit.lower() == 'y':
			t_conv = 86400 * 365.2422
		elif unit.lower() == 'd':
			t_conv = 86400
		elif unit.lower() == 'h':
			t_conv = 3600
		elif unit.lower() == 'm':
			t_conv = 60
		else:
			t_conv = 1
		try:
			lmb = np.log(2) / (value * t_conv)
		except:
			lmb = 0.0
		try:
			u_lmb = unc / value * lmb
		except:
			u_lmb = 0.0
		return lmb, u_lmb

	def _solve(self, full=False):
		if self.dtype == 'k0' and self.smp_decay_type in ['I', 'IIB', 'IVB', 'VI']:
			return self.target, self.emission, self._solve_typeI(full)
		return self.target, self.emission, None

	def _solve_typeI(self, full=False):#value, uncertainty, DL, z_score, 5major_uncertainty_contributions
		Z_score = np.nan
		DL = np.nan
		if self.smp_np > 0.0:
			#M_data =self._get_array_typeI()[0]
			#M_data = M_data[:,0], M_data[:,1]

			smp_np = self.smp_np - self.bkg_counts - 0.0 - 0.0

			Dtd_m = self.smp_start_counting - self.std_start_counting
			Dtd_m = Dtd_m.total_seconds()
			td_m = self.std_start_counting - self.irradiation.datetime
			td_m = td_m.total_seconds()

			#k0 model type I
			#y = ((self.smp_lambda1 * (smp_np/self.smp_COI) * self.smp_real / self.smp_live * np.exp(self.calibration.mu * (1 - self.smp_live/self.smp_real)) * (1-np.exp(-self.std_lambda1*self.irradiation.irradiation_time)) * (1-np.exp(-self.std_lambda1*self.std_real))) / (self.std_lambda1 * (self.std_np/self.std_COI) * self.std_real / self.std_live * np.exp(self.calibration.mu * (1 - self.std_live/self.std_real)) * (1-np.exp(-self.smp_lambda1*self.irradiation.irradiation_time)) * (1-np.exp(-self.smp_lambda1*self.smp_real)) * (1+self.irradiation.beta*self.smp_Dl)) * np.exp((self.smp_lambda1-self.std_lambda1)*td_m + self.smp_lambda1*Dtd_m) * self.std_k0/self.smp_k0 * (self.std_Gth+self.std_Gepi/self.irradiation.f_value*((self.std_Q0-0.429)/self.std_Er**self.irradiation.a_value+0.429/((1+2*self.irradiation.a_value)*0.55**self.irradiation.a_value)))/(self.smp_Gth+self.smp_Gepi/self.irradiation.f_value*((self.smp_Q0-0.429)/self.smp_Er**self.irradiation.a_value+0.429/((1+2*self.irradiation.a_value)*0.55**self.irradiation.a_value))) * self.keDe * self.keDd * (1+self.std_der*self.standard_dd)/(1+self.smp_der*self.sample_dd) * self.std_mass * self.std_w - self.blank_mass*self.blank_w) / self.smp_mass
			#k0 model type I
			y = ((smp_np * self.smp_lambda1 * self.smp_real * np.exp(self.calibration.mu * (1-self.smp_live/self.smp_real)) * self.std_live * self.std_COI * (1-np.exp(-self.std_lambda1 * self.irradiation.irradiation_time)) * (1-np.exp(-self.std_lambda1 * self.std_real))) / (self.std_np * self.std_lambda1 * self.std_real * np.exp(self.calibration.mu * (1-self.std_live/self.std_real)) * self.smp_live * self.smp_COI * (1-np.exp(-self.smp_lambda1 * self.irradiation.irradiation_time)) * (1-np.exp(-self.smp_lambda1 * self.smp_real))) * np.exp((self.smp_lambda1-self.std_lambda1)*td_m + self.smp_lambda1*Dtd_m) * (1/(1+self.irradiation.beta*self.smp_Dl)) * (self.std_k0/self.smp_k0) * (self.std_Gth+self.std_Gepi/self.irradiation.f_value*((self.std_Q0-0.429)/self.std_Er**self.irradiation.a_value+0.429/((1+2*self.irradiation.a_value)*0.55**self.irradiation.a_value))) / (self.smp_Gth+self.smp_Gepi/self.irradiation.f_value*((self.smp_Q0-0.429)/self.smp_Er**self.irradiation.a_value+0.429/((1+2*self.irradiation.a_value)*0.55**self.irradiation.a_value))) * self.keDe * self.keDd * ((self.standard_pos-self.std_der)/(self.standard_pos+self.standard_dd-self.std_der))**2 / ((self.sample_pos-self.smp_der)/(self.sample_pos+self.sample_dd-self.smp_der))**2 * (1+self.smp_Dh/(self.sample_pos+self.sample_dd-self.smp_der)) / (1+self.std_Dh/(self.standard_pos+self.standard_dd-self.std_der)) * ((1-np.exp(-self.std_murho * self.std_Dh * self.std_density)) / (self.std_murho * self.std_Dh * self.std_density)) / ((1-np.exp(-self.smp_murho * self.smp_Dh * self.smp_density)) / (self.smp_murho * self.smp_Dh * self.smp_density)) * self.std_mass * (1-self.std_moisture) * self.std_w - self.blank_mass*self.blank_w) / (self.smp_mass * (1-self.smp_moisture))

			if self.currie_limit is not None:
				CL = 2.71 + 4.65*np.sqrt(self.currie_limit)
				#DL = ((self.smp_lambda1 * (CL/self.smp_COI) * self.smp_real / self.smp_live * np.exp(self.calibration.mu * (1 - self.smp_live/self.smp_real)) * (1-np.exp(-self.std_lambda1*self.irradiation.irradiation_time)) * (1-np.exp(-self.std_lambda1*self.std_real))) / (self.std_lambda1 * (self.std_np/self.std_COI) * self.std_real / self.std_live * np.exp(self.calibration.mu * (1 - self.std_live/self.std_real)) * (1-np.exp(-self.smp_lambda1*self.irradiation.irradiation_time)) * (1-np.exp(-self.smp_lambda1*self.smp_real)) * (1+self.irradiation.beta*self.smp_Dl)) * np.exp((self.smp_lambda1-self.std_lambda1)*td_m + self.smp_lambda1*Dtd_m) * self.std_k0/self.smp_k0 * (self.std_Gth+self.std_Gepi/self.irradiation.f_value*((self.std_Q0-0.429)/self.std_Er**self.irradiation.a_value+0.429/((1+2*self.irradiation.a_value)*0.55**self.irradiation.a_value)))/(self.smp_Gth+self.smp_Gepi/self.irradiation.f_value*((self.smp_Q0-0.429)/self.smp_Er**self.irradiation.a_value+0.429/((1+2*self.irradiation.a_value)*0.55**self.irradiation.a_value))) * self.keDe * self.keDd * (1+self.std_der*self.standard_dd)/(1+self.smp_der*self.sample_dd) * self.std_mass * self.std_w - self.blank_mass*self.blank_w) / self.smp_mass
				DL = ((CL * self.smp_lambda1 * self.smp_real * np.exp(self.calibration.mu * (1-self.smp_live/self.smp_real)) * self.std_live * self.std_COI * (1-np.exp(-self.std_lambda1 * self.irradiation.irradiation_time)) * (1-np.exp(-self.std_lambda1 * self.std_real))) / (self.std_np * self.std_lambda1 * self.std_real * np.exp(self.calibration.mu * (1-self.std_live/self.std_real)) * self.smp_live * self.smp_COI * (1-np.exp(-self.smp_lambda1 * self.irradiation.irradiation_time)) * (1-np.exp(-self.smp_lambda1 * self.smp_real))) * np.exp((self.smp_lambda1-self.std_lambda1)*td_m + self.smp_lambda1*Dtd_m) * (1/(1+self.irradiation.beta*self.smp_Dl)) * (self.std_k0/self.smp_k0) * (self.std_Gth+self.std_Gepi/self.irradiation.f_value*((self.std_Q0-0.429)/self.std_Er**self.irradiation.a_value+0.429/((1+2*self.irradiation.a_value)*0.55**self.irradiation.a_value))) / (self.smp_Gth+self.smp_Gepi/self.irradiation.f_value*((self.smp_Q0-0.429)/self.smp_Er**self.irradiation.a_value+0.429/((1+2*self.irradiation.a_value)*0.55**self.irradiation.a_value))) * self.keDe * self.keDd * ((self.standard_pos-self.std_der)/(self.standard_pos+self.standard_dd-self.std_der))**2 / ((self.sample_pos-self.smp_der)/(self.sample_pos+self.sample_dd-self.smp_der))**2 * (1+self.smp_Dh/(self.sample_pos+self.sample_dd-self.smp_der)) / (1+self.std_Dh/(self.standard_pos+self.standard_dd-self.std_der)) * ((1-np.exp(-self.std_murho * self.std_Dh * self.std_density)) / (self.std_murho * self.std_Dh * self.std_density)) / ((1-np.exp(-self.smp_murho * self.smp_Dh * self.smp_density)) / (self.smp_murho * self.smp_Dh * self.smp_density)) * self.std_mass * (1-self.std_moisture) * self.std_w) / (self.smp_mass * (1-self.smp_moisture))#- self.blank_mass*self.blank_w deleted!
				#no blank correction in the detection limit!
		else:
			y = np.nan
		if full == False:
			return y
		M_data, cov_matrix = self._get_array_typeI()
		values, uncertainties = M_data[:,0], M_data[:,1]
		values[1], uncertainties[1] = values[1] - self.bkg_counts - 0.0 - 0.0, uncertainties[1]
		comput_values = list(values)
		res = []
		for idx in range(len(values)): #also operate here
			comput_values[idx] = values[idx] + uncertainties[idx]
			#solplus = ((comput_values[2] * (comput_values[1]/comput_values[6]) * comput_values[4] / comput_values[5] * np.exp(comput_values[38] * (1 - comput_values[5]/comput_values[4])) * (1-np.exp(-comput_values[14]*comput_values[0])) * (1-np.exp(-comput_values[14]*comput_values[16]))) / (comput_values[14] * (comput_values[13]/comput_values[18]) * comput_values[16] / comput_values[17] * np.exp(comput_values[38] * (1 - comput_values[17]/comput_values[16])) * (1-np.exp(-comput_values[2]*comput_values[0])) * (1-np.exp(-comput_values[2]*comput_values[4])) * (1+comput_values[36]*comput_values[37])) * np.exp((comput_values[2]-comput_values[14])*comput_values[15] + comput_values[2]*comput_values[3]) * comput_values[21]/comput_values[8] * (comput_values[22]+comput_values[23]/comput_values[26]*((comput_values[24]-0.429)/comput_values[25]**comput_values[27]+0.429/((1+2*comput_values[27])*0.55**comput_values[27])))/(comput_values[9]+comput_values[10]/comput_values[26]*((comput_values[11]-0.429)/comput_values[12]**comput_values[27]+0.429/((1+2*comput_values[27])*0.55**comput_values[27]))) * comput_values[28] * comput_values[29] * (1+comput_values[33]*comput_values[34])/(1+comput_values[30]*comput_values[31]) * comput_values[19] * comput_values[20] - comput_values[40]*comput_values[39]) / comput_values[7]

			solplus = ((comput_values[1]*comput_values[2]*comput_values[4]*np.exp(comput_values[44]*(1-comput_values[5]/comput_values[4]))*comput_values[18]*comput_values[19]*(1-np.exp(-comput_values[15]*comput_values[0]))*(1-np.exp(-comput_values[15]*comput_values[17]))) / (comput_values[14]*comput_values[15]*comput_values[17]*np.exp(comput_values[44]*(1-comput_values[18]/comput_values[17]))*comput_values[5]*comput_values[6]*(1-np.exp(-comput_values[2]*comput_values[0]))*(1-np.exp(-comput_values[2]*comput_values[4]))) * np.exp((comput_values[2]-comput_values[15])*comput_values[16]+comput_values[2]*comput_values[3]) * 1/(1+comput_values[42]*comput_values[43]) * comput_values[23]/comput_values[9] * (comput_values[24]+comput_values[25]/comput_values[28]*((comput_values[26]-0.429)/comput_values[27]**comput_values[29]+0.429/((2*comput_values[29]+1)*0.55**comput_values[29]))) / (comput_values[10]+comput_values[11]/comput_values[28]*((comput_values[12]-0.429)/comput_values[13]**comput_values[29]+0.429/((2*comput_values[29]+1)*0.55**comput_values[29]))) * comput_values[30]*comput_values[31]*((self.standard_pos-comput_values[37])/(self.standard_pos+comput_values[38]-comput_values[37]))**2/((self.sample_pos-comput_values[32])/(self.sample_pos+comput_values[33]-comput_values[32]))**2*(1+comput_values[35]/(self.sample_pos+comput_values[33]-comput_values[32]))/(1+comput_values[40]/(self.standard_pos+comput_values[38]-comput_values[37]))*((1-np.exp(-comput_values[39]*comput_values[40]*comput_values[41]))/(comput_values[39]*comput_values[40]*comput_values[41]))/((1-np.exp(-comput_values[34]*comput_values[35]*comput_values[36]))/(comput_values[34]*comput_values[35]*comput_values[36])) * comput_values[20]*(1-comput_values[21])*comput_values[22]-comput_values[46]*comput_values[45])/(comput_values[7]*(1-comput_values[8]))

			comput_values[idx] = values[idx] - uncertainties[idx]
			#solminus = ((comput_values[2] * (comput_values[1]/comput_values[6]) * comput_values[4] / comput_values[5] * np.exp(comput_values[38] * (1 - comput_values[5]/comput_values[4])) * (1-np.exp(-comput_values[14]*comput_values[0])) * (1-np.exp(-comput_values[14]*comput_values[16]))) / (comput_values[14] * (comput_values[13]/comput_values[18]) * comput_values[16] / comput_values[17] * np.exp(comput_values[38] * (1 - comput_values[17]/comput_values[16])) * (1-np.exp(-comput_values[2]*comput_values[0])) * (1-np.exp(-comput_values[2]*comput_values[4])) * (1+comput_values[36]*comput_values[37])) * np.exp((comput_values[2]-comput_values[14])*comput_values[15] + comput_values[2]*comput_values[3]) * comput_values[21]/comput_values[8] * (comput_values[22]+comput_values[23]/comput_values[26]*((comput_values[24]-0.429)/comput_values[25]**comput_values[27]+0.429/((1+2*comput_values[27])*0.55**comput_values[27])))/(comput_values[9]+comput_values[10]/comput_values[26]*((comput_values[11]-0.429)/comput_values[12]**comput_values[27]+0.429/((1+2*comput_values[27])*0.55**comput_values[27]))) * comput_values[28] * comput_values[29] * (1+comput_values[33]*comput_values[34])/(1+comput_values[30]*comput_values[31]) * comput_values[19] * comput_values[20] - comput_values[40]*comput_values[39]) / comput_values[7]

			solminus = ((comput_values[1]*comput_values[2]*comput_values[4]*np.exp(comput_values[44]*(1-comput_values[5]/comput_values[4]))*comput_values[18]*comput_values[19]*(1-np.exp(-comput_values[15]*comput_values[0]))*(1-np.exp(-comput_values[15]*comput_values[17]))) / (comput_values[14]*comput_values[15]*comput_values[17]*np.exp(comput_values[44]*(1-comput_values[18]/comput_values[17]))*comput_values[5]*comput_values[6]*(1-np.exp(-comput_values[2]*comput_values[0]))*(1-np.exp(-comput_values[2]*comput_values[4]))) * np.exp((comput_values[2]-comput_values[15])*comput_values[16]+comput_values[2]*comput_values[3]) * 1/(1+comput_values[42]*comput_values[43]) * comput_values[23]/comput_values[9] * (comput_values[24]+comput_values[25]/comput_values[28]*((comput_values[26]-0.429)/comput_values[27]**comput_values[29]+0.429/((2*comput_values[29]+1)*0.55**comput_values[29]))) / (comput_values[10]+comput_values[11]/comput_values[28]*((comput_values[12]-0.429)/comput_values[13]**comput_values[29]+0.429/((2*comput_values[29]+1)*0.55**comput_values[29]))) * comput_values[30]*comput_values[31]*((self.standard_pos-comput_values[37])/(self.standard_pos+comput_values[38]-comput_values[37]))**2/((self.sample_pos-comput_values[32])/(self.sample_pos+comput_values[33]-comput_values[32]))**2*(1+comput_values[35]/(self.sample_pos+comput_values[33]-comput_values[32]))/(1+comput_values[40]/(self.standard_pos+comput_values[38]-comput_values[37]))*((1-np.exp(-comput_values[39]*comput_values[40]*comput_values[41]))/(comput_values[39]*comput_values[40]*comput_values[41]))/((1-np.exp(-comput_values[34]*comput_values[35]*comput_values[36]))/(comput_values[34]*comput_values[35]*comput_values[36])) * comput_values[20]*(1-comput_values[21])*comput_values[22]-comput_values[46]*comput_values[45])/(comput_values[7]*(1-comput_values[8]))

			comput_values[idx] = values[idx]
			res.append((solplus-solminus)/(2*uncertainties[idx]+1E-12))
		res = np.array(res)
		uncertainties = np.array(uncertainties)
		indexes = []
		for ii in range(len(uncertainties)):
			count = 0.0
			for dd in range(len(uncertainties)):
				cov_matrix[ii,dd] = cov_matrix[ii,dd] * uncertainties[ii] * uncertainties[dd]
				count += res[ii] * res[dd] * cov_matrix[ii, dd]
			indexes.append(count)
		uy = np.sqrt((res.T@cov_matrix) @ res)
		indexes = np.array(indexes)
		description = [r'$t_\mathrm{i}$',r'$n_\mathrm{p\:a}$',r'$\lambda_\mathrm{a}$',r'$\Delta td_\mathrm{m}$',r'$t_\mathrm{r\:a}$',r'$t_\mathrm{l\:a}$',r'$COI_\mathrm{a}$',r'$m_\mathrm{sm}$',r'$\eta_\mathrm{sm}$',r'$k_\mathrm{0\:Au}(\mathrm{a})$',r'$G_\mathrm{th\:a}$',r'$G_\mathrm{epi\:a}$',r'$Q_\mathrm{0\:a}$',r'$\bar{E}_\mathrm{r\:a}$',r'$n_\mathrm{p\:m}$',r'$\lambda_\mathrm{m}$',r'$td_\mathrm{m}$',r'$t_\mathrm{r\:m}$',r'$t_\mathrm{l\:m}$',r'$COI_\mathrm{m}$',r'$m_\mathrm{std}$',r'$\eta_\mathrm{std}$',r'$w_\mathrm{m}$',r'$k_\mathrm{0\:Au}(\mathrm{m})$',r'$G_\mathrm{th\:m}$',r'$G_\mathrm{epi\:m}$',r'$Q_\mathrm{0\:m}$',r'$\bar{E}_\mathrm{r\:m}$', r'$f$', r'$\alpha$', r'$k_{\varepsilon\Delta E}$', r'$k_{\varepsilon\Delta \mathrm{d_{ref}}}$', r"$d^{\:'}_\mathrm{0\:a}$", r'$\Delta d_\mathrm{a}$',r'$\nu_\mathrm{a}$',r'$h_\mathrm{a}$',r'$\rho_\mathrm{a}$', r"$d^{\:'}_\mathrm{0\:m}$", r'$\Delta d_\mathrm{m}$',r'$\nu_\mathrm{m}$',r'$h_\mathrm{m}$',r'$\rho_\mathrm{m}$',r'$\beta$', r'$\Delta l$',r'$\mu$',r'$w_\mathrm{blank}$',r'$m_\mathrm{blank}$'] #input parameters!
		indexes = [(idx_value / indexes.sum(), tag) for idx_value, tag in zip(indexes, description)]
		indexes.sort(key=lambda x: x[0], reverse=True)
		if self.z_score[0] is not None:
			Z_score = (y - self.z_score[0]) / np.sqrt(np.power(self.z_score[1],2) + np.power(uy,2))
		else:
			Z_score = np.nan
		return y, uy, DL, Z_score, indexes[:5]

	def _get_requests(self):
		if self.smp_decay_type in ['I', 'IIB', 'IVB', 'VI']:
			return 'D55', 'E55', 'D56', 'D57' #value, uncertainty, DL, zscore
		else:
			return 'A1', 'A2', 'A3', 'A4'

    #defaults are important
	def _get_array_typeI(self):
		Dtd_m = self.smp_start_counting - self.std_start_counting
		Dtd_m = Dtd_m.total_seconds()
		td_m = self.std_start_counting - self.irradiation.datetime
		td_m = td_m.total_seconds()
		M_input = np.array([
            [self.irradiation.irradiation_time, self.irradiation.unc_irradiation_time],
            [self.smp_np, self.smp_unp],
            [self.smp_lambda1, self.smp_ulambda1],
            [Dtd_m, self.dafault_times],
            [self.smp_real, self.dafault_times],
            [self.smp_live, self.dafault_times],
            [self.smp_COI, self.smp_uCOI], #COI calculator
            [self.smp_mass, self.smp_umass],
            [self.smp_moisture, self.smp_umoisture],
            [self.smp_k0, self.smp_uk0],
            [self.smp_Gth, self.smp_uGth],
            [self.smp_Gepi, self.smp_uGepi],
            [self.smp_Q0, self.smp_uQ0],
            [self.smp_Er, self.smp_uEr],
            [self.std_np, self.std_unp],
            [self.std_lambda1, self.std_ulambda1],
            [td_m, self.default_td],
            [self.std_real, self.dafault_times],
            [self.std_live, self.dafault_times],
            [self.std_COI, self.std_uCOI], #COI calculator
            [self.std_mass, self.std_umass],
            [self.std_moisture, self.std_umoisture],
            [self.std_w, self.std_uw],
            [self.std_k0, self.std_uk0],
            [self.std_Gth, self.std_uGth],
            [self.std_Gepi, self.std_uGepi],
            [self.std_Q0, self.std_uQ0],
            [self.std_Er, self.std_uEr],
            [self.irradiation.f_value, self.irradiation.unc_f_value],
            [self.irradiation.a_value, self.irradiation.unc_a_value],
            [self.keDe, self.ukeDe],
            [self.keDd, self.ukeDd],
            [self.smp_der, self.smp_uder],
            [self.sample_dd, self.sample_udd],
            [self.smp_murho, self.smp_umurho], #mu sample
            [self.smp_Dh, self.smp_uDh], #h sample
            [self.smp_density, self.smp_udensity], #ro sample
            [self.std_der, self.std_uder],
            [self.standard_dd, self.standard_udd],
            [self.std_murho, self.std_umurho], #mu standard
            [self.std_Dh, self.std_uDh], #h standard
            [self.std_density, self.std_udensity], #ro standard
            [self.irradiation.beta, self.irradiation.unc_beta],
            [self.smp_Dl, self.smp_uDl],
            [self.calibration.mu, self.calibration.u_mu],
            [self.blank_w, self.blank_uw],
            [self.blank_mass, self.blank_umass]
        ])
		# correlation matrix
		if self.detection_limit == False:
			M_corr = np.identity(len(M_input))
			# condition for same emitting isotope
			if self.std_Q0 == self.smp_Q0 and self.std_Er == self.smp_Er:
				M_corr[2,15], M_corr[15,2] = 1.0, 1.0 #lambda
				M_corr[12,26], M_corr[26,12] = 1.0, 1.0 #Q0
				M_corr[13,27], M_corr[27,13] = 1.0, 1.0 #Er
				# relative analysis conditions
				if self.std_energy == self.smp_energy and self.std_k0 == self.smp_k0:
					M_corr[9,23], M_corr[23,9] = 1.0, 1.0 #k0
					#full relative analysis
					if self.standard_pos == self.sample_pos: 
						M_corr[6,19], M_corr[19,6] = 1.0, 1.0 #COI
						M_corr[32,37], M_corr[37,32] = 1.0, 1.0 #d0
		else:
			M_corr = None
		return M_input, M_corr


class Emission:
	"""
	Store information relative to identified emissions.
	"""
	def __init__(self,dtype,line):
		self.dtype,self.target,self.energy,self.emission = self._decrypt(dtype,line)
		self.line = line

	def _decrypt(self,dtype,line):
		if dtype == 'k0':
			target = line[1]
			energy = line[5]
			emission = f'{line[2]}-{int(line[3])}{self._state(line[4])} {line[5]} keV'
		return dtype,target,energy,emission

	def _state(self,identifier):
		if int(float(identifier)) == 2:
			return 'm'
		else:
			return ''


class GSourceEmission:
	"""
	Store information relative to identified gamma source emissions.
	"""
	def __init__(self,energy,emitter,reference):
		self.reference,self.emission = self._decrypt(energy, emitter, reference)

	def _decrypt(self,energy, emitter, reference):
		target = emitter
		energy = energy
		emission = f'{target} {energy} keV'
		return reference,emission


class ExcelOutput:
    def __init__(self, filename, NAA, M, budgets, btype='target'):
        wb = xlsxwriter.Workbook(filename, {'nan_inf_to_errors': True})
        self.font_bold = wb.add_format({'bold': True})
        self.font_ital = wb.add_format({'italic': True})
        self.font_result = wb.add_format(
            {'bold': True, 'font_color': 'green', 'num_format': '0.00E+00'})
        self.font_uncresult = wb.add_format(
            {'bold': True, 'font_color': 'green', 'num_format': '0.0E+00'})
        self.font_pct = wb.add_format({'num_format': 0x0a})
        self.font_DL = wb.add_format(
            {'bold': True, 'font_color': '#FF6347', 'num_format': '0.0E+00'})
        self.font_zscore = wb.add_format(
            {'bold': True, 'font_color': '#2A2CC9', 'num_format': '0.0'})
        self.font_sups = wb.add_format({'font_script': 1})
        self.font_subs = wb.add_format({'font_script': 2})
        self.font_gray = wb.add_format({'font_color': 'gray'})
        self.font_grayit = wb.add_format({'italic': True, 'font_color': 'gray'})
        self.font_graysub = wb.add_format({'font_script': 2, 'font_color': 'gray'})
        self.font_graypct = wb.add_format({'num_format': 0x0a, 'font_color': 'gray'})
        self.font_dateandtime = wb.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
        self.grey_header = wb.add_format({'bg_color': '#e7e6e6', 'font_color': 'black', 'bold': True})
        self.grey_info = wb.add_format({'bg_color': '#e7e6e6', 'font_color': 'black', 'italic': True, 'left': 3})
        self.grey_fill = wb.add_format({'bg_color': '#e7e6e6', 'font_color': 'black'})
        try:
            self.font_sym = wb.add_format({'font_name': 'Symbol'})
            self.font_graysym = wb.add_format({'font_name': 'Symbol', 'font_color': 'gray'})
        except:
            self.font_sym = wb.add_format({'font_name': 'Times New Roman'})
            self.font_graysym = wb.add_format(
                {'font_name': 'Times New Roman', 'font_color': 'gray'})

        if btype == 'target':
            self._summary_worksheet(wb, NAA, M, budgets, btype)
        else:
            self._summary_worksheet_spectra(wb, NAA, M, budgets, btype)
        wmodel = wb.add_worksheet('Models')
        self.display_models(wmodel)
        wb.close()

    def display_models(self, wsheet):
        wsheet.insert_image(0,0,'data/models/model_I.png')
        wsheet.set_column(0, 0, 250)
        wsheet.set_row(0, 100)
        parameters_line = 2
        wsheet.write(parameters_line, 0, 'Parameters', self.font_bold)
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'w', self.font_subs, 'a', ' : mass fraction of analyte in the sample / g g', self.font_sups, '-1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'l', self.font_subs, 'a', ' : decay constant of analyte emitter / s', self.font_sups, '-1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'n', self.font_subs, 'p a', ' : net peak area (corrected for counts due to background, interferent peaks and fast activations) of analyte / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'COI', self.font_subs, 'a', ' : true coincidence correction factor for analyte emission / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 't', self.font_subs, 'c a', ' : real counting time of sample spectrum / s')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 't', self.font_subs, 'l a', ' : live counting time of sample spectrum / s')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'm', ' : excess counting loss constant of the detection system / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 't', self.font_subs, 'i', ' : irradiation time of sample and standard / s')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'l', self.font_subs, 'm', ' : decay constant of monitor emitter / s', self.font_sups, '-1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'n', self.font_subs, 'p m', ' : net peak area (corrected for counts due to background, interferent peaks and fast activations) of monitor / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'COI', self.font_subs, 'm', ' : true coincidence correction factor for monitor emission / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 't', self.font_subs, 'c m', ' : real counting time of standard spectrum / s')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 't', self.font_subs, 'l m', ' : live counting time of standard spectrum / s')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 't', self.font_subs, 'd m', ' : decay time between start of standard spectrum and irradiation end / s')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'D', self.font_ital, 't', self.font_subs, 'd', ' : decay time between start of sample spectrum and start of standard spectrum / s')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'b', ' : vertical count rate gradient due to unit distance of irradiation position / mm', self.font_sups, '-1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'D', self.font_ital, 'l', ' : vertical distance of sample from standard during irradiation / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'k', self.font_subs, '0 Au', '(m) : ', self.font_ital, 'k', self.font_subs, '0', ' constant referred to monitor emission / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'k', self.font_subs, '0 Au', '(a) : ', self.font_ital, 'k', self.font_subs, '0', ' constant referred to analyte emission / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'G', self.font_subs, 'th m', ' : thermal neutron self-shielding correction factor on standard sample / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'G', self.font_subs, 'e m', ' : epithermal neutron self-shielding correction factor on standard sample / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'f', ' : thermal to epithermal flux ratio / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'Q', self.font_subs, '0 m', ' : resonance integral to thermal cross section ratio for monitor target / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'E', self.font_subs, 'r m', ' : effective resonance energy for monitor target / eV')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'a', ' : correction to the E', self.font_sups, '-1', 'epithermal flux trend / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'G', self.font_subs, 'th a', ' : thermal neutron self-shielding correction factor on sample / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'G', self.font_subs, 'e a', ' : epithermal neutron self-shielding correction factor on sample / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'Q', self.font_subs, '0 a', ' : resonance integral to thermal cross section ratio for analyte target / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'E', self.font_subs, 'r a', ' : effective resonance energy for analyte target / eV')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'k', self.font_subs, 'eDE', ' : efficiency ratio at reference position / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'k', self.font_subs, 'eDd ref', ' : efficiency ratio at nominal counting distance with respect to the reference position / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, 'd', self.font_subs, 'ref m', ' : nominal standard counting distance to the detector end-cap (treated as a constant and not included in the uncertainty budget) / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, "d'", self.font_subs, '0 m', ' : distance travelled by the gamma emission of monitor within the detector / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'D', self.font_ital, 'd', self.font_subs, 'm', ' : local difference between the experimental and nominal standard counting distance / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, 'd', self.font_subs, 'ref a', ' : nominal sample counting distance to the detector end-cap (treated as a constant and not included in the uncertainty budget) / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, "d'", self.font_subs, '0 a', ' : distance travelled by the gamma emission of analyte within the detector / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'D', self.font_ital, 'd', self.font_subs, 'a', ' : local difference between the experimental and nominal sample counting distance / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'n', self.font_subs, 'm', ' : mass attenuation coefficient of the monitor gamma emission within the standard / mm', self.font_sups, '2', ' g', self.font_sups, '-1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'h', self.font_subs, 'm', ' : height of the standard / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'r', self.font_subs, 'm', ' : density of the standard / g mm', self.font_sups, '-3')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'n', self.font_subs, 'a', ' : mass attenuation coefficient of the analyte gamma emission within the sample / mm', self.font_sups, '2', ' g', self.font_sups, '-1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'h', self.font_subs, 'a', ' : height of the sample / mm')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'r', self.font_subs, 'a', ' : density of the sample / g mm', self.font_sups, '-3')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'm', self.font_subs, 'std', ' : weighted mass of the standard / g')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'h', self.font_subs, 'std', ' : relative moisture content of the standard / 1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'w', self.font_subs, 'm', ' : mass fraction of monitor element in the standard / g g', self.font_sups, '-1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'm', self.font_subs, 'blank', ' : weighted mass of the blank container / g')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'w', self.font_subs, 'blank', ' : mass fraction of analyte element in the blank / g g', self.font_sups, '-1')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_ital, 'm', self.font_subs, 'smp', ' : weighted mass of the sample / g')
        parameters_line += 1
        wsheet.write_rich_string(parameters_line,0, self.font_sym, 'h', self.font_subs, 'smp', ' : relative moisture content of the sample / 1')
        parameters_line += 1

    def _summary_worksheet_spectra(self, wb, NAA, M, budgets, btype):
        ws = wb.add_worksheet('Analysis')
        ws.set_column('A:A', 16)
        # ws.set_column('F:F', 10)
        #ws.set_column('F:H', 12)
        #ws.set_column('M:M', 13)
        ws.write(0, 0, 'irradiation end')
        ws.write_rich_string(0, 2, self.font_ital, 't', self.font_subs, 'i', ' / s')
        ws.write(0, 4, 'channel')
        ws.write_rich_string(0, 5, self.font_ital, 'f', ' / 1')
        ws.write_rich_string(0, 6, self.font_sym, 'a', ' / 1')
        ws.write(0, 8, 'calibration name')
        ws.write(0, 10, 'detector')
        ws.write(0, 11, 'd ref / mm')
        ws.write(0, 13, 'k0-INRIM version: 2.1')
        ws.write(1, 13, f'database version: {NAA.settings_dict["database"]}')
        ws.write(1, 0, NAA.irradiation.datetime, self.font_dateandtime)
        ws.write(1, 2, NAA.irradiation.irradiation_time)
        ws.write(1, 4, NAA.irradiation.channel_name)
        ws.write(1, 5, NAA.irradiation.f_value)
        ws.write(1, 6, NAA.irradiation.a_value)
        ws.write(1, 8, NAA.calibration.name)
        ws.write(1, 10, NAA.calibration.detector)
        ws.write(1, 11, NAA.calibration.get_distance(M.standard_position.get(),M.sample_position.get()))
        ws.write(3, 0, 'Standard', self.font_bold)
        idx = 4
        for spectrum in NAA.standard_spectra:
            ws.write(idx, 0, 'name')
            ws.write(idx, 1, spectrum.filename())
            idx += 1
            ws.write(idx, 0, 'start acquisition')
            ws.write_rich_string(idx, 2, self.font_ital,'t',self.font_subs,'real',' / s')
            ws.write_rich_string(idx, 3, self.font_ital,'t',self.font_subs,'live',' / s')
            ws.write_rich_string(idx, 4, self.font_ital,'t',self.font_subs,'dead',' / 1')
            ws.write_rich_string(idx, 5, self.font_ital,'t',self.font_subs,'d',' / s')
            ws.write_rich_string(idx, 6, self.font_ital,'m',' / g')
            ws.write(idx, 7, 'monitor')
            idx += 1
            ws.write(idx, 0, spectrum.datetime, self.font_dateandtime)
            ws.write(idx, 2, spectrum.real_time)
            ws.write(idx, 3, spectrum.live_time)
            fml = f'=(C{idx+1}-D{idx+1})/C{idx+1}'
            ws.write(idx, 4, fml, self.font_pct)
            fml = f'=(A{idx+1}-A2)*86400'
            ws.write(idx, 5, fml)
            ws.write(idx, 6, spectrum.sample.mass)
            ws.write(idx, 7, spectrum.get_k0_monitor().emission)
            idx += 1
        idx += 1
        ws.write(idx, 0, 'Sample', self.font_bold)
        idx += 1
        for block, spectrum in zip(budgets, NAA.sample_spectra): 
            idx = self._result_block_spectrum(wb, ws, idx, block, spectrum, M)

    def _summary_worksheet(self, wb, NAA, M, budgets, btype):
        ws = wb.add_worksheet('Analysis')
        ws.set_column('A:A', 16)
        # ws.set_column('F:F', 10)
        #ws.set_column('F:H', 12)
        #ws.set_column('M:M', 13)
        ws.write(0, 0, 'irradiation end')
        ws.write_rich_string(0, 2, self.font_ital, 't', self.font_subs, 'i', ' / s')
        ws.write(0, 4, 'channel')
        ws.write_rich_string(0, 5, self.font_ital, 'f', ' / 1')
        ws.write_rich_string(0, 6, self.font_sym, 'a', ' / 1')
        ws.write(0, 8, 'calibration name')
        ws.write(0, 10, 'detector')
        ws.write(0, 11, 'd ref / mm')
        ws.write(0, 13, 'k0-INRIM version: 2.1')
        ws.write(1, 13, f'database version: {NAA.settings_dict["database"]}')
        ws.write(1, 0, NAA.irradiation.datetime, self.font_dateandtime)
        ws.write(1, 2, NAA.irradiation.irradiation_time)
        ws.write(1, 4, NAA.irradiation.channel_name)
        ws.write(1, 5, NAA.irradiation.f_value)
        ws.write(1, 6, NAA.irradiation.a_value)
        ws.write(1, 8, NAA.calibration.name)
        ws.write(1, 10, NAA.calibration.detector)
        ws.write(1, 11, NAA.calibration.get_distance(M.standard_position.get(),M.sample_position.get()))

        ws.write(3, 0, 'Standard', self.font_bold)
        ws.write(4, 0, 'start acquisition')
        ws.write(4, 1, 'name')
        ws.write_rich_string(4, 2, self.font_ital,'t',self.font_subs,'real',' / s')
        ws.write_rich_string(4, 3, self.font_ital,'t',self.font_subs,'live',' / s')
        ws.write_rich_string(4, 4, self.font_ital,'t',self.font_subs,'dead',' / 1')
        ws.write_rich_string(4, 5, self.font_ital,'t',self.font_subs,'d',' / s')

        ws.write_rich_string(4, 6, self.font_ital,'m',' / g')
        ws.write(4, 7, 'monitor')
        idx = 5
        for spectrum in NAA.standard_spectra:
            ws.write(idx, 0, spectrum.datetime, self.font_dateandtime)
            ws.write(idx, 1, spectrum.filename())
            ws.write(idx, 2, spectrum.real_time)
            ws.write(idx, 3, spectrum.live_time)
            fml = f'=(C{idx+1}-D{idx+1})/C{idx+1}'
            ws.write(idx, 4, fml, self.font_pct)
            fml = f'=(A{idx+1}-A2)*86400'
            ws.write(idx, 5, fml)
            ws.write(idx, 6, spectrum.sample.mass)
            ws.write(idx, 7, spectrum.get_k0_monitor().emission)
            idx += 1

        idx += 1
        ws.write(idx, 0, 'Sample', self.font_bold)
        idx += 1
        ws.write(idx, 0, 'start acquisition')
        ws.write(idx, 1, 'name')
        ws.write_rich_string(idx, 2, self.font_ital,'t',self.font_subs,'real',' / s')
        ws.write_rich_string(idx, 3, self.font_ital,'t',self.font_subs,'live',' / s')
        ws.write_rich_string(idx, 4, self.font_ital,'t',self.font_subs,'dead',' / 1')
        ws.write_rich_string(idx, 5, self.font_ital,'t',self.font_subs,'d',' / s')
        ws.write_rich_string(idx, 6, self.font_ital,'m',' / g')
        ws.write(idx, 7, 'spectrum code')
        idx += 1

        for spectrum in NAA.sample_spectra:
            ws.write(idx, 0, spectrum.datetime, self.font_dateandtime)
            ws.write(idx, 1, spectrum.filename())
            ws.write(idx, 2, spectrum.real_time)
            ws.write(idx, 3, spectrum.live_time)
            fml = f'=(C{idx+1}-D{idx+1})/C{idx+1}'
            ws.write(idx, 4, fml, self.font_pct)
            fml = f'=(A{idx+1}-A2)*86400'
            ws.write(idx, 5, fml)
            ws.write(idx, 6, spectrum.sample.mass)
            ws.write(idx, 7, f'#{NAA.sample_spectra.index(spectrum)+1}')
            idx += 1

        idx += 1
        for block in budgets:
            idx = self._result_block(wb, ws, idx, block, M)

    def _result_block_spectrum(self, wb, ws, index, results, spectrum, M):
        ws.write(index, 0, 'name', self.grey_info)
        ws.write(index, 1, spectrum.filename(), self.font_bold)
        index += 1
        ws.write(index, 0, 'spectrum info', self.grey_info)
        ws.write(index, 1, '', self.grey_fill)
        ws.write(index, 2, '', self.grey_fill)
        ws.write(index, 3, '', self.grey_fill)
        ws.write(index, 4, '', self.grey_fill)
        ws.write(index, 5, '', self.grey_fill)
        ws.write(index, 6, '', self.grey_fill)
        ws.write(index, 7, '', self.grey_fill)
        index += 1
        ws.write(index, 0, 'start acquisition')
        ws.write_rich_string(index, 2, self.font_ital,'t',self.font_subs,'real',' / s')
        ws.write_rich_string(index, 3, self.font_ital,'t',self.font_subs,'live',' / s')
        ws.write_rich_string(index, 4, self.font_ital,'t',self.font_subs,'dead',' / 1')
        ws.write_rich_string(index, 5, self.font_ital,'t',self.font_subs,'d',' / s')
        ws.write_rich_string(index, 6, self.font_ital,'m',' / g')
        ws.write(index, 7, '', self.grey_fill)
        index += 1
        ws.write(index, 0, spectrum.datetime, self.font_dateandtime)
        ws.write(index, 2, spectrum.real_time)
        ws.write(index, 3, spectrum.live_time)
        fml = f'=(C{index+1}-D{index+1})/C{index+1}'
        ws.write(index, 4, fml, self.font_pct)
        fml = f'=(A{index+1}-A2)*86400'
        ws.write(index, 5, fml)
        ws.write(index, 6, spectrum.sample.mass)
        ws.write(index, 7, '', self.grey_fill)
        index += 1
        ws.write(index, 0, 'element', self.grey_info)
        ws.write(index, 1, 'result', self.grey_info)
        ws.write(index, 2, '', self.grey_fill)
        ws.write(index, 3, '', self.grey_fill)
        ws.write(index, 4, 'info', self.grey_info)
        ws.write(index, 5, '', self.grey_fill)
        ws.write(index, 6, '', self.grey_fill)
        ws.write(index, 7, '', self.grey_fill)
        index += 1
        ws.write(index, 0, 'target')
        ws.write_rich_string(index, 1, self.font_ital,'w',self.font_subs,'a',' / g g',self.font_sups,'-1')
        ws.write_rich_string(index, 2, self.font_ital,'u','(',self.font_ital,'w',self.font_subs,'a',') / g g',self.font_sups,'-1')
        ws.write_rich_string(index, 3, self.font_ital,'u',self.font_subs,'r','(',self.font_ital,'w',self.font_subs,'a',') / 1')
        ws.write_rich_string(index, 4, 'DL / < g g',self.font_sups,'-1')
        ws.write(index, 5, 'emitter')
        ws.write_rich_string(index, 6, self.font_ital,'E',' / keV')
        ws.write(index, 7, 'budget')

        for i in range(len(results)):
            index += 1
            ws.write(index, 0, results[i].target)
            link_result = f"='{results[i]._get_code()}'!{results[i]._get_requests()[0]}"
            ws.write(index, 1, link_result, self.font_result)
            link_unc_result = f"='{results[i]._get_code()}'!{results[i]._get_requests()[1]}"
            ws.write(index, 2, link_unc_result, self.font_uncresult)
            fml = f'=IFERROR(ABS(C{index+1}/B{index+1}),"-")'
            ws.write(index, 3, fml, self.font_pct)
            link_DL = f"='{results[i]._get_code()}'!{results[i]._get_requests()[2]}"
            ws.write(index, 4, link_DL, self.font_DL)
            Eemitter, Eenergy = results[i].emission.replace(" keV", "").split()
            ws.write(index, 5, Eemitter)#emitter
            ws.write(index, 6, Eenergy)#energy

            if results[i].westcott_warning:
                ws.write(index, 10, '*non-1/v reaction, Westcott should be used')

            # Link to a cell on the current workbook.
            # worksheet.write_url('A1', 'internal:Sheet2!A1')
            ws.write_url(f'H{index+1}', f"internal:'{results[i]._get_code()}'!A1")

            #create_budget
            ws_bud = wb.add_worksheet(results[i]._get_code())
            self._write_budget(ws_bud, results[i])
            M.progress['value'] += 1
            M.progress.update()
        
        index += 3
        return index

    def _result_block(self, wb, ws, index, results, M):
        ws.write(index, 0, results[0].target, self.grey_header)
        ws.write(index, 1, 'result', self.grey_info)
        ws.write(index, 2, '', self.grey_fill)
        ws.write(index, 3, '', self.grey_fill)
        ws.write(index, 4, 'info', self.grey_info)
        ws.write(index, 5, '', self.grey_fill)
        ws.write(index, 6, '', self.grey_fill)
        ws.write(index, 7, '', self.grey_fill)
        ws.write(index, 8, '', self.grey_fill)
        ws.write(index, 9, '', self.grey_fill)
        ws.write(index, 10, '', self.grey_fill)
        ws.write(index, 11, '', self.grey_fill)
        ws.write(index, 12, '', self.grey_fill)
        ws.write(index, 13, '', self.grey_fill)
        ws.write(index, 14, '', self.grey_fill)
        ws.write(index, 15, '', self.grey_fill)
        ws.write(index, 16, '', self.grey_fill)
        index += 1
        ws.write_rich_string(index, 1, self.font_ital,'w',self.font_subs,'a',' / g g',self.font_sups,'-1')
        ws.write_rich_string(index, 2, self.font_ital,'u','(',self.font_ital,'w',self.font_subs,'a',') / g g',self.font_sups,'-1')
        ws.write_rich_string(index, 3, self.font_ital,'u',self.font_subs,'r','(',self.font_ital,'w',self.font_subs,'a',') / 1')
        ws.write_rich_string(index, 4, 'DL / < g g',self.font_sups,'-1')
        ws.write(index, 5, 'emitter')
        ws.write_rich_string(index, 6, self.font_ital,'E',' / keV')
        ws.write(index, 7, 'spectrum')
        ws.write(index, 8, 'budget')
        ws.write(index, 16, '', self.grey_fill)
        start = index + 1
        ymin, ymax = None, None
        for i in range(len(results)):
            index += 1
            link_result = f"='{results[i]._get_code()}'!{results[i]._get_requests()[0]}"
            ws.write(index, 1, link_result, self.font_result)
            link_unc_result = f"='{results[i]._get_code()}'!{results[i]._get_requests()[1]}"
            ws.write(index, 2, link_unc_result, self.font_uncresult)
            fml = f'=IFERROR(ABS(C{index+1}/B{index+1}),"-")'
            ws.write(index, 3, fml, self.font_pct)
            link_DL = f"='{results[i]._get_code()}'!{results[i]._get_requests()[2]}"
            ws.write(index, 4, link_DL, self.font_DL)
            Eemitter, Eenergy = results[i].emission.replace(" keV", "").split()
            ws.write(index, 5, Eemitter)#emitter
            ws.write(index, 6, Eenergy)#energy
            ws.write(index, 7, results[i].spectrum_code)#spectrum

            # Link to a cell on the current workbook.
            # worksheet.write_url('A1', 'internal:Sheet2!A1')
            ws.write_url(f'I{index+1}', f"internal:'{results[i]._get_code()}'!A1")
            ws.write(index, 9, f'=C{index+1}*2')
            ws.write(index, 16, '', self.grey_fill)

            if results[i].westcott_warning:
                ws.write(index, 0, '*non-1/v reaction, Westcott should be used')

            #create_budget
            ws_bud = wb.add_worksheet(results[i]._get_code())
            self._write_budget(ws_bud, results[i])
            M.progress['value'] += 1
            M.progress.update()

            y_prov = results[i]._solve()[-1]
            if y_prov is not None:
                if 0.0 < y_prov <= 1.0:
                    if ymin is not None and ymax is not None:
                        if y_prov < ymin:
                            ymin = y_prov
                        if y_prov > ymax:
                            ymax = y_prov
                    else:
                        ymin, ymax = y_prov, y_prov
        #graph
        if ymin is not None and ymax is not None:
            ymin, ymax = ymin*0.7, ymax*1.3
        else:
            ymin, ymax = 0.0, 1.0
        x_size = 7
        y_size = 11
        chart = wb.add_chart({'type': 'line'})
        chart.add_series({'values': f'=Analysis!$B${start+1}:$B${start+len(results)}','marker': {'type': 'circle', 'size': 5, 'border': {'color': 'black'}, 'fill': {'color': 'black'}}, 'line': {'none': True}, 'y_error_bars': {'type' : 'custom', 'plus_values': f'=Analysis!$J${start+1}:$J${start+len(results)}', 'minus_values': f'=Analysis!$J${start+1}:$J${start+len(results)}'}})
        chart.set_y_axis({'name': 'w / g g-1', 'name_font': {'size': 11}, 'num_format': '0.00E+00', 'min': ymin, 'max': ymax})
        chart.set_legend({'none': True})
        chart.set_title({'name': f'=Analysis!$A${start-1}', 'name_font': {'size': 14}})
        chart.set_size({'width': x_size*64, 'height': y_size*20})
        ws.insert_chart(start-1, 9, chart)

        if index - start < 10:
            while index - start < 10:
                index += 1
                ws.write(index, 16, '', self.grey_fill)
        else:
            index += 1
            ws.write(index, 16, '', self.grey_fill)
        index += 1
        ws.write(index, 16, '', self.grey_fill)

        return index

    def _write_budget(self, w_bud, budget):
        if budget.smp_decay_type in ['I', 'IIB', 'IVB', 'VI']:
            self._wbudget_typeI(w_bud, budget)
        else:
            self._wbudget_type_NotImplemented(w_bud, budget)

    def _wbudget_typeI(self, w_bud, budget):
        data, corr = budget._get_array_typeI()
        w_bud.write(0, 0, 'Target')
        w_bud.write(0, 1, budget.target, self.font_bold)
        w_bud.write(0, 2, 'Emitter')
        Eemitter, Eenergy = budget.emission.replace(" keV", "").split()
        w_bud.write(0, 3, Eemitter, self.font_bold)
        w_bud.write_rich_string(0, 4, 'E', self.font_subs, 'p', ' / keV')
        w_bud.write(0, 5, Eenergy, self.font_bold)
        w_bud.set_column('I:I', 14)
        w_bud.set_column('L:L', 12)

        w_bud.write(2, 0, 'Quantity')
        w_bud.write(2, 2, 'Unit')
        w_bud.write(2, 3, 'Value')
        if corr is not None:
            w_bud.write(2, 4, 'Std unc')
            w_bud.write(2, 5, 'Rel unc')
            w_bud.write(2, 8, 'Sensitivity coef.')
            w_bud.write(2, 9, 'Contribution to variance')
        w_bud.write_rich_string(3, 0, self.font_ital, 'X', self.font_subs, 'i')
        w_bud.write_rich_string(3, 2, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        w_bud.write_rich_string(3, 3, self.font_ital, 'x', self.font_subs, 'i')

        if corr is not None:
            w_bud.write_rich_string(3, 4, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
            w_bud.write_rich_string(3, 5, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
            w_bud.write_rich_string(3, 6, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
            w_bud.write_rich_string(3, 7, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
            w_bud.write_rich_string(3, 8, self.font_ital, 'c', self.font_subs, 'i')
            w_bud.write_rich_string(3, 9, self.font_ital, 'I', ' / %')
            w_bud.write(3, 11, 'Corr. Matrix')
            w_bud.write(3, 61, 'Cov. Matrix')
        w_bud.write_rich_string(4, 0, self.font_ital, 't', self.font_subs, 'i')
        w_bud.write(4, 2, 's')
        parm_id = ['D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20', 'D21', 'D22', 'D23', 'D24', 'D25', 'D26', 'D27', 'D28', 'D29', 'D30', 'D31', 'D32', 'D33', 'D34', 'D35', 'D36', 'D37', 'D38', 'D39', 'D40', 'D41', 'D42', 'D43', 'D44', 'D45', 'D46', 'D47', 'D48', 'D49', 'D50', 'D51']
        parm_id_plus = []
        parm_id_minus = []

        for iny in parm_id:
            piny = '('+iny+'+'+iny.replace('D', 'E')+'+1E-9)'
            miny = '('+iny+'-'+iny.replace('D', 'E')+'-1E-9)'
            parm_id_plus.append(piny)
            parm_id_minus.append(miny)
        for ti in range(len(data)):
            w_bud.write(4+ti, 3, data[ti, 0])
            if corr is not None:
                w_bud.write(4+ti, 4, data[ti, 1])
                fml = f'=IFERROR(ABS(E{4+ti+1}/D{4+ti+1}),"-")'
                w_bud.write_formula(4+ti, 5, fml, self.font_pct)
                parm_id[ti] = parm_id_plus[ti]
                
                fml = f'=(({parm_id[1]}*{parm_id[2]}*{parm_id[4]}*EXP({parm_id[44]}*(1-{parm_id[5]}/{parm_id[4]}))*{parm_id[18]}*{parm_id[19]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*(1-EXP(-{parm_id[15]}*{parm_id[17]}))) / ({parm_id[14]}*{parm_id[15]}*{parm_id[17]}*EXP({parm_id[44]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[5]}*{parm_id[6]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*(1-EXP(-{parm_id[2]}*{parm_id[4]}))) * EXP(({parm_id[2]}-{parm_id[15]})*{parm_id[16]}+{parm_id[2]}*{parm_id[3]}) * 1/(1+{parm_id[42]}*{parm_id[43]}) * {parm_id[23]}/{parm_id[9]} * ({parm_id[24]}+{parm_id[25]}/{parm_id[28]}*(({parm_id[26]}-0.429)/{parm_id[27]}^{parm_id[29]}+0.429/((2*{parm_id[29]}+1)*0.55^{parm_id[29]}))) / ({parm_id[10]}+{parm_id[11]}/{parm_id[28]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[29]}+0.429/((2*{parm_id[29]}+1)*0.55^{parm_id[29]}))) * {parm_id[30]}*{parm_id[31]}*(({budget.standard_pos}-{parm_id[37]})/({budget.standard_pos}+{parm_id[38]}-{parm_id[37]}))^2/(({budget.sample_pos}-{parm_id[32]})/({budget.sample_pos}+{parm_id[33]}-{parm_id[32]}))^2*(1+{parm_id[35]}/({budget.sample_pos}+{parm_id[33]}-{parm_id[32]}))/(1+{parm_id[40]}/({budget.standard_pos}+{parm_id[38]}-{parm_id[37]}))*((1-EXP(-{parm_id[39]}*{parm_id[40]}*{parm_id[41]}))/({parm_id[39]}*{parm_id[40]}*{parm_id[41]}))/((1-EXP(-{parm_id[34]}*{parm_id[35]}*{parm_id[36]}))/({parm_id[34]}*{parm_id[35]}*{parm_id[36]})) * {parm_id[20]}*(1-{parm_id[21]})*{parm_id[22]}-{parm_id[46]}*{parm_id[45]})/({parm_id[7]}*(1-{parm_id[8]}))'
                w_bud.write(4+ti, 6, fml, self.font_gray)
                parm_id[ti] = parm_id_minus[ti]
                
                fml = f'=(({parm_id[1]}*{parm_id[2]}*{parm_id[4]}*EXP({parm_id[44]}*(1-{parm_id[5]}/{parm_id[4]}))*{parm_id[18]}*{parm_id[19]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*(1-EXP(-{parm_id[15]}*{parm_id[17]}))) / ({parm_id[14]}*{parm_id[15]}*{parm_id[17]}*EXP({parm_id[44]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[5]}*{parm_id[6]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*(1-EXP(-{parm_id[2]}*{parm_id[4]}))) * EXP(({parm_id[2]}-{parm_id[15]})*{parm_id[16]}+{parm_id[2]}*{parm_id[3]}) * 1/(1+{parm_id[42]}*{parm_id[43]}) * {parm_id[23]}/{parm_id[9]} * ({parm_id[24]}+{parm_id[25]}/{parm_id[28]}*(({parm_id[26]}-0.429)/{parm_id[27]}^{parm_id[29]}+0.429/((2*{parm_id[29]}+1)*0.55^{parm_id[29]}))) / ({parm_id[10]}+{parm_id[11]}/{parm_id[28]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[29]}+0.429/((2*{parm_id[29]}+1)*0.55^{parm_id[29]}))) * {parm_id[30]}*{parm_id[31]}*(({budget.standard_pos}-{parm_id[37]})/({budget.standard_pos}+{parm_id[38]}-{parm_id[37]}))^2/(({budget.sample_pos}-{parm_id[32]})/({budget.sample_pos}+{parm_id[33]}-{parm_id[32]}))^2*(1+{parm_id[35]}/({budget.sample_pos}+{parm_id[33]}-{parm_id[32]}))/(1+{parm_id[40]}/({budget.standard_pos}+{parm_id[38]}-{parm_id[37]}))*((1-EXP(-{parm_id[39]}*{parm_id[40]}*{parm_id[41]}))/({parm_id[39]}*{parm_id[40]}*{parm_id[41]}))/((1-EXP(-{parm_id[34]}*{parm_id[35]}*{parm_id[36]}))/({parm_id[34]}*{parm_id[35]}*{parm_id[36]})) * {parm_id[20]}*(1-{parm_id[21]})*{parm_id[22]}-{parm_id[46]}*{parm_id[45]})/({parm_id[7]}*(1-{parm_id[8]}))'
                w_bud.write(4+ti, 7, fml, self.font_gray)
                fml = '=(G'+str(4+ti+1)+'-H'+str(4+ti+1) + \
                    ')/(2*E'+str(4+ti+1)+'+2E-9)'
                w_bud.write(4+ti, 8, fml)
                parm_id = ['D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20', 'D21', 'D22', 'D23', 'D24', 'D25', 'D26', 'D27', 'D28', 'D29', 'D30', 'D31', 'D32', 'D33', 'D34', 'D35', 'D36', 'D37', 'D38', 'D39', 'D40', 'D41', 'D42', 'D43', 'D44', 'D45', 'D46', 'D47', 'D48', 'D49', 'D50', 'D51']
        w_bud.write_rich_string(5, 0, self.font_ital, 'n', self.font_subs, 'p a')
        w_bud.write(5, 2, '1')
        w_bud.write_rich_string(6, 0, self.font_sym, 'l', self.font_subs, 'a')
        w_bud.write_rich_string(6, 2, 's', self.font_sups, '-1')
        w_bud.write_rich_string(7, 0, self.font_sym, 'D', self.font_ital, 't', self.font_subs, 'd')
        w_bud.write(7, 2, 's')
        w_bud.write_rich_string(8, 0, self.font_ital, 't', self.font_subs, 'c a')
        w_bud.write(8, 2, 's')
        w_bud.write_rich_string(9, 0, self.font_ital, 't', self.font_subs, 'l a')
        w_bud.write(9, 2, 's')
        w_bud.write_rich_string(10, 0, self.font_ital, 'COI', self.font_subs, 'a')
        w_bud.write(10, 2, '1')
        w_bud.write_rich_string(11, 0, self.font_ital, 'm', self.font_subs, 'sm')
        w_bud.write(11, 2, 'g')
        w_bud.write_rich_string(12, 0, self.font_sym, 'h', self.font_subs, 'sm')
        w_bud.write(12, 2, '1')
        w_bud.write_rich_string(13, 0, self.font_ital, 'k', self.font_subs, '0 Au', '(a)')
        w_bud.write(13, 2, '1')
        w_bud.write_rich_string(14, 0, self.font_ital, 'G', self.font_subs, 'th a')
        w_bud.write(14, 2, '1')
        w_bud.write_rich_string(15, 0, self.font_ital, 'G', self.font_subs, 'e a')
        w_bud.write(15, 2, '1')
        w_bud.write_rich_string(16, 0, self.font_ital, 'Q', self.font_subs, '0 a')
        w_bud.write(16, 2, '1')
        w_bud.write_rich_string(17, 0, self.font_ital, 'E', self.font_subs, 'r a')
        w_bud.write(17, 2, 'eV')
        w_bud.write_rich_string(18, 0, self.font_ital, 'n', self.font_subs, 'p m')
        w_bud.write(18, 2, '1')
        w_bud.write_rich_string(19, 0, self.font_sym, 'l', self.font_subs, 'm')
        w_bud.write_rich_string(19, 2, 's', self.font_sups, '-1')
        w_bud.write_rich_string(20, 0, self.font_ital, 't', self.font_subs, 'd m')
        w_bud.write(20, 2, 's')
        w_bud.write_rich_string(21, 0, self.font_ital, 't', self.font_subs, 'c m')
        w_bud.write(21, 2, 's')
        w_bud.write_rich_string(22, 0, self.font_ital, 't', self.font_subs, 'l m')
        w_bud.write(22, 2, 's')
        w_bud.write_rich_string(23, 0, self.font_ital, 'COI', self.font_subs, 'm')
        w_bud.write(23, 2, '1')
        w_bud.write_rich_string(24, 0, self.font_ital, 'm', self.font_subs, 'std')
        w_bud.write(24, 2, 'g')
        w_bud.write_rich_string(25, 0, self.font_sym, 'h', self.font_subs, 'std')
        w_bud.write(25, 2, '1')
        w_bud.write_rich_string(26, 0, self.font_ital, 'w', self.font_subs, 'm')
        w_bud.write_rich_string(26, 2, 'g g', self.font_sups, '-1')
        w_bud.write_rich_string(27, 0, self.font_ital, 'k', self.font_subs, '0 Au', '(m)')
        w_bud.write(27, 2, '1')
        w_bud.write_rich_string(28, 0, self.font_ital, 'G', self.font_subs, 'th m')
        w_bud.write(28, 2, '1')
        w_bud.write_rich_string(29, 0, self.font_ital, 'G', self.font_subs, 'e m')
        w_bud.write(29, 2, '1')
        w_bud.write_rich_string(30, 0, self.font_ital, 'Q', self.font_subs, '0 m')
        w_bud.write(30, 2, '1')
        w_bud.write_rich_string(31, 0, self.font_ital, 'E', self.font_subs, 'r m')
        w_bud.write(31, 2, 'eV')
        w_bud.write(32, 0, 'f', self.font_ital)
        w_bud.write(32, 2, '1')
        w_bud.write(33, 0, 'a', self.font_sym)
        w_bud.write(33, 2, '1')
        w_bud.write_rich_string(34, 0, self.font_ital, 'k', self.font_sym,'eD', self.font_ital, 'E')
        w_bud.write(34, 2, '1')
        w_bud.write_rich_string(35, 0, self.font_ital, 'k', self.font_sym,'eD', 'd ref')
        w_bud.write(35, 2, '1')
        w_bud.write_rich_string(36, 0, self.font_ital, "d'", self.font_subs, '0 a')
        w_bud.write(36, 2, 'mm')
        w_bud.write_rich_string(37, 0, self.font_sym, 'D', self.font_ital, 'd',self.font_subs, 'a')
        w_bud.write(37, 2, 'mm')
        w_bud.write_rich_string(38, 0, self.font_sym, 'n', self.font_subs, 'a')
        w_bud.write_rich_string(38, 2, 'mm', self.font_sups, '2',' g', self.font_sups, '-1')
        w_bud.write_rich_string(39, 0, self.font_ital,'h',self.font_subs, 'a')
        w_bud.write(39, 2, 'mm')
        w_bud.write_rich_string(40, 0, self.font_sym, 'r', self.font_subs, 'a')
        w_bud.write_rich_string(40, 2, 'g mm', self.font_sups, '-3')
        w_bud.write_rich_string(41, 0, self.font_ital, "d'", self.font_subs, '0 m')
        w_bud.write(41, 2, 'mm')
        w_bud.write_rich_string(42, 0, self.font_sym, 'D', self.font_ital, 'd',self.font_subs, 'm')
        w_bud.write(42, 2, 'mm')
        w_bud.write_rich_string(43, 0, self.font_sym, 'n', self.font_subs, 'm')
        w_bud.write_rich_string(43, 2, 'mm', self.font_sups, '2',' g', self.font_sups, '-1')
        w_bud.write_rich_string(44, 0, self.font_ital,'h',self.font_subs, 'm')
        w_bud.write(44, 2, 'mm')
        w_bud.write_rich_string(45, 0, self.font_sym, 'r', self.font_subs, 'm')
        w_bud.write_rich_string(45, 2, 'g mm', self.font_sups, '-3')
        w_bud.write(46, 0, 'b', self.font_sym)
        w_bud.write_rich_string(46, 2, 'mm', self.font_sups, '-1')
        w_bud.write_rich_string(47, 0, self.font_sym, 'D', self.font_ital, 'l')
        w_bud.write(47, 2, 'mm')
        w_bud.write(48, 0, 'm', self.font_sym)
        w_bud.write(48, 2, '1')
        w_bud.write_rich_string(49, 0, self.font_ital, 'w', self.font_subs, 'a blank')
        w_bud.write_rich_string(49, 2, 'g g', self.font_sups, '-1')
        w_bud.write_rich_string(50, 0, self.font_ital, 'm', self.font_subs, 'blank')
        w_bud.write(50, 2, 'g')

        if corr is not None:
            w_bud.write_rich_string(4, 11, self.font_ital, 't', self.font_subs, 'i')
            w_bud.write_rich_string(5, 11, self.font_ital, 'n', self.font_subs, 'p a')
            w_bud.write_rich_string(6, 11, self.font_sym, 'l', self.font_subs, 'a')
            w_bud.write_rich_string(7, 11, self.font_sym, 'D', self.font_ital, 't', self.font_subs, 'd')
            w_bud.write_rich_string(8, 11, self.font_ital, 't', self.font_subs, 'c a')
            w_bud.write_rich_string(9, 11, self.font_ital, 't', self.font_subs, 'l a')
            w_bud.write_rich_string(10, 11, self.font_ital, 'COI', self.font_subs, 'a')
            w_bud.write_rich_string(11, 11, self.font_ital, 'm', self.font_subs, 'sm')
            w_bud.write_rich_string(12, 11, self.font_sym, 'h', self.font_subs, 'sm')
            w_bud.write_rich_string(13, 11, self.font_ital, 'k', self.font_subs, '0 Au', '(a)')
            w_bud.write_rich_string(14, 11, self.font_ital, 'G', self.font_subs, 'th a')
            w_bud.write_rich_string(15, 11, self.font_ital, 'G', self.font_subs, 'e a')
            w_bud.write_rich_string(16, 11, self.font_ital, 'Q', self.font_subs, '0 a')
            w_bud.write_rich_string(17, 11, self.font_ital, 'E', self.font_subs, 'r a')
            w_bud.write_rich_string(18, 11, self.font_ital, 'n', self.font_subs, 'p m')
            w_bud.write_rich_string(19, 11, self.font_sym, 'l', self.font_subs, 'm')
            w_bud.write_rich_string(20, 11, self.font_ital, 't', self.font_subs, 'd m')
            w_bud.write_rich_string(21, 11, self.font_ital, 't', self.font_subs, 'c m')
            w_bud.write_rich_string(22, 11, self.font_ital, 't', self.font_subs, 'l m')
            w_bud.write_rich_string(23, 11, self.font_ital, 'COI', self.font_subs, 'm')
            w_bud.write_rich_string(24, 11, self.font_ital, 'm', self.font_subs, 'std')
            w_bud.write_rich_string(25, 11, self.font_sym, 'h', self.font_subs, 'std')
            w_bud.write_rich_string(26, 11, self.font_ital, 'w', self.font_subs, 'm')
            w_bud.write_rich_string(27, 11, self.font_ital, 'k', self.font_subs, '0 Au', '(m)')
            w_bud.write_rich_string(28, 11, self.font_ital, 'G', self.font_subs, 'th m')
            w_bud.write_rich_string(29, 11, self.font_ital, 'G', self.font_subs, 'e m')
            w_bud.write_rich_string(30, 11, self.font_ital, 'Q', self.font_subs, '0 m')
            w_bud.write_rich_string(31, 11, self.font_ital, 'E', self.font_subs, 'r m')
            w_bud.write(32, 11, 'f', self.font_ital)
            w_bud.write(33, 11, 'a', self.font_sym)
            w_bud.write_rich_string(34, 11, self.font_ital, 'k', self.font_sym,'eD', self.font_ital, 'E')
            w_bud.write_rich_string(35, 11, self.font_ital, 'k', self.font_sym,'eD', 'd ref')
            w_bud.write_rich_string(36, 11, self.font_ital, "d'", self.font_subs, '0 a')
            w_bud.write_rich_string(37, 11, self.font_sym, 'D', self.font_ital, 'd',self.font_subs, 'a')
            w_bud.write_rich_string(38, 11, self.font_sym, 'n', self.font_subs, 'a')
            w_bud.write_rich_string(39, 11, self.font_ital,'h',self.font_subs, 'a')
            w_bud.write_rich_string(40, 11, self.font_sym, 'r', self.font_subs, 'a')
            w_bud.write_rich_string(41, 11, self.font_ital, "d'", self.font_subs, '0 m')
            w_bud.write_rich_string(42, 11, self.font_sym, 'D', self.font_ital, 'd',self.font_subs, 'm')
            w_bud.write_rich_string(43, 11, self.font_sym, 'n', self.font_subs, 'm')
            w_bud.write_rich_string(44, 11, self.font_ital,'h',self.font_subs, 'm')
            w_bud.write_rich_string(45, 11, self.font_sym, 'r', self.font_subs, 'm')
            w_bud.write(46, 11, 'b', self.font_sym)
            w_bud.write_rich_string(47, 11, self.font_sym, 'D', self.font_ital, 'l')
            w_bud.write(48, 11, 'm', self.font_sym)
            w_bud.write_rich_string(49, 11, self.font_ital, 'w', self.font_subs, 'a blank')
            w_bud.write_rich_string(50, 11, self.font_ital, 'm', self.font_subs, 'blank')
            w_bud.write_rich_string(3, 12, self.font_ital, 't', self.font_subs, 'i')
            w_bud.write_rich_string(3, 13, self.font_ital, 'n', self.font_subs, 'p a')
            w_bud.write_rich_string(3, 14, self.font_sym, 'l', self.font_subs, 'a')
            w_bud.write_rich_string(3, 15, self.font_sym, 'D', self.font_ital, 't', self.font_subs, 'd')
            w_bud.write_rich_string(3, 16, self.font_ital, 't', self.font_subs, 'c a')
            w_bud.write_rich_string(3, 17, self.font_ital, 't', self.font_subs, 'l a')
            w_bud.write_rich_string(3, 18, self.font_ital, 'COI', self.font_subs, 'a')
            w_bud.write_rich_string(3, 19, self.font_ital, 'm', self.font_subs, 'sm')
            w_bud.write_rich_string(3, 20, self.font_sym, 'h', self.font_subs, 'sm')
            w_bud.write_rich_string(3, 21, self.font_ital, 'k', self.font_subs, '0 Au', '(a)')
            w_bud.write_rich_string(3, 22, self.font_ital, 'G', self.font_subs, 'th a')
            w_bud.write_rich_string(3, 23, self.font_ital, 'G', self.font_subs, 'e a')
            w_bud.write_rich_string(3, 24, self.font_ital, 'Q', self.font_subs, '0 a')
            w_bud.write_rich_string(3, 25, self.font_ital, 'E', self.font_subs, 'r a')
            w_bud.write_rich_string(3, 26, self.font_ital, 'n', self.font_subs, 'p m')
            w_bud.write_rich_string(3, 27, self.font_sym, 'l', self.font_subs, 'm')
            w_bud.write_rich_string(3, 28, self.font_ital, 't', self.font_subs, 'd m')
            w_bud.write_rich_string(3, 29, self.font_ital, 't', self.font_subs, 'c m')
            w_bud.write_rich_string(3, 30, self.font_ital, 't', self.font_subs, 'l m')
            w_bud.write_rich_string(3, 31, self.font_ital, 'COI', self.font_subs, 'm')
            w_bud.write_rich_string(3, 32, self.font_ital, 'm', self.font_subs, 'std')
            w_bud.write_rich_string(3, 33, self.font_sym, 'h', self.font_subs, 'std')
            w_bud.write_rich_string(3, 34, self.font_ital, 'w', self.font_subs, 'm')
            w_bud.write_rich_string(3, 35, self.font_ital, 'k', self.font_subs, '0 Au', '(m)')
            w_bud.write_rich_string(3, 36, self.font_ital, 'G', self.font_subs, 'th m')
            w_bud.write_rich_string(3, 37, self.font_ital, 'G', self.font_subs, 'e m')
            w_bud.write_rich_string(3, 38, self.font_ital, 'Q', self.font_subs, '0 m')
            w_bud.write_rich_string(3, 39, self.font_ital, 'E', self.font_subs, 'r m')
            w_bud.write(3, 40, 'f', self.font_ital)
            w_bud.write(3, 41, 'a', self.font_sym)
            w_bud.write_rich_string(3, 42, self.font_ital, 'k', self.font_sym,'eD', self.font_ital, 'E')
            w_bud.write_rich_string(3, 43, self.font_ital, 'k', self.font_sym,'eD', 'd ref')
            w_bud.write_rich_string(3, 44, self.font_ital, "d'", self.font_subs, '0 a')
            w_bud.write_rich_string(3, 45, self.font_sym, 'D', self.font_ital, 'd',self.font_subs, 'a')
            w_bud.write_rich_string(3, 46, self.font_sym, 'n', self.font_subs, 'a')
            w_bud.write_rich_string(3, 47, self.font_ital,'h',self.font_subs, 'a')
            w_bud.write_rich_string(3, 48, self.font_sym, 'r', self.font_subs, 'a')
            w_bud.write_rich_string(3, 49, self.font_ital, "d'", self.font_subs, '0 m')
            w_bud.write_rich_string(3, 50, self.font_sym, 'D', self.font_ital, 'd',self.font_subs, 'm')
            w_bud.write_rich_string(3, 51, self.font_sym, 'n', self.font_subs, 'm')
            w_bud.write_rich_string(3, 52, self.font_ital,'h',self.font_subs, 'm')
            w_bud.write_rich_string(3, 53, self.font_sym, 'r', self.font_subs, 'm')
            w_bud.write(3, 54, 'b', self.font_sym)
            w_bud.write_rich_string(3, 55, self.font_sym, 'D', self.font_ital, 'l')
            w_bud.write(3, 56, 'm', self.font_sym)
            w_bud.write_rich_string(3, 57, self.font_ital, 'w', self.font_subs, 'a blank')
            w_bud.write_rich_string(3, 58, self.font_ital, 'm', self.font_subs, 'blank')

        w_bud.write(52, 0, 'Quantity')
        w_bud.write(52, 2, 'Unit')
        w_bud.write(52, 3, 'Value')

        if corr is not None:
            w_bud.write(52, 4, 'Std unc')
            w_bud.write(52, 5, 'Rel unc')
            w_bud.write(52, 9, 'Contribution to variance')
        w_bud.write(53, 0, 'Y', self.font_ital)
        w_bud.write_rich_string(53, 2, '[', self.font_ital, 'y', ']')
        w_bud.write(53, 3, 'y', self.font_ital)

        if corr is not None:
            w_bud.write_rich_string(53, 4, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
            w_bud.write_rich_string(53, 5, self.font_ital, 'u', self.font_subs, 'r', '(', self.font_ital, 'y', ')')
            w_bud.write_rich_string(53, 9, self.font_ital, 'I', ' / %')
        w_bud.write_rich_string(54, 0, self.font_ital, 'w', self.font_subs, 'a')
        w_bud.write_rich_string(54, 2, 'g g', self.font_sups, '-1')
        w_bud.write(55, 0, 'DL')
        w_bud.write_rich_string(55, 2, '< g g', self.font_sups, '-1')
        w_bud.write(56, 0, 'zeta score')
        w_bud.write(56, 2, '1')
        if corr is not None:

            fml = f'=(({parm_id[1]}*{parm_id[2]}*{parm_id[4]}*EXP({parm_id[44]}*(1-{parm_id[5]}/{parm_id[4]}))*{parm_id[18]}*{parm_id[19]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*(1-EXP(-{parm_id[15]}*{parm_id[17]}))) / ({parm_id[14]}*{parm_id[15]}*{parm_id[17]}*EXP({parm_id[44]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[5]}*{parm_id[6]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*(1-EXP(-{parm_id[2]}*{parm_id[4]}))) * EXP(({parm_id[2]}-{parm_id[15]})*{parm_id[16]}+{parm_id[2]}*{parm_id[3]}) * 1/(1+{parm_id[42]}*{parm_id[43]}) * {parm_id[23]}/{parm_id[9]} * ({parm_id[24]}+{parm_id[25]}/{parm_id[28]}*(({parm_id[26]}-0.429)/{parm_id[27]}^{parm_id[29]}+0.429/((2*{parm_id[29]}+1)*0.55^{parm_id[29]}))) / ({parm_id[10]}+{parm_id[11]}/{parm_id[28]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[29]}+0.429/((2*{parm_id[29]}+1)*0.55^{parm_id[29]}))) * {parm_id[30]}*{parm_id[31]}*(({budget.standard_pos}-{parm_id[37]})/({budget.standard_pos}+{parm_id[38]}-{parm_id[37]}))^2/(({budget.sample_pos}-{parm_id[32]})/({budget.sample_pos}+{parm_id[33]}-{parm_id[32]}))^2*(1+{parm_id[35]}/({budget.sample_pos}+{parm_id[33]}-{parm_id[32]}))/(1+{parm_id[40]}/({budget.standard_pos}+{parm_id[38]}-{parm_id[37]}))*((1-EXP(-{parm_id[39]}*{parm_id[40]}*{parm_id[41]}))/({parm_id[39]}*{parm_id[40]}*{parm_id[41]}))/((1-EXP(-{parm_id[34]}*{parm_id[35]}*{parm_id[36]}))/({parm_id[34]}*{parm_id[35]}*{parm_id[36]})) * {parm_id[20]}*(1-{parm_id[21]})*{parm_id[22]}-{parm_id[46]}*{parm_id[45]})/({parm_id[7]}*(1-{parm_id[8]}))'

            #new model
            #'=((D6*D7*D9*EXP(D49*(1-D10/D9))*D23*D24*(1-EXP(-D20*D5))*(1-EXP(-D20*D22))) / (D19*D20*D22*EXP(D49*(1-D23/D22))*D10*D11*(1-EXP(-D7*D5))*(1-EXP(-D7*D9))) * EXP((D7-D20)*D21+D7*D8) * 1/(1+D47*D48) * D28/D14 * (D29+D30/D33*((D31-0.429)/D32^D34+0.429/((2*D34+1)*0.55^D34))) / (D15+D16/D33*((D17-0.429)/D18^D34+0.429/((2*D34+1)*0.55^D34))) * D35*D36*((83.4-D42)/(83.4+D43-D42))^2/((203.4-D37)/(203.4+D38-D37))^2*(1+D40/(203.4+D38-D37))/(1+D45/(83.4+D43-D42))*((1-EXP(-D44*D45*D46))/(D44*D45*D46))/((1-EXP(-D39*D40*D41))/(D39*D40*D41)) * D25*(1-D26)*D27-D51*D50)/(D12*(1-D13))'

            w_bud.write(54, 3, fml, self.font_result)
            fml = '{=sqrt(MMULT(MMULT(TRANSPOSE(I5:I51),BJ5:DD51),I5:I51))}'
            w_bud.write(54, 4, fml, self.font_uncresult)
            fml = '=IFERROR(ABS(E55/D55),"-")'
            w_bud.write(54, 5, fml, self.font_pct)
            for ri in range(len(corr)):
                sm = '#'
                for ci in range(len(corr)):
                    w_bud.write(4+ri, 12+ci, corr[ri, ci])
                    cell_corr = xl_rowcol_to_cell(4+ri, 12+ci)
                    fml = '='+str(cell_corr)+'*E'+str(4+ri+1)+'*E'+str(4+ci+1)
                    w_bud.write(4+ri, 61+ci, fml, self.font_gray)
                    sms = str(cell_corr)+'*E'+str(4+ri+1)+'*E' + \
                        str(4+ci+1)+'*I'+str(4+ri+1)+'*I'+str(4+ci+1)
                    sm = sm+'+'+sms
                sm = sm.replace('#+', '=(')
                sm = sm+')/E55^2'
                w_bud.write(4+ri, 9, sm, self.font_pct)
            fml = '=SUM(J5:J51)'
            w_bud.write(54, 9, fml, self.font_pct)
        else:
            fml = '-'
            w_bud.write(54, 3, fml, self.font_result)
            w_bud.write(54, 4, fml, self.font_uncresult)
        if budget.currie_limit is not None:
            CUR = f'(2.71 + 4.65*SQRT({budget.currie_limit}))'

            fml = f'=(({CUR}*{parm_id[2]}*{parm_id[4]}*EXP({parm_id[44]}*(1-{parm_id[5]}/{parm_id[4]}))*{parm_id[18]}*{parm_id[19]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*(1-EXP(-{parm_id[15]}*{parm_id[17]}))) / ({parm_id[14]}*{parm_id[15]}*{parm_id[17]}*EXP({parm_id[44]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[5]}*{parm_id[6]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*(1-EXP(-{parm_id[2]}*{parm_id[4]}))) * EXP(({parm_id[2]}-{parm_id[15]})*{parm_id[16]}+{parm_id[2]}*{parm_id[3]}) * 1/(1+{parm_id[42]}*{parm_id[43]}) * {parm_id[23]}/{parm_id[9]} * ({parm_id[24]}+{parm_id[25]}/{parm_id[28]}*(({parm_id[26]}-0.429)/{parm_id[27]}^{parm_id[29]}+0.429/((2*{parm_id[29]}+1)*0.55^{parm_id[29]}))) / ({parm_id[10]}+{parm_id[11]}/{parm_id[28]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[29]}+0.429/((2*{parm_id[29]}+1)*0.55^{parm_id[29]}))) * {parm_id[30]}*{parm_id[31]}*(({budget.standard_pos}-{parm_id[37]})/({budget.standard_pos}+{parm_id[38]}-{parm_id[37]}))^2/(({budget.sample_pos}-{parm_id[32]})/({budget.sample_pos}+{parm_id[33]}-{parm_id[32]}))^2*(1+{parm_id[35]}/({budget.sample_pos}+{parm_id[33]}-{parm_id[32]}))/(1+{parm_id[40]}/({budget.standard_pos}+{parm_id[38]}-{parm_id[37]}))*((1-EXP(-{parm_id[39]}*{parm_id[40]}*{parm_id[41]}))/({parm_id[39]}*{parm_id[40]}*{parm_id[41]}))/((1-EXP(-{parm_id[34]}*{parm_id[35]}*{parm_id[36]}))/({parm_id[34]}*{parm_id[35]}*{parm_id[36]})) * {parm_id[20]}*(1-{parm_id[21]})*{parm_id[22]})/({parm_id[7]}*(1-{parm_id[8]}))'#-{parm_id[46]}*{parm_id[45]} deleted!
			#no blank correction for detection limit
        else:
            fml = '-'
        w_bud.write(55, 3, fml, self.font_DL)

        #z score test
        if budget.z_score[0] is not None and budget.smp_np > 0.0 and budget.z_score[2]:
            fml = f'=(D55-{budget.z_score[0]}) / SQRT((E55)^2 + ({budget.z_score[1]})^2)'
            w_bud.write(56, 4, f'ref certificate: {budget.cert_name}')
        else:
            fml = '-'
        w_bud.write(56, 3, fml, self.font_zscore)
        w_bud.write(59, 0, 'Additional information')
        w_bud.write(60, 0, 'Quantity')
        w_bud.write(60, 2, 'Unit')
        w_bud.write(60, 3, 'Value')
        w_bud.write_rich_string(61, 0, self.font_ital, 'X', self.font_subs, 'i')
        w_bud.write_rich_string(61, 2, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        w_bud.write_rich_string(61, 3, self.font_ital, 'x', self.font_subs, 'i')
        if corr is not None:
            w_bud.write(60, 4, 'Std unc')
            w_bud.write(60, 5, 'Rel unc')
            w_bud.write(60, 9, 'Contribution to variance')
            w_bud.write_rich_string(61, 4, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
            w_bud.write_rich_string(61, 5, self.font_ital, 'u', self.font_subs, 'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
            w_bud.write_rich_string(61, 9, self.font_ital, 'I', ' / %')
        w_bud.write_rich_string(62, 0, self.font_sym, 'e', self.font_subs, 'geo m', ' / ', self.font_sym, 'e', self.font_subs, 'geo a')
        #here the others
        w_bud.write_rich_string(63, 0, self.font_ital, 'k', self.font_sym,'eD', 'd a')
        w_bud.write_rich_string(64, 0, self.font_sym, 'w', self.font_subs,'a')
        w_bud.write_rich_string(65, 0, self.font_ital, 'F', self.font_subs,'abs a')
        w_bud.write_rich_string(66, 0, self.font_ital, 'k', self.font_sym,'eD', 'd m')
        w_bud.write_rich_string(67, 0, self.font_sym, 'w', self.font_subs,'m')
        w_bud.write_rich_string(68, 0, self.font_ital, 'F', self.font_subs,'abs m')
        w_bud.write_rich_string(69, 0, self.font_ital, 'Q', self.font_subs, '0,a', '(', self.font_sym, 'a', ')')
        w_bud.write_rich_string(70, 0, self.font_ital, 'Q', self.font_subs, '0,m', '(', self.font_sym, 'a', ')')
        w_bud.write_rich_string(71, 0, '1 + ', self.font_sym, 'b D', self.font_ital, 'l')
        w_bud.write_rich_string(72, 0, self.font_ital, 'm', self.font_subs, 'a')
        w_bud.write_rich_string(73, 0, self.font_ital, 'm', self.font_subs, 'a blank')
        w_bud.write_rich_string(74, 0, self.font_ital, 'n', self.font_subs, "p a'")
        w_bud.write_rich_string(75, 0, self.font_ital, 'n', self.font_subs, 'p b')
        w_bud.write_rich_string(76, 0, self.font_ital, 'n', self.font_subs, 'p i')
        w_bud.write_rich_string(77, 0, self.font_ital, 'n', self.font_subs, 'p f')
        w_bud.write(62, 2, '1')
        w_bud.write(63, 2, '1')
        w_bud.write(64, 2, '1')
        w_bud.write(65, 2, '1')
        w_bud.write(66, 2, '1')
        w_bud.write(67, 2, '1')
        w_bud.write(68, 2, '1')
        w_bud.write(69, 2, '1')
        w_bud.write(70, 2, '1')
        w_bud.write(71, 2, '1')
        w_bud.write(72, 2, 'g')
        w_bud.write(73, 2, 'g')
        w_bud.write(74, 2, '1')
        w_bud.write(75, 2, '1')
        w_bud.write(76, 2, '1')
        w_bud.write(77, 2, '1')
        #son tutti da rifare #budget
        fml = f'=D35*D36*(({budget.standard_pos}-D42)/({budget.standard_pos}+D43-D42))^2/(({budget.sample_pos}-D37)/({budget.sample_pos}+D38-D37))^2*(1+D40/({budget.sample_pos}+D38-D37))/(1+D45/({budget.standard_pos}+D43-D42))*((1-EXP(-D44*D45*D46))/(D44*D45*D46))/((1-EXP(-D39*D40*D41))/(D39*D40*D41))'
        w_bud.write(62, 3, fml)
        fml = f'=(({budget.sample_pos}-D37)/({budget.sample_pos}+D38-D37))^2'
        w_bud.write(63, 3, fml)
        fml = f'=1+D40/({budget.sample_pos}+D38-D37)'
        w_bud.write(64, 3, fml)
        fml = f'=(1-EXP(-D39*D40*D41))/(D39*D40*D41)'
        w_bud.write(65, 3, fml)
        fml = f'=(({budget.standard_pos}-D42)/({budget.standard_pos}+D43-D42))^2'
        w_bud.write(66, 3, fml)
        fml = f'=1+D45/({budget.standard_pos}+D43-D42)'
        w_bud.write(67, 3, fml)
        fml = f'=(1-EXP(-D44*D45*D46))/(D44*D45*D46)'
        w_bud.write(68, 3, fml)
        fml = '=(D17-0.429)/D18^D34+0.429/((2*D34+1)*0.55^D34)'
        w_bud.write(69, 3, fml)
        fml = '=(D31-0.429)/D32^D34+0.429/((2*D34+1)*0.55^D34)'
        w_bud.write(70, 3, fml)
        fml = '=1+D47*D48'
        w_bud.write(71, 3, fml)
        fml ='=D55*D12*(1-D13)'
        w_bud.write(72, 3, fml)
        fml ='=D50*D51'
        w_bud.write(73, 3, fml)

        #dulcis in fundo
        w_bud.write(74, 3, data[1, 0])
        w_bud.write(5, 3, '=D75-D76-D77-D78')
        w_bud.write(75, 3, budget.bkg_counts)
        #w_bud.write(76, 3, 0) #modify!
        #w_bud.write(77, 3, 0) #modify!
        if corr is not None:
            w_bud.write(74, 4, data[1, 1])
            w_bud.write(5, 4, '=SQRT(E75^2+E76^2+E77^2+E78^2)')
            fml = '-'#'=SQRT(J60*E54^2)/(((D6*D7*D9*EXP(D46*(1-D10/D9))*D22*(1-EXP(-D19*D5))*EXP((D7-D19)*D20+D7*D8)*(1-EXP(-D19*D21))*D23*D24*D25*D26*(D27+D28/D31*((D29-0.429)/D30^D32+0.429/((2*D32+1)*0.55^D32))))/(D19*D18*D21*EXP(D46*(1-D22/D21))*D10*(1-EXP(-D7*D5))*(1-EXP(-D7*D9))*D11*D13*(1+D47*D48)*(D14+D15/D31*((D16-0.429)/D17^D32+0.429/((2*D32+1)*0.55^D32))))-D49*D50)/D12)'#contribution to variance
            w_bud.write(62, 4, fml)
            fml = '=IFERROR(ABS(E63/D63),"-")'
            w_bud.write(62, 5, fml, self.font_pct)
            fml = '=SUM(J35:J46)'
            w_bud.write(62, 9, fml, self.font_pct)
            fml = '-'
            w_bud.write(63, 4, fml)
            fml = '=IFERROR(ABS(E64/D64),"-")'
            w_bud.write(63, 5, fml, self.font_pct)
            fml = '-'
            w_bud.write(64, 4, fml)
            fml = '=IFERROR(ABS(E65/D65),"-")'
            w_bud.write(64, 5, fml, self.font_pct)
            fml = '-'#=IFERROR(ABS(D41*D42)*SQRT((E41/D41)^2+(E42/D42)^2),"-")'
            w_bud.write(65, 4, fml)
            fml = '=IFERROR(ABS(E66/D66),"-")'
            w_bud.write(65, 5, fml, self.font_pct)
            fml = '-'
            w_bud.write(66, 4, fml)
            fml = '=IFERROR(ABS(E67/D67),"-")'
            w_bud.write(66, 5, fml, self.font_pct)
            fml = '-'#'=IFERROR(D62*SQRT((E44/D44)^2+(E45/D45)^2),"-")'
            w_bud.write(67, 4, fml)
            fml = '=IFERROR(ABS(E68/D68),"-")'
            w_bud.write(67, 5, fml, self.font_pct)
            fml = '-'
            w_bud.write(68, 4, fml)
            fml = '=IFERROR(ABS(E69/D69),"-")'
            w_bud.write(68, 5, fml, self.font_pct)
            fml = '-'
            w_bud.write(69, 4, fml)
            fml = '=IFERROR(ABS(E70/D70),"-")'
            w_bud.write(69, 5, fml, self.font_pct)
            fml = '-'
            w_bud.write(70, 4, fml)
            fml = '=IFERROR(ABS(E71/D71),"-")'
            w_bud.write(70, 5, fml, self.font_pct)
            fml = '-'
            w_bud.write(71, 4, fml)
            fml = '=IFERROR(ABS(E72/D72),"-")'
            w_bud.write(71, 5, fml, self.font_pct)
            fml = '-'
            w_bud.write(72, 4, fml)
            fml = '=IFERROR(ABS(E73/D73),"-")'
            w_bud.write(72, 5, fml, self.font_pct)
            fml = '-'
            w_bud.write(73, 4, fml)
            fml = '=IFERROR(ABS(E74/D74),"-")'
            w_bud.write(73, 5, fml, self.font_pct)
            fml = '=IFERROR(ABS(E75/D75),"-")'
            w_bud.write(74, 5, fml, self.font_pct)
            w_bud.write(75, 4, budget.bkg_ucounts)
            fml = '=IFERROR(ABS(E76/D76),"-")'
            w_bud.write(75, 5, fml, self.font_pct)
            fml = '=IFERROR(ABS(E77/D77),"-")'
            w_bud.write(76, 5, fml, self.font_pct)
            fml = '=IFERROR(ABS(E78/D78),"-")'
            w_bud.write(77, 5, fml, self.font_pct)

            w_bud.set_column('G:H', None, None, {'hidden': True})

        w_bud.write(80, 0, 'Measurement model')
        w_bud.write_url(f'A{81+1}', f"internal:'Models'!A1")


    def _wbudget_type_NotImplemented(self, w_bud, budget):
        w_bud.write(0, 0, 'This complex activation decay is not implemented yet')
        w_bud.write(1, 0, '')


def coi_correction_sda(emission, calibration, pos, R=0.2):

	def _get_COI_database():
		coi_df = pd.read_excel(os.path.join(os.path.join('data','coincidences'), 'COI_database.xlsx'), skiprows=1, names=['target','emitter','E','line','a','c','g','type'])
		coi_df['target'].fillna(method='ffill', inplace=True)
		coi_df['type'].fillna(value='', inplace=True)
		coi_df['line'].fillna(value=0.0, inplace=True)
		coi_df['line'] = coi_df['line'].astype(int)
		return coi_df

	def loss_type_I(emitter_df, idxs, Xindex):
		# (*A-B-C-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_II(emitter_df, idxs, Xindex):
		# (B-*A-C-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 1:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_III(emitter_df, idxs, Xindex):
		# (B-C-*A-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 2:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_IV(emitter_df, idxs, Xindex):
		# (B-C-D-*A-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 3:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_V(emitter_df, idxs, Xindex):
		# (B-C-D-E-*A)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 4:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def manage_losses(emitter_df, Xindex, idxs):
		correction = 0.0
		if idxs.index('X') == 0:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = loss_type_I(emitter_df, idxs, Xindex)
			F1 = aB*cB*etB+aB*aC*cC*etC+aB*aC*aD*cD*etD+aB*aC*aD*aE*cE*etE 
			F2 = aB*aC*cB*cC*etB*etC+aB*aC*aD*cB*cD*etB*etD+aB*aC*aD*aE*cB*cE*etB*etE+aB*aC*aD*cC*cD*etC*etD+aB*aC*aD*aE*cC*cE*etC*etE+aB*aC*aD*aE*cD*cE*etD*etE
			F3 = aB*aC*aD*cB*cC*cD*etB*etC*etD+aB*aC*aD*aE*cB*cC*cE*etB*etC*etE+aB*aC*aD*aE*cB*cD*cE*etB*etD*etE+aB*aC*aD*aE*cC*cD*cE*etC*etD*etE
			F4 = aB*aC*aD*aE*cB*cC*cD*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 1:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = loss_type_II(emitter_df, idxs, Xindex)
			F1 = gB/gA*aA*cA*etB+aC*cC*etC+aC*aD*cD*etD+aC*aD*aE*cE*etE
			F2 = gB/gA*aA*aC*cA*cC*etB*etC+gB/gA*aA*aC*aD*cA*cD*etB*etD+gB/gA*aA*aC*aD*aE*cA*cE*etB*etE+aC*aD*cC*cD*etC*etD+aC*aD*aE*cC*cE*etC*etE+aC*aD*aE*cD*cE*etD*etE
			F3 = gB/gA*aA*aC*aD*cA*cC*cD*etB*etC*etD+gB/gA*aA*aC*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+aC*aD*aE*cC*cD*cE*etC*etD*etE
			F4 = gB/gA*aA*aC*aD*aE*cA*cC*cD*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 2:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = loss_type_III(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aA*cA*etB+gC/gA*aA*cA*etC+aD*cD*etD+aD*aE*cE*etE
			F2 = gB/gA*aC*aA*cC*cA*etB*etC+gB/gA*aC*aA*aD*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cA*cE*etB*etE+gC/gA*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+aD*aE*cD*cE*etD*etE
			F3 = gB/gA*aC*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 3:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = loss_type_IV(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aD*aA*cA*etB+gC/gA*aD*aA*cA*etC+gD/gA*aA*cA*etD+aE*cE*etE
			F2 = gB/gA*aC*aD*aA*cC*cA*etB*etC+gB/gA*aC*aA*aD*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cA*cE*etB*etE+gC/gA*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+gD/gA*aA*aE*cA*cE*etD*etE
			F3 = gB/gA*aC*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*cC*cD*cA*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 4:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = loss_type_V(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aD*aE*aA*cA*etB+gC/gA*aD*aE*aA*cA*etC+gD/gA*aE*aA*cA*etD+gE/gA*aA*cA*etE
			F2 = gB/gA*aC*aD*aE*aA*cE*cA*etB*etE+gB/gA*aC*aD*aE*aA*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cC*cA*etB*etC+gC/gA*aE*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+gD/gA*aA*aE*cA*cE*etD*etE
			F3 = gB/gA*aC*aE*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aE*aA*aC*aD*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*cC*cD*cA*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		return correction

	def sum_type_I(emitter_df, idxs, Xindex):
		# (*A=B+C)
		aA, cA, gA, epA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, epB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, epC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, epD = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, epA = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 1:
				aB, cB, gB, epB = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 2:
				aC, cC, gC, epC = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 3:
				aD, cD, gD, epD = emitter_df.loc[idx, ['a','c','g','ep']]
		return aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD

	def sum_type_II(emitter_df, idxs, Xindex):
		# (*A=B+C+D)
		aA, cA, gA, epA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, epB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, epC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, epD = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, epA = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 1:
				aB, cB, gB, epB = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 2:
				aC, cC, gC, epC = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 3:
				aD, cD, gD, epD = emitter_df.loc[idx, ['a','c','g','ep']]
		return aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD

	def manage_sum(emitter_df, Xindex, idxs):
		correction = 0.0
		if len(idxs) == 3:
			aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD = sum_type_I(emitter_df, idxs, Xindex)
			correction = gB/gA*aC*cC*epB*epC/epA
		elif len(idxs) == 4:
			aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD = sum_type_II(emitter_df, idxs, Xindex)
			correction = gB/gA*aC*cC*aD*cD*epB*epC*epD/epA
		return correction
	
	coi_df = _get_COI_database()
	emit, energy = emission.replace(' keV','').split()
	filt_emission = coi_df['emitter'] == emit
	emitter_df = coi_df[filt_emission].copy(deep=True)
	emitter_df.set_index('line', drop=True, append=False, inplace=True, verify_integrity=False)

	filt_X = (float(energy) - 0.2 < emitter_df['E']) & (emitter_df['E'] < float(energy) + 0.2)
	#print(emitter_df[filt_X])
	try:
		Xindex = int(emitter_df[filt_X].index[0])
		scheme = emitter_df.loc[Xindex, 'type']
		emitter_df['ep'] = calibration.evaluate_efficiency(emitter_df['E'], pos)
		emitter_df['et'] = emitter_df['ep'] / calibration.evaluate_PT(emitter_df['E'], pos)

		coincidences = scheme.split(' : ')
		corrections_loss = []
		corrections_sum = []
		#print(emitter_df)
		for item in coincidences:
			if '-' in item:
				#print(item, ': Coincidence LOSS')
				if '*' in item:
					nn, item = item.split('*')
					nn = int(nn)
					#print(nn, item)
					item = item.replace('(','').replace(')','')
					idxs = [int(idx) if idx!='X' else idx for idx in item.split('-')]
					corrections_loss.append(nn * manage_losses(emitter_df, Xindex, idxs))
				else:
					idxs = [int(idx) if idx!='X' else idx for idx in item.split('-')]
					corrections_loss.append(manage_losses(emitter_df, Xindex, idxs))
			else:
				#print(item, ': Coincidence SUM')
				item = item.replace('=',' ').replace('+',' ')
				idxs = [int(idx) if idx!='X' else idx for idx in item.split()]
				corrections_sum.append(manage_sum(emitter_df, Xindex, idxs))
		#print('sum loss',np.sum(corrections_loss))
		coi = (1-np.sum(corrections_loss)) * (1+np.sum(corrections_sum))
		ucoi = coi * np.sqrt(np.power((np.sum(corrections_loss)*R)/(1-np.sum(corrections_loss)),2) + np.power((np.sum(corrections_sum)*R)/(1-np.sum(corrections_sum)),2))
		#print('coi',coi)
	except:
		coi, ucoi = 1.0, 0.0
	return coi, ucoi

def _irq_data(data):
	return pd.DataFrame(data=data, columns=['value', 'uncertainty'])

def _get_fast_data(path=os.path.join(os.path.join('data','literaturedata'), 'fast_data.csv'), columns=['emitter', 'target', 'reaction', 'half_life', 'M', 'isotopic_fraction', 'yield', 'cross_section', 'u_cross_section', 'energy']):
	df = pd.read_csv(path, header=0, names=columns, sep='|')
	df.drop_duplicates(subset=['emitter'], inplace=True)
	return df

def _get_true_table(df):
	#return pd.Series([True]*len(df['target']))
	return df['target'] != ''

def _store_analysis_data(NAA):
	columns = ['irradiation_date', 'channel', 'f', 'a', 'irradiation_time', 'target', 'emitter', 'sample', 'value', 'uncertainty', 'DL', 'z', 'certificate', 'w', 'uw']
	data = []
	for item in NAA.budgets:
		target, emitter, values = item._solve(full=True)
		if values is not None:
			if not np.isnan(values[3]) and item.z_score[2]:
				data_row = [NAA.irradiation.datetime, NAA.irradiation.channel_name, NAA.irradiation.f_value, NAA.irradiation.a_value, NAA.irradiation.irradiation_time, target, emitter, item.spectrum_code, values[0], values[1], values[2], values[3], item.cert_name, item.z_score[0], item.z_score[1]]
				data.append(data_row)
	df = pd.DataFrame(data, columns=columns)
	df['irradiation_date'] = pd.to_datetime(df['irradiation_date'], format="%d/%m/%Y %H:%M:%S")
	return df

def _update_analysis_data(df,filepath=os.path.join(os.path.join('data','results'),'result_data.csv')):
	columns = ['irradiation_date', 'channel', 'f', 'a', 'irradiation_time', 'target', 'emitter', 'sample', 'value', 'uncertainty', 'DL', 'z', 'certificate']
	df.to_csv(filepath, columns=columns, header=False, index=False, mode='w', date_format="%d/%m/%Y %H:%M:%S")

def _get_division(uncertainty, value):
	try:
		return np.abs(uncertainty / value) * 100
	except:
		return np.nan

def _get_emission_data(filename='emissions.csv', columns=['emitter', 'energy', 'yield','t_half', 'u_t_half', 'COIfree', 'reference']):
	return pd.read_csv(os.path.join(os.path.join('data','literaturedata'), filename), header=0, names=columns)

def _get_channel_data(filename='channels.csv', columns=['m_datetime','datetime', 'channel_name', 'pos', 'f_value', 'unc_f_value', 'a_value','unc_a_value', 'thermal_flux', 'unc_thermal_flux', 'epithermal_flux', 'unc_epithermal_flux', 'fast_flux', 'unc_fast_flux'],full_dataset=False):
	channel_df = pd.read_csv(os.path.join(os.path.join('data','facility'), filename), header=0, names=columns)
	channel_df['datetime'] = pd.to_datetime(channel_df['datetime'], format="%d/%m/%Y %H:%M:%S")
	channel_df['m_datetime'] = pd.to_datetime(channel_df['m_datetime'], format="%d/%m/%Y %H:%M:%S")
	channel_df['channel_name'] = channel_df['channel_name'].astype(str)
	channel_df['pos'] = channel_df['pos'].astype(str)
	channel_df.dropna(axis=0, how='any', subset=['f_value','unc_f_value', 'a_value','unc_a_value'], inplace=True)
	#selection
	channel_df.sort_values(by='datetime', inplace=True, ascending=False)
	if full_dataset == False:
		channel_df.drop_duplicates(subset='channel_name', keep='first', inplace=True)
		#channel_df.set_index(keys='channel_name', drop=True, inplace=True)
	return list(channel_df['channel_name']), channel_df
	#else:
	#	#channel_df.set_index(keys='channel_name', drop=True, inplace=True)
	#	return list(set(channel_df.index)), channel_df

def _get_beta_data(filename='beta.csv', columns=['channel_name', 'm_datetime', 'datetime','position', 'beta', 'unc_beta']):
	channel_df = pd.read_csv(os.path.join(os.path.join('data','facility'), filename), header=0, names=columns)
	channel_df['m_datetime'] = pd.to_datetime(channel_df['m_datetime'], format="%d/%m/%Y %H:%M:%S")
	channel_df['datetime'] = pd.to_datetime(channel_df['datetime'], format="%d/%m/%Y %H:%M:%S")
	channel_df['channel_name'] = channel_df['channel_name'].astype(str)
	channel_df['position'] = channel_df['position'].astype(str)
	channel_df.dropna(axis=0, how='any', subset=['beta', 'unc_beta'], inplace=True)
	#selection
	channel_df.sort_values(by='datetime', inplace=True, ascending=False)
	#channel_df.set_index(keys='channel_name', drop=True, inplace=True)
	return channel_df

def manage_spectra_files_and_get_infos(filename,limit,look_for_peaklist_option):
	"""
	Retrieve information from spectrum and peaklist file, deals with different situations
	"""
	peak_list, counts, start_acquisition, real_time, live_time, result, note = None, None, None, None, None, False, 'a generic error occurred!'
	allowed_extensions = ('.csv','.rpt','.asc','.chn')
	basename, extension = os.path.splitext(filename)
	source = []
	#.csv route
	if extension.lower() == allowed_extensions[0]:
		try:
			peak_list = openhyperlabfile(f'{basename}{extension}',limit)
			source.append((f'{basename}{extension}','peak list'))
		except:
			note = 'error while importing file'#maybe expand
		else:
			if True:#look_for_peaklist_option:
				try:#asc
					start_acquisition, real_time, live_time, counts = openASCfile(f'{basename}{allowed_extensions[2]}')
					source.append((f'{basename}{allowed_extensions[2]}','spectrum'))
					result = True
				except:
					note = 'some note'
				if not result:
					try:
						start_acquisition, real_time, live_time, counts = openchnfile(f'{basename}{allowed_extensions[3]}')
						source.append((f'{basename}{allowed_extensions[3]}','spectrum'))
						result = True
					except:
						note = 'no spectrum file found'#expand here
			else:
				note = 'you need spectrum information!'

	#.rpt route
	elif extension.lower() == allowed_extensions[1]:
		try:
			start_acquisition, real_time, live_time, peak_list = openrptfile(f'{basename}{extension}',limit)
			source.append((f'{basename}{extension}','peak list'))
			result = True
		except:
			note = 'error while importing file'
		else:
			if look_for_peaklist_option:
				try:#asc
					start_acquisition, real_time, live_time, counts = openASCfile(f'{basename}{allowed_extensions[2]}')
					source.append((f'{basename}{allowed_extensions[2]}','spectrum'))
				except:
					note = 'no spectrum file found'
				if counts is None:
					try:
						_start_acquisition, real_time, live_time, counts = openchnfile(f'{basename}{allowed_extensions[3]}')
						source.append((f'{basename}{allowed_extensions[3]}','spectrum'))
						if start_acquisition is None:
							start_acquisition = _start_acquisition
					except:
						note = 'no spectrum file found'#expand here
			else:
				note = 'imported anyway'

	#.asc route
	elif extension.lower() == allowed_extensions[2]:
		pass

	#.chn route
	elif extension.lower() == allowed_extensions[3]:
		pass

	return peak_list, counts, start_acquisition, real_time, live_time, result, note, source

def openhyperlabfile(file,limit=40):
	with open(file, newline='') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		S = [[float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9]), float(row[10]), np.nan] for row in spamreader if float(row[9])/float(row[8])*100 < limit]
	return S

def openASCfile(file):
	with open(file,'r') as ascfile:
		filelines = [line.replace('\n','') for line in ascfile.readlines()]
	idx = 0
	for line in filelines[::-1]:
		if '#AcqStart=' in line:
			date_time = line.replace('#AcqStart=','')
		if '#TrueTime=' in line:
			real = float(line.replace('#TrueTime=',''))
		if '#LiveTime=' in line:
			live = float(line.replace('#LiveTime=',''))
			idx = filelines.index(line)
			break
	startcounting = datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
	spectrum_counts = np.array([float(iks) for iks in filelines[:idx]])
	return startcounting, real, live, spectrum_counts

def openchnfile(file):
	import struct
	with open(file, "rb") as f:
		cs=4
		data = f.read(2)
		data = f.read(2)
		data = f.read(2)
		data = f.read(2)
		data = f.read(4)
		datev=struct.unpack('<I',data)
		real = int(datev[0])*20/1000
		data = f.read(4)
		datev=struct.unpack('<I',data)
		live = int(datev[0])*20/1000
		date = str(f.read(8),'utf-8')
		time = str(f.read(4),'utf-8')
		data = f.read(2)
		data = f.read(2)
		counts = []
		while data:
			data = f.read(cs)
			try:
				datev=struct.unpack('<I',data)
				counts.append(int(datev[0]))
			except:
				break
	if 65536 <= len(counts) < 131072:
		counts = counts[:65536]
	elif 32768 <= len(counts) < 65536:
		counts = counts[:32768]
	elif 16384 <= len(counts) < 32768:
		counts = counts[:16384]
	elif 8192 <= len(counts) < 16384:
		counts = counts[:8192]
	elif 8192 <= len(counts) < 16384:
		counts = counts[:8192]
	elif 4096 <= len(counts) < 8192:
		counts = counts[:4096]
	elif 2048 <= len(counts) < 4096:
		counts = counts[:2048]

	startcounting = datetime.datetime.strptime(f'{date[:-1]} {time}','%d%b%y %H%M')
	return startcounting, real, live, np.array(counts)

def openrptfile(file,limit):
	idx, ids = None, None
	with open(file, "r") as f:
		data = [line.replace('\r\n','').replace('\n','') for line in f.readlines()]
	for i in range(len(data)):
		if 'Start time:' in data[i]:
			startcounting = datetime.datetime.strptime(f'{data[i].split()[-2]} {data[i].split()[-1][:8]}','%d/%m/%Y %H:%M:%S')
			live = float(data[i+1].split()[-1])
			real = float(data[i+2].split()[-1])
		if '*' in data[i]:
			data[i] = data[i].replace(' ','')
			if '*UNIDENTIFIEDPEAKSUMMARY*' in data[i]:
				idx = i
			elif '*IDENTIFIEDPEAKSUMMARY*' in data[i]:
				ids = i
		if '\x00\x00\x00\x00\x00' in data[i]:
			data[i] = ''
		if '\x0c' in data[i]:
			data[i] = ''
		if 'Microsoft' in data[i]:
			data[i] = ''
		if 'Centroid' in data[i]:
			data[i] = ''
		if 'Channel' in data[i]:
			data[i] = ''
		if 'ORTEC' in data[i]:
			data[i] = ''
		if 'Page' in data[i]:
			data[i] = ''
		if 'Zero offset:' in data[i]:
			try:
				Z = float((data[i].split()[-2]).replace(',','.'))
			except:
				Z = 0
		if 'Gain:' in data[i]:
			try:
				G = float((data[i].split()[-2]).replace(',','.'))
			except:
				G = 1000000.0
		if 'Quadratic:' in data[i]:
			try:
				Q = float((data[i].split()[-2]).replace(',','.'))
			except:
				Q = 0.0
		if 'Spectrum' in data[i]:
			data[i] = ''
	peaklist = []
	if idx is not None:
		while True:
			try:
				values = data[idx+4].split()
				if values != '' and values != []:
					channel, energy, background, net_area, pinten, uncert, FWHM = float(values[0].replace(',','.')), float(values[1].replace(',','.')), float(values[2].replace(',','.')), float(values[3].replace(',','.')), float(values[4].replace(',','.')), float(values[5].replace(',','.')), float(values[6].replace(',','.'))
					if net_area > 0 and uncert >= 0 and uncert < limit:
						FW = (FWHM-Z)/G
						peaklist.append([channel, 0.0, energy, 0.0 , net_area, net_area*uncert/100, FW, background])
			except:
				break
			else:
				idx += 1
	if idx is not None:
		while True:
			try:
				values = data[ids+4].split()
				if values != '' and values != []:
					channel, energy, background, net_area, pinten, uncert, FWHM = float(values[1].replace(',','.')), float(values[2].replace(',','.')), float(values[3].replace(',','.')), float(values[4].replace(',','.')), float(values[5].replace(',','.')), float(values[6].replace(',','.')), float(values[7].replace(',','.')[:-1])
					if net_area > 0 and uncert >= 0 and uncert < limit:
						FW = (FWHM-Z)/G
						peaklist.append([channel, 0.0, energy, 0.0 , net_area, net_area*uncert/100, FW, background])
			except:
				break
			else:
				ids += 1
	peaklist.sort(key=lambda x:x[0])
	return startcounting, real, live, peaklist
