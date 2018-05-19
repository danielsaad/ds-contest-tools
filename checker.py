#!/usr/bin/python3


# TODO: clean temporary files

import os
import subprocess
import sys
import time
import shutil

""" Global definitions """

""" C definitions """
C_COMPILER = ['gcc']
C_FLAGS = ['-O2','-DNDEBUG']
C_LFLAGS = ['-lm']

""" CPP definitions """
CPP_COMPILER = ['g++']
CPP_FLAGS = ['-O2','-DNDEBUG','-std=c++11']
CPP_LFLAGS = ['-lm']

""" Java definitions """
JAVA_COMPILER = ['javac']
JAVA_INTERPRETER = ['java']

""" Python2 definitions """
PYTHON2_INTERPRETER = ['python2']

""" Python3 definitions """
PYTHON3_INTERPRETER = ['python3']


submissions_folder = 'submissoes'
problems_folder = 'Problemas'

def custom_key(str):
    return +len(str), str.lower()

def compile_c(submission_file,binary_file):
    """ Compile a source code 'submission_file' into its 
        corresponding 'binary_file' """
    command = C_COMPILER + C_FLAGS + [submission_file] + ['-o',binary_file] + C_LFLAGS
    print('Compiling: ', ' '.join(command))
    p = subprocess.run(command)
    if(p.returncode):
        print('CE: C Compilation of',submission_file,'Failed')
        sys.exit(1)
    else:
        print(binary_file,'generated')

def compile_cpp(submission_file,binary_file):
    # submission_folder = os.path.basename(submission_file)
    command = CPP_COMPILER + CPP_FLAGS + [submission_file] + ['-o',binary_file] + CPP_LFLAGS
    p = subprocess.run(command)
    print('Compiling: ',' '.join(command))
    if(p.returncode):
        print('CE: C++ Compilation of',submission_file,'Failed')
        sys.exit(1)
    else:
        print(binary_file,'generated')


def compile_java(submission_file,problem_id):
    """ Compile a java file into problem_id.class """
    renamed_file = os.path.join(os.path.dirname(submission_file),problem_id) + '.java'
    shutil.copy2(submission_file,renamed_file)
    command = JAVA_COMPILER + [renamed_file]
    print('Compiling: ',' '.join(command))
    p = subprocess.run(command)
    if(p.returncode):
        print('CE: Java Compilation of',renamed_file,'Failed')
        sys.exit(1)
    else:
        print(renamed_file,'class file','generated')

def run_binary(binary_file,input_folder,output_folder):
    input_files = [os.path.join(input_folder,f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder,f))]
    # Create temp dir
    tmp_dir = os.path.join(os.path.dirname(binary_file),'tmp')
    print('Creating temporary directory')
    os.makedirs(tmp_dir,exist_ok=True)
    input_files.sort(key=custom_key)
    for fname_in in input_files:
        fname_out = os.path.join(tmp_dir,os.path.basename(fname_in))
        print('Running test',os.path.basename(fname_in))
        local_time_start = time.perf_counter()
        with open(fname_in,'r') as inf, open(fname_out,'w') as ouf:
            p = subprocess.run([binary_file],stdin=inf,stdout=ouf)
        local_time_end = time.perf_counter()
        if(p.returncode):
            print('RE: Runtime error')
            exit(0)
        print('Time elapsed: {0:.2f}'.format(local_time_end-local_time_start),'seconds')

def run_java(class_name,input_folder,output_folder):
    input_files = [os.path.join(input_folder,f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder,f))]
    # Create temp dir
    tmp_dir = os.path.join(os.path.dirname(class_name),'tmp')
    os.makedirs(tmp_dir,exist_ok=True)
    input_files.sort(key=custom_key)
    for fname_in in input_files:
        fname_out = os.path.join(tmp_dir,os.path.basename(fname_in))
        print("Running test",os.path.basename(fname_in))
        local_time_start = time.perf_counter()
        with open(fname_in,'r') as inf, open(fname_out,'w') as ouf:
            command = JAVA_INTERPRETER + ['-classpath',os.path.dirname(class_name)] + [os.path.basename(class_name)]
            print(command)
            p = subprocess.run(command,stdin=inf,stdout=ouf)
        local_time_end = time.perf_counter()
        if(p.returncode):
            print('RE: Runtime error')
            exit(0)
        print('Time elapsed: {0:.2f}'.format(local_time_end-local_time_start),'seconds')


def run_python2(submission_file,input_folder,output_folder):
    input_files = [os.path.join(input_folder,f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder,f))]
    # Create temp dir
    tmp_dir = os.path.join(os.path.dirname(submission_file),'tmp')
    os.makedirs(tmp_dir,exist_ok=True)
    input_files.sort(key=custom_key)
    for fname_in in input_files:
        fname_out = os.path.join(tmp_dir,os.path.basename(fname_in))
        print("Running test",os.path.basename(fname_in))
        local_time_start = time.perf_counter()
        with open(fname_in,'r') as inf, open(fname_out,'w') as ouf:
            command = PYTHON2_INTERPRETER + [submission_file]
            # print(command)
            p = subprocess.run(command,stdin=inf,stdout=ouf)
        local_time_end = time.perf_counter()
        if(p.returncode):
            print('RE: Runtime error')
            exit(0)
        print('Time elapsed: {0:.2f}'.format(local_time_end-local_time_start),'seconds')



def run_python3(submission_file,input_folder,output_folder):
    input_files = [os.path.join(input_folder,f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder,f))]
    # Create temp dir
    tmp_dir = os.path.join(os.path.dirname(submission_file),'tmp')
    os.makedirs(tmp_dir,exist_ok=True)
    input_files.sort(key=custom_key)
    for fname_in in input_files:
        fname_out = os.path.join(tmp_dir,os.path.basename(fname_in))
        print("Running test",os.path.basename(fname_in))
        local_time_start = time.perf_counter()
        with open(fname_in,'r') as inf, open(fname_out,'w') as ouf:
            command = PYTHON3_INTERPRETER + [submission_file]
            p = subprocess.run(command,stdin=inf,stdout=ouf)
        local_time_end = time.perf_counter()
        if(p.returncode):
            print('RE: Runtime error')
            exit(0)
        print('Time elapsed: {0:.2f}'.format(local_time_end-local_time_start),'seconds')



def run(submission_file,input_folder,output_folder):
    binary_file, ext = os.path.splitext(submission_file)
    start_time =0.0
    end_time = 0.0
    if(ext == '.cpp'):
        compile_cpp(submission_file,binary_file)
        start_time = time.perf_counter()
        run_binary(binary_file,input_folder,output_folder)
        end_time =time.perf_counter()
    elif(ext == '.c'):
        compile_c(submission_file,binary_file)
        start_time = time.perf_counter()
        run_binary(binary_file,input_folder,output_folder)
        end_time =time.perf_counter()
    elif(ext == '.java'):
        problem_id = os.path.basename(os.path.dirname(input_folder))
        compile_java(submission_file,problem_id)
        start_time = time.perf_counter()
        run_java(os.path.join(os.path.dirname(submission_file),problem_id),input_folder,output_folder)
        end_time =time.perf_counter()
    elif(ext == '.py2'):
        start_time = time.perf_counter()
        run_python2(submission_file,input_folder,output_folder)
        end_time =time.perf_counter()
    elif(ext == '.py3'):
        start_time = time.perf_counter()
        run_python3(submission_file,input_folder,output_folder)
        end_time =time.perf_counter()
    else:
        print(submission_file,'has an invalid extension')
        sys.exit(1)
    print('Total time elapsed: {0:.2f}:'.format(end_time - start_time))

def run_checker(input_folder,output_folder,tmp_dir,checker_file):
    output_files = [os.path.join(output_folder,f) for f in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder,f))]
    output_files.sort(key=custom_key)
    for f in output_files:
        fname = os.path.basename(f)
        inf = os.path.join(input_folder,fname)
        ouf = f
        ans = os.path.join(tmp_dir,fname)
        if(not os.path.isfile(inf)):
            print('Input',fname,'not available')
            sys.exit(1)
        if(not os.path.isfile(ans)):
            print('Answer',fname,'not available')
            sys.exit(1)
        print('Checking input',fname)
        command = [checker_file,inf,ouf,ans]
        # print(' '.join(command))
        p = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        checker_output = p.stderr.decode('utf-8')
        if(checker_output.startswith('ok')):
            print('Input', fname, ': AC')
        elif(checker_output.startswith('wrong answer')):
            print('Input', fname, ': WA')
            sys.exit(0)
        elif(checker_output.startswith('wrong output format')):
            print('Input', fname, ': PE')
            sys.exit(0)
        elif(checker_output.startswith('FAIL')):
            print('Input', fname,
                  ': FAIL: maybe the jury solution or the checker are not correct')
            sys.exit(0)
        else:
            print('Input', fname, ': Output not recognized -> ', checker_output)
            sys.exit(0)
    print('OK: All tests passed!')

def check(submission_id,problem_id):    
    submission_file = os.path.join(submissions_folder,submission_id)
    input_folder = os.path.join(*[problems_folder,problem_id,'input'])
    output_folder = os.path.join(*[problems_folder,problem_id,'output'])
    checker_file = os.path.join(*[problems_folder,problem_id,'bin','checker'])
    if(not os.path.isfile(submission_file)):
        print(submission_file,'does not exists')
        sys.exit(1)
    if(not os.path.isdir(input_folder)):
        print(input_folder,'does not exists')
        sys.exit(1)
    if(not os.path.isdir(output_folder)):
        print(output_folder,'doest not exists')
        sys.exit(1)
    if(not os.path.isfile(checker_file)):
        print(checker_file,'does not exists')
        sys.exit(1)

    tmp_dir = os.path.join(os.path.dirname(submission_file),'tmp')
    print(tmp_dir)
    # Remove tmp_dir if it exists
    if(os.path.isdir(tmp_dir)):
        print('Removing',tmp_dir)
        shutil.rmtree(tmp_dir)

    run(submission_file,input_folder,output_folder)
    run_checker(input_folder,output_folder,tmp_dir,checker_file)


if __name__=="__main__":
    if(len(sys.argv)<3):
        print('usage: <submission_id> <problem_id>')
        sys.exit(1)
    submission_id = sys.argv[1]
    problem_id = sys.argv[2]
    check(submission_id,problem_id)
