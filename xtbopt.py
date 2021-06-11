import os
import sys
import subprocess

import config

# CONST
INIT_XYZ_FILE = 'init.xyz'
CONSTRAIN_FILE = 'constrain.txt'
XTB_OPT_FILE = 'xtbopt.xyz'
XTB_TRAJ_FILE = 'xtbopt.log'
XTB_LOG_FILE = 'xtboptlog.txt'

def setenv():
    if not config.PATH in os.environ['PATH']:
        os.environ['PATH'] = '{:};{:}'.format(config.PATH, os.environ['PATH'])
    os.environ['XTBPATH'] = config.XTBPATH
    os.environ['OMP_NUM_THREADS'] = str(config.OMP_NUM_THREADS) + ',1'
    os.environ['OMP_STACKSIZE'] = str(config.OMP_STACKSIZE)
    os.environ['MKL_NUM_THREADS'] = str(config.OMP_NUM_THREADS)


def set_work_dir_name():
    count = 0
    dir = os.path.join(config.WORK_DIR, str(count))
    while(os.path.exists(dir)):
        count += 1
        dir = os.path.join(config.WORK_DIR, str(count))
    os.makedirs(dir)
    return dir


def xtbopt(atoms, coordinates, xtb_ver, charge, multi, solvent, constrain_atom_numbers):
    odir = os.getcwd()
    try:
        work_dir = set_work_dir_name()
        os.chdir(work_dir)
        prep_xyz(atoms=atoms, coordinates=coordinates, xyz_file=INIT_XYZ_FILE, title='initial structure')
        if len(constrain_atom_numbers) > 0:
            prep_constrain_file(constrain_atom_numbers=constrain_atom_numbers, constrain_file=CONSTRAIN_FILE)
            constrain = True
        else:
            constrain = False

        # prep xtb command
        xtb_commands = ['xtb', '--opt']
        if constrain:
            xtb_commands.extend(['--input', CONSTRAIN_FILE])
        spin = str(int(multi) - 1)
        charge = str(charge)
        xtb_commands.extend(['--chrg', charge, '--uhf', spin])
        if (solvent.lower() != 'none') and (solvent.strip() != ''):
            xtb_commands.extend(['-g', solvent])
        xtb_commands.extend(['--gfn', str(xtb_ver)])
        xtb_commands.append(INIT_XYZ_FILE)

        # RUN XTB
        xtb_log_data = []
        process = subprocess.Popen(xtb_commands, encoding='utf-8', bufsize=1, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True: 
            line = process.stdout.readline()
            xtb_log_data.append(line)
            print(line, end='')
            if not line and process.poll() is not None:
                break
        with open(XTB_LOG_FILE, 'w', encoding='utf-8', newline='\n') as f:
            f.writelines(xtb_log_data)

        """
        # RUN XTB
        with open(XTB_LOG_FILE, 'w') as f:
            subprocess.run(xtb_commands, stdout=f)

        with open(XTB_LOG_FILE, 'r', encoding='utf-8') as f:
            xtb_log_data = f.readlines()
        """

        normal_termination = False
        for line in xtb_log_data[::-1]:
            if 'normal termination of xtb' in line.lower():
                normal_termination = True
                break

        if normal_termination:
            new_coordinates = read_xyz_coordinates(XTB_OPT_FILE)
        else:
            try:
                new_coordinates = read_final_xyz_coordinates(XTB_TRAJ_FILE)
            except:
                new_coordinates = None

    except Exception as e:
        raise e
    finally:
        os.chdir(odir)

    return normal_termination, new_coordinates, xtb_log_data


def prep_xyz(atoms, coordinates, xyz_file, title=''):
    data = []
    data.append(str(len(atoms)) + '\n')
    data.append(title.rstrip() + '\n')
    for i in range(len(atoms)):
        data.append(config.XYZ_FORMAT.format(atoms[i], *coordinates[i]))
    with open(xyz_file, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(data)


def read_xyz_coordinates(xyz_file):
    with open(xyz_file, 'r') as f:
        data = f.readlines()
    coordinates = []
    num_atoms = int(data[0].strip())
    for line in data[2:2+num_atoms]:
        temp = line.strip().split()
        x = float(temp[1])
        y = float(temp[2])
        z = float(temp[3])
        coordinates.append([x, y, z])
    return coordinates


def read_final_xyz_coordinates(trajectory_xyz_file):
    with open(trajectory_xyz_file, 'r') as f:
        data = f.readlines()
    coordinates = []
    num_atoms = int(data[0].strip())

    start_final = -1
    for (i, line) in enumerate(data):
        if line.strip().lower().startswith('energy:'):
            start_final = i

    for line in data[start_final:start_final+num_atoms]:
        temp = line.strip().split()
        x = float(temp[1])
        y = float(temp[2])
        z = float(temp[3])
        coordinates.append([x, y, z])
    return coordinates


def prep_constrain_file(constrain_atom_numbers, constrain_file):
    data= []
    data.append('$fix\n')
    data.append('    atoms: ' + ','.join([str(c) for c in constrain_atom_numbers]) + '\n')
    data.append('$end\n')
    with open(constrain_file, 'w') as f:
        f.writelines(data)