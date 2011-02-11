boxee.enableLog(true);
boxee.autoChoosePlayer=false;
boxee.renderBrowser=true;

var btn_y1 = 500;
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
            widget.setCrop(81, 76, 81, 76);
            boxee.notifyConfigChange(widget.width-160, widget.height-150);
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
	boxee.getActiveWidget().mouseMove(btn_x2,btn_y1);
	setTimeout(function(){
		boxee.getActiveWidget().click(btn_x2,btn_y1);
	},100);
}

boxee.onPlay = function()
{
	boxee.getActiveWidget().mouseMove(btn_x2,btn_y1);
	setTimeout(function(){
		boxee.getActiveWidget().click(btn_x2,btn_y1);
	},100);
}
