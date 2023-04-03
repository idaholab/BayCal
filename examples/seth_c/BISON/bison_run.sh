#!/bin/bash
module load pbs use.moose PETSc gcc/9.3.0-gcc-4.8.5-twls
# module load use.moose moose-dev
#module load pbs use.moose PETSc

~/projects/bison/bison-opt "$@"
