"""Dilute elastic quantum binary-mixture transport in reduced units.

Radial Numerov integration, quantum exchange-averaged angular cross sections,
and a Sonine/spherical-harmonic Galerkin solution of the linearized Boltzmann
operator. Collision brackets use centre-of-mass and relative velocities; the
centre-of-mass Maxwell integrals and angular projections are exact polynomial
quadratures. Adaptive scattering splines resolve threshold and shape resonances.
The velocity basis is carried through degree 20, including the diffusion/heat
coupling and the zero-diffusion heat-flux constraint.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import sys, json
import numpy as np
from scipy.special import roots_legendre, roots_genlaguerre, spherical_jn, spherical_yn, gammaln
from scipy.linalg import solve

# Mass and exchange trace: all molecules except HD are bosons. The
# internal-state dimensions are 1, 9, 6, 6, 9, respectively.
SPECIES={'pH2':(1.,1.),'oH2':(1.,1/9),'HD':(1.5,-1/6),'oD2':(2.,1/6),'pD2':(2.,1/9)}

def potential(r,a):
    z=(1-a)/(r-a)
    z6=z**6
    return 4*z6*(z6-1)

def numerov(E,mu,a,hbar,lmax,h=.002,R=25.):
    E=np.asarray(E)
    k=np.sqrt(2*mu*E)/hbar
    K=2*mu/hbar**2
    r0=a+.48*(1-a)
    steps=int(np.ceil((R-r0)/h)); h=(R-r0)/steps
    ls=np.arange(lmax+1); ll=ls*(ls+1)
    en=K*E[:,None]; centrifugal=ll[None,:]
    ratio=np.full((len(E),lmax+1),np.inf)
    h12=h*h/12
    for n in range(1,steps):
        r=r0+n*h
        f=1-h12*(centrifugal/r**2+K*potential(r,a)-en)
        ratio=12/f-10-1/ratio
    rp=R-h
    fp=1-h12*(centrifugal/rp**2+K*potential(rp,a)-en)
    fn=1-h12*(centrifugal/R**2+K*potential(R,a)-en)
    ur=ratio*fp/fn
    z=k[:,None]*R; zp=k[:,None]*rp
    j=z*spherical_jn(ls[None,:],z); y=z*spherical_yn(ls[None,:],z)
    jp=zp*spherical_jn(ls[None,:],zp); yp=zp*spherical_yn(ls[None,:],zp)
    with np.errstate(invalid='ignore',divide='ignore',over='ignore'):
        delta=np.arctan((ur*jp-j)/(ur*yp-y))
    delta=np.nan_to_num(delta)
    # Distorted-wave first-order correction for the weak far tail.
    xx,ww=roots_legendre(40); sx=(xx+1)/2; rs=R/sx
    ints=np.array([np.sum(ww/2*potential(rs,a)*R/sx**2/rs**(2*n)) for n in range(10)])
    avg=np.full_like(delta,ints[0]); amp=np.ones_like(delta)
    ap=np.zeros_like(delta); term=np.ones_like(delta)
    for n in range(1,10):
        term=term*(2*n-1)/(2*n)*(centrifugal-n*(n-1))/k[:,None]**2
        avg+=term*ints[n]
        amp+=term/R**(2*n)
        ap+=-2*n*term/R**(2*n+1)
    V=potential(R,a); zz=(1-a)/(R-a)
    Vp=4*(-12*zz**12+6*zz**6)/(R-a)
    omega=2*k[:,None]/amp; op=-omega*ap/amp
    with np.errstate(invalid='ignore',over='ignore',divide='ignore'):
        ang=np.exp(2j*(np.arctan2(j,-y)+delta))
        osc=np.real(ang*(1j*V*amp/omega-((Vp*amp+V*ap)/omega**2-V*amp*op/omega**3)))
    tail=-K/(2*k[:,None])*(avg-osc)
    tail[centrifugal> (.75*k[:,None]*R)**2]=0
    for idx in np.where(k*R<12)[0]:
        ki=k[idx]; cutoff=min(lmax,int(8*ki+16)); li=ls[:cutoff+1]
        xx,ww=roots_legendre(120); sx=(xx+1)/2; rr=R/sx
        zr=ki*rr[:,None]
        jj=zr*spherical_jn(li[None,:],zr)
        yy=zr*spherical_yn(li[None,:],zr)
        di=delta[idx,:cutoff+1]
        with np.errstate(invalid='ignore',over='ignore'):
            u=jj*np.cos(di)-yy*np.sin(di)
            v=np.sum((ww/2*R/sx**2*potential(rr,a))[:,None]*u*u,axis=0)
        tail[idx]=0
        tail[idx,:cutoff+1]=-K/ki*np.nan_to_num(v)
        delta[idx,cutoff+1:]=0
    result=delta+tail
    # Beyond the centrifugal turning points the inverse-power Born series is
    # exceptionally accurate and avoids ill-conditioned irregular waves.
    for l in range(6,lmax+1):
        impact=np.sqrt(l*(l+1))/k
        weak=impact>7
        if not np.any(weak): continue
        kk=k[weak]
        born=np.zeros(len(kk))
        for n in range(min(14,2*l-4)):
            lam=5+n
            integ=np.exp(np.log(np.pi/2)+gammaln(lam)+gammaln(l+.5+(1-lam)/2)-lam*np.log(2)-2*gammaln((lam+1)/2)-gammaln(l+.5+(1+lam)/2))
            coef=np.exp(gammaln(n+6)-gammaln(6)-gammaln(n+1))*a**n
            born+=4*K*(1-a)**6*coef*kk**(4+n)*integ
        result[weak,l]=born
    return result

def phases(E,mu,a,hbar,lmax,h=.003,R=25.):
    d0=numerov(E,mu,a,hbar,lmax,h,R)
    d1=numerov(E,mu,a,hbar,lmax,h/2,R)
    dif=(d1-d0+np.pi/2)%np.pi-np.pi/2
    return d1+dif/15

def cross_sections(E,mu,a,hbar,order,stats=0.,h=.003,R=25.,lmax=None):
    E=np.asarray(E); k=np.sqrt(2*mu*E)/hbar
    if lmax is None: lmax=max(80,int(np.ceil(max(k)*5+30)))
    delta=phases(E,mu,a,hbar,lmax,h,R)
    na=lmax+(order+1)//2+2
    c,w=roots_legendre(na)
    pol=np.empty((lmax+1,na)); pol[0]=1
    if lmax: pol[1]=c
    for l in range(1,lmax): pol[l+1]=((2*l+1)*c*pol[l]-l*pol[l-1])/(l+1)
    coeff=(2*np.arange(lmax+1)+1)[None,:]*np.exp(1j*delta)*np.sin(delta)/k[:,None]
    if stats:
        fe=coeff[:,::2]@pol[::2]; fo=coeff[:,1::2]@pol[1::2]
        dcs=(1+stats)*abs(fe)**2+(1-stats)*abs(fo)**2
    else:
        dcs=abs(coeff@pol)**2
    q=2*np.pi*dcs@((1-pol[1:order+1])*w).T
    return q

def laguerres(n,alpha,z):
    out=np.empty(z.shape+(n+1,)); out[...,0]=1
    if n: out[...,1]=1+alpha-z
    for j in range(1,n): out[...,j+1]=((2*j+1+alpha-z)*out[...,j]-(j+alpha)*out[...,j-1])/(j+1)
    return out

def harmonic_projectors(nc,lmax):
    c,w=roots_legendre(nc); w=w/2
    p=[]
    for m in range(3):
        from scipy.special import lpmv
        pp=np.zeros((nc,lmax+1))
        for l in range(m,lmax+1):
            pp[:,l]=lpmv(m,l,c)*np.sqrt((2*l+1)*np.exp(gammaln(l-m+1)-gammaln(l+m+1)))
        p.append(pp*w[:,None])
    return c,p

def pair_brackets(e,q,mi,mj,T,N,identical=False):
    # q has l=1,...,N+2. Maxwell averages normalized to unity.
    M=mi+mj; mu=mi*mj/M
    wr,ww=roots_genlaguerre(N+3,.5); ww=ww/(np.sqrt(np.pi)/2)
    c,proj=harmonic_projectors(N+3,N+2)
    W=np.sqrt(2*T/M*wr)
    g=np.sqrt(2*T/mu*e)
    # dimensions: energy, centre-of-mass radius, relative polar angle
    s=np.sqrt(1-c*c)[None,None,:]
    cv=c[None,None,:]
    wz=W[None,:,None]
    sets=[]
    for mass,b in ((mi,mj/M*g),(mj,-mi/M*g)):
        b=b[:,None,None]
        vz=wz+b*cv
        vx=b*s+np.zeros_like(wz)
        v2=vz*vz+vx*vx
        z=mass/(2*T)*v2
        Lv=laguerres(N,1.5,z); Lt=laguerres(N,2.5,z)
        def project(func,p):
            # result energy,W,l,Sonine
            return np.einsum('ewcn,cl->ewln',func,p,optimize=True)
        v0=project(vz[...,None]*Lv,proj[0])
        v1=project(vx[...,None]*Lv,proj[1])
        t0=project((vz*vz-v2/3)[...,None]*Lt,proj[0])
        t1=project((vx*vz)[...,None]*Lt,proj[1])
        t2=project((vx*vx)[...,None]*Lt,proj[2])
        sets.append(([v0,v1],[t0,t1,t2]))
    # Eigenvalues of the scattering operator multiply positive harmonic products.
    weight=ww[None,:,None]*q[:,None,:]*g[:,None,None]
    def build(index,factors,denom):
        out=np.zeros((len(e),2*(N+1),2*(N+1))) if not identical else np.zeros((len(e),N+1,N+1))
        for m,factor in enumerate(factors):
            if identical:
                A=sets[0][index][m][:,:,1:]+sets[1][index][m][:,:,1:]
            else:
                A=np.concatenate((sets[0][index][m][:,:,1:],sets[1][index][m][:,:,1:]),axis=-1)
            out+=factor/denom*np.einsum('ewln,ewl,ewlk->enk',A,weight,A,optimize=True)
        if identical: out*=.5
        return out
    return build(0,[1,1],3),build(1,[1.5,2,.5],5)


def transport_from_brackets(Bv,Bt,m1,m2,x,T,N):
    x2=1-x; nn=N+1; masses=np.array([m1,m2]); xs=np.array([x,x2])
    P=np.zeros(2*nn); H=P.copy(); S=P.copy()
    P[::nn]=T/masses*np.array([1.,-1.])
    H[1::nn]=-2.5*xs*T/masses
    S[::nn]=2*xs*T/masses
    # Remove the conserved total momentum, using an orthogonal complement.
    null=np.zeros(2*nn); null[::nn]=masses
    from scipy.linalg import null_space
    Z=null_space(null[None,:])
    a,b=(Z@solve(Z.T@Bv@Z,Z.T@np.stack([P,H],axis=1),assume_a='pos')).T
    t=solve(Bt,S,assume_a='pos')
    pd=P@a; ph=P@b
    return dict(viscosity=float(T/2*(S@t)),thermal_conductivity=float(H@b-ph*ph/pd),binary_diffusion=float(x*x2*pd),thermal_diffusion_factor=float(ph/(x*x2*pd)))

def energy_grid(mu,a,hbar,T,order,stats,tol=3e-6):
    # Interpolate Q_l as a function of sqrt(E/T). This resolves threshold
    # scattering as well as shape resonances and avoids a singular endpoint.
    from scipy.interpolate import CubicSpline
    ymax=np.sqrt(100.)
    y=np.unique(np.r_[np.geomspace(.0001,.02,24),np.linspace(.002,1.,161),np.linspace(1.,3.,141),np.linspace(3.,ymax,100)])
    llimit=max(80,int(np.ceil(np.sqrt(2*mu*T)*ymax/hbar*3+30)))
    cache={}
    def evaluate(yy):
        missing=np.array([v for v in yy if float(v) not in cache])
        for i in range(0,len(missing),100):
            chunk=missing[i:i+100]
            out=cross_sections(T*chunk**2,mu,a,hbar,order,stats,h=.003,R=22.,lmax=llimit)
            for val,row in zip(chunk,out): cache[float(val)]=row
        return np.array([cache[float(v)] for v in yy])
    vals=evaluate(y)
    y=np.r_[0.,y]; vals=np.r_[vals[:1],vals]
    for it in range(24):
        sp=CubicSpline(y,vals)
        ym=(y[:-1]+y[1:])/2
        vm=evaluate(ym)
        err=np.max(abs(vm-sp(ym))/(1+abs(vm)),axis=1)
        # Small far-tail errors do not matter; high polynomial orders do.
        threshold=tol*(1+np.maximum(ym-6,0)**4)
        threshold[ym<.005]=1.
        threshold+=2e-7/(ym+.01)**2
        select=err>threshold
        if not np.any(select):
            y=np.r_[y,ym]; vals=np.r_[vals,vm]; ind=np.argsort(y)
            return CubicSpline(y[ind],vals[ind])
        y=np.r_[y,ym[select]]; vals=np.r_[vals,vm[select]]; ind=np.argsort(y); y=y[ind]; vals=vals[ind]
    return CubicSpline(y,vals)

def integrate_pair(sp,mi,mj,T,N,identical):
    # Collision brackets at fixed energy, divided by g, are polynomials of
    # degree at most 2*N+2. Recover their Maxwell integrals in a Laguerre basis.
    K=2*N+3
    e,we=roots_genlaguerre(K,.5)
    basis=laguerres(K-1,.5,e)
    norms=np.exp(gammaln(np.arange(K)+1.5)-gammaln(np.arange(K)+1))
    mu=mi*mj/(mi+mj); speed=np.sqrt(2*T/mu*e)
    xx,ww=roots_legendre(8)
    knots=sp.x
    ym=(knots[:-1]+knots[1:])/2; yh=(knots[1:]-knots[:-1])/2
    y=(ym[:,None]+yh[:,None]*xx).ravel()
    w=(yh[:,None]*ww).ravel()
    z=y*y
    L=laguerres(K-1,.5,z)
    w*=4/np.sqrt(np.pi)*y*y*np.exp(-z)*np.sqrt(2*T/mu)*y
    Q=sp(y)[:,:N+2]
    moments=L.T@(w[:,None]*Q)
    # Interpolatory weights at generalized Gauss nodes for each angular l.
    wq=(basis@(moments/norms[:,None]))*we[:,None]
    v,t=pair_brackets(e,wq/speed[:,None],mi,mj,T,N,identical)
    return np.sum(v,axis=0),np.sum(t,axis=0)


def integrate_pair_direct(sp,mi,mj,T,N,identical):
    xx,ww=roots_legendre(4)
    knots=sp.x
    ym=(knots[:-1]+knots[1:])/2; yh=np.diff(knots)/2
    y=(ym[:,None]+yh[:,None]*xx).ravel()
    w=(yh[:,None]*ww).ravel()*4/np.sqrt(np.pi)*y*y*np.exp(-y*y)
    dim=N+1 if identical else 2*(N+1)
    bv=np.zeros((dim,dim)); bt=bv.copy()
    for i in range(0,len(y),64):
        v,t=pair_brackets(y[i:i+64]**2,sp(y[i:i+64])[:,:N+2],mi,mj,T,N,identical)
        bv+=np.einsum('e,enk->nk',w[i:i+64],v)
        bt+=np.einsum('e,enk->nk',w[i:i+64],t)
    return bv,bt


def run(s1,s2,a,L,x,T):
    m1,st1=SPECIES[s1]; m2,st2=SPECIES[s2]; hb=L/(2*np.pi)
    maximum=20
    # Each pair uses its own reduced mass and exchange-averaged cross section.
    grids=[]
    for mi,mj,st in [(m1,m1,st1),(m2,m2,st2),(m1,m2,0.)]:
        grids.append(energy_grid(mi*mj/(mi+mj),a,hb,T,maximum+2,st))
    N=maximum; nn=N+1; bv=np.zeros((2*nn,2*nn)); bt=bv.copy()
    for j,(mi,mj,sp,ident) in enumerate([(m1,m1,grids[0],True),(m2,m2,grids[1],True),(m1,m2,grids[2],False)]):
        v,t=integrate_pair(sp,mi,mj,T,N,ident)
        if ident:
            sl=slice(j*nn,(j+1)*nn); factor=(x if j==0 else 1-x)**2
            bv[sl,sl]+=factor*v; bt[sl,sl]+=factor*t
        else:
            bv+=x*(1-x)*v; bt+=x*(1-x)*t
    try:
        result=transport_from_brackets(bv,bt,m1,m2,x,T,maximum)
    except (np.linalg.LinAlgError,ValueError):
        # Positive-weight quadrature avoids the cancellations in the fast
        # polynomial-moment reduction if an unusually ill-conditioned case
        # makes that reduction unsuitable.
        bv[:]=0; bt[:]=0
        for j,(mi,mj,sp,ident) in enumerate([(m1,m1,grids[0],True),(m2,m2,grids[1],True),(m1,m2,grids[2],False)]):
            v,t=integrate_pair_direct(sp,mi,mj,T,N,ident)
            if ident:
                sl=slice(j*nn,(j+1)*nn); factor=(x if j==0 else 1-x)**2
                bv[sl,sl]+=factor*v; bt[sl,sl]+=factor*t
            else:
                bv+=x*(1-x)*v; bt+=x*(1-x)*t
        result=transport_from_brackets(bv,bt,m1,m2,x,T,maximum)

    return result

if __name__=='__main__':
    s1,s2,a,L,x,T=sys.argv[1:]
    out=run(s1,s2,float(a),float(L),float(x),float(T))
    print(json.dumps(out,separators=(',',':'),allow_nan=False))
