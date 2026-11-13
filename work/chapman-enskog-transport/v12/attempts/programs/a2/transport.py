#!/usr/bin/env python3
"""Quantum dilute-mixture transport in reduced Kihara units.

The collision operator is evaluated in a converged Sonine-Galerkin basis.
Gaussian center-of-mass integration and rotational averaging are exact for
this basis; thermal relative-energy integration is adaptive. Quantum cross
sections include the molecular internal-state exchange weights. Positive-
energy centrifugal resonances are located before integration.
"""
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_key] = '1'
import sys, time, json
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import (spherical_jn, spherical_yn, roots_legendre,
                           roots_genlaguerre, gammaln, lpmv)
from scipy.linalg import solve


def laguerres(n,alpha,x):
    out=np.empty((n,)+np.shape(x)); out[0]=1
    if n>1: out[1]=1+alpha-x
    for j in range(1,n-1): out[j+1]=((2*j+1+alpha-x)*out[j]-(j+alpha)*out[j-1])/(j+1)
    return out

class Brackets:
    def __init__(self,m1,m2,N,q):
        self.N=N;self.q=q;self.m1=m1;self.m2=m2
        self.L=2*(N-1)+q
        t,wt=roots_legendre(self.L+2)
        y,wy=roots_genlaguerre(N+q+1,.5)
        self.t=t;self.w=np.sqrt(y);self.wy=wy*2/np.sqrt(np.pi)
        self.norm=np.sqrt(np.exp(gammaln(np.arange(N)+q+1.5)-gammaln(np.arange(N)+1)-gammaln(q+1.5)))
        self.H=[]
        for m in range(q+1):
            hh=np.zeros((self.L+1,len(t)))
            for l in range(m,self.L+1):
                hh[l]=lpmv(m,l,t)*np.sqrt((2*l+1)*np.exp(gammaln(l-m+1)-gammaln(l+m+1)))*wt/2
            self.H.append(hh)
    def parts(self,e,mass,other,sgn):
        al=np.sqrt(mass/(mass+other));be=sgn*np.sqrt(other/(mass+other))
        z=al*self.w[:,None]+be*np.sqrt(e)*self.t[None,:]
        x=be*np.sqrt(e)*np.sqrt(1-self.t**2)[None,:]
        c2=z*z+x*x
        la=laguerres(self.N,self.q+.5,c2)/self.norm[:,None,None]
        if self.q==1: fs=[z,x]
        else: fs=[z*z-c2/3,x*z,x*x]
        return [np.einsum('nwt,lt->lwn',la*f,h,optimize=True) for f,h in zip(fs,self.H)]
    def matrix(self,e,Q,selfpair=False):
        aa=self.parts(e,self.m1,self.m2,1)
        bb=self.parts(e,self.m2,self.m1,-1)
        factors=[1/3,1/3] if self.q==1 else [3/20,1/5,1/20]
        out=np.zeros((self.N if selfpair else 2*self.N,)*2)
        for a,b,fac in zip(aa,bb,factors):
            cc=a+b if selfpair else np.concatenate([a,b],axis=2)
            out+=fac*np.einsum('lwn,lwm,l,w->nm',cc,cc,Q,self.wy,optimize=True)
        return out
    def integrated(self,moments,selfpair=False):
        # moments[l,p] = integral e exp(-e) Q_l(e) L_p^1(e)/sqrt(p+1) de
        e,we=roots_genlaguerre(self.L+1,1)
        la=laguerres(self.L+1,1,e)/np.sqrt(np.arange(self.L+1)+1)[:,None]
        qq=moments@la
        out=0
        for j in range(len(e)):out=out+we[j]*self.matrix(e[j],qq[:,j],selfpair)
        mu=self.m1*self.m2/(self.m1+self.m2)
        return out*2/np.sqrt(np.pi)*np.sqrt(2/mu)

def transport(m1,m2,x,T,Cv,Cs,N):
    xs=np.array([x,1-x]); ms=np.array([m1,m2]);
    bd=np.zeros(2*N);bt=bd.copy();bv=bd.copy()
    bd[::N]=np.array([1,-1])*np.sqrt(T/(2*ms))
    bt[1::N]=-xs*1.25*np.sqrt(2*T/ms)/np.sqrt(2.5)
    bv[::N]=xs/2
    null=np.zeros(2*N);null[::N]=np.sqrt(ms)
    Cv=Cv*np.sqrt(T);Cs=Cs*np.sqrt(T)
    # fix momentum gauge, equivalent to invert on its orthogonal complement
    vv=null/np.linalg.norm(null)
    ac=solve(Cv+np.outer(vv,vv)*np.trace(Cv)/(2*N),np.stack([bd,bt],axis=1),assume_a='pos')
    d=bd@ac[:,0];dt=bd@ac[:,1];h=bt@ac[:,1]
    visc=T*bv@solve(Cs,bv,assume_a='pos')
    return [visc,h-dt*dt/d,x*(1-x)*d,dt/(x*(1-x)*d)]


class Scatter:
 def __init__(self,a,L,mu):
  self.a=a;self.b=1-a;self.c=8*np.pi**2*mu/L**2
 def potential(self,r):
  z=(self.b/(r-self.a))**6
  return 4*z*(z-1)
 def phases(self,E,h=.003,R=40,extra=10):
  E=np.atleast_1d(E);k=np.sqrt(self.c*E)
  R=32 if E.min()>.15 else 60
  h=min(h,.03/k.max(),.004*self.b)
  lm=int(np.ceil(k.max()*4.2))+extra
  l=np.arange(lm+1);ll=l*(l+1)
  d0=min(.64,(75/(np.sqrt(self.c)*self.b)+.8**-5)**(-.2))
  r0=self.a+d0*self.b;rb=self.a+.8*self.b
  z=np.zeros((2,len(E),len(l)));z[1]=1
  def rhs(r,z):
   z=z.reshape(2,len(E),len(l));q=ll[None,:]/r**2+self.c*(self.potential(r)-E[:,None])
   return np.stack([z[1],q*z[0]]).ravel()
  for end in self.a+self.b*np.linspace(d0,.8,5)[1:]:
   sol=solve_ivp(rhs,(r0,end),z.ravel(),method='DOP853',rtol=2e-10,atol=1e-12)
   z=sol.y[:,-1].reshape(z.shape);z/=np.maximum(abs(z[0]),abs(z[1]))[None,:,:];r0=end
  # two accurately initialized points
  sol=solve_ivp(rhs,(rb,rb+h),z.ravel(),method='DOP853',rtol=2e-11,atol=1e-13)
  prev=z[0].copy();cur=sol.y[:,-1].reshape(z.shape)[0].copy()
  def qq(r):return (ll[None,:]/r**2+self.c*(self.potential(r)-E[:,None])+(h**4/240)*k[:,None]**6)*(h*h/12)
  qp=qq(rb);qc=qq(rb+h)
  steps=int(np.ceil((R-rb)/h));R=rb+steps*h
  saved={}
  for i in range(2,steps+3):
   r=rb+i*h;qn=qq(r)
   nex=(2*(1+5*qc)*cur-(1-qp)*prev)/(1-qn)
   prev,cur=cur,nex;qp,qc=qc,qn
   if i>=steps-2: saved[i]=cur.copy()
   if i%80==0 and i<steps-2:
    norm=np.maximum(abs(cur),abs(prev));norm=np.maximum(norm,1e-100)
    cur/=norm;prev/=norm
  u=saved[steps]
  du=(saved[steps-2]-8*saved[steps-1]+8*saved[steps+1]-saved[steps+2])/(12*h)
  t0=k[:,None]*R
  j0=t0*spherical_jn(l,t0);y0=t0*spherical_yn(l,t0)
  dj=k[:,None]*(spherical_jn(l,t0)+t0*spherical_jn(l,t0,True))
  dy=k[:,None]*(spherical_yn(l,t0)+t0*spherical_yn(l,t0,True))
  A=u*dy-du*y0;B=u*dj-du*j0
  norm=np.hypot(A,B);A/=norm;B/=norm
  delta=np.arctan2(B,A)
  if R<40:
   # First-order tail: the nonoscillating term, including centrifugal enhancement.
   impact=(l+.5)[None,:]/k[:,None]
   rn,wn=roots_legendre(32)
   v=(rn+1)/2;weights=wn/2
   rs=R/v
   fac=1/np.sqrt(np.maximum(1-(impact[:,None,:]/rs[None,:,None])**2,.01))
   tail=-self.c/(2*k[:,None])*np.sum((self.potential(rs)*weights*R/v**2)[None,:,None]*fac,axis=1)
   delta+=tail
  return delta,A,B
 def born(self,E,l):
  k=np.sqrt(self.c*np.atleast_1d(E));l=np.asarray(l)
  out=np.zeros((len(k),len(l)))
  for base,sign in [(6,1),(12,-1)]:
   for j in range(16 if self.a else 1):
    power=base+j
    integ=np.exp(np.log(np.pi/2)+gammaln(power-1)-(power-1)*np.log(2)-2*gammaln(power/2)+gammaln(l+(3-power)/2)-gammaln(l+(1+power)/2))
    cf=np.exp(gammaln(base+j)-gammaln(base)-gammaln(j+1))*self.a**j
    out+=sign*4*self.c*self.b**base*cf*k[:,None]**(power-2)*integ[None,:]
  return out
 def cross(self,E,M,kind=0,h=.003,R=40):
  d,A,B=self.phases(E,h,R,extra=24)
  cut=d.shape[1]
  tail=self.born(E,np.arange(cut,max(2*cut,100)))
  d=np.concatenate([d,tail],axis=1)
  l=np.arange(d.shape[1]);k=np.sqrt(self.c*np.atleast_1d(E))
  n=len(l)+(M+1)//2+2
  t,wt=roots_legendre(n)
  P=np.empty((max(M+1,len(l)),n));P[0]=1
  if len(P)>1:P[1]=t
  for j in range(1,len(P)-1):P[j+1]=((2*j+1)*t*P[j]-j*P[j-1])/(j+1)
  coef=(2*l+1)[None,:]*np.exp(1j*d)*np.sin(d)/k[:,None]
  kinds=np.atleast_1d(kind)
  dd=abs(coef@P[:len(l)])**2 if 0 in kinds else None
  ee=abs(coef[:,::2]@P[:len(l):2])**2
  oo=abs(coef[:,1::2]@P[1:len(l):2])**2
  angular=((1-P[:M+1])*wt).T
  result=[]
  for kk in kinds:
   ds=dd if kk==0 else (1+kk)*ee+(1-kk)*oo
   qm=2*np.pi*ds@angular
   if kk!=0:
    kt=np.sqrt(self.c*np.atleast_1d(E))
    start=len(l)
    lt=np.arange(start,max(start+1000,6*start))
    dt=self.born(E,lt)
    rem=2*np.pi/kt**2*np.sum((2*lt+1)[None,:]*dt**2,axis=1)
    qm[:,1::2]+=rem[:,None]
   result.append(qm)
  Q=np.stack(result,axis=1)
  if np.ndim(kind)==0:Q=Q[:,0]
  return Q,A,B


def scan(s,T):
 # Only waves with a centrifugal barrier can support positive-energy shape resonances.
 r=np.linspace(s.a+.9*s.b,12,2000)
 barriers=[]
 for l in range(1,30):
  U=s.potential(r)+l*(l+1)/(s.c*r*r)
  minima=np.where((U[1:-1]<U[:-2])&(U[1:-1]<U[2:]))[0]+1
  maxima=np.where((U[1:-1]>U[:-2])&(U[1:-1]>U[2:]))[0]+1
  if not len(minima) or not len(maxima):break
  lo=minima[0];hi=maxima[maxima>lo]
  if not len(hi):break
  barriers.append((l,U[lo],U[hi[0]]))
 if not barriers:return []
 emax=max(b[2] for b in barriers)
 grid=np.unique(np.r_[np.geomspace(1e-7,min(.01,emax),60),np.linspace(.01,emax,200)])
 grid=grid[(grid>0)&(grid<=emax)]
 As=[];Bs=[]
 for chunk in np.array_split(grid,int(np.ceil(len(grid)/64))):
  d,A,B=s.phases(chunk,extra=35)
  As.append(A[:,:len(barriers)+1]);Bs.append(B[:,:len(barriers)+1])
 A=np.concatenate(As);B=np.concatenate(Bs)
 roots=[]
 for l,emin,emax in barriers:
  ids=np.where((A[:-1,l]*A[1:,l]<0)&(grid[:-1]<emax)&(grid[1:]>max(0,emin)))[0]
  for j in ids:
   left,right=grid[j:j+2];al=A[j,l];bl=B[j,l];ar=A[j+1,l];br=B[j+1,l]
   for iteration in range(35):
    mid=(left+right)/2
    d,am,bm=s.phases([mid]);am=am[0,l];bm=bm[0,l]
    if al*am<0:right=mid;ar=am;br=bm
    else:left=mid;al=am;bl=bm
    width=abs((right-left)*(bl+br)/2/(ar-al))
    if right-left<max(1e-12,width*.03):break
   root=(left+right)/2
   if width<.1*T:
    roots.append((root,width,l))
 return roots


species={'pH2':(1.,1.),'oH2':(1.,1/9),'HD':(1.5,-1/6),'oD2':(2.,1/6),'pD2':(2.,1/9)}

class Integrator:
 def __init__(self,a,L,mu,T,M,kind,tol=3e-8):
  self.s=Scatter(a,L,mu);self.T=T;self.M=M;self.kind=np.atleast_1d(kind);self.tol=tol;self.calls=0
  self.rn,self.wn=roots_legendre(16)
 def evaluate(self,edges):
  edges=np.array(edges);left=edges[:,0];right=edges[:,1]
  e=((left+right)[:,None]/2+(right-left)[:,None]/2*self.rn).ravel()
  w=((right-left)[:,None]/2*self.wn).ravel()
  order=np.argsort(e);Q=np.empty((len(e),len(self.kind),self.M+1))
  for chunk in np.array_split(order,max(1,int(np.ceil(len(e)/96)))):
   # limit energy disparity, and omit numerically irrelevant angular momenta
   q,A,B=self.s.cross(e[chunk]*self.T,self.M,self.kind)
   for j,kind in enumerate(self.kind):
    if kind!=0:q[:,j,1::2]=0
   Q[chunk]=q;self.calls+=len(chunk)
  la=laguerres(self.M+1,1,e)/np.sqrt(np.arange(self.M+1)+1)[:,None]
  f=(w*e*np.exp(-e))[:,None,None,None]*Q[:,:,:,None]*la.T[:,None,None,:]
  f=f.reshape(len(edges),16,len(self.kind),self.M+1,self.M+1).sum(axis=1)
  return f
 def run(self):
  bounds=[0,.001,.003,.01,.03,.1,.2,.4,.7,1,1.5,2,3,4,6,8,12,16,24,32,48,64,80,100]
  resonances=scan(self.s,self.T)
  for en,width,l in resonances:
   if width>1e-10:
    bounds.extend([(en+j*width)/self.T for j in [-128,-32,-8,-2,0,2,8,32,128] if 0<(en+j*width)/self.T<100])
  bounds=sorted(set(bounds))
  edges=list(zip(bounds[:-1],bounds[1:]));old=self.evaluate(edges);total=np.zeros_like(old[0]);errors=0
  for iteration in range(22):
   children=[pair for l,r in edges for pair in [(l,(l+r)/2),((l+r)/2,r)]]
   fine=self.evaluate(children).reshape(len(edges),2,len(self.kind),self.M+1,self.M+1)
   err=np.max(abs(fine.sum(axis=1)-old),axis=(1,2,3))
   ok=err<self.tol
   total+=fine[ok].sum(axis=(0,1));errors+=err[ok].sum()
   if np.all(ok):break
   edges=[pair for j,(l,r) in enumerate(edges) if not ok[j] for pair in [(l,(l+r)/2),((l+r)/2,r)]]
   old=fine[~ok].reshape(-1,len(self.kind),self.M+1,self.M+1)
  else:total+=old.sum(axis=0)
  return total

def compute(s1,s2,a,L,x,T,Nmax=12):
 m1,k1=species[s1];m2,k2=species[s2];M=2*Nmax
 st=time.perf_counter();mom=[None]*3
 groups={}
 for j,(mu,kind) in enumerate([(m1/2,k1),(m2/2,k2),(m1*m2/(m1+m2),0)]):
  groups.setdefault(mu,[]).append((j,kind))
 for mu,items in groups.items():
  it=Integrator(a,L,mu,T,M,[kind for j,kind in items]);allmom=it.run()
  for (j,kind),mm in zip(items,allmom):mom[j]=mm
 vals=[]
 for N in range(3,Nmax+1):
  cc=[]
  for q in [1,2]:
   out=np.zeros((2*N,2*N))
   for ma,mb,xx,sl,mm,sp in [(m1,m1,x*x/2,slice(0,N),mom[0],True),(m2,m2,(1-x)**2/2,slice(N,2*N),mom[1],True),(m1,m2,x*(1-x),slice(0,2*N),mom[2],False)]:
    br=Brackets(ma,mb,N,q);sz=br.L+1
    mat=br.integrated(mm[:sz,:sz],sp)
    out[sl,sl]+=xx*mat
   cc.append(out)
  v=np.array(transport(m1,m2,x,T,*cc,N));vals.append(v)
 if Nmax==18:
  scale=np.maximum(abs(vals[-1]),np.array([1e-12,1e-12,1e-12,.05]))
  change=np.max(abs(vals[-1]-vals[-3])/scale)
  if change>2e-6:
   return compute(s1,s2,a,L,x,T,24)
 return vals[-1],mom

if __name__ == '__main__':
    s1, s2 = sys.argv[1:3]
    a, L, x, T = map(float, sys.argv[3:7])
    values, _ = compute(s1, s2, a, L, x, T, 18)
    names = ('viscosity', 'thermal_conductivity', 'binary_diffusion',
             'thermal_diffusion_factor')
    print(json.dumps(dict(zip(names, map(float, values))), allow_nan=False,
                     separators=(',', ':')))
