import tkinter as tk
from tkinter import ttk

class Gui(tk.Tk):
    '''Currency Converter Class GUI '''
    # pylint: disable=too-many-instance-attributes
    def __init__(self, currency_list: list[list], submit_function):
        '''Redefine init'''
        super().__init__()
        self.title('Currency Converter')
        self.geometry('700x700')
        self.config(background='black')

        self.label = ttk.Label(
            self, text='Currency Converter', background='black', foreground='gold'
            )
        self.label.pack()

        codes = [x[0] for x in currency_list]

        frame_input = ttk.Frame(self, padding=10)
        frame_input.pack(side="top", padx=50, pady=20)

        frame_convert = ttk.Frame(self, padding=10)
        frame_convert.pack(side="top", padx=50, pady=20)

        self.label_input_quantity = ttk.Label(
            frame_input,
             text='Input Quantity',
              background='black',
               foreground='gold')
        self.label_input_quantity.pack(side="left", padx=5, pady=5)

        self.input_quantity = tk.Text(
            frame_input,
             height=1,
              width=20,
               font=("Arial", 14),
                bg='red',
                 fg='gold')
        self.input_quantity.pack(side="left", padx=5, pady=5)

        self.label_convert_from = ttk.Label(
            frame_convert,
             text='Convert From',
              background='black',
               foreground='gold')
        self.label_convert_from.pack(side="left", padx=5, pady=5)

        self.selected_from = ttk.Combobox(frame_convert,state="readonly", values=codes)
        self.selected_from.set("USD")
        self.selected_from.pack(side="left", padx=5, pady=5)

        self.label_convert_to = ttk.Label(
            frame_convert,
             text='Convert To',
              background='black',
               foreground='gold')
        self.label_convert_to.pack(side="left", padx=5, pady=5)

        self.selected_to = ttk.Combobox(frame_convert,state="readonly", values=codes)
        self.selected_to.set("EUR")
        self.selected_to.pack(side="left", padx=5, pady=5)

        self.button = tk.Button(
            self,
             text='Submit',
              width=25,
               font=("Arial", 14),
                command=submit_function, bg='red', fg='gold')
        self.button.pack(side="bottom", padx=50, pady=20)

        self.output_box = tk.Text(
            self,
             height=1,
              width=40,
               font=("Arial", 14),
                bg='red',
                 fg='gold',
                  state="disabled"
            )
        self.output_box.pack(side="bottom", padx=50, pady=20)

    def getinput_quantity(self) -> float | None:
        '''Function for obtaining the input quantity from the GUI'''
        input_quantity = self.input_quantity.get(1.0, "end-1c")
        try:
            input_quantity = float(input_quantity)
        except ValueError:
            return None
        return input_quantity

    def output(self, user_input):
        '''function to display outout to GUI/user'''
        self.output_box.config(state='normal')
        self.output_box.delete(1.0, "end")
        self.output_box.insert(tk.END, user_input)
        self.output_box.config(state='disabled')

