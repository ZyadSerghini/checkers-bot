from OtherStuff import CheckersGUI
import tkinter as tk

def main():
    """Launch the checkers game GUI application.
    
    Creates the main Tkinter window and initializes the CheckersGUI interface,
    then starts the event loop for user interaction.
    """
    root = tk.Tk()
    app = CheckersGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
