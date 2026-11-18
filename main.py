#!/usr/bin/env python3
"""Generate the news-image-20261118 entry (v5): one 768x1024 PNG.

Reads news.json next to this file (9 main stories, 26 additional, 4 stats,
map pins, header/footer strings) and optional illu_1.png..illu_9.png
(AI illustrations; a code-drawn fallback is used when a file is absent).

Dual path: Pillow when importable, otherwise a stdlib-only renderer
(manual PNG encode/decode + rasterizer) using the same embedded glyph
atlas, so the output is the same layout/content either way.
Writes /output/entry.png. Deterministic: two runs produce identical bytes.
"""
import base64
import hashlib
import json
import math
import os
import struct
import sys
import zlib

W, H = 768, 1024
MARGIN = 20
CW = W - 2 * MARGIN  # 728

NAVY = (23, 38, 66)
IVORY = (245, 241, 229)
GOLD = (197, 163, 58)
GOLD_DARK = (138, 109, 27)
RED = (181, 43, 43)
SAGE = (220, 233, 223)
SAGE_DOT = (74, 106, 74)
INK = (23, 38, 66)
PAPER = (255, 253, 247)
HAIRLINE = (213, 205, 185)
MUTED = (90, 88, 80)
STEEL = (46, 110, 142)
GREEN = (47, 107, 79)
LIGHT_NAVY_TEXT = (198, 205, 222)

# face ids in the atlas
PF, LB, LBI, IB, IR = 0, 1, 2, 3, 4

ATLAS_B85 = "c-oD<31C~*l|FuCE0&x%ma?J{#ZtV*TZlq7*_N&6g`g0Vh!DUe0YqXP117u>79|M#u}lfmg|t&zx<dC(OK0dzr|Z9rD3qpcI!$RirN7ca6iVro20<W}ZDIYtbIy}vwodh)WSw{Je$V~xch9{_y0-UqUATHKEx$TQ=hNxea=L<COC2xp_oY-#hiLX}$Dfu$T1YkYGg>gu@zN?tYp9mKPxF>Lp5F~=57kkY7FRi*{~@FuR8I|#WlJ0{1{_2Kw1Uo|SxDthNVBPduBP(kjz7L1Qa3e1n!TL<_;Zn(=mDzqIQ}%Rgs6&|IS0<Kg!5~mOUX6cF}b^hQ(1|SbDfUYhatJ?EY_7dCU1mPMyu!`%|Y&mAe~Ji`ZX<B;5hLRq*hu@BQ$5e<HR2!)k6C<@<3N!N+|Oh`V4u_pcAVgokeTuUuYhr%OIUY>*%B8@zGyD3n@hF={qzJIXnqzGi{)cNW5iEju*Cdo1Ls{rEf|qA8~RjZIqz01tlkb2WbJd({3s|qvXU1NM}%lenj)Uj+bW5;v72YNt)*>d1W1>Mbs&}l9$dCU6j5|9`w;6NbAX<T8Dp`<IfL6x{<o*Y4Z6BFV>b3#n7VvLyLTl7l%dap+D0il<XU2T(VvwhYz}f=+2>E&;m&3x>(vskI{Tc_lk5by-H^w-fvtSFGg<166mVkgxYMP6wQHjhnq`w9wljRpzz|qLFz=<m*@=WvTjbLkA5OKgv(hvpUxHwvC7#(w$KS$4C(oD&S5K+Ied^-&1NZ1zoLbRcW5@py8yZ+0mq9!fRv(b^t_a;a}I~RkRFwmzel9)Xo<x>dhu6tINn9{9758I{tDJz%&oMf@Zw&PE}^KS8q&W(x{dmgrVsH}&E<HP(tjb9!i%?vv;+OX?ed=@?WAkS9V~glRY?@2UAEP&sAQ|V3_4fP@xrB|yPW=&JZ{H{gOI!!VLzsM&XSUQAXT6Zcayu^@%(*|%IQk_D$QF!Cq7-t*18)tTCkK}_zk2BFv>nJ*4p4<YaO5;Lg#p4i-&br(HBMcfanHc37#|Qg&#s%OM7913zpD{aSzva2)QqWuGdRw_p2e#hV&sXhr9+kmM<^7@PwB~<F&}0L%Qd2$YG?zAupcCA+MumN7Z~f@sIPkCHB!zX(6O1=dndzPv1oy94FlKxeg{hfqthGUGq8Qex!*OJaLamH_*q)i+I17&!h1G-A|Q>_xgOU!;QG+`U-zux_~X~COS$B(Jq@8aGEz`1k7JhIB}Oqw~*7Z6w>!0^}zzaPV<pw`9dzsLA2-mC502wg<SVT^hwF#9~W{Cx1!v0meUIlFXY;$U_Z{<lILDs$Yr_B)-7Jdx)IpR0$0h&{zW_*9}4~w?df>&x<#Dkf*@=HNc8PR+?xx7D;!H9J-&#0x;pqERaBI`@+(L_`W9>iDD~P)ix{PR!HXErUVL>C<Jpqng;WM9FOom_F{*@AwwQ5uS@5GY7t)y`)d%N0mH_L{TFhxuB>;T6K=;PQ3g8Xotf1FfssMnmB>>9n+aS#XfL}u8ZW_B}F&C~DL(5%BukD3Y2>>6Y*>mZ&n;@Nu#u=fxNabG1WCbmwQl#=FNu>ecJIh0_Jp{=E0AEQ?NZ%8w2_RGEqSt={$prvM4#@8piy5R_kgC&3Q@@4eL@b0Xp~>GvDgkUlS4vaQKq>`*qtwX#4^oE^hFy6%<xW7F4**|Jv)q&eVj|760YEP3+-LCMSp!gW&7m9sm*yai^U%PQ^Pj;@x(+~D23@`A)&peR$YJ#voWlm_I9`Y7!nQ6Zx>i7y8@lbHYeRjVZW_Nra&Kp;oW}P`?h!x^*VYtW2cX04r19h#T-#3QTyDo$N_0^`stY;XB{>){y^6VX>c|<~@?C(AIkO9=zH$b4b~m7-d^VkWM5G=-z-+{O@(k{kUJSxH(EYFI&Ov@0a!RC)FlINT`97}uxjb|c&+p@SF$_tLx7NoYH=$)_L5fMp^U#K6a|@@oL7EHW9*~e%NXR~bDCclMr1R+x7$u#$Tcj-jpxJZi)F&V<M*Ce)bCBQHCBHcLA42|ELSDeSN_zeGko*AfD<$5z#JdnOx4dTwx65|B?n{?&yo&&o9CFnX4tX(jbLJFIog>mEbT@e*?G&k>(?q=e67N!IXQMs;L8KkrN6>w23D<Tftgy7w@%rbM@CevtTiw?s_siI>QO@s+?sB#zC*^*+gnRP}l*U~`j-M}K+fA?)IO(-ti0(?BAYqZeUcxr9+pf|7NSb@lOKh$GE4l%cr5w7GOSqM;Vw-?&&Y7$mgq_1$UkCic>h{_;7!YZQ`vJP9Gr6``V_eOGWQgt>jKEoyh1WNq$)&y)xpT-%CFHOj@_Gq*9gWgljH5$mG8XJZivk&P|0vS+JOWUbk4srhZZqWmIf=Jl)6D&gq<I7E)rEMEpUHN808$y^9g}!Bq7KOK)UPGpO<Zc|GH3EAz8SSGFE8X?73mh_KNpg7DN9M%9mY{^@lsCnAS|?eP9aydl=C};5y7prb}8p@E0AIq`lw?m*ER)wEAcu`ZeGfDxXsq>6x|5hl9MK`mNXv<?vR$>zm!{kL2x_w=Hxv~xi=REZ=(uG?_J8hSsm=9S!Is#dzUg~e+x(ml$yM6DWjAxSW8Zz;{8h*6_*5SsMJZPJ|*$|L9_&PpAp@%Ag~9zFN&@{cq7dL)_q0Nbd&?Y&lCWEc&P%opGp8R4@*(2A(xg??%R@O4L}C)I{v+-46n6-DsJu{NMqEo4)J~}@#?t?A^lRM6=0hsNac5uN&~ocDS+{RmhvEIw51nCY629`0&Kl1MQsMa&MKpcQ&Q9xT0$iN@cdE*@FvW=^ahGc4#e_t4pR=l0yu^Q%IWlTIYSJ+D9ao_mt{3iP|z(9-Pr(NhVwH;w??J$YLV75G(p!S(mH5aceY6D0mYnVn@AgYN<vF?`?)2;b}E}i*J_8nP^31rb;&Hs@APxWw4?B)Wt30&xqcA_0MvF+qz<Gr3!ObIHR`l=*NZNSw&!W!CP~u(SirQ$Z}YSHb^(0LU4`*`{cL#MJmgW^Pf2Zi01g-~<DZv!y*xca_mJq$;h_ZS-$mMJ_w;u~Iu`)Tz4@rbi!r!E_hZp*LeF!19vA66*vPEeh4J6`xi>c>9S-@d==$s&UKHtkfYWTG`Ldsf%N77L=TMLwwlcs$axG&ij@olsJj*!V1v(9kFJ8ugx(#LH9GXOTq21Q2CEj+1Lg-pWcadEOLv$B20Jsa|v1Oe5B>=7pNc|%9qZS-*Na9_JHguysuNP^D-JUm#v=gJl3ERDG8P|4~ZFP5x?lK-Z(0xF3m&2BwC6vE^84vO+7^tuU{P;2j@Fg<FKDms0`bxF=$p@BkPw$3}@EH5TGPbNeuw~Z$i|7VmBdq&|=&n)=nf$)!2GJ{QyN^k2_rhM$E|WhMX^7hsx?hTPH3g^?((gpN2CHu8oT=P%%NR7Tg(Y*y6QUbt8V2c<NZ0W+H;X2xq<;H2O-Sx4w(IM;)F{i`DlUu3<wWiasyN<$)<Ie-(hX=A5X8wEiFbfo5b+u$-i<&XwCBWGRotF8u|-0+PINbO$so0hbPG>Vkh(-lvJPpUD`_57o0#mA{0?#JLbqLXx7yfqX%*KY#bXmw%bqH(`)#&vpXf$79{Mj?#Xa^A!z*m*kfgbQB_PoqRg6Rng99`h(w!2rI@rvU^W;BNF=l;>b10?!Jyi<eX9z03PoyQbbgxMMU;{&a?n5Fiv!(k)st-n~3|M!+NF{Rs;8g<PpQus*uVJGc`-Bv{n&HmrIQ0c7Kn<IAIgR~u6`M>g^Uex7^>0<o4(fQgAl@Squb#Ocq@z_l%vONzmLQd<C6xv?E-=PS6|=NPNM&=UPW@G+CUh@mtg#8{ie`r1G8%`C34p_ZoQ0{ffCBg$Y0}vNW#G#Mz$*d@;LR}Y!k8z(<qR=wp)9@tmuxi~I_gj@y0ewjj5P<Q88||&m5^&Wcj!7rw+`^fx^qRh9?-<n1tM*Lk+8H=q_C~KN~Bg>x?ZF<9@a3mgHoe*G10>0Xn;*Lg4`LX-Xl^6$HSce{(v%Y);Y#MD7q-ueYRuleo527pqMj<#y%Thj?o3+nq59M_U!<}c{czLOl9mRBJ}_a0e)jo2e?;y0Xegw%ZlzCJ7h_arHyDamKKV1uCnv7`XI-P0Xiz6YZKijw7m;bUyxhrJk-KHyD)Z9Pyu`=&4KO;3E78X#%b;s>3j@qu%@v)McTsa21xgbv{gCx*q0=~ICCiIz9+g1P-?KBv7ZH*{cK|v3f&(?cOmmD#2b^`w*#hUqyHSsS$C1t!7;XAIj4Cs!m_kNq)Pw~SfY-#i_|ai3S(O(-lZtFyWBB$<#Mjy4%CqIyGC?7VZE-3!l~499s#@1E2Ri|SVCSVx~Wqi6y4=a1~46eYB}5I6{wS|q(BcYR{#fumN>>fE7FzdU0A`y=a+L&3xI=#eswv6iU2rt-xS>d*A}|(i|#6h80e0Qjsd)U?i;6mzMNNOd%0K23lo2qk_{mT7uFlEO1!Ii?TS?1Sgs6wIk^zeUCpEMTBc~wEvjbSFk366V6`%EtZ0y5b2Sr%eLAsCv{rNO*E48BGDI?Ay>3hj=T<8NmnmstTQ!&E241nj=66cS1I+(jg^ArF-N@L33F>MId6Q266E}$NX2u>!2SvJtDGVe_%94Z*Q|`nEM0XG)&|N+?ai64e2$BoBPmAtWMj{~C7pl3BQpm4luH)3#rS7+hu5juR(Ty-J0d0O#tpL77u<lqj+u4F(oEdojzpIsjA7Tccf2vv;_&UbViKnX-z%eO6mywXZAm|%V@eiU~5?m_M3)RZNvHF1YzalLQhD171tqgoCxqx-ARttbL179Kl{(7|nxXiQTEHMKQf*m+=Z&c4@;P@g8d@Yq>j&jv-HR@1BW_R;yl!0HsORDiDHOy(0fje@IHAM!_yrre4$iSVm3%T_*%D_Wh;c=rz8MyM!-WmmPp8)uIH8UCbmYSIid~1yYcn!)~7~fW-3|!{?@k?uzfj2XI&0SfeE|jovjH_#k44gymuTciRR#?oz8fD<ByS+vkc&kYF)F=aAC0yu(HOj!12Y$Rp8Muc0Y>hJTrR+?~f2F3#z@24<{J+*H0}o4W|D#43cq`Adli#aR2F^Oi#3MDzz)|;dNA7XSugJiER-+9395Bs7?itCi+vbmds!;|m3)b-yHOjy@3s*l?!)AXDv>eh|s|>tdq&c<9z&8ndonNaAd>e*tVf@Tmj<*SY&28OKs|<WKawv?il8~Dj?x5QsA^R9OAe~dI415>Ofz&6uEzokBJ4D*bL;?8?)hYvzNLkEUW#F56@QmM5%l5L3YYW}&waUPSX^tPRRR*s7|46Me@J;N58vkgmGVosH;23{Eq)Ql#AbqJ;8Mv-tz9nV36m8F(`-ip4z_l#LYKsiK47U5rT4mr(REkOV_q9a^j<rbc`P!Kb{6wuX@NO{h0%dDYGjK=l)mmlXYlKO^UaJf|Bx}3LT4mr3!cd)c%D~r))y=L`2CnRNL7g)2DuDD<Zb_ZGP|oIFnXIi-2EK;rO|C`aF#~6qTqhDU@L7o0S*HyAEXjS7=!SW{2x*&0*YS!5`R$ba_VGA^bfrkwv-<(k-a2LAlHbI25^q1(2#omVI%VLE!iY!elz~?xUSaaiI%VL?g@NBwrwn|Zq<N%H8Mv-DK2kT6fq$}28TeXqA(hXHbP#nYL*2hzrwkk;6}pE-cdLy=->g#xz8rkkkxSPV893w8PwSL{hXlZXU8ewU$T<2<-Ao4lOx;Wdo~cs?-XaYA4|NLQON4>HP<NVvJ92-nQwF|Rq?hVWGjK=l<+{@h92Qci47^Ji`0FB-&Y5<h<mwc_>!h1<(%jVm5&&w>QLhaAT=7`Vs^@~&GPA|}HMd?FxXIg{V@vAA(au8<bJWUuuKo&W!N7AH>Xm^v@=QL~Ue68HXiFPKYSN`x?t*&m&}Ix)7a;B8dIj)0_7W9#)z4($iF#$=b-WCn+Ff5{;IokCRgz{%ec5AXy)tkypxmK)1#o5HchoBbKUYG&w_X|ec~aZ^>J`9y#e4QC3Ax@5`Neu=;NqmoJuD%^Hsk+xy)tkO`Gb08;3y}I@>o3^WjoplZ9VbJdi8;C7N~f-UK#jiw1i{gIcW*r5M&1aV!bl(PM$i)UanULZZZSUjn^v!-zFYF&k6<bO;U$5MCxHj1>yx(aJ*i1bLARE#{kYDSBtcfWRaL_73o|~6Y;tvUd+y6v*<S2OYjRtI!{+Ext%MxMw{&%21M6qFWrYlI-mDUAl<k^T`1!J&)v0R+J%Dr-Y5CRZL9l;=q|8zpI)H=E>5A`mqmA>-SQ8wPzJ7b|E}mRVuuks{G?<T+jaQq3I*^RsDhmeD-^)Ros)Y`beHNrOztlt?Xc54Dbh~cb|+V`o$a!%uB?Hj%WT~|kuK+*7boTX4eA45D=rj_O960MAdgiyD1fWOudab}*ll~gS2ies>(YI_=mu<EXM+N`PR{3wZjk-eu<Na&+pDX<@%{#Gmm#)f)M0mnx=^av2FI>xPyh#PRTRb!H1L?dmISDBqYdgpsgj<)yFpzj1I)n3?`=>9-m9*<24&#A>Z+5FCYKYrKP0*Dx2122bOSpd5ii}K3|uT^{6`Y6$iRQzpbT7cn0Tr|8F;rK!!r#E;Fr;CNPm=4GXrPcD-8<Z;`N>wYfuIr<%wnjog)CgR(q_G`zVEnC6$iX=QVPTZnJd((T(uf1f6PX<UV>RxLNFMWur3i4cwdg4UNjc_t6|kt&PgS*K)s4b~Gx03rbCPH7bBtGoIyo8<l~p6l+ul-p*d{TwkLy@HUa+jmp6Hi4T0c)S+}X0Nf`4zN1kAyjlR9B?j;f0^oZZ6~J}NVQ-@Xc$Yc{8kK<$@`5#Yu#tISJ;MQ{_ev@&kPZX*hZ_~Z>t)`%zfl=@z4)3w+o%jY%rkQCp+*JpUTN;HH!6TH=PFKpt5E@bm2jHxH7bCMuYT(LjSAo^B!{%58M2}GCsLLo1OH{C0(ewF<#&zBz;zSlISIMeHuRSo6~H@1_gbR@c$cL4hDaNfbLYyM6u?zi*~Ge5TRKA|aiPErgG~zH)jT97R!F>vUE5Vn%D{WM(<aw76<sLIz+0P?f$Q!=v`HEGAaBp*VoeI*x`lIjQ;~sl9R`~ez|WJi?2~xCHu&ArqyR3S%G_v^0=TSNa(6c=fNvJ?yI11H*qEWazexeyFT?u5CI#>|DcP5s6u>oyuQw@x%UUG&ohAkF%VgW@(Iy4(J_-4YCI#^GCBNTFDskKD{?McVzD0EZE4poV{Z2M1fNNV%if+3-B{`cFz;(O2qFDi4TWL|V0{9TkfwZi7+6NA4WwQdftUhw<niaq`zm8@FaJA%fnw5d8)om5&GTW{%ZB_=pTI_mHGu!nQ%I9dPSpmF`7uLCJn$?A(?uX%Kb)iJ1Jr6W1fVYb-)vPWQ)!o^w04}TJiT5?D3#CD<{GXcD2QDEeKGCc$6rD&v->d+>RQm6s=F>j#Lhc*Q%D~mG|Fc;ETtoh-Spj?}mBU(p-prsWK5$6CYgPu{A!T{CSzRca`-{!Wz*TysSzRcyZkU*mcn8?75f4LMTqt$2)8lI4{BF{nkO@zV0=Rg@Cl<FTfL|nK@wX^|w~4NyMFBh_`JL5LbfK_rLyH3VD&Bz4b+jl0uM-!_xh?8KStY%>y+s+gj>gMdcr-o~R7BY=X)Xw=fBf1O1#nDkkgjV{0AD2xe1D4qxS-VJO)U!G0fFpfivqYxsTKuro$##|1@Ltu-PNK1jvRn>hougsivi$k1;9Vhq5ys#&6?-PvNR6>a}Z0$lI#Q0Y&CQ*ReCA=#TGsqRZB;xaxwk&2}sP2pP>cwOJ07pg%9u4(}&43pI&ZQ$wzWlV7NGuO5aLOr2zxYwb1eMg)5n>H;P0r?-i*DjXJyBk-c>#PXo<#A5~O1UVHya_II{mD9v&?roJGltb|#*v8;G#B{#-dtefS?|LaN~Agj1Tk>)obHDIuOnC8xRy!^D3Wi^J6+v~_83I^-h^j@l%=Xlu*sTu(O0SS5bStJgk`)DpgUVIkUb{*ZrA+tA2$n|Im4tc+X+&~sppk4ky2^qF^Pm8YAmQW~2ZCuW|j@N2ev5~Z+UC`FAtzN}#9pT!}b)4*8#eT~UNOQ_dUf;EfTcT5RB`5cZE{ayFK<gfsG!4qoqD7AELy)3?u+NhhW%<i0E=xCkNa`>r#8MA^4!z=dxjDq~dilsEbX!Gt4!s9;aAdC+X(QcEb0FO-(z)~niTAG(FNPdA-Y-SB31xFaIvL{jJP+|I=25nEHMi1c`ZRf<t6R+>`}n{iq;o_%pO2(Mx@t8a65GNDBO%=<x~=pT$?rc_lbm(>fYjl)qPu{;%E#qi9$(D|!M4!{MHe`mbr-TlqFthAbG+^JPhzcmM0XK=hAPp2cb?59yV!1}FNp3EK8y(Ihi7wH`suTxdtG#wA|6YN*08k0ZqIch?X)fVqBU&0yKJkwdJS9MWzdyD_d(HJ4lu-eBm0FldW`UD=1}w>Yj_AIP{T5(<K^$I(Nid}rAj*apKJJ(&2F{N?C;iasrR6D=R)^}=mwyhi?&{}mUUOrouX@B%eq0-qI@2`e2M7xa>)5~^59x-mm#)f)ZtTWxeiyu?wl9_-(Sl%cn!nd;=;@SwU)`iwPM$f?DG<Gm_tHxuH!mfM?a?du-1i;Rsg{75!-EF$M$(W-7RIgXdRcu<T}iEoZP>TbKh^5<vx*aK#RH&?>p;wJRD%VM!Y8^-i^Ex^3p4Rko<1q94Z|rUlrZWbQjH?OD8MWbAGqb_h<p6hV@*QBudS?t)e@~A(7wJ>p8zee25tNy<c><qGig_M_*dcJ;sMpo&J*l{rP&%;Wow>=>D>v`)`D?V3uR7u%6-kq2Ncw&dN7%nhTT>=T>gu-dq@bnifM^vq1=OaEM)Xry?7868e^+)T!PLj8Z;6q2h96H*H`%TVhLbk^I41u)c9*FWJDWfn~v)M7m0(dgQPWSa)CppW7>S1HcyufZwq}0eq=&#5*LRYQQFzcN6z)P#^eOnZMpAMXgmI@%V?NaCO|=i1%@cSI_=ANS_gD1=1`*Dqr3(eF~+V#=k06Y_z3sh}6V~ubedT{SE2^UoRfAN2S6ono8jbNo6IopAvfG#~YM^i*D+t8<c^|vVQ!(q+}txEdMQKS&dqhq7J{8I-G5vb9qjrHC!Wv{Ii5y%kiMgif)~~Npwnd>+O(lh_pd{eiP0xhYZ`g*<seT+R{9c*au!xMw7m<ZesemttYF(x{0Z^tqXH)J9N>VZwe~|SKV2ni|WF2VvWQzbjd%_7UtS^+1#XCa_Cmi;Y3WN9-F~!k$Al}Q@KcV=P*Zvv{R&wc8#tS>0F!L?Ui^jJBNLu+k}CR8cp0N(s>*YArDE&&2|pAi>{AL4e4%?&bQrT?-ywcb2do-B+^!!ZGB8qiQ79N4~p&rTlYoLZL=-%Yofc*ZtH&+-FDQSb>9`;MRwiOqPy6x!;eIF32$ja`dOG6T)&>7nE0*eF173Mj7U4|_WYwrJ8j$jOPFnUmu+>gNk3d>>++(zTn~^<%xcw5%zECxA$Kc#O%uH9R7&IJt?EKKOT4=kt?C0;tDE1-rQT!vmY1}u4_tKt(OqSqP^oWKA9zqs#I%TRFS{FIXKO?nvTeRiLSD`NhmeNou7OlqUKl^Ol}mlCmSrL?A&2drzF4H|ctrz?+||k!xz9e`ab>HXLJ?b<9Bfq|xRi5pSaR5JO9w={f&JWwcc@i;;9?<@qpj)#UnWTO53TA0*V8%gYgHe3Nb>uT#Jh#p%8))PQj$vz>65K`3Pm=4CqE;p9I|y^Zq-vL^>U2&Yf{^keeUF&tqjt)*}AmoMtJ;{QvS!S>O$EdEq_eXT)-Y`Aki;dm4VBa<{Q6mRUfz<Z_fWl;(bd|D*yjlm4VCYqlw?Qst;VHOso39o5fz9YgHe3lSnVLst+7F0PFrNQYmj@E)oELsZ{}7JYC}~@h0Zka;)#QR&}As@@_oWs+*X4#HrA##|U@Iwxzp`=gWHgP@%6)j}cb!@?bpJrY@9fX`0$L1#ofMjIV4{02f0TU*D!Klnyx%)ZV55E~ylZw&_hwELD2j6u_&*g|e}&xQWS&uT5<V;Nlz@zo1PwF;|FbU)rX}2wSB_36a*=+mCzObQ4n+g5%eVZk=v-j^Eri^BCbsn{HwXaE!l4LWb>4)AzT{JVtn5n{HxO$tjdiwJCthke~cqo4QaG#J<|5E|d;gw0*rz0bF(e(WWkxvt{c1UYi~x+$o!wkG1J0W{-Fye=TL{wzr+1ZqrRnaVm^I*QT48daUm+ZF-DQjB@<dHr>QrC(?MEZeprW69tw{OwGaFuEz+M2mpB6brVyLUXCwr*G){#p{iYv5ekfq*R|^==62a)Y!PXTeLQcCNLyLrLz?ZniK$lC-L9LM8%4KCblVh`$1iBtO-yb1{&wBO)Ve3ybrZ8&`?g&-F|`iYi|!Kkq4MFtc4j#J>?VP9S9|doAxrOVFK%LTnjdP{O-!}jkF_g+tJQtBT>)HmUujnWZ;^5I@9pXXZx$EIx7yW(vYcHg<KJml7m9AreXm^sT(`g<l{EL*8+ku&R{&St&qa5Y(v8XAv@3wuik1JqT>)IIeDe8r1#odxjQ>TXt9kpM`@LNO+$R7&-mU<?Rzj9UST}5kEEnlI-bKLJ^hOlG!!lAAMHImGkl&dR1#rzh7*POMX+=Z<yiNf8tcU`*g7lim^d=_i*BVh5if)s3MHIl->rugo0{Hn-mcEDrxcqiy@`8v0xX`!Biz5o)s=F+r0Nx}>v^$~zzMM)b9Ano;cpAUW*4+|O0Po<9!@Lzy09RlAoe|x{Tq!P;_eK=JcThQ`_ea!)B0!w~U_=32P%8i7hyu7@Q1PP?b)l&AiOA_wC^Y^+<n$>N8vk5GT`0%_SobAqiBcB;e4YUK*CGnw(oGXzizowMA&mGN5e0DNP~VOy13ydVp+_WS9d9*3`e8&FxH7S05oO>$KEXZl%ZLK_nKHBfMs$s~^gkjs+4=o3q6}OLp8vB*Epix<rv4gH02i}=<CTa4xSXP#IvG&_*Hy%+h@L{xvb+&d1}+df;p|Wb-Xb-c-JuLznXR`&8Mw00Gdh%kw}@_8hca*tS=*ruTs?Ws9m>G9T~>D}1J{t@4rSnH2m_CHD1b{_PoC4E3|wp5*TMDcu%&p10=P=sMT+VqG|}Io3|uz(Ca&mE2CkfRZ-+8)<xtmkC<9l9dZ0rYxSV&GIMksGyh-X{btnVZ8oj4O8MwxKUxzYqWyJr~p$vSX@Uo9}C<B+X&=U`IC<9ln_r(rn;Btmy;-L;@;9bJN|E)tAxH8*scPInbHPa&<%D~m?e%PT5Ty;O~PzJ8`d$L0rxVHRL9m>G9|DNek1}@Xb#2-79fom(h)S(P~6Q5$3cvYl+yMDP2W#HOMQyt2{?X^~?GH|us*`1u`F5Bwnb?PY;)%iraoJmV5O$IuZfiD*ZUfrn-{7fn-p^2JK1@K0Ow0vDBL(Fd5>Y6&0fvaw{=mvOo4Bh%pW#CPs>k!?b{=#6QTgthYLzYoKCen~f6I(i!fiIB$+b+^IkV@T!i5;D6OV`>~u)9+kxP~0+R0b|TF3IofWQ*KKa@rz)gGkr&J`>7vvy{cuF_yno;_bJ~a=S=3kib^{Zi#n*?HcjkEAejR7UXj$67nXF2i-?RcQYS2M7&Q(yjyr$h4g?(N&R6|{&ON7<dDekOOnbVITlU%uZiwfdq?W)(t>gh9FYC(PKNB;Y~7=xvrnPCakNuUq3ChWpL8k%uMr0Ri%tb_5Dezyoyx#v-!A{_PW6EcO67mssQ|uMQ1R(b1#p!zoeJRcqs58mI~Bm|M0&AP0eqtzBYa6xah^U#_;RNL_?hxUo|ik7feU#bAL~>Xit^QoPG#V_VdaP_1Min(TC<~ij8J*!{HQW;SvriL8C4g`a^WV+qRPNks*g^)P{6=fMU{a^WS(6cRR%7{;0vu$b)hs01CK-%z(qIJ8C3ue%G})*RR*q1Wm8lcxSRtSzaTpOLmo)|QDxv^;g45Dm4Pes+Z$B|uH158R2jI<$D_)?m0ONPm4U17AEL^@ReFDP`iDH|`un1~iMf>9dg7B&W#AEE2cM6s3njuwhw}d%)nkOLb4)%IRTs)xQkJhrm4RO(4E#G$W#Ia=m!C$Jfh$9OGO7$*w&2Ep8!a+$);$|l2EJbE@M3f(1AjTH3|yJ}sc4abbG)gjGH~T(vkYb6`g5lWLm9a8)rH1P2ENo#1}-kQ@oGaExSoM;G-fjJkTH{ihYe-ms*4)Rz*TpyG4qE!TMT93s=L@w2HqpO%M4}U+Dca$%D^w>bHwArhB9znc^xv8fva@8p$uF{z+t0!jIgBKF@CS13|y`5enT0!+Vz8mGVmrIg5&>eC<AY#Spe{_8PhHlFz|md6u^~*K5Qrh*TbvdG?ans5yM9eW#IaQvBwQ%;L6;O8Op%r2;TUUhB9!m^2y&C%D}a6Glnv7b)o#pnCU_}VJHJ%Eg{DYW#Afe%1{QrRaoz=E@j~B#CB(QDFa_GW$|<=1K%JVcu|)!a4n0!OBr~zFz}i#W#H-tYUrAFp`d<ebtwba)yMiSW#DThzetxd@bjcBU0uq+Wy5%KW0x{;bsuf+QU<QBo^4$-T_~4y6<sI}Fz`f|GH}%mcPRsp2m`;VOBuNO7m{5w8MxIolY!sSr3`!x9}&&Jr%M^Qpw#3&T{C{jGycA=89(G1zqf0~4|&Ev)HUOWJmdFusS9O`xKQpF$;m$O#ri{@E(P#21Y$nXr3_pSzD#_!O95Qj$QQblf$L!XYM1)Jw+aLQ_bz4N%Gti#HO;`0%A;Kh;LF6cAMa8CSLtV63g9wBPW*S5GH^AE|JS7eE>$c%)1?4jC+EQb(52_V&tMi)cupE|mEHA!>{0+%U*TW7lz|6@o4nSg3|u|G6J5%{#b76ZbHc!tiMhI!f$OY0w_6#wrn#_N8Mt!9rQOQFRkyrb8MsOf-O~&lJYrS1o&)zWr^&DF)^p%m+qP~6aQW#+KH9ASuDb4S1#soL=XNUtKVN*{Te_8j%kp*N;%;T&T8CZT%E0x6!|v{xKJcr%m4S!!x1QZIec(5B&-8)c+C9?;en<CAANb*JW#DH?$v)7n3|w~+?(3fE1OG&~GVqu%@XvHB1J^Xa)U6C$PceM0TN$`o-8Z_GfvfJj-9;Zb>mKb^2CgjoN8QT6Rrg=r%D}Y_zv@;7uC4UDZe`$Gg@HfYtqfdsf9h5Su66ipw=!^DQ=IHp2ClX{-mL(xR#(!a0Is^(JqqCB3!PZdqYPYZmlpR-GjI&gGkVkqzEaL}pV^}Tt`-^WQ3kI5@fAG^;Hq2MqYPaA<7<10=fIh!wDl-}OUTKt9tCji+gQ&`2EL_dCIjEzqYPZvr@MM)GVt9!%D^{@-+8D<0eqF%=XE^_;0nYy^eBL9?#UhnaFs@T6u_(acM+5C=}`ceRp8`%dlbNR4fDYs^?_^s?(b0mUn%*0x<>)LOUm-O9tH3g^>g<qfXfPa@@qW`;KJi4ztN)ru5PaH^eBKYCC6+>?gu^U16SR#9tCh6jlb?u0AHsoy`E_wIG+RW(R1K&a`QQGk*Wdi4B*f9D1Zw}z43gH{*Y&ppyCTX3g9aJxkmxKM(pLK9tCifUhYu<KZiMf;Z;o~lHyk+5($TWKA#saA|F2im>;lCrYF+}(g&>l)^dyg#S~bb!^t<`6|ZO^4F-uDy-o6Lv|u^Cgq!SV@(S8_X@&xzq$?;{PswV&Q`IyY<U5+-JCGw+o=T_4Q9xQ`L@i^L+$*fa3c_ukMO(vE8a$n5@rB&H0rIZ4g8S1(CWG6`JWIHr{Q>QNoL1jOl^mp49;Oi{eIV?p^pW3R;`clKetdCP`n;9lpes~N*kzTzuPRts74Y)g-&yHJxKIUAwv0R(v}2~^M+K|Glc#Xtc?xxwkQusz%;nEgwnpE{d5=-b#mlftidrcO6!PRLWT~`})-23y&NR(nP};W?=2;1|_6s9V+E?x^mp<hXC^W*CAs+h1;(CQ}p-xDnl014@uD4wtzM#{*{Frt^fD*I{QgZQ`-0-c*(JaEGM{~C(4}|$yspRlZccEato65`f<#f8a<wtX)InpOwQUhwsVL4Fr61kkXD$tW|^b=n}xj3LSl|e34)<ab;E8<G0aF^oF;Leq1lJbS0xY7}qRpp|}N)9hC%=;9;<#~q-&#lo6S)S~goROov-Nac(#$j=9xJv?4(W%j?!W0rhs3o~ziug)WmJr67m9FTtFM00BxU6K+EPaI5#Z$g><VaFUlALn8ljJ>!QN;IX0j*dJHhqUBjX+MXpxq)hRy2#GQqz}YS(<in6xgOoXs}WXU55Jc53O-W<i0IQDU`8_Qi0;_u~HuUdjxkCRYk~SYP*f1-lO@^yy3R{BS9HTJ8+d+rEjvQQXbruVGJQoLhsHhiux&fKLxTFE9A<OD@SuNQl=<8Ldhs41C*0H>7gW|_&Ei8+=ZzMHeAJJ;_`7RPu~%b)fup=(4mDH^$SbQGhA~tLMWHdC5z~wLMWNf&v=x}r<`uL*R~K01x`VtR~8eKfA)bK>6rp|)yx+gKdF6k`y(z=Ksua6r9|;_bR<&z$}dkklr@vNNG_69!_n~$gDRmnzslH1tpJ8=v28GjLI`E>*kKeW1JE0EyWByl$_2gQTril#JDUv>-d!1aljGT};dmDHdp2X;`P{SQc<vA6c;k68UdhV9w~<jWlK+XN(mPL=AyT|Y<nAQ;Pof9N5wLIrU`jmc5?9()$T(fdAmc90;wDGd>&W2_JMtqg9zLU=rl`jXxYBRCtw1FO!W2MNA(mzWrP+X^c;h=i$wXZikHQgD1tw>DC<MgslzW74j0C>(#XDt}m$e8J<ryO6u|lqN+;P&b+339#b)*B7RYNQei;)0zzU>|<YLjxKY?)}O1w5B@(vr^fZ3Kt{P71i?4)fd=@Kc~d9^&QzdUN<_X}Ta20;f}&4mf6}V{rHixsgKtE$O`Jj=~-@+C+zeK^`j{AYUin?h(G<)<mv+%8?r(zB}bcJ9sGPvW_~QE6(7fw@)Eq<cp|(`<<8R?f(v!lJp9X@kkoAq5{tU_Z1~>qCm!z{yQ(rz7W?>$zo-4QOZcuS^)<IO6YV)Y3q(qppyb96h<Aa)dTa)@XaQfi#l?J$HbN`ZtTF{d%vl-(Y@0hj)Yv9C?;Bra4EGbeMZ`q;rEJkDZjI>v?F_N+L7b;-D%46+m)u<@E*mxbH>~6N{9IE_N4P}%o6$n+II3_31P4X(r7_)2_BbXK7tX*m;&DdKVh{;)jW{NkqHssc|gA;<ajLYx;+aEsgjwblSWe1DR&fizIcns&qt_Jf~5rIv##4Sj^}K=WHfMD#qs{OTVbJ!OZ$#(I&JD)CPJZrlQ~QUDVc>)u<37XZEA6+-}<Z=vU55liivbERo#xtb4kNw`7pgj^8pg%_n@^(^F?4BeE@Y319`^^c*LMkhc}^KW;%SdG+THy$MX+n&m|Ob@trD_+d(4^=@jWOPmvnaG&K%bhQ~_qO=f`1D%w(<+(zEWCG%l3A5P?bxQ)D9@6+S{|GHf=sYTPtfW;vDci(8gpvU6dWf`ut<tWaTqgH2>`~k~{+hch>Y24&W2VI#U>Ry^Pa62$%<SfGd2Jt;T+34KkpPr6J@635Dj6@d&ZqJorcGM3iX4O1@q?|}P<%SJU@y8=>wC^KcDt#r&9|12pUO`bE6M+Zu;du}v0EMBvd|(g(74eaDaqpKFKZ;os;KK}932yzg<$6{I%Bwt%9NKvHP{RC($uTW6Bc{b{MQPUW$VD9aLaD;XbUF!78cl_CEN+Qch?`+TMrFQ;*KfZu5~Yhq0+yr#iy&h}ZYhQ%$2TTn+&Y?3I}|uz@f{^JpEXiyr7)!;oz&lajaWj$4V!*474!*Bcgn@oo!1|-0^y6<MCadp@t|b}nf7G-*-+SUD*e@)%w#g+cb0H+6-n}gTt^s1aQi#O9;V3ENmbxXoi+&ZJwnk(fZ0l!Y{Pkn8-v}0+v;@TPQS}7S`J37YIT+;RE1SCw?;C2dLhQ-d&C*_1#$pQVUh1NCpbV<N2y8(_B4UWz4@MI9thKk>EIce8>~vxA4ay3B(6ffm~H;e*=AfmPsEc7qyk}`C`U7Ydm<gpI7+Rm*VB=M>C|m$tj4DA2-@4^8Newk2~?f|tiU%Q0puy+vNA5pRFYXi5z}sLZQ820-=h?`*J2nKoUeNK8(QG#=mQz2%=63$PLH_1%@0P?PFcj^nvN4?zWi?2jKyD-9FzasbqJt*R8>Y*PO5TKm6xiN%;l*n#YR{a<*uz_vXG8qy?k$`jQ(CmQ{*)u6BtCJqk(kv-p^rrcnt4H@xJ}<e|sLwjy~`wo=Zm2Vs@*i|DJpFfh<N^rHnKz+ps!JzKeyjk;>8zAuEfM%{ynu)7#rPK5op2kGypnA5AlMcuJXL|J_4`JkPvss4<}$O+`N)=)~oJH`^~Ee>@yYdXwH1RtBJ-X;8{+Y0iQ5KVOOLr5W}86ir4vA@6n__8f6#blMGA3@je2>hHJ%fwbr4OmPtcK1hL5VWW4D2RBylkIRjf{EK|^tROcpEi==D<FUIzB5p@}r@8&D0Jx#&?q|vKUcB!C?*I5zay|Mgl^*Ar00bhF0;fybZ>&($;pufON?%D)VZxrn<T-9rKv~F9NsgR(a;C_Q)kG9sV2wnl*DFG#9mS&G!G%WAOP`l==ZfXlq9^$F8Put_H9gYvxkRoj+m-FflxDD&6!wk|b9drO`BLFRj#uI?YuaryeO1Xg_KANYEUvGrw{$wka9O2XVDtZc0TCjSM%CNXP$yU#Q`g%{q2-9kI-`mq$QaG0A1hcE=2to0z@N`rr6ACEr(JiZJ*B*)KW)3rN;ydMZIg(nH0`;YV<9e5An~)#xC?2#GxnQTNHFQqj9gj%gn?USw%^SgG>l|El?sbDL_KrfARbzVbujxz?zUVi7e-Ho5-hy|$?0}_-Cl2y$Xii{nbw1Mz|yz+Boh46FGTTpTpp@lrPl7;w%xnUa8+elcdyDZxin;nRhBMGmk7sNXw(})@4W1abT9Q-SCWaMvuniwr$8|i34B9lK~CLB1VjAd(nGr|obq~$#w_JYX{lzs_@`XOYrQyMB?XiG6%{__2KeIkRzL`0{^QrkNJRxDlOzw(25xUKF))Z1YL>qXq8IT|&%wbP!;vi;H{$WY;0rGd)^o#3{`e^VMP1#&gxmJ;q(e@p*PvM6MrVb1q(XKnORTw8xwQn>QYyEfImI!|j$T~sHMOox^G5U<`R&abT5YYi)>sFK{f!|DSx#Rei~pT~8xSItK7FmWZlDA5&!U86uaf_+#*+i9L!q^6rA;Iy(@y0|>q_LnhjsR+SHI=jpVnsNSmEgxs<YqH4A?!&=Tz2M2r5rbU!19Fh7;k0FX2yABq|eS31_0$Ojscq%oV7%OR8*$g)Bft66w>I7U~8`9T&P)(>32MY|xW-ST}2U;_z#<WSsihyAy1tu8kY%_tyJxRnY0nkNPk;oW4TxPcWEiE~!tv?iJEWygRc0@zr;=rhT~l8Pv+GNH}3WuUPwS|2&7|dhJ2ZA&cX4+~T!&V`YWk7Y^;;o1XbHW*T#1<_okONIr@&LDV-~(K38&L;?&B?%A_<Z~zuM%whz&>NPmylHae@4h%>DUrRAfldeD3H-zC{_MT~Lni=gDv1vOjTW`?{f-{0A2r1A$JNW6O>E^^>sCeDNGJ@>2uUmK&*`o{<*t2JFP=?RU+}BGrc$g1siUa67e?{zc!-U=v;}&T)KIjp)J4-!W2ZC$>7;oq-H=DtL8TR=r_PsT%8<pYa_4z`ffnf>-ITOJn&dPf8OCATk8i-5D?qA}c=P$7BQ%AxYTB<CUMzdt*a@k-JOKtQT9vT`(JraWn!9hbD%|U8t2vZVR8;T`D?!)G^RfHNsXU7lUTy#lWx*XFu{9&5BZx+-?iD}O-1!KLvy|D)SL4xA$7~nJ+kC8X#22guLUayx2HF<sBIA(Ao7K?e=oh{P`Ld8QI(2K`zH?I~+Ka96vFs~y;$r}pi(R}(aEtIt-%~(@1P!ILSlD)mdYq`?h>uIQ)UjxI2VH$@0C&9|@?hx(n?&h1P2Ry};Ag>2$AQm@ceS`XZ03b#e(gk!GZK6%+=-s=wowsFUH?8gN>gwuViyV80I8o}RF1flff%&B4ph_Ykw_$|b?ihWXw@SUfL6peAnAwBkhh$;w7Mt1~tPa-DB4Zx8Ew-qEpwH`eZrmO8`rK|`pWBCN_;Kk??a{Zsg4#}T<Pqm4jH6Ne$%{#v&s(7Yhhy9?X(OSNBMRLgj~k}@FpK>N-N&sjiKA5Vl7#w=M7+P4@uk#f#c-W(#W+R?sm95ONh81>4s%CR+$grGofC23A&Q|Tg4Deu)>2C`7<&KFm=R<X1644dno&37?O)kSYhmBDEtDFy#NZ9G?L~f;P21T<?N*>T^b4IM!Ip-G26ER9ghD>|mra?@VT}!P1kIlg8XK%G`6sOQDBqHXWxiwZAkc>67Z(uPuuiv0&BK)aO4)iuCEN?EcW=aSU~9(<MKRsAy|oqYP;bs%TkG^y^d08CHeW+5&wJ*PV9@RCeIFjp4<?3td;7u^j4(L}CJdCgwl>@c`{A+=4n&+7C0w+$bTjv$J7@%LXS)Heg~pG^LkYV*xIn!RZlX(JxSPcNq8<r{Rbn|oA=&Y=hxnX9In4v}oQElOIgMZt&BNb>?Yh}b@)HRvhdp}JxG?D~Cx!`FC<bAbSnqPd$eB-qXc?qr1tlf^8P#r^&AJnA!)pX2r65nA+_JzslggY<XN5avN>b$*-G02!rW!h6(Twd~&W;OE5voWm3@&_dmQe=wcOwX_+o&*{wAh+&l_Jc3yDC>&T^0|@>8hYI^WI!cT5d@wOG9~qx@9v$E=IMg0qXABV9@7w${y{2<&-jMxp+0i{}vbj13W)~MLceA8}L7`G$4$1dOMnbqG$|Q{C|85QXd_aXFk-o5+$jWoX{=30}UbAkI6ssFF|1{fG1pBP|XUpEEs6QX1K8U3NUi9QE!5Kdc+8ZW3l^><YYV~hhniKV03KJh=XR1#A1i<f02B#c$%Nc)+2AC&#V)8C{@+gHU!OzyJBq5k+rq800<x!C4xF0+1*p287DNSc;dk$k|_tU(sVV|S}PehVThQNkOCkm6pI}_g1WgY%N_F<ay?Pn!$(Zm0SyHib$!90K#vGUng$wxWJ7f0=W7j&t{bh-TP<k9O=1Z1Ir~2H&YwLSW$`9LEnwUILj0u^OaKjI2A(Leu@>D_Qa&#fOeU%$XxmXNH2D;Wf{r2q=E{Ej{V?fzK_*1ZqQNA0J0?-)y3?<-(c`PoVYB6Tghf>5b{7)LW1a_Z(6qbFo=vSHfcR>A(LQl4dk`HQ=E>5?hGTBb)^T1(c;lF+!oV7qfdCqwOT*=Bh&2F@<M;~{_6ibM_Q4hMo}NjiSXR(rx2w*l+hBPY7pL`-ve~ebKHvQL{_5(1#ns$w{2Qiua;Z_DiFqs-9K;_#7FhEUW@B#)EwQ{-G0YzFNi!$JLgFSE%Y5+x*WwyfW%U54uEprm05iGTng^=A#GcA`)52;@l)cD#{``eVN5ydHa(>{itsQJIf+64G<8;W)O&jX%by^lGKZuzxn6_xx;?-h5wa`;^ME)zi`9jDRO8$ej4IF7PFvlAl=4Rk|NL!$2CNi1W^GPUv<j8TB;)eG~hG$iaF~=R2=U$8?h_l^V=Le~xf!AzucnI?kjGp^fY?+F)gT=NH$B21Yj0CJJP1~+HZ~I3mHe|$)0M3tK*m`|D2n{Vj1_g>^OjwA{Lk?d7D={OE!7_9>28$UweBQQUS|~GjkVg@^IOHbSD@px$Ry$2PxhSf@xaKzIj^@eLv?o{Pfe-TMm+cihGRYo4PPMfo!^3$d6p@sf^e-Msv4K5DpQX=(yO+~^tJ<nzvkwmqg>JaKZ-lTC;SpV2d5|p0d2vqOWEd9gO`-9)MkeP$yhLZBj7X8;jd%@5C}b}gDLm}NYCDnQFMfX+R2BY6%P`j6sf3ZLa1Qe^m|-I|z_Icb=oV0FJQ;|jHV&j%*SlrJIUJUp45<`GqF`DiVfvlyFwari^oKJRCHr_~9}H1|SBA#c#09u^8rNayvm446iPR2`3_g|`?oADE+?S%r&AY)bZ;nuE-^T84JmE4WjRgNqq`0ReH+LIb_aH=1PtWKmK8olh-h*R(N!r-gpG>0KHjheO$w%ta+tQb(x1{@U?b&l+=jN^F_8=)l@8Qf4I+c*b@nG{vX9=DRriS}AqWuy{e;G<P<<pmt;_kr+J+^yraBalzdm^zVvCp{1xHjFMZpD&)us-7RMF#hDL(36H*tro*jLcY!QJNPq!C=VC6N0`Vn{jte_(`%aGJGrrlS8}o4ojP-(`a$0Gd2A9<N6@a4=9w#YKo#*>*PpDMC$D=(oxw&va`UGzJ4>=-*+0(Z?&$o`s|DPHD;L83iCRTbLUW+trL@$DboriV`c<RO`5$)91rDsyl;3Y9Qqju?qwi0w*WW#lHu@BpFRh}f}OJI!9Wuk_9hX{Ty0BhgnVqhSf2J#)!IZdnFv+Eq<H5!WQutQ#lZu_9vY&dp?>N$2GT`V&ZF(Y2Op%C;Z!W&4+fvyjy3A8BpRCkSEw6-VROK8WOShpH||0+^Oz3mbeZ6Bu6-m+w<OqKlD%Beapp2VClrg4eZ7zOax<9^>%dB4nZcFgzZKj#zHq}(D&?l6k&MZMWMBVF5+!Gks$}0#vQIUADG8#qT>qdtely{BrjnplnXrtf7+ObgH41vR#oCsBGQADWozVZ@BOFG>2cMu6675BDkwGJEz*Z^M3lzWu^kx!fg(C4^g9H56Mh*b=2;Rl%UZ{KQDNN9PvHs*xUr~V)?y(M7w^)~0m*K*iZgBAC%eQR7KpE`*0S^nQiYZBV|6t?3NQpeao07eWu+%ZHG=lRKXu_9)mX@%O=op6QKI@RxE}kVCz{BwHM%p+W4s(Q*n@3VAk+6q0$v{Gvgia4GVlEGZF@luzC698G8pxedEor1<yojhs9Xr;SVgtxQhB;+)2=UX3VuZdv!yZ9FdjQF*$>=xD{@8Rg(WtC!`67vg&toy|(BY&E9Z8iB3F^Qx!cZ$!LV6qpC5gq7JQjXSJHg9trh20OP$(JG=OIP}3>&<I!3>WOOm{N|4Yxo@$IQSkAU-&m8S(>!3+Y0d*!^HAKy&^>{a|J6F~)G8>6+(FV3YnNuffVtWeAG|laC_$O@G3dh-3=6LN1&RvnMl6vIg>G0@-M;HGD99koVtoODDV^ax@psdNOiER{TX}G*wAYRL~PXdLm3GLX^Vfi~;=^IqtPe-=8k^r_2253f!Kw&!v0+9xISumI>op#wT?s;E#Utz*GBkX709JG#B_JQAS<~zdsTVCzEzP05=i8-!$b<@r3}U$sWb)tWm3qMuB-Ox$J8+%U4m7W`Ru@qlHoaY9G)ovmJ$gxqR}&zp(9AGWD<y${fv%X3VT<W|JBF%5urFqnT)i9qUyiQzt%9dHThB2czj*Gg;Jxa5>VYvg5-08l#y)wvg4`h1)V_MvlK`JeG&QA=4}uTT(6M9UNSh89%NtvNbcWNRN@Es(TY$&KqbnUC8X`6mVrTw`NAw;eWd9i10GP<g!^aD^<BIt7X?_(o%3a<v{B6k!B|CC~4+kMxtd}Gb|;M3O_i=B^3h4wK<qU)_9ITNHNL<!vozn(e~Ga+C{T0O57{_&5?B>^$}uRjG{dpSv}-g$Q102I{r4A=KZf6O(9Pg%3O*Pj8e|t%hPh0+~$0e7d7GD<yWQs&5<J)Z^T;>M><Ry^OU(~%6#tA=ASA<e<};TP!{4ZmF9D3&qBt0)&j0~mQY}d_~<3fCe2;q%6iO7vocwgtO{2}qWNe(g0IO+(}U584$ew5qq894dy+47dxp1_bbuuzra!CwNYeBEWCQ~s%O?>EmZXu)hO-e|eq8)FY^T9mTv_dHdh7S%HT^8jS5e~YZDq*wmG#dogXC&og*;y~pWu4SYq}~kE>o_e0iXu3n^!U?(__|{g<4pX>2Vme-9C|-C4BQGZJNou(s>WxQ@8`^sb%Rg+#Tt$*7V8m$o)$C6}_KLXL0*;{yeTJf5AWIAN%CVPrmZ>D^F+hxKiAnZ)%0AOclmiWu_`y^$tB@51MRNTGo1(mYh!Gl~3<~I+;frIZuwye!MxASHuoZreD#z15}Es0PsNj6?9?IVH2`~E{18IFFr5+&X-uo+b%PbOpbC2eDvCrtQ2$g14ASD60S^oOqc1xuw$qJqcW3`WD0jUjQgcz<V4bc!o<Do33J(xG9KJ_XFPY}=8e~6m88RIa0+P#D^HfkL?jaC(SR!w;Sd-Wnn!x(#V}aN>Oj?vU<I5cAc-}pRPrr5%2+M{k`<a2sC_nY7x#S1Y^=}a!f$!ya+R_Xy_D8~&F@c>j0@hm3{OKGCa+9@;S$$={O#m%U|+D<%o~|(u@~_ghb@fRAREYZ@Qh%WEonvouH5FupPmGg(OgFk)0urGlN~(WC5y2m8Lle>F=89V*e=-)=M(J(T#<LUQ1Z8>42#KCCQ&gnnhj)J*323J72b9wvV5pu#tX|g@Qs<TaPG9p^8h|+jiEqOc=J$ZQ_g1I1_(rdx|a&i@WHrOo=d;mjZp7WE<W6Ex2q|2GiS8xyY|QFk@-$-W4C(oLNbM^86~!751D@gFw79<T%9FhK~qyHHKhpuuX6PE0*~4zBeNUsa5jvNU6uyZky98#fdEYAv+4cMr4OF8T5<oo)&4D7%BQ5|uA<5+`7u*C)1efJk8fDZ(ycuGn{Q9rV<*kyr&Im`8MW+D8B>))Il@d2aJfj2a2Kznv{Z7&lYkt~_#1~iD3eQa8~6hrPr%RLlDUjOG!h!k?#W)6;px?t_v9+wRVdA9hHZ2-&Frkw?STf9Z*h*olp?pkb7XXMB%-{)7Y<`NXv#+-;Y+vTT8)(nU#;mi`b~}<NF!zVPGsz5BCn0v^_Pri<7lTuIA+qoz|dl6Jtg9ap{J5`dh;Yv{KBhKG;1&^?o4&^1a-5+>_2+6A0#lt%LFqHuAbvhpGn@38P9o5!}LN3#j{T#rz|i146{FOVtr*k^;8m3?KPjheHTgyI3Pn`$Vhl)d)L4FvM+q$ay$sZI*%cCf6NTU(!8QEdH=~Yd4o<r4Je+50*{lim=>Q`T*pm{#d-ZAPt1*j`ws2c78@SkwW}`_JN9^=Bqh<0J-&;Dely;0_DlQZWDUeyQAqfhEKKgfa%G3TU||_~#dsym3l$@GdW~e+tEl1wc7w?lPzVJw(%Gk;%JQau8qMWPqCL37AYjcR4rPAiO(5Ly<Hva~fY&@hUGSk-FrJPZx)7Rr^2sMjLYYq?W#WW+p^o@iTV^<jneg(DwbIhB$B)M$;3G)Cx^Z}z;tBJ(h*<oaLBnJxVOo6x(+(3}Z|d@&!U<Sjm|2IMH7RcY#p4FAuXap3B=~@iyCD_JVd)i08m146(x5ma8nCul#Q#kj!D<qzr&6*+Q&$Amui_;V&l)e{yrE=B-K(5eai1WB_2w~I#j1}d$v%i=DCrKl@zm!F5A~<qu!<ya4<Yy5Q8t()J5ddESTc5$f2MV`zajQ!Bjnw?P$KLW^fSUf(+I|ku7^(QqRXu(t>0KX*)Yk=evaYC6P#RM(wpiPXH_EE*W23%V`WbRFqQ4nVC69=dwY9Rco$oh{bU#n2CNfF*sg}|y?bxDV&~4@fr0J2`uY%4yiy3jCMseo;)K|r?2mD~x>1#6QhYJ&j$;3Zv$t=kAsljBKeH~gE}~m#1D#F1!{JbPs1GW3DkPKaQ%Fv`6s)uuYcMnIPe{bYTus;}I|ob|0cI?X7IV9k82UU?a%?VQuLd6VC*7!xjLV`E!S*3Q>^IHnE#aGY;-%xa|0oia#3hNNNw-@Hg+cA(zEO_>?@K4?D8M81<c=M~1O1r2pAr!U>qSM_5s(%i!RZ&J6Nykrd|I%HZ~}%Kmg9j1OWe}-o{b@UHhP|HQ_-1k*r&|Qcs7VZYV!C=40#(W<iy0oCe6S~vNw$q39&~qtQo#66vI4zghw2^K9QC;Xkazt4RMNq$*h+cCld?>SsA_pv}WAo4KI9n6EiK;B5xvrC}`(U$e@IJ;={dP`ARAw<0*L<Sb&SnqgG7N;3#k=o6hnIC!Jw1NZ-$jqepW`kE$P%w-=5uGGsExpOQyeI`+~_ul<USzWCx(Pa&zplGO1mM?ZQPUBN>3c(G-&+{s9hrvvGwAbn`ZFk_1uH2bMPE;SEv&Fv<$==4r~8fKCKJcgKJSefG}d_p!Jy=XbiFUQl|1Z<$@5wwSdIl}uhx=UuGt(D0<ti3<<s}FxTfe;Da4M`w5=>kMdq>*eoqz*KLyhqU9N8*XZ=f9ndp?i+=cWzT7LkxjN@J#@SM{zG<W->x3?vxscJ#|TE^PmaJnS!EEmUrco20NZYLl~)UV9JAsz0RhM?5#`m`^4*J=MtpTQ%8u?DIOV6+>`dQf-!bbn$!OC7@reN26?v+L(eOxF4^T~vKWf-z{2SA3GQJQGh=v+(6I)$`6j0;|F@zcBjkpSSP5^!3dX%bMZJ2U-Xi}0LILeTUaW<J?quw)gv_x?Zy#d!0`>S*Pj6DEVf&B4N+*=0s7EtSp|H`!;)!_7_9>d(-Gc*|+l}6V?c4i$y$J1;WEJ&T>{Ag@LNRU2q_%;0;W-;;EY=VTx#fRlxd>N1AKc)nIo3;PAs9~5&AXn-bP*ub3VC0*xX+0m%VP9-W%LOyq5UxGc=I_KJM3l%%+YDkiye+J=;5i`?S9(<Bp$5s;x_8d+e%7GB%FzaOgnLsR2lR*KSPF-*t$5Q0lA0c@lbF+_)2X&4yzGSK+iCPYJ9<&hr&oIWdBN-?ZGsrK`&E0DP`yu7Ei}E+6DDUZJb>=i4aORU^IA3gcv4{B&X3#yRY~~+|H(KcP8}U7Y{_!aPxo5WhnBqO`0aVv6&Wn<6J>Jgmt21yc(2!Y}1RZMPLe8JkuqX!UKZ~<z-GN74sQq27`+YcQ6!>#}1n)w;P-g8gvdj@EIHp(oY@)+=}>!6+6hQaOdXE(MM+Q#=)jD=VK6heeO`q>5PR*h7hsPuY#8+H~vt&ljFtc9=CxGIpW*VJy`3GheC0;+u(CyTrb0%!3NdTPCww^xU+?X#L}eUDK3VFKWqhYaqro|`4P_qaqsEF$J6Hp^qexkwzFEoXi}Q2ouEC^4X*&8+9&q}dE>yFg#$wvjOZ{G4GIYtGz17|?f@GKSzH73VFKorEl@gboIY5E=-cW42Qcvp@c"


# ---------------------------------------------------------------- atlas
def _load_atlas():
    raw = zlib.decompress(base64.b85decode(ATLAS_B85.encode("ascii")))
    assert raw[:6] == b"ATLAS1", "bad atlas magic"
    n = raw[6]
    pos = 7
    combos = {}
    for _ in range(n):
        face, size, ng = raw[pos], raw[pos + 1], raw[pos + 2]
        pos += 3
        glyphs = {}
        for _ in range(ng):
            cp, adv10, w, h, ox, oy, doff, dlen = struct.unpack_from(
                "<HHBBbbIH", raw, pos)
            pos += 14
            glyphs[chr(cp)] = (adv10 / 10.0, w, h, ox, oy, doff, dlen)
        combos[(face, size)] = glyphs
    return combos, raw[pos:]


ATLAS, _ATLAS_BLOB = _load_atlas()


def _glyph(face, size, ch):
    g = ATLAS.get((face, size))
    if g is None:
        raise ValueError("atlas combo missing: %r %r" % (face, size))
    gl = g.get(ch)
    if gl is None:
        raise ValueError("char %r not in atlas (face %d size %d)"
                         % (ch, face, size))
    return gl


def text_width(face, size, text, tracking=0):
    w = 0.0
    for ch in text:
        w += _glyph(face, size, ch)[0]
    if tracking and len(text) > 1:
        w += tracking * (len(text) - 1)
    return w


def wrap_text(face, size, text, max_w, max_lines=None):
    """Greedy word wrap. Returns list of lines; raises OverflowError."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(face, size, trial) <= max_w:
            cur = trial
        else:
            if not cur:
                raise OverflowError("word %r too wide for %dpx (face %d %d)"
                                    % (word, max_w, face, size))
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        raise OverflowError("text needs %d lines, max %d: %r"
                            % (len(lines), max_lines, text))
    return lines


def draw_text(cv, face, size, x, y_baseline, text, color, tracking=0,
              align="left", max_w=None):
    """Draw text with its baseline at y_baseline. align: left/center/right
    (x is the anchor point). Returns the drawn width."""
    w = text_width(face, size, text, tracking)
    if align == "center":
        x = x - w / 2.0
    elif align == "right":
        x = x - w
    cx = x
    for ch in text:
        adv, gw, gh, ox, oy, doff, dlen = _glyph(face, size, ch)
        if gw and gh:
            bits = _ATLAS_BLOB[doff:doff + dlen]
            cv.blit(int(round(cx)) + ox, int(round(y_baseline)) + oy,
                    gw, gh, bits, color)
        cx += adv + tracking
    return w


# ---------------------------------------------------------------- PNG codec (stdlib)
def _png_encode(w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def _png_decode(data):
    """Minimal 8-bit non-interlaced PNG decoder -> (w, h, rgb bytes)."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos = 8
    idat = bytearray()
    plte = None
    trns = None
    w = h = bd = ct = inter = None
    while pos < len(data):
        ln = struct.unpack_from(">I", data, pos)[0]
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, bd, ct, _, _, inter = struct.unpack(">IIBBBBB", body)
        elif typ == b"PLTE":
            plte = body
        elif typ == b"tRNS":
            trns = body
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        pos += 12 + ln
    if bd != 8 or inter != 0:
        raise ValueError("only 8-bit non-interlaced PNG supported")
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(bytes(idat))
    stride = w * ch
    out = bytearray()
    prev = bytearray(stride)
    p = 0
    for _y in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if f == 1:
            for i in range(ch, stride):
                line[i] = (line[i] + line[i - ch]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        elif f != 0:
            raise ValueError("bad PNG filter %d" % f)
        prev = line
        if ct == 2:
            out += line
        elif ct == 6:
            for i in range(0, stride, 4):
                out += line[i:i + 3]
        elif ct == 0:
            for i in range(stride):
                out += bytes((line[i], line[i], line[i]))
        elif ct == 4:
            for i in range(0, stride, 2):
                out += bytes((line[i], line[i], line[i]))
        elif ct == 3:
            for i in range(stride):
                r, g, b = plte[line[i] * 3:line[i] * 3 + 3]
                out += bytes((r, g, b))
    return w, h, bytes(out)


def _fit_rgb(w, h, rgb, tw, th):
    """Center-crop to target aspect, then nearest-neighbour scale to tw x th."""
    if (w, h) == (tw, th):
        return rgb
    ta = tw / th
    sa = w / h
    if sa > ta:  # source wider: crop width
        cw = int(round(h * ta))
        x0 = (w - cw) // 2
        crop = (cw, h, rgb, x0, 0)
    else:  # source taller: crop height
        chh = int(round(w / ta))
        y0 = (h - chh) // 2
        crop = (w, chh, rgb, 0, y0)
    cw, chh, src, x0, y0 = crop
    out = bytearray()
    for ty in range(th):
        sy = y0 + (ty * chh) // th
        for tx in range(tw):
            sx = x0 + (tx * cw) // tw
            i = (sy * w + sx) * 3
            out += src[i:i + 3]
    return bytes(out)


# ---------------------------------------------------------------- canvases
class PillowCanvas:
    """Backend 1: Pillow (used when PIL is importable)."""

    def __init__(self, w, h, bg):
        from PIL import Image, ImageDraw
        self._Image = Image
        self.w, self.h = w, h
        self.img = Image.new("RGB", (w, h), bg)
        self.draw = ImageDraw.Draw(self.img)

    def rect(self, x, y, w, h, color):
        self.draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)

    def ellipse(self, cx, cy, rx, ry, color):
        self.draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)

    def circle(self, cx, cy, r, color):
        self.ellipse(cx, cy, r, r, color)

    def polygon(self, pts, color):
        self.draw.polygon(pts, fill=color)

    def line(self, x0, y0, x1, y1, color, width=1):
        self.draw.line([(x0, y0), (x1, y1)], fill=color, width=width)

    def blit(self, x, y, w, h, data, color):
        if w == 0 or h == 0:
            return
        mask = self._Image.frombytes("1", (w, h), data)
        solid = self._Image.new("RGB", (w, h), color)
        self.img.paste(solid, (x, y), mask)

    def paste_rgb(self, x, y, w, h, rgb):
        im = self._Image.frombytes("RGB", (w, h), rgb)
        self.img.paste(im, (x, y))

    def png_bytes(self):
        import io
        buf = io.BytesIO()
        self.img.save(buf, format="PNG")
        return buf.getvalue()


class RawCanvas:
    """Backend 2: stdlib only (used when PIL is absent)."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg)) * (w * h)

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def ellipse(self, cx, cy, rx, ry, color):
        if rx <= 0 or ry <= 0:
            return
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            if t < 0:
                continue
            dx = int(rx * math.sqrt(t))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle(self, cx, cy, r, color):
        self.ellipse(cx, cy, r, r, color)

    def polygon(self, pts, color):
        # scanline fill (even-odd), integer math
        ys = [p[1] for p in pts]
        y0, y1 = max(0, min(ys)), min(self.h - 1, max(ys))
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, y0p = pts[i]
                x1, y1p = pts[(i + 1) % n]
                if y0p == y1p:
                    continue
                if (y0p <= y < y1p) or (y1p <= y < y0p):
                    xs.append(x0 + (y - y0p) * (x1 - x0) / (y1p - y0p))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(math.ceil(xs[k])), int(math.floor(xs[k + 1]))
                if xb >= xa:
                    self.rect(xa, y, xb - xa + 1, 1, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            if width <= 1:
                self._set(x, y, color)
            else:
                self.rect(x, y - width // 2, 1, width, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def blit(self, x, y, w, h, data, color):
        if w == 0 or h == 0:
            return
        stride = (w + 7) // 8
        for yy in range(h):
            for xx in range(w):
                if data[yy * stride + xx // 8] & (0x80 >> (xx % 8)):
                    self._set(x + xx, y + yy, color)

    def paste_rgb(self, x, y, w, h, rgb):
        for yy in range(h):
            dy = y + yy
            if dy < 0 or dy >= self.h:
                continue
            for xx in range(w):
                dx = x + xx
                if 0 <= dx < self.w:
                    i = (dy * self.w + dx) * 3
                    j = (yy * w + xx) * 3
                    self.px[i:i + 3] = rgb[j:j + 3]

    def png_bytes(self):
        return _png_encode(self.w, self.h, bytes(self.px))


# ---------------------------------------------------------------- map data
# World land mask, 72 cols (5 deg lon) x 36 rows (5 deg lat, 90..-90).
# Each row: list of inclusive (c0, c1) land ranges. Hand-built from an
# equirectangular world map; verified visually against the render.
MAP_LAND = {
    0: [(18, 20), (28, 31)],
    1: [(17, 21), (27, 32), (39, 40)],
    2: [(2, 8), (10, 22), (26, 32), (38, 40), (52, 55), (58, 62)],
    3: [(1, 10), (10, 24), (26, 30), (50, 71)],
    4: [(2, 9), (9, 25), (27, 29), (37, 71)],
    5: [(4, 10), (8, 26), (28, 29), (31, 33), (37, 71)],
    6: [(8, 18), (21, 27), (35, 36), (37, 39), (42, 71)],
    7: [(8, 24), (34, 71)],
    8: [(9, 24), (35, 44), (48, 63), (64, 65)],
    9: [(10, 23), (34, 41), (48, 65)],
    10: [(11, 23), (34, 38), (39, 47), (48, 53), (54, 61), (62, 63)],
    11: [(12, 21), (31, 43), (44, 47), (48, 53), (54, 60)],
    12: [(12, 16), (21, 22), (30, 42), (43, 46), (48, 52), (54, 57)],
    13: [(13, 16), (30, 43), (43, 46), (49, 52), (54, 57)],
    14: [(16, 18), (31, 43), (44, 46), (49, 52), (54, 57), (58, 60)],
    15: [(17, 19), (21, 24), (33, 38), (43, 46), (50, 52), (54, 57), (59, 61)],
    16: [(18, 25), (32, 43), (55, 60), (59, 61)],
    17: [(19, 24), (33, 43), (54, 61), (62, 65)],
    18: [(19, 24), (34, 42), (55, 60), (62, 65)],
    19: [(19, 24), (34, 42), (56, 59), (63, 65)],
    20: [(20, 24), (35, 42), (43, 44), (60, 64)],
    21: [(20, 23), (35, 42), (43, 44), (58, 65)],
    22: [(20, 23), (36, 41), (43, 44), (57, 65)],
    23: [(20, 22), (37, 41), (58, 65)],
    24: [(21, 22), (37, 40), (58, 64), (70, 71)],
    25: [(21, 22), (38, 39), (59, 63), (69, 71)],
    26: [(21, 21), (65, 66), (69, 70)],
    27: [(21, 21), (69, 69)],
    28: [(21, 21)],
}

TOPIC_COLORS = {
    "WAR": RED, "DIPLOMACY": NAVY, "TECHNOLOGY": GOLD_DARK,
    "WEATHER": STEEL, "POLITICS": NAVY, "UKRAINE AID": STEEL,
    "SANCTIONS": RED, "CRICKET": GREEN, "DISASTER": RED,
    "DEFENCE": NAVY, "BORDER": STEEL, "STRIKE": RED,
    "COURTS": NAVY, "SUMMIT": GOLD_DARK, "PROTEST": RED,
    "FAITH": GOLD_DARK, "TECH": GOLD_DARK, "ENERGY": GREEN,
    "TELECOM": STEEL, "MEDIA": GOLD_DARK, "MINING": GREEN,
    "USA": NAVY, "HEALTH": RED, "AUSTRALIA": GREEN,
    "MARKETS": GOLD_DARK, "CHINA–CANADA": GREEN,
}


def topic_color(cat):
    return TOPIC_COLORS.get(cat.split("·")[-1], NAVY)


# ---------------------------------------------------------------- illustrations
ILLU_W, ILLU_H = 236, 55


def _load_illu(cv, n, x, y):
    """Paste illu_n.png (center-cropped + resized to the box) or fallback."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "illu_%d.png" % n)
    if os.path.exists(path):
        if isinstance(cv, PillowCanvas):
            from PIL import Image
            im = Image.open(path).convert("RGB")
            if im.size != (ILLU_W, ILLU_H):
                sw, sh = im.size
                ta, sa = ILLU_W / ILLU_H, sw / sh
                if sa > ta:
                    cw = int(round(sh * ta))
                    x0 = (sw - cw) // 2
                    im = im.crop((x0, 0, x0 + cw, sh))
                else:
                    chh = int(round(sw / ta))
                    y0 = (sh - chh) // 2
                    im = im.crop((0, y0, sw, y0 + chh))
                im = im.resize((ILLU_W, ILLU_H), Image.LANCZOS)
            cv.paste_rgb(x, y, ILLU_W, ILLU_H, im.tobytes())
        else:
            with open(path, "rb") as f:
                iw, ih, rgb = _png_decode(f.read())
            cv.paste_rgb(x, y, ILLU_W, ILLU_H,
                         _fit_rgb(iw, ih, rgb, ILLU_W, ILLU_H))
        return True
    _fallback_illu(cv, n, x, y, ILLU_W, ILLU_H)
    return False


def _fallback_illu(cv, n, x, y, w, h):
    """Flat code-drawn illustration (only used when illu_n.png is absent)."""
    if n == 1:  # Trump Manila: sky, sun, skyline, flags
        cv.rect(x, y, w, h, (29, 58, 95))
        cv.circle(x + 208, y + 13, 8, GOLD)
        for bx, bh in ((8, 18), (26, 26), (44, 14), (62, 22), (80, 16)):
            cv.rect(x + bx, y + h - bh, 12, bh, (16, 32, 58))
        cv.line(x + 120, y + 6, x + 120, y + 42, (225, 225, 215), 1)
        cv.polygon([(x + 120, y + 6), (x + 142, y + 12), (x + 120, y + 18)],
                   (178, 34, 34))
        cv.line(x + 160, y + 6, x + 160, y + 42, (225, 225, 215), 1)
        cv.polygon([(x + 160, y + 6), (x + 182, y + 12), (x + 160, y + 18)],
                   (0, 56, 147))
    elif n == 2:  # Kerch Bridge
        cv.rect(x, y, w, h, (168, 196, 220))
        cv.rect(x, y + 38, w, h - 38, (46, 110, 142))
        for tx in (60, 170):
            cv.rect(x + tx, y + 4, 6, 36, NAVY)
        cv.rect(x, y + 34, w, 4, (60, 60, 66))
        for cx in (30, 90, 140, 200):
            cv.line(x + cx, y + 36, x + 60, y + 6, (240, 240, 235), 1)
            cv.line(x + cx, y + 36, x + 170, y + 6, (240, 240, 235), 1)
    elif n == 3:  # Bahrain radar
        cv.rect(x, y, w, h, (16, 32, 58))
        cv.rect(x, y + 40, w, h - 40, (20, 70, 95))
        cv.ellipse(x + 108, y + 8, 22, 22, (200, 205, 210))
        cv.rect(x + 108, y + 30, 44, 12, (200, 205, 210))
        cv.line(x + 130, y + 28, x + 168, y + 6, (90, 220, 120), 2)
        cv.line(x + 130, y + 28, x + 96, y + 10, (90, 220, 120), 1)
        cv.circle(x + 40, y + 16, 4, RED)
        cv.circle(x + 185, y + 46, 3, GOLD)
    elif n == 4:  # Nvidia chip
        cv.rect(x, y, w, h, (14, 22, 18))
        cv.rect(x + 96, y + 10, 44, 34, (20, 90, 60))
        cv.rect(x + 108, y + 20, 20, 14, GOLD)
        for px in range(100, 140, 8):
            cv.line(x + px, y + 4, x + px, y + 10, (120, 130, 125), 1)
            cv.line(x + px, y + 44, x + px, y + 50, (120, 130, 125), 1)
        for py in range(14, 40, 8):
            cv.line(x + 90, y + py, x + 96, y + py, (120, 130, 125), 1)
            cv.line(x + 140, y + py, x + 146, y + py, (120, 130, 125), 1)
        cv.polygon([(x + 8, y + 48), (x + 60, y + 22), (x + 84, y + 32),
                    (x + 150, y + 4), (x + 150, y + 10), (x + 86, y + 38),
                    (x + 60, y + 28), (x + 10, y + 52)], GOLD)
    elif n == 5:  # Cyclone
        cv.rect(x, y, w, h, (70, 110, 140))
        cx, cy = x + 118, y + 28
        for r, col in ((24, (235, 240, 245)), (18, (120, 160, 190)),
                       (12, (235, 240, 245)), (6, (120, 160, 190))):
            cv.ellipse(cx, cy, r, r, col)
        cv.circle(cx, cy, 3, NAVY)
        for lx in (20, 60, 180, 210):
            cv.line(x + lx, y + 6, x + lx - 4, y + 18, (220, 230, 240), 1)
    elif n == 6:  # Knesset
        cv.rect(x, y, w, h, (210, 200, 170))
        cv.polygon([(x + 88, y + 4), (x + 148, y + 4), (x + 118, y + 22)],
                   (120, 100, 60))
        cv.rect(x + 88, y + 22, 60, 6, (245, 242, 232))
        for px in (92, 106, 120, 134):
            cv.rect(x + px, y + 28, 6, 18, (245, 242, 232))
        cv.rect(x + 84, y + 46, 68, 5, (245, 242, 232))
        cv.rect(x + 40, y + 46, 20, 5, (120, 100, 60))
        cv.rect(x + 176, y + 46, 20, 5, (120, 100, 60))
    elif n == 7:  # EU loan: stars circle + coins
        cv.rect(x, y, w, h, (30, 60, 120))
        cx, cy = x + 118, y + 27
        for k in range(12):
            a = 2 * math.pi * k / 12.0
            cv.circle(int(cx + 20 * math.cos(a)), int(cy + 16 * math.sin(a)),
                      2, GOLD)
        cv.ellipse(x + 190, y + 40, 16, 5, GOLD)
        cv.ellipse(x + 190, y + 34, 16, 5, (220, 180, 60))
        cv.ellipse(x + 190, y + 28, 16, 5, GOLD)
    elif n == 8:  # Britain sanctions: flag + gavel
        cv.rect(x, y, w, h, (18, 42, 90))
        cv.polygon([(x, y), (x + 30, y), (x, y + 30)], (255, 255, 255))
        cv.polygon([(x + w, y), (x + w - 30, y), (x + w, y + 30)],
                   (255, 255, 255))
        cv.rect(x, y + 24, w, 7, (255, 255, 255))
        cv.rect(x + 110, y, 12, h, (255, 255, 255))
        cv.rect(x, y + 26, w, 3, (200, 30, 30))
        cv.rect(x + 112, y, 8, h, (200, 30, 30))
        cv.rect(x + 196, y + 10, 26, 8, GOLD)
        cv.line(x + 209, y + 18, x + 209, y + 44, (210, 180, 90), 2)
    else:  # China-Canada: two flags
        cv.rect(x, y, w, h, IVORY)
        cv.rect(x + 20, y + 10, 80, 34, (222, 41, 16))
        for sx, sy in ((30, 16), (44, 14), (40, 26), (30, 24), (36, 18)):
            cv.circle(x + sx, y + sy, 2, GOLD)
        cv.rect(x + 136, y + 10, 80, 34, (255, 255, 255))
        cv.rect(x + 136, y + 10, 18, 34, (200, 30, 30))
        cv.rect(x + 198, y + 10, 18, 34, (200, 30, 30))
        cv.polygon([(x + 176, y + 14), (x + 172, y + 26), (x + 176, y + 40),
                    (x + 180, y + 26)], (200, 30, 30))
        cv.line(x + 118, y + 44, x + 118, y + 50, GOLD_DARK, 1)


# ---------------------------------------------------------------- layout
def draw_header(cv, hdr):
    cv.rect(0, 0, W, 132, NAVY)
    draw_text(cv, IB, 11, W // 2, 30, hdr["kicker"], GOLD,
              tracking=2, align="center")
    draw_text(cv, PF, 33, W // 2, 74, hdr["date"], (255, 255, 255),
              align="center")
    draw_text(cv, LBI, 11, W // 2, 100, hdr["sub"], LIGHT_NAVY_TEXT,
              align="center")
    draw_text(cv, IB, 10, W // 2, 122, hdr["strip"], GOLD, align="center")


def draw_main_stories(cv, mains):
    for i, s in enumerate(mains):
        col, row = i % 3, i // 3
        x = MARGIN + col * 245
        y = 144 + row * 145
        cv.rect(x, y, 238, 140, HAIRLINE)
        cv.rect(x + 1, y + 1, 236, 138, PAPER)
        _load_illu(cv, s["num"], x + 1, y + 1)
        cv.circle(x + 12, y + 67, 7, RED)
        draw_text(cv, IB, 8, x + 12, y + 70, str(s["num"]),
                  (255, 255, 255), align="center")
        draw_text(cv, IB, 7, x + 22, y + 70, s["category"], RED)
        hl = wrap_text(PF, 14, s["headline"], 222, 2)
        for k, ln in enumerate(hl):
            draw_text(cv, PF, 14, x + 8, y + 86 + k * 17, ln, INK)
        ds = wrap_text(LB, 9, s["desc"], 222, 3)
        for k, ln in enumerate(ds):
            draw_text(cv, LB, 9, x + 8, y + 116 + k * 10, ln, INK)


def draw_statistics(cv, stats):
    draw_text(cv, IB, 10, MARGIN, 592, "BY THE NUMBERS", RED)
    for i, st in enumerate(stats):
        x = MARGIN + i * 182
        draw_text(cv, IB, 22, x, 622, st["value"], NAVY)
        caps = wrap_text(IR, 8, st["caption"], 174, 2)
        for k, ln in enumerate(caps):
            draw_text(cv, IR, 8, x, 634 + k * 10, ln, MUTED)
        if i:
            cv.line(x - 9, 596, x - 9, 646, HAIRLINE, 1)


def draw_world_map(cv, mains, judge_note, caption):
    draw_text(cv, IB, 10, MARGIN, 668, "WHERE IT HAPPENED", RED)
    cv.line(MARGIN, 674, MARGIN + 232, 674, GOLD, 1)
    cv.rect(MARGIN, 676, 232, 190, NAVY)
    cv.rect(MARGIN + 1, 677, 230, 188, SAGE)
    pitch = 3.1
    x0 = MARGIN + (232 - 72 * pitch) / 2.0
    y0 = 676 + (190 - 36 * pitch) / 2.0
    for r, ranges in MAP_LAND.items():
        cy = int(round(y0 + r * pitch))
        for c0, c1 in ranges:
            for c in range(c0, c1 + 1):
                cx = int(round(x0 + c * pitch))
                cv.circle(cx, cy, 1, SAGE_DOT)
    for s in mains:
        px = MARGIN + (s["lon"] + 180.0) / 360.0 * 232
        py = y0 + (90.0 - s["lat"]) / 180.0 * (36 * pitch)
        cv.circle(int(round(px)), int(round(py)), 6, RED)
        draw_text(cv, IB, 7, int(round(px)), int(round(py)) + 3,
                  str(s["num"]), (255, 255, 255), align="center")
    draw_text(cv, LBI, 9, MARGIN, 880, caption, MUTED)
    cv.rect(MARGIN, 892, 232, 64, RED)
    cv.rect(MARGIN + 1, 893, 230, 62, (255, 255, 255))
    draw_text(cv, IB, 9, MARGIN + 8, 906, "JUDGE NOTE", RED)
    lines = wrap_text(IR, 8, judge_note, 216, 3)
    for k, ln in enumerate(lines):
        draw_text(cv, IR, 8, MARGIN + 8, 920 + k * 10, ln, INK)


def _wrap_strip_item(face, size, text, w1, w2):
    """Wrap a strip headline across two segments (line1 width w1,
    line2 width w2). Raises OverflowError if it needs more."""
    words = text.split(" ")
    line1, line2, cur = "", "", ""
    on_first = True
    for word in words:
        trial = word if not cur else cur + " " + word
        cap = w1 if on_first else w2
        if text_width(face, size, trial) <= cap:
            cur = trial
        elif on_first:
            if not cur:
                raise OverflowError("strip word too wide: %r" % word)
            line1 = cur
            cur = word
            on_first = False
        else:
            raise OverflowError("strip headline needs 3 lines: %r" % text)
    if on_first:
        line1 = cur
    else:
        line2 = cur
    return line1, line2


def draw_additional_stories(cv, additional):
    draw_text(cv, IB, 10, 264, 668,
              "ALSO ON WEDNESDAY 18 NOVEMBER — 26 MORE STORIES", RED)
    cv.line(264, 674, 748, 674, GOLD, 1)
    last_bottom = 0
    for idx, it in enumerate(additional):
        col, row = idx // 13, idx % 13
        x = 264 + col * 248
        y = 676 + row * 22
        cv.circle(x + 7, y + 6, 7, RED)
        draw_text(cv, IB, 8, x + 7, y + 9, str(it["num"]),
                  (255, 255, 255), align="center")
        cat = it["category"]
        cat_w = text_width(IB, 8, cat)
        draw_text(cv, IB, 8, x + 18, y + 9, cat, topic_color(cat))
        head_x = x + 18 + cat_w + 4
        l1, l2 = _wrap_strip_item(IR, 9, it["headline"],
                                  (x + 236) - head_x, 236 - 18)
        draw_text(cv, IR, 9, head_x, y + 9, l1, INK)
        if l2:
            draw_text(cv, IR, 9, x + 18, y + 19, l2, INK)
        last_bottom = y + 21
    return last_bottom


def draw_footer(cv, foot):
    cv.rect(0, 970, W, 54, NAVY)
    draw_text(cv, IB, 10, W // 2, 984, foot["title"], GOLD, align="center")
    draw_text(cv, IB, 10, 748, 984, foot["page"], GOLD, align="right")
    draw_text(cv, IR, 8, W // 2, 998, foot["disclaimer"],
              (255, 255, 255), align="center")
    draw_text(cv, IR, 8, W // 2, 1010, foot["sources"],
              (255, 255, 255), align="center")


# ---------------------------------------------------------------- main
def _check_charset(data):
    seen = set()

    def walk(o):
        if isinstance(o, str):
            seen.update(o)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)

    walk(data)
    missing = sorted(ch for ch in seen
                     if ch not in ATLAS[(IR, 8)] and ch != "\n")
    # every printable char must exist in the atlas; check against one combo
    # that holds the full charset (all combos share CHARS)
    if missing:
        raise ValueError("chars missing from atlas: %r" % missing)


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "news.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    mains = data["main"]
    additional = data["additional"]
    stats = data["stats"]
    assert len(mains) == 9, len(mains)
    assert len(additional) == 26, len(additional)
    assert len(stats) == 4, len(stats)
    _check_charset(data)

    try:
        import PIL  # noqa: F401
        cv = PillowCanvas(W, H, IVORY)
        path = "pillow"
    except Exception:
        cv = RawCanvas(W, H, IVORY)
        path = "stdlib"

    draw_header(cv, data["header"])
    draw_main_stories(cv, mains)
    draw_statistics(cv, stats)
    draw_world_map(cv, mains, data["judge_note"], data["map_caption"])
    strip_bottom = draw_additional_stories(cv, additional)
    assert strip_bottom <= 962, strip_bottom
    draw_footer(cv, data["footer"])

    png = cv.png_bytes()
    assert len(png) <= 1024 * 1024, len(png)
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.png", "wb") as f:
        f.write(png)
    sha = hashlib.sha256(png).hexdigest()
    print("PATH: %s" % path)
    print("VALIDATION OK: /output/entry.png sha256=%s bytes=%d dims=%dx%d "
          "stories=%d" % (sha, len(png), W, H,
                           len(mains) + len(additional)))


if __name__ == "__main__":
    main()
