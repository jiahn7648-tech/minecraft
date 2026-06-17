import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Minecraft 3D (Pointer Lock) - Streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

minecraft_pointerlock_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Minecraft 3D - Pointer Lock</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#000; overflow:hidden; font-family:monospace; user-select:none; }
canvas { display:block; outline:none; width:100vw; height:100vh; cursor:pointer; }
#start {
  position:fixed; inset:0; background:rgba(0,0,0,0.9);
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
  width:50px; height:50px; border:2px solid #555; background:rgba(255,255,255,0.1);
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  cursor:pointer; border-radius:4px; position:relative;
}
.slot.active { border-color:#fff; background:rgba(255,255,255,0.3); box-shadow: 0 0 8px #fff; }
.slot-color { width:26px; height:26px; border-radius:3px; border:1px solid rgba(255,255,255,0.4); }
.slot-label { font-size:9px; color:#eee; margin-top:2px; font-weight:bold; }
.slot-num   { position:absolute; top:2px; left:4px; font-size:9px; color:#aaa; }
#lock-warn {
  position: absolute; bottom: 90px; left: 50%; transform: translateX(-50%);
  background: rgba(0,0,0,0.7); color: #ffeb3b; padding: 6px 16px; border-radius: 20px;
  font-size: 12px; display: none; font-weight: bold;
}
</style>
</head>
<body>
<canvas id="c" tabindex="0"></canvas>

<div id="start">
  <h1>⛏ MINECRAFT 3D</h1>
  <p style="color:#aef;font-size:15px;margin-bottom:14px">Pointer Lock Edition</p>
  <p>🖱 <b>화면 클릭</b>: 마우스 고정 및 게임 제어 시작</p>
  <p>W, A, S, D / 방향키: 이동 &nbsp;|&nbsp; Space: 점프</p>
  <p>좌클릭: 블록 제거 &nbsp;|&nbsp; 우클릭: 블록 설치</p>
  <p>1 ~ 7 / 마우스 휠: 블록 선택</p>
  <p style="color:#ffaa00; margin-top:10px;">※ 마우스를 풀려면 <b>ESC</b> 키를 누르세요.</p>
  <button id="startBtn">▶ 게임 시작</button>
</div>

<div id="hud">
  <div id="cross"></div>
  <div id="info">
    <div id="ipos">위치: 0, 0, 0</div>
    <div id="iblk">블록: 잔디</div>
    <div id="ifps">FPS: --</div>
  </div>
  <div id="tip">
    마우스 이동: 시점회전<br>
    좌클릭: 블록제거<br>
    우클릭: 블록설치<br>
    WASD: 이동<br>
    Space: 점프<br>
    ESC: 마우스 해제
  </div>
  <div id="hotbar"></div>
  <div id="lock-warn">화면을 클릭하면 다시 마우스가 고정됩니다.</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const BTYPES = [
  {name:'잔디', color:0x5d8a2e},
  {name:'흙',   color:0x8B6340},
  {name:'돌',   color:0x888888},
  {name:'나무', color:0x8B4513},
  {name:'잎',   color:0x2e7d32},
  {name:'모래', color:0xd4b483},
  {name:'벽돌', color:0xb34c3a},
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
    for(let y=0;y<=h;y++) setV(x,y,z, y===h?0:y>=h-2?1:2);
    if(Math.random()<0.04&&h<14){
      const th=3+Math.floor(Math.random()*3);
      for(let ty=1;ty<=th;ty++) setV(x,h+ty,z,3);
      for(let lx=-2;lx<=2;lx++) for(let lz=-2;lz<=2;lz++) for(let ly=th-1;ly<=th+2;ly++)
        if(Math.abs(lx)+Math.abs(lz)+Math.abs(ly-th)<4&&getV(x+lx,h+ly,z+lz)===undefined)
          setV(x+lx,h+ly,z+lz,4);
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
const sun=new THREE.DirectionalLight(0xffffff,0.7);
sun.position.set(20,40,15); scene.add(sun);

const mats={};
function mat(id){ if(!mats[id]) mats[id]=new THREE.MeshLambertMaterial({color:BTYPES[id].color}); return mats[id]; }
const baseGeo = new THREE.BoxGeometry(1,1,1);
const meshMap={};

function addMesh(x,y,z,id){
  const k=vk(x,y,z);
  if(meshMap[k]) scene.remove(meshMap[k]);
  const m=new THREE.Mesh(baseGeo,mat(id));
  m.position.set(x+0.5,y+0.5,z+0.5);
  m.userData={x,y,z};
  scene.add(m); meshMap[k]=m;
}
function delMesh(x,y,z){
  const k=vk(x,y,z);
  if(meshMap[k]){ scene.remove(meshMap[k]); delete meshMap[k]; }
}
function buildScene(){
  for(const k in voxels){
    const[x,y,z]=k.split('|').map(Number);
    addMesh(x,y,z,voxels[k]);
  }
}

// 플레이어 정밀 물리 엔진
const PL = {x:WS/2+0.5, y:13, z:WS/2+0.5, vy:0, onGround:false};
const EYE = 1.6;   
const PW  = 0.3;   
const PH  = 1.8;   
const SPEED = 5.5;
const GRAV  = -28;
const JV    = 9.0;

function isSolid(x,y,z){
  return getV(Math.floor(x), Math.floor(y), Math.floor(z)) !== undefined;
}

function collidesHoriz(px, py, pz){
  const ys = [0.1, 0.9, PH-0.1];
  for(const oy of ys){
    if( isSolid(px-PW, py+oy, pz-PW) || isSolid(px+PW, py+oy, pz-PW) ||
        isSolid(px-PW, py+oy, pz+PW) || isSolid(px+PW, py+oy, pz+PW) )
      return true;
  }
  return false;
}

function collidesDown(px, py, pz){
  return isSolid(px-PW,py,pz-PW)||isSolid(px+PW,py,pz-PW)||
         isSolid(px-PW,py,pz+PW)||isSolid(px+PW,py,pz+PW);
}

function collidesUp(px, py, pz){
  const top = py + PH;
  return isSolid(px-PW,top,pz-PW)||isSolid(px+PW,top,pz-PW)||
         isSolid(px-PW,top,pz+PW)||isSolid(px+PW,top,pz+PW);
}

function movePlayer(dx, dy, dz){
  PL.x += dx;
  if(collidesHoriz(PL.x, PL.y, PL.z)) PL.x -= dx;

  PL.z += dz;
  if(collidesHoriz(PL.x, PL.y, PL.z)) PL.z -= dz;

  PL.y += dy;
  if(dy < 0 && collidesDown(PL.x, PL.y, PL.z)){
    PL.y = Math.floor(PL.y) + 1;
    PL.vy = 0;
    PL.onGround = true;
  } else if(dy > 0 && collidesUp(PL.x, PL.y, PL.z)){
    PL.y = Math.floor(PL.y + PH) - PH - 0.005;
    PL.vy = 0;
  }
}

const keys={};
let yaw=0, pitch=0, selID=0, started=false;
let isLocked = false;

// 포인터락 이벤트 처리 파트
function requestLock() {
  if (started && !isLocked) {
    canvas.requestPointerLock();
  }
}

document.exitPointerLock = document.exitPointerLock || document.mozExitPointerLock;

document.addEventListener('pointerlockchange', lockChange, false);
document.addEventListener('mozpointerlockchange', lockChange, false);

function lockChange() {
  if (document.pointerLockElement === canvas || document.mozPointerLockElement === canvas) {
    isLocked = true;
    document.getElementById('lock-warn').style.display = 'none';
    canvas.focus();
  } else {
    isLocked = false;
    if(started) {
      document.getElementById('lock-warn').style.display = 'block';
    }
  }
}

// 화면 클릭 시 포인터락 재요청
canvas.addEventListener('click', requestLock);

// 마우스 움직임 감지 (포인터락 기반 변환)
window.addEventListener('mousemove', e => {
  if (!started || !isLocked) return;
  
  // 드래그 상태가 아니어도 마우스 감도를 입력받음
  const dx = e.movementX || e.mozMovementX || 0;
  const dy = e.movementY || e.mozMovementY || 0;
  
  yaw   -= dx * 0.0025; // 회전 감도 조절
  pitch -= dy * 0.0025;
  pitch = Math.max(-1.55, Math.min(1.55, pitch));
});

// 키보드 핸들러
window.addEventListener('keydown', e=>{
  keys[e.code] = true;
  const n = parseInt(e.key);
  if(n>=1&&n<=7){ selID=n-1; updateHB(); }
  if(e.code==='Space') e.preventDefault();
});
window.addEventListener('keyup', e=>{ keys[e.code]=false; });

// 마우스 클릭 (설치 / 해제) -> 포인터락 상태에서만 작동하도록 안전장치 추가
window.addEventListener('mousedown', e=>{
  if(!started || !isLocked) return;
  e.preventDefault();
  if(e.button === 0) doBreak(); // 좌클릭
  if(e.button === 2) doPlace(); // 우클릭
});

canvas.addEventListener('contextmenu', e => e.preventDefault());

window.addEventListener('wheel', e=>{
  if(!started) return;
  selID=(selID+(e.deltaY>0?1:-1)+BTYPES.length)%BTYPES.length;
  updateHB();
},{passive:true});

const rc = new THREE.Raycaster(); rc.far=7;
function raycast(){
  rc.setFromCamera({x:0,y:0}, camera);
  const hits = rc.intersectObjects(Object.values(meshMap), false);
  return hits.length ? hits[0] : null;
}
function doBreak(){
  const h=raycast(); if(!h) return;
  const{x,y,z}=h.object.userData;
  setV(x,y,z,null); delMesh(x,y,z);
}
function doPlace(){
  const h=raycast(); if(!h) return;
  const n=h.face.normal;
  const{x,y,z}=h.object.userData;
  const nx=x+Math.round(n.x), ny=y+Math.round(n.y), nz=z+Math.round(n.z);
  if( Math.abs(nx+0.5-PL.x)<PW+0.5 &&
      ny+1>PL.y && ny<PL.y+PH &&
      Math.abs(nz+0.5-PL.z)<PW+0.5 ) return;
  if(getV(nx,ny,nz)===undefined){ setV(nx,ny,nz,selID); addMesh(nx,ny,nz,selID); }
}

function buildHB(){
  const hb=document.getElementById('hotbar'); hb.innerHTML='';
  BTYPES.forEach((b,i)=>{
    const d=document.createElement('div');
    d.className='slot'+(i===selID?' active':'');
    const n=document.createElement('div'); n.className='slot-num'; n.textContent=i+1;
    const c=document.createElement('div'); c.className='slot-color';
    c.style.background='#'+b.color.toString(16).padStart(6,'0');
    const l=document.createElement('div'); l.className='slot-label'; l.textContent=b.name;
    d.append(n,c,l);
    d.onclick=()=>{ selID=i; updateHB(); };
    hb.appendChild(d);
  });
}
function updateHB(){
  document.querySelectorAll('.slot').forEach((s,i)=>s.classList.toggle('active',i===selID));
}

let last=0, fpsN=0, fpsT=0, fpsCur=0;
function loop(ts){
  requestAnimationFrame(loop);
  const dt = Math.min((ts-last)/1000, 0.05); last=ts;
  fpsN++; fpsT+=dt;
  if(fpsT>=1){ fpsCur=fpsN; fpsN=0; fpsT=0;
    document.getElementById('ifps').textContent='FPS:'+fpsCur; }

  if(!started){ renderer.render(scene,camera); return; }

  const sy=Math.sin(yaw), cy=Math.cos(yaw);
  let mx=0, mz=0;
  if(keys['KeyW']||keys['ArrowUp'])   { mx-=sy; mz-=cy; }
  if(keys['KeyS']||keys['ArrowDown']) { mx+=sy; mz+=cy; }
  if(keys['KeyD']||keys['ArrowRight']){ mx+=cy; mz-=sy; }
  if(keys['KeyA']||keys['ArrowLeft']) { mx-=cy; mz+=sy; }
  const ml=Math.sqrt(mx*mx+mz*mz);
  if(ml>0){ mx/=ml; mz/=ml; }

  if((keys['Space'])&&PL.onGround){
    PL.vy=JV; PL.onGround=false;
  }

  PL.vy += GRAV*dt;
  PL.onGround = false;

  movePlayer(mx*SPEED*dt, PL.vy*dt, mz*SPEED*dt);

  if(PL.y < -10){ PL.y=hAt(Math.floor(PL.x),Math.floor(PL.z))+3; PL.vy=0; }

  camera.position.set(PL.x, PL.y+EYE, PL.z);
  camera.quaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));

  document.getElementById('ipos').textContent=`위치: ${Math.floor(PL.x)}, ${Math.floor(PL.y)}, ${Math.floor(PL.z)}`;
  document.getElementById('iblk').textContent=`블록: ${BTYPES[selID].name}`;
  renderer.render(scene,camera);
}

window.addEventListener('resize',()=>{
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
});

document.getElementById('startBtn').addEventListener('click',()=>{
  document.getElementById('start').style.display='none';
  document.getElementById('hud').style.display='block';
  started=true;
  genWorld(); buildScene();
  PL.x=WS/2+0.5; PL.z=WS/2+0.5;
  PL.y=hAt(Math.floor(PL.x), Math.floor(PL.z))+2;
  camera.position.set(PL.x, PL.y+EYE, PL.z);
  buildHB();
  requestLock(); // 시작하자마자 마우스 고정 요청
  requestAnimationFrame(loop);
});
</script>
</body>
</html>
"""

st.title("⛏ Streamlit 마인크래프트 3D (포인터락)")
st.caption("포인터락 API가 도입되어 실제 FPS 게임처럼 부드럽게 화면이 회전합니다. (풀려면 ESC)")

components.html(minecraft_pointerlock_html, height=750, scrolling=False)
