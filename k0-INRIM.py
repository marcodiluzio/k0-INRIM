# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 10:30:09 2018

k0-INRIM should allow to perform k0-standardization NAA analysis 
by returning results (concentration of target elements) together with
compiled uncertainty budgets aderent to the prescriptions reported in 
the Guide to the expression of uncertainty in Measurement (GUM)

@author: Marco Di Luzio
"""

from tkinter import *
import os
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
import datetime
from tkinter import ttk
from tkinter import messagebox
try:
    import xlrd
    import numpy as np
    import matplotlib
    import xlsxwriter
    from scipy.optimize import fsolve
except ModuleNotFoundError:
    answ = input('Additional python modules have not been found.\nThe required modules (modules name and version are found in the requirements.txt file) will be installed in your current python environment, otherwise you will need to manually manage the additional packages.\nInternet connection is necessary.\n\nPress <y> key to confirm the modules installation or any other key to exit: ')
    if answ.lower()=='y':
        os.system('cmd /k "pip install -r requirements.txt"')
        os.system('cmd /c "pip list"')
    quit()
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
try:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
except:
    from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from classes.naaobj import *

#Version #update these in case of modifications
VERSION = 1.3
VERSION_DATE = '29 October 2020'

#Matplotlib graph visualization parameters
matplotlib.rcParams['font.size'] = 8
matplotlib.rcParams['savefig.dpi'] = 300
matplotlib.rcParams['axes.formatter.limits'] = [-5,5]

def main():
    def initialization(settingsfile):
        f=open(settingsfile, 'r')
        rs=f.readlines()
        f.close()
        for i in range(len(rs)):
            rs[i]=rs[i].replace('\n','')
        return rs
    
    def findoutexceltable(wb,sheet):
        fs=wb.sheet_by_name(sheet)
        table=[]
        a=0
        while a>-1:
            try:
                vlx=str(fs.cell(0,a).value)
            except:
                break
            else:
                a=a+1
        table=[]
        r=1
        while r>0:
            try:
                line=[]
                for i in range(a):
                    vlx=str(fs.cell(r,i).value)
                    try:
                        line.append(float(vlx))
                    except:
                        line.append(vlx)
            except:
                break
            else:
                table.append(line)
                r=r+1
        return table
    
    def totalk0tables(wb,sssh):
        tablesk0databases=[]
        for index in sssh:
            tablesk0databases.append(findoutexceltable(wb,index))
        return tablesk0databases
    
    def openselectedk0database(k0database):
        """Open k0 database from file xls"""
        try:
            wb=xlrd.open_workbook('data/k0data/'+k0database)
        except FileNotFoundError:
            pass
        else:
            sssh=wb.sheet_names()
            A=totalk0tables(wb,sssh)
            return A
        
    def lineacumulata(A):
        """Arrange k0 database on memory"""
        keyline=[]
        for i in range(len(A[0])-1):
            key=A[0][i][0]
            emission=A[0][i][:18]
            for decay in range(len(A[4])):
                if A[4][decay][0]==key:
                    emiss,fath,grandfa=A[4][decay][0],A[4][decay][5],A[4][decay][6]
                    decaycode=A[4][decay][:8]
                    break
            for nuclide in range(len(A[3])-1):
                if A[3][nuclide][0]==emiss:
                    daught=A[3][nuclide][:13]
                    break
            for nuclide in range(len(A[3])-1):
                if A[3][nuclide][0]==fath:
                    father=A[3][nuclide][:13]
                    break
                else:
                    father=['','','','','','','','','','','','','']
            for nuclide in range(len(A[3])-1):
                if A[3][nuclide][0]==grandfa:
                    grandfather=A[3][nuclide][:13]
                    break
                else:
                    grandfather=['','','','','','','','','','','','','']
            newkey=daught[0]
            capture=[]
            for capt in range(len(A[1])-2):
                if A[1][capt][14]==newkey:
                    capture=A[1][capt][:27]
                    break
            if capture==[]:
                newkey=father[0]
                for capt in range(len(A[1])-2):
                    if A[1][capt][14]==newkey:
                        capture=A[1][capt][:27]
                        break
            if capture==[]:
                newkey=grandfather[0]
                for capt in range(len(A[1])-2):
                    if A[1][capt][14]==newkey:
                        capture=A[1][capt][:27]
                        break
            if grandfather[0]!='':
                keyline.append(emission+decaycode+daught+grandfather+father+capture)
            else:
                keyline.append(emission+decaycode+daught+father+grandfather+capture)
        return keyline
    
    def td(S1,S2):
        TD=S1.datetime-S2.datetime
        return abs(TD.days*86400+TD.seconds)
        
    def listeffy_short(n):
        H = [file[:-4] for file in os.listdir('data/efficiencies') if file[-4:]=='.efs']
        return H
    
    def delete_list(EC,NAA):
        """Delete a calibration entry"""
        extensions=['.efs','_log.txt']
        if EC.get()!='':
            if messagebox.askokcancel('Delete calibration', f'Do you want to delete calibration\n{EC.get()}?'):
                for k in extensions:
                    os.remove('data/efficiencies/'+EC.get()+k)
                EC.set('')
                values=listeffy()
                EC['values']=values
                NAA.calibration = None
            
    def recharge_lists(EC):
        E=listeffy_short(2)
        EC.configure(values=E)
        
    def rename_itemlist(EC,BT,NAA):
        """Rename a calibration entry"""
        def confirm_rename(E,EC,TLRN,NAA):
            listdir=os.listdir('data/efficiencies')
            if E.get()!='' and E.get()!=EC.get() and E.get()+'.eff' not in listdir:
                extensions=['.efs','_log.txt']
                for ex in extensions:
                    os.replace('data/efficiencies/'+EC.get()+ex,'data/efficiencies/'+E.get()+ex)
                recharge_lists(EC)
                EC.set(E.get())
                NAA.calibration.calibration_rename(E.get())
                TLRN.destroy()
            elif E.get()=='':
                print('An empty new calibration name is entered')
            elif E.get()==EC.get():
                print('The new calibration name should be different from the old one')
            elif E.get()+'.eff' in listdir:
                print('The new calibration name entered already exists')
        def return_confirm_rename(ew,E,EC,TLRN,NAA):
            confirm_rename(E,EC,TLRN,NAA)
        if EC.get()!='':
            h,w,a,b=EC.winfo_height(),EC.winfo_width(),EC.winfo_rootx(),EC.winfo_rooty()
            TLRN=Toplevel()
            TLRN.geometry(f'{w}x{h}+{a}+{b+h}')
            TLRN.overrideredirect(True)
            TLRN.resizable(False,False)
            E=Entry(TLRN)
            E.pack(side=LEFT, fill=X, expand=True)
            E.insert(0,EC.get())
            E.focus()            
            BC=Button(TLRN, text='Confirm', width=8, command=lambda E=E,EC=EC,TLRN=TLRN,NAA=NAA : confirm_rename(E,EC,TLRN,NAA)).pack(side=RIGHT)
            ew='<Return>'
            E.bind(ew,lambda ew=ew,E=E,EC=EC,TLRN=TLRN,NAA=NAA : return_confirm_rename(ew,E,EC,TLRN,NAA))
            event="<FocusOut>"
            TLRN.bind(event,lambda event=event,M=TLRN : M.destroy())
            
    def listeffy(f=None):
        H = [file[:-4] for file in os.listdir('data/efficiencies') if file[-4:]=='.efs']
        return H
    
    #def openeffy(w):#deprecated
    #    f=open(w,'r')
    #    r=f.readlines()
    #    f.close()
    #    R=[]
    #    for i in range(len(r)):
    #        R.append(str.split(r[i].replace('\n','')))
    #    return R
        
    def openchannels_drift_values(n):
        """Retrieve b information from file"""
        with open(n,'r') as f:
            rl=[str.split(line.replace('\n','')) for line in f.readlines()]
        rl.pop(0)
        listR=[]
        for k in range(len(rl)):
            listR.append(rl[k][0])
            try:
                rl[k][1],rl[k][2]=float(rl[k][1]),float(rl[k][2])
            except:
                pass
        return listR, rl
    
    def uncertainty_shaper(L,u):
        def selection(Rdint,RS1,RS2,RS3,ND,HD,TD):
            if Rdint.get()==1:
                RS1.select()
                RS2.deselect()
                RS3.deselect()
                ND.configure(state='normal')
                HD.configure(state='readonly')
                TD.configure(state='readonly')
            elif Rdint.get()==2:
                RS1.deselect()
                RS2.select()
                RS3.deselect()
                ND.configure(state='readonly')
                HD.configure(state='normal')
                TD.configure(state='readonly')
            else:
                RS1.deselect()
                RS2.deselect()
                RS3.select()
                ND.configure(state='readonly')
                HD.configure(state='readonly')
                TD.configure(state='normal')
        def effect(u,ND,HD,TD,TUS):
            DD=[None,ND,HD,TD]
            try:
                U=float(DD[int(Rdint.get())].get())
                if Rdint.get()==2:
                    U=np.sqrt(np.power(U,2)/3)
                elif Rdint.get()==3:
                    U=np.sqrt(np.power(U,2)/6)
            except:
                pass
            else:
                u.delete(0,END)
                u.insert(0,U)
                TUS.destroy()
        try:
            U=float(u.get())
        except:
            U=0.0
        TUS=Toplevel()
        TUS.title(L)
        TUS.resizable(False,False)
        L=Label(TUS).pack()
        Rdint=IntVar(TUS)
        F=Frame(TUS)
        L=Label(F, width=1).pack(side=LEFT)
        RS1=Radiobutton(F, text='Gaussian distribution - Standard uncertainty', anchor=W, variable=Rdint, value=1, width=40)
        RS1.pack(side=LEFT)
        ND=Spinbox(F, from_=0, to=1, increment=0.001, width=10)
        ND.delete(0,END)
        ND.insert(0,U)
        ND.pack(side=LEFT)
        F.pack(anchor=W)
        F=Frame(TUS)
        L=Label(F, width=1).pack(side=LEFT)
        RS2=Radiobutton(F, text='Rectangular distribution - Half-width interval', anchor=W, variable=Rdint, value=2, width=40)
        RS2.pack(side=LEFT)
        HD=Spinbox(F, from_=0, to=1, increment=0.001, width=10)
        HD.pack(side=LEFT)
        F.pack(anchor=W)
        F=Frame(TUS)
        L=Label(F, width=1).pack(side=LEFT)
        RS3=Radiobutton(F, text='Triangular distribution - Half-width interval', anchor=W, variable=Rdint, value=3, width=40)
        RS3.pack(side=LEFT)
        TD=Spinbox(F, from_=0, to=1, increment=0.001, width=10)
        TD.pack(side=LEFT)
        L=Label(F, width=1).pack(side=LEFT)
        F.pack(anchor=W)
        RS1.configure(command=lambda Rdint=Rdint,RS1=RS1,RS2=RS2,RS3=RS3,ND=ND,HD=HD,TD=TD : selection(Rdint,RS1,RS2,RS3,ND,HD,TD))
        RS2.configure(command=lambda Rdint=Rdint,RS1=RS1,RS2=RS2,RS3=RS3,ND=ND,HD=HD,TD=TD : selection(Rdint,RS1,RS2,RS3,ND,HD,TD))
        RS3.configure(command=lambda Rdint=Rdint,RS1=RS1,RS2=RS2,RS3=RS3,ND=ND,HD=HD,TD=TD : selection(Rdint,RS1,RS2,RS3,ND,HD,TD))
        TUS.focus()
        RS1.invoke()
        L=Label(TUS).pack()
        BAPY=Button(TUS, text='Apply', width=8, command= lambda u=u,ND=ND,HD=HD,TD=TD,TUS=TUS: effect(u,ND,HD,TD,TUS))
        BAPY.pack()
        L=Label(TUS).pack()
        
    def funcEnergy(x, a, b):
        return a*x+b
    
    def funcFWHM(x, a, b):
        return np.sqrt(a*x+b)
    
    def write_hyperlabfiles(wbname,TLHPL):
        wbname=wbname.cget('text')
        foldername=askdirectory()
        if foldername!='' and foldername!=None and wbname!='':
            wb = xlrd.open_workbook(wbname)
            ss=wb.sheet_names()
            head=['SERIAL#',"PEAK_ID","EMPLOYEE_ID","PEAKEVAL_ID","POS","POSUNC","E","EUNC","AREA","AREAUNC","FWHM","FWHMUNC","CREATIONDATE","PEAKEVALPEAK_ID","HEIGHT","HEIGHTUNC","BACKGROUND","EFF","EFFUNC","EFF.CORR.AREA","EFF.CORR.AREA UNC"]
            try:
                for sht in ss:
                    fs=wb.sheet_by_name(sht)
                    date=xlrd.xldate_as_tuple(fs.cell(0,1).value,0)#tuple(year,month,day,hour,minute,second)
                    real_t=float(fs.cell(1,1).value)
                    live_t=float(fs.cell(2,1).value)
                    n_chs=int(fs.cell(3,1).value)
                    RS=[]
                    xch=[]
                    xE=[]
                    xF=[]
                    r=5
                    while r>0:
                        try:
                            CH=float(fs.cell(r,0).value)
                            EG=float(fs.cell(r,1).value)
                            AR=float(fs.cell(r,2).value)
                            UA=float(fs.cell(r,3).value)
                            FW=fs.cell(r,4).value
                            if FW=='':
                                FW=0
                        except:
                            break
                        else:
                            line=['0','0','0','0',CH,'0',EG,'0',AR,UA,FW,'0','0','0','0','0','0','0','0','0','0']
                            RS.append(line)
                            xch.append(CH)
                            xE.append(EG)
                            xF.append(FW)
                            r+=1
                    Cch=[]
                    r=1
                    while r<n_chs+5:
                        try:
                            Cch.append(int(fs.cell(r,8).value))
                        except:
                            Cch.append(0)
                        r+=1
                    with open(foldername+'/'+sht+'.csv', 'w', newline='') as csvfile:
                        spamwriter = csv.writer(csvfile)
                        spamwriter.writerow(head)
                        spamwriter.writerows(RS)
                    with open(foldername+'/'+sht+'.ASC', 'w') as ASCfile:
                        for cn in range(n_chs):
                            ASCfile.write(f'{Cch[cn]}\n')
                        ASCfile.write(f'#LiveTime={live_t}\n')
                        ASCfile.write(f'#TrueTime={real_t}\n')
                        ASCfile.write(f'#AcqStart={date[0]}-{date[1]}-{date[2]}T{date[3]}:{date[4]}:{date[5]}\n')
                        DT=datetime.datetime(date[0],date[1],date[2],date[3],date[4],date[5])
                        RT=datetime.timedelta(0,real_t)
                        DT=str(DT+RT)
                        Da,Ti=str.split(DT)
                        ASCfile.write(f'#AcqEnd={Da}T{Ti}\n')
                        ASCfile.write('#Comment=\n')
                        ASCfile.write(f'#Title={sht}\n')
                        ASCfile.write('#FileName=\n')
                        ASCfile.write('#LinEnergyCalParams=\n')
                        ASCfile.write('#EnergyCalEquation=\n')
                        ASCfile.write('#FwhmCalParams=\n')
                        ASCfile.write('#FwhmCalEquation=\n')
                        ASCfile.write('#SpePartType[0]=\n')
                TLHPL.destroy()
                print(f'{len(ss)} spectra converted')
            except:
                print('unable to convert the provided file')
        
    def software_information():
        print(f'k0-INRIM\nversion {VERSION} ({VERSION_DATE})\nauthor m.diluzio@inrim.it\n')
    
    #Settings
    settings='data/kimp0-01s.txl'
    database,tolerance_energy,rows,visual,default01,default02,default03,default04,unclimit_calib,unclimit_std,unclimit_sample=initialization(settings)
    unclimit_calib, unclimit_std, unclimit_sample = int(unclimit_calib), int(unclimit_std), int(unclimit_sample)
    A=lineacumulata(openselectedk0database(database))
    #Initialization Analysis Class
    NAA=NAAnalysis()
    NAA.default_utdm,NAA.default_udeltatd,NAA.default_utc,NAA.default_uE=int(default01),float(default02),float(default03),float(default04)
    NAA.info = {'version':VERSION, 'database':database}
    #software information
    software_information()

    #GUI
    
    def mainscreen(M,NAA):
        def settings_modifications(M):
            def save_destroy(P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,M):
                f=open(settings,'w')
                f.write(P1.get())
                f.write('\n')
                f.write(str(float(P2.get())))
                f.write('\n')
                f.write(str(int(float(P3.get()))))
                f.write('\n')
                f.write(str(float(P4.get())))
                f.write('\n')
                f.write(str(int(P5.get())))
                f.write('\n')
                f.write(str(float(P6.get())))
                f.write('\n')
                f.write(str(float(P7.get())))
                f.write('\n')
                f.write(str(float(P8.get())))
                f.write('\n')
                f.write(str(int(P9.get())))
                f.write('\n')
                f.write(str(int(P10.get())))
                f.write('\n')
                f.write(str(int(P11.get())))
                f.close()
                M.destroy()
                print('\n...Restart')
                main()
            
            def change_parameter(V,name,somthing,Scale,Label):
                Label.configure(text=str(Scale.get()))
            
            PRM1,PRM2,PRM3,PRM4,PRM5,PRM6,PRM7,PRM8,PRM9,PRM10,PRM11=initialization(settings)
            TSS=Toplevel()
            TSS.title('Settings')
            TSS.resizable(False,False)
            TSS.focus()
            L=Label(TSS).pack()
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='k0 database', width=28, anchor=W).pack(side=LEFT)
            VVV=os.listdir('data/k0data')
            values=[]
            for kls in VVV:
                if kls[-4:]=='.xls' or kls[-5:]=='.xlsx':
                    values.append(kls)
            databases_omboBCP=ttk.Combobox(F, values=values, state='readonly', width=35)
            databases_omboBCP.pack(side=LEFT)
            databases_omboBCP.set(PRM1)
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W, pady=2)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='ΔE / keV', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_energy_tolerance_S=DoubleVar(TSS)
            energy_tolerance_S = Scale(F, from_=0.1, to=2, orient=HORIZONTAL, resolution=0.1, width=15, length=150, variable=variable_energy_tolerance_S, showvalue=False)
            energy_tolerance_S.pack(side=LEFT)
            energy_tolerance_S.set(PRM2)
            valueL.configure(text=str(PRM2))
            event='w'
            variable_energy_tolerance_S.trace(event, lambda V='',name='',somthing='',Scale=variable_energy_tolerance_S,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='N peak-list', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_rows_S=IntVar(TSS)
            rows_S = Scale(F, from_=10, to=30, orient=HORIZONTAL, resolution=1, width=15, length=150, variable=variable_rows_S, showvalue=False)
            rows_S.pack(side=LEFT)
            rows_S.set(PRM3)
            valueL.configure(text=str(PRM3))
            variable_rows_S.trace(event, lambda V='',name='',somthing='',Scale=variable_rows_S,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='max ur(ai) / 1', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_uncertaintyparam_S=DoubleVar(TSS)
            uncertaintyparam_S = Scale(F, from_=0.0, to=1.20, orient=HORIZONTAL, resolution=0.05, width=15, length=150, variable=variable_uncertaintyparam_S, showvalue=False)
            uncertaintyparam_S.pack(side=LEFT)
            uncertaintyparam_S.set(PRM4)
            valueL.configure(text=str(PRM4))
            variable_uncertaintyparam_S.trace(event, lambda V='',name='',somthing='',Scale=variable_uncertaintyparam_S,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='u(tdm) / s', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_uncertaintydefault1=IntVar(TSS)
            uncertaintyparam_D1 = Scale(F, from_=0, to=200, orient=HORIZONTAL, resolution=1, width=15, length=150, variable=variable_uncertaintydefault1, showvalue=False)
            uncertaintyparam_D1.pack(side=LEFT)
            uncertaintyparam_D1.set(PRM5)
            valueL.configure(text=str(PRM5))
            variable_uncertaintydefault1.trace(event, lambda V='',name='',somthing='',Scale=variable_uncertaintydefault1,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='u(Δtd) / s', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_uncertaintydefault2=DoubleVar(TSS)
            uncertaintyparam_D2 = Scale(F, from_=0.05, to=2.00, orient=HORIZONTAL, resolution=0.05, width=15, length=150, variable=variable_uncertaintydefault2, showvalue=False)
            uncertaintyparam_D2.pack(side=LEFT)
            uncertaintyparam_D2.set(PRM6)
            valueL.configure(text=str(PRM6))
            variable_uncertaintydefault2.trace(event, lambda V='',name='',somthing='',Scale=variable_uncertaintydefault2,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='u(tc) and u(tl) / s', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_uncertaintydefault3=DoubleVar(TSS)
            uncertaintyparam_D3 = Scale(F, from_=0.01, to=1.00, orient=HORIZONTAL, resolution=0.01, width=15, length=150, variable=variable_uncertaintydefault3, showvalue=False)
            uncertaintyparam_D3.pack(side=LEFT)
            uncertaintyparam_D3.set(PRM7)
            valueL.configure(text=str(PRM7))
            variable_uncertaintydefault3.trace(event, lambda V='',name='',somthing='',Scale=variable_uncertaintydefault3,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='u(Ep) / keV', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_uncertaintydefault4=DoubleVar(TSS)
            uncertaintyparam_D4 = Scale(F, from_=0.01, to=1.00, orient=HORIZONTAL, resolution=0.01, width=15, length=150, variable=variable_uncertaintydefault4, showvalue=False)
            uncertaintyparam_D4.pack(side=LEFT)
            uncertaintyparam_D4.set(PRM8)
            valueL.configure(text=str(PRM8))
            variable_uncertaintydefault4.trace(event, lambda V='',name='',somthing='',Scale=variable_uncertaintydefault4,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='Calib peaks max. unc. / %', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_unclimit_calib=IntVar(TSS)
            unclimit_calib = Scale(F, from_=3, to=20, orient=HORIZONTAL, resolution=1, width=15, length=150, variable=variable_unclimit_calib, showvalue=False)
            unclimit_calib.pack(side=LEFT)
            unclimit_calib.set(PRM9)
            valueL.configure(text=str(PRM9))
            variable_unclimit_calib.trace(event, lambda V='',name='',somthing='',Scale=variable_unclimit_calib,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='Std peaks max. unc. / %', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_unclimit_std=IntVar(TSS)
            unclimit_std = Scale(F, from_=10, to=50, orient=HORIZONTAL, resolution=1, width=15, length=150, variable=variable_unclimit_std, showvalue=False)
            unclimit_std.pack(side=LEFT)
            unclimit_std.set(PRM10)
            valueL.configure(text=str(PRM10))
            variable_unclimit_std.trace(event, lambda V='',name='',somthing='',Scale=variable_unclimit_std,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TSS)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='Sample peaks max. unc. / %', width=24, anchor=W).pack(side=LEFT)
            valueL=Label(F, text='', width=3, anchor=W)
            valueL.pack(side=LEFT)
            variable_unclimit_sample=IntVar(TSS)
            unclimit_sample = Scale(F, from_=10, to=50, orient=HORIZONTAL, resolution=1, width=15, length=150, variable=variable_unclimit_sample, showvalue=False)
            unclimit_sample.pack(side=LEFT)
            unclimit_sample.set(PRM11)
            valueL.configure(text=str(PRM11))
            variable_unclimit_sample.trace(event, lambda V='',name='',somthing='',Scale=variable_unclimit_sample,Label=valueL : change_parameter(V,name,somthing,Scale,Label))
            L=Label(F, text='', width=1).pack(side=LEFT)
            F.pack(anchor=W)
            
            L=Label(TSS).pack()
            B=Button(TSS, text='Confirm and close', command=lambda P1=databases_omboBCP,P2=variable_energy_tolerance_S,P3=variable_rows_S,P4=variable_uncertaintyparam_S,P5=variable_uncertaintydefault1,P6=variable_uncertaintydefault2,P7=variable_uncertaintydefault3,P8=variable_uncertaintydefault4,P9=variable_unclimit_calib,P10=variable_unclimit_std,P11=variable_unclimit_sample,M=M : save_destroy(P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,M)).pack()
            L=Label(TSS).pack()
        
        def create_HyperLabmanually():
            def selectionLP(LP):
                types=[('Excel file','.xls'),('Excel file','.xlsx')]
                filename=askopenfilename(filetypes=types)
                LP.configure(text=filename)
                LP.focus()
            TLHPL=Toplevel()
            TLHPL.title('Select and convert')
            TLHPL.resizable(False,False)
            L=Label(TLHPL).pack()
            F=Frame(TLHPL)
            L=Label(F, width=1).pack(side=LEFT)
            BL=Button(F, text='Select', width=8)
            BL.pack(side=LEFT)
            L=Label(F, width=1).pack(side=LEFT)
            LPfile=Label(F, text='', width=60, anchor=E)
            LPfile.pack(side=LEFT)
            BL.configure(command=lambda LP=LPfile : selectionLP(LP))
            L=Label(F, width=1).pack(side=LEFT)
            F.pack(anchor=W)
            L=Label(TLHPL).pack()
            F=Frame(TLHPL)
            L=Label(F, width=1).pack(side=LEFT)
            BCv=Button(F, text='Convert', width=8, command=lambda wbname=LPfile,TLHPL=TLHPL : write_hyperlabfiles(wbname,TLHPL))
            BCv.pack(side=LEFT)
            F.pack(anchor=W)
            L=Label(TLHPL).pack()
            TLHPL.focus()
        
        def openpeaklistandspectrum(BT,NAA,LBB,LPKS,LDT):
            if BT.cget('text')!='Sample':
                nomeHyperLabfile,startcounting,realT,liveT,peak_list,spectrum_counts,linE,linW=searchforhypelabfile(unclimit_std)
                if realT!=None:
                    S=Spectrum(BT.cget('text'),startcounting,realT,liveT,peak_list,spectrum_counts,nomeHyperLabfile)
                    if S.define()=='Background':
                        NAA.set_backgroungspectrum(S)
                    else:
                        NAA.set_comparatorspectrum(S)
                        NAA.relative_method=[]
                        NAA.standard_comparator=[None,None]
                    shortnm=str.split(nomeHyperLabfile,'/')
                    LBB.configure(text=shortnm[-1])
                    LPKS.configure(text=str(len(S.peak_list)))
                    LDT.configure(text=S.readable_datetime())
                    if S.define()!='Sample':
                        LBB.configure(text=shortnm[-1])
                        LPKS.configure(text=str(len(S.peak_list)))
                        LDT.configure(text=S.readable_datetime())
            else:
                AAA=searchforhypelabmultiplefiles(unclimit_sample)
                for item in AAA:
                    if item[2]!=None:
                        S=Spectrum(BT.cget('text'),item[1],item[2],item[3],item[4],item[5],item[0])
                        NAA.set_samplespectrum(S)
                        shortnm=str.split(item[0],'/')
                try:
                    if len(NAA.sample)>1:
                        LBB.configure(text=str(len(NAA.sample))+' spectra')
                        LPKS.configure(text='-')
                        LDT.configure(text='-')
                    else:
                        LBB.configure(text=shortnm[-1])
                        LPKS.configure(text=str(len(NAA.sample[0].peak_list)))
                        LDT.configure(text=NAA.sample[0].readable_datetime())
                except TypeError:
                    pass
                except UnboundLocalError:
                    pass
                
        def irradiation_info(BIR,NAA,LCH,LF,LALF,LIDT,LITM):
            def automatic_f_a(event,CB,F,UF,A,UA,CHNL):
                for t in CHNL:
                    if t[0]==CB.get():
                        try:
                            F.delete(0,END)
                            F.insert(0,t[1])
                            UF.delete(0,END)
                            UF.insert(0,t[2])
                            A.delete(0,END)
                            A.insert(0,t[3])
                            UA.delete(0,END)
                            UA.insert(0,t[4])
                            break
                        except:
                            pass
                        
            def automatic_irradiation_data(event,CB,DS,MS,YS,HS,MinS,SS,ITS,UTS,CHNL,CBB,F,UF,A,UA):
                for t in CHNL:
                    if t[0]==CB.get():
                        try:
                            DS.delete(0,END)
                            DS.insert(0,t[1])
                            MS.delete(0,END)
                            MS.insert(0,t[2])
                            YS.delete(0,END)
                            YS.insert(0,t[3])
                            HS.delete(0,END)
                            HS.insert(0,t[4])
                            MinS.delete(0,END)
                            MinS.insert(0,t[5])
                            SS.delete(0,END)
                            SS.insert(0,t[6])
                            ITS.delete(0,END)
                            ITS.insert(0,t[7])
                            UTS.delete(0,END)
                            UTS.insert(0,t[8])
                            CBB.set(t[9])
                            F.delete(0,END)
                            F.insert(0,t[10])
                            UF.delete(0,END)
                            UF.insert(0,t[11])
                            A.delete(0,END)
                            A.insert(0,t[12])
                            UA.delete(0,END)
                            UA.insert(0,t[13])
                            break
                        except:
                            pass
                        
            def save_update_channels(CB,F,UF,A,UA,CHNL):
                try:
                    float(F.get())
                    float(UF.get())
                    float(A.get())
                    float(UA.get())
                except:
                    pass
                else:
                    if float(F.get())>0 and CB.get()!='':
                        index=None
                        CBG=CB.get().replace(' ','_')
                        for th in range(len(CHNL)):
                            if CBG==CHNL[th][0]:
                                index=th
                                break
                        if index==None:
                            CHNL.append([CBG,float(F.get()),float(UF.get()),float(A.get()),float(UA.get())])
                        else:
                            CHNL[index]=[CBG,float(F.get()),float(UF.get()),float(A.get()),float(UA.get())]
                        listCH=[]
                        f=open('data/channels/chn.txt','w')
                        f.write('#flux parameters{this line is for comments and is not considered} #name_of_facility(without spaces) f uf alpha ualpha')
                        for th in CHNL:
                            listCH.append(th[0])
                            f.write('\n')
                            f.write(th[0])
                            f.write(' ')
                            f.write(str(th[1]))
                            f.write(' ')
                            f.write(str(th[2]))
                            f.write(' ')
                            f.write(str(th[3]))
                            f.write(' ')
                            f.write(str(th[4]))
                        f.close()
                        CB['values']=listCH
                        CB.set(CBG)
                        
            def delete_channel(CB,F,UF,A,UA,CHNL):
                if CB.get()!='':
                    CBG=CB.get().replace(' ','_')
                    for th in range(len(CHNL)):
                        if CBG==CHNL[th][0]:
                            CHNL.pop(th)
                            break
                    listCH=[]
                    f=open('data/channels/chn.txt','w')
                    f.write('#flux parameters{this line is for comments and is not considered} #name_of_facility(without spaces) f uf alpha ualpha')
                    for th in CHNL:
                        listCH.append(th[0])
                        f.write('\n')
                        f.write(th[0])
                        f.write(' ')
                        f.write(str(th[1]))
                        f.write(' ')
                        f.write(str(th[2]))
                        f.write(' ')
                        f.write(str(th[3]))
                        f.write(' ')
                        f.write(str(th[4]))
                    f.close()
                    CB['values']=listCH
                    CB.set('')
                    F.delete(0,END)
                    F.insert(END,'0.0')
                    UF.delete(0,END)
                    UF.insert(END,'0.0')
                    A.delete(0,END)
                    A.insert(END,'0.0000')
                    UA.delete(0,END)
                    UA.insert(END,'0.0000')
        
            def openchannels(n):
                """Retrieve f and α information from file"""
                f=open(n,'r')
                rl=f.readlines()
                f.close()
                rl.pop(0)
                r=[]
                for i in rl:
                    r.append(i.replace('\n',''))
                R=[]
                for i in r:
                    R.append(str.split(i))
                listR=[]
                for k in range(len(R)):
                    listR.append(R[k][0])
                    try:
                        R[k][1],R[k][2],R[k][3],R[k][4]=float(R[k][1]),float(R[k][2]),float(R[k][3]),float(R[k][4])
                    except:
                        pass
                return R,listR
            
            def openchannelsI(n):
                """Retrieve irradiation data information from file"""
                f=open(n,'r')
                rl=f.readlines()
                f.close()
                rl.pop(0)
                r=[]
                for i in rl:
                    r.append(i.replace('\n',''))
                R=[]
                for i in r:
                    R.append(str.split(i))
                listR=[]
                for k in range(len(R)):
                    listR.append(R[k][0])
                    try:
                        R[k][1],R[k][2],R[k][3],R[k][4],R[k][5],R[k][6],R[k][7],R[k][8],R[k][10],R[k][11],R[k][12],R[k][13]=float(R[k][1]),float(R[k][2]),float(R[k][3]),float(R[k][4]),float(R[k][5]),float(R[k][6]),float(R[k][7]),float(R[k][8],float(R[k][10]),float(R[k][11]),float(R[k][12]),float(R[k][13]))
                    except:
                        pass
                return R,listR
            
            def delete_irradiation_code(ECC,IRRD,listIRR):
                if ECC.get()!='':
                    index=None
                    try:
                        for i in range(len(IRRD)):
                            if ECC.get()==IRRD[i][0]:
                                index=i
                                break
                    except:
                        index=None
                    if index!=None:
                        IRRD.pop(index)
                        listIRR.pop(index)
                        ECC['values']=listIRR
                        ECC.set('')
                        f=open('data/irradiations/irr.txt','w')
                        f.write('#Irradiation data {This line is for comments and is ignored}')
                        for t in IRRD:
                            f.write('\n')
                            f.write(t[0])
                            f.write(' ')
                            f.write(str(t[1]))
                            f.write(' ')
                            f.write(str(t[2]))
                            f.write(' ')
                            f.write(str(t[3]))
                            f.write(' ')
                            f.write(str(t[4]))
                            f.write(' ')
                            f.write(str(t[5]))
                            f.write(' ')
                            f.write(str(t[6]))
                            f.write(' ')
                            f.write(str(t[7]))
                            f.write(' ')
                            f.write(str(t[8]))
                            f.write(' ')
                            f.write(t[9])
                            f.write(' ')
                            f.write(str(t[10]))
                            f.write(' ')
                            f.write(str(t[11]))
                            f.write(' ')
                            f.write(str(t[12]))
                            f.write(' ')
                            f.write(str(t[13]))
                        f.close()
            
            def apply(ECC,CHomboB,Fspinbox,UFspinbox,Aspinbox,UAspinbox,Dayspinbox,Monthspinbox,Yearspinbox,Hourspinbox,Minutespinbox,Secondspinbox,Itimespinbox,UItimespinbox,NAA,LCH,LF,LALF,LIDT,LITM,TL,IRRD):
                try:
                    float(Fspinbox.get())
                    float(UFspinbox.get())
                    float(Aspinbox.get())
                    float(UAspinbox.get())
                    int(Itimespinbox.get())
                    float(UItimespinbox.get())
                    dt=datetime.datetime(int(Yearspinbox.get()),int(Monthspinbox.get()),int(Dayspinbox.get()),int(Hourspinbox.get()),int(Minutespinbox.get()),int(Secondspinbox.get()))
                except:
                    print('Invalid data entered\na) f,a,u(f),u(a) and u(ti) should be of floating point type\nb) ti, should be of integer type\nc) set f and ti different from 0')
                else:
                    if float(Fspinbox.get())>0 and int(Itimespinbox.get())>0 and CHomboB.get()!='':
                        IR=Irradiation(dt,int(Itimespinbox.get()),float(UItimespinbox.get()),float(Fspinbox.get()),float(UFspinbox.get()),float(Aspinbox.get()),float(UAspinbox.get()),CHomboB.get(),ECC.get())
                        NAA.set_irradiation(IR)
                        LCH.configure(text=NAA.irradiation.channel)
                        LF.configure(text=str(NAA.irradiation.f))
                        LALF.configure(text=str(NAA.irradiation.a))
                        LIDT.configure(text=NAA.irradiation.readable_datetime())
                        LITM.configure(text=f'{NAA.irradiation.time}')
                        if ECC.get()!='':
                            ECCC=ECC.get().replace(' ','_')
                        else:
                            ECCC='_'
                        CHombo=CHomboB.get().replace(' ','_')
                        index=None
                        for th in range(len(IRRD)):
                            if ECCC==IRRD[th][0]:
                                index=th
                        if index==None:
                            IRRD.append([ECCC,int(Dayspinbox.get()),int(Monthspinbox.get()),int(Yearspinbox.get()),int(Hourspinbox.get()),int(Minutespinbox.get()),int(Secondspinbox.get()),int(Itimespinbox.get()),float(UItimespinbox.get()),CHombo,float(Fspinbox.get()),float(UFspinbox.get()),float(Aspinbox.get()),float(UAspinbox.get())])
                        else:
                            IRRD[index]=[ECCC,int(Dayspinbox.get()),int(Monthspinbox.get()),int(Yearspinbox.get()),int(Hourspinbox.get()),int(Minutespinbox.get()),int(Secondspinbox.get()),int(Itimespinbox.get()),float(UItimespinbox.get()),CHombo,float(Fspinbox.get()),float(UFspinbox.get()),float(Aspinbox.get()),float(UAspinbox.get())]
                        f=open('data/irradiations/irr.txt','w')
                        f.write('#Irradiation data {This line is for comments and is ignored}')
                        for t in IRRD:
                            f.write('\n')
                            f.write(t[0])
                            f.write(' ')
                            f.write(str(t[1]))
                            f.write(' ')
                            f.write(str(t[2]))
                            f.write(' ')
                            f.write(str(t[3]))
                            f.write(' ')
                            f.write(str(t[4]))
                            f.write(' ')
                            f.write(str(t[5]))
                            f.write(' ')
                            f.write(str(t[6]))
                            f.write(' ')
                            f.write(str(t[7]))
                            f.write(' ')
                            f.write(str(t[8]))
                            f.write(' ')
                            f.write(t[9])
                            f.write(' ')
                            f.write(str(t[10]))
                            f.write(' ')
                            f.write(str(t[11]))
                            f.write(' ')
                            f.write(str(t[12]))
                            f.write(' ')
                            f.write(str(t[13]))
                        f.close()
                        TL.destroy()
                    else:
                        print('Invalid data entered\na) f and ti should be greater than 0\nb) irr. channel name cannot be empty')
                        
            def f_alpha_evaluations(root,channel_box,f_box,uf_box,a_box,ua_box,date,time,tirr):
                def shrinked_line(aline):
                    allowedtypes = ['I','IIA']
                    def emission(nucl,AA,state,energy):
                        def statetype(state):
                            if state != 1.0:
                                return 'm'
                            else:
                                return ''
                        return f'{nucl}-{int(AA)}{statetype(state)} {energy}'
                    def lambdatime(timezzi,unit):
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
                        return [emission(aline[2],aline[3],aline[4],aline[5]),aline[1],aline[5],aline[7],aline[8],aline[75],aline[76],aline[77],aline[78],lambdatime(aline[31],aline[32]),lambdatime(aline[31+13],aline[32+13]),lambdatime(aline[31+26],aline[32+26]),aline[22]] #change the last two lambdatime!
                    else:
                        return None
                        
                #creation sub database for f and alpha evaluation
                flux_monitors_entries = ['Au','Zr']
                sub_A = [shrinked_line(aline) for aline in A if aline[1] in flux_monitors_entries and shrinked_line(aline) is not None]
                
                def check_label(label,extended=False):
                    for i in sub_A:
                        if i[0] == label:
                            return (i[1], i[5], i[7])
                    return ('','','')
                    
                def update_date(box,LM,LQ,LE):
                    resp = check_label(box.get())
                    LM.configure(text=resp[0])
                    LQ.configure(text=resp[1])
                    LE.configure(text=resp[2])
                    
                def fa_add_spectra(SPCIn,SPClist,unclimit,setforall):
                    spectra_names=searchforhypelabmultiplefiles(unclimit,setforall)
                    if spectra_names!=None:
                        for tg in spectra_names:
                            if tg[2]!=None:
                                SPT=Spectrum('f_and_alpha',tg[1],tg[2],tg[3],tg[4],tg[5],tg[0])
                                SPCIn.append(SPT)
                                SPClist.insert(END,SPT.filename())
                    SPClist.focus()
                    
                def fa_clear_spectra(SPCIn,SPClist):
                    g=len(SPCIn)
                    for _ in range(g):
                        SPCIn.pop(0)
                    SPClist.delete(0,END)
                    
                def harvest_monitor(sub_A,label,M,correct_harvesting,irrtime,endirr,mass,umass,coi,ucoi,gs,ugs,ge,uge,strategy='low. unc.'):
                    #retrieve target information
                    targetinfo = None
                    lis = None
                    for i in sub_A:
                        if i[0] == label:
                            targetinfo = i
                    if targetinfo is None:
                        print('Target not found')
                        correct_harvesting = False
                    #retrieve emissions
                    else:
                        best_match = None
                        for i in M.spectra:
                            for line in i.peak_list:
                                if targetinfo[2] - float(tolerance_energy) < float(line[6]) < targetinfo[2] + float(tolerance_energy):
                                    if best_match is None:
                                        if strategy == 'low. unc.':
                                            best_match = float(line[9]) / float(line[8])
                                        if strategy == 'shor. acq.' or strategy == 'lon. acq.':
                                            best_match = i.live_time
                                        if strategy == 'earliest' or strategy == 'latest':
                                            best_match = i.datetime
                                        fa_td = i.datetime - endirr
                                        fa_td = fa_td.days * 86400 + fa_td.seconds
                                        lis = [irrtime,i.real_time,i.live_time,fa_td,float(line[8]),float(line[9]),coi,ucoi,mass,umass,gs,ugs,ge,uge,i.filename()]
                                    else:
                                        if strategy == 'low. unc.':
                                            if float(line[9]) / float(line[8]) < best_match:
                                                best_match = float(line[9]) / float(line[8])
                                                fa_td = i.datetime - endirr
                                                fa_td = fa_td.days * 86400 + fa_td.seconds
                                                lis = [irrtime,i.real_time,i.live_time,fa_td,float(line[8]),float(line[9]),coi,ucoi,mass,umass,gs,ugs,ge,uge,i.filename()]
                                        if strategy == 'shor. acq.':
                                            if i.live_time < best_match:
                                                best_match = i.live_time
                                                fa_td = i.datetime - endirr
                                                fa_td = fa_td.days * 86400 + fa_td.seconds
                                                lis = [irrtime,i.real_time,i.live_time,fa_td,float(line[8]),float(line[9]),coi,ucoi,mass,umass,gs,ugs,ge,uge,i.filename()]
                                        if strategy == 'lon. acq.':
                                            if i.live_time > best_match:
                                                best_match = i.live_time
                                                fa_td = i.datetime - endirr
                                                fa_td = fa_td.days * 86400 + fa_td.seconds
                                                lis = [irrtime,i.real_time,i.live_time,fa_td,float(line[8]),float(line[9]),coi,ucoi,mass,umass,gs,ugs,ge,uge,i.filename()]
                                        if strategy == 'earliest':
                                            if i.datetime < best_match:
                                                best_match = i.datetime
                                                fa_td = i.datetime - endirr
                                                fa_td = fa_td.days * 86400 + fa_td.seconds
                                                lis = [irrtime,i.real_time,i.live_time,fa_td,float(line[8]),float(line[9]),coi,ucoi,mass,umass,gs,ugs,ge,uge,i.filename()]
                                        if strategy == 'latest':
                                            if i.datetime > best_match:
                                                best_match = i.datetime
                                                fa_td = i.datetime - endirr
                                                fa_td = fa_td.days * 86400 + fa_td.seconds
                                                lis = [irrtime,i.real_time,i.live_time,fa_td,float(line[8]),float(line[9]),coi,ucoi,mass,umass,gs,ugs,ge,uge,i.filename()]
                    if targetinfo is not None and lis is not None:
                        return targetinfo + lis, correct_harvesting
                    else:
                        return None, False
                        
                def do_the_fa_job(monitor_1,monitor_2,monitor_3,calibration):
                    def e_polynomial_model(parameters,energy):
                        """6-terms polynomial efficiency fit"""
                        energy = energy / 1000
                        return np.exp(parameters[0]*energy + parameters[1] + parameters[2]*np.power(energy,-1) + parameters[3]*np.power(energy,-2) + parameters[4]*np.power(energy,-3) + parameters[5]*np.power(energy,-4))
                    
                    def the_uncertainty_job(value,unc,default=0.02):
                        try:
                            return float(unc) / 100 * value
                        except:
                            return default * value
                    
                    def get_specific(line):
                        """Calculate specific count rate at saturation"""
                        if line[12] == 'IIA':
                            _l2, _l3, _ti, _tr, _tl, _td, _np, _unp, _coi, _ucoi, _m, _um = line[9], line[10], line[13], line[14], line[15], line[16], line[17], line[18], line[19], line[20], line[21], line[22]
                            Asp = (_np * _tr * (_l3 - _l2)) / (_tl * _coi * _m * (_l3/_l2*(1 - np.exp(-_l2 * _ti)) * np.exp(-_l2 * _td) * (1 - np.exp(-_l2 * _tr)) - _l2/_l3*(1 - np.exp(-_l3 * _ti)) * np.exp(-_l3 * _td) * (1 - np.exp(-_l3 * _tr))))
                        else:
                            _l, _ti, _tr, _tl, _td, _np, _unp, _coi, _ucoi, _m, _um = line[9], line[13], line[14], line[15], line[16], line[17], line[18], line[19], line[20], line[21], line[22]
                            Asp = (_np * _l * _tr) / (_tl * (1 - np.exp(-_l * _ti)) * np.exp(-_l * _td) * (1 - np.exp(-_l * _tr)) * _coi * _m)
                        unc = Asp * np.sqrt(np.power(_unp / _np,2) + np.power(_um / _m,2) + np.power(_ucoi / _coi,2))
                        return Asp, unc
                    
                    def func_a(x):
                        """Function to solve for alpha"""
                        return ((1 / ((_Asp_1*_k0_2*_e2)/(_Asp_2*_k0_1*_e1) - 1)) - (1 / ((_Asp_1*_k0_3*_e3)/(_Asp_3*_k0_1*_e1) - 1)))*_Ge1*((_q01-0.429)/_Er1**x + 0.429/((2*x + 1)*0.55**x)) - (1 / (1 - (_Asp_2*_k0_1*_e1)/(_Asp_1*_k0_2*_e2)))*_Ge2*((_q02-0.429)/_Er2**x + 0.429/((2*x + 1)*0.55**x)) + (1 / (1 - (_Asp_3*_k0_1*_e1)/(_Asp_1*_k0_3*_e3)))*_Ge3*((_q03-0.429)/_Er3**x + 0.429/((2*x + 1)*0.55**x))
                    
                    def func_f(Asp1,k01,e1,Ge1,q01,Er1,Asp2,k02,e2,Ge2,q02,Er2,Gs,a):
                        """Function that returns f"""
                        return ((k01*e1)/(k02*e2)*Ge1*((q01-0.429)/Er1**a + 0.429/((2*a + 1)*0.55**a)) - Asp1/Asp2*Ge2*((q02-0.429)/Er2**a + 0.429/((2*a + 1)*0.55**a))) / (Gs*(Asp1/Asp2 - (k01*e1)/(k02*e2)))
                        
                    def func_thermal_f(Asp1,e1,Ge1,q01,Er1,Gs,f,a,MolarM,Theta,Gamma,Sg0):
                        """Function that returns thermal flux"""
                        NA = 6.02214086E23
                        return (Asp1*MolarM)/(Theta*Gamma*e1*NA*Sg0*(Gs+Ge1/f*((q01-0.429)/Er1**a + 0.429/((2*a + 1)*0.55**a))))
                        
                    def func_epithermal_f(Asp1,e1,Ge1,q01,Er1,Gs,f,a,MolarM,Theta,Gamma,Sg0):
                        """Function that returns thermal flux"""
                        NA = 6.02214086E23
                        return (Asp1*MolarM)/(Theta*Gamma*e1*NA*Sg0*(Gs*f+Ge1*((q01-0.429)/Er1**a + 0.429/((2*a + 1)*0.55**a))))
                    
                    f, uf, alpha, ualpha = 0.0,0.0,0.0,0.0
                    textual = []
                    #test parameter!!!
                    #xtol = 1E-3
                    Asp_1, uAsp_1 = get_specific(monitor_1)
                    Asp_2, uAsp_2 = get_specific(monitor_2)
                    Asp_3, uAsp_3 = get_specific(monitor_3)
                    k0_1, uk0_1, k0_2, uk0_2, k0_3, uk0_3 = monitor_1[3], the_uncertainty_job(monitor_1[3],monitor_1[4]), monitor_2[3], the_uncertainty_job(monitor_2[3],monitor_2[4]), monitor_3[3], the_uncertainty_job(monitor_3[3],monitor_3[4])
                    q01, uq01, q02, uq02, q03, uq03 = monitor_1[5], the_uncertainty_job(monitor_1[5],monitor_1[6],0.2), monitor_2[5], the_uncertainty_job(monitor_2[5],monitor_2[6],0.2), monitor_3[5], the_uncertainty_job(monitor_3[5],monitor_3[6],0.2)
                    Er1, uEr1, Er2, uEr2, Er3, uEr3 = monitor_1[7], the_uncertainty_job(monitor_1[7],monitor_1[8],0.5), monitor_2[7], the_uncertainty_job(monitor_2[7],monitor_2[8],0.5), monitor_3[7], the_uncertainty_job(monitor_3[7],monitor_3[8],0.5)
                    Ge1, uGe1, Ge2, uGe2, Ge3, uGe3 = monitor_1[25], monitor_1[26], monitor_2[25], monitor_2[26], monitor_3[25], monitor_3[26]
                    e1, e2, e3 = calibration.efficiency_fit(monitor_1[2]), calibration.efficiency_fit(monitor_2[2]), calibration.efficiency_fit(monitor_3[2])
                    _Asp_1, _Asp_2, _Asp_3, _k0_1, _k0_2, _k0_3, _e1, _e2, _e3, _q01, _q02, _q03, _Er1, _Er2, _Er3, _Ge1, _Ge2, _Ge3 = Asp_1, Asp_2, Asp_3, k0_1, k0_2, k0_3, e1, e2, e3, q01, q02, q03, Er1, Er2, Er3, Ge1, Ge2, Ge3
                    sol = fsolve(func_a, 0)
                    alpha = float(sol) #alpha is calculated
                    a1, a2, a3, a4, a5, a6 = calibration.efficiency_parameters
                    ua1, ua2, ua3, ua4, ua5, ua6 = np.sqrt(np.diag(calibration.efficiency_cov))
                    _a1, _a2, _a3, _a4, _a5, _a6 = a1, a2, a3, a4, a5, a6
                    original_values = [Asp_1, Asp_2, Asp_3, k0_1, k0_2, k0_3, q01, q02, q03, Er1, Er2, Er3, Ge1, Ge2, Ge3, a1, a2, a3, a4, a5, a6]
                    comput_values = [_Asp_1, _Asp_2, _Asp_3, _k0_1, _k0_2, _k0_3, _q01, _q02, _q03, _Er1, _Er2, _Er3, _Ge1, _Ge2, _Ge3, _a1, _a2, _a3, _a4, _a5, _a6]
                    uncertainties = [uAsp_1, uAsp_2, uAsp_3, uk0_1, uk0_2, uk0_3, uq01, uq02, uq03, uEr1, uEr2, uEr3, uGe1, uGe2, uGe3, ua1, ua2, ua3, ua4, ua5, ua6]
                    res = []
                    for idx in range(len(original_values)):
                        comput_values[idx] = original_values[idx] + uncertainties[idx]
                        _Asp_1, _Asp_2, _Asp_3, _k0_1, _k0_2, _k0_3, _q01, _q02, _q03, _Er1, _Er2, _Er3, _Ge1, _Ge2, _Ge3, _a1, _a2, _a3, _a4, _a5, _a6 = comput_values
                        _e1, _e2, _e3 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_1[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_2[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_3[2])
                        sol = fsolve(func_a, 0)
                        solplus = (float(sol) - alpha) / (uncertainties[idx] + 1E-12)
                        comput_values[idx] = original_values[idx] - uncertainties[idx]
                        _Asp_1, _Asp_2, _Asp_3, _k0_1, _k0_2, _k0_3, _q01, _q02, _q03, _Er1, _Er2, _Er3, _Ge1, _Ge2, _Ge3, _a1, _a2, _a3, _a4, _a5, _a6 = comput_values
                        _e1, _e2, _e3 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_1[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_2[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_3[2])
                        sol = fsolve(func_a, 0)
                        solminus = (float(sol) - alpha) / -(uncertainties[idx] + 1E-12)
                        comput_values[idx] = original_values[idx]
                        res.append((solplus+solminus)/2)
                    res = np.array(res)
                    uncertainties = np.array(uncertainties)
                    uncertainties = np.power(uncertainties,2)
                    unc_cov_matrix = np.diag(uncertainties)
                    unc_cov_matrix[-len(calibration.efficiency_cov):,-len(calibration.efficiency_cov):] = calibration.efficiency_cov
                    ualpha = np.sqrt((res.T@unc_cov_matrix) @ res)
                    limit = 0.15
                    warning1, warning2 = '',''
                    if not -limit < alpha < limit:
                        warning1 = f'warning: calculated α value is questionable since lies outside the range +-{limit}\n'
                    if np.abs(ualpha / alpha) > 0.8:
                        warning2 = 'warning: excessive evaluated uncertainty for α\n'
                    indexes = []
                    for row in range(len(unc_cov_matrix)):
                        count = 0
                        for colu in range(len(unc_cov_matrix)):
                            count += res[row] * res[colu] * unc_cov_matrix[row,colu]
                        indexes.append(count)
                    indexes = np.array(indexes[:-6]+[np.sum(indexes[-6:])])
                    description = ['Specific count rate of monitor 1','Specific count rate of monitor 2','Specific count rate of monitor 3','k0 factor of monitor 1','k0 factor of monitor 2','k0 factor of monitor 3','Resonance integral on thermal cross section value of monitor 1','Resonance integral on thermal cross section value of monitor 2','Resonance integral on thermal cross section value of monitor 3','Effective resonance value of monitor 1','Effective resonance value of monitor 2','Effective resonance value of monitor 3','Epithermal self shielding value of monitor 1','Epithermal self shielding value of monitor 2','Epithermal self shielding value of monitor 3','Efficiency evaluation']
                    indexes = [(idx_value / indexes.sum(),tag) for idx_value,tag in zip(indexes,description)]
                    indexes.sort(key= lambda x : x[0], reverse=True)
                    text_major_contributors = [f'{format(100*line[0],".1f").rjust(5, " ")} % - {line[1]}' for line in indexes[:5]]
                    textual.append(f'\nα value found by iteratively solving the α implicit equation\n{"".ljust(4)}{"value".ljust(10)}{"u (k=1)".ljust(9)}rel. u\n{"α".ljust(4)}{format(alpha,".4f").ljust(10)}{format(ualpha,".4f").ljust(9)}({np.abs(100 * ualpha / alpha):.1f} %)\n{warning1}{warning2}\nList of 5 major contributors to the combined uncertainty of α evaluation:\n'+'\n'.join(text_major_contributors)+'\n')
                    f = func_f(Asp_2,k0_2,e2,Ge2,q02,Er2,Asp_3,k0_3,e3,Ge3,q03,Er3,monitor_2[23],alpha)
                    original_values = [Asp_2,k0_2,Ge2,q02,Er2,Asp_3,k0_3,Ge3,q03,Er3,monitor_2[23],alpha,a1, a2, a3, a4, a5, a6]
                    comput_values = [Asp_2,k0_2,Ge2,q02,Er2,Asp_3,k0_3,Ge3,q03,Er3,monitor_2[23],alpha,a1, a2, a3, a4, a5, a6]
                    uncertainties = [uAsp_2,uk0_2,uGe2,uq02,uEr2,uAsp_3,uk0_3,uGe3,uq03,uEr3,monitor_2[24],ualpha,ua1, ua2, ua3, ua4, ua5, ua6]
                    res = []
                    for idx in range(len(original_values)):
                        comput_values[idx] = original_values[idx] + uncertainties[idx]
                        _Asp_1,_k0_1,_Ge1,_q01,_Er1,_Asp_2,_k0_2,_Ge2,_q02,_Er2,_Gs,_alpha,_a1,_a2,_a3,_a4,_a5,_a6 = comput_values
                        _e1, _e2 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_2[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_3[2])
                        solplus = (func_f(_Asp_1,_k0_1,_e1,_Ge1,_q01,_Er1,_Asp_2,_k0_2,_e2,_Ge2,_q02,_Er2,_Gs,_alpha) - f) / (uncertainties[idx] + 1E-12)
                        comput_values[idx] = original_values[idx] - uncertainties[idx]
                        _Asp_1,_k0_1,_Ge1,_q01,_Er1,_Asp_2,_k0_2,_Ge2,_q02,_Er2,_Gs,_alpha,_a1,_a2,_a3,_a4,_a5,_a6 = comput_values
                        _e1, _e2 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_2[2]), e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],monitor_3[2])
                        solminus = (func_f(_Asp_1,_k0_1,_e1,_Ge1,_q01,_Er1,_Asp_2,_k0_2,_e2,_Ge2,_q02,_Er2,_Gs,_alpha) - f) / -(uncertainties[idx] + 1E-12)
                        comput_values[idx] = original_values[idx]
                        res.append((solplus+solminus)/2)
                    res = np.array(res)
                    uncertainties = np.array(uncertainties)
                    uncertainties = np.power(uncertainties,2)
                    unc_cov_matrix = np.diag(uncertainties)
                    unc_cov_matrix[-len(calibration.efficiency_cov):,-len(calibration.efficiency_cov):] = calibration.efficiency_cov
                    uf = np.sqrt((res.T@unc_cov_matrix) @ res)
                    warning1, warning2 = '',''
                    if f <= 0:
                        warning1 = f'warning: calculated f value is problematic since is negative or equal to 0\n'
                    if np.abs(uf / f) > 0.8:
                        warning2 = 'warning: excessive evaluated uncertainty for f\n'
                    indexes = []
                    for row in range(len(unc_cov_matrix)):
                        count = 0
                        for colu in range(len(unc_cov_matrix)):
                            count += res[row] * res[colu] * unc_cov_matrix[row,colu]
                        indexes.append(count)
                    indexes = np.array(indexes[:-6]+[np.sum(indexes[-6:])])
                    description = ['Specific count rate of monitor 2','k0 factor of monitor 2','Epithermal self shielding value of monitor 2','Resonance integral on thermal cross section value of monitor 2','Effective resonance value of monitor 2','Specific count rate of monitor 3','k0 factor of monitor 3','Epithermal self shielding value of monitor 3','Resonance integral on thermal cross section value of monitor 3','Effective resonance value of monitor 3','Thermal self shielding value','α','Efficiency evaluation']
                    indexes = [(idx_value / indexes.sum(),tag) for idx_value,tag in zip(indexes,description)]
                    indexes.sort(key= lambda x : x[0], reverse=True)
                    text_major_contributors = [f'{format(100*line[0],".1f").rjust(5, " ")} % - {line[1]}' for line in indexes[:5]]
                    textual.append(f'f value evaluated through values related to monitors 2 and 3\n{"".ljust(4)}{"value".ljust(8)}{"u (k=1)".ljust(8)}rel. u\n{"f".ljust(4)}{format(f,".2f").ljust(8)}{format(uf,".2f").ljust(8)}({np.abs(100 * uf / f):.1f} %)\n{warning1}{warning2}\nList of 5 major contributors to the combined uncertainty of f evaluation:\n'+'\n'.join(text_major_contributors))
                    mon_Au = None
                    for i in (monitor_1, monitor_2, monitor_3):
                        if i[0] == 'Au-198 411.8':
                            mon_Au = monitor_1 + [196.966569,1,0.9562,9.87E-23] #9.87E-27 uncertainty of s0_Au
                            break
                    if mon_Au is not None:
                        Asp1, uAsp1 = get_specific(mon_Au)
                        q01, uq01 = mon_Au[5], the_uncertainty_job(mon_Au[5],mon_Au[6],0.2)
                        Er1, uEr1 = mon_Au[7], the_uncertainty_job(mon_Au[7],mon_Au[8],0.5)
                        Ge1, uGe1, Gs, uGs = mon_Au[25], mon_Au[26], mon_Au[23], mon_Au[24]
                        e1 = calibration.efficiency_fit(mon_Au[2])
                        F_th = func_thermal_f(Asp1,e1,Ge1,q01,Er1,Gs,f,alpha,mon_Au[28],mon_Au[29],mon_Au[30],mon_Au[31])
                        F_epi = func_epithermal_f(Asp1,e1,Ge1,q01,Er1,Gs,f,alpha,mon_Au[28],mon_Au[29],mon_Au[30],mon_Au[31])
                        original_values = [Asp1,Ge1,q01,Er1,Gs,f,alpha,a1, a2, a3, a4, a5, a6]
                        comput_values = [Asp1,Ge1,q01,Er1,Gs,f,alpha,a1, a2, a3, a4, a5, a6]
                        uncertainties = [uAsp1,uGe1,uq01,uEr1,uGs,uf,ualpha,ua1, ua2, ua3, ua4, ua5, ua6]
                        res = []
                        resepi = []
                        for idx in range(len(original_values)):
                            comput_values[idx] = original_values[idx] + uncertainties[idx]
                            _Asp1,_Ge1,_q01,_Er1,_Gs,_f,_alpha,_a1, _a2, _a3, _a4, _a5, _a6 = comput_values
                            _e1 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],mon_Au[2])
                            solplus = (func_thermal_f(_Asp1,_e1,_Ge1,_q01,_Er1,_Gs,_f,_alpha,mon_Au[28],mon_Au[29],mon_Au[30],mon_Au[31]) - F_th) / (uncertainties[idx] + 1E-12)
                            solplusepi = (func_epithermal_f(_Asp1,_e1,_Ge1,_q01,_Er1,_Gs,_f,_alpha,mon_Au[28],mon_Au[29],mon_Au[30],mon_Au[31]) - F_th) / (uncertainties[idx] + 1E-12)
                            comput_values[idx] = original_values[idx] - uncertainties[idx]
                            _Asp1,_Ge1,_q01,_Er1,_Gs,_f,_alpha,_a1, _a2, _a3, _a4, _a5, _a6 = comput_values
                            _e1 = e_polynomial_model([_a1, _a2, _a3, _a4, _a5, _a6],mon_Au[2])
                            solminus = (func_thermal_f(_Asp1,_e1,_Ge1,_q01,_Er1,_Gs,_f,_alpha,mon_Au[28],mon_Au[29],mon_Au[30],mon_Au[31]) - F_th) / -(uncertainties[idx] + 1E-12)
                            solminusepi = (func_epithermal_f(_Asp1,_e1,_Ge1,_q01,_Er1,_Gs,_f,_alpha,mon_Au[28],mon_Au[29],mon_Au[30],mon_Au[31]) - F_th) / -(uncertainties[idx] + 1E-12)
                            comput_values[idx] = original_values[idx]
                            res.append((solplus+solminus)/2)
                            resepi.append((solplusepi+solminusepi)/2)
                        res = np.array(res)
                        resepi = np.array(resepi)
                        uncertainties = np.array(uncertainties)
                        uncertainties = np.power(uncertainties,2)
                        unc_cov_matrix = np.diag(uncertainties)
                        unc_cov_matrix[-len(calibration.efficiency_cov):,-len(calibration.efficiency_cov):] = calibration.efficiency_cov
                        uF_th = np.sqrt((res.T@unc_cov_matrix) @ res)
                        uF_epi = np.sqrt((resepi.T@unc_cov_matrix) @ resepi)
                        textual.append(f'\nConventional fluxes value evaluated through Au monitor\n{"".ljust(12)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n{"thermal".ljust(12)}{format(F_th,".2e").ljust(11)}{format(uF_th,".2e").ljust(11)}({np.abs(100 * uF_th / F_th):.1f} %)\n{"epithermal".ljust(12)}{format(F_epi,".2e").ljust(11)}{format(uF_epi,".2e").ljust(11)}({np.abs(100 * uF_epi / F_epi):.1f} %)')
                    textual = '\n'.join(textual)
                    return f, uf, alpha, ualpha, textual
                    
                def compute_f_alpha_baretriple(MM,DAY,MONTH,YEAR,HOUR,MINUTE,SECOND,IIRTIME,CALIB,sub_A,MON_1,MON_2,MON_3,MASS_1,UMASS_1,MASS_2,UMASS_2,MASS_3,UMASS_3,COI_1,UCOI_1,COI_2,UCOI_2,COI_3,UCOI_3,GS_1,UGS_1,GS_2,UGS_2,GS_3,UGS_3,GE_1,UGE_1,GE_2,UGE_2,GE_3,UGE_3,text,cond_1,cond_2,cond_3):
                    #processing
                    #end irradiation date
                    try:
                        endirr = datetime.datetime(int(YEAR.get()), int(MONTH.get()), int(DAY.get()), int(HOUR.get()), int(MINUTE.get()), int(SECOND.get()))
                    except:
                        endirr = None
                    #irradiation time
                    try:
                        irrtime = int(float(IIRTIME.get()))
                    except:
                        irrtime = 0
                    try:
                        mass_1 = float(MASS_1.get())
                    except:
                        mass_1 = 0
                    try:
                        umass_1 = float(UMASS_1.get())
                    except:
                        umass_1 = 0
                    try:
                        mass_2 = float(MASS_2.get())
                    except:
                        mass_2 = 0
                    try:
                        umass_2 = float(UMASS_2.get())
                    except:
                        umass_2 = 0
                    try:
                        mass_3 = float(MASS_3.get())
                    except:
                        mass_3 = 0
                    try:
                        umass_3 = float(UMASS_3.get())
                    except:
                        umass_3 = 0
                    try:
                        coi_1 = float(COI_1.get())
                        ucoi_1 = float(UCOI_1.get())
                    except:
                        coi_1 = 1
                        ucoi_1 = 0
                    try:
                        coi_2= float(COI_2.get())
                        ucoi_2 = float(UCOI_2.get())
                    except:
                        coi_2 = 1
                        ucoi_2 = 0
                    try:
                        coi_3 = float(COI_3.get())
                        ucoi_3 = float(UCOI_3.get())
                    except:
                        coi_3 = 1
                        ucoi_3 = 0
                    try:
                        gs_1 = float(GS_1.get())
                        ugs_1 = float(UGS_1.get())
                    except:
                        gs_1 = 1
                        ugs_1 = 0
                    try:
                        gs_2= float(GS_2.get())
                        ugs_2 = float(UGS_2.get())
                    except:
                        gs_2 = 1
                        ugs_2 = 0
                    try:
                        gs_3 = float(GS_3.get())
                        ugs_3 = float(UGS_3.get())
                    except:
                        gs_3 = 1
                        ugs_3 = 0
                    try:
                        ge_1 = float(GE_1.get())
                        uge_1 = float(UGE_1.get())
                    except:
                        ge_1 = 1
                        uge_1 = 0
                    try:
                        ge_2= float(GE_2.get())
                        uge_2 = float(UGE_2.get())
                    except:
                        ge_2 = 1
                        uge_2 = 0
                    try:
                        ge_3 = float(GE_3.get())
                        uge_3 = float(UGE_3.get())
                    except:
                        ge_3 = 1
                        uge_3 = 0
                    #check
                    if endirr is None:
                        text.configure(state='normal')
                        text.delete('0.0',END)
                        text.insert(END,'Invadid data are entered\n- end irradiation date is not valid')
                        text.configure(state='disable')
                    elif irrtime <= 0:
                        text.configure(state='normal')
                        text.delete('0.0',END)
                        text.insert(END,'Invadid data are entered\n- irradiation time is not a numeric value or <= 0')
                        text.configure(state='disable')
                    elif len(MM.spectra) == 0:
                        text.configure(state='normal')
                        text.delete('0.0',END)
                        text.insert(END,'Invadid data are entered\n- no spectra were recalled')
                        text.configure(state='disable')
                    elif CALIB.get() == '':
                        text.configure(state='normal')
                        text.delete('0.0',END)
                        text.insert(END,'Invadid data are entered\n- no calibration was selected')
                        text.configure(state='disable')
                    elif mass_1 <= 0:
                        text.configure(state='normal')
                        text.delete('0.0',END)
                        text.insert(END,'Invadid data are entered\n- an invalid value was inserted for mass of monitor 1')
                        text.configure(state='disable')
                    elif mass_2 <= 0:
                        text.configure(state='normal')
                        text.delete('0.0',END)
                        text.insert(END,'Invadid data are entered\n- an invalid value was inserted for mass of monitor 2')
                        text.configure(state='disable')
                    elif mass_3 <= 0:
                        text.configure(state='normal')
                        text.delete('0.0',END)
                        text.insert(END,'Invadid data are entered\n- an invalid value was inserted for mass of monitor 3')
                        text.configure(state='disable')
                    else:
                        #calibration
                        calibration = Calibration(CALIB.get())
                        #monitors' information
                        correct_harvesting = True
                        COND_1,COND_2,COND_3 = cond_1.get(),cond_2.get(),cond_3.get()
                        cond_descriptors = {'low. unc.':'lowest statistical uncertainty','shor. acq.':'shortest live time','lon. acq.':'longest live time','earliest':'earliest acquisition','latest':'latest acquisition'}
                        monitor_1, correct_harvesting = harvest_monitor(sub_A,MON_1.get(),MM,correct_harvesting,irrtime,endirr,mass_1,umass_1,coi_1,ucoi_1,gs_1,ugs_1,ge_1,uge_1,COND_1)
                        monitor_2, correct_harvesting = harvest_monitor(sub_A,MON_2.get(),MM,correct_harvesting,irrtime,endirr,mass_2,umass_2,coi_2,ucoi_2,gs_2,ugs_2,ge_2,uge_2,COND_2)
                        monitor_3, correct_harvesting = harvest_monitor(sub_A,MON_3.get(),MM,correct_harvesting,irrtime,endirr,mass_3,umass_3,coi_3,ucoi_3,gs_3,ugs_3,ge_3,uge_3,COND_3)
                        if monitor_1 is None:
                            text.configure(state='normal')
                            text.delete('0.0',END)
                            text.insert(END,f'Invadid data are entered\n- {MON_1.get()} not found in any of the selected spectra')
                            text.configure(state='disable')
                        elif monitor_2 is None:
                            text.configure(state='normal')
                            text.delete('0.0',END)
                            text.insert(END,f'Invadid data are entered\n- {MON_2.get()} not found in any of the selected spectra')
                            text.configure(state='disable')
                        elif monitor_3 is None:
                            text.configure(state='normal')
                            text.delete('0.0',END)
                            text.insert(END,f'Invadid data are entered\n- {MON_3.get()} not found in any of the selected spectra')
                            text.configure(state='disable')
                        elif monitor_1[5] == monitor_2[5] and monitor_1[7] == monitor_2[7]:
                            text.configure(state='normal')
                            text.delete('0.0',END)
                            text.insert(END,f'Invadid data are entered\n- Same target isotope selected for emitters {monitor_1[0]} and {monitor_2[0]}')
                            text.configure(state='disable')
                        elif monitor_1[5] == monitor_3[5] and monitor_1[7] == monitor_3[7]:
                            text.configure(state='normal')
                            text.delete('0.0',END)
                            text.insert(END,f'Invadid data are entered\n- Same target isotope selected for emitters {monitor_1[0]} and {monitor_3[0]}')
                            text.configure(state='disable')
                        elif monitor_2[5] == monitor_3[5] and monitor_2[7] == monitor_3[7]:
                            text.configure(state='normal')
                            text.delete('0.0',END)
                            text.insert(END,f'Invadid data are entered\n- Same target isotope selected for emitters {monitor_2[0]} and {monitor_3[0]}')
                            text.configure(state='disable')
                        elif correct_harvesting == True:
                            text.configure(state='normal')
                            text.delete('0.0',END)
                            text.insert(END,f'Selected monitors\nmonitor 1: {monitor_1[0]} keV emission (found on spectrum {monitor_1[-1]} based on {cond_descriptors[COND_1]})\nmonitor 2: {monitor_2[0]} keV emission (found on spectrum {monitor_2[-1]} based on {cond_descriptors[COND_2]})\nmonitor 3: {monitor_3[0]} keV emission (found on spectrum {monitor_3[-1]} based on {cond_descriptors[COND_3]})\n')
                            text.configure(state='disable')
                            MM.f, MM.uf, MM.alpha, MM.ualpha, textual = do_the_fa_job(monitor_1,monitor_2,monitor_3,calibration)
                            text.configure(state='normal')
                            text.insert(END,textual)
                            text.configure(state='disable')
                    
                def accept_values(CHB,MM,channel_box,f_box,uf_box,a_box,ua_box):
                    channel_box.delete(0,END)
                    channel_box.insert(END,CHB.get())
                    f_box.delete(0,END)
                    f_box.insert(END,f'{MM.f:.1f}')
                    uf_box.delete(0,END)
                    uf_box.insert(END,f'{MM.uf:.1f}')
                    a_box.delete(0,END)
                    a_box.insert(END,f'{MM.alpha:.4f}')
                    ua_box.delete(0,END)
                    ua_box.insert(END,f'{MM.ualpha:.4f}')
                    MM.destroy()
                    
                def display_peaklist_fa(In,SPClist):
                    """Display multiple calibration spectra"""
                    def singlescreen_of_multiple(NA,SC,NMS=None,Z=None):
                        """Display single of multiple spectra"""
                        ratiooflines=int(rows)
                        residuallenS=len(NA.peak_list)
                        i=0
                        paginazionepicchi=[]
                        if NA.assign_nuclide==None:
                            NA.assign_nuclide=['']*len(NA.peak_list)
                        while residuallenS>0:
                            try:
                                paginapicco=NA.peak_list[ratiooflines*i:ratiooflines*i+ratiooflines]
                            except IndexError:
                                paginapicco=NA.peak_list[ratiooflines*i:]
                            paginazionepicchi.append(paginapicco)
                            residuallenS=residuallenS-ratiooflines
                            i=i+1
                        cdn=SC.winfo_children()
                        for i in cdn:
                            i.destroy()
                        F=Frame(SC)
                        L=Label(F, width=1).pack(side=LEFT)
                        BSS=Button(F, text='Plot', width=8)
                        BSS.pack(side=LEFT, anchor=W)
                        BSS.configure(command=lambda SC=SC,S=NA: showspectrum(SC,S))
                        F.pack(anchor=W)
                        F=Frame(SC)
                        L=Label(F, width=1).pack(side=LEFT)
                        L=Label(F, text='start acqusition: '+NA.readable_datetime(), width=30, anchor=W).pack(side=LEFT)
                        L=Label(F, text='tc / s: '+str(NA.real_time), width=16, anchor=W).pack(side=LEFT)
                        L=Label(F, text='tl / s: '+str(NA.live_time), width=16, anchor=W).pack(side=LEFT)
                        L=Label(F, text='tdead: '+NA.deadtime(), width=14, anchor=W).pack(side=LEFT)
                        F.pack(anchor=W)
                        F=Frame(SC)
                        L=Label(F, width=1).pack(side=LEFT)
                        if len(NA.spectrumpath)>71:
                            L=Label(F, text='...'+NA.spectrumpath[-70:], width=76, anchor=E).pack(side=LEFT)
                        else:
                            L=Label(F, text=NA.spectrumpath, width=76, anchor=E).pack(side=LEFT)
                        F.pack(anchor=W)
                        L=Label(SC).pack()
                        F=Frame(SC)
                        P=Frame(F)
                        P.pack()
                        indice=IntVar(SC)
                        indice.set(0)
                        sciogliipicchibkg(F,paginazionepicchi,indice)
                        F.pack()
                        
                    def BmenocommandscrollE(MS,superi,In):
                        if superi>0:
                            superi-=1
                            cdn=MS.winfo_children()
                            for i in cdn:
                                i.destroy()
                            F=Frame(MS)
                            Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,In=In : BmenocommandscrollE(MS,superi,In)).pack(side=LEFT)
                            L=Label(F, text=f'spectrum {superi+1} of {len(In)}').pack(side=LEFT)
                            Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,In=In : BpiucommandscrollE(MS,superi,In)).pack(side=LEFT)
                            F.pack()
                            L=Label(MS).pack()
                            SC=Frame(MS)
                            SC.pack()
                            singlescreen_of_multiple(In[superi],SC)
                    
                    def BpiucommandscrollE(MS,superi,In):
                        if superi<len(In)-1:
                            superi+=1
                            cdn=MS.winfo_children()
                            for i in cdn:
                                i.destroy()
                            F=Frame(MS)
                            Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,In=In : BmenocommandscrollE(MS,superi,In)).pack(side=LEFT)
                            L=Label(F, text=f'spectrum {superi+1} of {len(In)}').pack(side=LEFT)
                            Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,In=In : BpiucommandscrollE(MS,superi,In)).pack(side=LEFT)
                            F.pack()
                            L=Label(MS).pack()
                            SC=Frame(MS)
                            SC.pack()
                            singlescreen_of_multiple(In[superi],SC)

                    try:
                        superi = SPClist.curselection()[0]
                    except IndexError:
                        superi = 0
                    if len(In) > 0:
                        MS=Toplevel()
                        MS.title(In[0].identity+' peak list')
                        MS.resizable(False,False)
                        MS.focus()
                        F=Frame(MS)
                        Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,In=In : BmenocommandscrollE(MS,superi,In)).pack(side=LEFT)
                        L=Label(F, text=f'spectrum {superi+1} of {len(In)}').pack(side=LEFT)
                        Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,In=In : BpiucommandscrollE(MS,superi,In)).pack(side=LEFT)
                        F.pack()
                        L=Label(MS).pack()
                        SC=Frame(MS)
                        SC.pack()
                        singlescreen_of_multiple(In[superi],SC)
                
                def bare_triple_monitor_method(MM,channel_box,date,time,tirr):
                    date = [item.get() for item in date]
                    time = [item.get() for item in time]
                    for i in MM.winfo_children():
                        i.destroy()
                    MM.title('Bare triple monitor')
                    MM.spectra = []
                    MM.f, MM.uf, MM.alpha, MM.ualpha = 0.0, 0.0, 0.0, 0.0
                    modetypes = ['low. unc.','shor. acq.','lon. acq.','earliest','latest']
                    F = Frame(MM)
                    CHNL,listCHN=openchannels('data/channels/chn.txt')
                    L=Label(F, text='channel', width=7, anchor=W).pack(side=LEFT)
                    channel_doublebox = ttk.Combobox(F, values=listCHN, width=20)
                    channel_doublebox.pack(side=LEFT)
                    channel_doublebox.set(channel_box.get())
                    L=Label(F, text='end irr. dd/MM/yyyy', width=20, anchor=E).pack(side=LEFT)
                    Day_spinbox = Spinbox(F, from_=1, to=31, width=3, increment=1)
                    Day_spinbox.pack(side=LEFT)
                    Day_spinbox.delete(0,END)
                    Day_spinbox.insert(END,date[0])
                    Month_spinbox = Spinbox(F, from_=1, to=12, width=3, increment=1)
                    Month_spinbox.pack(side=LEFT)
                    Month_spinbox.delete(0,END)
                    Month_spinbox.insert(END,date[1])
                    Year_spinbox = Spinbox(F, from_=2019, to=2100, width=5, increment=1)
                    Year_spinbox.pack(side=LEFT)
                    Year_spinbox.delete(0,END)
                    Year_spinbox.insert(END,date[2])
                    L=Label(F, text='HH/mm/ss', width=12, anchor=E).pack(side=LEFT)
                    Hour_spinbox = Spinbox(F, from_=0, to=23, width=3, increment=1)
                    Hour_spinbox.pack(side=LEFT)
                    Hour_spinbox.delete(0,END)
                    Hour_spinbox.insert(END,time[0])
                    Minute_spinbox = Spinbox(F, from_=0, to=59, width=3, increment=1)
                    Minute_spinbox.pack(side=LEFT)
                    Minute_spinbox.delete(0,END)
                    Minute_spinbox.insert(END,time[1])
                    Second_spinbox = Spinbox(F, from_=0, to=59, width=3, increment=1)
                    Second_spinbox.pack(side=LEFT)
                    Second_spinbox.delete(0,END)
                    Second_spinbox.insert(END,time[2])
                    L=Label(F, text='ti / s', width=8, anchor=E).pack(side=LEFT)
                    Itime_spinbox = Spinbox(F, from_=0, to=999999999, width=10, increment=1)
                    Itime_spinbox.pack(side=LEFT)
                    Itime_spinbox.delete(0,END)
                    Itime_spinbox.insert(END,tirr.get())
                    F.pack(anchor=W, padx=5, pady=5)
                    F = Frame(MM)
                    L=Label(F, text='calibration', width=10, anchor=W).pack(side=LEFT)
                    values=listeffy()
                    calib_omboBCP=ttk.Combobox(F, values=values, state='readonly', width=50)
                    calib_omboBCP.pack(side=LEFT)
                    F.pack(anchor=W, padx=5, pady=5)
                    values = [line[0] for line in sub_A]
                    F_monitors = Frame(MM)
                    L=Label(F_monitors, text='emitter', width=13).grid(row=0,column=1)
                    L=Label(F_monitors, text='monitor', width=8).grid(row=0,column=2)
                    L=Label(F_monitors, text='Q0 / 1', width=8).grid(row=0,column=3)
                    L=Label(F_monitors, text='Er / eV', width=8).grid(row=0,column=4)
                    L=Label(F_monitors, text='mass / g', width=10).grid(row=0,column=5)
                    L=Label(F_monitors, text='u(mass) / g', width=10).grid(row=0,column=6)
                    L=Label(F_monitors, text='COI / 1', width=9).grid(row=0,column=7)
                    L=Label(F_monitors, text='u(COI) / 1', width=9).grid(row=0,column=8)
                    L=Label(F_monitors, text='Gs / 1', width=9).grid(row=0,column=9)
                    L=Label(F_monitors, text='u(Gs) / 1', width=9).grid(row=0,column=10)
                    L=Label(F_monitors, text='Ge / 1', width=9).grid(row=0,column=11)
                    L=Label(F_monitors, text='u(Ge) / 1', width=9).grid(row=0,column=12)
                    L=Label(F_monitors, text='condition', width=9).grid(row=0,column=13)
                    L=Label(F_monitors, text='1', width=2).grid(row=1,column=0)
                    mon_1 = ttk.Combobox(F_monitors, values=values, state='readonly', width=13)
                    mon_1.grid(row=1,column=1)
                    L_mon_1 = Label(F_monitors, text='')
                    L_mon_1.grid(row=1,column=2)
                    L_Q0_1 = Label(F_monitors, text='')
                    L_Q0_1.grid(row=1,column=3)
                    L_Er_1 = Label(F_monitors, text='')
                    L_Er_1.grid(row=1,column=4)
                    try:
                        mon_1.set('Au-198 411.8')
                        resp = check_label('Au-198 411.8')
                        L_mon_1.configure(text=resp[0])
                        L_Q0_1.configure(text=resp[1])
                        L_Er_1.configure(text=resp[2])
                    except:
                        pass
                    mon_1.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>',box=mon_1 : update_date(box,L_mon_1,L_Q0_1,L_Er_1))
                    mass_1 = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
                    mass_1.grid(row=1,column=5)
                    umass_1 = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
                    umass_1.grid(row=1,column=6)
                    COI_1 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    COI_1.grid(row=1,column=7)
                    COI_1.delete(0,END)
                    COI_1.insert(END,1.000)
                    UCOI_1 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UCOI_1.grid(row=1,column=8)
                    GS_1 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    GS_1.grid(row=1,column=9)
                    GS_1.delete(0,END)
                    GS_1.insert(END,1.000)
                    UGS_1 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UGS_1.grid(row=1,column=10)
                    GE_1 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    GE_1.grid(row=1,column=11)
                    GE_1.delete(0,END)
                    GE_1.insert(END,1.000)
                    UGE_1 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UGE_1.grid(row=1,column=12)
                    cond_1 = ttk.Combobox(F_monitors, values=modetypes, state='readonly', width=7)
                    cond_1.grid(row=1,column=13)
                    cond_1.set(modetypes[0])
                    
                    L=Label(F_monitors, text='2', width=2).grid(row=2,column=0)
                    mon_2 = ttk.Combobox(F_monitors, values=values, state='readonly', width=13)
                    mon_2.grid(row=2,column=1)
                    L_mon_2 = Label(F_monitors, text='')
                    L_mon_2.grid(row=2,column=2)
                    L_Q0_2 = Label(F_monitors, text='')
                    L_Q0_2.grid(row=2,column=3)
                    L_Er_2 = Label(F_monitors, text='')
                    L_Er_2.grid(row=2,column=4)
                    try:
                        mon_2.set('Nb-97m 743.4')
                        resp = check_label('Nb-97m 743.4')
                        L_mon_2.configure(text=resp[0])
                        L_Q0_2.configure(text=resp[1])
                        L_Er_2.configure(text=resp[2])
                    except:
                        pass
                    mon_2.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>',box=mon_2 : update_date(box,L_mon_2,L_Q0_2,L_Er_2))
                    mass_2 = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
                    mass_2.grid(row=2,column=5)
                    umass_2 = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
                    umass_2.grid(row=2,column=6)
                    COI_2 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    COI_2.grid(row=2,column=7)
                    COI_2.delete(0,END)
                    COI_2.insert(END,1.000)
                    UCOI_2 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UCOI_2.grid(row=2,column=8)
                    GS_2 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    GS_2.grid(row=2,column=9)
                    GS_2.delete(0,END)
                    GS_2.insert(END,1.000)
                    UGS_2 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UGS_2.grid(row=2,column=10)
                    GE_2 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    GE_2.grid(row=2,column=11)
                    GE_2.delete(0,END)
                    GE_2.insert(END,1.000)
                    UGE_2 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UGE_2.grid(row=2,column=12)
                    cond_2 = ttk.Combobox(F_monitors, values=modetypes, state='readonly', width=7)
                    cond_2.grid(row=2,column=13)
                    cond_2.set(modetypes[0])
                    
                    L=Label(F_monitors, text='3', width=2).grid(row=3,column=0)
                    mon_3 = ttk.Combobox(F_monitors, values=values, state='readonly', width=13)
                    mon_3.grid(row=3,column=1)
                    L_mon_3 = Label(F_monitors, text='')
                    L_mon_3.grid(row=3,column=2)
                    L_Q0_3 = Label(F_monitors, text='')
                    L_Q0_3.grid(row=3,column=3)
                    L_Er_3 = Label(F_monitors, text='')
                    L_Er_3.grid(row=3,column=4)
                    try:
                        mon_3.set('Zr-95 756.7')
                        resp = check_label('Zr-95 756.7')
                        L_mon_3.configure(text=resp[0])
                        L_Q0_3.configure(text=resp[1])
                        L_Er_3.configure(text=resp[2])
                    except:
                        pass
                    mon_3.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>',box=mon_3 : update_date(box,L_mon_3,L_Q0_3,L_Er_3))
                    mass_3 = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
                    mass_3.grid(row=3,column=5)
                    umass_3 = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
                    umass_3.grid(row=3,column=6)
                    COI_3 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    COI_3.grid(row=3,column=7)
                    COI_3.delete(0,END)
                    COI_3.insert(END,1.000)
                    UCOI_3 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UCOI_3.grid(row=3,column=8)
                    GS_3 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    GS_3.grid(row=3,column=9)
                    GS_3.delete(0,END)
                    GS_3.insert(END,1.000)
                    UGS_3 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UGS_3.grid(row=3,column=10)
                    GE_3 = Spinbox(F_monitors, from_=0.000, to=1.999, width=7, increment=0.001)
                    GE_3.grid(row=3,column=11)
                    GE_3.delete(0,END)
                    GE_3.insert(END,1.000)
                    UGE_3 = Spinbox(F_monitors, from_=0.000, to=1.000, width=7, increment=0.001)
                    UGE_3.grid(row=3,column=12)
                    cond_3 = ttk.Combobox(F_monitors, values=modetypes, state='readonly', width=7)
                    cond_3.grid(row=3,column=13)
                    cond_3.set(modetypes[0])
                    
                    F_monitors.pack(anchor=W, pady=5, padx=5)
                    F = Frame(MM).pack(anchor=W, padx=5, pady=5)
                    L = Label(MM, text='spectra',anchor=W).pack(anchor=W, padx=5)
                    F_spectra = Frame(MM)
                    F_listboxspectra = Frame(F_spectra)
                    scrollbar = Scrollbar(F_listboxspectra, orient=VERTICAL)
                    listbox = Listbox(F_listboxspectra, width=75, heigh=5, yscrollcommand=scrollbar.set)
                    scrollbar.config(command=listbox.yview)
                    scrollbar.pack(side=RIGHT, fill=Y)
                    listbox.pack(side=LEFT, fill=BOTH, expand=1)
                    F_commandlistspectra = Frame(F_spectra)
                    B_add = Button(F_commandlistspectra, text='Add', width=15)
                    B_add.pack()
                    B_pklist = Button(F_commandlistspectra, text='Peak list', width=15)
                    B_pklist.pack()
                    B_clear = Button(F_commandlistspectra, text='Clear', width=15)
                    B_clear.pack()
                    F_listboxspectra.pack(side=LEFT, anchor=NW, fill=BOTH, expand=1)
                    F_commandlistspectra.pack(side=RIGHT)
                    F_spectra.pack(anchor=W, padx=5)
                    
                    F = Frame(MM).pack(anchor=W, padx=5, pady=5)
                    L = Label(MM, text='log',anchor=W).pack(anchor=W, padx=5)
                    LogBox = Frame(MM)
                    fa_scrollbar_text = Scrollbar(LogBox, orient=VERTICAL)
                    fa_textbox = Text(LogBox, heigh=8, yscrollcommand=fa_scrollbar_text.set, wrap=WORD)
                    fa_scrollbar_text.config(command=fa_textbox.yview)
                    fa_scrollbar_text.pack(side=RIGHT, fill=Y)
                    fa_textbox.pack(side=LEFT, fill=BOTH, expand=1)
                    LogBox.pack(anchor=W, padx=5, fill=X)
                    fa_textbox.configure(state='disable')
                    
                    F = Frame(MM)
                    B_compute = Button(F, text='Compute', width=10)
                    B_compute.pack(side=LEFT)
                    B_accept_values = Button(F, text='Confirm', width=10)
                    B_accept_values.pack(side=LEFT)
                    F.pack(anchor=W, padx=5, pady=10)
                    B_add.configure(command=lambda SPCIn=MM.spectra,SPClist=listbox,unclimit=unclimit_calib,setforall=True : fa_add_spectra(SPCIn,SPClist,unclimit,setforall))
                    B_clear.configure(command=lambda SPCIn=MM.spectra,SPClist=listbox : fa_clear_spectra(SPCIn,SPClist))
                    B_pklist.configure(command=lambda SPCIn=MM.spectra,SPClist=listbox : display_peaklist_fa(SPCIn,SPClist))
                    B_compute.configure(command=lambda : compute_f_alpha_baretriple(MM,Day_spinbox,Month_spinbox,Year_spinbox,Hour_spinbox,Minute_spinbox,Second_spinbox,Itime_spinbox,calib_omboBCP,sub_A,mon_1,mon_2,mon_3,mass_1,umass_1,mass_2,umass_2,mass_3,umass_3,COI_1,UCOI_1,COI_2,UCOI_2,COI_3,UCOI_3,GS_1,UGS_1,GS_2,UGS_2,GS_3,UGS_3,GE_1,UGE_1,GE_2,UGE_2,GE_3,UGE_3,fa_textbox,cond_1,cond_2,cond_3))
                    B_accept_values.configure(command=lambda : accept_values(channel_doublebox,MM,channel_box,f_box,uf_box,a_box,ua_box))
                
                Main_evaluator = Toplevel(root)
                Main_evaluator.title('f alpha')
                Main_evaluator.resizable(False,False)
                F = Frame(Main_evaluator)
                L = Label(F, text='Choice of method', width=30, anchor=W).pack(pady=5,padx=5)
                B_baretriple = Button(F, text='Bare triple monitor', width=20, command=lambda MM=Main_evaluator: bare_triple_monitor_method(MM,channel_box,date,time,tirr))
                B_baretriple.pack(padx=5)
                B_cdcovered = Button(F, text='Cd covered monitor', width=20, state='disable')
                B_cdcovered.pack(padx=5)
                B_other = Button(F, text='Bare multi monitor', width=20, state='disable')
                B_other.pack(padx=5)
                F.pack(anchor=NW, pady=5)
                Main_evaluator.focus()
            
            CHNL,listCHN=openchannels('data/channels/chn.txt')
            IRRD,listIRR=openchannelsI('data/irradiations/irr.txt')
            if type(listCHN)!=list:
                listCHN=list(listCHN)
            TL=Toplevel()
            TL.title('Irradiation')
            TL.resizable(False,False)
            L=Label(TL).pack()
            F=Frame(TL)
            L=Label(F, width=1).pack(side=LEFT)
            L=Label(F, text='irr. code', width=9, anchor=W).pack(side=LEFT)
            CIRRComboB=ttk.Combobox(F, values=listIRR)
            CIRRComboB.pack(side=LEFT)
            L=Label(F, width=1).pack(side=LEFT)
            BDELCIRR=Button(F, text='Delete', width=8, command=lambda CIRRComboB=CIRRComboB,IRRD=IRRD,listIRR=listIRR : delete_irradiation_code(CIRRComboB,IRRD,listIRR)).pack(side=LEFT)
            F.pack(anchor=W)
            L=Label(TL).pack()
            F=Frame(TL)
            L=Label(F, width=1).pack(side=LEFT)
            L=Label(F, text='irr. channel', width=9, anchor=W).pack(side=LEFT)
            CHomboB=ttk.Combobox(F, values=listCHN)
            CHomboB.pack(side=LEFT)
            L=Label(F, width=1).pack(side=LEFT)
            BEVAL=Button(F, text='Evaluate', width=8)
            BEVAL.pack(side=LEFT)
            BSU=Button(F, text='Save', width=8)
            BSU.pack(side=LEFT)
            BDEL=Button(F, text='Delete', width=8)
            BDEL.pack(side=LEFT)
            L=Label(F, width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TL)
            L=Label(F, width=1).pack(side=LEFT)
            L=Label(F, text='f / 1', width=9, anchor=W).pack(side=LEFT)
            Fspinbox = Spinbox(F, from_=0, to=99999, width=10, increment=0.1)
            Fspinbox.pack(side=LEFT)
            L=Label(F, width=4).pack(side=LEFT)
            L=Label(F, text='u(f) / 1', width=6, anchor=W).pack(side=LEFT)
            UFspinbox = Spinbox(F, from_=0, to=99999, width=7, increment=0.1)
            UFspinbox.pack(side=LEFT)
            USH=Button(F, text='o', relief='flat', command=lambda L='Irradiation - u(f) / 1',u=UFspinbox : uncertainty_shaper(L,u))
            USH.pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TL)
            L=Label(F, width=1).pack(side=LEFT)
            L=Label(F, text='α / 1', width=9, anchor=W).pack(side=LEFT)
            Aspinbox = Spinbox(F, from_=-1, to=1, width=10, increment=0.0001)
            Aspinbox.pack(side=LEFT)
            Aspinbox.delete(0,END)
            Aspinbox.insert(END,'0.0000')
            L=Label(F, width=4).pack(side=LEFT)
            L=Label(F, text='u(α) / 1', width=6, anchor=W).pack(side=LEFT)
            UAspinbox = Spinbox(F, from_=0.0, to=1, width=7, increment=0.0001)
            UAspinbox.pack(side=LEFT)
            UAspinbox.delete(0,END)
            UAspinbox.insert(END,'0.0000')
            USH=Button(F, text='o', relief='flat', command=lambda L='Irradiation - u(α) / 1',u=UAspinbox : uncertainty_shaper(L,u))
            USH.pack(side=LEFT)
            F.pack(anchor=W)
            BSU.configure(command=lambda CB=CHomboB,F=Fspinbox,UF=UFspinbox,A=Aspinbox,UA=UAspinbox,CHNL=CHNL:save_update_channels(CB,F,UF,A,UA,CHNL))
            BDEL.configure(command=lambda CB=CHomboB,F=Fspinbox,UF=UFspinbox,A=Aspinbox,UA=UAspinbox,CHNL=CHNL:delete_channel(CB,F,UF,A,UA,CHNL))
            L=Label(TL).pack()
            F=Frame(TL)
            L=Label(F, width=1).pack(side=LEFT)
            L=Label(F, text='ti / s', width=9, anchor=W).pack(side=LEFT)
            Itimespinbox = Spinbox(F, from_=0, to=999999999, width=10, increment=1)
            Itimespinbox.pack(side=LEFT)
            L=Label(F, width=4).pack(side=LEFT)
            L=Label(F, text='u(ti) / s', width=6, anchor=W).pack(side=LEFT)
            UItimespinbox = Spinbox(F, from_=0, to=1000, width=7, increment=1)
            UItimespinbox.pack(side=LEFT)
            USH=Button(F, text='o', relief='flat', command=lambda L='Irradiation - u(ti) / s',u=UItimespinbox : uncertainty_shaper(L,u))
            USH.pack(side=LEFT)
            F.pack(anchor=W)
            L=Label(TL).pack()
            F=Frame(TL)
            L=Label(F, width=1).pack(side=LEFT)
            L=Label(F, text='end irr.', width=6, anchor=W).pack(side=LEFT)
            L=Label(F, text='dd/MM/yyyy', width=11, anchor=W).pack(side=LEFT)
            Dayspinbox = Spinbox(F, from_=1, to=31, width=3, increment=1)
            Dayspinbox.pack(side=LEFT)
            Monthspinbox = Spinbox(F, from_=1, to=12, width=3, increment=1)
            Monthspinbox.pack(side=LEFT)
            Yearspinbox = Spinbox(F, from_=2019, to=2100, width=5, increment=1)
            Yearspinbox.pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(TL)
            L=Label(F, width=8).pack(side=LEFT)
            L=Label(F, text='HH/mm/ss', width=11, anchor=W).pack(side=LEFT)
            Hourspinbox = Spinbox(F, from_=0, to=23, width=3, increment=1)
            Hourspinbox.pack(side=LEFT)
            Minutespinbox = Spinbox(F, from_=0, to=59, width=3, increment=1)
            Minutespinbox.pack(side=LEFT)
            Secondspinbox = Spinbox(F, from_=0, to=59, width=3, increment=1)
            Secondspinbox.pack(side=LEFT)
            L=Label(F, width=1).pack(side=LEFT)
            F.pack(anchor=W)
            L=Label(TL).pack()
            event='<<ComboboxSelected>>'
            CHomboB.bind(event,lambda event=event,CB=CHomboB,F=Fspinbox,UF=UFspinbox,A=Aspinbox,UA=UAspinbox,CHNL=CHNL: automatic_f_a(event,CB,F,UF,A,UA,CHNL))
            CIRRComboB.bind(event,lambda event=event,CB=CIRRComboB,DS=Dayspinbox,MS=Monthspinbox,YS=Yearspinbox,HS=Hourspinbox, MinS=Minutespinbox, SS=Secondspinbox, ITS=Itimespinbox, UTS=UItimespinbox, CHNL=IRRD,CBB=CHomboB,F=Fspinbox,UF=UFspinbox,A=Aspinbox,UA=UAspinbox: automatic_irradiation_data(event,CB,DS,MS,YS,HS,MinS,SS,ITS,UTS,CHNL,CBB,F,UF,A,UA))
            CB=Button(TL, text='Confirm', width=10, command= lambda ECC=CIRRComboB,CHomboB=CHomboB,Fspinbox=Fspinbox,UFspinbox=UFspinbox,Aspinbox=Aspinbox,UAspinbox=UAspinbox,Dayspinbox=Dayspinbox,Monthspinbox=Monthspinbox,Yearspinbox=Yearspinbox,Hourspinbox=Hourspinbox,Minutespinbox=Minutespinbox,Secondspinbox=Secondspinbox,Itimespinbox=Itimespinbox,UItimespinbox=UItimespinbox,NAA=NAA,LCH=LCH,LF=LF,LALF=LALF,LIDT=LIDT,LITM=LITM,TL=TL,IRRD=IRRD : apply(ECC,CHomboB,Fspinbox,UFspinbox,Aspinbox,UAspinbox,Dayspinbox,Monthspinbox,Yearspinbox,Hourspinbox,Minutespinbox,Secondspinbox,Itimespinbox,UItimespinbox,NAA,LCH,LF,LALF,LIDT,LITM,TL,IRRD))
            CB.pack()
            L=Label(TL).pack()
            BEVAL.configure(command=lambda root=TL, channel_box=CHomboB, f_box=Fspinbox,uf_box=UFspinbox,a_box=Aspinbox,ua_box=UAspinbox, date=[Dayspinbox,Monthspinbox,Yearspinbox], time=[Hourspinbox,Minutespinbox,Secondspinbox], tirr=Itimespinbox : f_alpha_evaluations(root,channel_box,f_box,uf_box,a_box,ua_box,date,time,tirr))
            TL.focus()
            
        def confirm_calibrations_2parameters(Em,Eq,Ename,ext):
            if Ename!='':
                f=open('data/efficiencies/'+Ename+ext,'w')
                f.write(str(Eq))
                f.write(' ')
                if Em==0.0:
                    f.write(str(0.000000001))
                else:
                    f.write(str(Em))
                f.close()
                    
        def confirm_calibrations_6parameters(EP,EC,Ename,NC):
            if Ename!='' and EP[0,0]!=0.0 and EP[1,0]!=0.0:
                f=open('data/efficiencies/'+Ename+'.eff','w')
                for i in range(len(EP)):
                    for k in range(EP[i].size):
                        f.write(str(EP[i,k]))
                        f.write('    ')
                    f.write('\n')
                for i in range(len(EC)):
                    for k in range(EC[i].size):
                        f.write(str(EC[i,k]))
                        f.write('    ')
                    f.write('\n')
                f.close()
                
        def new_calibrations(CB_master,CB_std=None,CB_sample=None):
            def update_figure_model(CB,L,B):
                lin = PhotoImage(file=f"data/models/{CB.get()}.png")
                L.configure(image=lin)
                L.logo = lin
                B.configure(state='disable')
                
            def add_position(SPCIn,SPClist,C_posix,SBD,SBL):
                nn = len(C_posix['values']) + 1
                while f'position {nn}' in C_posix['values']:
                    nn += 1
                SPCIn[f'position {nn}'] = []
                SPClist.delete(0,END)
                C_posix['values'] = list(SPCIn.keys())
                C_posix.set(f'position {nn}')
                indc = PhotoImage(file=f"data/models/dg.png")
                SBD.configure(to=500, increment=1)
                SBD.delete(0,END)
                SBD.insert(END,'0')
                SBL.configure(image=indc)
                SBL.logo = indc
                #B.configure(state='disable')
                
            def rename_position(SPCIn,C_posix):
                def return_confirm_rename_position(ew,E,C_posix,TLRN,SPCIn):
                    if E.get() not in C_posix.keys():
                        temporary_storage = SPCIn[C_posix.get()]
                        SPCIn.pop(C_posix.get())
                        SPCIn[E.get()] = temporary_storage
                        C_posix['values'] = list(SPCIn.keys())
                        C_posix.set(E.get())
                        TLRN.destroy()
                h,w,a,b=C_posix.winfo_height(),C_posix.winfo_width(),C_posix.winfo_rootx(),C_posix.winfo_rooty()
                TLRN=Toplevel()
                TLRN.geometry(f'{w}x{h}+{a}+{b+h}')
                TLRN.overrideredirect(True)
                TLRN.resizable(False,False)
                E=Entry(TLRN)
                E.pack(side=LEFT, fill=X, expand=True)
                E.insert(0,C_posix.get())
                E.focus()            
                #BC=Button(TLRN, text='Confirm', width=8, command=lambda E=E,EC=EC,TLRN=TLRN,NAA=NAA : confirm_rename(E,EC,TLRN,NAA)).pack(side=RIGHT)
                ew='<Return>'
                E.bind(ew,lambda ew=ew,E=E,C_posix=C_posix,TLRN=TLRN,SPCIn=SPCIn : return_confirm_rename_position(ew,E,C_posix,TLRN,SPCIn))
                event="<FocusOut>"
                TLRN.bind(event,lambda event=event,M=TLRN : M.destroy())
                
            def delete_position(SPCIn,SPClist,C_posix,SBD,SBL):
                if len(SPCIn) > 1:
                    SPCIn.pop(C_posix.get())
                    C_posix['values'] = list(SPCIn.keys())
                    C_posix.set(C_posix['values'][0])
                    SPClist.delete(0,END)
                    for spectrum in SPCIn[C_posix.get()]:
                        SPClist.insert(END,spectrum.filename())
                    if len(SPCIn.keys()) == 1:
                        indc = PhotoImage(file=f"data/models/der.png")
                        SBD.configure(to=1, increment=0.001)
                        SBD.delete(0,END)
                        SBD.insert(END,'0.00')
                    elif len(SPCIn.keys()) > 1:
                        indc = PhotoImage(file=f"data/models/dg.png")
                        SBD.configure(to=500, increment=1)
                        SBD.delete(0,END)
                        SBD.insert(END,'0')
                    else:
                        indc = None
                    SBL.configure(image=indc)
                    SBL.logo = indc
                    #B.configure(state='disable')
                
            def update_spectralist_by_position(CB,SPCIn,SPClist):
                SPClist.delete(0,END)
                for spectrum in SPCIn[CB.get()]:
                    SPClist.insert(END,spectrum.filename())
                
            def add_spectra(SPCIn,SPClist,unclimit,setforall,B,SBL,SBD,C_posix):
                spectra_names=searchforhypelabmultiplefiles(unclimit,setforall)
                if spectra_names!=None:
                    for tg in spectra_names:
                        if tg[2]!=None:
                            SPT=Spectrum('Calibration',tg[1],tg[2],tg[3],tg[4],tg[5],tg[0])
                            SPCIn[C_posix.get()].append(SPT)
                            SPClist.insert(END,SPT.filename())
                SPClist.focus()
                
                if len(SPCIn.keys()) == 1:
                    indc = PhotoImage(file=f"data/models/der.png")
                    SBD.configure(to=1, increment=0.001)
                    SBD.delete(0,END)
                    SBD.insert(END,'0.00')
                elif len(SPCIn.keys()) > 1:
                    indc = PhotoImage(file=f"data/models/dg.png")
                    SBD.configure(to=500, increment=1)
                    SBD.delete(0,END)
                    SBD.insert(END,'0')
                else:
                    indc = None
                SBL.configure(image=indc)
                SBL.logo = indc
                B.configure(state='disable')
                
            def display_peaklist(In,SPClist,CB):
                """Display multiple calibration spectra"""
                def singlescreen_of_multiple(NA,SC,NMS=None,Z=None):
                    """Display single of multiple spectra"""
                    ratiooflines=int(rows)
                    residuallenS=len(NA.peak_list)
                    i=0
                    paginazionepicchi=[]
                    if NA.assign_nuclide==None:
                        NA.assign_nuclide=['']*len(NA.peak_list)
                    while residuallenS>0:
                        try:
                            paginapicco=NA.peak_list[ratiooflines*i:ratiooflines*i+ratiooflines]
                        except IndexError:
                            paginapicco=NA.peak_list[ratiooflines*i:]
                        paginazionepicchi.append(paginapicco)
                        residuallenS=residuallenS-ratiooflines
                        i=i+1
                    cdn=SC.winfo_children()
                    for i in cdn:
                        i.destroy()
                    F=Frame(SC)
                    L=Label(F, width=1).pack(side=LEFT)
                    BSS=Button(F, text='Plot', width=8)
                    BSS.pack(side=LEFT, anchor=W)
                    BSS.configure(command=lambda SC=SC,S=NA: showspectrum(SC,S))
                    F.pack(anchor=W)
                    F=Frame(SC)
                    L=Label(F, width=1).pack(side=LEFT)
                    L=Label(F, text='start acqusition: '+NA.readable_datetime(), width=30, anchor=W).pack(side=LEFT)
                    L=Label(F, text='tc / s: '+str(NA.real_time), width=16, anchor=W).pack(side=LEFT)
                    L=Label(F, text='tl / s: '+str(NA.live_time), width=16, anchor=W).pack(side=LEFT)
                    L=Label(F, text='tdead: '+NA.deadtime(), width=14, anchor=W).pack(side=LEFT)
                    F.pack(anchor=W)
                    F=Frame(SC)
                    L=Label(F, width=1).pack(side=LEFT)
                    if len(NA.spectrumpath)>71:
                        L=Label(F, text='...'+NA.spectrumpath[-70:], width=76, anchor=E).pack(side=LEFT)
                    else:
                        L=Label(F, text=NA.spectrumpath, width=76, anchor=E).pack(side=LEFT)
                    F.pack(anchor=W)
                    L=Label(SC).pack()
                    F=Frame(SC)
                    P=Frame(F)
                    P.pack()
                    indice=IntVar(SC)
                    indice.set(0)
                    sciogliipicchibkg(F,paginazionepicchi,indice)
                    F.pack()
                    
                def BmenocommandscrollE(MS,superi,In):
                    if superi>0:
                        superi-=1
                        cdn=MS.winfo_children()
                        for i in cdn:
                            i.destroy()
                        F=Frame(MS)
                        Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,In=In : BmenocommandscrollE(MS,superi,In)).pack(side=LEFT)
                        L=Label(F, text=f'spectrum {superi+1} of {len(In)}').pack(side=LEFT)
                        Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,In=In : BpiucommandscrollE(MS,superi,In)).pack(side=LEFT)
                        F.pack()
                        L=Label(MS).pack()
                        SC=Frame(MS)
                        SC.pack()
                        singlescreen_of_multiple(In[superi],SC)
                
                def BpiucommandscrollE(MS,superi,In):
                    if superi<len(In)-1:
                        superi+=1
                        cdn=MS.winfo_children()
                        for i in cdn:
                            i.destroy()
                        F=Frame(MS)
                        Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,In=In : BmenocommandscrollE(MS,superi,In)).pack(side=LEFT)
                        L=Label(F, text=f'spectrum {superi+1} of {len(In)}').pack(side=LEFT)
                        Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,In=In : BpiucommandscrollE(MS,superi,In)).pack(side=LEFT)
                        F.pack()
                        L=Label(MS).pack()
                        SC=Frame(MS)
                        SC.pack()
                        singlescreen_of_multiple(In[superi],SC)

                try:
                    superi = SPClist.curselection()[0]
                except IndexError:
                    superi = 0
                In = In[CB.get()]
                if len(In) > 0:
                    MS=Toplevel()
                    MS.title(f'{In[0].identity} peak list ({CB.get()})')
                    MS.resizable(False,False)
                    MS.focus()
                    F=Frame(MS)
                    Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,In=In : BmenocommandscrollE(MS,superi,In)).pack(side=LEFT)
                    L=Label(F, text=f'spectrum {superi+1} of {len(In)}').pack(side=LEFT)
                    Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,In=In : BpiucommandscrollE(MS,superi,In)).pack(side=LEFT)
                    F.pack()
                    L=Label(MS).pack()
                    SC=Frame(MS)
                    SC.pack()
                    singlescreen_of_multiple(In[superi],SC)
                
            def clear_spectra(SPCIn,SPClist,B,SBL,CB):
                g=len(SPCIn[CB.get()])
                for _ in range(g):
                    SPCIn[CB.get()].pop(0)
                SPClist.delete(0,END)
                B.configure(state='disable')
                
            def source_emission_selection(WN,selection,B):
                lsel = len(selection)
                for _ in range(lsel):
                    selection.pop(0)
                f=open('data/sources/'+WN.get()+'.sce','r')
                r=f.readlines()
                f.close()
                for gla in range(len(r)):
                    r[gla]=r[gla].replace('\n','')
                    r[gla]=r[gla].replace('\t',' ')
                    selection.append(r[gla])
                B.configure(state='disable')
                
            def viewSL(VWS,selection,B):
                def _on_mousewheel(self, event):#deprecated for the moment
                    canvas.yview_scroll(-1*(event.delta/120), "units")
                
                def push_selector(vb,cb,selection,B):
                    B.configure(state='disable')
                    if vb.get()=='':
                        selection.remove(cb.cget('onvalue'))
                    else:
                        if vb.get() not in selection:
                            selection.append(cb.cget('onvalue'))
                if VWS.get()!='':
                    f=open('data/sources/'+VWS.get()+'.sce','r')
                    r=f.readlines()
                    f.close()
                    for gla in range(len(r)):
                        r[gla]=r[gla].replace('\n','')
                        r[gla]=r[gla].replace('\t',' ')
                    dt=r[0]
                    r.pop(0)
                    TSCL=Toplevel()
                    TSCL.resizable(False,False)
                    TSCL.title('Source')
                    TSCL.focus()
                    F=Frame(TSCL)
                    L=Label(F, text='', width=1).pack(side=LEFT)
                    L=Label(F, text=f'certificate date: {dt}', anchor=W).pack(side=LEFT)
                    L=Label(F, width=5).pack(side=LEFT)
                    L=Label(F, text=VWS.get(), anchor=W).pack(side=LEFT)
                    F.pack(anchor=W)
                    L=Label(TSCL).pack()
                    F=Frame(TSCL)
                    L=Label(F, text='', width=6).pack(side=LEFT)
                    L=Label(F, text='energy / keV', width=12).pack(side=LEFT)
                    L=Label(F, text='nuclide', width=12).pack(side=LEFT)
                    L=Label(F, text='activity / Bq', width=12).pack(side=LEFT)
                    L=Label(F, text='γ yield / 1', width=12).pack(side=LEFT)
                    L=Label(F, text='half-life / s', width=12).pack(side=LEFT)
                    F.pack(anchor=W)
                    
                    container = Frame(TSCL)
                    canvas = Canvas(container, height=450)
                    scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
                    scrollable_frame = Frame(canvas)
                    
                    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                    canvas.configure(yscrollcommand=scrollbar.set)
                    
                    for item in r:
                        F=Frame(scrollable_frame)
                        var = StringVar(TSCL)
                        var.set('')
                        cb = Checkbutton(F, variable=var, onvalue=item, offvalue='', width=3)
                        cb.pack(side=LEFT)
                        if item in selection:
                            cb.select()
                        else:
                            cb.deselect()
                        cb.configure(command=lambda vb=var,cb=cb,selection=selection: push_selector(vb,cb,selection,B))
                        TT=str.split(item)
                        L=Label(F, text=f'{TT[0]}', width=12).pack(side=LEFT)
                        L=Label(F, text=f'{TT[1]}', width=12).pack(side=LEFT)
                        L=Label(F, text=f'{TT[2]}', width=12).pack(side=LEFT)
                        L=Label(F, text=f'{TT[3]}', width=12).pack(side=LEFT)
                        L=Label(F, text=f'{TT[4]}', width=12).pack(side=LEFT)
                        F.pack(anchor=W)
                    container.pack(fill="both", expand=True)
                    canvas.pack(side="left", fill="both", expand=True)
                    scrollbar.pack(side="right", fill="y")
                    canvas.bind("<MouseWheel>", lambda : _on_mousewheel(event))
                    
            def perform_fit(CB_detector,CB_energy,CB_fwhm,CB_efficiency,SPCIn,selection,SB_der,textB,B,fig,ax_plot,ax_res,canvas,res_energy,res_fwhm,res_efficiency,res_der,res_values,CB_source,CB_distance,C_posix):
                def display_text(text,textB):
                    textB.configure(state='normal')
                    textB.delete('0.0',END)
                    textB.insert(END,'\n'.join(text))
                    textB.configure(state='disabled')
                    
                def display_graphics(fig,ax_plot,ax_res,canvas,x,y,res,multiy,x_fit,y_fit,y_fit_others):
                    ax_plot.grid(False)
                    ax_res.grid(False)
                    h = len(ax_plot.lines)
                    for times in range(h):
                        ax_plot.lines.pop(0)
                    h = len(ax_res.lines)
                    for times in range(h):
                        ax_res.lines.pop(0)
                    ax_plot.plot(x, multiy, marker='s', markersize=3, markeredgewidth=0.5, markerfacecolor='b', color='k', linestyle='')
                    ax_plot.plot(x, y, marker='o', markersize=4, markeredgewidth=0.5, markerfacecolor='r', color='k', linestyle='')
                    ax_plot.plot(x_fit, y_fit_others, marker=None, color='k', linestyle='--', linewidth=0.5)
                    ax_plot.plot(x_fit, y_fit, marker=None, color='r', linestyle='-', linewidth=0.75)
                    ax_res.plot(x, res, marker='o', markersize=4, markeredgewidth=0.5, markerfacecolor='r', color='k', linestyle='')
                    
                    ax_plot.set_ylim(0,np.max(multiy)*1.03+0.00002)
                    mvl = np.max(np.abs(res))
                    ax_res.set_ylim(-mvl*1.1,mvl*1.1)
                    if np.max(x) > 2000:
                        ax_plot.set_xlim(0,3000)
                        ax_res.set_xlim(0,3000)
                    else:
                        ax_plot.set_xlim(0,2000)
                        ax_res.set_xlim(0,2000)
                    ax_plot.grid(True, which='major', axis='y', linestyle='-.', linewidth=0.4)
                    ax_res.grid(True, which='major', axis='y', linestyle='-.', linewidth=0.4)
                    fig.tight_layout()
                    canvas.draw()
                
                def get_source(selection):
                    dt=selection[0]
                    selections=selection[1:]
                    en,Tg,bql,GY,ld=[],[],[],[],[]
                    for line in selections:
                        try:
                            energy,tg,Bq,gY,lamb=str.split(line)
                            energy,Bq,gY,lamb=float(energy),float(Bq),float(gY),float(np.log(2)/float(lamb))
                        except:
                            break
                        else:
                            en.append(energy)
                            Tg.append(tg)
                            bql.append(Bq)
                            GY.append(gY)
                            ld.append(lamb)
                    GSC=GSource(dt,en,Tg,bql,GY,ld)
                    return GSC
                
                def get_data_to_fit(source,spectralist,C_posix):
                    def calculate_efficiency(n_area,spc,source,nn):
                        _lbd = source.decay_constant[nn]
                        td = spc.datetime - source.datetime
                        td = td.days*86400 + td.seconds
                        return (n_area*_lbd*spc.real_time)/(spc.live_time*np.exp(-_lbd*td)*(1-np.exp(-_lbd*spc.real_time))*source.g_yield[nn]*source.activity[nn])
                    
                    fit_ch = [] #mean(axis=1)
                    fit_en = [] #single
                    fit_fw = [] #mean(axis=1)
                    fit_efy = [] #mean(axis=1)
                    index = []
                    for nn,s_energy in enumerate(source.energy):
                        fit_ch_line = []
                        fit_en_line = []
                        fit_fw_line = []
                        fit_efy_line = []
                        for position in C_posix['values']:
                            emission_found = None
                            for spc in SPCIn[position]:
                                for plist_line in spc.peak_list:
                                    if float(plist_line[6])+float(tolerance_energy)>s_energy and float(plist_line[6])-float(tolerance_energy)<s_energy:
                                        if emission_found is None:
                                            emission_found = (s_energy, float(plist_line[4]), float(plist_line[10]), calculate_efficiency(float(plist_line[8]),spc,source,nn), float(plist_line[9])/float(plist_line[8]))
                                        else:
                                            if float(plist_line[9])/float(plist_line[8]) < emission_found[4]:
                                                emission_found = (s_energy, float(plist_line[4]), float(plist_line[10]), calculate_efficiency(float(plist_line[8]),spc,source,nn), float(plist_line[9])/float(plist_line[8]))
                            if emission_found is not None:
                                fit_en_line.append(emission_found[0])
                                fit_ch_line.append(emission_found[1])
                                fit_fw_line.append(emission_found[2])
                                fit_efy_line.append(emission_found[3])
                        if len(fit_en_line)==len(SPCIn.keys()):
                            fit_en.append(fit_en_line)
                            fit_ch.append(fit_ch_line)
                            fit_fw.append(fit_fw_line)
                            fit_efy.append(fit_efy_line)
                            index.append(nn)
                    fit_ch, fit_en, fit_fw, fit_efy = np.array(fit_ch), np.array(fit_en), np.array(fit_fw), np.array(fit_efy)
                    try:
                        fit_en = fit_en.mean(axis=1)
                    except IndexError:
                        pass
                    return fit_ch, fit_en, fit_fw, fit_efy, index
                
                def lineofsource(source,index):
                    line = f'{(str(source.energy[index])+" keV").ljust(13)}{source.emitter[index].rjust(8)}'
                    return line
                
                def fit_linear(X,Y):
                    W = X[:, np.newaxis]**[1,0]
                    I = np.identity(W.shape[0])
                    popt = np.linalg.inv(W.T@W)@(W.T@Y)
                    ress = Y - popt@W.T
                    n, k = Y.shape[0],W.shape[1]
                    pcov = np.linalg.inv((W.T@np.linalg.inv(np.true_divide(1,n-k)*np.dot(ress,ress)*I))@W)
                    return popt, pcov, ress
                
                def fit_quadratic(X,Y):
                    Y = np.power(Y,2)
                    W = X[:, np.newaxis]**[1,0]
                    I = np.identity(W.shape[0])
                    popt = np.linalg.inv(W.T@W)@(W.T@Y)
                    ress = Y - popt@W.T
                    n, k = Y.shape[0],W.shape[1]
                    pcov = np.linalg.inv((W.T@np.linalg.inv(np.true_divide(1,n-k)*np.dot(ress,ress)*I))@W)
                    return popt, pcov, ress
                
                def fit_6polynomial(X,Y,esp=[1, 0, -1, -2, -3, -4]):
                    X = X / 1000
                    Y = np.log(Y)
                    W = X[:, np.newaxis]**esp
                    I = np.identity(W.shape[0])
                    popt = np.linalg.inv(W.T@W)@(W.T@Y)
                    ress = Y - popt@W.T
                    n, k = Y.shape[0],W.shape[1]
                    pcov = np.linalg.inv((W.T@np.linalg.inv(np.true_divide(1,n-k)*np.dot(ress,ress)*I))@W)
                    return popt, pcov, ress
                
                def energy_fit_completition(fit_ch, fit_en, CB_energy, text):
                    X, X_std = fit_ch.mean(axis=1), np.max(fit_ch.std(axis=1))
                    fit = fits.get(CB_energy.get())
                    popt, pcov, _ = fit(X, fit_en)
                    perr = np.sqrt(np.diag(pcov))
                    pcorr = np.copy(pcov)
                    for ii in range(len(perr)):
                        for ij in range(len(perr)):
                            pcorr[ii,ij] = pcov[ii,ij] / (perr[ii] * perr[ij])
                    label = [f'p{i}:' for i in range(len(popt))]
                    text.append(f'Energy fit: {CB_energy.get()} model\n(evaluted averaging values for all spectra, max deviation {round(X_std,4)} channels)\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{(str(round(value,6))).ljust(11)}{(str(round(unc,6))).ljust(11)}({round(abs(unc/value)*100,2)} %)' for lbl, value, unc in zip(label,popt,perr)])+f'\n\n{"corr. M".ljust(9)}'+''.join([f'{lbl.ljust(9)}' for lbl in label])+'\n'+''.join([f'{lbl.ljust(9)}'+''.join([f'{str(round(col,4)).ljust(9)}' for col in row])+'\n' for lbl, row in zip(label,pcorr)]))
                    return popt
                
                def fwhm_fit_completition(fit_ch, fit_fw, CB_fwhm, text):
                    X, X_std = fit_ch.mean(axis=1), np.max(fit_ch.std(axis=1))
                    Y, Y_std = fit_fw.mean(axis=1), np.max(fit_fw.std(axis=1))
                    fit = fits.get(CB_fwhm.get())
                    popt, pcov, _ = fit(X, Y)
                    perr = np.sqrt(np.diag(pcov))
                    pcorr = np.copy(pcov)
                    for ii in range(len(perr)):
                        for ij in range(len(perr)):
                            pcorr[ii,ij] = pcov[ii,ij] / (perr[ii] * perr[ij])
                    label = [f'p{i}:' for i in range(len(popt))]
                    text.append(f'FWHM fit: {CB_fwhm.get()} model\n(evaluated averaging values for all spectra,\nmax deviation on X-axis variable {round(X_std,4)} channels\nmax deviation on Y-axis variable {round(Y_std,4)} channels)\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{(str(round(value,6))).ljust(11)}{(str(round(unc,6))).ljust(11)}({round(abs(unc/value)*100,2)} %)' for lbl, value, unc in zip(label,popt,perr)])+f'\n\n{"corr. M".ljust(9)}'+''.join([f'{lbl.ljust(9)}' for lbl in label])+'\n'+''.join([f'{lbl.ljust(9)}'+''.join([f'{str(round(col,4)).ljust(9)}' for col in row])+'\n' for lbl, row in zip(label,pcorr)]))
                    return popt
                
                def efficiency_fit_completition(fit_en, fit_efy, CB_efficiency, text):
                    def zerodivision(unc,value,default='-'):
                        try:
                            return f'{round(abs(unc/value)*100,2)}'
                        except ZeroDivisionError:
                            return default
                        
                    def zerodivision_matrix(pcov,perr1,perr2,default=0):
                        try:
                            return pcov / (perr1 * perr2)
                        except ZeroDivisionError:
                            return default
                        
                    Y, Y_std = fit_efy.mean(axis=1), np.max(fit_efy.std(axis=1)/fit_efy.mean(axis=1))
                    fit = fits.get(CB_efficiency.get())
                    esp = [1, 0, -1, -2, -3, -4]
                    popt, pcov, res = fit(fit_en, Y)
                    perr = np.sqrt(np.diag(pcov))
                    vmax = np.argmax(np.abs(perr/popt)) 
                    if np.abs(perr/popt)[vmax] > float(visual):
                        esp = [1, 0, -1, -2, -3]
                        popt, pcov = np.zeros(6), np.zeros((6,6))
                        popt_v, pcov_v, res = fit(fit_en, Y, esp)
                        perr = np.sqrt(np.diag(pcov_v))
                        vmax = np.argmax(np.abs(perr/popt_v)) 
                        if np.abs(perr/popt_v)[vmax] > float(visual):
                            esp = [1, 0, -1, -2]
                            popt, pcov = np.zeros(6), np.zeros((6,6))
                            popt_v, pcov_v, res = fit(fit_en, Y, esp)
                            perr = np.sqrt(np.diag(pcov_v))
                            vmax = np.argmax(np.abs(perr/popt_v)) 
                            if np.abs(perr/popt_v)[vmax] > float(visual):
                                popt, pcov = None, None
                            else:
                                popt[:len(popt_v)] = popt_v
                                pcov[:len(pcov_v),:len(pcov_v)] = pcov_v
                        else:
                            popt[:len(popt_v)] = popt_v
                            pcov[:len(pcov_v),:len(pcov_v)] = pcov_v
                    perr = np.sqrt(np.diag(pcov))
                    h_curve, l_curve = None, None
                    ord_res = np.flip(np.argsort(np.abs(res)))
                    if popt is not None and pcov is not None:
                        x_fitgraphs = np.linspace(np.min(fit_en),np.max(fit_en),300)
                        W = x_fitgraphs / 1000
                        W = W[:, np.newaxis]**esp
                        fits_for_single_data = []
                        ppoints_for_single_data = []
                        pcovs_for_single_data = []
                        for points_fit in fit_efy.T:
                            p_points, p_pcov, _ = fit(fit_en, points_fit, esp)
                            ppoints_for_single_data.append(p_points)
                            pcovs_for_single_data.append(p_pcov)
                            fits_for_single_data.append(np.exp(p_points@W.T))
                        fits_for_single_data = np.array(fits_for_single_data)
                        fits_for_single_data = fits_for_single_data.T
                        y_averaged_fit = np.exp(popt[:len(esp)]@W.T)
                        display_graphics(fig,ax_plot,ax_res,canvas,fit_en,Y,100*res,fit_efy,x_fitgraphs,y_averaged_fit,fits_for_single_data)
                        pcorr = np.copy(pcov)
                        for ii in range(len(perr)):
                            for ij in range(len(perr)):
                                pcorr[ii,ij] = zerodivision_matrix(pcov[ii,ij],perr[ii],perr[ij])
                        Q = np.array([0.13])
                        Q = Q[:,np.newaxis]**esp
                        tempo = [float(np.exp(p_parameters@Q.T)) for p_parameters in ppoints_for_single_data]
                        h_curve, l_curve, h_pcov, l_pcov = ppoints_for_single_data[tempo.index(np.max(tempo))], ppoints_for_single_data[tempo.index(np.min(tempo))], pcovs_for_single_data[tempo.index(np.max(tempo))], pcovs_for_single_data[tempo.index(np.min(tempo))]
                        dropd = ['',' (p5)',' (p4 and p5)']
                        label = [f'p{i}:' for i in range(len(popt))]
                        text.append(f'Efficiency fit: {CB_efficiency.get()} model\n(evaluated averaging values for all spectra, max deviation {round(Y_std*100,1)} % efficiency)\n{6-len(esp)} parameters{dropd[int(6-len(esp))]} were dropped due to higher uncertainty than the {int(float(visual)*100)} % value set by the user\n{"".ljust(6)}{"value".ljust(11)}{"u (k=1)".ljust(11)}rel. u\n'+'\n'.join([f'{lbl.ljust(6)}{(str(round(value,6))).ljust(11)}{(str(round(unc,6))).ljust(11)}({zerodivision(unc,value)} %)' for lbl, value, unc in zip(label,popt,perr)])+f'\n\n{"corr. M".ljust(9)}'+''.join([f'{lbl.ljust(9)}' for lbl in label])+'\n'+''.join([f'{lbl.ljust(9)}'+''.join([f'{str(round(col,4)).ljust(9)}' for col in row])+'\n' for lbl, row in zip(label,pcorr)])+f'\n{"energy".ljust(13)}{"isotope".rjust(8)}{"efficiency".rjust(12)}{"residual".rjust(10)}\n'+'\n'.join([lines[i_res]+f'{str((round(Y[i_res],6))).rjust(12)}{(str(round(100*res[i_res],2))+" %").rjust(10)}' for i_res in ord_res])+'\n')
                    else:
                        text.append(f'Efficiency fit: {CB_efficiency.get()} model\n(evaluated averaging values for all spectra, max deviation {round(Y_std,4)} efficiency)\nFit aborted due to high uncertainty obtained for parameters: greater than the {int(float(visual)*100)} % value set by the user.\n')
                    return (popt, pcov), h_curve, l_curve, h_pcov, l_pcov
                
                def der_calculation(SPCIn,h_curve,l_curve,p_parameters,SB_der,text,h_pcov,l_pcov,lowend=50,highend=3103,default_uder=0.2):
                    p_parameters, p_rescov = p_parameters
                    x_range = np.array([lowend,highend])
                    x_range = x_range / 1000
                    esp = [1,0,-1,-2,-3,-4]
                    if len(SPCIn) > 1:
                        try:
                            inter_distance = float(SB_der.get())
                            comp = f'{inter_distance} mm'
                            if inter_distance == 0:
                                inter_distance = 0.1
                                comp = f'{inter_distance} mm (fallback to default value since the user selection was {SB_der.get()})'
                        except:
                            inter_distance = 0.1
                            comp = f'{inter_distance} mm (fallback to default value since the user selection was {SB_der.get()})'
                        x_range = x_range[:,np.newaxis]**esp[:len(h_curve)]
                        der = np.array((np.exp(h_curve@x_range.T) - np.exp(l_curve@x_range.T))/(np.exp(p_parameters[:len(h_curve)]@x_range.T) * inter_distance))
                        uderpcov = np.identity(19)
                        uderpcov[0:len(h_pcov),0:len(h_pcov)] = h_pcov
                        uderpcov[6:6+len(l_pcov),6:6+len(l_pcov)] = l_pcov
                        uderpcov[12:12+len(p_rescov),12:12+len(p_rescov)] = p_rescov
                        uderpcov[18,18] = 0.01
                        udererr = np.sqrt(np.diag(uderpcov))
                        uderparams = [0]*18
                        uderparams.append(inter_distance)
                        uderparams = np.array(uderparams)
                        uderparams[0:0+len(h_curve)] = h_curve
                        uderparams[6:6+len(l_curve)] = l_curve
                        uderparams[12:12+len(p_parameters)] = p_parameters
                        uder = []
                        for energypin in x_range:
                            ci_arrary = []
                            for i in range(len(uderparams)):
                                copyp = uderparams[:]
                                copym = uderparams[:]
                                copyp[i] = uderparams[i] + udererr[i]
                                copym[i] = uderparams[i] - udererr[i]
                                v = (((np.exp(copyp[:len(h_curve)]@energypin) - np.exp(copyp[6:6+len(h_curve)]@energypin))/(np.exp(copyp[12:12+len(h_curve)]@energypin) * inter_distance)) - ((np.exp(copym[:len(h_curve)]@energypin) - np.exp(copym[6:6+len(h_curve)]@energypin))/(np.exp(copym[12:12+len(h_curve)]@energypin) * inter_distance))) / (2*udererr[i]+1E-9)
                                ci_arrary.append(v)
                            ci_arrary = np.array(ci_arrary)
                            uder.append(ci_arrary.T@uderpcov@ci_arrary)
                        uder = np.array(uder)
                        kind = 'calculus'
                        text.append(f'Vertical variability of detection efficiency calculated on multiple spectra for distance among farthest samples of {comp}\nextremes:\nfrom {lowend} keV with {round(der[0]*100,2)} % efficiency variation per mm\nto {highend} keV with {round(der[-1]*100,2)} % efficiency variation per mm\n')
                        der = inter_distance
                        uder = 0
                    else:
                        try:
                            default_der = float(SB_der.get())
                        except:
                            default_der = 0.0
                        der = default_der
                        uder = der * default_uder
                        kind = 'default'
                        text.append(f'Vertical variability of detection efficiency assumed equal to the user assigned value of {round(100*default_der,2)} % efficiency variation per mm throughout the energy range considered, from {lowend} keV to {highend} keV\n')
                    return der, uder, kind
                
                text = []
                fits = {'linear':fit_linear, 'quadratic':fit_quadratic, '6term-polynomial':fit_6polynomial}
                check_mix = [item_value for dict_value in SPCIn.values() for item_value in dict_value]
                if CB_detector.get()!='' and len(check_mix)>0 and len(selection)>7:
                    try:
                        ddist = float(CB_distance.get())
                    except ValueError:
                        ddist = -1
                    positional = [f'{c_position} ('+', '.join([spc.filename() for spc in SPCIn[c_position]])+')' for c_position in C_posix['values']]
                    text.append(f'Calibration performed on {CB_detector.get()} detector, at nominal distance {ddist} mm.\n\n{len(SPCIn.keys())} positions selected to acquire {CB_source.get()} source over {len(check_mix)} spectra:\n'+'\n'.join(positional)+'\n')#[spc.filename() for pos in for spc in SPCIn[pos]])+'\n')
                    Cal_source = get_source(selection)
                    fit_ch, fit_en, fit_fw, fit_efy, nn = get_data_to_fit(Cal_source,SPCIn,C_posix)
                    lines = [lineofsource(Cal_source,ii) for ii in nn]
                    if len(fit_en)>6:
                        text.append(f'{len(fit_en)} of the selected emissions were found in the spectra:\n'+'\n'.join(lines)+'\n')
                        for hh in range(len(res_values)):
                            res_values.pop(0)
                        res_values_1, res_values_2 = (fit_en, fit_efy.mean(axis=1))
                        for value in (res_values_1, res_values_2):
                            res_values.append(value)
                        
                        for hh in range(len(res_energy)):
                            res_energy.pop(0)
                        res_energy_1 = energy_fit_completition(fit_ch, fit_en, CB_energy, text)
                        for value in (res_energy_1,):
                            res_energy.append(value)
                        
                        for hh in range(len(res_fwhm)):
                            res_fwhm.pop(0)
                        res_fwhm_1 = fwhm_fit_completition(fit_ch, fit_fw, CB_fwhm, text)
                        for value in (res_fwhm_1,):
                            res_fwhm.append(value)
                        
                        for hh in range(len(res_efficiency)):
                            res_efficiency.pop(0)
                        res_efficiency_tuple, h_curve, l_curve, h_pcov, l_pcov  = efficiency_fit_completition(fit_en, fit_efy, CB_efficiency, text)
                        for value in res_efficiency_tuple:
                            res_efficiency.append(value)
                        
                        hotkeys = [key for key in res_der.keys()]
                        for hkey in hotkeys:
                            res_der.pop(hkey)
                        if res_efficiency[0] is not None:
                            res_der_2, res_uder, kind = der_calculation(SPCIn,h_curve,l_curve,res_efficiency,SB_der,text,h_pcov,l_pcov)
                            B.configure(state='normal')
                            for descriptor, value in zip(('h_curve','l_curve','h_pcov','l_pcov','delta','udelta','kind'),(h_curve, l_curve, h_pcov, l_pcov, res_der_2, res_uder, kind)):
                                res_der[descriptor] = value
                        else:
                            pass
                    else:
                        text.append(f'Fit is aborted since less than 7 of the selected emissions were found in the spectra: {len(fit_en)} found\n'+'\n'.join(lines)+'\n')
                    
                else:
                    text.append('Insert all the required information:\n- name of the detector\n- calibration spectra files\n- name of source certificate and select more than 7 emissions\n')

                display_text(text,textB)
                
            def save_calibration(res_energy,res_fwhm,res_efficiency,res_der,res_values,CB_detector,CB_energy,CB_fwhm,CB_efficiency,SPCIn,selection,SB_geo,textB,fn):
                def thatshowitsdone(CB_master,CB_std,CB_sample):
                    with open('data/efficiencies/'+fn.get()+'.efs','w') as f:
                        f.write(f'detector: {CB_detector.get()}\ngeometry: {SB_geo.get()}\nenergy: {CB_energy.get()}\n{" ".join([str(ene) for ene in res_energy[0]])}\nfwhm: {CB_fwhm.get()}\n{" ".join([str(fwh) for fwh in res_fwhm[0]])}\nefficiency: {CB_efficiency.get()}\n{" ".join([str(eff) for eff in res_efficiency[0]])}\ncov_matrix:\n'+'\n'.join([' '.join([f'{col}' for col in row]) for row in res_efficiency[1]])+f'\nder_kind: {res_der["kind"]}\nder_value: {res_der["delta"]}\nder_uvalue: {res_der["udelta"]}\nder_h_curve:\n{" ".join([str(derp) for derp in res_der["h_curve"]])}\nder_h_curve_pcov:\n'+'\n'.join([' '.join([f'{col}' for col in row]) for row in res_der["h_pcov"]])+f'\nder_l_curve:\n{" ".join([str(derp) for derp in res_der["l_curve"]])}\nder_l_curve_pcov:\n'+'\n'.join([' '.join([f'{col}' for col in row]) for row in res_der["l_pcov"]])+f'\ncertificate: {selection.get()}\nx_points:\n{" ".join([f"{xpt}" for xpt in res_values[0]])}\ny_points:\n{" ".join([f"{ypt}" for ypt in res_values[1]])}\nspectra:\n'+'\n'.join([spectrum.filename() for spectrum in [item_value for dict_value in SPCIn.values() for item_value in dict_value]]))
                    with open('data/efficiencies/'+fn.get()+'_log.txt','w') as f:
                        f.write(textB.get('0.0',END))
                    CBeff_values = listeffy()
                    CB_master['values'] = CBeff_values
                    #CB_std['values'] = CBeff_values
                    #CB_sample['values'] = CBeff_values
                    if CB_detector.get() not in CB_detector['values']:
                        newvalues = [item for item in CB_detector['values']]
                        newvalues.append(CB_detector.get())
                        CB_detector['values'] = newvalues
                        with open('data/channels/detlist.txt','a') as f:
                            f.write(f'{CB_detector.get()}\n')
                    messagebox.showinfo('Calibration saved', f'Calibration: {fn.get()+".efs"}\nand\nlog: {fn.get()+"_log.txt"}\nsaved in folder "efficiencies"')
                if fn.get()!='':
                    if os.path.exists('data/efficiencies/'+fn.get()+'.efs'):
                        if messagebox.askokcancel('Save calibration', f'A file called {fn.get()} already exists.\nDo you want to overwrite it?'):
                            thatshowitsdone(CB_master,CB_std,CB_sample)
                    else:
                        thatshowitsdone(CB_master,CB_std,CB_sample)
                else:
                    messagebox.showinfo('Save calibration', 'Select filename')
            
            MTL=Toplevel()
            MTL.title('Calibration')
            MTL.resizable(False,False)
            MTL.spectra_list = {} #spectra_list dict of lists, key is the name of counting position : value is a list of spectum objects
            MTL.selection_sources = []
            MTL.res_energy = []
            MTL.res_fwhm = []
            MTL.res_efficiency = [] #2value tuple(parameters,matrix)
            MTL.res_der = {} #dictionary
            MTL.res_values = [] #2value tuple(x_values, y_values)
            
            F_commands = Frame(MTL)
            F_graphs = Frame(MTL)
            
            F = Frame(F_commands)
            L=Label(F, text='name', width=10, anchor=W).pack(side=LEFT)
            E_geometry = Entry(F, width=25)
            E_geometry.pack(side=LEFT)
            L=Label(F, text='', width=7).pack(side=LEFT)
            L=Label(F, text='detector', width=10, anchor=W).pack(side=LEFT)
            detlistvalues = initialization('data/channels/detlist.txt')
            CB_detector = ttk.Combobox(F, width=16, values=detlistvalues)
            CB_detector.pack(side=LEFT)            
            L=Label(F, text='', width=7).pack(side=LEFT)
            L=Label(F, text='distance / mm', width=12, anchor=W).pack(side=LEFT)
            SB_geometry = Spinbox(F, width=8, from_=-1, to=500, increment=1)
            SB_geometry.pack(side=LEFT)
            F.pack(anchor=W, padx=5, pady=5)
            
            F = Frame(F_commands)
            L=Label(F, text='energy fit', width=12, anchor=W).pack(side=LEFT)
            values_energy=['linear']
            CB_model = ttk.Combobox(F, width=14, values=values_energy, state='readonly')
            CB_model.pack(side=LEFT)
            CB_model.set(values_energy[0])
            lin = PhotoImage(file=f"data/models/{CB_model.get()}.png")
            LE_figure = Label(F, image=lin)
            LE_figure.pack(side=LEFT)
            LE_figure.logo = lin
            F.pack(anchor=W, padx=5, pady=5)
            
            F = Frame(F_commands)
            L=Label(F, text='fwhm fit', width=12, anchor=W).pack(side=LEFT)
            values_fwhm=['quadratic']
            CB_Fmodel = ttk.Combobox(F, width=14, values=values_fwhm, state='readonly')
            CB_Fmodel.pack(side=LEFT)
            CB_Fmodel.set(values_fwhm[0])
            fwh = PhotoImage(file=f"data/models/{CB_Fmodel.get()}.png")
            LF_figure = Label(F, image=fwh)
            LF_figure.pack(side=LEFT)
            LF_figure.logo = fwh
            F.pack(anchor=W, padx=5, pady=5)
            
            F = Frame(F_commands)
            L=Label(F, text='efficiency fit', width=12, anchor=W).pack(side=LEFT)
            values_eff=['6term-polynomial']
            CB_EFmodel = ttk.Combobox(F, width=14, values=values_eff, state='readonly')
            CB_EFmodel.pack(side=LEFT)
            CB_EFmodel.set(values_eff[0])
            eff = PhotoImage(file=f"data/models/{CB_EFmodel.get()}.png")
            LEF_figure = Label(F, image=eff)
            LEF_figure.pack(side=LEFT)
            LEF_figure.logo = eff
            F.pack(anchor=W, padx=5, pady=3)
            
            F = Frame(F_commands)
            F.pack(anchor=W, padx=5, pady=5)
            F = Frame(F_commands)
            L=Label(F, text='spectra', anchor=W, width=12).pack(side=LEFT)
            values_positions = ['position 1']
            CB_positions = ttk.Combobox(F, width=12, values=values_positions, state='readonly')
            CB_positions.pack(side=LEFT, padx=3)
            CB_positions.set(values_positions[0])
            B_add_position = Button(F, text='Add', width=8)
            B_add_position.pack(side=LEFT)
            B_rename_position = Button(F, text='Rename', width=8)
            B_rename_position.pack(side=LEFT)
            B_delete_position = Button(F, text='Delete', width=8)
            B_delete_position.pack(side=LEFT)
            F.pack(anchor=W, padx=5, pady=2)
            F.pack(anchor=W, padx=5, pady=2)
            BigBox = Frame(F_commands)
            ListFrame = Frame(BigBox)
            scrollbar = Scrollbar(ListFrame, orient=VERTICAL)
            listbox = Listbox(ListFrame, heigh=7, yscrollcommand=scrollbar.set)
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
            listbox.pack(side=LEFT, fill=BOTH, expand=1)
            ListFrame.pack(side=LEFT, anchor=NW, fill=BOTH, expand=1)
            MTL.spectra_list[CB_positions.get()] = []
            
            Buttoncolumn = Frame(BigBox)
            Buttoncolumns = Frame(Buttoncolumn)
            Buttoncolumn1 = Frame(Buttoncolumns)
            B_add = Button(Buttoncolumn1, text='Add', width=15)
            B_add.pack()
            B_pklist = Button(Buttoncolumn1, text='Peak list', width=15)
            B_pklist.pack()
            B_clear = Button(Buttoncolumn1, text='Clear', width=15)
            B_clear.pack()
            Buttoncolumn1.pack(side=LEFT, anchor=NW)
            Buttoncolumnhalf = Frame(Buttoncolumns)
            Buttoncolumnhalf.pack(side=LEFT, padx=2)
            Buttoncolumn2 = Frame(Buttoncolumns)
            L = Label(Buttoncolumn2, text='source', anchor=W).pack(anchor=W)
            values_sources = [gk[:-4] for gk in os.listdir('data/sources') if gk[-4:]=='.sce']
            CB_source = ttk.Combobox(Buttoncolumn2, values=values_sources, state='readonly')
            CB_source.pack(fill=X)
            B_select = Button(Buttoncolumn2, text='Select emissions', width=15)
            B_select.pack()
            F_d = Frame(Buttoncolumn2)
            Line = Label(F_d, text='')
            Line.pack(side=LEFT)
            SB_der = Spinbox(F_d, from_=0, to=100, increment=1, width=5)
            SB_der.pack(side=LEFT, padx=5, pady=5)
            F_d.pack(anchor=E)
            Buttoncolumn2.pack(side=RIGHT, anchor=NE)
            Buttoncolumns.pack()
            F = Frame(Buttoncolumn)
            F.pack(pady=2)
            B_fit = Button(Buttoncolumn, text='Compute', width=18)
            B_fit.pack()
            Buttoncolumn.pack(side=RIGHT, anchor=NE)
            BigBox.pack(anchor=W, padx=5,fill=X)
            
            F = Frame(F_commands)
            F.pack(pady=6)
            L = Label(F_commands, text='log', anchor=W).pack(padx=5, anchor=W)
            LogBox = Frame(F_commands)
            scrollbar_text = Scrollbar(LogBox, orient=VERTICAL)
            textbox = Text(LogBox, heigh=8, yscrollcommand=scrollbar_text.set, wrap=WORD)
            scrollbar_text.config(command=textbox.yview)
            scrollbar_text.pack(side=RIGHT, fill=Y)
            textbox.pack(side=LEFT, fill=BOTH, expand=1)
            LogBox.pack(anchor=W, padx=5, fill=X)
            textbox.configure(state='disable')
            F = Frame(F_commands)
            B_save = Button(F, text='Save', width=10, state='disable')
            B_save.pack()
            F.pack(padx=5, pady=7, anchor=W)
            
            f = Figure(figsize=(5, 5))
            ax_plot=f.add_subplot(211)
            ax_res=f.add_subplot(212)
            Figur=Frame(F_graphs)
            Figur.pack(anchor=CENTER, fill=BOTH, expand=1)
            canvas = FigureCanvasTkAgg(f, master=Figur)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            
            ax_plot.set_xlim(0,2000)
            ax_res.set_xlim(0,2000)
            ax_plot.set_ylabel(r'$\varepsilon$ / 1')
            ax_res.set_ylabel(r'rel. residuals / $\%$')
            ax_res.set_xlabel(r'$E$ / keV')
            f.tight_layout()
            canvas.draw()
            
            F_commands.pack(side=LEFT, anchor=NW)
            F_graphs.pack(side=RIGHT, anchor=N)
            MTL.focus()
            
            #commands!
            CB_model.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>', CB=CB_model,L=LE_figure,B=B_save : update_figure_model(CB,L,B))
            CB_Fmodel.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>', CB=CB_Fmodel,L=LF_figure,B=B_save : update_figure_model(CB,L,B))
            CB_EFmodel.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>', CB=CB_EFmodel,L=LEF_figure,B=B_save : update_figure_model(CB,L,B))
            CB_detector.bind('<FocusIn>', lambda event='<FocusIn>',B=B_save : B.configure(state='disable'))
            SB_geometry.bind('<FocusIn>', lambda event='<FocusIn>',B=B_save : B.configure(state='disable'))
            SB_geometry.configure(command= lambda B=B_save : B.configure(state='disable'))
            SB_der.bind('<FocusIn>', lambda event='<FocusIn>',B=B_save : B.configure(state='disable'))
            SB_der.configure(command= lambda B=B_save : B.configure(state='disable'))
            
            B_rename_position.configure(command=lambda SPCIn=MTL.spectra_list,C_posix=CB_positions: rename_position(SPCIn,C_posix))
            B_delete_position.configure(command=lambda SPCIn=MTL.spectra_list,SPClist=listbox,C_posix=CB_positions,SBD=SB_der,SBL=Line : delete_position(SPCIn,SPClist,C_posix,SBD,SBL))
            CB_positions.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>', CB=CB_positions,SPCIn=MTL.spectra_list,SPClist=listbox : update_spectralist_by_position(CB,SPCIn,SPClist))
            CB_source.bind('<<ComboboxSelected>>', lambda event='<<ComboboxSelected>>',WN=CB_source,selection=MTL.selection_sources,B=B_save: source_emission_selection(WN,selection,B))
            B_add_position.configure(command=lambda SPCIn=MTL.spectra_list,SPClist=listbox,C_posix=CB_positions,SBD=SB_der,SBL=Line : add_position(SPCIn,SPClist,C_posix,SBD,SBL))
            B_select.configure(command=lambda VWS=CB_source,selection=MTL.selection_sources,B=B_save : viewSL(VWS,selection,B))
            B_add.configure(command=lambda SPCIn=MTL.spectra_list,SPClist=listbox,unclimit=unclimit_calib,setforall=True,B=B_save,SBL=Line,SBD=SB_der,C_posix=CB_positions : add_spectra(SPCIn,SPClist,unclimit,setforall,B,SBL,SBD,C_posix))#NAA.limit, NAA.set_true_forall
            B_pklist.configure(command=lambda SPCIn=MTL.spectra_list,SPClist=listbox,CB=CB_positions : display_peaklist(SPCIn,SPClist,CB))
            B_clear.configure(command=lambda SPCIn=MTL.spectra_list,SPClist=listbox,B=B_save,SBL=Line,CB=CB_positions : clear_spectra(SPCIn,SPClist,B,SBL,CB))
            B_fit.configure(command= lambda CB_detector=CB_detector,CB_energy=CB_model,CB_fwhm=CB_Fmodel,CB_efficiency=CB_EFmodel,SPCIn=MTL.spectra_list,selection=MTL.selection_sources,SB_der=SB_der,textB=textbox,B=B_save,fig=f,ax_plot=ax_plot,ax_res=ax_res,canvas=canvas,res_energy=MTL.res_energy,res_fwhm=MTL.res_fwhm,res_efficiency=MTL.res_efficiency,res_der=MTL.res_der,res_values=MTL.res_values,CB_source=CB_source,CB_distance=SB_geometry,C_posix=CB_positions : perform_fit(CB_detector,CB_energy,CB_fwhm,CB_efficiency,SPCIn,selection,SB_der,textB,B,fig,ax_plot,ax_res,canvas,res_energy,res_fwhm,res_efficiency,res_der,res_values,CB_source,CB_distance,C_posix))
            B_save.configure(command= lambda res_energy=MTL.res_energy,res_fwhm=MTL.res_fwhm,res_efficiency=MTL.res_efficiency,res_der=MTL.res_der,res_values=MTL.res_values,CB_detector=CB_detector,CB_energy=CB_model,CB_fwhm=CB_Fmodel,CB_efficiency=CB_EFmodel,SPCIn=MTL.spectra_list,selection=CB_source,SB_geo=SB_geometry,textB=textbox,fn=E_geometry: save_calibration(res_energy,res_fwhm,res_efficiency,res_der,res_values,CB_detector,CB_energy,CB_fwhm,CB_efficiency,SPCIn,selection,SB_geo,textB,fn))
            
        def showfit(box):
            """Show fits"""
            def get_log(filename):
                try:
                    with open(f'data/efficiencies/{filename}_log.txt') as f:
                        r = f.read()
                except:
                    r = None
                    print(f'{filename}_log.txt log file unreadable or missing')
                return r
            
            if box.get()!='':
                CalB = Calibration(box.get())
                log_text = get_log(box.get())
                x_limit = 2000
                if np.max(CalB.x_points) > 2000:
                    x_limit = 3000
                x_E = np.linspace(50,3100,1000)
                
                TL=Toplevel()
                TL.title('Calibration result - '+box.get())
                TL.resizable(False,False)
                text_frame = Frame(TL)
                graph_frame = Frame(TL)
                
                if log_text is not None:
                    scrollbar_text = Scrollbar(text_frame, orient=VERTICAL)
                    textbox = Text(text_frame, width=75, heigh=20, yscrollcommand=scrollbar_text.set, wrap=WORD)
                    scrollbar_text.config(command=textbox.yview)
                    scrollbar_text.pack(side=RIGHT, fill=Y)
                    textbox.pack(side=LEFT, fill=BOTH, expand=1)
                    text_frame.pack(side=LEFT, anchor=NW, padx=5, pady=5, fill=BOTH)
                    textbox.insert(END, log_text)
                    textbox.configure(state='disable')
                
                f = Figure(figsize=(5.8, 6.5))
                ax_up=f.add_subplot(311)
                ax_middle=f.add_subplot(312)
                ax_down=f.add_subplot(313)
                Figur=Frame(graph_frame)
                Figur.pack(anchor=CENTER, fill=BOTH, expand=1)
                canvas = FigureCanvasTkAgg(f, master=Figur)
                canvas.draw()
                canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
                ax_up.plot(x_E, CalB.efficiency_fit(x_E), marker='', linestyle='-', linewidth=0.75, color='b')
                ax_up.plot(CalB.x_points, CalB.y_points, marker='o', markersize=3, markerfacecolor='r', linestyle='', markeredgewidth=0.5, color='k')
                ax_up.set_xlim(0,x_limit)
                ax_up.set_ylim(0,None)
                ax_up.set_ylabel(r'$\varepsilon$ / 1')
                ax_up.grid(True, linestyle='-.')
                
                y_range = CalB.efficiency_fit(CalB.x_points)
                y_range = (CalB.y_points - y_range) * 100 / y_range
                ax_middle.axhline(y=0, xmin=50/x_limit, linestyle='-', linewidth=0.75, color='b')
                ax_middle.plot(CalB.x_points, y_range, marker='o', markersize=3, markerfacecolor='r', linestyle='', markeredgewidth=0.5, color='k')
                ax_middle.set_xlim(0,x_limit)
                ax_middle.set_ylabel(r'$\varepsilon_\mathrm{residual}$ / $\%$')
                ax_middle.grid(True, linestyle='-.')
                
                x_range = np.linspace(50,3100,300)
                der, uder = CalB.der_fit(x_range)
                ax_down.plot(x_range, der*100, marker='', linestyle='-', linewidth=0.75, color='b')
                ax_down.plot(x_range, (der+2*uder)*100, marker='', linestyle='--', linewidth=0.5, color='b')
                ax_down.plot(x_range, (der-2*uder)*100, marker='', linestyle='--', linewidth=0.5, color='b')
                ax_down.set_xlim(0,x_limit)
                ax_down.set_ylabel(r'$\delta\varepsilon_\mathrm{r}$ / $\%$ mm$^{-1}$')
                ax_down.set_xlabel(r'$E$ / keV')
                ax_down.grid(True, linestyle='-.')
                f.tight_layout()
                canvas.draw()
                graph_frame.pack(side=RIGHT, anchor=NE, padx=5, fill=BOTH)
                            
        def showspectrum(SC,S,B=None):
            def becamelog(ax,canvas,B):
                """Logarithm view of graph function"""
                if ax.get_yscale()=='linear':
                    ax.set_yscale('log', nonposy='clip')
                    B.configure(text='lin')
                else:
                    ax.set_yscale('linear')
                    B.configure(text='log')
                canvas.draw()
                
            def reset_command(ax,canvas,axis):
                """Reset the original view"""
                ax.axis(axis)
                canvas.draw()
                
            def on_scroll(event,ax,canvas,evx):
                """Scroll spectrum"""
                if event.xdata!=None and event.ydata!=None:
                    evx=evx.get()
                    if int(ax.get_xlim()[1]-ax.get_xlim()[0])!=evx:
                        try:
                            ax.set_xlim(int(event.xdata-evx/2),int(event.xdata+evx/2))
                        except ValueError:
                            pass
                        else:
                            canvas.draw()
                    elif int(ax.get_xlim()[1]-ax.get_xlim()[0])==evx:
                        try:
                            ax.set_xlim(int(ax.get_xlim()[0]+event.step*evx/6),int(ax.get_xlim()[1]+event.step*evx/6))
                        except ValueError:
                            pass
                        else:
                            canvas.draw()
                            
            def change_xticks(ax,canvas,B):
                """Change visualization unit of x axis"""
                if B.cget('text')=='keV':
                    ax.set_xticklabels(ticklabels)
                    ax.set_xlabel(r'$E$ / keV')
                    B.configure(text='ch')
                elif B.cget('text')=='ch':
                    ax.set_xticklabels(ticksint)
                    ax.set_xlabel('channel')
                    B.configure(text='keV')
                canvas.draw()
            
            def aggiungibackgroundinsicurezza(ax,canvas,S,B):
                """Add/drop background to the graph"""
                countsofthebackground=np.array(NAA.background.counts)
                countsofthebackground=(S.live_time/NAA.background.live_time)*countsofthebackground
                if len(ax.lines)==2:
                    ax.lines.pop()
                    B.configure(text='+BG')
                else:
                    ax.plot(np.linspace(0.5,len(countsofthebackground)+0.5,num=len(countsofthebackground)), countsofthebackground, marker='', linestyle='-', color='g', linewidth=0.5)
                    B.configure(text='-BG')
                canvas.draw()
                
            if S.counts!=None:
                class CustomToolbar(NavigationToolbar2TkAgg):
                    toolitems = filter(lambda x: x[0] != "Home", NavigationToolbar2TkAgg.toolitems)
                    toolitems = filter(lambda x: x[0] != "Back", toolitems)
                    toolitems = filter(lambda x: x[0] != "Forward", toolitems)
                TL=Toplevel(SC)
                TL.title('Spectrum')
                f = Figure(figsize=(6, 4))
                ax=f.add_subplot(111)
                ax.format_coord = lambda x, y: f'channel={int(x)}, counts={int(y)}'
                Figur=Frame(TL)
                Figur.pack(anchor=CENTER, fill=BOTH, expand=1)
                canvas = FigureCanvasTkAgg(f, master=Figur)
                canvas.draw()
                canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
                toolbar = CustomToolbar(canvas, Figur)
                toolbar.update()
                ax.plot(np.linspace(0.5,len(S.counts)+0.5,num=len(S.counts)), S.counts, marker='o', linestyle='-', color='k', linewidth=0.5, markersize=3, markerfacecolor='r')
                ax.set_ylabel('counts')
                ax.set_xlabel('channel')
                ticks=[]
                ticksint=[]
                ticklabels=[]
                for tyll in S.peak_list:
                    ticks.append(float(tyll[4]))
                    ticksint.append(int(float(tyll[4]).__round__(0)))
                    ticklabels.append(float(tyll[6]).__round__(1))
                ax.set_xticks(ticks)
                ax.set_xticklabels(ticksint)
                ax.grid(linestyle='-.')
                ax.set_xlim(0,len(S.counts))
                ax.set_ylim(1,max(S.counts)*3+2)
                ax.set_yscale('log', nonposy='clip')
                axis=ax.axis()
                f.tight_layout()
                canvas.draw()
                RESET=Button(TL, text='Reset', width=5, command=lambda ax=ax, canvas=canvas, axis=axis : reset_command(ax,canvas,axis))
                RESET.pack(side=LEFT)
                LOG=Button(TL, text='lin', width=3)
                LOG.configure(command=lambda ax=ax, canvas=canvas, B=LOG : becamelog(ax,canvas,B))
                LOG.pack(side=LEFT)
                if NAA.background!=None and S.identity!='Background':
                    BG=Button(TL, text='+BG', width=3)
                    BG.configure(command=lambda ax=ax, canvas=canvas, S=S, B=BG : aggiungibackgroundinsicurezza(ax,canvas,S,B))
                    BG.pack(side=LEFT)
                ECH=Button(TL, text='keV', width=3)
                ECH.configure(command=lambda ax=ax,canvas=canvas,B=ECH : change_xticks(ax,canvas,B))
                ECH.pack(side=LEFT)
                L=Label(TL, text='+', width=3, anchor=E).pack(side=LEFT)
                evx=Scale(TL, from_=40, to=320, resolution=40, showvalue=0, orient=HORIZONTAL)
                evx.pack(side=LEFT)
                evx.set(120)
                L=Label(TL, text='-').pack(side=LEFT)
                    
                cid=canvas.mpl_connect('scroll_event', lambda event='scroll_event',ax=ax,canvas=canvas,evx=evx : on_scroll(event,ax,canvas,evx))
                
        def altreemissioni(I,Ai,S,E,T):
            """Find other emissions"""
            listaltremissioni=[]
            listaltriisotopi=[]
            for t in A:
                if I==t[2] and Ai==t[3] and S==t[4] and E!=t[5]:
                    try:
                        PR=str((float(t[12])).__round__(1))+' %'
                    except ValueError:
                        PR=str(t[12])+' %'
                    lineemiss=str(t[5])+' keV,  '+PR
                    listaltremissioni.append(lineemiss)
                elif T==t[1] and Ai!=t[3]:
                    if t[4]==1.0:
                        g=''
                    else:
                        g='m'
                    lineemiss=str(t[2])+'-'+str(int(t[3]))+g+',  '+str(t[5])+' keV'
                    listaltriisotopi.append(lineemiss)
                elif T==t[1] and Ai==t[3] and S!=t[4]:
                    if t[4]==1.0:
                        g=''
                    else:
                        g='m'
                    lineemiss=str(t[2])+'-'+str(int(t[3]))+g+',  '+str(t[5])+' keV'
                    listaltriisotopi.append(lineemiss)
            return listaltremissioni,listaltriisotopi #to check
                
        def commandinfoemission(WN):
            """Emission information screen"""
            if WN.get()!='':
                nuc,ene=str.split(WN.get())
                N,Ai=str.split(nuc,'-')
                if Ai[-1]=='m':
                    Ai=Ai.replace('m','')
                    mg=2.0
                else:
                    mg=1.0
                ene=float(ene)
                Ai=float(Ai)
                for t in A:
                    if N==t[2] and Ai==t[3] and mg==t[4] and ene==t[5]:
                        target,Q0,uQ0,Er,uEr,nuclide_emissione,A_emissione,energia,k0,uk0,decaymode,douter_Z,douter_A,douter_state,douter_HF,douter_unit,father_Z,father_A,father_state,father_HF,father_unit,Gfather_Z,Gfather_A,Gfather_state,Gfather_HF,Gfather_unit,COI,probalitity,note1,note2,isot_N,isot_A=t[1],t[75],t[76],t[77],t[78],t[2],t[3],t[5],t[7],t[8],t[22],t[27],t[28],t[29],t[31],t[32],t[40],t[41],t[42],t[44],t[45],t[53],t[54],t[55],t[57],t[58],t[10],t[12],t[14],t[83],t[68],t[69]
                labels=['target','q','Q0','urQ0','Er','urEr','emitter','Ep','k0','urk0','half-life','decay:','cascade','nuclide','state','COI','γ yield','isotope']
                Tinfo=Toplevel()
                lines=nuclide_emissione+'-'+str(int(A_emissione))
                Tinfo.title('Information - '+lines)
                Tinfo.resizable(False,False)
                L=Label(Tinfo).pack()
                F=Frame(Tinfo)
                L=Label(F, text=labels[0], width=15).pack(side=LEFT)
                L=Label(F, text=labels[17], width=10).pack(side=LEFT)
                L=Label(F, text=labels[2], width=10).pack(side=LEFT)
                L=Label(F, text=labels[3], width=10).pack(side=LEFT)
                L=Label(F, text=labels[4], width=10).pack(side=LEFT)
                L=Label(F, text=labels[5], width=10).pack(side=LEFT)
                F.pack(anchor=W)
                F=Frame(Tinfo)
                L=Label(F, text=target, width=15).pack(side=LEFT)
                L=Label(F, text=isot_N+'-'+str(int(isot_A)), width=10).pack(side=LEFT)
                L=Label(F, text=str(Q0), width=10).pack(side=LEFT)
                if uQ0=='':
                    uQ0='20'
                L=Label(F, text=str(uQ0)[:5]+' %', width=10).pack(side=LEFT)
                L=Label(F, text=str(Er)+' eV', width=10).pack(side=LEFT)
                if uEr=='':
                    uEr='50'
                L=Label(F, text=str(uEr)[:5]+' %', width=10).pack(side=LEFT)
                F.pack(anchor=W)
                L=Label(Tinfo).pack()
                F=Frame(Tinfo)
                L=Label(F, text=labels[6], width=15).pack(side=LEFT)
                L=Label(F, text=labels[7], width=10).pack(side=LEFT)
                L=Label(F, text=labels[8], width=10).pack(side=LEFT)
                L=Label(F, text=labels[9], width=10).pack(side=LEFT)
                L=Label(F, text=labels[15], width=10).pack(side=LEFT)
                L=Label(F, text=labels[16], width=10).pack(side=LEFT)
                F.pack(anchor=W)
                F=Frame(Tinfo)
                L=Label(F, text=lines, width=15).pack(side=LEFT)
                L=Label(F, text=str(energia)+' keV', width=10).pack(side=LEFT)
                L=Label(F, text=str(k0), width=10).pack(side=LEFT)
                if uk0=='':
                    uk0='2'
                L=Label(F, text=str(uk0)+' %', width=10).pack(side=LEFT)
                if COI!=0:
                    coi='yes'
                else:
                    coi='no'
                L=Label(F, text=coi, width=10).pack(side=LEFT)
                L=Label(F, text=str(probalitity)+' %', width=10).pack(side=LEFT)
                F.pack(anchor=W)
                L=Label(Tinfo).pack()
                F=Frame(Tinfo)
                L=Label(F, text='', width=1).pack(side=LEFT)
                L=Label(F, text=labels[11], width=9).pack(side=LEFT)
                L=Label(F, text=decaymode, width=3).pack(side=LEFT)
                F.pack(anchor=W)
                F=Frame(Tinfo)
                L=Label(F, text='', width=1).pack(side=LEFT)
                L=Label(F, text=labels[12], width=10).pack(side=LEFT)
                F.pack(anchor=W)
                F=Frame(Tinfo)
                L=Label(F, text='', width=4).pack(side=LEFT)
                L=Label(F, text=labels[13], width=10).pack(side=LEFT)
                L=Label(F, text=labels[14], width=6).pack(side=LEFT)
                L=Label(F, text=labels[10], width=10).pack(side=LEFT)
                F.pack(anchor=W)
                cascade=[[Gfather_Z,Gfather_A,Gfather_state,Gfather_HF,Gfather_unit],[father_Z,father_A,father_state,father_HF,father_unit],[douter_Z,douter_A,douter_state,douter_HF,douter_unit]]
                for casc in cascade:
                    if casc[0]!='':
                        F=Frame(Tinfo)
                        L=Label(F, text='*', width=4).pack(side=LEFT)
                        nucld=casc[0]+'-'+str(int(casc[1]))
                        L=Label(F, text=nucld, width=10).pack(side=LEFT)
                        if casc[2]!=1:
                            gstate='m'
                        else:
                            gstate='g'
                        L=Label(F, text=gstate, width=6).pack(side=LEFT)
                        HL=str(casc[3])+' '+str(casc[4])
                        L=Label(F, text=HL, width=10).pack(side=LEFT)
                        F.pack(anchor=W)
                L=Label(Tinfo).pack()
                F=Frame(Tinfo)
                L=Label(F, text='', width=4).pack(side=LEFT)
                if cascade[-1][2]!=1:
                    GSTATE='m'
                else:
                    GSTATE=''
                L=Label(F, text='further emissions '+cascade[-1][0]+'-'+str(int(cascade[-1][1]))+GSTATE, width=22, anchor=W).pack(side=LEFT)
                L=Label(F, text='', width=12).pack(side=LEFT)
                L=Label(F, text='further emitters from target', width=22, anchor=W).pack(side=LEFT)
                F.pack(anchor=W)
                lst,lstiso=altreemissioni(cascade[-1][0],cascade[-1][1],cascade[-1][2],energia,target)
                F=Frame(Tinfo)
                L=Label(F, text='', width=4).pack(side=LEFT)
                BoxBoxBox=Frame(F)
                scrollbarListspectra = Scrollbar(BoxBoxBox, orient=VERTICAL)
                LBX=Listbox(BoxBoxBox, yscrollcommand=scrollbarListspectra.set, width=25, height=5)
                scrollbarListspectra.config(command=LBX.yview)
                LBX.pack(side=LEFT)
                scrollbarListspectra.pack(side=RIGHT, fill=Y)
                for k in lst:
                    LBX.insert(END, k)
                BoxBoxBox.pack(side=LEFT)
                L=Label(F, text='', width=10).pack(side=LEFT)
                BoxBoxBox=Frame(F)
                scrollbarListspectraiso = Scrollbar(BoxBoxBox, orient=VERTICAL)
                LBXiso=Listbox(BoxBoxBox, yscrollcommand=scrollbarListspectraiso.set, width=25, height=5)
                scrollbarListspectraiso.config(command=LBXiso.yview)
                LBXiso.pack(side=LEFT)
                scrollbarListspectraiso.pack(side=RIGHT, fill=Y)
                for k in lstiso:
                    LBXiso.insert(END, k)
                BoxBoxBox.pack(side=LEFT)
                F.pack(anchor=W)
                L=Label(Tinfo).pack()
                L=Label(Tinfo, text=' notes:').pack(anchor=W)
                if note1!='':
                    L=Label(Tinfo, text=note1, width=75, anchor=W).pack(anchor=W)
                if note2!='':
                    L=Label(Tinfo, text=note2, width=75, anchor=W).pack(anchor=W)
                L=Label(Tinfo).pack()
                Tinfo.focus()
                event="<FocusOut>"
                #Tinfo.bind(event,lambda event=event,M=Tinfo : M.destroy()) #Decomment this line for only on-focus info window
                
        def delete_preset_peakselection(preset):
            if preset.get()!='':
                try:
                    os.remove('data/presets/'+preset.get()+'.spl')
                except:
                    pass
                h=os.listdir('data/presets')
                values=[]
                for t in h:
                    if t[-4:]=='.spl':
                        values.append(t[:-4])
                values.append('')
                preset['values']=values
                preset.set('')
                
        def save_preset_peakselection(preset,NA):
            if preset.get()!='':
                workinglist=NA.assign_nuclide[:]
                while '' in workinglist:
                    workinglist.remove('')
                if workinglist!=[]:
                    with open('data/presets/'+preset.get()+'.spl','w') as f:
                        for wd in workinglist:
                            f.write(wd)
                            f.write('\n')
                    h=os.listdir('data/presets')
                    values=[]
                    for t in h:
                        if t[-4:]=='.spl':
                            values.append(t[:-4])
                    values.append('')
                    preset['values']=values
                else:
                    print('the current emissions selection is empty')
            else:
                print('the preset name field is empty')
                
        def propagate_selection(NA,NAS):
            workinglist=NA.assign_nuclide[:]
            while '' in workinglist:
                workinglist.remove('')
            workingenergylist=[]
            for i in workinglist:
                mid=str.split(i)
                workingenergylist.append(float(mid[-1]))
            if len(workingenergylist)>0:
                for i in NAS:
                    if i!=NA:
                        if i.assign_nuclide is None:
                            i.assign_nuclide=['']*len(i.peak_list)
                        for tiy in range(len(i.peak_list)):
                            if float(i.peak_list[tiy][6])>workingenergylist[0]-3 and float(i.peak_list[tiy][6])<workingenergylist[-1]+3:
                                for pp in range(len(workingenergylist)):
                                    if float(i.peak_list[tiy][6])-float(tolerance_energy)<workingenergylist[pp] and float(i.peak_list[tiy][6])+float(tolerance_energy)>workingenergylist[pp]:
                                        i.assign_nuclide[tiy]=workinglist[pp]
                                        break
            else:
                print('no emissions have been selected in the current peak list')
                
        def recall_emission_selection(F,paginazionepicchi,indice,NA,preset,NMS=None,Z=None):
            if preset.get()!='':
                try:
                    with open('data/presets/'+preset.get()+'.spl','r') as f:
                        r=f.readlines()
                    for t in range(len(r)):
                        r[t]=r[t].replace('\n','')
                except:
                    print(f'the selected {preset.get()} preset does not exist')
                else:
                    workingenergylist=[]
                    for i in r:
                        mid=str.split(i)
                        workingenergylist.append(float(mid[-1]))
                    for tiy in range(len(NA.peak_list)):
                        if float(NA.peak_list[tiy][6])>workingenergylist[0]-3 and float(NA.peak_list[tiy][6])<workingenergylist[-1]+3:
                            for pp in range(len(workingenergylist)):
                                if float(NA.peak_list[tiy][6])-float(tolerance_energy)<workingenergylist[pp] and float(NA.peak_list[tiy][6])+float(tolerance_energy)>workingenergylist[pp]:
                                    NA.assign_nuclide[tiy]=r[pp]
                                    break
                    if NA.identity=='Standard':
                        sciogliipicchicom(F,paginazionepicchi,indice,NA,NMS,Z)
                    else:
                        sciogliipicchiana(F,paginazionepicchi,indice,NA)
            else:
                NA.assign_nuclide=['']*len(NA.peak_list)
                if NA.identity=='Standard':
                    NMS[0],NMS[1]=None,None
                    sciogliipicchicom(F,paginazionepicchi,indice,NA,NMS,Z)
                else:
                    sciogliipicchiana(F,paginazionepicchi,indice,NA)
                
        def singlescreen_of_multiple(NA,SC,NMS=None,Z=None,NAS=None):
            """Display single of multiple spectra"""
            ratiooflines=int(rows)
            residuallenS=len(NA.peak_list)
            i=0
            paginazionepicchi=[]
            if NA.assign_nuclide==None:
                NA.assign_nuclide=['']*len(NA.peak_list)
            while residuallenS>0:
                try:
                    paginapicco=NA.peak_list[ratiooflines*i:ratiooflines*i+ratiooflines]
                except IndexError:
                    paginapicco=NA.peak_list[ratiooflines*i:]
                paginazionepicchi.append(paginapicco)
                residuallenS=residuallenS-ratiooflines
                i=i+1
            cdn=SC.winfo_children()
            for i in cdn:
                i.destroy()
            F=Frame(SC)
            L=Label(F, width=1).pack(side=LEFT)
            BSS=Button(F, text='Plot', width=8)
            BSS.pack(side=LEFT, anchor=W)
            BSS.configure(command=lambda SC=SC,S=NA: showspectrum(SC,S))
            L=Label(F, width=5).pack(side=LEFT)
            L=Label(F, text='selection name', width=12).pack(side=LEFT)
            lLD=os.listdir('data/presets')
            CLD=[]
            for gk in lLD:
                if gk[-4:]=='.spl':
                    CLD.append(gk[:-4])
            CLD.append('')
            SP_comboB=ttk.Combobox(F, values=CLD, width=20)
            SP_comboB.pack(side=LEFT)
            BTTSSRC=Button(F, text='Recall', width=8)
            BTTSSRC.pack(side=LEFT, anchor=W)
            BTTSSSV=Button(F, text='Save', width=8)
            BTTSSSV.pack(side=LEFT, anchor=W)
            BTTSSSV.configure(command=lambda preset=SP_comboB,NA=NA : save_preset_peakselection(preset,NA))
            BTTSSDD=Button(F, text='Delete', width=8)
            BTTSSDD.pack(side=LEFT, anchor=W)
            BTTSSDD.configure(command=lambda preset=SP_comboB : delete_preset_peakselection(preset))
            BTTSS=Button(F, text='Apply', width=8)
            BTTSS.pack(side=LEFT, anchor=W)
            BTTSS.configure(command=lambda NA=NA,NAS=NAS: propagate_selection(NA,NAS))
            L=Label(F, width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(SC)
            L=Label(F, width=1).pack(side=LEFT)
            L=Label(F, text='start acqusition: '+NA.readable_datetime(), width=30, anchor=W).pack(side=LEFT)
            L=Label(F, text='tc / s: '+str(NA.real_time), width=16, anchor=W).pack(side=LEFT)
            L=Label(F, text='tl / s: '+str(NA.live_time), width=16, anchor=W).pack(side=LEFT)
            L=Label(F, text='tdead: '+NA.deadtime(), width=14, anchor=W).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(SC)
            L=Label(F, width=1).pack(side=LEFT)
            if len(NA.spectrumpath)>71:
                L=Label(F, text='...'+NA.spectrumpath[-70:], width=76, anchor=E).pack(side=LEFT)
            else:
                L=Label(F, text=NA.spectrumpath, width=76, anchor=E).pack(side=LEFT)
            F.pack(anchor=W)
            L=Label(SC).pack()
            F=Frame(SC)
            P=Frame(F)
            P.pack()
            indice=IntVar(SC)
            indice.set(0)
            BTTSSRC.configure(command=lambda F=F,paginazionepicchi=paginazionepicchi,indice=indice,NA=NA,preset=SP_comboB: recall_emission_selection(F,paginazionepicchi,indice,NA,preset))
            sciogliipicchiana(F,paginazionepicchi,indice,NA)
            F.pack()
            
        def Bmenocommandscroll(MS,superi,NA):
            if superi>0:
                superi-=1
                cdn=MS.winfo_children()
                for i in cdn:
                    i.destroy()
                F=Frame(MS)
                Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,NA=NA : Bmenocommandscroll(MS,superi,NA)).pack(side=LEFT)
                L=Label(F, text=f'spectrum {superi+1} of {len(NA)}').pack(side=LEFT)
                Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,NA=NA : Bpiucommandscroll(MS,superi,NA)).pack(side=LEFT)
                F.pack()
                L=Label(MS).pack()
                SC=Frame(MS)
                SC.pack()
                singlescreen_of_multiple(NA[superi],SC,NAS=NA)
        
        def Bpiucommandscroll(MS,superi,NA):
            if superi<len(NA)-1:
                superi+=1
                cdn=MS.winfo_children()
                for i in cdn:
                    i.destroy()
                F=Frame(MS)
                Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,NA=NA : Bmenocommandscroll(MS,superi,NA)).pack(side=LEFT)
                L=Label(F, text=f'spectrum {superi+1} of {len(NA)}').pack(side=LEFT)
                Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,NA=NA : Bpiucommandscroll(MS,superi,NA)).pack(side=LEFT)
                F.pack()
                L=Label(MS).pack()
                SC=Frame(MS)
                SC.pack()
                singlescreen_of_multiple(NA[superi],SC,NAS=NA)
            
        def multiplescreen(NA):
            """Display multiple spectra"""
            superi=0
            MS=Toplevel()
            MS.title(NA[0].identity+' peak list')
            MS.resizable(False,False)
            MS.focus()
            F=Frame(MS)
            Bmeno=Button(F, text='<', relief='flat', command=lambda MS=MS,superi=superi,NA=NA : Bmenocommandscroll(MS,superi,NA)).pack(side=LEFT)
            L=Label(F, text=f'spectrum {superi+1} of {len(NA)}').pack(side=LEFT)
            Bpiu=Button(F, text='>', relief='flat', command=lambda MS=MS,superi=superi,NA=NA : Bpiucommandscroll(MS,superi,NA)).pack(side=LEFT)
            F.pack()
            L=Label(MS).pack()
            SC=Frame(MS)
            SC.pack()
            singlescreen_of_multiple(NA[superi],SC,NAS=NA)
        
        def search(energia,tz=0.3):
            """Search correspondance in k0 database"""
            result=[]
            tz=float(tz)
            energia=float(energia)
            for i in A:
                try:
                    if i[5]+tz>energia and i[5]-tz<energia:
                        if i[4]==2.0:
                            m='m'
                        else:
                            m=''
                        lines=i[2]+'-'+str(int(i[3]))+m+' '+str(i[5])
                        result.append(lines)
                except:
                    pass
            return result
        
        def BmenocommandANA(P,paginazionepicchi,indice,NA):
            if indice.get()>0:
                indice.set(indice.get()-1)
                sciogliipicchiana(P,paginazionepicchi,indice,NA)
        
        def BpiucommandANA(P,paginazionepicchi,indice,NA):
            if indice.get()<len(paginazionepicchi)-1:
                indice.set(indice.get()+1)
                sciogliipicchiana(P,paginazionepicchi,indice,NA)
                
        def selectionecomboselectedWN(event,WN,indice,valuei,NAN):
            NAN[indice.get()*int(rows)+valuei]=WN.get()
            
        def eliminapasticci(event,WN,indice,paginazionepicchi,valuei,NAN):
            WN.set('')
            NAN[indice.get()*int(rows)+valuei]=WN.get()
        
        def sciogliipicchiana(P,paginazionepicchi,indice,NA):
            """Display peaklist analyte"""
            if indice.get()>-1 and indice.get()<len(paginazionepicchi):
                cdn=P.winfo_children()
                for i in cdn:
                    i.destroy()
                F=Frame(P)
                chrw=10
                Bmeno=Button(F, text='<', relief='flat', command=lambda P=P,paginazionepicchi=paginazionepicchi,indice=indice,NA=NA : BmenocommandANA(P,paginazionepicchi,indice,NA)).pack(side=LEFT)
                L=Label(F, text=f'page {indice.get()+1} of {len(paginazionepicchi)}').pack(side=LEFT)
                Bpiu=Button(F, text='>', relief='flat', command=lambda P=P,paginazionepicchi=paginazionepicchi,indice=indice,NA=NA : BpiucommandANA(P,paginazionepicchi,indice,NA)).pack(side=LEFT)
                F.pack()
                titles=['channel','E / keV','net area / 1','uncertainty','FWHM / ch','emission','selection','','','','','','']
                FL=Frame(P)
                L=Label(FL, text=titles[0], width=chrw).pack(side=LEFT)
                L=Label(FL, text=titles[1], width=chrw).pack(side=LEFT)
                L=Label(FL, text=titles[2], width=chrw).pack(side=LEFT) #area
                L=Label(FL, text=titles[3], width=chrw).pack(side=LEFT) #uncertainty
                L=Label(FL, text=titles[4], width=chrw).pack(side=LEFT) #FWHM
                L=Label(FL, text=titles[5], width=chrw+2).pack(side=LEFT)
                FL.pack(anchor=W)
                valuei=0
                for j in range(len(paginazionepicchi[indice.get()])):
                    FL=Frame(P)
                    L=Label(FL, text=str(float(paginazionepicchi[indice.get()][j][4]).__round__(2)), width=chrw).pack(side=LEFT) #channel
                    L=Label(FL, text=str(float(paginazionepicchi[indice.get()][j][6]).__round__(2)), width=chrw).pack(side=LEFT) #energy
                    L=Label(FL, text=str(int(float(paginazionepicchi[indice.get()][j][8]))), width=chrw).pack(side=LEFT) #area
                    dinc=float(paginazionepicchi[indice.get()][j][9])/float(paginazionepicchi[indice.get()][j][8])*100
                    L=Label(FL, text=str(dinc.__round__(2))+' %', width=chrw).pack(side=LEFT) #uncetainty
                    if float(paginazionepicchi[indice.get()][j][10])<0.01:
                        L=Label(FL, text='-', width=chrw).pack(side=LEFT) #FWHM
                    else:
                        L=Label(FL, text=paginazionepicchi[indice.get()][j][10], width=chrw).pack(side=LEFT) #FWHM
                    possiblenuclides=search(paginazionepicchi[indice.get()][j][6],tolerance_energy)
                    WN=ttk.Combobox(FL, values=possiblenuclides, state='readonly')
                    WN.set(NA.assign_nuclide[indice.get()*int(rows)+j])
                    WN.pack(side=LEFT)
                    WN.configure(width=chrw+2)
                    ewent='<<ComboboxSelected>>'
                    WN.bind(ewent, lambda event=ewent,WN=WN,indice=indice,valuei=valuei,NAN=NA.assign_nuclide: selectionecomboselectedWN(event,WN,indice,valuei,NAN))
                    if len(possiblenuclides)==0:
                        WN.configure(state='disabled')
                    if len(possiblenuclides)>0:
                        NboX=Label(FL, text=f'({len(possiblenuclides)})', width=3).pack(side=LEFT)
                    else:
                        NboX=Label(FL, text=f'', width=3).pack(side=LEFT)
                    XboX=Button(FL, text='X', width=3, command= lambda event=ewent,WN=WN,indice=indice,paginazionepicchi=paginazionepicchi,valuei=valuei,NAN=NA.assign_nuclide : eliminapasticci(event,WN,indice,paginazionepicchi,valuei,NAN))
                    XboX.pack(side=LEFT)
                    Buttoninfo=Button(FL, text='Info', width=chrw, command= lambda WN=WN: commandinfoemission(WN))
                    Buttoninfo.pack(side=LEFT)
                    L=Label(FL, width=1).pack(side=LEFT)
                    FL.pack(anchor=W)
                    valuei=valuei+1
                L=Label(P).pack()
                
        def checkboxbutton_comparator(C,indice,CheckVar,paginazionepicchi,NAN,NMS):
            """Allow only direct activated nuclides as comparators"""
            allowed=['I','IVB','IIB','VI']
            try:
                int(CheckVar.get())
            except:
                C.deselect()
                NMS[0],NMS[1]=None,None
            else:
                kk=''
                for k in A:
                    S=['','','m']
                    if k[2]+'-'+str(int(k[3]))+S[int(k[4])]+' '+str(k[5])==NAN[indice.get()*int(rows)+int(CheckVar.get())]:
                        kk=k[22]
                        break
                if NAN[indice.get()*int(rows)+int(CheckVar.get())]!='' and kk in allowed:
                    NMS[0],NMS[1]=indice.get()*int(rows)+int(CheckVar.get()),NAN[indice.get()*int(rows)+int(CheckVar.get())]
                else:
                    NMS[0],NMS[1]=None,None
                    C.deselect()

        def Bmenocommandcom(P,paginazionepicchi,indice,NA,NMS,Z):
            if indice.get()>0:
                indice.set(indice.get()-1)
                sciogliipicchicom(P,paginazionepicchi,indice,NA,NMS,Z)
        
        def Bpiucommandcom(P,paginazionepicchi,indice,NA,NMS,Z):
            if indice.get()<len(paginazionepicchi)-1:
                indice.set(indice.get()+1)
                sciogliipicchicom(P,paginazionepicchi,indice,NA,NMS,Z)
                
        def sciogliipicchicom(P,paginazionepicchi,indice,NA,NMS,Z):
            """Display peaklist comparator"""
            if indice.get()>-1 and indice.get()<len(paginazionepicchi):
                cdn=P.winfo_children()
                for i in cdn:
                    i.destroy()
                F=Frame(P)
                chrw=10
                Bmeno=Button(F, text='<', relief='flat', command=lambda P=P,paginazionepicchi=paginazionepicchi,indice=indice,NA=NA,NMS=NMS,Z=Z : Bmenocommandcom(P,paginazionepicchi,indice,NA,NMS,Z)).pack(side=LEFT)
                L=Label(F, text=f'page {indice.get()+1} of {len(paginazionepicchi)}').pack(side=LEFT)
                Bpiu=Button(F, text='>', relief='flat', command=lambda P=P,paginazionepicchi=paginazionepicchi,indice=indice,NA=NA,NMS=NMS,Z=Z : Bpiucommandcom(P,paginazionepicchi,indice,NA,NMS,Z)).pack(side=LEFT)
                F.pack()
                titles=['channel','E / keV','net area / 1','uncertainty','FWHM / ch','emission','selection','relative','','','','','']
                FL=Frame(P)
                L=Label(FL, text=titles[6], width=chrw).pack(side=LEFT)
                L=Label(FL, text=titles[0], width=chrw).pack(side=LEFT)
                L=Label(FL, text=titles[1], width=chrw).pack(side=LEFT)
                L=Label(FL, text=titles[2], width=chrw).pack(side=LEFT) #area
                L=Label(FL, text=titles[3], width=chrw).pack(side=LEFT) #uncertainty
                L=Label(FL, text=titles[4], width=chrw).pack(side=LEFT) #FWHM
                L=Label(FL, text=titles[5], width=chrw+2).pack(side=LEFT)
                L=Label(FL, text=titles[8], width=chrw).pack(side=LEFT)
                FL.pack(anchor=W)
                valuei=0
                CheckVar=StringVar(P)
                for j in range(len(paginazionepicchi[indice.get()])):
                    FL=Frame(P)
                    C=Checkbutton(FL, variable=CheckVar, onvalue=valuei, offvalue='', width=chrw-3)
                    if indice.get()*int(rows)+valuei==NMS[0]:
                        CheckVar.set(valuei)
                    C.pack(side=LEFT)
                    L=Label(FL, text=str(float(paginazionepicchi[indice.get()][j][4]).__round__(2)), width=chrw).pack(side=LEFT) # channel
                    L=Label(FL, text=str(float(paginazionepicchi[indice.get()][j][6]).__round__(2)), width=chrw).pack(side=LEFT) #energy
                    L=Label(FL, text=str(int(float(paginazionepicchi[indice.get()][j][8]))), width=chrw).pack(side=LEFT) #area
                    dinc=float(paginazionepicchi[indice.get()][j][9])/float(paginazionepicchi[indice.get()][j][8])*100
                    L=Label(FL, text=str(dinc.__round__(2))+' %', width=chrw).pack(side=LEFT) #uncertainty
                    if float(paginazionepicchi[indice.get()][j][10])<0.01:
                        L=Label(FL, text='-', width=chrw).pack(side=LEFT) #FWHM
                    else:
                        L=Label(FL, text=paginazionepicchi[indice.get()][j][10], width=chrw).pack(side=LEFT) #FWHM
                    possiblenuclides=search(paginazionepicchi[indice.get()][j][6],tolerance_energy)
                    WN=ttk.Combobox(FL, values=possiblenuclides, state='readonly')
                    WN.set(NA.assign_nuclide[indice.get()*int(rows)+j])
                    WN.pack(side=LEFT)
                    WN.configure(width=chrw+2)
                    ewent='<<ComboboxSelected>>'
                    WN.bind(ewent, lambda event=ewent,WN=WN,indice=indice,valuei=valuei,NAN=NA.assign_nuclide: selectionecomboselectedWN(event,WN,indice,valuei,NAN))
                    if len(possiblenuclides)==0:
                        WN.configure(state='disabled')
                    if len(possiblenuclides)>0:
                        NboX=Label(FL, text=f'({len(possiblenuclides)})', width=3).pack(side=LEFT)
                    else:
                        NboX=Label(FL, text=f'', width=3).pack(side=LEFT)
                    Buttoninfo=Button(FL, text='Info', width=chrw, command= lambda WN=WN: commandinfoemission(WN))
                    Buttoninfo.pack(side=LEFT)
                    L=Label(FL, width=1).pack(side=LEFT)
                    FL.pack(anchor=W)
                    C.configure(command=lambda C=C,indice=indice,CheckVar=CheckVar,paginazionepicchi=paginazionepicchi,NAN=NA.assign_nuclide,NMS=NMS: checkboxbutton_comparator(C,indice,CheckVar,paginazionepicchi,NAN,NMS))
                    valuei=valuei+1
                L=Label(P).pack()
                
        def Bmenocommandbkg(P,paginazionepicchi,indice):
            if indice.get()>0:
                indice.set(indice.get()-1)
                sciogliipicchibkg(P,paginazionepicchi,indice)
        
        def Bpiucommandbkg(P,paginazionepicchi,indice):
            if indice.get()<len(paginazionepicchi)-1:
                indice.set(indice.get()+1)
                sciogliipicchibkg(P,paginazionepicchi,indice)
        
        def sciogliipicchibkg(P,paginazionepicchi,indice):
            """Display peaklist background"""
            if indice.get()>-1 and indice.get()<len(paginazionepicchi):
                cdn=P.winfo_children()
                for i in cdn:
                    i.destroy()
                F=Frame(P)
                chrw=10
                Bmeno=Button(F, text='<', relief='flat', command=lambda P=P,paginazionepicchi=paginazionepicchi,indice=indice : Bmenocommandbkg(P,paginazionepicchi,indice)).pack(side=LEFT)
                L=Label(F, text=f'page {indice.get()+1} of {len(paginazionepicchi)}').pack(side=LEFT)
                Bpiu=Button(F, text='>', relief='flat', command=lambda P=P,paginazionepicchi=paginazionepicchi,indice=indice : Bpiucommandbkg(P,paginazionepicchi,indice)).pack(side=LEFT)
                F.pack()
                titles=['channel','E / keV','net area / 1','uncertainty','FWHM / ch','emission','selection','','','','','','']
                FL=Frame(P)
                L=Label(FL, text=titles[0], width=chrw).pack(side=LEFT)
                L=Label(FL, text=titles[1], width=chrw).pack(side=LEFT)
                L=Label(FL, text=titles[2], width=chrw).pack(side=LEFT) #area
                L=Label(FL, text=titles[3], width=chrw).pack(side=LEFT) #uncertainty
                L=Label(FL, text=titles[4], width=chrw).pack(side=LEFT) #FWHM
                FL.pack(anchor=W)
                for j in range(len(paginazionepicchi[indice.get()])):
                    FL=Frame(P)
                    L=Label(FL, text=str(float(paginazionepicchi[indice.get()][j][4]).__round__(2)), width=chrw).pack(side=LEFT) # channel
                    L=Label(FL, text=str(float(paginazionepicchi[indice.get()][j][6]).__round__(2)), width=chrw).pack(side=LEFT) #energy
                    L=Label(FL, text=str(int(float(paginazionepicchi[indice.get()][j][8]))), width=chrw).pack(side=LEFT) #area
                    dinc=float(paginazionepicchi[indice.get()][j][9])/float(paginazionepicchi[indice.get()][j][8])*100
                    L=Label(FL, text=str(dinc.__round__(2))+' %', width=chrw).pack(side=LEFT) #uncertainty
                    if float(paginazionepicchi[indice.get()][j][10])<0.01:
                        L=Label(FL, text='-', width=chrw).pack(side=LEFT) #FWHM
                    else:
                        L=Label(FL, text=paginazionepicchi[indice.get()][j][10], width=chrw).pack(side=LEFT) #FWHM
                    FL.pack(anchor=W)
                L=Label(P).pack()
            
        def singlescreen(NA,NMS=None,Z=None):
            """Display single spectrum"""
            ratiooflines=int(rows)
            residuallenS=len(NA.peak_list)
            i=0
            paginazionepicchi=[]
            if NA.assign_nuclide==None:
                NA.assign_nuclide=['']*len(NA.peak_list)
            while residuallenS>0:
                try:
                    paginapicco=NA.peak_list[ratiooflines*i:ratiooflines*i+ratiooflines]
                except IndexError:
                    paginapicco=NA.peak_list[ratiooflines*i:]
                paginazionepicchi.append(paginapicco)
                residuallenS=residuallenS-ratiooflines
                i=i+1
            SC=Toplevel()
            SC.title(NA.identity+' peak list')
            SC.resizable(False,False)
            SC.focus()
            F=Frame(SC)
            L=Label(SC).pack()
            L=Label(F, width=1).pack(side=LEFT)
            BSS=Button(F, text='Plot', width=8)
            BSS.pack(side=LEFT, anchor=W)
            BSS.configure(command=lambda SC=SC,S=NA: showspectrum(SC,S))
            if NA.identity=='Sample' or NA.identity=='Standard':#NA.identity!='Background':
                L=Label(F, width=5).pack(side=LEFT)
                L=Label(F, text='selection name', width=12).pack(side=LEFT)
                lLD=os.listdir('data/presets')
                CLD=[]
                for gk in lLD:
                    if gk[-4:]=='.spl':
                        CLD.append(gk[:-4])
                CLD.append('')
                SP_comboB=ttk.Combobox(F, values=CLD, width=20)
                SP_comboB.pack(side=LEFT)
                BTTSSRC=Button(F, text='Recall', width=8)
                BTTSSRC.pack(side=LEFT, anchor=W)
                BTTSSSV=Button(F, text='Save', width=8)
                BTTSSSV.pack(side=LEFT, anchor=W)
                BTTSSSV.configure(command=lambda preset=SP_comboB,NA=NA : save_preset_peakselection(preset,NA))
                BTTSSDD=Button(F, text='Delete', width=8)
                BTTSSDD.pack(side=LEFT, anchor=W)
                BTTSSDD.configure(command=lambda preset=SP_comboB : delete_preset_peakselection(preset))
                L=Label(F, width=1).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(SC)
            L=Label(F, width=1).pack(side=LEFT)
            L=Label(F, text='start acqusition: '+NA.readable_datetime(), width=30, anchor=W).pack(side=LEFT)
            L=Label(F, text='tc / s: '+str(NA.real_time), width=16, anchor=W).pack(side=LEFT)
            L=Label(F, text='tl / s: '+str(NA.live_time), width=16, anchor=W).pack(side=LEFT)
            L=Label(F, text='tdead: '+NA.deadtime(), width=14, anchor=W).pack(side=LEFT)
            F.pack(anchor=W)
            F=Frame(SC)
            L=Label(F, width=1).pack(side=LEFT)
            if len(NA.spectrumpath)>71:
                L=Label(F, text='...'+NA.spectrumpath[-70:], width=76, anchor=E).pack(side=LEFT)
            else:
                L=Label(F, text=NA.spectrumpath, width=76, anchor=E).pack(side=LEFT)
            F.pack(anchor=W)
            L=Label(SC).pack()
            F=Frame(SC)
            P=Frame(F)
            P.pack()
            indice=IntVar(SC)
            indice.set(0)
            if NA.identity=='Standard':
                sciogliipicchicom(F,paginazionepicchi,indice,NA,NMS,Z)
                BTTSSRC.configure(command=lambda F=F,paginazionepicchi=paginazionepicchi,indice=indice,NA=NA,preset=SP_comboB,NMS=NMS,Z=Z: recall_emission_selection(F,paginazionepicchi,indice,NA,preset,NMS,Z))
            elif NA.identity=='Sample':
                BTTSSRC.configure(command=lambda F=F,paginazionepicchi=paginazionepicchi,indice=indice,NA=NA,preset=SP_comboB: recall_emission_selection(F,paginazionepicchi,indice,NA,preset))
                sciogliipicchiana(F,paginazionepicchi,indice,NA)
            else:
                sciogliipicchibkg(F,paginazionepicchi,indice)
            F.pack()
            
        def overlookscreen(NA,NMS=None,Z=None):
            if NA!=None:
                try:
                    len(NA)
                except TypeError:
                    singlescreen(NA,NMS,Z)
                else:
                    if len(NA)==1:
                        singlescreen(NA[0])
                    else:
                        multiplescreen(NA)
        
        def overlook(BT,NAA):
            if BT.cget('text')=='Background':
                overlookscreen(NAA.background)
            elif BT.cget('text')=='Standard':
                overlookscreen(NAA.comparator,NAA.standard_comparator,NAA.relative_method)
            elif BT.cget('text')=='Sample':
                overlookscreen(NAA.sample)
                
        def clearall(NAA,LBS,LPKSS,LDTS):
            """Clear list of selected analyte spectra"""
            NAA.sample=None
            LBS.configure(text='')
            LPKSS.configure(text='')
            LDTS.configure(text='')
            
        def selectionecomboselected(box,NAA):
            """Calibration selection from listbox"""
            NAA.set_efficiency_calibration(box.get())
                    
        def select_one_nuclide(vb,CB,NASN,Lb):
            if vb.get()!='':
                NASN.append(vb.get())
            else:
                NASN.remove(CB.cget('onvalue'))
            Lb.configure(text=f'{len(NASN)} elements')
        
        def save_current_selection(NASN,preset,ENE):
            if len(NASN)!=0 and ENE.get()!='':
                n=0
                nomefile=f'data/presets/{ENE.get()}.sel'
                pool=os.listdir('data/presets')
                while nomefile[13:] in pool:
                    n+=1
                    nomefile=f'data/presets/{ENE.get()}_{n}.sel'
                f=open(nomefile,'w')
                for ks in NASN:
                    f.write(ks)
                    f.write(' ')
                f.close()
                h=os.listdir('data/presets')
                values=[]
                for t in h:
                    if t[-4:]=='.sel':
                        values.append(t[:-4])
                values.append('')
                preset['values']=values
                nomefile=nomefile.replace('data/presets/','')
                nomefile=nomefile.replace('.sel','')
                if nomefile in values:
                    preset.set(nomefile)
                else:
                    preset.set('')
                ENE.delete(0,END)
                ENE.insert(0,'New_saved_selection')
                
        def delete_preset(preset):
            default_list=['All','Medium & Long-lived (50 elements)','Rare earths (16 elements)','Short & Medium-lived (54 elements)','']
            if preset.get() not in default_list:
                os.remove('data/presets/'+preset.get()+'.sel')
                h=os.listdir('data/presets')
                values=[]
                for t in h:
                    if t[-4:]=='.sel':
                        values.append(t[:-4])
                values.append('')
                preset['values']=values
                preset.set('')
            
        def select_preset(ACB,NASN,Lb,preset):
            if preset.get()!='':
                f=open('data/presets/'+preset.get()+'.sel','r')
                r=f.readlines()
                f.close()
                presets=str.split(r[0])
            else:
                presets=[]
            for t in range(len(NASN)):
                NASN.pop(0)
            for txt in presets:
                NASN.append(txt)
            for k in ACB:
                if k.cget('text') in NASN:
                    k.select()
                else:
                    k.deselect()
            Lb.configure(text=f'{len(NASN)} elements')
                    
        def select_nuclides_k0(NASN,Lb):
            lbs=[]
            for i in A:
                lbs.append(i[1])
            lbs=sorted(set(lbs))
            SN=Toplevel()
            SN.title('Element selection')
            SN.resizable(False,False)
            L=Label(SN).pack()
            SN.focus()
            i=0
            ACB=[]
            while i < len(lbs):
                F=Frame(SN)
                L=Label(F, text='', width=1).pack(side=LEFT)
                for k in range(10):
                    try:
                        vb=StringVar(F)
                        CB = Checkbutton(F, text=lbs[i], variable=vb, onvalue=lbs[i], offvalue='', width=5, anchor=W)
                        CB.pack(side=LEFT)
                        if lbs[i] in NASN:
                            CB.select()
                        else:
                            CB.deselect()
                        CB.configure(command=lambda vb=vb,CB=CB,NASN=NASN,Lb=Lb: select_one_nuclide(vb,CB,NASN,Lb))
                        ACB.append(CB)
                        i+=1
                    except IndexError:
                        break
                F.pack(anchor=W)
            L=Label(SN).pack()
            
            F=Frame(SN, pady=2)
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='filename', width=10, anchor=W).pack(side=LEFT)
            ENW_sel=Entry(F, width=39)
            ENW_sel.pack(side=LEFT)
            ENW_sel.insert(0,'New_saved_selection')
            L=Label(F, text='', width=1).pack(side=LEFT)
            B_save=Button(F, text='Save', width=8, padx=2)
            B_save.pack(side=LEFT)
            F.pack(anchor=W)
            
            F=Frame(SN)
            h=os.listdir('data/presets')
            values=[]
            for t in h:
                if t[-4:]=='.sel':
                    values.append(t[:-4])
            values.append('')
            L=Label(F, text='', width=1).pack(side=LEFT)
            L=Label(F, text='selection', width=10, anchor=W).pack(side=LEFT)
            preset_selectionCB=ttk.Combobox(F, values=values, state='readonly', width=36)
            preset_selectionCB.pack(side=LEFT)
            preset_selectionCB.set('')
            L=Label(F, text='', width=1).pack(side=LEFT)
            B_pre=Button(F, text='Recall', width=8)
            B_pre.pack(side=LEFT)
            B_pre.configure(command=lambda ACB=ACB,NASN=NASN,Lb=Lb,preset=preset_selectionCB : select_preset(ACB,NASN,Lb,preset))
            B_predel=Button(F, text='Delete', width=8)
            B_predel.pack(side=LEFT)
            B_predel.configure(command=lambda preset=preset_selectionCB : delete_preset(preset))
            F.pack(anchor=W)
            B_save.configure(command=lambda NASN=NASN,preset=preset_selectionCB,ENE=ENW_sel : save_current_selection(NASN,preset,ENE))
            L=Label(SN).pack()
            
        def flux_drift_select(box,fvalues,BETAS,UBETAS):
            for line in fvalues:
                if box.get()==line[0]:
                    BETAS.delete(0,END)
                    BETAS.insert(END,line[1])
                    UBETAS.delete(0,END)
                    UBETAS.insert(END,line[2])
                    break
        
        def flux_drift_evaluate(box,fvalues,BETAS,UBETAS,irrdata):
            def g_discr(i):
                if i==2.0:
                    return 'm'
                else:
                    return ''
                    
            def recall_spectrum_drift(MM,namelabel,which):
                nomeHyperLabfile,startcounting,realT,liveT,peak_list,spectrum_counts,linE,linW=searchforhypelabfile(unclimit_calib)
                if realT!=None:
                    S=Spectrum('Drift evaluation',startcounting,realT,liveT,peak_list,spectrum_counts,nomeHyperLabfile)
                    MM.spectra[which] = S
                    namelabel.configure(text=f'{S.filename()}')
                    MM.focus()
                    
            def flux_drift_save(MM,box,fvalues,BETAS,UBETAS,channel_doublebox):
                if MM.beta is not None:
                    name = channel_doublebox.get().replace(' ','_')
                    if name == '':
                        name = '_'
                    found = False
                    for line in fvalues:
                        if line[0] == name:
                            line[1], line[2] = MM.beta, MM.ubeta
                            found = True
                            break
                    if found == False:
                        fvalues.append([name, format(MM.beta,'.5f'), format(MM.ubeta,'.5f')])
                    channel_doublebox['values'] = [line[0] for line in fvalues]
                    channel_doublebox.set(name)
                    box['values'] = [line[0] for line in fvalues]
                    box.set(name)
                    BETAS.delete(0,END)
                    BETAS.insert(END,format(MM.beta,'.5f'))
                    UBETAS.delete(0,END)
                    UBETAS.insert(END,format(MM.ubeta,'.5f'))
                    with open('data/irradiations/irr_var.txt', 'w') as f:
                        f.write('#Irradiation trend data {This line is for comments and is ignored}\n')
                        for line in fvalues:
                            f.write(f'{line[0]} {line[1]} {line[2]}\n')
                    MM.destroy()
            
            def calculate_thermal_drift(DAY,MONTH,YEAR,HOUR,MINUTE,SECOND,IEFFE,IUEFFE,IALPHA,IUALPHA,calib,monit,MM,MASS_1,UMASS_1,MASS_2,UMASS_2,GS_1,UGS_1,GS_2,UGS_2,GE_1,UGE_1,GE_2,UGE_2,UDD_1,UDD_2,DX,UDX,textbox,AX,FIG,CANV):
                def get_lamb(value,unit,uncertainty):
                    units = {'d':86400, 's':1, 'm':60, 'h':3600, 'y':86400*365.24}
                    lamb = np.log(2)/(value*units[unit.lower()])
                    unc = uncertainty/value * lamb
                    return lamb, unc
                    
                def get_values(value,relative_uncertainty,default=20):
                    try:
                        uncertainty = value * relative_uncertainty / 100
                    except:
                        uncertainty = value * default / 100
                    return value, uncertainty
                    
                def get_monitor_data(mon):
                    emit, energy = mon.split()
                    target, isot = emit.split('-')
                    energy = float(energy)
                    try:
                        isot = float(isot)
                        state = 1.0
                    except:
                        isot = float(isot.replace('m',''))
                        state = 2.0
                    for line in A:
                        if line[2] == target and line[3] == isot and line[4] == state and line[5] == energy:
                            return line
                            
                def relative_displacement(der,uder,dd,udd):
                    """Return the relative uncertainty due to positioning variability"""
                    #return (der * dd * np.sqrt(np.power(uder,2) + np.power(udd,2))) / (1 - der * dd) #check this
                    return der * udd
                            
                def get_dt(spectrum,irradiation_end):
                    tdi = spectrum.datetime - irradiation_end
                    td = tdi.days * 86400 + tdi.seconds
                    return td
                    
                def get_netarea_unc(spectrum,monitor_energy):
                    npp, unpp = None, None
                    for line in spectrum.peak_list:
                        if monitor_energy - float(tolerance_energy) < float(line[6]) < monitor_energy + float(tolerance_energy):
                            npp, unpp = float(line[8]), float(line[9])
                            break
                    return npp, unpp
                
                def specific_count_rate(_np,_tr,_tl,_lb,_td,_m,_der,_dd,_Gth,_Ge,_f,_Q0,_Er,_a):
                    return (_np * _tr) / (_tl * np.exp(-_lb*_td) * (1-np.exp(-_lb*_tr)) * _m * (1-_der*_dd) * (_Gth + _Ge / _f * ((_Q0 - 0.429)/(_Er**_a) + 0.429/((2*_a + 1) * 0.55**_a))))
                    
                #check integrity
                #end irradiation date
                try:
                    endirr = datetime.datetime(int(YEAR.get()), int(MONTH.get()), int(DAY.get()), int(HOUR.get()), int(MINUTE.get()), int(SECOND.get()))
                except:
                    endirr = None
                try:
                    ff = float(IEFFE.get())
                except:
                    ff = 0
                try:
                    uff = float(IUEFFE.get())
                except:
                    uff = 0
                try:
                    aa = float(IALPHA.get())
                except:
                    aa = 0
                try:
                    uaa = float(IUALPHA.get())
                except:
                    uaa = 0
                try:
                    mass_1 = float(MASS_1.get())
                except:
                    mass_1 = 0
                try:
                    umass_1 = float(UMASS_1.get())
                except:
                    umass_1 = 0
                try:
                    mass_2 = float(MASS_2.get())
                except:
                    mass_2 = 0
                try:
                    umass_2 = float(UMASS_2.get())
                except:
                    umass_2 = 0
                try:
                    gs_1 = float(GS_1.get())
                    ugs_1 = float(UGS_1.get())
                except:
                    gs_1 = 1
                    ugs_1 = 0
                try:
                    gs_2= float(GS_2.get())
                    ugs_2 = float(UGS_2.get())
                except:
                    gs_2 = 1
                    ugs_2 = 0
                try:
                    ge_1 = float(GE_1.get())
                    uge_1 = float(UGE_1.get())
                except:
                    ge_1 = 1
                    uge_1 = 0
                try:
                    ge_2= float(GE_2.get())
                    uge_2 = float(UGE_2.get())
                except:
                    ge_2 = 1
                    uge_2 = 0
                try:
                    udd_1 = float(UDD_1.get())
                except:
                    udd_1 = 0
                try:
                    udd_2 = float(UDD_2.get())
                except:
                    udd_2 = 0
                try:
                    dx = float(DX.get())
                except:
                    dx = 0
                try:
                    udx = float(UDX.get())
                except:
                    udx = 0
                if endirr is None:
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- End irradiation date is invalid')
                    textbox.configure(state='disabled')
                elif ff <= 0:
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- f value is less or equal to 0')
                    textbox.configure(state='disabled')
                elif calib.get() == '':
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- choose a calibration from the corresponding combobox')
                    textbox.configure(state='disabled')
                elif monit.get() == '':
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- choose a monitor from the corresponding combobox')
                    textbox.configure(state='disabled')
                elif mass_1 <= 0:
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- mass value for "lower" monitor is less or equal to 0')
                    textbox.configure(state='disabled')
                elif mass_2 <= 0:
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- mass value for "higher" monitor is less or equal to 0')
                    textbox.configure(state='disabled')
                elif MM.spectra[0] is None:
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- select a spectra for the "lower" monitor')
                    textbox.configure(state='disabled')
                elif MM.spectra[1] is None:
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- select a spectra for the "higher" monitor')
                    textbox.configure(state='disabled')
                elif dx <= 0:
                    textbox.configure(state='normal')
                    textbox.delete('0.0',END)
                    textbox.insert(END,'Insert all the relevant data\n- distance (L) value for "higher" monitor is less or equal to 0')
                    textbox.configure(state='disabled')
                else:
                    monitor = get_monitor_data(monit.get())
                    lamb, ulamb = get_lamb(monitor[31], monitor[32], monitor[33])
                    Q0, uQ0 = get_values(monitor[75], monitor[76])
                    Er, uEr = get_values(monitor[77], monitor[78],50)
                    np1, unp1 = get_netarea_unc(MM.spectra[0],monitor[5])
                    np2, unp2 = get_netarea_unc(MM.spectra[1],monitor[5])
                    td1 = get_dt(MM.spectra[0],endirr)
                    td2 = get_dt(MM.spectra[1],endirr)
                    cal = Calibration(calib.get())
                    der1 = cal.der_fit(np.array([monitor[5]]))
                    der1, uder1 = float(der1[0]), float(der1[1])
                    if np1 is None:
                        textbox.configure(state='normal')
                        textbox.delete('0.0',END)
                        textbox.insert(END,f'Elaboration error\n- peak for {monit.get()} monitor was not found in the "lower" spectrum')
                        textbox.configure(state='disabled')
                    elif np2 is None:
                        textbox.configure(state='normal')
                        textbox.delete('0.0',END)
                        textbox.insert(END,f'Elaboration error\n- peak for {monit.get()} monitor was not found in the "higher" spectrum')
                        textbox.configure(state='disabled')
                    elif td1 < 0:
                        textbox.configure(state='normal')
                        textbox.delete('0.0',END)
                        textbox.insert(END,'Elaboration error\n- acquisition date of "lower" spectrum is before the end of irradiation!')
                        textbox.configure(state='disabled')
                    elif td2 < 0:
                        textbox.configure(state='normal')
                        textbox.delete('0.0',END)
                        textbox.insert(END,'Elaboration error\n- acquisition date of "higher" spectrum is before the end of irradiation!')
                        textbox.configure(state='disabled')
                    else:
                        textual = []
                        textual.append(f'Irradiation performed on {endirr.strftime("%d/%m/%Y %H:%M:%S")}\nAdopted emission for monitor: {monit.get()}\nCalibration: {calib.get()}, counting distance {cal.distance} mm on {cal.detector} detector ({format(der1*100,".2f")} % efficiency variability per mm of vertical displacement)\n')
                        textual.append(f'- Monitor found on "lower" spectrum "{MM.spectra[0].filename()}" ({format(np1,".0f")} net area counts with {format(unp1/np1*100,".2f")} % relative uncertainty)\n- Monitor found on "higher" spectrum "{MM.spectra[1].filename()}" ({format(np2,".0f")} net area counts with {format(unp2/np2*100,".2f")} % relative uncertainty)\n- Distance between two monitor positions (L) is {format(dx,".1f")} mm\n')
                        Asp_1 = specific_count_rate(np1,MM.spectra[0].real_time,MM.spectra[0].live_time,lamb,td1,mass_1,der1,0.0,gs_1,ge_1,ff,Q0,Er,aa)
                        Asp_2 = specific_count_rate(np2,MM.spectra[1].real_time,MM.spectra[1].live_time,lamb,td2,mass_2,der1,0.0,gs_2,ge_2,ff,Q0,Er,aa)
                        #beta evaluation
                        MM.beta = (Asp_2 / Asp_1 - 1)/ dx
                        original_values = [np1, MM.spectra[0].real_time, MM.spectra[0].live_time, td1, mass_1, gs_1, ge_1, np2, MM.spectra[1].real_time, MM.spectra[1].live_time, td2, mass_2, gs_2, ge_2, lamb, der1, 0.0, 0.0, ff, Q0, Er, aa, dx]
                        comput_values = [np1, MM.spectra[0].real_time, MM.spectra[0].live_time, td1, mass_1, gs_1, ge_1, np2, MM.spectra[1].real_time, MM.spectra[1].live_time, td2, mass_2, gs_2, ge_2, lamb, der1, 0.0, 0.0, ff, Q0, Er, aa, dx]
                        uncertainties = [unp1, NAA.default_utc, NAA.default_utc, NAA.default_utdm, umass_1, ugs_1, uge_1, unp2, NAA.default_utc, NAA.default_utc, NAA.default_utdm, umass_2, ugs_2, uge_2, ulamb, uder1, udd_1, udd_2, uff, uQ0, uEr, uaa, udx]
                        res = []
                        for idx in range(len(original_values)):
                            comput_values[idx] = original_values[idx] + uncertainties[idx]
                            _np1, _tr1, _tl1, _td1, _mass_1, _gs_1, _ge_1, _np2, _tr2, _tl2, _td2, _mass_2, _gs_2, _ge_2, _lamb, _der1, _ddr1, _ddr2, _ff, _Q0, _Er, _aa, _dx = comput_values
                            solplus = (specific_count_rate(_np2,_tr2,_tl2,_lamb,_td2,_mass_2,_der1,_ddr2,_gs_2,_ge_2,_ff,_Q0,_Er,_aa) / Asp_1 - specific_count_rate(_np1,_tr1,_tl1,_lamb,_td1,_mass_1,_der1,_ddr1,_gs_1,_ge_1,_ff,_Q0,_Er,_aa) / Asp_1)/ _dx
                            comput_values[idx] = original_values[idx] - uncertainties[idx]
                            _np1, _tr1, _tl1, _td1, _mass_1, _gs_1, _ge_1, _np2, _tr2, _tl2, _td2, _mass_2, _gs_2, _ge_2, _lamb, _der1, _ddr1, _ddr2, _ff, _Q0, _Er, _aa, _dx = comput_values
                            solminus = (specific_count_rate(_np2,_tr2,_tl2,_lamb,_td2,_mass_2,_der1,_ddr2,_gs_2,_ge_2,_ff,_Q0,_Er,_aa) / Asp_1 - specific_count_rate(_np1,_tr1,_tl1,_lamb,_td1,_mass_1,_der1,_ddr1,_gs_1,_ge_1,_ff,_Q0,_Er,_aa) / Asp_1)/ _dx
                            comput_values[idx] = original_values[idx]
                            res.append((solplus-solminus)/(2*uncertainties[idx] + 1E-12))
                        res = np.array(res)
                        uncertainties = np.array(uncertainties)
                        unc_cov_matrix = np.diag(np.power(uncertainties,2))
                        MM.ubeta = np.sqrt((res.T@unc_cov_matrix) @ res)
                        if np.abs(MM.ubeta / MM.beta) > 1.0:
                            warning1 = 'warning: excessive evaluated uncertainty for β, value might be non-significant\n'
                        else:
                            warning1 = ''
                        indexes = np.power(np.array([x1*x2 for x1, x2 in zip(res,uncertainties)]),2)
                        description = ['Net area of "lower" monitor', 'Real time of acquisition of "lower" monitor', 'Live time of acquisition of "lower" monitor', 'Decay time of "lower" monitor', 'Mass of "lower" monitor', 'Thermal self shielding correction of "lower" monitor', 'Epithermal self shielding correction of "lower" monitor', 'Net area of "higher" monitor', 'Real time of acquisition of "higher" monitor', 'Live time of acquisition of "higher" monitor', 'Decay time of "higher" monitor', 'Mass of the "higher" monitor', 'Thermal self shielding correction of "higher" monitor', 'Epithermal self shielding correction of "higher" monitor', 'Decay constant', 'Vertical variability on efficiency', 'Positioning of "lower" monitor', 'Positioning of "higher" monitor', 'f', 'Q0', 'Er', 'α', 'Distance between monitors']#['Specific count rate of monitor 2','k0 factor of monitor 2','Epithermal self shielding value of monitor 2','Resonance integral on thermal cross section value of monitor 2','Effective resonance value of monitor 2','Specific count rate of monitor 3','k0 factor of monitor 3','Epithermal self shielding value of monitor 3','Resonance integral on thermal cross section value of monitor 3','Effective resonance value of monitor 3','Thermal self shielding value','α','Efficiency evaluation']
                        indexes = [(idx_value / indexes.sum(),tag) for idx_value,tag in zip(indexes,description)]
                        indexes.sort(key= lambda x : x[0], reverse=True)
                        text_major_contributors = [f'{format(100*line[0],".1f").rjust(5, " ")} % - {line[1]}' for line in indexes[:5]]
                        textual.append(f'β value found by calculating the slope of the line through two points\n{"".ljust(4)}{"value".ljust(10)}{"u (k=1)".ljust(9)}rel. u\n{"β".ljust(4)}{format(MM.beta,".5f").ljust(10)}{format(MM.ubeta,".5f").ljust(9)}({np.abs(100 * MM.ubeta / MM.beta):.1f} %)\n{warning1}\nList of 5 major contributors to the combined uncertainty of β evaluation:\n'+'\n'.join(text_major_contributors)+'\n')
                        textbox.configure(state='normal')
                        textbox.delete('0.0',END)
                        textbox.insert(END,'\n'.join(textual))
                        textbox.configure(state='disabled')
                        #plot data
                        X_OFFSET= 3
                        x_plot = [0, dx]
                        y_plot = [1, Asp_2 / Asp_1]
                        y_uncplot = np.array([y_plot[0]*np.sqrt(np.power(unp1/np1,2)+np.power(umass_1/mass_1,2)+np.power(relative_displacement(der1,uder1,0.0,udd_1),2)), y_plot[1]*np.sqrt(np.power(unp2/np2,2)+np.power(umass_2/mass_2,2)+np.power(relative_displacement(der1,uder1,0.0,udd_2),2))])
                        AX.grid(False)
                        h = len(AX.lines)
                        for times in range(h):
                            AX.lines.pop(0)
                            try:
                                AX.collections.pop(0)
                            except IndexError:
                                pass
                        AX.errorbar(x_plot, y_plot, yerr=[2*y_uncplot, 2*y_uncplot], marker='o', markersize=3, markerfacecolor='w', markeredgecolor='k', markeredgewidth=0.5, color='r', linestyle='-', linewidth=0.75, elinewidth=0.5, ecolor='k')
                        AX.set_xlim(-X_OFFSET,dx+X_OFFSET)
                        AX.set_ylim(np.min(y_plot)-np.max(y_uncplot)*3,np.max(y_plot)+np.max(y_uncplot)*3)
                        AX.grid(True, linestyle='-.')
                        FIG.tight_layout()
                        CANV.draw()
                
            allowed = {'Au', 'Co'}#question this
            allowed_type = {'I', 'IVB'}
            MM = Toplevel()
            MM.resizable(False,False)
            irrdata=irrdata.irradiation
            if irrdata is not None:
                day,month,year = irrdata.datetime.day,irrdata.datetime.month,irrdata.datetime.year
                hour,minute,second = irrdata.datetime.hour,irrdata.datetime.minute,irrdata.datetime.second
                date=[day,month,year]
                time=[hour,minute,second]
                effe, ueffe = irrdata.f, irrdata.uf
                alpha, ualpha = irrdata.a, irrdata.ua
            else:
                date=[1,1,2019]
                time=[0,0,0]
                effe, ueffe = 0.0, 0.0
                alpha, ualpha = 0.0, 0.0
            MM.title('Thermal flux gradient evaluation')
            MM.spectra = [None,None]
            MM.beta=None
            MM.ubeta=None
            F = Frame(MM)
            listCHN=[line[0] for line in fvalues]
            L=Label(F, text='name', width=7, anchor=W).pack(side=LEFT)
            channel_doublebox = ttk.Combobox(F, values=listCHN, width=20)
            channel_doublebox.pack(side=LEFT)
            channel_doublebox.set(box.get())
            L=Label(F, text='end irr. dd/MM/yyyy', width=20, anchor=E).pack(side=LEFT)
            Day_spinbox = Spinbox(F, from_=1, to=31, width=3, increment=1)
            Day_spinbox.pack(side=LEFT)
            Day_spinbox.delete(0,END)
            Day_spinbox.insert(END,date[0])
            Month_spinbox = Spinbox(F, from_=1, to=12, width=3, increment=1)
            Month_spinbox.pack(side=LEFT)
            Month_spinbox.delete(0,END)
            Month_spinbox.insert(END,date[1])
            Year_spinbox = Spinbox(F, from_=2019, to=2100, width=5, increment=1)
            Year_spinbox.pack(side=LEFT)
            Year_spinbox.delete(0,END)
            Year_spinbox.insert(END,date[2])
            L=Label(F, text='HH:mm:ss', width=12, anchor=E).pack(side=LEFT)
            Hour_spinbox = Spinbox(F, from_=0, to=23, width=3, increment=1)
            Hour_spinbox.pack(side=LEFT)
            Hour_spinbox.delete(0,END)
            Hour_spinbox.insert(END,time[0])
            Minute_spinbox = Spinbox(F, from_=0, to=59, width=3, increment=1)
            Minute_spinbox.pack(side=LEFT)
            Minute_spinbox.delete(0,END)
            Minute_spinbox.insert(END,time[1])
            Second_spinbox = Spinbox(F, from_=0, to=59, width=3, increment=1)
            Second_spinbox.pack(side=LEFT)
            Second_spinbox.delete(0,END)
            Second_spinbox.insert(END,time[2])
            F.pack(anchor=W, padx=5, pady=5)
            
            F = Frame(MM)
            L=Label(F, text='f / 1', width=6, anchor=W).pack(side=LEFT)
            Ieffe_spinbox = Spinbox(F, from_=0.0, to=10000.0, width=6, increment=0.1)
            Ieffe_spinbox.pack(side=LEFT)
            Ieffe_spinbox.delete(0,END)
            Ieffe_spinbox.insert(END,effe)
            L=Label(F, text='', width=3, anchor=W).pack(side=LEFT)
            L=Label(F, text='u(f) / 1', width=6, anchor=W).pack(side=LEFT)
            IUeffe_spinbox = Spinbox(F, from_=0.0, to=100.0, width=6, increment=0.1)
            IUeffe_spinbox.pack(side=LEFT)
            IUeffe_spinbox.delete(0,END)
            IUeffe_spinbox.insert(END,ueffe)
            L=Label(F, text='', width=6, anchor=W).pack(side=LEFT)
            L=Label(F, text='a / 1', width=6, anchor=W).pack(side=LEFT)
            Ialpha_spinbox = Spinbox(F, from_=-1.000, to=1.000, width=7, increment=0.001)
            Ialpha_spinbox.pack(side=LEFT)
            Ialpha_spinbox.delete(0,END)
            Ialpha_spinbox.insert(END,alpha)
            L=Label(F, text='', width=3, anchor=W).pack(side=LEFT)
            L=Label(F, text='u(a) / 1', width=6, anchor=W).pack(side=LEFT)
            IUalpha_spinbox = Spinbox(F, from_=-1.0, to=1.0, width=7, increment=0.001)
            IUalpha_spinbox.pack(side=LEFT)
            IUalpha_spinbox.delete(0,END)
            IUalpha_spinbox.insert(END,ualpha)
            F.pack(anchor=W, padx=5, pady=5)
            
            F = Frame(MM)
            L=Label(F, text='calibration', width=10, anchor=W).pack(side=LEFT)
            values=listeffy()
            calib_omboBCP=ttk.Combobox(F, values=values, state='readonly', width=50)
            calib_omboBCP.pack(side=LEFT)
            L=Label(F, text='', width=8, anchor=W).pack(side=LEFT)
            L=Label(F, text='monitor', width=8, anchor=W).pack(side=LEFT)
            mon_values=[f'{line[2]}-{int(line[3])}{g_discr(line[4])} {line[5]}' for line in A if line[1] in allowed and line[22] in allowed_type]
            moni_omboBCP=ttk.Combobox(F, values=mon_values, state='readonly', width=15)
            moni_omboBCP.pack(side=LEFT)
            F.pack(anchor=W, padx=5, pady=5)
            F_monitors = Frame(MM)
            L=Label(F_monitors, text='position', width=7).grid(row=0,column=0)
            L=Label(F_monitors, text='spectrum filename', width=30).grid(row=0,column=2)
            L=Label(F_monitors, text='mass / g', width=10).grid(row=0,column=4)
            L=Label(F_monitors, text='u(mass) / g', width=10).grid(row=0,column=5)
            L=Label(F_monitors, text='Gs / 1', width=9).grid(row=0,column=6)
            L=Label(F_monitors, text='u(Gs) / 1', width=9).grid(row=0,column=7)
            L=Label(F_monitors, text='Ge / 1', width=9).grid(row=0,column=8)
            L=Label(F_monitors, text='u(Ge) / 1', width=9).grid(row=0,column=9)
            L=Label(F_monitors, text='u(Δd) / mm', width=9).grid(row=0,column=10)
            L=Label(F_monitors, text='L / mm', width=9).grid(row=0,column=11)
            L=Label(F_monitors, text='u(L) / mm', width=9).grid(row=0,column=12)
            L=Label(F_monitors, text='lower', width=7).grid(row=1,column=0)
            L=Label(F_monitors, text='higher', width=7).grid(row=2,column=0)
            B_bot=Button(F_monitors, text='Recall', width=8)
            B_bot.grid(row=1,column=1)
            L_filename_bottom=Label(F_monitors, text='', width=30, anchor=E)
            L_filename_bottom.grid(row=1,column=2)
            B_botpl=Button(F_monitors, text='Peak list', width=8,command=lambda : overlookscreen(MM.spectra[0])).grid(row=1,column=3)
            mass_bot = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
            mass_bot.grid(row=1,column=4)
            umass_bot = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
            umass_bot.grid(row=1,column=5)
            GS_bot = Spinbox(F_monitors, from_=0.000, to=1.000, width=8, increment=0.001)
            GS_bot.grid(row=1,column=6)
            GS_bot.delete(0,END)
            GS_bot.insert(END,1.000)
            UGS_bot = Spinbox(F_monitors, from_=0.000, to=1.000, width=8, increment=0.001)
            UGS_bot.grid(row=1,column=7)
            GE_bot = Spinbox(F_monitors, from_=0.000, to=1.000, width=8, increment=0.001)
            GE_bot.grid(row=1,column=8)
            GE_bot.delete(0,END)
            GE_bot.insert(END,1.000)
            UGE_bot = Spinbox(F_monitors, from_=0.000, to=1.000, width=8, increment=0.001)
            UGE_bot.grid(row=1,column=9)
            DDM_bot = Spinbox(F_monitors, from_=0.0, to=30.0, width=8, increment=0.1)
            DDM_bot.grid(row=1,column=10)
            B_bot.configure(command=lambda MM=MM,namelabel=L_filename_bottom: recall_spectrum_drift(MM,namelabel,0))
            
            B_top=Button(F_monitors, text='Recall', width=8)
            B_top.grid(row=2,column=1)
            L_filename_top=Label(F_monitors, text='', width=30, anchor=E)
            L_filename_top.grid(row=2,column=2)
            B_toppl=Button(F_monitors, text='Peak list', width=8, command=lambda : overlookscreen(MM.spectra[1])).grid(row=2,column=3)
            mass_top = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
            mass_top.grid(row=2,column=4)
            umass_top = Spinbox(F_monitors, from_=0.0000, to=1.0000, width=8, increment=0.0001)
            umass_top.grid(row=2,column=5)
            GS_top = Spinbox(F_monitors, from_=0.000, to=1.000, width=8, increment=0.001)
            GS_top.grid(row=2,column=6)
            GS_top.delete(0,END)
            GS_top.insert(END,1.000)
            UGS_top = Spinbox(F_monitors, from_=0.000, to=1.000, width=8, increment=0.001)
            UGS_top.grid(row=2,column=7)
            GE_top = Spinbox(F_monitors, from_=0.000, to=1.000, width=8, increment=0.001)
            GE_top.grid(row=2,column=8)
            GE_top.delete(0,END)
            GE_top.insert(END,1.000)
            UGE_top = Spinbox(F_monitors, from_=0.000, to=1.000, width=8, increment=0.001)
            UGE_top.grid(row=2,column=9)
            DDM_top = Spinbox(F_monitors, from_=0.0, to=30.0, width=8, increment=0.1)
            DDM_top.grid(row=2,column=10)
            DIS_top = Spinbox(F_monitors, from_=0.0, to=300.0, width=8, increment=0.1)
            DIS_top.grid(row=2,column=11)
            UDIS_top = Spinbox(F_monitors, from_=0.0, to=30.0, width=8, increment=0.1)
            UDIS_top.grid(row=2,column=12)
            B_top.configure(command=lambda MM=MM,namelabel=L_filename_top: recall_spectrum_drift(MM,namelabel,1))
            F_monitors.pack(anchor=W, padx=5, pady=5)
            
            F = Frame(MM)
            F.pack(anchor=W, padx=5, pady=5)
            
            L = Label(MM, text='log').pack(anchor=W, padx=5)
            FSH = Frame(MM)
            F_log = Frame(FSH)
            scrollbar_text = Scrollbar(F_log, orient=VERTICAL)
            textbox = Text(F_log, width=75, heigh=12, yscrollcommand=scrollbar_text.set, wrap=WORD)
            scrollbar_text.config(command=textbox.yview)
            scrollbar_text.pack(side=RIGHT, fill=Y)
            textbox.pack(side=LEFT, fill=BOTH, anchor=NW, expand=1)
            textbox.configure(state='disable')
            F_log.pack(side=LEFT)
            
            F_grap = Frame(FSH)
            f = Figure(figsize=(3.8, 1.7))
            ax_fit=f.add_subplot(111)
            Figur=Frame(F_grap)
            Figur.pack(anchor=CENTER, fill=BOTH, expand=1)
            canvas = FigureCanvasTkAgg(f, master=Figur)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            ax_fit.set_xlim(0,None)
            ax_fit.set_ylim(0,2)
            ax_fit.set_ylabel(r'$C_\mathrm{sp\:n}$ / 1 ($k=2$)')
            ax_fit.set_xlabel(r'$L$ / mm')
            ax_fit.grid(True, linestyle='-.')
            f.tight_layout()
            canvas.draw()
            F_grap.pack(side=RIGHT, anchor=NE, padx=5, fill=BOTH)
            FSH.pack(anchor=W, padx=5, pady=5, fill=X)
            
            F = Frame(MM)
            B_calculatedrift = Button(F, text='Evaluate', width=8, command=lambda DAY=Day_spinbox, MONTH=Month_spinbox, YEAR=Year_spinbox, HOUR=Hour_spinbox, MINUTE=Minute_spinbox, SECOND=Second_spinbox, IEFFE=Ieffe_spinbox, IUEFFE=IUeffe_spinbox, IALPHA=Ialpha_spinbox, IUALPHA=IUalpha_spinbox, calib=calib_omboBCP, monit=moni_omboBCP, MM=MM, MASS_1=mass_bot, UMASS_1=umass_bot, MASS_2=mass_top, UMASS_2=umass_top, GS_1=GS_bot, UGS_1=UGS_bot, GS_2=GS_top, UGS_2=UGS_top, GE_1=GE_bot, UGE_1=UGE_bot, GE_2=GE_top, UGE_2=UGE_top, UDD_1=DDM_bot, UDD_2=DDM_top, DX=DIS_top, UDX=UDIS_top, textbox=textbox, AX=ax_fit, FIG=f, CANV=canvas : calculate_thermal_drift(DAY,MONTH,YEAR,HOUR,MINUTE,SECOND,IEFFE,IUEFFE,IALPHA,IUALPHA,calib,monit,MM,MASS_1,UMASS_1,MASS_2,UMASS_2,GS_1,UGS_1,GS_2,UGS_2,GE_1,UGE_1,GE_2,UGE_2,UDD_1,UDD_2,DX,UDX,textbox,AX,FIG,CANV))
            B_calculatedrift.pack(side=LEFT)
            B_savedrift = Button(F, text='Save', width=8, command= lambda : flux_drift_save(MM,box,fvalues,BETAS,UBETAS,channel_doublebox))
            B_savedrift.pack(side=LEFT)
            F.pack(anchor=W, padx=5, pady=5)
            
        def flux_drift_delete(box,fvalues):
            for line in fvalues:
                if box.get()==line[0]:
                    fvalues.remove(line)
                    break
            box['values'] = [line[0] for line in fvalues]
            box.set('')
            with open('data/irradiations/irr_var.txt','w') as f:
                f.write('#Irradiation trend data {This line is for comments and is ignored}\n')
                for line in fvalues:
                    f.write(f'{line[0]} {line[1]} {line[2]}\n')
            
        def split_strip(item):
            nuc,ene=str.split(item)
            N,Ai=str.split(nuc,'-')
            if Ai[-1]=='m':
                Ai=Ai.replace('m','')
                mg=2.0
            else:
                mg=1.0
            ene=float(ene)
            Ai=float(Ai)
            for t in A:
                if N==t[2] and Ai==t[3] and mg==t[4] and ene==t[5]:
                    mnuclide=t
                    break
            return mnuclide
        
        def ordemeprogresso(Plist,idx=22):
            indexlst=[]
            for y in A:
                if y[1] not in indexlst:
                    indexlst.append(y[1])
            ordered_list=[]
            for lx in indexlst:
                for ix in Plist:
                    if ix[idx]==lx:
                        ordered_list.append(ix)
            return ordered_list
            
        def do_everything(NAA,nomefile):
            """Start analysis"""
            monitor=None
            if NAA.standard_comparator[0]!=None:
                mnuclide=split_strip(NAA.standard_comparator[1])
                monitor=NAA.comparator.peak_list[NAA.standard_comparator[0]]+mnuclide
                total_assigned_peaklist=[]
                total_residus_list=[]
                for agn in NAA.sample:
                    analyte_assigned_list=[]
                    try:
                        for y in range(len(agn.assign_nuclide)):
                            if agn.assign_nuclide[y]!='':
                                ln=split_strip(agn.assign_nuclide[y])
                                analyte_assigned_list.append((agn.peak_list[y]+ln))
                    except TypeError:
                        analyte_assigned_list=[]
                    if analyte_assigned_list!=[]:
                        #order list
                        analyte_assigned_list=ordemeprogresso(analyte_assigned_list)
                    total_assigned_peaklist.append(analyte_assigned_list)
                    #unidentified to modify
                    partial_residus=agn.peak_list[:]
                    for hkl in analyte_assigned_list:
                        if hkl[:21] in partial_residus:
                            partial_residus.remove(hkl[:21])
                    total_residus_list.append(partial_residus)
                NAA.analysis_from_assignednuclides(total_assigned_peaklist,monitor)
            #Detection limit
            cumulate_peaklist=[]
            cumulate_detection=[]
            if NAA.selected_nuclides!=[] and monitor!=None and NAA.calibration!=None:
                nuclides_to_investigate=[]
                for aa in NAA.selected_nuclides:
                    for ii in A:
                        if ii[1]==aa:
                             nuclides_to_investigate.append(ii)
                nuclides_to_investigate=ordemeprogresso(nuclides_to_investigate,1)
                cumulate_peaklist=[]
                cumulate_detection=[]
                for klm in range(len(NAA.sample)):
                    nuclides_to_investigate_sorted=nuclides_to_investigate[:]
                    for ksa in total_assigned_peaklist[klm]:
                        if ksa[21:] in nuclides_to_investigate_sorted:
                            nuclides_to_investigate_sorted.remove(ksa[21:])
                    Quantified,Detection,MQ,MD=NAA.analysis_from_nuclidelist(monitor,nuclides_to_investigate_sorted,klm,float(tolerance_energy))
                    for hkl in Quantified:
                        if hkl[:21] in total_residus_list[klm]:
                            total_residus_list[klm].remove(hkl[:21])
                    cumulate_peaklist.append((Quantified,MQ))
                    cumulate_detection.append((Detection,MD))
                    if len(NAA.sample[klm].spectrumpath)>40:
                        print(NAA.sample[klm].spectrumpath[-39:])
                    else:
                        print(NAA.sample[klm].spectrumpath)
                    if NAA.quantification[klm]!=None:
                        print('user-identified from spectrum',len(NAA.quantification[klm]))
                    else:
                        print('user-identified from spectrum 0')
                    #print('total lines',len(nuclides_to_investigate_sorted))
                    #print('quantified',len(Quantified))
                    print('detection limits',len(Detection))
                    print()
            writeonfile(nomefile,NAA,monitor,total_assigned_peaklist,cumulate_peaklist,cumulate_detection,total_residus_list)
            
        def outcome(message):
            NF=Toplevel()
            NF.title('Message')
            NF.resizable(False,False)
            L=Label(NF).pack()
            L=Label(NF, text=message, width=60).pack()
            L=Label(NF).pack()
            NF.focus()
            event="<FocusOut>"
            NF.bind(event, lambda event=event,G=NF : G.destroy())
        
        def check_allright(EMC,EUMC,EMS,EUMS,EDDC,EDDS,EMUD,EUMUD,EGTHC,EUGTHC,EGEC,EUGEC,EGTHS,EUGTHS,ECOIC,EUCOIC,EWC,EUWC,BETAS,UBETAS,DXS,UDXS,NAA):
            try:
                float(EMC.get())
                float(EUMC.get())
                float(EMS.get())
                float(EUMS.get())
                float(EDDC.get())
                float(EDDS.get())
                float(EMUD.get())
                float(EUMUD.get())
                float(EGTHC.get())
                float(EUGTHC.get())
                float(EGEC.get())
                float(EUGEC.get())
                float(EGTHS.get())
                float(EUGTHS.get())
                float(ECOIC.get())
                float(EUCOIC.get())
                float(EWC.get())
                float(EUWC.get())
                float(BETAS.get())
                float(UBETAS.get())
                float(DXS.get())
                float(UDXS.get())
            except:
                messagebox.showerror('Invalid data entered','values in the spin-boxes should have floating point data type')
                print('Invalid data entered\na) values in the spin-boxes should have floating point data type')
            else:
                if float(EMC.get())>0 and float(EMS.get())>0 and float(EWC.get()):
                    NAA.masses=[float(EMC.get()),float(EUMC.get()),float(EMS.get()),float(EUMS.get())]
                    NAA.ddcomparator,NAA.ddsample=float(EDDC.get()),float(EDDS.get())
                    NAA.detector_mu=[float(EMUD.get()),float(EUMUD.get())]
                    NAA.comparatorselfshieldingth=[float(EGTHC.get()),float(EUGTHC.get())]
                    NAA.comparatorselfshieldingepi=[float(EGEC.get()),float(EUGEC.get())]
                    NAA.comparatorCOI=[float(ECOIC.get()),float(EUCOIC.get())]
                    NAA.sampleselfshieldingth=[float(EGTHS.get()),float(EUGTHS.get())]
                    NAA.comparatormassfraction=[float(EWC.get()),float(EUWC.get())]
                    NAA.beta_flux=[float(BETAS.get()),float(UBETAS.get())]
                    NAA._Delta_x=[float(DXS.get()),float(UDXS.get())]
                    if NAA.comparator!=None and NAA.irradiation!=None and NAA.sample!=None and NAA.standard_comparator!=[None,None] and NAA.calibration!=None:#Add something here
                        fileTypes = [('Excel file', '.xlsx')]
                        nomefile=asksaveasfilename(filetypes=fileTypes, defaultextension='.xlsx')
                        if nomefile!=None and nomefile!='':
                            try:
                                do_everything(NAA,nomefile)
                                outcome('Excel file successfully created!')
                                print('Complete!')
                            except:
                                outcome('Some error occurred! Incomplete file saved')
                    elif NAA.calibration==None:
                        outcome('Detector calibration is required')
                    elif NAA.standard_comparator==[None,None]:
                        outcome('Emission for comparator has not been selected')
                    else:
                        outcome('Check irradiation, sample and standard data selection')
                else:
                    outcome('sample and standard masses, and monitor mass fraction\nmust be greater than 0')
        
        heightsize=10
        logo = PhotoImage(file='k0log.gif')
        F=Frame(M)
        F1=Frame(F)
        L=Label(F1, text='', width=1).pack(side=LEFT)
        L=Label(F1, image=logo)
        L.image = logo
        L.pack(side=LEFT)
        F1.pack(anchor=W, side=LEFT, fill=X, expand=1)
        F2=Frame(F)
        L=Label(F2, text='', width=1).pack(side=RIGHT)
        Bopti=Button(F2, text='Elaborate', width=8)
        Bopti.pack(side=RIGHT)
        BHPL=Button(F2, text='Input workbook', width=13, command=lambda : create_HyperLabmanually())
        BHPL.pack(side=RIGHT)
        BSTTGS=Button(F2, text='Settings', width=8, command=lambda M=M : settings_modifications(M))
        BSTTGS.pack(side=RIGHT)
        F2.pack(anchor=E, side=RIGHT, fill=X, expand=1)
        F.pack(pady=heightsize, fill=X, expand=1)
        separator = ttk.Separator(M, orient="horizontal")
        separator.pack(fill=X,expand=1)
        
        #Background
        F=Frame(M)
        L=Label(F, text='', width=1).pack(side=LEFT)
        BB=Button(F, text='Background', width=10)
        BB.pack(side=LEFT)
        L=Label(F, text='filename:', width=8).pack(side=LEFT)
        LBB=Label(F, width=40, anchor=W)
        LBB.pack(side=LEFT)
        L=Label(F, text='peaks:', width=5).pack(side=LEFT)
        LPKS=Label(F, width=5, anchor=W)
        LPKS.pack(side=LEFT)
        L=Label(F, text='start:', width=6).pack(side=LEFT)
        LDT=Label(F, width=20, anchor=W)
        LDT.pack(side=LEFT)
        BTCB=Button(F, text='Peak list', width=8, command= lambda BB=BB,NAA=NAA : overlook(BB,NAA))
        BTCB.pack(side=LEFT, anchor=W)
        BB.configure(command=lambda BB=BB,NAA=NAA,LBB=LBB,LPKS=LPKS,LDT=LDT : openpeaklistandspectrum(BB,NAA,LBB,LPKS,LDT))
        F.pack(anchor=W, pady=heightsize)
        separator = ttk.Separator(M, orient="horizontal")
        separator.pack(fill=X,expand=1)

        FB=Frame(M)
        F=Frame(FB)
        L=Label(F, text='', width=1).pack(side=LEFT)
        BTNZC=Button(F, text='Calibration', width=10)
        BTNZC.pack(side=LEFT)
        L=Label(F, text='', width=1).pack(side=LEFT)
        values=listeffy()
        varCPEF=StringVar(M)
        effy_omboBCP=ttk.Combobox(F, values=values, state='readonly', width=63)
        effy_omboBCP.pack(side=LEFT)
        L=Label(F, text='', width=1).pack(side=LEFT)
        ewent='<<ComboboxSelected>>'
        effy_omboBCP.bind(ewent, lambda event=ewent,box=effy_omboBCP,NAA=NAA : selectionecomboselected(box,NAA))
        BTNZC.configure(command=lambda CB_master=effy_omboBCP : new_calibrations(CB_master))
        BTNRNM=Button(F, text='Rename', width=8)
        BTNRNM.configure(command=lambda EC=effy_omboBCP, BT=BTNRNM,NAA=NAA : rename_itemlist(EC,BT,NAA))
        BTNRNM.pack(side=LEFT)
        BTNRCHG=Button(F, text='Delete', width=8, command=lambda EC=effy_omboBCP,NAA=NAA : delete_list(EC,NAA))
        BTNRCHG.pack(side=LEFT)
        BTSEC=Button(F, text='Show', width=8, command=lambda box=effy_omboBCP : showfit(box))
        BTSEC.pack(side=LEFT)
        F.pack(anchor=W)
        
        F=Frame(FB)
        L=Label(F, text='', width=13).pack(side=LEFT)
        L_EC=Label(F, text='μ / 1', width=9, anchor=W)
        L_EC.pack(side=LEFT)
        EMUD=Spinbox(F, from_=-1, to=1, width=10, increment=0.00001)
        EMUD.pack(side=LEFT)
        EMUD.delete(0,END)
        EMUD.insert(END,'0.00000')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(μ) / 1', width=10, anchor=W).pack(side=LEFT)
        EUMUD=Spinbox(F, from_=-1, to=1, width=10, increment=0.00001)
        EUMUD.pack(side=LEFT)
        EUMUD.delete(0,END)
        EUMUD.insert(END,'0.00000')
        USH=Button(F, text='o', relief='flat', command=lambda L='Calibration - u(μ) / 1',u=EUMUD : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        F.pack(anchor=W)
        FB.pack(anchor=W, pady=heightsize)
        separator = ttk.Separator(M, orient="horizontal")
        separator.pack(fill=X,expand=1)
        
        #Irradiation
        FB=Frame(M)
        F=Frame(FB)
        L=Label(F, text='', width=1).pack(side=LEFT)
        BIR=Button(F, text='Irradiation', width=10)
        BIR.pack(side=LEFT)
        L=Label(F, text='channel:', width=8).pack(side=LEFT)
        LCH=Label(F, width=22)
        LCH.pack(side=LEFT)
        L=Label(F, text='f / 1:', width=5).pack(side=LEFT)
        LF=Label(F, width=8, anchor=W)
        LF.pack(side=LEFT)
        L=Label(F, text='α / 1:', width=5).pack(side=LEFT)
        LALF=Label(F, width=8, anchor=W)
        LALF.pack(side=LEFT)
        L=Label(F, text='end irr:', width=6).pack(side=LEFT)
        LIDT=Label(F, width=20, anchor=W)
        LIDT.pack(side=LEFT)
        L=Label(F, text='ti / s:', width=5).pack(side=LEFT)
        LITM=Label(F, width=12, anchor=W)
        LITM.pack(side=LEFT)
        F.pack(anchor=W)
        BIR.configure(command=lambda BIR=BIR,NAA=NAA,LCH=LCH,LF=LF,LALF=LALF,LIDT=LIDT,LITM=LITM : irradiation_info(BIR,NAA,LCH,LF,LALF,LIDT,LITM))
        
        F=Frame(FB)
        L=Label(F, text='', width=13).pack(side=LEFT)
        L=Label(F, text='β / mm-1', width=9, anchor=W).pack(side=LEFT)
        BETAS=Spinbox(F, from_=-0.10, to=0.10, width=10, increment=0.0001)
        BETAS.pack(side=LEFT)
        BETAS.delete(0,END)
        BETAS.insert(END,'0.0000')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(β) / mm-1', width=10, anchor=W).pack(side=LEFT)
        UBETAS=Spinbox(F, from_=0, to=0.2, width=10, increment=0.0001)
        UBETAS.pack(side=LEFT)
        UBBSH=Button(F, text='o', relief='flat', command=lambda L='Irradiation - u(β) / mm-1',u=UBETAS : uncertainty_shaper(L,u))
        UBBSH.pack(side=LEFT)
        L=Label(F, text='', width=1).pack(side=RIGHT)
        BBETDEL=Button(F, text='Delete', width=8)
        BBETDEL.pack(side=RIGHT)
        #BBETSAL=Button(F, text='Save', width=8)#, command= lambda BC=BC,NAA=NAA : overlook(BC,NAA))
        #BBETSAL.pack(side=RIGHT)
        BBETEVAL=Button(F, text='Evaluate', width=8)
        BBETEVAL.pack(side=RIGHT)
        L=Label(F, text='', width=1, anchor=W).pack(side=RIGHT)
        flistv,fvalues=openchannels_drift_values('data/irradiations/irr_var.txt')
        fluxdrift_omboBCP=ttk.Combobox(F, values=flistv, state='readonly', width=20)
        fluxdrift_omboBCP.pack(side=RIGHT)
        L=Label(F, text='recall', width=6, anchor=W).pack(side=RIGHT)
        F.pack(anchor=W, fill=X,expand=1)
        FB.pack(anchor=W, pady=heightsize, fill=X,expand=1)
        
        fluxdrift_omboBCP.bind(ewent, lambda event=ewent,box=fluxdrift_omboBCP,fvalues=fvalues,BETAS=BETAS,UBETAS=UBETAS : flux_drift_select(box,fvalues,BETAS,UBETAS))
        BBETDEL.configure(command=lambda box=fluxdrift_omboBCP,fvalues=fvalues : flux_drift_delete(box,fvalues))
        BBETEVAL.configure(command=lambda box=fluxdrift_omboBCP,fvalues=fvalues,BETAS=BETAS,UBETAS=UBETAS,irrdata=NAA : flux_drift_evaluate(box,fvalues,BETAS,UBETAS,irrdata))
        separator = ttk.Separator(M, orient="horizontal")
        separator.pack(fill=X,expand=1)
        
        #Sample
        FB=Frame(M)
        F=Frame(FB)
        L=Label(F, text='', width=1).pack(side=LEFT)
        BS=Button(F, text='Sample', width=10)
        BS.pack(side=LEFT)
        L=Label(F, text='filename:', width=8).pack(side=LEFT)
        LBS=Label(F, width=40, anchor=W)
        LBS.pack(side=LEFT)
        L=Label(F, text='peaks:', width=5).pack(side=LEFT)
        LPKSS=Label(F, width=5, anchor=W)
        LPKSS.pack(side=LEFT)
        L=Label(F, text='start:', width=6).pack(side=LEFT)
        LDTS=Label(F, width=20, anchor=W)
        LDTS.pack(side=LEFT)
        BTCS=Button(F, text='Peak list', width=8, command= lambda BS=BS,NAA=NAA : overlook(BS,NAA))
        BTCS.pack(side=LEFT)
        BTCAll=Button(F, text='Clear', width=8, command= lambda NAA=NAA,LBS=LBS,LPKSS=LPKSS,LDTS=LDTS : clearall(NAA,LBS,LPKSS,LDTS))
        BTCAll.pack(side=LEFT)
        BS.configure(command=lambda BS=BS,NAA=NAA,LBS=LBS,LPKSS=LPKSS,LDTS=LDTS : openpeaklistandspectrum(BS,NAA,LBS,LPKSS,LDTS))
        L=Label(F, text='', width=1).pack(side=LEFT)
        F.pack(anchor=W)
        
        F=Frame(FB)
        L=Label(F, text='', width=13).pack(side=LEFT)
        L=Label(F, text='m / g', width=9, anchor=W).pack(side=LEFT)
        EMS=Spinbox(F, from_=0, to=1000, width=10, increment=0.000001)
        EMS.pack(side=LEFT)
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(m) / g', width=10, anchor=W).pack(side=LEFT)
        EUMS=Spinbox(F, from_=0, to=1000, width=10, increment=0.000001)
        EUMS.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Sample - u(m) / g',u=EUMS : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        F.pack(anchor=W)
        
        F=Frame(FB)
        L=Label(F, text='', width=13).pack(side=LEFT)
        L=Label(F, text='Gth / 1', width=9, anchor=W).pack(side=LEFT)
        EGTHS=Spinbox(F, from_=0, to=2, width=10, increment=0.001)
        EGTHS.pack(side=LEFT)
        EGTHS.delete(0,END)
        EGTHS.insert(END,'1.000')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(Gth) / 1', width=10, anchor=W).pack(side=LEFT)
        EUGTHS=Spinbox(F, from_=0, to=2, width=10, increment=0.001)
        EUGTHS.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Sample - u(Gth) / 1',u=EUGTHS : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        F.pack(anchor=W)
        
        F=Frame(FB)
        L=Label(F, text='', width=13).pack(side=LEFT)
        L=Label(F, text='Δd / mm', width=9, anchor=W).pack(side=LEFT)
        DDDS=Spinbox(F, from_=-10, to=10, width=10, increment=0.1)
        DDDS.pack(side=LEFT)
        DDDS.delete(0,END)
        DDDS.insert(END,'0.0')
        DDDS.configure(state='disabled')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(Δd) / mm', width=10, anchor=W).pack(side=LEFT)
        EDDS=Spinbox(F, from_=0, to=50, width=10, increment=0.1)
        EDDS.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Sample - u(Δd) / mm',u=EDDS : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        
        L=Label(F, text='', width=6).pack(side=LEFT)
        L=Label(F, text='Δx / mm', width=9, anchor=W).pack(side=LEFT)
        DXS=Spinbox(F, from_=-100, to=100, width=10, increment=0.1)
        DXS.pack(side=LEFT)
        DXS.delete(0,END)
        DXS.insert(END,'0.0')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(Δx) / mm', width=10, anchor=W).pack(side=LEFT)
        UDXS=Spinbox(F, from_=0, to=15, width=10, increment=0.1)
        UDXS.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Sample - u(Δx) / mm',u=UDXS : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        
        F.pack(anchor=W)
        FB.pack(anchor=W, pady=heightsize)
        
        separator = ttk.Separator(M, orient="horizontal")
        separator.pack(fill=X,expand=1)
        
        #Standard
        FB=Frame(M)
        F=Frame(FB)
        L=Label(F, text='', width=1).pack(side=LEFT)
        BC=Button(F, text='Standard', width=10)
        BC.pack(side=LEFT)
        L=Label(F, text='filename:', width=8).pack(side=LEFT)
        LBC=Label(F, width=40, anchor=W)
        LBC.pack(side=LEFT)
        L=Label(F, text='peaks:', width=5).pack(side=LEFT)
        LPKSC=Label(F, width=5, anchor=W)
        LPKSC.pack(side=LEFT)
        L=Label(F, text='start:', width=6).pack(side=LEFT)
        LDTC=Label(F, width=20, anchor=W)
        LDTC.pack(side=LEFT)
        BTCC=Button(F, text='Peak list', width=8, command= lambda BC=BC,NAA=NAA : overlook(BC,NAA))
        BTCC.pack(side=LEFT)
        BC.configure(command=lambda BC=BC,NAA=NAA,LBC=LBC,LPKSC=LPKSC,LDTC=LDTC : openpeaklistandspectrum(BC,NAA,LBC,LPKSC,LDTC))
        F.pack(anchor=W)
        
        F=Frame(FB)
        L=Label(F, text='', width=13).pack(side=LEFT)
        L=Label(F, text='m / g', width=9, anchor=W).pack(side=LEFT)
        EMC=Spinbox(F, from_=0, to=1000, width=10, increment=0.000001)
        EMC.pack(side=LEFT)
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(m) / g', width=10, anchor=W).pack(side=LEFT)
        EUMC=Spinbox(F, from_=0, to=1000, width=10, increment=0.000001)
        EUMC.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Comparator - u(m) / g',u=EUMC : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        L=Label(F, text='', width=6).pack(side=LEFT)
        L=Label(F, text='w / g g-1', width=9, anchor=W).pack(side=LEFT)
        EWC=Spinbox(F, from_=0, to=1, width=10, increment=0.001)
        EWC.pack(side=LEFT)
        EWC.delete(0,END)
        EWC.insert(END,'1.000')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(w) / g g-1', width=10, anchor=W).pack(side=LEFT)
        EUWC=Spinbox(F, from_=0, to=1, width=10, increment=0.001)
        EUWC.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Comparator - u(w) / g g-1',u=EUWC : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        F.pack(anchor=W)
        
        F=Frame(FB)
        L=Label(F, text='', width=13).pack(side=LEFT)
        L=Label(F, text='Gth / 1', width=9, anchor=W).pack(side=LEFT)
        EGTHC=Spinbox(F, from_=0, to=2, width=10, increment=0.001)
        EGTHC.pack(side=LEFT)
        EGTHC.delete(0,END)
        EGTHC.insert(END,'1.000')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(Gth) / 1', width=10, anchor=W).pack(side=LEFT)
        EUGTHC=Spinbox(F, from_=0, to=2, width=10, increment=0.001)
        EUGTHC.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Comparator - u(Gth) / 1',u=EUGTHC : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        L=Label(F, text='', width=6).pack(side=LEFT)
        L=Label(F, text='Ge / 1', width=9, anchor=W).pack(side=LEFT)
        EGEC=Spinbox(F, from_=0, to=2, width=10, increment=0.001)
        EGEC.pack(side=LEFT)
        EGEC.delete(0,END)
        EGEC.insert(END,'1.000')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(Ge) / 1', width=10, anchor=W).pack(side=LEFT)
        EUGEC=Spinbox(F, from_=0, to=2, width=10, increment=0.001)
        EUGEC.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Comparator - u(Ge) / 1',u=EUGEC : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        F.pack(anchor=W)
        
        F=Frame(FB)
        L=Label(F, text='', width=13).pack(side=LEFT)
        L=Label(F, text='Δd / mm', width=9, anchor=W).pack(side=LEFT)
        DDDM=Spinbox(F, from_=-10, to=10, width=10, increment=0.1)
        DDDM.pack(side=LEFT)
        DDDM.delete(0,END)
        DDDM.insert(END,'0.0')
        DDDM.configure(state='disabled')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(Δd) / mm', width=10, anchor=W).pack(side=LEFT)
        EDDC=Spinbox(F, from_=0, to=50, width=10, increment=0.1)
        EDDC.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Comparator - u(Δd) / mm',u=EDDC : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        L=Label(F, text='', width=6).pack(side=LEFT)
        L=Label(F, text='COI / 1', width=9, anchor=W).pack(side=LEFT)
        ECOIC=Spinbox(F, from_=0, to=2, width=10, increment=0.001)
        ECOIC.pack(side=LEFT)
        ECOIC.delete(0,END)
        ECOIC.insert(END,'1.000')
        L=Label(F, text='', width=2).pack(side=LEFT)
        L=Label(F, text='u(COI) / 1', width=10, anchor=W).pack(side=LEFT)
        EUCOIC=Spinbox(F, from_=0, to=2, width=10, increment=0.001)
        EUCOIC.pack(side=LEFT)
        USH=Button(F, text='o', relief='flat', command=lambda L='Comparator - u(COI) / 1',u=EUCOIC : uncertainty_shaper(L,u))
        USH.pack(side=LEFT)
        F.pack(anchor=W)
        
        FB.pack(anchor=W, pady=heightsize)
        
        separator = ttk.Separator(M, orient="horizontal")
        separator.pack(fill=X,expand=1)
        
        F=Frame(M)
        L=Label(F, text='', width=1).pack(side=LEFT)
        Binv_nucl=Button(F, text='Detection limits')
        Binv_nucl.pack(side=LEFT)
        Linv_nucl=Label(F, text=f'{len(NAA.selected_nuclides)} elements', width=15)
        Linv_nucl.pack(side=LEFT)
        Binv_nucl.configure(command=lambda NASN=NAA.selected_nuclides,Lb=Linv_nucl: select_nuclides_k0(NASN,Lb))
        F.pack(anchor=W, pady=heightsize)
        Bopti.configure(command=lambda EMC=EMC,EUMC=EUMC,EMS=EMS,EUMS=EUMS,EDDC=EDDC,EDDS=EDDS,EMUD=EMUD,EUMUD=EUMUD,EGTHC=EGTHC,EUGTHC=EUGTHC,EGEC=EGEC,EUGEC=EUGEC,EGTHS=EGTHS,EUGTHS=EUGTHS,ECOIC=ECOIC,EUCOIC=EUCOIC,EWC=EWC,EUWC=EUWC,BETAS=BETAS,UBETAS=UBETAS,DXS=DXS,UDXS=UDXS,NAA=NAA : check_allright(EMC,EUMC,EMS,EUMS,EDDC,EDDS,EMUD,EUMUD,EGTHC,EUGTHC,EGEC,EUGEC,EGTHS,EUGTHS,ECOIC,EUCOIC,EWC,EUWC,BETAS,UBETAS,DXS,UDXS,NAA))
    
    def on_closing():
        if messagebox.askokcancel('Quit k0-INRIM', 'Unsaved data will be lost.\n\nDo you want to quit?'):
            M.destroy()
    M=Tk()
    M.title('Main')
    M.resizable(False,False)
    M.protocol("WM_DELETE_WINDOW", on_closing)
    mainscreen(M,NAA)
    M.mainloop()

if __name__=='__main__':
    main()
