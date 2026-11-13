#!/usr/bin/env python3
"""Classical binary-gas transport from converged Boltzmann collision brackets.

Units: sigma = epsilon = k_B = mass of species 1 = 1.
Angular collision integrals are evaluated from classical central-force orbits.
The variational vector and traceless-tensor equations use Laguerre polynomials
and exact finite spherical-harmonic angular projections.  Energy quadrature
and nested polynomial spaces resolve the non-polynomial collision operator.
"""
import os
for _key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
import sys, json, math, multiprocessing
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.special import roots_legendre
from scipy.optimize import brentq
import time
G16,W16=roots_legendre(16)
G32,W32=roots_legendre(32)

def potential(r,a):
    h=((1-a)/(r-a))**6
    return 4*h*(h-1)

def critical(a,E):
    s=1-a
    def ec(t):
        h=t**-6
        return 4*h*(2-5*h+3*a/(s*t)*(1-2*h))
    # E at a stationary point of b(r)^2
    opt=__import__('scipy.optimize',fromlist=['minimize_scalar']).minimize_scalar(lambda z:-ec(np.exp(z)),bounds=(np.log(2**(1/6)),np.log(5)),method='bounded')
    tm=np.exp(opt.x)
    if E>=ec(tm): return None
    tc=brentq(lambda t:ec(t)-E,tm,max(10,(16/E)**(1/6)))
    ti=brentq(lambda t:ec(t)-E,1,tm)
    rc=a+s*tc
    bc=rc*np.sqrt(1-potential(rc,a)/E)
    return rc,bc,a+s*ti

def turning(b,a,E,crit):
    s=1-a
    h0=(1+np.sqrt(1+E))/2
    r0=a+s*h0**(-1/6)
    lo=np.full_like(b,r0)
    hi=b+r0
    if crit is not None:
        rc,bc,ri=crit
        lo=np.where(b>bc,rc,lo)
        hi=np.where(b>bc,hi,ri)
    for j in range(57):
        r=(lo+hi)/2
        f=r*r*(1-potential(r,a)/E)-b*b
        good=f>0
        hi=np.where(good,r,hi)
        lo=np.where(good,lo,r)
    return (lo+hi)/2

def deflections(b,a,E,crit,tol=2e-9):
    r=turning(b,a,E,crit)
    tolerances=np.full_like(b,tol)
    if crit is not None: tolerances=np.maximum(tolerances,2e-13/(np.abs(b/crit[1]-1)+1e-14))
    # u=rmin/r=1-v^2 cancels the turning-point singularity
    owner=np.arange(len(b))
    left=np.zeros(len(b)); right=np.ones(len(b))
    if crit is not None:
        rc,bc,ri=crit
        ix=np.flatnonzero((b<bc)&(r<rc))
        v=np.sqrt(np.maximum(0,1-r[ix]/rc))
        owner=np.r_[owner,ix]
        right[ix]=v
        left=np.r_[left,v];right=np.r_[right,np.ones(len(ix))]
    sums=np.zeros(len(b))
    rb=(b/r)**2
    h=((1-a)/(r-a))**6
    # Stable subtraction from the turning condition:
    # F(u)= (b/r)^2(1-u^2)+(V(r)-V(r/u))/E
    for it in range(35):
        def evaluate(nodes,weights):
            v=(left[:,None]+right[:,None])/2+(right-left)[:,None]/2*nodes
            u=1-v*v
            rr=r[owner,None]
            # h(u)/h(1), using expm1 to maintain precision near u=1
            d=(rr*v*v)/(rr-a)
            lr=6*(np.log1p(-v*v)-np.log1p(a*v*v/(rr-a)))
            dh=np.expm1(lr)
            hh=h[owner,None]
            hm1=(E*(1-rb[owner,None]))/(4*hh)
            dv=-4*hh*dh*(hm1+hh*np.exp(lr))
            f=rb[owner,None]*v*v*(2-v*v)+dv/E
            f=np.maximum(f,1e-300)
            vals=2*v*(b/r)[owner,None]/np.sqrt(f)
            return (right-left)/2*(vals@weights)
        q16=evaluate(G16,W16); q32=evaluate(G32,W32)
        err=np.abs(q32-q16)
        ok=(err<tolerances[owner]+2e-10*np.abs(q32))|((right-left)<1e-10)
        np.add.at(sums,owner[ok],q32[ok])
        if np.all(ok): break
        own=owner[~ok];l=left[~ok];rr=right[~ok];mid=(l+rr)/2
        owner=np.repeat(own,2)
        left=np.column_stack((l,mid)).ravel();right=np.column_stack((mid,rr)).ravel()
    else:
        np.add.at(sums,owner,evaluate(G32,W32))
    return np.pi-2*sums

def cross_sections(a,E,L=12,tol=2e-8):
    crit=critical(a,E)
    scale=a+(1-a)*max(E**(-1/6),E**(-1/12))
    cuts=[0.,50/51]
    if crit is not None:
        bc=crit[1];cuts=[0.,bc*(1-1e-8)/(bc*(1-1e-8)+scale),bc*(1+1e-8)/(bc*(1+1e-8)+scale),50/51]
    left=np.array(cuts[:-1]);right=np.array(cuts[1:])
    if crit is not None:
        left=left[[0,2]];right=right[[0,2]]
    ans=np.zeros(L)
    for iteration in range(30):
        def evaluate(nodes,weights):
            z=(left[:,None]+right[:,None])/2+(right-left)[:,None]/2*nodes
            b=scale*z/(1-z)
            chi=deflections(b.ravel(),a,E,crit).reshape(b.shape)
            dc=2*np.sin(chi/2)**2
            ds=[np.zeros_like(dc),dc]
            for l in range(2,L+1):
                ds.append((2*l-1)/l*(ds[-1]+dc*(1-ds[-1]))-(l-1)/l*ds[-2])
            vals=np.stack(ds[1:],axis=-1)*(2*np.pi*scale**2*z/(1-z)**3)[:,:,None]
            return (right-left)[:,None]/2*np.einsum('pnl,n->pl',vals,weights)
        q16=evaluate(G16,W16);q32=evaluate(G32,W32)
        err=np.max(np.abs(q32-q16),axis=1)
        ref=np.maximum(np.max(np.abs(q32),axis=1),scale**2*(right-left))
        ok=(err<tol*(ref+scale**2))|((right-left)<2e-9)
        ans+=np.sum(q32[ok],axis=0)
        if np.all(ok): return ans
        l=left[~ok];r=right[~ok];mid=(l+r)/2
        left=np.column_stack((l,mid)).ravel();right=np.column_stack((mid,r)).ravel()
    return ans+np.sum(q32,axis=0)


import numpy as np
from scipy.special import roots_genlaguerre, roots_legendre, eval_genlaguerre, lpmv, gammaln
from scipy.linalg import solve
import time

def angular_basis(N,rank):
    u,wu=roots_legendre(N+3)
    L=N+rank
    projs=[]
    for m in range(rank+1):
        out=np.zeros((len(u),L))
        for l in range(max(1,m),L+1):
            out[:,l-1]=lpmv(m,l,u)*np.exp(.5*(np.log(2*l+1)+gammaln(l-m+1)-gammaln(l+m+1)))*wu/2
        projs.append(out)
    return u,projs

def pair_matrix_chunk(N,rank,mi,mj,z,wz,Q,T,same=False):
    L=N+rank
    u,proj=angular_basis(N,rank)
    s,ws=roots_genlaguerre(N+2,.5);ws/=np.sqrt(np.pi)/2
    # arrays shape energy, CM magnitude, polar angle
    aa=np.sqrt(mi/(mi+mj));bb=np.sqrt(mj/(mi+mj))
    c=np.sqrt(s)[None,:,None];h=np.sqrt(z)[:,None,None]
    sn=np.sqrt(1-u*u)[None,None,:];uu=u[None,None,:]
    coeff=[]
    for v0,t0 in [(aa*c,bb*h),(bb*c,-aa*h)]:
        vv=v0+t0*uu
        w2=v0*v0+t0*t0+2*v0*t0*uu
        lag=np.empty(w2.shape+(N,))
        lag[...,0]=1
        if N>1: lag[...,1]=rank+1.5-w2
        for p in range(1,N-1):
            lag[...,p+1]=((2*p+rank+1.5-w2)*lag[...,p]-(p+rank+.5)*lag[...,p-1])/(p+1)
        if rank==1:
            funcs=[vv,t0*sn]
        else:
            funcs=[np.sqrt(1.5)*(vv*vv-w2/3),np.sqrt(2)*vv*t0*sn,t0*t0*sn*sn/np.sqrt(2)]
        coeff.append([np.einsum('zsun,ul->zsnl',f[:,:,:,None]*lag,P,optimize=True) for f,P in zip(funcs,proj)])
    if same:
        coeff=[ [a+b for a,b in zip(*coeff)] ]
    dim=N if same else 2*N
    out=np.zeros((dim,dim))
    weight=wz[:,None,None]*ws[None,:,None]*Q[:,:L][:,None,:]
    for m in range(rank+1):
        cc=np.concatenate([sp[m] for sp in coeff],axis=2)
        out+=np.einsum('zsnl,zsml,zsl->nm',cc,cc,weight,optimize=True)
    mu=mi*mj/(mi+mj)
    out*=np.sqrt(2*T/mu)/(np.sqrt(np.pi)/2)/(2*rank+1)
    return out

def pair_matrix(N,rank,mi,mj,z,wz,Q,T,same=False):
    out=np.zeros((N if same else 2*N,)*2)
    for k in range(0,len(z),32):
        out+=pair_matrix_chunk(N,rank,mi,mj,z[k:k+32],wz[k:k+32],Q[k:k+32],T,same)
    return out

def matrices(N,R,X,T,z,wz,Q):
    mats=[]
    for rank in [1,2]:
        C=np.zeros((2*N,2*N))
        selfmat=pair_matrix(N,rank,1,1,z,wz,Q,T,True)
        C[:N,:N]+=.5*X**2*selfmat
        C[N:,N:]+=.5*(1-X)**2*selfmat/np.sqrt(R)
        C+=X*(1-X)*pair_matrix(N,rank,1,R,z,wz,Q,T,False)
        mats.append(C)
    return mats

def properties(N,R,X,T,Cv,Cs):
    bD=np.zeros(2*N);bT=bD.copy();bS=bD.copy()
    bD[0]=np.sqrt(T/2);bD[N]=-np.sqrt(T/(2*R))
    bT[1]=-2.5*X*np.sqrt(T/2);bT[N+1]=-2.5*(1-X)*np.sqrt(T/(2*R))
    bS[0]=X;bS[N]=1-X
    # The null vector is total momentum. Fix one velocity coefficient.
    ix=np.arange(1,2*N)
    c=solve(Cv[np.ix_(ix,ix)],np.column_stack((bD[ix],bT[ix])),assume_a='pos')
    DD=bD[ix]@c[:,0];DT=bD[ix]@c[:,1];TT=bT[ix]@c[:,1]
    eta=T/2*bS@solve(Cs,bS,assume_a='pos')
    return np.array([eta,TT-DT*DT/DD,X*(1-X)*DD,DT/(X*(1-X)*DD)])


import numpy as np
from scipy.special import roots_legendre
from scipy.optimize import minimize_scalar
import time

def ecritical(a):
    s=1-a
    def ec(t):
        h=t**-6
        return 4*h*(2-5*h+3*a/(s*t)*(1-2*h))
    opt=minimize_scalar(lambda z:-ec(np.exp(z)),bounds=(np.log(2**(1/6)),np.log(5)),method='bounded')
    return ec(np.exp(opt.x))

def energy_grid(a,T,n=16,zmax=120):
    # z=t^3 makes the low-energy fractional power integrable and smooth.
    ec=ecritical(a)/T
    cuts=np.unique(np.r_[0,.015,.06,.2,.5,1,2,4,7,11,16,23,32,44,60,80,105,135,170,210,250,295,345,400,460,zmax,ec,ec*.8,ec*1.2])
    cuts=cuts[(cuts>=0)&(cuts<=zmax)]
    cuts=cuts[np.r_[True,np.diff(cuts)>1e-10*np.maximum(1,cuts[1:])]]
    t=cuts**(1/3)
    x,w=roots_legendre(n)
    tt=(t[:-1,None]+t[1:,None])/2+(t[1:]-t[:-1])[:,None]/2*x
    z=tt**3
    wz=(t[1:]-t[:-1])[:,None]/2*w*3*tt**5*np.exp(-z)
    return z.ravel(),wz.ravel()



def scattering_job(args):
    a,T,z,L=args
    return np.array([cross_sections(a,T*max(float(zi),.001),L) for zi in z])

def matrix_job(args):
    N,rank,R,X,T,z,wz,Q=args
    selfmat=pair_matrix(N,rank,1,1,z,wz,Q,T,True)
    C=X*(1-X)*pair_matrix(N,rank,1,R,z,wz,Q,T,False)
    C[:N,:N]+=.5*X**2*selfmat
    C[N:,N:]+=.5*(1-X)**2*selfmat/np.sqrt(R)
    return C

def collision_matrix(pool,N,rank,R,X,T,z,wz,Q):
    # Moderate-sized chunks bound memory and balance the two CPU workers.
    chunks=[(N,rank,R,X,T,z[k:k+48],wz[k:k+48],Q[k:k+48])
            for k in range(0,len(z),48)]
    C=sum(pool.map(matrix_job,chunks),np.zeros((2*N,2*N)))
    return (C+C.T)/2

def vector_properties(C,N,R,X,T):
    bD=np.zeros(2*N);bT=bD.copy()
    bD[0]=np.sqrt(T/2);bD[N]=-np.sqrt(T/(2*R))
    bT[1]=-2.5*X*np.sqrt(T/2)
    bT[N+1]=-2.5*(1-X)*np.sqrt(T/(2*R))
    # Fix the redundant total-momentum coefficient; both sources are
    # orthogonal to the momentum invariant, so transport is gauge invariant.
    ix=np.arange(1,2*N)
    cc=solve(C[np.ix_(ix,ix)],np.column_stack((bD[ix],bT[ix])),assume_a='pos')
    DD=bD[ix]@cc[:,0];DT=bD[ix]@cc[:,1];TT=bT[ix]@cc[:,1]
    return np.array([TT-DT*DT/DD,X*(1-X)*DD,DT/(X*(1-X)*DD)])

def tensor_property(C,N,X,T):
    b=np.zeros(2*N);b[0]=X;b[N]=1-X
    return T/2*(b@solve(C,b,assume_a='pos'))

def submatrix(C,N,full):
    ix=np.r_[np.arange(N),full+np.arange(N)]
    return C[np.ix_(ix,ix)]

def calculate(a,R,X,T):
    Nv=32 if R<=3 else (48 if R<=8 else 64)
    Ns=24 if R<=8 else 32
    z,wz=energy_grid(a,T,32,400)
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('fork')) as pool:
        args=[(a,T,z[k:k+8],Nv+2) for k in range(0,len(z),8)]
        Q=np.concatenate(list(pool.map(scattering_job,args)))
        Cv=collision_matrix(pool,Nv,1,R,X,T,z,wz,Q)
        vp=vector_properties(Cv,Nv,R,X,T)
        # Compare several nested spaces, not merely one adjacent order.
        prev=[vector_properties(submatrix(Cv,n,Nv),n,R,X,T)
              for n in (Nv-12,Nv-8,Nv-4)]
        tolerance=np.r_[2e-6*np.abs(vp[:2]),max(2e-6*abs(vp[2]),1.2e-7)]
        if np.any(np.max(np.abs(np.array(prev[-2:])-vp),axis=0)>tolerance):
            Nv2=Nv+16
            # Existing cross sections already cover every harmonic in the
            # old basis; calculate extra harmonics only if refinement needs it.
            args=[(a,T,z[k:k+8],Nv2+2) for k in range(0,len(z),8)]
            Q=np.concatenate(list(pool.map(scattering_job,args)))
            Cv=collision_matrix(pool,Nv2,1,R,X,T,z,wz,Q)
            vp=vector_properties(Cv,Nv2,R,X,T)
        Cs=collision_matrix(pool,Ns,2,R,X,T,z,wz,Q)
        eta=tensor_property(Cs,Ns,X,T)
        eta0=tensor_property(submatrix(Cs,Ns-8,Ns),Ns-8,X,T)
        if abs(eta-eta0)>2e-6*eta:
            Ns+=12
            if Q.shape[1]<Ns+2:
                args=[(a,T,z[k:k+8],Ns+2) for k in range(0,len(z),8)]
                Q=np.concatenate(list(pool.map(scattering_job,args)))
            Cs=collision_matrix(pool,Ns,2,R,X,T,z,wz,Q)
            eta=tensor_property(Cs,Ns,X,T)
    if R==1: vp[2]=0.
    return dict(viscosity=float(eta),thermal_conductivity=float(vp[0]),
                binary_diffusion=float(vp[1]),thermal_diffusion_factor=float(vp[2]))

if __name__=='__main__':
    A,R,X,T=map(float,sys.argv[1:5])
    print(json.dumps(calculate(A,R,X,T),allow_nan=False,separators=(',',':')))
