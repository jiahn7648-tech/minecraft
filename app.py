import streamlit as st
import streamlit.components.v1 as components

# 스트림릿 페이지 설정 (전체 화면 최적화)
st.set_page_config(
    page_title="Minecraft 3D (3D Hand & Bug Fix) - Streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

minecraft_3d_hand_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Minecraft 3D - 3D Hand Fixed</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#000; overflow:hidden; font-family:monospace; user-select:none; }
canvas { display:block; outline:none; width:100vw; height:100vh; }
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
</style>
</head>
<body>
<canvas id="c" tabindex="0"></canvas>

<div id="start">
  <h1>⛏ MINECRAFT 3D</h1>
  <p style="color:#cef;font-size:15px;margin-bottom:14px">Pure 3D Hand & Action Bug Fixed</p>
  <p><b>[안내]</b> 시점을 돌리며 클릭해도 블록 제거/설치가 정상 작동합니다.</p>
  <p style="margin-top:10px;">🖱 <b>마우스 드래그</b>: 시점 회전</p>
  <p>W, A, S, D / 방향키: 이동 &nbsp;|&nbsp; Space: 점프</p>
  <p>좌클릭: 블록 제거 (3D 곡괭이 스윙) &nbsp;|&nbsp; 우클릭: 블록 설치</p>
  <p>1 ~ 7 / 마우스 휠: 도구 선택</p>
  <button id="startBtn">▶ 게임 시작</button>
</div>

<div id="hud">
  <div id="cross"></div>
  <div id="info">
    <div id="ipos">위치: 0, 0, 0</div>
    <div id="iblk">선택: 철 곡괭이</div>
    <div id="ifps">FPS: --</div>
  </div>
  <div id="tip">
    드래그: 시점회전<br>
    좌클릭: 블록제거 (3D 애니메이션)<br>
    우클릭: 블록설치<br>
    WASD: 이동 | Space: 점프
  </div>
  <div id="hotbar"></div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const BTYPES = [
  {name:'철 곡괭이', color:0xb0bec5, isTool:true},
  {name:'잔디',     color:0x5d8a2e, isTool:false},
  {name:'흙',       color:0x8B6340, isTool:false},
  {name:'돌',       color:0x888888, isTool:false},
  {name:'나무',     color:0x8B4513, isTool:false},
  {name:'잎',       color:0x2e7d32, isTool:false},
  {name:'모래',     color:0xd4b483, isTool:false},
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

// 🐏 동물 시스템
const animals = [];
const animalGroup = new THREE.Group();
scene.add(animalGroup);

function spawnAnimals() {
  const types = [{ name: 'sheep', bodyColor: 0xffffff, headColor: 0xf5f5f5 }, { name: 'cow', bodyColor: 0x5c4033, headColor: 0x3d2723 }];
  for(let i=0; i<8; i++) {
    const type = types[Math.floor(Math.random() * types.length)];
    const ax = 5 + Math.random() * (WS - 10);
    const az = 5 + Math.random() * (WS - 10);
    const ay = hAt(Math.floor(ax), Math.floor(az)) + 1;

    const mGroup = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.6, 1.2), new THREE.MeshLambertMaterial({color: type.bodyColor}));
    body.position.y = 0.4; mGroup.add(body);
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.5, 0.5), new THREE.MeshLambertMaterial({color: type.headColor}));
    head.position.set(0, 0.6, 0.6); mGroup.add(head);
    
    const legGeo = new THREE.BoxGeometry(0.18, 0.4, 0.18);
    const legMat = new THREE.MeshLambertMaterial({color: type.headColor});
    [[-0.3, 0, 0.4], [0.3, 0, 0.4], [-0.3, 0, -0.4], [0.3, 0, -0.4]].forEach(pos => {
      const leg = new THREE.Mesh(legGeo, legMat); leg.position.set(...pos); mGroup.add(leg);
    });
    mGroup.position.set(ax, ay, az); animalGroup.add(mGroup);
    animals.push({ mesh: mGroup, x: ax, y: ay, z: az, vx: 0, vz: 0, changeTimer: 0 });
  }
}

function updateAnimals(dt) {
  animals.forEach(a => {
    a.changeTimer -= dt;
    if(a.changeTimer <= 0) {
      if(Math.random() < 0.6) {
        const angle = Math.random() * Math.PI * 2;
        a.vx = Math.cos(angle) * 1.5; a.vz = Math.sin(angle) * 1.5;
        a.mesh.rotation.y = -angle + Math.PI/2;
      } else { a.vx = 0; a.vz = 0; }
      a.changeTimer = 2 + Math.random() * 4;
    }
    a.x += a.vx * dt; a.z += a.vz * dt;
    const curH = hAt(Math.floor(a.x), Math.floor(a.z)) + 1;
    a.y = a.y > curH ? a.y - 9.8 * dt : curH;
    a.mesh.position.set(a.x, a.y, a.z);
  });
}

// 🛡️ 플레이어 물리 파트
const PL = {x:WS/2+0.5, y:13, z:WS/2+0.5, vy:0, onGround:false};
const EYE = 1.6, PW = 0.3, PH = 1.8, SPEED = 5.5, GRAV = -28, JV = 9.0;

function isSolid(x,y,z){ return getV(Math.floor(x), Math.floor(y), Math.floor(z)) !== undefined; }
function collidesHoriz(px, py, pz){
  for(const oy of [0.1, 0.9, PH-0.1]) {
    if(isSolid(px-PW, py+oy, pz-PW) || isSolid(px+PW, py+oy, pz-PW) || isSolid(px-PW, py+oy, pz+PW) || isSolid(px+PW, py+oy, pz+PW)) return true;
  }
  return false;
}
function collidesDown(px, py, pz){ return isSolid(px-PW,py,pz-PW)||isSolid(px+PW,py,pz-PW)||isSolid(px-PW,py,pz+PW)||isSolid(px+PW,py,pz+PW); }
function collidesUp(px, py, pz){ const top = py + PH; return isSolid(px-PW,top,pz-PW)||isSolid(px+PW,top,pz-PW)||isSolid(px-PW,top,pz+PW)||isSolid(px+PW,top,pz+PW); }

function movePlayer(dx, dy, dz){
  PL.x += dx; if(collidesHoriz(PL.x, PL.y, PL.z)) PL.x -= dx;
  PL.z += dz; if(collidesHoriz(PL.x, PL.y, PL.z)) PL.z -= dz;
  PL.y += dy;
  if(dy < 0 && collidesDown(PL.x, PL.y, PL.z)){ PL.y = Math.floor(PL.y) + 1; PL.vy = 0; PL.onGround = true; }
  else if(dy > 0 && collidesUp(PL.x, PL.y, PL.z)){ PL.y = Math.floor(PL.y + PH) - PH - 0.005; PL.vy = 0; }
}

// 🖐️ [핵심 인게임 3D 손 및 아이템 구조화 시스템]
let handGroup;     // 카메라에 기속되어 따라다닐 3D 손 그룹
let current3DItem; // 현재 들고 있는 3D 메쉬 오브젝트 참조변수
let swingTime = 0;
let isSwinging = false;

function init3DHand() {
  handGroup = new THREE.Group();
  scene.add(handGroup); // 월드에 추가 후 루프에서 카메라 좌표계로 연속 추적 동기화
  rebuild3DHandItem();
}

function rebuild3DHandItem() {
  if (!handGroup) return;
  
  // 기존 잔여 메쉬 제거
  while(handGroup.children.length > 0){
    handGroup.remove(handGroup.children[0]);
  }

  // 1. 플레이어의 3D 오른팔 복셀 생성
  const armGeo = new THREE.BoxGeometry(0.25, 0.25, 0.7);
  const armMat = new THREE.MeshLambertMaterial({ color: 0xe0a96d });
  const armMesh = new THREE.Mesh(armGeo, armMat);
  // 카메라 우측 하단에 배치하기 위한 초기 오프셋
  armMesh.position.set(0.35, -0.35, -0.6);
  armMesh.rotation.set(-0.2, -0.2, 0);
  handGroup.add(armMesh);

  // 2. 들고 있는 아이템 메쉬 분기 설계
  const current = BTYPES[selID];
  const itemGroup = new THREE.Group();

  if (current.isTool) {
    // ⛏️ 3D 복셀 조합형 철 곡괭이 제작
    // 자루(막대기)
    const stickGeo = new THREE.BoxGeometry(0.05, 0.5, 0.05);
    const stickMat = new THREE.MeshLambertMaterial({ color: 0x8b5a2b });
    const stick = new THREE.Mesh(stickGeo, stickMat);
    stick.position.set(0, 0.2, 0);
    itemGroup.add(stick);

    // 머리 철조각 (날 부위)
    const headGeo = new THREE.BoxGeometry(0.4, 0.06, 0.06);
    const headMat = new THREE.MeshLambertMaterial({ color: 0xb0bec5 });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.set(0, 0.42, 0);
    itemGroup.add(head);
    
    itemGroup.rotation.set(0.3, 0, -0.4);
  } else {
    // 📦 3D 복셀 축소판 블록 오브젝트 제작
    const blockGeo = new THREE.BoxGeometry(0.2, 0.2, 0.2);
    const blockMat = new THREE.MeshLambertMaterial({ color: current.color });
    const blockMesh = new THREE.Mesh(blockGeo, blockMat);
    blockMesh.position.set(0, 0.15, 0);
    itemGroup.add(blockMesh);
  }

  // 아이템을 팔의 끝 지점(손 위치) 근처에 바인딩
  itemGroup.position.set(0.35, -0.25, -0.75);
  handGroup.add(itemGroup);
  current3DItem = itemGroup; // 애니메이션 변형 타겟 지정
}

// 3D 스윙 애니메이션 구동 제어 엔진
function update3DHandAnimation(dt) {
  if (!handGroup) return;

  // 1. 카메라의 물리적 위치와 회전값을 매 프레임 1:1 결합 (화면에 고정된 것처럼 보이게 함)
  handGroup.position.copy(camera.position);
  handGroup.quaternion.copy(camera.quaternion);

  // 2. 좌클릭 발동 시 3D 아이템 회전각 연산 구현
  if (isSwinging) {
    swingTime += dt * 5.0; // 애니메이션 스피드 배수 정밀화
    if (swingTime > Math.PI) {
      swingTime = 0;
      isSwinging = false;
      current3DItem.rotation.x = 0; // 원위치 롤백
    } else {
      // 사인 파형 곡선 수식을 연동하여 타격 후 돌아오는 궤적 형성
      const swingAngle = Math.sin(swingTime) * 1.2;
      current3DItem.rotation.x = swingAngle;
      current3DItem.rotation.z = -swingAngle * 0.4;
    }
  }
}

// 🕹️ 조작 제어 및 충돌 수집 메커니즘
const keys={};
let yaw=0, pitch=0, selID=0, started=false;
let dragging=false, lastMX=0, lastMY=0;

// [버그 수정의 핵심]: 드래그 이동 거리 측정 방식을 절대 좌표 기반에서 이벤트 변위량으로 완전 변경하여 조작 씹힘 차단
let totalDragDist = 0; 

window.addEventListener('keydown', e=>{
  keys[e.code] = true;
  const n = parseInt(e.key);
  if(n>=1&&n<=7){ selID=n-1; updateHB(); rebuild3DHandItem(); }
  if(e.code==='Space') e.preventDefault();
});
window.addEventListener('keyup', e=>{ keys[e.code]=false; });

function focusGame() { canvas.focus(); }
window.addEventListener('click', focusGame);

// 마우스 다운 시점 초기화
canvas.addEventListener('mousedown', e=>{
  if(!started) return;
  e.preventDefault();
  focusGame();
  dragging = true;
  totalDragDist = 0; // 마우스를 누를 때마다 누적 드래그 거리 초기화
  lastMX = e.clientX;
  lastMY = e.clientY;
});

// 마우스 무브 시 회전 가속 및 거리 누적
window.addEventListener('mousemove', e=>{
  if(!started || !dragging) return;
  const dx = e.clientX - lastMX;
  const dy = e.clientY - lastMY;
  
  totalDragDist += Math.abs(dx) + Math.abs(dy); // 움직인 총 거리를 기록

  yaw   -= dx * 0.004;
  pitch -= dy * 0.004;
  pitch = Math.max(-1.55, Math.min(1.55, pitch));
  
  lastMX = e.clientX;
  lastMY = e.clientY;
});

// [버그 전면 수정]: 마우스를 뗄 때(mouseup) 이동한 거리가 극소량이거나 제자리 클릭이면 '무조건 타격/설치 판정' 처리
window.addEventListener('mouseup', e=>{
  if(!started || !dragging) return;
  dragging = false;

  // 임계값(Threshold)을 8픽셀 미만으로 책정하여 미세한 흔들림 속에서도 클릭이 무조건 발동하도록 보정
  if (totalDragDist < 8) {
    if(e.button === 0) { // 좌클릭 (제거)
      isSwinging = true; swingTime = 0; // 3D 애니메이션 큐 발동
      doBreak();
    }
    else if(e.button === 2) { // 우클릭 (설치)
      isSwinging = true; swingTime = 0;
      doPlace();
    }
  }
});

canvas.addEventListener('contextmenu', e=>e.preventDefault());
window.addEventListener('wheel', e=>{
  if(!started) return;
  selID=(selID+(e.deltaY>0?1:-1)+BTYPES.length)%BTYPES.length;
  updateHB();
  rebuild3DHandItem();
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
  if(BTYPES[selID].isTool) return; // 곡괭이는 설치에서 배제
  const h=raycast(); if(!h) return;
  const n=h.face.normal;
  const{x,y,z}=h.object.userData;
  const nx=x+Math.round(n.x), ny=y+Math.round(n.y), nz=z+Math.round(n.z);
  if( Math.abs(nx+0.5-PL.x)<PW+0.5 && ny+1>PL.y && ny<PL.y+PH && Math.abs(nz+0.5-PL.z)<PW+0.5 ) return;
  if(getV(nx,ny,nz)===undefined){ setV(nx,ny,nz,selID); addMesh(nx,ny,nz,selID); }
}

function buildHB(){
  const hb=document.getElementById('hotbar'); hb.innerHTML='';
  BTYPES.forEach((b,i)=>{
    const d=document.createElement('div'); d.className='slot'+(i===selID?' active':'');
    const n=document.createElement('div'); n.className='slot-num'; n.textContent=i+1;
    const c=document.createElement('div'); c.className='slot-color';
    c.style.background='#'+b.color.toString(16).padStart(6,'0');
    if(b.isTool) c.style.background = "linear-gradient(135deg, #b0bec5 40%, #8b5a2b 0)";
    const l=document.createElement('div'); l.className='slot-label'; l.textContent=b.name;
    d.append(n,c,l);
    d.onclick=()=>{ selID=i; updateHB(); rebuild3DHandItem(); focusGame(); };
    hb.appendChild(d);
  });
}
function updateHB(){ document.querySelectorAll('.slot').forEach((s,i)=>s.classList.toggle('active',i===selID)); }

let last=0, fpsN=0, fpsT=0, fpsCur=0;
function loop(ts){
  requestAnimationFrame(loop);
  const dt = Math.min((ts-last)/1000, 0.05); last=ts;
  fpsN++; fpsT+=dt;
  if(fpsT>=1){ fpsCur=fpsN; fpsN=0; fpsT=0; document.getElementById('ifps').textContent='FPS:'+fpsCur; }

  if(!started){ renderer.render(scene,camera); return; }

  updateAnimals(dt);
  
  // 3D 손 위치 동기화 및 휘두르기 애니메이션 루틴 업데이트
  update3DHandAnimation(dt);

  const sy=Math.sin(yaw), cy=Math.cos(yaw);
  let mx=0, mz=0;
  if(keys['KeyW']||keys['ArrowUp'])   { mx-=sy; mz-=cy; }
  if(keys['KeyS']||keys['ArrowDown']) { mx+=sy; mz+=cy; }
  if(keys['KeyD']||keys['ArrowRight']){ mx+=cy; mz-=sy; }
  if(keys['KeyA']||keys['ArrowLeft']) { mx-=cy; mz+=sy; }
  const ml=Math.sqrt(mx*mx+mz*mz); if(ml>0){ mx/=ml; mz/=ml; }

  if((keys['Space'])&&PL.onGround){ PL.vy=JV; PL.onGround=false; }
  PL.vy += GRAV*dt; PL.onGround = false;
  movePlayer(mx*SPEED*dt, PL.vy*dt, mz*SPEED*dt);

  if(PL.y < -10){ PL.y=hAt(Math.floor(PL.x),Math.floor(PL.z))+3; PL.vy=0; }

  camera.position.set(PL.x, PL.y+EYE, PL.z);
  camera.quaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));

  document.getElementById('ipos').textContent=`위치: ${Math.floor(PL.x)}, ${Math.floor(PL.y)}, ${Math.floor(PL.z)}`;
  document.getElementById('iblk').textContent=`선택: ${BTYPES[selID].name}`;
  renderer.render(scene,camera);
}

window.addEventListener('resize',()=>{
  camera.aspect=window.innerWidth/window.innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
});

document.getElementById('startBtn').addEventListener('click',()=>{
  document.getElementById('start').style.display='none';
  document.getElementById('hud').style.display='block';
  started=true;
  genWorld(); buildScene(); spawnAnimals();
  PL.x=WS/2+0.5; PL.z=WS/2+0.5; PL.y=hAt(Math.floor(PL.x), Math.floor(PL.z))+2;
  camera.position.set(PL.x, PL.y+EYE, PL.z);
  buildHB();
  
  // 게임이 시작될 때 카메라 앞에 3D 오른팔 엔진 레이어 안착시킴
  init3DHand();
  
  focusGame();
  requestAnimationFrame(loop);
});
</script>
</body>
</html>
"""

st.title("⛏ Minecraft 3D (완전체 3D 복셀 손 & 버그 전면 수정본)")
st.caption("2D 이미지/CSS 오버레이 방식을 폐기하고, 마우스 변위 연산 버그를 잡아 시점 회전 중에도 완벽하게 블록이 상호작용합니다.")

# 스트림릿 내장 아이프레임 렌더러 파트 호출
components.html(minecraft_3d_hand_html, height=750, scrolling=False)
