import cv2
import face_recognition
import os
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter
import numpy as np

# Initializarea variabilelor
folder_path = "database"  # Calea catre folderul cu imagini
captured_frame = None    # Variabila pentru pozele facute
recognition_state = False  # Variabila pornire recunoastere faciala
webcam_state = True  # Variabila pentru starea webcamului


# Functie pentru a incarca imaginile si recunoasterea faciala din baza de date
def load_images():
    known_faces = []
    known_names = []

    for file_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, file_name)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(file_name.split('.')[0])

    return known_faces, known_names


# Functie pentru a actualiza vizualizarea camerei
def update_camera():
    if webcam_state:
        ret, frame = cap.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if recognition_state:
            faces = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, faces)

            for (top, right, bottom, left), face_encoding in zip(faces, face_encodings):
                matches = face_recognition.compare_faces(known_faces, face_encoding)
                name = "Necunoscut"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
    else:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        panel.imgtk = imgtk
        panel.config(image=imgtk)
    panel.after(10, update_camera)


# Functie pentru a realiza captura de la webcam
def capture_image():
    global captured_frame
    ret, captured_frame = cap.read()


# Functie pentru a adauga o persoana in baza de date
def add_person():
    # Realizarea capturii de la webcam
    capture_image()

    if captured_frame is not None:
        # Identificare persoane in imagine
        face_locations = face_recognition.face_locations(captured_frame)
        num_faces = len(face_locations)

        if num_faces == 0:
            messagebox.showerror("Eroare",
                                 "Nu s-a găsit nicio față în imagine. Adăugarea în baza de date nu este posibilă.")
            return
        elif num_faces > 1:
            messagebox.showerror("Eroare",
                                 "Există mai multe persoane în cadru. Adăugarea în baza de date nu este posibilă.")
            return

    name = customtkinter.CTkInputDialog(title="Input", text="Introduceți numele persoanei:").get_input()

    if name is None:
        return  # Utilizatorul a apasat butonul "Cancel", fara a introduce un nume

    if captured_frame is not None:

        # Salvarea imaginii in folderul bazei de date
        image_path = os.path.join(folder_path, f"{name}.jpg")
        cv2.imwrite(image_path, captured_frame)

        # incarcarea imaginii pentru recunoasterea faciala
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(name)

        messagebox.showinfo("Succes", f"Persoana {name} a fost adăugată în baza de date.")
    else:
        messagebox.showerror("Eroare", "Nu s-a putut realiza captura de la webcam.")


# Functie pentru a sterge o persoana din baza de date
def delete_person():
    name = customtkinter.CTkInputDialog(title="Input",
                                        text="Introduceți numele persoanei pe care doriți să o ștergeți:").get_input()

    if name is None:
        return  # Utilizatorul a apasat butonul "Cancel", fara a introduce un nume

    if name:
        if name in known_names:
            index = known_names.index(name)
            del known_faces[index]
            del known_names[index]

            image_path = os.path.join(folder_path, f"{name}.jpg")
            os.remove(image_path)
            messagebox.showinfo("Succes", f"Persoana {name} a fost ștearsă din baza de date.")

        else:
            messagebox.showerror("Eroare 404", f"Persoana {name} nu a fost găsită în baza de date.")


# Functie pentru oprire pornire recunoastere faciala
def toggle_recognition():
    global recognition_state
    recognition_state = not recognition_state
    if recognition_state:
        btn_start_stop.configure(text="Oprire recunoaștere facială")
    else:
        btn_start_stop.configure(text="Pornire recunoaștere facială")


# Functie pentru oprire pornire webcam
def toggle_webcam():
    global webcam_state
    global cap
    webcam_state = not webcam_state
    if webcam_state:
        add_button.configure(state=NORMAL)
        btn_start_stop_webcam.configure(text="Oprire webcam")
        cap = cv2.VideoCapture(0)
    else:
        add_button.configure(state=DISABLED)
        btn_start_stop_webcam.configure(text="Pornire webcam")
        cap.release()  # Adaugăm această linie pentru a opri webcam-ul când este oprit explicit


# Crearea interfetei grafice
root = customtkinter.CTk()
root.title("Recunoaștere facială")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# Crearea unui panou pentru afisarea camerei
panel = Label(root)
panel.grid(row=0, column=0, columnspan=2, padx=0, pady=0)

# Buton pentru adăugare persoane in baza de date
add_button = customtkinter.CTkButton(root, text="Adaugă persoană", command=add_person)
add_button.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

# Buton pentru tergere persoane din baza de date
delete_button = customtkinter.CTkButton(root, text="Șterge persoană", command=delete_person)
delete_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

# Buton pentru start stop recunoastere
btn_start_stop = customtkinter.CTkButton(root, text="Pornire recunoaștere facială", command=toggle_recognition)
btn_start_stop.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

# Buton pentru start stop webcam
btn_start_stop_webcam = customtkinter.CTkButton(root, text="Oprire Webcam", command=toggle_webcam)
btn_start_stop_webcam.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

# Initializarea camerei
cap = cv2.VideoCapture(0)

# Incarcarea imaginilor pentru recunoasterea faciala
known_faces, known_names = load_images()

# Actualizarea camerei
update_camera()

# Rulare in loop
root.mainloop()
