#!/usr/bin/env python3
"""The Day in World News - entry for make.fun news-image-20261118 (v6).

Renders a 1024x1024 newspaper front page for Wednesday 18 November 2026.
Dual path: Pillow when available, pure stdlib otherwise. Deterministic:
the same input files always produce the same output PNG.
No network access. Reads only news.json and illu_*.png next to this file.
Writes exactly one image: /output/entry.png
"""

import base64
import json
import math
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

NAVY = (20, 38, 74)
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (193, 39, 45)
MUTED = (90, 90, 82)
LINE = (216, 210, 192)
MAPDOT = (122, 140, 163)
PANEL = (239, 233, 216)
WHITE = (255, 255, 255)
SOFT = (214, 222, 235)

ATLAS_B85 = "c-pMJ348jyk}vpGIt^j6G<PI<Zy>=y*vy^)ftd-rA#4c&lCXaEkz`x8!Q?%C?tPzg^u&LPQmIrb{i;+JyZ_WXy}|N7|NB37|M{tNGX0~o><#8C{3nn8>p%W;INf}X42u82?f(P*>p$546yuNo50m-HX9z!W@_+pY{ICBAa`?*#Q342gLUK(>L`)($NM!msZg|QkK!`XFf1nsdgn+}JBY_eLgy{bwL?Zd3O+&~O@*PMh{)<o$*2thB#8?uZG!PMrAfX@~6W*ADQsQs$L}-~%{4bM-<YvL)Mk1g8-;@J#i%L0i_$vbC0qB@bRZtp8hJtAn+=wEffs_v!GPG$R{#Xzpk%!PAN+X}}!IFr8v-oh726v4l2Oouej2oHig{L%%K?59oBmr170;Lhnxgj*9PfRa!kO)O+L~FX8V<)_1nGjO_NK9tY><but6bUOyqWY1UJSTi05Rk=4aSF`_PlzDLM)u!?NHP?JtihB2BPu4<V#uPAPHBj#BifltM`jWQX>XD-We^cPLO=zNQ8L~klVl7Oa*|}p6lX-v(Mi;fWovW^XNQav`GUX;tiLB_NKPuUBt(I;`b$zGctS*Hk1QdBD8>473Pq+`CPoJ#o!~U3QrxVF=|hEsOsWhsT?Z9e0tk?q5$L+lS}TpL`=Faj!QYkW!q+_2K>iO!j&+#xR09zJNzfW$p7{{jA-g~biBXxJreL`vCzYX9g-{u8qDZOa6MsZ3N(4O9R*6z^=d*((#MV{WQYj~%u#y2$DNnUk@f3?ZE7Tkev7Vjl23eDc2tR=>z!%C&a4dGyk~!QLQ)$)NA#ilaA;H!|jZKeyvMe}G<QZ9=s$M=JBmR)%C6Vd=)j8R&K1C=p$r?`igHE+_60!%-vV4(1Re=nH;AFDBK)PRan6^&5Cnxig<vzRC;vx1;WTI0;RH_gQS2#k{V?GwSeJl@vXmRRWM#`BEopRy`k%TNxgNvN-inciE77+(*nTRwzBD@u<%pqI#io>Uqt%IW;ncBk0vQQ@{DiaT6i_^Qcqq(|6gh-LeUPFk+l*ruagVykf8|4M!)g&tU#IrxbN+hnx=x=(lKRUlge=}-QyfGwec;uOvWNHL-isx(vI;iOQWSMM%ROcUT*Fx@%1n<Vk()lNIF|wPJ0LW%0(^a})I+q=s@RtM#kVW*xHb93=<XM2SXvwr>yRFj>2od%}MDv7bMTuN1K{O0OK*WU_j&{v-fKDXmY%~96l0%CXFbq%N2}47wAFA|IDl$C+UB|`%H%=`uD!LQ}5m;1PHbM*E0CR*QaYF{c`G3~{bR~0tHn(RA3n}Cv>XHmH1R!TEXThZ7%wdW|7sisOgcR*?z(q(bN05lkBVZABdTh>}dm^Po#zuWO5Yy0+=!VFI{!fT35+q1w&PK^pT+soo1dB#M3@1}>#hcTJ%n6c3q8!9<GL;w@oah&b5)`uY8cT=bWS${dQ)PleaI(Z;vOvKzAuvcq>dIsrBm)YP34vlPPZ5x*u|cvx`8qk!rNBV4Vu%S$86d^2#FUNQ09e)yO)hleDIbygK8BJN12-@l%1EKRl8utl2_xc3Al<2e4U<i@4=f^L`A{H4qK%We6C%n<ffkX#IGK)@c1!ew=&mO-q)eyWF;Rq2M8wY<8jw6?BAoDkZgnSL<izpN;-pw$>r8M?W`h5>IcZKc5&zB;r5o!fWQADr2?^a*Wrmcg42rq>=>wTJo<tLZ#DFs8t2iux5D7rCh~mseIEP0169~94hL&*lXK|u25QSm}rzeY(t2??ilW5AAlO!`ZClTFs$<i>0Qp|fhWg=@!;v{Q@rL7&sB@-k>3L9O<GF|0l4ag*>HG0chD~&9ArcBbCOwcGVGmLzy0V<NhGll0aYCut#Rpwb_;#imDSpozoi#9@rr;C^P4xliiqLT<ZG$7ICWDu1u8G(eT-;->7Y^uP;2@%+2_`Qm!OayjtJcA6+)*?7vDH0EuIlWwziRYO)Rh>rQ>P{e--RQ37l*zRaBpSjSRCR`Vom9jxNg~B*HZne&V$z{RIy9teSW>xH9@!)%0>KQbmLtPq?7WnM?liIui+MvePERPw26AJtm_iQ+sGz!(1<t}JJ?1XYI4R77_nn*=(jg)#bT8m-SnS0~ApxGjNoScC2e2ZU003CVWXO604(Cj~7~na}21ZV30vsaAK;|q??`9szNkc#Z-BS=`nAps81fi3LC(La`eAXA43rNh{=xchRFGQ^wGCYh-uWo6GJmX0dEIxDQ1RO+kU`S%y<%j3|6N!vn2QWD7@|6}Rj&x_ZlZ7V{<s@+y(HGm~c=skJ^AK7x8E_b$Y~hrM;2J}w6(eHyFB=BHi_CwonF@px!Rf|haQb#ak05l|8@6sn^<#l87Zr`{1%gnFtmMY2grF0C$RZ7LWE%~m6S2quMFChH+GyB@R%CM^p}i;r6I(gJFz<qBA|<nyxebMBsKdy}8kY^ojNC}r+KHWBQI>!KS4<=fB{vd=|Ad5z9wgq4gn<L62*##p&=@%7`l7BRnK^?1Q@dqWruUF#+pH)O<|rJuNQgW##mWo`^NfI_YL{gqi^z~LF$k6nCd*P5h!_k98?)g2KH1=ThJ!`7kRqj^Nn;xZn<+_P&Nwu3s>n)VLQ@WNohgP*$O?(683b0`JjlXO0B5n_tlT(flaRqEG|9;^_^Y@{C>NUAvB9qw7n%*?Z0HM4W`@uywiA*ZnR;_XG#>#3%PwUH@^^Ak0AySgZ-Es+CJ@=6m$MHIpb-};K!Vn(LC7NEPDo^AjY(zu6K5@Qlcz#Kk<nL-O(o}$nGiu5E{itkMJEFz2_nd|fhC;%F(Q(Wf)eZQi7EQDI|NvFNlzl8CuC&bY|zVj$b<yWk}1vh4JRjJfk<ZEWh{f|Tn4Xj#Q7S!%$l|gC5I|0jd4<7L*CQz(<~atq|RL&8YglVQT}X8<P2AdjaspWR=7APylrenPbHB#;i<XFHstj(0bXJ<m6;}`Q%*Dxu`|M+b0TnTPM$BVHHAV@gXra=OafJbXhU8v6^M|HuI7}<y$nR22~}q})kQ^gE=mlky|NBZr&xkaQw=APyF-a%vbRh(z%j&2G$4tV7w>p`N9>NE<sG|Bk<LAbvQZc)?paO?x}2XvakJq|`WN}gBn4&g8F=s^^2kO?onc+s4Vs7oWl69$j^WwdTWoB@9<izCPsCAd!+t;Aq<F*s87B`sL%M>oZ8MBRX#~Ye3{1}CVSU+te`+yu_XUCB`FRF)p?UDic0_~9h_`I43s0!%|LG}|LG|G=^(K*^Sd;(hrAd=YX3J=CnF<1?@h@xQfXhZO4RKr$FtmGaN0^4}0EPjq92>2naYQWu6H)BI*<csgy(vs0YT6F4YZ3)b6i5kaQVZEw*8*b}k>N}bWK<ic$91uy2NT9>+@5GaF$aePrT`o0+So}l4FOSTeFAg=UEIJvkH>UmgrXbik^wmA41UD;#1o_oPy8G;BP1Ixj6&V+gm&$Oy4*iQT?jZjsSN8nmoPFF!5Q5%sH@m82trez9E~!08|gwfks&e1D;5=nx`=6$d`@SNMq)g}x&}g}F{ULj(T~8uu8}h*Q!AME#t|5V7~18Sijma?IgsI8a2MKAm^_$agNs8}WNR?c@)D<fXqkq=2c0e=XsVazm^bE5P^L{oPeKs`y^<FnLA3Y?7L9`sHD+FvEI#7Jz9hw>kuLI4pbPhU@eu%v*_4Ykkm2Y5HVwkAV=<1+2<nrZuvcLV#vtIVph9JvuXP$^xm!%dv%n(8oPtAxCY2~yRB=Xy&ZuO`n)t+7FvM(Kglw~ZI(6!n35gt&DtVDcU^1mHuPjkwGNqkrU{vH8(Bz!KE8}6Z)c;5}IAF+EFjkL)h~upkyymF_swjzPTUO3X>2!P!P?Kjk(>Xpm%M{fZ<FmmpIvt-3nHGwFP?2*8gQ|2%>#}VL<+EI$%}Hj-m&#=|7|_Koi11nn^f=5|2rqwd5}2;4mu*3jn67G0Eu1U~nrAo2>MY6ZBBSO35Ic~0y=d)_)^iw=HJnuLKFK^<WEKcUjxs%nDWK{8JEp2+w%tkwft4`oIvg|WhB{aXnF4yI37>Ky;6`Qu*u%X;$g>@7aDfReSYzl{I$ul>N^Bn)p7?*s5>}QilF<cggiv8>d-qtkMqvwL34*cX;Eb(XgUGHnnOxY9AhJQ-)Py|eoe50nnYCyoHZJ2t+^9q28TM72By?C5z!(%CXR~d{qFD3vd7>MO2h9N+s#%<qP$nE=w)tfr-J2A2&!o6SVo+Cf%3%-))>-q)(yfga>1-I~MS!7P#mU2vRHB((264|v%PGL@<;Pk>HU%^*31y4P=E87!n)O8t+Pa2I8S$K5s9*tG#FB=BImbNNGC4P}m7QoyF{nfnZ8=~q=OlwBH`xJ`4Or{7?08b*f|s2IYS9U({ikAIx_Qy!4;$1<j-VY{I-qr490Ro;;SJ<vR;e4fl=XyA0IYKJ6x3Ss2(+Zg8`PQv;yI`VMx_EZK!L_9mq9J0NftM#bwqR~579DF;2qIp8lHhjcw*^hni133ff2IQ>!6|Pr3Vhsu4ItheHk>ibL21bq23X=K<ybHg*hYf(o~9oO{L_)hYnh#`8>!#tyf<n$GoiKL1XmAGth5kb0vmZ>15Gj*grrm6iHo@1JpuCpv&fp7EBv~Zp>Ov;AB2UnbE{Ar52zB*!Ge*jnHj7mpB$zKV9lh5*SVLLSg|@z-LTp%5zm2GRX|;q&+hy^jk7LF90q;dupymwhOobEpKg%jEG}fk>;fWIyzd0Y4n!6qybv|WYFXpaCDB2K2zXmjIMCmvnckw6#t;&n5IgXbgl?Y2j#QGsm)1bInl~RB`9_h=J~>E!}|bRB`=-^MdK=96o%Po7I+u}0z5las+}WCQz`^Rw&~SbI?hRDgcU#*Ewb0kf<e3Pu5p%(VqHSSs9N^kXk%Ff$(Dy0mOTTI2nyg7%Q{7t4I0^!xaWyY5R`!v%X-a+17i*@h@zZf*^_mI5MVCd1Itn_2udz2>tTurA?DHFEqLjmq0@voMl*IKVA+y2h<J7;Iq~Ss5J*H8qv^%YBt|o{R;&Zd(j*3=M{72gm7OHUuoMeZc|%#m5m#kHS%<WY0y4+AxI}^&$(LyjZYYa5;tgylD>&s43<CKC%9?wRY!MI$pfDioF%rQF!M;6XG(?ZHF5+0a#5lSM*f{n)FhY(ToHvd|6bzr>SQ{A`xm6s_&?*rx9BTqB#h{We;aHQ*umt*U)(MXF08)rIV6TN^-~TNji+Cjb1CTXH96(m_SpPi7oXBM$i+IruWI0xbK`Z_!iR=MnjZz{@V)<_*i)iZ5MzZJ>$zlQ*l9f(;uVB#p31#V^1>lCVr;MmH0(4_pFONl2kbh%YM9Xmg#<ED@-B?!k;v@VcmPLZ-#<KD`mc{Y88_Rm~QQTP8i$(;0U|H%uMd-q^#(D}uCk65bv&gw#MC1mu-g~ad{|RRe8u0|po`Pq?1Br?o&U$w!K{ud1qoP`JK;zV9BqIqYkd`|Yj4ne-a${Q01wiwm4p4iF9jGzMb~TO0P~W*GWO{aU25a3zq%}rPT+5&Gq7K5yn*w*9)}u?Akrgj1OtEu2rOV1!5JTMMi$|VFv5QqIm#15igulQo)vBThZg30FQ8GtgPVm6CE;VofiEeCrLS?YxWjD0tPgv1n3?KnFvh@lXIiMgHvbD}%9s0y51bN`vAY{OngB<!3*kS_S32eo42gN}<NIu84bVq{%_Xn;u`VpZE*LpCKkQ3Khwh`nU2#}))+OUn`>0+{mgaDg`kwYBUg5wa!yzW_^*6IxL?mVsJC6Vz?qm6C7G>9GD#XK$JW2abV7oZr2WR_B#djdX=1J-nYc!nStb0Uv4Ep_nbo9P^9zu&w#*&rDg9{mk&Ir?JkX`a@aCc&UkE}~ni5st*?Ho85xT}~36=+=Wk=3VF(oU4?hujZbiTdELiEEI6M;jLpZ1_@MHaqLBWi?t^GGrr~Mg#iDIZ#nwrj7OgKWS8Y=4jIoU#kcSCe+%An^!@US@K$Cd4tUF)r~RH6CbFwX0^ZdeoN;0ePO`Kn7dm=@9X<V*jeboJ${7TLNpJ#f&B_Bzp!}Jn<pc<w&{lBdzpWK3Kz7m(PS%Mv6q+oC_UmT6v(A>T0-EVnoC#W2Auc8$ySd^*wBUq7VCNaUsZ!-c4ADAx7cTLT7)TK>k;sfhx*#e+I*KbPd&0xOsKAwzJtcvR#DcN*nx#`CvI{j>d9Cf9=*)=JxdVn{&ov_Q7SN5^V}ULL#UzNI<PXidBu*4qQYmr9!=R94lgE?k18o9htg_|dk{1XR%Q{jQq@YFg$bNO~TnY(U29z;ZlTASNDY3GQ?8$kAC5FVasn@*KB?;El=e$QEk@SwjFsb4sFbYVGWV2l~>oF49nv>!sZ76I`N@sFVL1k#oN%;Z~*#@Z<@4?dKvciz3$GVpVw(eiN4Nw-XnXNi_I7e&LW7_Y7dGL^}nXOv@-lj0zEv@4>l=|w;M1j`CG%gU(ccB=@G~P2d#!EezLKho@nBv(kOtaoL#PnG6Mo9&@Tm`@>yy8TdUOeohuE7N!qT~da!g+#`Q*50N&!LaOMP?);Z#PJz4uv60&PhOzE&#9=+}J{c$S!&`NFb}ont1lY1GcQE_Of>M!j|>S+Knam5j9U=Tyx|~&+>LWEf%qJrDsazX*S=+ljjOEuBdS2O1(&AH=Gola?p%2jfVa>_QwP+G|9URguXQe?WDLjp5!5vPVnT3Hs}j_k_%5tZam4;fD77}8F-AAzQSh+vONRO28AI0bGDSH*Vvq(N%0ivU@DJOf8-=HPMDx5duB`Bo{fj*Y+7Ivo`6aCFMvrNlKFOnN#u?f4HAf4xl-WXF)-%lU0CwmEAR;N7qFyk%7PI8Czj;tDG2YKCZ)ECxWB7dF@dX!)e-$!wuv}*5v$io?3APhC1qE<#M4S2``QBW%w-_9=Wv%gvHc(KUL&$a!QKKC+?_B21_CbtNgUoF7myU4olu*#gH-tv4+Q=JNb;Nw0=>`nd5#Ac&-P6M$(at7or2QUU>6(3yw$}q_ZYvhpg7w-CN6X$TiSR!Q<u>RD@ICQ(5GTqM(TnTJYYU4?JWflt)W^l(k7tF;*mAf?3rayDQLW^Fc2x9jf3Ycppf$(2hUJI-d(sQTke;qC_rQ&(qkNwm8&XV(uK_8&yx47(g;;%AkvG6!Vpcxn+J_R<qIIvps)`-UM}!J)`nGeV>fHC0%w7QnzuFt-kP-fNzzHSysRLw49V*SCZc6t4eyB+Sfa)gLh=H=cgY(<iUxsj0wGVljvab>AHDN5^0Wcux!)3@6%h_DaDc9JcULG+{jZ2DZ!tWHqpW>hw9C3i-WD$MmZsjlQJpBbup{Sz9YxWN9X)!HEOk!3*Rm*Ei)40I4{9tldM4w5j%OJ_o<^pBK}X4*iu6EAlI`Ue7gQ?QUjECzoXC+3;3ekeFF;3$mrkIgI}yoCg5XR<iq4J1;6S{*#DJs7-uh+)?2V!yQ=c}0Vi2&mJvMIpWGq<lyS>l{y;1F-K%)%!KR}~-@{6gYbI=G~DM)D0DQBS3!;{Iz`56O^-~=>+e+4ws;xHRDiY^o-G71AlUEBT;I`;>e1x0}~M`G~cEk{D}B0R&3vVgqtB4Pxh6EE^-cu^L?-*{0bxe_;C1a6C@XLpW6_4Cb^W)GA<(4x$8<H*}d&})KZh8EAeP=Mtzd2bF1+v0=^9H8XHiXH^WLaY~%qQVJIr0Btc&8KpKK(J8B1(c|W@B}5wrv%par+RPGisV9x=KxNTT`2K<ds7rk$b@GX0==i^0!9=K0_9JPC;%4xraWa3?1V%5f(+~^(HkKOv_8;Ah{EYy2tWW%gy_))J2T2%7zNAmoFhbfWfPzgj_AxXy3q{AW$*+bDyIaNCoXvlL5mVy@bH8KgqB&KgF}M@5}e@h%xVS5S!VrmK?bJls`qq4rt6xwt|8NP{p9e>@}>e5B^NaGV8Vbz;{pNGcFRi2IiaCIs~v4<D4g!S0s_|d-t|@$ErxVK!&45>%C__`a6sG%G(6?NS=lMw)7fGIOP52>-CaN|()0#~0uoMvp-n(v6hbW096RnM2|_1{#18V$fg#m4V$(If&<mTcnQ7W?AcG043vlM1Fh!tm0g28N>Jw$s+DeJR!gF15EQP<gK)`_bm-`YPv&>202o4vWm6x^*R1frgTXI4|_ZgJHu}E}%VH7NJ`h7tUWWH=j=+Y#05*#TL5icV`fgXR`h)_81LKglR5el3F&k*5Rk_%Ju=ZFxv5Fs$=L@z{m;(T}mI+%E{%bfs1?w<gm$wYD8{Ukds&o!@UGl^vP&jld!hJNcdVN6BCN71gjRP0Lwk##|)K<_k>kn0BnfXND33ZS<_8qn;&PEK|>Mq|HM;k*zPIp3qjK{a$<iE2zLGE=q&8`)ZG_Adum*I%1~AtoZH5rX4BDA{Xh^!;DSz7PsJ?=&_qNr8e)@B8BIn^DcX(k))bt%wwyii-Oe1o%@bg`fq=eox-@TLjiMw4&n@Y~id&^P*HtMI4)G1Ig1d8dQ*nR*%xz9m(b|5<n3_b_t<;QC}jxaYC}+nD_3HLrkmxZ5fPp6|r^Ogviso+9lV|30T)f*+jGh`@$%M9QP+$zXl=F1e)l$Fv?S>^tL+DzA?&qL#B1vGo~VWGRdyZL?;$uP>DRdTKvgVr?g;+mS!3{P5wbe!fb;o#qNQ2%0;jGkrbxW^kunZiD|;RH_Ayw`%^gfW>1z$#W`+BHmC>;;zj!x1-$x`=p8en<L)TI!?q-PGng^LJiChC$&2)el|^rQvwu?Hv`3-`3E98XQM{-viN4t@IqEV`EW)^qkF)Kj%y<c>ym&w_Aa!4wdTLz~tvfe(Jzrcu5-qTn952y(S*j!&m+{)AnTmV$8=9q;d5bob^;{bgwJw8Ko!v$5prUUJO0w~jBlb@Uc=Dowt!Q5(b%9D^J+>^H;H@3ZxKSCfjCY6Kl4ISEY~Eu=h!pF!{_aH|C<B>!U3TT7i<kL>9K6M=f0-8~2MVH%c)fWcfyrgxpUR!=KQbcwkFkD+r@Mi5SuTzeY~MWc^bnMaw|%p9vlKHe1EXOYf!&p0U82gdE9V&zz3tIP!mgi9u$HSVKxWF*3r<89Bvx!Xvz9cJ?BUTD5@Zq3+nL=LsY<6x5JlO#qV0oS^KhniiDa^k4gK@7LM3{HY!`8QQ^|-e!!K5f?39a6Ax-ocaxE{LDc#Twb70r0x~}-8<vj{PwLI^>PgOpVOQF}nbM_1Pl)}2v&eDWJ(***wFH{xWRJ8a`q4!i6y5Be*lA9N_9p#pdQ92o;LMwtf-VLd3WM;i4fC(kRd4&|`UjO!;9mWNR^7#)8I4@f=IMO%VPj8!YUg~fC;FCf_EQu9-cK@x4Plevz<i2hSxnDUkNF0as?Dh~x36gmk;$Ib?3I*wZReUP6zV<@a)gVCJ$tgYOs)JDM+S~u-zC?j>AbP%7@hKQ2oU7u~Ybd<nI;Iy+D?SyTohF=Dd>SlRwI+9|6T4c|yW&&fW$y2aPsR96BH(&`>7*Os<e>hn2uTrG@tAyxhy5C)a*2e4u7moso23+ihbJ#C$*zE2p>V=Z!75HcsY4NHL7tt1J=d5Z@qZV5DzpIBQSf=*3;pdhXs2P%6(+J`y5t1{4*Xs5i76CU#ixfD_RWbI&k8h!-a)0f-m^b34+^RrC7&L>C`_d}@3Babch-EG7l!~x36El2VP#|8^KK-bm4#lY`ouU(aaDbuPp%{>e^-4fk}SKbKF@i`Kz3GrdKj{Na$xVlgJq_w=RBw!vVBBc^Hzw=GriZXR|8JUKF#YsZ5ZppMP@&{(eS3AyFPTC+9Su0(2&~&{(fm*QIPAUc@K>#_8aEC3q066(0%V(TSc+U=>`{gu-vJB;pPcNvF`-(DEu_~k@&w0KNWh6<0|}g_Cpt*V!sT?YCk#0yGhi;0P04#i^ZRqf*l}Cy%snoV23sAWg>U+Cnlj6!(A@^#1y>z*9kr*V6T^ZzbKC>MDCB`PlLqX%sh)fF@?-IPw+kDU<FVfcRuk3h5TpnCx%|^(B|7)8;~6nTqyp;B#8UF_!BwrYTaJwhnN2G$|p=Ec%I|CKo6mEy>P^eKRH+NC;mhPXE&LiEmuM&I?wUD|4#KM=5l`Jle_xUByj>ua8~|_iENkc0W2vW`YPb1@=vNq1m%n6p9TTD5X!UslMsj(kMm6q@+q){ZtFz$RYl(ApP0mc;|{uSi;yij1mrx>KX)34-BiR~>O@rjEdRt5lIuwSG_#KhWa-cHPfTH72;h0Bj{wJhE=<0_gR{$el}jXuzg+%l{Gceu|8=z!Cg9;;<)4^<-3k-)Ru{)ga^n}46eo&*mVaUjRz2`^p%Yd;ki4KzR>_gNAO$^-`J?<3Q$XN6+~-aX_X&agSNSKo97w!a{%Lf<YB_S=<Dl2v*@ye*C(@WifPdD1BI91&Kk7d*g<S+)^42)d$`Q++Fb-4L`+UWlhrlkGdA?x5f_=%%%LN_?{#E};2$a9-KQRG=SL_uccl{?Oq4?@@{U@dn(Z%{tgFpf&^`FRb$WK0ZA<5GcJxm~jzv@2;f&5qfCniv&6C8QMK?H*HkpCPYi0mf{^|Qd9x(oVVqH_7&AxvRMx+Cuy6<I>~-5c21?<HP%cL<Zv_i$bB4xKC{k<G`{doj~D7v)Ru4$+ln1c-mZM~PKtT!4=fkp3(H#S~EZ``sZ-f`rTPk<N?634axUVggnx<5>WT30SSn+C5a!5<*a%r~Q)iDBd6tMdxY1c{6}rIDsi7<f;IboZFGXgM}BK6`;ttdHJvNeq%87hd}<W0L8copnstPl+f}2Pys3%WU?DM{!dFlDNLm=Z@Q7=iO-}IhBYwYsGRH(vhmyG-bJ7W7k00f=SxGFKoI^a0wn~>Uqztgc02B`B2Z*pYyC$ND4~#DMW7zzU@sth7J(w;R_x0~pqM}r{we}Rfc^}W@&{s6Se3VMfdjj9Nc1YnB?QV}MWEz2-{lj$c%lb|&8Kpq3zn1hECR&@BL7zrC?=4gGXp7~>wzKX3s_NMa}mEV3ie*9XAvlZfL;FKSp<p+*jywp5U`9*$`eqKU$XeC2o#YYefSe6Liz(*f8a#&GXZ}Ufnov%H*yz7!L~QgB2Ypg|5*fzDHQ&%B2WbBuW~Ei7?BDAA^fWdln^Kvi$Li(>8+J6gs7Ylu)8B(E^uJFu3q54bY1hbT5{9wAMXbNN+N;F_|RY?i+{ZzgbA3oTdo+}#E0bm(Gz^=s<tBp{9i?&m;l1Ria-&$GxM(^P(mR6RRoI2U5bAdfg*CZ-(N+bh+J{^R}m<JG=g`b!;{5@SSkA0@uq1II!Pq)auKM}3v)!%3%#&SVdnKV3xb^edm^4ypom-<^;Z=rCP05yff9m0t3VN?Kj(J23KSFYt}0Lu8HCGKpauuw&ni#^=@mwot3Z)))BJ@OgQ%C_=<R@)UkpN!WA6rd!$L?4%>JPalu$|kSO$t9O#}R687QGc|5ye}s6?X-l-|5K{UD3?KS5&6kM!8x2iecYBaq7YBKLt~OVgI&FD=`RWLtW@I=$M4N9)6275>%q%y%^p#Jk;0Exg?K+s7J7Xk^rPP$>rU+pmrq3yGE5M!Sj@u7>q({63^y#ojuJS^Gx+{eHjFv;9;W6!^l#(Jv7L*#A{33dGIo7cAG=3M`fqU0AF%e$edW{z{0aGo56o@p-EjOVM|2*1LY)ZVJzjdMr4<!{3g~aFbIABc3!eYf_}C_d}C-$hYe&vC%9492-qG^`BwBbBGV~U6`;MDT$kG5`VhNV!B8mkpA7@0sv!m;Qnv7OjiR?J>~)c`23q_FD#|5_K(|=APh1xKgy480Mw69D3?7xfyCr62B4EcptRKRU(bg{Ya`vL`_%2?1I?21Gy^B?EQsG8=4vsw5__LNAT5O-dunf<&2spIz&_cj>SBgJy!?R0ey|@5ldmceuaCv;M$;EMf8<*G!u)fDW|M#jFywk8f|An?FzapA!K$~>UczcI-H-;WZ(kBDLmd^(R&T<-P=0F>x{dJx`A;oo-u>0kviqRT^be@VA_~%DZ%ZtFCXQ9S?5KD|MXcS>ECt{OYe-OE+kk5pMnJqDv#AyFbl)Z(`1_PE0~Wi&JerAz2ZLcT@c_#0Vs97!cz^AOR+9193Xio4`7{O=?RYx+6#NaMX7Tn7Po5m59JRS7e{8qWOynP%tgsD7f^+<(BEX`hs!3l{_!->2UmdY(vOXX#>Q~vf>km8*KGy`X_FE-*?A#`>J!Uwt{P8XJ%3<}RXI7$Lk6rUa{3sb?LzCdP&_33CLm)<u8c1}bI-ZnT+hA4t+y}Rt>?3~MRUt@Zulu;8`2bs!TmxJ=Rnv0PkB<4IuIQ)OBC37>8nC479xBYzL`0M=^25IVj=w8Zsm!>e`U?QUM;KJ!v#-i>R`CN^j1JM~wE{Js`}zzeq?>C!cH8^fYnjN=_%4@LtC%>sF&@qT;?13yQp^TjAGT)K_v4RH>~<Y(ADhYEV3@tzXW#C*4F1d4Zf%k`{t(Cp=0MZuc|wmZ2Oiee$n`0nc=W;F1wJOmpsBKtzKQxN`>PYZl=nXmM&P@Q#worSibq<(!3f^|*pJ!PN8}diSIrwe(Mg0+H*)=^&H9y`UK)Ik=zQ#UwHcm(`;UM&3ktWeSm?yDD4`+{_PcemQ<fh9kXlPncnq%a)ZSr3XvV*x7EWw}$1cJ;2zIt;9Gl<bPa}94BtGBCV5E<jpG#teeRJ8?Y{8>O^w`idlVVV7POj(U-J&=E@HZr*>2Hy1AFCm(Vqah6VdrL`>7TFSHq14Y-duT_pm8#o3B}hp-F~>%8==Ny7(4d`Pgcr1o^ue}0XX8{mGx6j;}1iwqL=u`#tx+T0@CkuuUAOz&CJK^&0!nv|0J^QUU#gf>+!fAyH``xr0~?H1eg7NzK|6vgG4bE-Q8q=d$tc7fJplhJI2J@;O_ah>2z;=<88M~RCU;TNjLEG@Ci5Lq%n<VqeQUn=5khZpJEO6#r$2?Y?K%5hm>@LG<)nk3J2^r3On+vk>sxmBn^j!{FHDrpOfYTpy?(+8l<OhCTqP^`+}je?{2B-hr)W;cs=A=zMiyIRe$<Pzg|37%tzmwsQdV(u=Rb+OKO(C>gay|bq0UR<y7_KcB_{PAK}4xA_wiq9oi23YI;8Co2#22$HAiYBZeSX%c1<kb4XPuy%hj2UF`HnrODuKIKb1*_jR`H_vYi|Ff>1nmHd$VzP{5MzTira$Da=<FFqY$e)cHr3bn5_-tMrY=3Y?`a8=(kZmvE_qtQlBCQDP=;K4{`y9uG2!Oz9!gqU&hG0t<+TaomeHzcT3<Tp+K;fs19@cEnUukXI_c%vOXF}|A#$$no{)m1Y$ly3l*w3g@9qFlKey$YQnW_2H>pXvip)zN2kF5vHeJ?l@e^|j=Og*!Dp_?hhU56ib!;9*YGUY_cyo!EAFM5OXRsA_mxARS@O&1_AL6@wMCU-~KOD0cr-$B)|x{_cxrKGu(4`+Q(V_dKA>qk1Cxl+GkV5Zyj*H~Y}L9*+g0xVga&KoRkxQ^-uy2EZX}^wXyD@|wp!VT_&3cA!}eo@uL5uv0)C(mZbi?K>_ci~{A>QBKd`Tl8CumXfW9t#47y(OLMPH)K<f{F~p!{nj6_1p9b2^Snv@n_To{`ZE^IRPQ&@crEf30)=Gv-)y#9eihhmBRds))<l7nVt{Dx7XEGnL0?sWx}B!=r+Oiwr&{~2p3DYwc<YtFu)qJR>;2gGgC6Jw9!J7ex;@@~KJmL<g{zTO8~J=mb%&F*<SS3K5%?MXtc!tRqaMB*Hnq;Z9zes8(e&QNVZ8U~RqR!!we1b4kD|T%iWH4aX1z1J`X4^-4dajh<Oam}yQ(^?JnF?|a?(bP*B}Obt2|ccEVf%h{s@-o)=TiX^ev=s?d1VGyqJp7bq9jon9H;_smz0L{qP<G@GX|XA5>%Lq5GZNVQ_+ke)=~Kp#LL`KPat)-tqlq5QeLukO@`_0AAJa@CU_rymcg-cn#is2nl~Bh@skdgnaO<_cpI<lzaZ>g?K2dVRtNSc1w8=(QH`$Fi|c_Y8Z{&P4KWLZM@ltziPVHTB+Ji45;~GJ|+F$98zMl9ZU&<_iMB1m#<PnX_H9_na5p9NDlAKCUKij3Gtn(3GsLQjd=O@$!yYJ2_c@4Rzh68d!$YJ7=AnA`R&IY8&f<nOn}eAivrUF8S#gnkH?LFiiHf`YB^a;l4gn>@-qEDZ!jX;NfwuE2M_vTO8Y>%?_Gpiv?+noZ?sPl*}gCqYgaq@>n{5Am|kGtR7mT+?dXMUC-?5hTVtcbTTw2Af(P&~nACRj+(}y7F^2(Z8sYG!fiQ4bee$%?lj=23d`^-!7&5KX|3)Jw(tVqYv0)?zPZ+-4m+|h<e8L;EJnmD(C~dyAP_n<t%%bt&bc5Fn1Q<6xd}F9l!wC6qHnMiLSP2j2=9W0_pt}is{M!v7-ry!Y!Jc1>U<Q-2`B)8KS*#pQ$eZ&kRJ4cfi)hF~{u5%Q^$tlNcLY_v>iy7fpbZlK!vMR2DWID*4sYb88Q}&n23}IwO(NXH*KJ<YziuMi@WXz--M-bIk$$WGY>%;l7EPqYXJyxZ##;x<li`nt{Z`?3)>|I&^oiYh95-FL+Iqf<;%5Dztzv}{ZSdC7^Zg%c2<V^<EapRD9fzfByjEXt>4Fu6g4X{(+dOq~Q`YSU>D$jP8ppc;=I6%_%?pt5kk^R=#PPxS1sioA`=Q!?O&f!i{4)#^?7hXoRA@&V43B0zh*3Nbz5*=-mKh8_%a5-Kqp7GEd?xx_*ci0v+v4UHcZMV399=y|13!hN+2AnTL<Ng(cPA!}eGtD}aD%%^mzsQCO*iD4T6)M&vFY8Xu*jdc7)$ASJfhzZZJxV9c=jh>YP!>Sil)9k;@GnnFwRbgUok3un-}C&ces<d!V;9<vY!}Mz;QJ2^b;I5doz7-sErOFG39aW#}7w1RM>7nxj%l(zD24lb05TOt9jf+Rx|{q;_kJ=>r!j@?-#h)&hcDsqJsR3?U^)a5(*Vzp{H(OVer}q%RELSBxW@lLpekxhH^*~Yhk;WzTem2X~Z`{#V7AUWh~=eD3k%P1(yOBid-+1<>EV(eY?3k>{HS2M_o;{?lk?QQpFM!uW5tljmUx<EJjhL4W6>&Gi|_9!y#??P1=G=VmLGcDnp?Exp|WzR7(3LMGAYZ(q3YXhYC2Z?Z%9-9?kEL*{aX~rsd-CJxC1V*=#j**Tc^ISHnSRFwZ}Z_!a(C#LGSp(mPQ~e`~qaq6ZSg#zBYutwN2O07FRpfo2Ekcw;GEojj`Qw0pDljekn2x))@yXeTq#r{G3a_Huj;zHWTwmhW|%u^-8&NZCu_8Pp<qF@$`X7isTHZqaNKlJQE31O6z9Dt~u-Qvl-E@N+QMXJuvA`i_9|!`&VmjSt7B^4p%~3ao%*h}}p)E^4#XO2#C|y}4mvXGFGW=`6x^JZ{$^h(V9C-)`^hkh>qQe=KplddP>$l~82|(#e(ah{M-A^646l6M=C^<bRWDLVDaqrZL{wqG6#Kjw#D|PQamlG@5PKRy8x4Eue24X(l_y5Xgu~;Mq1~rYRh0O<{*HC=x0(c&GpMX8Aw}fID@EdZ}aVQ{FV*09;EU$9|buT{r(X@S3&P79L2F2*%L#RxD_*Z#AvAe9VYs7O;bF`7_w(fKYZXUf*Zm0?Qk`EpEbKxy+=D=$Pb|)M8RS?zL?9E_e*1va}U81*q-hN~rL>nnYvKbO7bFNYl!9s-u4v632dvmyw#jnTH5^$YQ9Wjg2t(Uw+(IE0O7SZ=>uU8yfZ{A(dEh&B7M%fc_gc>YndkXmq(zj$u%AUB<59nBx!K<qxwufd8!{;Kj6!{0j}{lByZa-OXyO05nLDbq=Y^_=kCm=Tgr!5rD(o*vg0u1N}!5peCT2@by1-yXV9LKL&kjA}T7Av>ZBOx9-oXvDcS4`EH?w!vh&qYG3eQ9sVE9N5s@aVj=cg8)XuWOs5t8>hRrY<5_r_Qiy}i=VuYk#P8p9|8+<tv(^3I_+S~$<Q`kYW`3R4mE3g_<FIOea16dCx9j`N`@dr^=3|a1M<wIoaJ-Nku~gVC$w57A!~I4V`-4RsjkVFW<t?7#wzn9Jz<NrcGY)-YB_8#pXj_{#0)DI^;YZVF>hWrSdksjxUo4e_eP@r~;0cW-^j;}jG9Rr(k16C%j}Bi7pHCRB&IhNqk*+<c(b%|qk9`T``1>!EGn|%{V_ctkI5Gsw!z~SWDDq7y+wRYzvpb<#4j%Ps_|%ocpW~f2oo3c}L<{UQ_GljX`B6#O91_%cs`d77`5}-Dm)}Yv4~4V>yW62i7K9H+4n5G?v^Iy`rq$O6bD<g<EC$ope%p^|sE~9dzrzpt$A2wJo(cHC%P@g0cKS{Bl<#OJpByOrGWft~?lq4$uK@qAKR)(8`QtWy_tva`K7%-iHPqOZ@Ac-@7~-|6yb3~Pqhk4f6g|G?G_3p8HJ+{c1_P>P7^A*r+uH5|Zy<iFV-S_Ux}r;~x^K50v_>e0O<);3U}KFQv2CP|f}o?R*?efXXxvcew1K(jXc`t^;FUJu>o)R@_hkRA(UiW#6eullq(Gb4F7`@0s>ND<6|c9)4~hgSCd6wi`io_TSHuMT7>FF-jg8>z7}&R8w&SS1MH87tBOxxRuQMU8_$NTT`cSpvupQE7&F8LxN@M=(*G?jxdDI>%?M5!0noS4>#?r^*2|*|ppH(%mS!=n#tTq^J9|-J${av}L8~OWv;fq^Z$SC+|{@XIPKWXR(nS%dLZ62f12biAx<gVcF(>so0xDoN=VcQ&OaO-?bho9|7i&$-Uz$85<tg@lfW2N4kl@B{|LWBtVmr0ab>co|sh0u#nGeYTEj}u6@z;RSH5iQ-X!mUUqn#yQ5<4kf<>@1D1vH$c$dHS7tt?6w&Fw~MjZH#|wFJ0`QV!=9&FEcsAEU;H02p8-sp#G_-$)gfzY&YMv82SpUYBE~9o8c`wZ=T|5Lpbr5yMsigv}#G!@MC0}Egl6w|M)p+4GyUt57f$MJTzM1S^E(i*;*poz3t6<izMEy0yy~oJ;o_q2o*XL4$oz)*9tuf9U(6NrgVWLfhUarwnAJ+BcPJJA0u)Oz0gB5+!V>lS&E28P5}UI#H}x1o@L@cGdVl=SAUdtDpyrXllE=4vkP{U-LK~$J*)#_Bi97zfGzB#5f_at34Y$TH@(M~?dGfYvE6*iL6Wz4B3-sZ3GtUKx*i~@(`E4Z<u7eF&FqYXOL!CMRHM<@S9=wWUG;SG-2)9wv{{!Q5xNO!KDOKZ%{~6>z19l*<mc9=@RT+`Ehq5OK!xG<27Lj#DVZlk4OphVnO$Ph@FdSPf*!8*c<;C+LpTCqf52X^bBChcRP&}6eme|$n|!q2iO-%lA@upF(Ufhpl&trH$3A=|=RyUN<i!ruH%yRmJUbfvZ@%qy_cstN)?WglxbImubL(GvI28LRbfQhY*zA;Q_krr$y3LcrtGAHQ`$fj#so7wJvD{`h&7(hvwKkeW_4rJP0O4u<idX!$X&txrwd6bzyfy6@#&3FCaR{k_u=A)To`BIByNuyIxas~<mw_=vui?j2tKk^zI&2)d2+78S4`ZanL{GIx{@&+mi>(QzU-1f1ew6R)vS7e&E|c6S-_s{9eT<->@#*?Wdm#8~qbHFzVUG_KI)l$_DyS@@@3CyL_!IBV2J@HJCM5>VCN_EL&0gQ)*<yd0M9om=mkj4hKDN;{1_brCvfQTuO!sy_A@tS4!Q*wR3O+Rm?MM3Q*4Oz=D68`K4L^Jbbk$yA!QW$WuiW2)@8I*5T4}BZA@p4ssFlXMg#QgI;yXCGMbd0B#ZghOi;4Fk;{z_OZq&-Kx2-+|K|@HE?jGsC;U*T+<0$@ua@X<@><(R`&ce1gtK9}crTNgJ!FOvTRq%q4Z`OLRxcuzR!?%FHyFc7v;_C;ZriHXwO^i?^+ggBIHjb!0X!=Ni|KZ}N_%RbFTL2)DgM=qa+x%05BXBzLc%szmzt%`E_`6R(>Eq+`4b?6=WrSE8`35`ioluXd1l|=c8k<aHz~yS!%4Xkb645ZI%w)F8Ium$Bjdm#?Ja+tbOQ#naHb?wg?XT#WdjBC*)s)>)?CZs^%6o4vi%FOs#(kkcWPaV7^?d{I)mW6G#pitjZx}}n#KF^BC;r|l^|qtmoE1$F7zMWx%&O|s`|+Cw0Qb*TsO_`cXfLz~;K{pdfy8rgV4kFtART+X8jiBcWxNSThIH+%XKG{s&~Y@%7F(}7JT{)&hS7fC+UPGF-n<%#D-i70$zzO4N<PhGz-qt4tZqNCV}7y1C1cUyRmPSTRs@b+$fLOivkD|=F6(*XPLm-Md76-qtz8h?+Ngv(I;?5GcsoXeXso5T4XMZ@ma6haKh@JWICv>W!f}4szZzq28d+uEZugPBmU)a}ANxQN#Z|T#?=)?xEFl-~)KOs1AcU}xIl<*O$i!3PpcJC+8s&06p~F9DuN^qZEB(;NXPX3y5t2HXW0ZzXG=6_Q*S6)XI&T(k1)}R}q)~&Mo(Uy7xu=_#pHM;y-{^5TPk_%%du<-Tr@_kO@dsn-@|C&Xq?;kAyp;S_g~q&ZR7!X}GVKy$P1X7Pbfk<|chNWt91Lrk4hF|eL{F+W55$_L_@5{E8@KWT>Dx-@>Nt$9XjuSQh$BDt%7c~Rm5GzCh8D?~8QAsF>oyQ7{t#D+!?|*AZ#3}p`5l9u2+7Nn5!^oE?e2bszjj~4p1QHBVD>(2v1x8*H4q~*@osK5)_?tQaaDkCt@{woH}S_(Iy@=7O`3*$L~CT%z(^tg+J)UwYGiB^aGRZG;An=U@>=){>*ec?C@}_>tMV(6>WYB2Ykwi|yfQHBq9ukd%*QMU3(e3D?+}3~(d14~#}4&S{5knTP{B_$9=+{Fi``zGG}CB?8}ukDH6RIVLc&9?pAn1YK(;!)x_31nf!=ac%aLuiU2Q3?3Sl+Ca38CkHVN&eN=_PlCVIe9MPu`3oNm1xSd9+wRvwMu9XnKXHTQUr?`}zDLwuq?Jq}|X;p%SFN!02*V;=!x69Z<bEJOoyZ9n7n5E^}#Pln*x&}1fD2+2o~-<3nL`A;hp?<mLZc9j0W&}H9<W~x8ymhXL*$!N9gqWZS{E@6)pcyh8D`g6VIuRK0i4sCp&gJD{K%$9#iZC7rUcYNBN7be-=;Rl<=N)IUCfm+kipjI2t2mjj77882Y(Ntr-WwtW&PqOc;)IR%AA3kR1*Mk*CmIrL~U&W5MEFU5l?LK|n5OH-nc^721zaiBJqv`hPp9Xk%ZB$#r>s@avrysExN6l)2-QH*EJBw}77YGT*%7A`N5nqb3vN;S@{8vV#|CSMF_ivVB^J#+hn!V-Eu8To*C+=#RuN1!h#(wpC><Qm0{m?4@5fUQ%8n)uJP;J4^#ACX#(I}II-tEkDWEyv*j)K?ArPkv%QtVarmt}oG<I{iGFKGkc^D;S}TA^(auiHyX>_0@tQ;PKQP=#;&-JeGx@#~+cB{=Qq@n!fykEbevdD4Z_LPjh+Jz)HIl_mT6om#p*D*Rg}S<F8UD*5det-4Uf@$xX=<y9;H_j-eapJM`h(an~E3DhfBrWn7V4=^}nIG}@gGW$8`)d?P2cRmh9U+(%rk}<##lJpzO_i@xGcJ(&sUCWBvRetC#3!se}O3;c@AKuIg4NeuuD{hfe*1{(=RFYV}>DXz#N=!}f{3y%)@WZdsy@{a<p%74CA_a5(F6vS2*FLs-=5{mD3+v|2QQ0Ib^&6wH{)1|9QijRS3MAEH`n3+w<KsN@+qxert8~S;z5gjq{0&7;2${FFN_|ds|DZuE?qNxBd;3_uDw0E*3Ju+GY<NGj3b=NaWc0c4U6bR<0B$lj$!LjIP8IzbA@s1sP2@miek3tioD7BpFu**!!(b-@+o|gT${l(Q19vW$9T{)*zZ!gthT<jR?Ye0_E=3@&Lm85K)?jO@&&;}45>N_i;{n7A@r|DEsxNvmuI+*FJpRDW{D7^bGwVn`E&D*efn8O1u_MF+(fAgq$5Nes&G-iXFAvlid<N=b5+omt0YWb&62lr9|4`xigA{Qf91C><1+rFg2rummhKg~(tB}>G8g?27-NSZMDL#f!YZt)VSihjB4^3qocuj@%jN*%I1EqW>Bn<Jih8rIlqNZE*<r#-dv9{g3J*d@`J~b->_VNdIugY~t*i6#NVaeZ14xdrF`nG89@Y0yKwt?)&v$m}JMPgx1;-4!(1e&OA8}TlPA8Rj^gnUp1VkucONN5O3dH`q^%&MKlGc+WK^WA<mdVSEV;r28@Y^#a4nA@Fa6JLa<y=DIU)v|-fSG@Pg1<99{V`ig~GegWJBy<iN()o*7UG%bv5aopM){7%UZ1<uin$^&8Ec-K=9Ke4oLiBB=ptp8Hft~iF0)Be;A92yADQfbL)Jeli_3g6|Au;xlVCB3X&&=<PNl`W}nmv-Y0d2eJ#C}Hanb>`3N1LQR=quIm{(elj^vJwnx}q8+@;zW^I=(jqBKbN1T6MfZ2d2+SY>{D$%S^#4(Q;VQ<y~u243mWeJB(Fm8>qHoKuiQb>7ch^HBcr3&GmfdFwhIvBh6U$;FhbCWk1vN_1QPEzuS;>-H_GN2FHyjkv}~Ijt8+a@Y0B#HT&JsG^G2~QmrPdHKLpW%Njh96IIc2mc^W&e(2w3Vz=RP^SF&*{0DYNe%9?C)5q`t6Z`ch+&wM^=E)vF_n}y$O_}}>rWEmf;kD39gkt(rfQXjXK3{Px?&#8Pa0h1J(Yz0@&|(Ro-cl!PwFBb6%?6!Swm!BXUinGsg_iPdG{tz%DCd<s>2j&Me{4Tu#5lWx>S8F-Mh;fMPwh|;U#w<1&Z>iQ8lYMob;aFlt0O+=c`0@)%AMFIP@oOTR>btY|G5d&hisjsm1fwR9W^}*BQlV<b>JUF!_6<P;-@~=;_TmLg!{*ewOnZPnRm0o-;LmqBK}dutKzrgC!8~sl`S7-1>)Oga~$*E?wrkG7A9Z2a?65s^)yledYLVl!+SBjp5VVDC(y7#V89b4-iB~zbO@$Xpmq<yjA(q!zDqoCP9XkIA`SU%%G6CK@PcPAw&nR$s+SpLE6+#1*wKWkJ!r|d9PjDmxf_AHG(8;>p8=ZwF3go&2&Je884I^Rx$RXrEQL@%rgb2vUXhajTgNvrahcd!hWPOX%}xU~ddMqiv<h|t?aoyvw!T?fh0t(_H@*#yah~h#?N#t&!`AtM{-r<7;%Nheh@B6uBm6!#awX-4Cj20f$Lj~SVWa@}{@egk?v`f8@Zx+cbO4Gq-?xFEcmYUr^o1RA^#_O{lF;QEF>Ths@sY93l3h1BmW)Fr`PhECsy*$uMY~boLLXPuRFZlxm8VT_Rt&Xs&#jJ(J__k4z;8b%upBJRbES!h{Yxk`K=aN%v0H}qCT6M>VzX%Z<9ZWT?j&XPkgrE!tP}%UDBN$|$_@09pK@xWmmFnlUu!+X&&PpWv4_pRu~;^7@O2l;y{(gbsuJRrUumjXt)Vv>Mv7!xOpxL_6~OS-Mo*Sk1H5xytAM*2+~Nj12dt)mo-Ee(q(~8vP_U)vh1xYxHLMrXXkVWP>oje0z`<>K`L2D2d&}yh5Q5s*{HkIUwbJA=*DPRY6`b6X$F^STNF(|+<5OYslVx-iGT|-oshzfa+ujeGo2_p=`J&nlp$G;RpP@=`dtHY+@>gEl;DD~f#S1;P@^v%9`(*{8dE>WkHJdEW5a`J%Um>zQ5_FxQgVqbXnoM@~UrP+D!D7sa$=_!%M(LIOckzgj0xy0cRX{nRSoEa~f%tiIp?$@k2HHaCSF{Cq3v5H_$urG5>#4oAtL`JpYjT8lakZg;q_q#B-Ze^m4P`$^ht?}BxL>-Q;p#J|{rnu`YK{NuB_}fsE293OkL0QSLcCl+HUr$eaE=ibf5S<Q&%ZrqOJBWqu2#6#K&2RpYV)5ZN7i7GHMH>fdF%U4yt_u;TIxyFAE67I^t%LTk$un;a`V<ek;Z`n$r?P}KCG`^A_+f+V#^OXvE0t_vcJPy+q!WD+l%Y6nR+H2UH9%|01BHt@d9-M=@xo3T5N*&LrK%0I=2lXRmME3Sayt5JKm_0J#zEi$RQ*KRAnF(!9Y*TbG){qIUGH8S0CD{uzfLK6(S9$d%#=5_mng(v$m%jc{S)bph{{N!3nmU+g{@FcvDY~Qt<PttJZ_e2s=RSwJRndB@KNqOU+?8NWMm#ThW24_Mv<jZ+G>ddOleT)$?zqRrQgZ=LvDXdVFm~g=7eoB>!vVRSLBx8O**lBa?Se)*$vd-R&y3m{z(Vc6HOop+|U3X8M*4MlqzK$1wP7En{r>ub??-QiT<peeS7f8EM{4OWSGn25^1to=Ekc?7aM5*M`M#nKt#n<Pq<Kaw4og3(J+X`PohC;o5H^u@)C;q2FmV$USY}wPF5a8k_0wYaAuqlLM_;ie{+#;ro!7oZRVY>~mgo<OQ&M`qGBb?+&k%ohtv(4^0cfWT*UdO<u|&Iitf}C-!|)5gsP;JvpxVt$^jAkQnt73o<k<wfV?|<kae?U-ZqFSNUP>ibR@)5q3N`<n5Ko6D>9}LJzLfpdTb-5N@w?i{_z3T=>ZF2bJ}g*tpsHMK1i)xb27LhcPV03dQ{Vi^n4mH`noYcU4E9%4Dq;vvmm;{oe#a#5>ydC#mJXvi>V=yPTG>2cCqe2Y$*vqeQmWT*u-ezxJ4GCs(U%D_giVr6P?{tDI})%^+#nNs&3q5vN+mKDIt4PP%VQJkS41mOpr-$Awu!@@~A+hMNcCmCZs|bq1#7@p|jqb_!(uj`dQ0a3mj)D%Sih@dpz5>zc-SwXnReW-CYTfrOD02WJU36NHt|#G+`sqn!23$1G<2MO>uqUNQLG{@U)fP>4>Sa3mM=8=e(!%n}~V55_r_b=cFh(!euzd`y#wVEH+?%9PdTdU35bHpLKis@v;E@u;U}nS-7jj_&p3Yj13f9Bs=<vL!rLTe@;h;^bG;RdI_&taztA(&_f1+g@=~>_I9OzY#5}519qgJvn#D#Q^u!xWgdpJs4ZP_#z6J4bmi$*T3FgFQ;7S{<mm1B=KAA3^vKF+Kqf%o6SSAPd~sT*xo1S`|UMeDdAT%o4(|6>>Mx>AIa!dE+_m(k0Z3!$|-*OffBIt^V1<V@|^5cK!o-oiLg<O<#N{_grA6m{<+R&QhFX13o{uvZy5r5U(jb<5gVI9s6pSH#0H$$tDoa_K>eI#_Y`phE_~P0R{7Esj@e_WdITx+{A~0-imm*QSK9Ip-B90T&aZD3E2MXkZC+kJ*74UqU_FYm>)Mz0?X#8@c0uF-nRz{~v>E$}f4N<E;<I##ZeG;gRQI8MzE^BihqY-l-^ERL2-LUVQElPdzsFXSdw+hmU5{}e`S055eHN*PzQ!2HsR;!vLo>DaGkLqkTn<p%)TX`CW~BdCTm8eU_BBpc^7Gejx*pm@AL{wpE+<`8zXw3wE_Qk<P)h)z`*~-SRV-S*igZ=eLfC1g5dQ1#&=1X;nZe!UNJ+BE8!0@gJ|=Q~l0LajjPILUMT@QuG^dbAO81A@Y;f11t}ij{h&40Rg75=d_A|;}$J*muMl5pJHslobR}_NLjnpiL?R4l{t21q-mG4r@HrL9Pp0gy@iqjP}6B1$ZCjI*Gx#YsXlSBJhpP|_Ndi0o=R}~D5JDc}-TfY*7#O?h?tt^*)1p5=>Hs2y@m+#!<=N~JX#H#`7ud1!??*qn@?Q86>J`{3Tyo&KJFacY&L6kyWLo@@AYc~&OWrO~KwApw6nbhQ`^w<GAExZQTdVKqx)}QnjiXx+Wn&)X6NYPWr;m%+{T?_szXr{orJ-;?DE*`3pmw8_MNNod#zrxVoM_hOVpzGi}(Tm@}ogN>U$OtBrdNLb=q>qW7@h6+~EQUI-WcTSNrj~E2f$etZf5mR3w8lO*FhrlK;uq2dK_tPg!rmg5Nvh7rN}uD~ZLD`NN*Qo~(8T})Hc3XVVH8f_jecOga@-W?H>B-O=7gtw`*Z!Fzu<Kg$>fNC*;m7lsH@FZDWCSyjU|Z>+Y<fV5`5Lu^UC9+p7~wkfUQ2S+iD`(ZRkn(%R2^**4JU`v$r=&r$7=AZGr{J%e{fp$#+RYZAPHgEr{=>7M}RXr?eH1KeS39Ufl2f)PrCrGu5zf`mJY+vFfJw{B?b!J@`{&Jn?Jp>gC}enRNxwFJXuBdlQ?z4_A1d`+lpTpMz1YlxhacYaIOSK1<ozbEh7dbsAU4AxWR$Re`QDRX@!lV$XH;qJGXkFh1Z$Pxu>=`}8p!Xk)*YuTzi!65TgY9PN*>$PAReu^%6%bM4-ql(clR+U+5UXJI*v!xx~HM~`2}HQ-CH`EB^^_7MyY*$EvMKkR>H@UUVj+EDi9K^knYVzZ$XiifUiq28<zpAI|fgrqS-10ivb-QMCQFfj^a@V33g5OK34@AdLrICtpa#d(-v-}E42(W>c=ig!66#Ksl1G3Z0>D!wGINf%r3+D+}D7}f4jVbQv&0bbaba_!gS1dE&h_K%+`2r~_(&_kq<!OhpRB%<U5d;UzD?9RdBJIFos=7&xd#KwUD_Q3Oe{4tgOEQR`wrP@ht=k(uz`coYia<4xLP|kn*>IJaclO)<IUfkV(<za2V>1pi+#?*K34K6$28$$j?uVnX&MmIT8KUUhTU(D&M(j~^<Pe_qU;y|Gq9%X&3zJ;&oy#}dFT#uDAC=-uoOTiHbk^>w&tKVV)&+*f}u|?xZ>FIS8QA#g}pNv6bgJXCjl;(3y5-qlI04-P4nvh!RvEb~5IPOI5*~c%EGdvg}arf#MGHUuBmS!<d?e-Jju(+9a!1gUZ<|0Zk7F*p&epvl&=b!6OA%tVyCm-Id2d|jbNWp6%y29&Rjp6x7zT^(|LYD^G8Fkv}<L&Odnm&fwO{;9na&ttJ_-lDCwwNDcSI?PdX<UA)UJtKk@3&Y7(I;Aagd6ESmV3Is#wvavjIwL=G|IkJahyC(b!pQI-#i)(d7V%LV(XKFtPk>6lAgzd#M|A+P+rvLdb>Ur@z;_FH;EZ6{)SSpHf<-sQ@ng!hwou~oCsWHOcD&^^?E<B(_a$vd%d#$80ybbq@kCt*M~)}bPz@w_pKY^(nU-fTioG?R{16!g)q)(J`sV&M#CrkcjOY~AnxrU(Tc1dwi)%h<I8|ycb+XK?+3=rB<`9rmibfF+l>~6?6KawHc>K~<jd5L`SJBrqj1j$wM6did5}D+)p73mJ-x)xU>wgaGJ9Xjmk<hQK1!Dwn}_gyao!Iq+IMhzlPkrtct`Z@Gk7Ytq*yRs#AyBdJJ*tWzl|H;x=8*SB_|)@I7K7cN5T(tt$kO4&D&)ja|wpYV;awqkT*y^?|BRT6Rbikv7k)~d?BlC69x%xG9Y$S`P|-&x(jXf6H#ndLSf~X^7GG3@wwrDxXV3X53n6HYZ>}!wm1#kmhJ-+x)6JXOfV)C=iH=>Vb9^3{M$Y5vR$P@Vi?f;d>!<rJ^a_EQJlX`GpW~NCY^fCHygRb%@J?qcRPP?J_!ZY#&EVLnWrs{qqw)H-K+*Ww>m+VlZ+hNCKM#s@-(Qf4NJ$L#isO4V)5^6>?*dW#g^+rcHNy9-(T-@WX|8IjbqpHK(onpwX#@`v{jMpp`f0pBT645tBIMq>gYGQuoB27``5lkMp7PbxNu>=G9x8@`-Zml1?<g!6AiMWD!JD5c#XM$d_Vkp43c&JOF3s^jpNuPA+uGRX3UERNJCRdR5WZQ>wau|)o%AzlXkQ?dN1xs5WFCB)Wk;UKVmotmHaAM?irJ}{n>T!5N6*PMpZJkxsn>@p2z%>(A`mDHp$QoRyv0skcKONDf}`9x#Ht3M?dZF+tVD$^Q*eHh(`46LBG{AkK0DMCpLAA=3>j-;u$Kn*=kiF;|NokvyH`fQ`^7gbZ|3JxjcB!g>#`zI*(E5=LlPD|7b0o#tRjQ%6HXit%|XQf7l-mcbQ!w+y}WryRhgbqh;`v%RTOPl7IKM$(1TKKV?8l;X2Z7E&WQY_>ImME%Bw&<2_XLXX}MTnl6%z3}9MY)_qO27VB&%2@pH&My`F=srF{Y<6Cdt7)5ifHmcH9K?j2)hjGkUE;aP_psm&IcSnh>c9s(HW<z2PJv&Wrj3ySozoW8PHU#n@ejml_@>sYg?zKjyu|!u2z}WGga_OyNt2x?MpGR8g`SFqNu#`)2xU596*~YJu?{dCql&%W?dk$#r4v0q|pAXg0y0a9L6YUC{&-B}RIqSHofqqL;E2-K>D7KNFAt!}+eQedm&5_T>4*5vFBQ?Ln6{-FGf_EmOlF-eFpn?a2&i!;#qSpfTR)?&DH|t{AO7Hyton2|OvbwVVEnbImD62q4rEoyS0T6IPgb#``IO1|1K>h6}39jMYd+mMd+%H`s7&=LJr#pGNjV`cSGA$D=o?ioJEDU_9)djwna%#F+-lm)#DNHdZfU@YG{2h2CVr%lTFt!y6G;kclMwO+=R|Ez$m0_f*a3Fqc6Zi@N7y@D5rkZl&X&R0s0d&EeqMdCpbOBhqNMPF?QYRtSdCR-}`ttpWccx>WKZi~t@aBegyHl$IHOO7M?-}H~yYFyaT6h>Ha+m7-eOKCy;Q@CS?rzm#E*g#HqD%ouY_cF0^Wu^lwv@ELZ4D<`WaGfD0oDW{*|P>>4Qc@0rrdG_$X{7NkkYpX#FC7!0Z>H2bWe-5aUk5o>MtV$^^LNb<hT!Gajji`1XDG=oT|5V#qELyrX!3TEoEP5P7=0i>)M9Ea(8*hyR2A;Tj-_KS!&AQyE6&DTl3coH9`U>awq)AVxdqSO1lg?Eg{D><g12n4&QQL1>(qTWv`)(zvaGvYc&s|+3jq=Z^gC99Rq9FHz>B-0vy-{dIy+pXZO}9zGna{U<E!E>;t?KgbpHieUgC5)3IT?GKk#GYx#W{m}ik2S{df*Yu;Hn7g(VQtXtD%k-whr4?jYK^={xHrhwAEc&Fpqo;NhgcBiVwjaaBxg^3(MyyGJU<`XZxBXV+b<0>Z9T7^)BeURYcD{WW9>7eKJ>oO`O^Vzbp^rMM%w|Rqjc^YF5Q4OnAV?ZXW2@a3~4+vEN1T@O*!Z|D(;rk$%ia=NZJV%7f3YNkcU?VmSKpe}x_j(YxEi~R_S7Gd$lgrtRcAS1=&|r2$nXaz4K)4e8nUh!h3MVmhh&njdVA}r%LiMs(dQ_?NtI?)59^~q2+vp#rlfpHb<lD8}4QMhj8;-JU6nF`kRk%a<Mp0*32npKR;Ie6AJ*g-JQcG?L0!19&Z6)6b@%>)+!Ru~Hnb@`c4yE+UkPN=SzQh;ur{crAzA|WW!Rf%<C8`JdVF$TKwMW2wM9!8DeZkn~GnbT|AO|Q5VsfW<;4<ta-GVvln#E?YSgAN41vJS-^`dcaP+_8Thp6@t<hkj3q)xpN_Ww>Grt)1f>InvCH+#O3vXhnfonQ*FjWdMZf+%H=uC81V3tb8`2r1pe(lm20u=w1r-WRYs0^G4kzGxt3l`JgRz+ntuNEq8f1XW&=5$Y6|2#EmPPXYHViTlVxl*1t%c0173(2;MGx{bODx6!e80Th^>*~>pL@9=uPPz5ufj(FfBGU}8ud|z2X4C#zKesneP-b5VqXqb33=_{DfwXysQ_!Xw9T7b!>3+BTJzzoo$U#tj**JknxYguS*17+#@O!{5GR*i{!9WG!d<`(@Hsnt8h>$jQCMmCwJUC#S0x2)^HJLW+bdKE(UaD3oE6mSj#lozo3y9}6&`d??d*CW6XcVADybH(Mx@ki67juQo97s7N^|5#C&kRjgXOuDdJ`_b%=;$UE=v%#wkXIk>n<qY3B!aPzF7=_jgyt2{<79`L@a$p<MnVh%*8p<iTve^^Su86Pp>>JPen+#>*B}M%DEe>UTfl8L~oB6e0RC{aHt|szV2y)MW7sV+sOv)Wr^Bekui1HVJ=J~^kQWrpIzEyc_q<>?m?mx8lGm-cCmJJ|RxL~rS$O_NWcI~9CQuC#ZFAnS3-gQeko~Y%V#)Ic^j7m{hf*U`X4%Rv5SCc|7-!Z9=jYe0u&+eCa)0N7{hlxbg*pB-PpK+MAU{`lDoo`nseKdnWlhbvmx|4TZFsK^GjH&uuA6pXwXvz+5SS6}_ds5MHp5D}GDcpwpaG}1RY4*+v==Ob?WVmDpL~M(4YE^S{Zt%FPrkq)%0{T0C0XFQOT^)5iRDcXsctLEyA|Vy3#&>Q$(tRhkvfr1VcNZgLtM3MnO6q_?V3rNSe<SWiPu}xEJ_-6K4E6-%FM1k3yhv;s|GGhcJ^b?T0#f?%GxP|9AIFd+|Gbg-1S`M_T+}K@)H3zVqnV&`R5l}~O)3}&`D1{FBsfo{D#9*f(UMF|4QI&Tu>Eu0r&%G*`$^BuSb5+VI7C~le|Gxsmv-%EaXPU|{M*CuQkob4$in%NkHeG4t>}_oSqc0DQEL_QR@#x#I9|54Sa9Rvg!lksaLA!4BZ%IVwWX7EHjbsr21w#GiZM9RHWSHI7|JA%q|Q2NwJEd$W2_e6MvzQGBhzpTspr6OE~WY3$N8TL{WWh7uy$iXMC{I##J))&W$SDJKPnYOsGSk)e3P-7VL!(5!DD?Q#-^tAidXYKNix|FUI<D_M94E6H6WS$lP5i=H7kD4B<xVEF4LWQM>FGnYe4O_T7Z@c5#6e@;>EI-2Qcwbi!w`kfvgDYQvxW?ya|F#CV>n4Yu~pZziAn|>ucF?-Nw33FRA0}0tlv>d2qRi!n;z%nkzbiv<zAX;a4p?!lkGd-$`iLzpXdAgt^y4UytC!V9IX%SK?^mdx`nX(E7XF*NV}nFZZ1@$A2<Oh7ivasuXV<$3aWxXp$b$teA2tQd1Zrxp(iU!^FqXcg~9%V1qW_tMgEbyv-L8)*#Off5Dyfm=?4fHhS2?!jnFbt3=V4tDQ4xLb(!=n}Qt2$vr<6(b9(2iccpdGlpxZ2Ll)dtt3RXv}vH4Sg0o8<X)1e;Jr=G?u=q>=&6!m*_r3wklY<D{8+62Yl6mqy|l6as>y%9G%2t90S$5;SReHcJ;os_x{1nS_-O?-s#u&vY-i1li$mqJGAJym(V4M0U$~FJ62nO;&CTPXN@WTx3|F<$dQ^_HDi8q(;X6*V(39~zun4DP+-#^WEG*I#%(1RN%}G6vO(J*R^hvO@Fz7lJ7($}>gkerq3eV^|g_E{LVePR3NO<eI*%RiI`$^u~HC_t*Anf!-@a;}phn&tRJhwlm7Q-=7eiT=-&)Sa~ABfXc4VE_RF2O=Nl`=0uAECk_G+Qf=fDfW4v929Bqf0mjDr(su1K2WHgmcz+ry+7#`9lr<q7~q>*L^*_?&X3iV3ufBzCFEKv!4Tw|Hks}36=G9`nljaHPW);bM@ifW8~x4_O6R1=!{0HNF^<&oVbFu`-*)p<-T}#GQ}G7UwR;3V1eVx9e}Hr84gfY3ZkOkfM?WBkAXrQuHQ+C#;%*+SWW^PS44Rvz0*ozbxMfze0z+&APa)5$+{fpcN^qSLf15i($cW5mCXZxa)d*_$wUsbbqWkz7>I#ZuA{y0|1!%ekUIL7<Fg-(29F<yFq3+WOgPCjbiuo5nK`t71z6o~MWqrY6txAwaAHTQ8*q>Q<v$V#6#1Vxg{Fls$2k))8QX+Wr@`p1YiO|f&2wJzoy9*_oFR6&pvA`H)&AxQSH#V4g!Et@4)O$l1Z-c#5!ngw`8y!;Vw=QY^G*PXdirZs{8hrRj8H?GY!m}xaB{Ei>lnixb9UxMv|+?NLiXOWEdCDeZld5}y^Pjm(7{dfA3Ol-gjEFlX117N-%OTILsW*#It6C~pwq<A*jXdve<xU_LoQ89S&c2nV>8C?P~ZGcoJR*l?+*5k!7}{@vg4EBXxT!Z`R6pE0Os1n7>i`VL@lylqA1_1hj60J|6ga6(68F<7xD9YYGjoLu?Ac}%!#l+L*Y98DO`}rqXb*-!t%&GmR8RVB3tD4-!a%v1w%;2Vlr;V8=7Ab*l@a!#P38%7!_f;r0nW!y)~R3S+ohftAPP)bm5)?(6V(l$8Vg$88!UQg8fi(umsie(TrdAzb488=k8T$DevM2|1w91?#`|T!aTod6yJdAS}cUYD4)v2V=jSZ4|e`DBT_Oj{Lm<6%8ev(*F2U*HHkowDV1TNig&%6T70eBo$RWJG400?%T6JN1rZ~-0o~exc)Bg`0b$2jx)YiLDX9{W!~r3KFgZ~CBz?a|8T1rP5R8T$o8<;07$_R=6wUr9j~L>l>Y;@gLY0T#48e>(KZg<)F-E&oYB2En%6^%nU_gJF&^$<m=vU<0Mb!d6Lxsc3*QoE%*XyNTU|onmzKM?qh8RBJ0A0o8tAI~ZD|STq^{(;L$Mqe9VP+i(4UqO_3+QyBkM5?_QuG2#s>Pu5v_a+KtS77(fTe29;gOrIgj3YSvC5$I1ktGc0Z{^s8xS8!2<=p{Y-%`Si4u3w7Kcm5)uTaLo|uoL;SAQWl)0lc?AhT6zI&CiblSw*9WJ-Fob4_&%?tS>+7e}%N)u0))N9vrT2TY{%89i$wdfj|nnZ6($H<l}EZ#TGLL*w{q?&vgVr9UeZqa!Qd)Ztr$mutEeB4_K^|(wFYC<@sp8im|iIIq)%`Zd{_y(e%!Z7Ri43<<8IFkaMvf``9Igt7&vI=d^h~Y8qpz5;p7k*<5cl<d&tYT*4(+~I~xYRL5YGj63Nv4K4IbX>ST4~6S^3eTi<$>k4s306_1q**QaQ@L$wxHv0m{5T<(nWIZgl~ssuDw$4FZFKUu1ISUu3#Adh-BUm(?iOohIJ4Dv4IhPqmBfBuTvO*4V^ixMqnYV+M2EXT!o5*&EH(9s^+67zWQbz$X3pLBnDLe<+ZZI_)d?vGn%m0E`|`}+qrwl!c*4)u=o#6p`NR?Ji*5aFyh&fwG7gI1c7Rw9tUZtH}DrXjuz*`_#W#6cGXx*=8qy8dtqbGm{A=USdGEGEW5d$3oJiM<&?<UO`=EgFTMB}<x5iqbbsf4{x-gU;~7p7g6Q<izy%V-Du2C+jzSx!vPo_5mcj;A4``@EwH9}wCLD7kis;Ct34hB!k60F0NV*+AvGSvM?JC8T&~M4~TINqeF%Daafg$E{pRldrs9^@|l7Ap*hC*5JwrU@0=t7(7yY71yO3uM1Qv0T&Xu%>PVuw%NL3_uN`824m8cE&~=F@x;+G0TA7*Q{_g>6#2;FAqeej~dIYkG)H^B!D3*3-^VPyv(YMEkkVsLEJcRNH#f&DPn}{>UeU)YTU6kFee9x-6E<GDS5M5D7xc93EzgynRfWl-2P!iQY)mdAYIOicVubS)DLEAj;F)O74N6`c_5A);-}qlcQ;U&?j`Qaj2^C&=?HZnQS-<o3`dc6L{A`xW+pM9Eg(x#$~oIA+>_Ls}D6gDFuZ?u@P%HqKl(Z0}Vu;P{k`I<<v%aPaH+yXu#~z2=Mw2cSoMg^ER#lXN@ERt&Ne{v~&<=%#&{vgVC(3$?AD89MUBdv=<F@xL)6Fy-MsFV#|P<7RJ!+Q%k&~9fMpSU&TkM5zYyi7nij~cV-$H(#^ExvspA>T}^IxHU-&y#Mzi}s-8pelVwguI?!5UTIA2gG7oG-P-<TvA5MF}uH-(?j{;GkoK8a8rZ-h-by<gCr!W59>+NZ~)V9mH@yz4HjUBFiH>Rz(L$6q{I#x8i;ijS7rM-7j7mN{i8{zb^tHUEJ3cQ1BTTV1_Q=?ugq{g<L7pL8{C5i334Avv#8y{mBbvJu>h_vD)R$>%-T6D>jbIW#`%p<SXF54y7>J_UEx>pEr-5dQ>=t_OijJ$TGT(Fk{A$+ol`-*dtT)sVd7T{6EYvSsmumP<6Y@>QJk%4h-MN4V9Fg&>ChK%5_NFmHuEi_QWFUdcL^&tw>-P(Meu$3SV**`{=siScO!z7&hO7l7UdSqc<$B&@29mivcVC0M-;fa{aR?YQVjc6)ZIP$H&TDZ-5SPnlB<V|~kOE(aRlh26<PnX7`IJt(Ay7)T%a>zD3M!lHSA%9kro2VPf5Uc*6bkEKW{xQXZxzp<gGZ}zc=l7GwdMDB{b$?{wUo?PFfqmu;m)tKA%)q#aM};J#=+F`CcjacR4@^)y0Q7@J=}4L=dY66Jl}3e6gu%yFdj)G*GzJKsiSh!ag%gjVZcW)`Y6(=MaWl?}a)lf)=u=vMmJKYmy=tSa(d1EW2ayq*9ay0oEO(7ciyMb`r!TD-OB>}fMR*J2tj5lM1Ha%3Sc0-h^SKzlO#RB8+j=rda$34D=5M{q8H7B|oUlz~K~yfJAI7P&QozeYWAJHt!LqZ$Inrrq3{W-u1iXT{C(H*RGDLIfXoQ~HPG4IHt6;^pT3JeqJ8r$v39ML0*=&Y-4A10@%(cY*B<3g+X1?z*1I|zir(qf_A{iQWVVZT$3BcOq0StGKg2LLeFr|Nn$E^bvuS3jYe!}<%s<mn(DQx3~AUx|`2?v}=vnlPMhhxq-t}UXOAXk}JyAWRzsk69UQKPgvRwJ`fgkb1>2RM*28JcddVF;m!OPiR!1uu$BMJZen(nV%n3!m9h2(XcD!0(RoLm#J*8d&5g&X|Q_8%Js&EtTpP%A}9GfzXn-20+h)KZ&yf1QN9V1QN(tE_vr{?kp5x_w&+J>b1hB$m5K9t`<aC-ZG;VARFa0m5@yTycSGP0x(p?DN!y&kS#_WK&|bHQY10Lu-tVsXcGx@Ha=2GbS4Z9G73y~K<cU_?<{s7$iK(3+GsAnwlNU-|KIaJCeoiU"

# ---------------------------------------------------------------- atlas ---

_atlas = None
_blob = None


def _load_atlas():
    global _atlas, _blob
    if _atlas is not None:
        return _atlas
    raw = zlib.decompress(base64.b85decode(ATLAS_B85.encode("ascii")))
    _atlas = json.loads(raw.decode("utf-8"))
    _blob = base64.b85decode(_atlas["blob"].encode("ascii"))
    return _atlas


def _face(face):
    return _load_atlas()["faces"][face]


def text_width(face, s):
    f = _face(face)
    w = 0
    for ch in s:
        g = f["glyphs"].get(ch)
        if g is None:
            raise ValueError("char %r missing from face %s" % (ch, face))
        w += g[4]
    return w


def wrap_text(face, s, maxw):
    """Greedy word wrap; returns a list of lines. Raises OverflowError if a
    single word is wider than maxw."""
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        cand = word if not cur else cur + " " + word
        if text_width(face, cand) <= maxw:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            if text_width(face, word) > maxw:
                raise OverflowError("word %r too wide for %s @ %dpx"
                                    % (word, face, maxw))
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(face, s, maxw, maxlines):
    lines = wrap_text(face, s, maxw)
    if len(lines) > maxlines:
        raise OverflowError("text %r needs %d lines in %s (max %d)"
                            % (s, len(lines), face, maxlines))
    return lines


# ------------------------------------------------------------- page -----
# One renderer for both paths: all drawing happens on an RGB bytearray
# buffer, all text is blitted from the embedded atlas (so Pillow and
# stdlib produce identical pixels). Only image loading and PNG saving
# differ between paths.


class Page:
    def __init__(self, use_pil):
        self.use_pil = use_pil
        self.buf = bytearray(bytes(PAPER) * (W * H))
        self._glyph_cache = {}

    def _set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(W, x1)
        y1 = min(H, y1)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * W + x0) * 3
            self.buf[i:i + len(row)] = row

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self._set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            half = int(math.sqrt(r * r - dy * dy))
            self.rect(cx - half, cy + dy, cx + half + 1, cy + dy + 1, color)

    def _glyph_pixels(self, face, ch):
        key = (face, ch)
        px = self._glyph_cache.get(key)
        if px is not None:
            return px
        f = _face(face)
        g = f["glyphs"].get(ch)
        if g is None:
            raise ValueError("char %r missing from face %s" % (ch, face))
        w, h, dx, dy, adv, off, ln = g
        pts = []
        if w and h:
            rowbytes = (w + 7) // 8
            for row in range(h):
                base = off + row * rowbytes
                for col in range(w):
                    byte = _blob[base + col // 8]
                    if byte & (0x80 >> (col % 8)):
                        pts.append((dx + col, dy + row))
        px = (pts, adv)
        self._glyph_cache[key] = px
        return px

    def text(self, face, x, y_baseline, s, color, anchor="left"):
        if anchor == "center":
            x = x - text_width(face, s) // 2
        elif anchor == "right":
            x = x - text_width(face, s)
        pen = x
        for ch in s:
            pts, adv = self._glyph_pixels(face, ch)
            for ox, oy in pts:
                self._set(pen + ox, y_baseline + oy, color)
            pen += adv

    def paste(self, name, x, y):
        w, h, rgb = load_image(os.path.join(HERE, name), self.use_pil)
        for row in range(h):
            src = row * w * 3
            dst = ((y + row) * W + x) * 3
            self.buf[dst:dst + w * 3] = rgb[src:src + w * 3]

    def save(self, path):
        if self.use_pil:
            from PIL import Image
            img = Image.frombytes("RGB", (W, H), bytes(self.buf))
            img.save(path, optimize=True)
        else:
            _save_png_stdlib(bytes(self.buf), W, H, path)

# -------------------------------------------------------- png codec ----
# Pure-stdlib PNG decode (8-bit, non-interlaced, colour types 0/2/3/6)
# and encode. Used by the stdlib path; the Pillow path uses PIL instead.
# Both paths paste the SAME embedded PNG files, so the pictures match.


def _png_chunk(data, pos):
    ln = struct.unpack(">I", data[pos:pos + 4])[0]
    typ = data[pos + 4:pos + 8]
    body = data[pos + 8:pos + 8 + ln]
    return typ, body, pos + 8 + ln + 4


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _png_decode(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, w, h, depth, ctype = 8, 0, 0, 0, 0
    plte, idat = None, bytearray()
    while pos < len(data):
        typ, body, pos = _png_chunk(data, pos)
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            if body[12] != 0:
                raise ValueError("unsupported PNG (interlaced)")
        elif typ == b"PLTE":
            plte = body
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
    ch = {0: 1, 2: 3, 3: 1, 6: 4}.get(ctype)
    if ch is None:
        raise ValueError("unsupported PNG colour type %d" % ctype)
    if depth == 8:
        stride, bpp = w * ch, ch
    elif depth in (1, 2, 4) and ctype in (0, 3):
        stride, bpp = (w * depth + 7) // 8, 1
    else:
        raise ValueError("unsupported PNG depth %d type %d" % (depth, ctype))
    raw = zlib.decompress(bytes(idat))
    out = bytearray(w * h * ch)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + _paeth(a, b, c)) & 0xFF
        elif f != 0:
            raise ValueError("bad PNG filter %d" % f)
        out[y * stride:(y + 1) * stride] = line
        prev = line
    if depth < 8:
        up = bytearray(w * h)
        mask = (1 << depth) - 1
        per_byte = 8 // depth
        for y in range(h):
            row = out[y * stride:(y + 1) * stride]
            for x in range(w):
                v = (row[x // per_byte] >> (8 - depth * (x % per_byte + 1))) & mask
                if ctype == 0:
                    v = v * 255 // mask
                up[y * w + x] = v
        out = up
    if ctype == 0:
        rgb = bytearray(w * h * 3)
        for i in range(w * h):
            g = out[i]
            rgb[i * 3:i * 3 + 3] = bytes((g, g, g))
        return w, h, bytes(rgb)
    if ctype == 2:
        return w, h, bytes(out)
    if ctype == 3:
        if plte is None:
            raise ValueError("palette PNG without PLTE")
        rgb = bytearray(w * h * 3)
        for i in range(w * h):
            idx = out[i] * 3
            rgb[i * 3:i * 3 + 3] = plte[idx:idx + 3]
        return w, h, bytes(rgb)
    rgb = bytearray(w * h * 3)
    for i in range(w * h):
        rgb[i * 3:i * 3 + 3] = out[i * 4:i * 4 + 3]
    return w, h, bytes(rgb)


def _png_chunk_out(typ, body):
    return (struct.pack(">I", len(body)) + typ + body +
            struct.pack(">I", zlib.crc32(typ + body) & 0xFFFFFFFF))


def _save_png_stdlib(rgb, w, h, path):
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    stride = w * 3
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    data = (b"\x89PNG\r\n\x1a\n" + _png_chunk_out(b"IHDR", ihdr) +
            _png_chunk_out(b"IDAT", zlib.compress(bytes(raw), 9)) +
            _png_chunk_out(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(data)


def load_image(path, use_pil):
    """Return (width, height, RGB bytes) for an embedded PNG file."""
    if use_pil:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        return im.size[0], im.size[1], im.tobytes()
    with open(path, "rb") as fh:
        return _png_decode(fh.read())

# ------------------------------------------------------------ layout ----

LAND = [(-168, -55, 14, 71), (-58, -20, 60, 84), (-80, -35, -55, 10),
        (-11, 40, 36, 70), (-18, 51, -35, 35), (40, 180, 5, 75),
        (95, 141, -11, 10), (113, 154, -40, -12), (-5, 2, 50, 59),
        (129, 146, 31, 46), (166, 179, -47, -34), (-22, -14, 63, 67),
        (43, 51, -26, -12)]


def _in_land(lon, lat):
    for a, b, c, d in LAND:
        if a <= lon <= b and c <= lat <= d:
            return True
    return False


def draw_map(pg, mx, my, mw, mh, mains):
    pg.rect(mx, my, mx + mw, my + mh, PANEL)
    pg.rect(mx, my, mx + mw, my + 1, LINE)
    pg.rect(mx, my + mh - 1, mx + mw, my + mh, LINE)
    pg.rect(mx, my, mx + 1, my + mh, LINE)
    pg.rect(mx + mw - 1, my, mx + mw, my + mh, LINE)
    step = 5
    for gy in range(my + 3, my + mh - 2, step):
        lat = 75 - (gy - my) / mh * 140
        for gx in range(mx + 3, mx + mw - 2, step):
            lon = -170 + (gx - mx) / mw * 360
            if _in_land(lon, lat):
                pg.rect(gx, gy, gx + 2, gy + 2, MAPDOT)
    for m in mains:
        p = m["pin"]
        px = mx + (p["lon"] + 170) / 360 * mw
        py = my + (75 - p["lat"]) / 140 * mh
        bx, by = int(px + p["dx"]), int(py + p["dy"])
        pg.line(int(px), int(py), bx, by, RED)
        pg.circle(int(px), int(py), 3, RED)
        pg.circle(bx, by, 10, RED)
        pg.text("inb10", bx, by + 4, str(m["n"]), WHITE, "center")


def _place(pg, name, x, y, ew, eh):
    w, h, _ = load_image(os.path.join(HERE, name), pg.use_pil)
    if (w, h) != (ew, eh):
        raise ValueError("%s is %dx%d, expected %dx%d"
                         % (name, w, h, ew, eh))
    pg.paste(name, x, y)


def render(use_pil):
    with open(os.path.join(HERE, "news.json")) as fh:
        news = json.load(fh)
    pg = Page(use_pil)
    # header
    pg.rect(0, 0, W, 108, NAVY)
    pg.text("pf38", W // 2, 52, news["title"], WHITE, "center")
    pg.text("in11", W // 2, 76, news["date"], SOFT, "center")
    pg.text("bki12", W // 2, 98, news["tagline"], SOFT, "center")
    pg.text("inb11", W - 24, 76, "35 STORIES · 6 CONTINENTS · ONE PAGE",
            SOFT, "right")
    # heroes
    pg.text("inb12", 24, 134, "TOP STORIES", NAVY, "left")
    heroes = [m for m in news["mains"] if m["hero"]]
    for i, m in enumerate(heroes):
        x = 24 + i * 328
        _place(pg, m["image"], x, 144, 312, 140)
        pg.rect(x, 284, x + 312, 300, NAVY)
        pg.text("inb10", x + 8, 295, m["location"], WHITE, "left")
        pg.text("inb11", x, 316, m["category"], RED, "left")
        y = 340
        for ln in fit_lines("pf26", m["headline"], 312, 2):
            pg.text("pf26", x, y, ln, INK, "left")
            y += 30
        y = 392
        for ln in fit_lines("bk13", m["summary"], 312, 2):
            pg.text("bk13", x, y, ln, INK, "left")
            y += 16
    # secondaries
    pg.text("inb12", 24, 434, "MORE TOP STORIES", NAVY, "left")
    secs = [m for m in news["mains"] if not m["hero"]]
    for i, m in enumerate(secs):
        col, row = i % 2, i // 2
        x = 24 + col * 496
        y = 446 + row * 66
        _place(pg, m["image"], x, y, 56, 56)
        for ln in fit_lines("pf17", m["headline"], 412, 1):
            pg.text("pf17", x + 68, y + 21, ln, INK, "left")
        yy = y + 38
        for ln in fit_lines("bk12", m["summary"], 412, 2):
            pg.text("bk12", x + 68, yy, ln, INK, "left")
            yy += 15
    # stats
    pg.rect(24, 716, W - 24, 717, LINE)
    for i, st in enumerate(news["stats"]):
        cx = 24 + 122 + i * 244
        pg.text("inb30", cx, 752, st["value"], NAVY, "center")
        pg.text("in11", cx, 772, st["caption"], MUTED, "center")
    # map + strip
    pg.text("inb12", 24, 800, "ON THE MAP", NAVY, "left")
    pg.text("inb12", 392, 800, "ALSO IN THE NEWS", NAVY, "left")
    draw_map(pg, 24, 812, 344, 180, news["mains"])
    for i, item in enumerate(news["strip"]):
        col, row = i // 12, i % 12
        x = 392 + col * 312
        y = 823 + row * 15
        num = str(item["n"])
        w_num = text_width("inb12", num)
        w_dot = text_width("in12", " · ")
        w_lead = text_width("inb12", item["lead"])
        clause = (" — " + item["clause"]) if item["clause"] else ""
        w_clause = text_width("in12", clause)
        if w_num + w_dot + w_lead + w_clause > 296:
            raise OverflowError("strip %d too wide: %d > 296"
                                % (item["n"], w_num + w_dot + w_lead + w_clause))
        pg.text("inb12", x, y, num, RED, "left")
        cx = x + w_num
        pg.text("in12", cx, y, " · ", MUTED, "left")
        cx += w_dot
        pg.text("inb12", cx, y, item["lead"], INK, "left")
        cx += w_lead
        if clause:
            pg.text("in12", cx, y, clause, INK, "left")
    # footer
    pg.text("in10", W // 2, 1002, news["note"], MUTED, "center")
    pg.text("in10", W // 2, 1016, news["footer"], MUTED, "center")
    return pg


def main():
    use_pil = "--stdlib" not in sys.argv
    if use_pil:
        try:
            import PIL  # noqa: F401
        except ImportError:
            use_pil = False
    pg = render(use_pil)
    os.makedirs("/output", exist_ok=True)
    out = "/output/entry.png"
    pg.save(out)
    print("wrote %s %d bytes (%s path)"
          % (out, os.path.getsize(out), "pillow" if use_pil else "stdlib"))


if __name__ == "__main__":
    main()
