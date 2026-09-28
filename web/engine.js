(function(root){
'use strict';
const finite=Number.isFinite;
const profiles={
 vertical:{label:'Heliport / Helideck · Vertical',part:'A',wat:'A',operation:'takeoff',height:[35,70],manoeuvres:['CTO'],page:25},
 short:{label:'Short Field',part:'B',wat:'B',operation:'takeoff',height:[35,400],manoeuvres:['CTO','RTO'],page:85},
 backup:{label:'Heliport / Helideck · Back-Up',part:'C',wat:'C',operation:'takeoff',height:[85,400],manoeuvres:['CTO'],page:120},
 confined:{label:'Confined Area',part:'D',wat:'D',operation:'takeoff',height:[100,400],manoeuvres:['CTO'],page:155},
 offshore:{label:'Offshore Helideck',part:'E',wat:'E',operation:'takeoff',height:[20,20],manoeuvres:['CTO'],page:232},
 clear:{label:'Clear Area',part:'F',wat:'F',operation:'takeoff',height:[30,30],manoeuvres:['CTO','RTO'],page:276},
 heliport:{label:'Heliport / Helideck',part:'G',wat:'A',operation:'landing',height:[50,400],manoeuvres:['LD','BL'],page:338},
 confinedLanding:{label:'Confined Area',part:'H',wat:'D',operation:'landing',height:[100,400],manoeuvres:['LD','BL'],page:365},
 offshoreLevel:{label:'Offshore Helideck · Level approach',part:'I',wat:'E',operation:'landing',height:[40,40],manoeuvres:['BL'],page:401},
 offshoreDescending:{label:'Offshore Helideck · Descending approach',part:'I',wat:'E',operation:'landing',height:[50,50],manoeuvres:['BL'],page:412},
 clearLanding:{label:'Clear Area',part:'J',wat:'F',operation:'landing',height:[50,50],manoeuvres:['LD','BL'],page:454}
};
for(const [key,base,page]of [['confined60','confined',163],['offshore60','offshore',232],['confinedLanding60','confinedLanding',364],['offshoreLevel60','offshoreLevel',401],['offshoreDescending60','offshoreDescending',412]])profiles[key]={...profiles[base],base,label:profiles[base].label+' · 60 KIAS climb',page};
function map(v,a){return a[2]+(v-a[0])/(a[1]-a[0])*(a[3]-a[2]);}
function intersect(paths,v,axis){
 const out=[];
 for(const pts of paths)for(let i=1;i<pts.length;i++){
  const a=pts[i-1],b=pts[i],d=b[axis]-a[axis];
  if(Math.abs(d)<1e-9)continue;
  if(v>=Math.min(a[axis],b[axis])-1e-6&&v<=Math.max(a[axis],b[axis])+1e-6)out.push(a[1-axis]+(b[1-axis]-a[1-axis])*(v-a[axis])/d);
 }
 return out.length?out.reduce((a,b)=>a+b,0)/out.length:null;
}
function interpolate(rows,v){
 const a=rows.filter(x=>finite(x[0])&&finite(x[1])).sort((x,y)=>x[0]-y[0]);
 const exact=a.find(x=>Math.abs(x[0]-v)<1e-6);if(exact)return exact[1];
 for(let i=1;i<a.length;i++)if(v>a[i-1][0]&&v<a[i][0])return a[i-1][1]+(a[i][1]-a[i-1][1])*(v-a[i-1][0])/(a[i][0]-a[i-1][0]);
 return null;
}
function densityAltitude(pa,oat){const theta=1-0.0065*pa*.3048/288.15;const sigma=Math.pow(theta,5.25588)*288.15/(oat+273.15);return 288.15/.0065*(1-Math.pow(sigma,1/4.25588))/.3048;}
function densityOAT(pa,hd){return 288.15*Math.pow(1-.0065*pa*.3048/288.15,5.25588)/Math.pow(1-.0065*hd*.3048/288.15,4.25588)-273.15;}
function wat(chart,pa,oat){
 if(!chart||!finite(pa)||!finite(oat)||pa< -1000||pa>chart.paMax||oat< -40||oat>50)return null;
 const maxOAT=Math.min(50,50-.0019812*pa,densityOAT(pa,chart.densityMax));
 if(oat>maxOAT+.05)return null;
 const rows=chart.curves.map(c=>[c.oat,intersect([c.points],pa,1)]);
 if(!rows.some(r=>r[0]>=oat&&finite(r[1]))){
  const edge=chart.limits.map(c=>intersect([c],pa,1)).filter(finite);
  if(edge.length)rows.push([maxOAT,Math.min(...edge)]);
 }
 const value=interpolate(rows,oat);return finite(value)?Math.min(chart.cap,value):null;
}
function nomogram(n,pa,oat,weight,tdp){
 const d=root.AW139_DISTANCE[n];if(!d)return null;
 const a=d.paAxis;const x=a[0]+(pa-a[2])/(a[3]-a[2])*(a[1]-a[0]);
 const rows=d.temperature.map(t=>[t.value,intersect(t.paths,x,0)]);
 const maxT=Math.min(50,50-.0019812*pa);
 if(d.maxOAT&&maxT>oat){const y=intersect(d.maxOAT,x,0);if(finite(y)&&!rows.some(r=>r[0]>=oat&&finite(r[1])))rows.push([maxT,y]);}
 const y=interpolate(rows,oat);if(!finite(y))return null;
 const dx=d.weight.length===1?intersect(d.weight[0].paths,y,1):interpolate(d.weight.map(w=>[w.value,intersect(w.paths,y,1)]),weight);
 if(!finite(dx))return null;
 if(d.tdp){const dy=interpolate(d.tdp.map(t=>[t.value,intersect(t.paths,dx,0)]),tdp);return finite(dy)?map(dy,d.tdpAxis):null;}
 return map(dx,d.distanceAxis);
}
function offshore(n,pa,oat,weight){
 const d=root.AW139_OFFSHORE?.[n];if(!d)return null;
 const axis=d.kind==='offshoreBL'?d.oatAxis:d.paAxis, v=d.kind==='offshoreBL'?oat:pa;
 const x=axis[0]+(v-axis[2])/(axis[3]-axis[2])*(axis[1]-axis[0]);
 const first=d.kind==='offshoreBL'?d.pressure:d.weight, firstValue=d.kind==='offshoreBL'?pa:weight;
 const y=interpolate(first.map(c=>[c.value,intersect(c.paths,x,0)]),firstValue);
 if(!finite(y))return null;
 const second=d.kind==='offshoreBL'?d.weight:d.temperature, secondValue=d.kind==='offshoreBL'?weight:oat;
 const xx=interpolate(second.map(c=>[c.value,intersect(c.paths,y,1)]),secondValue);
 if(!finite(xx)||xx<d.distanceAxis[0]-.5||xx>d.distanceAxis[1]+.5)return null;
 return map(xx,d.distanceAxis);
}
const backup=[71,84,96,109,121,134,147,159,172,184,197,209,222,234,247,260,272,285,297,310,322,335].map((v,i)=>[85+15*i,v]);
const rearward=[36,44,51,58,65,73,80,87,94,102,109,116,124,131,138,145].map((v,i)=>[100+20*i,v]);
const confinedLD=[36,44,51,58,66,73,80,87,94,102,109,116,123,131,138,145].map((v,i)=>[100+20*i,v]);
function distance(s){
 if(profiles[s.profile]?.base)s={...s,profile:profiles[s.profile].base};
 const c=Number(s.config),p=profiles[s.profile],m=s.manoeuvre;
 let pages=[],value=null,note='Still air. No headwind distance credit applied.';
 const calc=n=>nomogram(n,s.pa,s.oat,s.weight,s.height);
 if(s.mode==='training')return {value:null,pages:[517],note:'Part L, S12-L11: Standard CTO, RTO, landing and balked landing distances are NOT applicable to training procedures.'};
 if(s.profile==='vertical'){pages=[53];value=calc(53);}
 if(s.profile==='short'){pages=[m==='CTO'?111:[103,105,107,109][c]];value=calc(pages[0]);}
 if(s.profile==='backup'){pages=[143,145];value=calc(143);if(finite(value))value-=interpolate(backup,s.height);note+=' CTO = distance from TDP minus Back-Up distance (Figure 4C-7).';}
 if(s.profile==='confined'){pages=[199,197];value=calc(199);if(finite(value))value-=interpolate(rearward,s.height);note+=' CTO = distance from TDP minus rearward climb distance (Figure 4D-7).';}
 if(s.profile==='clear'){pages=[(m==='CTO'?[301,303,305,307]:[293,295,297,299])[c]];value=calc(pages[0]);}
 if(s.profile==='heliport'){
  pages=m==='LD'?[354]:[357];
  value=m==='LD'?(s.height===50?160:null):calc(357);
  if(m==='LD')note='S12-G20: 160 m from 50 ft ALS to the landing point. This distance does not describe an approach from a higher variable LDP.';
 }
 if(s.profile==='confinedLanding'){pages=m==='LD'?[391]:[393];value=m==='LD'?interpolate(confinedLD,s.height):calc(393);}
 if(s.profile==='clearLanding'){
  pages=m==='LD'?[467,469]:[465];
  if(m==='LD'){const touchdown=calc(467),braking=calc(469);value=finite(touchdown)&&finite(braking)?touchdown+braking:null;note='Total landing distance = LDP to touchdown + touchdown to stop (Figures 4J-2/1 and 4J-2/2). Still air.';}
  else value=calc(465);
 }
 if(p.wat==='E'){
  pages=s.profile==='offshore'?[[261,263,265,267][c],269]:[[443,445,447,449][c],441];
  value=offshore(pages[0],s.pa,s.oat,s.weight);
  note='Still air. Offshore horizontal distance only. Check drop-down, helideck height and obstacle clearance against the supplied source chart.';
  if(s.profile==='offshoreDescending')note+=' Descending approach: add 15 ft to the Figure 4I-1 drop-down (S12-I35).';
 }
 if(finite(value)&&value<0)note+=' The calculated CTO endpoint lies behind the takeoff point. Assess rearward geometry in the RFM; no forward-distance comparison is given.';
 return {value:finite(value)&&value>=0?Math.ceil(value):null,pages,note};
}
function assess(s){
 const p=profiles[s.profile];const r={max:null,margin:null,distance:null,distanceMargin:null,watState:'NOT ASSESSABLE',distanceState:'NOT ASSESSABLE',status:'ENTER VALID INPUTS',comparison:'NOT ASSESSABLE',full:'OBSTACLES AND PROFILE TO BE CHECKED',watPage:null,watFigure:null,distancePages:[],note:'',conditions:''};
 if(!p||p.operation!==s.operation||!['standard','training'].includes(s.mode)||![0,1,2,3].includes(Number(s.config)))return r;
 const f=s.mode==='training'?(p.wat==='F'?'LC':'L'):p.wat;
 const chart=root.AW139_WAT[f+'-'+s.config];r.watPage=chart.page;r.watFigure=chart.figure;
 r.conditions='Rotor speed 102%. Heater OFF; ECS not FULL AUTO or MAN HEAT. Still-air calculation; no headwind weight or distance credit. Tailwind prohibited; crosswind and power assurance require separate checks.';
 if(s.mode==='training')r.conditions+=' Part L: P&WC SB 41020 required; torque limiter ON; training hours recorded in the helicopter logbook.';
 if(p.base)r.conditions+=' Alternative 60 KIAS climb selected; verify its separate Path 1 / Path 2 gradient charts.';
 if(s.mode==='training'&&p.wat==='D'&&s.operation==='takeoff')r.conditions+=' Confined takeoff Training delta PI maximum 18% (Standard 23%).';
 if(s.mode==='training'&&p.wat==='E'){r.watPage=512;r.watFigure='Part L applicability';r.status='OFFSHORE NOT COVERED BY PART L';r.note='Parts E and I are not listed in the supplied Training applicability section.';return r;}
 if(![s.weight,s.pa,s.oat].every(finite)||s.weight<=0)return r;
 if(s.heater!=='off'){r.status='HEATER / ECS CONFIGURATION NOT APPLICABLE';return r;}
 let altitudeLimit=p.wat==='E'?5000:p.wat==='D'?10000:14000;
 if(s.profile==='vertical'&&s.height>35)altitudeLimit=7000;
 if(s.pa>altitudeLimit||densityAltitude(s.pa,s.oat)>altitudeLimit+.5){r.status='PRESSURE / DENSITY ALTITUDE LIMIT EXCEEDED';return r;}
 const max=wat(chart,s.pa,s.oat);
 if(!finite(max)){r.status='OUTSIDE DIGITIZED WAT ENVELOPE — CHECK RFM';return r;}
 r.max=Math.min(6400,Math.floor((max+.01)/10)*10);r.margin=Math.round((r.max-s.weight)*10)/10;
 r.watState=r.margin<0?'WEIGHT ABOVE WAT LIMIT':r.margin<50?'NEAR WAT LIMIT — CHECK SOURCE':'WEIGHT WITHIN WAT LIMIT';
 r.status='GRAPH INTERPOLATION · CHECK SOURCE';
 if(s.weight>6400){r.status='ABOVE 6,400 kg — SUPPLEMENT 50 REQUIRED';return r;}
 if(!finite(s.height)||s.height<p.height[0]||s.height>p.height[1]){r.status=`ENTER ${p.operation==='takeoff'?'TDP':'LDP'} ${p.height[0]===p.height[1]?p.height[0]:p.height.join('–')} ft`;return r;}
 if(!p.manoeuvres.includes(s.manoeuvre)){r.status='SELECT AN APPLICABLE MANOEUVRE';return r;}
 const d=distance(s);r.distancePages=d.pages;r.note=d.note;
 if(s.mode==='training'){r.status='PART L WAT ONLY — DISTANCES NOT PROVIDED';return r;}
 // Standard distances are not applicable beyond the selected WAT limit.
 if(r.margin<0){r.status='WAT LIMIT EXCEEDED — DISTANCE NOT ASSESSABLE';r.comparison='WEIGHT LIMIT EXCEEDED';return r;}
 r.distance=d.value;
 if(finite(d.value)&&finite(s.available)&&s.available>=0){r.distanceMargin=Math.round((s.available-d.value)*10)/10;r.distanceState=r.distanceMargin<0?'AVAILABLE DISTANCE INSUFFICIENT':'AVAILABLE DISTANCE SUFFICIENT';r.comparison=r.distanceMargin<0?'DISTANCE LIMIT EXCEEDED':r.margin<50?'CHECK SOURCE — NEAR WAT LIMIT':'NUMERICAL LIMITS SATISFIED';}
 if(!finite(d.value))r.status=p.wat==='E'?'OFFSHORE DISTANCE — READ SOURCE CHART':s.profile==='heliport'&&s.manoeuvre==='LD'&&s.height>50?'160 m APPLIES FROM 50 ft ALS ONLY':'DISTANCE OUTSIDE DIGITIZED CHART — CHECK RFM';
 return r;
}
root.AW139={profiles,assess,wat,nomogram,offshore,distance,interpolate,densityAltitude};
if(typeof module!=='undefined')module.exports=root.AW139;
})(globalThis);
