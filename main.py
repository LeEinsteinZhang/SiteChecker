## =======================================================
## Program: Site Checker (main) - WCMS
## Author: Le Zhang (20916452)
## Email: l652zhan@uwaterloo.ca
## Update Time: Nov. 15 2023
## Company: University of Waterloo
## Faculty: MECHANICAL AND MECHATRONICS ENGINEERING
## =======================================================


from gui import *

def main():
    root = tk.Tk()
    app = SiteCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
