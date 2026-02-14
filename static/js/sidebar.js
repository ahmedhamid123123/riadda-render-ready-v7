(function(){
    'use strict';

    function log() {
        if (window.console && console.log) console.log.apply(console, arguments);
    }

    function initSidebar() {
        const toggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('siteSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const body = document.body;
        if(!toggle || !sidebar) {
            log('sidebar:init - missing elements', { toggle: !!toggle, sidebar: !!sidebar });
            return;
        }

        // Persist collapsed state on desktop
        const STORAGE_KEY = 'riadda.sidebarCollapsed';

        // Use matchMedia so JS breakpoint matches CSS media query exactly
        function isMobile() { return window.matchMedia('(max-width: 991px)').matches; }

        function applyDesktopStateFromStorage(){
            try{
                const stored = localStorage.getItem(STORAGE_KEY);
                log('sidebar:applyDesktopStateFromStorage', { stored: stored });
                if(stored === 'true') body.classList.add('sidebar-collapsed');
                else body.classList.remove('sidebar-collapsed');
            }catch(e){/* ignore */}
        }

        function saveDesktopState(){
            try{ localStorage.setItem(STORAGE_KEY, body.classList.contains('sidebar-collapsed') ? 'true' : 'false'); }catch(e){ }
        }

        function openMobile(){
            body.classList.add('sidebar-open');
            toggle.classList.add('active');
            toggle.setAttribute('aria-expanded', 'true');
            toggle.setAttribute('aria-pressed', 'true');
            if(overlay) overlay.classList.add('visible');
            // Keep CSS checkbox in sync so label.overlay appears correctly
            try{ var cb = document.getElementById('sidebar-toggle'); if(cb) cb.checked = true; }catch(e){}
            sidebar.classList.add('open');
            log('sidebar:opened');
        }

        function closeMobile(){
            body.classList.remove('sidebar-open');
            toggle.classList.remove('active');
            toggle.setAttribute('aria-expanded', 'false');
            toggle.setAttribute('aria-pressed', 'false');
            if(overlay) overlay.classList.remove('visible');
            // Uncheck the CSS checkbox so the label.overlay stops blocking clicks
            try{ var cb = document.getElementById('sidebar-toggle'); if(cb) cb.checked = false; }catch(e){}
            sidebar.classList.remove('open');
            log('sidebar:closed');
        }

        function toggleDesktop(){
            if(body.classList.contains('sidebar-collapsed')){
                body.classList.remove('sidebar-collapsed');
                toggle.classList.add('active');
                toggle.setAttribute('aria-expanded', 'true');
                toggle.setAttribute('aria-pressed', 'true');
            } else {
                body.classList.add('sidebar-collapsed');
                toggle.classList.remove('active');
                toggle.setAttribute('aria-expanded', 'false');
                toggle.setAttribute('aria-pressed', 'false');
            }
            saveDesktopState();
            log('sidebar:toggleDesktop', { collapsed: body.classList.contains('sidebar-collapsed') });
        }

        function handleToggle(e){
            if(e && e.preventDefault) try{ e.preventDefault(); }catch(_){ }
            if(e && e.stopPropagation) try{ e.stopPropagation(); }catch(_){ }
            log('sidebar:handleToggle', { type: e && e.type, innerWidth: window.innerWidth, isMobile: isMobile(), bodyClass: body.className });
            if(isMobile()){
                if(body.classList.contains('sidebar-open')) closeMobile();
                else openMobile();
            } else {
                toggleDesktop();
            }
        }

        // Attach listeners (idempotent per event)
        function safeAdd(el, evt, fn){
            if(!el) return;
            el._sidebarListeners = el._sidebarListeners || {};
            if(!el._sidebarListeners[evt]){
                el.addEventListener(evt, fn);
                el._sidebarListeners[evt] = true;
            }
        }

        safeAdd(toggle, 'click', handleToggle);
        safeAdd(toggle, 'touchstart', handleToggle);
        safeAdd(toggle, 'keydown', function(e){ if(e.key === 'Enter' || e.key === ' ') handleToggle(e); });
        // Ensure onclick fallback for restrictive environments and mark as attached
        try{ toggle.onclick = handleToggle; toggle._sidebarListeners = toggle._sidebarListeners || {}; toggle._sidebarListeners.onclick = true; }catch(e){ }

        if(overlay){ overlay.addEventListener('click', closeMobile); }

        document.addEventListener('click', function(e){
            if(isMobile()){
                if(!sidebar.contains(e.target) && !toggle.contains(e.target) && !(overlay && overlay.contains(e.target))){
                    closeMobile();
                }
            }
        });

        window.addEventListener('resize', function(){
            if(!isMobile()){
                // leaving mobile, ensure classes cleaned
                closeMobile();
                // also ensure the CSS-only checkbox is unchecked on desktop
                try{ var cb = document.getElementById('sidebar-toggle'); if(cb) cb.checked = false; }catch(e){}
                applyDesktopStateFromStorage();
            }
        });

        // Close on ESC
        document.addEventListener('keydown', function(e){ if(e.key === 'Escape' || e.key === 'Esc') { if(isMobile()) closeMobile(); } });

        // Initialize desktop state
        applyDesktopStateFromStorage();

        log('sidebar:init - done');
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSidebar);
    else initSidebar();
})();
