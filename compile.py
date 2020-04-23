cu_head = '''#include <math.h>
#include <cuComplex.h>
#include <complex.h>
#include <stdbool.h>

extern "C" {
__device__ unsigned short int rot = 0;
__global__ void rotation(unsigned short int angle){
   rot = angle;}

__host__ void rotate(unsigned short int angle){
rotation<<<1,1>>>(angle);}

__device__ unsigned char sin255(unsigned short int l){
  return 127.5*(sin(l*M_PI/180)+1);}

__device__ unsigned char sin255d(double l){
  return 127.5*(sin(l*M_PI/180)+1);}

__device__ unsigned char cos255(unsigned short int l){
  return 127.5*(cos(l*M_PI/180)+1);}

__device__ unsigned char cos255d(double l){
  return 127.5*(cos(l*M_PI/180)+1);}

__device__ unsigned char tan255(unsigned short int l){
  return 127.5*(tan(l*M_PI/180)+1);}

__device__ double sinusfr(unsigned short int l){
  return sin(l*M_PI/180);}

__device__ double cosinusfr(unsigned short int l){
  return cos(l*M_PI/180);}

__device__ double sqrtI(unsigned short int l){
  return sqrt((double)l);}

__device__ cuDoubleComplex cuCaddD(cuDoubleComplex z, double r){
  return make_cuDoubleComplex(z.x+r,z.y+r);}

__device__ cuDoubleComplex mod(cuDoubleComplex z, int i){
  return make_cuDoubleComplex(z.x,exp(double(i*M_PI/180*z.y)));}

__device__ cuDoubleComplex cuCmulD(cuDoubleComplex z, double r){
  return make_cuDoubleComplex(z.x*r,z.y*r);}

__device__ cuDoubleComplex cuExp(cuDoubleComplex z){
  return make_cuDoubleComplex(exp(z.x)*cos(z.y),exp(z.x)*sin(z.y));}

__device__ cuDoubleComplex Ccos(cuDoubleComplex z){
     return make_cuDoubleComplex(cos(z.x)*cosh(z.y),-sin(z.x)*sinh(z.y));}

__device__ cuDoubleComplex Csin(cuDoubleComplex z){
	return make_cuDoubleComplex(sin(z.x)*cosh(z.y),sinh(z.y)*cos(z.x));}

__device__ cuDoubleComplex cuCsin(cuDoubleComplex z){
  return make_cuDoubleComplex(sin(z.x*M_PI),z.y);}

__device__ cuDoubleComplex cusin(cuDoubleComplex z){
  return make_cuDoubleComplex(sin(z.x*z.y),z.y+z.x);}

__device__ cuDoubleComplex cuCsinh(cuDoubleComplex z){
  return make_cuDoubleComplex(sinh(z.x*M_PI/2),z.y);}

__device__ cuDoubleComplex erfC(cuDoubleComplex z){
  return make_cuDoubleComplex(erfc(z.x),0.0);}

__device__ cuDoubleComplex cuPow(cuDoubleComplex z,unsigned short int x){
  cuDoubleComplex z0 = z;
  while (x-->1)
    z = cuCmul(z,z0);
  return z;}

__device__ cuDoubleComplex mnd( cuDoubleComplex x, cuDoubleComplex d)
{
    return make_cuDoubleComplex(x.x*x.x-d.x - x.y*x.y , x.x*x.y-d.y + x.y*x.x);}

__device__ cuDoubleComplex mnd2( double xx, double xy, double dx, double dy)
{
    return make_cuDoubleComplex(xx*xx-dx - xy*xy , xx*xy-dy + xy*xx);}

__device__ void inside(unsigned char* img,cuDoubleComplex z, unsigned short int iter,unsigned short int frame, unsigned char R, unsigned char G, unsigned char B){
  switch (R){
    case 0:img[0] = sin255(iter);break;
    case 1:img[0] = 0;break;//cos255((iter*2+frame));break;
    case 2:img[0] = sin255((iter*2+frame));break;
    case 3:img[0] = sin255(frame+iter);break;
    case 4:img[0] = 0; break;
    case 5:img[0] = sin255d(z.x*6+frame);break;
    default:img[0] = sin255(iter*R+frame*R);}
  switch (G){
    case 0:img[1] = sin255(iter);break;
    case 1:img[1] = 0;break;//sin255((iter*3-frame*5));break; 
    case 2:img[1] = cos255((iter*3-frame*5));break;
    case 3:img[1] = sin255(frame+iter); break;
    case 4:img[1] = 0;break;
    case 5:img[1] = cos255d(z.y*8+2*frame);break;
    default:img[1]= sin255(iter*G+frame*G);}
  switch (B){
    case 0:img[2] = sin255(iter);break;
    case 1:img[2] = 0;break;//cos255((iter*14+frame*8));break;
    case 2:img[2] = sin255((iter*14+frame*8));break;
    case 3:img[2] = sin255(frame+iter);break;
    case 4:img[2] = tan255(iter+frame);break;
    case 5:img[2] = sin255d(z.x*12+z.y*13+frame);break;
    default:img[2]= sin255(iter*B+frame*B);}}

__device__ void outside(unsigned char* img,cuDoubleComplex z,unsigned short int iter,unsigned short int frame, unsigned char R, unsigned char G, unsigned char B){
  switch (R){
    case 0:img[0] = sin255(iter);break;
    case 1:img[0] = sin255(sqrt(z.x*z.x*(3+2*sinusfr(frame))+z.y*z.y));break;//cos255((iter*2+frame+(z.x-z.y*3*cosinusfr(frame*10))*(cosinusfr(iter+frame))));break;
    case 2:img[0] = sin255((iter*2+frame+(z.x-z.y*3*cosinusfr(frame*10))*(cosinusfr(iter+frame))));break;
    case 3:img[0] = sin255(frame*iter);break;
    case 4:img[0] = 0; break;
     case 5:img[0] = sin255d(z.x*6+frame);break;   
    default:img[0] = sin255(iter*R+frame*R);}
  switch (G){
    case 0:img[1] = sin255(iter);break;
    case 1:img[1] = sin255(30+frame+sqrt(z.x*z.x*(3+2*sinusfr(frame))+z.y*z.y));break;//sin255((iter*3-frame*5+(sqrt(fabs(z.y)) - z.x*4*cosinusfr(frame*4)) ));break;
    case 2:img[1] = cos255((iter*3-frame*5+(sqrt(fabs(z.y)) - z.x*4*cosinusfr(frame*4)) ));break;
    case 3:img[1] = sin255(frame*iter); break;
    case 4:img[1] = 0;break;
case 5:img[1] = cos255d(z.y*8+2*frame);break;
    default:img[1] = sin255(iter*G+frame*G);}
  switch (B){
    case 0:img[2] = sin255(iter);break;
    case 1:img[2] = sin255(frame+iter + sqrt(z.x*z.x*(3+2*sinusfr(frame))+z.y*z.y));break;//cos255((iter*40+frame*8)+(erf(z.x)*5*cosinusfr(frame*13)) );break;
    case 2:img[2] = cos255((iter*40+frame*8)+(erf(z.x)*5*cosinusfr(frame*13)) );break;
    case 3:img[2] = sin255(frame*iter);break;
    case 4:img[2] = tan255(iter+frame);break;
    case 5:img[2] = sin255d(z.x*12+z.y*13+frame);break;
    default:img[2] = sin255(iter*B+frame*B);}
}
'''

cu_func =  '''__global__ void %s(const unsigned short int width,const unsigned short int height,const double span,const double center_x, const double center_y,const unsigned short int iterations,const unsigned short int frame,unsigned char* image_buffer, unsigned char R, unsigned char G, unsigned char B, _Bool julia)
{
  unsigned short int row = (blockIdx.y * blockDim.y + threadIdx.y);  // WIDTH
  unsigned short int col = (blockIdx.x * blockDim.x + threadIdx.x);  // HEIGHT
  unsigned int idx = 3*(row * width + col);
  if(col >= width || row >= height) return;
  double y0 = (double)  (row -width)/(width/span/2)+span;
  double x0 = (double) -((col -height)/(height/span/2)+span);
  _Bool rotation = 1;
  if (rotation){
	//noch die Rotation des "klicks" anpassen in pygame
	//und natürlich das "Setting" erstmal ermöglichen
	double xx = x0;
  	x0 = ((x0) * cosinusfr(rot) - (y0) * sinusfr(rot));
  	y0 = ((xx)*sinusfr(rot) + (y0) * cosinusfr(rot));}
  x0 -= center_x;
  y0 += center_y;
  cuDoubleComplex z,c;
  if(julia){  z = make_cuDoubleComplex(x0,-y0);
  	c = make_cuDoubleComplex(0.8+0.15*sinusfr(frame),-0.156-0.15*cosinusfr(frame));}
  else{
  	z = make_cuDoubleComplex(0.0f,-0.0f);
  	c = make_cuDoubleComplex(x0,y0);}
  unsigned short int iter = 0;
  while(++iter < iterations && z.x*z.x + z.y*z.y < 256)
     %s;

  if (iter == iterations)
    inside(&image_buffer[idx],z,iter,frame,R,G,B);
  else
    outside(&image_buffer[idx],z,iter,frame,R,G,B);}

'''

cu_make = '''__host__ void %s(const unsigned short int width,const unsigned short int height, const long double span,const long double center_x, const long double center_y,const unsigned short int iterations,const unsigned short int frame, unsigned char* image_buffer, unsigned char R, unsigned char G, unsigned char B,_Bool julia){
  unsigned char* d_image_buffer;
  unsigned int arr_size = 3 * width * height;
  cudaMallocManaged(&d_image_buffer, arr_size*sizeof(unsigned char));
  dim3 block_size(16, 16);
  dim3 grid_size(width / block_size.x, height / block_size.y);
  %s<<<grid_size, block_size>>>(height,width,span,center_x,center_y,iterations,frame,d_image_buffer,R,G,B,julia);
  cudaPeekAtLastError();
  cudaDeviceSynchronize();
  cudaMemcpy(image_buffer, d_image_buffer, arr_size, cudaMemcpyDeviceToHost);
  cudaFree(d_image_buffer);}

'''
final = "}"

def compile(functions):
  with open("frac.cu","w+") as f:
   f.write(cu_head)
   for name, func in functions:
     f.write(cu_func%(name+"_calc",func))
     f.write(cu_make%(name,name+"_calc"))
   f.write(final)

if __name__ == '__main__':
  functions = []
  with open("rep/cuda_funcs.txt") as f:
    for line in f:
      if '#' in line:
        functions.append((line.split("#")[0],line.split('#')[1][:-1]))
  compile(functions)
     

