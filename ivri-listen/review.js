const VERSION = 'ivri-stress-2026-11-17-v1';
const KEY = `ivri-listening:${VERSION}`;
const set = new URLSearchParams(location.search).get('set') === '2' ? '2' : '1';
const localPreview = location.hostname === '192.168.0.58';
const endpoint = localPreview ? 'http://192.168.0.58:4312/api/reviews' : 'https://ivri-listening-review.samh.chatgpt.site/api/reviews';
const app = document.querySelector('#app');
const progress = document.querySelector('#progress');
function uuid() { const b=crypto.getRandomValues(new Uint8Array(16)); b[6]=(b[6]&15)|64;b[8]=(b[8]&63)|128;const h=[...b].map(n=>n.toString(16).padStart(2,'0')).join('');return `${h.slice(0,8)}-${h.slice(8,12)}-${h.slice(12,16)}-${h.slice(16,20)}-${h.slice(20)}`; }
let storageAvailable = true;
let state;
try { state = JSON.parse(localStorage.getItem(KEY)); } catch { storageAvailable = false; }
if (!state || state.version !== VERSION || !state.sessionId || !state.pairs) {
  state = { version:VERSION, sessionId:uuid(), profile:{alias:'',background:'unspecified'}, pairs:{}, started:false };
}
function persist() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { storageAvailable = false; } }
persist();
let pairs = [];
let activeAudio = [];
let busy = false;
const escape = text => String(text).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const playIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 4 12 8-12 8Z"/></svg>';
const pauseIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4v16M16 4v16"/></svg>';
function stopAudio() { activeAudio.forEach(a => { a.pause(); a.removeAttribute('src'); a.load(); }); activeAudio=[]; }
function focusPage() { app.querySelector('h1,h2')?.focus({preventScroll:true}); window.scrollTo({top:0,behavior:'instant'}); }
function intro() {
  stopAudio(); progress.textContent='3 comparisons';
  app.innerHTML=`<section class="intro"><h1 tabindex="-1">A little help with Hebrew?</h1><p>Listen to two readings. Tell us which gets the word right and which sounds natural.</p><p class="muted">Three comparisons, about 3 minutes. “Not sure” is always fine.</p></section><form id="begin"><div class="profile"><label class="field"><span>Your Hebrew</span><select name="background"><option value="unspecified">Choose, or leave blank</option><option value="native">Native speaker</option><option value="fluent">Fluent speaker / reader</option><option value="teacher">Hebrew teacher</option><option value="learning">Still learning</option></select></label><label class="field"><span>Name or nickname (optional)</span><input name="alias" maxlength="80" autocomplete="off" value="${escape(state.profile.alias)}"></label></div><p class="toast">Modern Israeli reading, without chanting. Answers go privately to Sam and the Ivri team.</p><button class="primary">Start listening</button></form>`;
  app.querySelector('select').value=state.profile.background;
  app.querySelector('form').onsubmit=e=>{e.preventDefault();state.profile={alias:e.target.alias.value.trim(),background:e.target.background.value};state.started=true;persist();showNext();};
  focusPage();
}
function entry(pair) {
  if(!state.pairs[pair.id]) {
    const flip=crypto.getRandomValues(new Uint8Array(1))[0]%2;
    state.pairs[pair.id]={order:flip?['changed','original']:['original','changed'],heard:{a:false,b:false},stressCorrect:'',natural:'',note:'',status:'draft'};persist();
  }
  return state.pairs[pair.id];
}
function choices(name,legend,value) {
  return `<fieldset><legend>${legend}</legend><div class="choices">${[['a','A'],['b','B'],['both','Both'],['neither','Neither'],['unsure','Not sure']].map(([v,label])=>`<label class="choice"><input type="radio" name="${name}" value="${v}" ${v===value?'checked':''}><span>${label}</span></label>`).join('')}</div></fieldset>`;
}
function showNext() { busy=false;const next=pairs.find(p=>!['saved','savedElsewhere','skipped'].includes(state.pairs[p.id]?.status));if(next)review(next);else done(); }
function review(pair) {
  stopAudio(); const answer=entry(pair); const index=pairs.indexOf(pair);
  progress.textContent=`${index+1} of 3`;
  const words=pair.hebrew.split(' ');
  const target=words[pair.targetIndex];
  const targetCue=`<span class="sr-only"> Target: <span lang="he" dir="rtl">${escape(target)}</span>${words.filter(w=>w===target).length>1?' (first occurrence)':''}.</span>`;
  const hebrew=words.map((word,i)=>i===pair.targetIndex?`<mark>${escape(word)}</mark>`:escape(word)).join(' ');
  app.innerHTML=`<section><h1 tabindex="-1">Listen to A and B</h1><div class="reference"><span>${escape(pair.reference)}</span></div><p class="hebrew" lang="he" dir="rtl">${hebrew}</p><div class="players">${['a','b'].map(letter=>`<button class="player" type="button" data-letter="${letter}" aria-label="Play clip ${letter.toUpperCase()}"><span class="play-icon">${playIcon}</span><span><span class="clip-label">Play ${letter.toUpperCase()}</span><small class="heard">${answer.heard[letter]?'Listened':''}</small></span><span class="track"></span></button>`).join('')}</div><p class="listen-hint">Focus on the highlighted word. Replay anytime.</p><form id="review">${choices('stressCorrect','Which gets the word’s stress right?'+targetCue,answer.stressCorrect)}${choices('natural','Which reading sounds natural?',answer.natural)}<details><summary>Add a note (optional)</summary><label class="field"><span>Which word or clip sounded wrong? Another reading tradition?</span><textarea name="note" maxlength="1000" dir="auto">${escape(answer.note)}</textarea></label></details><p class="status" role="status" aria-live="polite"></p><div class="actions"><button class="primary" type="submit">${index===2?'Send & finish':'Send & next'}</button><button class="text-button" type="button" id="skip">Skip this comparison</button></div></form></section>`;
  const form=app.querySelector('form'),status=app.querySelector('.status');
  for(const [i,letter] of ['a','b'].entries()) {
    const audio=new Audio(pair.clips[answer.order[i]].src);audio.preload='metadata';activeAudio.push(audio);
    const button=app.querySelector(`[data-letter=${letter}]`),icon=button.querySelector('.play-icon');
    const sync=()=>{const playing=!audio.paused;button.dataset.playing=String(playing);button.querySelector(".clip-label").textContent=`${playing?"Pause":"Play"} ${letter.toUpperCase()}`;icon.innerHTML=playing?pauseIcon:playIcon;button.setAttribute('aria-label',`${playing?'Pause':'Play'} clip ${letter.toUpperCase()}`);};
    audio.addEventListener('play',sync);audio.addEventListener('pause',sync);
    audio.addEventListener('timeupdate',()=>button.querySelector('.track').style.width=`${Number.isFinite(audio.duration)?audio.currentTime/audio.duration*100:0}%`);
    audio.addEventListener('ended',()=>{answer.heard[letter]=true;persist();button.querySelector('.heard').textContent='Listened';sync();});
    audio.addEventListener('error',()=>{status.textContent=`Clip ${letter.toUpperCase()} didn’t load. Tap Play to retry, or skip this comparison.`;});
    button.onclick=async()=>{if(!audio.paused){audio.pause();return;}activeAudio.filter(x=>x!==audio).forEach(x=>x.pause());if(audio.error)audio.load();try{await audio.play();status.textContent='';}catch{status.textContent='Audio could not start. Tap Play to try again.';}};
  }
  form.oninput=()=>{answer.stressCorrect=form.elements.stressCorrect.value;answer.natural=form.elements.natural.value;answer.note=form.elements.note.value;persist();};
  app.querySelector('#skip').onclick=()=>{if(busy)return;answer.status='skipped';persist();showNext();};
  function showConflict() {
    answer.status='conflict';persist();
    form.querySelectorAll('input,textarea').forEach(x=>x.disabled=true);form.querySelector('#skip').disabled=true;
    status.textContent='This comparison was already submitted from this browser. Your first response was kept.';
    const button=form.querySelector('.primary');button.disabled=false;button.type='button';button.textContent='Continue';button.onclick=()=>{answer.status='savedElsewhere';persist();showNext();};
  }
  form.onsubmit=async e=>{
    e.preventDefault();if(busy)return;
    if(!answer.heard.a||!answer.heard.b){status.textContent='Listen to both clips to the end, or skip this comparison.';return;}
    if(!answer.stressCorrect||!answer.natural){status.textContent='Choose an answer for both questions. “Not sure” is fine.';return;}
    const body={schemaVersion:1,reviewVersion:VERSION,sessionId:state.sessionId,set,pairId:pair.id,order:answer.order,stressCorrect:answer.stressCorrect,natural:answer.natural,note:answer.note,...state.profile,heard:answer.heard};
    // Keep the exact first submitted bytes on retry, including a lost response.
    answer.pendingBody??=body;persist();busy=true;activeAudio.forEach(a=>a.pause());
    const controls=[...form.querySelectorAll('button,input,textarea')];controls.forEach(x=>x.disabled=true);const submit=form.querySelector('.primary');submit.textContent='Sending…';status.textContent='';
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),12000);
    try {
      const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(answer.pendingBody),signal:controller.signal,credentials:'omit'});
      if(response.status===409){busy=false;showConflict();return;}
      if(!response.ok){const failure=new Error(`HTTP ${response.status}`);failure.definite=response.status>=400&&response.status<500;throw failure;}
      const result=await response.json();if(result.saved!==true)throw new Error('Save not confirmed');
      answer.status='saved';persist();showNext();
    } catch(error) {
      busy=false;controls.forEach(x=>x.disabled=false);submit.textContent='Try sending again';status.textContent='We couldn’t confirm it was saved. Your answers are kept here. Check your connection and try again.';
      // Freeze a possibly saved submission until its idempotent retry succeeds.
      form.querySelectorAll('input,textarea').forEach(x=>x.disabled=true);form.querySelector('#skip').disabled=true;
      if(error.definite){delete answer.pendingBody;persist();controls.forEach(x=>x.disabled=false);status.textContent='This answer wasn’t accepted. Your draft is kept. You can try again or skip this comparison.';}
    } finally {clearTimeout(timer);}
  };
  if(answer.status==='conflict')showConflict();
  else if(answer.pendingBody){form.querySelector('#skip').disabled=true;form.querySelectorAll('input,textarea').forEach(x=>x.disabled=true);form.querySelector('.primary').textContent='Try sending again';status.textContent='Your previous submission still needs confirmation. Tap to retry.';}
  focusPage();
}
function done() {
  stopAudio();const saved=pairs.filter(p=>['saved','savedElsewhere'].includes(state.pairs[p.id]?.status)).length;
  const previous=pairs.some(p=>state.pairs[p.id]?.status==='savedElsewhere');
  progress.textContent='Finished';
  app.innerHTML=`<section class="done"><svg class="saved-symbol" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="29"/><path d="m18 32 9 9 19-20" fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg><h1 tabindex="-1">${saved?'Thank you. That helps.':'Thanks for taking a look.'}</h1><p>${saved===3?'All three answers are saved.':`${saved} of 3 answers saved. Skipped comparisons weren’t submitted.`}${previous?' Earlier answers from this browser were kept.':''}</p><p class="muted">You’ve helped us hear what needs work.</p>${saved<3?'<button class="primary" id="revisit">Try skipped comparisons</button>':''}<a class="text-button" href="?set=${set==='1'?'2':'1'}">Want to hear three more?</a></section>`;
  app.querySelector('#revisit')?.addEventListener('click',()=>{for(const p of pairs){if(state.pairs[p.id]?.status==='skipped')state.pairs[p.id].status='draft';}persist();showNext();});focusPage();
}
document.addEventListener('visibilitychange',()=>{if(document.hidden)activeAudio.forEach(a=>a.pause());});
window.addEventListener('pagehide',()=>activeAudio.forEach(a=>a.pause()));
try {
  const response=await fetch('pairs.json');if(!response.ok)throw new Error('Unavailable');const manifest=await response.json();if(manifest.version!==VERSION)throw new Error('Version mismatch');
  const order=set==='1'?['oshb:Lev.7.1','oshb:2Sam.23.4','oshb:Num.18.10']:['oshb:Hos.7.6','oshb:Isa.6.13','oshb:Num.18.9'];
  pairs=order.map(id=>manifest.pairs.find(p=>p.id===id&&p.set===set));if(pairs.some(p=>!p))throw new Error('Missing clips');
  app.setAttribute('aria-busy','false');if(state.started)showNext();else intro();
  if(!storageAvailable)app.insertAdjacentHTML('beforeend','<p class="toast">This browser can’t keep a draft after you close the page. Submitted answers are still saved.</p>');
} catch {app.setAttribute('aria-busy','false');app.innerHTML='<h1>Clips didn’t load</h1><p>Please check your connection and reload.</p><button class="primary" id="reload">Reload</button>';app.querySelector('#reload').onclick=()=>location.reload();}
