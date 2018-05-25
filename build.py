#!/usr/bin/python3

# TODO: clean temporary files


import sys
import os
import subprocess
import glob
import shutil
import re
import errno
import json

def custom_key(str):
    return +len(str), str.lower()


def parse_json(json_file):
    json_data = {}

    if(not os.path.isfile(json_file)):
        print(json_file,'does not exists.')
        sys.exit(1)

    with open(json_file) as f:
        json_data = json.load(f)
    return json_data

class default_boca_limits:
    time_limit = 1 # time limit for all tests
    number_of_repetitions = 1 # number of repetitions
    maximum_memory = 512 # Maximum memory size (MB)
    maximum_ouput_size = 4096 # Maximum output size (KB)

def boca_zip(boca_folder):
    old_cwd = os.getcwd()
    os.chdir(boca_folder)
    zip_filename = os.path.basename(boca_folder)+'.zip'
    subprocess.run('zip'+' -r ' + zip_filename + ' . ',shell=True)
    os.rename(zip_filename,os.path.join('..',zip_filename))
    os.chdir(old_cwd)

def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
    else:
        shutil.copyfile(src, dest)

def copy_directory(source, dest):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            rel_path = root.replace(source, '').lstrip(os.sep)
            dest_path = os.path.join(dest, rel_path)

            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)
            if(dirs and files):
                shutil.copyfile(os.path.join(root, file), os.path.join(dest_path, file))

class statement_metadata:
    def __init__(self,problem_id='',title='',timelimit=0,author=''):
        self.problem_id = problem_id
        self.title = title
        self.timelimit = timelimit
        self.author = author

def parse_yaml(f):
    # read the first ---
    line = f.readline()
    d = {}
    while(True):
        line = f.readline().rstrip()
        if('---' in line):
            break
        lhs = line.split(": ")[0]
        rhs = line.split(": ")[1]
        rhs = rhs.strip('\"')
        d[lhs] = rhs
        # print(d[lhs])
    smd =  statement_metadata(d['problem_id'],d['title'],int(d['timelimit']),d['author'])
    return smd

def get_io(io_folder,problem_metadata):
    l = []
    io_samples = problem_metadata["io_samples"]
    io_files = [os.path.join(io_folder,str(f)) for f in range(1,io_samples+1)]
    print(os.getcwd())
    for f in io_files:
        print(f)
        tc_io = []
        with open(f) as inf:
            for line in inf.readlines():
                tc_io.append(line.strip())
        l.append(tc_io)
    return l

def print_line(line,f_out):
    line = re.sub(r'\*\*(.+)\*\*', r'\\textbf{\1}',line)
    line = re.sub(r'\*(.+)\*', r'\\textit{\1}',line)
    print(line,file=f_out,end='')
    
# Parse the markdown file to a .tex file
def print_to_latex(problem_folder, md_file):
    input_folder = os.path.join(problem_folder,'input')
    output_folder = os.path.join(problem_folder,'output')
    problem_metadata = parse_json(os.path.join(problem_folder,'problem.json'))
    with open(md_file) as f_in, open(os.path.join(os.path.dirname(md_file), problem_metadata["problem"]["label"]+'.tex'),'w') as f_out:
        print("\\documentclass{maratona}",file=f_out)
        print("\\begin{document}\n",file=f_out)
        print("\\begin{Problema}{"+ problem_metadata["problem"]["label"] 
            +"}{" + problem_metadata["problem"]["title"] + "}{"+ 
            str(problem_metadata["problem"]["time_limit"]) + 
            "}{" + problem_metadata["author"]["name"] + "}",file=f_out)
        for line in f_in:
            if(line.startswith('# Descrição')):
                pass
            elif(line.startswith('# Entrada')):
                print("\\Entrada\n",file=f_out)
            elif(line.startswith('# Saída')):
                print("\\Saida\n",file=f_out)
            else:
                print_line(line,f_out)
        in_list = get_io(input_folder,problem_metadata)
        out_list = get_io(output_folder,problem_metadata)
        print("\n\n\\ExemploEntrada",file=f_out)
        print("\\begin{Exemplo}",file=f_out)
        for tc in range(0,len(in_list)):
            tc_input = in_list[tc]
            tc_output = out_list[tc]
            print(tc_input)
            max_lines = max(len(tc_input),len(tc_output))
            for i in range(0,max_lines):
                if(tc % 2):
                    print('\\rowcolor{gray!20}',end='',file=f_out)
                if(i<len(tc_input)):
                    print('\\texttt{'+tc_input[i]+'}',end='',file=f_out)
                print(' & ',end='',file=f_out)
                if(i<len(tc_output)):
                    print('\\texttt{'+ tc_output[i] + '}',end='',file=f_out)
                print ( '\\\\',file=f_out)
        print("\\end{Exemplo}",file=f_out)
        print("\\end{Problema}",file=f_out)
        print("\\end{document}",file=f_out)

# Builds a pdf file from a markdown
def build_pdf(problem_folder):
    problem_metadata = parse_json(os.path.join(problem_folder,'problem.json'))
    md_list = glob.glob(os.path.join(problem_folder,'*.md'))
    filepath = md_list[0]
    print('fp = ' ,filepath)
    if(not os.path.exists(filepath)):
        print("Statement file does not exists")
        sys.exit(1)
    print_to_latex(problem_folder,filepath)
    cwd = os.getcwd()
    os.chdir(problem_folder)
    subprocess.run(["pdflatex",problem_metadata["problem"]["label"]+".tex"])
    os.chdir(cwd)    

def build_executables(problem_folder):
    build_folder = os.path.join(problem_folder,'build')
    build_debug_folder = os.path.join(problem_folder,'build_debug')
    os.makedirs(build_folder,exist_ok=True)
    os.makedirs(build_debug_folder,exist_ok=True)

    # store cwd
    old_cwd = os.getcwd() 

    # change cwd to build folder
    os.chdir(build_debug_folder) 

    # run cmake and install executables
    subprocess.run(['cmake','..','-DCMAKE_BUILD_TYPE=DEBUG'])
    subprocess.run(['make','-j'])
    subprocess.run(['make','install'])
    # run cmake and install executables

    # restore cwd
    os.chdir(old_cwd) 
    # change cwd to build folder
    os.chdir(build_folder)
    # run cmake and install executables
    subprocess.run(['cmake','..','-DCMAKE_BUILD_TYPE=RELEASE'])
    subprocess.run(['make','-j'])
    subprocess.run(['make','install'])
    # restore cwd
    os.chdir(old_cwd) 

def run_programs(problem_folder):
    input_folder = os.path.join(problem_folder,'input')
    output_folder = os.path.join(problem_folder,'output')
    # Generate input and output folders
    os.makedirs(input_folder,exist_ok=True)
    os.makedirs(output_folder,exist_ok=True)
    # store old cwd
    old_cwd = os.getcwd()

    #change cwd to input folder
    os.chdir(input_folder)
    # run generator 
    generator_path = os.path.join('../bin','generator')
    print("Running generator",problem_folder)
    subprocess.run(generator_path)

    # Run validator on generated inputs
    input_files = [f for f in os.listdir() if os.path.isfile(f)]
    input_files.sort(key=custom_key)
    for fname in input_files:
        with open(fname) as f:
            print("Validating input ",fname)
            p = subprocess.Popen([os.path.join('../bin','validator')],stdin=f,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
            out,err = p.communicate()
            print(out,err)

    # change cwd to output folder
    os.chdir(old_cwd)
    os.chdir(output_folder)
    # Run ac solution on inputs to produce outputs
    for fname in input_files:
        with open(os.path.join('../input',fname),'r') as inf, open(fname,'w') as ouf:
            print('Producing output on input',fname)
            ac_solution = os.path.join('../bin','ac')
            p = subprocess.Popen([ac_solution],stdin=inf,stdout=ouf)
            _,err = p.communicate()
            print(out,err)
    os.chdir(old_cwd)



def build(problem_id):
    problem_folder = os.path.join('Problemas',problem_id)
    build_executables(problem_folder)
    run_programs(problem_folder)
    build_pdf(problem_folder)
    shutil.copy2(os.path.join(problem_folder,problem_id+'.pdf'), 'Maratona') 

def merge_pdfs():
    # Remove merge pdf file if already existed
    if(os.path.exists('Maratona/Maratona.pdf')):
        os.remove('Maratona/Maratona.pdf')

    print("Merging PDFs")
    old_cwd = os.getcwd()
    os.chdir('Maratona')
    subprocess.run(['pdflatex','Capa.tex'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    os.chdir(old_cwd)
    pdfs = [os.path.join('Maratona',f) for f in os.listdir('Maratona')]
    pdfs = sorted([f for f in pdfs if f.endswith('.pdf') if f!='Maratona/Capa.pdf'])
    command = ['pdfjam','Maratona/Capa.pdf']
    for f in pdfs:
        command+=[f]
    command += ['-o','Maratona/Maratona.pdf']
    subprocess.run(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print("PDFs Merged")

def build_all():
    problem_ids = [f for f in os.listdir('Problemas') if os.path.isdir(os.path.join('Problemas',f))]
    for id in problem_ids:
        build(id)
    merge_pdfs()

# Create the structure for the folder of a problem
def init(problem_folder):
    folder = 'arquivos'
    new_folder = os.path.join('Problemas',problem_folder)
    shutil.copytree(folder,new_folder,ignore=shutil.ignore_patterns('boca')) 
    # Rename files and folders


def pack2boca(problem_id):
    build(problem_id)
    # Create Boca folder
    boca_template_folder = os.path.join(*['arquivos','boca'])
    boca_folder = os.path.join(*['boca',problem_id]) 
    problem_folder = os.path.join(*['Problemas',problem_id])
    # Copy template files
    recursive_overwrite(boca_template_folder,boca_folder)
    # Get problem metadata
    problem_md = glob.glob(os.path.join(problem_folder,'*.md'))[0]
    tl = 0
    smd = statement_metadata()
    with open(problem_md) as f:
        smd = parse_yaml(f)

    # Compile, Run and Tests Remains the Same

    # Description
    boca_description_folder = os.path.join(boca_folder,'description')
    with open(os.path.join(boca_description_folder,'problem.info'),'w+') as f:
        f.write('basename='+smd.problem_id+'\n')
        f.write('fullname='+smd.problem_id+'\n')
        f.write('descfile='+smd.problem_id+'.pdf\n')
    
    pdf_file = os.path.join(problem_folder,smd.problem_id+'.pdf')
    shutil.copy2(pdf_file,boca_description_folder)

    # Compare
    shutil.copy2(os.path.join(*[problem_folder,'bin','checker']),os.path.join(boca_folder,'compare'))
    shutil.copy2(os.path.join(*[boca_folder,'compare','checker']),os.path.join(*[boca_folder,'compare','c']))
    shutil.copy2(os.path.join(*[boca_folder,'compare','checker']),os.path.join(*[boca_folder,'compare','cpp']))
    shutil.copy2(os.path.join(*[boca_folder,'compare','checker']),os.path.join(*[boca_folder,'compare','java']))
    shutil.copy2(os.path.join(*[boca_folder,'compare','checker']),os.path.join(*[boca_folder,'compare','py2']))
    shutil.copy2(os.path.join(*[boca_folder,'compare','checker']),os.path.join(*[boca_folder,'compare','py3']))
    # Limits
    
    java_python_time_factor = 3
    for filename in os.listdir(os.path.join(boca_template_folder,'limits')):
        with open(os.path.join(*[boca_folder,'limits',filename]),'w+') as f:
            tl = smd.timelimit
            if(filename in ['java','py2','py3']):
                tl = smd.timelimit * java_python_time_factor
            f.write('echo ' + str(tl) + '\n')
            f.write('echo ' + str(default_boca_limits.number_of_repetitions)+'\n')
            f.write('echo ' + str(default_boca_limits.maximum_memory)+'\n')
            f.write('echo ' + str(default_boca_limits.maximum_ouput_size)+'\n')
            f.write('exit 0\n')

    # Input
    boca_input_folder = os.path.join(boca_folder,'input')
    problem_input_folder = os.path.join(problem_folder,'input')
    input_files = [os.path.join(problem_input_folder,f) for 
        f in os.listdir(problem_input_folder) if os.path.isfile(os.path.join(problem_input_folder,f))]
    print('input_files = ',' '.join(input_files))
    for filename in input_files:
        shutil.copy2(filename,boca_input_folder)

    # Output
    boca_output_folder = os.path.join(boca_folder,'output')
    problem_output_folder = os.path.join(problem_folder,'output')
    output_files = [os.path.join(problem_output_folder,f) for 
        f in os.listdir(problem_output_folder) if os.path.isfile(os.path.join(problem_output_folder,f))]
    print('output_files = ',' '.join(output_files))
    for filename in output_files:
        shutil.copy2(filename,boca_output_folder)
    boca_zip(boca_folder)


def packall2boca():
    problem_ids = [f for f in os.listdir('Problemas') if os.path.isdir(os.path.join('Problemas',f))]
    for id in problem_ids:
        pack2boca(id)


def pack2uri(problem_id):
    print('Not implemented')
    pass

def packall2uri():
    print('Not implemented')
    pass

if __name__=="__main__":
    op = sys.argv[1]
    if(len(sys.argv)>2):
        problem_id = sys.argv[2]
    if(op == 'init'):
        print("Initializing problem",problem_id)
        init(problem_id)
    elif(op == 'build'):
        print("Bulding problem",problem_id)
        build(problem_id)
    elif(op == 'buildall'):
        build_all()
    elif(op == 'pack2boca'):
        pack2boca(problem_id)
    elif(op == 'packall2boca'):
        packall2boca()
    elif(op == 'pack2uri'):
        pack2uri(problem_id)
    elif(op == 'packall2uri'):
        packall2uri()