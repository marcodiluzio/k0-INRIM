import os
import tkinter

def adjust_things(messagebox,recovery_file='requirements.txt',see_list=True):
    """
    Call to pip from the prompt of the system, only Windows for the moment!
    """
    #works on Windows systems!
    os.system(f'cmd /k "pip install --upgrade -r {recovery_file}"')
    if see_list:
        os.system('cmd /c "pip list"')
    messagebox.destroy()

def recovery():
    """
    Message with script for auto installation of missing required python modules
    """
    messagebox = tkinter.Tk()
    messagebox.title('Required python modules have not been found.')
    messagebox.resizable(False, False)
    tkinter.Label(messagebox, text='The required modules (modules name and version are found in the requirements.txt file)\nwill be installed in your current python environment,\notherwise you will need to manually manage the additional packages.\nInternet connection is necessary.\n').grid(row=0, column=0, columnspan=2, padx=5, pady=5)
    tkinter.Button(messagebox, text='Accept', width=10, command=lambda : adjust_things(messagebox)).grid(row=1, column=0, pady=5)
    tkinter.Button(messagebox, text='Refuse', width=10, command=lambda : messagebox.destroy()).grid(row=1, column=1, pady=5)
    messagebox.mainloop()