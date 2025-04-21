import tkinter as tk
from tkinter import ttk, messagebox
import pymongo
from pymongo.errors import ConnectionFailure, ConfigurationError
import re
from PIL import Image, ImageTk
import os

# --- Configuración ---
MONGO_URI = "mongodb+srv://michellpolicarpio:policarpio@cluster0.2yrckuk.mongodb.net/"
DATABASE_NAME = "Usuarios"

# Colecciones
COLLECTIONS = {
    'estudiantes': "Alumnos",
    'materias': "Materias",
    'profesores': "Profesores"
}

# Consultas precargadas
CONSULTAS = {
    "Estudiantes por carrera": {
        "coleccion": "Alumnos",
        "consulta": {"carrera": "Ingeniería Mecatrónica"},
        "descripcion": "Muestra todos los estudiantes de Ingeniería Mecatrónica"
    },
    "Materias con más de 4 créditos": {
        "coleccion": "Materias",
        "consulta": {"creditos": {"$gt": 4}},
        "descripcion": "Muestra todas las materias que tienen más de 4 créditos"
    },
    "Estudiantes ordenados por nombre": {
        "coleccion": "Alumnos",
        "consulta": {},
        "orden": [("nombre", 1)],
        "descripcion": "Muestra todos los estudiantes ordenados por nombre"
    },
    "Materias por carrera": {
        "coleccion": "Materias",
        "consulta": {"carreras": "Ingeniería Informática"},
        "descripcion": "Muestra todas las materias de Ingeniería Informática"
    }
}

# Lista predefinida de carreras
CARRERAS = [
    "Ingeniería Mecatrónica",
    "Ingeniería Electrónica",
    "Ingeniería Informática"
]

# Lista predefinida de departamentos
DEPARTAMENTOS = [
    "Departamento de Eléctrica",
    "Departamento de Electrónica",
    "Departamento de Informática",
    "Departamento de Mecatrónica"
]

# Columnas esperadas por tabla
EXPECTED_COLUMNS = {
    'estudiantes': ['nombre', 'matricula', 'carrera'],
    'materias': ['codigo', 'nombre', 'creditos', 'carreras'],
    'profesores': ['nombre', 'licenciatura', 'email']
}

class MongoViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión Académica - FIEE")
        self.root.geometry("1000x800")
        
        # Configurar tema y estilo
        self.style = ttk.Style()
        self.configure_styles()
        
        # Configurar color de fondo
        self.root.configure(bg='#F5F5F5')

        self.client = None
        self.db = None
        self.collection = None
        self.selected_item = None
        self.current_section = 'estudiantes'

        self.create_widgets()
        self.configure_layout()
        self.create_menu()
        self.load_logo()

    def load_logo(self):
        try:
            # Cargar y redimensionar el logo
            logo_path = "FIEE.png"
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                # Redimensionar manteniendo la proporción
                logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                
                # Crear y posicionar el label del logo
                self.logo_label = ttk.Label(
                    self.control_frame,
                    image=self.logo_photo,
                    background='#F5F5F5'
                )
                self.logo_label.grid(row=0, column=3, padx=5, pady=5)
            else:
                print("Logo no encontrado en:", logo_path)
        except Exception as e:
            print("Error al cargar el logo:", e)

    def configure_styles(self):
        # Estilo general
        self.style.configure(".",
            font=('Helvetica', 10),
            background='#F5F5F5',
            foreground='#000000'
        )
        
        # Estilo para frames con título
        self.style.configure("Title.TLabelframe",
            background='#F5F5F5',
            foreground='#003366',
            font=('Helvetica', 12, 'bold'),
            borderwidth=2,
            relief="solid"
        )
        self.style.configure("Title.TLabelframe.Label",
            font=('Helvetica', 12, 'bold'),
            foreground='#003366',
            background='#F5F5F5',
            padding=(10, 5)
        )
        
        # Estilo para botones principales
        self.style.configure("Connect.TButton",
            font=('Helvetica', 10),
            background='#007bff',
            foreground='#ffffff'
        )
        
        self.style.configure("Refresh.TButton",
            font=('Helvetica', 10),
            background='#17a2b8',  # Color cyan
            foreground='#ffffff'
        )

        self.style.configure("Help.TButton",
            font=('Helvetica', 10),
            background='#28a745',  # Color verde
            foreground='#ffffff'
        )
        
        self.style.configure("Add.TButton",
            font=('Helvetica', 10),
            background='#28a745',
            foreground='#ffffff'
        )
        
        self.style.configure("Update.TButton",
            font=('Helvetica', 10),
            background='#ffc107',
            foreground='#000000'
        )
        
        self.style.configure("Delete.TButton",
            font=('Helvetica', 10),
            background='#dc3545',
            foreground='#ffffff'
        )
        
        self.style.configure("Clear.TButton",
            font=('Helvetica', 10),
            background='#6c757d',
            foreground='#ffffff'
        )
        
        # Mapeo de estados para botones
        self.style.map("Connect.TButton",
            background=[('active', '#0056b3')],
            foreground=[('active', '#ffffff')]
        )
        
        self.style.map("Refresh.TButton",
            background=[('active', '#138496')],
            foreground=[('active', '#ffffff')]
        )

        self.style.map("Help.TButton",
            background=[('active', '#218838')],
            foreground=[('active', '#ffffff')]
        )
        
        self.style.map("Add.TButton",
            background=[('active', '#218838')],
            foreground=[('active', '#ffffff')]
        )
        
        self.style.map("Update.TButton",
            background=[('active', '#e0a800')],
            foreground=[('active', '#000000')]
        )
        
        self.style.map("Delete.TButton",
            background=[('active', '#c82333')],
            foreground=[('active', '#ffffff')]
        )
        
        self.style.map("Clear.TButton",
            background=[('active', '#5a6268')],
            foreground=[('active', '#ffffff')]
        )
        
        # Estilo para etiquetas
        self.style.configure("TLabel",
            font=('Helvetica', 10),
            background='#F5F5F5',
            foreground='#000000'
        )
        
        self.style.configure("Status.TLabel",
            font=('Helvetica', 10, 'bold'),
            background='#F5F5F5',
            foreground='#28a745',
            padding=8
        )
        
        # Estilo para entradas
        self.style.configure("TEntry",
            font=('Helvetica', 10),
            fieldbackground='white',
            foreground='#000000',
            padding=8,
            borderwidth=2,
            relief="solid"
        )
        
        # Estilo para Treeview
        self.style.configure("Treeview",
            font=('Helvetica', 10),
            rowheight=25,
            background='white',
            fieldbackground='white',
            foreground='#000000'
        )
        self.style.configure("Treeview.Heading",
            font=('Helvetica', 10, 'bold'),
            background='#E0E0E0',
            foreground='#000000'
        )
        self.style.map("Treeview",
            background=[('selected', '#E0E0E0')],
            foreground=[('selected', '#000000')]
        )

    def configure_layout(self):
        # Configurar el frame principal para que se expanda
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configurar el main_frame para que se expanda
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Más peso para el notebook
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar el control_frame
        self.control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.control_frame.grid_columnconfigure(0, weight=0)  # Sin expansión para los botones
        self.control_frame.grid_columnconfigure(1, weight=1)  # Expansión para el estado
        
        # Cargar el logo
        self.load_logo()

        # Configurar el notebook
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # Configurar los frames de las pestañas
        for frame in [self.estudiantes_frame, self.materias_frame, self.profesores_frame, self.consultas_frame]:
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(1, weight=1)  # Más peso para la tabla

    def create_menu(self):
        menubar = tk.Menu(self.root, bg='#E0E0E0', fg='#000000')
        self.root.config(menu=menubar)

        # Menú Archivo
        file_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg='#F5F5F5',
            fg='#000000',
            activebackground='#E0E0E0',
            activeforeground='#000000'
        )
        file_menu.add_command(label="Conectar", command=self.connect_mongo)
        file_menu.add_command(label="Refrescar", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        # Menú Ayuda
        help_menu = tk.Menu(
            menubar,
            tearoff=0,
            bg='#F5F5F5',
            fg='#000000',
            activebackground='#E0E0E0',
            activeforeground='#000000'
        )
        help_menu.add_command(label="Ayuda", command=self.show_help)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

    def create_widgets(self):
        # --- Frame Principal ---
        self.main_frame = ttk.Frame(self.root, padding="10", style="Title.TLabelframe")
        
        # --- Frame Superior (Controles) ---
        self.control_frame = ttk.LabelFrame(
            self.main_frame,
            text="Panel de Control",
            padding="10",
            style="Title.TLabelframe"
        )
        
        # Frame para los botones
        button_frame = ttk.Frame(self.control_frame)
        button_frame.grid(row=0, column=0, padx=20, pady=5)  # Aumenté el padding horizontal
        
        # Primera fila de botones
        self.connect_button = ttk.Button(
            button_frame, 
            text="Conectar a MongoDB",
            command=self.connect_mongo,
            style="Connect.TButton",
            width=18  # Aumenté el ancho
        )
        self.connect_button.grid(row=0, column=0, padx=3, pady=2)
        
        self.refresh_button = ttk.Button(
            button_frame,
            text="Refrescar",
            command=self.load_data,
            state=tk.DISABLED,
            style="Refresh.TButton",  # Cambié el estilo
            width=18
        )
        self.refresh_button.grid(row=0, column=1, padx=3, pady=2)
        
        # Segunda fila de botones
        self.help_button = ttk.Button(
            button_frame,
            text="Ayuda",
            command=self.show_help,
            style="Help.TButton",  # Nuevo estilo
            width=18
        )
        self.help_button.grid(row=1, column=0, padx=3, pady=2)
        
        self.exit_button = ttk.Button(
            button_frame,
            text="Salir",
            command=self.on_closing,
            style="Delete.TButton",
            width=18
        )
        self.exit_button.grid(row=1, column=1, padx=3, pady=2)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(
            self.control_frame,
            text="Estado: Desconectado",
            foreground='#dc3545',
            style="TLabel"
        )
        self.status_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Frames para cada pestaña
        self.estudiantes_frame = ttk.Frame(self.notebook)
        self.materias_frame = ttk.Frame(self.notebook)
        self.profesores_frame = ttk.Frame(self.notebook)
        self.consultas_frame = ttk.Frame(self.notebook)
        
        # Agregar pestañas al notebook
        self.notebook.add(self.estudiantes_frame, text="Estudiantes")
        self.notebook.add(self.materias_frame, text="Materias")
        self.notebook.add(self.profesores_frame, text="Profesores")
        self.notebook.add(self.consultas_frame, text="Consultas")
        

        # Configurar eventos de cambio de pestaña
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

        # Crear widgets para cada sección
        self.create_estudiantes_widgets()
        self.create_materias_widgets()
        self.create_profesores_widgets()
        self.create_consultas_widgets()

    def on_tab_change(self, event):
        # Obtener el índice de la pestaña seleccionada
        current_tab = self.notebook.index(self.notebook.select())
        sections = ['estudiantes', 'materias', 'profesores', 'consultas']
        self.current_section = sections[current_tab]
        
        # Actualizar la colección actual solo si no estamos en la pestaña de consultas
        if self.db is not None and self.current_section != 'consultas':
            self.collection = self.db[COLLECTIONS[self.current_section]]
            self.load_data()

    def create_estudiantes_widgets(self):
        # Frame para gestión de estudiantes
        self.student_frame = ttk.LabelFrame(
            self.estudiantes_frame,
            text="Gestión de Estudiantes",
            padding="10",
            style="Title.TLabelframe"
        )
        self.student_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.student_frame.grid_columnconfigure(1, weight=1)
        
        # Frame para campos de entrada
        input_frame = ttk.Frame(self.student_frame)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Campos de entrada para estudiantes
        self.nombre_label = ttk.Label(input_frame, text="Nombre:", style="TLabel")
        self.nombre_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        self.nombre_entry = ttk.Entry(input_frame, width=30, style="TEntry")
        self.nombre_entry.grid(row=0, column=1, sticky="ew", pady=2)

        self.matricula_label = ttk.Label(input_frame, text="Matrícula:", style="TLabel")
        self.matricula_label.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
        self.matricula_entry = ttk.Entry(input_frame, width=20, style="TEntry")
        self.matricula_entry.grid(row=1, column=1, sticky="ew", pady=2)

        self.carrera_label = ttk.Label(input_frame, text="Carrera:", style="TLabel")
        self.carrera_label.grid(row=2, column=0, sticky="w", padx=(0, 5), pady=2)
        self.carrera_var = tk.StringVar()
        self.carrera_entry = ttk.Combobox(
            input_frame,
            textvariable=self.carrera_var,
            values=CARRERAS,
            width=30,
            style="TEntry"
        )
        self.carrera_entry.grid(row=2, column=1, sticky="ew", pady=2)
        self.carrera_entry.bind('<KeyRelease>', self.filter_carreras)
        self.carrera_entry.bind('<<ComboboxSelected>>', self.on_carrera_select)

        # Frame para botones
        button_frame = ttk.Frame(self.student_frame)
        button_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)

        # Botones CRUD para estudiantes
        self.add_student_button = ttk.Button(
            button_frame,
            text="Agregar",
            command=self.add_alumno,
            state=tk.DISABLED,
            style="Add.TButton",
            width=12
        )
        self.add_student_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        self.update_student_button = ttk.Button(
            button_frame,
            text="Actualizar",
            command=self.update_alumno,
            state=tk.DISABLED,
            style="Update.TButton",
            width=12
        )
        self.update_student_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.delete_student_button = ttk.Button(
            button_frame,
            text="Eliminar",
            command=self.delete_alumno,
            state=tk.DISABLED,
            style="Delete.TButton",
            width=12
        )
        self.delete_student_button.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        self.clear_student_button = ttk.Button(
            button_frame,
            text="Limpiar",
            command=self.clear_fields,
            style="Clear.TButton",
            width=12
        )
        self.clear_student_button.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Tabla de estudiantes
        self.create_treeview(self.estudiantes_frame, 'estudiantes')

    def create_materias_widgets(self):
        # Frame para gestión de materias
        self.materias_control_frame = ttk.LabelFrame(
            self.materias_frame,
            text="Gestión de Materias",
            padding="5",
            style="Title.TLabelframe"
        )
        self.materias_control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.materias_control_frame.grid_columnconfigure(1, weight=1)
        
        # Frame para campos de entrada
        input_frame = ttk.Frame(self.materias_control_frame)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Campos de entrada para materias en una disposición más compacta
        # Primera fila: Código y Créditos
        row1_frame = ttk.Frame(input_frame)
        row1_frame.grid(row=0, column=0, sticky="ew", pady=2)
        
        self.codigo_label = ttk.Label(row1_frame, text="Código:", style="TLabel", width=8)
        self.codigo_label.grid(row=0, column=0, padx=(0, 5))
        self.codigo_entry = ttk.Entry(row1_frame, width=15, style="TEntry")
        self.codigo_entry.grid(row=0, column=1, padx=(0, 10))

        self.creditos_label = ttk.Label(row1_frame, text="Créditos:", style="TLabel", width=8)
        self.creditos_label.grid(row=0, column=2, padx=(0, 5))
        self.creditos_entry = ttk.Entry(row1_frame, width=8, style="TEntry")
        self.creditos_entry.grid(row=0, column=3)

        # Segunda fila: Nombre
        nombre_frame = ttk.Frame(input_frame)
        nombre_frame.grid(row=1, column=0, sticky="ew", pady=2)
        
        self.nombre_materia_label = ttk.Label(nombre_frame, text="Nombre:", style="TLabel", width=8)
        self.nombre_materia_label.grid(row=0, column=0, padx=(0, 5))
        self.nombre_materia_entry = ttk.Entry(nombre_frame, width=37, style="TEntry")
        self.nombre_materia_entry.grid(row=0, column=1, sticky="ew")

        # Frame para lista de carreras (más compacto)
        carreras_frame = ttk.LabelFrame(input_frame, text="Carreras", padding="2")
        carreras_frame.grid(row=2, column=0, sticky="ew", pady=2)
        
        # Lista de carreras con checkboxes en dos columnas
        self.carreras_vars = {}
        for i, carrera in enumerate(CARRERAS):
            var = tk.BooleanVar()
            self.carreras_vars[carrera] = var
            cb = ttk.Checkbutton(
                carreras_frame,
                text=carrera,
                variable=var,
                style="TCheckbutton"
            )
            cb.grid(row=i//2, column=i%2, sticky="w", padx=5, pady=1)

        # Frame para botones
        button_frame = ttk.Frame(self.materias_control_frame)
        button_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        
        # Botones CRUD para materias
        self.add_materia_button = ttk.Button(
            button_frame,
            text="Agregar",
            command=self.add_materia,
            state=tk.DISABLED,
            style="Add.TButton",
            width=12
        )
        self.add_materia_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        self.update_materia_button = ttk.Button(
            button_frame,
            text="Actualizar",
            command=self.update_materia,
            state=tk.DISABLED,
            style="Update.TButton",
            width=12
        )
        self.update_materia_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.delete_materia_button = ttk.Button(
            button_frame,
            text="Eliminar",
            command=self.delete_materia,
            state=tk.DISABLED,
            style="Delete.TButton",
            width=12
        )
        self.delete_materia_button.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        self.clear_materia_button = ttk.Button(
            button_frame,
            text="Limpiar",
            command=self.clear_materia_fields,
            style="Clear.TButton",
            width=12
        )
        self.clear_materia_button.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Tabla de materias
        table_frame = ttk.LabelFrame(
            self.materias_frame,
            text="Registro de Materias",
            padding="10",
            style="Title.TLabelframe"
        )
        table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Crear Treeview
        self.materias_tree = ttk.Treeview(
            table_frame,
            columns=EXPECTED_COLUMNS['materias'],
            show='headings',
            height=15,
            style="Treeview"
        )

        # Configurar columnas
        column_widths = {
            'codigo': 100,
            'nombre': 300,
            'creditos': 100,
            'carreras': 400
        }

        for col in EXPECTED_COLUMNS['materias']:
            self.materias_tree.heading(col, text=col.capitalize(), command=lambda c=col: self.sort_treeview(c))
            width = column_widths.get(col, 150)
            self.materias_tree.column(col, anchor=tk.W, width=width, minwidth=width)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.materias_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.materias_tree.xview)
        self.materias_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Posicionar Treeview y Scrollbars
        self.materias_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        vsb.grid(row=0, column=1, sticky="ns", pady=5)
        hsb.grid(row=1, column=0, sticky="ew", padx=5)

        # Binding para selección
        self.materias_tree.bind('<<TreeviewSelect>>', lambda e: self.on_select(e, 'materias'))

    def create_profesores_widgets(self):
        # Frame para gestión de profesores
        self.prof_frame = ttk.LabelFrame(
            self.profesores_frame,
            text="Gestión de Profesores",
            padding="10",
            style="Title.TLabelframe"
        )
        self.prof_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.prof_frame.grid_columnconfigure(1, weight=1)
        
        # Frame para campos de entrada
        input_frame = ttk.Frame(self.prof_frame)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        input_frame.grid_columnconfigure(1, weight=1)
        
        # Campos de entrada para profesores
        self.nombre_prof_label = ttk.Label(input_frame, text="Nombre:", style="TLabel")
        self.nombre_prof_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        self.nombre_prof_entry = ttk.Entry(input_frame, width=30, style="TEntry")
        self.nombre_prof_entry.grid(row=0, column=1, sticky="ew", pady=2)

        self.licenciatura_label = ttk.Label(input_frame, text="Licenciatura:", style="TLabel")
        self.licenciatura_label.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
        self.licenciatura_entry = ttk.Entry(input_frame, width=30, style="TEntry")
        self.licenciatura_entry.grid(row=1, column=1, sticky="ew", pady=2)

        self.email_label = ttk.Label(input_frame, text="Email:", style="TLabel")
        self.email_label.grid(row=2, column=0, sticky="w", padx=(0, 5), pady=2)
        self.email_entry = ttk.Entry(input_frame, width=30, style="TEntry")
        self.email_entry.grid(row=2, column=1, sticky="ew", pady=2)

        # Frame para botones
        button_frame = ttk.Frame(self.prof_frame)
        button_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)

        # Botones CRUD para profesores
        self.add_profesor_button = ttk.Button(
            button_frame,
            text="Agregar",
            command=self.add_profesor,
            state=tk.DISABLED,
            style="Add.TButton",
            width=12
        )
        self.add_profesor_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        self.update_profesor_button = ttk.Button(
            button_frame,
            text="Actualizar",
            command=self.update_profesor,
            state=tk.DISABLED,
            style="Update.TButton",
            width=12
        )
        self.update_profesor_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.delete_profesor_button = ttk.Button(
            button_frame,
            text="Eliminar",
            command=self.delete_profesor,
            state=tk.DISABLED,
            style="Delete.TButton",
            width=12
        )
        self.delete_profesor_button.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        self.clear_profesor_button = ttk.Button(
            button_frame,
            text="Limpiar",
            command=self.clear_profesor_fields,
            style="Clear.TButton",
            width=12
        )
        self.clear_profesor_button.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Tabla de profesores
        self.create_treeview(self.profesores_frame, 'profesores')

    def create_consultas_widgets(self):
        # Frame para gestión de consultas
        self.consultas_control_frame = ttk.LabelFrame(
            self.consultas_frame,
            text="Consultas MongoDB",
            padding="10",
            style="Title.TLabelframe"
        )
        self.consultas_control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.consultas_control_frame.grid_columnconfigure(0, weight=1)  # Hacer que el frame sea responsivo
        
        # Frame para controles de consulta
        query_frame = ttk.Frame(self.consultas_control_frame)
        query_frame.grid(row=0, column=0, sticky="nsew")
        query_frame.grid_columnconfigure(1, weight=1)  # Hacer que el contenido se expanda
        
        # Combobox para seleccionar consulta
        self.consulta_label = ttk.Label(query_frame, text="Seleccionar Consulta:", style="TLabel")
        self.consulta_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        
        self.consulta_var = tk.StringVar()
        self.consulta_combo = ttk.Combobox(
            query_frame,
            textvariable=self.consulta_var,
            values=list(CONSULTAS.keys()),
            state="readonly"
        )
        self.consulta_combo.grid(row=0, column=1, sticky="ew", pady=2)
        self.consulta_combo.bind('<<ComboboxSelected>>', self.on_consulta_select)
        
        # Descripción de la consulta
        self.descripcion_label = ttk.Label(query_frame, text="Descripción:", style="TLabel")
        self.descripcion_label.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
        
        self.descripcion_text = ttk.Label(
            query_frame,
            text="Seleccione una consulta para ver su descripción",
            style="TLabel",
            wraplength=400,
            justify="left"  # Justificar el texto a la izquierda
        )
        self.descripcion_text.grid(row=1, column=1, sticky="ew", pady=2)
        
        # Visualización de la consulta en formato Compass
        self.consulta_compass_label = ttk.Label(query_frame, text="Consulta (formato Compass):", style="TLabel")
        self.consulta_compass_label.grid(row=2, column=0, sticky="w", padx=(0, 5), pady=2)
        
        self.consulta_compass_text = tk.Text(
            query_frame,
            height=3,
            wrap=tk.WORD,
            font=('Courier', 10)
        )
        self.consulta_compass_text.grid(row=2, column=1, sticky="ew", pady=2)
        
        # Frame para el botón (centrado y más compacto)
        button_frame = ttk.Frame(query_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=5)
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Botón para ejecutar consulta (más compacto)
        self.ejecutar_button = ttk.Button(
            button_frame,
            text="Ejecutar",  # Texto más corto
            command=self.ejecutar_consulta,
            state=tk.DISABLED,
            style="Connect.TButton",
            width=15  # Ancho fijo más pequeño
        )
        self.ejecutar_button.grid(row=0, column=0, pady=5)
        
        # Frame para resultados
        results_frame = ttk.LabelFrame(
            self.consultas_frame,
            text="Resultados",
            padding="10",
            style="Title.TLabelframe"
        )
        results_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview para resultados
        self.consultas_tree = ttk.Treeview(
            results_frame,
            columns=[],
            show='headings',
            height=15,
            style="Treeview"
        )
        
        # Scrollbars para resultados
        vsb = ttk.Scrollbar(
            results_frame,
            orient="vertical",
            command=self.consultas_tree.yview
        )
        hsb = ttk.Scrollbar(
            results_frame,
            orient="horizontal",
            command=self.consultas_tree.xview
        )
        self.consultas_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Posicionar Treeview y Scrollbars
        self.consultas_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        vsb.grid(row=0, column=1, sticky="ns", pady=5)
        hsb.grid(row=1, column=0, sticky="ew", padx=5)

    def on_consulta_select(self, event=None):
        """Manejar la selección de una consulta"""
        consulta_nombre = self.consulta_var.get()
        if consulta_nombre in CONSULTAS:
            consulta_info = CONSULTAS[consulta_nombre]
            self.descripcion_text.config(text=consulta_info["descripcion"])
            
            # Mostrar la consulta en formato Compass
            self.consulta_compass_text.delete(1.0, tk.END)
            
            # Formatear la consulta para Compass
            coleccion = consulta_info["coleccion"]
            consulta = consulta_info["consulta"]
            orden = consulta_info.get("orden", [])
            
            # Convertir la consulta a formato JSON para Compass
            import json
            consulta_json = json.dumps(consulta, indent=2, ensure_ascii=False)
            
            # Construir el texto de la consulta
            consulta_texto = f"db.{coleccion}.find({consulta_json})"
            
            # Agregar orden si existe
            if orden:
                orden_json = json.dumps(orden, indent=2, ensure_ascii=False)
                consulta_texto += f".sort({orden_json})"
                
            self.consulta_compass_text.insert(tk.END, consulta_texto)
            self.ejecutar_button.config(state=tk.NORMAL)

    def ejecutar_consulta(self):
        """Ejecutar la consulta seleccionada"""
        if self.db is None:
            messagebox.showwarning("No Conectado", "Por favor, conecta a MongoDB primero.")
            return
            
        try:
            # Obtener la consulta del campo de texto
            consulta_texto = self.consulta_compass_text.get(1.0, tk.END).strip()
            
            # Parsear la consulta
            import re
            # Patrón más flexible para detectar la consulta
            match = re.match(r"db\.(\w+)\.find\((.*?)\)(?:\s*\.sort\((.*?)\))?$", consulta_texto, re.DOTALL)
            if not match:
                messagebox.showerror("Error", "Formato de consulta inválido. Debe ser: db.coleccion.find({consulta}).sort([orden])")
                return
                
            coleccion_nombre, consulta_json, orden_json = match.groups()
            
            # Convertir JSON a diccionario
            import json
            try:
                # Manejar consulta vacía
                consulta = json.loads(consulta_json) if consulta_json and consulta_json.strip() else {}
                
                # Manejar orden vacío o None
                orden = None
                if orden_json and orden_json.strip():
                    try:
                        orden = json.loads(orden_json)
                    except json.JSONDecodeError:
                        # Si no es un JSON válido, intentar convertirlo a una lista de tuplas
                        orden_texto = orden_json.strip('[]').strip()
                        if orden_texto:
                            # Convertir "(campo, 1)" a [("campo", 1)]
                            orden = []
                            for orden_item in orden_texto.split(','):
                                orden_item = orden_item.strip()
                                if orden_item:
                                    # Extraer campo y dirección
                                    campo_match = re.match(r'\(?\s*"?(\w+)"?\s*,\s*([-+]?\d+)\s*\)?', orden_item)
                                    if campo_match:
                                        campo, direccion = campo_match.groups()
                                        orden.append((campo, int(direccion)))
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Formato JSON inválido en la consulta: {e}")
                return
                
            # Obtener la colección
            coleccion = self.db[coleccion_nombre]
            
            # Limpiar tabla de resultados
            for item in self.consultas_tree.get_children():
                self.consultas_tree.delete(item)
                
            # Configurar columnas dinámicamente
            self.consultas_tree["columns"] = []
            for col in self.consultas_tree["columns"]:
                self.consultas_tree.heading(col, text="")
                self.consultas_tree.column(col, width=0)
                
            # Ejecutar consulta
            if orden:
                resultados = list(coleccion.find(consulta).sort(orden))
            else:
                resultados = list(coleccion.find(consulta))
                
            if not resultados:
                messagebox.showinfo("Resultados", "La consulta no devolvió resultados.")
                return
                
            # Configurar columnas basadas en el primer resultado
            columnas = list(resultados[0].keys())
            columnas.remove("_id")  # Excluir el ID de MongoDB
            
            self.consultas_tree["columns"] = columnas
            for col in columnas:
                self.consultas_tree.heading(col, text=col.capitalize())
                self.consultas_tree.column(col, width=150, minwidth=100)
                
            # Insertar resultados
            for doc in resultados:
                valores = [str(doc.get(col, "")) for col in columnas]
                self.consultas_tree.insert("", tk.END, values=valores)
                
            messagebox.showinfo("Éxito", f"Consulta ejecutada. Se encontraron {len(resultados)} resultados.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar la consulta: {e}")

    def create_treeview(self, parent, section):
        # Frame para la tabla
        table_frame = ttk.LabelFrame(
            parent,
            text=f"Registro de {section.capitalize()}",
            padding="10",
            style="Title.TLabelframe"
        )
        table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Crear Treeview
        tree = ttk.Treeview(
            table_frame,
            columns=EXPECTED_COLUMNS[section],
            show='headings',
            height=15,
            style="Treeview"
        )

        # Configurar columnas con anchos específicos
        column_widths = {
            'estudiantes': {
                'nombre': 300,
                'matricula': 150,
                'carrera': 250
            },
            'materias': {
                'codigo': 100,
                'nombre': 300,
                'creditos': 100,
                'carreras': 400
            },
            'profesores': {
                'nombre': 300,
                'licenciatura': 250,
                'email': 250
            }
        }

        # Configurar columnas
        for col in EXPECTED_COLUMNS[section]:
            tree.heading(col, text=col.capitalize(), command=lambda c=col: self.sort_treeview(c))
            width = column_widths[section].get(col, 150)  # Ancho por defecto si no está especificado
            tree.column(col, anchor=tk.W, width=width, minwidth=width)

        # Scrollbars
        vsb = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )
        hsb = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree.xview
        )
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Posicionar Treeview y Scrollbars
        tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        vsb.grid(row=0, column=1, sticky="ns", pady=5)
        hsb.grid(row=1, column=0, sticky="ew", padx=5)

        # Binding para selección
        tree.bind('<<TreeviewSelect>>', lambda e: self.on_select(e, section))

        # Guardar referencia al treeview
        setattr(self, f'{section}_tree', tree)

    def filter_carreras(self, event=None):
        """Filtrar carreras basado en el texto ingresado"""
        search_term = self.carrera_var.get().lower()
        filtered_carreras = [carrera for carrera in CARRERAS if search_term in carrera.lower()]
        self.carrera_entry['values'] = filtered_carreras
        self.carrera_entry.event_generate('<Down>')

    def on_carrera_select(self, event=None):
        """Manejar la selección de una carrera"""
        selected = self.carrera_var.get()
        if selected in CARRERAS:
            self.carrera_entry.set(selected)

    def connect_mongo(self):
        self.status_label.config(text="Estado: Conectando...", foreground='#ffc107')
        self.root.update_idletasks()

        try:
            self.client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]

            # Habilitar botones para todas las secciones
            self.refresh_button.config(state=tk.NORMAL)
            self.add_student_button.config(state=tk.NORMAL)
            self.add_materia_button.config(state=tk.NORMAL)
            self.add_profesor_button.config(state=tk.NORMAL)
            
            # Cargar datos para todas las secciones
            for section in ['estudiantes', 'materias', 'profesores']:
                self.current_section = section
                self.collection = self.db[COLLECTIONS[section]]
                self.load_data()
            
            self.status_label.config(
                text=f"Estado: Conectado a {DATABASE_NAME}",
                foreground='#28a745'
            )
            messagebox.showinfo("Conexión Exitosa", "Conectado a MongoDB correctamente.")

        except Exception as e:
            self.status_label.config(text="Estado: Error de Conexión", foreground='#dc3545')
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a MongoDB.\nError: {e}")
            self.client = None
            self.db = None
            self.disable_buttons()

    def load_data(self):
        if self.db is None:
            messagebox.showwarning("No Conectado", "Por favor, conecta a MongoDB primero.")
            return

        try:
            self.status_label.config(text="Estado: Cargando datos...", foreground='#17a2b8')
            self.root.update_idletasks()

            # Obtener el árbol correspondiente a la sección actual
            tree = getattr(self, f'{self.current_section}_tree')

            # Limpiar tabla
            for item in tree.get_children():
                tree.delete(item)

            # Cargar datos
            collection = self.db[COLLECTIONS[self.current_section]]
            documents = list(collection.find())

            if not documents:
                messagebox.showinfo("Información", f"No hay {self.current_section} registrados.")
                self.status_label.config(
                    text=f"Estado: Conectado a {DATABASE_NAME}/{COLLECTIONS[self.current_section]} (Vacía)",
                    foreground='#28a745'
                )
                return

            # Insertar datos en la tabla
            for doc in documents:
                values = [str(doc.get(col, '')) for col in EXPECTED_COLUMNS[self.current_section]]
                tree.insert('', tk.END, values=values)

            self.status_label.config(
                text=f"Estado: Conectado ({len(documents)} {self.current_section})",
                foreground='#28a745'
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")
            self.status_label.config(text="Estado: Error al cargar", foreground='#dc3545')

    def add_alumno(self):
        if not self.validate_fields():
            return

        try:
            alumno_data = {
                "nombre": self.nombre_entry.get().strip(),
                "matricula": self.matricula_entry.get().strip(),
                "carrera": self.carrera_entry.get().strip()
            }

            # Verificar si la matrícula ya existe
            if self.db[COLLECTIONS['estudiantes']].find_one({"matricula": alumno_data["matricula"]}):
                messagebox.showerror("Error", "Ya existe un estudiante con esta matrícula.")
                return

            self.db[COLLECTIONS['estudiantes']].insert_one(alumno_data)
            messagebox.showinfo("Éxito", "Estudiante agregado correctamente.")
            self.clear_fields()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar estudiante: {e}")

    def update_alumno(self):
        if not self.selected_item or not self.validate_fields():
            return

        try:
            matricula = self.matricula_entry.get().strip()
            alumno_data = {
                "nombre": self.nombre_entry.get().strip(),
                "matricula": matricula,
                "carrera": self.carrera_entry.get().strip()
            }

            # Verificar si la nueva matrícula ya existe (si se cambió)
            existing = self.db[COLLECTIONS['estudiantes']].find_one({"matricula": matricula})
            if existing and str(existing.get("_id")) != str(self.selected_item):
                messagebox.showerror("Error", "Ya existe un estudiante con esta matrícula.")
                return

            self.db[COLLECTIONS['estudiantes']].update_one(
                {"_id": self.selected_item},
                {"$set": alumno_data}
            )
            messagebox.showinfo("Éxito", "Estudiante actualizado correctamente.")
            self.clear_fields()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar estudiante: {e}")

    def delete_alumno(self):
        if not self.selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un estudiante para eliminar.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este estudiante?"):
            try:
                self.db[COLLECTIONS['estudiantes']].delete_one({"_id": self.selected_item})
                messagebox.showinfo("Éxito", "Estudiante eliminado correctamente.")
                self.clear_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar estudiante: {e}")

    def validate_fields(self):
        nombre = self.nombre_entry.get().strip()
        matricula = self.matricula_entry.get().strip()
        carrera = self.carrera_entry.get().strip()

        if not all([nombre, matricula, carrera]):
            messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return False

        # Validar formato de matrícula (ejemplo: zS21002379)
        if not re.match(r'^zS\d{8}$', matricula):
            messagebox.showerror("Error", "Formato de matrícula inválido. Debe ser 'zS' seguido de 8 dígitos.")
            return False

        return True

    def clear_fields(self):
        self.nombre_entry.delete(0, tk.END)
        self.matricula_entry.delete(0, tk.END)
        self.carrera_entry.delete(0, tk.END)
        self.selected_item = None
        self.update_student_button.config(state=tk.DISABLED)
        self.delete_student_button.config(state=tk.DISABLED)

    def on_select(self, event, section):
        tree = getattr(self, f'{section}_tree')
        selected_items = tree.selection()
        if not selected_items:
            return

        item = selected_items[0]
        values = tree.item(item)['values']
        
        # Obtener el ID del documento seleccionado
        if section == 'estudiantes':
            doc = self.db[COLLECTIONS['estudiantes']].find_one({"matricula": values[1]})
            if doc:
                self.selected_item = doc["_id"]
                self.nombre_entry.delete(0, tk.END)
                self.nombre_entry.insert(0, values[0])
                self.matricula_entry.delete(0, tk.END)
                self.matricula_entry.insert(0, values[1])
                self.carrera_var.set(values[2])
                self.update_student_button.config(state=tk.NORMAL)
                self.delete_student_button.config(state=tk.NORMAL)
        elif section == 'materias':
            try:
                # Convertir el código a string para asegurar una comparación consistente
                codigo = str(values[0]).strip()
                doc = self.db[COLLECTIONS['materias']].find_one({"codigo": codigo})
                
                if doc:
                    self.selected_item = doc["_id"]
                    self.codigo_entry.delete(0, tk.END)
                    self.codigo_entry.insert(0, codigo)
                    self.nombre_materia_entry.delete(0, tk.END)
                    self.nombre_materia_entry.insert(0, values[1])
                    self.creditos_entry.delete(0, tk.END)
                    self.creditos_entry.insert(0, values[2])
                    
                    # Obtener las carreras del documento
                    carreras = doc.get("carreras", [])
                    
                    # Actualizar los checkboxes
                    for carrera, var in self.carreras_vars.items():
                        var.set(carrera in carreras)
                    
                    self.update_materia_button.config(state=tk.NORMAL)
                    self.delete_materia_button.config(state=tk.NORMAL)
                else:
                    messagebox.showwarning("Advertencia", f"No se encontró la materia con código {codigo}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al seleccionar materia: {e}")
        elif section == 'profesores':
            doc = self.db[COLLECTIONS['profesores']].find_one({"email": values[2]})
            if doc:
                self.selected_item = doc["_id"]
                self.nombre_prof_entry.delete(0, tk.END)
                self.nombre_prof_entry.insert(0, values[0])
                self.licenciatura_entry.delete(0, tk.END)
                self.licenciatura_entry.insert(0, values[1])
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, values[2])
                self.update_profesor_button.config(state=tk.NORMAL)
                self.delete_profesor_button.config(state=tk.NORMAL)

    def sort_treeview(self, col):
        """Ordenar la tabla por la columna seleccionada"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort()
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

    def disable_buttons(self):
        self.refresh_button.config(state=tk.DISABLED)
        self.add_student_button.config(state=tk.DISABLED)
        self.update_student_button.config(state=tk.DISABLED)
        self.delete_student_button.config(state=tk.DISABLED)
        self.add_materia_button.config(state=tk.DISABLED)
        self.update_materia_button.config(state=tk.DISABLED)
        self.delete_materia_button.config(state=tk.DISABLED)
        self.add_profesor_button.config(state=tk.DISABLED)
        self.update_profesor_button.config(state=tk.DISABLED)
        self.delete_profesor_button.config(state=tk.DISABLED)

    def show_help(self):
        help_text = """
Sistema de Gestión de Estudiantes - FIEE

Instrucciones de Uso:

1. Conexión
   • Conectar: Inicia la conexión con MongoDB
   • Refrescar: Actualiza los datos mostrados

2. Gestión de Estudiantes
   • Agregar: Ingresa datos y presiona "Agregar"
   • Actualizar: Selecciona, modifica y presiona "Actualizar"
   • Eliminar: Selecciona y presiona "Eliminar"
   • Limpiar: Borra todos los campos

3. Formato de Matrícula
   • Estructura: zS + 8 dígitos
   • Ejemplo: zS21002379

4. Estados
   • 🔴 Rojo: Sin conexión
   • 🟢 Verde: Conectado
   • 🔵 Azul: Cargando
        """
        messagebox.showinfo("Ayuda del Sistema", help_text)

    def show_about(self):
        about_text = """
        Sistema de Gestión de Estudiantes - FIE
        
        Versión 2.0
        
        Desarrollado por: Michell Alexis Policarpio Moran
        Matrícula: zS21002379
        Materia: Base de Datos y en la Nube
        Profesora: Primavera Lucho Arguelles
        Facultad de Ingeniería Eléctrica y Electrónica
        
        © 2024 Todos los derechos reservados
        """
        messagebox.showinfo("Acerca de", about_text)

    def on_closing(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que deseas salir?"):
            if self.client:
                self.client.close()
            self.root.destroy()

    def add_materia(self):
        if not self.validate_materia_fields():
            return

        try:
            # Obtener las carreras seleccionadas
            carreras_seleccionadas = [
                carrera for carrera, var in self.carreras_vars.items()
                if var.get()
            ]

            if not carreras_seleccionadas:
                messagebox.showerror("Error", "Debe seleccionar al menos una carrera.")
                return

            materia_data = {
                "codigo": self.codigo_entry.get().strip(),
                "nombre": self.nombre_materia_entry.get().strip(),
                "creditos": int(self.creditos_entry.get().strip()),
                "carreras": carreras_seleccionadas
            }

            # Verificar si el código ya existe
            if self.db[COLLECTIONS['materias']].find_one({"codigo": materia_data["codigo"]}):
                messagebox.showerror("Error", "Ya existe una materia con este código.")
                return

            self.db[COLLECTIONS['materias']].insert_one(materia_data)
            messagebox.showinfo("Éxito", "Materia agregada correctamente.")
            self.clear_materia_fields()
            self.load_data()

        except ValueError:
            messagebox.showerror("Error", "El campo créditos debe ser un número.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar materia: {e}")

    def update_materia(self):
        if not self.selected_item or not self.validate_materia_fields():
            return

        try:
            # Obtener las carreras seleccionadas
            carreras_seleccionadas = [
                carrera for carrera, var in self.carreras_vars.items()
                if var.get()
            ]

            if not carreras_seleccionadas:
                messagebox.showerror("Error", "Debe seleccionar al menos una carrera.")
                return

            codigo = self.codigo_entry.get().strip()
            materia_data = {
                "codigo": codigo,
                "nombre": self.nombre_materia_entry.get().strip(),
                "creditos": int(self.creditos_entry.get().strip()),
                "carreras": carreras_seleccionadas
            }

            # Verificar si el nuevo código ya existe (si se cambió)
            existing = self.db[COLLECTIONS['materias']].find_one({"codigo": codigo})
            if existing and str(existing.get("_id")) != str(self.selected_item):
                messagebox.showerror("Error", "Ya existe una materia con este código.")
                return

            self.db[COLLECTIONS['materias']].update_one(
                {"_id": self.selected_item},
                {"$set": materia_data}
            )
            messagebox.showinfo("Éxito", "Materia actualizada correctamente.")
            self.clear_materia_fields()
            self.load_data()

        except ValueError:
            messagebox.showerror("Error", "El campo créditos debe ser un número.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar materia: {e}")

    def validate_materia_fields(self):
        codigo = self.codigo_entry.get().strip()
        nombre = self.nombre_materia_entry.get().strip()
        creditos = self.creditos_entry.get().strip()

        if not all([codigo, nombre, creditos]):
            messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return False

        try:
            int(creditos)
        except ValueError:
            messagebox.showerror("Error", "El campo créditos debe ser un número.")
            return False

        return True

    def delete_materia(self):
        if not self.selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una materia para eliminar.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar esta materia?"):
            try:
                self.db[COLLECTIONS['materias']].delete_one({"_id": self.selected_item})
                messagebox.showinfo("Éxito", "Materia eliminada correctamente.")
                self.clear_materia_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar materia: {e}")

    def clear_materia_fields(self):
        self.codigo_entry.delete(0, tk.END)
        self.nombre_materia_entry.delete(0, tk.END)
        self.creditos_entry.delete(0, tk.END)
        # Desmarcar todos los checkboxes
        for var in self.carreras_vars.values():
            var.set(False)
        self.selected_item = None
        self.update_materia_button.config(state=tk.DISABLED)
        self.delete_materia_button.config(state=tk.DISABLED)

    def add_profesor(self):
        if not self.validate_profesor_fields():
            return

        try:
            profesor_data = {
                "nombre": self.nombre_prof_entry.get().strip(),
                "licenciatura": self.licenciatura_entry.get().strip(),
                "email": self.email_entry.get().strip()
            }

            # Verificar si el email ya existe
            if self.db[COLLECTIONS['profesores']].find_one({"email": profesor_data["email"]}):
                messagebox.showerror("Error", "Ya existe un profesor con este email.")
                return

            self.db[COLLECTIONS['profesores']].insert_one(profesor_data)
            messagebox.showinfo("Éxito", "Profesor agregado correctamente.")
            self.clear_profesor_fields()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar profesor: {e}")

    def update_profesor(self):
        if not self.selected_item or not self.validate_profesor_fields():
            return

        try:
            email = self.email_entry.get().strip()
            profesor_data = {
                "nombre": self.nombre_prof_entry.get().strip(),
                "licenciatura": self.licenciatura_entry.get().strip(),
                "email": email
            }

            # Verificar si el nuevo email ya existe (si se cambió)
            existing = self.db[COLLECTIONS['profesores']].find_one({"email": email})
            if existing and str(existing.get("_id")) != str(self.selected_item):
                messagebox.showerror("Error", "Ya existe un profesor con este email.")
                return

            self.db[COLLECTIONS['profesores']].update_one(
                {"_id": self.selected_item},
                {"$set": profesor_data}
            )
            messagebox.showinfo("Éxito", "Profesor actualizado correctamente.")
            self.clear_profesor_fields()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar profesor: {e}")

    def delete_profesor(self):
        if not self.selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un profesor para eliminar.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este profesor?"):
            try:
                self.db[COLLECTIONS['profesores']].delete_one({"_id": self.selected_item})
                messagebox.showinfo("Éxito", "Profesor eliminado correctamente.")
                self.clear_profesor_fields()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar profesor: {e}")

    def validate_profesor_fields(self):
        nombre = self.nombre_prof_entry.get().strip()
        licenciatura = self.licenciatura_entry.get().strip()
        email = self.email_entry.get().strip()

        if not all([nombre, licenciatura, email]):
            messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return False

        # Validar formato de email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Error", "Formato de email inválido.")
            return False

        return True

    def clear_profesor_fields(self):
        self.nombre_prof_entry.delete(0, tk.END)
        self.licenciatura_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.selected_item = None
        self.update_profesor_button.config(state=tk.DISABLED)
        self.delete_profesor_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = MongoViewerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()