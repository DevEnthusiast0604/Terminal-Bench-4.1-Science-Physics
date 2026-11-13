#!/usr/bin/env python3
"""Classical binary-mixture transport for a common spherical-core potential.

Units are sigma = epsilon = k_B = m_1 = n = 1. The collision operator
is assembled from Maxwellian collision brackets in orthonormal Sonine
bases. Vector and traceless-tensor sectors are solved separately. The
vector sources are diffusion and enthalpy transport; eliminating the
relative particle current gives the zero-diffusion heat conductivity.

The centre-of-mass Gaussian integration is analytic. For the vector
sector it is evaluated by a bivariate Sonine generating function. The
tensor sector uses the equivalent Cartesian Hermite expansion. Physical
scattering cross sections are integrated over turning radius, splitting
at orbiting trajectories, then over Maxwellian collision energy.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import sys, json, warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
import numpy as np
from scipy.special import roots_legendre, roots_genlaguerre, eval_genlaguerre, gammaln
from scipy.optimize import brentq, minimize_scalar
from scipy.sparse import coo_matrix
from numpy.polynomial.legendre import legvander
from functools import lru_cache
from math import factorial, comb, sqrt, pi, prod
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.special import roots_legendre
from scipy.optimize import brentq, minimize_scalar
from functools import lru_cache

@lru_cache(None)
def gl(n):
    x,w=roots_legendre(n)
    return (x+1)/2,w/2

def potential(r,a):
    z=((1-a)/(r-a))**6
    return 4*z*(z-1)

def vp(r,a):
    z=((1-a)/(r-a))**6
    return 24*z*(1-2*z)/(r-a)

def F(r,a):
    return potential(r,a)+r*vp(r,a)/2

def geom(E,a):
    z=(1+np.sqrt(1+E))/2
    rp=a+(1-a)*z**(-1/6)
    peak=minimize_scalar(lambda r:-F(r,a),bounds=(a+(1-a)*2**(1/6),a+3*(1-a)),method='bounded',options={'xatol':1e-14}).x
    Ec=F(peak,a)
    if E<Ec:
        ro=brentq(lambda r:F(r,a)-E,peak,max(peak*2, (16*(1-a)**6/E)**(1/6)+a),xtol=1e-14)
        bc2=ro*ro*(1-potential(ro,a)/E)
        ri=brentq(lambda r:F(r,a)-E,rp,peak,xtol=1e-14)
        rc=brentq(lambda r:r*r*(1-potential(r,a)/E)-bc2,rp,ri,xtol=1e-14)
        return rp,ro,rc,bc2,Ec
    return rp,None,None,None,Ec

def chi_batch(r,E,a,n=128,ro=None):
    r=np.asarray(r)
    z=((1-a)/(r-a))**6
    h=1-4*z*(z-1)/E
    t,w=gl(n)
    def part(t,weights):
        t2=t*t
        lh=np.log1p(-t2)-np.log1p(a*t2/(r[:,None]-a))
        dv=4*(-z[:,None]**2*np.expm1(12*lh)+z[:,None]*np.expm1(6*lh))/E
        f=dv+h[:,None]*t2*(2-t2)
        return np.sum(weights*2*t/np.sqrt(np.maximum(f,1e-300)),axis=1)
    if ro is not None:
        # Each segment is clustered near the bottleneck.
        tm=np.sqrt(np.maximum(0,1-r/ro))
        # t = tm(1-s^2) below tm, tm+(1-tm)s^2 above
        s=t[None,:]
        I=part(tm[:,None]*(1-s*s),w[None,:]*2*tm[:,None]*s)
        I+=part(tm[:,None]+(1-tm[:,None])*s*s,w[None,:]*2*(1-tm[:,None])*s)
    else:
        I=part(np.broadcast_to(t,(len(r),n)),w)
    return np.pi-2*np.sqrt(np.maximum(h,0))*I

def cross_sections(E,a,L=16,n=160,nt=128):
    rp,ro,rc,bc,Ec=geom(E,a)
    t,w=gl(n)
    rr=[];ww=[];inner=[]
    if ro is not None:
        # orbiting endpoint, quartic clustering
        r=rc-(rc-rp)*(1-t)**4
        weights=w*4*(rc-rp)*(1-t)**3
        rr.append(r);ww.append(weights);inner.append(True)
        # outer branch: quadratic at orbit, inverse at infinity
        r=ro+(1-a)*t*t/(1-t)
        weights=w*(1-a)*t*(2-t)/(1-t)**2
        rr.append(r);ww.append(weights);inner.append(False)
    else:
        peak=minimize_scalar(lambda r:-F(r,a),bounds=(a+(1-a)*2**(1/6),a+3*(1-a)),method='bounded').x
        # subdivide around the former orbiting region
        bounds=[rp,peak,peak+2*(1-a)]
        for lo,hi in zip(bounds[:-1],bounds[1:]):
            r=lo+(hi-lo)*t
            rr.append(r);ww.append(w*(hi-lo));inner.append(False)
        r=bounds[-1]+(1-a)*t/(1-t)
        rr.append(r);ww.append(w*(1-a)/(1-t)**2);inner.append(False)
    Q=np.zeros(L+1)
    for r,weight,inside in zip(rr,ww,inner):
        c=chi_batch(r,E,a,nt,ro if inside else None)
        z=np.cos(c)
        weight=weight*2*np.pi*r*(1-F(r,a)/E)
        prev=np.ones_like(z);cur=z
        Q[1]+=np.sum(weight*(2*np.sin(c/2)**2))
        for l in range(2,L+1):
            nex=((2*l-1)*z*cur-(l-1)*prev)/l
            Q[l]+=np.sum(weight*(1-nex))
            prev,cur=cur,nex
    return Q

def indices(d):
 return [(i,j,d-i-j) for i in range(d+1) for j in range(d-i+1)]

class Basis:
 def __init__(self,N,l):
  self.N=N;self.l=l;self.dmax=2*N+l
  self.gammas=[g for d in range(self.dmax+1) for g in indices(d)]
  gmap={g:i for i,g in enumerate(self.gammas)}
  self.gammas=np.array(self.gammas)
  nc=3 if l==1 else 6
  self.nc=nc
  rows=[];cols=[];vals=[]
  self.slices=[]
  offset=0
  bmaps=[]
  parities=[(1,0),(0,1),(0,0)] if l==1 else [(0,0),(0,0),(0,0),(1,1),(1,0),(0,1)]
  for k in range(self.dmax+1):
   bs=[(c,b) for c in range(nc) for b in indices(k) if (b[0]%2,b[1]%2)==parities[c]];bmaps.append({b:i for i,b in enumerate(bs)})
   size=(N+1)*len(bs)
   self.slices.append((offset,offset+size,len(bs)))
   offset+=size
  for p in range(N+1):
   d=2*p+l
   norm=(.5 if l==1 else .25)*np.exp(gammaln(p+l+1.5)-gammaln(l+1.5)-gammaln(p+1))
   # tensor order: xx,yy,zz,xy,xz,yz; diagonal trace removed
   coeffs=[{} for _ in range(nc)]
   def add(ci,g,c):coeffs[ci][g]=coeffs[ci].get(g,0)+c
   for ijk in indices(p):
    pre=(-1)**p/(2**d*sqrt(norm)*prod([factorial(x) for x in ijk]))
    if l==1:
     for c in range(3):
      g=tuple(2*ijk[j]+(j==c) for j in range(3)); add(c,g,pre)
    else:
     for c,(ii,jj) in enumerate([(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)]):
      if ii!=jj:
       g=tuple(2*ijk[j]+(j==ii)+(j==jj) for j in range(3));add(c,g,pre*sqrt(2))
      else:
       for axis in range(3):
        g=tuple(2*ijk[j]+2*(j==axis) for j in range(3));add(c,g,pre*((1 if axis==ii else 0)-1/3))
   for c,coeff in enumerate(coeffs):
    for alpha,v in coeff.items():
     if not v:continue
     va=v*sqrt(2**d*prod([factorial(x) for x in alpha]))
     for bx in range(alpha[0]+1):
      for by in range(alpha[1]+1):
       for bz in range(alpha[2]+1):
        beta=(bx,by,bz);k=sum(beta)
        if k==d:continue
        gamma=tuple(alpha[j]-beta[j] for j in range(3))
        if (c,beta) not in bmaps[k]:continue
        start,end,nb=self.slices[k]
        rows.append(start+p*nb+bmaps[k][(c,beta)]);cols.append(gmap[gamma]);vals.append(va*sqrt(prod([comb(alpha[j],beta[j]) for j in range(3)])))
  self.mat=coo_matrix((vals,(rows,cols)),shape=(offset,len(gmap))).tocsr()
  self.mat.eliminate_zeros()
  cc,ww=roots_legendre(self.dmax+1)
  self.cos=np.r_[1.,cc];self.sin=np.sqrt(np.maximum(0,1-self.cos**2))
  from numpy.polynomial.legendre import legvander
  self.project=ww[None,:]/2*(2*np.arange(self.dmax+1)[:,None]+1)*legvander(cc,self.dmax).T
 def amplitudes(self,y):
  xx=np.sqrt(y)*self.sin; zz=np.sqrt(y)*self.cos
  hs=[]
  for x in [xx,np.zeros_like(xx),zz]:
   arr=[np.ones_like(x),sqrt(2)*x]
   for n in range(1,self.dmax):arr.append(sqrt(2/(n+1))*x*arr[-1]-sqrt(n/(n+1))*arr[-2])
   hs.append(np.array(arr))
  g=self.gammas
  H=hs[0][g[:,0]]*hs[1][g[:,1]]*hs[2][g[:,2]]
  return self.mat@H
 def accumulate(self,U,y,weight,Q):
  A=self.amplitudes(y)
  aq=self.project.T@Q[:self.dmax+1]
  for k,(start,end,nb) in enumerate(self.slices[:-1]):
   B=A[start:end].reshape(self.N+1,nb,-1)
   B0=B[:,:,0];BQ=B[:,:,1:]@aq
   z=B0@BQ.T
   U[k]+=weight*(z+z.T)/(3 if self.l==1 else 10)


def kernel(N,y,z,a,b,c,d,r=3.5):
 # arrays y,z broadcast already flattened
 y=y.astype(np.longdouble);z=z.astype(np.longdouble)
 a,b,c,d=map(np.longdouble,(a,b,c,d))
 B=b*b;D=d*d;C=1-a*a-c*c;e=a*c*b*d
 H={(0,0):1.,(1,0):-B,(0,1):-D,(1,1):C}
 H2={}
 for (i,j),v in H.items():
  for (k,l),w in H.items():H2[i+k,j+l]=H2.get((i+k,j+l),0)+v*w
 # derivative numerators F_t H^2 and F_s H^2
 nn={(1,0):B,(0,1):D,(1,1):-2*(B*D+e*z)}
 def numerator(axis):
  out={}
  for (i,j),v in H.items():
   deg=(i,j)[axis]
   if not deg:continue
   ij=(i-1,j) if axis==0 else (i,j-1)
   for (k,l),w in H.items():
    key=(ij[0]+k,ij[1]+l);out[key]=out.get(key,0)-r*v*deg*w
   for (k,l),w in nn.items():
    key=(ij[0]+k,ij[1]+l);out[key]=out.get(key,0)+y*v*deg*w
  for (i,j),v in nn.items():
   deg=(i,j)[axis]
   if not deg:continue
   ij=(i-1,j) if axis==0 else (i,j-1)
   for (k,l),w in H.items():
    key=(ij[0]+k,ij[1]+l);out[key]=out.get(key,0)-y*v*deg*w
  return out
 nt=numerator(0);ns=numerator(1)
 F=np.empty((N+1,N+1,len(y)),dtype=np.longdouble)
 F[0,0]=1.
 # first row with s-derivative
 for q in range(N):
  value=np.zeros(len(y),dtype=np.longdouble)
  for (i,j),v in ns.items():
   if i==0 and j<=q:value+=v*F[0,q-j]
  for (i,j),v in H2.items():
   if i==0 and j>0 and j<=q:value-=v*(q-j+1)*F[0,q-j+1]
  F[0,q+1]=value/(q+1)
 for p in range(N):
  for q in range(N+1):
   value=np.zeros(len(y),dtype=np.longdouble)
   for (i,j),v in nt.items():
    if i<=p and j<=q:value+=v*F[p-i,q-j]
   for (i,j),v in H2.items():
    if (i,j)!=(0,0) and i<=p and j<=q:value-=v*(p-i+1)*F[p-i+1,q-j]
   F[p+1,q]=value/(p+1)
 return F,H

def vector_bracket(N,y,z,w,a,b,c,d):
 t=__import__('time').time();F,H=kernel(N,y,z,a,b,c,d)
 B=b*b;D=d*d;ac=a*c;bd=b*d
 M={(0,0):bd*z,(1,0):-bd*z*B-ac*B,(0,1):-bd*z*D-ac*D,(1,1):bd*z*(B*D+a*a*c*c)+2*ac*B*D}
 U=np.zeros((N+1,N+1))
 norm=.5*np.exp(gammaln(np.arange(N+1)+2.5)-gammaln(2.5)-gammaln(np.arange(N+1)+1))
 for p in range(N+1):
  for q in range(N+1):
   value=np.zeros(len(y),dtype=np.longdouble)
   for (i,j),h in H.items():
    if i<=p and j<=q:value+=1.5*ac*h*F[p-i,q-j]
   for (i,j),v in M.items():
    if i<=p and j<=q:value+=y*v*F[p-i,q-j]
   U[p,q]=value@w*2/(3*sqrt(norm[p]*norm[q]))
 # no diagnostic output
 return U


def nodes(T,a,n=12,ymax=360):
 Ec=geom(1e6,a)[-1];yc=Ec/T
 edges=np.r_[0.,np.geomspace(.00001,1,11),np.arange(2,41,2),np.arange(50,ymax+1,10)]
 if yc<ymax:
  edges=np.r_[edges,yc]
  for delta in [.1,.01,.001,.0001]:edges=np.r_[edges,yc*(1-delta),yc*(1+delta)]
 edges=np.unique(edges);edges=edges[(edges>=0)&(edges<=ymax)]
 z,w=roots_legendre(n)
 return (((edges[:-1]+edges[1:])[:,None]+np.diff(edges)[:,None]*z)/2).ravel(),(np.diff(edges)[:,None]*w/2).ravel()



def tensor_matrix(U,T,R,X,N):
    sz=N+1
    K=np.zeros((2*sz,2*sz))
    masses=[1.,R]; fractions=[X,1-X]
    degree=2*np.arange(sz)+2
    for i,j in [(0,0),(1,1),(0,1)]:
        mi,mj=masses[i],masses[j]
        mu=mi*mj/(mi+mj)
        ai=sqrt(mi/(mi+mj)); bi=sqrt(mj/(mi+mj))
        rate=(.25 if i==j else .5)*fractions[i]*fractions[j]*sqrt(2*T/mu)
        for k,V in enumerate(U):
            ci=ai**k*bi**(degree-k)
            cj=bi**k*(-ai)**(degree-k)
            if i==j:
                c=ci+cj
                K[i*sz:(i+1)*sz,i*sz:(i+1)*sz]+=rate*V*c[:,None]*c[None,:]
            else:
                for a,ca in [(i,ci),(j,cj)]:
                    for b,cb in [(i,ci),(j,cj)]:
                        K[a*sz:(a+1)*sz,b*sz:(b+1)*sz]+=rate*V*ca[:,None]*cb[None,:]
    return (K+K.T)/2

def integrated_pair(N,yy,zz,weights,angular,pair):
    aa,bb,cc,dd=pair
    V=np.zeros((N+1,N+1),dtype=np.longdouble)
    for j in range(0,len(yy),12):
        y=yy[j:j+12]
        w=weights[j:j+12,None]*angular[j:j+12]
        V+=vector_bracket(N,np.repeat(y,len(zz)),np.tile(zz,len(y)),w.ravel(),aa,bb,cc,dd)
    return np.asarray(V,dtype=float)

def compute(A,R,X,T):
    # Mass contrast controls the slow velocity-space convergence.
    N=32 if R<=3. else 64
    NT=16
    yy,wy=nodes(T,A,24)
    zz,wz=roots_legendre(N+3)
    projection=wz[None,:]/2*(2*np.arange(N+3)[:,None]+1)*legvander(zz,N+2).T
    Q=np.array([cross_sections(T*y,A,N+2,320,256) for y in yy])
    weights=wy*yy*np.exp(-yy)*2/sqrt(pi)
    angular=Q@projection
    pair_matrices=[]
    a=sqrt(1/(1+R)); b=sqrt(R/(1+R)); s=sqrt(.5)
    pairs=[(s,s,s,s),(s,s,s,-s)]
    if R!=1.: pairs += [(a,b,a,b),(b,a,b,a),(a,b,b,-a)]
    with ProcessPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(integrated_pair,N,yy,zz,weights,angular,pair) for pair in pairs]
        pair_matrices=[future.result() for future in futures]
    if R==1.:
        pair_matrices += [pair_matrices[0],pair_matrices[0],pair_matrices[1]]
    V,C,L,H,B=pair_matrices
    sz=N+1; K=np.zeros((2*sz,2*sz))
    K[:sz,:sz]+=.25*X*X*sqrt(4*T)*(2*V+C+C.T)
    K[sz:,sz:]+=.25*(1-X)**2*sqrt(4*T/R)*(2*V+C+C.T)
    rate=.5*X*(1-X)*sqrt(2*T*(1+R)/R)
    K[:sz,:sz]+=rate*L; K[sz:,sz:]+=rate*H
    K[:sz,sz:]+=rate*B; K[sz:,:sz]+=rate*B.T
    K=(K+K.T)/2
    sd=np.zeros(2*sz); sh=sd.copy(); null=sd.copy()
    for i in range(2):
        mi=[1.,R][i]; xi=[X,1-X][i]
        sd[i*sz]=(1 if i==0 else -1)*sqrt(T/mi)
        sh[i*sz+1]=-xi*sqrt(5*T/(2*mi))
        null[i*sz]=sqrt(mi)
    # Lift only the conserved total-momentum null direction.
    K+=np.outer(null,null)/np.dot(null,null)*np.max(np.diag(K))
    sol=np.linalg.solve(K,np.array([sd,sh]).T)
    dd,dh=sd@sol; hd,hh=sh@sol
    conductivity=hh-dh*hd/dd
    diffusion=X*(1-X)*dd
    alpha=dh/(X*(1-X)*dd)
    if R==1.: alpha=0.
    # The finite tensor kernels are energy polynomials, so this projection
    # followed by Gaussian integration is exactly their moment contraction.
    M=np.array([eval_genlaguerre(j,1,yy)/(j+1) for j in range(2*NT+3)])
    M=(M*(wy*yy*np.exp(-yy)))@Q[:,:2*NT+3]
    basis=Basis(NT,2)
    UT=np.zeros((basis.dmax,NT+1,NT+1))
    y,w=roots_genlaguerre(2*NT+3,1)
    QQ=np.array([eval_genlaguerre(j,1,y) for j in range(2*NT+3)]).T@M
    for yi,wi,qi in zip(y,w,QQ):
        basis.accumulate(UT,yi,wi*2/sqrt(pi),qi)
    KT=tensor_matrix(UT,T,R,X,NT)
    source=np.zeros(2*(NT+1));source[0]=X;source[NT+1]=1-X
    viscosity=T*source@np.linalg.solve(KT,source)
    return dict(viscosity=float(viscosity),thermal_conductivity=float(conductivity),
                binary_diffusion=float(diffusion),thermal_diffusion_factor=float(alpha))

if __name__ == '__main__':
    A,R,X,T=map(float,sys.argv[1:5])
    print(json.dumps(compute(A,R,X,T),allow_nan=False,separators=(',',':')))
