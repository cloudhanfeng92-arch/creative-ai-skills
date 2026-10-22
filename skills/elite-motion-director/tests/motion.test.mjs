import test from 'node:test';
import assert from 'node:assert/strict';
import {smootherstep,hermiteAt,vectorHermiteAt,handoff2D,bridgeState,coveringCircleRadius,staggerProgress} from '../engine/motion.mjs';
const near=(a,b,tol=1e-6)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
test('quintic easing has stationary start/end, monotone progress',()=>{
 assert.equal(smootherstep(-1),0);assert.equal(smootherstep(2),1);
 const e=1e-5;near(smootherstep(e)/e,0);near((1-smootherstep(1-e))/e,0);
 let last=0;for(let i=0;i<=100;i++){const y=smootherstep(i/100);assert.ok(y>=last);last=y;}
});
test('Hermite endpoints preserve specified values and velocities',()=>{
 const a=hermiteAt(1,1,2,4,10,3,-1),b=hermiteAt(3,1,2,4,10,3,-1);
 assert.deepEqual(a,{value:4,velocity:3});assert.deepEqual(b,{value:10,velocity:-1});
});
test('adjacent segments hand off position AND velocity',()=>{
 const left=t=>hermiteAt(t,0,1,0,12,0,8),right=t=>hermiteAt(t,1,1.5,12,20,8,0),eps=1e-5;
 near(left(1).value,right(1).value);near(left(1).velocity,right(1).velocity);
 near((left(1).value-left(1-eps).value)/eps,(right(1+eps).value-right(1).value)/eps,1e-3);
});
test('linear extensions prevent hidden endpoint velocity reset',()=>{
 assert.deepEqual(hermiteAt(-1,0,1,2,8,3,4),{value:-1,velocity:3});
 assert.deepEqual(hermiteAt(2,0,1,2,8,3,4),{value:12,velocity:4});
});
test('camera vectors use matching dimensions and endpoint tangents',()=>{
 const s=vectorHermiteAt(1,0,1,[0,1,3],[5,6,7],[0,0,0],[1,2,3]);
 assert.deepEqual(s,{value:[5,6,7],velocity:[1,2,3]});
 assert.throws(()=>vectorHermiteAt(0,0,1,[0,1],[3]));
});
test('2D handoff uses positive log zoom and short rotation',()=>{
 const rig={start:0,duration:2,from:{x:0,y:5,scale:1,rotation:Math.PI*179/180},to:{x:10,y:20,scale:4,rotation:-Math.PI*179/180}};
 const s=handoff2D(1,rig);near(s.scale,2);near(s.rotation,Math.PI);near(s.x,5);
});
test('overlap never leaves an empty interval or duplicates ownership',()=>{
 for(let i=0;i<100;i++){const s=bridgeState(i*.02,.5,.7);assert.ok(s.outgoingVisible||s.incomingVisible);}
 assert.equal(bridgeState(.7,.5,.7).inTransition,true);
 assert.equal(bridgeState(1.2,.5,.7).outgoingVisible,false);
});
test('mask radius includes all corners even with offscreen anchor',()=>{
 const r=coveringCircleRadius(1920,1080,-40,20);
 for(const x of [0,1920])for(const y of [0,1080])assert.ok(Math.hypot(x+40,y-20)<=r+1e-9);
});
test('group staggering is deterministic and respects ordering',()=>{
 assert.ok(staggerProgress(.2,0)>staggerProgress(.2,3));
 assert.equal(staggerProgress(.21,2),staggerProgress(.21,2));
});
test('invalid time and scale fail instead of invisible NaN frames',()=>{
 assert.throws(()=>bridgeState(0,0,0));assert.throws(()=>smootherstep(NaN));
 assert.throws(()=>handoff2D(0,{start:0,duration:1,from:{x:0,y:0,scale:0},to:{x:0,y:0}}));
});
