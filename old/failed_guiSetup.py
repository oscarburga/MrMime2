
def setupMediaButtons(self, design):
    # Use video
    ## Open video button
    useVideo = QPushButton("Use Video")
    useVideo.clicked.connect(self.open_video)
    # self.video = Video()
    design.addWidget(useVideo, 0, 0, 1, 0)

    # Use webcam
    ## Open webcam button
    useWebCam = QPushButton("Use WebCam")
    useWebCam.clicked.connect(self.open_web_cam)
    # WebCam = WebCam()
    design.addWidget(useWebCam, 1, 0, 1, 0)
        
    # Use image
    ## Open image button
    useImage = QPushButton("Use Image")
    useImage.clicked.connect(self.openImage)
    # image = Image()
    design.addWidget(useImage, 2, 0, 1, 0)

def setupNaoPanel(self, design):
    # NAO Layout
    naoLayoutWidget = QWidget(self.widget)
    naoLayoutWidget.setStyleSheet("background-color:#60e0e0e0;")
    naoLayout = QGridLayout(naoLayoutWidget)
    ## Title
    title = QLabel()
    title.setFont(QFont('Arial', 25, QFont.Bold))
    title.setStyleSheet("color : black; ")
    title.setText("NAO Settings")
    naoLayout.addWidget(title, 0, 0)
    ##  Hostname label
    hostname_label = QLabel()
    hostname_label.setFont(QFont('Arial', 15, QFont.Bold))
    hostname_label.setStyleSheet("color : black; ")
    hostname_label.setText("Hostname")
    naoLayout.addWidget(hostname_label, 1, 0)
    ##  Hostname input
    hostname_input = QLineEdit()
    hostname_input.setPlaceholderText('Insert Hostname')
    naoLayout.addWidget(hostname_input, 1, 1)
    ##  Port label
    port_label = QLabel()
    port_label.setFont(QFont('Arial', 15, QFont.Bold))
    port_label.setStyleSheet("color : black; ")
    port_label.setText("Port")
    naoLayout.addWidget(port_label, 2, 0)
    ##  Port input
    port_input = QLineEdit()
    port_input.setPlaceholderText('Insert Port')
    naoLayout.addWidget(port_input, 2, 1)
    ## Connect button
    connect = QPushButton("Connect")
    naoLayout.addWidget(connect, 3, 0, 1, 0)
    ## Connection state
    connected = False
    connection = QLabel()
    connection.setPixmap(QPixmap('icon2.jpg').scaled(50, 50, Qt.KeepAspectRatio))
    naoLayout.addWidget(connection, 4, 0)
    connection_text = QLabel()
    connection_text.setFont(QFont('Arial', 15, QFont.Bold))
    connection_text.setStyleSheet("color : black; ")
    connection_text.setText("Not Connected")
    connect.clicked.connect(self.update_connection)
    naoLayout.addWidget(connection_text, 4, 1)
    design.addWidget(naoLayoutWidget, 3, 1)