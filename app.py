import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Minecraft 3D (텍스처 버전)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

minecraft_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Minecraft 3D - Textured</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:100%; height:100%; background:#000; overflow:hidden; font-family:monospace; user-select:none; }
#gameWrap { position:relative; width:100%; height:100%; }
canvas#c { display:block; outline:none; width:100%; height:100%; cursor:move; }
#start {
  position:absolute; inset:0; background:rgba(0,0,0,0.92);
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  color:#fff; z-index:999;
}
#start h1 { font-size:36px; color:#4caf50; text-shadow:3px 3px 0 #1b5e20; margin-bottom:10px; }
#start p  { color:#ccc; margin:5px 0; font-size:13px; }
#start button {
  margin-top:20px; padding:10px 40px; font-size:17px; font-family:monospace;
  background:#4caf50; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;
}
#start button:hover { background:#66bb6a; }
#hud { position:absolute; inset:0; pointer-events:none; display:none; }
#cross {
  position:absolute; top:50%; left:50%;
  transform:translate(-50%,-50%); width:20px; height:20px;
}
#cross::before,#cross::after {
  content:''; position:absolute; background:rgba(255,255,255,0.9); box-shadow:0 0 2px #000;
}
#cross::before { width:2px; height:20px; left:9px; top:0; }
#cross::after  { width:20px; height:2px; left:0; top:9px; }
#info {
  position:absolute; top:10px; left:10px;
  color:#fff; font-size:12px; line-height:1.8;
  text-shadow:1px 1px 2px #000; background:rgba(0,0,0,0.35); padding:7px 10px; border-radius:4px;
}
#tip {
  position:absolute; top:10px; right:10px;
  color:#ddd; font-size:11px; line-height:1.8;
  text-shadow:1px 1px 2px #000; text-align:right; background:rgba(0,0,0,0.35); padding:7px 10px; border-radius:4px;
}
#hotbar {
  position:absolute; bottom:16px; left:50%; transform:translateX(-50%);
  display:flex; gap:5px; pointer-events:auto; background:rgba(0,0,0,0.55); padding:5px; border-radius:6px;
}
.slot {
  width:50px; height:50px; border:2px solid #555; background:rgba(255,255,255,0.08);
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  cursor:pointer; border-radius:4px; position:relative;
}
.slot.active { border-color:#fff; background:rgba(255,255,255,0.25); box-shadow:0 0 7px #fff; }
.slot-icon   { width:28px; height:28px; image-rendering:pixelated; }
.slot-label  { font-size:8px; color:#eee; margin-top:1px; font-weight:bold; }
.slot-num    { position:absolute; top:2px; left:4px; font-size:9px; color:#aaa; }
</style>
</head>
<body>
<div id="gameWrap">
  <canvas id="c" tabindex="0"></canvas>

  <div id="start">
    <h1>⛏ MINECRAFT 3D</h1>
    <p style="color:#cef;font-size:14px;margin-bottom:12px">텍스처 버전 — Canvas 픽셀아트 16×16</p>
    <p>🖱 <b>마우스 드래그</b>: 시점 회전</p>
    <p>💡 <b>G 키</b>: 1인칭 ↔ 3인칭 전환</p>
    <p>⏳ <b>모래(6번)</b>: 공중 설치 시 낙하!</p>
    <p>W A S D: 이동 | Space: 점프 | 좌클릭: 제거 | 우클릭: 설치</p>
    <button id="startBtn">▶ 게임 시작</button>
  </div>

  <div id="hud">
    <div id="cross"></div>
    <div id="info">
      <div id="ipos">위치: 0, 0, 0</div>
      <div id="iblk">선택: 철 곡괭이</div>
      <div id="iview">시점: 1인칭</div>
      <div id="ifps">FPS: --</div>
    </div>
    <div id="tip">
      <b>드래그</b>: 시점 회전<br>
      <b>G</b>: 1인칭/3인칭<br>
      좌클릭: 제거 | 우클릭: 설치<br>
      1~7: 슬롯
    </div>
    <div id="hotbar"></div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ─────────────────────────────────────────────
// 캔버스/렌더러를 DOM 크기 기준으로 초기화
// (Streamlit iframe에서 window.innerWidth/Height가 0이 되는 문제 방지)
// ─────────────────────────────────────────────
const canvas = document.getElementById('c');
const wrap   = document.getElementById('gameWrap');

function getSize() {
  const w = wrap.clientWidth  || window.innerWidth  || 800;
  const h = wrap.clientHeight || window.innerHeight || 600;
  return { w: Math.max(w, 100), h: Math.max(h, 100) };
}

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
{ const {w,h} = getSize(); renderer.setSize(w, h); }

const scene  = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 22, 52);

const { w: IW, h: IH } = getSize();
const camera = new THREE.PerspectiveCamera(75, IW / IH, 0.05, 80);
scene.add(new THREE.AmbientLight(0xffffff, 0.65));
const sun = new THREE.DirectionalLight(0xffffff, 0.75);
sun.position.set(20, 40, 15);
scene.add(sun);

window.addEventListener('resize', () => {
  const {w,h} = getSize();
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
});

// ─────────────────────────────────────────────
// 텍스처 픽셀아트 생성
// ─────────────────────────────────────────────
function makeCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}
function noise(x, y, seed) {
  const n = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
  return n - Math.floor(n);
}

function makeGrassTop() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,1);
    let col = n<0.15?'#4a8a24':n<0.55?'#5d9e2f':n<0.80?'#6cb230':'#7dc435';
    if(noise(x,y,7)<0.06) col='#4a7a20';
    ctx.fillStyle=col; ctx.fillRect(x,y,1,1);
  }
  return c;
}
function makeGrassSide() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  for(let y=0;y<3;y++) for(let x=0;x<16;x++) {
    ctx.fillStyle = noise(x,y,2)<0.5?'#5d9e2f':'#6cb230';
    ctx.fillRect(x,y,1,1);
  }
  for(let y=3;y<16;y++) for(let x=0;x<16;x++) {
    const n=noise(x,y,3);
    ctx.fillStyle = n<0.2?'#7a5230':n<0.6?'#8B6340':'#9e7450';
    ctx.fillRect(x,y,1,1);
  }
  return c;
}
function makeDirt() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n=noise(x,y,4);
    let col = n<0.18?'#7a5230':n<0.55?'#8B6340':n<0.82?'#9e7450':'#6b4828';
    if(noise(x,y,9)<0.04) col='#6a5040';
    ctx.fillStyle=col; ctx.fillRect(x,y,1,1);
  }
  return c;
}
function makeStone() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n=noise(x,y,5);
    let col = n<0.22?'#6e6e6e':n<0.55?'#888888':n<0.82?'#999999':'#7a7a7a';
    if(noise(x,y,11)<0.03) col='#555555';
    ctx.fillStyle=col; ctx.fillRect(x,y,1,1);
  }
  return c;
}
function makeLogSide() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n=noise(x,y,6);
    const stripe=(Math.sin(x*1.1+noise(x,y,13)*2)*0.5+0.5);
    let col = stripe<0.3?'#5c3310':stripe<0.6?'#6e4118':'#7a4e20';
    if(n<0.1) col='#4e2c0e';
    ctx.fillStyle=col; ctx.fillRect(x,y,1,1);
  }
  for(let i=0;i<16;i++){
    ctx.fillStyle='#4a2a0c';
    ctx.fillRect(0,i,1,1); ctx.fillRect(15,i,1,1);
  }
  return c;
}
function makeLogTop() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const cx=x-7.5, cy=y-7.5;
    const ring=(Math.sin(Math.sqrt(cx*cx+cy*cy)*1.4)+1)/2;
    ctx.fillStyle = ring<0.35?'#5c3310':ring<0.65?'#7a4e20':'#6b4218';
    ctx.fillRect(x,y,1,1);
  }
  for(let i=0;i<16;i++){
    ctx.fillStyle='#3e2008';
    ctx.fillRect(0,i,1,1); ctx.fillRect(15,i,1,1);
    ctx.fillRect(i,0,1,1); ctx.fillRect(i,15,1,1);
  }
  return c;
}
function makeLeaves() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  ctx.clearRect(0,0,16,16);
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n=noise(x,y,8);
    if(n>=0.12){
      ctx.fillStyle = n<0.35?'#1e6b1a':n<0.65?'#2e7d32':'#388e3c';
      ctx.fillRect(x,y,1,1);
    }
  }
  return c;
}
function makeSand() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n=noise(x,y,10);
    let col = n<0.20?'#c8a85a':n<0.55?'#d4b483':n<0.82?'#dfc490':'#c0a070';
    if(noise(x,y,14)<0.07) col='#b89050';
    ctx.fillStyle=col; ctx.fillRect(x,y,1,1);
  }
  return c;
}
function makeToolIcon() {
  const c = makeCanvas(16,16), ctx = c.getContext('2d');
  ctx.fillStyle='#222'; ctx.fillRect(0,0,16,16);
  [[7,14],[8,13],[9,12],[10,11],[11,10],[12,9]].forEach(([x,y])=>{ctx.fillStyle='#8b5a2b';ctx.fillRect(x,y,1,1);});
  [[2,4],[3,3],[4,2],[5,3],[6,4],[7,5],[8,6],[9,7],[10,8],[11,9]].forEach(([x,y])=>{ctx.fillStyle='#b0bec5';ctx.fillRect(x,y,2,2);});
  [[3,4],[4,3],[5,2]].forEach(([x,y])=>{ctx.fillStyle='#cfd8dc';ctx.fillRect(x,y,1,1);});
  return c;
}

function canvasToTex(c, transparent) {
  const t = new THREE.CanvasTexture(c);
  t.magFilter = THREE.NearestFilter;
  t.minFilter = THREE.NearestFilter;
  if(transparent) t.format = THREE.RGBAFormat;
  return t;
}

const TEX = {};
function buildTextures() {
  TEX.grassTop  = canvasToTex(makeGrassTop());
  TEX.grassSide = canvasToTex(makeGrassSide());
  TEX.dirt      = canvasToTex(makeDirt());
  TEX.stone     = canvasToTex(makeStone());
  TEX.logSide   = canvasToTex(makeLogSide());
  TEX.logTop    = canvasToTex(makeLogTop());
  TEX.leaves    = canvasToTex(makeLeaves(), true);
  TEX.sand      = canvasToTex(makeSand());
  TEX.toolIcon  = makeToolIcon();
}

function mat(tex, opts={}) {
  return new THREE.MeshLambertMaterial({
    map: tex,
    transparent: !!opts.transparent,
    alphaTest: opts.alphaTest || 0,
    side: opts.side || THREE.FrontSide,
  });
}

const BMATS = {};
function buildMaterials() {
  BMATS[0] = null;
  BMATS[1] = [mat(TEX.grassSide),mat(TEX.grassSide),mat(TEX.grassTop),mat(TEX.dirt),mat(TEX.grassSide),mat(TEX.grassSide)];
  BMATS[2] = mat(TEX.dirt);
  BMATS[3] = mat(TEX.stone);
  BMATS[4] = [mat(TEX.logSide),mat(TEX.logSide),mat(TEX.logTop),mat(TEX.logTop),mat(TEX.logSide),mat(TEX.logSide)];
  BMATS[5] = mat(TEX.leaves, {transparent:true, alphaTest:0.1, side:THREE.DoubleSide});
  BMATS[6] = mat(TEX.sand);
}
function getMat(id){ return BMATS[id] || new THREE.MeshLambertMaterial({color:0xff00ff}); }

// ─────────────────────────────────────────────
// 블록 타입
// ─────────────────────────────────────────────
const BTYPES = [
  {name:'철 곡괭이', isTool:true},
  {name:'잔디',      isTool:false},
  {name:'흙',        isTool:false},
  {name:'돌',        isTool:false},
  {name:'나무',      isTool:false},
  {name:'잎',        isTool:false},
  {name:'모래',      isTool:false},
];

// ─────────────────────────────────────────────
// 월드
// ─────────────────────────────────────────────
const voxels={}, WS=36;
function vk(x,y,z){ return Math.floor(x)+'|'+Math.floor(y)+'|'+Math.floor(z); }
function getV(x,y,z){ return voxels[vk(x,y,z)]; }
function setV(x,y,z,id){ const k=vk(x,y,z); if(id===null) delete voxels[k]; else voxels[k]=id; }
function hAt(x,z){
  return 5+Math.round(Math.sin(x*0.32)*2.2+Math.cos(z*0.28)*2.2+Math.sin((x+z)*0.18)*1.3+Math.cos(x*0.7)*0.6);
}
function genWorld(){
  for(let x=0;x<WS;x++) for(let z=0;z<WS;z++){
    const h=hAt(x,z);
    for(let y=0;y<=h;y++) setV(x,y,z,y===h?1:y>=h-2?2:3);
    if(Math.random()<0.04&&h<14){
      const th=3+Math.floor(Math.random()*3);
      for(let ty=1;ty<=th;ty++) setV(x,h+ty,z,4);
      for(let lx=-2;lx<=2;lx++) for(let lz=-2;lz<=2;lz++) for(let ly=th-1;ly<=th+2;ly++)
        if(Math.abs(lx)+Math.abs(lz)+Math.abs(ly-th)<4&&getV(x+lx,h+ly,z+lz)===undefined)
          setV(x+lx,h+ly,z+lz,5);
    }
  }
}

const baseGeo=new THREE.BoxGeometry(1,1,1), meshMap={};
function addMesh(x,y,z,id){
  const k=vk(x,y,z);
  if(meshMap[k]) scene.remove(meshMap[k]);
  const m=new THREE.Mesh(baseGeo,getMat(id));
  m.position.set(x+0.5,y+0.5,z+0.5);
  m.userData={x,y,z};
  scene.add(m); meshMap[k]=m;
}
function delMesh(x,y,z){ const k=vk(x,y,z); if(meshMap[k]){scene.remove(meshMap[k]);delete meshMap[k];} }
function buildScene(){ for(const k in voxels){ const[x,y,z]=k.split('|').map(Number); addMesh(x,y,z,voxels[k]); } }

// ─────────────────────────────────────────────
// 동물
// ─────────────────────────────────────────────
const animals=[], animalGroup=new THREE.Group(); scene.add(animalGroup);
function spawnAnimals(){
  const types=[{bodyColor:0xf5f5f5,headColor:0xe0e0e0},{bodyColor:0x5c4033,headColor:0x3d2723}];
  for(let i=0;i<8;i++){
    const t=types[i%2];
    const ax=5+Math.random()*(WS-10),az=5+Math.random()*(WS-10);
    const ay=hAt(Math.floor(ax),Math.floor(az))+1;
    const mg=new THREE.Group();
    const body=new THREE.Mesh(new THREE.BoxGeometry(0.8,0.6,1.2),new THREE.MeshLambertMaterial({color:t.bodyColor}));
    body.position.y=0.4; mg.add(body);
    const head=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.5,0.5),new THREE.MeshLambertMaterial({color:t.headColor}));
    head.position.set(0,0.6,0.6); mg.add(head);
    const legG=new THREE.BoxGeometry(0.18,0.4,0.18),legM=new THREE.MeshLambertMaterial({color:t.headColor});
    [[-0.3,0,0.4],[0.3,0,0.4],[-0.3,0,-0.4],[0.3,0,-0.4]].forEach(p=>{const l=new THREE.Mesh(legG,legM);l.position.set(...p);mg.add(l);});
    mg.position.set(ax,ay,az); animalGroup.add(mg);
    animals.push({mesh:mg,x:ax,y:ay,z:az,vx:0,vz:0,t:0});
  }
}
function updateAnimals(dt){
  animals.forEach(a=>{
    a.t-=dt;
    if(a.t<=0){
      if(Math.random()<0.6){const ang=Math.random()*Math.PI*2;a.vx=Math.cos(ang)*1.5;a.vz=Math.sin(ang)*1.5;a.mesh.rotation.y=-ang+Math.PI/2;}
      else{a.vx=0;a.vz=0;}
      a.t=2+Math.random()*4;
    }
    a.x+=a.vx*dt;a.z+=a.vz*dt;
    const ch=hAt(Math.floor(a.x),Math.floor(a.z))+1;
    a.y=a.y>ch?a.y-9.8*dt:ch;
    a.mesh.position.set(a.x,a.y,a.z);
  });
}

// ─────────────────────────────────────────────
// 모래 물리
// ─────────────────────────────────────────────
const fallSands=[];
function checkSand(){
  for(const k in voxels){
    if(voxels[k]===6){
      const[x,y,z]=k.split('|').map(Number);
      if(getV(x,y-1,z)===undefined&&y>0){
        setV(x,y,z,null);delMesh(x,y,z);
        const sm=new THREE.Mesh(baseGeo,getMat(6));
        sm.position.set(x+0.5,y+0.5,z+0.5);
        scene.add(sm);fallSands.push({mesh:sm,x,y,z});
      }
    }
  }
}
function updateSand(dt){
  for(let i=fallSands.length-1;i>=0;i--){
    const s=fallSands[i];s.mesh.position.y-=12*dt;
    const ny=Math.floor(s.mesh.position.y-0.5);
    if(getV(s.x,ny,s.z)!==undefined||ny<0){
      setV(s.x,ny+1,s.z,6);addMesh(s.x,ny+1,s.z,6);
      scene.remove(s.mesh);fallSands.splice(i,1);checkSand();
    }
  }
}

// ─────────────────────────────────────────────
// 플레이어
// ─────────────────────────────────────────────
const PL={x:WS/2+0.5,y:13,z:WS/2+0.5,vy:0,onGround:false};
const EYE=1.6,PW=0.3,PH=1.8,SPEED=5.5,GRAV=-28,JV=9.0;
let isThird=false,pmg=null,pLL,pRL,pLA,pRA,animT=0;

function isSolid(x,y,z){return getV(Math.floor(x),Math.floor(y),Math.floor(z))!==undefined;}
function colH(px,py,pz){for(const oy of[0.1,0.9,PH-0.1])if(isSolid(px-PW,py+oy,pz-PW)||isSolid(px+PW,py+oy,pz-PW)||isSolid(px-PW,py+oy,pz+PW)||isSolid(px+PW,py+oy,pz+PW))return true;return false;}
function colD(px,py,pz){return isSolid(px-PW,py,pz-PW)||isSolid(px+PW,py,pz-PW)||isSolid(px-PW,py,pz+PW)||isSolid(px+PW,py,pz+PW);}
function colU(px,py,pz){const t=py+PH;return isSolid(px-PW,t,pz-PW)||isSolid(px+PW,t,pz-PW)||isSolid(px-PW,t,pz+PW)||isSolid(px+PW,t,pz+PW);}
function moveP(dx,dy,dz){
  PL.x+=dx;if(colH(PL.x,PL.y,PL.z))PL.x-=dx;
  PL.z+=dz;if(colH(PL.x,PL.y,PL.z))PL.z-=dz;
  PL.y+=dy;
  if(dy<0&&colD(PL.x,PL.y,PL.z)){PL.y=Math.floor(PL.y)+1;PL.vy=0;PL.onGround=true;}
  else if(dy>0&&colU(PL.x,PL.y,PL.z)){PL.y=Math.floor(PL.y+PH)-PH-0.005;PL.vy=0;}
}
function initPModel(){
  pmg=new THREE.Group();
  const bm=new THREE.MeshLambertMaterial({color:0x00bcd4}),sm=new THREE.MeshLambertMaterial({color:0xe0a96d}),pm=new THREE.MeshLambertMaterial({color:0x3f51b5});
  const torso=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.7,0.25),bm);torso.position.y=0.75;pmg.add(torso);
  const head=new THREE.Mesh(new THREE.BoxGeometry(0.35,0.35,0.35),sm);head.position.y=1.25;pmg.add(head);
  const lg=new THREE.BoxGeometry(0.2,0.4,0.22);
  pLL=new THREE.Mesh(lg,pm);pLL.position.set(-0.13,0.2,0);
  pRL=new THREE.Mesh(lg,pm);pRL.position.set(0.13,0.2,0);
  pmg.add(pLL,pRL);
  const ag=new THREE.BoxGeometry(0.18,0.6,0.2);
  pLA=new THREE.Mesh(ag,sm);pLA.position.set(-0.35,0.7,0);
  pRA=new THREE.Mesh(ag,sm);pRA.position.set(0.35,0.7,0);
  pmg.add(pLA,pRA);
  scene.add(pmg);pmg.visible=false;
}

// ─────────────────────────────────────────────
// 1인칭 손
// ─────────────────────────────────────────────
let handG=null,curItem=null,swT=0,swing=false;
function initHand(){handG=new THREE.Group();scene.add(handG);rebuildHand();}
function rebuildHand(){
  if(!handG)return;
  while(handG.children.length)handG.remove(handG.children[0]);
  const arm=new THREE.Mesh(new THREE.BoxGeometry(0.25,0.25,0.7),new THREE.MeshLambertMaterial({color:0xe0a96d}));
  arm.position.set(0.35,-0.35,-0.6);arm.rotation.set(-0.2,-0.2,0);handG.add(arm);
  const ig=new THREE.Group();
  if(BTYPES[selID].isTool){
    const st=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.5,0.05),new THREE.MeshLambertMaterial({color:0x8b5a2b}));st.position.set(0,0.2,0);ig.add(st);
    const hd=new THREE.Mesh(new THREE.BoxGeometry(0.4,0.06,0.06),new THREE.MeshLambertMaterial({color:0xb0bec5}));hd.position.set(0,0.42,0);ig.add(hd);
    ig.rotation.set(0.3,0,-0.4);
  }else{
    const bm=new THREE.Mesh(new THREE.BoxGeometry(0.22,0.22,0.22),getMat(selID));bm.position.set(0,0.15,0);ig.add(bm);
  }
  ig.position.set(0.35,-0.25,-0.75);handG.add(ig);curItem=ig;
}
function updateAnim(dt,mov){
  if(handG){handG.position.copy(camera.position);handG.quaternion.copy(camera.quaternion);handG.visible=!isThird;}
  if(swing&&curItem){swT+=dt*5;if(swT>Math.PI){swT=0;swing=false;curItem.rotation.x=0;}else curItem.rotation.x=Math.sin(swT)*1.2;}
  if(pmg){
    pmg.position.set(PL.x,PL.y,PL.z);pmg.rotation.y=yaw+Math.PI;
    if(isThird&&mov){animT+=dt*SPEED*2.2;const a=Math.sin(animT)*0.6;pLL.rotation.x=a;pRL.rotation.x=-a;pLA.rotation.x=-a*0.8;pRA.rotation.x=a*0.8;}
    else{pLL.rotation.x=0;pRL.rotation.x=0;pLA.rotation.x=0;pRA.rotation.x=0;}
  }
}

// ─────────────────────────────────────────────
// 입력
// ─────────────────────────────────────────────
let yaw=0,pitch=0,selID=0,started=false;
let drag=false,lmx=0,lmy=0,tdist=0;
const keys={};

function focusGame(){canvas.focus();}
wrap.addEventListener('click',focusGame);

canvas.addEventListener('mousedown',e=>{if(!started)return;e.preventDefault();focusGame();drag=true;tdist=0;lmx=e.clientX;lmy=e.clientY;});
window.addEventListener('mousemove',e=>{
  if(!started||!drag)return;
  const dx=e.clientX-lmx,dy=e.clientY-lmy;
  tdist+=Math.abs(dx)+Math.abs(dy);
  yaw-=dx*0.004;pitch-=dy*0.004;
  pitch=Math.max(-1.55,Math.min(1.55,pitch));
  lmx=e.clientX;lmy=e.clientY;
});
window.addEventListener('mouseup',e=>{
  if(!started||!drag)return;drag=false;
  if(tdist<8){swing=true;swT=0;if(e.button===0)doBreak();else if(e.button===2)doPlace();}
});
window.addEventListener('keydown',e=>{
  keys[e.code]=true;
  const n=parseInt(e.key);
  if(n>=1&&n<=7){selID=n-1;updateHB();rebuildHand();}
  if(e.code==='KeyG'){isThird=!isThird;pmg.visible=isThird;document.getElementById('iview').textContent='시점: '+(isThird?'3인칭':'1인칭');}
  if(e.code==='Space')e.preventDefault();
});
window.addEventListener('keyup',e=>{keys[e.code]=false;});
canvas.addEventListener('contextmenu',e=>e.preventDefault());
window.addEventListener('wheel',e=>{if(!started)return;selID=(selID+(e.deltaY>0?1:-1)+BTYPES.length)%BTYPES.length;updateHB();rebuildHand();},{passive:true});

const rc=new THREE.Raycaster();rc.far=7;
function raycast(){rc.setFromCamera({x:0,y:0},camera);const h=rc.intersectObjects(Object.values(meshMap),false);return h.length?h[0]:null;}
function doBreak(){const h=raycast();if(!h)return;const{x,y,z}=h.object.userData;setV(x,y,z,null);delMesh(x,y,z);checkSand();}
function doPlace(){
  if(BTYPES[selID].isTool)return;
  const h=raycast();if(!h)return;
  const n=h.face.normal,{x,y,z}=h.object.userData;
  const nx=x+Math.round(n.x),ny=y+Math.round(n.y),nz=z+Math.round(n.z);
  if(Math.abs(nx+0.5-PL.x)<PW+0.5&&ny+1>PL.y&&ny<PL.y+PH&&Math.abs(nz+0.5-PL.z)<PW+0.5)return;
  if(getV(nx,ny,nz)===undefined){setV(nx,ny,nz,selID);addMesh(nx,ny,nz,selID);checkSand();}
}

// ─────────────────────────────────────────────
// 핫바
// ─────────────────────────────────────────────
function getIconCanvas(id){
  const map={0:TEX.toolIcon,1:TEX.grassTop,2:TEX.dirt,3:TEX.stone,4:TEX.logSide,5:TEX.leaves,6:TEX.sand};
  return map[id];
}
function buildHB(){
  const hb=document.getElementById('hotbar');hb.innerHTML='';
  BTYPES.forEach((b,i)=>{
    const d=document.createElement('div');d.className='slot'+(i===selID?' active':'');
    const num=document.createElement('div');num.className='slot-num';num.textContent=i+1;
    const ic=document.createElement('canvas');ic.className='slot-icon';ic.width=28;ic.height=28;
    const ctx=ic.getContext('2d');
    const src=getIconCanvas(i);
    if(src){ctx.imageSmoothingEnabled=false;ctx.drawImage(src,0,0,28,28);}
    const lbl=document.createElement('div');lbl.className='slot-label';lbl.textContent=b.name;
    d.append(num,ic,lbl);
    d.onclick=()=>{selID=i;updateHB();rebuildHand();focusGame();};
    hb.appendChild(d);
  });
}
function updateHB(){document.querySelectorAll('.slot').forEach((s,i)=>s.classList.toggle('active',i===selID));}

// ─────────────────────────────────────────────
// 게임 루프
// ─────────────────────────────────────────────
let last=0,fpsN=0,fpsT=0,fpsCur=0;
function loop(ts){
  requestAnimationFrame(loop);
  const dt=Math.min((ts-last)/1000,0.05);last=ts;
  fpsN++;fpsT+=dt;
  if(fpsT>=1){fpsCur=fpsN;fpsN=0;fpsT=0;document.getElementById('ifps').textContent='FPS:'+fpsCur;}
  if(!started){renderer.render(scene,camera);return;}

  updateAnimals(dt);updateSand(dt);

  const sy=Math.sin(yaw),cy=Math.cos(yaw);
  let mx=0,mz=0,mov=false;
  if(keys['KeyW']||keys['ArrowUp']){mx-=sy;mz-=cy;mov=true;}
  if(keys['KeyS']||keys['ArrowDown']){mx+=sy;mz+=cy;mov=true;}
  if(keys['KeyD']||keys['ArrowRight']){mx+=cy;mz-=sy;mov=true;}
  if(keys['KeyA']||keys['ArrowLeft']){mx-=cy;mz+=sy;mov=true;}
  const ml=Math.sqrt(mx*mx+mz*mz);if(ml>0){mx/=ml;mz/=ml;}

  if(keys['Space']&&PL.onGround){PL.vy=JV;PL.onGround=false;}
  PL.vy+=GRAV*dt;PL.onGround=false;
  moveP(mx*SPEED*dt,PL.vy*dt,mz*SPEED*dt);
  if(PL.y<-10){PL.y=hAt(Math.floor(PL.x),Math.floor(PL.z))+3;PL.vy=0;}

  if(!isThird){
    camera.position.set(PL.x,PL.y+EYE,PL.z);
  }else{
    camera.position.set(
      PL.x+Math.sin(yaw)*2.8*Math.cos(pitch),
      PL.y+EYE+Math.sin(pitch)*2.8+0.3,
      PL.z+Math.cos(yaw)*2.8*Math.cos(pitch)
    );
  }
  camera.quaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));
  updateAnim(dt,mov);

  document.getElementById('ipos').textContent=`위치: ${Math.floor(PL.x)}, ${Math.floor(PL.y)}, ${Math.floor(PL.z)}`;
  document.getElementById('iblk').textContent=`선택: ${BTYPES[selID].name}`;
  renderer.render(scene,camera);
}

// ─────────────────────────────────────────────
// 시작 버튼 — 모든 초기화를 여기서 순서대로 실행
// ─────────────────────────────────────────────
document.getElementById('startBtn').addEventListener('click', () => {
  document.getElementById('start').style.display = 'none';
  document.getElementById('hud').style.display = 'block';
  started = true;

  // 1. 텍스처/머티리얼 (동기, 순서 중요)
  buildTextures();
  buildMaterials();

  // 2. 월드 & 씬
  genWorld();
  buildScene();
  spawnAnimals();

  // 3. 플레이어 위치
  PL.x = WS/2+0.5; PL.z = WS/2+0.5;
  PL.y = hAt(Math.floor(PL.x), Math.floor(PL.z)) + 2;

  // 4. UI / 3D 오브젝트
  buildHB();
  initPModel();
  initHand();

  // 5. 렌더러 크기 재확인 (iframe 완전 로드 후)
  const {w, h} = getSize();
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();

  focusGame();
  requestAnimationFrame(loop);
});
</script>
</body>
</html>
"""

st.title("⛏ Minecraft 3D — 픽셀아트 텍스처 버전")
st.caption("Canvas 생성 16×16 픽셀아트 텍스처 | 잔디 윗/옆/아랫면 분리 | Streamlit iframe 크기 버그 수정")
components.html(minecraft_html, height=750, scrolling=False)
