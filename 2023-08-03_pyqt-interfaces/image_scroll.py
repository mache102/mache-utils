import json 
import numpy as np 
import os
import shutil
import sys
import time

import PIL.Image, PIL.ImageOps
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from tkinter import *
from tkinter import filedialog
from tqdm import tqdm


from PyQt5.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, QPushButton, QMenu, QAction, QMessageBox, QInputDialog, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

FILE_DIR = "samples"
FILE_EXTENSION = ".jpg"
PREVIEW_IMAGE_WIDTH = 250
DISPLAY_IMAGE_DEFAULT_WIDTH = 600 

def check_consecutive(l):
    # check if list is consecutive
    n = len(l) - 1
    return (sum(np.diff(sorted(l)) == 1) >= n)
     

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

        elif color in self.colorDict:
            self.styles["background-color"] = "rgb({},{},{})".format(*self.colorDict[color])
            self.updateStyleSheet()

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
    def __init__(self, data, fp):
        super().__init__()


        image_name = fp.split('/')[-1]

        # Convert the image_data to a QPixmap for the preview image
        image = QImage.fromData(data)
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
        self.name.setFixedHeight(40)
        self.name.setAlignment(Qt.AlignCenter)
        self.name.setFontSize(20)


        # Layout manager to arrange the image and caption vertically
        layout = QVBoxLayout()
        layout.addWidget(self.preview_image, alignment=Qt.AlignHCenter)
        layout.addWidget(self.name, alignment=Qt.AlignHCenter)

        self.setLayout(layout)

class HeaderWidget(QWidget):
    # Create a custom signal for the "Select All" action
    TRIGGER_select_all_fileItems = pyqtSignal()
    TRIGGER_clear_fileItem_selection = pyqtSignal()
    TRIGGER_delete_fileItem_selection = pyqtSignal()
    TRIGGER_rescan_fileItem_selection = pyqtSignal()
    TRIGGER_move_fileItem_selection = pyqtSignal()
    TRIGGER_discard_unselected = pyqtSignal()

    TRIGGER_open_folder = pyqtSignal()
    TRIGGER_close_window = pyqtSignal()
    TRIGGER_save_files_to = pyqtSignal()
    TRIGGER_export_files = pyqtSignal()


    def __init__(self):
        super().__init__()

        # Create a horizontal layout for the header widget
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # List of dropdown names and their actions
        with open("dropdowns.json", "r") as f:
            dropdowns = json.load(f)

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
                else:
                    curr_action = QAction(action["action_name"], self)

                if action["connect"]:
                    curr_action.triggered.connect(getattr(self, action["connect"]))

                dropdown_menu.addAction(curr_action)

            # Set the dropdown menu for the dropdown button
            dropdown_button.setMenu(dropdown_menu)

    def select_all_fileItems(self):
        # Emit the custom signal when the "Select All" action is triggered
        self.TRIGGER_select_all_fileItems.emit()

    def clear_fileItem_selection(self):
        # Emit the custom signal when the "Clear Selection" action is triggered
        self.TRIGGER_clear_fileItem_selection.emit()

    
    def delete_fileItem_selection(self):
        self.TRIGGER_delete_fileItem_selection.emit()

    def rescan_fileItem_selection(self):
        self.TRIGGER_rescan_fileItem_selection.emit()

    def move_fileItem_selection(self):
        self.TRIGGER_move_fileItem_selection.emit()

    def discard_unselected(self):
        self.TRIGGER_discard_unselected.emit()

    def open_folder(self):
        self.TRIGGER_open_folder.emit()

    def close_window(self):
        self.TRIGGER_close_window.emit()

    def save_files_to(self):
        self.TRIGGER_save_files_to.emit()

    def export_files(self):
        self.TRIGGER_export_files.emit()


class RemoteCameraInterface(QWidget):
    def __init__(self):
        super().__init__()

        # Set default window size
        self.setGeometry(100, 100, 1280, 720)

        self.icon_lookup = {
            "warning": QMessageBox.Warning,
            "info": QMessageBox.Information,
            "error": QMessageBox.Critical,
            "question": QMessageBox.Question,
        }
        self.file_dir = FILE_DIR

        self.fileItems = []
        self.curr_fileIdxs = []
        self.prev_fileIdxs = []

        self.header = HeaderWidget()
        self.header.TRIGGER_select_all_fileItems.connect(self.select_all_fileItems)
        self.header.TRIGGER_clear_fileItem_selection.connect(self.clear_fileItem_selection)
        self.header.TRIGGER_delete_fileItem_selection.connect(self.delete_fileItem_selection)
        self.header.TRIGGER_rescan_fileItem_selection.connect(self.rescan_fileItem_selection)
        self.header.TRIGGER_move_fileItem_selection.connect(self.move_fileItem_selection)
        self.header.TRIGGER_discard_unselected.connect(self.discard_unselected)

        self.header.TRIGGER_open_folder.connect(self.open_folder)
        self.header.TRIGGER_close_window.connect(self.close_window)
        self.header.TRIGGER_save_files_to.connect(self.save_files_to)
        self.header.TRIGGER_export_files.connect(self.export_files)
        

        # Create a fileItem_ area to contain the preview images and captions
        self.fileItem_area = QScrollArea()
        self.fileItem_area.setWidgetResizable(True)
        self.fileItem_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Set the fixed width for the fileItem_area
        self.fileItem_area.setFixedWidth(PREVIEW_IMAGE_WIDTH+100)

        # Create a container widget to hold the preview images and captions
        self.fileItem_area_content = QWidget(self.fileItem_area)
        self.fileItem_area.setWidget(self.fileItem_area_content)

        # Layout manager to arrange the images and captions vertically
        self.fileItem_area_layout = QVBoxLayout(self.fileItem_area_content)



        self.display_area = QScrollArea()
        self.display_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.display_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.display_area.setWidgetResizable(True)

        self.display_label = BetterQLabel()
        self.display_label.setScaledContents(False)
        # alight display label to center of display area
        self.display_label.setAlignment(Qt.AlignCenter)
        # when mousedown, function
        # self.display_label.mousePressEvent = lambda event: self.select_sidebar

        self.display_area.setWidget(self.display_label)

        # add a footer that has no text
        self.footer_label = BetterQLabel()
        self.footer_label.setFixedHeight(50)
        self.footer_label.setBg(color="white")

        # button for options
        self.hide_preview_images = False

        # menu for image previews
        self.fileItem_menu = QVBoxLayout()
        self.fileItem_menu.setAlignment(Qt.AlignTop)

        self.preview_toggle_button = QPushButton("Hide Preview Images")
        self.preview_toggle_button.clicked.connect(self.toggle_sidebar)

        self.custom_fileItem_selection_label = BetterQLabel("\nEnter a range to select:")
        self.custom_fileItem_selection = QLineEdit()
        self.custom_fileItem_selection.setPlaceholderText("e.g. 1-5, 8, 11-13")
        self.custom_fileItem_selection.returnPressed.connect(self.parse_custom_fileItem_selection)

        self.fileItem_menu.addWidget(self.preview_toggle_button)
        self.fileItem_menu.addWidget(self.custom_fileItem_selection_label)
        self.fileItem_menu.addWidget(self.custom_fileItem_selection)

        # menu for the displayed image
        self.display_menu = QVBoxLayout()
        self.display_menu.setAlignment(Qt.AlignTop)


        # add zoom in and zoom out buttons. they increment/decrement the scale by 0.1.
        self.scale_factors = [0.25, 0.33, 0.5, 0.67, 0.75, 0.80, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0]
        self.default_scale_idx = self.scale_factors.index(1.0)
        self.scale_factors_bounds = [0, len(self.scale_factors) - 1]

        self.display_image_config = {
            "fp": None,
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


        # Make fileItem area occupy left half of interface, and display label occupy right half
        layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.fileItem_area, stretch=4)
        main_layout.addLayout(self.fileItem_menu, stretch=2)
        main_layout.addLayout(self.display_menu, stretch=1)
        main_layout.addWidget(self.display_area, stretch=8)
        layout.addWidget(self.header)
        layout.addLayout(main_layout)
        layout.addWidget(self.footer_label)

        self.setLayout(layout)

        # self.update_files() 

    def update_files(self):
        self.files = [file for file in sorted(os.listdir(self.file_dir)) if file.endswith(FILE_EXTENSION)]

    # def refresh_file_order(self):
    #     with open(os.path.join(FILE_DIR, "file_order.txt"), 'w') as f:
    #         f.write("\n".join(self.files))

    """ 
    File Item Sidebar 
    
    A sidebar for displaying the preview images and captions of the files captured by the camera.
    The preview images can be toggled.

    """


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

    
    def delete_all_fileItems(self):
        self.fileItems = []
        while self.fileItem_area_layout.count():
            item = self.fileItem_area_layout.takeAt(0)
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

    def add_fileItem(self, data=None, fp=None, curr_idx=None):
        if curr_idx == None:
            curr_idx = len(self.fileItems)

            self.fileItems.append({
                "fp": fp,
                "data": data,
            })

        else: 
            self.fileItems[curr_idx] = {
                "fp": fp,
                "data": data,
            }

        # Create an instance of ScrollbarWidget
        fileItem = ScrollbarWidget(data, fp)

        # Connect the mousePressEvent and mouseDoubleClickEvent to the respective functions
        fileItem.mousePressEvent = lambda event: self.process_fileItem_selection(curr_idx)
        fileItem.mouseDoubleClickEvent = lambda event: self.init_display_image(fp)

        if self.hide_preview_images:
            fileItem.preview_image.hide()

        self.fileItems[curr_idx]["f"] = fileItem

        self.fileItem_area_layout.addWidget(self.fileItems[curr_idx]["f"], alignment=Qt.AlignHCenter)

    # def update_fileItems(self):
    #     self.delete_all_fileItems()

    #     for fileItem in self.fileItems:
    #         self.fileItem_area_layout.addWidget(fileItem["f"], alignment=Qt.AlignHCenter)

    """
    Signals from 'File' dropdown actions
    """

    def open_folder(self):
        # ask open path
        file_dir = filedialog.askdirectory()
        if file_dir == ():
            return
        
        self.file_dir = file_dir
        self.update_files()
        # print(self.file_dir, self.files)
        
        self.delete_all_fileItems()
        for fn in self.files:
            fp = os.path.join(self.file_dir, fn)
            with open(fp, 'rb') as f:
                data = f.read()
            self.add_fileItem(data=data,
                                fp=fp)
    
        self.footer_label.setText(f"Successfully opened {self.file_dir} ({len(self.files)} files ending in {FILE_EXTENSION})")


    def close_window(self):
        exit()

    def save_files_to(self):
        if self.fileItems == []:
            return
        
        self.saveTo_dir = filedialog.askdirectory()
        if self.saveTo_dir == ():
            return

        # move self.file_dir to self.saveTo_dir
        shutil.move(self.file_dir, self.saveTo_dir)
        self.footer_label.setText(f"Successfully saved {self.file_dir} to {self.saveTo_dir}")

        self.files = []
        self.delete_all_fileItems()
        
        
    def export_files(self):
        if self.fileItems == []:
            return
        # Create the message box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Please select the export color option:")
        msg.setWindowTitle("File export settings")

        # Set standard buttons as the color options
        
        msg.addButton("Color", QMessageBox.YesRole)
        msg.addButton("Grayscale", QMessageBox.YesRole)
        msg.addButton("Black and White", QMessageBox.YesRole)
        msg.setStandardButtons(QMessageBox.Cancel)

        # Execute the message box and get the clicked button
        result = msg.exec_()

        # Handle the selected color option based on the clicked button
        if msg.clickedButton().text() == "Color":
            color_option = "color"
        elif msg.clickedButton().text() == "Grayscale":
            color_option = "grayscale"
        elif msg.clickedButton().text() == "Black and White":
            color_option = "b+w"
        else:
            return  # User clicked Cancel or closed the message box

        # Ask for save path
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Save Path", "", "PDF Files (*.pdf);;Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            # Save the selected file path
            file_path += '.pdf'
            print("Save Path:", file_path)

            # Call the function to be implemented with color_option and file_path as arguments
            self.export_with_color_option(color_option, file_path)


    def export_with_color_option(self, color_option, save_path, margin=0.05):
        # Create a PDF document
        c = canvas.Canvas(save_path, pagesize=letter)

        # Calculate the available image area in the PDF with margins
        page_width, page_height = letter
        image_area_width = page_width * (1 - 2 * margin)
        image_area_height = page_height * (1 - 2 * margin)

        for image_path in self.files:
            # Load the image using PIL
            image = PIL.Image.open(os.path.join(self.file_dir, image_path))

            if color_option == "color":
                pass  # No modification required for colored images
            elif color_option == "grayscale":
                # Convert the image to grayscale using PIL
                image = PIL.ImageOps.grayscale(image)
            elif color_option == "b+w":
                # Convert the image to black and white (threshold=128) using PIL
                image = image.convert("L").point(lambda x: 0 if x < 128 else 255, '1')

            # Calculate the aspect ratio of the image
            aspect_ratio = image.width / float(image.height)

            # Calculate the new width and height to fit in the available image area
            if image.height > image.width:
                new_height = image_area_height
                new_width = new_height * aspect_ratio
            else:
                new_width = image_area_width
                new_height = new_width / aspect_ratio

            # Resize the image
            image = image.resize((int(new_width), int(new_height)), PIL.Image.LANCZOS)

            # Calculate the position to center the image in the PDF
            x = (page_width - image.width) / 2
            y = (page_height - image.height) / 2

            # Draw the image on the PDF
            c.drawInlineImage(image, x, y, width=image.width, height=image.height)

            # Add a new page for the next image
            c.showPage()

        # Save the PDF
        c.save()

        self.footer_label.setText(f"Successfully exported {len(self.files)} files to {save_path}")

    """
    Signals from 'Selection' dropdown actions
    """

    def popup(self, title, message, icon="info", type="yesno"):
        assert icon in self.icon_lookup.keys(), f"Invalid icon type: {icon}"
        # qt popup dialog for confirming an action
        msg = QMessageBox()
        msg.setIcon(self.icon_lookup[icon])
        msg.setText(message)
        msg.setWindowTitle(title)

        if type == "yesno":
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            return msg.exec_() == QMessageBox.Yes
        elif type == "ok":
            msg.setStandardButtons(QMessageBox.Ok)
            return msg.exec_() == QMessageBox.Ok
        else:
            raise ValueError(f"Invalid popup type: {type}")

    def select_all_fileItems(self):
        self.curr_fileIdxs = list(range(len(self.fileItems)))
        self.update_fileItem_selection_drawer()

    def clear_fileItem_selection(self):
        self.curr_fileIdxs = []
        self.update_fileItem_selection_drawer()

    def delete_fileItem_selection(self):
        # obtain confirmation from the user
        selected_count = len(self.curr_fileIdxs)
        max_list_length = 10
        confirmation_message = f"Are you sure you want to delete the following {selected_count} files?\nThis action cannot be undone!\n\n"

        if selected_count > max_list_length:
            for idx in self.curr_fileIdxs[:max_list_length]:
                confirmation_message += f"{self.fileItems[idx]['fp']}\n"
            confirmation_message += f"...and {selected_count-max_list_length} more\n"
        else:
            for idx in self.curr_fileIdxs:
                confirmation_message += f"{self.fileItems[idx]['fp']}\n"

        response = self.popup("Delete Selection", 
                                confirmation_message,
                                icon="warning")
        if response == False:
            return 
        
        # delete the selected images from the file system
        for idx in self.curr_fileIdxs:
            fileItem = self.fileItems[idx]
            image_path = fileItem["fp"]
            os.remove(image_path)

        # Sort the selected indices in reverse order to avoid issues with index shifting
        curr_fileIdxs_sorted = sorted(self.curr_fileIdxs, reverse=True)

        # the next empty idx that we will start with when moving the file items 
        # after the deleted items
        #
        # also a deletion range for the fileItem widgets that we have to delete 
        # and replace with new widgets that have updated, correct indices
        next_empty_idx = curr_fileIdxs_sorted[-1]
        deletion_range = list(range(next_empty_idx, len(self.fileItems)))[::-1]

        # delete the fileItems from the fileItems list
        for idx in curr_fileIdxs_sorted: 
            del self.fileItems[idx]

        # Clear the current selection
        self.curr_fileIdxs.clear()

        # Update the fileItem_area_layout by removing the widgets for the deleted elements
        for idx in deletion_range:

            widget_to_remove = self.fileItem_area_layout.itemAt(idx).widget()
            self.fileItem_area_layout.removeWidget(widget_to_remove)

            # Ensure the widget is also deleted to release resources
            widget_to_remove.deleteLater()

        # now we update the widgets that come after the deleted widgets
        for idx in range(len(self.fileItems)):
            if idx < next_empty_idx:
                continue
            data = self.fileItems[idx]["data"]
            fp = self.fileItems[idx]["fp"]
            self.add_fileItem(data=data, fp=fp,
                                curr_idx=idx)

        # self.update_files()
        # self.refresh_file_order()

    def rescan_fileItem_selection(self):
        # Implementation for rescanning the selection images
        pass

    def move_fileItem_selection(self):
        if len(self.curr_fileIdxs) == 0 or not check_consecutive(self.curr_fileIdxs):
            return
        
        # ask user to enter the filename where the selection will be moved to:
        fn_as_position, ok = QInputDialog.getText(self, 'Move Selection', 
                                                'Enter filename where the selection will be moved to:')
        
        if not ok:
            return
        
        if fn_as_position not in self.files:
            self.popup("Move Selection",
                        f"Filename not found: {fn_as_position}",
                        icon="error",
                        type="ok")
            return 

        # self.update_files() 
        if self.files.index(fn_as_position) in self.curr_fileIdxs:
            self.popup("Move Selection",
                        f"Cannot move selection to itself!",
                        icon="error",
                        type="ok")
            return
        
        # obtain the index of fn as position in self.files
        # for self.files, move the selection to the position of fn_as_position

        moveTo_position = self.files.index(fn_as_position)
        fn_selection = [self.files[idx] for idx in self.curr_fileIdxs]

        # Sort the selected indices in reverse order to avoid issues with index shifting
        curr_fileIdxs_sorted = sorted(self.curr_fileIdxs, reverse=True)

        # the next empty idx that we will start with when moving the file items 
        # after the deleted items
        #
        # also a deletion range for the fileItem widgets that we have to delete 
        # and replace with new widgets that have updated, correct indices
        next_empty_idx = curr_fileIdxs_sorted[-1]
        deletion_range = list(range(next_empty_idx, len(self.fileItems)))[::-1]

        # delete the fileItems from the fileItems list
        for idx in curr_fileIdxs_sorted: 
            del self.fileItems[idx]

        # Clear the current selection
        self.curr_fileIdxs.clear()

        # Update the fileItem_area_layout by removing the widgets for the deleted elements
        for idx in deletion_range:

            widget_to_remove = self.fileItem_area_layout.itemAt(idx).widget()
            self.fileItem_area_layout.removeWidget(widget_to_remove)

            # Ensure the widget is also deleted to release resources
            widget_to_remove.deleteLater()

        # now we update the widgets that come after the deleted widgets
        for idx in range(len(self.fileItems)):
            if idx < next_empty_idx:
                continue
            data = self.fileItems[idx]["data"]
            fp = self.fileItems[idx]["fp"]
            self.add_fileItem(data=data, fp=fp,
                                curr_idx=idx)

        # self.update_files()
        # self.refresh_file_order()


    def discard_unselected(self):
        # Implementation for discarding images not part of the selection subset
        pass

    def parse_custom_fileItem_selection(self):
        self.curr_fileIdxs = []

        custom_fileItem_selection = self.custom_fileItem_selection.text()
        splits = [text.strip() for text in custom_fileItem_selection.split(",") if text.strip() != ""]

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

        self.update_fileItem_selection_drawer()

    """
    Process the selection of a single file item. 
    Might be pared with a Shift event to select a range of file items.
    """
    def process_fileItem_selection(self, fileItem_idx):
        # print("fileItem_idx ", fileItem_idx)
         
        # shift event
        if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            # no previous selections; same as selecting a single file item
            if self.curr_fileIdxs == [] or \
                len(self.curr_fileIdxs) == 1 and self.curr_fileIdxs[0] == fileItem_idx:
                self.curr_fileIdxs = [fileItem_idx]
                self.update_fileItem_selection_drawer()

            else:

                reverse = False
                if fileItem_idx > self.curr_fileIdxs[0]:
                    start = self.curr_fileIdxs[0]
                    end = fileItem_idx
                else:
                    start = fileItem_idx
                    end = self.curr_fileIdxs[0]
                    reverse = True

                self.curr_fileIdxs = list(range(start, end + 1))
                if reverse:
                    self.curr_fileIdxs.reverse()

                self.update_fileItem_selection_drawer()

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
            self.curr_fileIdxs = [fileItem_idx]
            self.update_fileItem_selection_drawer()


    """
    Update the file items based on the current selection.
    """
    def update_fileItem_selection_drawer(self):
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

        if len(self.curr_fileIdxs) == 0:
            self.footer_label.setText("")
        if len(self.curr_fileIdxs) == 1:
            selected_filename = self.fileItems[self.curr_fileIdxs[0]]["fp"].split("/")[-1]
            self.footer_label.setText(f'"{selected_filename}" selected')
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


    def init_display_image(self, fp):
        self.display_image_config = {
            "fp": fp,
            "scale_factor": self.default_scale_idx,
            "original_size": None,
            "pixmap": None,
        }
        self.update_zoom_percentage()

        # Open the original image to get config
        with open(self.display_image_config["fp"], 'rb') as f:
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

    # go to samples folder and for each sample (.jpg) file, add it to the fileItem area
    # files = [file for file in sorted(os.listdir(FILE_DIR)) if file.endswith(FILE_EXTENSION)]
    # # write the files to a txt file in FILE_DIR for debugging and ordering purposes
    # with open(os.path.join(FILE_DIR, "file_order.txt"), 'w') as f:
    #     f.write("\n".join(files))

    # for fn in files:
    #     fp = os.path.join(FILE_DIR, fn)
    #     with open(fp, 'rb') as f:
    #         data = f.read()
    #     window.add_fileItem(data=data,
    #                         fp=fp)
    
    
    # window.update_fileItems()

    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
