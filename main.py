import tkinter as tk
# Import specific components
from tkinter import filedialog, Canvas, Scrollbar, Label, Frame, Toplevel, Entry
from PIL import Image, ImageTk
import cv2
import numpy as np

# Done till getting the images and custom operations images


class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing App")

        self.canvas = Canvas(root, yscrollcommand=self.on_scroll)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(root, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.container = Frame(self.canvas)  # Explicitly using Frame
        self.canvas.create_window((0, 0), window=self.container, anchor=tk.NW)

        self.upload_button = tk.Button(
            self.container, text="Upload Photo", command=self.upload_image)
        self.upload_button.grid(row=0, column=0, columnspan=3, pady=10)

        self.process_button = tk.Button(
            self.container, text="Process Image", command=self.process_image)
        self.process_button.grid(row=1, column=0, pady=10)
        self.process_button.grid_remove()  # Hide initially

        self.change_filters_button = tk.Button(
            self.container, text="Change Filters", command=self.show_change_filters)
        self.change_filters_button.grid(row=1, column=0, columnspan=3, pady=10)
        self.change_filters_button.grid_remove()  # Hide initially

        self.builtin_operations_var = tk.BooleanVar()
        self.builtin_operations_button = tk.Checkbutton(
            self.container, text="Built-in Operations", variable=self.builtin_operations_var, command=self.show_builtin_checkboxes)
        self.builtin_operations_button.grid(row=2, column=0, pady=10)
        self.builtin_operations_button.grid_remove()  # Hide initially

        self.custom_operations_var = tk.BooleanVar()
        self.custom_operations_button = tk.Checkbutton(
            self.container, text="Custom Operations", variable=self.custom_operations_var, command=self.show_custom_checkboxes)
        self.custom_operations_button.grid(row=2, column=1, pady=10)
        self.custom_operations_button.grid_remove()  # Hide initially

        self.checkbox_vars = {
            "Built-in Erosion": tk.BooleanVar(),
            "Built-in Dilation": tk.BooleanVar(),
            "Built-in Opening": tk.BooleanVar(),
            "Built-in Closing": tk.BooleanVar(),
            "Custom Erosion": tk.BooleanVar(),
            "Custom Dilation": tk.BooleanVar(),
            "Custom Opening": tk.BooleanVar(),
            "Custom Closing": tk.BooleanVar()
        }

        self.checklist_buttons = []
        row = 3
        for label, var in self.checkbox_vars.items():
            checkbox = tk.Checkbutton(self.container, text=label, variable=var)
            checkbox.grid(row=row, column=0, columnspan=3, sticky=tk.W)
            checkbox.grid_remove()  # Hide initially
            self.checklist_buttons.append(checkbox)
            row += 1

        self.image_display_row = 4
        self.image_display_col = 0
        self.displayed_images = []  # Keep track of displayed images

        # Create the Toplevel for custom kernel input
        self.custom_kernel_dialog = None

        # Initialize custom kernel variable
        self.custom_kernel = None

        # Create the Toplevel for builtin kernel input
        self.builtin_kernel_dialog = None

        # Initialize builtin kernel variable
        self.builtin_kernel = None

    def upload_image(self):
        file_path = filedialog.askopenfilename(title="Select an image file", filetypes=[
                                               ("Image files", "*.png;*.jpg;*.jpeg")])

        if file_path:
            self.upload_button.grid_remove()  # Hide Upload Photo button
            self.process_button.grid()  # Show Process Image button
            self.builtin_operations_button.grid()  # Show Built-in Operations button
            self.custom_operations_button.grid()  # Show Custom Operations button
            for checkbox in self.checklist_buttons:
                checkbox.grid_remove()  # Hide checklist buttons
            self.original_image = cv2.imread(file_path)
            self.original_image = cv2.cvtColor(
                self.original_image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            self.display_image(self.original_image, "Original Image", row=0)

            # Update the canvas scroll region after adding new elements
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            self.builtin_operations_var.trace_add(
                'write', self.show_builtin_checkboxes)
            self.custom_operations_var.trace_add(
                'write', self.show_custom_checkboxes)

    def display_image(self, image, label, row):
        image = Image.fromarray(image)  # Convert NumPy array to PIL Image
        img = ImageTk.PhotoImage(image)

        label_widget = Label(self.container, image=img,
                             text=label, compound=tk.TOP)
        label_widget.grid(
            row=row, column=self.image_display_col, padx=10, pady=10)

        label_widget.image = img  # to prevent garbage collection

        # Keep track of displayed images
        self.displayed_images.append(label_widget)

    def clear_displayed_images(self):
        for img_widget in self.displayed_images:
            img_widget.grid_forget()
        self.displayed_images = []

    def process_image(self):
        if hasattr(self, 'original_image'):
            # Clear the existing displayed images
            self.clear_displayed_images()

            processed_images = []
            for label, var in self.checkbox_vars.items():
                if var.get():
                    processed_image = self.process_image_function(
                        label.lower())
                    processed_images.append((processed_image, label))

            for checkbox in self.checklist_buttons:
                checkbox.grid_remove()  # Hide checklist buttons after processing

            self.process_button.grid_remove()

            # Show the original image in the first row
            self.display_image(self.original_image, "Original Image", row=0)

            # Display processed images in separate rows
            self.image_display_row += 2
            for img, label in processed_images:
                self.display_image(img, label, row=self.image_display_row)
                self.image_display_row += 1
                # self.image_display_col += 1
                # self.image_display_col = self.image_display_col % 2

            # Update the canvas scroll region after removing elements
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            # Show the "Change Filters" button after processing
            self.change_filters_button.grid()
            self.builtin_operations_button.grid_remove()
            self.custom_operations_button.grid_remove()

    def process_image_function(self, operation):
        if operation.startswith("built-in"):
            return self.process_builtin_operation(operation)
        elif operation.startswith("custom"):
            return self.process_custom_operation(operation)

    def process_builtin_operation(self, operation):
        if self.builtin_kernel is not None:
            if operation == "built-in erosion":
                return cv2.erode(np.array(self.original_image), self.builtin_kernel, iterations=1)
            elif operation == "built-in dilation":
                return cv2.dilate(np.array(self.original_image), self.builtin_kernel, iterations=1)
            elif operation == "built-in opening":
                return cv2.morphologyEx(np.array(self.original_image), cv2.MORPH_OPEN, self.builtin_kernel)
            elif operation == "built-in closing":
                return cv2.morphologyEx(np.array(self.original_image), cv2.MORPH_CLOSE, self.builtin_kernel)

    def process_custom_operation(self, operation):
        if self.custom_kernel is not None:
            if operation == "custom erosion":
                return self.erode(np.array(self.original_image), self.custom_kernel)
            elif operation == "custom dilation":
                return self.dilate(np.array(self.original_image), self.custom_kernel)
            elif operation == "custom opening":
                return self.opening(np.array(self.original_image), self.custom_kernel)
            elif operation == "custom closing":
                return self.closing(np.array(self.original_image), self.custom_kernel)

    def show_builtin_checkboxes(self, *args):
        if self.builtin_operations_var.get():
            if self.builtin_kernel_dialog is None:
                self.create_builtin_kernel_dialog()

            # Show the builtin kernel dialog
            self.builtin_kernel_dialog.deiconify()
            self.builtin_kernel_dialog.lift()

            for checkbox in self.checklist_buttons[:4]:
                checkbox.grid()  # Show checkboxes corresponding to built-in operations
        else:
            # Destroy the custom kernel dialog if it exists
            self.builtin_kernel_dialog.destroy()
            self.builtin_kernel_dialog = None

            for checkbox in self.checklist_buttons[:4]:
                checkbox.grid_remove()  # Hide checkboxes corresponding to built-in operations

    def show_custom_checkboxes(self, *args):
        if self.custom_operations_var.get():
            if self.custom_kernel_dialog is None:
                self.create_custom_kernel_dialog()

            # Show the custom kernel dialog
            self.custom_kernel_dialog.deiconify()
            self.custom_kernel_dialog.lift()

            for checkbox in self.checklist_buttons[4:]:
                checkbox.grid()  # Show all checkboxes
        else:
            # Destroy the custom kernel dialog if it exists
            self.custom_kernel_dialog.destroy()
            self.custom_kernel_dialog = None

            for checkbox in self.checklist_buttons[4:]:
                checkbox.grid_remove()  # Hide all checkboxes

    def create_builtin_kernel_dialog(self):
        self.builtin_kernel_dialog = Toplevel(self.root)
        self.builtin_kernel_dialog.title('Builtin Kernel')
        self.builtin_kernel_dialog.withdraw()  # Hide initially

        # Create entry widgets for each of the 3x3 kernel
        self.builtin_entries = []
        for i in range(3):
            for j in range(3):
                label = Label(self.builtin_kernel_dialog,
                              text=f"Element ({i + 1}, {j + 1}):")
                label.grid(row=i, column=2*j, padx=10, pady=10)

                entry_var = tk.StringVar()
                entry = Entry(self.builtin_kernel_dialog,
                              textvariable=entry_var)
                entry.grid(row=i, column=2*j + 1, padx=10, pady=10)

                self.builtin_entries.append(entry_var)

        # Create a button to set the custom kernel
        set_kernel_button = tk.Button(
            self.builtin_kernel_dialog, text="Set Builtin Kernel", command=self.set_builtin_kernel)
        set_kernel_button.grid(row=4, column=1, columnspan=2, pady=10)
        # set_kernel_button.pack(side=tk.BOTTOM, pady=10)

    def create_custom_kernel_dialog(self):
        self.custom_kernel_dialog = Toplevel(self.root)
        self.custom_kernel_dialog.title('Custom Kernel')
        self.custom_kernel_dialog.withdraw()  # Hide initially

        # Create entry widgets for each of the 3x3 kernel
        self.custom_entries = []
        for i in range(3):
            for j in range(3):
                label = Label(self.custom_kernel_dialog,
                              text=f"Element ({i + 1}, {j + 1}):")
                label.grid(row=i, column=2*j, padx=10, pady=10)

                entry_var = tk.StringVar()
                entry = Entry(self.custom_kernel_dialog,
                              textvariable=entry_var)
                entry.grid(row=i, column=2*j + 1, padx=10, pady=10)

                self.custom_entries.append(entry_var)

        # Create a button to set the custom kernel
        set_kernel_button = tk.Button(
            self.custom_kernel_dialog, text="Set Custom Kernel", command=self.set_custom_kernel)
        set_kernel_button.grid(row=4, column=1, columnspan=2, pady=10)

    def get_custom_kernel(self):
        if self.custom_operations_var.get():
            if self.custom_kernel_dialog is None:
                self.create_custom_kernel_dialog()

            # Show the custom kernel dialog
            self.custom_kernel_dialog.deiconify()
            self.custom_kernel_dialog.lift()

            # Hide the checklist buttons corresponding to built-in operations
            for checkbox in self.checklist_buttons[:4]:
                checkbox.grid_remove()

    def set_builtin_kernel(self):
        try:
            # Extract values from entry widgets
            builtin_kernel_values = [float(var.get()) for var in self.builtin_entries]

            # Convert the list to a NumPy array
            builtin_kernel = np.array(builtin_kernel_values).reshape((3, 3))

            # Set the custom kernel
            self.builtin_kernel = builtin_kernel

            # Close the dialog
            self.builtin_kernel_dialog.destroy()
        except ValueError:
            tk.messagebox.showerror(
                "Error", "Invalid input. Please enter numeric values.")

    def set_custom_kernel(self):
        try:
            # Extract values from entry widgets
            custom_kernel_values = [float(var.get()) for var in self.custom_entries]

            # Convert the list to a NumPy array
            custom_kernel = np.array(custom_kernel_values).reshape((3, 3))

            # Set the custom kernel
            self.custom_kernel = custom_kernel

            # Close the dialog
            self.custom_kernel_dialog.destroy()
        except ValueError:
            tk.messagebox.showerror(
                "Error", "Invalid input. Please enter numeric values.")

    def show_change_filters(self):
        # Clear the existing displayed images
        self.clear_displayed_images()

        self.process_button.grid_remove()  # Hide Process Image button
        self.change_filters_button.grid_remove()  # Hide Change Filters button
        for checkbox in self.checklist_buttons:
            checkbox.grid_remove()  # Show checklist buttons

    # Reset the state of built-in and custom operations buttons
        self.builtin_operations_button.deselect()
        self.custom_operations_button.deselect()

        for checkbox in self.checklist_buttons:
            checkbox.deselect()  # Deselect checklist buttons

        self.builtin_operations_button.grid()
        self.custom_operations_button.grid()

        # Show the original image in the first row
        self.display_image(self.original_image, "Original Image", row=0)

        # Update the canvas scroll region after removing elements
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Show the "Process Image" button after clicking "Change Filters"
        self.process_button.grid()

    def erode(self, image, kernel):
        height, width = image.shape[:2]
        result = np.zeros_like(image)

        for i in range(1, height - 1):
            for j in range(1, width - 1):
                result[i, j] = np.min(image[i - 1:i + 2, j - 1:j + 2] * kernel)

        return result

    def dilate(self, image, kernel):
        height, width = image.shape[:2]
        result = np.zeros_like(image)

        for i in range(1, height - 1):
            for j in range(1, width - 1):
                result[i, j] = np.max(image[i - 1:i + 2, j - 1:j + 2] * kernel)

        return result

    def opening(self, image, kernel):
        eroded_image = self.erode(image, kernel)
        opened_image = self.dilate(eroded_image, kernel)
        return opened_image

    def closing(self, image, kernel):
        dilated_image = self.dilate(image, kernel)
        closed_image = self.erode(dilated_image, kernel)
        return closed_image

    def on_scroll(self, *args):
        self.canvas.yview(*args)

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    app.canvas.bind("<Configure>", app.on_canvas_configure)
    app.root.bind("<MouseWheel>", lambda event: app.canvas.yview_scroll(
        int(-1 * (event.delta / 120)), "units"))
    root.mainloop()
