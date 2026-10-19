(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const tokenKey = 'licitagoias_access_token';
  const visualComfortKey = 'licitagoias_visual_comfort';
  let accessToken = sessionStorage.getItem(tokenKey) || '';
  const applyVisualComfort = enabled => {
    document.documentElement.dataset.visualComfort = enabled ? 'on' : 'off';
    const toggle = $('#visual-comfort-toggle');
    if (!toggle) return;
    toggle.setAttribute('aria-pressed', String(enabled));
    toggle.setAttribute('aria-label', `${enabled ? 'Desativar' : 'Ativar'} conforto visual`);
    toggle.title = `${enabled ? 'Desativar' : 'Ativar'} conforto visual`;
    toggle.innerHTML = '<svg class="comfort-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h8m4 0h4M4 12h2m4 0h10M4 18h8m4 0h4"/><circle cx="14" cy="6" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="14" cy="18" r="2"/></svg>';
  };
  let visualComfort = false;
  try { visualComfort = localStorage.getItem(visualComfortKey) === 'on'; } catch (_) { /* Preferência indisponível neste navegador. */ }
  applyVisualComfort(visualComfort);
  let config;
  let catalog;
  let currentUser;
  let currentOrganization;
  let profiles = [];
  let selectedProfile = '';
  let feedPage = 1;
  let feedMode = new URLSearchParams(location.search).get('feed_view') === 'all' ? 'all' : 'matched';
  let explorePage = 1;
  let exploreRequestId = 0;
  let exploreDebounceTimer;
  let activeView = 'feed';
  let toastTimer;
  let sessionGeneration = 0;
  let followCountLoaded = false;
  let profileStep = 1;
  let pendingFeedback = null;

  const resetAccountUi = () => {
    sessionGeneration += 1;
    currentUser = null; currentOrganization = null; profiles = []; selectedProfile = '';
    feedPage = 1; explorePage = 1; activeView = 'feed';
    followCountLoaded = false;
    $('#organization-form').reset(); $('#profile-form').reset(); $('#search-form').reset();
    refreshCustomSelects();closeCustomSelects();closeDateCalendars();
    setDatePickerValue('from', ''); setDatePickerValue('to', '');
    $('#profile-form').elements.id.value = '';
    $('#profile-list').replaceChildren();$('#profile-list-panel').classList.remove('hidden');$('#profile-editor').classList.add('hidden');$('#new-profile').classList.remove('hidden');
    profileStep=1;
    $('#pref-email').checked = false; $('#pref-frequency').value = 'off'; $('#pref-hour').value = '8';
    $('#pref-timezone').value = 'America/Sao_Paulo'; $('#pref-critical').checked = false; $('#pref-feedback').textContent = '';
    $('#organization-name').textContent = 'Sua empresa'; $('#user-email').textContent = ''; $('#user-avatar').textContent = 'LG';
    $('#profile-name-label').textContent = 'Sem perfil'; $('#result-total').textContent = '—'; $('#explore-total').textContent = '—';
    const coverageLabel = $('#coverage-label'); if (coverageLabel) coverageLabel.textContent = 'Verificando atualização…'; $('#data-notice').textContent = ''; $('#data-notice').classList.add('hidden');
    $('#dock-feed-count').textContent='—'; $('#dock-follows-count').textContent='0'; $('#dock-alert-status').classList.remove('has-unread');
    $('#feed-volume').textContent='—'; $('#feed-match').textContent='—'; $('#feed-upcoming').textContent='—';
    $('#opportunity-list').innerHTML = ''; $('#explore-list').innerHTML = '<div class="empty-state">Digite um termo ou escolha ao menos um filtro para pesquisar.</div>';
    $('#follows-list').innerHTML = ''; $('#alerts-list').innerHTML = '';
    $('#pagination').classList.add('hidden'); $('#explore-pagination').classList.add('hidden');
    $('#organization-setup').classList.add('hidden'); $$('.view').forEach(node => node.classList.add('hidden'));
    $$('.nav-item').forEach(item => item.classList.toggle('active', item.dataset.view === 'feed'));
    $('#breadcrumb-label').textContent = 'PARA MINHA EMPRESA';
    $('#login-form').reset(); $('#login-error').textContent = '';
    clearTimeout(toastTimer); $('#toast').classList.remove('show');
    const picker = $('#profile-select'); if (picker) picker.remove();
    const dialog = $('#detail-dialog'); if (dialog.open) dialog.close(); $('#detail-content').innerHTML = '';
    history.replaceState(null, '', location.pathname);
  };

  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const datePickerMonths = new Map();
  const dateIso = date => `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
  const parseIsoDate = value => {
    if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
    const [year,month,day]=value.split('-').map(Number);
    const date=new Date(year,month-1,day,12);
    return date.getFullYear()===year&&date.getMonth()===month-1&&date.getDate()===day?date:null;
  };
  const displayDate = (value,name) => {
    const date=parseIsoDate(value);
    return date?new Intl.DateTimeFormat('pt-BR').format(date):(name==='from'?'Abertura desde':'Abertura até');
  };
  const setSelectValue = (select,value) => {
    if(!select)return;
    if(value&&!Array.from(select.options).some(option=>option.value===value)){
      const option=document.createElement('option');option.value=value;option.textContent=value;option.dataset.legacyValue='true';select.add(option);
    }
    select.value=value||'';
    customSelectControls.get(select)?.refresh();
  };
  const customSelectControls = new WeakMap();
  const createCustomSelect = select => {
    const existing=customSelectControls.get(select);if(existing){existing.refresh();return existing;}
    const searchable=select.dataset.searchable==='true';const label=select.getAttribute('aria-label')||select.labels?.[0]?.textContent.trim()||'Escolher opção';
    const root=document.createElement('div');root.className='custom-select';root.dataset.component='select';
    select.parentNode.insertBefore(root,select);root.append(select);select.classList.add('custom-select-native');select.tabIndex=-1;select.setAttribute('aria-hidden','true');
    const button=document.createElement('button');button.type='button';button.className='custom-select-trigger';button.setAttribute('role','combobox');button.setAttribute('aria-label',label);button.setAttribute('aria-haspopup','listbox');button.setAttribute('aria-expanded','false');
    const popover=document.createElement('div');popover.className='custom-select-popover';popover.hidden=true;
    let searchInput=null;
    if(searchable){searchInput=document.createElement('input');searchInput.type='search';searchInput.className='custom-select-search';searchInput.placeholder='Buscar município';searchInput.setAttribute('aria-label',`${label}: buscar opções`);popover.append(searchInput);}
    const listbox=document.createElement('div');listbox.className='custom-select-options';listbox.id=`${select.id}-options`;listbox.setAttribute('role','listbox');listbox.setAttribute('aria-label',label);popover.append(listbox);
    button.setAttribute('aria-controls',listbox.id);root.append(button,popover);
    let activeIndex=-1;let typeahead='';let typeaheadTimer;
    const renderOptions = (query='') => {
      const normalized=query.trim().toLocaleLowerCase('pt-BR');listbox.replaceChildren();
      Array.from(select.options).forEach((option,index)=>{
        if(normalized&&!option.textContent.toLocaleLowerCase('pt-BR').includes(normalized))return;
        const item=document.createElement('div');item.className='custom-select-option';item.id=`${select.id}-option-${index}`;item.setAttribute('role','option');item.setAttribute('aria-selected',String(option.selected));item.dataset.optionIndex=String(index);item.tabIndex=-1;
        const text=document.createElement('span');text.textContent=option.textContent;item.append(text);
        if(option.selected){const check=document.createElement('i');check.className='ti ti-check';check.setAttribute('aria-hidden','true');item.append(check);}
        listbox.append(item);
      });
      if(!listbox.children.length){const empty=document.createElement('div');empty.className='custom-select-no-results';empty.setAttribute('role','status');empty.textContent='Nenhum município encontrado.';listbox.append(empty);}
      const visible=Array.from(listbox.querySelectorAll('[role="option"]'));
      activeIndex=visible.some(item=>Number(item.dataset.optionIndex)===activeIndex)?activeIndex:(visible[0]?Number(visible[0].dataset.optionIndex):-1);
      setActive(activeIndex);
    };
    const setActive = index => {
      const item=listbox.querySelector(`[data-option-index="${index}"]`);
      listbox.querySelectorAll('[role="option"]').forEach(option=>option.classList.toggle('is-active',option===item));
      activeIndex=item?index:-1;
      const owner=searchInput&&document.activeElement===searchInput?searchInput:button;
      if(item){owner.setAttribute('aria-activedescendant',item.id);item.scrollIntoView({block:'nearest'});}else owner.removeAttribute('aria-activedescendant');
    };
    const visibleOptions=()=>Array.from(listbox.querySelectorAll('[role="option"]'));
    const moveActive=delta=>{const items=visibleOptions();if(!items.length)return;const position=items.findIndex(item=>Number(item.dataset.optionIndex)===activeIndex);setActive(Number(items[(position+delta+items.length)%items.length].dataset.optionIndex));};
    const close=(restoreFocus=false)=>{root.classList.remove('is-open');popover.hidden=true;button.setAttribute('aria-expanded','false');button.removeAttribute('aria-activedescendant');searchInput?.removeAttribute('aria-activedescendant');if(restoreFocus)button.focus();};
    const refresh=()=>{const selected=select.selectedOptions[0];button.replaceChildren();const text=document.createElement('span');text.className='custom-select-value';text.textContent=selected?.textContent||'Selecione';button.append(text);const icon=document.createElement('i');icon.className='ti ti-chevron-down';icon.setAttribute('aria-hidden','true');button.append(icon);button.title=selected?.textContent||label;renderOptions(searchInput?.value||'');};
    const position=()=>{const rect=button.getBoundingClientRect();const width=Math.min(Math.max(rect.width,searchable?300:250),window.innerWidth-24);popover.style.width=`${width}px`;const height=popover.offsetHeight;const left=Math.max(12,Math.min(rect.left,window.innerWidth-width-12));const below=rect.bottom+6+height<=window.innerHeight-12;popover.style.left=`${left}px`;popover.style.top=`${below?rect.bottom+6:Math.max(12,rect.top-height-6)}px`;};
    const open=()=>{closeCustomSelects(root);closeDateCalendars();root.classList.add('is-open');popover.hidden=false;document.body.append(popover);button.setAttribute('aria-expanded','true');if(searchInput){searchInput.value='';renderOptions();searchInput.focus();}else{renderOptions();button.focus();}position();};
    button.addEventListener('click',()=>root.classList.contains('is-open')?close():open());
    button.addEventListener('keydown',event=>{
      if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();if(!root.classList.contains('is-open'))open();else moveActive(event.key==='ArrowDown'?1:-1);}
      else if((event.key==='Enter'||event.key===' ')&&!root.classList.contains('is-open')){event.preventDefault();open();}
      else if((event.key==='Enter'||event.key===' ')&&root.classList.contains('is-open')&&activeIndex>=0){event.preventDefault();selectOption(activeIndex);}
      else if(event.key==='Escape'&&root.classList.contains('is-open')){event.preventDefault();close(true);}
      else if(event.key==='Home'&&root.classList.contains('is-open')){event.preventDefault();const item=visibleOptions()[0];if(item)setActive(Number(item.dataset.optionIndex));}
      else if(event.key==='End'&&root.classList.contains('is-open')){event.preventDefault();const items=visibleOptions();if(items.length)setActive(Number(items.at(-1).dataset.optionIndex));}
      else if(!searchable&&event.key.length===1&&!event.ctrlKey&&!event.metaKey){typeahead+=event.key.toLocaleLowerCase('pt-BR');clearTimeout(typeaheadTimer);typeaheadTimer=setTimeout(()=>{typeahead='';},650);const match=Array.from(select.options).findIndex(option=>option.textContent.toLocaleLowerCase('pt-BR').startsWith(typeahead));if(match>=0){activeIndex=match;if(!root.classList.contains('is-open'))open();setActive(match);}}
    });
    searchInput?.addEventListener('input',()=>renderOptions(searchInput.value));
    searchInput?.addEventListener('keydown',event=>{
      if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();moveActive(event.key==='ArrowDown'?1:-1);}
      else if(event.key==='Enter'&&activeIndex>=0){event.preventDefault();selectOption(activeIndex);}
      else if(event.key==='Escape'){event.preventDefault();close(true);}
      else if(event.key==='Home'&&!searchInput.value){event.preventDefault();const item=visibleOptions()[0];if(item)setActive(Number(item.dataset.optionIndex));}
      else if(event.key==='End'&&!searchInput.value){event.preventDefault();const items=visibleOptions();if(items.length)setActive(Number(items.at(-1).dataset.optionIndex));}
    });
    const selectOption=index=>{if(!select.options[index])return;select.selectedIndex=index;select.dispatchEvent(new Event('change',{bubbles:true}));refresh();close(true);};
    popover.addEventListener('pointerdown',event=>{if(event.target.closest('[role="option"]'))event.preventDefault();});
    popover.addEventListener('click',event=>{const option=event.target.closest('[data-option-index]');if(option)selectOption(Number(option.dataset.optionIndex));});
    select.addEventListener('change',refresh);
    const destroy=()=>{close();popover.remove();root.remove();customSelectControls.delete(select);};
    const control={root,button,popover,refresh,close,position,destroy};customSelectControls.set(select,control);refresh();return control;
  };
  const destroyCustomSelect = select => {const control=customSelectControls.get(select);if(control)control.destroy();else select.remove();};
  const clearCustomSelects = container => {container.querySelectorAll('select').forEach(destroyCustomSelect);container.replaceChildren();};
  const closeCustomSelects = (except=null,restoreFocus=false) => {
    document.querySelectorAll('.custom-select.is-open').forEach(root=>{if(root===except)return;const select=root.querySelector('select');customSelectControls.get(select)?.close(restoreFocus);});
  };
  const refreshCustomSelects = () => $$('select[data-custom-select]').forEach(select=>customSelectControls.get(select)?.refresh());
  const setDatePickerValue = (name,value) => {
    const input=$(`#search-${name}`);const display=$(`[data-date-display="${name}"]`);
    const normalized=parseIsoDate(value)?value:'';
    if(input)input.value=normalized;
    if(display)display.textContent=displayDate(normalized,name);
    if(normalized){const date=parseIsoDate(normalized);datePickerMonths.set(name,new Date(date.getFullYear(),date.getMonth(),1));}
  };
  const renderDateCalendar = name => {
    const calendar=$(`[data-calendar="${name}"]`);if(!calendar)return;
    const input=$(`#search-${name}`);const selected=parseIsoDate(input?.value||'');
    const stored=datePickerMonths.get(name)||new Date(new Date().getFullYear(),new Date().getMonth(),1);
    const year=stored.getFullYear(),month=stored.getMonth();
    const first=new Date(year,month,1,12);const offset=(first.getDay()+6)%7;const days=new Date(year,month+1,0).getDate();
    const weekdays=['Seg','Ter','Qua','Qui','Sex','Sáb','Dom'];
    const blanks=Array.from({length:offset},()=>'<span class="calendar-empty" aria-hidden="true"></span>');
    const cells=Array.from({length:days},(_,index)=>{
      const date=new Date(year,month,index+1,12);const value=dateIso(date);const isSelected=selected&&dateIso(selected)===value;const isToday=dateIso(new Date())===value;
      return `<button class="calendar-day${isSelected?' is-selected':''}${isToday?' is-today':''}" type="button" data-calendar-date="${value}" aria-label="${new Intl.DateTimeFormat('pt-BR',{dateStyle:'full'}).format(date)}" aria-pressed="${Boolean(isSelected)}"${isToday?' aria-current="date"':''}>${index+1}</button>`;
    });
    while(blanks.length+cells.length<42)cells.push('<span class="calendar-empty" aria-hidden="true"></span>');
    const monthLabel=new Intl.DateTimeFormat('pt-BR',{month:'long',year:'numeric'}).format(first);
    calendar.innerHTML=`<div class="calendar-heading"><button class="calendar-nav" type="button" data-calendar-step="-1" aria-label="Mês anterior">‹</button><strong>${monthLabel}</strong><button class="calendar-nav" type="button" data-calendar-step="1" aria-label="Próximo mês">›</button><button class="calendar-close" type="button" data-calendar-close="true" aria-label="Fechar calendário">×</button></div><div class="calendar-weekdays" aria-hidden="true">${weekdays.map(day=>`<span>${day}</span>`).join('')}</div><div class="calendar-days" aria-label="Dias do mês">${blanks.join('')}${cells.join('')}</div><div class="calendar-footer"><button type="button" class="calendar-clear" data-calendar-clear="${name}">Limpar data</button></div>`;
  };
  const closeDateCalendars = (returnFocus=false) => {
    const active=document.activeElement?.closest('[data-calendar]')?.dataset.calendar||document.activeElement?.closest('[data-date-picker]')?.dataset.datePicker;
    document.querySelectorAll('[data-calendar-trigger]').forEach(trigger=>trigger.setAttribute('aria-expanded','false'));
    document.querySelectorAll('.date-popover').forEach(popover=>popover.classList.add('hidden'));
    if(returnFocus&&active)$(`[data-calendar-trigger="${active}"]`)?.focus();
  };
  const positionDateCalendar = popover => {
    const trigger=$(`[data-calendar-trigger="${popover.dataset.calendar}"]`);if(!trigger)return;
    const rect=trigger.getBoundingClientRect();const width=popover.offsetWidth;const height=popover.offsetHeight;const margin=12;
    const left=Math.max(margin,Math.min(rect.right-width,window.innerWidth-width-margin));
    const below=rect.bottom+8+height<=window.innerHeight-margin;
    const top=below?rect.bottom+8:Math.max(margin,rect.top-height-8);
    popover.style.left=`${left}px`;popover.style.top=`${top}px`;
  };
  const repositionOpenDateCalendars = () => {
    document.querySelectorAll('.date-popover:not(.hidden)').forEach(positionDateCalendar);
    document.querySelectorAll('.custom-select.is-open').forEach(root=>customSelectControls.get(root.querySelector('select'))?.position());
  };
  const showToast = (message, type = 'success') => {
    const node = $('#toast');
    const icon = type === 'error' ? 'alert-circle' : type === 'info' ? 'info-circle' : 'circle-check';
    node.innerHTML = `<i class="ti ti-${icon} toast-icon" aria-hidden="true"></i><span class="toast-message">${esc(message)}</span><button class="toast-dismiss" type="button" aria-label="Fechar aviso"><i class="ti ti-x" aria-hidden="true"></i></button>`;
    node.className = `toast toast-${type} show`;
    node.setAttribute('role', type === 'error' ? 'alert' : 'status');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => node.classList.remove('show'), 3400);
  };
  $('#toast').addEventListener('click', event => {
    if (event.target.closest('.toast-dismiss')) { clearTimeout(toastTimer); $('#toast').classList.remove('show'); }
  });
  const shortDate = value => {
    if (!value) return null;
    const parsed = new Date(`${String(value).slice(0, 10)}T12:00:00`);
    return Number.isNaN(parsed.getTime()) ? null : parsed.toLocaleDateString('pt-BR');
  };
  const dataDate = field => {
    if (field && typeof field === 'object') return shortDate(field.iso || field.raw);
    return shortDate(field);
  };
  const money = field => {
    const raw = field && typeof field === 'object' ? field.decimal : field;
    if (raw === null || raw === undefined || raw === '') return 'Valor não informado';
    const number = Number(raw);
    return Number.isFinite(number) ? number.toLocaleString('pt-BR', {style:'currency',currency:'BRL'}) : 'Valor não informado';
  };
  const api = async (path, options = {}) => {
    const requestGeneration = sessionGeneration;
    const headers = new Headers(options.headers || {});
    headers.set('Content-Type', 'application/json');
    if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
    const response = await fetch(path, {...options, headers});
    if (requestGeneration !== sessionGeneration) throw new Error('A conta mudou durante a solicitação.');
    if (response.status === 401 && accessToken) {
      accessToken = ''; sessionStorage.removeItem(tokenKey); resetAccountUi(); showLogin('Sua sessão expirou. Entre novamente.');
    }
    if (response.status === 204) return null;
    const body = await response.json().catch(() => ({}));
    if (requestGeneration !== sessionGeneration) throw new Error('A conta mudou durante a solicitação.');
    if (!response.ok) throw new Error(body.detail || `A solicitação falhou (${response.status})`);
    return body;
  };
  const showLogin = message => {
    $('#boot-screen').classList.add('hidden'); $('#login-screen').classList.remove('hidden'); $('#app-screen').classList.add('hidden');
    $('#login-error').textContent = message || '';
  };
  const showBoot = () => { $('#boot-screen').classList.remove('hidden'); $('#login-screen').classList.add('hidden'); $('#app-screen').classList.add('hidden'); };
  const showApp = () => { $('#boot-screen').classList.add('hidden'); $('#login-screen').classList.add('hidden'); $('#app-screen').classList.remove('hidden'); };
  const cleanError = error => error instanceof Error ? error.message : 'Não foi possível concluir a operação.';

  $('#login-form').addEventListener('submit', async event => {
    event.preventDefault(); $('#login-error').textContent = '';
    const form = new FormData(event.currentTarget);
    try {
      const response = await fetch(`${config.supabase_url}/auth/v1/token?grant_type=password`, {
        method:'POST', headers:{'Content-Type':'application/json', apikey:config.publishable_key},
        body:JSON.stringify({email:form.get('email'), password:form.get('password')})
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok || !body.access_token || !body.user?.email_confirmed_at) throw new Error('Acesso inválido. Confirme o e-mail e verifique a senha da conta.');
      resetAccountUi();
      accessToken = body.access_token; sessionStorage.setItem(tokenKey, accessToken);
      showBoot();
      await startApp();
    } catch (error) { $('#login-error').textContent = cleanError(error); }
  });
  $('#logout-button').addEventListener('click', () => {
    accessToken = ''; sessionStorage.removeItem(tokenKey); resetAccountUi(); showLogin('');
  });

  const loadProfiles = async (preferredId = '') => {
    profiles = await api('/v1/interest-profiles');
    const requested = new URLSearchParams(location.search).get('profile');
    selectedProfile = profiles.some(profile => profile.id === preferredId) ? preferredId : (profiles.some(profile => profile.id === requested) ? requested : (profiles[0]?.id || ''));
    $('#profile-name-label').textContent = profiles.find(item => item.id === selectedProfile)?.name || 'Sem perfil';
    renderProfileSwitchOptions();
    renderProfileList();
  };
  const renderProfileSwitchOptions = () => {
    const container = $('#profile-switch-list');
    if (!container) return;
    if (!profiles.length) {
      container.innerHTML = '<div class="profile-switch-empty"><i class="ti ti-adjustments-horizontal" aria-hidden="true"></i><strong>Nenhum perfil criado</strong><span>Crie um perfil para receber oportunidades alinhadas aos interesses da sua empresa.</span></div>';
      return;
    }
    container.innerHTML = profiles.map(profile => `<button class="profile-switch-option${profile.id === selectedProfile ? ' is-current' : ''}" type="button" data-switch-profile="${esc(profile.id)}" ${profile.id === selectedProfile ? 'aria-current="true"' : ''}><span class="profile-switch-option-icon"><i class="ti ti-briefcase-2" aria-hidden="true"></i></span><span class="profile-switch-option-copy"><strong>${esc(profile.name)}</strong><small>${esc(profileSummary(profile))}</small></span><span class="profile-switch-option-state">${profile.id === selectedProfile ? '<i class="ti ti-check" aria-hidden="true"></i> Em uso' : '<i class="ti ti-arrow-right" aria-hidden="true"></i> Usar perfil'}</span></button>`).join('');
  };
  const updateUrl = values => {
    const params = new URLSearchParams(location.search);
    for (const [key, value] of Object.entries(values)) {
      if (value) params.set(key, value); else params.delete(key);
    }
    history.replaceState(null, '', `${location.pathname}${params.size ? `?${params}` : ''}${location.hash}`);
  };
  const setCoverage = coverage => {
    const label = $('#coverage-label');
    const states = {complete:'Coleta concluída',partial:'Coleta parcial',failed:'Falha na coleta',stale:'Atualização atrasada',unavailable:'Sem coleta registrada',running:'Coleta em andamento'};
    if (label) label.textContent = `${states[coverage?.state] || 'Estado desconhecido'}${coverage?.last_run_at ? ` · ${shortDate(coverage.last_run_at)}` : ''}`;
    const notice = $('#data-notice');
    const warn = !coverage || ['partial','failed','stale','unavailable','running'].includes(coverage.state);
    notice.classList.toggle('hidden', !warn);
    notice.classList.toggle('critical', ['failed','unavailable'].includes(coverage?.state));
    notice.textContent = coverage?.message || ({partial:'A última coleta foi parcial. A lista pode não conter todas as oportunidades disponíveis.',failed:'A última coleta falhou. Os resultados existentes continuam disponíveis, mas podem estar desatualizados.',stale:'A fonte não é atualizada há mais de 24 horas. Confira o edital e o portal oficial.',unavailable:'Ainda não há coleta PNCP registrada para esta base.',running:'Uma coleta está em andamento; os resultados podem estar incompletos.'}[coverage?.state] || 'O estado da fonte não pôde ser confirmado.');
  };
  const renderOpportunity = (opportunity, showClassification = false) => {
    const data = opportunity.data || {};
    const title = data.objeto || 'Objeto não informado';
    const agency = [data.orgao_comprador, data.municipio, data.uf].filter(Boolean).join(' · ') || 'Órgão/local não informado';
    const deadline = dataDate(data.data_fechamento);
    const classification = opportunity.match;
    const classificationReason = classification?.included ? classification.reasons?.[0] : classification?.exclusions?.[0];
    const classificationNote = showClassification && classification ? `<div class="classification-note ${classification.included?'is-compatible':'is-outside'}"><i class="ti ${classification.included?'ti-circle-check':'ti-filter-off'}" aria-hidden="true"></i><span><strong>${classification.included?'Compatível com o perfil':'Fora dos critérios do perfil'}</strong><small>${esc(classificationReason || 'Sem correspondência nos critérios atuais')}</small></span></div>` : '';
    return `<article class="op-card${opportunity.followed?' is-followed':''}" data-id="${esc(opportunity.id)}">
      <div class="card-main"><div class="card-meta"><span>${esc(data.modalidade || 'MODALIDADE NÃO INFORMADA')}</span><span class="meta-sep">/</span><span>${esc(opportunity.official_status || data.status || 'SITUAÇÃO NÃO INFORMADA')}</span></div>
        <h2 class="card-title">${esc(title)}</h2><div class="card-agency">${esc(agency)}</div>
        ${classificationNote}
        <div class="feedback-row"><button class="small-action feedback-choice" data-act="feedback-yes" aria-pressed="false"><i class="ti ti-thumb-up" aria-hidden="true"></i> Útil para mim</button><button class="small-action feedback-choice" data-act="feedback-no" aria-pressed="false"><i class="ti ti-thumb-down" aria-hidden="true"></i> Não é relevante</button></div>
      </div><div class="card-right"><div class="card-value">${esc(money(data.valor_estimado))}</div><div class="card-deadline ${deadline ? '' : 'unknown'}">${deadline ? `ABERTURA ${esc(dataDate(data.data_abertura) || 'N/D')} · FECHA ${esc(deadline)}` : 'PRAZO NÃO INFORMADO'}</div>
        <div class="card-actions"><button class="small-action" data-act="detail"><i class="ti ti-file-search" aria-hidden="true"></i> Ver ficha</button><button class="small-action ${opportunity.followed?'following':''}" data-act="follow" aria-pressed="${Boolean(opportunity.followed)}"><i class="ti ${opportunity.followed?'ti-check':'ti-bookmark'}" aria-hidden="true"></i> ${opportunity.followed?'Acompanhando':'Acompanhar'}</button></div></div>
    </article>`;
  };
  const loadFeed = async page => {
    feedPage = page; const list = $('#opportunity-list');
    if (!selectedProfile) {
      $('#result-total').textContent = '—';
      $('#feed-volume').textContent='—'; $('#feed-match').textContent='—'; $('#feed-upcoming').textContent='—';
      list.innerHTML = '<div class="empty-state">Configure um perfil para ver oportunidades alinhadas à sua empresa.<br><br><button class="button button-dark" data-act="create-profile"><i class="ti ti-plus" aria-hidden="true"></i> Criar perfil</button></div>';
      $('#pagination').classList.add('hidden'); return;
    }
    list.innerHTML = '<div class="loading-state"><span class="loader"></span> Consultando oportunidades coletadas…</div>';
    try {
      const result = await api(`/v1/feed?profile_id=${encodeURIComponent(selectedProfile)}&view=${feedMode}&page=${page}&page_size=30`);
      setCoverage(result.coverage); $('#result-total').textContent = result.total.toLocaleString('pt-BR'); $('#dock-feed-count').textContent=result.total.toLocaleString('pt-BR');
      $('#result-total-label').textContent=feedMode==='all'?'oportunidades na base coletada':'compatíveis com o perfil';
      $('#feed-match').textContent=Number(result.matched_total||0).toLocaleString('pt-BR');
      $('#feed-subheading').textContent=feedMode==='all'?'O perfil organiza os resultados sem ocultar as demais oportunidades.':'Oportunidades classificadas pelos critérios do perfil.';
      $('#feed-list-title').textContent=feedMode==='all'?'Todas as oportunidades':'Oportunidades compatíveis';
      $('#feed-list-description').textContent=feedMode==='all'?'O perfil classifica, mas não oculta resultados':'Classificadas pelos critérios do perfil';
      $$('[data-feed-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.feedView===feedMode)));
      const values=result.items.map(item=>Number((item.data?.valor_estimado&&typeof item.data.valor_estimado==='object'?item.data.valor_estimado.decimal:item.data?.valor_estimado)||0)).filter(Number.isFinite);
      const totalValue=values.reduce((sum,value)=>sum+value,0);$('#feed-volume').textContent=totalValue?totalValue.toLocaleString('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}):'Não informado';
      const now=new Date();now.setHours(0,0,0,0);const upcoming=result.items.filter(item=>{const raw=item.data?.data_abertura;const iso=typeof raw==='object'?(raw.iso||raw.raw):raw;if(!iso)return false;const date=new Date(`${String(iso).slice(0,10)}T12:00:00`);const days=(date-now)/86400000;return days>=0&&days<=7;}).length;$('#feed-upcoming').textContent=upcoming.toLocaleString('pt-BR');
      list.innerHTML = result.items.length ? result.items.map(item=>renderOpportunity(item,feedMode==='all')).join('') : (feedMode==='all' ? '<div class="empty-state">Nenhuma oportunidade disponível na cobertura coletada.</div>' : '<div class="empty-state">Nenhuma oportunidade corresponde ao perfil nesta página da cobertura coletada. Você pode consultar todas as oportunidades e revisar os critérios.</div>');
      renderPagination($('#pagination'), $('#page-label'), $('#prev-page'), $('#next-page'), page, result.pages, loadFeed);
    } catch (error) { list.innerHTML = `<div class="empty-state">${esc(cleanError(error))}</div>`; }
  };
  $$('[data-feed-view]').forEach(button=>button.addEventListener('click',()=>{
    const next=button.dataset.feedView;
    if(!['matched','all'].includes(next)||next===feedMode)return;
    feedMode=next;feedPage=1;updateUrl({feed_view:feedMode==='all'?'all':''});loadFeed(1);
  }));
  const renderPagination = (container, label, prev, next, page, pages, callback) => {
    container.classList.toggle('hidden', pages <= 1);
    label.textContent = `Página ${page} de ${pages}`; prev.disabled = page <= 1; next.disabled = page >= pages;
    prev.onclick = () => callback(page - 1); next.onclick = () => callback(page + 1);
  };
  const loadExplore = async (page = 1) => {
    const requestId = ++exploreRequestId;
    explorePage = page;
    const params = new URLSearchParams(location.search);
    const q = params.get('q') || ''; const municipality = params.get('municipality') || '';
    const statusValue=params.get('status')||'', openingFrom=params.get('opening_from')||'', openingTo=params.get('opening_to')||'';
    $('#search-query').value = q; setSelectValue($('#search-municipality'),municipality);setSelectValue($('#search-status'),statusValue);
    setDatePickerValue('from',openingFrom);setDatePickerValue('to',openingTo);
    const list = $('#explore-list');
    if (!q && !municipality && !statusValue && !openingFrom && !openingTo) { list.innerHTML = '<div class="empty-state">Digite um termo ou escolha ao menos um filtro para pesquisar.</div>'; $('#explore-total').textContent='—'; $('#explore-pagination').classList.add('hidden'); return; }
    list.innerHTML = '<div class="loading-state"><span class="loader"></span> Pesquisando na base…</div>';
    try {
      const query=new URLSearchParams(Object.entries({q,municipality,status:statusValue,opening_from:openingFrom,opening_to:openingTo,page,page_size:30}).filter(([,value])=>value!==''&&value!==null&&value!==undefined));
      const result = await api(`/v1/opportunities?${query}`);
      if(requestId!==exploreRequestId)return;
      setCoverage(result.coverage); $('#explore-total').textContent=result.total.toLocaleString('pt-BR');
      list.innerHTML = result.items.length ? result.items.map(item=>renderOpportunity(item)).join('') : '<div class="empty-state">Nenhum resultado nesta cobertura. Experimente outro termo.</div>';
      renderPagination($('#explore-pagination'), $('#explore-page-label'), $('#explore-prev'), $('#explore-next'), page, result.pages, loadExplore);
    } catch (error) { if(requestId===exploreRequestId)list.innerHTML=`<div class="empty-state">${esc(cleanError(error))}</div>`; }
  };
  const loadFollows = async () => {
    const list = $('#follows-list'); list.innerHTML='<div class="loading-state"><span class="loader"></span> Carregando acompanhamentos…</div>';
    try {
      const rows = await api('/v1/follows');
      followCountLoaded = true;
      $('#dock-follows-count').textContent=rows.length.toLocaleString('pt-BR');
      list.innerHTML = rows.length ? rows.map(row => `${renderOpportunity(row.opportunity)}<div class="follow-note">Acompanhando desde ${esc(shortDate(row.created_at))}</div>`).join('') : '<div class="empty-state">Você ainda não acompanha oportunidades.</div>';
    } catch (error) { list.innerHTML=`<div class="empty-state">${esc(cleanError(error))}</div>`; }
  };
  const showDetail = async id => {
    const dialog = $('#detail-dialog'); const content = $('#detail-content');
    content.innerHTML='<div class="detail-body"><div class="loading-state"><span class="loader"></span> Abrindo ficha…</div></div>'; dialog.showModal();
    try {
      const [opportunity, history] = await Promise.all([api(`/v1/opportunities/${id}`), api(`/v1/opportunities/${id}/changes`)]);
      const d = opportunity.data || {};
    const sourceCandidate = d.link_origem || d.link_edital || '';
    let sourceUrl = '';
    try { const parsed = new URL(sourceCandidate); if (parsed.protocol === 'https:') sourceUrl = parsed.href; } catch (_) { /* Link ausente ou inválido. */ }
      const status = opportunity.official_status || d.status || 'Situação não informada';
      const derivedStateLabels = {suspended:'Suspensa',closed:'Encerrada',unknown:'Não foi possível determinar'};
      const derivedStateLabel = derivedStateLabels[String(opportunity.derived_state || 'unknown').toLowerCase()] || 'Não foi possível determinar';
      const valueNature = d.valor_estimado?.natureza;
      const valueLabel = valueNature === 'total_estimado' ? 'Total estimado' : (valueNature && valueNature !== 'desconhecido' ? valueNature.replaceAll('_',' ') : 'Natureza não informada');
      const historyItems = history.items.map(item => `<div class="change-row"><time>${esc(new Date(item.observed_at).toLocaleString('pt-BR'))}</time><p>${Object.entries(item.changes).map(([key,value])=>`<strong>${esc(key)}:</strong> ${esc(value.before ?? 'Ausente')} → ${esc(value.after ?? 'Ausente')}`).join('<br>')}</p></div>`).join('') || '<p>Nenhuma alteração posterior ao início do acompanhamento foi observada.</p>';
      content.innerHTML=`<div class="detail-body"><p class="eyebrow">${esc(d.modalidade || 'OPORTUNIDADE')} / ${esc(opportunity.source)}</p><h2>${esc(d.objeto || 'Objeto não informado')}</h2><p class="detail-lead">${esc(d.orgao_comprador || 'Órgão não informado')} · ${esc(d.municipio || 'Município não informado')}${d.uf ? `, ${esc(d.uf)}` : ''}</p>
        <div class="detail-grid"><div class="detail-cell"><small>SITUAÇÃO OFICIAL</small><strong>${esc(status)}</strong></div><div class="detail-cell"><small>SITUAÇÃO IDENTIFICADA</small><strong>${esc(derivedStateLabel)}</strong></div><div class="detail-cell"><small>${esc(valueLabel.toUpperCase())}</small><strong>${esc(money(d.valor_estimado))}</strong></div><div class="detail-cell"><small>ABERTURA / DISPUTA</small><strong>${esc(dataDate(d.data_abertura) || 'Não informado')}</strong></div><div class="detail-cell"><small>ENCERRAMENTO / PROPOSTAS</small><strong>${esc(dataDate(d.data_fechamento) || 'Não informado')}</strong></div><div class="detail-cell"><small>ÚLTIMA OBSERVAÇÃO</small><strong>${esc(new Date(opportunity.last_observed_at).toLocaleString('pt-BR'))}</strong></div><div class="detail-cell"><small>FONTE</small><strong>${esc(opportunity.source)}</strong></div><div class="detail-cell"><small>IDENTIDADE</small><strong>${esc(opportunity.external_id)}${opportunity.review_required?' · requer revisão':''}</strong></div></div>
        <section class="detail-section"><h3>Objeto publicado</h3><p>${esc(d.objeto || 'Campo não informado pela fonte.')}</p></section>
        <section class="detail-section"><h3>Por que apareceu</h3><p>${esc(opportunity.match?.reasons?.join(' · ') || 'Busca textual na base pública.')}${opportunity.match?.exclusions?.length?`\nExclusões: ${esc(opportunity.match.exclusions.join(' · '))}`:''}</p></section>
        <section class="detail-section"><h3>Histórico observado</h3>${historyItems}</section>
        ${sourceUrl?`<a class="official-link" href="${esc(sourceUrl)}" target="_blank" rel="noopener noreferrer">Abrir processo na fonte oficial <i class="ti ti-external-link" aria-hidden="true"></i></a>`:'<p class="form-error">A fonte não forneceu um link oficial.</p>'}</div>`;
    } catch (error) { content.innerHTML=`<div class="detail-body"><div class="form-error">${esc(cleanError(error))}</div></div>`; }
  };
  const setView = view => {
    activeView = view; location.hash = view;
    $$('.view').forEach(node=>node.classList.add('hidden'));
    $(`#${view}-view`)?.classList.remove('hidden');
    $$('.nav-item').forEach(item=>item.classList.toggle('active',item.dataset.view===view));
    const labels={feed:'PARA MINHA EMPRESA',explore:'EXPLORAR OPORTUNIDADES',follows:'ACOMPANHADAS',profile:'PERFIL DE INTERESSE',alerts:'ALERTAS'};
    $('#breadcrumb-label').textContent=labels[view]||labels.feed;
    if(view==='feed') loadFeed(1); if(view==='explore') loadExplore(1); if(view==='follows') loadFollows(); if(view==='profile') showProfileList(); if(view==='alerts') loadAlerts();
  };
  const loadAlerts = async () => {
    try {
      const [alerts, prefs] = await Promise.all([api('/v1/alerts?limit=100'), api('/v1/notification-preferences')]);
      $('#pref-email').checked=prefs.email_enabled; $('#pref-frequency').value=prefs.digest_frequency;
      $('#pref-hour').value=prefs.digest_hour; $('#pref-timezone').value=prefs.timezone_name;
      $('#pref-critical').checked=prefs.critical_alerts;
      const unread=alerts.some(alert=>!alert.read_at);$('#dock-alert-status').classList.toggle('has-unread',unread);$('#dock-alert-status').setAttribute('aria-label',unread?'Alertas não lidos':'Sem alertas novos');
      $('#alerts-list').innerHTML=alerts.length?alerts.map(alert=>{
        const data=alert.opportunity.data||{}; const title=data.objeto||'Oportunidade';
        return `<article class="alert-card ${alert.severity==='critical'?'is-critical':''}"><div><p class="eyebrow">${esc(alert.severity==='critical'?'ALERTA CRÍTICO':'ALTERAÇÃO')} · ${esc(new Date(alert.created_at).toLocaleString('pt-BR'))}</p><h2>${esc(title)}</h2><p>${esc(alert.event_type.replaceAll('_',' '))}</p><details><summary>Ver alterações</summary><pre>${esc(JSON.stringify(alert.changes,null,2))}</pre></details>${alert.read_at?'':'<button class="small-action" data-alert-read="'+esc(alert.id)+'">Marcar como lido</button>'}</div></article>`;
      }).join(''):'<div class="empty-state">Ainda não há alterações em oportunidades acompanhadas.</div>';
    } catch(error) { $('#alerts-list').innerHTML=`<div class="empty-state">${esc(cleanError(error))}</div>`; showToast(cleanError(error),'error'); }
  };
  $('#save-prefs').addEventListener('click',async()=>{
    const feedback=$('#pref-feedback'); feedback.textContent='';
    try { await api('/v1/notification-preferences',{method:'PUT',body:JSON.stringify({email_enabled:$('#pref-email').checked,digest_frequency:$('#pref-frequency').value,digest_hour:Number($('#pref-hour').value),timezone_name:$('#pref-timezone').value.trim(),critical_alerts:$('#pref-critical').checked})}); feedback.textContent='Preferências salvas.'; showToast('Preferências salvas.'); }
      catch(error){feedback.textContent=cleanError(error);showToast(cleanError(error),'error');}
  });
  $('#refresh-alerts').addEventListener('click',loadAlerts);
  $('#alerts-list').addEventListener('click',async event=>{const button=event.target.closest('[data-alert-read]');if(!button)return;try{await api(`/v1/alerts/${button.dataset.alertRead}/read`,{method:'POST'});showToast('Alerta marcado como lido.');loadAlerts();}catch(error){showToast(cleanError(error),'error');}});
  const renderCatalogFilters = () => {
    $('#profile-municipality').innerHTML='<option value="">Qualquer município da cobertura</option>'+(catalog?.municipalities||[]).map(option=>`<option value="${esc(option.id)}">${esc(option.name)}</option>`).join('');
    $('#profile-municipality').setAttribute('data-searchable','true');
    createCustomSelect($('#profile-municipality'));
    createCustomSelect($('#profile-form [name="deadline_days"]'));
    $('#opportunity-category-options').innerHTML=(catalog?.opportunity_categories||[]).map(category=>`<label class="status-option category-option"><input type="checkbox" name="opportunity_category_ids" value="${esc(category.id)}"><span><strong>${esc(category.name)}</strong><small>${esc(category.description)}</small></span></label>`).join('');
    $('#status-options').innerHTML=(catalog?.statuses||[]).map(option=>`<label class="status-option"><input type="checkbox" name="status_codes" value="${esc(option.id)}"><span>${esc(option.name)}</span></label>`).join('');
    $('#modality-options').innerHTML=(catalog?.modalities||[]).map(option=>`<label class="status-option"><input type="checkbox" name="modality_codes" value="${esc(option.id)}"><span>${esc(option.name)}</span></label>`).join('');
    $('#search-municipality').innerHTML='<option value="">Qualquer município</option>'+(catalog?.search_municipalities||[]).map(option=>`<option value="${esc(option.name)}">${esc(option.name)}</option>`).join('');
    $('#search-status').innerHTML='<option value="">Qualquer situação</option>'+(catalog?.statuses||[]).map(option=>`<option value="${esc(option.id)}">${esc(option.name)}</option>`).join('');
    createCustomSelect($('#search-municipality'));
    createCustomSelect($('#search-status'));
  };
  $('#opportunity-category-options').addEventListener('change',()=>{
    const count=$$('#opportunity-category-options input:checked').length;
    $('#category-selection-count').textContent=count?`${count} ${count===1?'categoria selecionada':'categorias selecionadas'}`:'Todas as categorias';
  });
  const loadCatalog = async () => {
    catalog=await api('/v1/catalog');
    try {
      const response=await fetch('/assets/municipalities-go.json?v=1');
      if(!response.ok)throw new Error('Lista municipal indisponível');
      catalog.search_municipalities=await response.json();
    } catch (_) { catalog.search_municipalities=catalog.municipalities||[]; }
    renderCatalogFilters();
  };
  const fillProfileForm = (profileId = '') => {
    const form=$('#profile-form'); form.reset();
    form.elements.name.setCustomValidity('');
    const profile=profiles.find(item=>item.id===profileId);
    closeCustomSelects();
    form.elements.id.value=profile?.id||''; form.elements.name.value=profile?.name||'';
    $$('#opportunity-category-options input[name="opportunity_category_ids"]').forEach(input=>{input.checked=(profile?.opportunity_category_ids||[]).includes(input.value);});
    const selectedCategoryCount=(profile?.opportunity_category_ids||[]).length;
    $('#category-selection-count').textContent=selectedCategoryCount?`${selectedCategoryCount} ${selectedCategoryCount===1?'categoria selecionada':'categorias selecionadas'}`:'Todas as categorias';
    setSelectValue($('#profile-municipality'),profile?.municipality_codes?.[0]||'');
    setSelectValue(form.elements.deadline_days,profile?.deadline_days??'');
    $$('#status-options input[name="status_codes"]').forEach(input=>{input.checked=(profile?.status_codes||[]).includes(input.value);});
    $$('#modality-options input[name="modality_codes"]').forEach(input=>{input.checked=(profile?.modality_codes||[]).includes(input.value);});
    const warning=$('#legacy-profile-warning');
    warning.textContent=profile?.legacy_options?.length?'Este perfil usava critérios de itens, que foram removidos. Escolha as categorias de licitação que deseja acompanhar e salve para atualizar o perfil.':'';
    warning.classList.toggle('hidden',!profile?.legacy_options?.length);
    setProfileStep(1);
  };
  const setProfileStep = step => {
    profileStep=Math.max(1,Math.min(6,step));
    $('#profile-form [name="name"]').required=profileStep===1;
    $$('.profile-step').forEach(section=>{
      const active=Number(section.dataset.profileStep)===profileStep;
      section.classList.toggle('hidden',!active);
      if(active){section.setAttribute('aria-current','step');const heading=section.querySelector('h2');heading?.setAttribute('tabindex','-1');heading?.focus({preventScroll:true});}
      else section.removeAttribute('aria-current');
    });
    $('#profile-step-label').textContent=`Etapa ${profileStep} de 6`;
    $('#profile-progress-fill').style.width=`${(profileStep/6)*100}%`;
    $('#profile-step-back').disabled=profileStep===1;
    $('#profile-step-next').classList.toggle('hidden',profileStep===6);
    $('#profile-save').classList.toggle('hidden',profileStep!==6);
  };
  const profileSummary = profile => {
    const parts=[];
    const selectedCategories=(catalog?.opportunity_categories||[]).filter(item=>(profile.opportunity_category_ids||[]).includes(item.id));
    parts.push(profile.legacy_options?.length?'Revise as categorias':selectedCategories.length?selectedCategories.map(item=>item.name).join(', '):'Todas as categorias');
    const municipality=(catalog?.municipalities||[]).find(item=>item.id===profile.municipality_codes?.[0]);
    if(municipality)parts.push(municipality.name);else if(profile.municipality_codes?.length)parts.push('Município selecionado');
    if(profile.modality_codes?.length)parts.push(`${profile.modality_codes.length} ${profile.modality_codes.length===1?'modalidade':'modalidades'}`);
    parts.push(profile.deadline_days?`Até ${profile.deadline_days} dias`:'Sem limite de prazo');
    parts.push(profile.status_codes?.length?`${profile.status_codes.length} situações`:'Todas as situações');
    return parts.join(' · ');
  };
  const renderProfileList = () => {
    const list=$('#profile-list');
    if(!list)return;
    if(!profiles.length){
      list.innerHTML='<div class="profile-list-empty"><span class="profile-empty-icon"><i class="ti ti-adjustments-horizontal" aria-hidden="true"></i></span><h2>Nenhum perfil criado</h2><p>Crie um perfil para reunir os critérios de oportunidades que sua empresa procura.</p><button type="button" class="button button-dark" data-profile-new><i class="ti ti-plus" aria-hidden="true"></i> Criar primeiro perfil</button></div>';
      return;
    }
    list.innerHTML=profiles.map(profile=>`<article class="profile-list-card${profile.id===selectedProfile?' is-current':''}" data-profile-id="${esc(profile.id)}"><div class="profile-list-card-copy"><div class="profile-list-card-title"><h2>${esc(profile.name)}</h2>${profile.id===selectedProfile?'<span class="profile-current-tag">Em uso no radar</span>':''}</div><p>${esc(profileSummary(profile))}</p></div><div class="profile-list-card-actions"><button class="button button-outline" type="button" data-profile-edit="${esc(profile.id)}"><i class="ti ti-pencil" aria-hidden="true"></i> Editar</button><button class="icon-button profile-delete-button" type="button" data-profile-delete="${esc(profile.id)}" aria-label="Excluir perfil ${esc(profile.name)}" title="Excluir perfil"><i class="ti ti-trash" aria-hidden="true"></i></button></div></article>`).join('');
  };
  const showProfileList = () => {
    $('#profile-list-panel').classList.remove('hidden');
    $('#profile-editor').classList.add('hidden');
    $('#new-profile').classList.remove('hidden');
    $('#profile-page-title').textContent='Perfil de interesse';
    renderProfileList();
  };
  const openProfileEditor = (profileId = '') => {
    fillProfileForm(profileId);
    $('#profile-list-panel').classList.add('hidden');
    $('#profile-editor').classList.remove('hidden');
    $('#new-profile').classList.add('hidden');
    $('#profile-page-title').textContent=profileId?'Editar perfil':'Criar perfil';
    $('#profile-form [name="name"]').focus();
  };
  $('#new-profile').addEventListener('click',()=>openProfileEditor());
  $('#profile-cancel').addEventListener('click',showProfileList);
  $('#profile-cancel-top').addEventListener('click',showProfileList);
  $('#profile-step-next').addEventListener('click',()=>{
    if(profileStep===1){const name=$('#profile-form [name="name"]');name.setCustomValidity(name.value.trim()?'':'Informe um nome para o perfil.');if(!name.reportValidity())return;}
    setProfileStep(profileStep+1);
  });
  $('#profile-form [name="name"]').addEventListener('input',event=>event.currentTarget.setCustomValidity(''));
  $('#profile-step-back').addEventListener('click',()=>setProfileStep(profileStep-1));
  $('#profile-list').addEventListener('click',async event=>{
    const edit=event.target.closest('[data-profile-edit]');
    if(edit){openProfileEditor(edit.dataset.profileEdit);return;}
    const remove=event.target.closest('[data-profile-delete]');
    if(!remove)return;
    const profile=profiles.find(item=>item.id===remove.dataset.profileDelete);
    if(!profile||!window.confirm(`Excluir o perfil “${profile.name}”?`))return;
    remove.disabled=true;
    try{await api(`/v1/interest-profiles/${profile.id}`,{method:'DELETE'});await loadProfiles();showProfileList();showToast('Perfil excluído.');}
    catch(error){remove.disabled=false;showToast(cleanError(error),'error');}
  });
  $('#profile-list').addEventListener('click',event=>{
    if(event.target.closest('[data-profile-new]'))openProfileEditor();
  });
  $('#profile-form').addEventListener('submit',async event=>{
    event.preventDefault(); const form=event.currentTarget; const id=form.elements.id.value;
    if(!form.elements.name.value.trim()){setProfileStep(1);form.elements.name.setCustomValidity('Informe um nome para o perfil.');form.elements.name.focus();form.elements.name.reportValidity();return;}
    const opportunity_category_ids=$$('#opportunity-category-options input[name="opportunity_category_ids"]:checked').map(input=>input.value);
    const payload={name:form.elements.name.value,opportunity_category_ids,municipality_codes:$('#profile-municipality').value?[$('#profile-municipality').value]:[],status_codes:$$('#status-options input[name="status_codes"]:checked').map(input=>input.value),modality_codes:$$('#modality-options input[name="modality_codes"]:checked').map(input=>input.value),deadline_days:form.elements.deadline_days.value?Number(form.elements.deadline_days.value):null,active:true};
    const saveButton=$('#profile-save');saveButton.disabled=true;saveButton.setAttribute('aria-busy','true');
    try { const saved=await api(id?`/v1/interest-profiles/${id}`:'/v1/interest-profiles',{method:id?'PATCH':'POST',body:JSON.stringify(payload)}); await loadProfiles(saved.id); showProfileList(); showToast(opportunity_category_ids.length?'Perfil salvo com filtro por categorias de licitação.':'Perfil salvo sem filtro de categoria.'); }
    catch(error){showToast(cleanError(error),'error');}
    finally{saveButton.disabled=false;saveButton.removeAttribute('aria-busy');}
  });
  const profileSwitchDialog = $('#profile-switch-dialog');
  $('#edit-profile').addEventListener('click',()=>{renderProfileSwitchOptions();profileSwitchDialog.showModal();});
  $('.profile-switch-close').addEventListener('click',()=>profileSwitchDialog.close());
  profileSwitchDialog.addEventListener('click',event=>{if(event.target===profileSwitchDialog)profileSwitchDialog.close();});
  $('#profile-switch-list').addEventListener('click',event=>{
    const option=event.target.closest('[data-switch-profile]');if(!option)return;
    const nextProfile=option.dataset.switchProfile;if(!profiles.some(profile=>profile.id===nextProfile)||nextProfile===selectedProfile){profileSwitchDialog.close();return;}
    selectedProfile=nextProfile;$('#profile-name-label').textContent=profiles.find(profile=>profile.id===selectedProfile)?.name||'Sem perfil';
    updateUrl({profile:selectedProfile});profileSwitchDialog.close();loadFeed(1);
  });
  $('#profile-switch-manage').addEventListener('click',()=>{profileSwitchDialog.close();setView('profile');});
  $$('.nav-item').forEach(item=>{item.dataset.label=item.textContent.trim();item.addEventListener('click',event=>{event.preventDefault();setView(item.dataset.view);});});
  $('#quick-search').addEventListener('click',()=>{setView('explore');setTimeout(()=>$('#search-query').focus(),0);});
  $('#visual-comfort-toggle').addEventListener('click',()=>{
    visualComfort = !visualComfort;
    applyVisualComfort(visualComfort);
    try { localStorage.setItem(visualComfortKey, visualComfort ? 'on' : 'off'); } catch (_) { /* A preferência permanece ativa até recarregar. */ }
    showToast(visualComfort ? 'Conforto visual ativado.' : 'Conforto visual desativado.','info');
  });
  document.addEventListener('keydown',event=>{if(event.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName)){event.preventDefault();$('#quick-search').click();}});
  document.body.addEventListener('click',event=>{const jump=event.target.closest('[data-view-jump]');if(jump)setView(jump.dataset.viewJump);});
  document.addEventListener('click',event=>{
    const trigger=event.target.closest('[data-calendar-trigger]');
    if(trigger){
      const name=trigger.dataset.calendarTrigger;const popover=$(`[data-calendar="${name}"]`);
      const wasOpen=!popover.classList.contains('hidden');closeDateCalendars();
      if(!wasOpen){document.body.append(popover);popover.classList.remove('hidden');trigger.setAttribute('aria-expanded','true');renderDateCalendar(name);positionDateCalendar(popover);(popover.querySelector('[aria-pressed="true"]')||popover.querySelector('[aria-current="date"]')||popover.querySelector('.calendar-day'))?.focus();}
      return;
    }
    const step=event.target.closest('[data-calendar-step]');
    if(step){
      const name=step.closest('[data-calendar]')?.dataset.calendar;if(!name)return;
      const current=datePickerMonths.get(name)||new Date(new Date().getFullYear(),new Date().getMonth(),1);const next=new Date(current.getFullYear(),current.getMonth()+Number(step.dataset.calendarStep),1);datePickerMonths.set(name,next);renderDateCalendar(name);positionDateCalendar($(`[data-calendar="${name}"]`));$(`[data-calendar="${name}"] .calendar-day`)?.focus();return;
    }
    const day=event.target.closest('[data-calendar-date]');
    if(day){const name=day.closest('[data-calendar]')?.dataset.calendar;if(!name)return;setDatePickerValue(name,day.dataset.calendarDate);closeDateCalendars();$(`[data-calendar-trigger="${name}"]`)?.focus();return;}
    const clear=event.target.closest('[data-calendar-clear]');
    if(clear){const name=clear.dataset.calendarClear;setDatePickerValue(name,'');renderDateCalendar(name);$(`[data-calendar="${name}"] .calendar-day`)?.focus();return;}
    if(event.target.closest('[data-calendar-close]')){closeDateCalendars(true);return;}
  });
  document.addEventListener('pointerdown',event=>{
    if(!event.target.closest('[data-date-picker],.date-popover'))closeDateCalendars();
    if(!event.target.closest('.custom-select,.custom-select-popover'))closeCustomSelects();
    else if(event.target.closest('[data-date-picker],.date-popover'))closeCustomSelects();
  });
  window.addEventListener('resize',repositionOpenDateCalendars);
  window.addEventListener('scroll',repositionOpenDateCalendars,true);
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&document.querySelector('[data-calendar]:not(.hidden)')){event.preventDefault();closeDateCalendars(true);return;}
    const day=event.target.closest?.('[data-calendar-date]');if(!day)return;
    const offsets={ArrowLeft:-1,ArrowRight:1,ArrowUp:-7,ArrowDown:7};const offset=offsets[event.key];if(!offset)return;
    const calendar=day.closest('[data-calendar]');const days=Array.from(calendar.querySelectorAll('[data-calendar-date]'));const next=days[days.indexOf(day)+offset];if(next){event.preventDefault();next.focus();}
  });
  $('#search-form').addEventListener('submit',event=>{
    event.preventDefault();
    clearTimeout(exploreDebounceTimer);
    const q=$('#search-query').value.trim(),municipality=$('#search-municipality').value,status=$('#search-status').value,opening_from=$('#search-from').value,opening_to=$('#search-to').value;
    if(opening_from&&opening_to&&opening_from>opening_to){showToast('A data inicial precisa ser anterior à data final.','error');return;}
    updateUrl({q,municipality,status,opening_from,opening_to,profile:null});setView('explore');
  });
  $('#search-query').addEventListener('input',()=>{
    clearTimeout(exploreDebounceTimer);
    exploreDebounceTimer=setTimeout(()=>{
      if(activeView!=='explore')return;
      const q=$('#search-query').value.trim(),municipality=$('#search-municipality').value,status=$('#search-status').value,opening_from=$('#search-from').value,opening_to=$('#search-to').value;
      updateUrl({q,municipality,status,opening_from,opening_to,profile:null});
      loadExplore(1);
    },350);
  });
  $('#refresh-feed').addEventListener('click',()=>loadFeed(feedPage));

  const submitFeedback = async (id, relevant, button, reason=null) => {
    const card=button?.closest('.op-card');
    if(button){button.disabled=true;button.setAttribute('aria-busy','true');}
    try{
      await api(`/v1/opportunities/${id}/feedback`,{method:'POST',body:JSON.stringify({relevance:relevant?'relevant':'not_relevant',reason,profile_id:selectedProfile||null})});
      card?.querySelectorAll('.feedback-choice').forEach(choice=>{
        const selected=choice.dataset.act===(relevant?'feedback-yes':'feedback-no');
        choice.classList.toggle('is-selected',selected);
        choice.setAttribute('aria-pressed',String(selected));
      });
      showToast('Feedback registrado para sua empresa.');
    }
    catch(error){showToast(cleanError(error),'error');}
    finally{if(button){button.disabled=false;button.removeAttribute('aria-busy');}}
  };
  const feedbackDialog=$('#feedback-dialog');
  $('#feedback-form').addEventListener('submit',event=>{
    event.preventDefault();
    const reason=new FormData(event.currentTarget).get('feedback_reason');
    if(!reason){showToast('Escolha um motivo para continuar.','error');return;}
    const pending=pendingFeedback;
    if(!pending)return;
    pendingFeedback=null;
    feedbackDialog.close();
    submitFeedback(pending.id,false,pending.button,reason);
  });
  $('#feedback-cancel').addEventListener('click',()=>feedbackDialog.close());
  feedbackDialog.addEventListener('close',()=>{pendingFeedback=null;$('#feedback-form').reset();});
  const updateFollowedCard = (card, followed) => {
    if(!card)return;
    card.classList.toggle('is-followed',followed);
    const button=card.querySelector('[data-act="follow"]');
    if(!button)return;
    button.classList.toggle('following',followed);
    button.setAttribute('aria-pressed',String(followed));
    button.innerHTML=`<i class="ti ${followed?'ti-check':'ti-bookmark'}" aria-hidden="true"></i> ${followed?'Acompanhando':'Acompanhar'}`;
  };
  const changeFollowCount = delta => {
    const countNode=$('#dock-follows-count');
    if(!countNode)return;
    const current=Number(countNode.textContent.replace(/\D/g,''))||0;
    if(followCountLoaded)countNode.textContent=Math.max(0,current+delta).toLocaleString('pt-BR');
  };
  document.body.addEventListener('click',async event=>{
    const button=event.target.closest('[data-act]'); if(!button)return;
    const action=button.dataset.act; const card=button.closest('[data-id]'); const id=button.dataset.id||card?.dataset.id;
    if(action==='create-profile'){setView('profile');return;}
    if(action==='detail'){showDetail(id);return;}
    if(action==='changes'){showDetail(id);return;}
    if(action==='feedback-yes'){submitFeedback(id,true,button);return;}
    if(action==='feedback-no'){
      if(button.disabled)return;
      pendingFeedback={id,button};
      $('#feedback-form').reset();
      feedbackDialog.showModal();
      $('#feedback-form input[name="feedback_reason"]')?.focus();
      return;
    }
    if(action==='follow'){
      event.preventDefault();
      if(button.disabled)return;
      const wasFollowing=button.classList.contains('following');
      button.disabled=true;button.setAttribute('aria-busy','true');
      try {
        if(wasFollowing)await api(`/v1/follows/${id}`,{method:'DELETE'});
        else await api('/v1/follows',{method:'POST',body:JSON.stringify({opportunity_id:id})});
        updateFollowedCard(card,!wasFollowing);changeFollowCount(wasFollowing?-1:1);
        if(wasFollowing&&activeView==='follows'){
          const note=card.nextElementSibling;
          card.remove();if(note?.classList.contains('follow-note'))note.remove();
          if(!$('#follows-list').querySelector('[data-id]'))$('#follows-list').innerHTML='<div class="empty-state">Você ainda não acompanha oportunidades.</div>';
        }
        showToast(wasFollowing?'Acompanhamento removido.':'Oportunidade acompanhada.');
      }
      catch(error){showToast(cleanError(error),'error');}
      finally{button.disabled=false;button.removeAttribute('aria-busy');}
    }
  });

  $('#organization-form').addEventListener('submit',async event=>{
    event.preventDefault(); const name=new FormData(event.currentTarget).get('name');
    try { currentOrganization=await api('/v1/organizations',{method:'POST',body:JSON.stringify({name})});$('#organization-name').textContent=currentOrganization.name;$('#organization-setup').classList.add('hidden');await loadCatalog();showToast('Espaço criado. Configure seus interesses.');setView('profile'); }
    catch(error){showToast(cleanError(error),'error');}
  });
  const startApp = async () => {
    if(!accessToken){showLogin('');return;}
    const startGeneration = sessionGeneration;
    try {
      currentUser=await api('/v1/me');
      $('#user-email').textContent=currentUser.email;$('#user-avatar').textContent=currentUser.email.slice(0,2).toUpperCase();
      const membership=currentUser.memberships?.[0];
      if(!membership){$('#organization-setup').classList.remove('hidden');$$('.view').forEach(node=>node.classList.add('hidden'));showApp();return;}
      currentOrganization=await api(`/v1/organizations/${membership.organization_id}`);$('#organization-name').textContent=currentOrganization.name;
      $('#organization-setup').classList.add('hidden');await loadCatalog();await loadProfiles();
      const requestedView=location.hash.replace('#','');setView(['feed','explore','follows','profile','alerts'].includes(requestedView)?requestedView:'feed');showApp();
    } catch(error){if(accessToken && startGeneration === sessionGeneration)showLogin(cleanError(error));}
  };
  window.addEventListener('hashchange',()=>{const view=location.hash.slice(1);if(['feed','explore','follows','profile','alerts'].includes(view)&&view!==activeView)setView(view);});
  fetch('/v1/client-config').then(response=>response.json()).then(value=>{config=value;if(accessToken)startApp();else showLogin('');}).catch(()=>showLogin('Não foi possível carregar a configuração local da aplicação.'));
})();
