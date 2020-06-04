# FractalExplorer
Cuda based Fractal Explorer with Pygame UI

!Just working on unix systems!
If u want to use it on Windows, you have to compile the cuda code as DLL and modify the load_cuda-function for their usage


#REQUIREMENTS (Python Modules)

-pygame

-pillow

-numpy
  
#Also required:

-nvcc (Nvidia Compiler) and NVIDIA GPU

-ffmpeg (if u want to save a video from this)

Run 'create_cuda_code' to create and compile the 'frac.so'. If an error shows up, try changing compiler architecture in line 197.

Run fractal.py to explore the fractals :)

If u want to add new functions (in cuda_funcs.txt), check possible calculation methods in "cu_head" of 'create_cuda_code.py'. Simple use of operators like 'z = z*z+c' is not working with CUDA extention.
Also, you have to give the function an individual name and separate name and function by #

