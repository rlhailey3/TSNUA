'''A gui class using OOP'''


import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.messagebox import showinfo



class CurrencyConverter(tk.Tk):
  def __init__(self):
    super().__init__()

    def getinputQuantity():
        '''function that takes input'''
        return inputQuantity.get(1.0, "end-1c")


    def output(input):
        '''function that displays output'''
        outputBox.insert(END, input)

    def convert():
        inp = getinputQuantity()
        output(inp)


    self.title('Currency Converter')
    self.geometry('700x700')

    input_var = tk.StringVar()
    API_input_var = tk.StringVar()
    
    #Label
    self.label = ttk.Label(self, text='Currency Converter')
    self.label.pack()

    labelInputQuantity = ttk.Label(self, text='Input Quantity')
    labelInputQuantity.place(x= 20, y=210)

    labelAPIKey = ttk.Label(self, text='API Key Input')
    labelAPIKey.place(x=20, y=300)

    labelOutput = ttk.Label(self, text='Output')
    labelOutput.place(x=525, y=20)

    labelConvertFrom = ttk.Label(self, text='Convert From')
    labelConvertFrom.place(x=20, y=40)

    labelConvertTo = ttk.Label(self, text='Convert To')
    labelConvertTo.place(x=20, y=80)

    # Input and output text boxes
    inputQuantity = tk.Text(self,
                   height = 5,
                   width = 20,
                   bg="light blue")
  
    inputQuantity.place(x= 120,y=210)


    apiKeyTextBox = tk.Text(self,
                            height =5,
                            width = 20)
    apiKeyTextBox.place(x=120,y=300)


    outputBox = tk.Text(self,
                        height = 25,
                        width = 25, bg="light yellow")
    outputBox.place(x=450, y=40)

    #submit button
    button = tk.Button(self, text='Submit', width=25,command=convert)
    button.pack(side=tk.BOTTOM)

    #dropdown menus
   
    options = [
    "USD",
    "EURO",
    "BHD",
    "OMR",
    "KWD",
    "JOD",
    "GBP",
    "KYD",
    "GIP",
    "CHF"
]
    selected_from = StringVar()
    selected_from.set( "USD" )
    from_drop = OptionMenu(self, selected_from, *options)
    from_drop.place(x=120, y=40)

    selected_to = StringVar()
    selected_to.set( "EURO" )
    to_drop = OptionMenu(self, selected_to, *options)
    to_drop.place(x=120,y=80)

if __name__ == "__main__":
  app = CurrencyConverter()
  app.mainloop()
