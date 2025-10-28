import tkinter as tk
from PIL import Image, ImageTk
from manage_cinemas import ManageCinemasPage
from generate_reports import GenerateReportsPage
from view_listings import ViewListingsPage
from book_tickets import BookTicketsPage
from cancel_booking import CancelBookingPage
from manage_staff import ManageStaffPage

#inherits from App class in app.py
class MainMenuPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.user = self.app.user
        
        image = Image.open("img2.jpg") 
        image = image.resize((1600, 800))  
        self.photo = ImageTk.PhotoImage(image)  
        image_label = tk.Label(self, image=self.photo, bg="white")
        image_label.grid(row=0, column=0, rowspan=10, padx=0, pady=0)
      
        # Sidebar menu
        self.sidebar_width = 350  # Adjusted sidebar width
        self.sidebar = tk.Frame(self, bg="black", width=self.sidebar_width, height=self.winfo_height())
        self.sidebar.place(x=-self.sidebar_width, y=0)  # Initially hidden completely off-screen

        # Toggle Button (with no visible background)
        self.toggle_btn = tk.Button(self, text="☰", font=("Arial", 24), command=self.toggle_sidebar,
                                    bg=self["bg"], fg="black", bd=0)  # Transparent background
        self.toggle_btn.place(x=15, y=15)  # Adjusted position

        # Menu Buttons
        self.create_menu_buttons()

        # Logout Button
        self.logout_button = tk.Button(self, text="Logout", command=self.app.logout, #logout method defined in App class
                                       bg="white", fg="darkblue", font=("Arial", 16, "bold"),  # Larger font size
                                       padx=20, pady=10)  # Larger padding
        self.logout_button.place(x=1350, y=15)  # Adjusted position

        self.pack(fill="both", expand=True)

    def toggle_sidebar(self):
        """Opens or closes the sidebar menu."""
        current_x = self.sidebar.winfo_x()

        # If the sidebar is off-screen (negative x), we move it to x=0 (on-screen)
        if current_x < 0:
            self.sidebar.place(x=0, y=0)
        else:
            # If the sidebar is on-screen, we move it off-screen (negative x)
            self.sidebar.place(x=-self.sidebar_width, y=0)

    def create_menu_buttons(self):
        """Creates menu buttons based on user role."""
        #open access
        menu_options = [
            ("Home", lambda: self.app.show_page(MainMenuPage)),
            ("View Listings", lambda: self.app.show_page(ViewListingsPage)),
            ("Book Tickets", lambda: self.app.show_page(BookTicketsPage)),
            ("Cancel Booking", lambda: self.app.show_page(CancelBookingPage)),
        ]

        #manager only
        if hasattr(self.user.role, 'title') and self.user.role.title.lower() == "manager":
            menu_options.append(("Manage Cinemas", lambda: self.app.show_page(ManageCinemasPage)))

        #admin and manager only
        if hasattr(self.user.role, 'title') and self.user.role.title.lower() in ["manager", "admin"]:
            menu_options.extend([
                ("Generate Reports", lambda: self.app.show_page(GenerateReportsPage)),
                ("Manage Staff", lambda: self.app.show_page(ManageStaffPage))
            ])

        for i, (text, command) in enumerate(menu_options):
            btn = tk.Button(self.sidebar, text=text, command=command, font=("Arial", 16),
                            bg="#001a66", fg="white", width=25, height=2)
            btn.pack(pady=10)
