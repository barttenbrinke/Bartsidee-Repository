boxee.enableLog(true);
boxee.autoChoosePlayer=true;
boxee.renderBrowser=false;

var btn_y1 = 0;
var btn_x2 = 20;

hasSet = false;

if (boxee.getVersion() > 3.0)
{
	boxee.setCanSkip(false);
	boxee.setCanSetVolume(false);
}

_findPlayer = setInterval(function()
{
   if (!hasSet)
   {
      boxee.getWidgets().forEach(function(widget)
      {
         if (widget.getAttribute("id") == 'embeddedPlayer')
         {
            boxee.renderBrowser=false;
            widget.setCrop(0, 0, 0, 51);
            boxee.notifyConfigChange(widget.width, widget.height-50);
            widget.setActive(true);
            boxee.setCanPause(true);
			hasSet = true;
            clearInterval(_findPlayer);
         }
      });
   }
}, 1000);

boxee.onPause = function()
{
	boxee.getActiveWidget().click(btn_x2,btn_y1);
}

boxee.onPlay = function()
{
	boxee.getActiveWidget().click(btn_x2,btn_y1);
}
