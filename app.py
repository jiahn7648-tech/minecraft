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
body { background:#000; overflow:hidden; font-family:monospace; user-select:none; }
canvas { display:block; outline:none; width:100vw; height:100vh; cursor:move; }
#start {
  position:fixed; inset:0; background:rgba(0,0,0,0.92);
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  color:#fff; z-index:999;
}
#start h1 { font-size:42px; color:#4caf50; text-shadow:3px 3px 0 #1b5e20; margin-bottom:10px; }
#start p  { color:#ccc; margin:6px 0; font-size:14px; }
#start button {
  margin-top:25px; padding:12px 44px; font-size:18px; font-family:monospace;
  background:#4caf50; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;
}
#start button:hover { background:#66bb6a; }
#hud { position:fixed; inset:0; pointer-events:none; display:none; }
#cross {
  position:absolute; top:50%; left:50%;
  transform:translate(-50%,-50%); width:20px; height:20px;
}
#cross::before,#cross::after {
  content:''; position:absolute; background:rgba(255,255,255,0.9);
  box-shadow:0 0 2px #000;
}
#cross::before { width:2px; height:20px; left:9px; top:0; }
#cross::after  { width:20px; height:2px; left:0; top:9px; }
#info {
  position:absolute; top:12px; left:12px;
  color:#fff; font-size:13px; line-height:1.8;
  text-shadow:1px 1px 2px #000; background:rgba(0,0,0,0.3); padding:8px; border-radius:4px;
}
#tip {
  position:absolute; top:12px; right:12px;
  color:#ddd; font-size:12px; line-height:1.8;
  text-shadow:1px 1px 2px #000; text-align:right; background:rgba(0,0,0,0.3); padding:8px; border-radius:4px;
}
#hotbar {
  position:absolute; bottom:20px; left:50%; transform:translateX(-50%);
  display:flex; gap:6px; pointer-events:auto; background:rgba(0,0,0,0.5); padding:6px; border-radius:6px;
}
.slot {
  width:52px; height:52px; border:2px solid #555; background:rgba(255,255,255,0.1);
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  cursor:pointer; border-radius:4px; position:relative;
}
.slot.active { border-color:#fff; background:rgba(255,255,255,0.3); box-shadow:0 0 8px #fff; }
.slot-icon { width:28px; height:28px; border-radius:2px; image-rendering:pixelated; }
.slot-label { font-size:9px; color:#eee; margin-top:2px; font-weight:bold; }
.slot-num   { position:absolute; top:2px; left:4px; font-size:9px; color:#aaa; }
</style>
</head>
<body>
<canvas id="c" tabindex="0"></canvas>

<div id="start">
  <h1>⛏ MINECRAFT 3D</h1>
  <p style="color:#cef;font-size:15px;margin-bottom:14px">텍스처 버전 — Canvas 픽셀아트 텍스처</p>
  <p>🖱 <b>마우스 드래그</b>: 시점 회전</p>
  <p>💡 <b>G 키</b>: 1인칭 ↔ 3인칭 시점 전환</p>
  <p>⏳ <b>모래 블록(6번)</b>: 공중에 설치하면 아래로 떨어집니다!</p>
  <p>W, A, S, D: 이동 | Space: 점프 | 좌클릭: 제거 | 우클릭: 설치</p>
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
    <b>마우스 드래그</b>: 시점 회전<br>
    <b>G</b>: 1인칭/3인칭 전환<br>
    좌클릭: 블록제거 | 우클릭: 블록설치<br>
    1~7: 슬롯 선택
  </div>
  <div id="hotbar"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>

// =====================================================================
// 🎨 텍스처 생성기 (Canvas 픽셀아트 16×16)
// =====================================================================
function makeCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}

function px(ctx, x, y, hex) {
  ctx.fillStyle = hex;
  ctx.fillRect(x, y, 1, 1);
}

// 노이즈 헬퍼 (간단한 해시 기반)
function noise(x, y, seed) {
  const n = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
  return n - Math.floor(n);
}
function vary(hex, amount, x, y, seed=0) {
  const n = (noise(x, y, seed) - 0.5) * amount;
  const r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16), b = parseInt(hex.slice(5,7),16);
  const clamp = v => Math.max(0, Math.min(255, Math.round(v+n*255)));
  return `rgb(${clamp(r)},${clamp(g)},${clamp(b)})`;
}

// --- 잔디 윗면 ---
function makeGrassTop() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  const base = '#5d9e2f';
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,1);
    let col;
    if(n < 0.15) col = '#4a8a24';
    else if(n < 0.55) col = '#5d9e2f';
    else if(n < 0.80) col = '#6cb230';
    else col = '#7dc435';
    // 살짝 어두운 점 (흙 노출)
    if(noise(x,y,7) < 0.06) col = '#4a7a20';
    ctx.fillStyle = col; ctx.fillRect(x,y,1,1);
  }
  return c;
}

// --- 잔디 옆면 ---
function makeGrassSide() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  // 위 3픽셀: 초록
  for(let y=0;y<3;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,2);
    ctx.fillStyle = n < 0.5 ? '#5d9e2f' : '#6cb230';
    ctx.fillRect(x,y,1,1);
  }
  // 나머지: 흙
  for(let y=3;y<16;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,3);
    let col;
    if(n < 0.2) col = '#7a5230';
    else if(n < 0.6) col = '#8B6340';
    else col = '#9e7450';
    ctx.fillStyle = col; ctx.fillRect(x,y,1,1);
  }
  return c;
}

// --- 흙 ---
function makeDirt() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,4);
    let col;
    if(n < 0.18) col = '#7a5230';
    else if(n < 0.55) col = '#8B6340';
    else if(n < 0.82) col = '#9e7450';
    else col = '#6b4828';
    // 작은 돌 반점
    if(noise(x,y,9) < 0.04) col = '#6a5040';
    ctx.fillStyle = col; ctx.fillRect(x,y,1,1);
  }
  return c;
}

// --- 돌 ---
function makeStone() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,5);
    let col;
    if(n < 0.22) col = '#6e6e6e';
    else if(n < 0.55) col = '#888888';
    else if(n < 0.82) col = '#999999';
    else col = '#7a7a7a';
    // 균열선
    if(noise(x,y,11) < 0.03) col = '#555555';
    ctx.fillStyle = col; ctx.fillRect(x,y,1,1);
  }
  return c;
}

// --- 나무 옆면 (나이테 + 세로 결) ---
function makeLogSide() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,6);
    // 세로 결 (x 기반)
    const stripe = Math.sin(x * 1.1 + noise(x,y,13)*2) * 0.5 + 0.5;
    let col;
    if(stripe < 0.3) col = '#5c3310';
    else if(stripe < 0.6) col = '#6e4118';
    else col = '#7a4e20';
    if(n < 0.1) col = '#4e2c0e';
    ctx.fillStyle = col; ctx.fillRect(x,y,1,1);
  }
  // 테두리선
  for(let i=0;i<16;i++) {
    ctx.fillStyle = '#4a2a0c'; ctx.fillRect(0,i,1,1); ctx.fillRect(15,i,1,1);
  }
  return c;
}

// --- 나무 윗면 (나이테) ---
function makeLogTop() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const cx = x-7.5, cy = y-7.5;
    const dist = Math.sqrt(cx*cx+cy*cy);
    const ring = (Math.sin(dist * 1.4) + 1) / 2;
    let col;
    if(ring < 0.35) col = '#5c3310';
    else if(ring < 0.65) col = '#7a4e20';
    else col = '#6b4218';
    ctx.fillStyle = col; ctx.fillRect(x,y,1,1);
  }
  // 외곽 껍질
  for(let i=0;i<16;i++) {
    ctx.fillStyle = '#3e2008'; ctx.fillRect(0,i,1,1); ctx.fillRect(15,i,1,1);
    ctx.fillRect(i,0,1,1); ctx.fillRect(i,15,1,1);
  }
  return c;
}

// --- 잎 ---
function makeLeaves() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,8);
    if(n < 0.12) {
      ctx.fillStyle = 'rgba(0,0,0,0)'; // 투명 (구멍)
    } else {
      let col;
      if(n < 0.35) col = '#1e6b1a';
      else if(n < 0.65) col = '#2e7d32';
      else col = '#388e3c';
      ctx.fillStyle = col; ctx.fillRect(x,y,1,1);
    }
  }
  return c;
}

// --- 모래 ---
function makeSand() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
    const n = noise(x,y,10);
    let col;
    if(n < 0.20) col = '#c8a85a';
    else if(n < 0.55) col = '#d4b483';
    else if(n < 0.82) col = '#dfc490';
    else col = '#c0a070';
    // 작은 알갱이
    if(noise(x,y,14) < 0.07) col = '#b89050';
    ctx.fillStyle = col; ctx.fillRect(x,y,1,1);
  }
  return c;
}

// --- 툴 (곡괭이) 아이콘용 ---
function makeToolIcon() {
  const c = makeCanvas(16,16); const ctx = c.getContext('2d');
  ctx.fillStyle = '#1a1a1a'; ctx.fillRect(0,0,16,16);
  // 자루
  const stickColor = '#8b5a2b';
  [[7,14],[8,13],[9,12],[10,11],[11,10],[12,9]].forEach(([x,y])=>{ctx.fillStyle=stickColor;ctx.fillRect(x,y,1,1);});
  // 헤드
  const headColor = '#b0bec5';
  [[2,4],[3,3],[4,2],[5,3],[6,4],[7,5],[8,6],[9,7],[10,8],[11,9]].forEach(([x,y])=>{ctx.fillStyle=headColor;ctx.fillRect(x,y,2,2);});
  [[3,4],[4,3],[5,2]].forEach(([x,y])=>{ctx.fillStyle='#cfd8dc';ctx.fillRect(x,y,1,1);});
  return c;
}

// Canvas → Three.js Texture
function canvasToTexture(canvas, opts={}) {
  const tex = new THREE.CanvasTexture(canvas);
  tex.magFilter = THREE.NearestFilter;
  tex.minFilter = THREE.NearestFilter;
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  if(opts.transparent) tex.format = THREE.RGBAFormat;
  return tex;
}

// =====================================================================
// 텍스처 빌드
// =====================================================================
const TEX = {};
function buildTextures() {
  TEX.grassTop   = canvasToTexture(makeGrassTop());
  TEX.grassSide  = canvasToTexture(makeGrassSide());
  TEX.dirt       = canvasToTexture(makeDirt());
  TEX.stone      = canvasToTexture(makeStone());
  TEX.logSide    = canvasToTexture(makeLogSide());
  TEX.logTop     = canvasToTexture(makeLogTop());
  TEX.leaves     = canvasToTexture(makeLeaves(), {transparent:true});
  TEX.sand       = canvasToTexture(makeSand());
  TEX.toolIcon   = makeToolIcon(); // canvas 그대로 (HUD용)
}

// =====================================================================
// 블록 머티리얼 팩토리
//  - 잔디: [rt, lf, tp, bt, fr, bk] = [right,left,top,bottom,front,back]
//    Three.js BoxGeometry face order: +X,-X,+Y,-Y,+Z,-Z
// =====================================================================
function makeMat(tex, opts={}) {
  return new THREE.MeshLambertMaterial({
    map: tex,
    transparent: opts.transparent || false,
    alphaTest: opts.alphaTest || 0,
    side: opts.side || THREE.FrontSide,
  });
}

const BLOCK_MATS = {};
function buildMaterials() {
  // ID 0: 툴 (렌더 안 됨 — 더미)
  BLOCK_MATS[0] = null;

  // ID 1: 잔디 [+X,-X,+Y,-Y,+Z,-Z]
  BLOCK_MATS[1] = [
    makeMat(TEX.grassSide),
    makeMat(TEX.grassSide),
    makeMat(TEX.grassTop),
    makeMat(TEX.dirt),
    makeMat(TEX.grassSide),
    makeMat(TEX.grassSide),
  ];

  // ID 2: 흙
  BLOCK_MATS[2] = makeMat(TEX.dirt);

  // ID 3: 돌
  BLOCK_MATS[3] = makeMat(TEX.stone);

  // ID 4: 나무 [side, side, top, top, side, side]
  BLOCK_MATS[4] = [
    makeMat(TEX.logSide), makeMat(TEX.logSide),
    makeMat(TEX.logTop),  makeMat(TEX.logTop),
    makeMat(TEX.logSide), makeMat(TEX.logSide),
  ];

  // ID 5: 잎 (투명)
  BLOCK_MATS[5] = makeMat(TEX.leaves, {transparent:true, alphaTest:0.1, side:THREE.DoubleSide});

  // ID 6: 모래
  BLOCK_MATS[6] = makeMat(TEX.sand);
}

// =====================================================================
// 월드 / 씬
// =====================================================================
const BTYPES = [
  {name:'철 곡괭이', isTool:true,  color:0xb0bec5},
  {name:'잔디',      isTool:false, color:0x5d9e2f},
  {name:'흙',        isTool:false, color:0x8B6340},
  {name:'돌',        isTool:false, color:0x888888},
  {name:'나무',      isTool:false, color:0x8B4513},
  {name:'잎',        isTool:false, color:0x2e7d32},
  {name:'모래',      isTool:false, color:0xd4b483},
];

const voxels = {};
const WS = 36;
function vk(x,y,z){ return Math.floor(x)+'|'+Math.floor(y)+'|'+Math.floor(z); }
function getV(x,y,z){ return voxels[vk(x,y,z)]; }
function setV(x,y,z,id){ const k=vk(x,y,z); if(id===null) delete voxels[k]; else voxels[k]=id; }

function hAt(x,z){
  return 5+Math.round(
    Math.sin(x*0.32)*2.2+Math.cos(z*0.28)*2.2+
    Math.sin((x+z)*0.18)*1.3+Math.cos(x*0.7)*0.6
  );
}

function genWorld(){
  for(let x=0;x<WS;x++) for(let z=0;z<WS;z++){
    const h=hAt(x,z);
    for(let y=0;y<=h;y++) setV(x,y,z, y===h?1:y>=h-2?2:3);
    if(Math.random()<0.04&&h<14){
      const th=3+Math.floor(Math.random()*3);
      for(let ty=1;ty<=th;ty++) setV(x,h+ty,z,4);
      for(let lx=-2;lx<=2;lx++) for(let lz=-2;lz<=2;lz++) for(let ly=th-1;ly<=th+2;ly++)
        if(Math.abs(lx)+Math.abs(lz)+Math.abs(ly-th)<4&&getV(x+lx,h+ly,z+lz)===undefined)
          setV(x+lx,h+ly,z+lz,5);
    }
  }
}

const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(window.innerWidth,window.innerHeight);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb,22,52);

const camera = new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.05,80);
scene.add(new THREE.AmbientLight(0xffffff,0.65));
const sun=new THREE.DirectionalLight(0xffffff,0.75);
sun.position.set(20,40,15); scene.add(sun);

const baseGeo = new THREE.BoxGeometry(1,1,1);
const meshMap = {};

function getMat(id) {
  return BLOCK_MATS[id] || new THREE.MeshLambertMaterial({color:0xff00ff});
}

function addMesh(x,y,z,id){
  const k = vk(x,y,z);
  if(meshMap[k]) scene.remove(meshMap[k]);
  const mat = getMat(id);
  const m = new THREE.Mesh(baseGeo, mat);
  m.position.set(x+0.5, y+0.5, z+0.5);
  m.userData = {x,y,z};
  scene.add(m);
  meshMap[k] = m;
}
function delMesh(x,y,z){
  const k=vk(x,y,z);
  if(meshMap[k]){ scene.remove(meshMap[k]); delete meshMap[k]; }
}
function buildScene(){
  for(const k in voxels){
    const [x,y,z]=k.split('|').map(Number);
    addMesh(x,y,z,voxels[k]);
  }
}

// =====================================================================
// 동물
// =====================================================================
const animals = [];
const animalGroup = new THREE.Group();
scene.add(animalGroup);

function spawnAnimals() {
  const types = [
    {name:'sheep', bodyColor:0xf5f5f5, headColor:0xe0e0e0},
    {name:'cow',   bodyColor:0x5c4033, headColor:0x3d2723}
  ];
  for(let i=0;i<8;i++){
    const type = types[Math.floor(Math.random()*types.length)];
    const ax=5+Math.random()*(WS-10), az=5+Math.random()*(WS-10);
    const ay=hAt(Math.floor(ax),Math.floor(az))+1;
    const mg = new THREE.Group();
    const body=new THREE.Mesh(new THREE.BoxGeometry(0.8,0.6,1.2),new THREE.MeshLambertMaterial({color:type.bodyColor}));
    body.position.y=0.4; mg.add(body);
    const head=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.5,0.5),new THREE.MeshLambertMaterial({color:type.headColor}));
    head.position.set(0,0.6,0.6); mg.add(head);
    const legGeo=new THREE.BoxGeometry(0.18,0.4,0.18);
    const legMat=new THREE.MeshLambertMaterial({color:type.headColor});
    [[-0.3,0,0.4],[0.3,0,0.4],[-0.3,0,-0.4],[0.3,0,-0.4]].forEach(p=>{
      const leg=new THREE.Mesh(legGeo,legMat); leg.position.set(...p); mg.add(leg);
    });
    mg.position.set(ax,ay,az);
    animalGroup.add(mg);
    animals.push({mesh:mg,x:ax,y:ay,z:az,vx:0,vz:0,changeTimer:0});
  }
}
function updateAnimals(dt){
  animals.forEach(a=>{
    a.changeTimer-=dt;
    if(a.changeTimer<=0){
      if(Math.random()<0.6){
        const angle=Math.random()*Math.PI*2;
        a.vx=Math.cos(angle)*1.5; a.vz=Math.sin(angle)*1.5;
        a.mesh.rotation.y=-angle+Math.PI/2;
      } else { a.vx=0; a.vz=0; }
      a.changeTimer=2+Math.random()*4;
    }
    a.x+=a.vx*dt; a.z+=a.vz*dt;
    const curH=hAt(Math.floor(a.x),Math.floor(a.z))+1;
    a.y=a.y>curH?a.y-9.8*dt:curH;
    a.mesh.position.set(a.x,a.y,a.z);
  });
}

// =====================================================================
// 모래 물리
// =====================================================================
const fallingSands = [];
function checkSandPhysics(){
  for(const k in voxels){
    if(voxels[k]===6){
      const [x,y,z]=k.split('|').map(Number);
      if(getV(x,y-1,z)===undefined&&y>0){
        setV(x,y,z,null); delMesh(x,y,z);
        const sm=new THREE.Mesh(baseGeo,getMat(6));
        sm.position.set(x+0.5,y+0.5,z+0.5);
        scene.add(sm);
        fallingSands.push({mesh:sm,x,y,z});
      }
    }
  }
}
function updateSandPhysics(dt){
  for(let i=fallingSands.length-1;i>=0;i--){
    const s=fallingSands[i];
    s.mesh.position.y-=12*dt;
    const nextY=Math.floor(s.mesh.position.y-0.5);
    if(getV(s.x,nextY,s.z)!==undefined||nextY<0){
      const landY=nextY+1;
      setV(s.x,landY,s.z,6); addMesh(s.x,landY,s.z,6);
      scene.remove(s.mesh); fallingSands.splice(i,1);
      checkSandPhysics();
    }
  }
}

// =====================================================================
// 플레이어
// =====================================================================
const PL={x:WS/2+0.5,y:13,z:WS/2+0.5,vy:0,onGround:false};
const EYE=1.6,PW=0.3,PH=1.8,SPEED=5.5,GRAV=-28,JV=9.0;
let isThirdPerson=false;
let playerModelGroup,pLeftLeg,pRightLeg,pLeftArm,pRightArm,animTime=0;

function isSolid(x,y,z){ return getV(Math.floor(x),Math.floor(y),Math.floor(z))!==undefined; }
function collidesHoriz(px,py,pz){
  for(const oy of [0.1,0.9,PH-0.1])
    if(isSolid(px-PW,py+oy,pz-PW)||isSolid(px+PW,py+oy,pz-PW)||isSolid(px-PW,py+oy,pz+PW)||isSolid(px+PW,py+oy,pz+PW)) return true;
  return false;
}
function collidesDown(px,py,pz){ return isSolid(px-PW,py,pz-PW)||isSolid(px+PW,py,pz-PW)||isSolid(px-PW,py,pz+PW)||isSolid(px+PW,py,pz+PW); }
function collidesUp(px,py,pz){ const top=py+PH; return isSolid(px-PW,top,pz-PW)||isSolid(px+PW,top,pz-PW)||isSolid(px-PW,top,pz+PW)||isSolid(px+PW,top,pz+PW); }
function movePlayer(dx,dy,dz){
  PL.x+=dx; if(collidesHoriz(PL.x,PL.y,PL.z)) PL.x-=dx;
  PL.z+=dz; if(collidesHoriz(PL.x,PL.y,PL.z)) PL.z-=dz;
  PL.y+=dy;
  if(dy<0&&collidesDown(PL.x,PL.y,PL.z)){ PL.y=Math.floor(PL.y)+1; PL.vy=0; PL.onGround=true; }
  else if(dy>0&&collidesUp(PL.x,PL.y,PL.z)){ PL.y=Math.floor(PL.y+PH)-PH-0.005; PL.vy=0; }
}

function initPlayerModel(){
  playerModelGroup=new THREE.Group();
  const blueMat=new THREE.MeshLambertMaterial({color:0x00bcd4});
  const skinMat=new THREE.MeshLambertMaterial({color:0xe0a96d});
  const pantsMat=new THREE.MeshLambertMaterial({color:0x3f51b5});
  const torso=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.7,0.25),blueMat); torso.position.y=0.75; playerModelGroup.add(torso);
  const head=new THREE.Mesh(new THREE.BoxGeometry(0.35,0.35,0.35),skinMat); head.position.y=1.25; playerModelGroup.add(head);
  const legGeo=new THREE.BoxGeometry(0.2,0.4,0.22);
  pLeftLeg=new THREE.Mesh(legGeo,pantsMat); pLeftLeg.position.set(-0.13,0.2,0);
  pRightLeg=new THREE.Mesh(legGeo,pantsMat); pRightLeg.position.set(0.13,0.2,0);
  playerModelGroup.add(pLeftLeg,pRightLeg);
  const armGeo=new THREE.BoxGeometry(0.18,0.6,0.2);
  pLeftArm=new THREE.Mesh(armGeo,skinMat); pLeftArm.position.set(-0.35,0.7,0);
  pRightArm=new THREE.Mesh(armGeo,skinMat); pRightArm.position.set(0.35,0.7,0);
  playerModelGroup.add(pLeftArm,pRightArm);
  scene.add(playerModelGroup);
  playerModelGroup.visible=false;
}

// =====================================================================
// 1인칭 손
// =====================================================================
let handGroup, current3DItem, swingTime=0, isSwinging=false;
function init3DHand(){
  handGroup=new THREE.Group();
  scene.add(handGroup);
  rebuild3DHandItem();
}
function rebuild3DHandItem(){
  if(!handGroup) return;
  while(handGroup.children.length>0) handGroup.remove(handGroup.children[0]);
  const armMesh=new THREE.Mesh(new THREE.BoxGeometry(0.25,0.25,0.7),new THREE.MeshLambertMaterial({color:0xe0a96d}));
  armMesh.position.set(0.35,-0.35,-0.6); armMesh.rotation.set(-0.2,-0.2,0); handGroup.add(armMesh);
  const current=BTYPES[selID];
  const itemGroup=new THREE.Group();
  if(current.isTool){
    const stick=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.5,0.05),new THREE.MeshLambertMaterial({color:0x8b5a2b}));
    stick.position.set(0,0.2,0); itemGroup.add(stick);
    const hd=new THREE.Mesh(new THREE.BoxGeometry(0.4,0.06,0.06),new THREE.MeshLambertMaterial({color:0xb0bec5}));
    hd.position.set(0,0.42,0); itemGroup.add(hd);
    itemGroup.rotation.set(0.3,0,-0.4);
  } else {
    // 3D 블록 미니어처 (텍스처 적용)
    const blockMesh=new THREE.Mesh(new THREE.BoxGeometry(0.22,0.22,0.22), getMat(selID));
    blockMesh.position.set(0,0.15,0); itemGroup.add(blockMesh);
  }
  itemGroup.position.set(0.35,-0.25,-0.75);
  handGroup.add(itemGroup);
  current3DItem=itemGroup;
}

function updateAnimations(dt, isMoving){
  if(handGroup){
    handGroup.position.copy(camera.position);
    handGroup.quaternion.copy(camera.quaternion);
    handGroup.visible=!isThirdPerson;
  }
  if(isSwinging&&current3DItem){
    swingTime+=dt*5.0;
    if(swingTime>Math.PI){ swingTime=0; isSwinging=false; current3DItem.rotation.x=0; }
    else current3DItem.rotation.x=Math.sin(swingTime)*1.2;
  }
  if(playerModelGroup){
    playerModelGroup.position.set(PL.x,PL.y,PL.z);
    playerModelGroup.rotation.y=yaw+Math.PI;
    if(isThirdPerson&&isMoving){
      animTime+=dt*SPEED*2.2;
      const angle=Math.sin(animTime)*0.6;
      pLeftLeg.rotation.x=angle; pRightLeg.rotation.x=-angle;
      pLeftArm.rotation.x=-angle*0.8; pRightArm.rotation.x=angle*0.8;
    } else {
      pLeftLeg.rotation.x=0; pRightLeg.rotation.x=0;
      pLeftArm.rotation.x=0; pRightArm.rotation.x=0;
    }
  }
}

// =====================================================================
// 조작
// =====================================================================
let yaw=0,pitch=0,selID=0,started=false;
let dragging=false,lastMX=0,lastMY=0,totalDragDist=0;
const keys={};

function focusGame(){ canvas.focus(); }
window.addEventListener('click',focusGame);

canvas.addEventListener('mousedown',e=>{
  if(!started) return;
  e.preventDefault(); focusGame();
  dragging=true; totalDragDist=0; lastMX=e.clientX; lastMY=e.clientY;
});
window.addEventListener('mousemove',e=>{
  if(!started||!dragging) return;
  const dx=e.clientX-lastMX, dy=e.clientY-lastMY;
  totalDragDist+=Math.abs(dx)+Math.abs(dy);
  yaw-=dx*0.004; pitch-=dy*0.004;
  pitch=Math.max(-1.55,Math.min(1.55,pitch));
  lastMX=e.clientX; lastMY=e.clientY;
});
window.addEventListener('mouseup',e=>{
  if(!started||!dragging) return;
  dragging=false;
  if(totalDragDist<8){
    isSwinging=true; swingTime=0;
    if(e.button===0) doBreak();
    else if(e.button===2) doPlace();
  }
});
window.addEventListener('keydown',e=>{
  keys[e.code]=true;
  const n=parseInt(e.key);
  if(n>=1&&n<=7){ selID=n-1; updateHB(); rebuild3DHandItem(); }
  if(e.code==='KeyG'){
    isThirdPerson=!isThirdPerson;
    playerModelGroup.visible=isThirdPerson;
    document.getElementById('iview').textContent=`시점: ${isThirdPerson?'3인칭':'1인칭'}`;
  }
  if(e.code==='Space') e.preventDefault();
});
window.addEventListener('keyup',e=>{ keys[e.code]=false; });
canvas.addEventListener('contextmenu',e=>e.preventDefault());
window.addEventListener('wheel',e=>{
  if(!started) return;
  selID=(selID+(e.deltaY>0?1:-1)+BTYPES.length)%BTYPES.length;
  updateHB(); rebuild3DHandItem();
},{passive:true});

const rc=new THREE.Raycaster(); rc.far=7;
function raycast(){
  rc.setFromCamera({x:0,y:0},camera);
  const hits=rc.intersectObjects(Object.values(meshMap),false);
  return hits.length?hits[0]:null;
}
function doBreak(){
  const h=raycast(); if(!h) return;
  const {x,y,z}=h.object.userData;
  setV(x,y,z,null); delMesh(x,y,z); checkSandPhysics();
}
function doPlace(){
  if(BTYPES[selID].isTool) return;
  const h=raycast(); if(!h) return;
  const n=h.face.normal, {x,y,z}=h.object.userData;
  const nx=x+Math.round(n.x), ny=y+Math.round(n.y), nz=z+Math.round(n.z);
  if(Math.abs(nx+0.5-PL.x)<PW+0.5&&ny+1>PL.y&&ny<PL.y+PH&&Math.abs(nz+0.5-PL.z)<PW+0.5) return;
  if(getV(nx,ny,nz)===undefined){ setV(nx,ny,nz,selID); addMesh(nx,ny,nz,selID); checkSandPhysics(); }
}

// =====================================================================
// HUD 핫바 — 텍스처 아이콘
// =====================================================================
function getIconDataURL(id) {
  if(id===0) return TEX.toolIcon.toDataURL();
  const map = {1:TEX.grassTop, 2:TEX.dirt, 3:TEX.stone, 4:TEX.logSide, 5:TEX.leaves, 6:TEX.sand};
  return map[id] ? map[id].image.toDataURL() : '';
}

function buildHB(){
  const hb=document.getElementById('hotbar'); hb.innerHTML='';
  BTYPES.forEach((b,i)=>{
    const d=document.createElement('div'); d.className='slot'+(i===selID?' active':'');
    const num=document.createElement('div'); num.className='slot-num'; num.textContent=i+1;
    const img=document.createElement('canvas');
    img.className='slot-icon'; img.width=16; img.height=16;
    const ctx=img.getContext('2d');
    // 아이콘 소스
    const srcCanvas = i===0 ? TEX.toolIcon :
      ({1:TEX.grassTop,2:TEX.dirt,3:TEX.stone,4:TEX.logSide,5:TEX.leaves,6:TEX.sand})[i];
    if(srcCanvas) ctx.drawImage(srcCanvas,0,0,16,16);
    img.style.imageRendering='pixelated';
    const lbl=document.createElement('div'); lbl.className='slot-label'; lbl.textContent=b.name;
    d.append(num,img,lbl);
    d.onclick=()=>{ selID=i; updateHB(); rebuild3DHandItem(); focusGame(); };
    hb.appendChild(d);
  });
}
function updateHB(){ document.querySelectorAll('.slot').forEach((s,i)=>s.classList.toggle('active',i===selID)); }

// =====================================================================
// 게임 루프
// =====================================================================
let last=0,fpsN=0,fpsT=0,fpsCur=0;
function loop(ts){
  requestAnimationFrame(loop);
  const dt=Math.min((ts-last)/1000,0.05); last=ts;
  fpsN++; fpsT+=dt;
  if(fpsT>=1){ fpsCur=fpsN; fpsN=0; fpsT=0; document.getElementById('ifps').textContent='FPS:'+fpsCur; }
  if(!started){ renderer.render(scene,camera); return; }

  updateAnimals(dt);
  updateSandPhysics(dt);

  const sy=Math.sin(yaw), cy=Math.cos(yaw);
  let mx=0,mz=0,isMoving=false;
  if(keys['KeyW']||keys['ArrowUp'])   { mx-=sy; mz-=cy; isMoving=true; }
  if(keys['KeyS']||keys['ArrowDown']) { mx+=sy; mz+=cy; isMoving=true; }
  if(keys['KeyD']||keys['ArrowRight']){ mx+=cy; mz-=sy; isMoving=true; }
  if(keys['KeyA']||keys['ArrowLeft']) { mx-=cy; mz+=sy; isMoving=true; }
  const ml=Math.sqrt(mx*mx+mz*mz); if(ml>0){ mx/=ml; mz/=ml; }

  if(keys['Space']&&PL.onGround){ PL.vy=JV; PL.onGround=false; }
  PL.vy+=GRAV*dt; PL.onGround=false;
  movePlayer(mx*SPEED*dt, PL.vy*dt, mz*SPEED*dt);
  if(PL.y<-10){ PL.y=hAt(Math.floor(PL.x),Math.floor(PL.z))+3; PL.vy=0; }

  if(!isThirdPerson){
    camera.position.set(PL.x,PL.y+EYE,PL.z);
  } else {
    const tcx=PL.x+Math.sin(yaw)*2.8*Math.cos(pitch);
    const tcz=PL.z+Math.cos(yaw)*2.8*Math.cos(pitch);
    const tcy=PL.y+EYE+Math.sin(pitch)*2.8+0.3;
    camera.position.set(tcx,tcy,tcz);
  }
  camera.quaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));
  updateAnimations(dt,isMoving);

  document.getElementById('ipos').textContent=`위치: ${Math.floor(PL.x)}, ${Math.floor(PL.y)}, ${Math.floor(PL.z)}`;
  document.getElementById('iblk').textContent=`선택: ${BTYPES[selID].name}`;
  renderer.render(scene,camera);
}

window.addEventListener('resize',()=>{
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
});

// =====================================================================
// 시작
// =====================================================================
document.getElementById('startBtn').addEventListener('click',()=>{
  document.getElementById('start').style.display='none';
  document.getElementById('hud').style.display='block';
  started=true;

  buildTextures();
  buildMaterials();

  genWorld(); buildScene(); spawnAnimals();
  PL.x=WS/2+0.5; PL.z=WS/2+0.5;
  PL.y=hAt(Math.floor(PL.x),Math.floor(PL.z))+2;

  buildHB();
  initPlayerModel();
  init3DHand();
  focusGame();
  requestAnimationFrame(loop);
});
</script>
</body>
</html>
"""

st.title("⛏ Minecraft 3D — 픽셀아트 텍스처 버전")
st.caption("Canvas로 직접 생성한 16×16 픽셀아트 텍스처 적용 | 잔디 블록은 윗면/옆면/아랫면 각각 다른 텍스처")

components.html(minecraft_html, height=750, scrolling=False)
