import tkinter as tk
from tkinter import ttk
import json
import os

hosts = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "network", "host.json")

def gui_start():

    def load_hosts():
        if not os.path.exists(hosts):
            return {}
        with open(hosts, 'r') as f:
            return json.load(f)


    usr = load_hosts()
    print(usr)


    params = usr.values()

    def create_small_window(title):
        small_win = tk.Toplevel(root)
        small_win.title(title)
        main_width = root.winfo_width()
        main_height = root.winfo_height()
        small_width = main_width // 3
        small_height = main_height // 3
        small_win.geometry(f"{small_width}x{small_height}")
        tk.Label(small_win, text=f"This is {title} window").pack(expand=True)

    def open_window1():
        create_small_window("settings")

    def open_window2():
        create_small_window("Window 2")

    # Create main window
    root = tk.Tk()
    root.title("app")
    root.geometry("1200x800")


    left_width = int(0.25 * 800)  
    left_frame = tk.Frame(root, width=left_width, bg='gray')
    left_frame.pack(side='left', fill='both')

    # Canvas for scrolling
    canvas = tk.Canvas(left_frame, bg='gray', width=left_width)
    scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)

    # Inner frame to hold the parameter boxes
    inner_frame = tk.Frame(canvas, bg='gray')
    canvas.create_window((0, 0), window=inner_frame, anchor='nw', width=left_width)

    # Add unique boxes for each parameter (300px height, full scrollbar width)
    box_height = 300
    box_width = left_width - 5  # Small padding

    for i, (key, param) in enumerate(usr.items()):
        box = tk.Frame(inner_frame, width=box_width, height=box_height, 
                    bg='#4A4A4A', relief='raised', bd=2)
        box.pack(pady=5, padx=2, fill='x')
        
        # Botón con el nombre del parámetro
        def on_param_click(k=key, p=param):
            print(f"Botón de parámetro presionado: IP={k}, info={p}")
            # Aquí puedes abrir una ventana o mostrar más info si quieres
        param_btn = tk.Button(box, text=f"{param}", font=('Arial', 10, 'bold'),
                            bg='#4A4A4A', fg='white', anchor='w', relief='raised', bd=2,
                            command=on_param_click)
        param_btn.pack(pady=10, padx=10, fill='x')
        
        # Add some content to show it's a unique box (customize as needed)
        content_frame = tk.Frame(box, bg='#4A4A4A')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Mostrar la clave asociada al parámetro
        tk.Label(content_frame, text=f"IP: {key}", bg='#4A4A4A', fg='lightgray').pack(anchor='w')
        tk.Label(content_frame, text=f"Height: {box_height}px", bg='#4A4A4A', fg='lightgray').pack(anchor='w')

    # Bind mousewheel to canvas for better scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Update scroll region after adding content
    def update_scrollregion(event=None):
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))

    inner_frame.bind('<Configure>', update_scrollregion)
    canvas.bind('<Configure>', update_scrollregion)


    right_frame = tk.Frame(root, bg='black')
    right_frame.pack(side='right', fill='both', expand=True)


    button1 = tk.Button(right_frame, text="SETTINGS", command=open_window1, 
                    bg='gray', fg='white', font=('Arial', 10, 'bold'),
                    relief='raised', bd=2)
    button1.place(relx=1.0, rely=0.02, anchor='ne', x=-10)

    # Second button (below the first)
    button2 = tk.Button(right_frame, text="Open Window 2", command=open_window2,
                    bg='gray', fg='white', font=('Arial', 10, 'bold'),
                    relief='raised', bd=2)
    button2.place(relx=1.0, rely=0.08, anchor='ne', x=-10)
    # Run the GUI
    root.mainloop()