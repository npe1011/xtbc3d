import gc
import os
import traceback

import wx
from wx import xrc
from comtypes.client import CreateObject

try:
    _PYPERCLIP = True
    import pyperclip
except:
    _PYPERCLIP = False

import xtbopt
import config


class TextViewFrame(wx.Frame):
    def __init__(self, parent, title, text):
        wx.Frame.__init__(self, parent, -1, title)

        self.SetSize(config.TEXT_VIEW_FRAME_SIZE)
        self.init_frame()
        self.text_ctrl_main.SetValue(text)

    def init_frame(self):

        # set controls
        panel = wx.Panel(self, wx.ID_ANY)
        layout = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl_main = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_READONLY | wx.TE_MULTILINE )
        font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.text_ctrl_main.SetFont(font)
        layout.Add(self.text_ctrl_main, 1, wx.EXPAND | wx.ALL, border=3)
        panel.SetSizerAndFit(layout)

        # set menu and event
        file_menu = wx.Menu()
        save = file_menu.Append(11, '&Save\tCtrl+S')
        self.Bind(wx.EVT_MENU, self.on_menu_save, save)
        # set menu bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, '&File')
        self.SetMenuBar(menu_bar)

    def on_menu_save(self, event):

        global current_save_dir

        # get save file name
        dialog = wx.FileDialog(None, 'save file name',
                               wildcard='text (*.txt)||All files (*.*)|*.*',
                               style=wx.FD_SAVE)
        try:
            dialog.SetDirectory(current_save_dir)
        except:
            dialog.SetDirectory(config.INIT_SAVE_DIR)

        if dialog.ShowModal() == wx.ID_OK:
            file = dialog.GetPath()
            dialog.Destroy()
        else:
            dialog.Destroy()
            return

        # overwrite confirmation
        if os.path.exists(file):
            msgbox = wx.MessageDialog(None, 'File already exists. Overwrite?', 'Overwite?', style=wx.YES_NO)
            overwrite = msgbox.ShowModal()
            if overwrite == wx.ID_YES:
                msgbox.Destroy()
            else:
                msgbox.Destroy()
                return

        # update current save directory
        current_save_dir = os.path.dirname(file)

        with open(file, 'w') as f:
            f.write(self.text_ctrl_main.GetValue())


class ErrorViewFrame(wx.Frame):
    def __init__(self, parent, title, text):
        wx.Frame.__init__(self, parent, -1, title)
        self.SetSize(config.TEXT_VIEW_FRAME_SIZE)
        self.init_frame()
        self.text_ctrl_main.SetValue(text)

    def init_frame(self):
        # set controls
        panel = wx.Panel(self, wx.ID_ANY)
        layout = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl_main = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_READONLY | wx.TE_MULTILINE )
        font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.text_ctrl_main.SetFont(font)
        layout.Add(self.text_ctrl_main, 1, wx.EXPAND | wx.ALL, border=3)
        panel.SetSizerAndFit(layout)


class XTBC3DApp(wx.App):

    def OnInit(self):
        global chem3d
        self.chem3d = chem3d
        xtbopt.setenv()
        self.res = xrc.XmlResource(config.XRC_FILE)
        self.init_frame()
        return True

    def init_frame(self):

        self.frame = self.res.LoadFrame(None, 'frame')
        self.frame.SetSize(config.WINDOW_SIZE)

        self.get_controls_from_xrc()
        self.set_menu()
        self.set_event()
        self.init_controls()
        self.frame.Show()

    def get_controls_from_xrc(self):
        self.radio_box_xtb = xrc.XRCCTRL(self.frame, 'radio_box_xtb')
        self.text_ctrl_charge = xrc.XRCCTRL(self.frame, 'text_ctrl_charge')
        self.text_ctrl_multi = xrc.XRCCTRL(self.frame, 'text_ctrl_multi')
        self.choice_solvent = xrc.XRCCTRL(self.frame, 'choice_solvent')
        self.text_ctrl_constrain_atoms = xrc.XRCCTRL(self.frame, 'text_ctrl_constrain_atoms')
        self.button_run = xrc.XRCCTRL(self.frame, 'button_run')

    def set_menu(self):
        file_menu = wx.Menu()
        save = file_menu.Append(11, '&Save as xyz\tCtrl+S')
        self.Bind(wx.EVT_MENU, self.on_menu_save, save)
        edit_menu = wx.Menu()
        copy = edit_menu.Append(21, '&Copy as xyz\tCtrl+C')
        self.Bind(wx.EVT_MENU, self.on_menu_copy, copy)
        # set menu bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, '&File')
        menu_bar.Append(edit_menu, '&Edit')
        self.frame.SetMenuBar(menu_bar)

    def set_event(self):
        self.button_run.Bind(wx.EVT_BUTTON, self.run)

    def init_controls(self):
        self.radio_box_xtb.SetStringSelection('GFN2-xTB')
        self.text_ctrl_charge.SetValue('0')
        self.text_ctrl_multi.SetValue('1')
        self.text_ctrl_constrain_atoms.SetValue('')
        self.choice_solvent.Clear()
        self.choice_solvent.Append('none')
        with open(config.SOLVENT_LIST, 'r') as f:
            for line in f.readlines():
                if line.strip() == '':
                    continue
                self.choice_solvent.Append(line.strip())
        self.choice_solvent.SetStringSelection('none')

    # decorator to catch exception
    def with_logging_exceptions(func):
        def inner(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except Exception as e:
                # in debug mode, tracebacks are put in the log.
                if config.DEBUG:
                    tb = list(traceback.TracebackException.from_exception(e).format())
                    log = ''.join([str(t) for t in tb])
                    title = str(type(e))
                    evf = ErrorViewFrame(self.frame, title, log)
                    evf.Show(True)
                # in normal mode, only messages are logged.
                else:
                    title = str(type(e))
                    log = str(e.args)
                    evf = ErrorViewFrame(self.frame, title, log)
                    evf.Show()
                return None
            else:
                return result

        return inner

    @with_logging_exceptions
    def run(self, event):

        self.remove_lp()
        normal_termination, new_coordinates, xtb_log_data = \
            xtbopt.xtbopt(self.chem3d_atoms, self.chem3d_coordinates, self.xtb_ver, self.charge, self.multiplicity,
                    self.solvent, self.constrain_atoms)

        if normal_termination:
            self.chem3d_coordinates = new_coordinates
            wx.MessageBox('Optimization successfully finished.', 'Finished')

        else:
            flag = wx.MessageBox('Not terminated normally. Anyway read the final structure?',
                                 'xtb abnormal ternimation', wx.YES_NO | wx.YES_DEFAULT)
            if flag == wx.YES:
                if new_coordinates is not None:
                    self.chem3d_coordinates = new_coordinates
                    wx.MessageBox('Update finished.', 'Updated')
                else:
                    wx.MessageBox('New structure not found.', 'Failure')

            else:
                text_view = TextViewFrame(self.frame, 'XTB Log', ''.join(xtb_log_data))
                text_view.Show(True)

    def remove_lp(self):
        natoms = len(list(self.chem3d.ActiveDocument.Atoms))
        for n in range(natoms)[::-1]:
            if self.chem3d.ActiveDocument.Atoms[n].ElementSymbol.lower() == 'lp':
                self.chem3d.ActiveDocument.Atoms.Remove(n+1)

    @with_logging_exceptions
    def on_menu_save(self, event):
        global current_save_dir

        # get save file name
        dialog = wx.FileDialog(None, 'save file name',
                               wildcard='xyz (*.xyz)||All files (*.*)|*.*',
                               style=wx.FD_SAVE)
        try:
            dialog.SetDirectory(current_save_dir)
        except:
            dialog.SetDirectory(config.INIT_SAVE_DIR)

        if dialog.ShowModal() == wx.ID_OK:
            file = dialog.GetPath()
            dialog.Destroy()
        else:
            dialog.Destroy()
            return

        # overwrite confirmation
        if os.path.exists(file):
            msgbox = wx.MessageDialog(None, 'File already exists. Overwrite?', 'Overwite?', style=wx.YES_NO)
            overwrite = msgbox.ShowModal()
            if overwrite == wx.ID_YES:
                msgbox.Destroy()
            else:
                msgbox.Destroy()
                return

        # update current save directory
        current_save_dir = os.path.dirname(file)

        xtbopt.prep_xyz(self.chem3d_atoms, self.chem3d_coordinates, file, 'current structure')

    @with_logging_exceptions
    def on_menu_copy(self, event):

        if not _PYPERCLIP:
            wx.MessageBox('pyperclip is required to copy xyz.', 'pyperclip not found')
            return

        self.remove_lp()
        atoms = self.chem3d_atoms
        coordinates = self.chem3d_coordinates
        natoms = len(atoms)

        copy_string = str(natoms) + '\ncurrent structure\n'
        for i in range(natoms):
            copy_string += config.XYZ_FORMAT.format(atoms[i], *coordinates[i])

        pyperclip.copy(copy_string)

    @property
    def xtb_ver(self):
        value = self.radio_box_xtb.GetStringSelection()
        if value == 'GFN1-xTB':
            return '1'
        elif value == 'GFN2-xTB':
            return '2'
        else:
            return '2'

    @property
    def charge(self):
        value = self.text_ctrl_charge.GetValue()
        try:
            value = int(value)
        except:
            self.text_ctrl_charge.SetValue('0')
            value = 0
        return value

    @property
    def multiplicity(self):
        value = self.text_ctrl_multi.GetValue()
        try:
            value = int(value)
            assert value > 0
        except:
            self.text_ctrl_multi.SetValue('1')
            value = 1
        return value

    @property
    def solvent(self):
        return self.choice_solvent.GetStringSelection()

    @property
    def constrain_atoms(self):
        atom_string = self.text_ctrl_constrain_atoms.GetValue().strip()
        temp_block = [x.strip() for x in atom_string.split(',')]
        blocks = []
        atoms = set()
        for b in temp_block:
            blocks.extend(b.split())
        for block in blocks:
            if '-' in block:
                start, end = [int(x) for x in block.split('-')]
                for i in range(start, end + 1):
                    atoms.add(i)
            else:
                atoms.add(int(block))
        return sorted(list(atoms))

    @property
    def chem3d_atoms(self):
        atoms = self.chem3d.ActiveDocument.Atoms
        value = [a.ElementSymbol for a in atoms]
        gc.collect()
        return value

    @property
    def chem3d_coordinates(self):
        atoms = self.chem3d.ActiveDocument.Atoms
        coordinates = []
        for a in atoms:
            coordinates.append([a.XCoordinate, a.YCoordinate,a.ZCoordinate])
        return coordinates

    @chem3d_coordinates.setter
    def chem3d_coordinates(self, coordinates):
        _atoms = self.chem3d.ActiveDocument.Atoms
        for (n, coord) in enumerate(coordinates):
            _atoms[n].XCoordinate = coord[0]
            _atoms[n].YCoordinate = coord[1]
            _atoms[n].ZCoordinate = coord[2]


if __name__ == '__main__':

    current_save_dir = config.INIT_SAVE_DIR
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    chem3d = CreateObject(config.CHEM3D_COM_NAME)
    chem3d.Visible = True
    chem3d_doc = CreateObject(config.CHEM3D_DOC_COM_NAME)
    chem3d_doc.Activate()

    app = XTBC3DApp(False)
    app.MainLoop()

    try:
        chem3d.Quit()
    except Exception as e:
        if config.DEBUG:
            print(e)
    gc.collect()