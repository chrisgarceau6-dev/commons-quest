const $=s=>document.querySelector(s);
// absolute asset URL: CSS variables holding url() resolve against the stylesheet, so give them full URLs
const asset=p=>new URL(p,document.baseURI).href;
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fmt=n=>Math.round(n||0).toLocaleString();
const f1=n=>(Math.round((n||0)*10)/10).toLocaleString();
const pad=n=>String(n).padStart(2,"0");
const dayId=(d=new Date(Date.now()-4*3600e3))=>d.getFullYear()+"-"+pad(d.getMonth()+1)+"-"+pad(d.getDate());
const menuKey=(d=new Date())=>pad(d.getMonth()+1)+"/"+pad(d.getDate())+"/"+d.getFullYear();
const fromId=id=>{const [y,m,d]=id.split("-").map(Number);return new Date(y,m-1,d)};
const niceDay=id=>fromId(id).toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric"});
const MEALS={B:"Breakfast",L:"Lunch",D:"Dinner",N:"Late Night",G:"Grab 'n Go"};
// Tracked stats a person can pin to the top of the home screen (up to 3). "min" = reach it, "max" = stay under it.
const STATS={
  protein:{lab:"Protein",u:"g",get:t=>t.p,def:120,dir:"min",bg:"#e3f7ff",fg:"#1d6fa5",bar:"var(--pwr)"},
  carbs:{lab:"Carbs",u:"g",get:t=>t.c,def:275,dir:"min",bg:"#fff7d6",fg:"#8a6a00",bar:"var(--gold)"},
  fat:{lab:"Fat",u:"g",get:t=>t.f,def:78,dir:"max",bg:"#ffe9e0",fg:"#b23c17",bar:"#ff8a5c"},
  fiber:{lab:"Fiber",u:"g",get:t=>t.fi,def:28,dir:"min",bg:"#e4f8e4",fg:"#1f7a33",bar:"var(--green)"},
  sugar:{lab:"Sugar",u:"g",get:t=>t.su,def:50,dir:"max",bg:"#ffe6f6",fg:"#b0287f",bar:"var(--sug)"},
  sodium:{lab:"Sodium",u:"mg",get:t=>t.na,def:2300,dir:"max",bg:"#fff0de",fg:"#b5520e",bar:"var(--na)"},
  satfat:{lab:"Sat fat",u:"g",get:t=>t.sf,def:20,dir:"max",bg:"#f1e9ff",fg:"#6a3fb5",bar:"#a77bff"},
  chol:{lab:"Cholesterol",u:"mg",get:t=>t.ch,def:300,dir:"max",bg:"#eef1f5",fg:"#4a5568",bar:"#8fa3bf"}
};
const DEF_TRACK=[{k:"protein",v:120,dir:"min"},{k:"fiber",v:28,dir:"min"},{k:"sodium",v:2300,dir:"max"}];
// goals: {kcal, kmode:"reach"|"near", track:[{k,v,dir}]}. Also upgrades the old {kcal,protein,sugar,sodium} shape.
function normGoals(g){g=g||{};const out={kcal:+g.kcal||2400,kmode:g.kmode==="near"?"near":"reach"};
  if(Array.isArray(g.track))out.track=g.track.filter(x=>x&&STATS[x.k]).slice(0,3).map(x=>({k:x.k,v:+x.v||STATS[x.k].def,dir:x.dir==="max"?"max":"min"}));
  else if(g.protein!=null)out.track=[{k:"protein",v:+g.protein,dir:"min"},{k:"sugar",v:+g.sugar||50,dir:"max"},{k:"sodium",v:+g.sodium||2300,dir:"max"}];
  else out.track=DEF_TRACK.map(x=>({...x}));
  return out}
const trackOf=k=>GOALS.track.find(x=>x.k===k);
const CC_NAMES=["Harvest Market","Deli Delish","Green Fields","The Grill","Star Ginger","Tamales","Tavola","Yum! Bakery","Wasabi","People's Organic Coffee"];
const HALLS={
  berk:{name:"Berkshire",boss:"Berkshire Bear",locs:[3],spr:"bear",x:92,y:452,side:"r"},
  wor:{name:"Worcester",boss:"Worcester Wyrm",locs:[0],spr:"wyrm",x:225,y:83,side:"r"},
  frank:{name:"Franklin",boss:"Frankenfrank",locs:[1],spr:"frank",x:286,y:208,side:"l"},
  hamp:{name:"Hampshire",boss:"Hampshire Hog",locs:[2],spr:"hog",x:90,y:384,side:"r"},
  cc:{name:"Campus Center",boss:"The Blue Wall",locs:[],spr:"wall",x:163,y:118,retail:true,side:"l"}
};
const SHEETS={berk:{src:'assets/img/bear.png',fw:84,fh:84},wor:{src:'assets/img/wyrm.png',fw:82,fh:72},frank:{src:'assets/img/frank.png',fw:76,fh:84},hamp:{src:'assets/img/hog.png',fw:84,fh:84},cc:{src:'assets/img/wall.png',fw:84,fh:84}};
const PINS={berk:'assets/img/pin_berk.png',berk_h:46,wor:'assets/img/pin_wor.png',wor_h:46,frank:'assets/img/pin_frank.png',frank_h:46,hamp:'assets/img/pin_hamp.png',hamp_h:46,cc:'assets/img/pin_cc.png',cc_h:46};
let SPR={},DATA=[],LOCS=[],ST=[],DATES=[],BYK=new Map(),TIDX=-1;
let DAYS={},CUSTOM=[],GOALS=normGoals(),FAVES=[];
const HEROES=[["og","Hero 1"],["p2","Hero 2"],["p3","Hero 3"],["p4","Hero 4"],["p5","Hero 5"],["g1","Hero 6"],["g2","Hero 7"],["g3","Hero 8"],["g4","Hero 9"],["g5","Hero 10"],["g6","Hero 11"]];
const GPRE={bulk:{kcal:3300,protein:150,kmode:"reach"},maintain:{kcal:2800,protein:150,kmode:"near"},cut:{kcal:2200,protein:150,kmode:"near"}};
let PROFILE={name:"",hero:"og",setup:false,home:"",diet:"any",nope:[],avoid:[]},IS_OWNER=false;
const HOMES=[["berk","Berkshire"],["wor","Worcester"],["frank","Franklin"],["hamp","Hampshire"]];
const DIETS=[["any","Anything"],["veg","Vegetarian"],["plant","Plant-based"],["halal","Halal"]];
// allergen codes come from UMass Dining's own allergen data (see scripts/scrape_menu.py)
const ALLERGENS=[["P","Peanuts"],["N","Tree nuts"],["M","Milk"],["E","Eggs"],["W","Wheat"],["G","Gluten"],["S","Soy"],["X","Sesame"],["F","Fish"],["K","Shellfish"],["C","Corn"]];
const ALG_NAME=Object.fromEntries(ALLERGENS);
function allergenHits(r){const a=r[17]||"",av=PROFILE.avoid||[];return av.filter(c=>a.includes(c))}
function allergenOK(r){return !allergenHits(r).length}
function dietOK(r){const f=r[9]||"",d=PROFILE.diet||"any";return d==="any"||(d==="veg"&&/[VP]/.test(f))||(d==="plant"&&f.includes("P"))||(d==="halal"&&f.includes("H"))}
function noped(r){return (PROFILE.nope||[]).includes(r[0])||!allergenOK(r)}
// what this person actually eats: how many times each food name shows up in their history
let TASTE=null;function taste(){if(TASTE)return TASTE;const m=new Map();for(const d of Object.values(DAYS))for(const e of (d.items||[]))if(!String(e.k).startsWith("mine|")){const n=e.n;m.set(n,(m.get(n)||0)+1)}return TASTE=m}
function hallOfKey(k){const r=BYK.get(k);if(!r)return null;for(const [hk] of HOMES)if(r._l.some(i=>HALLS[hk].locs.includes(i)))return hk;return null}
function homeHall(){if(PROFILE.home&&HALLS[PROFILE.home])return PROFILE.home;const c={};for(const d of Object.values(DAYS))for(const e of (d.items||[])){const h=hallOfKey(e.k);if(h)c[h]=(c[h]||0)+1}
  const best=Object.entries(c).sort((a,b)=>b[1]-a[1])[0];return best?best[0]:"berk"}
function loadProfile(){try{const p=JSON.parse(localStorage.getItem("gq-profile")||"null");if(p)PROFILE={...PROFILE,...p}}catch(e){}applyHero()}
function saveProfile(){try{localStorage.setItem("gq-profile",JSON.stringify(PROFILE))}catch(e){}if(IS_OWNER)pushDoc("meta/profile",{...PROFILE})}
function applyHero(){const id=HEROES.some(h=>h[0]===PROFILE.hero)?PROFILE.hero:"og";document.documentElement.style.setProperty("--hero",`url(${asset(`assets/img/hero_${id}.png`)})`)}
const S={tab:"map",hall:null,meal:null,q:"",pq:"",ptab:"items",sel:null,logDay:null,month:null,fight:[],adding:false,dayOpen:null};
let pushDoc=()=>{};
const SND={on:false,ctx:null,buf:{},music:null,cur:null,want:null};
try{SND.on=localStorage.getItem("gq-sound")==="1"}catch(e){}
function sndInit(){if(SND.ctx)return true;try{if(navigator.audioSession)navigator.audioSession.type="playback"}catch(e){}
  try{SND.ctx=new(window.AudioContext||window.webkitAudioContext)();SND.master=SND.ctx.createGain();SND.master.connect(SND.ctx.destination);return true}catch(e){toast("Sound isn't supported here");return false}}
function sndLoad(n){if(!SND.buf[n])SND.buf[n]=fetch("assets/audio/"+n+".mp3").then(r=>{if(!r.ok)throw new Error("HTTP "+r.status);return r.arrayBuffer()}).then(a=>new Promise((res,rej)=>SND.ctx.decodeAudioData(a,res,rej))).catch(e=>{delete SND.buf[n];throw e});return SND.buf[n]}
function sfx(n,vol=.8){if(!SND.on||!SND.ctx)return;sndLoad(n).then(b=>{const src=SND.ctx.createBufferSource();src.buffer=b;const g=SND.ctx.createGain();g.gain.value=vol;src.connect(g);g.connect(SND.master);src.start()}).catch(()=>{})}
function stopMusic(){const m=SND.music;SND.music=null;SND.cur=null;if(m&&SND.ctx){const t=SND.ctx.currentTime;m.g.gain.setTargetAtTime(0,t,.12);try{m.src.stop(t+.6)}catch(e){}}}
function music(n){SND.want=n;if(!SND.on||!SND.ctx||SND.cur===n)return;stopMusic();SND.cur=n;
  sndLoad(n).then(b=>{if(SND.cur!==n||!SND.on)return;const src=SND.ctx.createBufferSource();src.buffer=b;src.loop=true;const g=SND.ctx.createGain();g.gain.value=0;g.gain.setTargetAtTime(.5,SND.ctx.currentTime,.25);src.connect(g);g.connect(SND.master);src.start();SND.music={src,g}})
  .catch(e=>{SND.cur=null;toast("Music couldn't load ("+(e&&e.message||"error")+")")})}
function jingle(){if(!SND.on||!SND.ctx)return;const m=SND.music,t=SND.ctx.currentTime;if(m){m.g.gain.setTargetAtTime(.06,t,.1);setTimeout(()=>{if(SND.music===m)m.g.gain.setTargetAtTime(.5,SND.ctx.currentTime,.4)},5200)}sfx("legendary",1)}
function toggleSound(){SND.on=!SND.on;try{localStorage.setItem("gq-sound",SND.on?"1":"0")}catch(e){}
  if(SND.on){if(!sndInit()){SND.on=false;return}SND.ctx.resume();const w=SND.want;SND.cur=null;music(w);sfx("sfx_coin");["sfx_hit","sfx_ko","legendary"].forEach(n=>sndLoad(n).catch(()=>{}))}else stopMusic();renderHUD()}
document.addEventListener("pointerdown",()=>{if(SND.on&&(!SND.ctx||SND.ctx.state!=="running")){if(sndInit()){SND.ctx.resume();const w=SND.want;SND.cur=null;music(w)}}},true);


function spr(name,px,label){const d=SPR[name];if(!d)return"";const[rows,pal]=d;const w=Math.max(...rows.map(r=>r.length)),h=rows.length,paths={};
  rows.forEach((r,y)=>{let x=0;while(x<r.length){const c=r[x];if(c==="."){x++;continue}const s0=x;while(x<r.length&&r[x]===c)x++;(paths[c]=paths[c]||[]).push(`M${s0} ${y}h${x-s0}v1h-${x-s0}z`)}});
  return `<svg width="${w*px}" height="${h*px}" viewBox="0 0 ${w} ${h}" shape-rendering="crispEdges" ${label?`role="img" aria-label="${esc(label)}"`:'aria-hidden="true"'}>${Object.entries(paths).map(([c,v])=>`<path fill="${pal[c]}" d="${v.join("")}"/>`).join("")}</svg>`}

const X=r=>[r[11],r[12],r[13],r[14],r[15],r[16]];
const fromRow=r=>({k:r._k,n:r[0],s:r[1],v:[r[2]||0,r[3]||0,r[4]||0,r[5]||0],x:X(r)});
const ckey=c=>"mine|"+c.n.toLowerCase()+"|"+String(c.s||"1 serving").toLowerCase();
const fromCustom=c=>({k:ckey(c),n:c.n,s:c.s||"1 serving",v:[+c.k||0,+c.p||0,+c.c||0,+c.f||0],x:[c.fi??null,c.su??null,c.sf??null,null,null,c.na??null]});
function lookup(k){if(k.startsWith("mine|")){const c=CUSTOM.find(c=>ckey(c)===k);return c?fromCustom(c):null}const r=BYK.get(k);return r?fromRow(r):null}
function totals(items){const t={k:0,p:0,c:0,f:0,fi:0,su:0,sf:0,na:0,ch:0,n:0};for(const e of items||[]){const q=e.q||1;t.k+=e.v[0]*q;t.p+=e.v[1]*q;t.c+=e.v[2]*q;t.f+=e.v[3]*q;const x=e.x||[];t.fi+=(x[0]||0)*q;t.su+=(x[1]||0)*q;t.sf+=(x[2]||0)*q;t.na+=(x[5]||0)*q;t.ch+=(x[4]||0)*q;t.n++}return t}
// "reach": beat the boss by eating at least the calorie goal. "near": land within 10% of it (cut / maintain).
function checks(t){const near=GOALS.kmode==="near";const cal=near?t.k>=GOALS.kcal*0.9:t.k>=GOALS.kcal;const over=near&&t.k>GOALS.kcal*1.1;
  const tr=GOALS.track.map(g=>{const val=STATS[g.k].get(t);return{...g,val,ok:g.dir==="min"?val>=g.v:val<=g.v}});
  return{cal,over,tr}}
const stars=c=>{const all=[...c.tr.map(x=>x.ok),...(c.over?[false]:[])];return{n:all.filter(Boolean).length,L:all.length}};
const statName=x=>x.dir==="max"?STATS[x.k].lab.toLowerCase()+" cap":STATS[x.k].lab.toLowerCase();
const statNum=(k,v)=>STATS[k].u==="mg"&&v>=1000?(v/1000).toFixed(1)+"k":fmt(v);
function grade(items){if(!items||!items.length)return"empty";const c=checks(totals(items));if(!c.cal)return"none";const{n,L}=stars(c);return n===L?"legend":n===L-1&&n>0?"rare":n>0?"unc":"none"}
function dayXP(items){if(!items||!items.length)return 0;const c=checks(totals(items));const{n,L}=stars(c);return(c.cal?100:0)+(L?Math.round(100*n/L):0)+(grade(items)==="legend"?100:0)}
const curDay=()=>S.logDay||dayId();
const dayItems=id=>(DAYS[id]&&DAYS[id].items)||[];

function curMeal(){const n=new Date(),h=n.getHours()+n.getMinutes()/60;return h<10.5?"B":h<16.5?"L":h<21?"D":"N"}
const servedToday=r=>TIDX<0||((r[10]>>TIDX)&1)===1;
function hallRows(hk){const h=HALLS[hk];return DATA.filter(r=>r._l.some(i=>h.locs.includes(i))&&servedToday(r))}
function stationOf(r,hk){return HALLS[hk].retail?LOCS[r._l.find(i=>HALLS[hk].locs.includes(i))]:(ST[r[8]]||"Other")}
const isBig=r=>(r[2]||0)>=150&&(r[2]||0)<=1400&&!/sauce|dressing|topping|broth|condiment|chutney|gravy|syrup/i.test(r[0]);
function comboFor(hk,meal){
  const t=totals(dayItems(curDay()));const rem=GOALS.kcal-t.k;
  let rows=hallRows(hk).filter(r=>HALLS[hk].retail||!meal||r[7].includes(meal)||r[7].includes("G")).filter(isBig).filter(r=>dietOK(r)&&!noped(r)&&!/dessert|ice cream|pastr|bakery/i.test(ST[r[8]]||"")&&!/turnover|cookie|brownie|muffin|donut|doughnut|cake|cupcake|pie\b|danish|croissant|soft serve|sundae/i.test(r[0]));
  const near=GOALS.kmode==="near",T=taste(),score=r=>(near?(r[3]||0)/Math.max(r[2],1)*2000:r[2])+Math.min(3,T.get(r[0])||0)*180;
  const seen=new Set();rows=rows.filter(r=>!seen.has(r[0])&&seen.add(r[0]));
  if(rem<=0){if(near||!trackOf("protein"))return{mode:"done",items:[],rem:0};return{mode:"pwr",items:rows.filter(r=>(r[3]||0)>=12).sort((a,b)=>(b[3]+Math.min(3,T.get(b[0])||0)*8)-(a[3]+Math.min(3,T.get(a[0])||0)*8)).slice(0,3),rem:Math.max(0,trackOf("protein").v-t.p)}}
  rows.sort((a,b)=>score(b)-score(a));const pick=[];let left=rem;
  for(const r of rows){if(left<=0||pick.length>=5)break;if(near&&r[2]>left*1.15)continue;pick.push(r);left-=r[2]}
  return{mode:"kcal",items:pick,rem}}
function worthWalk(hk){const locs=HALLS[hk].locs;const fav=new Set(FAVES);
  const T=taste();const rows=DATA.filter(r=>servedToday(r)&&!r._l.some(i=>locs.includes(i))&&isBig(r)&&(r[2]||0)>=350&&dietOK(r)&&!noped(r));
  const sc=r=>(fav.has(r._k)?1e4:0)+Math.min(3,T.get(r[0])||0)*400+r[2];rows.sort((a,b)=>sc(b)-sc(a));return rows[0]}
function nextServed(k){const base=BYK.get(k);if(!base)return null;let best=null;
  for(const r of DATA){if(r[0]!==base[0])continue;for(let i=Math.max(TIDX,0);i<DATES.length;i++){if((r[10]>>i)&1){if(!best||i<best.i)best={i,r};break}}}
  return best}

function loadLocal(){try{const s=JSON.parse(localStorage.getItem("gq-state")||"null");if(s){DAYS=s.days||{};CUSTOM=s.foods||[];GOALS=normGoals(s.goals);FAVES=s.faves||[]}}catch(e){}
  try{const old=JSON.parse(localStorage.getItem("macro-custom-foods")||"null");if(Array.isArray(old)&&!CUSTOM.length)CUSTOM=old}catch(e){}}
function saveLocal(){TASTE=null;try{localStorage.setItem("gq-state",JSON.stringify({days:DAYS,foods:CUSTOM,goals:GOALS,faves:FAVES}))}catch(e){}}
function persistDay(id){saveLocal();pushDoc("days/"+id,{day:id,items:dayItems(id),celebrated:!!(DAYS[id]&&DAYS[id].celebrated)})}
function persistMeta(name){saveLocal();const body=name==="foods"?{items:CUSTOM}:name==="goals"?{...GOALS}:{keys:FAVES};pushDoc("meta/"+name,body)}

function eat(item,q){const id=curDay();const d=DAYS[id]||(DAYS[id]={items:[]});d.items=d.items||[];
  const e=d.items.find(x=>x.k===item.k);if(e)e.q=Math.round((e.q+q)*2)/2;else d.items.push({k:item.k,n:item.n,s:item.s,v:item.v,x:item.x,q});
  persistDay(id);return item.v[0]*q}
function setQty(id,k,dq){const d=DAYS[id];if(!d)return;const e=d.items.find(x=>x.k===k);if(!e)return;e.q=Math.round((e.q+dq)*2)/2;if(e.q<=0)d.items=d.items.filter(x=>x!==e);persistDay(id)}
function toggleFav(k){FAVES=FAVES.includes(k)?FAVES.filter(x=>x!==k):[...FAVES,k];persistMeta("faves")}
function toast(t){document.querySelectorAll(".toast").forEach(x=>x.remove());const el=document.createElement("div");el.className="toast";el.textContent=t;document.body.appendChild(el);setTimeout(()=>el.remove(),1800)}
function buzz(){try{navigator.vibrate&&navigator.vibrate(25)}catch(e){}}

function renderHUD(){
  const xp=Object.values(DAYS).reduce((a,d)=>a+dayXP(d.items),0),lvl=1+Math.floor(xp/500),into=xp%500;
  let streak=0;for(let i=0;i<400;i++){const g=grade(dayItems(dayId(new Date(Date.now()-4*3600e3-i*864e5))));if(i===0&&(g==="none"||g==="empty"||g==="unc"))continue;if(g==="legend"||g==="rare")streak++;else break}
  const loot=Object.values(DAYS).filter(d=>["legend","rare","unc"].includes(grade(d.items))).length;
  $("#hud").innerHTML=`<div class="portrait"><div class="face" aria-hidden="true"></div><span class="lvl">${lvl}</span></div>
   <div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:5px"><div style="display:flex;justify-content:space-between;align-items:baseline;gap:6px"><span class="arc" style="font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc((PROFILE.name||"PLAYER").toUpperCase())}</span><span style="font-weight:700;font-size:14px;color:#e6dcff">${into}/500 XP</span></div><div class="xpbar"><i style="width:${into/5}%"></i></div></div>
   <div style="display:flex;flex-direction:column;gap:5px;flex:none"><span class="chip" title="Days in a row with rare or better loot">${spr("flame",3)}${streak}</span><span class="chip" title="Days with loot">${spr("chest",2)}${loot}</span></div>
   <div style="display:flex;flex-direction:column;gap:5px;flex:none"><button class="btn ${SND.on?"b-green":"b-cream"} gear" style="height:32px;font-size:16px" data-act="sound" aria-pressed="${SND.on}" aria-label="${SND.on?"Mute music":"Turn music on"}"><svg width="18" height="18" viewBox="0 0 12 12" shape-rendering="crispEdges" aria-hidden="true"><path fill="#2b1d3a" d="M1 4h3v4h-3zM4 3h1v6h-1zM5 2h1v8h-1z"/>${SND.on?'<path fill="#2b1d3a" d="M8 4h1v4h-1zM10 2h1v8h-1z"/>':'<path fill="#c2273a" d="M7 4h1v1h-1zM8 5h1v1h-1zM9 6h1v1h-1zM10 7h1v1h-1zM10 4h1v1h-1zM9 5h1v1h-1zM8 6h1v1h-1zM7 7h1v1h-1z"/>'}</svg></button><button class="btn b-cream gear" style="height:32px;font-size:16px" data-act="goals" aria-label="Settings">⚙</button></div>`}

function isWinter(){const d=new Date(),m=d.getMonth();return m===11||m===0||m===1||(m===2&&d.getDate()<15)}
function mapSrc(){return `assets/img/map_${isWinter()?"snow_":""}${isNight()?"night":"day"}.png`}
const WALKS=[[243,446,206,459],[159,437,152,407],[331,321,332,289],[56,101,62,129],[300,387,257,401],[263,169,264,197]];
function campusLife(){const P=(x,y)=>`left:${(x/368*100).toFixed(2)}%;top:${(y/478*100).toFixed(2)}%`;
  const w=WALKS.map((s,i)=>{const dur=10+i*2.3,flip=s[2]<s[0];return `<span class="walker2" style="--x0:${(s[0]/368*100).toFixed(2)}%;--y0:${(s[1]/478*100).toFixed(2)}%;--x1:${(s[2]/368*100).toFixed(2)}%;--y1:${(s[3]/478*100).toFixed(2)}%;--k:${i%4};animation-duration:${dur}s,.5s;animation-delay:${-i*3.1}s,0s;"></span>`}).join("");
  return `<div class="life" aria-hidden="true">${isNight()?w.split("</span>").slice(0,3).join("</span>")+"</span>":w}<span class="bus${isNight()?" lit":""}"></span></div>`}
function isNight(){const h=new Date().getHours()+new Date().getMinutes()/60;return h>=18.5||h<6.25}
function renderMap(){
  const id=dayId(),items=dayItems(id),t=totals(items),c=checks(t),g=grade(items),pct=Math.min(100,t.k/GOALS.kcal*100);
  const miss=[...c.tr.filter(x=>!x.ok).map(statName),...(c.over?["calories within 10% of goal"]:[])].join(", ");
  const capsTxt=c.tr.some(x=>x.dir==="max")?" Stay under your caps.":"";
  const lootTxt=!t.n?"Eat something to start today's quest.":!c.cal?(GOALS.kmode==="near"?`${fmt(GOALS.kcal-t.k)} DMG left to reach your target.`:`${fmt(GOALS.kcal-t.k)} DMG left to beat the boss.`)+(c.tr.length?" Loot needs calories first.":""):g==="legend"?"LEGENDARY secured."+capsTxt:`Boss down: <b>${g==="rare"?"RARE":g==="unc"?"UNCOMMON":"no"}</b> loot so far. Missing: ${miss}.`;
  const meal=curMeal();
  const pins=Object.entries(HALLS).map(([k,h])=>{const rows=hallRows(k);const on=openNow(k);const open=on?on.open:h.retail?rows.length>0:rows.some(r=>r[7].includes(meal));
    const status=on?on.txt:!rows.length?"No menu":open?(h.retail?"Open today":MEALS[meal]):"No "+MEALS[meal].toLowerCase();
    return `<button class="pin ${h.side}${({berk:" tr",hamp:" tr",wor:" tr"})[k]||""}${open?"":" closed"}" data-act="hall" data-h="${k}" style="left:${h.x/368*100}%;top:${h.y/478*100}%" aria-label="Fight ${esc(h.boss)} at ${esc(h.name)}"><span class="spr">${PINS[k]?`<img src="${PINS[k]}" alt="" style="display:block;height:${PINS[k+'_h']}px;image-rendering:pixelated;filter:drop-shadow(0 3px 0 rgba(18,12,43,.55))">`:spr(h.spr,2.25)}</span><span class="lbl" title="${esc(status)}"><i style="background:${open?"#3fd16a":"#8a7aa8"}"></i>${esc(h.name)}</span></button>`}).join("");
  const HH=homeHall(),cb=comboFor(HH,meal),ww=worthWalk(HH),usual=usuals();
  const faves=FAVES.map(k=>({k,ns:nextServed(k)})).filter(f=>f.ns).sort((a,b)=>a.ns.i-b.ns.i).slice(0,4);
  $("#view").innerHTML=`
  ${PROFILE.demo?`<div class="banner2" style="background:var(--gold)"><span>Demo mode · sample data</span><button class="btn b-cream" style="padding:4px 8px;font-size:13px" data-act="enddemo">Make it mine</button></div>`:""}
  ${S.logDay&&S.logDay!==id?logBanner():""}
  <section class="panel quest">
    <div style="display:flex;justify-content:space-between;align-items:center"><span class="arc" style="font-size:10px;color:var(--red)">DAILY QUEST</span><span style="font-weight:600;font-size:14px;color:var(--dim)">${niceDay(id)}</span></div>
    <div style="font-weight:700;font-size:26px;line-height:1">${fmt(t.k)} <span style="font-size:16px;color:var(--dim)">/ ${fmt(GOALS.kcal)} DMG</span></div>
    <div class="road"><div class="track"><i style="width:${pct}%"></i></div>
      <div class="walker" style="left:${Math.max(6,Math.min(88,pct))}%"><div class="herospr walk" style="--s:1.2;position:static"></div></div>
      <div class="chest">${spr("chest",3.6,"Loot chest")}</div></div>
    ${statTiles(c)}
    <div class="loot"><span class="tag">LOOT</span><span>${lootTxt}</span></div>
    <form class="quick" id="qlform" autocomplete="off"><input id="qlin" type="text" enterkeyhint="go" placeholder="Type what you ate… “2 slices pepperoni pizza at berk”" aria-label="Type what you ate"><button class="btn b-green" type="submit" aria-label="Find it">GO</button></form>
  </section>
  ${todayLog(id,items,t)}
  <h2 class="sec">CHOOSE YOUR BOSS</h2>
  <div class="map${isNight()?" night":""}"><img src="${mapSrc()}" alt="Pixel-art map of the UMass Amherst campus, traced from the official campus map"><div class="clouds" aria-hidden="true"></div>${campusLife()}<div class="glints" aria-hidden="true"><i style="left:51%;top:38%"></i><i style="left:49%;top:46%;animation-delay:.9s"></i><i style="left:50%;top:52%;animation-delay:1.7s"></i></div>${pins}<span class="attrib">${isNight()?"Night on campus":"Traced from the official UMass map"}</span></div>
  ${TIDX<0?`<p class="hint" style="margin-top:10px">Menu data ends ${esc(DATES[DATES.length-1])}. Ask Claude to refresh the menus.</p>`:""}
  ${cb.items.length?`<h2 class="sec">NEXT MOVE · ${esc(HALLS[HH].name.toUpperCase())} ${esc(MEALS[meal].toUpperCase())}</h2>${comboHTML(cb,HH,ww)}`:""}
  <h2 class="sec">YOUR USUALS</h2>
  ${usual.length?`<div class="panel listbox">${usual.map(u=>`<div class="row"><span class="nm">${esc(u.n)}</span><span class="tag" style="background:${u.today?"var(--green)":"#e6e0f5"};align-self:center">${u.today?"TODAY":u.when}</span>${u.k?`<button class="btn b-green eat" data-act="eat" data-k="${esc(u.k)}" aria-label="Eat ${esc(u.n)}">+</button>`:"<span></span>"}<span class="mt">${u.c}× logged${u.where?" · "+esc(u.where):""}</span></div>`).join("")}</div>`:emptyCard("usuals")}
  <h2 class="sec">FAVES SPOTTED</h2>
  ${faves.length?`<div class="panel listbox">${faves.map(f=>{const i=f.ns.i;const when=i===TIDX?"TODAY":DATES[i].slice(0,5);return `<div class="row" style="grid-template-columns:auto minmax(0,1fr)"><span class="tag" style="background:${i===TIDX?"var(--green)":"#e6e0f5"}">${when}</span><span><span class="nm">${esc(f.ns.r[0])}</span><br><span class="mt">${esc(f.ns.r._l.map(x=>LOCS[x]).join(", "))} · <span class="d">${fmt(f.ns.r[2])} DMG</span></span></span></div>`}).join("")}</div>`:emptyCard("favhome")}
  <button class="btn b-gold" data-act="tab" data-t="pack" style="width:100%;margin-top:18px;padding:12px;display:flex;align-items:center;gap:10px;text-align:left">${spr("choc",4)}<span style="display:flex;flex-direction:column;line-height:1.15"><span style="font-size:18px">BACKPACK</span><span style="font-weight:600;font-size:13px">Dorm snack or drink? Log it here, no boss fight.</span></span></button>`}
function usuals(){const T=taste();const top=[...T].filter(([n,c])=>c>=2).sort((a,b)=>b[1]-a[1]).slice(0,5);
  return top.map(([n,c])=>{const today=DATA.filter(r=>r[0]===n&&servedToday(r));const r=today[0];
    if(r)return{n,c,k:r._k,today:true,where:r._l.map(i=>LOCS[i]).join(", ")};
    let best=null;for(const x of DATA){if(x[0]!==n)continue;for(let i=Math.max(TIDX,0);i<DATES.length;i++)if((x[10]>>i)&1){if(!best||i<best.i)best={i,x};break}}
    return{n,c,k:best?null:null,today:false,when:best?DATES[best.i].slice(0,5):"—",where:best?best.x._l.map(i=>LOCS[i]).join(", "):"Not on the next two weeks of menus"}})}
function restoreFrom(txt){try{const b=JSON.parse(txt);if(!["commons-quest","gainz-quest"].includes(b.app))throw 0;
    DAYS={...DAYS,...(b.days||{})};CUSTOM=b.foods||CUSTOM;GOALS=normGoals(b.goals||GOALS);FAVES=b.faves||FAVES;PROFILE={...PROFILE,...(b.profile||{}),setup:true};
    saveLocal();saveProfile();applyHero();$("#overlay").innerHTML="";render();toast(`Restored ${Object.keys(b.days||{}).length} days`)}catch(e){toast("That file isn't a Commons Quest backup")}}
// ---------- quick log: type what you ate ----------
let QL={text:"",items:[],unmatched:[]};
function openQuickLog(){const v=($("#qlin")&&$("#qlin").value||"").trim();if(!v||!DATA.length)return;
  const today=DATA.filter(servedToday);const T=taste();
  const res=SmartLog.parse(v,today,{preferHall:(r,h)=>{const hk=h||homeHall();return HALLS[hk]&&r._l.some(i=>HALLS[hk].locs.includes(i))},taste:r=>T.get(r[0])||0});
  QL={text:v,items:res.items,unmatched:res.unmatched,hall:res.hall};renderQuickLog()}
function renderQuickLog(){const sum=QL.items.reduce((a,it)=>({k:a.k+it.row[2]*it.qty,p:a.p+(it.row[3]||0)*it.qty}),{k:0,p:0});
  $("#overlay").innerHTML=`<div class="sheet" data-act="closesheet"><div class="in panel" style="border-radius:14px 14px 0 0" data-stop="1" role="dialog" aria-label="Quick log">
   <b class="arc" style="font-size:12px">QUICK LOG</b><p class="hint" style="color:var(--dim);margin:6px 0 10px">“${esc(QL.text)}”${QL.hall?` · at ${esc(HALLS[QL.hall].name)}`:""}</p>
   ${QL.items.length?`<div class="panel listbox">${QL.items.map((it,i)=>`<div class="row" style="grid-template-columns:minmax(0,1fr) auto auto"><span class="nm">${esc(it.row[0])}${allergenHits(it.row).length?`<span class="warn alg">contains ${esc(allergenHits(it.row).map(c=>ALG_NAME[c].toLowerCase()).join(", "))}</span>`:""}</span>
     <span class="step" style="grid-row:span 2"><button class="btn b-cream" data-act="qlqty" data-i="${i}" data-dq="-0.5" aria-label="Less">−</button><b>${it.qty}×</b><button class="btn b-cream" data-act="qlqty" data-i="${i}" data-dq="0.5" aria-label="More">+</button></span>
     <button class="btn b-cream" style="grid-row:span 2;width:30px;height:30px;padding:0;font-size:12px" data-act="qldrop" data-i="${i}" aria-label="Remove">✕</button>
     <span class="mt">${esc(it.row[1])} · <span class="d">${fmt(it.row[2]*it.qty)} DMG</span> · <span class="pw">${fmt((it.row[3]||0)*it.qty)} PWR</span>${it.alts.length?` · <button class="linkbtn" data-act="qlswap" data-i="${i}">not it? swap</button>`:""}</span></div>`).join("")}</div>`:`<p style="font-weight:700">Couldn't find that on today's menus. Try the dish name, like “chicken tenders”.</p>`}
   ${QL.unmatched.length?`<p class="hint" style="color:var(--dim);margin-top:8px">Couldn't match: ${esc(QL.unmatched.join(", "))}</p>`:""}
   <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px"><button class="btn b-cream" style="padding:10px" data-act="closesheet">Cancel</button>${QL.items.length?`<button class="btn b-gold" style="padding:10px" data-act="qlgo">Log ${QL.items.length} · +${fmt(sum.k)}</button>`:""}</div></div></div>`}
function emptyCard(kind){const T={usuals:["Log a few meals and the foods you keep coming back to show up here, with where they're served today.","usuals"],
  faves:["No faves yet. Tap FAV on foods you love and I'll tell you when and where they're served next.","faves"],
  favhome:["Tap FAV on any food and this tells you when and where it's served next.","faves"]}[kind];
  return `<div class="panel emptyc"><div class="portrait" aria-hidden="true"><div class="face"></div></div><p>${T[0]}</p></div>`}
function todayLog(id,items,t){
  const rows=items.slice().reverse().map(e=>`<div class="row" style="grid-template-columns:minmax(0,1fr) auto"><span class="nm">${esc(e.n)}</span><span class="step" style="grid-row:span 2"><button class="btn b-cream" data-act="qty" data-d="${id}" data-k="${esc(e.k)}" data-dq="-0.5" aria-label="Less ${esc(e.n)}">−</button><b>${e.q}×</b><button class="btn b-cream" data-act="qty" data-d="${id}" data-k="${esc(e.k)}" data-dq="0.5" aria-label="More ${esc(e.n)}">+</button></span><span class="mt">${esc(e.s)} · <span class="d">${fmt(e.v[0]*e.q)} kcal</span> · <span class="pw">${f1(e.v[1]*e.q)}g P</span></span></div>`).join("");
  return `<h2 class="sec">TODAY'S LOG · ${items.length} ITEM${items.length===1?"":"S"}</h2>
  <div class="panel listbox">${items.length?rows+`<div style="padding:10px 12px;background:var(--panel2);display:flex;flex-direction:column;gap:8px">
    <div class="mac4"><div style="background:#ffe0e3"><b>${fmt(t.k)}</b><span style="color:var(--red)">KCAL</span></div><div style="background:#e3f7ff"><b>${fmt(t.p)}g</b><span style="color:#1d6fa5">PROTEIN</span></div><div style="background:#fff"><b>${fmt(t.c)}g</b><span>CARBS</span></div><div style="background:#fff"><b>${fmt(t.f)}g</b><span>FAT</span></div></div>
    <div style="font-weight:700;font-size:14px;color:#5b4a7a">Sugar ${fmt(t.su)}g · Sodium ${fmt(t.na)}mg · Fiber ${fmt(t.fi)}g · Sat fat ${fmt(t.sf)}g</div></div>`
   :`<p style="padding:14px;margin:0;color:var(--dim);font-weight:700">Nothing logged yet today.</p>`}</div>`}
function statTiles(c){if(!c.tr.length)return"";
  return `<div class="stats3" style="grid-template-columns:repeat(${c.tr.length},minmax(0,1fr))">${c.tr.map(x=>{const s=STATS[x.k],pct=Math.min(100,x.val/x.v*100),bad=x.dir==="max"&&x.val>x.v;
    return `<div class="stat" style="background:${s.bg}"><span class="lab" style="color:${s.fg}">${s.lab.toUpperCase()}${s.u==="mg"?" mg":""} ${x.dir==="min"?"≥":"≤"}</span><b>${statNum(x.k,x.val)}<small>/${statNum(x.k,x.v)}${s.u==="g"?"g":""}</small></b><div class="meter"><i style="width:${pct}%;background:${bad?"var(--red)":s.bar}"></i></div></div>`}).join("")}</div>`}
function checkChips(c,t){return `<span class="${c.cal&&!c.over?"ok":""}">${c.cal&&!c.over?"✓":"✗"} ${fmt(t.k)} / ${fmt(GOALS.kcal)} DMG</span>${c.tr.map(x=>`<span class="${x.ok?"ok":""}">${x.ok?"✓":"✗"} ${statNum(x.k,x.val)}${STATS[x.k].u} ${STATS[x.k].lab.toLowerCase()}</span>`).join("")}`}
function comboHTML(cb,hk,ww){
  const sum=cb.items.reduce((a,r)=>({k:a.k+r[2],p:a.p+(r[3]||0),na:a.na+(r[16]||0)}),{k:0,p:0,na:0});
  return `<div class="combo"><div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><span class="arc" style="font-size:10px">${cb.mode==="kcal"?"KO COMBO":"POWER TOP-UP"}</span><span style="font-weight:700;font-size:13px;text-align:right">${cb.mode==="kcal"?"biggest hits at "+esc(HALLS[hk].name):"boss is down, chase protein"}</span></div>
   ${cb.items.map(r=>`<div class="ci"><span>${esc(r[0])}<span style="font-weight:500;color:var(--dim)"> · ${esc(stationOf(r,hk))}</span></span><b>${fmt(r[2])}</b><button class="nope" data-act="nope" data-n="${esc(r[0])}" aria-label="Don't suggest ${esc(r[0])} again" title="Not for me">✕</button></div>`).join("")}
   <div style="display:flex;align-items:center;justify-content:space-between;gap:8px"><span style="font-weight:700;font-size:14px;line-height:1.2">+${fmt(sum.k)} DMG · +${fmt(sum.p)} PWR<br><span style="font-weight:600;font-size:12px">${cb.mode==="kcal"?(sum.k>=cb.rem?"KO!":fmt(cb.rem-sum.k)+" HP left after")+" · ":""}${fmt(sum.na)}mg sodium</span></span>
   <button class="btn b-red arc" style="font-size:10px;padding:11px 12px;flex:none" data-act="combo" data-ks="${esc(cb.items.map(r=>r._k).join("||"))}">EAT ALL</button></div>
   ${ww?`<div class="walk2"><span style="flex:1;min-width:0"><span class="tag" style="background:var(--pwr);display:inline-block;margin-bottom:4px">WORTH THE WALK</span><br>${esc(ww[0])} · <b>${fmt(ww[2])} DMG</b> · ${esc(ww._l.map(i=>LOCS[i]).join(", "))}</span><button class="btn b-green" style="width:36px;height:36px;font-size:18px;padding:0;flex:none" data-act="eat" data-k="${esc(ww._k)}" aria-label="Eat ${esc(ww[0])}">+</button></div>`:""}</div>`}
function logBanner(){return `<div class="banner2"><span>Logging to ${niceDay(S.logDay)}</span><button class="btn b-cream" style="padding:4px 8px;font-size:13px" data-act="logtoday">Back to today</button></div>`}

function renderBattle(){
  const hk=S.hall,h=HALLS[hk],rows=hallRows(hk);
  const letters=h.retail?[]:["B","L","D","N","G"].filter(m=>rows.some(r=>r[7].includes(m)));
  if(!h.retail&&(!S.meal||!letters.includes(S.meal)))S.meal=letters.includes(curMeal())?curMeal():letters[0];
  const t=totals(dayItems(curDay())),rem=Math.max(0,GOALS.kcal-t.k);
  const SH=SHEETS[hk];
  const bossEl=SH?`<div class="bossspr ${rem?"idle":"down"}" id="bossSpr" style="--fw:${SH.fw}px;--fh:${SH.fh}px;${SH.fh>72?"--s:2.0;":""}background-image:url(${SH.src})" ${rem?"":'data-ko="1"'}></div>`:`<div class="bosssvg" id="bossSpr" ${rem?"":'data-ko="1" style="transform:translateY(30px) rotate(80deg)"'}>${spr(h.spr,8,h.boss)}</div>`;
  const cb=comboFor(hk,S.meal);
  $("#view").innerHTML=`
  ${S.logDay&&S.logDay!==dayId()?logBanner():""}
  <div class="bhead"><button class="btn b-cream" style="padding:6px 10px;font-size:15px" data-act="tab" data-t="map">◀ MAP</button>
    <div style="flex:1;line-height:1.1;min-width:0"><span class="arc" style="font-size:9px;color:#ff6b6b">BOSS FIGHT</span><br><span style="font-weight:700;font-size:20px">${esc(h.boss.toUpperCase())}</span></div><span class="hint" style="text-align:right;line-height:1.2">${esc(h.name)}${openNow(hk)?`<br><b style="color:${openNow(hk).open?"#5be36b":"#ff8a8a"}">${esc(openNow(hk).txt)}</b>`:""}</span></div>
  ${letters.length?`<div class="tabs" style="margin-top:10px">${letters.map(m=>`<button data-act="meal" data-m="${m}" aria-pressed="${m===S.meal}">${MEALS[m]}</button>`).join("")}</div>`:""}
  <section class="arena" id="arena">
    <div class="hpwrap"><div class="hp"><i id="hpbar" style="width:${rem/GOALS.kcal*100}%"></i><span id="hptxt">HP ${fmt(rem)} / ${fmt(GOALS.kcal)}</span></div></div>
    <div class="stage${["berk","wor","frank","hamp","cc"].includes(hk)?" bgx":""}" id="stage" style="${["berk","wor","frank","hamp","cc"].includes(hk)?`--bg:url(${asset(`assets/img/bg_${hk}.png`)})`:""}"><svg class="cloud" style="top:20px;width:80px;animation-duration:30s" viewBox="0 0 20 7" shape-rendering="crispEdges" aria-hidden="true"><path fill="#b8dcf2" d="M6 0h4v1h-4zM4 1h2v1h-2zM10 1h2v1h-2zM14 1h3v1h-3zM3 2h1v1h-1zM12 2h3v1h-3zM17 2h1v1h-1zM1 3h2v1h-2zM18 3h1v1h-1zM0 4h1v1h-1zM19 4h1v1h-1zM0 5h1v1h-1zM19 5h1v1h-1zM1 6h18v1h-18z"/><path fill="#ffffff" d="M6 1h4v1h-4zM4 2h8v1h-8zM15 2h2v1h-2zM3 3h15v1h-15zM1 4h18v1h-18zM1 5h1v1h-1zM5 5h5v1h-5zM13 5h3v1h-3z"/><path fill="#e3f2fb" d="M2 5h3v1h-3zM10 5h3v1h-3zM16 5h3v1h-3z"/></svg><svg class="cloud" style="top:52px;width:56px;animation-duration:44s;animation-delay:-20s" viewBox="0 0 20 7" shape-rendering="crispEdges" aria-hidden="true"><path fill="#b8dcf2" d="M6 0h4v1h-4zM4 1h2v1h-2zM10 1h2v1h-2zM14 1h3v1h-3zM3 2h1v1h-1zM12 2h3v1h-3zM17 2h1v1h-1zM1 3h2v1h-2zM18 3h1v1h-1zM0 4h1v1h-1zM19 4h1v1h-1zM0 5h1v1h-1zM19 5h1v1h-1zM1 6h18v1h-18z"/><path fill="#ffffff" d="M6 1h4v1h-4zM4 2h8v1h-8zM15 2h2v1h-2zM3 3h15v1h-15zM1 4h18v1h-18zM1 5h1v1h-1zM5 5h5v1h-5zM13 5h3v1h-3z"/><path fill="#e3f2fb" d="M2 5h3v1h-3zM10 5h3v1h-3zM16 5h3v1h-3z"/></svg><svg class="hills" viewBox="0 0 120 16" preserveAspectRatio="xMidYMax slice" shape-rendering="crispEdges" aria-hidden="true"><path fill="#a9dcf3" d="M0 8h1v8h-1zM1 7h1v9h-1zM2 7h1v9h-1zM3 7h1v9h-1zM4 6h1v10h-1zM5 6h1v10h-1zM6 6h1v10h-1zM7 6h1v10h-1zM8 6h1v10h-1zM9 6h1v10h-1zM10 7h1v9h-1zM11 7h1v9h-1zM12 7h1v9h-1zM13 7h1v9h-1zM14 7h1v9h-1zM15 7h1v9h-1zM16 8h1v8h-1zM17 8h1v8h-1zM18 8h1v8h-1zM19 8h1v8h-1zM20 8h1v8h-1zM21 7h1v9h-1zM22 7h1v9h-1zM23 7h1v9h-1zM24 7h1v9h-1zM25 7h1v9h-1zM26 7h1v9h-1zM27 7h1v9h-1zM28 7h1v9h-1zM29 8h1v8h-1zM30 8h1v8h-1zM31 8h1v8h-1zM32 9h1v7h-1zM33 9h1v7h-1zM34 10h1v6h-1zM35 11h1v5h-1zM36 11h1v5h-1zM37 12h1v4h-1zM38 12h1v4h-1zM39 13h1v3h-1zM40 13h1v3h-1zM41 13h1v3h-1zM42 13h1v3h-1zM43 13h1v3h-1zM44 13h1v3h-1zM45 13h1v3h-1zM46 13h1v3h-1zM47 13h1v3h-1zM48 12h1v4h-1zM49 11h1v5h-1zM50 11h1v5h-1zM51 10h1v6h-1zM52 10h1v6h-1zM53 9h1v7h-1zM54 9h1v7h-1zM55 8h1v8h-1zM56 8h1v8h-1zM57 7h1v9h-1zM58 7h1v9h-1zM59 7h1v9h-1zM60 7h1v9h-1zM61 7h1v9h-1zM62 7h1v9h-1zM63 7h1v9h-1zM64 7h1v9h-1zM65 7h1v9h-1zM66 7h1v9h-1zM67 7h1v9h-1zM68 7h1v9h-1zM69 8h1v8h-1zM70 8h1v8h-1zM71 7h1v9h-1zM72 7h1v9h-1zM73 7h1v9h-1zM74 7h1v9h-1zM75 7h1v9h-1zM76 7h1v9h-1zM77 7h1v9h-1zM78 7h1v9h-1zM79 6h1v10h-1zM80 6h1v10h-1zM81 7h1v9h-1zM82 7h1v9h-1zM83 7h1v9h-1zM84 7h1v9h-1zM85 8h1v8h-1zM86 8h1v8h-1zM87 9h1v7h-1zM88 9h1v7h-1zM89 10h1v6h-1zM90 11h1v5h-1zM91 11h1v5h-1zM92 12h1v4h-1zM93 12h1v4h-1zM94 13h1v3h-1zM95 13h1v3h-1zM96 13h1v3h-1zM97 13h1v3h-1zM98 13h1v3h-1zM99 13h1v3h-1zM100 13h1v3h-1zM101 13h1v3h-1zM102 12h1v4h-1zM103 12h1v4h-1zM104 11h1v5h-1zM105 11h1v5h-1zM106 10h1v6h-1zM107 10h1v6h-1zM108 9h1v7h-1zM109 9h1v7h-1zM110 9h1v7h-1zM111 8h1v8h-1zM112 8h1v8h-1zM113 8h1v8h-1zM114 8h1v8h-1zM115 8h1v8h-1zM116 8h1v8h-1zM117 8h1v8h-1zM118 8h1v8h-1zM119 8h1v8h-1z"/><path fill="#7fcf63" d="M0 9h1v7h-1zM1 9h1v7h-1zM2 9h1v7h-1zM3 9h1v7h-1zM4 9h1v7h-1zM5 9h1v7h-1zM6 10h1v6h-1zM7 11h1v5h-1zM8 11h1v5h-1zM9 12h1v4h-1zM10 13h1v3h-1zM11 13h1v3h-1zM12 14h1v2h-1zM13 14h1v2h-1zM14 14h1v2h-1zM15 14h1v2h-1zM16 14h1v2h-1zM17 13h1v3h-1zM18 13h1v3h-1zM19 12h1v4h-1zM20 12h1v4h-1zM21 12h1v4h-1zM22 11h1v5h-1zM23 11h1v5h-1zM24 11h1v5h-1zM25 11h1v5h-1zM26 11h1v5h-1zM27 11h1v5h-1zM28 11h1v5h-1zM29 11h1v5h-1zM30 11h1v5h-1zM31 10h1v6h-1zM32 10h1v6h-1zM33 9h1v7h-1zM34 9h1v7h-1zM35 8h1v8h-1zM36 8h1v8h-1zM37 8h1v8h-1zM38 8h1v8h-1zM39 8h1v8h-1zM40 9h1v7h-1zM41 9h1v7h-1zM42 10h1v6h-1zM43 11h1v5h-1zM44 11h1v5h-1zM45 12h1v4h-1zM46 12h1v4h-1zM47 13h1v3h-1zM48 13h1v3h-1zM49 13h1v3h-1zM50 13h1v3h-1zM51 13h1v3h-1zM52 13h1v3h-1zM53 12h1v4h-1zM54 12h1v4h-1zM55 12h1v4h-1zM56 12h1v4h-1zM57 12h1v4h-1zM58 12h1v4h-1zM59 12h1v4h-1zM60 12h1v4h-1zM61 12h1v4h-1zM62 12h1v4h-1zM63 12h1v4h-1zM64 12h1v4h-1zM65 11h1v5h-1zM66 11h1v5h-1zM67 10h1v6h-1zM68 9h1v7h-1zM69 9h1v7h-1zM70 8h1v8h-1zM71 8h1v8h-1zM72 8h1v8h-1zM73 8h1v8h-1zM74 8h1v8h-1zM75 8h1v8h-1zM76 9h1v7h-1zM77 10h1v6h-1zM78 10h1v6h-1zM79 11h1v5h-1zM80 11h1v5h-1zM81 12h1v4h-1zM82 12h1v4h-1zM83 12h1v4h-1zM84 12h1v4h-1zM85 12h1v4h-1zM86 12h1v4h-1zM87 12h1v4h-1zM88 12h1v4h-1zM89 12h1v4h-1zM90 12h1v4h-1zM91 12h1v4h-1zM92 13h1v3h-1zM93 13h1v3h-1zM94 13h1v3h-1zM95 13h1v3h-1zM96 13h1v3h-1zM97 13h1v3h-1zM98 13h1v3h-1zM99 13h1v3h-1zM100 12h1v4h-1zM101 11h1v5h-1zM102 11h1v5h-1zM103 10h1v6h-1zM104 9h1v7h-1zM105 9h1v7h-1zM106 8h1v8h-1zM107 8h1v8h-1zM108 8h1v8h-1zM109 8h1v8h-1zM110 9h1v7h-1zM111 9h1v7h-1zM112 9h1v7h-1zM113 10h1v6h-1zM114 10h1v6h-1zM115 10h1v6h-1zM116 11h1v5h-1zM117 11h1v5h-1zM118 11h1v5h-1zM119 11h1v5h-1z"/><path fill="#3f8f3a" d="M14 11h1v1h1v1h-3v-1h1z"/><path fill="#3f8f3a" d="M15 11h1v1h1v1h-3v-1h1z"/><path fill="#3f8f3a" d="M41 6h1v1h1v1h-3v-1h1z"/><path fill="#3f8f3a" d="M77 7h1v1h1v1h-3v-1h1z"/><path fill="#3f8f3a" d="M96 10h1v1h1v1h-3v-1h1z"/><path fill="#3f8f3a" d="M110 6h1v1h1v1h-3v-1h1z"/></svg><div class="ground"></div>
      <div class="gshadow" style="left:40px;width:62px"></div><div class="gshadow" style="right:34px;width:110px"></div><div class="herospr idle" id="heroSpr"></div><div class="bosswrap" id="bossWrap">${bossEl}</div></div>
    <div class="say" id="say">${rem?`<b>${esc(h.boss.toUpperCase())}</b> ${h.retail?"guards the Campus Center":"is serving "+esc(MEALS[S.meal]||"")}: ${rows.length} items today. Tap + to attack.`:`<b>K.O.!</b> Today's boss is down. Stack protein for better loot.`}</div>
  </section>
  ${cb.items.length?`<div style="height:14px"></div>${comboHTML(cb,hk,worthWalk(hk))}`:""}
  <h2 class="sec">FULL MENU</h2>
  <input class="search" type="search" id="hq" placeholder="Search ${esc(h.name)}'s menu…" aria-label="Search ${esc(h.name)}'s menu" value="${esc(S.q)}" autocomplete="off">
  <div class="panel listbox" style="margin-top:10px" id="hlist"></div>
  <div class="fight" id="fight"></div><div style="height:8px"></div>`;
  renderHallList();renderFightBar()}
function itemRow(r,loc){const k=r._k,fav=FAVES.includes(k);const na=r[16]||0,su=r[12]||0;
  return `<div class="row"><span class="nm">${esc(r[0])}${na>=1150?`<span class="warn">high salt</span>`:""}${su>=30?`<span class="warn sug">high sugar</span>`:""}${allergenHits(r).length?`<span class="warn alg">contains ${esc(allergenHits(r).map(c=>ALG_NAME[c].toLowerCase()).join(", "))}</span>`:""}</span>
   <button class="btn fav${fav?" on":""}" data-act="fav" data-k="${esc(k)}" aria-pressed="${fav}" aria-label="Favorite ${esc(r[0])}">FAV</button>
   <button class="btn b-green eat" data-act="eat" data-k="${esc(k)}" aria-label="Eat ${esc(r[0])}">+</button>
   <span class="mt">${esc(r[1])}${loc?" · "+esc(loc):""} · <span class="d">${fmt(r[2])} DMG</span> · <span class="pw">${fmt(r[3])} PWR</span></span></div>`}
function renderHallList(){
  const hk=S.hall,h=HALLS[hk],q=S.q.toLowerCase().trim().split(/\s+/).filter(Boolean);
  let rows=hallRows(hk);
  if(q.length)rows=rows.filter(r=>q.every(t=>r._s.includes(t)));else if(!h.retail)rows=rows.filter(r=>r[7].includes(S.meal));
  const groups=new Map();for(const r of rows.slice().sort((a,b)=>b[2]-a[2])){const s=stationOf(r,hk);if(!groups.has(s))groups.set(s,[]);groups.get(s).push(r)}
  const openAll=q.length>0||groups.size<=2;S.openSt=S.openSt||{};
  $("#hlist").innerHTML=rows.length?[...groups].map(([s,rs],gi)=>{const key=hk+"|"+S.meal+"|"+s,op=openAll||S.openSt[key]||(S.openSt[key]===undefined&&gi===0);
    return `<details class="stn" data-key="${esc(key)}" ${op?"open":""}><summary class="station"><span>${esc(s.toUpperCase())}</span><span class="cnt">${rs.length} · top ${fmt(rs[0][2])} DMG</span></summary>${rs.map(r=>itemRow(r)).join("")}</details>`}).join(""):`<p style="padding:14px;margin:0;color:var(--dim);font-weight:600">${q.length?"No match. Try one word.":"Nothing listed for this meal today."}</p>`}
function renderFightBar(){const el=$("#fight");if(!el)return;const f=S.fight,t=totals(f);el.style.display=f.length?"":"none";el.innerHTML=`<span style="line-height:1.15"><b style="font-size:16px">THIS FIGHT · ${f.length} hit${f.length===1?"":"s"}</b><br><span class="hint">+${fmt(t.k)} DMG · +${fmt(t.p)} PWR · ${fmt(t.na)}mg Na</span></span><button class="btn b-cream" style="padding:7px 10px;font-size:14px" data-act="tab" data-t="map">DONE</button>`}

function attackFx(dmg){
  const stage=$("#stage"),hero=$("#heroSpr"),boss=$("#bossSpr"),arena=$("#arena");if(!stage||!hero)return;
  buzz();
  hero.className="herospr";const HF=i=>hero.style.backgroundPositionX=`calc(${-68*i}px*var(--s))`;
  [[13,0],[14,60],[15,120],[16,200],[17,235]].forEach(([f,t])=>setTimeout(()=>{HF(f);if(f>=16)hero.style.left="96px"},t));
  setTimeout(()=>HF(19),420);setTimeout(()=>{HF(20);hero.style.left=""},490);
  setTimeout(()=>{HF(18);hero.style.left="104px";
    if(boss){boss.classList.remove("hit");void boss.offsetWidth;boss.classList.add("hit")}
    if(SHEETS[S.hall]&&boss&&!boss.dataset.ko){boss.classList.remove("idle");const fw=SHEETS[S.hall].fw;const BF=i=>boss.style.backgroundPositionX=`calc(${-fw*i}px*var(--s))`;BF(6);setTimeout(()=>{if(!boss.dataset.ko)BF(7)},110);setTimeout(()=>{if(!boss.dataset.ko)BF(8)},270)}
    const big=dmg>=400;arena.classList.remove("shake","hard");void arena.offsetWidth;arena.classList.add("shake");if(big)arena.classList.add("hard");
    const bw=$("#bossWrap").getBoundingClientRect(),sr=stage.getBoundingClientRect();const cx=bw.left-sr.left+bw.width/2,cy=bw.top-sr.top+bw.height*0.42;
    [["",-28],["b",18]].forEach(([c,r])=>{const sl=document.createElement("div");sl.className="slash "+c;sl.style.left=cx+"px";sl.style.top=cy+"px";sl.style.setProperty("--r",r+"deg");stage.appendChild(sl);setTimeout(()=>sl.remove(),420)});
    const n=document.createElement("div");n.className="dmg"+(big?" big":"");n.innerHTML=(big?'<span class="crit">CRIT!</span>':"")+"-"+fmt(dmg);
    n.style.left=Math.max(4,bw.left-sr.left-44)+"px";n.style.top=Math.max(26,bw.top-sr.top+18)+"px";stage.appendChild(n);setTimeout(()=>n.remove(),1200);
    const cols=["#ffcc3d","#ff4f5e","#fff","#3ec7ff","#5be36b"],crumbs=["#c98a4a","#e8b060","#8a5a2a","#f4d35e","#d0502e"];
    for(let i=0;i<(big?18:12);i++){const p=document.createElement("div");const star=i%4===0;p.className="part"+(star?" star":"");const a=Math.random()*Math.PI*2,d=26+Math.random()*(big?70:46);p.style.left=cx+"px";p.style.top=cy+"px";p.style.background=star?"":cols[i%cols.length];p.style.color=cols[i%cols.length];p.style.setProperty("--dx",Math.cos(a)*d+"px");p.style.setProperty("--dy",Math.sin(a)*d-20+"px");stage.appendChild(p);setTimeout(()=>p.remove(),750)}
    for(let i=0;i<8;i++){const p=document.createElement("div");p.className="part crumb";p.style.left=cx+"px";p.style.top=(cy+10)+"px";p.style.background=crumbs[i%crumbs.length];p.style.setProperty("--dx",(Math.random()*80-20)+"px");p.style.setProperty("--dy",(-20-Math.random()*30)+"px");stage.appendChild(p);setTimeout(()=>p.remove(),800)}
  },270);
  setTimeout(()=>{hero.style.left="";hero.style.backgroundPositionX="";hero.className="herospr idle";
    const t=totals(dayItems(curDay())),rem=Math.max(0,GOALS.kcal-t.k);
    if($("#hpbar")){$("#hpbar").style.width=rem/GOALS.kcal*100+"%";$("#hptxt").textContent=`HP ${fmt(rem)} / ${fmt(GOALS.kcal)}`}
    if(boss&&SHEETS[S.hall]&&rem&&!boss.dataset.ko){boss.style.backgroundPositionX="";boss.classList.add("idle")}
    if(!rem&&boss&&!boss.dataset.ko){boss.dataset.ko="1";koFx(boss)}
  },600)}
function popDmg(el,dmg){const r=el.getBoundingClientRect();const n=document.createElement("div");n.className="dmg";n.style.position="fixed";n.style.left=(r.left-30)+"px";n.style.top=(r.top-10)+"px";n.textContent="-"+fmt(dmg);document.body.appendChild(n);setTimeout(()=>n.remove(),1200)}
function koFx(boss){const stage=$("#stage");sfx("sfx_ko",.9);
  if(SHEETS[S.hall]){boss.classList.remove("idle");const fw=SHEETS[S.hall].fw;const BF=i=>boss.style.backgroundPositionX=`calc(${-fw*i}px*var(--s))`;[[9,0],[10,170],[9,340],[11,510],[12,650],[13,790]].forEach(([f,t])=>setTimeout(()=>BF(f),t));setTimeout(()=>{boss.style.backgroundPositionX="";boss.classList.add("down")},990)}else boss.classList.add("ko");
  const b=document.createElement("div");b.className="banner";b.textContent="K.O.!";stage.appendChild(b);setTimeout(()=>b.remove(),2200);
  try{const bw=$("#bossWrap").getBoundingClientRect(),sr=stage.getBoundingClientRect();const cx=bw.left-sr.left+bw.width/2,cy=bw.top-sr.top+bw.height/2;
    const ray=document.createElement("div");ray.className="burst";ray.style.left=cx+"px";ray.style.top=cy+"px";stage.insertBefore(ray,stage.firstChild);setTimeout(()=>ray.remove(),1700);
    const cols=["#ffcc3d","#ff4f5e","#fff","#3ec7ff","#5be36b","#c46bff"];
    for(let i=0;i<34;i++){const p=document.createElement("div");p.className="part"+(i%3===0?" star":"");const a=Math.random()*Math.PI*2,d=40+Math.random()*110;p.style.left=cx+"px";p.style.top=cy+"px";p.style.background=i%3===0?"":cols[i%cols.length];p.style.color=cols[i%cols.length];p.style.setProperty("--dx",Math.cos(a)*d+"px");p.style.setProperty("--dy",Math.sin(a)*d-30+"px");p.style.animationDuration="1.1s";stage.appendChild(p);setTimeout(()=>p.remove(),1150)}}catch(e){}
  if($("#say"))$("#say").innerHTML="<b>K.O.!</b> Calorie goal hit. Hit your other goals for better loot.";buzz()}
function maybeVictory(){const id=curDay(),d=DAYS[id];if(!d||d.celebrated||grade(d.items)!=="legend")return;d.celebrated=true;persistDay(id);
  const t=totals(d.items);jingle();
  $("#overlay").innerHTML=`<div class="victory" role="dialog" aria-label="Legendary day"><div class="rays"></div>
   <div style="position:relative;text-align:center" class="arc"><div style="font-size:26px;line-height:1.3;color:var(--gold);text-shadow:4px 4px 0 var(--ink)">LEGENDARY<br>DAY!</div></div>
   <div style="position:relative">${spr("chest",14,"Legendary loot chest")}</div>
   <div class="panel" style="position:relative;width:100%;max-width:400px;padding:12px"><div class="checks">
     ${checkChips(checks(t),t)}</div>
     <p style="margin:10px 0 0;font-weight:700;text-align:center">+${dayXP(d.items)} XP · +1 crown</p></div>
   <button class="btn b-red arc" style="position:relative;font-size:13px;padding:16px 26px" data-act="closevictory">CLAIM LOOT</button></div>`}

function renderPack(){
  const tabs=[["items","ITEMS"],["search","ALL CAMPUS"],["faves","FAVES"]];
  let body="";
  if(S.ptab==="items"){
    const sel=S.sel!=null?CUSTOM[S.sel]:null;
    const icons=[["choc",/choc|candy|bar|cookie|brownie/i],["milk",/milk|coffee|latte|drink|juice|shake|celsius|soda/i],["fish",/goldfish|chip|cracker|snack|pretzel/i]];
    const icon=c=>{for(const[n,re]of icons)if(re.test(c.n))return n;return"chest"};
    const slots=CUSTOM.map((c,i)=>`<button class="slot" data-act="sel" data-i="${i}" aria-pressed="${S.sel===i}" aria-label="${esc(c.n)}">${spr(icon(c),4)}<span>${esc(c.n.split(" ").slice(0,2).join(" "))}</span></button>`).join("");
    body=`<div class="slots" style="margin-top:12px">${slots}<button class="slot add" data-act="newitem" aria-label="Add a new item">+</button>${'<div class="slot empty"></div>'.repeat(Math.max(0,7-CUSTOM.length))}</div>
    ${sel?`<section class="panel" style="margin-top:16px;padding:12px;display:flex;flex-direction:column;gap:10px">
      <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px"><span style="font-weight:700;font-size:19px;line-height:1.1">${esc(sel.n)}</span><span style="font-weight:600;font-size:13px;color:var(--dim);flex:none">${esc(sel.s||"1 serving")}</span></div>
      <div class="mac4"><div style="background:#ffe0e3"><b>${fmt(sel.k)}</b><span style="color:var(--red)">DMG</span></div><div style="background:#e3f7ff"><b>${fmt(sel.p)}</b><span style="color:#1d6fa5">PWR</span></div><div style="background:#ffe6f6"><b>${sel.su==null?"?":fmt(sel.su)+"g"}</b><span style="color:#b0287f">SUGAR</span></div><div style="background:#fff0de"><b>${sel.na==null?"?":fmt(sel.na)}</b><span style="color:#b5520e">SODIUM</span></div></div>
      <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px">${[.5,1,2].map(q=>`<button class="btn b-green" style="padding:10px 0;font-size:16px" data-act="use" data-q="${q}">USE ×${q===.5?"½":q}</button>`).join("")}</div>
      <button class="btn b-cream" style="padding:6px;font-size:13px" data-act="delitem">Remove from backpack</button></section>`:`<p class="hint" style="margin-top:12px">Tap an item to use it. Tap + to add a new snack with its label numbers.</p>`}
    ${S.adding?addForm():""}`}
  else if(S.ptab==="search"){body=`<input class="search" style="margin-top:12px" type="search" id="pq" placeholder="Search every food on campus…" aria-label="Search every food on campus" value="${esc(S.pq)}" autocomplete="off"><div class="panel listbox" style="margin-top:10px" id="plist"></div>`}
  else{const f=FAVES.map(k=>({k,r:BYK.get(k),ns:nextServed(k)})).filter(x=>x.r);
    body=f.length?`<div class="panel listbox" style="margin-top:12px">${f.map(x=>`<div class="row"><span class="nm">${esc(x.r[0])}</span><button class="btn fav on" data-act="fav" data-k="${esc(x.k)}" aria-pressed="true" aria-label="Remove ${esc(x.r[0])} from faves">FAV</button><button class="btn b-green eat" data-act="eat" data-k="${esc(x.k)}" aria-label="Eat ${esc(x.r[0])}">+</button><span class="mt">${x.ns?(x.ns.i===TIDX?"<b style='color:#1f9a3a'>TODAY</b>":"Next: "+esc(DATES[x.ns.i].slice(0,5)))+" · "+esc(x.ns.r._l.map(i=>LOCS[i]).join(", ")):"Not on the next two weeks of menus"} · <span class="d">${fmt(x.r[2])} DMG</span></span></div>`).join("")}</div>`:`<div style="margin-top:12px">${emptyCard("faves")}</div>`}
  $("#view").innerHTML=`${S.logDay&&S.logDay!==dayId()?logBanner():""}
   <div style="margin-top:14px"><span class="arc" style="font-size:15px;color:var(--gold);text-shadow:3px 3px 0 var(--ink)">BACKPACK</span><p class="hint" style="margin:6px 0 0">Snacks and drinks count toward the daily quest without a boss fight.</p></div>
   <div class="tabs" style="margin-top:12px">${tabs.map(([k,l])=>`<button data-act="ptab" data-t="${k}" aria-pressed="${S.ptab===k}">${l}</button>`).join("")}</div>${body}`;
  if(S.ptab==="search")renderPackSearch()}
function addForm(){return `<form class="panel form" id="addf" style="margin-top:16px">
  <label class="w4">Name<input id="f-n" required placeholder="e.g. Celsius energy drink"></label>
  <label class="w4">Serving<input id="f-s" placeholder="e.g. 1 can"></label>
  <label>Calories<input id="f-k" inputmode="decimal" required></label><label>Protein g<input id="f-p" inputmode="decimal"></label><label>Carbs g<input id="f-c" inputmode="decimal"></label><label>Fat g<input id="f-f" inputmode="decimal"></label>
  <label>Sugar g<input id="f-su" inputmode="decimal"></label><label>Fiber g<input id="f-fi" inputmode="decimal"></label><label>Sat fat g<input id="f-sf" inputmode="decimal"></label><label>Sodium mg<input id="f-na" inputmode="decimal"></label>
  <div class="w4" style="display:flex;gap:8px;justify-content:flex-end;align-items:center"><span id="f-err" style="margin-right:auto;color:var(--red);font-weight:700;font-size:13px"></span><button type="button" class="btn b-cream" style="padding:8px 12px" data-act="canceladd">Cancel</button><button type="submit" class="btn b-gold" style="padding:8px 12px">Save to backpack</button></div></form>`}
function renderPackSearch(){
  const q=S.pq.toLowerCase().trim().split(/\s+/).filter(Boolean);const el=$("#plist");if(!el)return;
  if(!q.length){el.innerHTML=`<p style="padding:14px;margin:0;color:var(--dim);font-weight:600">${DATA.length.toLocaleString()} foods from 28 campus spots. Type to search.</p>`;return}
  const mine=CUSTOM.map(fromCustom).filter(c=>q.every(t=>c.n.toLowerCase().includes(t)));
  const rows=DATA.filter(r=>q.every(t=>r._s.includes(t))).sort((a,b)=>(+servedToday(b)-+servedToday(a))||b[2]-a[2]).slice(0,80);
  el.innerHTML=mine.map(c=>`<div class="row"><span class="nm">${esc(c.n)} <span class="tag" style="font-size:8px">MINE</span></span><span></span><button class="btn b-green eat" data-act="eat" data-k="${esc(c.k)}" aria-label="Eat ${esc(c.n)}">+</button><span class="mt">${esc(c.s)} · <span class="d">${fmt(c.v[0])} DMG</span> · <span class="pw">${fmt(c.v[1])} PWR</span></span></div>`).join("")
   +rows.map(r=>itemRow(r,r._l.map(i=>LOCS[i]).join(", ")+(TIDX>=0&&servedToday(r)?" · today":""))).join("")
   ||`<p style="padding:14px;margin:0;color:var(--dim);font-weight:600">No match. Add it yourself under Items.</p>`}

function renderTrophies(){
  if(!S.month){const t=fromId(dayId());S.month=new Date(t.getFullYear(),t.getMonth(),1)}
  const m=S.month,y=m.getFullYear(),mo=m.getMonth(),first=new Date(y,mo,1).getDay(),n=new Date(y,mo+1,0).getDate(),today=dayId();
  const all=Object.values(DAYS).filter(d=>d.items&&d.items.length);
  const leg=all.filter(d=>grade(d.items)==="legend").length,beaten=all.filter(d=>checks(totals(d.items)).cal).length;
  let best=0,run=0,prevId=null;Object.keys(DAYS).sort().forEach(id=>{const g=grade(dayItems(id));const consec=prevId&&Math.round((fromId(id)-fromId(prevId))/864e5)===1;run=(g==="legend"||g==="rare")?(consec?run+1:1):0;best=Math.max(best,run);prevId=id});
  let tiles="";for(let i=0;i<first;i++)tiles+=`<div class="tile blank"></div>`;
  for(let d=1;d<=n;d++){const id=y+"-"+pad(mo+1)+"-"+pad(d);const fut=id>today;const g=fut?"empty":grade(dayItems(id));
    const icon=g==="legend"?spr("crown",3):g==="rare"?spr("gem",3):g==="unc"?spr("coin",3):"";
    tiles+=`<button class="tile ${g}${id===today?" today":""}" data-act="day" data-d="${id}" ${fut?"disabled":""} aria-label="${niceDay(id)}: ${({legend:"legendary",rare:"rare",unc:"uncommon",none:"boss escaped",empty:"nothing logged"})[g]}"><span>${d}</span><span style="position:relative;z-index:1">${icon}</span></button>`}
  $("#view").innerHTML=`<div style="margin-top:14px"><span class="arc" style="font-size:15px;color:var(--gold);text-shadow:3px 3px 0 var(--ink)">TROPHY WALL</span></div>
   <div class="stats"><div class="panel"><b style="color:#c99300">${leg}</b><span>Legendary</span></div><div class="panel"><b style="color:#1f9a3a">${beaten}</b><span>Bosses beaten</span></div><div class="panel"><b style="color:#e0640f">${best}</b><span>Best streak</span></div></div>
   <section class="cal"><div class="calhd"><button class="btn b-cream" data-act="month" data-dir="-1" aria-label="Previous month">◀</button><span class="arc" style="font-size:12px">${m.toLocaleDateString(undefined,{month:"short",year:"numeric"}).toUpperCase()}</span><button class="btn b-cream" data-act="month" data-dir="1" aria-label="Next month">▶</button></div>
    <div class="dow"><span>S</span><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span></div><div class="grid7">${tiles}</div></section>
   <div class="legendkey"><div><span class="tile legend"></span>Legendary · every goal</div><div><span class="tile rare"></span>Rare · all but one</div><div><span class="tile unc"></span>Uncommon · calories + 1</div><div><span class="tile none"></span>Boss escaped</div></div>
   <p class="hint" style="margin-top:12px">Tap a day to see or fix its log.</p>`}
function openDay(id){S.dayOpen=id;const items=dayItems(id),t=totals(items),c=checks(t),g=grade(items);
  $("#overlay").innerHTML=`<div class="sheet" data-act="closesheet"><div class="in panel" style="border-radius:14px 14px 0 0" data-stop="1" role="dialog" aria-label="${niceDay(id)}">
   <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px"><b style="font-size:19px">${niceDay(id)}</b><span style="font-weight:700;color:var(--dim)">${({legend:"LEGENDARY",rare:"RARE",unc:"UNCOMMON",none:"BOSS ESCAPED",empty:"NOTHING LOGGED"})[g]}</span></div>
   <div class="checks" style="margin-top:10px">${checkChips(c,t)}</div>
   <div style="margin-top:12px;border:3px solid var(--ink);border-radius:8px;overflow:hidden;background:#fff">${items.length?items.map(e=>`<div class="row" style="grid-template-columns:minmax(0,1fr) auto"><span class="nm">${esc(e.n)}</span><span class="step" style="grid-row:span 2"><button class="btn b-cream" data-act="qty" data-d="${id}" data-k="${esc(e.k)}" data-dq="-0.5" aria-label="Less ${esc(e.n)}">−</button><b>${e.q}×</b><button class="btn b-cream" data-act="qty" data-d="${id}" data-k="${esc(e.k)}" data-dq="0.5" aria-label="More ${esc(e.n)}">+</button></span><span class="mt">${esc(e.s)} · <span class="d">${fmt(e.v[0]*e.q)} DMG</span> · <span class="pw">${f1(e.v[1]*e.q)} PWR</span></span></div>`).join(""):`<p style="padding:12px;margin:0;font-weight:600;color:var(--dim)">Nothing logged.</p>`}</div>
   <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px"><button class="btn b-gold" style="padding:10px" data-act="logto" data-d="${id}">Add food to this day</button><button class="btn b-cream" style="padding:10px" data-act="closesheet">Close</button></div></div></div>`}
function openGoals(first){
  let had=false;try{had=!!(JSON.parse(localStorage.getItem("gq-state")||"null")||{}).goals}catch(e){}
  const cur=PROFILE.hero,gk=first&&!IS_OWNER&&!had?null:GOALS;
  const g=gk?normGoals(gk):normGoals({kcal:GPRE.maintain.kcal,kmode:GPRE.maintain.kmode,track:DEF_TRACK.map(x=>x.k==="protein"?{...x,v:GPRE.maintain.protein}:x)});
  const gp=(g.track.find(x=>x.k==="protein")||{}).v;
  const preset=Object.keys(GPRE).find(k=>GPRE[k].kcal===g.kcal&&GPRE[k].kmode===g.kmode&&(gp==null||GPRE[k].protein===gp))||(gk?"custom":"maintain");
  $("#overlay").innerHTML=`<div class="sheet" ${first?"":'data-act="closesheet"'}><form class="in panel form" style="border-radius:14px 14px 0 0" data-stop="1" id="goalf" aria-label="${first?"Set up your hero":"Settings"}" data-first="${first?1:0}">
  <b class="w4 arc" style="font-size:13px;line-height:1.5">${first?"CHOOSE YOUR HERO":"SETTINGS"}</b>
  ${first?`<button type="button" class="w4 btn b-purple" style="padding:10px;font-size:14px" data-act="demo">Just looking? Skip setup and try the demo →</button>`:""}
  <div class="w4 chars" role="group" aria-label="Character">${HEROES.map(([id,lab])=>`<button type="button" data-act="pickhero" data-h="${id}" aria-pressed="${id===cur}" aria-label="${lab}"><span class="face" style="background-image:url(assets/img/hero_${id}.png)"></span></button>`).join("")}</div>
  <label class="w4">Your name<input id="g-name" maxlength="12" autocomplete="nickname" value="${esc(PROFILE.name||"")}" placeholder="Player"></label>
  <span class="w4" style="font-size:12px;font-weight:700;color:var(--dim);text-transform:uppercase">Usual dining hall</span>
  <div class="w4 goalpick homepick" role="group" aria-label="Usual dining hall">${HOMES.map(([k,l])=>`<button type="button" class="btn ${k===(PROFILE.home||(IS_OWNER?"berk":""))?"b-gold":"b-cream"}" data-act="sethome" data-h="${k}" aria-pressed="${k===PROFILE.home}">${l}</button>`).join("")}</div>
  <span class="w4" style="font-size:12px;font-weight:700;color:var(--dim);text-transform:uppercase">I eat</span>
  <div class="w4 goalpick dietpick" role="group" aria-label="Diet">${DIETS.map(([k,l])=>`<button type="button" class="btn ${k===(PROFILE.diet||"any")?"b-gold":"b-cream"}" data-act="setdiet" data-v="${k}" aria-pressed="${k===(PROFILE.diet||"any")}">${l}</button>`).join("")}</div>
  <span class="w4" style="font-size:12px;font-weight:700;color:var(--dim);text-transform:uppercase">Allergies to avoid</span>
  <div class="w4 algpick" role="group" aria-label="Allergies to avoid">${ALLERGENS.map(([c,l])=>`<button type="button" class="chip2${(PROFILE.avoid||[]).includes(c)?" on":""}" data-act="togalg" data-c="${c}" aria-pressed="${(PROFILE.avoid||[]).includes(c)}">${l}</button>`).join("")}</div>
  <p class="w4 setupnote">Allergen info comes from UMass Dining's labels. Recipes can change, so always confirm with dining staff.</p>
  <span class="w4" style="font-size:12px;font-weight:700;color:var(--dim);text-transform:uppercase">Daily goal</span>
  <div class="w4 goalpick" role="group" aria-label="Goal preset">${[["bulk","Bulk"],["maintain","Maintain"],["cut","Cut"],["custom","Custom"]].map(([k,l])=>`<button type="button" class="btn ${k===preset?"b-gold":"b-cream"}" data-act="gpre" data-g="${k}" aria-pressed="${k===preset}">${l}${GPRE[k]?`<small>${fmt(GPRE[k].kcal)} cal</small>`:"<small>your own</small>"}</button>`).join("")}</div>
  <label class="w2">Calories<input id="g-k" inputmode="numeric" value="${g.kcal}"></label>
  <div class="w2 kmode" role="group" aria-label="Calorie goal type" data-v="${g.kmode}" style="display:flex;flex-direction:column;gap:3px"><span style="font-size:12px;font-weight:700;color:var(--dim);text-transform:uppercase">Beat the boss by</span><div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">${[["reach","Reaching it"],["near","Landing near"]].map(([k,l])=>`<button type="button" class="btn ${k===g.kmode?"b-gold":"b-cream"}" style="padding:7px 2px;font-size:12px" data-act="kmode" data-v="${k}" aria-pressed="${k===g.kmode}">${l}</button>`).join("")}</div></div>
  <span class="w4" style="font-size:12px;font-weight:700;color:var(--dim);text-transform:uppercase">Track at the top · pick up to 3</span>
  <div class="w4 trackpick" style="display:flex;flex-direction:column;gap:6px">${Object.entries(STATS).map(([k,st])=>{const on=g.track.find(x=>x.k===k),dir=on?on.dir:st.dir;
    return `<div class="trow" data-k="${k}" style="display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr) auto;gap:6px;align-items:center"><button type="button" class="chip2 trk${on?" on":""}" data-act="togtrack" aria-pressed="${!!on}">${st.lab}</button><input class="tv" inputmode="numeric" aria-label="${st.lab} goal in ${st.u}" value="${on?on.v:st.def}" ${on?"":"disabled"} style="padding:6px"><button type="button" class="btn b-cream tdir" style="padding:6px 6px;font-size:12px;min-width:84px" data-act="togdir" data-v="${dir}" ${on?"":"disabled"}>${dir==="min"?"≥ at least":"≤ at most"} ${st.u}</button></div>`}).join("")}</div>  <p class="w4 setupnote">"Landing near" means within 10% of your calories, a good fit for cutting or maintaining. Not sure what to pick? Maintain is a common starting point. A doctor or dietitian can give you numbers made for you.</p>
  <span class="w4" id="g-err" style="color:var(--red);font-weight:700;font-size:13px" role="alert"></span>
  <div class="w4" style="display:flex;gap:8px;justify-content:flex-end">${first?"":`<button type="button" class="btn b-cream" style="padding:8px 12px" data-act="closesheet">Cancel</button>`}<button type="submit" class="btn b-gold" style="padding:10px 14px">${first?"START QUEST":"Save"}</button></div>
  ${first?"":`<div class="w4" style="display:flex;gap:8px"><button type="button" class="btn b-cream" style="flex:1;padding:8px" data-act="backup">Back up my data</button><button type="button" class="btn b-cream" style="flex:1;padding:8px" data-act="restore">Restore backup</button></div>`}
  <p class="w4 setupnote">Your food log stays on this device. Commons Quest is a student project and isn't affiliated with UMass Amherst.</p></form></div>`}
function setKmode(v){const box=$(".kmode");if(!box)return;box.dataset.v=v;box.querySelectorAll("button").forEach(b=>{const on=b.dataset.v===v;b.setAttribute("aria-pressed",String(on));b.className="btn "+(on?"b-gold":"b-cream")})}
function toggleTrack(row,force){const b=row.querySelector(".trk"),on=force??!b.classList.contains("on");
  if(on&&document.querySelectorAll(".trow .trk.on").length>=3){toast("Pick up to 3. Turn one off first.");return}
  b.classList.toggle("on",on);b.setAttribute("aria-pressed",String(on));row.querySelector(".tv").disabled=!on;row.querySelector(".tdir").disabled=!on}
// Demo: a ready-made profile and two weeks of sample days from the real menus, so a visitor can look around without setting up.
function startDemo(){if(!DATA.length){toast("Menus are still loading…");return}
  PROFILE={...PROFILE,name:"DEMO",hero:"og",setup:true,demo:true,home:"berk",diet:"any",avoid:[],nope:[]};
  GOALS=normGoals({kcal:2600,kmode:"reach",track:[{k:"protein",v:130,dir:"min"},{k:"fiber",v:20,dir:"min"},{k:"sugar",v:50,dir:"max"}]});
  const pool=DATA.filter(r=>isBig(r)&&r._l.some(i=>HALLS.berk.locs.includes(i)||HALLS.wor.locs.includes(i))&&!/dessert|bakery/i.test(ST[r[8]]||""));
  let seed=7;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
  DAYS={};const reach=[1.05,.7,1.1,.95,1.2,1.0,.5,1.1,1.15,.85,1.05,1.1,.9];
  for(let i=13;i>=1;i--){const id=dayId(new Date(Date.now()-4*3600e3-i*864e5)),items=[];let k=0;const target=GOALS.kcal*reach[i-1];
    let tries=0;const big=pool.filter(r=>r[2]>=300&&(r[3]||0)>=18&&(r[12]||0)<=20);while(k<target&&items.length<12&&big.length&&tries++<200){const r=big[Math.floor(rnd()*big.length)];if(items.some(e=>e.k===r._k))continue;const x=fromRow(r);items.push({...x,q:1});k+=x.v[0]}
    DAYS[id]={items,celebrated:true}}
  const today=pool.filter(r=>(r[3]||0)>=20).slice(0,2).map(r=>({...fromRow(r),q:1}));DAYS[dayId()]={items:today};
  FAVES=pool.filter(r=>(r[3]||0)>=30).slice(0,2).map(r=>r._k);saveLocal();saveProfile();applyHero();
  $("#overlay").innerHTML="";S.tab="map";render();toast("Demo mode: sample data. Tap “Make it mine” to start fresh.")}
function endDemo(){DAYS={};CUSTOM=[];FAVES=[];GOALS=normGoals();try{localStorage.removeItem("gq-state")}catch(e){}
  PROFILE={name:"",hero:"og",setup:false,demo:false,home:"",diet:"any",nope:[],avoid:[]};saveProfile();applyHero();render();openGoals(true)}
function render(){renderHUD();
  document.querySelectorAll(".nav button").forEach(b=>{const on=b.dataset.t===(S.tab==="battle"?"map":S.tab);b.setAttribute("aria-pressed",String(on));b.className="btn "+(on?"b-gold":"b-purple")});
  if(!DATA.length)return;
  music(S.tab==="battle"?"boss_fight":"map_theme");
  if(S.tab==="map")renderMap();else if(S.tab==="battle")renderBattle();else if(S.tab==="pack")renderPack();else renderTrophies()}
function refresh(){
  renderHUD();const a=document.activeElement;
  if(S.tab==="battle"&&$("#hlist")){renderHallList();renderFightBar();const t=totals(dayItems(curDay())),rem=Math.max(0,GOALS.kcal-t.k);if($("#hpbar")){$("#hpbar").style.width=rem/GOALS.kcal*100+"%";$("#hptxt").textContent=`HP ${fmt(rem)} / ${fmt(GOALS.kcal)}`}}
  else if(S.tab==="pack"&&S.ptab==="search"&&$("#plist"))renderPackSearch();
  else if(!(a&&a.tagName==="INPUT"))render();
  if(S.dayOpen&&$("#overlay .sheet"))openDay(S.dayOpen)}

document.addEventListener("click",ev=>{
  const el=ev.target.closest("[data-act]");if(!el)return;
  if(el.classList.contains("sheet")&&ev.target!==el)return;
  const a=el.dataset.act,d=el.dataset;
  if(a==="tab"){S.tab=d.t;S.fight=[];window.scrollTo(0,0);render()}
  else if(a==="hall"){S.hall=d.h;S.meal=null;S.q="";S.fight=[];S.tab="battle";window.scrollTo(0,0);render()}
  else if(a==="meal"){S.meal=d.m;S.q="";render()}
  else if(a==="eat"){const it=lookup(d.k);if(!it)return;const dmg=eat(it,1);
    if(S.tab==="battle"){S.fight.push({...it,q:1});popDmg(el,dmg);setTimeout(()=>sfx("sfx_hit"),130);attackFx(dmg);setTimeout(refresh,560)}else{sfx("sfx_coin");toast(`+${fmt(dmg)} DMG · ${it.n}`);refresh()}
    setTimeout(maybeVictory,900)}
  else if(a==="combo"){let tot=0;d.ks.split("||").forEach(k=>{const it=lookup(k);if(it){tot+=eat(it,1);if(S.tab==="battle")S.fight.push({...it,q:1})}});
    if(S.tab==="battle"){setTimeout(()=>sfx("sfx_hit"),130);attackFx(tot);setTimeout(()=>{renderBattle()},700)}else{toast(`Combo! +${fmt(tot)} DMG`);render()}setTimeout(maybeVictory,900)}
  else if(a==="fav"){toggleFav(d.k);const on=FAVES.includes(d.k);el.classList.toggle("on",on);el.setAttribute("aria-pressed",String(on));if(S.tab==="pack"&&S.ptab==="faves")render()}
  else if(a==="ptab"){S.ptab=d.t;S.adding=false;render()}
  else if(a==="sel"){S.sel=+d.i;S.adding=false;render()}
  else if(a==="newitem"){S.adding=true;S.sel=null;render();setTimeout(()=>{const f=$("#f-n");if(f){f.focus();f.scrollIntoView({block:"center"})}},50)}
  else if(a==="canceladd"){S.adding=false;render()}
  else if(a==="use"){const c=CUSTOM[S.sel];if(!c)return;sfx("sfx_coin");const dmg=eat(fromCustom(c),+d.q);toast(`+${fmt(dmg)} DMG · ${c.n}`);refresh();setTimeout(maybeVictory,600)}
  else if(a==="delitem"){CUSTOM.splice(S.sel,1);S.sel=null;persistMeta("foods");render()}
  else if(a==="day"){openDay(d.d)}
  else if(a==="qty"){setQty(d.d,d.k,+d.dq);if($("#overlay .sheet"))openDay(d.d);renderHUD();if(S.tab==="trophies")renderTrophies();else if(S.tab==="map"){const y=window.scrollY;renderMap();window.scrollTo(0,y)}}
  else if(a==="logto"){S.logDay=d.d===dayId()?null:d.d;S.dayOpen=null;$("#overlay").innerHTML="";S.tab="pack";S.ptab="search";render()}
  else if(a==="logtoday"){S.logDay=null;render()}
  else if(a==="month"){S.month=new Date(S.month.getFullYear(),S.month.getMonth()+(+d.dir),1);renderTrophies()}
  else if(a==="goals"){openGoals(false)}
  else if(a==="pickhero"){document.querySelectorAll(".chars button").forEach(b=>b.setAttribute("aria-pressed",String(b===el)));el.closest("form").dataset.hero=d.h;
    document.documentElement.style.setProperty("--hero",`url(${asset(`assets/img/hero_${d.h}.png`)})`);sfx("sfx_coin")}
  else if(a==="gpre"){document.querySelectorAll(".goalpick:not(.homepick):not(.dietpick) button").forEach(b=>{const on=b===el;b.setAttribute("aria-pressed",String(on));b.className="btn "+(on?"b-gold":"b-cream")});
    const p=GPRE[d.g];if(p){$("#g-k").value=p.kcal;setKmode(p.kmode);const pr=document.querySelector('.trow[data-k="protein"]');if(pr){if(!pr.querySelector(".trk").classList.contains("on"))toggleTrack(pr,true);pr.querySelector(".tv").value=p.protein}}else $("#g-k").focus()}
  else if(a==="kmode"){setKmode(d.v)}
  else if(a==="togtrack"){toggleTrack(el.closest(".trow"))}
  else if(a==="togdir"){const v=d.v==="min"?"max":"min";el.dataset.v=v;el.textContent=(v==="min"?"≥ at least ":"≤ at most ")+STATS[el.closest(".trow").dataset.k].u}
  else if(a==="demo"){startDemo()}
  else if(a==="enddemo"){endDemo()}
  else if(a==="sound"){toggleSound()}
  else if(a==="togalg"){const on=el.getAttribute("aria-pressed")!=="true";el.setAttribute("aria-pressed",String(on));el.classList.toggle("on",on)}
  else if(a==="quicklog"){openQuickLog()}
  else if(a==="qlswap"){const it=QL.items[+d.i];if(it&&it.alts.length){it.alts.push(it.row);it.row=it.alts.shift();renderQuickLog()}}
  else if(a==="qlqty"){const it=QL.items[+d.i];if(it){it.qty=Math.max(0.5,Math.min(12,it.qty+(+d.dq)));renderQuickLog()}}
  else if(a==="qldrop"){QL.items.splice(+d.i,1);renderQuickLog()}
  else if(a==="qlgo"){let tot=0,n=0;for(const it of QL.items){const x=lookup(it.row._k);if(x){tot+=eat(x,it.qty);n++}}
    $("#overlay").innerHTML="";sfx("sfx_coin");toast(`Logged ${n} item${n===1?"":"s"} · +${fmt(tot)} DMG`);render();setTimeout(maybeVictory,600)}
  else if(a==="backup"){const blob=JSON.stringify({app:"commons-quest",v:1,exported:new Date().toISOString(),profile:PROFILE,days:DAYS,foods:CUSTOM,goals:GOALS,faves:FAVES});
    try{const u=URL.createObjectURL(new Blob([blob],{type:"application/json"}));const a2=document.createElement("a");a2.href=u;a2.download="commons-quest-backup.json";document.body.appendChild(a2);a2.click();a2.remove();setTimeout(()=>URL.revokeObjectURL(u),2000)}catch(e){}
    try{navigator.clipboard&&navigator.clipboard.writeText(blob)}catch(e){}toast("Backup saved (also copied)")}
  else if(a==="restore"){const inp=document.createElement("input");inp.type="file";inp.accept="application/json,.json";inp.onchange=()=>{const fr=new FileReader();fr.onload=()=>restoreFrom(fr.result);fr.readAsText(inp.files[0])};inp.click()}
  else if(a==="nope"){PROFILE.nope=[...new Set([...(PROFILE.nope||[]),d.n])].slice(-200);saveProfile();toast("Got it. I won't suggest that again.");if(S.tab==="battle")renderBattle();else{const y=window.scrollY;render();window.scrollTo(0,y)}}
  else if(a==="sethome"){document.querySelectorAll(".homepick button").forEach(b=>{const on=b===el;b.setAttribute("aria-pressed",String(on));b.className="btn "+(on?"b-gold":"b-cream")});el.closest("form").dataset.home=d.h}
  else if(a==="setdiet"){document.querySelectorAll(".dietpick button").forEach(b=>{const on=b===el;b.setAttribute("aria-pressed",String(on));b.className="btn "+(on?"b-gold":"b-cream")});el.closest("form").dataset.diet=d.v}
  else if(a==="closesheet"){if($("#goalf")&&$("#goalf").dataset.first==="1")return;S.dayOpen=null;$("#overlay").innerHTML="";applyHero()}
  else if(a==="closevictory"){$("#overlay").innerHTML="";S.tab="trophies";render()}
});
document.addEventListener("toggle",ev=>{const el=ev.target;if(el.classList&&el.classList.contains("stn")){S.openSt=S.openSt||{};S.openSt[el.dataset.key]=el.open}},true);
document.addEventListener("input",ev=>{if(ev.target.id==="hq"){S.q=ev.target.value;renderHallList()}else if(ev.target.id==="pq"){S.pq=ev.target.value;renderPackSearch()}});
document.addEventListener("submit",ev=>{ev.preventDefault();
  if(ev.target.id==="qlform"){openQuickLog();return}
  if(ev.target.id==="addf"){const v=id=>{const x=parseFloat($(id).value);return isNaN(x)?null:x};const n=$("#f-n").value.trim();
    if(!n){$("#f-err").textContent="Add a name.";return}if(v("#f-k")==null){$("#f-err").textContent="Add calories.";return}
    CUSTOM.push({n,s:$("#f-s").value.trim()||"1 serving",k:v("#f-k"),p:v("#f-p")||0,c:v("#f-c")||0,f:v("#f-f")||0,su:v("#f-su"),fi:v("#f-fi"),sf:v("#f-sf"),na:v("#f-na")});
    persistMeta("foods");S.adding=false;S.sel=CUSTOM.length-1;render();toast("Saved to backpack")}
  else if(ev.target.id==="goalf"){const n=id=>{const x=parseFloat($(id).value);return isNaN(x)?null:x};
    const track=[...document.querySelectorAll(".trow")].filter(r=>r.querySelector(".trk").classList.contains("on")).map(r=>({k:r.dataset.k,v:parseFloat(r.querySelector(".tv").value),dir:r.querySelector(".tdir").dataset.v}));
    const ng={kcal:n("#g-k"),kmode:$(".kmode").dataset.v,track};
    if(ng.kcal==null||ng.kcal<1200||ng.kcal>7000){$("#g-err").textContent="Calories should be between 1,200 and 7,000.";return}
    const badT=track.find(x=>!(x.v>0)||x.v>20000);if(badT){$("#g-err").textContent=`Add a number for ${STATS[badT.k].lab.toLowerCase()}.`;return}
    const first=ev.target.dataset.first==="1",h=ev.target.dataset.hero||PROFILE.hero;
    const avoid=[...document.querySelectorAll(".algpick button[aria-pressed=true]")].map(b=>b.dataset.c);
    PROFILE={...PROFILE,name:$("#g-name").value.trim().slice(0,12),hero:h,setup:true,demo:false,home:ev.target.dataset.home||PROFILE.home||(IS_OWNER?"berk":""),diet:ev.target.dataset.diet||PROFILE.diet||"any",avoid};saveProfile();applyHero();
    GOALS=normGoals(ng);persistMeta("goals");$("#overlay").innerHTML="";render();if(first){sfx("sfx_coin");toast(`Welcome, ${PROFILE.name||"hero"}! Pick a dining hall to fight.`)}else toast("Saved")}});

loadLocal();loadProfile();render();
let setupTimer=setTimeout(()=>{if(!PROFILE.setup)openGoals(true)},1200);
let HOURS=null;fetch("data/hours.json").then(r=>r.json()).then(h=>{HOURS=h;if(DATA.length)render()}).catch(()=>{});
// "open now" from today's posted hours; null when we don't know (keeps the menu-based status)
function hoursFor(hk){if(!HOURS||HOURS.date!==menuKey())return null;const name=HALLS[hk]&&HALLS[hk].retail?null:HALLS[hk]&&LOCS[HALLS[hk].locs[0]];const h=name&&HOURS.locations[name];return h||null}
function openNow(hk){const h=hoursFor(hk);if(!h)return null;if(h.closed)return{open:false,txt:"Closed today"};const n=new Date(),m=n.getHours()*60+n.getMinutes();
  const tm=t=>{const[a,b]=t.split(":").map(Number);return a*60+b},o=tm(h.open),c=tm(h.close);const f=t=>{const[a,b]=t.split(":").map(Number);const hh=a%12||12;return hh+(b?":"+String(b).padStart(2,"0"):"")+(a<12?"am":"pm")};
  if(m<o)return{open:false,txt:"Opens "+f(h.open)};if(m>=c)return{open:false,txt:"Closed · opens tomorrow"};return{open:true,txt:"Open till "+(h.close==="23:59"?"midnight":f(h.close))}}
Promise.all([fetch("data/menu.json").then(r=>r.json()),fetch("data/spr.json").then(r=>r.json())]).then(([d,sp])=>{
  SPR=sp;LOCS=d.locs;ST=d.st;DATES=d.dates;TIDX=DATES.indexOf(menuKey());
  HALLS.cc.locs=CC_NAMES.map(n=>LOCS.indexOf(n)).filter(i=>i>=0);
  DATA=d.rows.map(r=>{r._l=String(r[6]).split(",").map(Number);r._n=r[0].toLowerCase();r._k=r._n+"|"+String(r[1]).toLowerCase();r._s=r._n+" "+(ST[r[8]]||"").toLowerCase()+" "+r._l.map(i=>LOCS[i]).join(" ").toLowerCase();return r});
  BYK=new Map(DATA.map(r=>[r._k,r]));render()}).catch(()=>{$("#view").innerHTML=`<p class="hint" style="margin-top:20px">Couldn't load the menus. Reload to try again.</p>`});

// Optional: when this page runs as a Claude artifact, the owner's log also syncs to the artifact's database.
// On GitHub Pages window.claude doesn't exist, so everything stays in the browser's localStorage.
(async()=>{let user=null;try{user=await window.claude?.use?.("user")}catch(e){}
  try{IS_OWNER=!!(user&&await user.isOwner())}catch(e){IS_OWNER=false}
  if(!IS_OWNER)return;                       // visitors keep everything on their own device
  let db=null;try{db=await window.claude?.use?.("db")}catch(e){}if(!db)return;
  const W={};pushDoc=(path,body)=>{const st=W[path]||(W[path]={busy:false,pend:null});st.pend=JSON.parse(JSON.stringify(body));if(st.busy)return;st.busy=true;
    (async()=>{while(st.pend){const b=st.pend;st.pend=null;try{await db.doc(path).set(b)}catch(e){if(e&&e.code==="unavailable"){await new Promise(r=>setTimeout(r,800));try{await db.doc(path).set(b)}catch(e2){}}}}st.busy=false})()};
  const clone=x=>JSON.parse(JSON.stringify(x));let synced=false;
  db.collection("days").onSnapshot(s=>{const server=!s.metadata.fromCache;const nd={};s.docs.forEach(doc=>{nd[doc.id]=clone(doc.data())});
    if(server&&!synced){for(const id of Object.keys(DAYS))if(!nd[id]&&DAYS[id].items&&DAYS[id].items.length)persistDay(id)}
    DAYS={...DAYS,...nd};if(server)synced=true;saveLocal();refresh()},()=>{});
  const meta=(name,apply,has)=>db.doc("meta/"+name).onSnapshot(s=>{if(s.exists)apply(clone(s.data()));else if(!s.metadata.fromCache&&has())persistMeta(name);saveLocal();refresh()},()=>{});
  meta("foods",d=>{if(Array.isArray(d.items))CUSTOM=d.items},()=>CUSTOM.length>0);
  meta("goals",d=>{GOALS=normGoals(d)},()=>false);
  meta("faves",d=>{if(Array.isArray(d.keys))FAVES=d.keys},()=>FAVES.length>0);
  db.doc("meta/profile").onSnapshot(sn=>{if(sn.exists){PROFILE={...PROFILE,...clone(sn.data())};try{localStorage.setItem("gq-profile",JSON.stringify(PROFILE))}catch(e){}applyHero();
      if(PROFILE.setup&&$("#goalf")&&$("#goalf").dataset.first==="1")$("#overlay").innerHTML="";refresh()}},()=>{});
})();

// installable app + offline menus (only on a real web host, not inside an embedded preview)
if ("serviceWorker" in navigator && location.protocol === "https:" && !window.claude) navigator.serviceWorker.register("sw.js").catch(() => {});
