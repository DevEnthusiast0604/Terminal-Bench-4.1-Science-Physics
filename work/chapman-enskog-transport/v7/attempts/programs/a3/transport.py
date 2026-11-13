#!/usr/bin/env python3
"""Classical Kihara binary-gas transport by collision-bracket Galerkin solution.
Units: sigma = epsilon = k_B = light molecular mass = 1.
"""
import os, sys, json, warnings
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
os.environ['OPENBLAS_MAIN_FREE']='1'
warnings.filterwarnings('ignore')
import numpy as np
from scipy.special import roots_legendre, eval_legendre
from scipy.optimize import minimize_scalar
from time import time

G16,W16=roots_legendre(16); G32,W32=roots_legendre(32)

def orbit(A,E):
    d=1-A
    def H(y):
        return -20/y**12+8/y**6+12*A/d*(1/y**7-2/y**13)
    yc=minimize_scalar(lambda y:-H(y),bounds=(1,3),method='bounded',options={'xatol':1e-14}).x
    Ec=H(yc)
    mask=E<Ec
    lo=np.full_like(E,yc); hi=np.maximum(3.,(30/E)**(1/6))
    for _ in range(55):
        mid=(lo+hi)/2
        low=H(mid)>E
        lo=np.where(low,mid,lo);hi=np.where(low,hi,mid)
    rc=A+d*(lo+hi)/2
    lo=np.ones_like(E);hi=np.full_like(E,yc)
    for _ in range(55):
        mid=(lo+hi)/2
        low=H(mid)<E
        lo=np.where(low,mid,lo);hi=np.where(low,hi,mid)
    rm=A+d*(lo+hi)/2
    V=lambda r:4*((d/(r-A))**12-(d/(r-A))**6)
    bc=rc*np.sqrt(np.maximum(0,1-V(rc)/E))
    return mask,rc,rm,bc,Ec

def angles(A,E,b,rc,rm,bc,mask,tol=1e-8):
    d=1-A
    inner=mask & (b<bc)
    outer=mask & ~inner
    rmin=A+d*(2/(1+np.sqrt(1+E)))**(1/6)
    lo=np.where(outer,rc,rmin)
    hi=np.where(inner,rm,np.maximum(b+d+A,rc+d))
    for _ in range(57):
        mid=(lo+hi)/2
        u=d/(mid-A); f=mid**2*(1-4*(u**12-u**6)/E)
        low=f<b*b
        lo=np.where(low,mid,lo); hi=np.where(low,hi,mid)
    r0=(hi+lo)/2
    u6=(d/(r0-A))**6
    # regularized t=1-s^2; root relation avoids loss of digits
    def integrand(idx,s):
        s2=s*s
        lt=np.log1p(-s2)
        lk=lt-np.log1p(A*s2/(r0[idx,None]-A))
        tt=np.exp(2*lt)
        dif12=-tt*np.expm1(12*lk-2*lt)
        dif6=-tt*np.expm1(6*lk-2*lt)
        f=-np.expm1(2*lt)+4/E[idx,None]*(u6[idx,None]**2*dif12-u6[idx,None]*dif6)
        return 2*s/np.sqrt(np.maximum(f,1e-300))
    nn=len(E)
    cut=np.where(inner,np.sqrt(np.maximum(0,1-r0/rc)),0.)
    idx=np.concatenate([np.arange(nn),np.nonzero(inner)[0]])
    left=np.concatenate([cut,np.zeros(np.count_nonzero(inner))])
    right=np.concatenate([np.ones(nn),cut[inner]])
    result=np.zeros(nn)
    for depth in range(25):
        if len(idx)==0:break
        h=(right-left)/2; mid=(right+left)/2
        i16=np.sum(integrand(idx,mid[:,None]+h[:,None]*G16)*W16,axis=1)*h
        i32=np.sum(integrand(idx,mid[:,None]+h[:,None]*G32)*W32,axis=1)*h
        good=(np.abs(i32-i16)<tol*(1+np.abs(i32))) | (depth==24)
        np.add.at(result,idx[good],i32[good])
        bad=~good
        idx=np.repeat(idx[bad],2)
        left=np.column_stack((left[bad],mid[bad])).ravel()
        right=np.column_stack((mid[bad],right[bad])).ravel()
    return np.pi-2*b/r0*result


def cross_raw(A,E,L,rtol=1e-8):
    E=np.asarray(E,dtype=float)
    mask,rc,rm,bc,Ec=orbit(A,E)
    d=1-A
    yc=minimize_scalar(lambda y:-(-20/y**12+8/y**6+12*A/d*(1/y**7-2/y**13)),bounds=(1,3),method='bounded',options={'xatol':1e-14}).x
    rs=A+d*yc
    vs=4*(yc**(-12)-yc**(-6))
    base=np.where(mask,bc,rs*np.sqrt(1-vs/E))
    scale=np.maximum(.3,E**(-1/6)*(1-A)+A)
    # three regions: below base, immediately above base, and infinite tail
    idx=[];reg=[];left=[];right=[]
    panels=[0,1,2,4,8,12,18,21]
    for e in range(len(E)):
        for j in [0,1]:
            for a,b in zip(panels[:-1],panels[1:]):
                idx.append(e);reg.append(j);left.append(a);right.append(b)
        for a,b in zip([0,.25,.5,.75],[.25,.5,.75,1]):
            idx.append(e);reg.append(2);left.append(a);right.append(b)
    idx=np.array(idx);reg=np.array(reg);left=np.array(left);right=np.array(right)
    out=np.zeros((len(E),L+1))
    def fun(idx,reg,s,w):
        ex=np.exp(-s)
        b=np.where(reg[:,None]==0,base[idx,None]*(1-ex),np.where(reg[:,None]==1,base[idx,None]+scale[idx,None]*ex,(base[idx,None]+scale[idx,None])/s))
        jac=np.where(reg[:,None]==0,base[idx,None]*ex,np.where(reg[:,None]==1,scale[idx,None]*ex,(base[idx,None]+scale[idx,None])/s**2))
        sh=b.shape
        args=[np.broadcast_to(v[idx,None],sh).ravel() for v in [E,rc,rm,bc,mask]]
        chi=angles(A,args[0],b.ravel(),*args[1:],tol=3e-9).reshape(sh)
        # stable 1-P_l(cos chi) recurrence in terms of 1-cos chi
        v=2*np.sin(chi/2)**2
        out=np.zeros((len(idx),L+1))
        p0=np.zeros_like(v);p1=v
        weight=2*np.pi*b*jac*w
        for l in range(1,L+1):
            if l==1:p=p1
            else:
                p=((2*l-1)*(v+(1-v)*p1)-(l-1)*p0)/l
                p0,p1=p1,p
            out[:,l]=np.sum(weight*p,axis=1)
        return out
    for depth in range(22):
        if len(idx)==0:break
        # limit working arrays in angle integrator
        got=[];goodlist=[]
        for start in range(0,len(idx),700):
            sl=slice(start,start+700)
            h=(right[sl]-left[sl])/2; mid=(left[sl]+right[sl])/2
            a=fun(idx[sl],reg[sl],mid[:,None]+h[:,None]*G16,h[:,None]*W16)
            b=fun(idx[sl],reg[sl],mid[:,None]+h[:,None]*G32,h[:,None]*W32)
            err=np.max(np.abs(a-b)/(1+(np.arange(L+1)/12)**4),axis=1)
            target=rtol*base[idx[sl]]**2*(right[sl]-left[sl])/21
            good=(err<target)|(depth==21)
            got.append(b);goodlist.append(good)
        got=np.concatenate(got);good=np.concatenate(goodlist)
        np.add.at(out,idx[good],got[good])
        bad=~good;mid=(left+right)/2
        idx=np.repeat(idx[bad],2);reg=np.repeat(reg[bad],2)
        left=np.column_stack((left[bad],mid[bad])).ravel();right=np.column_stack((mid[bad],right[bad])).ravel()
    return out

def cross(A,E,L,rtol=1e-8):
    E=np.asarray(E,dtype=float)
    ee=np.maximum(E,1e-5)
    unique,inv=np.unique(ee,return_inverse=True)
    q=np.zeros((len(unique),L+1))
    low=unique<.0003
    if np.any(low):q[low]=cross_raw(A,unique[low],L,max(rtol,2e-5))
    if np.any(~low):q[~low]=cross_raw(A,unique[~low],L,rtol)
    q=q[inv]
    small=E<1e-5
    q[small]*=(E[small]/1e-5)[:,None]**(-1/3)
    return q

import numpy as np
from scipy.special import roots_legendre,roots_genlaguerre,gammaln,lpmv
from scipy.linalg import solve
from time import time
from functools import lru_cache

def basis(c,q,t,N,k):
    zz=c[...,None]**2+q[...,None]**2+2*c[...,None]*q[...,None]*t
    pol=np.empty(zz.shape+(N,))
    pol[...,0]=1
    if N>1:pol[...,1]=k+1.5-zz
    for s in range(1,N-1):pol[...,s+1]=((2*s+k+1.5-zz)*pol[...,s]-(s+k+.5)*pol[...,s-1])/(s+1)
    norm=np.sqrt(2*np.exp(gammaln(np.arange(N)+1)+gammaln(k+1.5)-gammaln(np.arange(N)+k+1.5)))
    pol*=norm
    z=c[...,None]+q[...,None]*t
    h=q[...,None]*np.sqrt(1-t*t)
    if k==1:return [z[...,None]*pol,h[...,None]*pol]
    return [((2*z*z-h*h)/3)[...,None]*pol,(h*z)[...,None]*pol,(h*h)[...,None]*pol]

@lru_cache(maxsize=20)
def setup(N,k):
    t,wt=roots_legendre(N+k+1)
    L=N+k
    H=[]
    for m in range(k+1):
        h=np.zeros((len(t),L))
        for l in range(max(1,m),L):
            h[:,l]=lpmv(m,l,t)*np.sqrt((2*l+1)*np.exp(gammaln(l-m+1)-gammaln(l+m+1)))*wt/2
        H.append(h)
    u,wu=roots_genlaguerre(N+k,.5)
    wu/=np.sqrt(np.pi)/2
    return t,wt,L,H,u,wu

def matrix_part(R,X,T,N,k,energy,weight,Q):
    t,wt,L,H,u,wu=setup(N,k)
    w=np.sqrt(energy/T)
    zweight=weight
    masses=[1.,R];xs=[X,1-X]
    B=np.zeros((2*N,2*N))
    factors=[1/3,1/3] if k==1 else [1.5/5,2/5,.5/5]
    for i,j in [(0,0),(0,1)]:
        if i!=j:
            B[N:,N:]=B[:N,:N]*(xs[1]/xs[0])**2/np.sqrt(R)
        a=masses[i];b=masses[j];M=a+b;mu=a*b/M
        c=np.broadcast_to(np.sqrt(a/M*u)[None,:],(len(w),len(u)))
        q=np.broadcast_to(np.sqrt(b/M)*w[:,None],c.shape)
        v=basis(c,q,t,N,k)
        c=np.broadcast_to(np.sqrt(b/M*u)[None,:],c.shape)
        q=np.broadcast_to(-np.sqrt(a/M)*w[:,None],c.shape)
        v2=None if i==j else basis(c,q,t,N,k)
        weight_l=zweight[:,None,None]*np.sqrt(2*T/mu)*wu[None,:,None]*Q[:,None,:L]
        fac=xs[i]*xs[j]*(.5 if i==j else 1)
        for m in range(k+1):
            acoef=np.einsum('eutn,tl->euln',v[m],H[m],optimize=True)
            bcoef=acoef*((-1.)**np.arange(L))[None,None,:,None] if i==j else np.einsum('eutn,tl->euln',v2[m],H[m],optimize=True)
            if i==j:
                p=acoef+bcoef
                pp=p.reshape(-1,N); block=pp.T@(pp*weight_l.reshape(-1,1))
                B[i*N:(i+1)*N,i*N:(i+1)*N]+=fac*factors[m]*block
            else:
                for ii,p in enumerate([acoef,bcoef]):
                    for jj,q in enumerate([acoef,bcoef]):
                        pp=p.reshape(-1,N); qq=q.reshape(-1,N); block=pp.T@(qq*weight_l.reshape(-1,1))
                        B[ii*N:(ii+1)*N,jj*N:(jj+1)*N]+=fac*factors[m]*block
    return (B+B.T)/2

def matrix(R,X,T,N,k,energy,weight,Q):
    B=np.zeros((2*N,2*N))
    chunk=max(2,min(24,1000000//((N+k)*(N+k)*(N))))
    for start in range(0,len(energy),chunk):
        sl=slice(start,start+chunk)
        B+=matrix_part(R,X,T,N,k,energy[sl],weight[sl],Q[sl])
    return B

def properties(Bv,Bh,R,X,T,N):
    # remove total momentum invariant by eliminating one zeroth mode
    cols=list(range(2*N));cols.remove(N)
    P=np.eye(2*N)[:,cols]
    # any representative modulo invariant gives identical physical contractions
    D=np.zeros(2*N);D[0]=np.sqrt(T);D[N]=-np.sqrt(T/R)
    H=np.zeros(2*N);H[1]=-X*np.sqrt(2.5*T);H[N+1]=-(1-X)*np.sqrt(2.5*T/R)
    s=np.stack([D,H],axis=1)
    c=P@solve(P.T@Bh@P,P.T@s,assume_a='pos')
    K=s.T@c
    alpha=K[0,1]/(X*(1-X)*K[0,0])
    diff=X*(1-X)*K[0,0]
    lam=K[1,1]-K[0,1]**2/K[0,0]
    v=np.zeros(2*N);v[0]=X;v[N]=1-X
    eta=T*v@solve(Bv,v,assume_a='pos')
    return np.array([eta,lam,diff,alpha])


@lru_cache(maxsize=30)
def setup2(N,k,nt,L):
 t,wt=roots_legendre(nt)
 H=[]
 for m in range(k+1):
  h=np.zeros((nt,L))
  for l in range(max(1,m),L):h[:,l]=lpmv(m,l,t)*np.sqrt((2*l+1)*np.exp(gammaln(l-m+1)-gammaln(l+m+1)))*wt/2
  H.append(h)
 u,wu=roots_genlaguerre(N+k,.5);wu/=np.sqrt(np.pi)/2
 return t,L,H,u,wu

def pair(R,X,T,N,HN,k,energy,weight,Q,selfpair=False,angular=40):
 nh=N if selfpair else HN
 nt=N+k+1 if selfpair else angular
 L=N+k if selfpair else angular-2
 t,L,H,u,wu=setup2(N,k,nt,L)
 if selfpair:a=b=1.
 else:a=1.;b=R
 M=a+b;mu=a*b/M
 w=np.sqrt(energy/T)
 c=np.broadcast_to(np.sqrt(a/M*u)[None,:],(len(w),len(u)))
 q=np.broadcast_to(np.sqrt(b/M)*w[:,None],c.shape)
 v=basis(c,q,t,N,k)
 c=np.broadcast_to(np.sqrt(b/M*u)[None,:],c.shape)
 q=np.broadcast_to(-np.sqrt(a/M)*w[:,None],c.shape)
 v2=None if selfpair else basis(c,q,t,nh,k)
 weight_l=weight[:,None,None]*np.sqrt(2*T/mu)*wu[None,:,None]*Q[:,None,:L]
 size=N if selfpair else N+nh
 B=np.zeros((size,size));factors=[1/3,1/3] if k==1 else [1.5/5,2/5,.5/5]
 for m in range(k+1):
  ac=np.einsum('eutn,tl->euln',v[m],H[m],optimize=True)
  bc=ac*((-1.)**np.arange(L))[None,None,:,None] if selfpair else np.einsum('eutn,tl->euln',v2[m],H[m],optimize=True)
  if selfpair:
   p=(ac+bc).reshape(-1,N)
   B+=.5*X**2*factors[m]*(p.T@(p*weight_l.reshape(-1,1)))
  else:
   pp=ac.reshape(-1,N);qq=bc.reshape(-1,nh);ww=weight_l.reshape(-1,1)
   fac=X*(1-X)*factors[m]
   B[:N,:N]+=fac*(pp.T@(pp*ww));B[N:,N:]+=fac*(qq.T@(qq*ww))
   block=fac*(pp.T@(qq*ww));B[:N,N:]+=block;B[N:,:N]+=block.T
 return B

def matrix2(R,X,T,N,HN,k,e,w,Q,angular=40):
 B=np.zeros((N+HN,N+HN));chunk=max(2,min(16,500000//((N+k)**2*N)))
 for start in range(0,len(e),chunk):
  sl=slice(start,start+chunk)
  selfb=pair(R,X,T,N,N,k,e[sl],w[sl],Q[sl],True)
  B[:N,:N]+=selfb;B[N:,N:]+=selfb[:HN,:HN]*((1-X)/X)**2/np.sqrt(R)
  B+=pair(R,X,T,N,HN,k,e[sl],w[sl],Q[sl],False,angular)
 return (B+B.T)/2

def vectorprops(B,R,X,T,N,HN):
 ids=list(range(N+HN));ids.remove(N)
 D=np.zeros(N+HN);D[0]=np.sqrt(T);D[N]=-np.sqrt(T/R)
 H=np.zeros(N+HN);H[1]=-X*np.sqrt(2.5*T);H[N+1]=-(1-X)*np.sqrt(2.5*T/R)
 s=np.stack([D,H],axis=1)
 K=s[ids].T@solve(B[np.ix_(ids,ids)],s[ids],assume_a='pos')
 return np.array([K[1,1]-K[0,1]**2/K[0,0],X*(1-X)*K[0,0],K[0,1]/(X*(1-X)*K[0,0])])

from scipy.special import roots_laguerre

def equad2(A,T,N,nq=24):
 ec=orbit(A,np.array([1.]))[-1];zc=ec/T
 cut=max(4.,zc*1.5)
 # very high core threshold at low T: no need to extend low panels beyond 24
 cut=min(cut,24.)
 borders=sorted(set([0.,.005,.02,.1,.3,1.,2.,4.,8.,16.,24.,float(zc),cut]))
 borders=[b for b in borders if b<cut]+[cut]
 z,w=roots_legendre(nq);es=[];ws=[]
 for a,b in zip(borders[:-1],borders[1:]):
  if b-a<1e-12*max(1.,b):continue
  if a==0:
   t=(z+1)/2;zz=b*t**3;ww=b*3*t*t*w/2
  else:
   zz=(a+b)/2+(b-a)*z/2;ww=(b-a)*w/2
  es.extend(zz*T);ws.extend(ww*zz*np.exp(-zz)*2/np.sqrt(np.pi))
 z,w=roots_laguerre(N+25);z+=cut
 es.extend(z*T);ws.extend(w*z*np.exp(-cut)*2/np.sqrt(np.pi))
 return np.array(es),np.array(ws)
def flush_subnormals():
    # These intermediates are at least 280 orders below meaningful brackets.
    try:
        import ctypes, platform
        if platform.machine().lower() in ('x86_64','amd64'):
            lib=ctypes.CDLL(None)
            env=(ctypes.c_uint32*8)()
            if lib.fegetenv(ctypes.byref(env))==0:
                env[7]|=0x8040
                lib.fesetenv(ctypes.byref(env))
    except Exception:
        pass

def main():
    flush_subnormals()
    A,R,X,T=map(float,sys.argv[1:5])
    # Radial order is largest for a light tracer in a much heavier gas.
    if X<.08 and R>8:
        N=120 if R>=40 else 88
        HN=32
        angular=56 if R>=40 else min(N+2,72)
    else:
        N=64 if R>=8 else 44
        HN=N
        angular=N+2
    e,w=equad2(A,T,N,30)
    Q=cross(A,e,max(N+1,angular-3),rtol=1e-7)
    nv=28
    Bv=matrix(R,X,T,nv,2,e,w,Q)
    v=np.zeros(2*nv);v[0]=X;v[nv]=1-X
    eta=T*v@solve(Bv,v,assume_a='pos')
    iv=np.r_[np.arange(18),np.arange(18)+nv]
    sv=v[iv]
    eta18=T*sv@solve(Bv[np.ix_(iv,iv)],sv,assume_a='pos')
    if abs(eta-eta18)>3e-6*eta:
        nv2=44
        bv2=matrix(R,X,T,nv2,2,e,w,Q)
        vv=np.zeros(2*nv2);vv[0]=X;vv[nv2]=1-X
        eta=T*vv@solve(bv2,vv,assume_a='pos')
    if HN==N:
        Bh=matrix(R,X,T,N,1,e,w,Q)
    else:
        Bh=matrix2(R,X,T,N,HN,1,e,w,Q,angular)
    vals=vectorprops(Bh,R,X,T,N,HN)
    # Principal subspaces give independent, nested Galerkin convergence checks.
    smaller=max(HN if HN!=N else 2,N-20)
    sh=HN if HN!=N else smaller
    ix=np.r_[np.arange(smaller),np.arange(sh)+N]
    prev=vectorprops(Bh[np.ix_(ix,ix)],R,X,T,smaller,sh)
    tol=np.array([5e-6*abs(vals[0]),5e-6*abs(vals[1]),max(4e-7,5e-6*abs(vals[2]))])
    if np.any(np.abs(vals-prev)>tol) and N<128:
        nn=min(128,N+32)
        hh=HN if HN!=N else nn
        aa=angular if HN!=N else nn+2
        ee,ww=equad2(A,T,nn,32)
        qq=cross(A,ee,max(nn+1,aa-3),rtol=8e-8)
        bb=matrix2(R,X,T,nn,hh,1,ee,ww,qq,aa) if hh!=nn else matrix(R,X,T,nn,1,ee,ww,qq)
        vals=vectorprops(bb,R,X,T,nn,hh)
    if R==1:vals[2]=0.
    print(json.dumps(dict(zip(['viscosity','thermal_conductivity','binary_diffusion','thermal_diffusion_factor'],map(float,[eta,*vals]))),allow_nan=False))

if __name__=='__main__':
    main()
