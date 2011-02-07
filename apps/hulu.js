boxee.browserWidth=1280;
boxee.browserHeight=720;
boxee.earlyTimers = true;
boxee.enableLog(true);

boxee.onInit = function() {
   //browser.setConfigChar('general.useragent.override','Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.1) Gecko/200807820');
}

if (boxee.getVersion() < 5)
   boxee.renderBrowser = true;

boxee.parseBoxeeTags = false;
boxee.autoChoosePlayer = false;

var current    = 0;
var h_width    = 720;
var h_bottom   = 23;
var started    = false;
var active     = false;
var duration   = false;
var is_paused  = false;
var alt_player = false;

boxee.onBack = function()  { boxee.onEnter(); }
boxee.onLeft = function()  { boxee.onEnter(); }
boxee.onRight = function() { boxee.onEnter(); }
boxee.onUp = function()    { boxee.onEnter(); }
boxee.onDown = function()  { boxee.onEnter(); }

wmodeFix = setInterval(function() {
   boxee.getWidgets().forEach(function(widget) {
      zorder_id = widget.getAttribute("id");
      if (zorder_id == 'banner_c')
         browser.execute('document.getElementById("'+zorder_id+'").style.zIndex = 99999;');
   });
}, 500);

boxee.onDocumentLoaded = function() {
   boxee.setMode(1);
   boxee.showNotification("[B]Press Enter to view full screen[/B]", ".", 500);
}

boxee.onEnter = function()
{
   boxee.setMode(0);

   if (boxee.getVersion() < 5)
      browser.execute('window.scrollTo(0,50);');

   clearInterval(wmodeFix);
   boxee.showNotification("[B]Switching to full screen...[/B]", ".", 2);
   playerTimer = setInterval(function(){
      if (!active) locatePlayer();
      else updateProgress();
   }, 1000)
}

function playerReference()
{
   id = boxee.getActiveWidget().getAttribute('id');
   if (id.length > 0)
      return 'document.'+id+'.';

   else if (alt_player != false)
      return alt_player;

   else
   {
      var locateMe = "(function(){objects=document.getElementsByTagName('embed'); for (var i in objects) { if (objects[i].getAttribute('src') == '"+boxee.getActiveWidget().getAttribute('src')+"') return i; }})()";
      locateMe = browser.execute(locateMe);
      if (locateMe > 0)
      {
         alt_player = 'document.getElementsByTagName("embed")['+locateMe+'].';
         return alt_player;
      }
      else
         return 'document.player.';
   }
}

function updateProgress()
{
   if (!duration)
      duration = parseInt(browser.execute(playerReference()+'getDuration()')) / 1000;

   if (duration)
      boxee.setDuration(duration);

   current = parseInt(browser.execute(playerReference()+'getCurrentTime()')) / 1000;
   if (isNaN(current))
      alt_player = false;

   if (current > 0 && !started)
      started = true;

   progress = current / duration * 100;
   alert(progress);
   boxee.notifyCurrentTime(current);
   boxee.notifyCurrentProgress(progress);

   if (started && progress > 99.9)
      boxee.notifyPlaybackEnded();
}

function locatePlayer()
{
   boxee.getWidgets().forEach(function(widget) {
      flashvars = widget.getAttribute("flashvars");
      if (flashvars.indexOf('hulu.com/watch') != -1 && flashvars.indexOf('bitrate=') != -1 && !active) {
         active = true;
         boxee.renderBrowser = false;
         var crop = (widget.width - h_width) / 2;
         widget.setCrop(crop, 0, crop, h_bottom);
         boxee.notifyConfigChange(widget.width-(crop*2),widget.height-h_bottom);
         widget.setActive(true);
      }
   });

   if (active)
   {
      boxee.setCanPause(true);
      boxee.setCanSkip(true);
      boxee.setCanSetVolume(true);
   }

   return active;
}

boxee.onPause = function()
{
   is_paused = true;
   browser.execute(playerReference() + 'pauseVideo()')
}

boxee.onPlay = function()
{
   is_paused = false;
   browser.execute(playerReference() + 'resumeVideo()')
}

boxee.onSkip = function ()
{
   if (is_paused) return;
   update = (duration < 3000) ? (current + 60) : (current + 120);
   browser.execute(playerReference() + 'seekVideo('+update+')');
}

boxee.onBigSkip = function ()
{
   if (is_paused) return;
   update = (duration < 3000) ? (current + 180) : (current + 360);
   browser.execute(playerReference() + 'seekVideo('+update+')');
}

boxee.onBack = function ()
{
   if (is_paused) return;
   update = (duration < 3000) ? (current - 60) : (current - 120);
   browser.execute(playerReference() + 'seekVideo('+update+')');
}

boxee.onBigBack = function ()
{
   if (is_paused) return;
   update = (duration < 3000) ? (current - 180) : (current - 360);
   browser.execute(playerReference() + 'seekVideo('+update+')');
}

boxee.onSetVolume = function(volume)
{
   browser.execute(playerReference() + 'setVolume('+volume/100+')');
}