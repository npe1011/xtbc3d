import os
import argparse
import traceback

import xtbopt

def convert_atom_list(atom_string):
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


def input_param(args_param, name, defalut):
    if args_param is not None:
        return args_param
    else:
        value = input('Input {:} (default = {:}) : '.format(name, defalut))
        if value.strip() == '':
            return defalut
        return value


def main():
    ap = argparse.ArgumentParser(description='xtb optimization of xyz file')
    ap.add_argument('--xtb', '-x', help='xtb version')
    ap.add_argument('--charge', '-c', help='charge')
    ap.add_argument('--multiplicity', '--multi', '-m', help='spin multiplicity')
    ap.add_argument('--solvent', '-s', help='solvent (GBSA model)')
    ap.add_argument('--constrain', '--const', '-t', help='constrain atoms')
    ap.add_argument('file')
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print('xyz file not found.')
        return

    # Read xyz
    with open(args.file) as f:
        data = f.readlines()
    atoms = []
    coordinates = []
    try:
        num_atoms = int(data[0])
        for n in range(num_atoms):
            a, x, y, z = data[2+n].strip().split()
            atoms.append(a)
            coordinates.append([float(x), float(y), float(z)])
    except:
        print('Format Error. Input file should be in xyz format.')


    # get parameter
    xtb_ver = input_param(args.xtb, 'XTB version (1 or 2)', '2')
    charge = input_param(args.charge, 'charge', '0')
    multi = input_param(args.multiplicity, 'spin multiplicity', '1')
    solvent = input_param(args.charge, 'solvent', 'none')
    const_string = input_param(args.constrain, 'constrain numbers', '')

    # convert atom number list
    constrain_atoms = convert_atom_list(const_string)

    # file output directory
    output_dir = os.path.dirname(os.path.abspath(args.file))

    # Run XTB
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    xtbopt.setenv()
    normal_termination, new_coordinates, xtb_log_data = \
        xtbopt.xtbopt(atoms, coordinates, xtb_ver, charge, multi, solvent, constrain_atoms)

    # set file names
    root = os.path.splitext(os.path.basename(args.file))[0]
    new_xyz_file = os.path.join(output_dir, root + '_xtbopt.xyz')
    log_file = os.path.join(output_dir, root + '_xtbopt.log')

    # output files
    with open(log_file, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(xtb_log_data)
    if new_coordinates is not None:
        xtbopt.prep_xyz(atoms, coordinates, new_xyz_file, 'optimized structure by xtb')
    else:
        print('No new structure available...')

    if not normal_termination:
        print('Some errors in the XTB calculation. Plase check the log file.')


if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
    finally:
        _ = input('Finished.')


