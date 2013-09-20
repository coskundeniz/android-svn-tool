#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pysvn
import urllib2
from Tkinter import *
from tkFileDialog import askdirectory
import xml.etree.ElementTree as ET


class SvnGui(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.parent_dir = None

        self.client = pysvn.Client()

        self.variables = {}
        self.row = 0

        self.url = StringVar()
        self.workspace_name = StringVar()

        self.init_ui()

    def init_ui(self):
        """ initialize gui """

        self.parent.title("Create Workspace")
        self.pack(fill=BOTH, expand=1)

        self.place_url_lbl()
        self.place_url_entry()

        self.place_workspace_lbl()
        self.place_workspace_entry()

        self.bottom_frame = Frame(self, width=680, height=50)
        self.bottom_frame.grid(row=3, columnspan=2, padx=10)

        self.place_list_button()
        self.place_browse_button()
        self.place_exit_button()

    def place_url_lbl(self):
        package_name_lbl = Label(self,
                                 text="URL ")
        package_name_lbl.grid(row=0, column=0, ipady=5,
                              pady=10, padx=5,  sticky=W+E)

    def place_url_entry(self):
        url_entry = Entry(self,
                          textvariable=self.url,
                          bg="white",
                          width=100,
                          justify=LEFT)
        url_entry.grid(row=0, column=1, pady=10, sticky=W)

    def place_workspace_lbl(self):
        package_workspace_lbl = Label(self,
                                      text="Workspace ")
        package_workspace_lbl.grid(row=2, column=0, ipady=5,
                                   pady=10, padx=5, sticky=W+E)

    def place_workspace_entry(self):
        workspace_entry = Entry(self,
                                textvariable=self.workspace_name,
                                bg="white",
                                width=30,
                                justify=CENTER)
        workspace_entry.grid(row=2, column=1, pady=10, sticky=W)

    def place_list_button(self):
        self.list_button = Button(self.bottom_frame,
                                  text="List",
                                  width=10,
                                  command=self.project_selection_window)
        self.list_button.grid(row=0, column=1, padx=10, pady=10, sticky=W)

    def place_browse_button(self):
        self.browse_button = Button(self.bottom_frame,
                                    text="Parent",
                                    width=10,
                                    command=self.ask_directory)
        self.browse_button.grid(row=0, column=0, pady=10, sticky=W)

    def place_create_button(self):
        create_button = Button(self.frame,
                               text="CREATE WORKSPACE",
                               width=30,
                               command=self.create_workspace)
        create_button.grid(row=self.row, columnspan=2, ipadx=30,
                           padx=20, pady=20, sticky=W+E)

    def place_exit_button(self):
        exit_button = Button(self.bottom_frame,
                             text="Exit",
                             width=10,
                             command=self.parent.quit)
        exit_button.grid(row=0, column=2, pady=10, sticky=W)

    def get_workspace(self):
        return self.workspace_name.get()

    def get_project_name(self, path):

        url = path + '/.project'
        response = urllib2.urlopen(url)
        data = response.read()

        f = open("project.xml", "w")
        f.write(data)
        f.close()

        xml_tree = ET.parse("project.xml")

        if(os.name == "nt"):
            os.system("del %s" % os.path.join(os.getcwd(), 'project.xml'))
        if(os.name == "posix" or os.name == "mac"):
            os.system("rm %s" % os.path.join(os.getcwd(), 'project.xml'))

        root = xml_tree.getroot()

        # return project name
        return root[0].text

    def create_workspace(self):

        # create parent workspace directory
        ws_parent_dir = self.parent_dir

        # main_dir_path/workspace_name
        created_ws = os.path.join(ws_parent_dir, self.get_workspace())
        os.system("mkdir %s" % created_ws)

        # get selevted projects
        selected_projects = self.get_selected_directories()

        for project in selected_projects:
            # extract project name from .project file
            project_name = self.get_project_name(project)

            # create directory for project
            os.system("mkdir %s" % os.path.join(created_ws, project_name))

            # checkout from url to parent_dir_path/workspace_dir/project_name
            self.client.checkout(project, os.path.join(created_ws, project_name))

        self.top_win.destroy()

    def get_dir_list(self, parent_dir):
        return self.client.ls(parent_dir)

    def populate_checkboxes(self, root_url=None, level=1):
        if root_url is None:
            root_url = self.url.get()

        dirs = self.get_dir_list(root_url)
        level += 25

        for dir in dirs:
            content_info = self.client.info2(dir.name, recurse=False)

            # if content is a directory, place a checkbutton for it
            if(content_info[0][1]['kind'] == pysvn.node_kind.dir):
                offset = dir.name.rfind('/') + 1

                checked = IntVar()
                self.place_checkbox(dir.name[offset:], # text beside checkbox
                                    variable=checked,  # associated variable with checkbox
                                    level_padx=level)  # padx for proper indent

                self.variables.update({dir.name: checked})
                self.row += 1

                self.populate_checkboxes(dir.name, level)
            else:
                level -= 25
                return

        # disable List button
        self.list_button.config(state="disabled")

    def place_checkbox(self, dirname, variable, level_padx):
        sign_checkbox = Checkbutton(self.frame,
                                    text=dirname,
                                    variable=variable,
                                    bg="white")
        sign_checkbox.grid(row=self.row, columnspan=2, ipadx=level_padx, sticky=W)

    def ask_directory(self):

        if(os.name == "nt"):
            self.parent_dir = askdirectory(initialdir='C:\\',
                                           title='Select Parent Directory')
        elif(os.name == "mac"):
            self.parent_dir = askdirectory(initialdir='/Users/%s' % os.getlogin(),
                                           title='Select Parent Directory')
        else:
            self.parent_dir = askdirectory(initialdir='/home/%s' % os.environ['USER'],
                                           title='Select Parent Directory')

        # disable browse button
        self.browse_button.config(state="disabled")

    def get_selected_directories(self):

        selected_dirs = []

        for dir_path, checked in self.variables.iteritems():
            if(checked.get()):
                selected_dirs.append(dir_path)

        return selected_dirs

    def project_selection_window(self):

        self.top_win = Toplevel(bg="white")
        self.top_win.transient(self.parent)

        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        x = (screen_width - 450) / 2
        y = (screen_height - 500) / 2

        self.top_win.geometry("450x600+%d+%d" %(x, y))

        self.canvas = Canvas(self.top_win, bd=0, bg="white")
        self.frame = Frame(self.canvas, bg="white")

        self.scrollbar = Scrollbar(self.top_win, orient="vertical",
                                   command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.create_window((50,0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", self.frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        self.populate_checkboxes()
        self.place_create_button()

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta/120), "units")

    def frame_configure(self, event):
        ''' Reset the scroll region to encompass the inner frame '''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def run():
    root = Tk()

    width = 900
    height = 150

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - width) / 2
    y = (screen_height - height) / 2

    root.geometry("%dx%d+%d+%d" %(width, height, x, y))
    root.resizable(width=FALSE, height=FALSE)

    app = SvnGui(root)
    root.mainloop()


if __name__ == '__main__':
    run()
