#!/usr/bin/env python3
"""Quantum Kihara binary-mixture transport, in reduced units.

Radial partial waves are propagated with Numerov integration. Collision
brackets are evaluated in orthonormal Sonine polynomial bases, with exact
Gaussian velocity quadrature and adaptive integration over collision energy.
The vector collision operator is projected off conserved total momentum;
the heat coefficient uses the zero-diffusion Schur complement.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import sys, json, time, tempfile, base64, zlib, ctypes
import numpy as np
from scipy.special import roots_genlaguerre, roots_legendre, gammaln, lpmv, eval_legendre
from scipy.integrate import quad_vec
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq

_KERNEL = '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'
_tmp = tempfile.TemporaryDirectory(prefix='quantum_transport_')
_path = os.path.join(_tmp.name,'radial.so')
with open(_path,'wb') as _f:
    _f.write(zlib.decompress(base64.b64decode(_KERNEL)))
lib = ctypes.CDLL(_path)
ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
lib.cross.argtypes=[ctypes.c_double]*5+[ctypes.c_int]*3+[ptr]*4
lib.phases.argtypes=[ctypes.c_double]*5+[ctypes.c_int,ptr,ptr]

class Scattering:
 def __init__(self,A,L,mu,identical,nj=16,emax=35):
  self.A=A;self.q=8*np.pi**2*mu/L**2;self.identical=identical;self.nj=nj
  self.tables={}
  self.nt=int(14*np.sqrt(self.q*emax)+80+nj/2+4)
  self.t,self.w=roots_legendre(self.nt)
  self.pol=np.ascontiguousarray(np.array([eval_legendre(j,self.t) for j in range(nj)]).T)
 def __call__(self,E,spacing=.05,radius=30):
  nt=int(np.ceil((14*np.sqrt(self.q*E)+80+self.nj/2+4)/32))*32
  if nt not in self.tables:
   t,w=roots_legendre(nt)
   pol=np.ascontiguousarray(np.array([eval_legendre(j,t) for j in range(self.nj)]).T)
   self.tables[nt]=(t,w,pol)
  t,w,pol=self.tables[nt]
  out=np.zeros(self.nj)
  lib.cross(self.A,self.q,E,spacing,radius,self.identical,self.nj,nt,t,w,pol,out)
  return out

def bracket_h(e, mass1, mass2, n, rank, identical=False):
    ny=n+rank+1; nt=n+rank+1
    y, wy=roots_genlaguerre(ny, .5); wy*=2/np.sqrt(np.pi)
    t, wt=roots_legendre(nt); wt*=.5
    lmax=n-1+rank
    projections=[]
    for m in range(rank+1):
        proj=np.zeros((lmax+1,nt))
        for l in range(m,lmax+1):
            proj[l]=wt*lpmv(m,l,t)*np.sqrt((2*l+1)*np.exp(gammaln(l-m+1)-gammaln(l+m+1)))
        projections.append(proj)
    norm=np.exp(.5*(gammaln(np.arange(n)+rank+1.5)-gammaln(rank+1.5)-gammaln(np.arange(n)+1)))
    norm*=np.sqrt(1.5 if rank==1 else 2.5)
    out=[]
    for ma,mb,sign in [(mass1,mass2,1),(mass2,mass1,-1)]:
        a=np.sqrt(ma/(ma+mb)); b=sign*np.sqrt(mb/(ma+mb))
        z=a*np.sqrt(y)[None,:,None]+b*np.sqrt(e)[:,None,None]*t[None,None,:]
        w=b*np.sqrt(e)[:,None,None]*np.sqrt(1-t*t)[None,None,:]
        v2=z*z+w*w
        if rank==1: hs=[z,w]
        else: hs=[np.sqrt(1.5)*(2*z*z-w*w)/3,np.sqrt(2)*w*z,w*w/np.sqrt(2)]
        ps=[]
        sp0=np.ones_like(v2); sp1=rank+1.5-v2
        for p in range(n):
            if p==0: sp=sp0
            elif p==1: sp=sp1
            else:
                sp=((2*p-1+rank+.5-v2)*sp1-(p-1+rank+.5)*sp0)/p
                sp0,sp1=sp1,sp
            ps.append(np.stack([np.einsum('eyt,lt->eyl',sp*h/norm[p],pr,optimize=True) for h,pr in zip(hs,projections)],axis=-1))
        out.append(np.stack(ps,axis=-1))
    if identical: vals=out[0]+out[1]
    else: vals=np.concatenate(out,axis=-1)
    return np.einsum('eylmp,eylmq,y->elpq',vals,vals,wy,optimize=True)

def build_b(e,w,q,m1,m2,n,rank,identical=False):
    B=np.zeros((n if identical else 2*n,)*2)
    for st in range(0,len(e),64):
        h=bracket_h(e[st:st+64],m1,m2,n,rank,identical)
        B+=np.einsum('e,el,elpq->pq',w[st:st+64],q[st:st+64,:h.shape[1]],h,optimize=True)
    return B

def transport(Bv,Bt,R,X,T,n):
    x=np.array([X,1-X]); mass=np.array([1,R]); s=np.sqrt(2*T/mass)
    bd=np.zeros(2*n); bt=np.zeros(2*n); be=np.zeros(2*n)
    bd[::n]=np.array([1,-1])*s*np.sqrt(1.5)
    bt[1::n]=-x*s*np.sqrt(3.75)
    be[::n]=2*x*np.sqrt(2.5)
    null=np.zeros(2*n); null[::n]=np.sqrt(mass); null/=np.linalg.norm(null)
    Bv=Bv+np.outer(null,null)*np.max(np.diag(Bv))
    v=np.linalg.solve(Bv,np.array([bd,bt]).T)
    dd,dt=bd@v; td,tt=bt@v
    eta=T/10*(be@np.linalg.solve(Bt,be))
    lam=(tt-dt*td/dd)/3
    dif=X*(1-X)*dd/3
    alpha=dt/(X*(1-X)*dd)
    return np.array([eta,lam,dif,alpha])


def candidates(a,q,emax):
 h=.003*(1-a)
 r=np.arange(a+(1-a)*.52,10,h)
 z=((1-a)/(r-a))**6
 v=4*z*(z-1)
 result=[]
 for l in range(1,60):
  ve=v+l*(l+1)/(q*r*r)
  mins=np.where((ve[1:-1]<ve[:-2])&(ve[1:-1]<ve[2:]))[0]+1
  if not len(mins):break
  mi=mins[0]
  mx=mi+np.argmax(ve[mi:])
  if mx==mi:continue
  Ebar=ve[mx]
  if Ebar<=0:continue
  # Include enough of the barrier that tunnelling only weakly shifts levels.
  rr=r[:mx+1]; vv=ve[:mx+1]
  diag=2/(q*h*h)+vv;off=np.full(len(rr)-1,-1/(q*h*h))
  vals=eigh_tridiagonal(diag,off,select='v',select_range=(0,min(emax,Ebar)),check_finite=False,eigvals_only=True)
  for e in vals:result.append((l,e,Ebar,r[mx]))
 return result
def resonance_points(sc,T):
 from scipy.optimize import brentq
 pts=[]
 for l,ec,bar,rb in candidates(sc.A,sc.q,12*T):
  if sc.identical and l%2:continue
  sn=np.zeros(l+1);cs=sn.copy()
  def phase(e):
   lib.phases(sc.A,sc.q,e,.05,30,l+1,sn,cs)
   return cs[l]
  interval=max(.002,.08*bar)
  lo=max(1e-10,ec-interval);hi=min(bar*1.3,ec+interval)
  if phase(lo)*phase(hi)>=0:continue
  er=brentq(phase,lo,hi,xtol=2e-13)
  de=1e-5
  width=de
  for j in range(9):
   phase(er+de);cp=cs[l]/sn[l]
   phase(max(er-de,er*.5));cm=cs[l]/sn[l]
   width=abs(2*de/(cp-cm))
   if max(abs(cp),abs(cm))<.05:break
   de*=.1
  if width<1e-9:continue
  print('resonance',sc.q,l,er,width,file=__import__('sys').stderr,flush=True)
  offsets=width*np.array([0,1,4,16,64,256,1024,4096])
  pts.extend((er+offsets)/T);pts.extend((er-offsets[1:])/T)
 return [p for p in pts if 0<p<60]

def lag(e,p):
 e=np.asarray(e); out=np.empty(e.shape+(p,));out[...,0]=1
 if p>1:out[...,1]=2-e
 for j in range(2,p):out[...,j]=((2*j-e)*out[...,j-1]-j*out[...,j-2])/j
 return out/np.sqrt(np.arange(p)+1)

def moments(sc,T,n,eps=1e-7):
 p=2*n+2
 count=0;st=time.time()
 def f(e):
  nonlocal count
  count+=1
  if count%2000==0:print("progress",sc.q,count,e,time.time()-st,file=sys.stderr,flush=True)
  v=sc(e*T)
  if sc.identical:v[1::2]=0
  return np.outer(v,lag(e,p))*e*np.exp(-e)
 # Avoid missing narrow low-energy features by prepartitioning.
 edges=np.unique(np.r_[0,np.geomspace(.0001,.1,12),np.arange(.1,4,.05),np.arange(4,12,.2),np.arange(12,40,1),80,120,160,200,resonance_points(sc,T)])
 m,err=quad_vec(f,0,200,epsabs=eps,epsrel=eps,points=edges[1:-1],quadrature='gk15',limit=10000)
 print('moments',sc.q,sc.identical,'calls',count,'err',err,'time',time.time()-st,file=sys.stderr,flush=True)
 return m

def collision_matrices(m1,m2,m12,R,X,T,n):
 e,w=roots_genlaguerre(2*n+3,1)
 lp=lag(e,2*n+1)
 bv=np.zeros((2*n,2*n)); bt=bv.copy()
 for idx,(ma,mb,ident,m,x) in enumerate([(1,1,True,m1,X*X),(R,R,True,m2,(1-X)**2),(1,R,False,m12,X*(1-X))]):
  q=np.ascontiguousarray(lp@m[:,:2*n+1].T)
  we=w*2/np.sqrt(np.pi)*np.sqrt(2*T/(ma*mb/(ma+mb)))*x
  for rank,B in [(1,bv),(2,bt)]:
   b=build_b(e,we,q,ma,mb,n,rank,ident)
   if ident:
    if idx==0:B[:n,:n]+=b/2
    else:B[n:,n:]+=b/2
   else:B+=b
 return bv,bt

def matrices(m1,m2,m12,R,X,T,n):
 return transport(*collision_matrices(m1,m2,m12,R,X,T,n),R,X,T,n)


def main():
 A,R,L,X,T=map(float,sys.argv[1:6])
 n=32
 ss=[Scattering(A,L,mu,i,n+2,120) for mu,i in [(.5,True),(R/2,True),(R/(1+R),False)]]
 from concurrent.futures import ThreadPoolExecutor
 with ThreadPoolExecutor(max_workers=2) as pool:
  f1=pool.submit(moments,ss[0],T,n,8e-8)
  f2=None if R==1 else pool.submit(moments,ss[1],T,n,8e-8)
  f12=pool.submit(moments,ss[2],T,n,8e-8)
  m1=f1.result()
  m2=m1 if f2 is None else f2.result()
  m12=f12.result()
 bv,bt=collision_matrices(m1,m2,m12,R,X,T,n)
 vals=transport(bv,bt,R,X,T,n)
 # Nested Galerkin subspaces provide an a posteriori convergence diagnostic.
 for order in (n-8,n-4):
  ix=np.r_[np.arange(order),np.arange(n,n+order)]
  earlier=transport(bv[np.ix_(ix,ix)],bt[np.ix_(ix,ix)],R,X,T,order)
  print('basis',order,earlier,file=sys.stderr)
 if R==1 and X==.5:vals[3]=0.0
 print(json.dumps(dict(zip(['viscosity','thermal_conductivity','binary_diffusion','thermal_diffusion_factor'],map(float,vals))),allow_nan=False,separators=(',',':')))

if __name__=='__main__':
 main()
