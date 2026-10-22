// Observation bookkeeping only: no image inspection, aesthetic scoring or browser.
const sameBasis=(a,b)=>Boolean(a?.videoSHA256&&a?.coverSHA256&&a.videoSHA256===b?.videoSHA256&&a.coverSHA256===b?.coverSHA256);
const empty=basis=>({status:'not-checked',basis,coverage:[],issues:[],constraints:[],cover:{status:'not-checked',notes:''},history:[]});
const snapshot=review=>{const {history,...record}=review;return structuredClone(record);};

export function reviewStatus(review,duration){
 if(!Array.isArray(review.coverage)||!Array.isArray(review.issues))throw new Error('visualReview 需要 coverage 和 issues 数组。');
 if(typeof review.constraints!=='string'&&(!Array.isArray(review.constraints)||review.constraints.some(x=>typeof x!=='string')))throw new Error('visualReview.constraints 须为字符串或字符串数组。');
 if(!review.cover||!['not-checked','reviewed'].includes(review.cover.status)||typeof review.cover.notes!=='string')throw new Error('visualReview.cover 需要 status(not-checked/reviewed) 和 notes 字符串。');
 const time=value=>Number.isFinite(value)&&value>=0&&value<=duration;
 for(const item of review.coverage){
  if(!item||!['continuous','keyframe','local'].includes(item.kind)||!time(item.start)||!time(item.end)||item.end<item.start||!Number.isFinite(item.playbackRate)||item.playbackRate<=0)throw new Error('visualReview.coverage 的时间范围、kind 或 playbackRate 无效。');
 }
 const ids=new Set();
 for(const issue of review.issues){
  if(!issue||typeof issue.id!=='string'||!issue.id.trim()||ids.has(issue.id)||!['video','cover'].includes(issue.area)||typeof issue.description!=='string'||!issue.description.trim()||!['open','fixed-pending-review','resolved'].includes(issue.status))throw new Error('每个问题需要唯一 id、area(video/cover)、description 和有效 status。');
  // Carried issues retain the old edition's timecodes, which may exceed a shorter cut.
  const issueTime=value=>Number.isFinite(value)&&value>=0&&(issue.needsRecheck===true||value<=duration);
  if((issue.start!==undefined&&!issueTime(issue.start))||(issue.end!==undefined&&(!issueTime(issue.end)||issue.start===undefined||issue.end<issue.start)))throw new Error('问题的时间范围无效。');
  ids.add(issue.id);
 }
 if(review.issues.some(issue=>issue.status!=='resolved'||issue.needsRecheck===true))return 'issues-open';
 let end=0;
 for(const item of review.coverage.filter(x=>x.kind==='continuous'&&x.playbackRate===1).sort((a,b)=>a.start-b.start)){
  if(item.start>end+0.001)break;
  end=Math.max(end,item.end);
 }
 const constraintsChecked=typeof review.constraints==='string'?Boolean(review.constraints.trim()):review.constraints.some(item=>item.trim());
 if(end>=duration-0.001&&review.cover.status==='reviewed'&&constraintsChecked)return 'reviewed';
 return review.coverage.length||review.cover.status==='reviewed'?'partial':'not-checked';
}

export function preserveReview(previous,basis,duration){
 if(!previous)return empty(basis);
 // Recover observations after an interrupted/failed run could not hash the files.
 if(!previous.basis?.videoSHA256&&!previous.basis?.coverSHA256&&sameBasis(previous.history?.at(-1)?.basis,basis))previous=previous.history.at(-1);
 if(sameBasis(previous.basis,basis)){
  const result=structuredClone(previous);
  result.history=Array.isArray(result.history)?result.history.slice(-1):[];
  result.status=reviewStatus(result,duration);
  if(result.status==='not-checked'&&previous.status==='needs-review')result.status='needs-review';
  else delete result.reason;
  return result;
 }
 const hasObservations=previous.coverage?.length||previous.cover?.status==='reviewed'||previous.issues?.some(issue=>!issue.needsRecheck);
 const old=hasObservations?snapshot(previous):(previous.history?.at(-1)||snapshot(previous));
 return {...empty(basis),status:'needs-review',reason:'成品内容已改变或旧记录没有内容哈希；旧观察不能代表当前成品。',
  issues:(previous.issues||[]).map(issue=>({...issue,needsRecheck:true})),history:[old]};
}
