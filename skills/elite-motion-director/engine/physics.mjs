/* Self-consistent two-body illustration helpers. All lengths/time/mu must use matching units. */
const TAU=Math.PI*2;
export const add=(a,b)=>a.map((v,i)=>v+b[i]);
export const sub=(a,b)=>a.map((v,i)=>v-b[i]);
export const mul=(a,k)=>a.map(v=>v*k);
export const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export const norm=a=>Math.sqrt(dot(a,a));
export const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
export function unit(a){const n=norm(a);if(n<1e-12)throw new Error('Cannot normalize zero vector');return mul(a,1/n);}
const rz=(p,a)=>[Math.cos(a)*p[0]-Math.sin(a)*p[1],Math.sin(a)*p[0]+Math.cos(a)*p[1],p[2]];
const rx=(p,a)=>[p[0],Math.cos(a)*p[1]-Math.sin(a)*p[2],Math.sin(a)*p[1]+Math.cos(a)*p[2]];
export function orbitAt(o,t){
  const {a,e=0,mu, inclination=0,ascendingNode=0,argPeriapsis=0,meanAnomaly0=0,center=[0,0,0],bodyRadius=0}=o;
  if(!Number.isFinite(a)||!Number.isFinite(mu)||a<=0||mu<=0||e<0||e>=1||!Number.isFinite(e)||!Number.isFinite(t))throw new Error('Requires finite a, mu, t; a,mu>0; 0<=e<1');
  if(a*(1-e)<=bodyRadius)throw new Error('Periapsis intersects central body');
  const n=Math.sqrt(mu/(a*a*a)),M=((meanAnomaly0+n*t+Math.PI)%TAU+TAU)%TAU-Math.PI;
  let E=e<0.8?M:(M<0?-Math.PI:Math.PI),converged=false;
  for(let k=0;k<40;k++){const d=(E-e*Math.sin(E)-M)/(1-e*Math.cos(E));E-=d;if(Math.abs(d)<1e-12){converged=true;break;}}
  if(!converged)throw new Error('Kepler solve did not converge');
  const q=Math.sqrt(1-e*e),dEdt=n/(1-e*Math.cos(E));
  const rotate=p=>rz(rx(rz(p,argPeriapsis),inclination),ascendingNode);
  const local=[a*(Math.cos(E)-e),a*q*Math.sin(E),0];
  const velocity=rotate([-a*Math.sin(E)*dEdt,a*q*Math.cos(E)*dEdt,0]);
  return {position:add(center,rotate(local)),velocity,radius:norm(local),period:TAU/n};
}
export function ballisticAt({position,velocity,gravity=[0,-9.81,0]},t){return {position:add(add(position,mul(velocity,t)),mul(gravity,t*t/2)),velocity:add(velocity,mul(gravity,t))};}
export function project(point,{position,target,up=[0,1,0],fovY=Math.PI/3,width,height,near=0.01,far=1e9}){
  if(!(width>0&&height>0&&fovY>0&&fovY<Math.PI&&near>0&&far>near))throw new Error('Invalid perspective camera');
  const forward=unit(sub(target,position)),right=unit(cross(forward,up)),vertical=cross(right,forward),d=sub(point,position),z=dot(d,forward);
  if(z<near||z>far)return null;
  const focal=height/(2*Math.tan(fovY/2));return {x:width/2+dot(d,right)*focal/z,y:height/2-dot(d,vertical)*focal/z,depth:z,pixelsPerUnit:focal/z};
}
export function sphereOccludes(camera,point,center,radius){
  if(!(radius>0))throw new Error('Invalid radius');
  const delta=sub(point,camera),distance=norm(delta);if(distance<1e-12)return false;
  const direction=mul(delta,1/distance),oc=sub(camera,center),b=dot(oc,direction),c=dot(oc,oc)-radius*radius,disc=b*b-c;
  if(disc<0)return false;
  const hit=-b-Math.sqrt(disc),exit=-b+Math.sqrt(disc);
  return exit>1e-8 && Math.max(hit,0)<distance-1e-8;
}
