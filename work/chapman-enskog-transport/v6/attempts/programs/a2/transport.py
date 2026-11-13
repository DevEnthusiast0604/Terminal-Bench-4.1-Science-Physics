#!/usr/bin/env python3
"""Classical binary-gas transport from variational Boltzmann collision brackets.
Units: sigma = epsilon = k_B = lighter molecular mass = 1.
Vector and traceless tensor Laguerre bases are integrated over Maxwellian
centre-of-mass velocities and expanded in angular harmonics. Classical
scattering supplies the harmonic eigenvalues of the collision operator.
The vector response is constrained to zero total momentum; its Schur
complement gives the conductivity at zero relative species velocity.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from scipy.special import roots_legendre
from scipy.optimize import minimize_scalar, brentq

GL={n:roots_legendre(n) for n in (12,24)}
class Scatter:
 def __init__(self,A):
  self.a=A;self.d=1-A
  opt=minimize_scalar(lambda y:-self.ec(A+self.d*y),bounds=(2**(1/6),5),method='bounded',options={'xatol':1e-14})
  self.rc=A+self.d*opt.x;self.emax=self.ec(self.rc)
 def pot(self,r):
  z=(self.d/(r-self.a))**6
  return 4*z*(z-1)
 def ec(self,r):
  z=(self.d/(r-self.a))**6
  return 4*z*(z-1)+12*r/(r-self.a)*z*(1-2*z)
 def setup(self,E):
  self.E=E
  rhead=self.a+self.d*(2/(1+np.sqrt(1+E)))**(1/6)
  self.rhead=rhead
  if E<self.emax:
   ro=brentq(lambda r:self.ec(r)-E,self.rc,max(self.rc*2,self.a+self.d*(20/E)**(1/6)),xtol=1e-14)
   self.ro=ro;self.bc=ro*np.sqrt(1-self.pot(ro)/E);self.orbit=True
   self.ri=brentq(lambda r:r*r*(1-self.pot(r)/E)-self.bc**2,rhead,self.rc,xtol=1e-14)
  else:
   self.ro=self.rc;self.bc=self.rc*np.sqrt(1-self.pot(self.rc)/E);self.orbit=False
 def angles(self,b,tol=1e-8):
  E=self.E; b=np.asarray(b);b2=b*b
  tol=max(tol,1e-6 if E<.001 else 1e-7 if E<.01 else 1e-8)
  lo=np.full_like(b,self.rhead);hi=np.maximum(b,self.ro*1.01)
  if self.orbit:
   inner=b<self.bc
   hi[inner]=self.ri;lo[~inner]=self.ro
  for _ in range(58):
   mid=(lo+hi)/2
   f=mid*mid*(1-self.pot(mid)/E)-b2
   take=f>0;hi=np.where(take,mid,hi);lo=np.where(take,lo,mid)
  r0=(lo+hi)/2
  z6=(self.d/(r0-self.a))**6
  # Split at the orbiting barrier, where an inner trajectory has a narrow peak.
  cut=np.sqrt(np.maximum(0,1-r0/self.ro))
  idx=np.concatenate((np.arange(len(b)),np.flatnonzero(cut>0)))
  left=np.concatenate((np.zeros(len(b)),cut[cut>0]))
  right=np.concatenate((np.where(cut>0,cut,1),np.ones(np.sum(cut>0))))
  total=np.zeros_like(b)
  iterations=0
  while len(idx):
   mid=(left+right)/2;half=(right-left)/2
   vals=[]
   for n in (12,24):
    xx,ww=GL[n];u=mid[:,None]+half[:,None]*xx
    z=1-u*u
    lr=np.log1p((self.a/(r0[idx]-self.a))[:,None]*(1-z))-np.log(z)
    lz=2*np.log(z)
    f=(1-z*z)+4/E*z*z*(z6[idx,None]**2*(-np.expm1(-12*lr-lz))-z6[idx,None]*(-np.expm1(-6*lr-lz)))
    val=2*u/np.sqrt(np.maximum(f,1e-24))
    vals.append(half*np.sum(val*ww,axis=1))
   err=np.abs(vals[1]-vals[0]);ok=(err<tol*(right-left)+max(tol*.1,2e-8)) | (iterations>8)
   np.add.at(total,idx[ok],vals[1][ok])
   idx0=idx[~ok];l0=left[~ok];r0p=right[~ok];m0=mid[~ok]
   idx=np.concatenate((idx0,idx0));left=np.concatenate((l0,m0));right=np.concatenate((m0,r0p))
   iterations+=1
   if len(idx)>2000000: raise RuntimeError('angle convergence')
  return np.pi-2*b/r0*total
 def moments(self,E,L,tol=1e-8):
  self.setup(E)
  tol=max(tol,1e-6 if E<.001 else 1e-7 if E<.01 else 1e-8)
  bc=self.bc
  # Parameterize both sides of a possible orbiting impact parameter logarithmically.
  tmax=np.log((max(20.,20*E**(-1/6))/bc)**2-1)
  edges1=np.linspace(0,19,20);edges2=np.linspace(-19,tmax,int(np.ceil(tmax+19))+1)
  sides=np.concatenate((np.zeros(len(edges1)-1,dtype=int),np.ones(len(edges2)-1,dtype=int)))
  left=np.concatenate((edges1[:-1],edges2[:-1]));right=np.concatenate((edges1[1:],edges2[1:]))
  total=np.zeros(L+1)
  iterations=0;num=0
  while len(left):
   mid=(left+right)/2;half=(right-left)/2
   estimates=[]
   for n in (12,24):
    xx,ww=GL[n];t=mid[:,None]+half[:,None]*xx
    ex=np.exp(np.where(sides[:,None]==0,-t,t))
    b=bc*np.sqrt(np.where(sides[:,None]==0,1-ex,1+ex))
    chi=self.angles(b.ravel()).reshape(b.shape);num+=b.size
    c=np.cos(chi);p0=np.ones_like(c);p1=c
    vals=[np.zeros(len(left))]
    for l in range(1,L+1):
     pl=p1 if l==1 else ((2*l-1)*c*p1-(l-1)*p0)/l
     vals.append(np.sum((1-pl)*ex*ww,axis=1)*half*np.pi*bc*bc)
     if l>1:p0,p1=p1,pl
    estimates.append(np.array(vals).T)
   err=np.max(np.abs(estimates[1]-estimates[0]),axis=1)
   scale=np.max(np.abs(estimates[1]),axis=1)
   ok=(err<tol*(right-left)/max(1.,30+tmax)+tol*scale) | (iterations>8)
   total+=np.sum(estimates[1][ok],axis=0)
   l0=left[~ok];r0=right[~ok];m0=mid[~ok];s0=sides[~ok]
   sides=np.concatenate((s0,s0));left=np.concatenate((l0,m0));right=np.concatenate((m0,r0));iterations+=1
  return total,num


from scipy.special import roots_genlaguerre, gammaln, lpmv
from scipy.linalg import solve


class Brackets:
 def __init__(self,R,X,T,N):
  self.R=R;self.X=X;self.T=T;self.N=N
  # p=0..N-1, vector degree 2p+1, tensor degree 2p+2.
  self.L=N+1
  c,w=roots_legendre(N+2)
  self.c=c;self.w=w
  self.proj={}
  for m in (0,1,2):
   mat=np.zeros((self.L+1,len(c)))
   for l in range(m,self.L+1):
    norm=np.exp((np.log(2*l+1)+gammaln(l-m+1)-gammaln(l+m+1))/2)
    mat[l]=w/2*norm*lpmv(m,l,c)
   self.proj[m]=mat
  self.s=np.sqrt(1-c*c)
  z,wz=roots_genlaguerre(N+2,.5)
  self.z=z;self.wz=wz/np.exp(gammaln(1.5))
  self.normv=np.sqrt(np.exp(gammaln(np.arange(N)+2.5)-gammaln(2.5)-gammaln(np.arange(N)+1)))
  self.normt=np.sqrt(np.exp(gammaln(np.arange(N)+3.5)-gammaln(3.5)-gammaln(np.arange(N)+1)))
 def harmonics(self,i,j,y,kind,q=None):
  masses=[1.,self.R];mi=masses[i];mj=masses[j];M=mi+mj;mu=mi*mj/M
  g=np.sqrt(2*self.T*y/mu)
  G=np.sqrt(2*self.T*self.z/M)
  vx1=np.broadcast_to((mj/M*g*self.s)[None,:],(len(G),len(self.c)))
  vz1=G[:,None]+mj/M*g*self.c
  vx2=np.broadcast_to((-mi/M*g*self.s)[None,:],vx1.shape)
  vz2=G[:,None]-mi/M*g*self.c
  allvals=[]
  for mass,vx,vz in [(mi,vx1,vz1),(mj,vx2,vz2)]:
   v2=vx*vx+vz*vz;z=mass*v2/(2*self.T)
   alpha=1.5 if kind=='v' else 2.5
   lag=np.empty((self.N,)+z.shape);lag[0]=1
   if self.N>1:lag[1]=alpha+1-z
   for p in range(1,self.N-1):
    lag[p+1]=((2*p+alpha+1-z)*lag[p]-(p+alpha)*lag[p-1])/(p+1)
   lag=lag/(self.normv if kind=='v' else self.normt)[:,None,None]
   if kind=='v':
    comp=[lag*vz,lag*vx]
   else:
    # Tensor contraction = (3/2)Tzz*Tzz + 2*Txz*Txz + (1/2)(Txx-Tyy)^2.
    comp=[lag*(vz*vz-v2/3),lag*vx*vz,lag*vx*vx]
   allvals.append(comp)
  result=np.zeros((2*self.N,2*self.N)) if q is not None else np.zeros((self.L+1,2*self.N,2*self.N))
  weights=[1.,1.] if kind=='v' else [1.5,2.,.5]
  for m,weight in enumerate(weights):
   vals=np.concatenate((allvals[0][m],allvals[1][m]),axis=0)
   if i==j:vals=np.concatenate((vals[:self.N]+vals[self.N:],np.zeros_like(vals[:self.N])),axis=0)
   # Both transverse Fourier components are included in the contraction weights.
   h=(vals.reshape(-1,len(self.c))@self.proj[m].T).reshape(2*self.N,len(self.z),self.L+1).transpose(2,1,0).copy()
   if q is None:
    result+=weight*np.einsum('lza,lzb,z->lab',h,h,self.wz,optimize=True)
   else:
    h*=np.sqrt(np.maximum(q,0)[:,None,None]*self.wz[None,:,None]*weight)
    h=h.reshape(-1,2*self.N)
    result+=h.T@h
  return result,g
 def matrices(self,ys,wy,Q,kind):
  n=self.N;B=np.zeros((2*n,2*n))
  for i,j in [(0,0),(0,1),(1,1)]:
   block=np.zeros((2*n,2*n))
   for y,w,q in zip(ys,wy,Q):
    H,g=self.harmonics(i,j,y,kind,q)
    block+=w*g*H
   x=[self.X,1-self.X];factor=x[i]*x[j]/(3 if kind=='v' else 10)
   if i==j:
    factor*=.5
    B[i*n:(i+1)*n,i*n:(i+1)*n]+=factor*block[:n,:n]
   else:B+=factor*block
  return B
 def transport(self,Bv,Bt):
  n=self.N;T=self.T;x=np.array([self.X,1-self.X]);mass=np.array([1.,self.R]);
  # Force source c_i * d_i/x_i, where d_1=-d_2=d12.
  d=np.zeros(2*n);d[0]=T;d[n]=-T/self.R
  h=np.zeros(2*n);h[1]=-2.5*x[0]*T**2/(mass[0]*self.normv[1]);h[n+1]=-2.5*x[1]*T**2/(mass[1]*self.normv[1])
  # Constraint sum x_i*m_i*<c_i phi_i>=0 fixes the momentum invariant.
  constraint=np.zeros(2*n);constraint[0]=x[0]*T;constraint[n]=x[1]*T
  augmented=np.zeros((2*n+1,2*n+1));augmented[:-1,:-1]=Bv;augmented[-1,:-1]=constraint;augmented[:-1,-1]=constraint
  uv=solve(augmented,np.column_stack((np.r_[d,0],np.r_[h/T,0])),assume_a='sym')[:-1]
  Ldd=d@uv[:,0];Ldh=d@uv[:,1];Lhh=(h/T)@uv[:,1]
  D=x.prod()*Ldd
  alpha=Ldh/(x.prod()*Ldd)
  conductivity=Lhh-Ldh*Ldh/Ldd
  bt=np.zeros(2*n);bt[0]=x[0]*T;bt[n]=x[1]*T/self.R
  ut=solve(Bt,bt,assume_a='pos')
  viscosity=T*bt@ut
  return dict(viscosity=viscosity,thermal_conductivity=conductivity,binary_diffusion=D,thermal_diffusion_factor=alpha)


def energy_nodes(T,S,order=12):
 edges=np.unique(np.r_[0.,np.geomspace(1e-5,.1,8),np.linspace(.1,2,12),np.linspace(2,20,19),np.linspace(20,60,11),np.linspace(60,150,10),np.linspace(150,350,21),S.emax/T])
 edges=edges[edges<=350]
 # add intervals close to critical energy
 yc=S.emax/T
 if yc<350:
  edges=np.unique(np.r_[edges,(yc+np.array([-1,1])[:,None]*np.geomspace(1e-5,min(.1,yc/2),7)).ravel()])
  edges=edges[(edges>=0)&(edges<=350)]
 c,w=roots_legendre(order);half=np.diff(edges)/2;mid=(edges[1:]+edges[:-1])/2
 ys=(mid[:,None]+half[:,None]*c).ravel()
 wy=(half[:,None]*w).ravel()*np.sqrt(ys)*np.exp(-ys)/np.exp(gammaln(1.5))
 return ys,wy


def main():
 import sys,json
 A,R,X,T=map(float,sys.argv[1:5])
 N=64 if R>12 else 48 if R>4 else 32 if R>1.5 else 24
 S=Scatter(A)
 ys,wy=energy_nodes(T,S)
 Q=np.array([S.moments(T*y,N+1)[0] for y in ys])
 B=Brackets(R,X,T,N)
 bv=B.matrices(ys,wy,Q,'v')
 bt=B.matrices(ys,wy,Q,'t')
 result=B.transport(bv,bt)
 if R==1:result['thermal_diffusion_factor']=0.0
 print(json.dumps({k:float(v) for k,v in result.items()},allow_nan=False,separators=(',',':')))

if __name__=='__main__':
 main()
