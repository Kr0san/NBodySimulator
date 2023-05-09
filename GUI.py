import sys
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QApplication, QLineEdit, QLabel, QGridLayout, QGroupBox,\
     QPushButton, QComboBox, QVBoxLayout, QScrollArea, QSpacerItem, QSizePolicy, QRadioButton, QStatusBar
from PyQt6.QtGui import QIntValidator, QDoubleValidator, QAction
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import axes3d
from NBodySimulator.ColorButton import ColorButton
from NBodySimulator.NBodySimulation import NBodySimulation
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import seaborn as sns
sns.set_style("white")


class MainWindow(QMainWindow):
    """
    Main window GUI class defining the application. It consists of a settings panel on the left and the simulation plot
    on the right. Buttons enable user to add/remove additional objects and Simulate button kicks off NBody simulation
    for the respective number of bodies added. There's Import menu allowing users to import some predefined bodies like
    inner solar system.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('NBody Simulator')
        self.setMinimumSize(400, 600)
        int_validator = QIntValidator()
        int_validator.setBottom(0)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        import_bar = self.menuBar()
        import_menu = import_bar.addMenu('&Import')

        import_action1 = QAction('Inner solar system', self)
        import_action1.setStatusTip('Import coordinate settings for the inner solar system')
        import_action1.triggered.connect(lambda: self.import_template(selection='Inner Solar System'))

        import_action2 = QAction('Sun, Earth, Mars', self)
        import_action2.setStatusTip('Import coordinate settings for the Sun, Earth and Mars system')
        import_action2.triggered.connect(lambda: self.import_template(selection='Sun, Earth, Mars'))

        import_menu.addActions([import_action1, import_action2])

        self.base_settings_box = QGroupBox('Base Settings')
        self.base_settings_layout = QGridLayout()
        self.steps_label = QLabel('Time Steps:')
        self.steps_label.setStatusTip('Number of time steps for numerical simulation.')
        self.steps_edit = QLineEdit('10000')
        self.steps_edit.setValidator(int_validator)
        self.period_label = QLabel('Time Periods:')
        self.period_label.setStatusTip('Number of orbital years. Larger orbits will require higher input.')
        self.period_edit = QLineEdit('50')
        self.period_edit.setValidator(int_validator)
        self.integrators_label = QLabel('Integrator:')
        self.integrators_label.setStatusTip('Choice of numerical integrator. '
                                            'Simulation results will vary depending on the selection.')
        self.integrators = QComboBox()
        self.integrators.addItems(['IAS15', 'WHFast', 'BS', 'Mercurius', 'Leapfrog', 'None'])
        self.center_radiobutton_label = QLabel('Center of Frame:')
        self.center_radiobutton_label.setStatusTip('Moves all particles in the simulation to a center of the '
                                                   'momentum frame. In that frame, the center of mass is at '
                                                   'the origin and does not move.')
        self.center_radiobutton = QRadioButton()
        self.center_radiobutton.setChecked(True)
        self.add_particle_button = QPushButton('Add Object')
        self.add_particle_button.setStatusTip('Adds a new settings box for a new object.')
        self.add_particle_button.clicked.connect(lambda: self.add_object_layout())
        self.delete_particle_button = QPushButton('Delete Object')
        self.delete_particle_button.setStatusTip('Deletes the last object with its settings.')
        self.delete_particle_button.clicked.connect(self.remove_object_layout)
        self.base_settings_layout.addWidget(self.steps_label, 0, 0)
        self.base_settings_layout.addWidget(self.steps_edit, 0, 1)
        self.base_settings_layout.addWidget(self.period_label, 1, 0)
        self.base_settings_layout.addWidget(self.period_edit, 1, 1)
        self.base_settings_layout.addWidget(self.integrators_label, 2, 0)
        self.base_settings_layout.addWidget(self.integrators, 2, 1)
        self.base_settings_layout.addWidget(self.center_radiobutton_label, 3, 0)
        self.base_settings_layout.addWidget(self.center_radiobutton, 3, 1)
        self.base_settings_layout.addWidget(self.add_particle_button, 4, 0)
        self.base_settings_layout.addWidget(self.delete_particle_button, 4, 1)
        self.base_settings_box.setLayout(self.base_settings_layout)

        # self.object_settings_box = QGroupBox('Object Settings')
        # self.object_settings_layout = QVBoxLayout()
        # self.object_settings_box.setLayout(self.object_settings_layout)

        self.object_scroll_area = QScrollArea()
        self.object_scroll_area.setWidgetResizable(True)
        self.object_scroll_area_widget = QWidget()
        self.object_scroll_area_layout = QVBoxLayout(self.object_scroll_area_widget)
        self.object_scroll_area_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.object_scroll_area.setWidget(self.object_scroll_area_widget)

        self.run_simulation_button = QPushButton('Run Simulation')
        self.run_simulation_button.setStatusTip('Run NBody simulation')
        self.run_simulation_button.clicked.connect(self.trigger_simulation)

        all_settings_container = QWidget()
        all_settings_layout = QVBoxLayout()
        all_settings_layout.addWidget(self.base_settings_box)
        all_settings_layout.addWidget(self.object_scroll_area)
        all_settings_layout.addWidget(self.run_simulation_button)
        all_settings_container.setLayout(all_settings_layout)

        self.fig = Figure()
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        toolbar = NavigationToolbar(self.canvas, self)

        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addWidget(toolbar)
        canvas_widget.setLayout(canvas_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(all_settings_container, stretch=2)
        main_layout.addWidget(canvas_widget, stretch=4)
        main_widget_container = QWidget()
        main_widget_container.setLayout(main_layout)
        self.setCentralWidget(main_widget_container)

    def add_object_layout(self, star_name='Star', mass=1.0, x=0, y=0, z=0, vx=0, vy=0, vz=0):
        """
        Creates a layout with stellar object settings.

        Parameters
        ----------
        star_name   :   str
            Name of the stellar object.
        mass        :   float
            Mass of the stellar object in solar masses.
        x           :   float
            Positional coordinate of x.
        y           :   float
            Positional coordinate of y.
        z           :   float
            Positional coordinate of z.
        vx          :   float
            Velocity of x coordinate.
        vy          :   float
            Velocity of y coordinate.
        vz          :   float
            Velocity of z coordinate.
        """
        count = self.object_scroll_area_layout.count() - 1
        object_group_box = QGroupBox('Stellar Object ' + str(count + 1), self.object_scroll_area_widget)
        self.object_scroll_area_layout.insertWidget(count, object_group_box)

        object_layout = QHBoxLayout()
        object_label = QLabel('Name | Mass')
        object_name = QLineEdit()
        object_name.setText(star_name)
        object_name.setObjectName('Object')
        object_mass = QLineEdit()
        object_mass.setObjectName('Mass')
        object_mass.setText(str(mass))
        object_mass.setValidator(QDoubleValidator(0.0, 999.0, 20))
        object_color = ColorButton()
        object_color.setObjectName('Color')
        object_layout.addWidget(object_label)
        object_layout.addWidget(object_name)
        object_layout.addWidget(object_mass)
        object_layout.addWidget(object_color)

        coordinates_layout = QGridLayout()
        for i, n in enumerate(['X', 'Y', 'Z']):
            coordinates_label = QLabel(n)
            coordinates_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
            coordinates_layout.addWidget(coordinates_label, 0, i+1)
        for i, n in enumerate(['Position', 'Velocity']):
            value_label = QLabel(n)
            value_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            coordinates_layout.addWidget(value_label, i+1, 0)

        positions = [(i, j) for i in range(2) for j in range(3)]
        coordinate_params = [[x, y, z], [vx, vy, vz]]
        for i, n in positions:
            coordinate_value = QLineEdit()
            coordinate_value.setObjectName('Coordinate')
            coordinate_value.setText(str(coordinate_params[i][n]))
            coordinate_value.setValidator(QDoubleValidator(-999.0, 999.0, 20))
            coordinates_layout.addWidget(coordinate_value, i + 1, n+1)

        combined_layout = QVBoxLayout()
        combined_layout.addLayout(object_layout)
        combined_layout.addLayout(coordinates_layout)
        object_group_box.setLayout(combined_layout)

    def remove_object_layout(self):
        count = self.object_scroll_area_layout.count()
        if count == 1:
            return
        item = self.object_scroll_area_layout.itemAt(count - 2)
        widget = item.widget()
        widget.deleteLater()

    def trigger_simulation(self):
        object_names = []
        object_params = []
        object_colors = []

        group_boxes = self.object_scroll_area_widget.findChildren(QGroupBox)
        for box in group_boxes:
            children = box.children()
            params = []
            object_params.append(params)
            for n in children:
                if isinstance(n, QLineEdit):
                    if n.objectName() == 'Object':
                        object_names.append(n.text())
                    if n.objectName() in ('Mass', 'Coordinate'):
                        params.append(float(n.text()))
                if isinstance(n, ColorButton):
                    object_colors.append(n.color())

        steps = int(self.steps_edit.text())
        periods = int(self.period_edit.text())
        integrator = self.integrators.currentText()

        simulation = NBodySimulation(duration=periods, steps=steps, integrator=integrator,
                                     center=self.center_radiobutton.isChecked())
        for i in object_params:
            simulation.add_particle(*i)

        x, y, z = simulation.simulation()
        self.plot_simulation(x, y, z, simulation.objects, object_names, object_colors)

    def plot_simulation(self, x_array, y_array, z_array, objects, object_names, object_colors):
        self.ax.clear()
        for i, c in zip(range(objects), object_colors):
            self.ax.plot(x_array[i, :], y_array[i, :], z_array[i, :], c=c)
        self.ax.legend(object_names, loc='upper left')  # , bbox_to_anchor=(-0.3, 1.15)
        self.canvas.draw()

    def import_template(self, selection='Inner Solar System'):

        self.delete_all_objects()

        if selection == 'Inner Solar System':
            self.add_object_layout('Sun', mass=0.9999999999950272, x=-0.00890210412706074, y=-0.0007758899444505249,
                                   z=0.00021366342527047113, vx=0.00012285790850338033, vy=-0.0005003466219408352,
                                   vz=1.2221812993419404e-06)
            self.add_object_layout('Mercury', mass=1.6601208254808336e-07, x=-0.22315977761416272, y=0.24730989644698195,
                                   z=0.04013999600464757, vx=-1.5687025317960195, vy=-1.0045716938695024,
                                   vz=0.06184822134989955)
            self.add_object_layout('Venus', mass=2.447838287784771e-06, x=-0.351559999949463, y=0.6301825177996836,
                                   z=0.028648566009433794, vx=-1.037125876769079, vy=-0.5681607665275994,
                                   vz=0.05205962596614349)
            self.add_object_layout('Earth', mass=3.0404326489511185e-06, x=-0.9546368779826236, y=-0.3302360750379641,
                                   z=0.00023607966526552235, vx=0.3128945163587852, vy=-0.948783682591208,
                                   vz=4.910243972132018e-05)
            self.add_object_layout('Mars', 3.2271560828978514e-07, x=-1.1493486927142729, y=1.194646916419061,
                                   z=0.053242123669011245, vx=-0.5577910043907098, vy=-0.4927482311008652,
                                   vz=0.003370059888074412)

        if selection == 'Sun, Earth, Mars':
            self.add_object_layout('Sun', mass=0.9999999999950272, x=-0.00890210412706074, y=-0.0007758899444505249,
                                   z=0.00021366342527047113, vx=0.00012285790850338033, vy=-0.0005003466219408352,
                                   vz=1.2221812993419404e-06)
            self.add_object_layout('Earth', mass=3.0404326489511185e-06, x=-0.9546368779826236, y=-0.3302360750379641,
                                   z=0.00023607966526552235, vx=0.3128945163587852, vy=-0.948783682591208,
                                   vz=4.910243972132018e-05)
            self.add_object_layout('Mars', 3.2271560828978514e-07, x=-1.1493486927142729, y=1.194646916419061,
                                   z=0.053242123669011245, vx=-0.5577910043907098, vy=-0.4927482311008652,
                                   vz=0.003370059888074412)

    def delete_all_objects(self):
        while self.object_scroll_area_layout.count() > 1:
            child = self.object_scroll_area_layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.delete_all_objects()

    def placeholder(self):
        print(self.center_radiobutton.isChecked())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    app.exec()
