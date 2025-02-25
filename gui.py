import os
import time
import threading
import funcs as fx
from examenes import main
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from tqdm import tqdm
from IPython.display import clear_output
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox


# --- Interfaz gráfica con Tkinter ---
def start_scraping():
    credentials_file = entry_credentials.get()
    año = entry_año.get()
    llamado = entry_llamado.get()
    residual_timeout = entry_timeout.get()

    if not os.path.exists(credentials_file):
        messagebox.showerror("Error", "El archivo de credenciales no existe.")
        return

    try:
        año_val = int(año) if año else None
    except ValueError:
        messagebox.showerror("Error", "El año debe ser un número.")
        return

    try:
        timeout_val = int(residual_timeout)
    except ValueError:
        messagebox.showerror("Error", "El tiempo residual debe ser un número.")
        return

    btn_start.config(state="disabled")
    lbl_status.config(text="Scraping iniciado...")

    def run_thread():
        try:
            main(credentials_file, año_val, llamado, timeout_val)
            lbl_status.config(text="Scraping completado. Archivo examenes.csv creado.")
        except Exception as e:
            lbl_status.config(text=f"Error: {e}")
        finally:
            btn_start.config(state="normal")

    t = threading.Thread(target=run_thread)
    t.start()


def select_file():
    filename = filedialog.askopenfilename(title="Seleccionar archivo de credenciales")
    if filename:
        entry_credentials.delete(0, tk.END)
        entry_credentials.insert(0, filename)


# Crear ventana principal
root = tk.Tk()
root.title("Scraping de Actas")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Archivo de credenciales
lbl_credentials = tk.Label(frame, text="Archivo de credenciales:")
lbl_credentials.grid(row=0, column=0, sticky="e")
entry_credentials = tk.Entry(frame, width=50)
entry_credentials.grid(row=0, column=1)
btn_browse = tk.Button(frame, text="Examinar", command=select_file)
btn_browse.grid(row=0, column=2, padx=5)

# Año
lbl_año = tk.Label(frame, text="Año:")
lbl_año.grid(row=1, column=0, sticky="e")
entry_año = tk.Entry(frame)
entry_año.grid(row=1, column=1)

# Llamado
lbl_llamado = tk.Label(frame, text="Llamado:")
lbl_llamado.grid(row=2, column=0, sticky="e")
entry_llamado = tk.Entry(frame)
entry_llamado.grid(row=2, column=1)

# Tiempo residual
lbl_timeout = tk.Label(frame, text="Tiempo residual:")
lbl_timeout.grid(row=3, column=0, sticky="e")
entry_timeout = tk.Entry(frame)
entry_timeout.grid(row=3, column=1)

# Botón de inicio
btn_start = tk.Button(frame, text="Iniciar Scraping", command=start_scraping)
btn_start.grid(row=4, column=0, columnspan=3, pady=10)

# Etiqueta de estado
lbl_status = tk.Label(frame, text="Estado: Esperando...")
lbl_status.grid(row=5, column=0, columnspan=3)

root.mainloop()
