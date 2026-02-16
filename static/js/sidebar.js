(function(){
  'use strict';

  const STORAGE_KEY = 'riadda.sidebarCollapsed';

  function isMobile(){
    return window.matchMedia('(max-width: 991px)').matches;
  }

  function qs(id){ return document.getElementById(id); }

  function setAria(toggle, expanded){
    if(!toggle) return;
    toggle.classList.toggle('active', expanded);
    toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    toggle.setAttribute('aria-pressed', expanded ? 'true' : 'false');
  }

  function openMobile(){
    document.body.classList.add('sidebar-open');
    setAria(qs('sidebarToggle'), true);
  }

  function closeMobile(){
    document.body.classList.remove('sidebar-open');
    setAria(qs('sidebarToggle'), false);
  }

  function toggleDesktop(){
    const body = document.body;
    const collapsed = body.classList.toggle('sidebar-collapsed');
    setAria(qs('sidebarToggle'), !collapsed);
    try{
      localStorage.setItem(STORAGE_KEY, collapsed ? 'true' : 'false');
    }catch(e){}
  }

  function applyDesktopState(){
    try{
      const stored = localStorage.getItem(STORAGE_KEY);
      if(stored === 'true') document.body.classList.add('sidebar-collapsed');
      else document.body.classList.remove('sidebar-collapsed');
    }catch(e){}
  }

  function handleToggle(e){
    if(e){ e.preventDefault?.(); e.stopPropagation?.(); }
    if(isMobile()){
      document.body.classList.contains('sidebar-open') ? closeMobile() : openMobile();
    }else{
      toggleDesktop();
    }
  }

  function init(){
    const toggle = qs('sidebarToggle');
    const overlay = qs('sidebarOverlay');
    const sidebar = qs('siteSidebar');

    if(!toggle || !sidebar){
      console.warn('sidebar:init - missing elements');
      return;
    }

    toggle.addEventListener('click', handleToggle);
    toggle.addEventListener('keydown', (e)=>{ if(e.key === 'Enter' || e.key === ' ') handleToggle(e); });

    if(overlay){
      overlay.addEventListener('click', closeMobile);
    }

    document.addEventListener('keydown', (e)=>{
      if((e.key === 'Escape' || e.key === 'Esc') && isMobile()){
        closeMobile();
      }
    });

    window.addEventListener('resize', ()=>{
      if(!isMobile()){
        // leaving mobile: ensure mobile state cleared, then apply desktop state
        closeMobile();
        applyDesktopState();
      }
    });

    // init desktop state on load
    applyDesktopState();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
