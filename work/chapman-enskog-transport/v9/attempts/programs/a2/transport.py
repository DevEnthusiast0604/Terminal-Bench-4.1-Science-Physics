#!/usr/bin/env python3
"""Quantum binary-gas transport in Kihara reduced units.

The collision operator is evaluated as its symmetric collision bracket.
Vector and symmetric-traceless tensor Sonine spaces are used for the two
Navier--Stokes integral equations. The vector system retains diffusion/heat
coupling, and conductivity is the zero-diffusion Schur complement.

Maxwellian centre-of-mass integrations are analytic generating-function
coefficients; the quantum angular integrals use phase-difference sums with
Gaunt coefficients. Radial waves use an adaptive eighth-order integrator.
Shape resonances are located independently by unwrapped phase scans.
Local Chebyshev representations of weighted brackets avoid cancellation in
global high-degree collision integrals. The native arithmetic kernel was
compiled from the source included below; its binary is embedded so no compiler
or additional package is needed at runtime.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import sys, math, json, time, ctypes as ct, tempfile, zlib, base64
import numpy as np
import scipy.special as sp
import scipy.linalg as la
from scipy.integrate import quad_vec
from scipy.optimize import brentq
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

_NATIVE = 'c-rlK4OkRcvS{}J293}|f`-JnVlr;fAOWKrN#cXinb;&lmLwR58zLY-N*0mekeDnt(F_<nIL4c}S?{j9>+bdDnq7C-&1UzS#KajC<wq1z<BSNw{~mu4qv8+FtEzK)7!b^T-@W_Z_r1^7>C>l9ojP^uRMn|-y6Jw~Y<Ws2ih_0o3I9vz$q7O-PZ!P&giRI(!})$;1mOk?10QSd=$#6BmSDY*fPCNdXOH(z1M5+HX&l}s4ZgE?8dz@-{M46OUY*xFU8rN}s*8KYz<N4fuZ!2~n%6sR5__kiyxCy>o6PC<O$|ctRFh%aF<Ty9H@(Q|_DM5^-l<maIjA>C_^%(DxS!|k4J4N+UGG#3Xg8AdMG&SxJ40ytmrpN*rM@WaEIlCB96UDj-ar1zEAVoCfc&9{F>o4&un10T#9I@WY#d|1P`*F*o}c~Tn~~qgcXU5+l*e8DzzYU|&lmvy$^h`!2Y`zM@blpS_&Ec>%LjnJIsiO&fOeM*fd3Ty9_R=DivjSf2tHI;G=b&+lPk=xIXrn9%ZG6M4IJ*2S$+psl>gxHG>%`QRmjSkGjD!z)&g5jsVyr@$Vy31&C1I!&7V`az?NT{o;s~)esO+!&g`OmR@Q$>R_?-_tb)SgoT9=v^M!f&^A_aWgo1fF3*l5)ER@WDU06_9oI8JkkYmd!o*?AlWpRE^>FhTOi*3S!S4-iPn_~mQLeZR@dGm6F{Dma~G*B`(XF<L&yEG^FC;7GoLjG$xMP)g*e4(gt_Pn?S^W%PmSGnwJx+P`mw5$nn6XGWITtC`#naDIn2i6b_XB}LJP^u$nFu=ute_I0dyzIWh!DwxbetioPJ`b>8`@eiN2uH!gVG8Aggrhvq>g)XVHM`dQ)EaJt9ev>09BwV?4cGFu^I1A5z$cKO3V`1c0Cxw#hX%mg1K{C-3dq~JgZp6Z2n~P-1^R^mc;I{#6#x$jfJX<w1N~-906a7R9v=W78~~pj03Q-KZwA2c41mi4@UQ@QS^!)UZXdUg+sEzW_Hp~TecV3&affU_9V%Ca)MUYBrPHSKHOcm^p<DdrzDe~^<QuaC&eEu4xWYVb26)?jaEz(OJcfYYCdz+-c?{XSPRf6Zc?{LO8z}#K%wve=T|@cbVID&>?+VKQ0`nM>c^6Us1I%Ms<Sn86dzi=2%$rU5cQB73nKzB{Z(<%pF>f;Eug-#1;0k|#9a9Riua1z}m?U=DhC%ngp2fO9*w-$NT7-C8cnbK5gg<ElCSz~NN{8$^n<Trsf@E=<y!(bN5(qdrflyz2fi%k0Q~!eWgR6_CT%3iW_`@?~`;=GkQdW-HhRRh_zJZLI0bHtiaM~8q2zl{ksN1W)_jM@b`4_&xEt!N%FmBQ6`!{?(Q`NAIP|KrwoGp{hmCe%fC>V^EB13YD;*uR{dZWEs+=%1jaeCT4)lias>P}#?g5=@Zp_mLq?M_j)SL<8g(&KbjyN|ecwC!x`_Ur(nZ+4gxo67dLy73>>jyG<^h&;h({1O)^jC6ZTxj_%VWQ$V&IYN*sl9R_?MaoFkqqcdWzTREe@=Axh&V6B8%abB9>TZB@T3Z9^SIfAmj{EPG9TOk7yF@v+1uM(0Bf;)^V@uJ!9q#&;SK8f;ZLT)2`@5+vPYyCA?k;O!ytTTa8%Fz<XnFBD<S=Ei6BFQGs>}xowz^O0THT=D(JyWB_un{ER(6w2jV~H!7}ICSO1G@+dO=n$kdUL)aos57F)zF<2<FP8($Z5jekWzcWp)%9!~|!;8P8c|o2=|NE2>FpH!5con_;L~IWo2*#dRz=MY$ro+6SkIjk4%IbsrzcR(FcsrBAWf=*`MCquuATy=iP2>v4JNTD+~EHwT#=KlRxTm>mmzDarwhayC`DoMPW5rnrs=lYSXn#w9ej)wRU6xmy00xw7T02Maj7=q^1_f}*0~dMGR(u16VK5<AO|$cwk3L@bF-w#9&xvbY+vr~X<6{Mu_kZrd>r&6pCmNtN*=Gmux*OD`KUjV~K#8MC$+XL32cpj?m_pAKCdBq);}%S4rIS#L;&tn65C5JXW>HW@aNs8$*_P<oEU3|MJ^<#D;|J?g<j(BE=HH0BO^Tb?vPCcX_pY3irfd_LJxVGtIJf~NG!b{P~)RzHHWmRN)A_{<=<$caVE%4O6gqzFn2WKgF_FQYwmma05Mw5h7d5W^rA=rQEWA+M6=K54*CVdrE8Xo3c-A6$nv)*GDICFLBLjuUcgAa}6dQxBO<hBdgZWtZ4PNRop@f%5GF^>hQG*Bz`Qo;Der3@Z(!gFOZgOWNxARd!oln~SiTSltz5vTheiD7me{QxAe!Z)gINZHydZzz8!Qp%5rT`!Hb1a@A+lnCw_-5R9Ur4g)2wY=O>hB6&ic5~u@7HYTwK>>92-mmi0&%ODupbJpZ|M)x&3atn-t9;lccFZwLtRFtdSpMalIf(<Rf2J#;+P_&c!mckBT<rO`4C$XdKTayxr7&2&;Y~QYLyV8<mN!(fX*H*Wu&M{52<nH+#-AF>St34zIToo6S@pEiB#dSDXcC0oC(?Fjph();y6hL;AbjS|!Ln%rZ485`w%oxnu<1mV{(r8iEk{E$I*>!Aif)hBfz`(YXOd=n#h&2|V*8y3Rvfkjv29=8@P+1jQRd&hP%}s_bQr!K}PtRFdaYI|iFGZs9oSxa6Nx2`pm*SYHPf@lOtdQ+z!K$}{2^JZ^$+Z-tAgWV9631HI;G9G`g!v{F6LVri*;k%wPo2B7r94bXNo=;=*?Iu9r4GAO)#@=RXD!MVOBL&msfzJxsp4G$A8CZ2sfsafsbYPSs~GF{ZPAIJv4O2TbOWs!l?8{c;Z!iR(g4CnJ%Hv=$f6Exj7&{dzJ;P}D&mR`CZdk&0+Rq$wKLNe!I+pL9YoDs!EFO|3`lY10u`=rYvB5Y8PfJ>xZ2rP4VtIb2+|3jYImc%5vLgUF7WX6)V3Z-aTAGet3L?l(ALPU0|?i^<s#JnM$ZmJ1}aj;2#7X3^{BOiQK$J1-c<{@5OPp>SwUoYPXqe-*kzy3f~K?BU)`eYw<zg`Y<0wCl0k{Aw1Jc?j%DD1bU>>fgt3Vl^n`r)1kJ$l*j;iP+1wA%Ja<y#nRgJY)Vpg*GO?hhLk(1?MDraD;1?Q5)W{z?6A)7a7dU9wR*l{c8qjDX$$k-=mN!u+P~rz0JvHtIKG%AA9i)ahcHp57cz|-?1xBH*+SBN1hg<`B(1teVeRz{D@-{-HPEfxDoshwuW~0)rU~{ATF#tUwD;@{QIW1K~4cI;#k062BO-oUT;O;cG#ENZ)j4e-sDm(S^6qI$@(N+(%ne7Qle;h51xnr<#3%LF?7#_JQ*ie;j2z@@yXEVg$ug7=W3?-`P5;i^pE2Ar<W|6>ls9R+*K)4%ec<%X|>zZJ6e?@h-C$hRUx{JZClwG%M*P>Vq$!ZSNWzN@Th({lqW^t?q?GT~<VfDkyOis}hJAA9!nI2`McoLi*=fSX7p;gfIuvADvH$q;9bOp%?VxQRHHWx|@0yCGp4kQ*FAh821{E@5pR13|>7UhIG3fo+~6({L{DZCZYQN;0{kk-k)MEt$d%~pSU5he7=WKFv3xpdFnvaV{n*dv^1GMpaKEWAXbh_@*1ARKpC8W3+8NBx7y1)S*I4w&W^cF2ia%1*Spy^$0SYw;V8N0jatARfVmN2e5FF{E`$8TD`llLef?aN)e#fa{b3DaKVGovSO5;%cRL^M_%D=bVH(w^P!WV+DQK>BkVBxr>M;1F^7^k5S$8ShrIe*VrjpFGDGG2hPh3*&<f3hV5Z!E+n#<h|B`Q>ef!54?qmN!mti+O-YYzla|~YDF_a;2yMZjA#HQQQR&Y$fIDmjRF}7#3^8mWGBRxf%xLQk<sweWQ+_vry84-6qktFsNrlwfxLR0_#L*>myM#ELjKxE6$Uw>C(IVE+cvl!oL@qBY^6UE%Ct1r#GCqMd6PoX&70{ybE1dt-8CrMZ;cTI1f(>wKLRrnK;5-4P6&OnGKTp^e>^ul~vJCSWYgr!&wKBRuU>;~D<TYX-!$ZixQpR?m)<6uv0A`qQSgkI)it#sGVORyUylZv1&MPoVF+T)yC!sjg5Mxrjkf|Ux3Z%$0yCIu#tUwyhL;#tsK+#<w4Rf+IMk~0Bk!2YAJnX2oo#VCJuZU8`GfbH(3>)wQ+I<URf{bn=?qpTB-$dN05#QK@5kOWaReUFKvP~M<Xg}HZfylONWZnIe4U#H;rIGE>$j1B0VkputSyljKyZR*?QuZ{V>2*Xhqd1w!MKf|WH<63h$VK&F_{pskZHe~w8}cd$(4L3i3RpD-gXq@><KT4~C4KOI82M`Wsqm`^Ud1e~l@Y-akH{Bbk(AB#aH^CMdkTP=hA3EPLG)Rp2h<|6z;pv#M+`MUy<?zWdE_OE456TITh*9zq^@~nHv|M#ih}b{RMvJ>)W%0idx=cOnNCefti4rr7SOgrNyZkSZthC4cMr8aXj0Ua+<kB@N|n!c^OoY7x+XZi*C9^pG=VYx4x50B^`yK|zKJvwE<PiTgR+SA1}nQlUk8{@meVuk0njo-GKo57JA&7eo{(K)_=pr(z=(ybNi*<jC5=0|1?>A;8ec5<j7AWvt%XGlgKaXzGvxIYf}&=D`9^G_Kov$UqqV>+ojZd(!U$QRlURSXL1vt+r9c%yD-FrKS8O`Mt4)SbHuf1cNEm%CEZt+;(4YNc0;do1?c^$kZgafC3m`*HZo#T<h6)Uie{KR3*-1|AAXFNYN#2x*9R`Mhl3B_)jre26a{R+U!b*Hx$HF58CgcRJ4j|gF2RK?YqHV>~7KD$yYl1e8ZZ5L5hIM?@uqLRTo|UVjCR{yJZQ>j{n{klgMKQcCUfV<ffG-4;ayV0IC=NLE-~whdVFXD}76}>`Q8Zi`pD_?}30-KzmJTq~r2-?cpW#o|X#>5Ax4Vbot>Sp6*+@<1rCy}B3$CmdP-_rFHPfk$qBhP^Y)qMaRvT)0!D>Ua$S58mufBn?oN<U|q8O%SEMzB$tU=ary{kc@E+kNo^<b9Hu#kbWK6PT-@g&)dwVX`GYU&1}vxO4!U5mtM1YxSN)*{HIO<&e}gm=-D?_`ss1)T@R0@kzeLz6#9HjOjkAvQ}D;BY{_OHgm3febK>+2vOCi<1G~W+f-eyv&?O2&bOKGI|!>VIcs&^E(_HIUE}~9M)b;fs`KB98bgh9hwK^hgHWDvFZX@dTSrCVAXMF5QCHS1B?&!iRocKi|4X!;(7zoBItYilyan!BE8iJr(!aOU8?HE&^F}rI99Zc{O??7r?^(#0cD7Kyns0YJ$G5sEbN3EqmC<ad_bF6@0cTDhN5|ykkxU_s2g#p#_z<O8NDv##?%r4>sDyuD5N`Zz)sU3yBWm_3jDAL+Pu!tptPNNC~G(5+*DDro`4^^nPbE+GSk7#1c9fqzwN|NWSr(TWxv-<W<GbN=F;@sk(p@%upUCbj-iJ-H=e27$l-CCZG~z+o*PHTS!}D8+S)LlF%N`5wahpNLgitH#xu2N47D(%Lx_Y1no-?DV3$S!yxEuI8AsdD)6o<LKHlo>L4IXClgeSOMhXLDoap52FXe!9h(F~W-kGZ!nO*4ceOm3GP}{tzC=w!*zrnyoevGCr=JICMqGoiW@d67FeP<lSixW&plesi;GRv4!7t6dwEw<-GhE(i)EuOkC+l6Qq<W*4gjYtW3M!ME+WYx=z8K>K6v8>xFqekvkPXMd|fscMlR4jD`JKBwMNMrev)U}0d7UmW7A=e&et?t5_asHa19n9~7axCSZr&=Q@X#~yaageK!SguklIPT6)>;sUz@G#-tU|q%*|Mg)`cU51yyB-dti{#cYr6x*+8YN8@A^*X6M;*~K?|?m_$#tbhidSC7@>gL{n`t6u-qCuN&Bn7p@iQ>IgC$oCihU=fofy<J>qjR|O5lOj&;eo%J+$=hByx}ETF94xKRf43aH1b+By(nd5F$H0#d4ugxeNVGjr4P;QQWG&c#M1*l|u}~(3z^EhCyHx!^1hAjVC<jdn3rvGq(<2ej^3WxL$n3BfUFC3&Hpbjuv!Km93aE>ZNyarB}sPX%s#}c}9_8F7B``rIi~@#+WK+VHwP%6cKAs_Z;>4D#7FEV{skDaEUS^qt8A7xQ7a)nPUcn$fb&0w))uOu#6Ws22ty?fK(<5x)vuEp5Fq2=G%z?fJN5KDUIV8F?7Bl@|bp%T0KI#@yh8PCbIi{G*d`1J8@ib)e8&DCc9I|Vy%oOAbt^kFpp$j;ET7tNG{P;Rs-o(Y%6CRad;R5Hfq7kSE^xi#xmZa=aB~W^CLJ|86i1iS?P0-sw)Y|1*;xsIb1CE5<Q<BVIBW0EHS;6Hy9;f4ABRPrH^bFt1T&MHh03Zze9T05~3~pXVDzg{Sc9Cklu*^8r~%km$Q8;WW15_3J!=Z@*(1ac{d`@0P8)7lB9_Hab2*7%cGu&3$!ST={(MzP`-m9XY2*MM$(KJZMd|33O#K>WOQJc0KN@=5LRSd=)`%C0@_UIZss=i(qWPZkwE35SwEi0grZ8R`xpW;rVoo^;^-(q$A(dZp6Xh01A<mTufaOYdfwkdrj*tx>O&;D8rBVn>4;rz=VWsbVS*|=*Gvlxl*mG+bzqb66j?A|7g3Ikg1K7N>xZ~yT2bE`iDf<4g-k=XdOu^loUiZoWVWzUje#|vK4cc-XjdnTnx)L$ofuzAndoXlWGGb|SOZTQsE>M5m_=;uTU)^9iE+3j3%ife+Ro?pZP+_nzM+%YuG%#^%uqG=k%7)_KUxR%(yER)#P>EzXc}9j`3G*lv>^h_#?wYjjJl(pE$?W3sOQ^8CfXxnvcPW6AHyPI+)|<K4p)GWi69R3Y>!1P=k#dzrJSPO3POZ{Ecu5lK&VBhT+8H!{tg<CCI!{AQYKIc{3v1@*G?TuC#^yksULZH42jA@$^`<*IKVA}94sx#aigY|iN(scZzeMbtseN6=!JbThFQ}V#(-M=Esr;89|=Vp_M0&@PF-w^E(Yeh%&-qx+uM*iG=xd-F#tz^s(RJ|=siZ<oA}<-ESEMa)()<o6AfzWw*j3iBE{<J)JDUG6Ad~P=vOuw%0deGrHtczX;@EzHdt!rL6+mKOy=e><!=u%1qJ^Xmctn(j3{oy(EH4tJf2UdEiUv*!3KHpR@}Q}+q9_Ev{j38d+$LS%$FcBCmi+f2hsqRXv-3ut!Q)4KV@OnnGbS2Tv~(;Hc*b~kvIDaN&+l1+wah5HxG<BhL7BuHg1dA%wPC7{PIXpO-up2zH3B@ZK=S5Q=Qw!g{&uxQ13@qeLnShg5oZ#_h%>l&olJezf~IWmU4bi=lB+Gn(~=pEx(sstF7etWWAb}4ZSyYpVbF!>Y|K8@<|f<VP8>d4SAX6r(nuFLpu2FxGS$c+9^x1PDYBBC*u!~MwA&%P%sW`rP?zHka5!qLYNoP*}FDQ8N`B>vEZb};XXtImqc7E)BUp#a09a97IDV|jG1_1A{Kq}l)Vg=NhSteNr%}tu8ZIEWL#kfofrflR~E+AZsZCGRJS8n$Ji<eyF;99QU7=l8Hja)Y7~hokVBzMOP>lB1p6kEsmSkt-rFoInTCbtgfpOJ_G+D+TMg2tyNs^(AerAQ!@Xm6Q<UuuW4?puSMj{S_m($k`A1nEwQ_|iaV@(c=@=YDJs$Z^G_9gD4QZg|zlvs&0l6X?T?~@dk6Lg(rf6_{^=KB4p(95t4Eba<jVaseONQDInPg6SfzTe=DcL84lL1W~&Gkxe+>DPGVG~UN9~aH8-OOJAq+=A`*X=fbEs|!<4Ey<LKJ8~CVmpgDnd#!h?R^J3#Pk_PA;dbGk1u1PNqYBVw(9_WWOML1Tn~mU9Yu}`!{8%E`;FmJ#an=9uMx4Uh-kEL69Ksu733unlb$X1uR#wlll6wuT?D&X^hZ>ghIpf6mJjz29-;;!XlntiJ4#)CfN$GJ5$9;d+tfD>aKnruPYCwQu*RrV-AX$d5j1D$Y3{LZRm}(ZtQX@*CEST@;8eniBJ0Q9l0*D%3GT&&MNt>5&1_SYW?P!O)#*UZk$R&Cm(Ouvyy`DK+zH8Slf-^4n1xJ!|AN8Qb>`wT*u4Sdv5C1P>D^aYP}oQILx0dCd#`e%#~;~!L#2u<L->}&QZ|$RU=-7lT6HL6XZ({)Hbtm#$aO}@$&n-hQoe6SYRdQLAw-}C0LINj1JthJ2VCvE72N?51UNgBaw1?SNY5OcdiOEhWMPXtyw$qS9}K9g+*qWoinRR)j2Or??d67rLg!S7wPO&APYx(0fDMhY-HDG>EW}K343wkE!x{=v(c)9YnkwctjEP&N<xgIx)s36D0Dn<=Mq2)x!GZudYx%5m2>NR867Q|EyL5^LP@GcbFNg5ETp0Pu+nKXSo*)WjW9S{|ag|&X?Pa#e%4*sKk{v^9_++<?wOQy~O75jW=FSXwFY-?VyH!VUB|b|Ch4>dR1uLqS5no2-q9yl6Wu0w^@zQotsw@~x&j9}VF(44TA+g9%BrQ7yFtc*ixKT%Xa9A{tZ89cyNbffza_&AEXsu#>9N9PmT?E$;NAUCDMAtD_8H~J>>l2$&a+~mRqK%ZRH7Q<v*rc76nZ~+g$FT0l_(C>Rc05^aKXe1TGu4qkUNDW_ZB+Kk%2m5lG&x=kHUXg(?7_McX_VkFji)KctaO`{<2dce_;^B!vfrqjuBzZ0o>n02$P5wqSehKcF=l1kDMLY=cK;M@#=b?DV&9IN9TC$zOo<nyieH0_9g!p0G)P7R6R{QIKS$)FP@~~ewOCf8>~ozNCGImRCwF(76HgnZ)V+xZB+H(}lW%{5wG<mpcjIs=K_<!W%0gddb<j6HpHcCe#~vaTPSyf*7sEAy+Qg`b_W69uxv}4BYXstBJHt?5O{F>!;iP!RH1;I(UmT~J<D?rVtE>0n(|feuM;C?|X0a}yE%i;ns4C~HC){apioTwP)R(Y0ojj-s<3%WL?rB4Pavyh|lX>IV-H^8Xz+y-5<6#iE&&+gM<+QU1Ig?yuCb?9rlPJZ|IiAkYR_0c90yaz{)RW-Aa%68Rc`ADD=$H&_WrMzy7?tl}(n!tiHrls}^5SZ=ki;6P(%ntAN{U&<m9mPdBR)yg&NenE*ui`IFhm$ijB8Zy*~^|)0HqB3=|mQ!(1-^A1@#jQdg+THXe?KZo6uOy%2}h*X|x{_$#xJ`GZypM9jUo>vSa++lQ47KGPc$-w$7|vG~;u$5Lh@YjbLoYt{YvdPIjyerf9)Y5sXoUSv&^wVh{$l(PrtX(+R$m+#0jvWgS97Qwq1E2f=H7O70d+qtKN_V`rkdKQ|}tmEN~QxC8!8pI+O6NoIWql9iV1q9v?;0{k%SItjlcc$XM{M+>Ckr7&c}WxS~iYxj(c1ybgDz)V4C3TToQY$Ic50o#*<;A|M~Wx0&t`lKagjB+WU>E&po6_2#y`_e*aO7bme>7<IWoK`Z@!aJ;`X-F%rFD-<oWZ!~TkW|sCW3;l7RyNWqL0Tn!X(3c$%jN;e1xppn8M#jxrhX|)hkv?)rAt}bi?qValr^`e9wJr5bLwk2^);OO22OoLKh$}d;=DEWK~hDt$f!Fxbtk9Z#Hly+L!Fl??YE|Whg4zX)Z01rc22#6Q}5`9IxkZM@s`v>rHbL4I>Xd2W$Exw^(<Y=(%#g0nG$_#>Vu^Uw&SV)G@4V7=G5ak_4t0M^D-s**3^gCW&!ql3~Ts%X^c`Mz}9itIu1L{wmbDo8mG*5rZSIl>e%{@K<aG2ZmMJABbHpBoO=oHTz@C9`}E7cLkT_OnE1BrIv$KOm_@u{sbc#jhxv7AiU=`v<{@+umTsIqF|OOu$=fj}?s<EP+41BPskuIUwqWITA`VxpuOoFN5e1~sUth!(%^psH-@dcDz@sjd#RIbF7B8bCUPO_=`NVRFJ{&Jx<Ijgt;KpxUg}od}Vd^sN-dHV$WwgDsxF?3fskNgEODKrKCvEZhZIPZh<AGFVi)|R6p(^<9e}ug&0SRrz6?ee%VH6zd`^K8;gq^*j%w<}X$)6ygSkfO~QZVWL(?yy)iz=I?r5|Igwv3`OdMa7ue>#90%n;A;y~!c?#23y(c4sgT=W(8HN_3UsDk$XG-6RkHy~64N<YBs59u*xoFzCQI(0dsfgP9CsEAN#qwniU!mmqkp7ipo{eCh+-XrVu{_FlN)^QkKv`8;p+u0Kbc!z_OC{uCAj1wHYUab}9Li?%eBefX5Ty!f=bm~T`tyTV-ss|Ny@SlY%wal(8RgZD~sQ-#gQan;hh=Y!b|TfUP~!50L0>x58T(z`2zX``dgzpX<TP5y};$;@In&9IOiwiEgY0}?|mqmJRoG_fc;7H_hc6E2w)Sk%b5MTVGE<s#m-K-XnXI0~cEWmLA&sx$u75I(=ADEp>4BI5!guaMEuh-%ou<wYBs;dfCq3IUFKCo2dxXfYoJO#cj`Ry!Jc_Kh+l4g5w1#!D`uhxdQJWBd0-L2QR7#W6!9WjmFUct)x$_F=RK{6l|Y@S$BFMb8rjzFlF0C`J17H*#*X>^dB*{umlG+Pg*iixt#?<q@!S*)70|DON1Q6=>Md2wK}<<tltYr<o*-ng)cn0onDW(9=W~`qv~l6J65sFJb0tWu^jAs15h+9PGh<e5#ynq_F4QWl)5Ln87D=@J|t1E4DUqcpAZt1dj(e;)7PwUy9@31hg_^LsV<aCgx83Ps#KB8vAMe)Yjl=nJ)?O+M~8SY4Fr(k7y!_$BBP?!8ilhT>SOGffFBd20qOvFuko}_b|ajEJF{`-bl}QX8RaeOL#l{nPemjM737%Z#Fd0O>Jzvxs7sYgZBlS@`OAV4q6NWX^@D2lVnly@JVEwA<dlN#7DSkwFU9N6&C?EOKv8tvhh)}s}`l1ych+km1oM{VDm?6?x6%{s(3KPbu>6tyuJc(?rMo01a1j8e46liWiMRpc01|j)xn7d?b%%ZL~deDS%d7DE}F&jX0e0+#f`k!MM>f{+YDLRj%^bY(6G&sn%kb>{NDEJZqeSU<*jb~6PIlK11IjU#d1SQiv4=1?M~w+`fE9FH#uV)ssgGA{ecA_lLCX8h{%mpF{PWH8AhiSFej)hYkj^x#wK3(`Mk@oqce=DRu|OLMU!{sHM(#GJY}c8SnJ>Gk6`{9G1R15&EV12y-BQQwRT6A-`|ZisKaad7D>GSu5P5kd*UjX?@Xmb`NrhP@)=)DRkj(GCS|*EhDrK!wVc~zPG~l!<6~M*<7U1v@y#$P`(6Os?UI!Sd~Uld)iLxNr5d~fn9+Bb?1$1lm%kMui13*lhP!0fiJ;Wnqh`>uiYWd7F{)S>ILZz=cOTAC(;cxo6PWsG8K{|*W|MN(tXze84W<E$0#VYrOHh6J-<U&CWoWql)ZI`n+iOD2Voge-7outAh2}vEap&ID*^ZbiTcqXn0%|2auF#Gv{%0JK58(|RTubhO=JuGB1E<2Y`3KQ<W0!ZZ=MhX&Cf;htN4u<pW$}vrq*&I1&rsCzmJy@A^C`(X^cp@h0m^2*h}=|``bb|?v>tpSqr+Z}f8>J;`B%FVzmY0O1A<xE5AL?Z1c;|WB;T3D8lwm+L7!;*p>Z?)Rp?fjc6;VWoLsRtz+t`D1{4C6jQ$q2*I%FBK5iekkK4!X;~#xIe*D1Xxo3Z$v_5w2xSbO|OVUldlr+imb&@A^b;`0q%}F!p*q6kxo01}*_{-f-{AEv4S?YdU>i(likJ51@spaqU;QuL(*OBypi|>CFeI}2UTpoY=A8&`z{k5O2@zbtz4}Jdk|FL$idK=#gJGRqL?~Y-A{M+Ntp5A=%*W2Hmvg*u#yPdg@{PwGgOTW8`&X4A`Jn{F|nxtQxFGzYpa{f2l`L~<upPBxsw5Pr%DYbpVmcQ=R#^r;}|EH8cc=yDOjoml%U;1*!r3ZJ_B(3_mEqO`Vmr0N8xgNbE>;28I-gzy~bAHi(xj%PXS5^II*O8m>-`lip{fHw&oL3^2cPywqwRuLA!~NmUpGYqJ;|E<O4^2$IGBtC_XJ4D0-$#GO-$x$_`JnA4`foQs^Ka`;1UYLzT=vl?M-Fd3JL8*=k3K#rd84)SZ<m+HC4U~VKkDe(Wan$^KJ)x__sRj~_RGYPqweZHb5r@R?z~p${yH-Glejl@@4j|E>HeV+hc{TFo$JcHArDqga6Z1IVbG7i`cd+)^t)a^(HWE+JM-bNZCRl=_2=OA!B2ekh%Wi2e%+|g{Ul<HbA9RhNp+&&92D<cUVbsbDZcl&sFR&fB;S4d{(pY_+d<Ax9{tUIC%zu-%!#U<x_V<wvhMH;v)6xgG(aBNKsy?Kq=V3YGF)$f-wOCGO8&#|@feb<`K#-noNrE@ot!i_^Zn|JF$X!FAMx^do<{LhpIm;=?zy=;{*ZL|pZ?hVgT{#D-~3^pdEK-dNz?xP(XQf&_c&Lb>gXJKa!-<O!?gExZ*JK<{>0mbGq=?xRsZA<X+J*tankwUZXT8QOzr0T-pc;%pW5C_+VZ!5`u8cnxUjkOy|%CIUwpfH@V}qAobubNNyGp14?lc7tY!17Z-xJ*?kC@DRuUIB#pmuzniTnO>8H9rOFEP691=R==bY|Gn|~Vlr|E~@tl<1RH~->a@u*8`+=0hw4v$QZ8gEL!HhM7cPkR!}dwF^<hu_cB2Y4E)jTcX+@-&90LwPz;lN)>c<DzFYxp6({N*Z?e@5g+3{9w|##H%-^#vM=k<-@;S^2>@rQ&{_n9N*yA4<9?;?xQY?v<q=W&=dGBP<#PQ+UGvsLTv2|pAT2O?U3S@Li{G5?;vW%S3Vy;+}u&)^OeK;a6^mFw*%6W(>~w*K|mDJct|_W`+TSQ%LXI0cHVqm5Etsj5kv0?#lO$O_qg7VGvh{|k2)8we=0ocY3a__Ll+52_dPN0QNsgTeG~dk;4Sd|g7^*u<U1O8oQ~@zW4PX~dnP<SC{Ya88^aM-<{h<s349^W)NuX#x~IdVmIqA@k9Gu44UbtCVhoR8GH81EWcwW{;b}p^V)$f$7{g-#V`_L5)R;=Na94c?m&MXhjn>qDXc-wT=R4uLCE@LGo*J&c6FxP(15aIeT4WE`)gVI9@!;^<cfyU~P49%8!rgdkM}(X4(-D2<KLYt#;`C=j`s=sx&N=^xCP_FrE;xRmKSf)7zR!o<N~Y6LrqjdMgamDh?8E6(oKsG(1n3=f`+W5N)mzhhI^0<=29-(!be+8q)QRtZ@%nt)yD-rn_TttQ!06qq)P~vLhPk&M0M8Y=pmJUKh6>$F;TtP-rf?^onksZ@;cmQY$5RJpyDD_k!xvTRvartd@O60FfTdcsXRz9Ie>EAaJ?*bnKux_Y4%i)XJ}ba3ub%<C?QIWFBkvaEJq>v`A@4!U#QrSd_Hq08|Nqe5^Q*nrS9@pg=R)tiw)f_LM=yWTu=cLnWlyv8UY^(9Cp?1ZHH*5Br`mgk@9$H7@rIAy{F}{R?yLEuh5Y5c+B<ny@pA3my61SRy;C=er`o%KRsKF<?VZ7)V()oddnfTd8vQ}N;T<8p`CP}-!F}4h;bZ)-2=T`y^8?%M;Q6_{{0h$p{XZIi?S1t(t<(7UKE=})d0N2J*Lb>wryue3W1jw<r`ve?4NtZAL{FbK?eXXsQ~vD2oZ{#Nd_{Kr_=JfM=jG2%m{685mV*Z7o4xP<yss~OD9L)L(4p@Q59jdch~Dtg9G=|={us4!kC0u`+YYAD^<94b)s9y<oi%;vyhivDetXc4pAEqO8ct^er!$>5{4wWe5$8vHm-QzcU$~n`)Exg$93IaVd?{DlIU<8Qx#3Yf0>>9bKivPlglta#D-O@*@I|~~C+BAk=VvR&uh;l|l><82cM}F0uVyNP!FuWDG42n)o%$8#_cz*coahYq>z8(1Ao$%k>G^d!OaAXCXon;+I@x{bj3D?hzaP<#1d`|Ao)@oc`Xl!L9{v}^{@<&gC-(pT{CNZ5mk$7ce*pOJ27v!{06wb+z~4In{MZ2SYXiW;bp3x9V7RXT?*fd{_5a<0hjjh(Z`AeQ?(@3-zjrWi0DK|0)V9D@R!|U^EA)JZAj>u{D;GaEut3Pl%A21xr)d7{oT98e+x*f6Svh43h1~h`N{aGr`FY^O`o+MH6BK6Ul$Peak(FO;D}6&KD9xFdpOsfOZ{8bFB_Njtn6_T1#W}XZ*YY2o06dk<e?7lcc=lOnvG_G%PJVHIX^t&Ft0+&HHcc=Zh1c^7=ghU?hY#2lGW^u@##D2b`B@WwUjg|*78lIVnwwLchaXQcWjt$4O_>JJ>Ceu{GRwSzY<eC*>8aDSs?#k$o@%sY{rIV;UNEO;r5mSO%m77hZ~55<{0u{K;HMG%UsZt4BnNyPfqk~27b^Q`LoZNHUqGKPNU+a0BnNzd0Y3rJtA_u>54{QFmmzvV{2zPpfBr%HM#R9MqQFl{^kFaX+Z4U&FDwb{zYw?Jjd`}5*^t^wSvps{DxPo4kDF6m7B{=BuqbbQVV*!a5aV1SF7J(EsL4`WDJyv`zjQ(2{Ni4jEGR3@FUmngepOOr6XIwH@iK1Ce7LaXFN8BGN?hsuJdleJmp_-Q=-j;0o*b*nbd}Z6uAzmTd4;(GQe=%VI<prn5aPgE=7DDaPsB4Lgx=qV80h;tJ#$R&BMyF-ASTo5YjLQSPV5s`_FXAX<}s+QPn@cy?P5>6VnF?<fQ_@Dfcje8tEK1qiGu<Una7-3eJ#$^(wIK{>-wZKcnquMwK!HwvjgO&>!<&D0cC-4vzD$KKz>^Pi+TO2ed2H})#7%nKdhhn3x&XM3JEuTKkA<E8UF=+>PPE)r+qi7`+lbCtv>bJ^}W-+@(S&fzT2n17RPGo>csxr*A7RY`dXZ%rGvkx{~z-D{%@=F`HogopN~oPoqK=Tr~W|SsT!#LPx{o4pV>Rz8`Qu2{P7Hr^@IAXL$&W%eV_a{3+y{9L4DS#9skAp4P5p?eb!gncfy*)-u({kGmh`@{%iHM@9ETL^)K(f?eFbVUyD~&Uccmf>bLf(uf@~W>|6I=JC1OeR$q&wvw8jK3wy;|>5t0W@4NKV>OVAq{|iiY{mctXvwN>!a35l1KmKFz0Bdo47MkL2-L3s^!~pdx=CJhq_xSJs4d;)fX#'
_NATIVE_SOURCE = '#include <math.h>\n#include <stdlib.h>\n#include <string.h>\nstatic const double AA[12][12] = {{0,0,0,0,0,0,0,0,0,0,0,0},{0.0526001519587677296,0,0,0,0,0,0,0,0,0,0,0},{0.0197250569845379004,0.0591751709536137011,0,0,0,0,0,0,0,0,0,0},{0.0295875854768068505,0,0.0887627564304205446,0,0,0,0,0,0,0,0,0},{0.241365134159266692,0,-0.884549479328286092,0.924834003261791993,0,0,0,0,0,0,0,0},{0.037037037037037035,0,0,0.170828608729473863,0.125467687566822417,0,0,0,0,0,0,0},{0.037109375,0,0,0.170252211019544047,0.0602165389804559595,-0.017578125,0,0,0,0,0,0},{0.0370920001185047893,0,0,0.170383925712239981,0.10726203044637328,-0.015319437748624402,0.00827378916381402325,0,0,0,0,0},{0.624110958716075692,0,0,-3.36089262944694145,-0.86821934684172597,27.5920996994467096,20.1540675504778939,-43.4898841810699608,0,0,0,0},{0.47766253643826434,0,0,-2.48811461997166772,-0.590290826836842975,21.2300514481811931,15.2792336328824234,-33.2882109689848633,-0.0203312017085086269,0,0,0},{-0.937142430085987299,0,0,5.1863724288440638,1.09143734899672951,-8.1497870107469268,-18.5200656599969591,22.7394870993505052,2.49360555267965234,-3.04676447189821964,0,0},{2.27331014751653804,0,0,-10.5344954667372495,-2.00087205822486247,-17.9589318631187993,27.9488845294199599,-2.85899827713502352,-8.87285693353062932,12.3605671757943032,0.643392746015763572,0}};\nstatic const double BB[12] = {0.0542937341165687648,0,0,0,0,4.45031289275240916,1.89151789931450032,-5.80120396001058491,0.311164366957819905,-0.152160949662516087,0.201365400804030342,0.0447106157277725874};\nstatic const double CC[12] = {0,0.0526001519587677296,0.0789002279381516014,0.118350341907227402,0.281649658092772592,0.333333333333333315,0.25,0.307692307692307709,0.6512820512820513,0.599999999999999978,0.857142857142857095,1};\nstatic const double EE3[13] = {-0.189800754072407624,0,0,0,0,4.45031289275240916,1.89151789931450032,-5.80120396001058491,-0.42268232132379191,-0.152160949662516087,0.201365400804030342,0.0226517921983608213,0};\nstatic const double EE5[13] = {0.01312004499419488,0,0,0,0,-1.22515644637620436,-0.495758949657250203,1.66437718245498645,-0.350328848749973665,0.334179118713017476,0.0819232064851157099,-0.0223553078638862937,0};\n\n#define MAXL 1600\nstatic double pot(double r,double a){double s=(1-a)/(r-a),s6=pow(s,6);return 4*s6*(s6-1);}\nstatic void rhs(double r,double *y,double *f,double a,double cc,double e,int l){f[0]=y[1]; f[1]=(l*(l+1)/(r*r)+cc*(pot(r,a)-e))*y[0];}\nstatic double phase(double a,double cc,double e,int l,double tol){\n double k=sqrt(cc*e),r=a+.44*(1-a),end=fmax(22.,(l+16.)/k),h=.0005,y[2]={0,1},ks[13][2],yn[2]; int nodes=0;\n while(r<end){\n  h=fmin(h,end-r); rhs(r,y,ks[0],a,cc,e,l);\n  for(int s=1;s<12;s++){double yy[2]={y[0],y[1]};for(int j=0;j<s;j++)for(int q=0;q<2;q++)yy[q]+=h*AA[s][j]*ks[j][q];rhs(r+CC[s]*h,yy,ks[s],a,cc,e,l);}\n  for(int q=0;q<2;q++){yn[q]=y[q];for(int j=0;j<12;j++)yn[q]+=h*BB[j]*ks[j][q];}rhs(r+h,yn,ks[12],a,cc,e,l);\n  double scale0=fmax(fabs(y[0]),fabs(yn[0]))+fmax(fabs(y[1]),fabs(yn[1]))/fmax(k,1.),err3=0,err5=0;\n  for(int q=0;q<2;q++){double v3=0,v5=0;for(int j=0;j<13;j++){v3+=EE3[j]*ks[j][q];v5+=EE5[j]*ks[j][q];}double sc=tol*scale0*(q?fmax(k,1.):1.);err3+=pow(v3/sc,2);err5+=pow(v5/sc,2);}\n  double err=(err5+err3>0)?fabs(h)*err5/sqrt(2*(err5+.01*err3)):0;\n  if(err<=1){if(y[0]*yn[0]<0)nodes++;r+=h;double sc=fmax(fabs(yn[0]),fabs(yn[1]));y[0]=yn[0]/sc;y[1]=yn[1]/sc;}\n  double fac=err>0?.9*pow(err,-.125):5;h*=fmin(5,fmax(.2,fac));\n }\n double x=k*r,j0=sin(x),j1=sin(x)/x-cos(x),n0=-cos(x),n1=-cos(x)/x-sin(x),j=j0,n=n0,jprev=cos(x),nprev=sin(x);\n if(l){j=j1;n=n1;jprev=j0;nprev=n0;for(int t=1;t<l;t++){double jnew=(2*t+1)*j/x-jprev,nnew=(2*t+1)*n/x-nprev;jprev=j;nprev=n;j=jnew;n=nnew;}}\n double jp=jprev-l*j/x,np=nprev-l*n/x;\n double delta=atan2(k*jp*y[0]-j*y[1],k*np*y[0]-n*y[1]);\n double phi=atan2(k*y[0],y[1]);if(phi<0)phi+=M_PI;\n double nu=l+.5, wkb=sqrt(x*x-nu*nu)-nu*acos(nu/x)+M_PI/4;\n double freephi=atan2(j,-n);freephi+=2*M_PI*nearbyint((wkb-freephi)/(2*M_PI));\n delta+=M_PI*nearbyint((nodes*M_PI+phi-freephi-delta)/M_PI);\n // Asymptotic first-order tail, with the leading oscillatory boundary term.\n double b0=pow(1-a,6),ll=l*(l+1.),ra=r-a;\n double tail=cc/k*2*b0/(5*pow(ra,5));\n tail+=cc/k*b0*ll/(7*k*k*pow(r,7));\n tail+=cc/k*b0*3*ll*(ll-2)/(36*pow(k,4)*pow(r,9));\n double v=-pot(r,a),f=cos(delta)*j-sin(delta)*n,fp=k*(cos(delta)*jp-sin(delta)*np);\n tail+=cc/(2*k*k*k)*v*f*fp;\n\n return delta+tail;\n}\nstatic double born(double a,double cc,double k,int l){\n double ans=0;\n for(int n=6;n<=12;n+=6){double coef=n==6?-4*pow(1-a,6):4*pow(1-a,12),term=1;\n for(int p=0;p<22;p++){\n  int v=n+p;if(l+1.5-v/2.<=0)break;\n  double in=exp(log(M_PI/2)+lgamma(v-1.)+lgamma(l+1.5-v/2.)-(v-1)*log(2.)-2*lgamma(v/2.)-lgamma(l+.5+v/2.));\n  double add=-cc*coef*term*pow(k,v-2)*in;ans+=add;\n  if(p>4&&fabs(add)<1e-14)break;term*=a*(n+p)/(p+1.);\n }}return ans;\n}\nstatic double gaunt(int l,int m,int j){int s=(l+m+j)/2;if((l+m+j)%2||s<l||s<m||s<j)return 0;return exp(2*(lgamma(s+1.)-lgamma(s-l+1.)-lgamma(s-m+1.)-lgamma(s-j+1.))+lgamma(2*(s-l)+1.)+lgamma(2*(s-m)+1.)+lgamma(2*(s-j)+1.)-lgamma(2*s+2.));}\nstatic double weights[49][MAXL][49];static int weightmax[49];\nvoid scatter(double a,double cc,double e,int nb,int boson,double tol,double *q,double *ds){\n double k=sqrt(cc*e),delta[MAXL],ss[MAXL],cs[MAXL];int ln=fmin(MAXL-nb-3,ceil(3.5*k+20)),lm=fmin(MAXL-nb-3,ceil(20*k+55));\n for(int l=0;l<=lm+nb;l+=(boson?2:1)){delta[l]=l<=ln?phase(a,cc,e,l,tol):born(a,cc,k,l);ss[l]=sin(delta[l]);cs[l]=cos(delta[l]);if(ds&&l<=ln)ds[l]=delta[l];}\n for(int j=1;j<=nb;j++){\n  double v=0;\n  if(boson&&(j%2)){for(int l=0;l<=lm;l+=2)v+=(2*l+1)*ss[l]*ss[l];q[j-1]=8*M_PI/(k*k)*v;continue;}\n  for(int l=weightmax[j];l<=lm;l++)for(int d=(j%2?1:2);d<=j;d+=2){int m=l+d;weights[j][l][d]=(2*l+1.)*(2*m+1.)*gaunt(l,m,j);}\n  weightmax[j]=fmax(weightmax[j],lm+1);\n  for(int l=0;l<=lm;l+=(boson?2:1))for(int d=(j%2?1:2);d<=j;d+=2){int m=l+d;double sd=ss[l]*cs[m]-cs[l]*ss[m];v+=2*weights[j][l][d]*sd*sd;}\n  q[j-1]=(boson?4:2)*M_PI/(k*k)*v;\n }\n if(ds)ds[MAXL-1]=ln;\n}\n\ndouble onephase(double a,double cc,double e,int l,double tol){return phase(a,cc,e,l,tol);}\n\n#define S 32\nstatic int NN;\nstatic void conv(long double *a,long double *b,long double *c){memset(c,0,S*S*sizeof(long double));for(int i=0;i<=NN;i++)for(int j=0;j<=NN;j++)if(a[i*S+j])for(int k=0;k<=NN-i;k++)for(int l=0;l<=NN-j;l++)c[(i+k)*S+j+l]+=a[i*S+j]*b[k*S+l];}\nstatic void power(long double d10,long double d01,long double d11,long double p,long double *out){\n memset(out,0,S*S*sizeof(long double));out[0]=1;\n for(int j=1;j<=NN;j++)out[j]=-d01*(p+j-1)*out[j-1]/j;\n for(int i=1;i<=NN;i++)for(int j=0;j<=NN;j++)out[i*S+j]=(-d10*(p+i-1)*out[(i-1)*S+j]-(j?d01*i*out[i*S+j-1]+d11*(p+i-1)*out[(i-1)*S+j-1]:0))/i;\n}\nstatic void generate_ld(int rank,int n,long double ai,long double aj,long double di,long double dj,long double z,long double c,long double *out){\n NN=n;long double bi=1-ai*ai,bj=1-aj*aj,aa=ai*aj;\n long double D1[S*S],D2[S*S],D3[S*S],inv[S*S],F[S*S]={0},J[S*S],H[S*S]={0},tmp[S*S],term[S*S]={0};\n power(-bi,-bj,1-ai*ai-aj*aj,1,inv);\n F[S]=-z*di*di;F[1]=-z*dj*dj;F[S+1]=z*(di*di*bj+dj*dj*bi+2*aa*di*dj*c);conv(F,inv,J);\n H[0]=1;\n for(int j=1;j<=n;j++){long double v=0;for(int q=1;q<=j;q++)v+=q*J[q]*H[j-q];H[j]=v/j;}\n for(int i=1;i<=n;i++)for(int j=0;j<=n;j++){long double v=0;for(int p=1;p<=i;p++)for(int q=0;q<=j;q++)v+=p*J[p*S+q]*H[(i-p)*S+j-q];H[i*S+j]=v/i;}\n long double Z[S*S]={0};Z[0]=z*di*dj*c;Z[S]=-z*(di*dj*c*bi+aa*di*di);Z[1]=-z*(di*dj*c*bj+aa*dj*dj);Z[S+1]=z*(di*dj*c*(bi*bj+aa*aa)+aa*(di*di*bj+dj*dj*bi));\n if(rank==1){power(-bi,-bj,1-ai*ai-aj*aj,3.5,D1);power(-bi,-bj,1-ai*ai-aj*aj,2.5,D2);conv(Z,D1,tmp);for(int i=0;i<S*S;i++)tmp[i]+=1.5*aa*D2[i];conv(tmp,H,out);}\n else{\n  long double II[S*S]={0},JJ[S*S]={0},ZZ[S*S],IJ[S*S],poly[S*S];\n  II[0]=z*di*di;II[1]=z*(-2*bj*di*di-2*aa*di*dj*c);II[2]=z*(bj*bj*di*di+aa*aa*dj*dj+2*bj*aa*di*dj*c);\n  JJ[0]=z*dj*dj;JJ[S]=z*(-2*bi*dj*dj-2*aa*di*dj*c);JJ[2*S]=z*(bi*bi*dj*dj+aa*aa*di*di+2*bi*aa*di*dj*c);\n  conv(Z,Z,ZZ);conv(II,JJ,IJ);for(int i=0;i<S*S;i++)poly[i]=ZZ[i]-IJ[i]/3;\n  power(-bi,-bj,1-ai*ai-aj*aj,5.5,D1);power(-bi,-bj,1-ai*ai-aj*aj,4.5,D2);power(-bi,-bj,1-ai*ai-aj*aj,3.5,D3);\n  conv(poly,D1,tmp);conv(Z,D2,IJ);for(int i=0;i<S*S;i++)tmp[i]=4*(tmp[i]+10./3*aa*IJ[i]+2.5*aa*aa*D3[i]);conv(tmp,H,out);\n }\n}\nvoid brackets(int rank,int n,double mi,double mj,double z,double c,int same,long double *out){\n double a[2]={sqrt(mi/(mi+mj)),sqrt(mj/(mi+mj))},d[2]={sqrt(mj/(mi+mj)),-sqrt(mi/(mi+mj))};\n double norm[S];for(int p=0;p<=n;p++)norm[p]=sqrt(exp(lgamma(p+rank+1.5)-lgamma(rank+1.5)-lgamma(p+1.)));\n int sz=2*(n+1);memset(out,0,sz*sz*sizeof(long double));\n for(int i=0;i<(same?1:2);i++)for(int j=0;j<2;j++){\n  long double g1[S*S],g2[S*S];generate_ld(rank,n,a[i],a[j],d[i],d[j],z,1,g1);generate_ld(rank,n,a[i],a[j],d[i],d[j],z,c,g2);\n  for(int p=0;p<=n;p++)for(int q=0;q<=n;q++){int ii=(same?0:i)*(n+1)+p,jj=(same?0:j)*(n+1)+q;out[ii*sz+jj]+=(same?4:2)*(g1[p*S+q]-g2[p*S+q])/(norm[p]*norm[q]*(rank==1?3:10));}\n }\n}\n#include <stddef.h>\nvoid evaluate(int nc,int nj,int sz,double x,double z,double *co,double *q,double *out){\n int block=2*nj*sz*sz;\n for(int r=0;r<2;r++)for(int p=0;p<sz*sz;p++){\n  double val=0;\n  for(int j=0;j<nj;j++)if(q[j]){\n   int index=(r*nj+j)*sz*sz+p;double b1=0,b2=0;\n   for(int k=nc-1;k>=1;k--){double b=2*x*b1-b2+co[k*block+index];b2=b1;b1=b;}\n   val+=q[j]*(x*b1-b2+co[index]);\n  }\n  out[r*sz*sz+p]=z*z*val;\n }\n}\n'

_native_dir = None
lib = None
ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
ldptr=np.ctypeslib.ndpointer(dtype=np.longdouble,flags='C_CONTIGUOUS')
def load_kernel():
 global lib,_native_dir,ldlib,elib
 if lib is not None:return
 _native_dir=tempfile.TemporaryDirectory(prefix='quantum_transport_')
 path=os.path.join(_native_dir.name,'kernel.so')
 with open(path,'wb') as f:f.write(zlib.decompress(base64.b85decode(_NATIVE)))
 lib=ct.CDLL(path)
 lib.scatter.argtypes=[ct.c_double,ct.c_double,ct.c_double,ct.c_int,ct.c_int,ct.c_double,ptr,ct.c_void_p]
 lib.onephase.argtypes=[ct.c_double,ct.c_double,ct.c_double,ct.c_int,ct.c_double]
 lib.onephase.restype=ct.c_double
 lib.brackets.argtypes=[ct.c_int,ct.c_int,ct.c_double,ct.c_double,ct.c_double,ct.c_double,ct.c_int,ldptr]
 lib.evaluate.argtypes=[ct.c_int,ct.c_int,ct.c_int,ct.c_double,ct.c_double,ptr,ptr,ptr]
 ldlib=elib=lib

def scatter(a,cc,e,nb,boson,tol=1e-9):
 q=np.zeros(nb)
 lib.scatter(a,cc,e,nb,int(boson),tol,q,None)
 return q

def solve(Kv,Ks,R,X,T,n):
 x=np.array([X,1-X]);m=np.array([1.,R]);sz=2*(n+1)
 bd=np.zeros(sz);bt=np.zeros(sz);bs=np.zeros(sz)
 bd[0]=np.sqrt(T/2);bd[n+1]=-np.sqrt(T/(2*R))
 for i in range(2):
  bt[i*(n+1)+1]=-x[i]*np.sqrt(5*T/(4*m[i]));bs[i*(n+1)]=x[i]
 null=np.zeros(sz);null[0]=np.sqrt(m[0]);null[n+1]=np.sqrt(m[1]);null/=la.norm(null)
 # Constraint <m v phi>=0.
 con=null.copy();con[0]*=x[0];con[n+1]*=x[1]
 mat=np.zeros((sz+1,sz+1));mat[:sz,:sz]=Kv;mat[:sz,sz]=con;mat[sz,:sz]=con
 sol=la.solve(mat,np.vstack([np.column_stack([bd,bt]),np.zeros((1,2))]),assume_a='sym')[:sz]
 dd=bd@sol[:,0];dt=bd@sol[:,1];tt=bt@sol[:,1]
 D=dd*x.prod();alpha=dt/(dd*x.prod());lam=tt-dt*dt/dd
 eta=T*bs@la.solve(Ks,bs,assume_a='pos')
 return np.array([eta,lam,D,alpha])

def resonances(A,cc,boson):
 r=np.linspace(A+.8*(1-A),10,12000);s=(1-A)/(r-A);V=4*(s**12-s**6);found=[]
 for l in range(1,55):
  if boson and l%2:continue
  U=V+l*(l+1)/(cc*r*r);idx=np.where((U[1:-1]>U[:-2])&(U[1:-1]>U[2:]))[0]+1
  if len(idx)==0:continue
  barrier=U[idx[-1]];well=U[:idx[-1]].min()
  def phase(e):return lib.onephase(A,cc,float(e),l,2e-9)
  emin=max(1e-7,well+.005);emax=barrier*1.15
  if emin>=emax:continue
  grid=np.linspace(emin,emax,33)
  vals=[phase(e) for e in grid]
  i=0
  while i<len(grid)-1:
   if vals[i+1]-vals[i]<.5:
    i+=1;continue
   first=i
   while i+1<len(grid)-1 and vals[i+2]-vals[i+1]>.3:i+=1
   lo,hi=grid[first],grid[i+1];vlo,vhi=vals[first],vals[i+1];i+=1
   if vhi-vlo<1:continue
   target=(vlo+vhi)/2
   root=lambda t:brentq(lambda v:phase(v)-t,lo,hi,xtol=2e-14)
   e=root(target);left=root(target-.5);right=root(target+.5)
   width=(right-left)/2
   if width<(hi-lo)*.12 and width>2e-13:found.append((l,e,width))

 return found

def angular(mi,mj,n,rank,same,z):
 degree=n+rank;cc,cw=sp.roots_legendre(degree+1);sz=2*(n+1)
 b=np.empty((len(cc),sz,sz),dtype=np.longdouble)
 for j,c in enumerate(cc):ldlib.brackets(rank,n,mi,mj,z,c,int(same),b[j])
 leg=np.array([sp.eval_legendre(j,cc)*cw*(2*j+1)/2 for j in range(1,degree+1)],dtype=np.longdouble)
 return -np.einsum('jc,cab->jab',leg,b,optimize=True)

def interpolants(mi,mj,n,same,log=False):
 edges=[0,2,4,7,11,16,23,32,45,60,80,105,135];N=24;theta=(np.arange(N)+.5)*np.pi/N;cs=np.cos(theta);D=np.cos(np.arange(N)[:,None]*theta[None,:])*2/N;D[0]/=2
 ans=[];start=time.time()
 for lo,hi in zip(edges[:-1],edges[1:]):
  vals=[]
  for z in (lo+hi)/2+(hi-lo)/2*cs:
   v=np.zeros((2,n+2,2*(n+1),2*(n+1)),dtype=np.longdouble)
   for rank in [1,2]:
    w=angular(mi,mj,n,rank,same,float(z))
    v[rank-1,:len(w)]=w
   vals.append(v*float(np.exp(-z)/z))
  co=np.einsum('ki,irjab->krjab',D.astype(np.longdouble),np.array(vals),optimize=True)
  ans.append(np.ascontiguousarray(co,dtype=float))
 return np.array(edges),ans

def directpair(A,mi,mj,L,T,n,same,log=False,eps=2e-9,prepared=None):
 start=time.time();edges,interp=interpolants(mi,mj,n,same,log) if prepared is None else prepared;mu=mi*mj/(mi+mj);cc=8*np.pi**2*mu/L**2
 rr=resonances(A,cc,same);points=list(edges)
 for _,e,w in rr:
  if w<1e-10:continue
  for scale in [0,1,4,16,64,256]:
   for sign in [-1,1]:
    z=(e+sign*scale*w)/T
    if 0<z<edges[-1]:points.append(z)
 points=sorted(set(points));result=np.zeros((2,2*(n+1),2*(n+1)));calls=0
 def fn(z):
  nonlocal calls
  calls+=1;j=min(len(interp)-1,np.searchsorted(edges,z,side='right')-1);lo,hi=edges[j:j+2]
  q=scatter(A,cc,z*T,n+2,same,1e-9)
  out=np.zeros_like(result);elib.evaluate(24,n+2,2*(n+1),(2*z-hi-lo)/(hi-lo),z,interp[j],q,out)
  return out
 for lo,hi in zip(points[:-1],points[1:]):
  v,e=quad_vec(fn,lo,hi,epsabs=eps,epsrel=eps,quadrature='gk15',limit=300);result+=v
 return result



def collision_job(args):
 A,R,L,T,n,like=args
 load_kernel()
 if like:
  pre=interpolants(1.,1.,n,True)
  light=directpair(A,1.,1.,L,T,n,True,prepared=pre)
  heavy=light.copy() if R==1. else directpair(A,R,R,L,T,n,True,prepared=pre)
  return light,heavy
 return directpair(A,1.,R,L,T,n,False)

def mixture_matrix(pairs,R,X,T,n):
 K=np.zeros_like(pairs[0])
 weights=[X*X,2*X*(1-X),(1-X)**2]
 for i,mu in enumerate([.5,R/(R+1),R/2]):
  fac=weights[i]/4*2/np.sqrt(np.pi)*np.sqrt(2*T/mu)
  if i==1:K+=fac*pairs[i]
  else:
   off=0 if i==0 else n+1
   K[:,off:off+n+1,off:off+n+1]+=fac*pairs[i,:,:n+1,:n+1]
 return (K+K.transpose(0,2,1))/2

def nested_solution(K,R,X,T,n,order):
 ix=np.r_[np.arange(order+1),n+1+np.arange(order+1)]
 return solve(*[a[np.ix_(ix,ix)] for a in K],R,X,T,order)

def main():
 A,R,L,X,T=map(float,sys.argv[1:6])
 start=time.monotonic()
 load_kernel()
 value=None
 for n in (22,28):
  with ProcessPoolExecutor(2,mp_context=multiprocessing.get_context('fork')) as ex:
   f0=ex.submit(collision_job,(A,R,L,T,n,True))
   f1=ex.submit(collision_job,(A,R,L,T,n,False))
   light,heavy=f0.result();unlike=f1.result()
  K=mixture_matrix(np.array([light,unlike,heavy]),R,X,T,n)
  value=nested_solution(K,R,X,T,n,n)
  previous=nested_solution(K,R,X,T,n,n-4)
  earlier=nested_solution(K,R,X,T,n,n-8)
  tolerance=np.maximum(np.abs(value)*2e-6,np.array([0.,0.,0.,1e-7]))
  converged=np.all(np.abs(value-previous)<tolerance) and np.all(np.abs(value-earlier)<4*tolerance)
  if converged or n==28 or time.monotonic()-start>250:break
 print(json.dumps(dict(zip(('viscosity','thermal_conductivity','binary_diffusion','thermal_diffusion_factor'),map(float,value))),allow_nan=False,separators=(',',':')))

if __name__=='__main__':
 main()
