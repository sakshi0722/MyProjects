// content.js — injected into every page
// Detects user activity (scroll, click, keypress) to avoid counting idle time

let lastActivity = Date.now();
let isIdle = false;
const IDLE_THRESHOLD = 60000; // 1 min

['mousemove', 'keydown', 'scroll', 'click', 'touchstart'].forEach(event => {
  document.addEventListener(event, () => {
    lastActivity = Date.now();
    if (isIdle) {
      isIdle = false;
      chrome.runtime.sendMessage({ type: 'USER_ACTIVE' }).catch(() => {});
    }
  }, { passive: true });
});

setInterval(() => {
  if (Date.now() - lastActivity > IDLE_THRESHOLD && !isIdle) {
    isIdle = true;
    chrome.runtime.sendMessage({ type: 'USER_IDLE' }).catch(() => {});
  }
}, 10000);
