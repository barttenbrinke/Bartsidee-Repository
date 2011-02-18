const volume_x1 = 453;
const volume_x2 = 459;
const volume_y1 = 205;
const volume_y2 = 245;

const progress_x1 = 2;
const progress_x2 = 511;
const progress_y  = 256;

const progress_skip_pixels = 20;
const progress_big_skip_pixels = 40;

const progress_back_pixels = 10;
const progress_big_back_pixels = 20;

var isPaused = false;

boxee.rewriteSrc = function(url) { originalUrl = url; return url; } 

if(boxee.getVersion() > 1.8)
{
  boxee.setCanPause(true);
  boxee.setCanSkip(false);
  boxee.setCanSetVolume(false);
  boxee.enableLog(true);
}

boxee.autoChoosePlayer=false;
boxee.renderBrowser=false;

var hasActive=false;
var hasGuidance=false;

function R(p) { return (p & 0x00ff0000) >> 16; }
function G(p) { return (p & 0x0000ff00) >> 8; }
function B(p) { return (p & 0x000000ff) ; }

function poll()
{
  if (!hasActive)
  {
    boxee.getWidgets().forEach(function(A)
    {
      var widgetId = A.getAttribute('name');
      if (widgetId == "Mercury_VideoPlayervideoplayer")
      {
        A.setActive(true);
        boxee.notifyConfigChange(A.width,A.height);
        boxee.renderBrowser=false;
        hasActive=true;
        setTimeout(poll_guidance,1000);
      }
    });
  }
  if(!hasActive)
  {
  	setTimeout(poll,1000);
  }
}

function poll_guidance()
{
  if (!hasGuidance)
  {
    boxee.getWidgets().forEach(function(A)
    {
      var widgetId = A.getAttribute('name');
      var src = A.getAttribute('src');
      if (widgetId == "cDiv" && src != "" && src.indexOf("Guidance.swf") != -1) // "Mature Content" warning
      {
        hasGuidance = true;
        A.setActive(true);
        boxee.getActiveWidget().setActive(false); // Deactivate widget
        boxee.notifyConfigChange(A.width,A.height);
        boxee.renderBrowser=false;
        setTimeout( function() { click_guidance(); }, 5000);
      }
    });
  }
  if(!hasGuidance)
  {
  	setTimeout(poll_guidance,1000);
  }
}

function click_guidance()
{
	boxee.getActiveWidget().mouseMove(28,450);
	boxee.getActiveWidget().click(28,450);
	boxee.getActiveWidget().mouseMove(0,0);
	
	boxee.getActiveWidget().mouseMove(90,512);
        boxee.getActiveWidget().click(90,512);
        boxee.getActiveWidget().mouseMove(0,0);
        
        browser.mouseMove(1,1);
        
        setTimeout( function() { click_guidance_screen2(); }, 1000);
}

function click_guidance_screen2()
{
	boxee.getActiveWidget().mouseMove(62,345);
	boxee.getActiveWidget().click(62,345);
	boxee.getActiveWidget().mouseMove(0,0);
        browser.mouseMove(1,1);
        
        //setTimeout( function() { clear_guidance(); }, 1000);
        clear_guidance();
}

function clear_guidance()
{
	hasGuidance = false;
        hasActive = false;
        boxee.getActiveWidget().setActive(false); // Deactivate widget
        setTimeout(poll,1000);
}

boxee.onDocumentLoaded = function()
{
	setTimeout(poll,1000);
}

function PlayOrPause()
{
	boxee.getActiveWidget().click(24,334);
	boxee.getActiveWidget().mouseMove(0,0);
	browser.mouseMove(1,1);
}

boxee.onPlay = function()
{
  if(hasGuidance)
  {
  	hasGuidance = false;
  	click_guidance();
  }
  if(isPaused)
  {
    boxee.getActiveWidget().mouseMove(10,10);
    //setTimeout( function() { PlayOrPause();}, 1000);
    PlayOrPause();
    isPaused = false;
  }
}

boxee.onPause = function()
{  
  if(!isPaused)
  {
    boxee.getActiveWidget().mouseMove(10,10);
    //setTimeout( function() { PlayOrPause();}, 1000);
    PlayOrPause();
    isPaused = true;
  }
}

boxee.onSkip = function()
{
  var currentPosX = GetCurrentLocationX();

  var x = currentPosX + progress_skip_pixels;
  
  if (x > progress_x2)
  {
    x = progress_x2;
  }
  
  boxee.getActiveWidget().click(x, progress_y);
  boxee.getActiveWidget().mouseMove(0,0);
  browser.mouseMove(1,1);
}

boxee.onBigSkip = function()
{
  var currentPosX = GetCurrentLocationX();

  var x = currentPosX + progress_big_skip_pixels;

  if (x > bbc_progress_x2)
  {
    x = bbc_progress_x2;
  }
  
  boxee.getActiveWidget().click(x, progress_y);
  boxee.getActiveWidget().mouseMove(0,0);
  browser.mouseMove(1,1);
}

boxee.onBack = function()
{
  var currentPosX = GetCurrentLocationX();

  var x = currentPosX - progress_back_pixels;

  if (x < progress_x1)
  {
    x = progress_x1;
  }
  
  boxee.getActiveWidget().click(x, progress_y);
  boxee.getActiveWidget().mouseMove(0,0);
  browser.mouseMove(1,1);
}

boxee.onBigBack = function()
{
  var currentPosX = GetCurrentLocationX();

  var x = currentPosX - progress_big_back_pixels;

  if (x < progress_x1)
  {
    x = progress_x1;
  }
  
  boxee.getActiveWidget().click(x, progress_y);
}

// This returns the current location in the bar of the OSD (pixels)
function GetCurrentLocationX()
{
  var r, g, b, p;
  boxee.getActiveWidget().mouseMove(0,0);
  for (var x = progress_x1; x < progress_x2; x += progress_skip_pixels)
  {
    p = boxee.getActiveWidget().getPixel(x, progress_y);
    b = B(p);
    g = G(p);
    r = R(p);
    if(g < 100 || g == 255)
    {
    	return x;
    }
  }
 
  // fall through
  return progress_x2;
}
