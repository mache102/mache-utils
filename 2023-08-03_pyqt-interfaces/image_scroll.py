import numpy as np 
import os
import sys
import time

from tqdm import tqdm

from PyQt5.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, QPushButton, QMenu, QAction
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

PREVIEW_IMAGE_WIDTH = 250
DISPLAY_IMAGE_DEFAULT_WIDTH = 600 

class BetterQLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.colorDict = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "gray": (128, 128, 128),
            "light_gray": (192, 192, 192),
            "light_gray_2": (224, 224, 224),
            "light_gray_3": (240, 240, 240),
            "light_gray_4": (248, 248, 248),
            "dark_gray": (64, 64, 64),
            "dark_gray_2": (32, 32, 32),
            "dark_gray_3": (16, 16, 16),
            "dark_gray_4": (8, 8, 8),
        }

        self.styles = {

        }

    def updateStyleSheet(self):
        self.styleSheet = ""
        for k, v in self.styles.items():
            self.styleSheet += "{}: {}; ".format(k, v)
        
        self.setStyleSheet(self.styleSheet)

    def setBg(self, color="white"):
        """
        Set background image of the label
        """

        if isinstance(color, tuple):
            self.styles["background-color"] = "rgb({},{},{})".format(*color)
            self.updateStyleSheet()
            # self.setStyleSheet("background-color: rgb({},{},{});".format(*color))

        elif color in self.colorDict:
            self.styles["background-color"] = "rgb({},{},{})".format(*self.colorDict[color])
            self.updateStyleSheet()
            # self.setStyleSheet("background-color: rgb({},{},{});".format(*self.colorDict[color]))

        else: raise ValueError("Invalid color name: {}".format(color))

    def setContentsMargins(self, *args):
        if len(args) == 4:
            super().setContentsMargins(*args)
        elif len(args) == 3:
            raise ValueError("setContentsMargins expects 1, 2, or 4 arguments")
        elif len(args) == 2:
            super().setContentsMargins(args[1], args[0], args[1], args[0])
        elif len(args) == 1:
            super().setContentsMargins(args[0], args[0], args[0], args[0])

    def setFontSize(self, size):
        # append to stylesheet instead of setting
        # this way, we don't overwrite any other styles

        self.styles["font-size"] = "{}px".format(size)
        self.updateStyleSheet()

    def setBorder(self, width=1, color="black"):
        if isinstance(color, tuple):
            self.styles["border"] = "{}px solid rgb({},{},{})".format(width, *color)
            self.updateStyleSheet()

        elif color in self.colorDict:
            self.styles["border"] = "{}px solid rgb({},{},{})".format(width, *self.colorDict[color])
            self.updateStyleSheet()

        else: raise ValueError("Invalid color name: {}".format(color))


class ScrollbarWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        with open(image_path, 'rb') as f:
            image_data = f.read()

        image_name = image_path.split('/')[-1]

        # Convert the image_data to a QPixmap for the preview image
        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaledToWidth(PREVIEW_IMAGE_WIDTH)  # Set the width of the preview image

        # Create labels for the image and its name
        self.preview_image = BetterQLabel()
        self.preview_image.setPixmap(pixmap)
        self.preview_image.setContentsMargins(5)
        self.preview_image.setBg(color="white")

        self.name = BetterQLabel(image_name)
        self.name.setBg(color="white")
        self.name.setContentsMargins(5, 0)
        self.name.setBorder(color="black", width=1)
        self.name.setFixedWidth(PREVIEW_IMAGE_WIDTH)
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setFontSize(20)


        # Layout manager to arrange the image and caption vertically
        layout = QVBoxLayout()
        layout.addWidget(self.preview_image, alignment=Qt.AlignHCenter)
        layout.addWidget(self.name, alignment=Qt.AlignHCenter)

        self.setLayout(layout)

class HeaderWidget(QWidget):
    # Create a custom signal for the "Select All" action
    select_all_triggered = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Create a horizontal layout for the header widget
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # List of dropdown names and their actions
        dropdowns = [
            {
                "name": "File", 
                "actions": [
                    {
                        "action_name": "Open",
                        "quick": "Ctrl+O",
                        "connect": None,
                    },

                    {
                        "action_name": "Save",
                        "quick": "Ctrl+S",
                        "connect": None,
                    },

                    {
                        "action_name": "Save As",
                        "quick": None,
                        "connect": None,
                    },

                    {
                        "action_name": "Close",
                        "quick": "Ctrl+W",
                        "connect": None,
                    },
                ]
            },

            {
                "name": "Edit",
                "actions": [
                    {
                        "action_name": "Undo",
                        "quick": "Ctrl+Z",
                        "connect": None,
                    },

                    {
                        "action_name": "Redo",
                        "quick": "Ctrl+Y",
                        "connect": None,
                    },

                    {
                        "action_name": "Cut",
                        "quick": "Ctrl+X",
                        "connect": None,
                    },

                    {
                        "action_name": "Copy",
                        "quick": "Ctrl+C",
                        "connect": None,
                    },

                    {
                        "action_name": "Paste",
                        "quick": "Ctrl+V",
                        "connect": None,
                    },
                ]
                
            },

            {
                "name": "Selection",
                "actions": [
                    {
                        "action_name": "Select All",
                        "quick": "Ctrl+A",
                        "connect": self.sel_all_fileItems,
                    },

                    {
                        "action_name": "Clear Selection",
                        "quick": None,
                        "connect": None,
                    },
                ]
            },

            {
                "name": "View",
                "actions": [
                    {
                        "action_name": "Zoom In",
                        "quick": "Ctrl++",
                        "connect": None,
                    },

                    {
                        "action_name": "Zoom Out",
                        "quick": "Ctrl+-",
                        "connect": None,
                    },

                    {
                        "action_name": "Actual Size",
                        "quick": "Ctrl+0",
                        "connect": None,
                    },
                ]
            },
            
            {
                "name": "Help",
                "actions": [
                    {
                        "action_name": "Help Contents",
                        "quick": None,
                        "connect": None,
                    },

                    {
                        "action_name": "About",
                        "quick": None,
                        "connect": None,
                    },
                ]
            }, 

            {
                "name": "Settings",
                "actions": [
                    {
                        "action_name": "Preferences",
                        "quick": None,
                        "connect": None,
                    },

                    {
                        "action_name": "Options",
                        "quick": None,
                        "connect": None,
                    },
                ]
            },
        ]

        for dropdown in dropdowns:
            # Create a QPushButton for each dropdown
            dropdown_button = QPushButton(dropdown["name"])
            layout.addWidget(dropdown_button)

            # Create a QMenu for the dropdown
            dropdown_menu = QMenu(self)

            # Add actions to the dropdown menu
            for action in dropdown["actions"]:
                if action["quick"]:
                    curr_action = QAction(action["action_name"], self, shortcut=action["quick"])
                    if action["connect"]:
                        curr_action.triggered.connect(action["connect"])
                else:
                    curr_action = action["action_name"]
                dropdown_menu.addAction(curr_action)

            # # For "Selection" dropdown, add a clickable action with keyboard shortcut ctrl+A
            # if dropdown_name == "Selection":
            #     select_all_action = QAction("Select All", self, shortcut="Ctrl+A")
            #     select_all_action.triggered.connect(self.sel_all_fileItems)
            #     dropdown_menu.addAction(select_all_action)

            # Set the dropdown menu for the dropdown button
            dropdown_button.setMenu(dropdown_menu)

    def sel_all_fileItems(self):
        # Emit the custom signal when the "Select All" action is triggered
        self.select_all_triggered.emit()


class RemoteCameraInterface(QWidget):
    def __init__(self):
        super().__init__()

        # Set default window size
        self.setGeometry(100, 100, 1280, 720)

        self.fileItems = []
        self.curr_fileIdxs = []
        self.prev_fileIdxs = []

        self.header = HeaderWidget()
        self.header.select_all_triggered.connect(self.sel_all_fileItems)


        # Create a file_item_ area to contain the preview images and captions
        self.file_item_area = QScrollArea()
        self.file_item_area.setWidgetResizable(True)
        self.file_item_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Set the fixed width for the file_item_area
        self.file_item_area.setFixedWidth(PREVIEW_IMAGE_WIDTH+100)

        # Create a container widget to hold the preview images and captions
        self.file_item_area_content = QWidget(self.file_item_area)
        self.file_item_area.setWidget(self.file_item_area_content)

        # Layout manager to arrange the images and captions vertically
        self.file_item_area_layout = QVBoxLayout(self.file_item_area_content)



        self.display_area = QScrollArea()
        self.display_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.display_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.display_area.setWidgetResizable(True)

        self.display_label = BetterQLabel()
        self.display_label.setScaledContents(False)
        # alight display label to center of display area
        self.display_label.setAlignment(Qt.AlignCenter)
        # when mousedown, function
        self.display_label.mousePressEvent = lambda event: self.select_sidebar

        self.display_area.setWidget(self.display_label)

        # add a footer that has no text
        self.footer_label = BetterQLabel()
        self.footer_label.setFixedHeight(50)
        self.footer_label.setBg(color="white")

        # button for options
        self.hide_preview_images = False

        # menu for image previews
        self.file_item_menu = QVBoxLayout()
        self.file_item_menu.setAlignment(Qt.AlignTop)

        self.preview_toggle_button = QPushButton("Hide Preview Images")
        self.preview_toggle_button.clicked.connect(self.toggle_sidebar)

        self.custom_sel_label = BetterQLabel("\nEnter a range to select:")
        self.custom_sel = QLineEdit()
        self.custom_sel.setPlaceholderText("e.g. 1-5, 8, 11-13")
        self.custom_sel.returnPressed.connect(self.parse_custom_sel)

        self.file_item_menu.addWidget(self.preview_toggle_button)
        self.file_item_menu.addWidget(self.custom_sel_label)
        self.file_item_menu.addWidget(self.custom_sel)

        # menu for the displayed image
        self.display_menu = QVBoxLayout()
        self.display_menu.setAlignment(Qt.AlignTop)


        # add zoom in and zoom out buttons. they increment/decrement the scale by 0.1.
        self.scale_factors = [0.25, 0.33, 0.5, 0.67, 0.75, 0.80, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0]
        self.default_scale_idx = self.scale_factors.index(1.0)
        self.scale_factors_bounds = [0, len(self.scale_factors) - 1]

        self.display_image_config = {
            "image_path": None,
            "scale_factor": self.default_scale_idx,
            "original_size": None,
            "pixmap": None,
        }

        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.reset_zoom_button = QPushButton("Reset Zoom")
        self.reset_zoom_button.clicked.connect(self.reset_zoom)

        # text box that displays the zoom percentage
        self.zoom_percentage = QLineEdit()
        self.zoom_percentage.setReadOnly(True)
        self.zoom_percentage.setText("100%")

        self.display_menu.addWidget(self.zoom_in_button)
        self.display_menu.addWidget(self.zoom_out_button)
        self.display_menu.addWidget(self.reset_zoom_button)
        self.display_menu.addWidget(self.zoom_percentage)


        # Make file_item area occupy left half of interface, and display label occupy right half
        layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.file_item_area, stretch=4)
        main_layout.addLayout(self.file_item_menu, stretch=2)
        main_layout.addLayout(self.display_menu, stretch=1)
        main_layout.addWidget(self.display_area, stretch=8)
        layout.addWidget(self.header)
        layout.addLayout(main_layout)
        layout.addWidget(self.footer_label)

        self.setLayout(layout)



    """ 
    File Item Sidebar 
    
    A sidebar for displaying the preview images and captions of the files captured by the camera.
    The preview images can be toggled.

    """

    def select_sidebar(self):
        self.sidebar_selected = True

    def toggle_sidebar(self):
        self.hide_preview_images = not self.hide_preview_images
        if self.hide_preview_images:
            # Hide the preview images in the sidebar
            for fileItem in self.fileItems:
                fileItem["f"].preview_image.hide()
            self.preview_toggle_button.setText("Show Preview Images")

        else:
            # Show the preview images in the sidebar
            for fileItem in self.fileItems:
                fileItem["f"].preview_image.show()
            self.preview_toggle_button.setText("Hide Preview Images")

    
    def clear_fileItems(self):
        while self.file_item_area_layout.count():
            item = self.file_item_area_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                layout = item.layout()
                if layout:
                    self.clear_layout(layout)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                nested_layout = item.layout()
                if nested_layout:
                    self.clear_layout(nested_layout)

    def add_preview_image(self, image_path, update=False):
        # Create an instance of ScrollbarWidget
        fileItem = ScrollbarWidget(image_path)

        # Connect the mousePressEvent and mouseDoubleClickEvent to the respective functions
        fileItem_id = len(self.fileItems)
        fileItem.mousePressEvent = lambda event: self.process_fileItem_sel(fileItem_id)
        fileItem.mouseDoubleClickEvent = lambda event: self.init_display_image(image_path)

        self.fileItems.append({
            "image_path": image_path,
            "f": fileItem,
        })

        if update:
            self.file_item_area_layout.addWidget(fileItem, alignment=Qt.AlignHCenter)

    def update_fileItems(self):
        self.clear_fileItems()

        for fileItem in self.fileItems:
            self.file_item_area_layout.addWidget(fileItem["f"], alignment=Qt.AlignHCenter)

    def parse_custom_sel(self):
        self.curr_fileIdxs = []

        custom_sel = self.custom_sel.text()
        splits = [text.strip() for text in custom_sel.split(",") if text.strip() != ""]

        for split in splits:
            split = split.split("-")
            split = [text.strip() for text in split if text.strip() != ""]

            if len(split) == 1:
                # single number was entered. select the fileItem at that index
                sel = int(split[0])
                if sel >= len(self.fileItems):
                    continue
                self.curr_fileIdxs.append(sel - 1)

            elif len(split) == 2:
                # two numbers were entered. select the range of fileItems
                range_ = np.sort(np.clip(np.array(split, dtype=np.int64), 1, len(self.fileItems)))
                range_[0] -= 1
                
                self.curr_fileIdxs.extend(np.arange(*range_))

            else:
                # invalid input
                print("Invalid input")
        
        self.curr_fileIdxs = list(set(self.curr_fileIdxs))
        print(self.curr_fileIdxs)

        self.update_selection_indicators()

    """
    Process the selection of a single file item. 
    Might be pared with a Shift event to select a range of file items.
    """
    def process_fileItem_sel(self, fileItem_id):
         
        # shift event
        if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            # no previous selections; same as selecting a single file item
            if self.curr_fileIdxs == [] or \
                len(self.curr_fileIdxs) == 1 and self.curr_fileIdxs[0] == fileItem_id:
                self.curr_fileIdxs = [fileItem_id]
                self.update_selection_indicators()

            else:

                reverse = False
                if fileItem_id > self.curr_fileIdxs[0]:
                    start = self.curr_fileIdxs[0]
                    end = fileItem_id
                else:
                    start = fileItem_id
                    end = self.curr_fileIdxs[0]
                    reverse = True

                self.curr_fileIdxs = list(range(start, end + 1))
                if reverse:
                    self.curr_fileIdxs.reverse()

                self.update_selection_indicators()

                """
                We reverse the order of the last selected file item indices.

                Explanation:
                A shift click select (SCS) is performed with the following steps:
                1. Click on file A. This is our initial file.
                2. Scroll up/down the file list if necessary.
                3. Press and hold down Shift, before clicking on file B. 
                4. All files from A to B, inclusive, are selected.

                If our previous selecton included multiple files (i.e. shift click select or select all), 
                then the last selected file item list will have multiple elements.
                
                Let's suppose we selected files 3 to 17 using a shift click select operation (SCS1). 17 > 3, and the previous selected range (PSR) is 3 to 17. Note that PSR must be strictly increasing.
                Our next operation is to press and hold down shift, before clicking on file 24, which is an attempt to trigger Step 3 in the SCS process. However, since we completed SCS1, we haven't selected an initial file (A). In other words, we need to assume A.
                This assumption, "AS", is simple to program as we simply select the last element in our PSR. In this case, it is file 17, because the PSR for SCS1 is 3 to 17. The file range 17 to 24 is then successfully selected.
                Now let's perform SCS1 by selecting file 17 as A, followed by file 3 as B. However, the selected range is still the same, 3 to 17. Going by our same assumption AS, we select the last element in PSR, which is 17. However, the true previous element we selected is file 3. This is where we need to reverse the order of the PSR.

                In summary, we reverse the order of the PSR if the shift-selected file (B) is less than the initial file (A).
                """
        else:        
            self.curr_fileIdxs = [fileItem_id]
            self.update_selection_indicators()

    """
    Select all file items.
    """
    def sel_all_fileItems(self):
        self.curr_fileIdxs = list(range(len(self.fileItems)))
        self.update_selection_indicators()

    """
    Update the file items based on the current selection.
    """
    def update_selection_indicators(self):
        if self.curr_fileIdxs == [] and self.prev_fileIdxs == []:
            return 
        
        # remove all fileItems that were previously selected but not selected anymore
        for idx in self.prev_fileIdxs:
            if idx not in self.curr_fileIdxs:
                self.fileItems[idx]["f"].preview_image.setBg(color="white")
                self.fileItems[idx]["f"].name.setBg(color="white")
        
        # add all fileItems that were not previously selected, but are selected now
        for idx in self.curr_fileIdxs:
            if idx not in self.prev_fileIdxs:
                self.fileItems[idx]["f"].preview_image.setBg(color="blue")
                self.fileItems[idx]["f"].name.setBg(color="light_gray")

        # update the previous selection
        self.prev_fileIdxs = self.curr_fileIdxs

        if len(self.curr_fileIdxs) == 1:
            sel_fn = self.fileItems[self.curr_fileIdxs[0]]["image_path"].split("/")[-1]
            self.footer_label.setText(f'"{sel_fn}" selected')
        else: 
            self.footer_label.setText(f"{len(self.curr_fileIdxs)} files selected")
       
        
    """
    Zoom Functions:
    Zoom in, zoom out, and reset zoom.

    If no image is loaded, then the zoom functions will do nothing.
    If the image is at its maximum zoom level, zoom in will do nothing.
    If the image is at its minimum zoom level, zoom out will do nothing.
    If the image is at its default zoom level, reset zoom will do nothing.
    
    """

    def zoom_in(self):
        if self.display_image_config["pixmap"] == None or \
            self.display_image_config["scale_factor"] == self.scale_factors_bounds[1]:
            return
        self.display_image_config["scale_factor"] += 1
        self.update_display_image()

    def zoom_out(self):
        if self.display_image_config["pixmap"] == None or \
            self.display_image_config["scale_factor"] == self.scale_factors_bounds[0]:
            return
        self.display_image_config["scale_factor"] -= 1
        self.update_display_image()

    def reset_zoom(self):
        if self.display_image_config["pixmap"] == None or \
            self.display_image_config["scale_factor"] == self.default_scale_idx:
            return
        self.display_image_config["scale_factor"] = self.default_scale_idx
        self.update_display_image()


    def init_display_image(self, image_path):
        self.display_image_config = {
            "image_path": image_path,
            "scale_factor": self.default_scale_idx,
            "original_size": None,
            "pixmap": None,
        }
        self.update_zoom_percentage()

        # Open the original image to get config
        with open(self.display_image_config["image_path"], 'rb') as f:
            image_data = f.read()

        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)
        self.display_image_config["pixmap"] = pixmap

        # Set the scaled pixmap as the pixmap of the BetterQLabel
        self.display_label.setPixmap(pixmap.scaledToWidth(DISPLAY_IMAGE_DEFAULT_WIDTH))
        self.display_image_config["original_size"] = self.display_label.pixmap().size()

    def update_zoom_percentage(self):
        percentage = int(self.scale_factors[self.display_image_config['scale_factor']] * 100)
        self.zoom_percentage.setText(f"{percentage}%")

    
    def update_display_image(self):
        self.update_zoom_percentage()

        # Calculate the new size based on the scale_factor
        new_size = self.display_image_config["original_size"] * self.scale_factors[self.display_image_config["scale_factor"]]

        # Set the scaled pixmap as the pixmap of the BetterQLabel
        self.display_label.setPixmap(self.display_image_config["pixmap"].scaled(new_size))


def main():
    # initialize the pyqt interface
    app = QApplication(sys.argv)
    window = RemoteCameraInterface()

    # go to samples folder and for each sample (.jpg) file, add it to the file_item area
    samples = sorted(os.listdir('samples'))


    for sample in samples:
        if sample.endswith('.jpg'):
            image_path = os.path.join('samples', sample)
            window.add_preview_image(image_path)
        
    window.update_fileItems()

    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
