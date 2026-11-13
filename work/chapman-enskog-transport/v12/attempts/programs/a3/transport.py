#!/usr/bin/env python3
"""Quantum dilute-mixture transport in units sigma=epsilon=m=k_B=1.
The Navier--Stokes integral equations are solved by successively converged
Sonine Galerkin systems. Collision brackets use exact Gaussian integration
of the velocity polynomials and adaptive quantum scattering moments.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import sys,json,time

import numpy as np
from scipy.special import spherical_jn,spherical_yn, eval_legendre
from time import time

def phases(E,mu,A,L,h=.0015,R=40,lmax=40):
    E=np.asarray(E); C=8*np.pi**2*mu/L**2
    k=np.sqrt(C*E)
    ls=np.arange(lmax+1); ll=ls*(ls+1)
    # start where potential is very strongly forbidden; irregular contamination dies exponentially
    r0=A+(1-A)*.48
    steps=int(np.ceil((R-r0)/h));h=(R-r0)/steps
    def q(r):
        s=((1-A)/(r-A))**6
        return ll[None,:]/r**2+C*(4*s*(s-1)-E[:,None])
    qm=q(r0);q0=q(r0+h)
    um=np.zeros((len(E),lmax+1));u=np.ones_like(um)
    # renormalize periodically to suppress overflow in high partial waves
    for t in range(1,steps):
        r=r0+(t+1)*h
        qp=q(r)
        up=((2+5*h*h*q0/6)*u-(1-h*h*qm/12)*um)/(1-h*h*qp/12)
        if t%100==0:
            norm=np.maximum(np.abs(up),np.abs(u)); norm=np.maximum(norm,1e-100)
            up/=norm;u/=norm
        um,u=u,up;qm,q0=q0,qp
    # Numerov corrected central derivative at R-h, with u at R and R-2h
    qp=q(R+h)
    up=((2+5*h*h*q0/6)*u-(1-h*h*qm/12)*um)/(1-h*h*qp/12)
    deriv=(up-um)/(2*h)-h*(qp*up-qm*um)/12
    z=k[:,None]*R
    j=z*spherical_jn(ls[None,:],z);n=z*spherical_yn(ls[None,:],z)
    jp=k[:,None]*(spherical_jn(ls[None,:],z)+z*spherical_jn(ls[None,:],z,True))
    np_=k[:,None]*(spherical_yn(ls[None,:],z)+z*spherical_yn(ls[None,:],z,True))
    return np.nan_to_num(np.arctan2(u*jp-deriv*j,u*np_-deriv*n),nan=0.0)

def cross(E,mu,A,L,ang,deg=1,sign=0,**kwargs):
    d=phases(E,mu,A,L,**kwargs);k=np.sqrt(8*np.pi**2*mu*np.asarray(E))/L
    l=np.arange(d.shape[1]);pl=np.array([eval_legendre(i,ang) for i in l])
    amp=(2*l+1)[None,:]*np.exp(1j*d)*np.sin(d)/k[:,None]
    if sign==0:
        f=amp@pl;return np.abs(f)**2
    fe=amp[:,::2]@pl[::2];fo=amp[:,1::2]@pl[1::2]
    return (1+sign/deg)*np.abs(fe)**2+(1-sign/deg)*np.abs(fo)**2


import numpy as np
from scipy.special import roots_legendre,eval_legendre,eval_genlaguerre,roots_genlaguerre
from scipy.special import gammaln
def born(E,mu,A,L,ls):
 C=8*np.pi**2*mu/L**2;k=np.sqrt(C*np.asarray(E))[:,None];ls=np.asarray(ls)[None,:]
 out=np.zeros(np.broadcast_shapes(k.shape,ls.shape))
 for base,coef in [(6,-4*(1-A)**6),(12,4*(1-A)**12)]:
  for t in range(24 if A else 1):
   s=base+t
   coeff=coef*np.exp(gammaln(base+t)-gammaln(base)-gammaln(t+1))*A**t
   logint=gammaln(s-1)+gammaln(ls+(3-s)/2)-(s-1)*np.log(2)-2*gammaln(s/2)-gammaln(ls+(s+1)/2)
   out-=C*coeff*np.exp((s-2)*np.log(k)+logint)*np.pi/2
 return out


from time import time

def scattering_moments(T,mu,A,L,N=11,tol=2e-8,h=.0015,R=40):
    ne=2*N+3;na=N+2;cut=max(85.,4*N+20.)
    global_lmax=int(np.sqrt(8*np.pi**2*mu/L**2*T*cut)*9+60)
    C=8*np.pi**2*mu/L**2
    rr=np.linspace(A+(1-A)*.95,5,5000)
    vv=4*((1-A)/(rr-A))**6*(((1-A)/(rr-A))**6-1)
    s6=((1-A)/(rr-A))**6
    vp=24*s6*(1-2*s6)/(rr-A)
    well=np.max(C*vp*rr**3/2)
    resonant_l=int((np.sqrt(1+4*well)-1)/2)+1
    zl,wl=roots_legendre(4);zh,wh=roots_legendre(8)
    zz=np.r_[zl,zh];ww=np.r_[-wl,wh]
    edges=np.unique(np.r_[1e-8,np.geomspace(1e-6,1,70),np.arange(1,8,.15),np.arange(8,20,.45),np.arange(20,cut,1.5),cut])
    panels=np.stack([edges[:-1],edges[1:]],axis=1)
    total=np.zeros((3,ne,na));count=0;level=0;starttime=time()
    while len(panels):
        new=[]
        for start in range(0,len(panels),35):
            pp=panels[start:start+35];mid=pp.mean(axis=1);half=np.diff(pp,axis=1).ravel()/2
            yy=mid[:,None]+half[:,None]*zz
            y=yy.ravel()
            lmax=min(global_lmax,int(np.sqrt(C*T*np.max(y))*9+60))
            ls=np.arange(lmax+1)
            d=np.zeros((len(y),lmax+1))
            # centrifugal barrier and van der Waals tail determine the useful cutoff
            perm=np.argsort(y)
            for off in range(0,len(y),140):
                ix=perm[off:off+140];emax=T*np.max(y[ix])
                lm=min(lmax,int(np.sqrt(C*emax)*4+42))
                d[ix,:lm+1]=phases(y[ix]*T,mu,A,L,h=h,R=R,lmax=lm)
            # Complete the weak high-partial-wave tail instead of abruptly truncating f.
            bph=born(y*T,mu,A,L,np.arange(30,lmax+1))
            for row,yi in enumerate(y):
                switch=np.sqrt(C*T*yi)*4+30
                blend=np.clip((np.arange(30,lmax+1)-switch)/8,0,1)
                weak=np.arctan(np.tan(d[row,30:]))
                d[row,30:]=np.where(blend>0,weak*(1-blend)+bph[row]*blend,d[row,30:])
            count+=len(y)
            amp=(2*ls+1)[None,:]*np.exp(1j*d)*np.sin(d)/np.sqrt(C*T*y[:,None])
            amp=np.pad(amp,((0,0),(0,na)))
            moment_ls=np.arange(lmax+1+na)
            # Multiplication by x in the Legendre coefficient representation.
            def times_x(v):
                out=np.zeros_like(v)
                out[:,1:]+=v[:,:-1]*(moment_ls[1:]/(2*moment_ls[1:]-1))
                out[:,:-1]+=v[:,1:]*((moment_ls[:-1]+1)/(2*moment_ls[:-1]+3))
                return out
            even=amp.copy();even[:,1::2]=0
            odd=amp.copy();odd[:,::2]=0
            v=np.stack([even,odd]).reshape(2*len(y),lmax+1+na)
            prev=np.zeros_like(v);curr=v.copy();q=np.empty((3,len(y),na))
            ew=even.conj()/(2*moment_ls+1);ow=odd.conj()/(2*moment_ls+1)
            for order in range(na):
                ev=curr[:len(y)];ov=curr[len(y):]
                q[0,:,order]=4*np.pi*np.real(np.sum(ew*ev,axis=1))
                q[1,:,order]=4*np.pi*np.real(np.sum(ow*ov,axis=1))
                q[2,:,order]=8*np.pi*np.real(np.sum(ew*ov,axis=1))
                nxt=((2*order+1)*times_x(curr)-order*prev)/(order+1)
                prev,curr=curr,nxt
            qs=q.reshape(3,len(pp),len(zz),na)
            le=np.array([eval_genlaguerre(n,1,yy) for n in range(ne)])/(np.arange(ne)+1)[:,None,None]
            integrand=np.einsum('nap,bapk->banpk',le,qs)
            weight=yy*np.exp(-yy)*half[:,None]
            hi=np.einsum('banpk,ap,p->bank',integrand[:,:, :,4:,:],weight[:,4:],wh)
            lo=np.einsum('banpk,ap,p->bank',integrand[:,:,:,:4,:],weight[:,:4],wl)
            # ensure both low and high Sonine moments are accurate
            err=np.max(np.abs(hi-lo),axis=(0,2,3))
            scale=np.maximum(np.max(np.abs(hi),axis=(0,2,3)),.03*(pp[:,1]-pp[:,0]))
            refine=err>np.maximum(tol*scale,2e-11)
            # arctan2 phases retain a pi jump through even very narrow shape resonances
            order=np.argsort(zz);dd=d.reshape(len(pp),len(zz),lmax+1)[:,order]
            diff=np.diff(dd,axis=1);diff=(diff+np.pi)%(2*np.pi)-np.pi
            jump=np.max(abs(diff[:,:,:resonant_l+1]),axis=(1,2))
            refine|=(jump>.35)&(pp[:,0]<30)&(pp[:,1]-pp[:,0]>1e-7)
            refine&=(pp[:,1]-pp[:,0]>2e-9)
            if level>18:refine[:]=False
            total+=hi[:,~refine].sum(axis=1)
            if np.any(refine):
                p=pp[refine];md=p.mean(axis=1)
                new.extend(np.stack([p[:,0],md],axis=1));new.extend(np.stack([md,p[:,1]],axis=1))
        panels=np.asarray(new);level+=1
        print('adaptive',mu,level,count,len(panels),time()-starttime,file=__import__('sys').stderr)
    return total

def effective_weights(mom,N,deg=1,sign=0):
    ne=2*N+3;na=N+2
    if sign==0:q=mom[0]+mom[1]+mom[2]
    else:q=(1+sign/deg)*mom[0]+(1-sign/deg)*mom[1]
    q=q[:ne,:na]*(np.arange(ne)+1)[:,None]
    yy,wy=roots_genlaguerre(ne,1);aa,wa=roots_legendre(na)
    ly=np.array([eval_genlaguerre(n,1,yy)/(n+1) for n in range(ne)])
    pa=np.array([eval_legendre(n,aa)*(2*n+1)/2 for n in range(na)])
    return (ly.T@q@pa)*wa


import numpy as np
from scipy.special import roots_genlaguerre,roots_legendre
from time import time

def series(N,f,g,j,a,b,c,p,y):
    # F^-p exp[-y (a z+b w+c zw)/F], F=1+f z+g w+j zw
    shape=np.broadcast_shapes(np.shape(y),np.shape(c));y=np.broadcast_to(y,shape);c=np.broadcast_to(c,shape)
    out=np.zeros((N,N)+shape);out[0,0]=1
    # F^2 derivative coefficients
    D={(0,0):1,(1,0):2*f,(0,1):2*g,(2,0):f*f,(0,2):g*g,(1,1):2*j+2*f*g,(2,1):2*f*j,(1,2):2*g*j,(2,2):j*j}
    R={(0,0):-p*f-y*a,(1,0):-p*f*f,(0,1):-p*(j+g*f)-y*(c+a*g-b*f),(1,1):-2*p*f*j,(0,2):-p*g*j-y*(c*g-b*j),(1,2):-p*j*j}
    for m in range(N-1):
        rhs=(-p*g-y*b)*out[0,m]
        if m:rhs-=p*g*g*out[0,m-1]
        rhs-=2*g*m*out[0,m]
        if m>1:rhs-=g*g*(m-1)*out[0,m-1]
        out[0,m+1]=rhs/(m+1)
    for n in range(N-1):
        for m in range(N):
            rhs=np.zeros(shape)
            for (i,k),v in R.items():
                if n>=i and m>=k:rhs+=v*out[n-i,m-k]
            for (i,k),v in D.items():
                if (i,k)==(0,0):continue
                ni=n-i+1;mi=m-k
                if ni>=1 and mi>=0:rhs-=v*ni*out[ni,mi]
            out[n+1,m]=rhs/(n+1)
    return out

def mulpoly(S,P):
    out=np.zeros_like(S);N=S.shape[0]
    for (i,j),v in P.items():
        out[i:,j:]+=S[:N-i,:N-j]*v
    return out

def gaussian_kernel(N,ma,mb,mass,T,sa,sb,y,cos):
    # sa and sb are velocity shifts per sqrt(y)
    d=T/mass;P=ma/mass;Q=mb/mass;qa=ma/(2*T);qb=mb/(2*T)
    s2=sa*sa;t2=sb*sb;st=sa*sb*cos
    U2=(1-Q)**2*s2+Q**2*t2+2*Q*(1-Q)*st
    V2=(1-P)**2*t2+P**2*s2+2*P*(1-P)*st
    sV=(1-P)*st+P*s2;tU=(1-Q)*st+Q*t2
    UV=((1-Q)*(1-P)+P*Q)*st+P*(1-Q)*s2+Q*(1-P)*t2
    AB={(0,0):st*y,(1,0):-sV*y,(0,1):-tU*y,(1,1):UV*y}
    A2={(0,0):s2*y,(0,1):-2*((1-Q)*s2+Q*st)*y,(0,2):U2*y}
    B2={(0,0):t2*y,(1,0):-2*((1-P)*t2+P*st)*y,(2,0):V2*y}
    tensor={}
    for (i,j),v in AB.items():
        for (k,l),w in AB.items():tensor[i+k,j+l]=tensor.get((i+k,j+l),0)+v*w
    for (i,j),v in A2.items():
        for (k,l),w in B2.items():tensor[i+k,j+l]=tensor.get((i+k,j+l),0)-v*w/3
    a=qa*s2;b=qb*t2;c=-qa*(1-Q)*s2-qb*(1-P)*t2-4*d*qa*qb*st
    args=(N,P-1,Q-1,1-P-Q,a,b,c)
    G25=series(*args,2.5,y);G35=series(*args,3.5,y)
    vec=mulpoly(G35,AB)+3*d*G25
    G45=series(*args,4.5,y);G55=series(*args,5.5,y)
    ten=mulpoly(G55,tensor)+(20/3)*d*mulpoly(G45,AB)+10*d*d*G35
    return vec,ten

def transport(m,x,T,N=10,ne=None,qs=None):
    if ne is None:ne=2*N+3
    yy,wy=roots_genlaguerre(ne,1);ang,wa=roots_legendre(N+2)
    y=yy[:,None];cos=ang[None,:]
    BV=np.zeros((2*N,2*N));BT=BV.copy();start=time()
    for i,j in [(0,0),(0,1),(1,1)]:
        mass=m[i]+m[j];mu=m[i]*m[j]/mass
        shifts=[m[j]/mass,-m[i]/mass];sp=[i,j]
        factor=x[i]*x[j]*(.25 if i==j else .5)*np.sqrt(8*T/(np.pi*mu))
        ww=np.broadcast_to(wa*np.pi/2,(ne,len(ang))).copy() if qs is None else np.array([qs(i,j,z,ang,wa) for z in range(ne)])
        ww=ww*wy[:,None]*factor
        for a,b in [(0,0),(0,1),(1,1)]:
            sa=shifts[a]*np.sqrt(2*T/mu);sb=shifts[b]*np.sqrt(2*T/mu)
            v0,t0=gaussian_kernel(N,m[sp[a]],m[sp[b]],mass,T,sa,sb,y,np.ones_like(cos))
            vc,tc=gaussian_kernel(N,m[sp[a]],m[sp[b]],mass,T,sa,sb,y,cos)
            v=2*np.sum((v0-vc)*ww,axis=(-1,-2))/3
            t=2*np.sum((t0-tc)*ww,axis=(-1,-2))/5
            ia=sp[a]*N;ib=sp[b]*N
            BV[ia:ia+N,ib:ib+N]+=v;BT[ia:ia+N,ib:ib+N]+=t
            if a!=b:
                BV[ib:ib+N,ia:ia+N]+=v.T;BT[ib:ib+N,ia:ia+N]+=t.T
    BV=(BV+BV.T)/2;BT=(BT+BT.T)/2
    def solve(n):
        ix=np.r_[np.arange(n),np.arange(N,N+n)]
        bv=BV[np.ix_(ix,ix)];bt=BT[np.ix_(ix,ix)]
        sd=np.zeros(2*n);st=sd.copy();sv=sd.copy()
        sd[0]=T/m[0];sd[n]=-T/m[1]
        st[1]=-2.5*x[0]*T/m[0];st[n+1]=-2.5*x[1]*T/m[1]
        sv[0]=2*x[0]*T/m[0];sv[n]=2*x[1]*T/m[1]
        vd=np.linalg.solve(bv[1:,1:],sd[1:]);vt=np.linalg.solve(bv[1:,1:],st[1:])
        d=sd[1:]@vd;h=sd[1:]@vt;t=st[1:]@vt
        eta=T/2*sv@np.linalg.solve(bt,sv)
        return np.array([eta,t-h*h/d,x[0]*x[1]*d,h/(x[0]*x[1]*d)])
    results=[solve(n) for n in range(4,N+1)]
    print('generating brackets',time()-start,'convergence',results,file=__import__('sys').stderr)
    transport.history=results
    return results[-1]



def main():
    s1,s2=sys.argv[1:3]
    A,L,X,T=map(float,sys.argv[3:7])
    species={'pH2':(1.,1,1),'oH2':(1.,9,1),'HD':(1.5,6,-1),'oD2':(2.,6,1),'pD2':(2.,9,1)}
    sp=[species[s1],species[s2]];m=[p[0] for p in sp];x=[X,1-X]
    N=18; reserve=22
    moms={};ws={}
    for i,j in [(0,0),(0,1),(1,1)]:
        mu=m[i]*m[j]/(m[i]+m[j])
        if mu not in moms:
            moms[mu]=scattering_moments(T,mu,A,L,reserve,h=.001 if L<1.4 else .0015)
        ws[i,j]=effective_weights(moms[mu],N,sp[i][1],sp[i][2] if i==j else 0)
    for order in [18,20,22]:
        ws={}
        for i,j in [(0,0),(0,1),(1,1)]:
            mu=m[i]*m[j]/(m[i]+m[j])
            ws[i,j]=effective_weights(moms[mu],order,sp[i][1],sp[i][2] if i==j else 0)
        out=transport(m,x,T,N=order,ne=2*order+3,qs=lambda i,j,z,a,w:ws[i,j][z])
        # Require agreement over several consecutive orders; extending this
        # system is cheap because the scattering moments are already available.
        history=np.asarray(transport.history)
        stable=False
        for k in range(8,len(history)):
            scale=np.maximum(np.abs(history[k])*1e-6,np.array([0.,0.,0.,5e-8]))
            if np.all(np.max(np.abs(history[k-3:k]-history[k]),axis=0)<scale):
                out=history[min(k+2,len(history)-1)]
                stable=True
                break
        if stable:break
    print(json.dumps(dict(zip(['viscosity','thermal_conductivity','binary_diffusion','thermal_diffusion_factor'],map(float,out)))))
if __name__=='__main__':
    main()
