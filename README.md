**Sambvca 2.1 Distribution**
Luigi Cavallo - 2025

Source file       :   sambvca21.f
Information       :   Fortran source code to calculate buried volume and array of points 
                      defining the surface of the catalytic pocket.
To be compiled as :   gfortran -o  sambvca21.x sambvca21.f
Input file        :   Input file is myfile.inp, examples with instructions in the Examples directory.
Executed as       :   sambvca21.x myfile      It automatically generates a myfile.out plus other output files

Script file       :   plot_map.py
Information       :   Python script file to generate png and a ps images of the catalytic pocket.
Input file        :   Input file is myfile-TopSurface.dat generated by sambvca21.x
Executed as       :   plot_map.py  myfile-TopSurface.dat levels-spacing

Examples          :   Directory with examples. Check the README file there for further info
