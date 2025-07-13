import tkinter as tk
from tkinter import messagebox, filedialog
import pyperclip
import threading
import time
import json # Importar el módulo json para guardar/cargar datos
import csv # Importar el módulo csv para guardar en formato CSV

# Variable global para controlar el estado del monitoreo
# True significa que el monitoreo está activo, False significa que está detenido
monitor_activo = False
# Evento para señalar al hilo de monitoreo que debe detenerse
stop_event = threading.Event()
# Variable para almacenar el hilo del monitor
monitor_thread = None

def iniciar_o_parar_monitor():
    """
    Controla el inicio y la detención del monitoreo del portapapeles.
    Cambia el texto y el comando del botón según el estado actual.
    """
    global monitor_activo, monitor_thread

    if not monitor_activo:
        # Intentar iniciar el monitoreo
        pares = []
        for i in range(10):
            original = entradas_a_reemplazar[i].get()
            reemplazo = entradas_nuevo_texto[i].get()
            if original: # Solo añadir pares si el campo "Reemplazar" no está vacío
                pares.append((original, reemplazo))

        if not pares:
            messagebox.showwarning("Atención", "Debes completar al menos un par de reemplazo para iniciar el monitoreo.")
            return

        # Restablecer el evento de detención antes de iniciar un nuevo hilo
        stop_event.clear()
        
        # Iniciar el hilo de monitoreo
        monitor_thread = threading.Thread(target=monitor_portapapeles, args=(pares, stop_event), daemon=True)
        monitor_thread.start()
        
        monitor_activo = True
        boton_control.config(text="Parar", bg="#FF5733", activebackground="#E04E2D") # Cambiar texto y color a rojo al parar
    else:
        # Intentar detener el monitoreo
        stop_event.set() # Señalar al hilo que se detenga
        # Esperar un corto tiempo para que el hilo tenga la oportunidad de detenerse
        # if monitor_thread and monitor_thread.is_alive():
        #     monitor_thread.join(timeout=1) # Esperar como máximo 1 segundo

        monitor_activo = False
        boton_control.config(text="Iniciar", bg="#4CAF50", activebackground="#45a049") # Cambiar texto y color a verde al iniciar


def monitor_portapapeles(pares_reemplazo, stop_event_obj):
    """
    Función que se ejecuta en un hilo separado para monitorear el portapapeles.
    """
    texto_anterior = ""
    while not stop_event_obj.is_set(): # Continuar mientras el evento de detención no esté activado
        try:
            texto_actual = pyperclip.paste()
            if texto_actual != texto_anterior:
                texto_modificado = texto_actual
                for original, reemplazo in pares_reemplazo:
                    texto_modificado = texto_modificado.replace(original, reemplazo)
                
                if texto_modificado != texto_actual:
                    pyperclip.copy(texto_modificado)
                    print("Reemplazado:", texto_modificado)
                    texto_anterior = texto_modificado
                else:
                    texto_anterior = texto_actual
            time.sleep(0.5) # Esperar medio segundo antes de la próxima comprobación
        except pyperclip.PyperclipException as e:
            # Manejar errores específicos de pyperclip, por ejemplo, si no hay un copiador/pegador disponible
            print(f"Error de Pyperclip: {e}. El monitoreo se detendrá.")
            stop_event_obj.set() # Detener el monitoreo en caso de error
            # En una aplicación real, se usaría un Queue para comunicar esto al hilo principal
            # Por simplicidad, lo dejamos así para demostración, pero es una mala práctica para UIs
        except Exception as e:
            # Capturar cualquier otra excepción inesperada
            print(f"Ha ocurrido un error inesperado: {e}. El monitoreo se detendrá.")
            stop_event_obj.set() # Detener el monitoreo en caso de error

def limpiar_entradas():
    """
    Limpia el contenido de todos los campos de entrada.
    """
    for i in range(10):
        entradas_a_reemplazar[i].delete(0, tk.END)
        entradas_nuevo_texto[i].delete(0, tk.END)

def guardar_entradas():
    """
    Guarda el contenido de todos los campos de entrada en un archivo CSV.
    Propone como nombre de archivo "TextoOriginalTextoRemplazo.csv".
    """
    pares_a_guardar = []
    for i in range(10):
        original = entradas_a_reemplazar[i].get()
        reemplazo = entradas_nuevo_texto[i].get()
        # Solo guardar pares que tengan al menos el texto original
        if original or reemplazo:
            pares_a_guardar.append([original, reemplazo])
    
    # Nombre de archivo predeterminado
    default_filename = f"{entradas_a_reemplazar[0].get()}-{entradas_nuevo_texto[0].get()}.csv"

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Guardar configuración de reemplazo",
        initialfile=default_filename # Sugerir el nombre de archivo
    )
    
    if file_path:
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["TextoOriginal", "TextoReemplazo"]) # Escribir encabezado
                writer.writerows(pares_a_guardar) # Escribir los datos
            messagebox.showinfo("Guardado", f"Configuración guardada en: {file_path}")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo: {e}")

def cargar_entradas():
    """
    Carga el contenido de los campos de entrada desde un archivo CSV.
    """
    file_path = filedialog.askopenfilename(
        defaultextension=".csv",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
        title="Cargar configuración de reemplazo"
    )
    
    if file_path:
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None) # Leer el encabezado, si existe
                
                # Limpiar entradas actuales antes de cargar las nuevas
                limpiar_entradas()

                for i, row in enumerate(reader):
                    if i < 10: # Asegurarse de no exceder el número de campos disponibles
                        original_text = row[0] if len(row) > 0 else ""
                        reemplazo_text = row[1] if len(row) > 1 else ""
                        entradas_a_reemplazar[i].insert(0, original_text)
                        entradas_nuevo_texto[i].insert(0, reemplazo_text)
        except FileNotFoundError:
            messagebox.showerror("Error al cargar", "El archivo no fue encontrado.")
        except Exception as e:
            messagebox.showerror("Error al cargar", f"No se pudo cargar el archivo: {e}")

def invertir_entradas():
    """
    Invierte el contenido de los campos "Reemplazar" y "Por" para cada par.
    """
    for i in range(10):
        original_text = entradas_a_reemplazar[i].get()
        reemplazo_text = entradas_nuevo_texto[i].get()

        entradas_a_reemplazar[i].delete(0, tk.END)
        entradas_nuevo_texto[i].delete(0, tk.END)

        entradas_a_reemplazar[i].insert(0, reemplazo_text)
        entradas_nuevo_texto[i].insert(0, original_text)

# Interfaz de usuario
ventana = tk.Tk()
ventana.title("Reemplazo Automático de Portapapeles")

# Frame para los campos de entrada
frame_campos = tk.Frame(ventana, padx=10, pady=10)
frame_campos.pack(padx=10, pady=10)

entradas_a_reemplazar = []
entradas_nuevo_texto = []

# Crear 10 pares de etiquetas y campos de entrada
for i in range(10):
    tk.Label(frame_campos, text=f"Reemplazar {i+1}:").grid(row=i, column=0, sticky="w", pady=2)
    e1 = tk.Entry(frame_campos, width=25) # Ancho reducido
    e1.grid(row=i, column=1, padx=5, pady=2)
    entradas_a_reemplazar.append(e1)

    tk.Label(frame_campos, text="Por:").grid(row=i, column=2, sticky="w", pady=2)
    e2 = tk.Entry(frame_campos, width=25) # Ancho reducido
    e2.grid(row=i, column=3, padx=5, pady=2)
    entradas_nuevo_texto.append(e2)

# Frame para los botones de control
frame_botones = tk.Frame(ventana, pady=10)
frame_botones.pack()

# Configuración de estilo base para los botones (excepto "Parar")
button_font = ("Arial", 10, "bold")
button_bg = "#4CAF50" # Verde
button_fg = "white"
button_active_bg = "#45a049"
button_relief = "raised"
button_bd = 3
button_padx = 10 # Padding reducido
button_pady = 5 # Padding reducido
button_cursor = "hand2"

# Botón de control (iniciar/parar)
boton_control = tk.Button(frame_botones, text="Iniciar", command=iniciar_o_parar_monitor,
                          font=button_font, bg=button_bg, fg=button_fg,
                          activebackground=button_active_bg, activeforeground=button_fg,
                          relief=button_relief, bd=button_bd, padx=button_padx, pady=button_pady, cursor=button_cursor)
boton_control.pack(side=tk.LEFT, padx=5)

# Botón para limpiar entradas
boton_limpiar = tk.Button(frame_botones, text="Limpiar", command=limpiar_entradas,
                          font=button_font, bg=button_bg, fg=button_fg,
                          activebackground=button_active_bg, activeforeground=button_fg,
                          relief=button_relief, bd=button_bd, padx=button_padx, pady=button_pady, cursor=button_cursor)
boton_limpiar.pack(side=tk.LEFT, padx=5)

# Botón para guardar configuración
boton_guardar = tk.Button(frame_botones, text="Guardar", command=guardar_entradas,
                          font=button_font, bg=button_bg, fg=button_fg,
                          activebackground=button_active_bg, activeforeground=button_fg,
                          relief=button_relief, bd=button_bd, padx=button_padx, pady=button_pady, cursor=button_cursor)
boton_guardar.pack(side=tk.LEFT, padx=5)

# Botón para cargar configuración
boton_cargar = tk.Button(frame_botones, text="Cargar", command=cargar_entradas,
                          font=button_font, bg=button_bg, fg=button_fg,
                          activebackground=button_active_bg, activeforeground=button_fg,
                          relief=button_relief, bd=button_bd, padx=button_padx, pady=button_pady, cursor=button_cursor)
boton_cargar.pack(side=tk.LEFT, padx=5)

# Botón para invertir el orden de los textos
boton_invertir = tk.Button(frame_botones, text="Invertir", command=invertir_entradas,
                           font=button_font, bg=button_bg, fg=button_fg,
                           activebackground=button_active_bg, activeforeground=button_fg,
                           relief=button_relief, bd=button_bd, padx=button_padx, pady=button_pady, cursor=button_cursor)
boton_invertir.pack(side=tk.LEFT, padx=5)

# Iniciar el bucle principal de la interfaz de usuario
ventana.mainloop()
