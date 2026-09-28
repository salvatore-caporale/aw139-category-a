const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
require('../web/wat-data.js');require('../web/distance-data.js');require('../web/offshore-data.js');require('../web/source-catalog.js');const E=require('../web/engine.js');
let checks=0;const ok=(x,m)=>{assert.ok(x,m);checks++;},near=(a,b,t,m)=>ok(Number.isFinite(a)&&Math.abs(a-b)<=t,`${m}: ${a} vs ${b}`);
const base={mode:'standard',profile:'confined',operation:'takeoff',weight:6000,oat:30,pa:0,config:'0',height:100,available:50,heater:'off',manoeuvre:'CTO'};
// Independent published example: S12-J12/J13, PDF 462–463.
near(E.nomogram(467,6000,12,6000,50),400,5,'RFM example touchdown');near(E.nomogram(469,6000,12,6000,50),35,3,'RFM example braking');
const example=E.assess({...base,profile:'clearLanding',operation:'landing',height:50,pa:6000,oat:12,manoeuvre:'LD',available:435});near(example.distance,435,5,'RFM total landing example');ok(example.distanceMargin<0,'Rounded chart estimate compared without hiding a negative margin');
// Independently transcribed RFM table knots, rather than copies of algorithm internals.
near(E.distance({...base,profile:'confinedLanding',operation:'landing',height:180,manoeuvre:'LD'}).value,66,0,'Figure 4H-3 at 180 ft');near(E.distance({...base,profile:'confinedLanding',operation:'landing',height:400,manoeuvre:'LD'}).value,145,0,'Figure 4H-3 at 400 ft');near(E.distance({...base,profile:'heliport',operation:'landing',height:50,manoeuvre:'LD'}).value,160,0,'S12-G20 fixed landing distance');
ok(E.distance({...base,profile:'heliport',operation:'landing',height:200,manoeuvre:'LD'}).value===null,'Do not extend fixed 160 m to a higher LDP');
const fromTDP=E.nomogram(199,0,30,6000,100);near(E.distance(base).value,Math.ceil(fromTDP-36),0,'4D-7 rearward distance subtraction');
near(E.distance({...base,profile:'backup',height:400,pa:6000,oat:20}).value,Math.ceil(E.nomogram(143,6000,20,6000,400)-335),0,'4C-7 Back-Up distance subtraction');
for(const config of ['0','1','2','3'])for(const [profile,p]of Object.entries(E.profiles)){
 const s={...base,profile,operation:p.operation,config,height:p.height[0],manoeuvre:p.manoeuvres[0],weight:5400,available:1000};
 const r=E.assess(s);ok(r.max>4000&&r.max<=6400,`Standard WAT ${profile}/${config}`);
 const t=E.assess({...s,mode:'training'});ok(t.distance===null&&t.distanceMargin===null,`Never substitute Standard distance in Training ${profile}/${config}`);
 if(p.wat==='E')ok(t.max===null&&t.status.includes('NOT COVERED'),'Offshore excluded from Part L');else ok(t.max>4000&&t.max<=6200,`Training WAT ${profile}/${config}`);
}
for(const bad of [{weight:NaN},{pa:NaN},{oat:NaN},{pa:15000},{oat:60},{oat:-41},{pa:-1001},{heater:'on'}])ok(E.assess({...base,...bad}).max===null,'Invalid input or applicability cannot produce a WAT');
const train=E.assess({...base,mode:'training'});ok(train.margin<0&&train.watState.includes('ABOVE'),'Training reduction reflected in negative weight margin');ok(train.status.includes('PART L'),'Part L restriction stated');
ok(E.assess({...base,profile:'vertical',height:70,pa:7000,oat:30}).max===null,'Extended vertical TDP density altitude limit');
ok(E.assess({...base,mode:'training',profile:'confined',pa:10000,oat:20}).max===null,'Confined original altitude limit preserved in Training');
ok(E.assess({...base,weight:6500}).status.includes('SUPPLEMENT 50'),'Missing Supplement 50 not inferred');
ok(E.assess({...base,height:50}).distance===null,'AW139 confined minimum 100 ft, not AW189 height');
ok(E.assess(base).distanceMargin<0,'Negative distance margin retained');
for(const d of Object.values(AW139_WAT)){
 ok(d.curves.length===10,`All temperatures mapped for ${d.figure}`);
 for(const [pa,oat]of [[0,0],[0,30],[2000,20]]){const w=E.wat(d,pa,oat);ok(w===null||(w>=4000&&w<=6800),`Plausible digitization ${d.figure}`);}
}
for(const n of [...Object.values(AW139_WAT).map(d=>d.page),...Object.values(AW139_DISTANCE).map(d=>d.page),...Object.values(AW139_OFFSHORE).map(d=>d.page),...Object.values(E.profiles).map(p=>p.page)]){
 ok(AW139_SOURCES.some(s=>s.page===n),`Source catalog contains PDF ${n}`);ok(fs.existsSync(path.join(__dirname,`../web/charts/p${n}.webp`)),`Source image exists PDF ${n}`);
}
console.log(`${checks} checks passed. Published RFM example within graphical reading tolerance; not operational certification.`);
