/** Deterministic motion primitives, not a visual template or a physics solver.
 * Positions use the caller's units; velocities are units/second; angles are radians.
 * Import into the project's source and bundle with its existing IIFE build pipeline.
 */
const finite = (x, name) => { if (!Number.isFinite(x)) throw new Error(`${name} must be finite`); return x; };
const positive = (x, name) => { finite(x, name); if (x <= 0) throw new Error(`${name} must be positive`); return x; };
export const clamp01 = x => Math.max(0, Math.min(1, finite(x, 'progress')));
export function smootherstep(x) { const u=clamp01(x); return u*u*u*(u*(u*6-15)+10); }
export function lerp(a,b,u) { return a+(b-a)*u; }

/** Hermite segment with endpoint velocities. Linear extension preserves C1 at ends.
 * Use adjacent segments' actual endpoint states, not zero-velocity resets per shot.
 */
export function hermiteAt(t,start,duration,p0,p1,v0=0,v1=0) {
  for (const [name,x] of Object.entries({t,start,p0,p1,v0,v1})) finite(x,name);
  positive(duration,'duration');
  const u=(t-start)/duration;
  if(u<0) return {value:p0+v0*(t-start),velocity:v0};
  if(u>1) return {value:p1+v1*(t-start-duration),velocity:v1};
  const u2=u*u,u3=u2*u;
  return {
    value:(2*u3-3*u2+1)*p0+(u3-2*u2+u)*duration*v0+(-2*u3+3*u2)*p1+(u3-u2)*duration*v1,
    velocity:((6*u2-6*u)*p0+(-6*u2+6*u)*p1)/duration+(3*u2-4*u+1)*v0+(3*u2-2*u)*v1
  };
}

export function vectorHermiteAt(t,start,duration,from,to,v0=from.map(()=>0),v1=to.map(()=>0)) {
  if(!Array.isArray(from)||!Array.isArray(to)||!from.length||[to,v0,v1].some(x=>!Array.isArray(x)||x.length!==from.length)) throw new Error('Vector dimensions must match');
  const samples=from.map((x,i)=>hermiteAt(t,start,duration,x,to[i],v0[i],v1[i]));
  return {value:samples.map(x=>x.value),velocity:samples.map(x=>x.velocity)};
}

export function unwrapAngle(from,to) {
  finite(from,'from');finite(to,'to');
  const tau=2*Math.PI;return from+((to-from+Math.PI)%tau+tau)%tau-Math.PI;
}

/** Shared 2D anchor, suitable for abstract objects/text and camera rigs.
 * Scale interpolates in log-space; it must NOT rescale a real object's world size.
 * Log-scale velocity is d(log(scale))/dt. Shortest rotation can be disabled.
 */
export function handoff2D(t,{start,duration,from,to,fromVelocity={},toVelocity={},shortestRotation=true}) {
  const sample=(key,a,b)=>hermiteAt(t,start,duration,a,b,fromVelocity[key]??0,toVelocity[key]??0);
  const x=sample('x',from.x,to.x), y=sample('y',from.y,to.y);
  const a=from.rotation??0,b=to.rotation??0;
  const angle=sample('rotation',a,shortestRotation?unwrapAngle(a,b):b);
  const zoom=sample('logScale',Math.log(positive(from.scale??1,'from.scale')),Math.log(positive(to.scale??1,'to.scale')));
  const scale=Math.exp(zoom.value);if(!Number.isFinite(scale)||scale<=0)throw new Error('Scale overflow; reduce zoom range/tangents');
  return {x:x.value,y:y.value,rotation:angle.value,scale,velocity:{x:x.velocity,y:y.velocity,rotation:angle.velocity,logScale:zoom.velocity}};
}

/** The transition interval owns both scenes. Shared objects are drawn only once. */
export function bridgeState(t,start,duration) {
  finite(t,'t');finite(start,'start');positive(duration,'duration');
  const progress=clamp01((t-start)/duration);
  return {progress,eased:smootherstep(progress),outgoingVisible:t<start+duration,incomingVisible:t>=start,inTransition:t>=start&&t<start+duration};
}

export function coveringCircleRadius(width,height,cx,cy) {
  positive(width,'width');positive(height,'height');finite(cx,'cx');finite(cy,'cy');
  return Math.hypot(Math.max(Math.abs(cx),Math.abs(width-cx)),Math.max(Math.abs(cy),Math.abs(height-cy)));
}

/** Stagger only groups that have a semantic order; do not bounce every character. */
export function staggerProgress(t,index,{start=0,interval=0.035,travel=0.3}={}) {
  if(!Number.isInteger(index)||index<0)throw new Error('index must be a nonnegative integer');
  finite(t,'t');finite(start,'start');finite(interval,'interval');positive(travel,'travel');
  if(interval<0)throw new Error('interval must be nonnegative');
  return smootherstep((t-start-index*interval)/travel);
}
