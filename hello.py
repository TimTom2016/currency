import customtkinter
import requests
from tkinter import messagebox
import json
from datetime import datetime

class CurrencyConverter(customtkinter.CTk):
    def __init__(self):
        # Set the appearance settings
        customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

        # Set scaling factors
        customtkinter.set_widget_scaling(1.3)
        customtkinter.set_window_scaling(1.3)

        super().__init__()
        self.title("Currency Converter")
        self.geometry("550x380")
        self.grid_columnconfigure((0, 1), weight=1)

        # Initialize exchange rates
        self.exchange_rates = {}
        self.last_updated = None
        self.currencies = []

        # Status label for API connection
        self.status_label = customtkinter.CTkLabel(self, text="Fetching exchange rates...", text_color="orange")
        self.status_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # Amount input
        self.amount_label = customtkinter.CTkLabel(self, text="Amount:")
        self.amount_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.amount_entry = customtkinter.CTkEntry(self, placeholder_text="Enter amount")
        self.amount_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.amount_entry.insert(0, "1")

        # From currency dropdown
        self.from_label = customtkinter.CTkLabel(self, text="From Currency:")
        self.from_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.from_currency = customtkinter.CTkOptionMenu(self, values=["Loading..."])
        self.from_currency.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        # To currency dropdown
        self.to_label = customtkinter.CTkLabel(self, text="To Currency:")
        self.to_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.to_currency = customtkinter.CTkOptionMenu(self, values=["Loading..."])
        self.to_currency.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        # Swap currencies button
        self.swap_button = customtkinter.CTkButton(
            self, text="↑↓", width=50, command=self.swap_currencies
        )
        self.swap_button.grid(row=2, column=2, rowspan=2, padx=(0, 20), pady=10)

        # Convert button
        self.convert_button = customtkinter.CTkButton(self, text="Convert", command=self.convert_currency)
        self.convert_button.grid(row=4, column=0, columnspan=3, padx=20, pady=20, sticky="ew")

        # Result label
        self.result_label = customtkinter.CTkLabel(self, text="", font=("Helvetica", 16))
        self.result_label.grid(row=5, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        # Last updated info
        self.updated_label = customtkinter.CTkLabel(self, text="", text_color="gray")
        self.updated_label.grid(row=6, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="ew")

        # Refresh rates button
        self.refresh_button = customtkinter.CTkButton(
            self, text="Refresh Rates", command=self.fetch_exchange_rates
        )
        self.refresh_button.grid(row=7, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")

        # Fetch exchange rates when starting the app
        self.after(100, self.fetch_exchange_rates)

    def fetch_exchange_rates(self):
        """Fetch real-time exchange rates from the API"""
        try:
            self.status_label.configure(text="Fetching exchange rates...", text_color="orange")
            self.update_idletasks()

            # Using a free currency API (Exchange Rate API)
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.exchange_rates = data["rates"]
                self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Update currency lists
                self.currencies = sorted(list(self.exchange_rates.keys()))

                # Update dropdowns
                self.from_currency.configure(values=self.currencies)
                self.to_currency.configure(values=self.currencies)

                # Set default values
                self.from_currency.set("USD")
                self.to_currency.set("EUR")

                # Update status
                self.status_label.configure(text="Exchange rates loaded successfully!", text_color="green")
                self.updated_label.configure(text=f"Last updated: {self.last_updated}")
            else:
                self.status_label.configure(text=f"API Error: {response.status_code}", text_color="red")
        except requests.exceptions.RequestException as e:
            self.status_label.configure(text=f"Connection error: {str(e)}", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def swap_currencies(self):
        """Swap the 'from' and 'to' currencies"""
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        self.from_currency.set(to_curr)
        self.to_currency.set(from_curr)

        # If there's already a result, recalculate with swapped currencies
        if self.result_label.cget("text"):
            self.convert_currency()

    def convert_currency(self):
        """Convert the currency based on the current exchange rates"""
        try:
            if not self.exchange_rates:
                messagebox.showerror("Error", "Exchange rates not loaded yet. Please try again later.")
                return

            # Get input values
            amount = float(self.amount_entry.get())
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()

            # Convert using the rates
            from_rate = self.exchange_rates[from_curr]
            to_rate = self.exchange_rates[to_curr]

            # First convert to USD (base currency), then to target currency
            result = amount * (to_rate / from_rate)

            # Format result with appropriate decimal places
            if result < 0.01:
                formatted_result = f"{amount:.2f} {from_curr} = {result:.6f} {to_curr}"
            else:
                formatted_result = f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}"

            self.result_label.configure(text=formatted_result)

        except ValueError:
            self.result_label.configure(text="Please enter a valid number")
        except KeyError:
            self.result_label.configure(text="Selected currency not available")
        except Exception as e:
            self.result_label.configure(text=f"Error: {str(e)}")

def main():
    app = CurrencyConverter()
    app.mainloop()

if __name__ == "__main__":
    main()
