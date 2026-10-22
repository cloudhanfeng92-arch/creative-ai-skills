import test from 'node:test';
import assert from 'node:assert/strict';
import {orbitAt,ballisticAt,project,sphereOccludes,norm,dot,cross} from '../engine/physics.mjs';
const close=(a,b,t=1e-8)=>assert.ok(Math.abs(a-b)<t,`${a} vs ${b}`);
test('circular orbit: shared radius, period and repeatable seek',()=>{
 const o={a:2,mu:1,bodyRadius:1},first=orbitAt(o,0);
 for(const t of [0,0.1,3,17,800]){close(orbitAt(o,t).radius,2);assert.deepEqual(orbitAt(o,t),orbitAt(o,t));}
 const end=orbitAt(o,first.period);first.position.forEach((v,i)=>close(v,end.position[i]));
});
test('ellipse: focus, energy, angular momentum and non-uniform speed',()=>{
 const o={a:4,e:0.4,mu:3,bodyRadius:1,inclination:0.6,ascendingNode:0.2,argPeriapsis:0.4};
 let reference;
 for(let t=0;t<30;t+=0.5){const s=orbitAt(o,t),energy=dot(s.velocity,s.velocity)/2-o.mu/s.radius;close(energy,-o.mu/(2*o.a));const h=norm(cross(s.position,s.velocity));if(reference===undefined)reference=h;close(h,reference);}
 close(orbitAt(o,0).radius,2.4);close(orbitAt(o,orbitAt(o,0).period/2).radius,5.6);
 assert.ok(norm(orbitAt(o,0).velocity)>norm(orbitAt(o,orbitAt(o,0).period/2).velocity));
});
test('bad orbit fails rather than intersecting Earth',()=>{assert.throws(()=>orbitAt({a:1.2,e:0.5,mu:1,bodyRadius:1},0));});
test('front visible, back occluded, lateral visible',()=>{
 const cam=[0,0,5];assert.equal(sphereOccludes(cam,[0,0,2],[0,0,0],1),false);assert.equal(sphereOccludes(cam,[0,0,-2],[0,0,0],1),true);assert.equal(sphereOccludes(cam,[2,0,0],[0,0,0],1),false);
});
test('common perspective gives near/far scale and rejects behind camera',()=>{
 const c={position:[0,0,5],target:[0,0,0],width:1920,height:1080};const near=project([0,0,3],c),far=project([0,0,1],c);close(near.pixelsPerUnit/far.pixelsPerUnit,2);assert.equal(project([0,0,6],c),null);
});
test('ballistic position and speed follow one acceleration',()=>{const s=ballisticAt({position:[0,1,0],velocity:[2,3,0],gravity:[0,-10,0]},1);assert.deepEqual(s.position,[2,-1,0]);assert.deepEqual(s.velocity,[2,-7,0]);});
