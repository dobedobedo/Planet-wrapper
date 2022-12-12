# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 13:54:30 2018

@author: uqytu1
"""

import tkinter as tk
from tkinter.font import Font
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showerror, showinfo, askyesno, askquestion
from tkinter import ttk
from tkinter.ttk import Style
import os
import sys
import gc
import getpass
import json
from threading import Thread
from time import sleep
from datetime import datetime, timedelta
import webbrowser
from planet import api

def CleanWidget(parent):
    # This function tries to clean all the widgets to avoid garbages
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype in ('TFrame', 'TLabelframe'):
            CleanWidget(child)
            child = None
        else:
            child = None

def AuthInputBox():
    class GetAPIKey:
        @staticmethod
        def get_from_account(_email, _password):
            return api.ClientV1().login(_email, _password)['api_key']

        @staticmethod
        def get_from_input(_input):
            return _input
            
    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            self.resizable(width=False, height=False)
            self.title('Authentication')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)

            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = int(w/2 - size[0]/2)
            y = int(h/2 - size[1]/2)
            self.geometry('+{}+{}'.format(x, y))
            
            # Apply system scaling factor
            dpi = self.winfo_fpixels('1i')
            scaling = dpi/72
            self.tk.call('tk', 'scaling', scaling)
            ScaledFont = Font()
            ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
            Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TEntry', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))

        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)
            
    class Account(ttk.Frame):
        def __init__(self, container, KeyMethod):
            super().__init__(container)

            self.KeyMethod = KeyMethod

            # Set API Key variable
            self.API_KEY = tk.StringVar(self, name='API_KEY')
            
            # Email
            self.Label = ttk.Label(self, text='Planet account email:')
            self.Label.grid(column=0, row=0, padx=5, pady=5)
            self.email = ttk.Entry(self)
            self.email.bind('<Return>', self.jump_to_pwd)
            self.email.bind('<KP_Enter>', self.jump_to_pwd)
            self.email.bind('<Tab>', self.jump_to_pwd)
            self.email.grid(column=0, row=1, padx=5, pady=5)

            # Password
            self.Label = ttk.Label(self, text='Planet account password:')
            self.Label.grid(column=0, row=2, padx=5, pady=5)
            self.password = ttk.Entry(self, show='*')
            self.password.bind('<Return>', self.get_Key)
            self.password.bind('<KP_Enter>', self.get_Key)
            self.password.grid(column=0, row=3, padx=5, pady=5)

            # OK button
            self.Ok = ttk.Button(self,text='Ok')
            self.Ok.bind('<Button-1>', self.get_Key)
            self.Ok.grid(column=0, row=4, padx=5, pady=5)

            # Draw
            self.grid(column=0, row=0, padx=5, pady=5, sticky='ns')
        
        def jump_to_pwd(self, event):
            self.password.focus()
        
        # Planet login
        def get_Key(self, event):
            self.PL_acc = self.email.get()
            self.PL_pwd = self.password.get()
            if len(self.PL_acc) == 0 or len(self.PL_pwd) == 0:
                showerror('Warning!', 'Input cannot be blank!')
            else:
                try:
                    API_KEY = self.KeyMethod(self.PL_acc, self.PL_pwd)
                    self.setvar(name='API_KEY', value=API_KEY)
                    self.quit()
                except api.exceptions.InvalidIdentity:
                    showerror('Authentication failed!', 'Invalid email or password.')
                    self.reset()
                except api.exceptions.APIException:
                    showerror('Input error', 'Invalid parameters.')
                    self.reset()

        def reset(self):
            self.email.delete(0, 'end')
            self.password.delete(0, 'end')

    class APIKey(ttk.Frame):
        def __init__(self, container, KeyMethod):
            super().__init__(container)

            self.KeyMethod = KeyMethod

            # Input API Key
            self.API_KEY = tk.StringVar(self, name='API_KEY')
            self.Label = ttk.Label(self, text='Planet API Key:')
            self.Label.grid(column=0, row=0, padx=5, pady=5)
            self.APIKey = ttk.Entry(self, textvariable=self.API_KEY, show='*')
            self.APIKey.bind('<Return>', self.get_Key)
            self.APIKey.bind('<KP_Enter>', self.get_Key)
            self.APIKey.grid(column=0, row=1, padx=5, pady=5)
            
            # OK button
            self.Ok = ttk.Button(self,text='Ok')
            self.Ok.bind('<Button-1>', self.get_Key)
            self.Ok.grid(column=0, row=2, padx=5, pady=5)

            # Draw
            self.grid(column=0, row=0, padx=5, pady=5, sticky='ns')
            
        def get_Key(self, event):
            API_KEY = self.KeyMethod(self.APIKey.get())
            if len(API_KEY) == 0:
                showerror('Warning!', 'Input cannot be blank!')
            else:
                try:
                    api.ClientV1(API_KEY).get_searches()
                    self.setvar(name='API_KEY', value=API_KEY)
                    self.quit()
                except api.exceptions.InvalidAPIKey:
                    showerror('Authentication failed!', 'Invalid API Key')
                    self.reset()
                except requests.exceptions.InvalidHeader:
                    showerror('Authentication failed!', 'Invalid return character')
                    self.reset()

        def reset(self):
            self.APIKey.delete(0, 'end')

    class ControlFrame(ttk.LabelFrame):
        def __init__(self, container):

            super().__init__(container)
            self['text'] = 'Login method'

            # Radio buttons of login methods
            self.selected_value = tk.IntVar()
            ttk.Radiobutton(
                self,
                text='email and password',
                value=0,
                variable=self.selected_value,
                command=self.change_frame).grid(column=0, row=0, padx=5, pady=5)
            ttk.Radiobutton(
                self,
                text='API Key',
                value=1,
                variable=self.selected_value,
                command=self.change_frame).grid(column=1, row=0, padx=5, pady=5)
            self.grid(column=0, row=1, padx=5, pady=5, sticky='ew')

            # Initilise frames
            self.frames = {}
            self.frames[0] = Account(container, GetAPIKey.get_from_account)
            self.frames[1] = APIKey(container, GetAPIKey.get_from_input)

            self.change_frame()
            
        # Change input frame based on selected login methods
        def change_frame(self):
            frame = self.frames[self.selected_value.get()]
            frame.reset()
            frame.tkraise()

    # Try GUI, otherwise CLI
    try:
        Auth = App()
        ControlFrame(Auth)
        Auth.mainloop()
        API_KEY = Auth.getvar(name='API_KEY')
        CleanWidget(Auth)
        Auth.destroy()
        Auth = None
        gc.collect()
    
    except tk._tkinter.TclError:
        print('Couldn\'t find Planet API Key.')
        login_method = PromptUserSingleSelect(['email', 'API Key'],
                                                'Please select the method you want to proceed.')
        if login_method == 'email':
            while True:
                email = input('Your planet account: ')
                pwd = getpass.getpass('Your password: ')
                try:
                    API_KEY = GetAPIKey.get_from_account(email, pwd)
                    break
                except api.exceptions.InvalidIdentity:
                    print('Authentication failed: Invalid email or password.')
                except api.exceptions.APIException:
                    print('Input error: Invalid parameters.')

        else:
            API_KEY = GetAPIKey.get_from_input(input('Please input your Planet API Key: '))
            while True:
                try:
                    api.ClientV1(API_KEY).get_searches()
                    break
                except api.exceptions.InvalidAPIKey:
                    print('Authentication failed!: Invalid API Key')
                except requests.exceptions.InvalidHeader:
                    print('Authentication failed!: Invalid return character')
    return API_KEY

def RangeInputBox(_property, Input_Min, Input_Max):
    class popupWindow(tk.Tk):
        def __init__(self, _property, Input_Min, Input_Max):
            tk.Tk.__init__(self)
            self.resizable(width=False, height=False)
            self.title(_property)
            self.protocol('WM_DELETE_WINDOW', self.on_exit)
                             
            self.l = ttk.Label(self, text='Please enter the desired {} ({}-{})'.format(
                              _property, Input_Min, Input_Max))
            self.l.grid(column=0, row=0, padx=5, pady=5)

            # Label of minimum range
            self.minLabel = ttk.Label(self, text='Minimum {} (must greater than or equal to {})'.format(_property, Input_Min))
            self.minLabel.grid(column=0, row=1, padx=5, pady=5)

            # Entry for minimum input
            self.min = ttk.Entry(self, width=30)
            self.min.insert('end', Input_Min)
            self.min.bind('<Return>', self.jump_to_max)
            self.min.bind('<KP_Enter>', self.jump_to_max)
            self.min.bind('<Tab>', self.jump_to_max)
            self.min.grid(column=0, row=2, padx=5, pady=5)

            # Label of maximum range
            self.maxLabel = ttk.Label(self, text='Maximum {} (must less than or equal to {})'.format(_property, Input_Max))
            self.maxLabel.grid(column=0, row=3, padx=5, pady=5)

            # Entry for maximum input
            self.max = ttk.Entry(self, width=30)
            self.max.insert('end', Input_Max)
            self.max.bind('<Return>', self.get_value)
            self.max.bind('<KP_Enter>', self.get_value)
            self.max.grid(column=0, row=4, padx=5, pady=5)

            # Ok Button
            self.b = ttk.Button(self,text='Ok', width=40)
            self.b.bind('<Button-1>', self.get_value)
            self.b.grid(column=0, row=5, padx=5, pady=5)
            
            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = int(w/2 - size[0]/2)
            y = int(h/2 - size[1]/2)
            self.geometry('+{}+{}'.format(x, y))
            
            # Apply system scaling factor
            dpi = self.winfo_fpixels('1i')
            scaling = dpi/72
            self.tk.call('tk', 'scaling', scaling)
            ScaledFont = Font()
            ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
            Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TEntry', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        
        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)

        def jump_to_max(self, event):
            self.max.focus()
        
        def get_value(self, event):
            try:
                # Test if they are numbers
                Min = float(self.min.get())
                Max = float(self.max.get())

                # Only allow non-empty inputs and the max must be grater than min
                if Min >= Input_Min and Max <= Input_Max and (Max - Min) >= 0:
                    self.minrange = Min
                    self.maxrange = Max
                    self.quit()
                elif (Max - Min) < 0:
                    showerror('Error!', 
                              'Make sure the maximum is larger than minimum!')
                    self.reset()
                else:
                    showerror('Error!', 
                              'Make sure the input are in range between {} and {}!'.format(
                               Input_Min, Input_Max))
                    self.reset()
                    
            except ValueError:
                showerror('Error!', 'You must input numbers')
                self.reset()

        def reset(self):
            self.min.delete(0, 'end')
            self.min.insert('end', Input_Min)
            self.max.delete(0, 'end')
            self.max.insert('end', Input_Max)

    # Try GUI, otherwise CLI
    try:
        InputBox = popupWindow(_property, Input_Min, Input_Max)
        InputBox.mainloop()
        Min = InputBox.minrange
        Max = InputBox.maxrange
        CleanWidget(InputBox)
        InputBox.destroy()
        InputBox = None
        gc.collect()

    except tk._tkinter.TclError:
        print('Please enter the desired {} ({}-{})'.format(_property, Input_Min, Input_Max))
        while True:
            try:
                # Test if they are numbers
                Min = float(input('Minimum {} (must greater than or equal to {}): '.format(_property, Input_Min)))
                Max = float(input('Maximum {} (must less than or equal to {}): '.format(_property, Input_Max)))

                # Only allow non-empty inputs and the max must be grater than min
                if Min >= Input_Min and Max <= Input_Max and (Max - Min) >= 0:
                    print()
                    break
                elif (Max - Min) < 0:
                    print('Error!: Make sure the maximum is larger than minimum!\n')
                else:
                    print('Error!: Make sure the input are in range between {} and {}!\n'.format(Input_Min, Input_Max))
                
            except ValueError:
                print('Error!: You must input numbers\n')

    return Min, Max

def DateInputBox():        
    class popupWindow(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)
            self.resizable(width=False, height=False)
            self.title('Date')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)

            # Title label
            self.l = ttk.Label(self, text='Please enter the desired Date')
            self.l.grid(column=0, row=0, padx=5, pady=5)

            # Label of start date
            self.SLabel = ttk.Label(self, text='Start from (yyyy-mm-dd)')
            self.SLabel.grid(column=0, row=1, padx=5, pady=5)

            # Entry for start date
            self.SDate = ttk.Entry(self, width=30)
            self.SDate.bind('<Return>', self.jump_to_end)
            self.SDate.bind('<KP_Enter>', self.jump_to_end)
            self.SDate.bind('<Tab>', self.jump_to_end)
            self.SDate.grid(column=0, row=2, padx=5, pady=5)

            # Label of end date
            self.ELabel = ttk.Label(self, text='End on (yyyy-mm-dd)')
            self.ELabel.grid(column=0, row=3, padx=5, pady=5)

            # Entry for end date
            self.EDate = ttk.Entry(self, width=30)
            self.EDate.bind('<Return>', self.get_value)
            self.EDate.bind('<KP_Enter>', self.get_value)
            self.EDate.grid(column=0, row=4, padx=5, pady=5)

            # Ok Button
            self.b = ttk.Button(self,text='Ok', width=40)
            self.b.bind('<Button-1>', self.get_value)
            self.b.grid(column=0, row=5, padx=5, pady=5)

            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = int(w/2 - size[0]/2)
            y = int(h/2 - size[1]/2)
            self.geometry('+{}+{}'.format(x, y))
            
            # Apply system scaling factor
            dpi = self.winfo_fpixels('1i')
            scaling = dpi/72
            self.tk.call('tk', 'scaling', scaling)
            ScaledFont = Font()
            ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
            Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TEntry', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        
        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)

        def jump_to_end(self, event):
            self.EDate.focus()
        
        def get_value(self, event):
            try:
                SYear, SMonth, SDay = self.SDate.get().split('-')
                self.start = datetime(year=int(SYear), month=int(SMonth), day=int(SDay))
                
                EYear, EMonth, EDay = self.EDate.get().split('-')
                self.end = datetime(year=int(EYear), month=int(EMonth), day=int(EDay))

                # Check if end date is later than start date
                time_diff = self.end - self.start
                if time_diff > timedelta(0):
                    # Convert datetime to ISO format
                    self.start = self.start.isoformat()
                    self.end = self.end.isoformat()
                    self.quit()
                else:
                    showerror('Error!', 'The end date must be later than the start date.')
                    self.reset()
                    
            except ValueError:
                showerror('Wrong value!', 'Make sure the input are valid dates and follow the format yyyy-mm-dd')
                self.reset()

        def reset(self):
            self.SDate.delete(0, 'end')
            self.EDate.delete(0, 'end')
               
    # Try GUI, otherwise CLI
    try:
        InputDate = popupWindow()
        InputDate.mainloop()
        StartDate = InputDate.start
        EndDate = InputDate.end
        CleanWidget(InputDate)
        InputDate.destroy()
        InputDate = None
        gc.collect()
    
    except tk._tkinter.TclError:
        print('Please enter the desired date')
        while True:
            try:
                # Start date
                SYear, SMonth, SDay = input('Start from (yyyy-mm-dd): ').split('-')
                StartDate = datetime(year=int(SYear), month=int(SMonth), day=int(SDay))

                # End date
                EYear, EMonth, EDay = input('End on (yyyy-mm-dd): ').split('-')
                EndDate = datetime(year=int(EYear), month=int(EMonth), day=int(EDay))

                # Check if end date is later than start date
                time_diff = EndDate - StartDate
                if time_diff > timedelta(0):
                    # Convert datetime to ISO format
                    StartDate = StartDate.isoformat()
                    EndDate = EndDate.isoformat()
                    print()
                    break
                else:
                    print('Error!: The end date must be later than the start date.')

            except ValueError:
                print('Wrong value!: Make sure the input are valid dates and follow the format yyyy-mm-dd')

    return StartDate, EndDate

def CheckBox(picks, text, *URL, additional_info=False, allow_none=False):
    class checkboxfromlist(ttk.Frame):
        def __init__(self, parent, picks):
            ttk.Frame.__init__(self, parent)
            self.vars = []
            max_width = len(max(picks, key=len))
            total_pick = len(picks)
            # Change row every three columns
            total_row = total_pick // 3 + (total_pick % 3 > 0)

            # Map the checkboxes
            for _row, _column in [(_row, _column) for _row in range(total_row) for _column in range(3)]:
                if _row * 3 + _column < total_pick:
                    var = tk.BooleanVar()
                    chk = ttk.Checkbutton(self, text='{:<{width}}'.format(picks[_row*3+_column], width=max_width),
                                          variable=var, onvalue=True, offvalue=False)
                    chk.grid(column=_column, row=_row, padx=5, pady=5, sticky='ew')
                    self.vars.append(var)
        
        def state(self):
            return list(map((lambda var: var.get()), self.vars))

    class MainWindow(tk.Tk):
        def __init__(self, picks, text, *URL, additional_info=False, allow_none=False):
            tk.Tk.__init__(self)
            self.resizable(width=False, height=False)
            self.title('Please select below options')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)

            # Label
            self.l = ttk.Label(self, text=text)
            self.l.grid(column=0, row=0, padx=5, pady=10)

            current_row = 1
            # Show additional information
            if additional_info:
                self.info = ttk.Label(self, text='For more information, visit the below website')
                self.info.grid(column=0, row=1, padx=5, sticky='ew')
                self.url_link = ttk.Label(self, text='{}'.format(*URL), foreground='blue', cursor='hand2')
                self.url_link.bind('<Button-1>', lambda e: webbrowser.open_new(*URL))
                self.url_link.grid(column=0, row=2, padx=5, sticky='ew')
                current_row += 2

            # Checkboxes frame
            self.ChkBox = checkboxfromlist(self, picks)
            self.ChkBox.grid(column=0, row=current_row, padx=5, pady=10)
            current_row += 1

            # Ok button
            self.Button = ttk.Button(self, text='Ok', width=40, command=self.get_value)
            self.Button.grid(column=0, row=current_row, padx=5, pady=5)
            
            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = int(w/2 - size[0]/2)
            y = int(h/2 - size[1]/2)
            self.geometry('+{}+{}'.format(x, y))
            
            # Apply system scaling factor
            dpi = self.winfo_fpixels('1i')
            scaling = dpi/72
            self.tk.call('tk', 'scaling', scaling)
            ScaledFont = Font()
            ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
            Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TCheckbutton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))

            # Initialise
            self.mask = None
            self.result = None
            
        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)

        def get_value(self):
            self.mask = self.ChkBox.state()
            if any(self.mask) or allow_none:
                selected = [item for index, item in enumerate(picks) if self.mask[index]]
                self.result = selected
                self.quit()
            else:
                InfoBox('No selection', 'Need to select at least one item.')

    # Try GUI, otherwise CLI
    try:
        App = MainWindow(picks, text, *URL, additional_info=additional_info, allow_none=allow_none)
        App.mainloop()
        result = App.result
        CleanWidget(App)
        App.destroy()
        App = None
        gc.collect()
    
    except tk._tkinter.TclError:
        result = PromptUserMultipleSelect(picks, text, *URL, additional_info=additional_info, allow_none=allow_none)

    return result

def ProgressBar(mode, task_thread, _max, Abort_command):
    # GUI progress bar
    class GUIApp(tk.Tk):
        def __init__(self, mode, task_thread, _max, Abort_command):
            super().__init__()
            self.resizable(width=False, height=False)
            self.title('Progress')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)

            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = int(w/2 - size[0]/2)
            y = int(h/2 - size[1]/2)
            self.geometry('+{}+{}'.format(x, y))
            
            # Apply system scaling factor
            dpi = self.winfo_fpixels('1i')
            scaling = dpi/72
            self.tk.call('tk', 'scaling', scaling)
            ScaledFont = Font()
            ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
            Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))

            # Progress label
            self.Label = ttk.Label(self, text=task_thread.message)
            self.Label.grid(column=0, row=0, padx=10, pady=10, sticky='ew')

            # Progress bar
            if mode == 'determinate':
                self.pb = ttk.Progressbar(self, orient='horizontal', mode='determinate', maximum=_max, length=400*scaling)
            elif mode == 'indeterminate':
                self.pb = ttk.Progressbar(self, orient='horizontal', mode='indeterminate', length=400*scaling)
            self.pb.grid(column=0, row=1, padx=10, pady=10)

            # Cancel button
            self.but_cancel = ttk.Button(self, text='Cancel', command=self.on_exit)
            self.but_cancel.grid(column=0, row=2, padx=10, pady=10)

            # Start the task automatically when the program starts
            if not task_thread.is_alive():
                task_thread.start()
            if mode == 'indeterminate':
                self.pb.start()

            # Monitor the progress
            self.monitor(task_thread)
            while not task_thread.result.empty():
                self.result = task_thread.result.get()

        def on_exit(self):
            # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                Abort_command()
                self.destroy()
                task_thread.join()
                sys.exit(0)

        # Monitor the progress
        def monitor(self, task_thread):
            if task_thread.is_alive():
                # Update progress every 0.5 second
                # We get the variable from working thread with Queue method
                self.after(500, lambda: self.monitor(task_thread))
                if mode == 'determinate':
                    while not task_thread.progress.empty():
                        self.pb['value'] = task_thread.progress.get()
                while not task_thread.message.empty():
                    self.Label['text'] = task_thread.message.get()
            else:
                task_thread.join()
                self.pb.stop()
                while not task_thread.result.empty():
                    self.result = task_thread.result.get()
                self.quit()

    # CLI progress bar
    class CLIApp(Thread):
        def __init__(self, mode, task_thread, _max, Abort_command, daemon=True):
            super().__init__()

            # Initialise parameters
            self.max_message_length = task_thread.max_message_length
            self.terminal_size = os.get_terminal_size().columns
            self.length = self.terminal_size - self.max_message_length - 10
            self.progress = task_thread.progress.get()
            self.message = task_thread.message.get()
            self.print_message = ''
            self.result = task_thread.result.get()

        def run(self):
            try:
                # Start the task
                if not task_thread.is_alive():
                    task_thread.start()
                counter = 1
                while task_thread.is_alive():
                    self.monitor(task_thread)
                    if mode == 'determinate':
                        self.PrintProgress(_max)
                    elif mode == 'indeterminate':
                        print('{:<{width}}'.format('{}{}'.format(self.message, '.'*counter), width=self.terminal_size), end='\r')
                        counter += 1
                        if counter > 6:
                            counter = 1
                    # Update progress every 0.5 second
                    sleep(0.5)
                    
                # Update the variable from stopped task thread
                self.monitor(task_thread)
                task_thread.join()

                # Print the final progress
                if mode == 'determinate':
                    print('{:<{width}}'.format(self.print_message, width=self.terminal_size))
                elif mode == 'indeterminate':
                    print('{:<{width}}'.format('Done', width=self.terminal_size))
                while not task_thread.result.empty():
                    self.result = task_thread.result.get()
            except KeyboardInterrupt:
                print('Abort! Exit the program.')
                Abort_command()
                task_thread.join()
                sys.exit(0)
            
        def monitor(self, task_thread):
            while not task_thread.progress.empty():
                self.progress = task_thread.progress.get()
            while not task_thread.message.empty():
                self.message = task_thread.message.get()

        def PrintProgress(self, _max):
            percent = '{0:>4.0%}'.format(float(self.progress/_max))
            BarLength = int(self.length * self.progress / _max)
            Bar = ''.join(['#'*BarLength, '-'*(self.length - BarLength)])
            self.print_message = '{message} [{Bar}] {percent}'.format(message=self.message, Bar=Bar, percent=percent)
            print('{:<{width}}'.format(self.print_message, width=self.terminal_size), end='\r')
        
    # Try GUI, otherwise CLI
    try:
        ProgressBar = GUIApp(mode, task_thread, _max, Abort_command)
        ProgressBar.mainloop()
        result = ProgressBar.result
        CleanWidget(ProgressBar)
        ProgressBar.destroy()
        
    except tk._tkinter.TclError:
        ProgressBar = CLIApp(mode, task_thread, _max, Abort_command)
        ProgressBar.start()
        ProgressBar.join()
        result = ProgressBar.result
        
    ProgressBar = None
    gc.collect()

    return result

def DeliveryBox():
    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            self.resizable(width=False, height=False)
            self.title('Delivery method')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)

            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = int(w/2 - size[0]/2)
            y = int(h/2 - size[1]/2)
            self.geometry('+{}+{}'.format(x, y))
            
            # Apply system scaling factor
            dpi = self.winfo_fpixels('1i')
            scaling = dpi/72
            self.tk.call('tk', 'scaling', scaling)
            ScaledFont = Font()
            ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
            Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TEntry', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
            Style().configure('TCheckbutton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))

            # Set the variables
            self.delivery_option = tk.StringVar(self, name='delivery_option')
            self.destination = tk.StringVar(self, name='destination')
            self.destination_valid = tk.IntVar(self, name='destination_valid')
            self.single_archive_selected = tk.IntVar(self, name='single_archive_selected')
            self.single_archive = tk.StringVar(self, name='single_archive')
            self.single_archive.set('{}')
            self.overwrite = tk.IntVar(self, name='overwrite')
            self.overwrite.set(0)
            
            self.amz_s3 = tk.IntVar(self, name='amz_s3')
            self.amz_s3_keyid = tk.StringVar(self, name='amz_s3_keyid')
            self.amz_s3_key = tk.StringVar(self, name='amz_s3_key')
            self.amz_s3_bucket = tk.StringVar(self, name='amz_s3_bucket')
            self.amz_s3_region = tk.StringVar(self, name='amz_s3_region')
            self.amz_s3_prefix = tk.StringVar(self, name='amz_s3_prefix')

            self.ms_az = tk.IntVar(self, name='ms_az')
            self.ms_az_account = tk.StringVar(self, name='ms_az_account')
            self.ms_az_container = tk.StringVar(self, name='ms_az_container')
            self.ms_az_token = tk.StringVar(self, name='ms_az_token')
            self.ms_az_suffix = tk.StringVar(self, name='ms_az_suffix')
            self.ms_az_prefix = tk.StringVar(self, name='ms_az_prefix')

            self.goo_cs = tk.IntVar(self, name='goo_cs')
            self.goo_cs_credentials = tk.StringVar(self, name='goo_cs_credentials')
            self.goo_cs_bucket = tk.StringVar(self, name='goo_cs_bucket')
            self.goo_cs_prefix = tk.StringVar(self, name='goo_cs_prefix')

            self.delivery_method = tk.IntVar(self, name='delivery_method')

            # Frame for location drive download option
            self.Local_frame = ttk.Frame(self)
            self.Local_frame.columnconfigure(0, weight=1)
            self.Local_frame.rowconfigure(0, weight=49)
            self.Local_frame.rowconfigure(1, weight=50)

            # Destination entry
            self.Local_Label = ttk.Label(self.Local_frame, text='Please select the directory to save files')
            self.Local_Label.grid(column=0, row=0, padx=5, pady=5, columnspan=2)
            self.destination_entry = ttk.Entry(self.Local_frame, width=60, textvariable=self.destination)
            self.destination_entry.bind('<Return>', self.get_delivery)
            self.destination_entry.bind('<KP_Enter>', self.get_delivery)
            self.destination_entry.grid(column=0, row=1, padx=10, pady=5, sticky='ew')

            # Ask for directory button
            self.askdirectory_but = ttk.Button(self.Local_frame,text='...', width=5)
            self.askdirectory_but.bind('<Button-1>', self.Ask_Directory)
            self.askdirectory_but.grid(column=1, row=1, padx=5, pady=5)

            # Draw the local frame
            self.Local_frame.grid(column=0, row=0, sticky='nsew')

            # Frame for cloud storage delivery
            self.Cloud_frame = ttk.Frame(self)

            # Label for Cloud storage frame
            self.Cloud_Label = ttk.Label(self.Cloud_frame, text='Please select the cloud storage options')
            self.Cloud_Label.grid(column=0, row=0, padx=5, pady=5, columnspan=3)
            self.info = ttk.Label(self.Cloud_frame, text='For more information, visit the below website')
            self.info.grid(column=0, row=1, padx=5, columnspan=3, sticky='ew')
            self.url_link = ttk.Label(self.Cloud_frame, text='https://developers.planet.com/docs/orders/delivery/',
                                      foreground='blue', cursor='hand2')
            self.url_link.bind('<Button-1>', lambda e: webbrowser.open_new('https://developers.planet.com/docs/orders/delivery/'))
            self.url_link.grid(column=0, row=2, padx=5, columnspan=3, sticky='ew')
            
            # Amazon S3
            self.amz_s3_frame = ttk.Frame(self.Cloud_frame)
            self.amz_s3_chkbox = ttk.Checkbutton(self.amz_s3_frame,
                                                 text='Amazon S3',
                                                 variable=self.amz_s3,
                                                 onvalue=1, offvalue=0,
                                                 command = lambda: self.set_CloudFrame(
                                                     self.getvar(name='amz_s3'), self.amz_s3_option_frame.winfo_children()))
            self.setvar(name='amz_s3', value=0)
            self.amz_s3_chkbox.grid(column=0, row=0, padx=5, pady=5)
            
            self.amz_s3_option_frame = ttk.Frame(self.amz_s3_frame)
            self.amz_s3_keyid_label = ttk.Label(self.amz_s3_option_frame, text='AWS access key ID')
            self.amz_s3_keyid_label.grid(column=0, row=0, padx=5, pady=5)
            self.amz_s3_keyid_entry = ttk.Entry(self.amz_s3_option_frame, textvariable=self.amz_s3_keyid)
            self.amz_s3_keyid_entry.grid(column=0, row=1, padx=5, pady=5)
            self.amz_s3_key_label = ttk.Label(self.amz_s3_option_frame, text='AWS secret access key')
            self.amz_s3_key_label.grid(column=0, row=2, padx=5, pady=5)
            self.amz_s3_key_entry = ttk.Entry(self.amz_s3_option_frame, textvariable=self.amz_s3_key)
            self.amz_s3_key_entry.grid(column=0, row=3, padx=5, pady=5)
            self.amz_s3_bucket_label = ttk.Label(self.amz_s3_option_frame, text='Bucket')
            self.amz_s3_bucket_label.grid(column=0, row=4, padx=5, pady=5)
            self.amz_s3_bucket_entry = ttk.Entry(self.amz_s3_option_frame, textvariable=self.amz_s3_bucket)
            self.amz_s3_bucket_entry.grid(column=0, row=5, padx=5, pady=5)
            self.amz_s3_region_label = ttk.Label(self.amz_s3_option_frame, text='AWS region')
            self.amz_s3_region_label.grid(column=0, row=6, padx=5, pady=5)
            self.amz_s3_region_entry = ttk.Entry(self.amz_s3_option_frame, textvariable=self.amz_s3_region)
            self.amz_s3_region_entry.grid(column=0, row=7, padx=5, pady=5)
            self.amz_s3_prefix_label = ttk.Label(self.amz_s3_option_frame, text='Path prefix (optional)')
            self.amz_s3_prefix_label.grid(column=0, row=8, padx=5, pady=5)
            self.amz_s3_prefix_entry = ttk.Entry(self.amz_s3_option_frame, textvariable=self.amz_s3_prefix)
            self.amz_s3_prefix_entry.grid(column=0, row=9, padx=5, pady=5)
            self.amz_s3_option_frame.grid(column=0, row=1)

            self.amz_s3_frame.grid(column=0, row=3)

            # Microsoft Azure
            self.ms_az_frame = ttk.Frame(self.Cloud_frame)
            self.ms_az_chkbox = ttk.Checkbutton(self.ms_az_frame,
                                                text='Microsoft Azure',
                                                variable=self.ms_az, 
                                                onvalue=1, offvalue=0,
                                                command = lambda: self.set_CloudFrame(
                                                    self.getvar(name='ms_az'), self.ms_az_option_frame.winfo_children()))
            self.setvar(name='ms_az', value=0)
            self.ms_az_chkbox.grid(column=0, row=0, padx=5, pady=5)

            self.ms_az_option_frame = ttk.Frame(self.ms_az_frame)
            self.ms_az_account_label = ttk.Label(self.ms_az_option_frame, text='Azure account')
            self.ms_az_account_label.grid(column=0, row=0, padx=5, pady=5)
            self.ms_az_account_entry = ttk.Entry(self.ms_az_option_frame, textvariable=self.ms_az_account)
            self.ms_az_account_entry.grid(column=0, row=1, padx=5, pady=5)
            self.ms_az_container_label = ttk.Label(self.ms_az_option_frame, text='Azure container')
            self.ms_az_container_label.grid(column=0, row=2, padx=5, pady=5)
            self.ms_az_container_entry = ttk.Entry(self.ms_az_option_frame, textvariable=self.ms_az_container)
            self.ms_az_container_entry.grid(column=0, row=3, padx=5, pady=5)
            self.ms_az_token_label = ttk.Label(self.ms_az_option_frame, text='Azure SAS token')
            self.ms_az_token_label.grid(column=0, row=4, padx=5, pady=5)
            self.ms_az_token_entry = ttk.Entry(self.ms_az_option_frame, textvariable=self.ms_az_token)
            self.ms_az_token_entry.grid(column=0, row=5, padx=5, pady=5)
            self.ms_az_suffix_label = ttk.Label(self.ms_az_option_frame, text='Storage endpoint suffix (optional)')
            self.ms_az_suffix_label.grid(column=0, row=6, padx=5, pady=5)
            self.ms_az_suffix_entry = ttk.Entry(self.ms_az_option_frame, textvariable=self.ms_az_suffix)
            self.ms_az_suffix_entry.grid(column=0, row=7, padx=5, pady=5)
            self.ms_az_prefix_label = ttk.Label(self.ms_az_option_frame, text='Path prefix (optional)')
            self.ms_az_prefix_label.grid(column=0, row=8, padx=5, pady=5)
            self.ms_az_prefix_entry = ttk.Entry(self.ms_az_option_frame, textvariable=self.ms_az_prefix)
            self.ms_az_prefix_entry.grid(column=0, row=9, padx=5, pady=5)
            self.ms_az_option_frame.grid(column=0, row=1)

            self.ms_az_frame.grid(column=1, row=3)

            # Google Cloud Storage
            self.goo_cs_frame = ttk.Frame(self.Cloud_frame)
            self.goo_cs_chkbox = ttk.Checkbutton(self.goo_cs_frame,
                                                 text='Google Cloud Storage',
                                                 variable=self.goo_cs, 
                                                 onvalue=1, offvalue=0,
                                                 command = lambda: self.set_CloudFrame(
                                                     self.getvar(name='goo_cs'), self.goo_cs_option_frame.winfo_children()))
            self.setvar(name='goo_cs', value=0)
            self.goo_cs_chkbox.grid(column=0, row=0, padx=5, pady=5)

            self.goo_cs_option_frame = ttk.Frame(self.goo_cs_frame)
            self.goo_cs_credentials_label = ttk.Label(self.goo_cs_option_frame, text='GCS credentials')
            self.goo_cs_credentials_label.grid(column=0, row=0, padx=5, pady=5)
            self.goo_cs_credentials_entry = ttk.Entry(self.goo_cs_option_frame, textvariable=self.goo_cs_credentials)
            self.goo_cs_credentials_entry.grid(column=0, row=1, padx=5, pady=5)
            self.goo_cs_bucket_label = ttk.Label(self.goo_cs_option_frame, text='GCS bucket')
            self.goo_cs_bucket_label.grid(column=0, row=2, padx=5, pady=5)
            self.goo_cs_bucket_entry = ttk.Entry(self.goo_cs_option_frame, textvariable=self.goo_cs_bucket)
            self.goo_cs_bucket_entry.grid(column=0, row=3, padx=5, pady=5)
            self.goo_cs_prefix_label = ttk.Label(self.goo_cs_option_frame, text='Path prefix (optional)')
            self.goo_cs_prefix_label.grid(column=0, row=4, padx=5, pady=5)
            self.goo_cs_prefix_entry = ttk.Entry(self.goo_cs_option_frame, textvariable=self.goo_cs_prefix)
            self.goo_cs_prefix_entry.grid(column=0, row=5, padx=5, pady=5)
            ttk.Label(self.goo_cs_option_frame, text = '').grid(column=0, row=6, padx=5, pady=5)
            ttk.Label(self.goo_cs_option_frame, text = '').grid(column=0, row=7, padx=5, pady=5)
            ttk.Label(self.goo_cs_option_frame, text = '').grid(column=0, row=8, padx=5, pady=5)
            ttk.Label(self.goo_cs_option_frame, text = '').grid(column=0, row=9, padx=5, pady=5)
            self.goo_cs_option_frame.grid(column=0, row=1)

            self.goo_cs_frame.grid(column=2, row=3)

            # Draw the cloud frame
            self.Cloud_frame.grid(column=0, row=0, padx=5, sticky='nsew')

            # Disable all widget at the begining
            self.set_CloudFrame(self.amz_s3.get(), self.amz_s3_option_frame.winfo_children())
            self.set_CloudFrame(self.ms_az.get(), self.ms_az_option_frame.winfo_children())
            self.set_CloudFrame(self.goo_cs.get(), self.goo_cs_option_frame.winfo_children())

            # Set the control frame
            self.delivery_method_frame = ttk.LabelFrame(self, text='Delivery methods')
            ttk.Radiobutton(
                self.delivery_method_frame,
                text='{:<23}'.format('Local drive'),
                value=0,
                variable=self.delivery_method,
                command=self.change_frame).grid(column=0, row=0, padx=50, pady=5)
            ttk.Radiobutton(
                self.delivery_method_frame,
                text='{:<23}'.format('Cloud storage'),
                value=1,
                variable=self.delivery_method,
                command=self.change_frame).grid(column=1, row=0, padx=50, pady=5)

            self.delivery_method_frame.grid(column=0, row=1, padx=5, pady=5, sticky='ew')

            # Other option frame
            self.other_frame = ttk.Frame(self)

            # Single archive option
            self.single_archive_chkbox = ttk.Checkbutton(self.other_frame,
                                                         text='Deliver in a single archive',
                                                         variable=self.single_archive_selected,
                                                         onvalue=1, offvalue=0,
                                                         command=self.set_single_archive)
            self.single_archive_chkbox.grid(column=0, row=0, padx=50, pady=5)

            # Overwrite option
            self.overwrite_chkbox = ttk.Checkbutton(self.other_frame,
                                                    text='Overwrite existing files',
                                                    variable=self.overwrite,
                                                    onvalue=1, offvalue=0)
            self.overwrite_chkbox.grid(column=1, row=0, padx=50, pady=5)

            self.other_frame.grid(column=0, row=2, sticky='ew')

            # OK button
            self.OK_button = ttk.Button(self, text='OK')
            self.OK_button.bind('<Button-1>', self.get_delivery)
            self.OK_button.grid(column=0, row=3, padx=5, pady=5)

            # Initilise frames
            self.frames = {}
            self.frames[0] = self.Local_frame
            self.frames[1] = self.Cloud_frame

            self.change_frame()
            
        # Change input frame based on selected login methods
        def change_frame(self):
            frame = self.frames[self.delivery_method.get()]
            self.destination.set('')
            self.amz_s3.set(0)
            self.ms_az.set(0)
            self.goo_cs.set(0)
            frame.tkraise()

        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)

        # Prompt for choosing directory
        def Ask_Directory(self, event):
            directory = askdirectory(title='Please select the directory to save files')
            self.destination_entry.delete(0, 'end')
            self.destination_entry.insert('end', directory)

        def set_CloudFrame(self, chkbox_value, childlist):
            if chkbox_value == True:
                for child in childlist:
                    child.configure(state='normal')
            else:
                for child in childlist:
                    child.configure(state='disable')

        def set_single_archive(self):
            if self.single_archive_selected.get() == True:
                self.single_archive.set(json.dumps({'archive_type': 'zip',
                                                    'single_archive': True,
                                                    'archive_filename':'{{name}}_{{order_id}}.zip'}))
            else:
                self.single_archive.set('{}')

        def get_delivery(self, event):
            destination = ''
            delivery = json.loads(self.single_archive.get())
            if self.delivery_method.get() == 0:
                self.valid_directory()
                if self.destination_valid.get() == True:    
                    self.delivery_option.set(json.dumps(delivery))
                    self.quit()
            else:
                # Raise error if some required information is missing
                try:
                    # Need to select at least one storage
                    if not any([self.amz_s3.get(), self.ms_az.get(), self.goo_cs.get()]):
                        showerror('No selection', 'Need to select at least one item.')
                    else:
                        
                        # Get Amazon S3 information
                        if self.amz_s3.get() == True:
                            keyid = self.amz_s3_keyid.get()
                            key = self.amz_s3_key.get()
                            bucket = self.amz_s3_bucket.get()
                            region = self.amz_s3_region.get()
                            if len(keyid) > 0 and len(key) > 0 and len(bucket) > 0 and len(region) > 0:
                                delivery['amazon_s3'] = {'aws_access_key_id': keyid,
                                                         'aws_secret_access_key': key,
                                                         'bucket': bucket,
                                                         'aws_region': region}
                                if len(self.amz_s3_prefix.get()) > 0:
                                    delivery['amazon_s3']['path_prefix'] = self.amz_s3_prefix.get()
                            else:
                                raise ValueError

                        # Get Microsoft Azure information
                        if self.ms_az.get() == True:
                            account = self.ms_az_account.get()
                            container = self.ms_az_container.get()
                            token = self.ms_az_token.get()
                            if len(account) > 0 and len(container) > 0 and len(token) > 0:
                                delivery['azure_blob_storage'] = {'account': account,
                                                                  'container': container,
                                                                  'sas_token': token}
                                if len(self.ms_az_suffix.get()) > 0:
                                    delivery['azure_blob_storage']['storage_endpoint_suffix'] = self.ms_az_suffix.get()
                                if len(self.ms_az_prefix.get()) > 0:
                                    delivery['azure_blob_storage']['path_prefix'] = self.ms_az_prefix.get()

                            else:
                                raise ValueError

                        # Get Google Cloud Storage information
                        if self.goo_cs.get() == True:
                            credentials = self.goo_cs_credentials.get()
                            bucket = self.goo_cs_bucket.get()
                            if len(credentials) > 0 and len(bucket) > 0:
                                delivery['google_cloud_storage'] = {'credentials': credentials,
                                                                    'bucket': bucket}
                                if len(self.goo_cs_prefix.get()) > 0:
                                    delivery['google_cloud_storage']['path_prefix'] = self.goo_cs_prefix.get()
                            else:
                                raise ValueError

                        # Save the final delivery information
                        self.delivery_option.set(json.dumps(delivery))
                        self.quit()

                except ValueError:
                    showerror('Missing information', 'Make sure to input all required information.')

        # Get the destination
        def valid_directory(self):
            output_dir = self.destination.get()
            if len(output_dir) == 0:
                showerror('Warning!', 'destination cannot be blank!')
            else:
                if not os.path.exists(output_dir):
                    try:
                        os.mkdir(output_dir)
                        self.destination_valid.set(1)
                    except PermissionError:
                        showerror('Permission issue', 'Please select another accessible directory')
                        self.destination_entry.delete(0, 'end')
                        self.destination_valid.set(0)
                else:
                    # Check if the directory is writable
                    if not os.access(output_dir, os.X_OK | os.W_OK):
                        showerror('Permission issue', 'Please select another accessible directory')
                        self.destination_entry.delete(0, 'end')
                        self.destination_valid.set(0)
                    else:
                        self.destination_valid.set(1)

    # Try GUI, otherwise CLI
    try:
        Delivery = App()
        Delivery.mainloop()
        destination = Delivery.getvar(name='destination')
        delivery_option = json.loads(Delivery.getvar(name='delivery_option'))
        overwrite = bool(Delivery.getvar(name='overwrite'))
        CleanWidget(Delivery)
        Delivery.destroy()
        Delivery = None
        gc.collect()
    
    except tk._tkinter.TclError:
        cloud_options = {'Amazon S3': [{'aws_access_key_id': 'AWS access key ID: '},
                                       {'aws_secret_access_key': 'AWS secret access key: '},
                                       {'bucket': 'Bucket: '},
                                       {'aws_region': 'AWS region: '},
                                       {'path_prefix': 'Path prefix (optional, press return to skip): '}],
                         'Microsoft Azure': [{'account': 'Azure account: '},
                                             {'container': 'Azure container: '},
                                             {'sas_token': 'Azure SAS token: '},
                                             {'storage_endpoint_suffix': 'Storage endpoint suffix (optional, press return to skip): '},
                                             {'path_prefix': 'Path prefix (optional, press return to skip): '}],
                         'Google Cloud Storage': [{'credentials': 'GCS credentials: '},
                                                  {'bucket': 'GCS bucket: '},
                                                  {'path_prefix': 'Path prefix (optional, press return to skip): '}]}

        delivery_method = PromptUserSingleSelect(['Local drive', 'Cloud storage'],
                                                  'Please select a delivery method')

        delivery_option = dict()
        destination = ''
        if delivery_method == 'Local drive':
            while len(destination) == 0:
                destination = input('Please select the directory to save files: ')
                if len(destination) == 0:
                    print('Warning: destination cannot be blank!')
                else:
                    if not os.path.exists(destination):
                        try:
                            os.mkdir(destination)
                        
                        except PermissionError:
                            print('Permission issue: Please select another accessible directory\n')
                            destination = ''
                            
                    else:
                        # Check if the directory is writable
                        if not os.access(destination, os.X_OK | os.W_OK):
                            print('Permission issue: Please select another accessible directory\n')
                            destination = ''
            # Get the full path
            destination = os.path.realpath(destination)

        else:
            selected_cloud = PromptUserMultipleSelect(list(cloud_options.keys()),
                                                      'Please select at least one cloud delivery method',
                                                      'https://developers.planet.com/docs/orders/delivery/',
                                                      additional_info=True)

            for cloud in selected_cloud:
                if cloud == 'Amazon S3':
                    cloud_name = 'amazon_s3'
                    required_field = 4
                if cloud == 'Microsoft Azure':
                    cloud_name = 'azure_blob_storage'
                    required_field = 3
                if cloud == 'Google Cloud Storage':
                    cloud_name = 'google_cloud_storage'
                    required_field = 2
                    
                total_field = len(cloud_options[cloud])
                for i in range(required_field):
                    while True:
                        code = list(cloud_options[cloud][i].keys())[0]
                        message = list(cloud_options[cloud][i].values())[0]
                        user_input = input('{}: {}'.format(cloud, message))
                        try:
                            delivery_option[cloud_name][code] = user_input
                        except KeyError:
                            delivery_option[cloud_name] = dict()
                            delivery_option[cloud_name][code] = user_input
                        if delivery_option[cloud_name][code] != '':
                            break
                        else:
                            print('Warning: Input cannot be balnk!')
                for i in range(required_field, total_field):
                    code = list(cloud_options[cloud][i].keys())[0]
                    message = list(cloud_options[cloud][i].values())[0]
                    _setting = input('{}: {}'.format(cloud, message))
                    if len(_setting) > 0:
                        delivery_option[cloud_name][code] = _setting

        print('Do you want to pack the order into single archive file?')
        correct_answers = ['yes', 'y', 'no', 'n']
        while True:
            user_answer = input('(yes/no)? >>> ')
            if user_answer.lower() in correct_answers:
                break
            print('Can\'t recognise input. Please try again.')

        if user_answer.lower() == 'yes' or user_answer == 'y':
            delivery_option['archive_type'] = 'zip'
            delivery_option['single_archive'] = True
            delivery_option['archive_filename'] = '{{name}}_{{order_id}}.zip'

        print('Do you want to overwrite existing file?')
        correct_answers = ['yes', 'y', 'no', 'n']
        while True:
            user_answer = input('(yes/no)? >>> ')
            if user_answer.lower() in correct_answers:
                break
            print('Can\'t recognise input. Please try again.')

        if user_answer.lower() == 'yes' or user_answer == 'y':
            overwrite = True
        else:
            overwrite = False
                
    return destination, delivery_option, overwrite
    
def User_Confirm(title, question):
    try:
        root = tk.Tk()
        
        # Apply system scaling factor
        dpi = root.winfo_fpixels('1i')
        scaling = dpi/72
        root.tk.call('tk', 'scaling', scaling)
        ScaledFont = Font()
        ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
        Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        
        root.withdraw()
        answer = askquestion(title, question)
        root.destroy()
    except tk._tkinter.TclError:
        print('{}: {}'.format(title, question))
        correct_answers = ['yes', 'y', 'no', 'n']
        while True:
            answer = input('(yes/no)? >>> ')
            if answer.lower() in correct_answers:
                break
            print('Can\'t recognise input. Please try again.')
    return answer

def InfoBox(title, info):
    try:
        root = tk.Tk()
        
        # Apply system scaling factor
        dpi = root.winfo_fpixels('1i')
        scaling = dpi/72
        root.tk.call('tk', 'scaling', scaling)
        ScaledFont = Font()
        ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
        Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        
        root.withdraw()
        showinfo(title, info)
        root.destroy()
    except tk._tkinter.TclError:
        print('{}: {}'.format(title, info))
    
def ErrorBox(title, error):
    try:
        root = tk.Tk()
        
        # Apply system scaling factor
        dpi = root.winfo_fpixels('1i')
        scaling = dpi/72
        root.tk.call('tk', 'scaling', scaling)
        ScaledFont = Font()
        ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
        Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        
        root.withdraw()
        showerror(title, error)
        root.destroy()
    except tk._tkinter.TclError:
        print('{}: {}'.format(title, error))

def AskOpenFile(title, filetype):
    try:
        root = tk.Tk()
        
        # Apply system scaling factor
        dpi = root.winfo_fpixels('1i')
        scaling = dpi/72
        root.tk.call('tk', 'scaling', scaling)
        ScaledFont = Font()
        ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
        Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        
        root.withdraw()
        filename = askopenfilename(title=title, filetypes=filetype)
        root.destroy()
    except tk._tkinter.TclError:
        while True:
            AOI_filetype = list()
            for item in filetype:
                AOI_filetype[-1:-1] = item[1]
            filename = input('{}: '.format(title))
            ext = os.path.splitext(filename)[1]
            if os.path.isfile(filename) and len([i for i in AOI_filetype if ext.lower() in i]) > 0:
                break
            else:
                print('Invalud input file. Please try again.')

    return filename

def AskDirectory(title):
    try:
        root = tk.Tk()
        
        # Apply system scaling factor
        dpi = root.winfo_fpixels('1i')
        scaling = dpi/72
        root.tk.call('tk', 'scaling', scaling)
        ScaledFont = Font()
        ScaledFont.config(size=int(ScaledFont.actual()['size']*scaling))
        Style().configure('TLabel', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        Style().configure('TButton', font=(ScaledFont.actual()['family'], -ScaledFont.actual()['size']))
        
        root.withdraw()
        directory = askdirectory(title=title)
        root.destroy()
    except tk._tkinter.TclError:
        directory = input('{}: '.format(title))
        
    return directory

def ParseInputNumbers(selects):
    try:
        selected_index = set()
        for select in selects:
            if '-' in select:
                start, end = select.split('-')
                for i in range(int(start), int(end)+1):
                    selected_index.add(i-1)
                        
            else:
                selected_index.add(int(select)-1)
        return selected_index
    except ValueError:
        print('Can\'t recognise input. Please try again!')
        return False

def PromptUserSingleSelect(Items, message, *URL, additional_info=False, allow_none=False):
    # Ask user to select items for download
    print()
    print(message)
    if additional_info:
        print('For more information, visit the below website')
        print(*URL)
        print()
    
    for index, item in enumerate(Items):
        print('*{:>2}: {:<}'.format(index+1, item))
    
    # Check whether input is valid
    while True:
        selects = input('>>> ').split()
        if len(selects) > 1:
            print('Only one selection is allowed!')
            continue
        
        selected_index = ParseInputNumbers(selects)
        if any([_index > len(Items)-1 for _index in selected_index]):
            print('>>> Invalid selection')
            continue
        if selected_index or allow_none:
            break
        else:
            print('>>> No selection: Need to select at least one item.')
        
    selected_item = list()
    for index in selected_index:
        selected_item.append(Items[index])

    return selected_item[0]

def PromptUserMultipleSelect(Items, message, *URL, additional_info=False, allow_none=False):
    # Ask user to select items for download
    print()
    print(message)
    if additional_info:
        print('For more information, visit the below website')
        print(*URL)
        print()

    # Print three items in each row
    counter = 0
    max_width = len(max(Items, key=len)) + 2
    for index, item in enumerate(Items):
        print('*{:>2}: {:<{width}}'.format(index+1, item, width=max_width), end='')
        counter += 1
        if counter == 3:
            print()
            counter = 0
    print('\ne.g.: "1-3" to select 1 to 3; 1 3 to select 1 and 3')
    
    # Check whether input is valid
    while True:
        selects = input('>>> ').split()
        selected_index = ParseInputNumbers(selects)
        if any([_index > len(Items)-1 for _index in selected_index]):
            print('>>> Invalid selection')
            continue
        if selected_index or allow_none:
            break
        else:
            print('>>> No selection: Need to select at least one item.')
        
    selected_items = list()
    for index in selected_index:
        selected_items.append(Items[index])

    return selected_items

