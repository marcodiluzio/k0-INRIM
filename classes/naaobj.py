# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 10:30:09 2018

@author: Marco Di Luzio
"""

from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
import datetime
import numpy as np
import csv
import os
import xlsxwriter

class MergedSpectrum:
    """merge multiple spectra It is useful for calibration performed on multiple sources in different times."""
    def __init__(self,spectra):
        self.spectra = spectra
        self.peak_list = self._get_peaklist()
        
    def _get_peaklist(self):
        peaklist = []
        for spectrum in self.spectra:
            if spectrum.peak_list is not None:
                peaklist = peaklist + spectrum.peak_list
        return peaklist
        
class Spectrum:
    """define a spectrum with all attached information."""
    def __init__(self,identity='Test',start_acquisition=datetime.datetime.today(),real_time=1000,live_time=999,peak_list=None,counts=None,path=None):
        self.identity=identity#Identity(Background,Comparator,Analytes) -> str
        self.datetime=start_acquisition#StartAcquisition -> datetime
        self.real_time=real_time#Real time -> float
        self.live_time=live_time#Live time -> float
        self.peak_list=peak_list#HyperLab_peaklist ->list
        self.counts=counts#spectrum -> np.array of ints
        self.spectrumpath=path
        self.assign_nuclide=None
        
    def deadtime(self,out='str'):
        try:
            deadtime=(self.real_time-self.live_time)/self.real_time
            if out=='str':
                deadtime=deadtime*100
                deadtime=str(deadtime.__round__(2))+' %'
        except:
            if out=='str':
                deadtime='Invalid'
            else:
                deadtime=None
        return deadtime
    
    def readable_datetime(self):
        #date,time=str.split(str(self.datetime))
        #year,month,day=str.split(date,'-')
        #hour,minute,second=str.split(time,':')
        #return (day+'/'+month+'/'+year+' '+hour+':'+minute+':'+second)
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
        
class Irradiation:
    """Define irradiation conditions and channel with respective parameters"""
    def __init__(self,irradiation_end,irradiation_time,u_irradiation_time,f,uf=0,alfa=0,ualfa=0,channel_name='Not defined',code='Not defined'):
        self.code=code
        self.channel=channel_name
        self.datetime=irradiation_end
        self.time=int(irradiation_time)
        self.utime=u_irradiation_time
        self.f=f
        self.uf=uf
        self.a=alfa
        self.ua=ualfa
        
    def __repr__(self):
        return 'Irradiation '+str(self.code)+' in channel '+str(self.channel)
    
    def readable_datetime(self):
        date,time=str.split(str(self.datetime))
        year,month,day=str.split(date,'-')
        hour,minute,second=str.split(time,':')
        return (day+'/'+month+'/'+year+' '+hour+':'+minute+':'+second)
            
class Calibration:
    def __init__(self,filename):
        self.name = filename
        self.detector, self.geometry, self.energy_model, self.energy_parameters, self.fwhm_model, self.fwhm_parameters, self.efficiency_model, self.efficiency_parameters, self.efficiency_cov, der_info, self.certificate, self.x_points, self.y_points, self.spectra = self.get_calibration('data/efficiencies/'+filename+'.efs')
        self.der_type, self.der_default, self.der_udefault, self.der_hcurve, self.der_hpcov, self.der_lcurve, self.der_lpcov = der_info
        try:
            self.distance = float(self.geometry)
        except ValueError:
            self.distance = -1
        self.f_parameters = {'energy':self.energy_parameters, 'fwhm':self.fwhm_parameters, 'efficiency':self.efficiency_parameters}
        self.fits = {'linear':self.linear_model, 'quadratic':self.quadratic_model, '6term-polynomial':self.polynomial_model}
        
    def calibration_rename(self,new_name):
        self.name = new_name
        
    def double_counting_position_setup(self,E):
        log_text = []
        if self.detector == E.detector and self.certificate == E.certificate:
            if np.array_equal(self.efficiency_parameters,E.efficiency_parameters):
                #log_text.append('single counting position setup')
                return None, None, None, None, log_text
            else:
                log_text.append('double counting position setup')
                intersected, ind1, ind2 = np.intersect1d(self.x_points,E.x_points,assume_unique=True, return_indices=True)
                if len(intersected) > 6:
                    ratio = self.y_points[ind1]/E.y_points[ind2]
                    popt, pcov = self.double_counting_fit(intersected,ratio)
                    return popt, pcov, intersected, ratio, log_text
                else:
                    log_text.append('not enought experimental points to fit data')
                    return None, None, None, None, log_text
        else:
            log_text.append('calibrations refer to different detectors or different sources were used')
            return None, None, None, None, log_text
            
    def double_counting_fit(self,x,y):
        x = x/1000
        y = np.log(y)
        W=x[:, np.newaxis]**[1,0,-2,-3,-4]
        I=np.identity(W.shape[0])
        popt=np.linalg.inv(W.T@W)@(W.T@y)
        RESSR=y-(popt[0]*W[:,0]+popt[1]*W[:,1]+popt[2]*W[:,2]+popt[3]*W[:,3]+popt[4]*W[:,4])
        n,k=y.shape[0],W.shape[1]
        pcov=np.linalg.inv((W.T@np.linalg.inv(np.true_divide(1,n-k)*np.dot(RESSR,RESSR)*I))@W)
        return popt, pcov
    
    def get_calibration(self,filename):
        with open(filename,'r') as f:
            r = f.readlines()
        for i in range(len(r)):
            r[i]=r[i].replace('\n','')
        for line in range(len(r)):
            if 'detector: ' in r[line]:
                detector = r[line].replace('detector: ','')
            if 'geometry: ' in r[line]:
                geometry = r[line].replace('geometry: ','')
            if 'energy: ' in r[line]:
                energy_model = r[line].replace('energy: ','')
                energy_parameters = np.array([float(num) for num in r[line+1].split()])
            if 'fwhm: ' in r[line]:
                fwhm_model = r[line].replace('fwhm: ','')
                fwhm_parameters = np.array([float(num) for num in r[line+1].split()])
            if 'efficiency: ' in r[line]:
                efficiency_model = r[line].replace('efficiency: ','')
                efficiency_parameters = np.array([float(num) for num in r[line+1].split()])
                eff_cov = np.array([[float(num) for num in r[line+3+o].split()] for o in range(len(efficiency_parameters))])
            if 'der_kind: ' in r[line]:
                kind = r[line].replace('der_kind: ','')
                default = float(r[line+1].replace('der_value: ',''))
                udefault = float(r[line+2].replace('der_uvalue: ',''))
                h_curve = np.array([float(num) for num in r[line+4].split()])
                h_pcov = np.array([[float(num) for num in r[line+6+o].split()] for o in range(len(h_curve))])
                l_curve = np.array([float(num) for num in r[line+6+len(h_curve)+1].split()])
                l_pcov = np.array([[float(num) for num in r[line+6+len(h_curve)+3+o].split()] for o in range(len(l_curve))])
            if 'certificate: ' in r[line]:
                certificate = r[line].replace('certificate: ','')
            if 'x_points:' in r[line]:
                x_points = np.array([float(num) for num in r[line+1].split()])
            if 'y_points:' in r[line]:
                y_points = np.array([float(num) for num in r[line+1].split()])
            if 'spectra:' in r[line]:
                spectra = [name for name in r[line:] if name!='spectra:']
                break
        return detector, geometry, energy_model, energy_parameters, fwhm_model, fwhm_parameters, efficiency_model, efficiency_parameters, eff_cov, (kind,default,udefault,h_curve,h_pcov,l_curve,l_pcov), certificate, x_points, y_points, spectra
    
    def linear_model(self,pars,channel):
        parameters = self.f_parameters[pars]
        return parameters[0] * channel + parameters[1]
        
    def reverse_linear_model(self,pars,energy):
        parameters = self.f_parameters[pars]
        return (energy - parameters[1]) / parameters[0]
    
    def energy_fit(self,channel):
        fit = self.fits.get(self.energy_model,self.linear_model)
        return fit('energy',channel)
        
    def energy_fit_reversed(self,energy):
        return self.reverse_linear_model('energy',energy)
    
    def quadratic_model(self,pars,channel):
        parameters = self.f_parameters[pars]
        return np.sqrt(parameters[0] * channel + parameters[1])
    
    def fwhm_fit(self,channel):
        fit = self.fits.get(self.fwhm_model,self.linear_model)
        return fit('fwhm',channel)
    
    def polynomial_model(self,pars,energy):
        parameters = self.f_parameters[pars]
        return np.exp(parameters[0]*energy + parameters[1] + parameters[2]*np.power(energy,-1) + parameters[3]*np.power(energy,-2) + parameters[4]*np.power(energy,-3) + parameters[5]*np.power(energy,-4))
    
    def efficiency_fit(self,energy):
        energy = energy/1000
        fit = self.fits.get(self.efficiency_model,self.linear_model)
        return fit('efficiency',energy)
    
    def der_fit(self,energy):
        x_range = energy / 1000
        if self.der_type == 'default':
            der, uder = np.array([self.der_default for xx in x_range]), np.array([self.der_udefault for xx in x_range])
        else:
            esp = [1,0,-1,-2,-3,-4]
            x_range = x_range[:,np.newaxis]**esp[:len(self.der_hcurve)]
            der = np.array((np.exp(self.der_hcurve@x_range.T) - np.exp(self.der_lcurve@x_range.T))/(np.exp(self.efficiency_parameters[:len(self.der_hcurve)]@x_range.T) * self.der_default))
            uderpcov = np.identity(19)
            uderpcov[0:len(self.der_hpcov),0:len(self.der_hpcov)] = self.der_hpcov
            uderpcov[6:6+len(self.der_lpcov),6:6+len(self.der_lpcov)] = self.der_lpcov
            uderpcov[12:12+len(self.efficiency_cov),12:12+len(self.efficiency_cov)] = self.efficiency_cov
            uderpcov[18,18] = np.power(self.der_udefault,2)
            udererr = np.sqrt(np.diag(uderpcov))
            uderparams = [0]*18
            uderparams.append(self.der_default)
            uderparams = np.array(uderparams)
            uderparams[0:0+len(self.der_hcurve)] = self.der_hcurve
            uderparams[6:6+len(self.der_lcurve)] = self.der_lcurve
            uderparams[12:12+len(self.efficiency_parameters)] = self.efficiency_parameters
            uder = []
            for energypin in x_range:
                ci_arrary = []
                for i in range(len(uderparams)):
                    copyp = uderparams[:]
                    copym = uderparams[:]
                    copyp[i] = uderparams[i] + udererr[i]
                    copym[i] = uderparams[i] - udererr[i]
                    v = (((np.exp(copyp[:len(self.der_hcurve)]@energypin) - np.exp(copyp[6:6+len(self.der_hcurve)]@energypin))/(np.exp(copyp[12:12+len(self.der_hcurve)]@energypin) * copyp[-1:])) - ((np.exp(copym[:len(self.der_hcurve)]@energypin) - np.exp(copym[6:6+len(self.der_hcurve)]@energypin))/(np.exp(copym[12:12+len(self.der_hcurve)]@energypin) * copym[-1:]))) / (2*udererr[i]+1E-9)
                    ci_arrary.append(float(v))
                ci_arrary = np.array(ci_arrary)
                uder.append(ci_arrary.T@uderpcov@ci_arrary)
            uder = np.array(uder)
        return der, uder
        
class GSource:
    def __init__(self,dt,E,Tg,Bq,gY,l):
        date,time=str.split(str(dt))
        day,month,year=str.split(date,'/')
        hour,minute,second=str.split(time,':')
        self.datetime=datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(second))
        self.energy=E
        self.emitter=Tg
        self.activity=Bq
        self.g_yield=gY
        self.decay_constant=l
        
    def readable_datetime(self):
        date,time=str.split(str(self.datetime))
        year,month,day=str.split(date,'-')
        hour,minute,second=str.split(time,':')
        return (day+'/'+month+'/'+year+' '+hour+':'+minute+':'+second)
    
class NAAnalysis:
    """Define the actual analysis"""
    def __init__(self):
        self.irradiation=None
        self.comparator=None
        self.ddcomparator=None
        self.sample=None
        self.ddsample=None
        self.calibration = None
        self.masses=[None,None,None,None]
        self.quantification=None
        self.detection_limits_FWHM=3
        self.selected_nuclides=[]
        self.background=None
        self.enegybackgroundfit=None
        self.fwhmbackgroundfit=None
        self.efficiencybackgroundfit=None
        self.standard_comparator=None
        self.relative_method=None
        self.detector_mu=[None,None]
        self.comparatorselfshieldingth=[None,None]
        self.comparatorselfshieldingepi=[None,None]
        self.sampleselfshieldingth=[None,None]
        self.comparatorCOI=[None,None]
        self.comparatormassfraction=[None,None]
        self.default_utdm=None#seconds
        self.default_udeltatd=None#seconds
        self.default_utc=None#seconds
        self.default_uE=None#keV
        self.beta_flux=[None,None]
        self._Delta_x=[None,None]
        self.info = {}
    
    def set_backgroungspectrum(self,S):
        if type(S)==Spectrum:
            self.background=S
            
    def set_comparatorspectrum(self,S):
        if type(S)==Spectrum:
            self.comparator=S
            
    def set_samplespectrum(self,S):
        if type(S)==Spectrum:
            try:
                self.sample.append(S)#lists!
            except:
                self.sample=[]
                self.sample.append(S)
                
    def set_irradiation(self,I):
        if type(I)==Irradiation:
            self.irradiation=I
            
    def set_efficiency_calibration(self,filename,identity='Standard'):
        try:
            self.calibration = Calibration(filename)
        except TypeError:
            self.calibration = None
            
    def set_matrix_typeI(self,iline,monitor,nn):
        HDGS=['ti','np,a','λ,a','td,a','tc,a','tl,a','COI,a','w,a','k0,Au(a)','Gth,a','Ge,a','Q0,a','Er,a','np,c','λ,c','td,c','tc,c','tl,c','COI,c','w,c','m,c','k0,Au(c)','Gth,c','Ge,c','Q0,c','Er,c','f','α','A1','A2','A3','A4','A5','A6','Ea','Ec','dεra','dεrc','dda','ddc','µ','β','ddx']
        MP=np.zeros((len(HDGS),2))
        MP[0,0],MP[0,1],MP[1,0],MP[1,1]=float(self.irradiation.time),float(self.irradiation.utime),float(iline[8]),float(iline[9])
        if iline[53]=='M':
            U=60
        elif iline[53]=='H':
            U=3600
        elif iline[53]=='D':
            U=86400
        elif iline[53]=='Y':
            U=86400*365.24
        else:
            U=1
        L=np.log(2)/(float(iline[52])*U)
        uL=float(iline[54])/float(iline[52])*L
        MP[2,0],MP[2,1]=L,uL
        dc=self.sample[nn].datetime-self.comparator.datetime
        td=dc.days*86400+dc.seconds
        MP[3,0],MP[3,1],MP[4,0],MP[4,1],MP[5,0],MP[5,1],MP[6,0],MP[6,1]=td,self.default_udeltatd,self.sample[nn].real_time,self.default_utc,self.sample[nn].live_time,self.default_utc,1.0,0.0
        MP[7,0],MP[7,1]=self.masses[2],self.masses[3]
        if iline[29]!='':
            uk0=iline[29]*iline[28]/100
        else:
            uk0=0.02*iline[28]
        MP[8,0],MP[8,1],MP[9,0],MP[9,1],MP[10,0],MP[10,1]=iline[28],uk0,self.sampleselfshieldingth[0],self.sampleselfshieldingth[1],1.0,0.0
        if iline[97]!='':
            uQ=iline[96]*iline[97]/100
        else:
            uQ=iline[96]*0.2
        MP[11,0],MP[11,1]=iline[96],uQ
        if iline[99]!='':
            uE=iline[98]*iline[99]/100
        else:
            uE=iline[98]*0.5
        MP[12,0],MP[12,1]=iline[98],uE
        MP[13,0],MP[13,1]=float(monitor[8]),float(monitor[9])
        if monitor[53]=='M':
            U=60
        elif monitor[53]=='H':
            U=3600
        elif monitor[53]=='D':
            U=86400
        elif monitor[53]=='Y':
            U=86400*365.24
        else:
            U=1
        L=np.log(2)/(float(monitor[52])*U)
        uL=float(monitor[54])/float(monitor[52])*L
        MP[14,0],MP[14,1]=L,uL
        dc=self.comparator.datetime-self.irradiation.datetime
        td=dc.days*86400+dc.seconds
        MP[15,0],MP[15,1],MP[16,0],MP[16,1],MP[17,0],MP[17,1]=td,self.default_utdm,self.comparator.real_time,0.01,self.comparator.live_time,0.01
        MP[18,0],MP[18,1],MP[19,0],MP[19,1]=self.comparatorCOI[0],self.comparatorCOI[1],self.masses[0],self.masses[1]
        if monitor[29]!='':
            uk0=monitor[29]*monitor[28]/100
        else:
            uk0=0.02*monitor[28]
        MP[20,0],MP[20,1],MP[21,0],MP[21,1],MP[22,0],MP[22,1],MP[23,0],MP[23,1]=self.comparatormassfraction[0],self.comparatormassfraction[1],monitor[28],uk0,self.comparatorselfshieldingth[0],self.comparatorselfshieldingth[1],self.comparatorselfshieldingepi[0],self.comparatorselfshieldingepi[1]
        if monitor[97]!='':
            uQ=monitor[96]*monitor[97]/100
        else:
            uQ=monitor[96]*0.2
        MP[24,0],MP[24,1]=monitor[96],uQ
        if monitor[99]!='':
            uE=monitor[98]*monitor[99]/100
        else:
            uE=monitor[98]*0.5
        MP[25,0],MP[25,1],MP[26,0],MP[26,1],MP[27,0],MP[27,1]=monitor[98],uE,self.irradiation.f,self.irradiation.uf,self.irradiation.a,self.irradiation.ua
        MP[28:34,0]=self.calibration.efficiency_parameters
        MP[28:34,1]=np.sqrt(np.diag(self.calibration.efficiency_cov))
        MP[34,0],MP[34,1]=iline[26]/1000,self.default_uE/1000
        MP[35,0],MP[35,1]=monitor[26]/1000,self.default_uE/1000
        der, uder = self.calibration.der_fit(np.array([monitor[26]]))
        MP[36,0],MP[36,1]=der, uder
        der, uder = self.calibration.der_fit(np.array([iline[26]]))
        MP[37,0],MP[37,1]=der, uder
        MP[38,0],MP[38,1]=0,self.ddsample
        MP[39,0],MP[39,1]=0,self.ddcomparator
        MP[40,0],MP[40,1]=self.detector_mu[0],self.detector_mu[1]
        MP[41,0],MP[41,1]=self.beta_flux[0],self.beta_flux[1]
        MP[42,0],MP[42,1]=self._Delta_x[0],self._Delta_x[1]
        #Correlations
        MC=np.identity((len(HDGS)))
        corr = np.identity(len(self.calibration.efficiency_cov))
        st_unc = np.sqrt(np.diag(self.calibration.efficiency_cov))
        for il in range(len(st_unc)):
            for ik in range(len(st_unc)):
                if st_unc[il]!=0 and st_unc[ik]!=0:
                    corr[il,ik] = self.calibration.efficiency_cov[il,ik] / (st_unc[il] * st_unc[ik])
                else:
                    corr[il,ik] = 0
        MC[28:28+len(self.calibration.efficiency_cov),28:28+len(self.calibration.efficiency_cov)]=corr
        if monitor[98]==iline[98] and monitor[96]==iline[96]:#condition for same emitting isotope
            MC[HDGS.index('λ,a'),HDGS.index('λ,c')],MC[HDGS.index('λ,c'),HDGS.index('λ,a')]=1.0,1.0
            MC[HDGS.index('Q0,a'),HDGS.index('Q0,c')],MC[HDGS.index('Q0,c'),HDGS.index('Q0,a')]=1.0,1.0
            MC[HDGS.index('Er,a'),HDGS.index('Er,c')],MC[HDGS.index('Er,c'),HDGS.index('Er,a')]=1.0,1.0
            if monitor[28]==iline[28] and monitor[26]==iline[26] and monitor[22]==iline[22]:#relative analysis conditions
                MC[HDGS.index('k0,Au(a)'),HDGS.index('k0,Au(c)')],MC[HDGS.index('k0,Au(c)'),HDGS.index('k0,Au(a)')]=1.0,1.0
                MC[HDGS.index('Ea'),HDGS.index('Ec')],MC[HDGS.index('Ec'),HDGS.index('Ea')]=1.0,1.0
                MC[HDGS.index('COI,a'),HDGS.index('COI,c')],MC[HDGS.index('COI,c'),HDGS.index('COI,a')]=1.0,1.0
        return MP,MC
    
    def set_matrix_detectiontypeI(self,iline,monitor,nn): #here is the key!
        HDGS=['ti','np,a','λ,a','td,a','tc,a','tl,a','COI,a','w,a','k0,Au(a)','Gth,a','Ge,a','Q0,a','Er,a','np,c','λ,c','td,c','tc,c','tl,c','COI,c','w,c','m,c','k0,Au(c)','Gth,c','Ge,c','Q0,c','Er,c','f','α','A1','A2','A3','A4','A5','A6','Ea','Ec','dεra','dεrc','dda','ddc','µ','β','ddx']
        channel_position = self.calibration.energy_fit_reversed(iline[5])
        detectionlimitrange=int(self.detection_limits_FWHM*self.calibration.fwhm_fit(channel_position))+1
        AD=self.sample[nn].defined_spectrum_integral(int(channel_position-detectionlimitrange/2),detectionlimitrange)
        if AD!=None and AD>0:
            MP=np.zeros((len(HDGS),2))
            MP[0,0],MP[0,1],MP[1,0],MP[1,1]=float(self.irradiation.time),0.0,2.71+3.29*np.sqrt(AD),0.0
            if iline[32]=='M':
                U=60
            elif iline[32]=='H':
                U=3600
            elif iline[32]=='D':
                U=86400
            elif iline[32]=='Y':
                U=86400*365.24
            else:
                U=1
            L=np.log(2)/(float(iline[31])*U)
            MP[2,0],MP[2,1]=L,0.0
            dc=self.sample[nn].datetime-self.comparator.datetime
            td=dc.days*86400+dc.seconds
            MP[3,0],MP[3,1],MP[4,0],MP[4,1],MP[5,0],MP[5,1],MP[6,0],MP[6,1]=td,0.0,self.sample[nn].real_time,0.0,self.sample[nn].live_time,0.0,1.0,0.0
            MP[7,0],MP[7,1]=self.masses[2],0.0
            MP[8,0],MP[8,1],MP[9,0],MP[9,1],MP[10,0],MP[10,1]=iline[7],0.0,self.sampleselfshieldingth[0],0.0,1.0,0.0
            MP[11,0],MP[11,1]=iline[75],0.0
            MP[12,0],MP[12,1]=iline[77],0.0
            MP[13,0],MP[13,1]=float(monitor[8]),0.0
            if monitor[53]=='M':
                U=60
            elif monitor[53]=='H':
                U=3600
            elif monitor[53]=='D':
                U=86400
            elif monitor[53]=='Y':
                U=86400*365.24
            else:
                U=1
            L=np.log(2)/(float(monitor[52])*U)
            MP[14,0],MP[14,1]=L,0.0
            dc=self.comparator.datetime-self.irradiation.datetime
            td=dc.days*86400+dc.seconds
            MP[15,0],MP[15,1],MP[16,0],MP[16,1],MP[17,0],MP[17,1]=td,0.0,self.comparator.real_time,0.0,self.comparator.live_time,0.0
            MP[18,0],MP[18,1],MP[19,0],MP[19,1]=self.comparatorCOI[0],0.0,self.masses[0],0.0
            MP[20,0],MP[20,1],MP[21,0],MP[21,1],MP[22,0],MP[22,1],MP[23,0],MP[23,1]=self.comparatormassfraction[0],0.0,monitor[28],0.0,self.comparatorselfshieldingth[0],0.0,self.comparatorselfshieldingepi[0],0.0
            MP[24,0],MP[24,1]=monitor[96],0.0
            MP[25,0],MP[25,1],MP[26,0],MP[26,1],MP[27,0],MP[27,1]=monitor[98],0.0,self.irradiation.f,0.0,self.irradiation.a,0.0
            MP[28:34,0]=self.calibration.efficiency_parameters
            MP[28:34,1]=np.sqrt(np.diag(self.calibration.efficiency_cov))
            MP[34,0],MP[34,1]=iline[5]/1000,0.0
            MP[35,0],MP[35,1]=monitor[26]/1000,0.0
            der, uder = self.calibration.der_fit(np.array([monitor[26]]))
            MP[36,0],MP[36,1]=der, uder
            der, uder = self.calibration.der_fit(np.array([iline[5]]))
            MP[37,0],MP[37,1]=der, uder
            MP[38,0],MP[38,1]=0,self.ddsample
            MP[39,0],MP[39,1]=0,self.ddcomparator
            MP[40,0],MP[40,1]=self.detector_mu[0],0.0
            MP[41,0],MP[41,1]=self.beta_flux[0],0
            MP[42,0],MP[42,1]=self._Delta_x[0],0
            #Correlations
            MC=np.identity((len(HDGS)))
            corr = np.identity(len(self.calibration.efficiency_cov))
            MC[28:28+len(self.calibration.efficiency_cov),28:28+len(self.calibration.efficiency_cov)]=corr #it's all right since it doesn't propagate
            if monitor[98]==iline[77] and monitor[96]==iline[75]:#condition for same emitting isotope
                MC[HDGS.index('λ,a'),HDGS.index('λ,c')],MC[HDGS.index('λ,c'),HDGS.index('λ,a')]=1.0,1.0
                MC[HDGS.index('Q0,a'),HDGS.index('Q0,c')],MC[HDGS.index('Q0,c'),HDGS.index('Q0,a')]=1.0,1.0
                MC[HDGS.index('Er,a'),HDGS.index('Er,c')],MC[HDGS.index('Er,c'),HDGS.index('Er,a')]=1.0,1.0
                if monitor[28]==iline[7] and monitor[26]==iline[5] and monitor[22]==iline[1]:#condition for relative analysis
                    MC[HDGS.index('k0,Au(a)'),HDGS.index('k0,Au(c)')],MC[HDGS.index('k0,Au(c)'),HDGS.index('k0,Au(a)')]=1.0,1.0
                    MC[HDGS.index('Ea'),HDGS.index('Ec')],MC[HDGS.index('Ec'),HDGS.index('Ea')]=1.0,1.0
                    MC[HDGS.index('COI,a'),HDGS.index('COI,c')],MC[HDGS.index('COI,c'),HDGS.index('COI,a')]=1.0,1.0
        else:
            MP,MC=None,None
        return MP,MC
        
    def set_matrix_typeIIA(self,iline,monitor,nn):#index 3 added!
        HDGS=['ti','np,a','λ,a','λ2,a','td,a','tc,a','tl,a','COI,a','w,a','k0,Au(a)','Gth,a','Ge,a','Q0,a','Er,a','np,c','λ,c','td,c','tc,c','tl,c','COI,c','w,c','m,c','k0,Au(c)','Gth,c','Ge,c','Q0,c','Er,c','f','α','A1','A2','A3','A4','A5','A6','Ea','Ec','dεra','dεrc','dda','ddc','µ','β','ddx']
        MP=np.zeros((len(HDGS),2))
        MP[0,0],MP[0,1],MP[1,0],MP[1,1]=float(self.irradiation.time),float(self.irradiation.utime),float(iline[8]),float(iline[9])
        if iline[53]=='M':
            U=60
        elif iline[53]=='H':
            U=3600
        elif iline[53]=='D':
            U=86400
        elif iline[53]=='Y':
            U=86400*365.24
        else:
            U=1
        L=np.log(2)/(float(iline[52])*U)
        uL=float(iline[54])/float(iline[52])*L
        MP[2,0],MP[2,1]=L,uL
        if iline[66]=='M':
            U=60
        elif iline[66]=='H':
            U=3600
        elif iline[66]=='D':
            U=86400
        elif iline[66]=='Y':
            U=86400*365.24
        else:
            U=1
        L=np.log(2)/(float(iline[65])*U)
        uL=float(iline[67])/float(iline[65])*L
        MP[3,0],MP[3,1]=L,uL #+1 from here, done!
        dc=self.sample[nn].datetime-self.comparator.datetime
        td=dc.days*86400+dc.seconds
        MP[4,0],MP[4,1],MP[5,0],MP[5,1],MP[6,0],MP[6,1],MP[7,0],MP[7,1]=td,self.default_udeltatd,self.sample[nn].real_time,self.default_utc,self.sample[nn].live_time,self.default_utc,1.0,0.0
        MP[8,0],MP[8,1]=self.masses[2],self.masses[3]
        if iline[29]!='':
            uk0=iline[29]*iline[28]/100
        else:
            uk0=0.02*iline[28]
        MP[9,0],MP[9,1],MP[10,0],MP[10,1],MP[11,0],MP[11,1]=iline[28],uk0,self.sampleselfshieldingth[0],self.sampleselfshieldingth[1],1.0,0.0
        if iline[97]!='':
            uQ=iline[96]*iline[97]/100
        else:
            uQ=iline[96]*0.2
        MP[12,0],MP[12,1]=iline[96],uQ
        if iline[99]!='':
            uE=iline[98]*iline[99]/100
        else:
            uE=iline[98]*0.5
        MP[13,0],MP[13,1]=iline[98],uE
        MP[14,0],MP[14,1]=float(monitor[8]),float(monitor[9])
        if monitor[53]=='M':
            U=60
        elif monitor[53]=='H':
            U=3600
        elif monitor[53]=='D':
            U=86400
        elif monitor[53]=='Y':
            U=86400*365.24
        else:
            U=1
        L=np.log(2)/(float(monitor[52])*U)
        uL=float(monitor[54])/float(monitor[52])*L
        MP[15,0],MP[15,1]=L,uL
        dc=self.comparator.datetime-self.irradiation.datetime
        td=dc.days*86400+dc.seconds
        MP[16,0],MP[16,1],MP[17,0],MP[17,1],MP[18,0],MP[18,1]=td,self.default_utdm,self.comparator.real_time,0.01,self.comparator.live_time,0.01
        MP[19,0],MP[19,1],MP[20,0],MP[20,1]=self.comparatorCOI[0],self.comparatorCOI[1],self.masses[0],self.masses[1]
        if monitor[29]!='':
            uk0=monitor[29]*monitor[28]/100
        else:
            uk0=0.02*monitor[28]
        MP[21,0],MP[21,1],MP[22,0],MP[22,1],MP[23,0],MP[23,1],MP[24,0],MP[24,1]=self.comparatormassfraction[0],self.comparatormassfraction[1],monitor[28],uk0,self.comparatorselfshieldingth[0],self.comparatorselfshieldingth[1],self.comparatorselfshieldingepi[0],self.comparatorselfshieldingepi[1]
        if monitor[97]!='':
            uQ=monitor[96]*monitor[97]/100
        else:
            uQ=monitor[96]*0.2
        MP[25,0],MP[25,1]=monitor[96],uQ
        if monitor[99]!='':
            uE=monitor[98]*monitor[99]/100
        else:
            uE=monitor[98]*0.5
        MP[26,0],MP[26,1],MP[27,0],MP[27,1],MP[28,0],MP[28,1]=monitor[98],uE,self.irradiation.f,self.irradiation.uf,self.irradiation.a,self.irradiation.ua
        MP[29:35,0]=self.calibration.efficiency_parameters
        MP[29:35,1]=np.sqrt(np.diag(self.calibration.efficiency_cov))
        MP[35,0],MP[35,1]=iline[26]/1000,self.default_uE/1000
        MP[36,0],MP[36,1]=monitor[26]/1000,self.default_uE/1000
        der, uder = self.calibration.der_fit(np.array([monitor[26]]))
        MP[37,0],MP[37,1]=der, uder
        der, uder = self.calibration.der_fit(np.array([iline[26]]))
        MP[38,0],MP[38,1]=der, uder
        MP[39,0],MP[39,1]=0,self.ddsample
        MP[40,0],MP[40,1]=0,self.ddcomparator
        MP[41,0],MP[41,1]=self.detector_mu[0],self.detector_mu[1]
        MP[42,0],MP[42,1]=self.beta_flux[0],self.beta_flux[1]
        MP[43,0],MP[43,1]=self._Delta_x[0],self._Delta_x[1]
        #Correlations
        MC=np.identity((len(HDGS)))
        corr = np.identity(len(self.calibration.efficiency_cov))
        st_unc = np.sqrt(np.diag(self.calibration.efficiency_cov))
        for il in range(len(st_unc)):
            for ik in range(len(st_unc)):
                if st_unc[il]!=0 and st_unc[ik]!=0:
                    corr[il,ik] = self.calibration.efficiency_cov[il,ik] / (st_unc[il] * st_unc[ik])
                else:
                    corr[il,ik] = 0
        MC[29:29+len(self.calibration.efficiency_cov),29:29+len(self.calibration.efficiency_cov)]=corr
        if monitor[98]==iline[98] and monitor[96]==iline[96]:#condition for same emitting isotope
            MC[HDGS.index('λ,a'),HDGS.index('λ,c')],MC[HDGS.index('λ,c'),HDGS.index('λ,a')]=1.0,1.0
            MC[HDGS.index('Q0,a'),HDGS.index('Q0,c')],MC[HDGS.index('Q0,c'),HDGS.index('Q0,a')]=1.0,1.0
            MC[HDGS.index('Er,a'),HDGS.index('Er,c')],MC[HDGS.index('Er,c'),HDGS.index('Er,a')]=1.0,1.0
            if monitor[28]==iline[28] and monitor[26]==iline[26] and monitor[22]==iline[22]:#relative analysis conditions
                MC[HDGS.index('k0,Au(a)'),HDGS.index('k0,Au(c)')],MC[HDGS.index('k0,Au(c)'),HDGS.index('k0,Au(a)')]=1.0,1.0
                MC[HDGS.index('Ea'),HDGS.index('Ec')],MC[HDGS.index('Ec'),HDGS.index('Ea')]=1.0,1.0
                MC[HDGS.index('COI,a'),HDGS.index('COI,c')],MC[HDGS.index('COI,c'),HDGS.index('COI,a')]=1.0,1.0
        return MP,MC
    
    def set_matrix_detectiontypeIIA(self,iline,monitor,nn): #here is the key!
        HDGS=['ti','np,a','λ,a','λ2,a','td,a','tc,a','tl,a','COI,a','w,a','k0,Au(a)','Gth,a','Ge,a','Q0,a','Er,a','np,c','λ,c','td,c','tc,c','tl,c','COI,c','w,c','m,c','k0,Au(c)','Gth,c','Ge,c','Q0,c','Er,c','f','α','A1','A2','A3','A4','A5','A6','Ea','Ec','dεra','dεrc','dda','ddc','µ','β','ddx']
        channel_position = self.calibration.energy_fit_reversed(iline[5])
        detectionlimitrange=int(self.detection_limits_FWHM*self.calibration.fwhm_fit(channel_position))+1
        AD=self.sample[nn].defined_spectrum_integral(int(channel_position-detectionlimitrange/2),detectionlimitrange)
        if AD!=None and AD>0:
            MP=np.zeros((len(HDGS),2))
            MP[0,0],MP[0,1],MP[1,0],MP[1,1]=float(self.irradiation.time),0.0,2.71+3.29*np.sqrt(AD),0.0
            if iline[32]=='M':
                U=60
            elif iline[32]=='H':
                U=3600
            elif iline[32]=='D':
                U=86400
            elif iline[32]=='Y':
                U=86400*365.24
            else:
                U=1
            L=np.log(2)/(float(iline[31])*U)
            MP[2,0],MP[2,1]=L,0.0            
            if iline[45]=='M':
                U=60
            elif iline[45]=='H':
                U=3600
            elif iline[45]=='D':
                U=86400
            elif iline[45]=='Y':
                U=86400*365.24
            else:
                U=1
            L=np.log(2)/(float(iline[44])*U)
            MP[3,0],MP[3,1]=L,0.0
            dc=self.sample[nn].datetime-self.comparator.datetime
            td=dc.days*86400+dc.seconds
            MP[4,0],MP[4,1],MP[5,0],MP[5,1],MP[6,0],MP[6,1],MP[7,0],MP[7,1]=td,0.0,self.sample[nn].real_time,0.0,self.sample[nn].live_time,0.0,1.0,0.0
            MP[8,0],MP[8,1]=self.masses[2],0.0
            MP[9,0],MP[9,1],MP[10,0],MP[10,1],MP[11,0],MP[11,1]=iline[7],0.0,self.sampleselfshieldingth[0],0.0,1.0,0.0
            MP[12,0],MP[12,1]=iline[75],0.0
            MP[13,0],MP[13,1]=iline[77],0.0
            MP[14,0],MP[14,1]=float(monitor[8]),0.0
            if monitor[53]=='M':#53
                U=60
            elif monitor[53]=='H':#53
                U=3600
            elif monitor[53]=='D':#53
                U=86400
            elif monitor[53]=='Y':#53
                U=86400*365.24
            else:
                U=1
            L=np.log(2)/(float(monitor[52])*U)#52
            MP[15,0],MP[15,1]=L,0.0
            dc=self.comparator.datetime-self.irradiation.datetime
            td=dc.days*86400+dc.seconds
            MP[16,0],MP[16,1],MP[17,0],MP[17,1],MP[18,0],MP[18,1]=td,0.0,self.comparator.real_time,0.0,self.comparator.live_time,0.0
            MP[19,0],MP[19,1],MP[20,0],MP[20,1]=self.comparatorCOI[0],0.0,self.masses[0],0.0
            MP[21,0],MP[21,1],MP[22,0],MP[22,1],MP[23,0],MP[23,1],MP[24,0],MP[24,1]=self.comparatormassfraction[0],0.0,monitor[28],0.0,self.comparatorselfshieldingth[0],0.0,self.comparatorselfshieldingepi[0],0.0
            MP[25,0],MP[25,1]=monitor[96],0.0
            MP[26,0],MP[26,1],MP[27,0],MP[27,1],MP[28,0],MP[28,1]=monitor[98],0.0,self.irradiation.f,0.0,self.irradiation.a,0.0
            MP[29:35,0]=self.calibration.efficiency_parameters
            MP[29:35,1]=np.sqrt(np.diag(self.calibration.efficiency_cov))
            MP[35,0],MP[35,1]=iline[5]/1000,0.0
            MP[36,0],MP[36,1]=monitor[26]/1000,0.0
            der, uder = self.calibration.der_fit(np.array([monitor[26]]))
            MP[37,0],MP[37,1]=der, uder
            der, uder = self.calibration.der_fit(np.array([iline[5]]))
            MP[38,0],MP[38,1]=der, uder
            MP[39,0],MP[39,1]=0,self.ddsample
            MP[40,0],MP[40,1]=0,self.ddcomparator
            MP[41,0],MP[41,1]=self.detector_mu[0],0.0
            MP[42,0],MP[42,1]=self.beta_flux[0],0.0
            MP[43,0],MP[43,1]=self._Delta_x[0],0.0
            #Correlations
            MC=np.identity((len(HDGS)))
            corr = np.identity(len(self.calibration.efficiency_cov))
            MC[28:28+len(self.calibration.efficiency_cov),28:28+len(self.calibration.efficiency_cov)]=corr #it's all right since it doesn't propagate
            if monitor[98]==iline[77] and monitor[96]==iline[75]:#condition for same emitting isotope
                MC[HDGS.index('λ,a'),HDGS.index('λ,c')],MC[HDGS.index('λ,c'),HDGS.index('λ,a')]=1.0,1.0
                MC[HDGS.index('Q0,a'),HDGS.index('Q0,c')],MC[HDGS.index('Q0,c'),HDGS.index('Q0,a')]=1.0,1.0
                MC[HDGS.index('Er,a'),HDGS.index('Er,c')],MC[HDGS.index('Er,c'),HDGS.index('Er,a')]=1.0,1.0
                if monitor[28]==iline[7] and monitor[26]==iline[5] and monitor[22]==iline[1]:#condition for relative analysis
                    MC[HDGS.index('k0,Au(a)'),HDGS.index('k0,Au(c)')],MC[HDGS.index('k0,Au(c)'),HDGS.index('k0,Au(a)')]=1.0,1.0
                    MC[HDGS.index('Ea'),HDGS.index('Ec')],MC[HDGS.index('Ec'),HDGS.index('Ea')]=1.0,1.0
                    MC[HDGS.index('COI,a'),HDGS.index('COI,c')],MC[HDGS.index('COI,c'),HDGS.index('COI,a')]=1.0,1.0
        else:
            MP,MC=None,None
        return MP,MC
            
    def define_matrix(self,iline,monitor,nn):
        if iline[43]=='I' or iline[43]=='IVB' or iline[43]=='IIB' or iline[43]=='VI' or iline[43]=='VB':
            MP,MC=self.set_matrix_typeI(iline,monitor,nn)
        elif iline[43]=='IIA':
            MP,MC=self.set_matrix_typeIIA(iline,monitor,nn)
        elif iline[43]=='VC':
            MP,MC=self.set_matrix_typeI(iline,monitor,nn)
            if iline[66]=='M':
                U=60
            elif iline[66]=='H':
                U=3600
            elif iline[66]=='D':
                U=86400
            elif iline[66]=='Y':
                U=86400*365.24
            else:
                U=1
            L=np.log(2)/(float(iline[65])*U)
            uL=float(iline[67])/float(iline[65])*L
            MP[2,0],MP[2,1]=L,uL
        else:
            MP,MC=None,None
        return MP,MC
    
    def define_matrix_detection(self,iline,monitor,nn):
        if iline[22]=='I' or iline[22]=='IVB' or iline[22]=='IIB' or iline[22]=='VI' or iline[22]=='VB':
            MP,MC=self.set_matrix_detectiontypeI(iline,monitor,nn)
        elif iline[22]=='IIA':
            MP,MC=self.set_matrix_detectiontypeIIA(iline,monitor,nn)
        elif iline[22]=='VC':
            MP,MC=self.set_matrix_detectiontypeI(iline,monitor,nn)
            if iline[45]=='M':
                U=60
            elif iline[45]=='H':
                U=3600
            elif iline[45]=='D':
                U=86400
            elif iline[45]=='Y':
                U=86400*365.24
            else:
                U=1
            L=np.log(2)/(float(iline[44])*U)
            MP[2,0],MP[2,1]=L,0.0
        else:
            MP,MC=None,None
        return MP,MC
            
    def analysis_from_assignednuclides(self,total_assigned_peaklist,monitor):
        self.quantification=[]
        nn=0
        for i in total_assigned_peaklist:
            if i==[] or i==None:
                self.quantification.append(None)
            else:
                spectrum_x=[]
                for th in i:
                    Mtrx=self.define_matrix(th,monitor,nn)
                    spectrum_x.append(Mtrx)
                self.quantification.append(spectrum_x)
            nn+=1
            
    def analysis_from_nuclidelist(self,monitor,nuclide_list,i,tolerance):
        nuclide_quantified_list=[]
        nuclide_detection_list=[]
        quantifiedMatrix_list=[]
        detectionMatrix_list=[]
        for ok in nuclide_list:
            nuclide_detection_list.append(ok)
            MD=self.define_matrix_detection(ok,monitor,i)
            detectionMatrix_list.append(MD)
        return nuclide_quantified_list,nuclide_detection_list,quantifiedMatrix_list,detectionMatrix_list
        
def openhyperlabfile(file,unclimit=40):
    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        S=[]
        for row in spamreader:
            S.append(row)
        S.pop(0)
        S = [line for line in S if float(line[9])/float(line[8])*100 < unclimit]
        return S
    
def read_rptfile2(file,statslim=40,set_forall=True):
    idx, ids = None, None
    def takeSecond(elem):
        return float(elem[4])
    def taketime(date,time):
        giorno, mese, anno = date.split('/')
        ore, minuti, secondi = time.split(':')
        dt = datetime.datetime(int(anno),int(mese),int(giorno),int(ore),int(minuti),int(secondi))
        return dt
    #statslim=40
    with open(file, "r") as f:
        data=f.readlines()
        for i in range(len(data)):
            data[i]=data[i].replace('\r\n','')
            data[i]=data[i].replace('\n','')
            if 'Start time:' in data[i]:
                strtime=data[i].split()[-2],data[i].split()[-1][:8]
                lvtime=int(data[i+1].split()[-1])
                rltime=int(data[i+2].split()[-1])
            if '*' in data[i]:
                data[i]=data[i].replace(' ','')
                if '*UNIDENTIFIEDPEAKSUMMARY*' in data[i]:
                    idx=i
                elif '*IDENTIFIEDPEAKSUMMARY*' in data[i]:
                    ids=i
            if '\x00\x00\x00\x00\x00' in data[i]:
                data[i]=''
            if '\x0c' in data[i]:
                data[i]=''
            if 'Microsoft' in data[i]:
                data[i]=''
            if 'Centroid' in data[i]:
                data[i]=''
            if 'Channel' in data[i]:
                data[i]=''
            if 'ORTEC' in data[i]:
                data[i]=''
            if 'Page' in data[i]:
                data[i]=''
            if 'Zero offset:' in data[i]:
                Z=str.split(data[i])[-2]
                try:
                    Z=float(Z)
                except:
                    Z=0
            if 'Gain:' in data[i]:
                G=str.split(data[i])[-2]
                try:
                    G=float(G)
                except:
                    G=1000000
            if 'Quadratic:' in data[i]:
                Q=str.split(data[i])[-2]
                try:
                    Q=float(Q)
                except:
                    Q=0
            if 'Spectrum' in data[i]:
                data[i]=''
    startcounting=taketime(*strtime)
    peaklist=[]
    if idx is not None:
        while idx>-1:
            try:
                values=str.split(data[idx+4])
                if values!='' and values!=[]:
                    float(values[0].replace(',','.')),float(values[1].replace(',','.')),float(values[2].replace(',','.')),float(values[3].replace(',','.')),float(values[4].replace(',','.')),float(values[5].replace(',','.')),float(values[6].replace(',','.'))
                    if float(values[3].replace(',','.'))>0 and float(values[5].replace(',','.'))>0 and float(values[5].replace(',','.'))<statslim:
                        fpc=str(float(values[3].replace(',','.'))*float(values[5].replace(',','.'))/100)
                        FW=(float(values[6].replace(',','.'))-Z)/G
                        peaklist.append(['','','','',values[0].replace(',','.'),'',values[1].replace(',','.'),'',values[3].replace(',','.'),fpc,str(FW)[:4],'','','','','','','','','',values[2].replace(',','.')])
            except:
                break
            else:
                idx+=1
    if ids is not None:
        while ids>-1:
            try:
                values=str.split(data[ids+4])
                if values!='' and values!=[]:
                    float(values[1].replace(',','.')),float(values[2].replace(',','.')),float(values[3].replace(',','.')),float(values[4].replace(',','.')),float(values[5].replace(',','.')),float(values[6].replace(',','.')),float(values[7][:-1].replace(',','.'))
                    if float(values[4].replace(',','.'))>0 and float(values[6].replace(',','.'))>0 and float(values[6].replace(',','.'))<statslim:
                        fpc=str(float(values[4].replace(',','.'))*float(values[6].replace(',','.'))/100)
                        FW=(float(values[7][:-1].replace(',','.'))-Z)/G
                        peaklist.append(['','','','',values[1].replace(',','.'),'',values[2].replace(',','.'),'',values[4].replace(',','.'),fpc,str(FW)[:4],'','','','','','','','','',values[3].replace(',','.')])
                    else:
                        if set_forall==False:
                            fpc=str(float(values[4].replace(',','.'))*float(values[6].replace(',','.'))/100)
                            FW=(float(values[7][:-1].replace(',','.'))-Z)/G
                            peaklist.append(['','','','',values[1].replace(',','.'),'',values[2].replace(',','.'),'',0.1,fpc,str(FW)[:4],'','','','','','','','','',values[3].replace(',','.')])
            except:
                break
            else:
                ids+=1
    peaklist.sort(key=takeSecond)
    return startcounting,rltime,lvtime,peaklist
    
def acquisiscispettroASC(n):
    f=open(n,'r')
    rl=f.readlines()
    f.close()
    r=[]
    for i in rl:
        r.append(i.replace('\n',''))
    a=0
    while a>-1:
        try:
            if '#LiveTime=' in r[a]:
                live=float(r[a].replace('#LiveTime=',''))
                afine=a-1
            if '#TrueTime=' in r[a]:
                real=float(r[a].replace('#TrueTime=',''))
            if '#AcqStart=' in r[a]:
                data=r[a].replace('#AcqStart=','')
                data=data.replace('T',' ')
                data,ora=str.split(data)
                anno,mese,giorno=str.split(data,'-')
                ora=ora.replace(':',' ')
                ore,minuti,secondi=str.split(ora)
            if '#LinEnergyCalParams=' in r[a]:
                linE=str.split(r[a].replace('#LinEnergyCalParams=',''))
                for l in range(len(linE)):
                    linE[l]=float(linE[l])
            if '#FwhmCalParams=' in r[a]:
                linW=str.split(r[a].replace('#FwhmCalParams=',''))
                for l in range(len(linW)):
                    linW[l]=float(linW[l])
        except IndexError:
            break
        else:
            a=a+1
    workinglist=r[:afine]
    spectrum_counts = [float(iks) for iks in workinglist]
    startcounting=datetime.datetime(int(anno),int(mese),int(giorno),int(ore),int(minuti),int(secondi))
    return startcounting,real,live,spectrum_counts,linE,linW

def read_chnfile(n):
    import struct
    with open(n, "rb") as f:
        cs=4
        data = f.read(2)
        data = f.read(2)
        data = f.read(2)
        data = f.read(2)
        secs = str(data,'utf-8')
        data = f.read(4)
        datev=struct.unpack('<I',data)
        real=int(datev[0])*20/1000
        data = f.read(4)
        datev=struct.unpack('<I',data)
        live=int(datev[0])*20/1000
        data = f.read(8)
        ddmmmyy = str(data,'utf-8')
        ddmmmyy,y1 = ddmmmyy[:-1],ddmmmyy[-1:]
        if y1=='1':
            y2000=2000
        else:
            y2000=0
        day,month,year=ddmmmyy[:2],ddmmmyy[2:5],int(ddmmmyy[5:])+y2000
        monthasint={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
        month=monthasint.get(month)
        data = f.read(4)
        hhmm = str(data,'utf-8')
        data = f.read(2)
        data = f.read(2)
        startcounting=datetime.datetime(int(year),int(month),int(day),int(hhmm[:2]),int(hhmm[2:]),int(secs))
        dtt=[]
        while data:
            data = f.read(cs)
            try:
                datev=struct.unpack('<I',data)
                datev=int(datev[0])
                dtt.append(datev)
            except:
                break
    lenit=65536
    if len(dtt)<65536:
        lenit=32768
    if len(dtt)<32768:
        lenit=16384
    if len(dtt)<16384:
        lenit=8192
    if len(dtt)<8192:
        lenit=4096
    dtt,rest=dtt[:lenit],dtt[lenit:]
    spectrum_counts = [float(iks) for iks in dtt]
    linE,linW=[0.0,0.0],[0.0,0.0]
    return startcounting,real,live,spectrum_counts,linE,linW

def searchforhypelabfile(unclimit=40,set_forall=True):
    types=[('csv file','.csv'),('rpt file','.rpt')]
    nomeHyperLabfile=askopenfilename(filetypes=types)
    if nomeHyperLabfile!=None and nomeHyperLabfile!='':
        startcounting,realT,liveT,spectrum_counts,linE,linW,peak_list=None,None,None,None,None,None,None
        if nomeHyperLabfile[-4:].lower() == '.csv': #cambia questo
            try:
                peak_list=openhyperlabfile(nomeHyperLabfile,unclimit)
            except:
                peak_list=[]
        else:
            try:
                startcounting,realT,liveT,peak_list=read_rptfile2(nomeHyperLabfile,unclimit,set_forall)
            except:
                peak_list=[]
        try:
            peak_list[0][20]
        except IndexError:
            print(f'failed to import peak list: {nomeHyperLabfile}')
        else:
            nomeHyperLabfile=nomeHyperLabfile.replace(nomeHyperLabfile[-4:],'.ASC')
            if os.path.isfile(nomeHyperLabfile):
                try:
                    startcounting,realT,liveT,spectrum_counts,linE,linW=acquisiscispettroASC(nomeHyperLabfile)
                except:
                    spectrum_counts = np.array([0]*8192)
                    print(f'failed to import spectrum: {nomeHyperLabfile}')
            else:
                nomeHyperLabfile=nomeHyperLabfile.replace(nomeHyperLabfile[-4:],'.chn')
                try:
                    startcounting,realT,liveT,spectrum_counts,linE,linW=read_chnfile(nomeHyperLabfile)
                except:
                    spectrum_counts = np.array([0]*8192)
                    print(f'failed to import spectrum: {nomeHyperLabfile}')
    else:
        startcounting,realT,liveT,spectrum_counts,linE,linW,peak_list=None,None,None,None,None,None,None
    return nomeHyperLabfile,startcounting,realT,liveT,peak_list,spectrum_counts,linE,linW
    
def searchforhypelabmultiplefiles(unclimit=40,set_forall=True):
    types=[('csv file','.csv'),('rpt file','.rpt')]
    nomeHyperLabfiles=askopenfilenames(filetypes=types)
    AAA=[]
    if nomeHyperLabfiles!=None and nomeHyperLabfiles!='':
        for nomeHyperLabfile in nomeHyperLabfiles:
            startcounting,realT,liveT,spectrum_counts,linE,linW,peak_list=None,None,None,None,None,None,None
            if nomeHyperLabfile[-4:].lower()=='.csv':
                try:
                    peak_list=openhyperlabfile(nomeHyperLabfile,unclimit)
                except:
                    peak_list=[]
            else:
                try:
                    startcounting,realT,liveT,peak_list=read_rptfile2(nomeHyperLabfile,unclimit,set_forall)
                except:
                    peak_list=[]
            try:
                peak_list[0][20]
            except IndexError:
                print(f'failed to import peak list: {nomeHyperLabfile}')
            else:
                nomeHyperLabfile=nomeHyperLabfile.replace(nomeHyperLabfile[-4:],'.ASC')
                if os.path.isfile(nomeHyperLabfile):
                    try:
                        startcounting,realT,liveT,spectrum_counts,linE,linW=acquisiscispettroASC(nomeHyperLabfile)
                    except:
                        spectrum_counts = np.array([0]*8192)
                        print(f'failed to import spectrum: {nomeHyperLabfile}')
                else:
                    nomeHyperLabfile=nomeHyperLabfile.replace(nomeHyperLabfile[-4:],'.chn')
                    try:
                        startcounting,realT,liveT,spectrum_counts,linE,linW=read_chnfile(nomeHyperLabfile)
                    except:
                        spectrum_counts = np.array([0]*8192)
                        print(f'failed to import spectrum: {nomeHyperLabfile}')
                AAA.append([nomeHyperLabfile,startcounting,realT,liveT,peak_list,spectrum_counts,linE,linW])
    return AAA
    
def budget_Mtype_I(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    wbud.write(0,0,'Isotope')
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    wbud.write(0,2,'Emitter')
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,3,link,bold)
    wbud.write_rich_string(0,4,'E',subs,'p',' / keV')
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,5,link,bold)
    wbud.set_column('I:I', 14)
    wbud.set_column('L:L', 12)
    if MP is not None:   
        wbud.write(2,0,'Quantity')
        wbud.write(2,2,'Unit')
        wbud.write(2,3,'Value')
        if style=='Q':
            wbud.write(2,4,'Std unc')
            wbud.write(2,5,'Rel unc')
            wbud.write(2,8,'Sensitivity coef.')
            wbud.write(2,9,'Contribution to variance')
        wbud.write_rich_string(3,0,ital,'X',subs,'i')
        wbud.write_rich_string(3,2,'[',ital,'X',subs,'i',']')
        wbud.write_rich_string(3,3,ital,'x',subs,'i')
        if style=='Q':
            wbud.write_rich_string(3,4,ital,'u','(',ital,'x',subs,'i',')')
            wbud.write_rich_string(3,5,ital,'u',subs,'r','(',ital,'x',subs,'i',')')
            wbud.write_rich_string(3,6,ital,'y','(',ital,'x',subs,'i',' + ',ital,'u','(',ital,'x',subs,'i','))')
            wbud.write_rich_string(3,7,ital,'y','(',ital,'x',subs,'i',' - ',ital,'u','(',ital,'x',subs,'i','))')
            wbud.write_rich_string(3,8,ital,'c',subs,'i')
            wbud.write_rich_string(3,9,ital,'I',' / %')
            wbud.write(3,11,'Corr. Matrix')
            wbud.write(3,57,'Cov. Matrix')
        wbud.write_rich_string(4,0,ital,'t',subs,'i')
        wbud.write(4,2,'s')
        parm_id=['D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','D21','D22','D23','D24','D25','D26','D27','D28','D29','D30','D31','D32','D33','D34','D35','D36','D37','D38','D39','D40','D41','D42','D43','D44','D45','D46','D47']
        parm_id_plus=[]
        parm_id_minus=[]
        for iny in parm_id:
            piny='('+iny+'+'+iny.replace('D','E')+'+1E-9)'
            miny='('+iny+'-'+iny.replace('D','E')+'-1E-9)'
            parm_id_plus.append(piny)
            parm_id_minus.append(miny)
        for ti in range(len(MP)):
            wbud.write(4+ti,3,MP[ti,0])
            if style=='Q':
                wbud.write(4+ti,4,MP[ti,1])
                fml='=IF(D'+str(4+ti+1)+'<>0,ABS(E'+str(4+ti+1)+'/D'+str(4+ti+1)+'),"-")'
                wbud.write_formula(4+ti,5,fml,pct)
                parm_id[ti]=parm_id_plus[ti]
                fml=f'=({parm_id[1]}*{parm_id[2]}*{parm_id[4]}*EXP({parm_id[40]}*(1-{parm_id[5]}/{parm_id[4]}))*{parm_id[17]}*(1-EXP(-{parm_id[14]}*{parm_id[0]}))*EXP(({parm_id[2]}-{parm_id[14]})*{parm_id[15]}+{parm_id[2]}*{parm_id[3]})*(1-EXP(-{parm_id[14]}*{parm_id[16]}))*{parm_id[18]}*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*({parm_id[22]}+{parm_id[23]}/{parm_id[26]}*(({parm_id[24]}-0.429)/{parm_id[25]}^{parm_id[27]}+0.429/((2*{parm_id[27]}+1)*0.55^{parm_id[27]})))*EXP({parm_id[28]}*{parm_id[35]}+{parm_id[29]}+{parm_id[30]}*{parm_id[35]}^-1+{parm_id[31]}*{parm_id[35]}^-2+{parm_id[32]}*{parm_id[35]}^-3+{parm_id[33]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))/({parm_id[14]}*{parm_id[13]}*{parm_id[16]}*EXP({parm_id[40]}*(1-{parm_id[17]}/{parm_id[16]}))*{parm_id[5]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*(1-EXP(-{parm_id[2]}*{parm_id[4]}))*{parm_id[6]}*{parm_id[7]}*{parm_id[8]}*(1+{parm_id[41]}*{parm_id[42]})*({parm_id[9]}+{parm_id[10]}/{parm_id[26]}*(({parm_id[11]}-0.429)/{parm_id[12]}^{parm_id[27]}+0.429/((2*{parm_id[27]}+1)*0.55^{parm_id[27]})))*EXP({parm_id[28]}*{parm_id[34]}+{parm_id[29]}+{parm_id[30]}*{parm_id[34]}^-1+{parm_id[31]}*{parm_id[34]}^-2+{parm_id[32]}*{parm_id[34]}^-3+{parm_id[33]}*{parm_id[34]}^-4)*(1-{parm_id[36]}*{parm_id[38]}))'
                wbud.write(4+ti,6,fml,gray)
                parm_id[ti]=parm_id_minus[ti]
                fml=f'=({parm_id[1]}*{parm_id[2]}*{parm_id[4]}*EXP({parm_id[40]}*(1-{parm_id[5]}/{parm_id[4]}))*{parm_id[17]}*(1-EXP(-{parm_id[14]}*{parm_id[0]}))*EXP(({parm_id[2]}-{parm_id[14]})*{parm_id[15]}+{parm_id[2]}*{parm_id[3]})*(1-EXP(-{parm_id[14]}*{parm_id[16]}))*{parm_id[18]}*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*({parm_id[22]}+{parm_id[23]}/{parm_id[26]}*(({parm_id[24]}-0.429)/{parm_id[25]}^{parm_id[27]}+0.429/((2*{parm_id[27]}+1)*0.55^{parm_id[27]})))*EXP({parm_id[28]}*{parm_id[35]}+{parm_id[29]}+{parm_id[30]}*{parm_id[35]}^-1+{parm_id[31]}*{parm_id[35]}^-2+{parm_id[32]}*{parm_id[35]}^-3+{parm_id[33]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))/({parm_id[14]}*{parm_id[13]}*{parm_id[16]}*EXP({parm_id[40]}*(1-{parm_id[17]}/{parm_id[16]}))*{parm_id[5]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*(1-EXP(-{parm_id[2]}*{parm_id[4]}))*{parm_id[6]}*{parm_id[7]}*{parm_id[8]}*(1+{parm_id[41]}*{parm_id[42]})*({parm_id[9]}+{parm_id[10]}/{parm_id[26]}*(({parm_id[11]}-0.429)/{parm_id[12]}^{parm_id[27]}+0.429/((2*{parm_id[27]}+1)*0.55^{parm_id[27]})))*EXP({parm_id[28]}*{parm_id[34]}+{parm_id[29]}+{parm_id[30]}*{parm_id[34]}^-1+{parm_id[31]}*{parm_id[34]}^-2+{parm_id[32]}*{parm_id[34]}^-3+{parm_id[33]}*{parm_id[34]}^-4)*(1-{parm_id[36]}*{parm_id[38]}))'
                wbud.write(4+ti,7,fml,gray)
                fml='=(G'+str(4+ti+1)+'-H'+str(4+ti+1)+')/(2*E'+str(4+ti+1)+'+2E-9)'
                wbud.write(4+ti,8,fml)
                parm_id=['D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','D21','D22','D23','D24','D25','D26','D27','D28','D29','D30','D31','D32','D33','D34','D35','D36','D37','D38','D39','D40','D41','D42','D43','D44','D45','D46','D47']
        wbud.write_rich_string(5,0,ital,'n',subs,'p a')
        wbud.write(5,2,'1')
        wbud.write_rich_string(6,0,sym,'l',subs,'a')
        wbud.write_rich_string(6,2,'s',sups,'-1')
        wbud.write_rich_string(7,0,sym,'D',ital,'t',subs,'d')
        wbud.write(7,2,'s')
        wbud.write_rich_string(8,0,ital,'t',subs,'c a')
        wbud.write(8,2,'s')
        wbud.write_rich_string(9,0,ital,'t',subs,'l a')
        wbud.write(9,2,'s')
        wbud.write_rich_string(10,0,ital,'COI',subs,'a')
        wbud.write(10,2,'1')
        wbud.write_rich_string(11,0,ital,'m',subs,'sm')
        wbud.write(11,2,'g')
        wbud.write_rich_string(12,0,ital,'k',subs,'0 Au','(a)')
        wbud.write(12,2,'1')
        wbud.write_rich_string(13,0,ital,'G',subs,'th a')
        wbud.write(13,2,'1')
        wbud.write_rich_string(14,0,ital,'G',subs,'e a')
        wbud.write(14,2,'1')
        wbud.write_rich_string(15,0,ital,'Q',subs,'0 a')
        wbud.write(15,2,'1')
        wbud.write_rich_string(16,0,ital,'E',subs,'r a')
        wbud.write(16,2,'eV')
        wbud.write_rich_string(17,0,ital,'n',subs,'p m')
        wbud.write(17,2,'1')
        wbud.write_rich_string(18,0,sym,'l',subs,'m')
        wbud.write_rich_string(18,2,'s',sups,'-1')
        wbud.write_rich_string(19,0,ital,'t',subs,'d m')
        wbud.write(19,2,'s')
        wbud.write_rich_string(20,0,ital,'t',subs,'c m')
        wbud.write(20,2,'s')
        wbud.write_rich_string(21,0,ital,'t',subs,'l m')
        wbud.write(21,2,'s')
        wbud.write_rich_string(22,0,ital,'COI',subs,'m')
        wbud.write(22,2,'1')
        wbud.write_rich_string(23,0,ital,'m',subs,'std')
        wbud.write(23,2,'g')
        wbud.write_rich_string(24,0,ital,'w',subs,'m')
        wbud.write_rich_string(24,2,'g g',sups,'-1')
        wbud.write_rich_string(25,0,ital,'k',subs,'0 Au','(m)')
        wbud.write(25,2,'1')
        wbud.write_rich_string(26,0,ital,'G',subs,'th m')
        wbud.write(26,2,'1')
        wbud.write_rich_string(27,0,ital,'G',subs,'e m')
        wbud.write(27,2,'1')
        wbud.write_rich_string(28,0,ital,'Q',subs,'0 m')
        wbud.write(28,2,'1')
        wbud.write_rich_string(29,0,ital,'E',subs,'r m')
        wbud.write(29,2,'eV')
        wbud.write(30,0,'f',ital)
        wbud.write(30,2,'1')
        wbud.write(31,0,'a',sym)
        wbud.write(31,2,'1')
        wbud.write_rich_string(32,0,grayit,'a',graysub,'1')
        wbud.write_rich_string(32,2,'MeV',sups,'-1')
        wbud.write_rich_string(33,0,grayit,'a',graysub,'2')
        wbud.write(33,2,'1')
        wbud.write_rich_string(34,0,grayit,'a',graysub,'3')
        wbud.write_rich_string(34,2,'MeV',sups,'1')
        wbud.write_rich_string(35,0,grayit,'a',graysub,'4')
        wbud.write_rich_string(35,2,'MeV',sups,'2')
        wbud.write_rich_string(36,0,grayit,'a',graysub,'5')
        wbud.write_rich_string(36,2,'MeV',sups,'3')
        wbud.write_rich_string(37,0,grayit,'a',graysub,'6')
        wbud.write_rich_string(37,2,'MeV',sups,'4')
        wbud.write_rich_string(38,0,grayit,'E',graysub,'p a')
        wbud.write(38,2,'MeV')
        wbud.write_rich_string(39,0,grayit,'E',graysub,'p m')
        wbud.write(39,2,'MeV')
        wbud.write_rich_string(40,0,sym,'de',subs,'a')
        wbud.write_rich_string(40,2,'mm',sups,'-1')
        wbud.write_rich_string(41,0,sym,'de',subs,'m')
        wbud.write_rich_string(41,2,'mm',sups,'-1')
        wbud.write_rich_string(42,0,sym,'D',ital,'d',subs,'a')
        wbud.write(42,2,'mm')
        wbud.write_rich_string(43,0,sym,'D',ital,'d',subs,'m')
        wbud.write(43,2,'mm')
        wbud.write(44,0,'m',sym)
        wbud.write(44,2,'1')
        wbud.write(45,0,'b',sym)
        wbud.write_rich_string(45,2,'mm',sups,'-1')
        wbud.write_rich_string(46,0,sym,'D',ital,'x',subs,'a')
        wbud.write(46,2,'mm')
        if style=='Q':
            wbud.write_rich_string(4,11,ital,'t',subs,'i')
            wbud.write_rich_string(5,11,ital,'n',subs,'p a')
            wbud.write_rich_string(6,11,sym,'l',subs,'a')
            wbud.write_rich_string(7,11,sym,'D',ital,'t',subs,'d')
            wbud.write_rich_string(8,11,ital,'t',subs,'c a')
            wbud.write_rich_string(9,11,ital,'t',subs,'l a')
            wbud.write_rich_string(10,11,ital,'COI',subs,'a')
            wbud.write_rich_string(11,11,ital,'m',subs,'sm')
            wbud.write_rich_string(12,11,ital,'k',subs,'0 Au','(a)')
            wbud.write_rich_string(13,11,ital,'G',subs,'th a')
            wbud.write_rich_string(14,11,ital,'G',subs,'e a')
            wbud.write_rich_string(15,11,ital,'Q',subs,'0 a')
            wbud.write_rich_string(16,11,ital,'E',subs,'r a')
            wbud.write_rich_string(17,11,ital,'n',subs,'p m')
            wbud.write_rich_string(18,11,sym,'l',subs,'m')
            wbud.write_rich_string(19,11,ital,'t',subs,'d m')
            wbud.write_rich_string(20,11,ital,'t',subs,'c m')
            wbud.write_rich_string(21,11,ital,'t',subs,'l m')
            wbud.write_rich_string(22,11,ital,'COI',subs,'m')
            wbud.write_rich_string(23,11,ital,'m',subs,'std')
            wbud.write_rich_string(24,11,ital,'w',subs,'m')
            wbud.write_rich_string(25,11,ital,'k',subs,'0 Au','(m)')
            wbud.write_rich_string(26,11,ital,'G',subs,'th m')
            wbud.write_rich_string(27,11,ital,'G',subs,'e m')
            wbud.write_rich_string(28,11,ital,'Q',subs,'0 m')
            wbud.write_rich_string(29,11,ital,'E',subs,'r m')
            wbud.write(30,11,'f',ital)
            wbud.write(31,11,'a',sym)
            wbud.write_rich_string(32,11,ital,'a',subs,'1')
            wbud.write_rich_string(33,11,ital,'a',subs,'2')
            wbud.write_rich_string(34,11,ital,'a',subs,'3')
            wbud.write_rich_string(35,11,ital,'a',subs,'4')
            wbud.write_rich_string(36,11,ital,'a',subs,'5')
            wbud.write_rich_string(37,11,ital,'a',subs,'6')
            wbud.write_rich_string(38,11,ital,'E',subs,'p a')
            wbud.write_rich_string(39,11,ital,'E',subs,'p m')
            wbud.write_rich_string(40,11,sym,'de',subs,'a')
            wbud.write_rich_string(41,11,sym,'de',subs,'m')
            wbud.write_rich_string(42,11,sym,'D',ital,'d',subs,'a')
            wbud.write_rich_string(43,11,sym,'D',ital,'d',subs,'m')
            wbud.write(44,11,'m',sym)
            wbud.write(45,11,'b',sym)
            wbud.write_rich_string(46,11,sym,'D',ital,'x',subs,'a')
            wbud.write_rich_string(3,12,ital,'t',subs,'i')
            wbud.write_rich_string(3,13,ital,'n',subs,'p a')
            wbud.write_rich_string(3,14,sym,'l',subs,'a')
            wbud.write_rich_string(3,15,sym,'D',ital,'t',subs,'d')
            wbud.write_rich_string(3,16,ital,'t',subs,'c a')
            wbud.write_rich_string(3,17,ital,'t',subs,'l a')
            wbud.write_rich_string(3,18,ital,'COI',subs,'a')
            wbud.write_rich_string(3,19,ital,'m',subs,'sm')
            wbud.write_rich_string(3,20,ital,'k',subs,'0 Au','(a)')
            wbud.write_rich_string(3,21,ital,'G',subs,'th a')
            wbud.write_rich_string(3,22,ital,'G',subs,'e a')
            wbud.write_rich_string(3,23,ital,'Q',subs,'0 a')
            wbud.write_rich_string(3,24,ital,'E',subs,'r a')
            wbud.write_rich_string(3,25,ital,'n',subs,'p m')
            wbud.write_rich_string(3,26,sym,'l',subs,'m')
            wbud.write_rich_string(3,27,ital,'t',subs,'d m')
            wbud.write_rich_string(3,28,ital,'t',subs,'c m')
            wbud.write_rich_string(3,29,ital,'t',subs,'l m')
            wbud.write_rich_string(3,30,ital,'COI',subs,'m')
            wbud.write_rich_string(3,31,ital,'m',subs,'std')
            wbud.write_rich_string(3,32,ital,'w',subs,'m')
            wbud.write_rich_string(3,33,ital,'k',subs,'0 Au','(m)')
            wbud.write_rich_string(3,34,ital,'G',subs,'th m')
            wbud.write_rich_string(3,35,ital,'G',subs,'e m')
            wbud.write_rich_string(3,36,ital,'Q',subs,'0 m')
            wbud.write_rich_string(3,37,ital,'E',subs,'r m')
            wbud.write(3,38,'f',ital)
            wbud.write(3,39,'a',sym)
            wbud.write_rich_string(3,40,ital,'a',subs,'1')
            wbud.write_rich_string(3,41,ital,'a',subs,'2')
            wbud.write_rich_string(3,42,ital,'a',subs,'3')
            wbud.write_rich_string(3,43,ital,'a',subs,'4')
            wbud.write_rich_string(3,44,ital,'a',subs,'5')
            wbud.write_rich_string(3,45,ital,'a',subs,'6')
            wbud.write_rich_string(3,46,ital,'E',subs,'p a')
            wbud.write_rich_string(3,47,ital,'E',subs,'p m')
            wbud.write_rich_string(3,48,sym,'de',subs,'a')
            wbud.write_rich_string(3,49,sym,'de',subs,'m')
            wbud.write_rich_string(3,50,sym,'D',ital,'d',subs,'a')
            wbud.write_rich_string(3,51,sym,'D',ital,'d',subs,'m')
            wbud.write(3,52,'m',sym)
            wbud.write(3,53,'b',sym)
            wbud.write_rich_string(3,54,sym,'D',ital,'x',subs,'a')
        wbud.write(48,0,'Quantity')
        wbud.write(48,2,'Unit')
        wbud.write(48,3,'Value')
        if style=='Q':
            wbud.write(48,4,'Std unc')
            wbud.write(48,5,'Rel unc')
            wbud.write(48,9,'Contribution to variance')
        wbud.write(49,0,'Y',ital)
        wbud.write_rich_string(49,2,'[',ital,'y',']')
        wbud.write(49,3,'y',ital)
        if style=='Q':
            wbud.write_rich_string(49,4,ital,'u','(',ital,'y',')')
            wbud.write_rich_string(49,5,ital,'u',subs,'r','(',ital,'y',')')
            wbud.write_rich_string(49,9,ital,'I',' / %')
        wbud.write_rich_string(50,0,ital,'w',subs,'a')
        wbud.write_rich_string(50,2,'g g',sups,'-1')
        if style=='Q':
            for ri in range(len(MC)):
                sm='#'
                for ci in range(len(MC)):
                    wbud.write(4+ri,12+ci,MC[ri,ci])
                    cell_corr = xl_rowcol_to_cell(4+ri,12+ci)
                    fml='='+str(cell_corr)+'*E'+str(4+ri+1)+'*E'+str(4+ci+1)
                    wbud.write(4+ri,57+ci,fml,gray)
                    sms=str(cell_corr)+'*E'+str(4+ri+1)+'*E'+str(4+ci+1)+'*I'+str(4+ri+1)+'*I'+str(4+ci+1)
                    sm=sm+'+'+sms
                sm=sm.replace('#+','=(')
                sm=sm+')/E51^2'
                if ri in [28,29,30,31,32,33,34,35]:
                    wbud.write(4+ri,9,sm,graypct)
                else:
                    wbud.write(4+ri,9,sm,pct)
        #fml=f'=({parm_id[1]}*{parm_id[2]}*{parm_id[4]}*EXP({parm_id[40]}*(1-{parm_id[5]}/{parm_id[4]}))*{parm_id[17]}*(1-EXP(-{parm_id[14]}*{parm_id[0]}))*EXP(({parm_id[2]}-{parm_id[14]})*{parm_id[15]}+{parm_id[2]}*{parm_id[3]})*(1-EXP(-{parm_id[14]}*{parm_id[16]}))*{parm_id[18]}*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*({parm_id[22]}+{parm_id[23]}/{parm_id[26]}*(({parm_id[24]}-0.429)/{parm_id[25]}^{parm_id[27]}+0.429/((2*{parm_id[27]}+1)*0.55^{parm_id[27]})))*EXP({parm_id[28]}*{parm_id[35]}+{parm_id[29]}+{parm_id[30]}*{parm_id[35]}^-1+{parm_id[31]}*{parm_id[35]}^-2+{parm_id[32]}*{parm_id[35]}^-3+{parm_id[33]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))/({parm_id[14]}*{parm_id[13]}*{parm_id[16]}*EXP({parm_id[40]}*(1-{parm_id[17]}/{parm_id[16]}))*{parm_id[5]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*(1-EXP(-{parm_id[2]}*{parm_id[4]}))*{parm_id[6]}*{parm_id[7]}*{parm_id[8]}*({parm_id[9]}+{parm_id[10]}/{parm_id[26]}*(({parm_id[11]}-0.429)/{parm_id[12]}^{parm_id[27]}+0.429/((2*{parm_id[27]}+1)*0.55^{parm_id[27]})))*EXP({parm_id[28]}*{parm_id[34]}+{parm_id[29]}+{parm_id[30]}*{parm_id[34]}^-1+{parm_id[31]}*{parm_id[34]}^-2+{parm_id[32]}*{parm_id[34]}^-3+{parm_id[33]}*{parm_id[34]}^-4)*(1-{parm_id[36]}*{parm_id[38]}))'
        fml=f'=({parm_id[1]}*{parm_id[2]}*{parm_id[4]}*EXP({parm_id[40]}*(1-{parm_id[5]}/{parm_id[4]}))*{parm_id[17]}*(1-EXP(-{parm_id[14]}*{parm_id[0]}))*EXP(({parm_id[2]}-{parm_id[14]})*{parm_id[15]}+{parm_id[2]}*{parm_id[3]})*(1-EXP(-{parm_id[14]}*{parm_id[16]}))*{parm_id[18]}*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*({parm_id[22]}+{parm_id[23]}/{parm_id[26]}*(({parm_id[24]}-0.429)/{parm_id[25]}^{parm_id[27]}+0.429/((2*{parm_id[27]}+1)*0.55^{parm_id[27]})))*EXP({parm_id[28]}*{parm_id[35]}+{parm_id[29]}+{parm_id[30]}*{parm_id[35]}^-1+{parm_id[31]}*{parm_id[35]}^-2+{parm_id[32]}*{parm_id[35]}^-3+{parm_id[33]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))/({parm_id[14]}*{parm_id[13]}*{parm_id[16]}*EXP({parm_id[40]}*(1-{parm_id[17]}/{parm_id[16]}))*{parm_id[5]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*(1-EXP(-{parm_id[2]}*{parm_id[4]}))*{parm_id[6]}*{parm_id[7]}*{parm_id[8]}*(1+{parm_id[41]}*{parm_id[42]})*({parm_id[9]}+{parm_id[10]}/{parm_id[26]}*(({parm_id[11]}-0.429)/{parm_id[12]}^{parm_id[27]}+0.429/((2*{parm_id[27]}+1)*0.55^{parm_id[27]})))*EXP({parm_id[28]}*{parm_id[34]}+{parm_id[29]}+{parm_id[30]}*{parm_id[34]}^-1+{parm_id[31]}*{parm_id[34]}^-2+{parm_id[32]}*{parm_id[34]}^-3+{parm_id[33]}*{parm_id[34]}^-4)*(1-{parm_id[36]}*{parm_id[38]}))'
        #fml='=(D6*D7*D9*EXP(D46*(1-D10/D9))*D22*D23*(1-EXP(-D19*D5))*EXP(-D19*D20)*(1-EXP(-D19*D21))*D24*D25*(D26+D27/D30*((D28-0.429)/D29^D31+0.429/((2*D31+1)*0.55^D31)))*EXP(D39*D45+D40+D41*D45^-1+D42*D45^-2+D43*D45^-3+D44*D45^-4)*(1-D50*D51))/(D18*D19*D21*EXP(D47*(1-D22/D21))*D10*D11*(1-EXP(-D7*D5))*EXP(-D7*D8)*(1-EXP(-D7*D9))*D12*D13*(D14+D15/D30*((D16-0.429)/D17^D31+0.429/((2*D31+1)*0.55^D31)))*EXP(D32*D38+D33+D34*D38^-1+D35*D38^-2+D36*D38^-3+D37*D38^-4)*(1-D48*D49))'
        wbud.write(50,3,fml)
        if style=='Q':
            fml='{=sqrt(MMULT(MMULT(TRANSPOSE(I5:I47),BF5:CV47),I5:I47))}'
            wbud.write_formula(50,4,fml)
            fml='=ABS(E51/D51)'
            wbud.write(50,5,fml,pct)
            fml='=SUM(J5:J47)'
            wbud.write(50,9,fml,pct)
        wbud.write(53,0,'Additional information')
        wbud.write(54,0,'Quantity')
        wbud.write(54,2,'Unit')
        wbud.write(54,3,'Value')
        wbud.write_rich_string(55,0,ital,'X',subs,'i')
        wbud.write_rich_string(55,2,'[',ital,'X',subs,'i',']')
        wbud.write_rich_string(55,3,ital,'x',subs,'i')
        if style=='Q':
            wbud.write(54,4,'Std unc')
            wbud.write(54,5,'Rel unc')
            wbud.write(54,9,'Contribution to variance')            
            wbud.write_rich_string(55,4,ital,'u','(',ital,'x',subs,'i',')')
            wbud.write_rich_string(55,5,ital,'u',subs,'r','(',ital,'x',subs,'i',')')
            wbud.write_rich_string(55,9,ital,'I',' / %')
        wbud.write_rich_string(56,0,sym,'e','(',ital,'a',subs,'i',', ',ital,'E',subs,'p a',', ',ital,'E',subs,'p m',')')
        wbud.write_rich_string(57,0,ital,'Q',subs,'0,a','(',sym,'a',')')
        wbud.write_rich_string(58,0,ital,'Q',subs,'0,m','(',sym,'a',')')
        wbud.write(56,2,'1')
        wbud.write(57,2,'1')
        wbud.write(58,2,'1')
        
        fml='=(EXP(D33*D40+D34+D35*D40^-1+D36*D40^-2+D37*D40^-3+D38*D40^-4))/(EXP(D33*D39+D34+D35*D39^-1+D36*D39^-2+D37*D39^-3+D38*D39^-4))'
        wbud.write(56,3,fml)
        if style=='Q':
            fml='=SQRT(J57*E51^2)/((D6*D7*D9*EXP(D45*(1-D10/D9))*D22*(1-EXP(-D19*D5))*EXP((D7-D19)*D20+D7*D8)*(1-EXP(-D19*D21))*D23*D24*D25*D26*(D27+D28/D31*((D29-0.429)/D30^D32+0.429/((2*D32+1)*0.55^D32)))*(1-D42*D44))/(D19*D18*D21*EXP(D45*(1-D22/D21))*D10*(1-EXP(-D7*D5))*(1-EXP(-D7*D9))*D11*D12*D13*(1+D46*D47)*(D14+D15/D31*((D16-0.429)/D17^D32+0.429/((2*D32+1)*0.55^D32)))*(1-D41*D43)))'
            wbud.write(56,4,fml)
            fml='=E57/D57'
            wbud.write(56,5,fml,pct)
            fml='=SUM(J33:J40)'
            wbud.write(56,9,fml,pct)
        
        fml='=(D16-0.429)/D17^D32+0.429/((2*D32+1)*0.55^D32)'
        wbud.write(57,3,fml)
        if style=='Q':
            wbud.write(57,4,'-')
            wbud.write(57,5,'-')
        
        fml='=(D29-0.429)/D30^D32+0.429/((2*D32+1)*0.55^D32)'
        wbud.write(58,3,fml)
        if style=='Q':
            wbud.write(58,4,'-')
            wbud.write(58,5,'-')
            wbud.set_column('G:H', None, None, {'hidden': True})
        wbud.write(61,0,'Measurement model')
        wbud.insert_image(62,0,'data/models/TypeI.jpg',{'x_scale': 1.5, 'y_scale': 1.5})
    else:
        wbud.write(2,0,'Missing spectrum data')
        wbud.write(50,3,'-')
    
def budget_Mtype_IIA(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    wbud.write(0,0,'Isotope')
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    wbud.write(0,2,'Emitter')
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,3,link,bold)
    wbud.write_rich_string(0,4,'E',subs,'p',' / keV')
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,5,link,bold)
    wbud.set_column('I:I', 14)
    wbud.set_column('L:L', 12)
    if MP is not None:
        wbud.write(2,0,'Quantity')
        wbud.write(2,2,'Unit')
        wbud.write(2,3,'Value')
        if style=='Q':
            wbud.write(2,4,'Std unc')
            wbud.write(2,5,'Rel unc')
            wbud.write(2,8,'Sensitivity coef.')
            wbud.write(2,9,'Contribution to variance')
        wbud.write_rich_string(3,0,ital,'X',subs,'i')
        wbud.write_rich_string(3,2,'[',ital,'X',subs,'i',']')
        wbud.write_rich_string(3,3,ital,'x',subs,'i')
        if style=='Q':
            wbud.write_rich_string(3,4,ital,'u','(',ital,'x',subs,'i',')')
            wbud.write_rich_string(3,5,ital,'u',subs,'r','(',ital,'x',subs,'i',')')
            wbud.write_rich_string(3,6,ital,'y','(',ital,'x',subs,'i',' + ',ital,'u','(',ital,'x',subs,'i','))')
            wbud.write_rich_string(3,7,ital,'y','(',ital,'x',subs,'i',' - ',ital,'u','(',ital,'x',subs,'i','))')
            wbud.write_rich_string(3,8,ital,'c',subs,'i')
            wbud.write_rich_string(3,9,ital,'I',' / %')
            wbud.write(3,11,'Corr. Matrix')
            wbud.write(3,57,'Cov. Matrix')
        wbud.write_rich_string(4,0,ital,'t',subs,'i')
        wbud.write(4,2,'s')
        parm_id=['D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','D21','D22','D23','D24','D25','D26','D27','D28','D29','D30','D31','D32','D33','D34','D35','D36','D37','D38','D39','D40','D41','D42','D43','D44','D45','D46','D47','D48']
        parm_id_plus=[]
        parm_id_minus=[]
        for iny in parm_id:
            piny='('+iny+'+'+iny.replace('D','E')+'+1E-9)'
            miny='('+iny+'-'+iny.replace('D','E')+'-1E-9)'
            parm_id_plus.append(piny)
            parm_id_minus.append(miny)
        for ti in range(len(MP)):
            wbud.write(4+ti,3,MP[ti,0])
            if style=='Q':
                wbud.write(4+ti,4,MP[ti,1])
                if style=='Q':
                    wbud.write(4+ti,4,MP[ti,1])
                    fml='=IF(D'+str(4+ti+1)+'<>0,ABS(E'+str(4+ti+1)+'/D'+str(4+ti+1)+'),"-")'
                    wbud.write_formula(4+ti,5,fml,pct)
                    parm_id[ti]=parm_id_plus[ti]
                    fml=f'=({parm_id[1]}*({parm_id[3]}-{parm_id[2]})*{parm_id[5]}*EXP({parm_id[41]}*(1-{parm_id[6]}/{parm_id[5]}))*{parm_id[18]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[15]})*{parm_id[16]}+{parm_id[3]}*{parm_id[4]})*(1-EXP(-{parm_id[15]}*{parm_id[17]}))*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*{parm_id[22]}*({parm_id[23]}+{parm_id[24]}/{parm_id[27]}*(({parm_id[25]}-0.429)/{parm_id[26]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[36]}+{parm_id[30]}+{parm_id[31]}*{parm_id[36]}^-1+{parm_id[32]}*{parm_id[36]}^-2+{parm_id[33]}*{parm_id[36]}^-3+{parm_id[34]}*{parm_id[36]}^-4)*(1-{parm_id[38]}*{parm_id[40]}))/({parm_id[15]}*{parm_id[14]}*{parm_id[17]}*EXP({parm_id[41]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[6]}*({parm_id[3]}/{parm_id[2]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[2]})*({parm_id[16]}+{parm_id[4]}))*(1-EXP(-{parm_id[2]}*{parm_id[5]}))-{parm_id[2]}/{parm_id[3]}*(1-EXP(-{parm_id[3]}*{parm_id[0]}))*(1-EXP(-{parm_id[3]}*{parm_id[5]})))*{parm_id[7]}*{parm_id[8]}*{parm_id[9]}*(1+{parm_id[42]}*{parm_id[43]})*({parm_id[10]}+{parm_id[11]}/{parm_id[27]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[35]}+{parm_id[30]}+{parm_id[31]}*{parm_id[35]}^-1+{parm_id[32]}*{parm_id[35]}^-2+{parm_id[33]}*{parm_id[35]}^-3+{parm_id[34]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))'
                    #fml=f'=({parm_id[1]}*({parm_id[3]}-{parm_id[2]})*{parm_id[5]}*EXP({parm_id[41]}*(1-{parm_id[6]}/{parm_id[5]}))*{parm_id[18]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[15]})*{parm_id[16]}+{parm_id[3]}*{parm_id[4]})*(1-EXP(-{parm_id[15]}*{parm_id[17]}))*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*{parm_id[22]}*({parm_id[23]}+{parm_id[24]}/{parm_id[27]}*(({parm_id[25]}-0.429)/{parm_id[26]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[36]}+{parm_id[30]}+{parm_id[31]}*{parm_id[36]}^-1+{parm_id[32]}*{parm_id[36]}^-2+{parm_id[33]}*{parm_id[36]}^-3+{parm_id[34]}*{parm_id[36]}^-4)*(1-{parm_id[38]}*{parm_id[40]}))/({parm_id[15]}*{parm_id[14]}*{parm_id[17]}*EXP({parm_id[41]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[6]}*({parm_id[3]}/{parm_id[2]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[2]})*({parm_id[16]}+{parm_id[4]}))*(1-EXP(-{parm_id[2]}*{parm_id[5]}))-{parm_id[2]}/{parm_id[3]}*(1-EXP(-{parm_id[3]}*{parm_id[0]}))*(1-EXP(-{parm_id[3]}*{parm_id[5]})))*{parm_id[7]}*{parm_id[8]}*{parm_id[9]}*({parm_id[10]}+{parm_id[11]}/{parm_id[27]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[35]}+{parm_id[30]}+{parm_id[31]}*{parm_id[35]}^-1+{parm_id[32]}*{parm_id[35]}^-2+{parm_id[33]}*{parm_id[35]}^-3+{parm_id[34]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))'
                    wbud.write(4+ti,6,fml,gray)
                    parm_id[ti]=parm_id_minus[ti]
                    fml=f'=({parm_id[1]}*({parm_id[3]}-{parm_id[2]})*{parm_id[5]}*EXP({parm_id[41]}*(1-{parm_id[6]}/{parm_id[5]}))*{parm_id[18]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[15]})*{parm_id[16]}+{parm_id[3]}*{parm_id[4]})*(1-EXP(-{parm_id[15]}*{parm_id[17]}))*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*{parm_id[22]}*({parm_id[23]}+{parm_id[24]}/{parm_id[27]}*(({parm_id[25]}-0.429)/{parm_id[26]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[36]}+{parm_id[30]}+{parm_id[31]}*{parm_id[36]}^-1+{parm_id[32]}*{parm_id[36]}^-2+{parm_id[33]}*{parm_id[36]}^-3+{parm_id[34]}*{parm_id[36]}^-4)*(1-{parm_id[38]}*{parm_id[40]}))/({parm_id[15]}*{parm_id[14]}*{parm_id[17]}*EXP({parm_id[41]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[6]}*({parm_id[3]}/{parm_id[2]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[2]})*({parm_id[16]}+{parm_id[4]}))*(1-EXP(-{parm_id[2]}*{parm_id[5]}))-{parm_id[2]}/{parm_id[3]}*(1-EXP(-{parm_id[3]}*{parm_id[0]}))*(1-EXP(-{parm_id[3]}*{parm_id[5]})))*{parm_id[7]}*{parm_id[8]}*{parm_id[9]}*(1+{parm_id[42]}*{parm_id[43]})*({parm_id[10]}+{parm_id[11]}/{parm_id[27]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[35]}+{parm_id[30]}+{parm_id[31]}*{parm_id[35]}^-1+{parm_id[32]}*{parm_id[35]}^-2+{parm_id[33]}*{parm_id[35]}^-3+{parm_id[34]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))'
                    #fml=f'=({parm_id[1]}*({parm_id[3]}-{parm_id[2]})*{parm_id[5]}*EXP({parm_id[41]}*(1-{parm_id[6]}/{parm_id[5]}))*{parm_id[18]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[15]})*{parm_id[16]}+{parm_id[3]}*{parm_id[4]})*(1-EXP(-{parm_id[15]}*{parm_id[17]}))*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*{parm_id[22]}*({parm_id[23]}+{parm_id[24]}/{parm_id[27]}*(({parm_id[25]}-0.429)/{parm_id[26]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[36]}+{parm_id[30]}+{parm_id[31]}*{parm_id[36]}^-1+{parm_id[32]}*{parm_id[36]}^-2+{parm_id[33]}*{parm_id[36]}^-3+{parm_id[34]}*{parm_id[36]}^-4)*(1-{parm_id[38]}*{parm_id[40]}))/({parm_id[15]}*{parm_id[14]}*{parm_id[17]}*EXP({parm_id[41]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[6]}*({parm_id[3]}/{parm_id[2]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[2]})*({parm_id[16]}+{parm_id[4]}))*(1-EXP(-{parm_id[2]}*{parm_id[5]}))-{parm_id[2]}/{parm_id[3]}*(1-EXP(-{parm_id[3]}*{parm_id[0]}))*(1-EXP(-{parm_id[3]}*{parm_id[5]})))*{parm_id[7]}*{parm_id[8]}*{parm_id[9]}*({parm_id[10]}+{parm_id[11]}/{parm_id[27]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[35]}+{parm_id[30]}+{parm_id[31]}*{parm_id[35]}^-1+{parm_id[32]}*{parm_id[35]}^-2+{parm_id[33]}*{parm_id[35]}^-3+{parm_id[34]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))'
                    wbud.write(4+ti,7,fml,gray)
                    fml='=(G'+str(4+ti+1)+'-H'+str(4+ti+1)+')/(2*E'+str(4+ti+1)+'+2E-9)'
                    wbud.write(4+ti,8,fml)
                    parm_id=['D5','D6','D7','D8','D9','D10','D11','D12','D13','D14','D15','D16','D17','D18','D19','D20','D21','D22','D23','D24','D25','D26','D27','D28','D29','D30','D31','D32','D33','D34','D35','D36','D37','D38','D39','D40','D41','D42','D43','D44','D45','D46','D47','D48']
        wbud.write_rich_string(5,0,ital,'n',subs,'p a')
        wbud.write(5,2,'1')
        wbud.write_rich_string(6,0,sym,'l',subs,'a')
        wbud.write_rich_string(6,2,'s',sups,'-1')
        wbud.write_rich_string(7,0,sym,'l',subs,'2 a')
        wbud.write_rich_string(7,2,'s',sups,'-1')       
        wbud.write_rich_string(8,0,sym,'D',ital,'t',subs,'d')
        wbud.write(8,2,'s')
        wbud.write_rich_string(9,0,ital,'t',subs,'c a')
        wbud.write(9,2,'s')
        wbud.write_rich_string(10,0,ital,'t',subs,'l a')
        wbud.write(10,2,'s')
        wbud.write_rich_string(11,0,ital,'COI',subs,'a')
        wbud.write(11,2,'1')
        wbud.write_rich_string(12,0,ital,'m',subs,'sm')
        wbud.write(12,2,'g')
        wbud.write_rich_string(13,0,ital,'k',subs,'0 Au','(a)')
        wbud.write(13,2,'1')
        wbud.write_rich_string(14,0,ital,'G',subs,'th a')
        wbud.write(14,2,'1')
        wbud.write_rich_string(15,0,ital,'G',subs,'e a')
        wbud.write(15,2,'1')
        wbud.write_rich_string(16,0,ital,'Q',subs,'0 a')
        wbud.write(16,2,'1')
        wbud.write_rich_string(17,0,ital,'E',subs,'r a')
        wbud.write(17,2,'eV')
        wbud.write_rich_string(18,0,ital,'n',subs,'p m')
        wbud.write(18,2,'1')
        wbud.write_rich_string(19,0,sym,'l',subs,'m')
        wbud.write_rich_string(19,2,'s',sups,'-1')
        wbud.write_rich_string(20,0,ital,'t',subs,'d m')
        wbud.write(20,2,'s')
        wbud.write_rich_string(21,0,ital,'t',subs,'c m')
        wbud.write(21,2,'s')
        wbud.write_rich_string(22,0,ital,'t',subs,'l m')
        wbud.write(22,2,'s')
        wbud.write_rich_string(23,0,ital,'COI',subs,'m')
        wbud.write(23,2,'1')
        wbud.write_rich_string(24,0,ital,'m',subs,'std')
        wbud.write(24,2,'g')
        wbud.write_rich_string(25,0,ital,'w',subs,'m')
        wbud.write_rich_string(25,2,'g g',sups,'-1')
        wbud.write_rich_string(26,0,ital,'k',subs,'0 Au','(m)')
        wbud.write(26,2,'1')
        wbud.write_rich_string(27,0,ital,'G',subs,'th m')
        wbud.write(27,2,'1')
        wbud.write_rich_string(28,0,ital,'G',subs,'e m')
        wbud.write(28,2,'1')
        wbud.write_rich_string(29,0,ital,'Q',subs,'0 m')
        wbud.write(29,2,'1')
        wbud.write_rich_string(30,0,ital,'E',subs,'r m')
        wbud.write(30,2,'eV')
        wbud.write(31,0,'f',ital)
        wbud.write(31,2,'1')
        wbud.write(32,0,'a',sym)
        wbud.write(32,2,'1')
        wbud.write_rich_string(33,0,grayit,'a',graysub,'1')
        wbud.write_rich_string(33,2,'MeV',sups,'-1')
        wbud.write_rich_string(34,0,grayit,'a',graysub,'2')
        wbud.write(34,2,'1')
        wbud.write_rich_string(35,0,grayit,'a',graysub,'3')
        wbud.write_rich_string(35,2,'MeV',sups,'1')
        wbud.write_rich_string(36,0,grayit,'a',graysub,'4')
        wbud.write_rich_string(36,2,'MeV',sups,'2')
        wbud.write_rich_string(37,0,grayit,'a',graysub,'5')
        wbud.write_rich_string(37,2,'MeV',sups,'3')
        wbud.write_rich_string(38,0,grayit,'a',graysub,'6')
        wbud.write_rich_string(38,2,'MeV',sups,'4')
        wbud.write_rich_string(39,0,grayit,'E',graysub,'p a')
        wbud.write(39,2,'MeV')
        wbud.write_rich_string(40,0,grayit,'E',graysub,'p m')
        wbud.write(40,2,'MeV')
        wbud.write_rich_string(41,0,sym,'de',subs,'a')
        wbud.write_rich_string(41,2,'mm',sups,'-1')
        wbud.write_rich_string(42,0,sym,'de',subs,'m')
        wbud.write_rich_string(42,2,'mm',sups,'-1')
        wbud.write_rich_string(43,0,sym,'D',ital,'d',subs,'a')
        wbud.write(43,2,'mm')
        wbud.write_rich_string(44,0,sym,'D',ital,'d',subs,'m')
        wbud.write(44,2,'mm')
        wbud.write(45,0,'m',sym)
        wbud.write(45,2,'1')
        wbud.write(46,0,'b',sym)
        wbud.write_rich_string(46,2,'mm',sups,'-1')
        wbud.write_rich_string(47,0,sym,'D',ital,'x',subs,'a')
        wbud.write(47,2,'mm')
        if style=='Q':
            wbud.write_rich_string(4,11,ital,'t',subs,'i')
            wbud.write_rich_string(5,11,ital,'n',subs,'p a')
            wbud.write_rich_string(6,11,sym,'l',subs,'a') #from here +1
            wbud.write_rich_string(7,11,sym,'l',subs,'2 a')
            wbud.write_rich_string(8,11,sym,'D',ital,'t',subs,'d')
            wbud.write_rich_string(9,11,ital,'t',subs,'c a')
            wbud.write_rich_string(10,11,ital,'t',subs,'l a')
            wbud.write_rich_string(11,11,ital,'COI',subs,'a')
            wbud.write_rich_string(12,11,ital,'m',subs,'sm')
            wbud.write_rich_string(13,11,ital,'k',subs,'0 Au','(a)')
            wbud.write_rich_string(14,11,ital,'G',subs,'th a')
            wbud.write_rich_string(15,11,ital,'G',subs,'e a')
            wbud.write_rich_string(16,11,ital,'Q',subs,'0 a')
            wbud.write_rich_string(17,11,ital,'E',subs,'r a')
            wbud.write_rich_string(18,11,ital,'n',subs,'p m')
            wbud.write_rich_string(19,11,sym,'l',subs,'m')
            wbud.write_rich_string(20,11,ital,'t',subs,'d m')
            wbud.write_rich_string(21,11,ital,'t',subs,'c m')
            wbud.write_rich_string(22,11,ital,'t',subs,'l m')
            wbud.write_rich_string(23,11,ital,'COI',subs,'m')
            wbud.write_rich_string(24,11,ital,'m',subs,'std')
            wbud.write_rich_string(25,11,ital,'w',subs,'m')
            wbud.write_rich_string(26,11,ital,'k',subs,'0 Au','(m)')
            wbud.write_rich_string(27,11,ital,'G',subs,'th m')
            wbud.write_rich_string(28,11,ital,'G',subs,'e m')
            wbud.write_rich_string(29,11,ital,'Q',subs,'0 m')
            wbud.write_rich_string(30,11,ital,'E',subs,'r m')
            wbud.write(31,11,'f',ital)
            wbud.write(32,11,'a',sym)
            wbud.write_rich_string(33,11,ital,'a',subs,'1')
            wbud.write_rich_string(34,11,ital,'a',subs,'2')
            wbud.write_rich_string(35,11,ital,'a',subs,'3')
            wbud.write_rich_string(36,11,ital,'a',subs,'4')
            wbud.write_rich_string(37,11,ital,'a',subs,'5')
            wbud.write_rich_string(38,11,ital,'a',subs,'6')
            wbud.write_rich_string(39,11,ital,'E',subs,'p a')
            wbud.write_rich_string(40,11,ital,'E',subs,'p m')
            wbud.write_rich_string(41,11,sym,'de',subs,'a')
            wbud.write_rich_string(42,11,sym,'de',subs,'m')
            wbud.write_rich_string(43,11,sym,'D',ital,'d',subs,'a')
            wbud.write_rich_string(44,11,sym,'D',ital,'d',subs,'m')
            wbud.write(45,11,'m',sym)
            wbud.write(46,11,'b',sym)
            wbud.write_rich_string(47,11,sym,'D',ital,'x',subs,'a')
            wbud.write_rich_string(3,12,ital,'t',subs,'i')
            wbud.write_rich_string(3,13,ital,'n',subs,'p a')
            wbud.write_rich_string(3,14,sym,'l',subs,'a')
            wbud.write_rich_string(3,15,sym,'l',subs,'2 a')
            wbud.write_rich_string(3,16,sym,'D',ital,'t',subs,'d')
            wbud.write_rich_string(3,17,ital,'t',subs,'c a')
            wbud.write_rich_string(3,18,ital,'t',subs,'l a')
            wbud.write_rich_string(3,19,ital,'COI',subs,'a')
            wbud.write_rich_string(3,20,ital,'m',subs,'sm')
            wbud.write_rich_string(3,21,ital,'k',subs,'0 Au','(a)')
            wbud.write_rich_string(3,22,ital,'G',subs,'th a')
            wbud.write_rich_string(3,23,ital,'G',subs,'e a')
            wbud.write_rich_string(3,24,ital,'Q',subs,'0 a')
            wbud.write_rich_string(3,25,ital,'E',subs,'r a')
            wbud.write_rich_string(3,26,ital,'n',subs,'p m')
            wbud.write_rich_string(3,27,sym,'l',subs,'m')
            wbud.write_rich_string(3,28,ital,'t',subs,'d m')
            wbud.write_rich_string(3,29,ital,'t',subs,'c m')
            wbud.write_rich_string(3,30,ital,'t',subs,'l m')
            wbud.write_rich_string(3,31,ital,'COI',subs,'m')
            wbud.write_rich_string(3,32,ital,'m',subs,'std')
            wbud.write_rich_string(3,33,ital,'w',subs,'m')
            wbud.write_rich_string(3,34,ital,'k',subs,'0 Au','(m)')
            wbud.write_rich_string(3,35,ital,'G',subs,'th m')
            wbud.write_rich_string(3,36,ital,'G',subs,'e m')
            wbud.write_rich_string(3,37,ital,'Q',subs,'0 m')
            wbud.write_rich_string(3,38,ital,'E',subs,'r m')
            wbud.write(3,39,'f',ital)
            wbud.write(3,40,'a',sym)
            wbud.write_rich_string(3,41,ital,'a',subs,'1')
            wbud.write_rich_string(3,42,ital,'a',subs,'2')
            wbud.write_rich_string(3,43,ital,'a',subs,'3')
            wbud.write_rich_string(3,44,ital,'a',subs,'4')
            wbud.write_rich_string(3,45,ital,'a',subs,'5')
            wbud.write_rich_string(3,46,ital,'a',subs,'6')
            wbud.write_rich_string(3,47,ital,'E',subs,'p a')
            wbud.write_rich_string(3,48,ital,'E',subs,'p m')
            wbud.write_rich_string(3,49,sym,'de',subs,'a')
            wbud.write_rich_string(3,50,sym,'de',subs,'m')
            wbud.write_rich_string(3,51,sym,'D',ital,'d',subs,'a')
            wbud.write_rich_string(3,52,sym,'D',ital,'d',subs,'m')
            wbud.write(3,53,'m',sym)
            wbud.write(3,54,'b',sym)
            wbud.write_rich_string(3,55,sym,'D',ital,'x',subs,'a')
        wbud.write(49,0,'Quantity')
        wbud.write(49,2,'Unit')
        wbud.write(49,3,'Value')
        if style=='Q':
            wbud.write(49,4,'Std unc')
            wbud.write(49,5,'Rel unc')
            wbud.write(49,9,'Contribution to variance')
        wbud.write(50,0,'Y',ital)
        wbud.write_rich_string(50,2,'[',ital,'y',']')
        wbud.write(50,3,'y',ital)
        if style=='Q':
            wbud.write_rich_string(50,4,ital,'u','(',ital,'y',')')
            wbud.write_rich_string(50,5,ital,'u',subs,'r','(',ital,'y',')')
            wbud.write_rich_string(50,9,ital,'I',' / %')
        wbud.write_rich_string(51,0,ital,'w',subs,'a')
        wbud.write_rich_string(51,2,'g g',sups,'-1')
        if style=='Q':
            for ri in range(len(MC)):
                sm='#'
                for ci in range(len(MC)):
                    wbud.write(4+ri,12+ci,MC[ri,ci])
                    cell_corr = xl_rowcol_to_cell(4+ri,12+ci)
                    fml='='+str(cell_corr)+'*E'+str(4+ri+1)+'*E'+str(4+ci+1)
                    wbud.write(4+ri,57+ci,fml,gray)
                    sms=str(cell_corr)+'*E'+str(4+ri+1)+'*E'+str(4+ci+1)+'*I'+str(4+ri+1)+'*I'+str(4+ci+1)
                    sm=sm+'+'+sms
                sm=sm.replace('#+','=(')
                sm=sm+')/E52^2'
                if ri in [29,30,31,32,33,34,35,36]:
                    wbud.write(4+ri,9,sm,graypct)
                else:
                    wbud.write(4+ri,9,sm,pct)
        fml=f'=({parm_id[1]}*({parm_id[3]}-{parm_id[2]})*{parm_id[5]}*EXP({parm_id[41]}*(1-{parm_id[6]}/{parm_id[5]}))*{parm_id[18]}*(1-EXP(-{parm_id[15]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[15]})*{parm_id[16]}+{parm_id[3]}*{parm_id[4]})*(1-EXP(-{parm_id[15]}*{parm_id[17]}))*{parm_id[19]}*{parm_id[20]}*{parm_id[21]}*{parm_id[22]}*({parm_id[23]}+{parm_id[24]}/{parm_id[27]}*(({parm_id[25]}-0.429)/{parm_id[26]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[36]}+{parm_id[30]}+{parm_id[31]}*{parm_id[36]}^-1+{parm_id[32]}*{parm_id[36]}^-2+{parm_id[33]}*{parm_id[36]}^-3+{parm_id[34]}*{parm_id[36]}^-4)*(1-{parm_id[38]}*{parm_id[40]}))/({parm_id[15]}*{parm_id[14]}*{parm_id[17]}*EXP({parm_id[41]}*(1-{parm_id[18]}/{parm_id[17]}))*{parm_id[6]}*({parm_id[3]}/{parm_id[2]}*(1-EXP(-{parm_id[2]}*{parm_id[0]}))*EXP(({parm_id[3]}-{parm_id[2]})*({parm_id[16]}+{parm_id[4]}))*(1-EXP(-{parm_id[2]}*{parm_id[5]}))-{parm_id[2]}/{parm_id[3]}*(1-EXP(-{parm_id[3]}*{parm_id[0]}))*(1-EXP(-{parm_id[3]}*{parm_id[5]})))*{parm_id[7]}*{parm_id[8]}*{parm_id[9]}*(1+{parm_id[42]}*{parm_id[43]})*({parm_id[10]}+{parm_id[11]}/{parm_id[27]}*(({parm_id[12]}-0.429)/{parm_id[13]}^{parm_id[28]}+0.429/((2*{parm_id[28]}+1)*0.55^{parm_id[28]})))*EXP({parm_id[29]}*{parm_id[35]}+{parm_id[30]}+{parm_id[31]}*{parm_id[35]}^-1+{parm_id[32]}*{parm_id[35]}^-2+{parm_id[33]}*{parm_id[35]}^-3+{parm_id[34]}*{parm_id[35]}^-4)*(1-{parm_id[37]}*{parm_id[39]}))'
        #fml=f'=({D6}*({D8}-{D7})*{D10}*EXP({D46}*(1-{D11}/{D10}))*{D23}*(1-EXP(-{D20}*{D5}))*EXP(({D8}-{D20})*{D21}+{D8}*{D9})*(1-EXP(-{D20}*{D22}))*{D24}*{D25}*{D26}*{D27}*({D28}+{D29}/{D32}*(({D30}-0.429)/{D31}^{D33}+0.429/((2*{D33}+1)*0.55^{D33})))*EXP({D34}*{D41}+{D35}+{D36}*{D41}^-1+{D37}*{D41}^-2+{D38}*{D41}^-3+{D39}*{D41}^-4)*(1-{D43}*{D45}))/({D20}*{D19}*{D22}*EXP({D46}*(1-{D23}/{D22}))*{D11}*({D8}/{D7}*(1-EXP(-{D7}*{D5}))*EXP(({D8}-{D7})*({D21}+{D9}))*(1-EXP(-{D7}*{D10}))-{D7}/{D8}*(1-EXP(-{D8}*{D5}))*(1-EXP(-{D8}*{D10})))*{D12}*{D13}*{D14}*({D15}+{D16}/{D32}*(({D17}-0.429)/{D18}^{D33}+0.429/((2*{D33}+1)*0.55^{D33})))*EXP({D34}*{D40}+{D35}+{D36}*{D40}^-1+{D37}*{D40}^-2+{D38}*{D40}^-3+{D39}*{D40}^-4)*(1-{D42}*{D44}))'
        wbud.write(51,3,fml)
        if style=='Q':
            fml='{=sqrt(MMULT(MMULT(TRANSPOSE(I5:I48),BF5:CW48),I5:I48))}'
            wbud.write_formula(51,4,fml)
            fml='=ABS(E52/D52)'
            wbud.write(51,5,fml,pct)
            fml='=SUM(J5:J48)'
            wbud.write(51,9,fml,pct)
        wbud.write(54,0,'Additional information')
        wbud.write(55,0,'Quantity')
        wbud.write(55,2,'Unit')
        wbud.write(55,3,'Value')
        wbud.write_rich_string(56,0,ital,'X',subs,'i')
        wbud.write_rich_string(56,2,'[',ital,'X',subs,'i',']')
        wbud.write_rich_string(56,3,ital,'x',subs,'i')
        if style=='Q':
            wbud.write(55,4,'Std unc')
            wbud.write(55,5,'Rel unc')
            wbud.write(55,9,'Contribution to variance')            
            wbud.write_rich_string(56,4,ital,'u','(',ital,'x',subs,'i',')')
            wbud.write_rich_string(56,5,ital,'u',subs,'r','(',ital,'x',subs,'i',')')
            wbud.write_rich_string(56,9,ital,'I',' / %')
        wbud.write_rich_string(57,0,sym,'e','(',ital,'a',subs,'i',', ',ital,'E',subs,'p a',', ',ital,'E',subs,'p m',')')
        wbud.write_rich_string(58,0,ital,'Q',subs,'0,a','(',sym,'a',')')
        wbud.write_rich_string(59,0,ital,'Q',subs,'0,m','(',sym,'a',')')
        wbud.write(57,2,'1')
        wbud.write(58,2,'1')
        wbud.write(59,2,'1')
        
        fml='=(EXP(D34*D41+D35+D36*D41^-1+D37*D41^-2+D38*D41^-3+D39*D41^-4))/(EXP(D34*D40+D35+D36*D40^-1+D37*D40^-2+D38*D40^-3+D39*D40^-4))'
        wbud.write(57,3,fml)
        if style=='Q':#here!
            fml='=SQRT(J58*E52^2)/((D6*(D8-D7)*D10*EXP(D46*(1-D11/D10))*D23*(1-EXP(-D20*D5))*EXP((D8-D20)*D21+D8*D9)*(1-EXP(-D20*D22))*D24*D25*D26*D27*(D28+D29/D32*((D30-0.429)/D31^D33+0.429/((2*D33+1)*0.55^D33)))*(1-D43*D45))/(D20*D19*D22*EXP(D46*(1-D23/D22))*D11*(D8/D7*(1-EXP(-D7*D5))*EXP((D8-D7)*(D21+D9))*(1-EXP(-D7*D10))-D7/D8*(1-EXP(-D8*D5))*(1-EXP(-D8*D10)))*D12*D13*D14*(1+D47*D48)*(D15+D16/D32*((D17-0.429)/D18^D33+0.429/((2*D33+1)*0.55^D33)))*(1-D42*D44)))'#(D6*D7*D9*EXP(D45*(1-D10/D9))*D22*(1-EXP(-D19*D5))*EXP((D7-D19)*D20+D7*D8)*(1-EXP(-D19*D21))*D23*D24*D25*D26*(D27+D28/D31*((D29-0.429)/D30^D32+0.429/((2*D32+1)*0.55^D32)))*(1-D42*D44))/(D19*D18*D21*EXP(D45*(1-D22/D21))*D10*(1-EXP(-D7*D5))*(1-EXP(-D7*D9))*D11*D12*D13*(D14+D15/D31*((D16-0.429)/D17^D32+0.429/((2*D32+1)*0.55^D32)))*(1-D41*D43)))'
            wbud.write(57,4,fml)
            fml='=E58/D58'
            wbud.write(57,5,fml,pct)
            fml='=SUM(J34:J41)'
            wbud.write(57,9,fml,pct)
        
        fml='=(D17-0.429)/D18^D33+0.429/((2*D33+1)*0.55^D33)'
        wbud.write(58,3,fml)
        if style=='Q':
            wbud.write(58,4,'-')
            wbud.write(58,5,'-')
        
        fml='=(D30-0.429)/D31^D33+0.429/((2*D33+1)*0.55^D33)'
        wbud.write(59,3,fml)
        if style=='Q':
            wbud.write(59,4,'-')
            wbud.write(59,5,'-')
            wbud.set_column('G:H', None, None, {'hidden': True})
        wbud.write(62,0,'Measurement model')
        wbud.insert_image(63,0,'data/models/TypeIIA.jpg',{'x_scale': 1.5, 'y_scale': 1.5})
    else:
        wbud.write(2,0,'Missing spectrum data')
        wbud.write(51,3,'-')
    
def budget_Mtype_IIC(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_IID(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_IIIA(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_IIIB(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_IIIC(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_IVA(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_IVD(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_VA(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_VB(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_VC(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
        
def budget_Mtype_VIIA(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_VIIB(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def budget_Mtype_VIII(wbud,starting_point,MP,MC,indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,style='Q'):
    from xlsxwriter.utility import xl_rowcol_to_cell
    link='=Analysis!B'+str(starting_point+indexs)
    wbud.write(0,0,link,bold)
    link='=Analysis!C'+str(starting_point+indexs)
    wbud.write(0,1,link,bold)
    link='=Analysis!E'+str(starting_point+indexs)
    wbud.write(0,2,link,bold)
    wbud.write(0,3,'keV',bold)
    wbud.write(2,0,'This particular decay type has not been implemented yet!')
    
def writeonfile(nomefile,NAA,monitor,total_assigned_peaklist,cumulate_peaklist,cumulate_detection,total_residus_list):
    wb = xlsxwriter.Workbook(nomefile)
    ws = wb.add_worksheet('Analysis')
    bold = wb.add_format({'bold': True})
    ital = wb.add_format({'italic': True})
    Green = wb.add_format({'bold': True, 'font_color': 'green'})
    pct = wb.add_format({'num_format': 0x0a})
    sups = wb.add_format({'font_script': 1})
    subs = wb.add_format({'font_script': 2})
    gray = wb.add_format({'font_color': 'gray'})
    grayit = wb.add_format({'italic': True, 'font_color': 'gray'})
    graysub = wb.add_format({'font_script': 2, 'font_color': 'gray'})
    graypct = wb.add_format({'num_format': 0x0a, 'font_color': 'gray'})
    dateandtime = wb.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
    try:
        sym = wb.add_format({'font_name': 'Symbol'})
        graysym = wb.add_format({'font_name': 'Symbol', 'font_color': 'gray'})
    except:
        sym = wb.add_format({'font_name': 'Times New Roman'})
        graysym = wb.add_format({'font_name': 'Times New Roman', 'font_color': 'gray'})
    check='non-1/v reaction'
    ws.set_column('A:A', 16)
    #ws.set_column('F:F', 10)
    ws.set_column('F:H', 12)
    ws.set_column('M:M', 13)
    ws.write(0,0,'Irradiation end')
    ws.write_rich_string(0,2,ital,'t',subs,'i',' / s')
    ws.write(0,4,'Channel')
    ws.write_rich_string(0,5,ital,'f',' / 1')
    ws.write_rich_string(0,6,sym,'a',' / 1')
    ws.write(0,8,'Calibration name')
    ws.write(0,10,'Detector')
    ws.write(0,11,'Distance / mm')
    ws.write(0,13,f'k0-INRIM version: {NAA.info["version"]}')
    ws.write(1,13,f'database version: {NAA.info["database"]}')
    ws.write(1,0,NAA.irradiation.datetime,dateandtime)
    ws.write(1,2,NAA.irradiation.time)
    ws.write(1,4,NAA.irradiation.channel)
    ws.write(1,5,NAA.irradiation.f)
    ws.write(1,6,NAA.irradiation.a)
    ws.write(1,8,NAA.calibration.name)
    ws.write(1,10,NAA.calibration.detector)
    ws.write(1,11,NAA.calibration.distance)
    ws.write(3,0,'Standard',bold)
    ws.write(3,2,NAA.comparator.spectrumpath,bold)
    ws.write(4,0,'Start acquisition')
    ws.write_rich_string(4,2,ital,'t',subs,'c',' / s')
    ws.write_rich_string(4,3,ital,'t',subs,'l',' / s')
    ws.write_rich_string(4,4,ital,'t',subs,'dead')
    ws.write_rich_string(4,5,ital,'t',subs,'d',' / s')
    ws.write(5,0,NAA.comparator.datetime,dateandtime)
    ws.write(5,2,NAA.comparator.real_time)
    ws.write(5,3,NAA.comparator.live_time)
    fml='=(C6-D6)/C6'
    ws.write(5,4,fml,pct)
    fml='=(A6-A2)*86400'
    ws.write(5,5,fml)
    if monitor!=None:
        ws.write(7,0,'Target')
        ws.write(7,1,'Isotope')
        ws.write(7,2,'Emitter')
        ws.write(7,3,'Half-life')
        ws.write_rich_string(7,4,ital,'E',subs,'p',' / keV')
        ws.write_rich_string(7,5,ital,'n',subs,'p',' / 1')
        ws.write(7,6,'FWHM / ch')
        ws.write(7,7,'Coincidence')
        ws.write_rich_string(7,8,ital,'m',subs,'std',' / g')#std
        ws.write(7,9,'Decay type')
        
        ws.write_rich_string(7,11,ital,'w',subs,'m',' / g g',sups,'-1')
        ws.write_rich_string(7,12,ital,'u','(',ital,'w',subs,'m',') / g g',sups,'-1')
        ws.write_rich_string(7,13,ital,'u',subs,'r','(',ital,'w',subs,'m',')')
        gstate=''
        if float(monitor[25])==2.0:
            gstate='m'
        istp=str(monitor[23])+'-'+str(int(monitor[24]))+gstate
        ws.write(8,0,monitor[22])
        ws.write(8,1,monitor[89]+'-'+str(int(monitor[90])))
        ws.write(8,2,istp)
        ws.write(8,3,str(monitor[52])+' '+str(monitor[53]))
        ws.write(8,4,monitor[26])
        ws.write(8,5,float(monitor[8]))
        ws.write(8,6,float(monitor[10]))
        if monitor[31]==0.0:
            ws.write(8,7,'no')
        else:
            ws.write(8,7,'yes')
        ws.write(8,8,NAA.masses[0])
        ws.write(8,9,monitor[43])
        ws.write(8,11,float(NAA.comparatormassfraction[0]))
        ws.write(8,12,float(NAA.comparatormassfraction[1]))
        ws.write(8,13,'=M9/L9',pct)
        if check in monitor[104]:
            ws.write(8,15,'non-1/v')
        analytes_start=11
        r=0
        for spct in range(len(NAA.sample)):
            ws.write(analytes_start+spct+r,0,'Sample',bold)
            ws.write(analytes_start+spct+r,2,NAA.sample[spct].spectrumpath,bold)
            r+=1
            ws.write(analytes_start+spct+r,0,'Start acquisition')
            ws.write_rich_string(analytes_start+spct+r,2,ital,'t',subs,'c',' / s')
            ws.write_rich_string(analytes_start+spct+r,3,ital,'t',subs,'l',' / s')
            ws.write_rich_string(analytes_start+spct+r,4,ital,'t',subs,'dead')
            ws.write_rich_string(analytes_start+spct+r,5,ital,'t',subs,'d',' / s')
            r+=1
            ws.write(analytes_start+spct+r,0,NAA.sample[spct].datetime,dateandtime)
            ws.write(analytes_start+spct+r,2,NAA.sample[spct].real_time)
            ws.write(analytes_start+spct+r,3,NAA.sample[spct].live_time)
            fml='=(C'+str(analytes_start+spct+r+1)+'-D'+str(analytes_start+spct+r+1)+')/C'+str(analytes_start+spct+r+1)
            ws.write(analytes_start+spct+r,4,fml,pct)
            fml='=(A'+str(analytes_start+spct+r+1)+'-A2)*86400'
            ws.write(analytes_start+spct+r,5,fml)
            r+=2
            ws.write(analytes_start+spct+r,0,'Quantifications',ital)
            r+=1
            ws.write(analytes_start+spct+r,0,'Target')
            ws.write(analytes_start+spct+r,1,'Isotope')
            ws.write(analytes_start+spct+r,2,'Emitter')
            ws.write(analytes_start+spct+r,3,'Half-life')
            ws.write_rich_string(analytes_start+spct+r,4,ital,'E',subs,'p',' / keV')
            ws.write_rich_string(analytes_start+spct+r,5,ital,'n',subs,'p',' / 1')
            ws.write(analytes_start+spct+r,6,'FWHM / ch')
            ws.write(analytes_start+spct+r,7,'Coincidence')
            ws.write_rich_string(analytes_start+spct+r,8,ital,'m',subs,'sm',' / g')
            ws.write(analytes_start+spct+r,9,'Decay type')
            ws.write_rich_string(analytes_start+spct+r,11,ital,'w',subs,'a',' / g g',sups,'-1')
            ws.write_rich_string(analytes_start+spct+r,12,ital,'u','(',ital,'w',subs,'a',') / g g',sups,'-1')
            ws.write_rich_string(analytes_start+spct+r,13,ital,'u',subs,'r','(',ital,'w',subs,'a',')')
            r+=1
            operator_point=analytes_start+spct+r
            if total_assigned_peaklist[spct]!=[]:
                for linna in total_assigned_peaklist[spct]:
                    ws.write(analytes_start+spct+r,0,linna[22])
                    ws.write(analytes_start+spct+r,1,linna[89]+'-'+str(int(linna[90])))
                    gstate=''
                    if float(linna[25])==2.0:
                        gstate='m'
                    ws.write(analytes_start+spct+r,2,str(linna[23])+'-'+str(int(linna[24]))+gstate)
                    ws.write(analytes_start+spct+r,3,str(linna[52])+' '+str(linna[53]))
                    ws.write(analytes_start+spct+r,4,linna[26])
                    ws.write(analytes_start+spct+r,5,float(linna[8]))
                    ws.write(analytes_start+spct+r,6,float(linna[10]))
                    if linna[31]==0.0:
                        ws.write(analytes_start+spct+r,7,'no')
                    else:
                        ws.write(analytes_start+spct+r,7,'yes')
                    ws.write(analytes_start+spct+r,8,NAA.masses[2])
                    ws.write(analytes_start+spct+r,9,linna[43])
                    if check in linna[104]:
                        ws.write(analytes_start+spct+r,15,'non-1/v')
                    r+=1
            else:
                ws.write(analytes_start+spct+r,0,'-',bold)
                r+=1
            r+=1
            ws.write(analytes_start+spct+r,0,'Detection limits',ital)
            r+=1
            ws.write(analytes_start+spct+r,0,'Target')
            ws.write(analytes_start+spct+r,1,'Isotope')
            ws.write(analytes_start+spct+r,2,'Emitter')
            ws.write(analytes_start+spct+r,3,'Half-life')
            ws.write_rich_string(analytes_start+spct+r,4,ital,'E',subs,'p',' / keV')
            ws.write_rich_string(analytes_start+spct+r,5,ital,'n',subs,'p','(Currie) / 1')
            ws.write(analytes_start+spct+r,6,'FWHM / ch')
            ws.write(analytes_start+spct+r,7,'Coincidence')
            ws.write_rich_string(analytes_start+spct+r,8,ital,'m',subs,'sm',' / g')
            ws.write(analytes_start+spct+r,9,'Decay type')
            ws.write_rich_string(analytes_start+spct+r,11,'(<)',ital,'w',subs,'a',' / g g',sups,'-1')
            ws.write(analytes_start+spct+r,13,'Lowest detection limit')
            r+=1
            detected_point=analytes_start+spct+r
            if cumulate_detection!=[]:
                if cumulate_detection[spct][0]!=[]:
                    for linna in cumulate_detection[spct][0]:
                        ws.write(analytes_start+spct+r,0,linna[1])
                        ws.write(analytes_start+spct+r,1,linna[68]+'-'+str(int(linna[69])))
                        gstate=''
                        if float(linna[4])==2.0:
                            gstate='m'
                        ws.write(analytes_start+spct+r,2,str(linna[2])+'-'+str(int(linna[3]))+gstate)
                        ws.write(analytes_start+spct+r,3,str(linna[31])+' '+str(linna[32]))
                        ws.write(analytes_start+spct+r,4,linna[5])
                        channel_position = NAA.calibration.energy_fit_reversed(linna[5])
                        detectionlimitrange=int(NAA.detection_limits_FWHM*NAA.calibration.fwhm_fit(channel_position))+1
                        AD=NAA.sample[spct].defined_spectrum_integral(int(channel_position-detectionlimitrange/2),detectionlimitrange)
                        if AD!=None:
                            ws.write(analytes_start+spct+r,5,AD)
                        else:
                            ws.write(analytes_start+spct+r,5,'-')
                        fml='='+str(NAA.detection_limits_FWHM)+'*'+str(detectionlimitrange/NAA.detection_limits_FWHM)
                        ws.write(analytes_start+spct+r,6,fml)
                        if linna[10]==0.0:
                            ws.write(analytes_start+spct+r,7,'no')
                        else:
                            ws.write(analytes_start+spct+r,7,'yes')
                        ws.write(analytes_start+spct+r,8,NAA.masses[2])
                        ws.write(analytes_start+spct+r,9,linna[22])
                        if check in linna[83]:
                            ws.write(analytes_start+spct+r,15,'non-1/v')
                        r+=1
                else:
                    ws.write(analytes_start+spct+r,0,'-',bold)
                    r+=1
            else:
                ws.write(analytes_start+spct+r,0,'-',bold)
                r+=1
            r+=1
            #budgets users
            if NAA.quantification[spct]!=[] and NAA.quantification[spct]!=None:
                operator_point=operator_point+1
                rsnl=operator_point+1
                for indexs in range(len(NAA.quantification[spct])):
                    numeral=1
                    avoidinferences='('+str(numeral)+')'
                    sheetname='('+str(spct+1)+')_UncBud_'+total_assigned_peaklist[spct][indexs][22]+avoidinferences
                    while wb.get_worksheet_by_name(sheetname)!=None:
                        numeral=numeral+1
                        avoidinferences='('+str(numeral)+')'
                        sheetname='('+str(spct+1)+')_UncBud_'+total_assigned_peaklist[spct][indexs][22]+avoidinferences
                    print(sheetname)
                    wbud=wb.add_worksheet(sheetname)
                    if total_assigned_peaklist[spct][indexs][43]=='IIA':
                        budget_Mtype_IIA(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!D52"
                        ws.write(operator_point-1+indexs,11,link,Green)
                        link="='"+str(sheetname)+"'!E52"
                        ws.write(operator_point-1+indexs,12,link,Green)
                        link="='"+str(sheetname)+"'!F52"
                        ws.write(operator_point-1+indexs,13,link,pct)
                    elif total_assigned_peaklist[spct][indexs][43]=='IIC':
                        budget_Mtype_IIC(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='IID':
                        budget_Mtype_IID(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='IIIA':
                        budget_Mtype_IIIA(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='IIIB':
                        budget_Mtype_IIIB(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='IIIC':
                        budget_Mtype_IIIC(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='IVA':
                        budget_Mtype_IVA(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='IVC':
                        budget_Mtype_IIC(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='IVD':
                        budget_Mtype_IVD(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='VA':
                        budget_Mtype_VA(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    #elif total_assigned_peaklist[spct][indexs][43]=='VB':
                    #    budget_Mtype_VB(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                    #    link="='"+str(sheetname)+"'!A3"
                    #    ws.write(operator_point-1+indexs,11,link,Green)
                    #elif total_assigned_peaklist[spct][indexs][43]=='VC':
                    #    budget_Mtype_VC(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                    #    link="='"+str(sheetname)+"'!A3"
                    #    ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='VIIA':
                        budget_Mtype_VIIA(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='VIIB':
                        budget_Mtype_VIIB(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    elif total_assigned_peaklist[spct][indexs][43]=='VIII':
                        budget_Mtype_VIII(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!A3"
                        ws.write(operator_point-1+indexs,11,link,Green)
                    else:
                        budget_Mtype_I(wbud,operator_point,NAA.quantification[spct][indexs][0],NAA.quantification[spct][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        link="='"+str(sheetname)+"'!D51"
                        ws.write(operator_point-1+indexs,11,link,Green)
                        link="='"+str(sheetname)+"'!E51"
                        ws.write(operator_point-1+indexs,12,link,Green)
                        link="='"+str(sheetname)+"'!F51"
                        ws.write(operator_point-1+indexs,13,link,pct)
            #detection limits
            try:
                if cumulate_detection[spct]!=[] and cumulate_detection[spct]!=None:
                    detected_point=detected_point+1
                    rsnl=detected_point+1
                    for indexs in range(len(cumulate_detection[spct][0])):
                        numeral=1
                        avoidinferences='('+str(numeral)+')'
                        sheetname='('+str(spct+1)+')_DetLim_'+cumulate_detection[spct][0][indexs][1]+avoidinferences
                        while wb.get_worksheet_by_name(sheetname)!=None:
                            numeral=numeral+1
                            avoidinferences='('+str(numeral)+')'
                            sheetname='('+str(spct+1)+')_DetLim_'+cumulate_detection[spct][0][indexs][1]+avoidinferences
                        print(sheetname)
                        wbud=wb.add_worksheet(sheetname)
                        if cumulate_detection[spct][0][indexs][22]=='IIA':
                            budget_Mtype_IIA(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,'D')
                            link="=IFERROR('"+str(sheetname)+"'!D52,"+'"-"'+")"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='IIC':
                            budget_Mtype_IIC(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='IID':
                            budget_Mtype_IID(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='IIIA':
                            budget_Mtype_IIIA(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='IIIB':
                            budget_Mtype_IIIB(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='IIIC':
                            budget_Mtype_IIIC(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='IVA':
                            budget_Mtype_IVA(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='IVC':
                            budget_Mtype_IIC(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='IVD':
                            budget_Mtype_IVD(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='VA':
                            budget_Mtype_VA(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        #elif cumulate_detection[spct][0][indexs][22]=='VB':
                        #    budget_Mtype_VB(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        #    link="='"+str(sheetname)+"'!A3"
                        #    ws.write(detected_point-1+indexs,11,link,Green)
                        #elif cumulate_detection[spct][0][indexs][22]=='VC':
                        #    budget_Mtype_VC(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                        #    link="='"+str(sheetname)+"'!A3"
                        #    ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='VIIA':
                            budget_Mtype_VIIA(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='VIIB':
                            budget_Mtype_VIIB(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        elif cumulate_detection[spct][0][indexs][22]=='VIII':
                            budget_Mtype_VIII(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct)
                            link="='"+str(sheetname)+"'!A3"
                            ws.write(detected_point-1+indexs,11,link,Green)
                        else:
                            budget_Mtype_I(wbud,detected_point,cumulate_detection[spct][1][indexs][0],cumulate_detection[spct][1][indexs][1],indexs,bold,ital,Green,pct,sups,subs,sym,gray,grayit,graysub,graysym,graypct,'D')
                            link="=IFERROR('"+str(sheetname)+"'!D51,"+'"-"'+")"
                            ws.write_formula(detected_point-1+indexs,11,link,Green)
                        try:
                            if cumulate_detection[spct][0][indexs][1]!=cumulate_detection[spct][0][indexs+1][1]:
                                fml='=MIN(L'+str(rsnl-1)+':L'+str(detected_point+indexs)+')'
                                ws.write(detected_point-1+indexs,13,fml,Green)
                                rsnl=detected_point+2+indexs
                        except IndexError:
                            fml='=MIN(L'+str(rsnl-1)+':L'+str(detected_point+indexs)+')'
                            ws.write(detected_point-1+indexs,13,fml,Green)
            except IndexError:
                pass
    print('\nSaving to .xlsx file\nplease wait...')
    wb.close()
        
if __name__=='__main__':
    searchforhypelabfile()
