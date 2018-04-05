#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 13:54:30 2018

@author: uqytu1
"""

import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showerror, showinfo, askyesno, askquestion
import sys
import re
from datetime import datetime, timedelta

def KeyInputBox():
    class popupWindow(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)
            self.resizable(width=False, height=False)
            self.title('Please enter your Planet API Key')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)
            self.Label = tk.Label(self, text='Planet API Key:')
            self.Label.pack()
            self.Entry = tk.Entry(self, width=30)
            self.Entry.bind('<Return>', self.cleanup)
            self.Entry.bind('<KP_Enter>', self.cleanup)
            self.Entry.pack()
            self.Ok = tk.Button(self,text='Ok', width=40, height=2)
            self.Ok.bind('<Button-1>', self.cleanup)
            self.Ok.pack()
            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = w/2 - size[0]/2
            y = h/2 - size[1]/2
            self.geometry('%dx%d+%d+%d' % (size + (x, y)))
        
        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)
                
        def cleanup(self, event):
            self.PL_API_Key = self.Entry.get()
            if len(self.PL_API_Key) == 0:
                showerror('Warning!', 'Input cannot be blank!')
            else:
                self.quit()
        
    m = popupWindow()
    m.mainloop()
    m.destroy()
    return m.PL_API_Key

def DateInputBox():        
    class popupWindow(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)
            self.resizable(width=False, height=False)
            self.title('Please enter the desired date')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)
            self.SLabel = tk.Label(self, text='Start from (yyyy-mm-dd)')
            self.SLabel.pack()
            self.SDate = tk.Entry(self, width=30)
            self.SDate.pack()
            self.ELabel = tk.Label(self, text='End on (yyyy-mm-dd)')
            self.ELabel.pack()
            self.EDate = tk.Entry(self, width=30)
            self.EDate.pack()
            self.b = tk.Button(self,text='Ok', width=40, height=2)
            self.b.bind('<Button-1>', self.cleanup)
            self.b.pack()
            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = w/2 - size[0]/2
            y = h/2 - size[1]/2
            self.geometry('%dx%d+%d+%d' % (size + (x, y)))
        
        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)
        
        def cleanup(self, event):
            try:
                SYear, SMonth, SDay = self.SDate.get().split('-')
                self.start = '-'.join([SYear, SMonth.zfill(2), SDay.zfill(2)])
                
                EYear, EMonth, EDay = self.EDate.get().split('-')
                self.end = '-'.join([EYear, EMonth.zfill(2), EDay.zfill(2)])
                
                if re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', self.start) and \
                   re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', self.end):
                       
                    time_diff = datetime.strptime(self.end, '%Y-%m-%d') - datetime.strptime(self.start, '%Y-%m-%d')
                    if time_diff > timedelta(0):
                        self.quit()
                    else:
                        showerror('Error!', 'The end date must be later than the start date.')
                        self.SDate.delete(0, 'end')
                        self.EDate.delete(0, 'end')
                    
            except ValueError:
                showerror('Wrong format!', 'Please follow the format yyyy-mm-dd')
                self.SDate.delete(0, 'end')
                self.EDate.delete(0, 'end')
               
    m = popupWindow()
    m.mainloop()
    m.destroy()
    return m.start, m.end

def CloudCover_inputBox():        
    class popupWindow(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)
            self.resizable(width=False, height=False)
            self.title('Cloud cover')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)
            self.l = tk.Label(self, text='Please enter the desired cloud cover range (0-1)')
            self.l.pack()
            self.minLabel = tk.Label(self, text='Minimum cloud cover')
            self.minLabel.pack()
            self.min = tk.Entry(self, width=30)
            self.min.insert('end', 0)
            self.min.pack()
            self.maxLabel = tk.Label(self, text='Maximum cloud cover')
            self.maxLabel.pack()
            self.max = tk.Entry(self, width=30)
            self.max.insert('end', 1)
            self.max.pack()
            self.b = tk.Button(self,text='Ok', width=40, height=2)
            self.b.bind('<Button-1>', self.cleanup)
            self.b.pack()
            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = w/2 - size[0]/2
            y = h/2 - size[1]/2
            self.geometry('%dx%d+%d+%d' % (size + (x, y)))
        
        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)
        
        def cleanup(self, event):
            Min = self.min.get()
            Max = self.max.get()
            try:
                float(Min)
                float(Max)
                if eval(Min) >= 0 and eval(Max) <=1:
                    self.mincloud = str(float(Min))
                    self.maxcloud = str(float(Max))
                    self.quit()
                else:
                    showerror('Error!', 
                              'Make sure the input are in range between 0 and 1!')
                    self.min.delete(0, 'end')
                    self.min.insert('end', 0)
                    self.max.delete(0, 'end')
                    self.max.insert('end', 1)
            except ValueError:
                showerror('Error!', 'You must input numbers')
                self.min.delete(0, 'end')
                self.min.insert('end', 0)
                self.max.delete(0, 'end')
                self.max.insert('end', 1)
    m = popupWindow()
    m.mainloop()
    m.destroy()
    return m.mincloud, m.maxcloud

def AreaCover_inputBox():        
    class popupWindow(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)
            self.resizable(width=False, height=False)
            self.title('Cloud cover')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)
            self.l = tk.Label(self, text='Please enter the desired area cover percentage (0-100)')
            self.l.pack()
            self.minLabel = tk.Label(self, text='Minimum area cover ercentage')
            self.minLabel.pack()
            self.min = tk.Entry(self, width=30)
            self.min.insert('end', 0)
            self.min.pack()
            self.maxLabel = tk.Label(self, text='Maximum area cover percentage')
            self.maxLabel.pack()
            self.max = tk.Entry(self, width=30)
            self.max.insert('end', 100)
            self.max.pack()
            self.b = tk.Button(self,text='Ok', width=40, height=2)
            self.b.bind('<Button-1>', self.cleanup)
            self.b.pack()
            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = w/2 - size[0]/2
            y = h/2 - size[1]/2
            self.geometry('%dx%d+%d+%d' % (size + (x, y)))
        
        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)
        
        def cleanup(self, event):
            Min = self.min.get()
            Max = self.max.get()
            try:
                float(Min)
                float(Max)
                if eval(Min) >= 0 and eval(Max) <=100:
                    self.mincover = str(float(Min))
                    self.maxcover = str(float(Max))
                    self.quit()
                else:
                    showerror('Error!', 
                              'Make sure the input are in range between 0 and 100!')
                    self.min.delete(0, 'end')
                    self.min.insert('end', 0)
                    self.max.delete(0, 'end')
                    self.max.insert('end', 1)
            except ValueError:
                showerror('Error!', 'You must input numbers')
                self.min.delete(0, 'end')
                self.min.insert('end', 0)
                self.max.delete(0, 'end')
                self.max.insert('end', 1)
    m = popupWindow()
    m.mainloop()
    m.destroy()
    return m.mincover, m.maxcover

def CheckBox(picks, *Args):
    class checkboxfromlist(tk.Frame):
        def __init__(self, parent, picks):
            tk.Frame.__init__(self, parent)
            self.vars = []
            for pick in picks:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(self, text=pick, variable=var, onvalue=True, offvalue=False)
                chk.pack()
                self.vars.append(var)
        
        def state(self):
            return list(map((lambda var: var.get()), self.vars))

    class MainWindow(tk.Tk):
        def __init__(self, picks, text):
            tk.Tk.__init__(self)
            self.resizable(width=False, height=False)
            self.title('Select desired download')
            self.protocol('WM_DELETE_WINDOW', self.on_exit)
            self.l = tk.Label(self, text='Please select desired download {}'.format(text))
            self.l.pack()
            self.ChkBox = checkboxfromlist(self, picks)
            self.ChkBox.pack()
            self.Button = tk.Button(self, text='Ok', width=40, height=2, command=self.quit)
            self.Button.pack()
            # Make popup window at the centre
            self.update_idletasks()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
            x = w/2 - size[0]/2
            y = h/2 - size[1]/2
            self.geometry('%dx%d+%d+%d' % (size + (x, y)))
            
        def on_exit(self):
        # When you click x to exit, this function is called
            if askyesno("Exit", "Do you want to quit the application?"):
                self.destroy()
                sys.exit(0)
            
    text = ' for '.join(Args)
    App = MainWindow(picks, text)
    App.mainloop()
    mask = App.ChkBox.state()
    App.destroy()
    selected = [item for index, item in enumerate(picks) if mask[index]]
    return selected

def User_Confirm(title, question):
    root = tk.Tk()
    root.withdraw()
    answer = askquestion(title, question)
    root.destroy()
    return answer

def InfoBox(title, info):
    root = tk.Tk()
    root.withdraw()
    showinfo(title, info)
    root.destroy()
    
def ErrorBox(title, error):
    root = tk.Tk()
    root.withdraw()
    showerror(title, error)
    root.destroy()

def AskOpenFile(title, filetype):
    root = tk.Tk()
    root.withdraw()
    filename = askopenfilename(title=title, filetypes=filetype)
    root.destroy()
    return filename

def AskDirectory(title):
    root = tk.Tk()
    root.withdraw()
    directory = askdirectory(title=title)
    root.destroy()
    return directory