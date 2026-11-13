#!/usr/bin/env python3
"""Classical dilute binary Kihara-gas transport.

Units: sigma = epsilon = k_B = lighter molecular mass = 1.
Collision brackets are evaluated with Maxwellian generating functions for
vector and traceless-tensor Laguerre (Sonine) polynomials.  Scattering is
integrated on the physically accessible turning-radius branches, separating
orbiting trajectories. Nested Galerkin spaces control the integral-equation
solution error; no tabulated transport correlations are used.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import sys, json, warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

from scipy.signal import lfilter

def series_integrated(nu,orders,e,h,a,b,p,q,polys,base):
    N,M=orders; B=b*b; C=q*q; E=1-a*a-p*p; F=B*C+a*p*b*q*h
    shape=np.broadcast_shapes(e.shape,h.shape)
    W=np.array([np.broadcast_to(v,shape)*base for v in polys.values()])
    keys=list(polys)
    out=np.zeros((N+1,M+1))
    curr=np.empty((M+1,)+shape); prev=np.zeros_like(curr); nxt=np.zeros_like(curr)
    for m in range(M+1): curr[m]=C**m*eval_genlaguerre(m,nu-1,e)
    for n in range(N+1):
        ints=np.einsum('muv,kuv->km',curr,W,optimize=True)
        for k,(i,j) in enumerate(keys):
            if n+i<=N and j<=M: out[n+i,j:]+=ints[k,:M+1-j]
        if n==N: break
        v0=B*(nu-e+2*n)
        v1=-(nu+2*n)*(E+B*C)+2*e*F
        v2=(nu+2*n)*C*E-e*(2*F*C-C*E)
        w0=-(nu+n-1)*B*B
        w1=2*(nu+n-1)*B*E
        w2=-(nu+n-1)*E*E
        nxt[:]=(v0*curr+w0*prev)/(n+1)
        nxt[1:]+=(v1*curr[:-1]+w1*prev[:-1])/(n+1)
        nxt[2:]+=(v2*curr[:-2]+w2*prev[:-2])/(n+1)
        nxt=lfilter([1.],[1.,-2*C,C*C],nxt,axis=0)
        prev,curr,nxt=curr,nxt,prev
    return out

def integrated_correlation(l,orders,e,h,a,b,p,q,base):
    ap=a*p; bq=b*q; B=b*b; C=q*q
    H={(0,0):bq*h,(1,0):-bq*B*h-ap*B,(0,1):-bq*C*h-ap*C,(1,1):bq*(B*C+ap*ap)*h+2*ap*B*C}
    if l==1:
        out=series_integrated(2.5,orders,e,h,a,b,p,q,{(0,0):1.5*ap},base)
        out+=series_integrated(3.5,orders,e,h,a,b,p,q,{k:e*v for k,v in H.items()},base)
    else:
        out=series_integrated(3.5,orders,e,h,a,b,p,q,{(0,0):2.5*ap*ap},base)
        out+=series_integrated(4.5,orders,e,h,a,b,p,q,{k:(10/3)*ap*e*v for k,v in H.items()},base)
        Hc={(0,0):B,(0,1):-2*B*C-2*ap*bq*h,(0,2):B*C*C+ap*ap*C+2*ap*bq*C*h}
        Hd={(0,0):C,(1,0):-2*B*C-2*ap*bq*h,(2,0):C*B*B+ap*ap*B+2*ap*bq*B*h}
        HH=polymul(H,H); CD=polymul(Hc,Hd)
        for k,v in CD.items(): HH[k]=HH.get(k,0)-v/3
        out+=series_integrated(5.5,orders,e,h,a,b,p,q,{k:e*e*v for k,v in HH.items()},base)
    return out


import numpy as np
from scipy.special import roots_genlaguerre, roots_legendre, eval_genlaguerre, gammaln
from scipy.linalg import solve
import time

def series(nu,N,e,h,a,b,p,q):
    M=N if isinstance(N,int) else N[1]
    N=N if isinstance(N,int) else N[0]
    B=b*b; C=q*q; E=1-a*a-p*p; F=B*C+a*p*b*q*h
    shape=np.broadcast_shapes(e.shape,h.shape)
    out=np.zeros((N+1,M+1)+shape)
    for m in range(M+1):
        out[0,m]=C**m*eval_genlaguerre(m,nu-1,e)
    for n in range(N):
        v0=B*(nu-e+2*n)
        v1=-(nu+2*n)*(E+B*C)+2*e*F
        v2=(nu+2*n)*C*E-e*(2*F*C-C*E)
        w0=-(nu+n-1)*B*B
        w1=2*(nu+n-1)*B*E
        w2=-(nu+n-1)*E*E
        for m in range(M+1):
            val=v0*out[n,m]
            if m>=1: val=val+v1*out[n,m-1]+(n+1)*2*C*out[n+1,m-1]
            if m>=2: val=val+v2*out[n,m-2]-(n+1)*C*C*out[n+1,m-2]
            if n>=1:
                val=val+w0*out[n-1,m]
                if m>=1: val=val+w1*out[n-1,m-1]
                if m>=2: val=val+w2*out[n-1,m-2]
            out[n+1,m]=val/(n+1)
    return out

def polyadd(dst,src,poly):
    N=dst.shape[0]-1; M=dst.shape[1]-1
    for (i,j),v in poly.items():
        if i<=N and j<=M:
            dst[i:,j:]+=v*src[:N+1-i,:M+1-j]

def polymul(P,Q):
    out={}
    for (i,j),v in P.items():
        for (k,l),w in Q.items():
            key=(i+k,j+l)
            out[key]=out.get(key,0)+v*w
    return out

def correlation(l,N,e,h,a,b,p,q):
    ap=a*p; bq=b*q; B=b*b; C=q*q
    H={(0,0):bq*h,(1,0):-bq*B*h-ap*B,(0,1):-bq*C*h-ap*C,(1,1):bq*(B*C+ap*ap)*h+2*ap*B*C}
    if l==1:
        out=1.5*ap*series(2.5,N,e,h,a,b,p,q)
        polyadd(out,series(3.5,N,e,h,a,b,p,q),{k:e*v for k,v in H.items()})
    else:
        out=2.5*ap*ap*series(3.5,N,e,h,a,b,p,q)
        polyadd(out,series(4.5,N,e,h,a,b,p,q),{k:(10/3)*ap*e*v for k,v in H.items()})
        Hc={(0,0):B,(0,1):-2*B*C-2*ap*bq*h,(0,2):B*C*C+ap*ap*C+2*ap*bq*C*h}
        Hd={(0,0):C,(1,0):-2*B*C-2*ap*bq*h,(2,0):C*B*B+ap*ap*B+2*ap*bq*B*h}
        HH=polymul(H,H); CD=polymul(Hc,Hd)
        for k,v in CD.items(): HH[k]=HH.get(k,0)-v/3
        polyadd(out,series(5.5,N,e,h,a,b,p,q),{k:e*e*v for k,v in HH.items()})
    return out

def angle_weights(L,h,wh,Q):
    # Q shape energies x L
    P0=np.ones_like(h); P1=h.copy()
    out=np.zeros((len(Q),len(h)))
    for l in range(1,L+1):
        if l==1: P=P1
        else:
            P=((2*l-1)*h*P1-(l-1)*P0)/l
            P0,P1=P1,P
        out+=(2*l+1)*Q[:,l-1,None]*P[None,:]*wh[None,:]/2
    return out

def matrix(l,N,R,X,T,e,we,Q,H=None):
    H=N if H is None else min(H,N)
    L=N+l
    h,wh=roots_legendre(L+1)
    aw=angle_weights(L,h,wh,Q[:,:L])
    base=we[:,None]*aw
    def integrate(a,b,p,q,mu,orders=None):
        orders=(N,N) if orders is None else orders
        vals=np.zeros((orders[0]+1,orders[1]+1))
        for start in range(0,len(e),16):
            sl=slice(start,start+16)
            vals+=integrated_correlation(l,orders,e[sl,None],h[None,:],a,b,p,q,base[sl])
        vals*=2/np.sqrt(np.pi)*np.sqrt(2*T/mu)
        return (vals+vals.T)/2 if a==p and b==q and orders[0]==orders[1] else vals
    r=np.sqrt(.5)
    self1=integrate(r,r,r,r,.5)+integrate(r,r,r,-r,.5)
    self2=self1[:H+1,:H+1]/np.sqrt(R)
    a=np.sqrt(1/(1+R)); b=np.sqrt(R/(1+R)); mu=R/(1+R)
    aa=integrate(a,b,a,b,mu)
    bb=integrate(b,-a,b,-a,mu,(H,H))
    ab=integrate(a,b,b,-a,mu,(N,H))
    x=X; y=1-X
    small=np.block([[x*x*self1+x*y*aa,x*y*ab],[x*y*ab.T,y*y*self2+x*y*bb]])
    ix=np.r_[np.arange(N+1),N+1+np.arange(H+1)]
    B=np.eye(2*(N+1)); B[np.ix_(ix,ix)]=small
    # Normalize each Sonine basis to unit Maxwell norm.
    norm=np.sqrt(np.exp(gammaln(np.arange(N+1)+l+1.5)-gammaln(np.arange(N+1)+1)-gammaln(l+1.5))*(1.5 if l==1 else 2.5))
    norm=np.tile(norm,2)
    if l==1:
        # The total pair momentum is exactly invariant.  Determine the
        # species-2 constant-vector row from that identity, avoiding loss
        # of significance in small angular transport differences.
        j=N+1
        B[j,:]=-B[0,:]/np.sqrt(R)
        B[:,j]=B[j,:]
        B[j,j]=B[0,0]/R
    B/=norm[:,None]*norm[None,:]
    return B,norm

def transport(N,R,X,T,e,we,Q):
    B2,norm2=matrix(2,N,R,X,T,e,we,Q)
    B1,norm1=matrix(1,N,R,X,T,e,we,Q)
    return transport_matrices(N,R,X,T,B2,norm2,B1,norm1)

def transport_matrices(N,R,X,T,B2,norm2,B1,norm1):
    big=len(norm1)//2-1
    ix=np.r_[np.arange(N+1),big+1+np.arange(N+1)]
    B=B2[np.ix_(ix,ix)].copy(); norm=norm2[ix]
    rhs=np.zeros(2*(N+1)); rhs[0]=5*X; rhs[N+1]=5*(1-X)
    aa=solve(B,rhs/norm,assume_a='sym')/norm
    eta=T/2*(X*aa[0]+(1-X)*aa[N+1])
    B=B1[np.ix_(ix,ix)].copy(); norm=norm1[ix]
    rhs=np.zeros((2*(N+1),2))
    rhs[0,0]=1.5*np.sqrt(2*T); rhs[N+1,0]=-1.5*np.sqrt(2*T/R)
    rhs[1,1]=-3.75*X*np.sqrt(2*T); rhs[N+2,1]=-3.75*(1-X)*np.sqrt(2*T/R)
    null=np.zeros(2*(N+1)); null[0]=X; null[N+1]=(1-X)*np.sqrt(R)
    null/=norm
    border=np.zeros((len(B)+1,len(B)+1)); border[:-1,:-1]=B; border[-1,:-1]=null; border[:-1,-1]=null
    rr=np.zeros((len(B)+1,2)); rr[:-1]=rhs/norm[:,None]
    ab=solve(border,rr,assume_a='sym')[:-1]/norm[:,None]
    delta=ab[0]-ab[N+1]/np.sqrt(R)
    D=X*(1-X)*np.sqrt(2*T)/2*delta[0]
    ratio=delta[1]/delta[0]
    h=ab[:,1]-ratio*ab[:,0]
    lam=-1.25*np.sqrt(2*T)*(X*h[1]+(1-X)*h[N+2]/np.sqrt(R))
    alpha=ratio/(X*(1-X))
    return np.array([eta,lam,D,alpha])

import numpy as np
from scipy.special import roots_legendre
from scipy.optimize import brentq, minimize_scalar
from functools import lru_cache

@lru_cache(None)
def gauss(n):
 x,w=roots_legendre(n)
 return (x+1)/2,w/2

def potential(r,A):
 z=(1-A)/(r-A); z6=z**6
 return 4*z6*(z6-1)

def deriv(r,A):
 z=(1-A)/(r-A); z6=z**6
 return 24*z6*(1-2*z6)/(r-A)

def orbit_energy(r,A):
 return potential(r,A)+r*deriv(r,A)/2

@lru_cache(None)
def critical(A):
 rm=A+(1-A)*2**(1/6)
 opt=minimize_scalar(lambda r:-orbit_energy(r,A),bounds=(rm,rm+2),method='bounded',options={'xatol':1e-14})
 return opt.x,orbit_energy(opt.x,A)

def branches(A,E):
 rc,ec=critical(A)
 z6=(1+np.sqrt(1+E))/2
 r0=A+(1-A)*z6**(-1/6)
 if E>=ec: return r0,None,None
 ro=brentq(lambda r:orbit_energy(r,A)-E,rc,max(rc*2,2+5*(1/E)**(1/6)),xtol=1e-14)
 ri=brentq(lambda r:orbit_energy(r,A)-E,A+(1-A)*2**(1/6),rc,xtol=1e-14)
 Bc=ro*ro*(1-potential(ro,A)/E)
 rin=brentq(lambda r:r*r*(1-potential(r,A)/E)-Bc,r0,ri,xtol=1e-14)
 return r0,ro,rin

def radial(rt,u,A,E):
 t=1-u*u
 z6=((1-A)/(rt-A))**6
 ld=np.log1p(-rt*u*u/(rt-A*t))
 diff=4*(z6*z6*np.expm1(12*ld)-z6*np.expm1(6*ld))
 return u*u*(2-u*u)*(1-4*z6*(z6-1)/E)-diff/E

def deflect(rt,A,E,ro=None,n=160):
 rt=np.asarray(rt); b2=rt*rt*(1-potential(rt,A)/E)
 u,w=gauss(n)
 # transform t=1-u^2 to remove the turning-point square root
 if ro is None:
  uu=u[None,:]; ww=w[None,:]
  t=1-uu*uu
  r=rt[:,None]/t
  f=radial(rt[:,None],uu,A,E)
  return np.pi-4*np.sqrt(b2)/rt*np.sum(ww*uu/np.sqrt(np.maximum(f,1e-300)),axis=1)
 # Inner branch: subdivide about the orbiting bottleneck in u.
 uc=np.sqrt(np.maximum(0,1-rt/ro))
 delta=np.maximum(0,ro*ro*(1-potential(ro,A)/E)-b2)
 width=np.minimum(.08,np.maximum(2e-7,np.sqrt(delta)/(4*ro)))
 edges=np.column_stack([np.zeros(len(rt)),np.maximum(0,uc-8*width),np.maximum(0,uc-width),uc,np.minimum(1,uc+width),np.minimum(1,uc+8*width),np.ones(len(rt))])
 edges=np.sort(np.clip(edges,0,1),axis=1)
 total=np.zeros(len(rt))
 for j in range(edges.shape[1]-1):
  lo=edges[:,j,None]; span=edges[:,j+1,None]-lo
  uu=lo+span*u; t=1-uu*uu; r=rt[:,None]/t
  f=radial(rt[:,None],uu,A,E)
  total+=np.sum(span*w*uu/np.sqrt(np.maximum(f,1e-300)),axis=1)
 return np.pi-4*np.sqrt(b2)/rt*total

def cross_sections(A,E,L,n=100,ndef=160):
 r0,ro,rin=branches(A,E)
 u,w=gauss(n)
 rs=[]; ws=[]
 if ro is not None:
  # quadratic clustering on both sides of the critical impact parameter
  for lo,hi in [(0,.5),(.5,.9),(.9,.99),(.99,.9999),(.9999,.99999999)]:
   v=lo+(hi-lo)*u; rt=r0+(rin-r0)*v
   db=2*rt*(1-potential(rt,A)/E)-rt*rt*deriv(rt,A)/E
   rs.append(rt); ws.append(w*(hi-lo)*(rin-r0)*np.pi*db)
  outer=ro
 else: outer=r0
 # outer branch, range to infinity. Geometric partition resolves critical limit.
 bounds=[0,.0001,.001,.01,.05,.2,.5,.8,.95,.98]
 rc,ec=critical(A)
 if ro is None and E<ec*1.15:
  vc=(rc-outer)/(1+rc-outer)
  dv=max(1e-7, min(.03,np.sqrt(max(0,E/ec-1))*.05))
  bounds=sorted(set(bounds+[max(0,min(.98,vc+k*dv)) for k in [-8,-2,-.5,0,.5,2,8]]))
 rtout=[]; wtout=[]
 for lo,hi in zip(bounds[:-1],bounds[1:]):
  v=lo+(hi-lo)*u
  rt=outer+v/(1-v)
  db=2*rt*(1-potential(rt,A)/E)-rt*rt*deriv(rt,A)/E
  rtout.append(rt); wtout.append(w*(hi-lo)/(1-v)**2*np.pi*db)
 rtout=np.concatenate(rtout); wtout=np.concatenate(wtout)
 co=np.cos(deflect(rtout,A,E,n=ndef))
 if rs:
  ri=np.concatenate(rs); wi=np.concatenate(ws)
  ci=np.cos(deflect(ri,A,E,ro,n=ndef))
  co=np.concatenate([ci,co]); wtout=np.concatenate([wi,wtout])
 # Use stable small-angle recurrence for 1-P_l(cos chi).
 z=1-co; pm=np.zeros_like(z); p=z.copy(); Q=[]
 for l in range(1,L+1):
  if l>1:
   pp=((2*l-1)*(z+(1-z)*p)-(l-1)*pm)/l
   pm,p=p,pp
  Q.append(np.dot(wtout,p))
 return np.array(Q)


def energy_grid(A,T,order,ng=40):
    ec=critical(A)[1]/T
    bounds=sorted(set([0,min(ec,70),.05,.15,.4,1,2,4,8,16,32,55,90,150,max(200,2.8*order)]))
    u,w=gauss(ng)
    e=np.concatenate([lo+(hi-lo)*u for lo,hi in zip(bounds[:-1],bounds[1:])])
    we=np.concatenate([(hi-lo)*w for lo,hi in zip(bounds[:-1],bounds[1:])])*e*np.exp(-e)
    return e,we

def calculate(A,R,X,T):
    if R>50 and X<.08: N=76
    elif R>25 and X<.2: N=56
    elif R>10: N=40
    else: N=32
    e,we=energy_grid(A,T,N)
    Q=np.array([cross_sections(A,T*z,N+2,130,260) for z in e])
    B2,n2=matrix(2,20,R,X,T,e,we,Q)
    B1,n1=matrix(1,N,R,X,T,e,we,Q,H=24 if R>25 else N)
    def evaluate(n,B1,n1):
        big=len(n1)//2-1
        ix=np.r_[np.arange(21),big+1+np.arange(21)]
        BB=np.eye(2*(big+1)); NN=np.ones(2*(big+1))
        BB[np.ix_(ix,ix)]=B2; NN[ix]=n2
        return transport_matrices(n,R,X,T,BB,NN,B1,n1)
    vals=evaluate(N,B1,n1)
    prev=evaluate(max(21,N-12),B1,n1)
    tol=np.maximum(np.abs(vals)*3e-6,np.array([0,0,0,1.5e-7]))
    if np.any(np.abs(vals-prev)>tol) and N<100:
        M=min(104,N+24)
        e,we=energy_grid(A,T,M)
        Q=np.array([cross_sections(A,T*z,M+2,130,260) for z in e])
        B1,n1=matrix(1,M,R,X,T,e,we,Q,H=24 if R>25 else M)
        vals=evaluate(M,B1,n1)
    if R==1: vals[3]=0.
    return vals

def main():
    A,R,X,T=map(float,sys.argv[1:5])
    vals=calculate(A,R,X,T)
    print(json.dumps(dict(zip(['viscosity','thermal_conductivity','binary_diffusion','thermal_diffusion_factor'],map(float,vals))),allow_nan=False,separators=(',',':')))

if __name__=='__main__':
    main()
