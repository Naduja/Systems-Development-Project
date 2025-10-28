#import here
from database import get_session
from models import *
from login import LoginPage
import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Horizon Cinemas")
        self.root.geometry("800x600")

        self.session = get_session()
        self.user = None  #set this after logging in

        #create an outer frame to hold the canvas and scrollbar
        self.outer_frame = ttk.Frame(self.root)
        self.outer_frame.pack(fill=tk.BOTH, expand=True)

        #create a canvas inside the outer frame
        self.canvas = tk.Canvas(self.outer_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) 

        #add a vertical scrollbar linked to the canvas
        self.scrollbar = ttk.Scrollbar(self.outer_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        #connect the canvas and scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        #create a frame (scrollable frame) as a child of the canvas
        self.scrollable_frame = ttk.Frame(self.canvas)

        #add the scrollable frame to the canvas using create_window
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        #make the canvas scrollable
        self.scrollable_frame.bind("<Configure>", self._configure_scrollable_region)

        #show the login page
        self.show_page(LoginPage)

    #configure the scrollable region of the canvas
    def _configure_scrollable_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    #function to clear the window and show a new page
    def show_page(self, PageClass, **kwargs):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        page = PageClass(self.scrollable_frame, self, **kwargs)
        page.pack(expand=True, fill="both")
    
    #logout function
    def logout(self):
        self.user = None  #set back to None after logging out
        self.show_page(LoginPage)