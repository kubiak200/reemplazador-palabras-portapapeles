import tkinter as tk
from tkinter import messagebox
import pyperclip
import threading
import time

monitoreando = False
hilo_monitor = None
detener_evento = threading.Event()

def iniciar_o_detener_monitor():
    global monitoreando, hilo_monitor, detener_evento

    if not monitoreando:
        pares = []
        for i in range(10):
            original = entradas_a_reemplazar[i].get()
            reemplazo = entradas_nuevo_texto[i].get()
            if original:
                pares.append((original, reemplazo))

        if not pares:
            messagebox.showwarning("Atenci├│n", "Debes completar al menos un par de reemplazo.")
            return

        detener_evento.clear()

        def monitor():
            texto_anterior = ""
            while not detener_evento.is_set():
                texto_actual = pyperclip.paste()
                if texto_actual != texto_anterior:
                    texto_modificado = texto_actual
                    for original, reemplazo in pares:
                        texto_modificado = texto_modificado.replace(original, reemplazo)
                    if texto_modificado != texto_actual:
                        pyperclip.copy(texto_modificado)
                        print("Reemplazado:", texto_modificado)
                        texto_anterior = texto_modificado
                    else:
                        texto_anterior = texto_actual
                time.sleep(0.5)

        hilo_monitor = threading.Thread(target=monitor, daemon=True)
        hilo_monitor.start()
        monitoreando = True
        boton_inicio.config(text="Parar Monitoreo")
        messagebox.showinfo("Ô£à Listo", "El monitoreo est├í en marcha.")
    else:
        detener_evento.set()
        monitoreando = False
        boton_inicio.config(text="Iniciar Monitoreo")
        messagebox.showinfo("­ƒøæ Detenido", "El monitoreo se ha detenido.")

# Interfaz
ventana = tk.Tk()
ventana.title("Reemplazo Autom├ítico de Portapapeles")

frame_campos = tk.Frame(ventana)
frame_campos.pack(padx=10, pady=10)

entradas_a_reemplazar = []
entradas_nuevo_texto = []

for i in range(10):
    tk.Label(frame_campos, text="Reemplazar:").grid(row=i, column=0)
    e1 = tk.Entry(frame_campos, width=20)
    e1.grid(row=i, column=1)
    entradas_a_reemplazar.append(e1)

    tk.Label(frame_campos, text="Por:").grid(row=i, column=2)
    e2 = tk.Entry(frame_campos, width=20)
    e2.grid(row=i, column=3)
    entradas_nuevo_texto.append(e2)

boton_inicio = tk.Button(ventana, text="Iniciar Monitoreo", command=iniciar_o_detener_monitor)
boton_inicio.pack(pady=10)

ventana.mainloop()
